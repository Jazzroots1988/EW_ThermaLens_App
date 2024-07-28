from opcua import Client
import time
import random

url = "opc.tcp://127.0.0.1:1234"
#url = "opc.tcp://localhost:62548/SampleServer"
#nodeId = "ns=2;i=2"


client = Client(url)
client.connect()
print("Server connected")

# alternate mode for auto search node
print("searching nodeId")
root = client.get_root_node()
nodeId = root.get_child(["0:Objects", "2:Trigger", "2:Value"])
print(f'NodeId: {nodeId}')

try:
	while True:

		value = random.randint(19, 21)
		print(f'value sent {value}')

		node = client.get_node(nodeId)
		value = float(value)
		node.set_data_value(value)
		time.sleep(5)


except KeyboardInterrupt:
	pass

client.disconnect()
print("Client stopped and disconnected")
