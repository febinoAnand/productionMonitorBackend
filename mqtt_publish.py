import paho.mqtt.client as mqtt
import json
import time

# MQTT broker details
broker = "mqtt.univa.cloud"  # Replace with your broker address
port = 1883  # Default MQTT port
topic = "subscribeTopic"  # Replace with your topic

# Initialize production count
production_count = 0

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
    else:
        print("Connection failed with code", rc)

def on_publish(client, userdata, mid):
    print(f"Data published with mid {mid}")

# Initialize the MQTT client
client = mqtt.Client()

# Assign event callbacks
client.on_connect = on_connect
client.on_publish = on_publish

# Connect to the broker
client.connect(broker, port)

# Start the MQTT loop to process network traffic and dispatch callbacks
client.loop_start()

try:
    while True:
        # Increment production count
        production_count += 1

        # Create JSON data with the current timestamp and incremented production count
        data = {
            "timestamp": int(time.time()),
            "device_token": "550e8400-e29b-41d4-a716-446655440000",
            "machine_id": "7AP2345ASW",
            "production_count": production_count
        }

        # Convert the data to JSON
        json_data = json.dumps(data)

        # Publish the JSON data to the topic
        client.publish(topic, json_data)
        print(f"Published data: {json_data}")

        # Wait for 1 second before sending the next message
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping script...")

# Stop the MQTT loop and disconnect from the broker
client.loop_stop()
client.disconnect()
