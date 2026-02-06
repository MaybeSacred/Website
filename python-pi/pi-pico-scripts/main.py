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
import machine
from enum import IntEnum
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
WIFI_TIMEOUT = 10
WIFI_STATUS_CONNECTED = 3
HTTP_PORT = 80
HTTP_STATUS_OK = '200 OK'
HTTP_TIMEOUT_ZERO = -1

# Sensor I2C addresses
DHT20_I2C_ADDR = 0x38
SHT30_I2C_ADDR = 0x44

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
MAIN_LOOP_SLEEP_SECONDS = 5
SENSOR_DELAY_MS = 10_000 # 30 seconds
CPU_TEMP_BUFFER_SIZE = 2
WATER_DEPTH_BUFFER_SIZE = 9

# Processor temperature constants
CPU_TEMP_BASE = 27
CPU_TEMP_VOLTAGE_OFFSET = 0.706
CPU_TEMP_SLOPE = 0.001721

# Water depth ADC constants
ADC_MAX_VALUE = 2**16

class LOG_LEVEL(IntEnum):
    DEBUG = 1
    INFO = 2
    ERROR = 3

class NetworkConfig:
    def __init__(self, network_ssid: str = "", network_password: str = "",
                 ingestion_server_url: str = "192.168.1.193", ingestion_server_port: int = 8000):
        self.network_ssid = network_ssid
        self.network_password = network_password
        self.ingestion_server_url = ingestion_server_url
        self.ingestion_server_port = ingestion_server_port

class LoggingConfig:
    def __init__(self, enable_logging: bool = True, log_level: int = LOG_LEVEL.INFO):
        self.enable_logging = enable_logging
        self.log_level = log_level

class GeneralConfig:
    def __init__(self, heartbeat_interval: int = 300, 
                 measurement_interval: int = 30, data_write_interval: int = 60):
        self.heartbeat_interval = heartbeat_interval
        self.measurement_interval = measurement_interval
        self.data_write_interval = data_write_interval

class NetworkConfigDto:
    def __init__(self, network_ssid: str | None = None, network_password: str | None = None,
                 ingestion_server_url: str | None = None, ingestion_server_port: int | None = None):
        self.network_ssid = network_ssid
        self.network_password = network_password
        self.ingestion_server_url = ingestion_server_url
        self.ingestion_server_port = ingestion_server_port

class LoggingConfigDto:
    def __init__(self, enable_logging: bool | None = None, log_level: int | None = None):
        self.enable_logging = enable_logging
        self.log_level = log_level

class GeneralConfigDto:
    def __init__(self, heartbeat_interval: int | None = None, 
                 measurement_interval: int | None = None, data_write_interval: int | None = None,
                 distance_measurement_interval: int | None = None, temperature_interval: int | None = None):
        self.heartbeat_interval = heartbeat_interval
        self.measurement_interval = measurement_interval
        self.data_write_interval = data_write_interval
        self.distance_measurement_interval = distance_measurement_interval
        self.temperature_interval = temperature_interval

class ConfigurationDto:
    def __init__(self, general: GeneralConfigDto | None = None, 
                 network: NetworkConfigDto | None = None, 
                 logging: LoggingConfigDto | None = None):
        self.general = general
        self.network = network
        self.logging = logging

class Configuration:
    def __init__(self, version: str = "0.1.0",
                 general: GeneralConfig = GeneralConfig(), 
                 network: NetworkConfig = NetworkConfig(), 
                 logging: LoggingConfig = LoggingConfig()):
        self.version = version
        self.general = general
        self.network = network
        self.logging = logging

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
            print(f"Read '{val}' from {configuration_filename}")
            c = Configuration(**val)
            print(f"Loaded configuration: {json.dumps(val)}")
            return c
    except OSError as e:
        log(lambda: f"Error reading config file: {e}", LOG_LEVEL.ERROR)
        return Configuration()

def initialize_hardware(config: Configuration):
    global water_depth_adc, sensor_temp_adc, temp_hum_i2c_bus, distance_trigger_pin, distance_echo_pin
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

# TODO: configuration as JSON, constrain values from the sensors, log to error file

def log(f, level: LOG_LEVEL = LOG_LEVEL.INFO):
    if config.logging.enable_logging and level >= config.logging.log_level:
        cur_time = clock.datetime()
        print(f'{cur_time[0]}-{cur_time[1]:02}-{cur_time[2]:02}T{cur_time[4]:02}:{cur_time[5]:02}:{cur_time[6]:02}Z: {f()}')

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

# Init Wi-Fi Interface
def init_wifi(ssid, password):
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
        time.sleep(1)
    # Check if connection is successful
    if wlan.status() != 3:
        log(lambda: 'Failed to connect to Wi-Fi', LOG_LEVEL.ERROR)
        return False
    else:
        log(lambda: 'Connection successful!')
        network_info = wlan.ifconfig()
        ipAddress = network_info[0]
        log(lambda: f'IP address: {network_info[0]}')
        return True

