$sourceFolder = "../waveshare-enviro-sensor-scripts/"
ssh jon@jon-zero-2-w-0 "pkill python"
scp $sourceFolder/test_1.py jon@jon-zero-2-w-0:~/Documents/source/Environment_Sensor_HAT_Code/Environment_Sensor_HAT_Code/python/
ssh jon@jon-zero-2-w-0 "nohup python3 ~/Documents/source/Environment_Sensor_HAT_Code/Environment_Sensor_HAT_Code/python/test_1.py &"