# Rui Santos & Sara Santos - Random Nerd Tutorials
# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-pico-w-asynchronous-web-server-micropython/

# Import necessary modules
import network
import asyncio
import socket
import ubinascii
import time
import json
import random
from machine import Pin, I2C, RTC, UART
import struct
import machine

VERSION = "0.1.3"

# constants
conversion_factor = const(3.3 / 65535)
speed_of_sound = const(343.26 / 10_000)  # in m/s

# Hardware pin constants
I2C_BUS_ID = 1
I2C_SCL_PIN = 19
I2C_SDA_PIN = 18
WATER_DEPTH_ADC_PIN = 2
VOLTAGE_PIN = 3
SENSOR_TEMP_ADC_PIN = 4
DISTANCE_TRIGGER_PIN = 17
DISTANCE_ECHO_PIN = 16

# Network constants
WIFI_TIMEOUT = 30
WIFI_STATUS_CONNECTED = 3
HTTP_PORT = 80
HTTP_STATUS_OK = '200 OK'
HTTP_TIMEOUT_ZERO = -1

# Sensor I2C addresses
STEMMA_MOISTURE_I2C_ADDR = 0x36
DHT20_I2C_ADDR = 0x38
SHT30_I2C_ADDR = 0x44

STEMMA_MOISTURE_CMD = b'\x0F\x10'

# DHT20 constants
DHT20_TRIGGER_CMD = b'\xAC\x33\x00'
DHT20_INIT_CMD = b'\x71\x00'
DHT20_MEASUREMENT_TIME_MS = 80
DHT20_HUMIDITY_SCALE = 100 / (2**20)
DHT20_TEMPERATURE_OFFSET = -50
DHT20_TEMPERATURE_SCALE = 200 / (2**20)
DHT20_BUFFER_SIZE = 7
DHT20_VALID_STATUS = 0x18

# SHT30 constants
SHT30_MEASUREMENT_CMD = b'\x24\x00'
SHT30_MEASUREMENT_TIME_MS = 15
SHT30_BUFFER_SIZE = 6
SHT30_TEMP_FORMULA_A = -45
SHT30_TEMP_FORMULA_B = 175
SHT30_RH_SCALE = 100
SHT30_SENSOR_RANGE = 2**16 - 1

# Timing constants
SENSOR_INITIALIZATION_DELAY_MS = 100
MAIN_LOOP_SLEEP_SECONDS = 10
MAIN_LOOP_SLEEP_MILLISECONDS = MAIN_LOOP_SLEEP_SECONDS * 1000
CPU_TEMP_BUFFER_SIZE = 2
WATER_DEPTH_BUFFER_SIZE = 9

# Processor temperature constants
CPU_TEMP_BASE = 27
CPU_TEMP_VOLTAGE_OFFSET = 0.706
CPU_TEMP_SLOPE = 0.001721

# Water depth ADC constants
ADC_MAX_VALUE = 2**16

# can't do enums in this type of python
DEBUG = 1
INFO = 2
ERROR = 3

def validate_range(value: float | None, min_value: float, max_value: float) -> float | None:
    if value is not None and value >= min_value and value <= max_value:
        return value
    else:
        return None
    
def validate_range_int(value: int | None, min_value: int, max_value: int) -> int | None:
    if value is not None and value >= min_value and value <= max_value:
        return value
    else:
        return None

def log_level_to_string(level: int) -> str:
    if level == DEBUG:
        return 'DEBUG'
    elif level == INFO:
        return 'INFO'
    elif level == ERROR:
        return 'ERROR'
    else:
        return 'UNKNOWN'

class NetworkConfig:
    def __init__(self, network_ssid: str = "", network_password: str = "",
                 ingestion_server_url: str = "192.168.1.193", ingestion_server_port: int = 8000):
        self.network_ssid = network_ssid
        self.network_password = network_password
        self.ingestion_server_url = ingestion_server_url
        self.ingestion_server_port = ingestion_server_port

class LoggingConfig:
    def __init__(self, enable_logging: bool = True, log_level: int = INFO):
        self.enable_logging = enable_logging
        self.log_level = log_level

