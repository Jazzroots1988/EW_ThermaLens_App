from opcua import Client
import time

url = "opc.tcp://127.0.0.1:1234"
#url = "opc.tcp://localhost:62548/SampleServer"
#nodeId = "ns=2;i=2"

client = Client(url)
client.connect()
root = client.get_root_node()
nodeId = root.get_child(["0:Objects", "2:Trigger", "2:Value"])
TIME_WAIT = 10

node = client.get_node(nodeId)
n = 20
value = 0
while True:
	if n == 20:
		for tempo in range(1, 5, 1):
			value = float(n)
			node.set_data_value(value)
			time.sleep(TIME_WAIT)
		n = 25
		for tempo in range(1, 5, 1):
			value = float(n)
			node.set_data_value(value)
			time.sleep(TIME_WAIT)
		n = 20

client.disconnect()
