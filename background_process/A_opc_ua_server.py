from opcua import Server
import time
from datetime import datetime

server = Server()
server_url = "opc.tcp://127.0.0.1:1234"
server.set_endpoint(server_url)

name ="opcuapython"
namespace = server.register_namespace(name)
node = server.get_objects_node()

param = node.add_object(namespace, "Sensors")
param2 = node.add_object(namespace, "Trigger")
var = param.add_variable(namespace, "Temperature",0)
var_trigger = param2.add_variable(namespace, "Value", 0)
var.set_writable()
var_trigger.set_writable()
server.start()

print("OPC UA Server Started")
print("Press Ctrl-C to Stop Program")

try:
	while True:
		now = datetime.now()
		current_time = now.strftime("%H:%M:%S")
		print("OPC UA Server Running", current_time)
		value = var.get_value()
		value_trigger = var_trigger.get_value()
		print("Current Value:", value)
		print("Trigger value", value_trigger)
		time.sleep(1)

except KeyboardInterrupt:
	pass

server.stop()
print("OPC UA Server Stopped")