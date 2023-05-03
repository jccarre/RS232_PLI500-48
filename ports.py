import serial
import serial.tools.list_ports


def find_serial_port():
    for port in serial.tools.list_ports.comports():
        if "/dev/ttyAMAO" not in port.device:
            return port.device
    return None

serial_port = find_serial_port()

print("port serie: "+serial_port)
