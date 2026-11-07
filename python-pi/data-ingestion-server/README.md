# PostgreSQL storage

Install the project's dependencies and set `POSTGRES_DSN` to a connection string
for an existing PostgreSQL database, such as
`postgresql://USER:PASSWORD@localhost:5432/home`. The server must be running.
On application startup, the service creates the `home_objects`, `groups`, `devices`,
and `envelopes` tables and the sensor lookup index if they do not already exist.
Initialization runs an ordered series of migration functions:
`migration_version_0` creates the sensor/device schema, and `migration_version_1`
adds libraries and documents. A `versions` table records each applied migration in its
`version` integer primary key; version 0 inserts its own record after creating
the initial schema. Already-recorded migrations are skipped. Schema changes and
version records commit together, or roll back together on failure. Existing
unversioned databases retain their tables/data and are recorded as version 0.
Missing configuration or database failures are surfaced as errors.

All home-object, device, environment-sensor, and heartbeat routes now use
PostgreSQL exclusively. Writes are committed before the API responds. Existing
URLs and response shapes are unchanged:

- `/groups/` lists groups and creates one with a generated ID. A group has a
  `name` and a `points` array of `{x, y, z}` points (the home-object location
  type). `/groups/{id}` reads (`GET`), creates with that ID (`POST`), or
  deletes (`DELETE`) a group; `/groups/{id}/update` replaces any provided
  `name`/`points`. Missing groups return HTTP 404.
- `/devices/` lists devices; `/devices/{name}` reads or creates a device.
- `/devices/{name}/provision` updates the existing device, retaining its ID and
  creation date, and requires an existing home object.
- `/data-ingestion/` reads all sensor and heartbeat envelopes.
- `/data-ingestion/{mac_address}` reads environment-sensor envelopes only,
  filtering by server recording time (not sensor source time). The inclusive
  `min_hours_ago` / `max_hours_ago` window defaults to 0 through 72 hours; negative,
  reversed, or wider-than-72-hour windows return HTTP 400.
- `/data-ingestion/environment-sensor` and `/data-ingestion/heartbeat` accept
  the existing payloads, including Unix seconds or datetime source dates.
- `DELETE /data-ingestion/` retains its existing behavior: delete envelopes
  recorded strictly before `2027-01-01T00:00:00Z`.

Timestamps are stored in UTC; datetime inputs without an offset are treated as
UTC. Lists are ordered by creation/recording date and ID. This switches storage;
it does not copy historical InfluxDB records. Back up or migrate those separately
if needed. InfluxDB is no longer required.

## Libraries and documents

Libraries are named collections of documents. A document requires a nonblank
`name` and optionally contains `description`, `ocr_text`, and one uploaded image.
Names need not be unique. IDs are server-generated UUIDs; creation timestamps
are UTC. Library and document metadata are persisted in PostgreSQL, and image
bytes are stored in the document's `BYTEA` column, not in application upload files.
Deleting a library also deletes its documents and images.

| Method | Path | Operation |
| --- | --- | --- |
| GET / POST | `/libraries/` | List libraries / create with `{"name": "Receipts"}` |
| GET | `/libraries/{library_id}` | Read library, including its `documents` |
| PATCH / DELETE | `/libraries/{library_id}` | Update name / delete library |
| GET / POST | `/libraries/{library_id}/documents/` | List / create documents |
| GET / PATCH / DELETE | `/libraries/{library_id}/documents/{document_id}` | Read / update / delete document |
| PUT | `/libraries/{library_id}/documents/{document_id}/image` | Upload or replace image using multipart field `image` |
| GET / DELETE | `/libraries/{library_id}/documents/{document_id}/image` | Download original image / clear image |

Creation returns HTTP 201 with generated metadata; updates return HTTP 200
with metadata; deletes return HTTP 204. Metadata responses include `has_image`
instead of binary image data. `GET /libraries/` returns library metadata without
documents; the individual library and document-list endpoints include documents.
PATCH preserves omitted fields; explicit `null` clears `description` or `ocr_text`
but is invalid for `name`. Empty PATCH bodies are no-ops. Unknown fields,
blank/null names, and malformed IDs/bodies return HTTP 422. Missing resources
return HTTP 404, including documents accessed through the wrong library and
images that have not been uploaded. Clearing an already-empty image succeeds
if the document exists.

Example document creation body:

```json
{"name": "November receipt", "description": "Office supplies", "ocr_text": null}
```

Images are optional: create metadata first, then PUT an image when needed.
Uploads require `python-multipart`, are limited to 10 MiB (HTTP 413 above that),
and are validated with Pillow (HTTP 422 for invalid/unsupported images). The
download media type is derived from the actual image, not the client filename or
content-type. FastAPI may spool multipart uploads to temporary files; the
application reads bytes and performs validation in a worker thread.
Image upload/replacement does not generate or overwrite `ocr_text`; callers
can store OCR results explicitly using document PATCH.

