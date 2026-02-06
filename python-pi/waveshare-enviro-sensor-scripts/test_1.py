#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
import ICM20948 #Gyroscope/Acceleration/Magnetometer
import MPU925x #Gyroscope/Acceleration/Magnetometer
import BME280   #Atmospheric Pressure/Temperature and humidity
import LTR390   #UV
import TSL2591  #LIGHT
import SGP40
import requests
from PIL import Image,ImageDraw,ImageFont
import math
import smbus

MPU_VAL_WIA = 0x71
MPU_ADD_WIA = 0x75
ICM_VAL_WIA = 0xEA
ICM_ADD_WIA = 0x00
ICM_SLAVE_ADDRESS = 0x68
bus = smbus.SMBus(1)

bme280 = BME280.BME280()
bme280.get_calib_param()
light = TSL2591.TSL2591()
uv = LTR390.LTR390()
sgp = SGP40.SGP40()

device_id1 = bus.read_byte_data(int(ICM_SLAVE_ADDRESS), int(ICM_ADD_WIA))
device_id2 = bus.read_byte_data(int(ICM_SLAVE_ADDRESS), int(MPU_ADD_WIA))
if device_id1 == ICM_VAL_WIA:
    mpu = ICM20948.ICM20948()
    print("ICM20948 9-DOF I2C address:0X68")
elif device_id2 == MPU_VAL_WIA:
    mpu = MPU925x.MPU925x()
    print("MPU925x 9-DOF I2C address:0X68")

print("TSL2591 Light I2C address:0X29")
print("LTR390 UV I2C address:0X53")
print("SGP40 VOC I2C address:0X59")
print("bme280 T&H I2C address:0X76")

try:
    while True:
        time.sleep(1)
        bme = []
        bme = bme280.readData()
        pressure = round(bme[0], 2) 
        temp = round(bme[1], 2) 
        hum = round(bme[2], 2)
        
        lux = round(light.Lux(), 2)
        
        UVS = uv.UVS()
        
        gas = round(sgp.raw(), 2)
        
        # icm = []
        # icm = mpu.getdata()
        
        print("==================================================")
        print("pressure : %7.2f hPa" %pressure)
        print("temp : %-6.2f ℃" %temp)
        print("hum : %6.2f ％" %hum)
        print("lux : %d " %lux)
        print("uv : %d " %UVS)
        print("gas : %6.2f " %gas)
        # print("Roll = %.2f , Pitch = %.2f , Yaw = %.2f" %(icm[0],icm[1],icm[2]))
        # print("Acceleration: X = %d, Y = %d, Z = %d" %(icm[3],icm[4],icm[5]))
        # print("Gyroscope:     X = %d , Y = %d , Z = %d" %(icm[6],icm[7],icm[8]))
        # print("Magnetic:      X = %d , Y = %d , Z = %d" %(icm[9],icm[10],icm[11]))
        print("Sending to API")
        r = requests.post('http://192.168.1.193:8000/data-ingestion/', json = {
            "temperature": temp,
            "humidity": hum,
            "pressure": pressure,
            "uv": UVS,
            "gas": gas,
            "lux": lux})
        print(r.json())

except KeyboardInterrupt:
    exit()