class GeneralConfig:
    def __init__(self, heartbeat_interval: int = 300, 
                 measurement_interval: int = 30, data_write_interval: int = 60,
                 enable_dht20_sensor: bool = False, enable_sht30_sensor: bool = False,
                 enable_stemma_moisture_sensor: bool = False, enable_moisture_temp_humidity: bool = False):
        self.heartbeat_interval = heartbeat_interval
        self.measurement_interval = measurement_interval
        self.data_write_interval = data_write_interval
        self.enable_dht20_sensor = enable_dht20_sensor
        self.enable_sht30_sensor = enable_sht30_sensor
        self.enable_stemma_moisture_sensor = enable_stemma_moisture_sensor
        self.enable_moisture_temp_humidity = enable_moisture_temp_humidity

class NetworkConfigDto:
    def __init__(self, network_ssid: str | None = None,
                 ingestion_server_url: str | None = None, ingestion_server_port: int | None = None):
        self.network_ssid = network_ssid
        self.ingestion_server_url = ingestion_server_url
        self.ingestion_server_port = ingestion_server_port

class LoggingConfigDto:
    def __init__(self, enable_logging: bool | None = None, log_level: int | None = None):
        self.enable_logging = enable_logging
        self.log_level = log_level

class GeneralConfigDto:
    def __init__(self, heartbeat_interval: int | None = None, 
                 measurement_interval: int | None = None, data_write_interval: int | None = None,
                 distance_measurement_interval: int | None = None, temperature_interval: int | None = None,
                 enable_dht20_sensor: bool | None = None, enable_sht30_sensor: bool | None = None,
                 enable_stemma_moisture_sensor: bool | None = None, enable_moisture_temp_humidity: bool | None = None):
        self.heartbeat_interval = heartbeat_interval
        self.measurement_interval = measurement_interval
        self.data_write_interval = data_write_interval
        self.distance_measurement_interval = distance_measurement_interval
        self.temperature_interval = temperature_interval
        self.enable_dht20_sensor = enable_dht20_sensor
        self.enable_sht30_sensor = enable_sht30_sensor
        self.enable_stemma_moisture_sensor = enable_stemma_moisture_sensor
        self.enable_moisture_temp_humidity = enable_moisture_temp_humidity

class ConfigurationDto:
    def __init__(self, general: GeneralConfigDto | None = None, 
                 network: NetworkConfigDto | None = None, 
                 logging: LoggingConfigDto | None = None):
        self.general = general
        self.network = network
        self.logging = logging

class Configuration:
    def __init__(self,
                 general: GeneralConfig = GeneralConfig(), 
                 network: NetworkConfig = NetworkConfig(), 
                 logging: LoggingConfig = LoggingConfig()):
        self.version = VERSION
        self.general = general
        self.network = network
        self.logging = logging

    def to_dict(self):
        return {
            "version": self.version,
            "general": self.general.__dict__,
            "network": self.network.__dict__,
            "logging": self.logging.__dict__
        }

configuration_filename = 'config.json'
log_file = 'pico_log.txt'
# globals
mac: str = ''
ipAddress: str = ''
config = Configuration()

# TODO: figure out how to make this more functional, add handling of bad values, 
# set up other capacitive sensor, set date from server responses
class SensorData:
    cpu_temperature: float | None = None
    humidity: float | None = None
    temperature: float | None = None
    moisture: float | None = None
    distance: float | None = None
    water_depth: int | None = None

sensor_data = SensorData()

def load_configuration():
    try:
        with open(configuration_filename, "r") as f:
            val = json.loads(f.read())
            log(lambda: f"Read '{val}' from {configuration_filename}", DEBUG)
            c = Configuration(GeneralConfig(**val.get("general", {})), NetworkConfig(**val.get("network", {})), LoggingConfig(**val.get("logging", {})))
            log(lambda: f"Loaded configuration: {json.dumps(c.to_dict())}", INFO)
            return c
    except OSError as e:
        log(lambda: f"Error reading config file: {e}", ERROR)
        return Configuration()
    
def write_configuration(config: Configuration):
    try:
        with open(configuration_filename, "w") as f:
            f.write(json.dumps(config.to_dict()))
    except OSError as e:
        log(lambda: f"Error reading config file: {e}", ERROR)

def write_log_file(log_data: str):
    try:
        with open(log_file, "a") as f:
            f.write(log_data + "\r\n")
    except OSError as e:
        print(f"Error reading config file: {e}")

