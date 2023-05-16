This project aims at sending commands to a Steca Solaris PLI 5000-48, and getting responses from it. All data transfered (both ways) are logged.

The main file is a python script. It is based on the documentation given by Steca.

If you want to use the C version (not required), you need to compile the calcul_CRC.c file in order to generate the calcul_CRC.so file. Here is the command to type : 
gcc -shared -o calcul_CRC.so -fPIC calcul_CRC.c
