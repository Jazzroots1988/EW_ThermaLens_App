from opcua import Client

class OpcRead:

	def __init__(self, url):

		self.url = url


	def data_extract(self):

		client = Client(self.url)
		client.connect()
		root = client.get_root_node()
		nodeId = root.get_child(["0:Objects", "2:Trigger", "2:Value"])

		node = client.get_node(nodeId)
		value = node.get_value()

		client.disconnect()
		return value