def update_configuration_from_dto(config: Configuration, dto: ConfigurationDto) -> Configuration:
    """Generate new configuration from DTO, using current values if not present in DTO"""
    # General config
    general = GeneralConfig(
        heartbeat_interval=dto.general.heartbeat_interval if dto.general and dto.general.heartbeat_interval is not None else config.general.heartbeat_interval,
        measurement_interval=dto.general.measurement_interval if dto.general and dto.general.measurement_interval is not None else config.general.measurement_interval,
        data_write_interval=dto.general.data_write_interval if dto.general and dto.general.data_write_interval is not None else config.general.data_write_interval,
        enable_dht20_sensor=dto.general.enable_dht20_sensor if dto.general and dto.general.enable_dht20_sensor is not None else config.general.enable_dht20_sensor,
        enable_sht30_sensor=dto.general.enable_sht30_sensor if dto.general and dto.general.enable_sht30_sensor is not None else config.general.enable_sht30_sensor,
        enable_stemma_moisture_sensor=dto.general.enable_stemma_moisture_sensor if dto.general and dto.general.enable_stemma_moisture_sensor is not None else config.general.enable_stemma_moisture_sensor,
        enable_moisture_temp_humidity=dto.general.enable_moisture_temp_humidity if dto.general and dto.general.enable_moisture_temp_humidity is not None else config.general.enable_moisture_temp_humidity
    )
    
    # Network config
    network = NetworkConfig(
        network_ssid=dto.network.network_ssid if dto.network and dto.network.network_ssid is not None else config.network.network_ssid,
        network_password=config.network.network_password,
        ingestion_server_url=dto.network.ingestion_server_url if dto.network and dto.network.ingestion_server_url is not None else config.network.ingestion_server_url,
        ingestion_server_port=dto.network.ingestion_server_port if dto.network and dto.network.ingestion_server_port is not None else config.network.ingestion_server_port
    )
    
    # Logging config
    logging = LoggingConfig(
        enable_logging=dto.logging.enable_logging if dto.logging and dto.logging.enable_logging is not None else config.logging.enable_logging,
        log_level=dto.logging.log_level if dto.logging and dto.logging.log_level is not None else config.logging.log_level
    )
    
    return Configuration(general=general, network=network, logging=logging)

# TODO: I probably do want to allow configuring the pins based on the configuration data, to allow for different sensors in different positions
def initialize_hardware():
    global water_depth_adc, sensor_temp_adc, temp_hum_i2c_bus, distance_trigger_pin
    global distance_echo_pin
    global led_control_pin, moisture_temp_humidity_uart, voltage_adc
    water_depth_adc = machine.ADC(WATER_DEPTH_ADC_PIN)
    voltage_adc = machine.ADC(VOLTAGE_PIN)
    sensor_temp_adc = machine.ADC(SENSOR_TEMP_ADC_PIN)
    moisture_temp_humidity_uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1), timeout=400)
    temp_hum_i2c_bus = I2C(I2C_BUS_ID, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN))
    distance_trigger_pin = Pin(DISTANCE_TRIGGER_PIN, Pin.OUT)
    distance_echo_pin = Pin(DISTANCE_ECHO_PIN, Pin.IN)
    led_control_pin = Pin("LED", Pin.OUT)

clock = RTC()
format_string = "%Y-%m-%d %H:%M:%S"

# TODO: constrain values from the sensors, log to error file

def log(f, level = INFO, error: Exception | None = None):
    if config.logging.enable_logging and level >= config.logging.log_level:
        cur_time = clock.datetime()
        formatted = f'{cur_time[0]}-{cur_time[1]:02}-{cur_time[2]:02}T{cur_time[4]:02}:{cur_time[5]:02}:{cur_time[6]:02}Z: {log_level_to_string(level)} {f()}{"\r\n" + str(error) if error else ""}'
        print(formatted)
        if config.logging.log_level == ERROR:
            write_log_file(formatted)

