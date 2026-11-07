import os
import asyncio
#from machine import Pin, I2C, RTC, UART
from gpiozero import LED
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import MethodResponse
RELAY_PIN = 18

relay_pin = LED(RELAY_PIN)

async def main():
    # Fetch the connection string from an environment variable
    conn_str = os.getenv("IOT_HUB_CONNECTION_STRING")
    # Create instance of the device client using the authentication provider
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # Connect the device client.
    await device_client.connect()

    # define behavior for receiving a message
    # NOTE: this could be a function or a coroutine
    def message_received_handler(message):
        print("the data in the message received was ")
        print(message.data)
        print("custom properties are")
        print(message.custom_properties)
        print("")
        print("content Type: {0}".format(message.content_type))
        if relay_pin.value == 0:
            print("Turning relay on")
            relay_pin.on()
        else:
            print("Turning relay off")
            relay_pin.off()

    # Define behavior for handling methods
    async def method_request_handler(method_request):
        # Determine how to respond to the method request based on the method name
        print(f"Received method request: {method_request.name}")
        if method_request.name == "catalog.1.send":
            payload = """{"Section":"Header"}
{"Section":"Enums"}
{"Section":"Assets"}
{"id":"8000AD5D","parentId":"03D94B97","name":"nECYD : AD5D","metadata":{"customProperties":{"deviceProperties":{"parent":"03D94B97","port":"4","service":"nlight","supported-capabilities":"Bridge","group-label":"","date-code":"0223"}},"model":"nECYD NLTAIR"}}
{"id":"03D94B97","parentId":"03D94B97","name":"","metadata":{"customProperties":{"deviceProperties":{"parent":"","port":"0","service":"nlight","supported-capabilities":"Gateway","group-label":"","date-code":"0824"}},"model":"nECYA"}}
{"Section":"Points"}
{"id":"/services/nlight/network/devices/03D94B97/master-settings","parentId":"03D94B97","valueType":"string","pointType":"value","name":"master-settings","metadata":{"capabilities":{"points-subscribe":{"version":"1","operations":{"subscribe":{}}},"points-write":{"version":"1","operations":{"set-value":{}}}}}}
{"id":"/services/nlight/network/devices/03D94B97/status/online","parentId":"03D94B97","valueType":"boolean","pointType":"value","name":"online","metadata":{"capabilities":{"points-subscribe":{"version":"1","operations":{"subscribe":{}}},"points-write":{"version":"1","operations":{}}}}}""" 
 # set response payload
            status = 200  # set return status code
            print("executed catalog.1.send")
        elif method_request.name == "relay.set":
            if relay_pin.value == 0:
                print("Turning relay on")
                relay_pin.on()
            else:
                print("Turning relay off")
                relay_pin.off()
            payload = {"result": True, "data": relay_pin.value == 1 }  # set response payload
            status = 200  # set return status code
            print("executed relay.set")
        else:
            payload = {"result": False, "data": "unknown method"}  # set response payload
            status = 400  # set return status code
            print("executed unknown method: " + method_request.name)

        # Send the response
        method_response = MethodResponse.create_from_method_request(method_request, status, payload)
        await device_client.send_method_response(method_response)

    # Set the method request handler on the client
    device_client.on_method_request_received = method_request_handler

    # set the message received handler on the client
    device_client.on_message_received = message_received_handler

    # define behavior for halting the application
    def stdin_listener():
        while True:
            selection = input("Press Q to quit\n")
            if selection == "Q" or selection == "q":
                print("Quitting...")
                break

    # Run the stdin listener in the event loop
    loop = asyncio.get_running_loop()
    user_finished = loop.run_in_executor(None, stdin_listener)

    # Wait for user to indicate they are done listening for messages
    await user_finished

    # finally, shut down the client
    await device_client.shutdown()


if __name__ == "__main__":
    asyncio.run(main())