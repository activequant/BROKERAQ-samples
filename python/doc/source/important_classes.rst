Important classes
=================


Throughout the API, two classes are very important:
- MessageListener
- AqSocket

These two classes provide key functionality. AqSocket is responsible for establishing a connection to the gateway and sending messages to the gateway. MessageListener is responsible for processing incoming messages and wiring them into its according methods that you can override and implement as needed. 

In addition to these classes, we maintain a file definitions.py that contains definitions of common, constant values, such as time frame definitions and common instrument names. 

