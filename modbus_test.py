import modbus
import time
import random

if __name__ == '__main__':

    client = modbus.modbusClient()

    # client basic configurations
    client.server_host = 'localhost'
    client.server_port = 502
    client.server_modbus_id = 1
    client.connect()
    sending_list = [10]
    sending_list2 = [0]

    while True:
        data = random.sample(range(-40, 500), 20)
        client.write_holding_registers(data)
        time.sleep(2)