def handle_json(writer: asyncio.StreamWriter, val) -> None:
    data = json.dumps(val)
    writer.write('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
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
    current_time = time.gmtime()
    timestamp = time.mktime(current_time)
    content = f"""{{
        "mac_address": "{mac}", 
        "case": "HEARTBEAT",
        "ip_address": "{ipAddress}",
        "source_date": "{timestamp}"
    }}"""
    await send_data_to_server('/data-ingestion/heartbeat', content)

def handle_request(writer: asyncio.StreamWriter, method: str, request: str, body: bytes) -> None:
    if request.startswith('/configuration'):
        if method == 'GET':
            return handle_json(writer, config)
        elif method == 'POST':
            val = json.loads(body)
            # Parse query parameters
            query_string = request.split('?')[1] if '?' in request else ''
            params = {}
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=')
                    try:
                        params[key] = int(value)
                    except ValueError:
                        pass
            
            # Update configuration
            if 'heartbeat' in params:
                config.general.heartbeat_interval = params['heartbeat']
            
            log(lambda: f'Configuration updated: heartbeat={config.general.heartbeat_interval}s')
            return handle_json(writer, config)
    elif request.startswith('/index') and method == 'GET':
        return handle_text(writer)
    # TODO: return 404 here

# Asynchronous function to handle client's requests
async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    global config
    
    request_line = await reader.readline()
    log(lambda: f'Request: {request_line}')
    
    # this doesn't do anything right now, presumably it's meant to later handle headers
    # Skip HTTP request headers
    while await reader.readline() != b"\r\n":
        pass
    
    request_exploded = str(request_line, 'utf-8').split()
    request_method = request_exploded[0]
    request = request_exploded[1]
    log(lambda: f'Request: {request_method}, {request}', LOG_LEVEL.DEBUG)

    body = await reader.readline()
    log(lambda: f'Body: {body}', LOG_LEVEL.DEBUG)
    
    # Process the request and update variables
    handle_request(writer, request_method, request, body)

    # Send the HTTP response and close the connection
    
    await writer.drain()
    await writer.wait_closed()
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
        log(lambda: f'Sent to: {path} {response}')
        
        writer.close()
        await writer.wait_closed()
    except Exception as e:
        log(lambda: f'Failed to send to: {path} {e} {content}', LOG_LEVEL.ERROR)

async def no_op():
    await asyncio.sleep(0)

async def read_sensors(delay_ms: int = SENSOR_DELAY_MS):
    global sensor_data
    try:
        await asyncio.gather(
            init_dht20(),
            init_sht30(),
        )
    except Exception as e:
        log(lambda: f'Error during sensor initialization: {e}', LOG_LEVEL.ERROR)
    while True:
        current_time = time.ticks_ms()
        try:
            [humidity_temp, 
             processor_temp, 
             #moisture_temp_humidity
             ] = await asyncio.gather(
                read_dht20(),
                # read_sht30(),
                read_processor(),
                # read_moisture_temp_humidity()
            )
            sensor_data = SensorData()
            log(lambda: f'Sensor readings obtained: {processor_temp}' )
            sensor_data.cpu_temperature = processor_temp[1]
            if humidity_temp is not None:
                sensor_data.humidity = humidity_temp[0]
                sensor_data.temperature = humidity_temp[1]
            # if moisture_temp_humidity is not None:
            #     sensor_data.moisture = moisture_temp_humidity[0]
            #     sensor_data.temperature = moisture_temp_humidity[1]
            #     sensor_data.humidity = moisture_temp_humidity[2]
        except Exception as e:
            log(lambda: f'Error reading sensors: {e}', LOG_LEVEL.ERROR)
        await asyncio.sleep_ms(delay_ms - (time.ticks_ms() - current_time))

async def init_sht30():
    await asyncio.sleep_ms(SENSOR_INITIALIZATION_DELAY_MS) 
    i2cs = temp_hum_i2c_bus.scan()
    log(lambda: f'I2C devices found: {[hex(device) for device in i2cs]}')

sht30_read_buffer = bytearray(6)
# https://cdn-shop.adafruit.com/product-files/5064/5064_Sensirion_Humidity_Sensors_SHT3x_Datasheet_digital.pdf
async def read_sht30():
    response = temp_hum_i2c_bus.writeto(SHT30_I2C_ADDR, SHT30_MEASUREMENT_CMD)  # Start measurement
    log(lambda: f'SHT30 write response: {response}', LOG_LEVEL.DEBUG)
    await asyncio.sleep_ms(SHT30_MEASUREMENT_TIME_MS)  # Wait for measurement to complete
    # TODO: there's a checksum byte we could verify here, also error handling
    temp_hum_i2c_bus.readfrom_into(SHT30_I2C_ADDR, sht30_read_buffer)  # Read 6 bytes of data
    # if data_bytes[0] != 0x18 or data_bytes[1:6] == b'\x00\x00\x00\x00\x00':
    #     print('DHT20 sensor returned invalid data')
    # else:
    temperature = SHT30_TEMP_FORMULA_A + SHT30_TEMP_FORMULA_B * ((sht30_read_buffer[0] << 8) | sht30_read_buffer[1]) / SHT30_SENSOR_RANGE
    humidity = SHT30_RH_SCALE * ((sht30_read_buffer[3] << 8) | sht30_read_buffer[4]) / SHT30_SENSOR_RANGE
    log(lambda: f'SHT30 Temperature: {temperature:.2f} C, Humidity: {humidity:.2f} %', LOG_LEVEL.DEBUG)
    return humidity, temperature

async def init_dht20():
    await asyncio.sleep_ms(SENSOR_INITIALIZATION_DELAY_MS) # docs say to wait 100ms before starting measurement
    #temp_hum_dht20.init()
    i2cs = temp_hum_i2c_bus.scan()
    log(lambda: f'I2C devices found: {[hex(device) for device in i2cs]}')
    response = temp_hum_i2c_bus.writeto(DHT20_I2C_ADDR, DHT20_INIT_CMD)
    log(lambda: f'DHT20 initialization response: {response}')

dht20_read_buffer = bytearray(7)
# https://cdn-shop.adafruit.com/product-files/5183/5193_DHT20.pdf
async def read_dht20():
    response = temp_hum_i2c_bus.writeto(DHT20_I2C_ADDR, DHT20_TRIGGER_CMD)  # Start measurement
    #print('DHT20 write response:', response)
    await asyncio.sleep_ms(DHT20_MEASUREMENT_TIME_MS)  # Wait for measurement to complete
    # TODO: there's a checksum byte we could verify here
    temp_hum_i2c_bus.readfrom_into(DHT20_I2C_ADDR, dht20_read_buffer)  # Read 7 bytes of data
    #print('DHT20 raw data:', data)
    if dht20_read_buffer[0] != DHT20_VALID_STATUS or dht20_read_buffer[1:6] == b'\x00\x00\x00\x00\x00':
        log(lambda: 'DHT20 sensor returned invalid data', LOG_LEVEL.ERROR)
    else:
        humidity = ((dht20_read_buffer[1] << 12) | (dht20_read_buffer[2] << 4) | (dht20_read_buffer[3] >> 4)) * DHT20_HUMIDITY_SCALE
        temperature = ((((dht20_read_buffer[3] & 0x0F) << 16) | (dht20_read_buffer[4] << 8) | dht20_read_buffer[5]) * DHT20_TEMPERATURE_SCALE) + DHT20_TEMPERATURE_OFFSET
        log(lambda: f'DHT20 Temperature: {temperature:.2f} C, Humidity: {humidity:.2f} %', LOG_LEVEL.DEBUG)
        return humidity, temperature

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
    #         0

    #     pulse_start = time.ticks_us()

    #     while distance_echo.value() == 1:
    #         0

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

async def read_moisture_temp_humidity():
    if moisture_temp_humidity_uart.write('j') != 0:
        val = moisture_temp_humidity_uart.readline()
        if val is not None:
            json_val = json.loads(val)
            temperature = json_val.get('temp', 0.0)
            humidity = json_val.get('humidity', 0.0)
            moisture = json_val.get('wetness', 0.0)
            log(lambda: f'Moisture/Temp/Humidity raw data: {json_val}', LOG_LEVEL.DEBUG)
            return moisture, temperature, humidity

async def main():
    global config
    # Load configuration
    config = load_configuration()
    initialize_hardware(config)
    if not init_wifi(config.network.network_ssid, config.network.network_password):
        log(lambda: 'Exiting program.')
        return
    # Start the server and run the event loop
    log(lambda: 'Setting up server')
    server = asyncio.start_server(handle_client, "0.0.0.0", 80)
    log(lambda: f'Server running on http://{ipAddress}:80')
    log(lambda: 'Starting background tasks')
    asyncio.create_task(server)
    log(lambda: 'Starting measurement tasks')
    asyncio.create_task(read_sensors(config.general.measurement_interval * 1000))

    log(lambda: 'Entering main loop')
    i = 0
    while True:
        # Add other tasks that you might need to do in the loop
        if i % (config.general.measurement_interval / MAIN_LOOP_SLEEP_SECONDS) == 0:
            await send_measurement(sensor_data)
        if i % (config.general.heartbeat_interval / MAIN_LOOP_SLEEP_SECONDS) == 0:
            await send_heartbeat()
        await asyncio.sleep(MAIN_LOOP_SLEEP_SECONDS)
        i += 1
        

# Create an Event Loop
loop = asyncio.get_event_loop()
# Create a task to run the main function
loop.create_task(main())

try:
    # Run the event loop indefinitely
    loop.run_forever()
except Exception as e:
    log(lambda: f'Error occurred: {e}', LOG_LEVEL.ERROR)
except KeyboardInterrupt:
    log(lambda: 'Program Interrupted by the user', LOG_LEVEL.INFO)