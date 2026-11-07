# pi-configuration-fe

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Recommended Browser Setup

- Chromium-based browsers (Chrome, Edge, Brave, etc.):
  - [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
  - [Turn on Custom Object Formatter in Chrome DevTools](http://bit.ly/object-formatters)
- Firefox:
  - [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)
  - [Turn on Custom Object Formatter in Firefox DevTools](https://fxdx.dev/firefox-devtools-custom-object-formatters/)

## Type Support for `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking. In editors, we need [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) to make the TypeScript language service aware of `.vue` types.

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

The development server automatically opens `/pi-website/` in your browser.

### BootstrapVueNext

Bootstrap and BootstrapVueNext are installed through npm. The app registers
`createBootstrap()` in `src/main.ts` and loads both libraries' CSS before the
project styles so existing custom styling takes precedence.

Import components directly where needed for tree-shaking:

```vue
<script setup lang="ts">
import { BButton } from 'bootstrap-vue-next'
</script>

<template>
  <BButton variant="primary">Confirm</BButton>
</template>
```

See the [BootstrapVueNext documentation](https://bootstrap-vue-next.github.io/bootstrap-vue-next/).

The map toolbar/detail editors, group naming controls, device connection form,
dashboard refresh/IP controls, Pi configuration panel, and theme toggle use BootstrapVueNext buttons
and form controls. Bootstrap's
color mode follows the existing light/dark theme. Native dialog containers are
retained for their existing Escape, focus, and cancellation behavior; other
screens can be restyled incrementally.

The Pi configuration panel uses responsive General/Network/Logging sections,
Bootstrap form inputs and sensor/logging switches. Current sensor values are
shown without adding untouched settings to the partial-update request.

### Editing map objects

Select an object to edit its name, tags, and user data in the right-hand form.
Use **Add tag** or **Add user data** to add rows, and **Remove** to delete them.
User data has separate key/value fields; keys must be nonempty and unique.
**Save** sends the edited fields to `POST /home-objects/{id}/update` on the
backend at `http://localhost:8000`. Changes appear on the map only after a
successful save. Closing the panel or selecting another object discards unsaved edits.

Use **Connect device** in the home-object detail panel to select a registered
device and enter its MAC address. Confirming calls
`POST /devices/{name}/provision` with `mac_address` and the selected
`home_object_id`. Success updates the device list/chart and closes the modal.
An already provisioned device can be reconnected; its current MAC address is
prefilled and its previous home-object connection is replaced.
**Cancel** or Escape closes the modal without writing or discarding detail
edits. Loading/provisioning errors are displayed for retry. While a write is
in progress, confirmation and cancellation are disabled to avoid ambiguous
partial writes.

### Creating map groups

Trackpad pinch and mouse-wheel zoom use one-quarter of the original sensitivity.
Zoom buttons retain their normal step.

Use **Create group**, enter a group name, and confirm. A 100-by-100 map-unit
square appears under the cursor and follows it. Click or tap the map to save
its four `{x, y, z: 0}` corners to `POST /groups/{id}`. Moving alone does not
save. **Cancel placement** or Escape
discards the preview. Failed saves keep the preview for retry; saved groups are
shown on the map and loaded again from `GET /groups/` when the map opens.

Click a saved group to select it. Drag a corner to move that point, or an edge
to move both of its endpoints. The shape updates while dragging; dropping
saves the points to `POST /groups/{id}/update`. Failed saves restore the previous
boundaries and show an error in the shared details panel. The panel shows group
information or the home-object form depending on the selection. **Close**, Escape,
or clicking empty map space hides the panel and handles. Corner heights (`z`) are preserved.

Group details list home objects whose XY location is inside or on the group's
boundary (including concave groups). Crossing, touching nonadjacent, or overlapping
polygon edges are rejected; an invalid drop restores the previous boundaries
without saving. The backend validates the same rule on group creation and updates.

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

### Run Unit Tests with [Vitest](https://vitest.dev/)

```sh
npm run test:unit
```

### Run End-to-End Tests with [Playwright](https://playwright.dev)

```sh
# Install browsers for the first run
npx playwright install

# When testing on CI, must build the project first
npm run build

# Runs the end-to-end tests
npm run test:e2e
# Runs the tests only on Chromium
npm run test:e2e -- --project=chromium
# Runs the tests of a specific file
npm run test:e2e -- tests/example.spec.ts
# Runs the tests in debug mode
npm run test:e2e -- --debug
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```
