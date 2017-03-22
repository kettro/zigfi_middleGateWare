# Python Middleware

## Purpose
This middleware is designed to be the main interface with the MQTT broker,
and by proxy the webclient. It is to connect to the management channel for
the given device, and receive and send commands out to and from the client.
On the receipt of a command, the command must be parsed, and the proper action
taken with the values. The "Proper Action" will be described here.

## Database
The middleware uses TinyDB as a database. It was chosen due to its No-SQL
nature, easy configuration, and lightweight nature (especially in  the space
constrained Beaglebone). It operates via a JSON file in the project. The
database is wrapped in a class called Database, which provides convenience
functions for creating, getting,and modifying the information about any given
Group, Device, or Control in the system.

### Tables
The database defines three main tables to catalogue the data for the system.
These are grpTable, devTable, and ctrlTable. Each table corresponds the the
items in the topology as expected. The relations between each table are as
follows:
* Groups:
  * has: name
  * has-many: devices
* Devices:
  * has: name, IEEE id, type
  * has-many: controls
  * belongs-to: Group
* Controls:
  * has: name, type, value
  * belongs-to: Group, Device

### Access
The Database class provides access to the database in the form of the CRUD
verbs specified in the Command Set document.

## Network
The middleware is set between the webclient on one end, and the Gateway
Application on the other. It is undecided how the network and the middleware
will connect. Current options are:
* embed C functions into the middleware (via cffi, or Python.c)
* utilize sockets to facilitate communications
* embed the Python middleware into the C code of the Gateway

# Project Structure
## Files
Each class represented will have its own file, as well as a single
run.py that runs the main loop of the code. The project is based on
a pseudo-MVC structure.

## Classes
### CommandInterpreter
This class is the main controller for the Application. It connects with
the MQTTClient, the Database, and the ZNetwork. It serves primarily to be an
interpreter for commands send into the Application from the webclient.
It responds and executes the commands, and returns the responses to the
MQTT client, which forwards it on to the webclient.

### MQTTClient
The MQTTClient is a wrapper for the Paho MQTT library. It serves as a
client for sending and receiving MQTT messages to and from the webclient.
It utilizes the MessageParser class to parse the raw incoming data, and to
then send off to the CommandInterpreter. It is never called from another class.

### ZNetwork
The ZNetwork is the wrapper for the Gateway application, and provides basic
methods for sending and receiving messages via the Network. It also establishes
the connection between the Python Application and the Gateway C Application.

### Database
The database is described above; it serves as a wrapper class for the TinyDB,
and provides a series of functions for accessing Network Metadata.
