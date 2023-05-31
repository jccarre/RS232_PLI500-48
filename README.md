# Communicating with Steca PLI5000-48 over RS232

## Introduction
The [Steca PLI5000-48](https://www.steca.com/index.php?Solarix-PLI-5000-EN) is a solar inverter that contains a RS-232 port. It allow to send requests, either to get data, or send orders to the PLI.

The RS-232 cable comes with the PLI, but you will probably need a USB to RS-232 adaptator.

This projects uses this communication port to communicate with the PLI, in order to log data, and send commands.

## Communication Protocol

The official documentation of the communication protocol can't be found directly online. But Steca easily accepts to send it if you kindly request it by email.

Roughly speaking, it is based on keywords that you send, and the PLI answers.

* Keywords starting with a 'Q' (like Query) ask for data, but do not affect the status of the PLI or its behaviour.
* All other Keywords are commands that will change one of the paramater described in the "Operation/Configuration" section (page 19 to 26) of the [user's manual](https://www.steca.com/frontend/standard/popup_download.php?datei=220/22067_0x0x0x0x0_Solarix_PLI_Manual_EN_Z07.pdf)

All data transfered (from the user as well as from the PLI) ends with a CRC computation.

### Available commands
* `QFLAG` Device flag status inquiry
* `QPIRI` Device Rating Information inquiry
* `QPIGS` Device general status parameters inquiry
* `QMOD` Device Mode inquiry
* `QPIWS` Device Warning and Fault Status inquiry
* `PCP` Setting device charger priority (setting n°16 of the user's manual)
* ... and more to come ;-)

