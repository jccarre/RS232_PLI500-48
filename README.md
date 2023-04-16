This project aims at sending commands to a Steca Solaris PLI 5000-48, and getting responses from it. All data transfered (both ways) are logged.

The main file is a python script. It uses a C library to compute the CRC required at the end of each message. The CRC computation is based on the documentation given by Steca. They use a custom look-up table for this. You need to compile the calcul_CRC.c file in order to generate the calcul_CRC.so file. Here is the command to type : 
gcc -shared -o calcul_CRC.so -fPIC calcul_CRC.c

You need to adapt the name of your COM port. To get the name of all available COM ports, execute the following command (the USB-RS232 adaptator must be plugged in).
python3 -m serial.tools.list_ports
Then, put that COM port name in the variable called "COM_port_name" in the beginning of the file "commande_PLI.py".

Then, run the python file.
