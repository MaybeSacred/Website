from influxdb_client_3 import (
  InfluxDBClient3, Point, WritePrecision,
  WriteOptions, write_client_options)
from influxdb_client_3.exceptions.exceptions import InfluxDBError
import pyarrow

# TODO: move to config file
_host = "http://192.168.1.230:8181" #os.getenv('INFLUX_HOST')
_token = "apiv3_WGmtNEnbETw8h2rNGT8G0XQUwW6JuJP3OKm__ASf9odOcyt3iv5mJjKtjMyFnB4HvJu0CFZMD6BEMWrjDyqxNA" #os.getenv('INFLUX_TOKEN')
_database = "home"#os.getenv('INFLUX_DATABASE')

POINT_DATA_TABLE = "point-data"
DEVICE_TABLE = "devices"
HOME_OBJECTS_TABLE = "home-objects"

# With batching mode, define callbacks to execute after a successful or
# failed write request.
# Callback methods receive the configuration and data sent in the request.
def success(self, data: str):
    print(f"Successfully wrote batch: data: {data}")

def error(self, data: str, exception: InfluxDBError):
    print(f"Failed writing batch: config: {self}, data: {data} due: {exception}")

def retry(self, data: str, exception: InfluxDBError):
    print(f"Failed retry writing batch: config: {self}, data: {data} retry: {exception}")

# Configure options for batch writing.
write_options = WriteOptions(batch_size=50,
                                    flush_interval=1_000,
                                    jitter_interval=500,
                                    retry_interval=5_000,
                                    max_retries=5,
                                    max_retry_delay=30_000,
                                    exponential_base=2)

# Create an options dict that sets callbacks and WriteOptions.
wco = write_client_options(success_callback=success,
                          error_callback=error,
                          retry_callback=retry,
                          write_options=write_options)

def write_points(points: list[Point]) -> None:
# Instantiate a synchronous instance of the client with your
# InfluxDB credentials and write options, such as Gzip threshold, default tags,
# and timestamp precision. Default precision is nanosecond ('ns').
    with InfluxDBClient3(host=_host,
                            token=_token,
                            database=_database,
                            write_client_options=wco) as client:
        client.write(points, write_precision='s')

async def query(string: str, **kwargs) -> pyarrow.Table:   
    with InfluxDBClient3(host=_host,
                            token=_token,
                            database=_database) as client:
        return await client.query_async(string, mode='all', query_parameters=kwargs)