# HTML template for the webpage
def webpage():
    global config
    html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pico Web Server</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
            <h1>Raspberry Pi Pico Web Server</h1>
            <h2>Configuration</h2>
            <form action="./config" method="get">
                <label>Heartbeat Interval (seconds): </label>
                <input type="number" name="heartbeat" value="{config.general.heartbeat_interval}" />
                <br><br>
                <input type="submit" value="Update Configuration" />
            </form>
        </body>
        </html>
        """
    return str(html)

async def blink_led():
    led_control_pin.on()
    await asyncio.sleep(0.2)
    led_control_pin.off()

async def sleep_ms(val: int):
    await asyncio.sleep_ms(val)

# Init Wi-Fi Interface
async def init_wifi(ssid, password):
    global mac, ipAddress
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # Connect to your network
    wlan.connect(ssid, password)
    mac = ubinascii.hexlify(wlan.config('mac'),':').decode()
    # Wait for Wi-Fi connection
    connection_timeout = WIFI_TIMEOUT
    while connection_timeout > 0:
        log(lambda: str(wlan.status()))
        if wlan.status() >= WIFI_STATUS_CONNECTED:
            break
        connection_timeout -= 1
        log(lambda: 'Waiting for Wi-Fi connection...')
        await asyncio.gather(blink_led(),
                             sleep_ms(1000))
    # Check if connection is successful
    if wlan.status() != 3:
        log(lambda: 'Failed to connect to Wi-Fi', ERROR)
        return False
    else:
        log(lambda: 'Connection successful!')
        network_info = wlan.ifconfig()
        ipAddress = network_info[0]
        log(lambda: f'IP address: {network_info[0]}')
        return True

def handle_json(writer: asyncio.StreamWriter, val, status_code: int = 200) -> None:
    data = json.dumps(val)
    writer.write(f'HTTP/1.0 {status_code} OK\r\nContent-type: application/json\r\n\r\n')
    writer.write(data)

def handle_text(writer: asyncio.StreamWriter) -> None:
    # Generate HTML response
    response = webpage()  
    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(response)

async def send_measurement(data: SensorData):
    current_time = time.gmtime()
    timestamp = time.mktime(current_time)
    content = f"""{{
        "mac_address": "{mac}", 
        "case": "ENVIRONMENT_SENSOR",
        "cpu_temperature": {data.cpu_temperature if data.cpu_temperature is not None else 'null'},
        "temperature": {data.temperature if data.temperature is not None else 'null'},
        "humidity": {data.humidity if data.humidity is not None else 'null'},
        "moisture_percent": {data.moisture if data.moisture is not None else 'null'},
        "distance": {data.distance if data.distance is not None else 'null'},
        "water_depth_raw": {int(data.water_depth) if data.water_depth is not None else 'null'},
        "source_date": "{timestamp}"
    }}"""
    await send_data_to_server('/data-ingestion/environment-sensor', content)

async def send_heartbeat():
    task =  asyncio.create_task(blink_led())
    current_time = time.gmtime()
    timestamp = time.mktime(current_time)
    content = f"""{{
        "mac_address": "{mac}", 
        "case": "HEARTBEAT",
        "ip_address": "{ipAddress}",
        "source_date": "{timestamp}"
    }}"""
    await asyncio.gather(task, send_data_to_server('/data-ingestion/heartbeat', content))

async def handle_request(writer: asyncio.StreamWriter, method: str, request: str, body: bytes) -> None:
    global config
    try:
        if request.startswith('/configuration'):
            if method == 'GET':
                log(lambda: 'Configuration requested', DEBUG)
                return handle_json(writer, config.to_dict())
            elif method == 'POST':
                val = json.loads(body)
                config_dto = ConfigurationDto(general= GeneralConfigDto(**val.get("general", {})),
                                              network= NetworkConfigDto(**val.get("network", {})),
                                              logging= LoggingConfigDto(**val.get("logging", {})))
                log(lambda: f'Config dto: {json.dumps(config_dto.__dict__)}', DEBUG)
                new_config = update_configuration_from_dto(config, config_dto)
                write_configuration(new_config)
                config = new_config
                log(lambda: f'Configuration updated: {json.dumps(config.to_dict())}', DEBUG)
                return handle_json(writer, config.to_dict())
        elif request.startswith('/measurement') and method == 'GET':
            log(lambda: 'Measurement requested', DEBUG)
            sensor_data = await read_sensors()
            if sensor_data is not None:
                return handle_json(writer, sensor_data.__dict__)
            else:
                return handle_json(writer, {"error": "Failed to read sensors"}, status_code=500)
        elif request.startswith('/index') and method == 'GET':
            return handle_text(writer)
        log(lambda: 'No matching route found', DEBUG)
        return handle_json(writer, {"error": "Not found"}, status_code=404)
    except Exception as e:
        log(lambda: f'Error handling request: {e}', ERROR)
        return handle_json(writer, {"error": "Internal server error", "message": str(e)}, status_code=500)

# Asynchronous function to handle client's requests
async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    global config
    task = asyncio.create_task(blink_led())
    request_line = await reader.readline()
    log(lambda: f'Request: {request_line}')
    
    # this doesn't do anything right now, presumably it's meant to later handle headers
    # Skip HTTP request headers
    line = b''
    while line != b"\r\n":
        line = await reader.readline()
        log(lambda: f'Line: {line}')
    
    request_exploded = str(request_line, 'utf-8').split()
    request_method = request_exploded[0]
    request = request_exploded[1]
    log(lambda: f'Request: {request_method}, {request}', INFO)

    body = await reader.read(2048)
    log(lambda: f'Body: {body}', INFO)
    
    # Process the request and update variables
    await handle_request(writer, request_method, request, body)

    # Send the HTTP response and close the connection
    
    await writer.drain()
    await writer.wait_closed()
    await task
    log(lambda: 'Client Disconnected')

async def send_data_to_server(path:str, content: str):
    try:
        reader, writer = await asyncio.open_connection(config.network.ingestion_server_url, config.network.ingestion_server_port)
        # Send HTTP POST request
        request = f"POST {path} HTTP/1.1\r\nHost: {config.network.ingestion_server_url}\r\nContent-Type: application/json\r\nContent-Length: {len(content)}\r\n\r\n{content}"
        writer.write(request.encode())
        await writer.drain()
        # Read response
        response = await reader.read(-1)
        log(lambda: f'Sent to: {path} {response}', DEBUG)
        
        writer.close()
        await writer.wait_closed()
    except Exception as e:
        log(lambda: f'Failed to send to: {path} {e} {content}', ERROR)

async def no_op():
    await asyncio.sleep(0)

async def initialize_sensors():
    try:
        await asyncio.gather(
            init_dht20(),
            init_sht30(),
        )
    except Exception as e:
        log(lambda: f'Error during sensor initialization: {e}', ERROR)

async def read_sensors():
    try:
        [dht20_humidity_temp, 
            sht30_humidity_temp,
            processor_temp, 
            moisture,
            moisture_temp_humidity
        ] = await asyncio.gather(
            read_dht20(),
            read_sht30(),
            read_processor(),
            read_stemma_moisture_sensor(),
            read_monk_makes_plant_monitor()
        )
        sensor_data = SensorData()
        sensor_data.cpu_temperature = processor_temp
        if dht20_humidity_temp is not None:
            sensor_data.humidity = dht20_humidity_temp[0]
            sensor_data.temperature = dht20_humidity_temp[1]
        if sht30_humidity_temp is not None:
            sensor_data.humidity = sht30_humidity_temp[0]
            sensor_data.temperature = sht30_humidity_temp[1]
        if moisture is not None:
            sensor_data.moisture = moisture
        if moisture_temp_humidity is not None:
            sensor_data.moisture = moisture_temp_humidity[0]
            sensor_data.temperature = moisture_temp_humidity[1]
            sensor_data.humidity = moisture_temp_humidity[2]
        log(lambda: f'Sensor readings obtained: {sensor_data.__dict__}')
        return sensor_data
    except Exception as e:
        log(lambda: 'Error reading sensors', ERROR, e)

async def init_sht30():
    if config.general.enable_sht30_sensor:
        await asyncio.sleep_ms(SENSOR_INITIALIZATION_DELAY_MS) 
        i2cs = temp_hum_i2c_bus.scan()
        log(lambda: f'I2C devices found: {[hex(device) for device in i2cs]}')

sht30_read_buffer = bytearray(6)
# https://cdn-shop.adafruit.com/product-files/5064/5064_Sensirion_Humidity_Sensors_SHT3x_Datasheet_digital.pdf
async def read_sht30():
    if not config.general.enable_sht30_sensor:
        return None
    response = temp_hum_i2c_bus.writeto(SHT30_I2C_ADDR, SHT30_MEASUREMENT_CMD)  # Start measurement
    log(lambda: f'SHT30 write response: {response}', DEBUG)
    await asyncio.sleep_ms(SHT30_MEASUREMENT_TIME_MS)  # Wait for measurement to complete
    # TODO: there's a checksum byte we could verify here, also error handling
    temp_hum_i2c_bus.readfrom_into(SHT30_I2C_ADDR, sht30_read_buffer)  # Read 6 bytes of data
    # if data_bytes[0] != 0x18 or data_bytes[1:6] == b'\x00\x00\x00\x00\x00':
    #     print('DHT20 sensor returned invalid data')
    # else:
    temperature = validate_range(SHT30_TEMP_FORMULA_A + SHT30_TEMP_FORMULA_B * ((sht30_read_buffer[0] << 8) | sht30_read_buffer[1]) / SHT30_SENSOR_RANGE, -40, 125)
    humidity = validate_range(SHT30_RH_SCALE * ((sht30_read_buffer[3] << 8) | sht30_read_buffer[4]) / SHT30_SENSOR_RANGE, 0, 100)
    log(lambda: f'SHT30 Temperature: {temperature:.2f} C, Humidity: {humidity:.2f} %', DEBUG)
    if humidity is not None and temperature is not None:
        return humidity, temperature

async def init_dht20():
    if config.general.enable_dht20_sensor:
        await asyncio.sleep_ms(SENSOR_INITIALIZATION_DELAY_MS) # docs say to wait 100ms before starting measurement
        #temp_hum_dht20.init()
        i2cs = temp_hum_i2c_bus.scan()
        log(lambda: f'I2C devices found: {[hex(device) for device in i2cs]}')
        response = temp_hum_i2c_bus.writeto(DHT20_I2C_ADDR, DHT20_INIT_CMD)
        log(lambda: f'DHT20 initialization response: {response}')

dht20_read_buffer = bytearray(7)
# https://cdn-shop.adafruit.com/product-files/5183/5193_DHT20.pdf
async def read_dht20():
    if not config.general.enable_dht20_sensor:
        return None
    response = temp_hum_i2c_bus.writeto(DHT20_I2C_ADDR, DHT20_TRIGGER_CMD)  # Start measurement
    #print('DHT20 write response:', response)
    await asyncio.sleep_ms(DHT20_MEASUREMENT_TIME_MS)  # Wait for measurement to complete
    # TODO: there's a checksum byte we could verify here
    temp_hum_i2c_bus.readfrom_into(DHT20_I2C_ADDR, dht20_read_buffer)  # Read 7 bytes of data
    #print('DHT20 raw data:', data)
    if dht20_read_buffer[0] != DHT20_VALID_STATUS or dht20_read_buffer[1:6] == b'\x00\x00\x00\x00\x00':
        log(lambda: 'DHT20 sensor returned invalid data', ERROR)
    else:
        humidity = validate_range(((dht20_read_buffer[1] << 12) | (dht20_read_buffer[2] << 4) | (dht20_read_buffer[3] >> 4)) * DHT20_HUMIDITY_SCALE, 0, 100)
        temperature = validate_range(((((dht20_read_buffer[3] & 0x0F) << 16) | (dht20_read_buffer[4] << 8) | dht20_read_buffer[5]) * DHT20_TEMPERATURE_SCALE) + DHT20_TEMPERATURE_OFFSET, -40, 80)
        log(lambda: f'DHT20 Temperature: {temperature:.2f} C, Humidity: {humidity:.2f} %', DEBUG)
        if humidity is not None and temperature is not None:
            return humidity, temperature

stemma_moisture_read_buffer = bytearray(2)
# https://learn.adafruit.com/adafruit-stemma-soil-sensor-i2c-capacitive-moisture-sensor
async def read_stemma_moisture_sensor():
    if not config.general.enable_stemma_moisture_sensor:
        return None
    response = temp_hum_i2c_bus.writeto(STEMMA_MOISTURE_I2C_ADDR, STEMMA_MOISTURE_CMD)  # Start measurement
    await asyncio.sleep_ms(8)  # Wait for measurement to complete
    # TODO: there's a checksum byte we could verify here
    temp_hum_i2c_bus.readfrom_into(STEMMA_MOISTURE_I2C_ADDR, stemma_moisture_read_buffer)  # Read 7 bytes of data
    val = validate_range_int(struct.unpack(">H", stemma_moisture_read_buffer)[0], 0, 4095)
    if val is None:
        log(lambda: 'Moisture sensor returned invalid data', ERROR)
    else:
        return val
    
# TODO: add error handling
async def measure_distance():
    pass
    # while True:
    #     distance_trigger.value(0)
    #     await asyncio.sleep_ms(1)
    #     distance_trigger.value(1)
    #     time.sleep_us(10)
    #     distance_trigger.value(0)

    #     while distance_echo.value() == 0:
    #         pass

    #     pulse_start = time.ticks_us()

    #     while distance_echo.value() == 1:
    #         pass

    #     pulse_end = time.ticks_us()

    #     pulse_duration = time.ticks_diff(pulse_end, pulse_start)
    #     #print('Pulse duration:', pulse_duration, pulse_start, pulse_end)
    #     distance = (pulse_duration * speed_of_sound) / 2  # in cm
    #     #print('Distance:', distance)
    #     await asyncio.sleep(1)

async def read_processor():
    #v_voltage = voltage_adc.read_u16()
    temp = sensor_temp_adc.read_u16()
    voltage = temp * conversion_factor
    # Formula from datasheet for chip temp
    return CPU_TEMP_BASE - (voltage - CPU_TEMP_VOLTAGE_OFFSET) / CPU_TEMP_SLOPE

async def read_water_depth_sensor():
    return water_depth_adc.read_u16()

# https://cdn-shop.adafruit.com/product-files/5587/datasheet_plant_monitor.pdf
async def read_monk_makes_plant_monitor():
    if not config.general.enable_moisture_temp_humidity:
        return None
    if moisture_temp_humidity_uart.write('j') != 0:
        val = moisture_temp_humidity_uart.readline()
        if val is not None:
            json_val = json.loads(val)
            temperature: float | None = validate_range(json_val.get('temp', None), -10, 60)
            humidity: float | None = validate_range(json_val.get('humidity', None), 0, 100)
            moisture: float | None = validate_range(json_val.get('wetness', None), 0, 100)
            log(lambda: f'Moisture/Temp/Humidity raw data: {json_val}', DEBUG)
            if temperature is not None and humidity is not None and moisture is not None:
                return moisture, temperature, humidity

async def make_measurement():
    global sensor_data
    task = asyncio.create_task(blink_led())
    sensor_data = await read_sensors()
    if sensor_data is not None:
        await send_measurement(sensor_data)
    await task

async def main():
    global config
    # Load configuration
    config = load_configuration()
    initialize_hardware()
    if not await init_wifi(config.network.network_ssid, config.network.network_password):
        log(lambda: 'Exiting program.')
        while True:
            led_control_pin.on()
            await asyncio.sleep(.5)
            led_control_pin.off()
            await asyncio.sleep(.5)
        return
    # Start the server and run the event loop
    log(lambda: 'Setting up server')
    server = asyncio.start_server(handle_client, "0.0.0.0", 80)
    log(lambda: f'Server running on http://{ipAddress}:80')
    log(lambda: 'Starting background tasks')
    asyncio.create_task(server)
    #log(lambda: 'Starting measurement tasks')
    #asyncio.create_task(read_sensors(config.general.measurement_interval * 1000))

    log(lambda: 'Entering main loop')
    i = 0
    while True:
        current_time = time.ticks_ms()
        # Add other tasks that you might need to do in the loop
        if i % (config.general.measurement_interval / MAIN_LOOP_SLEEP_SECONDS) == 0:
            await make_measurement()
        if i % (config.general.heartbeat_interval / MAIN_LOOP_SLEEP_SECONDS) == 0:
            await send_heartbeat()
        await asyncio.sleep_ms(MAIN_LOOP_SLEEP_MILLISECONDS - min(MAIN_LOOP_SLEEP_MILLISECONDS, time.ticks_diff(time.ticks_ms(), current_time)))
        i += 1

# Create an Event Loop
loop = asyncio.get_event_loop()
# Create a task to run the main function
loop.create_task(main())

try:
    # Run the event loop indefinitely
    loop.run_forever()
except Exception as e:
    log(lambda: f'Error occurred: {e}', ERROR)
except KeyboardInterrupt:
    log(lambda: 'Program Interrupted by the user', INFO)