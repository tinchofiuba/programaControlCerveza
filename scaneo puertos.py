import serial.tools.list_ports
ports=list(serial.tools.list_ports.comports())

#print(type(ports))
#print(ports[1])
##print(ports)

for i in ports:
    print(i)
