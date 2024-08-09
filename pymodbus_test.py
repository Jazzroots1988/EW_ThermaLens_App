import pymodbus.exceptions
from pymodbus.client.sync import ModbusTcpClient
import time

client = ModbusTcpClient('127.0.0.1', port=502)
try:
    client.connect()
except pymodbus.exceptions.ConnectionException:
    time.sleep(5)
    print("No connection waiting 5 secs")

ADDRESS = 2
value_write = int(0)
while True:
    try:
        pick_values = client.read_holding_registers(ADDRESS,1)

        #print('value present in: ', ADDRESS, 'is',  pick_values.registers[0])

        write_value = client.write_register(ADDRESS, int(value_write))
        value_write += 1
        time.sleep(3)

    except KeyboardInterrupt:
        client.close()