## In-memory OCR

Install the project's Python dependencies (including `Pillow` and `pytesseract`)
and the separate Tesseract executable, available on `PATH`:

```sh
# Debian / Raspberry Pi OS (includes English language data)
sudo apt-get install tesseract-ocr tesseract-ocr-eng
# macOS
brew install tesseract
```

The `ocr` module exposes synchronous library functions; no OCR HTTP endpoints
are registered yet:

```python
from .ocr import extract_text, extract_text_from_bytes

text = extract_text(pillow_image)
text = extract_text_from_bytes(uploaded_image_bytes, lang="eng", timeout=30)
```

`extract_text` accepts a Pillow image without modifying or closing it.
`extract_text_from_bytes` accepts encoded image bytes (for example PNG, JPEG,
or TIFF), decodes them with Pillow in memory, and closes its own resources.
Multi-frame images use only the first frame. Both return Tesseract's text
unchanged, including whitespace; an image with no recognized text returns `""`.
Both accept keyword-only `lang`, `config` (for example `"--psm 6"`), and `timeout`
in seconds, defaulting to `"eng"`, `""`, and 30. Additional OCR languages need
their Tesseract language-data packages installed.

Invalid image data, missing Tesseract/language data, and OCR failures/timeouts
raise their original Pillow/pytesseract exceptions for callers to handle.
There are no application-managed upload files or required input paths, but
pytesseract internally uses temporary files to communicate with Tesseract;
this is not a disk-free OCR engine. For future async HTTP endpoints, read upload
bytes asynchronously and run these blocking helpers in a worker thread (for
example with Starlette's `run_in_threadpool`), not on the event loop.

## Tests

Group creation and point updates reject self-intersecting polygons, nonadjacent
edges that touch, overlapping edges, and nonfinite XY coordinates with HTTP 422
before writing to PostgreSQL. Edges are interpreted in the XY plane.

From the repository root, using the project's Python environment:

```sh
python -B -m unittest discover -s python-pi/data-ingestion-server/tests -v
```

Set `TEST_POSTGRES_DSN` to also run real PostgreSQL integration tests. These
create and drop an isolated test schema in that database, not existing tables.
The test database user needs permission to create schemas. Each test starts
with an empty schema and drops it during cleanup, including on failure.

```sh
TEST_POSTGRES_DSN='postgresql://USER:PASSWORD@localhost:5432/home_test' \
  python -B -m unittest discover -s python-pi/data-ingestion-server/tests -v
```

The API suites send HTTP requests through FastAPI's ASGI transport, including
application startup and real PostgreSQL persistence, rather than calling route
functions or mocking storage:

- `test_home_objects_api.py`: generated/explicit IDs, read-back, field-by-field
  updates, omitted/null fields, clearing collections, duplicate/missing objects,
  and invalid bodies that must not alter stored data.
- `test_groups_api.py`: group create/read/update/delete, partial updates,
  duplicate/missing groups, and invalid points or IDs.
- `test_devices_api.py`: create/list/read, provisioning and reprovisioning,
  identity preservation, invalid provisioning, and literal name lookups.
- `test_ingestion_api.py`: sensor/heartbeat serialization, timestamp conversion,
  optional/zero values, MAC/event/recording-time filters, invalid input, and
  strict deletion cutoff/idempotence without deleting devices or home objects.
- `test_app_api.py`: root/item endpoints, OpenAPI route inventory, CORS,
  unknown routes, and unsupported methods. These checks do not need PostgreSQL.

Without `TEST_POSTGRES_DSN`, database-backed suites are explicitly skipped.
The existing route/storage regression tests remain part of the same command.
Camera routes are not registered in the application and require Raspberry Pi
hardware, so camera behavior is outside this suite. There is no API
authentication configured; authentication flows are therefore not exercised.

Type-check the server with the optional `tooling` dependencies installed:

```sh
cd python-pi/data-ingestion-server
.venv/bin/pyright --pythonpath .venv/bin/python postgres_data.py library_data.py main.py ocr.py routers/devices.py routers/data_ingestion.py routers/home_objects.py routers/groups.py routers/libraries.py domain tests
```

The server uses CPython's standard-library types. Keep MicroPython hardware stubs
on the editor's extra search path rather than overriding the workspace typeshed.

Run only the OCR tests with:

```sh
python -B -m unittest discover -s python-pi/data-ingestion-server/tests -p 'test_ocr.py' -v
```

OCR unit tests do not require the Tesseract executable. A generated-image
integration test also checks real text recognition when Tesseract is on `PATH`;
otherwise it is explicitly skipped.

`test_libraries_api.py` covers library/document CRUD, nullable metadata updates,
image upload/replacement/download/removal, invalid input, library isolation,
and cascading deletion. Contract tests with mocked storage run without
PostgreSQL; persistence tests use `TEST_POSTGRES_DSN` and the same isolated
schema setup as the other database-backed API suites.
