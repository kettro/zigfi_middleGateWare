# Imports
import paho.mqtt.client as mqtt
from command_interpreter import CommandInterpreter
from message_parser import MessageParser as mp


class MQTTClient:
    def __init__(self, brokerAddr, mgmtTopic):
        '''
        Initialize the MQTT Client, as well as the Command interpreter
        Params:
            * brokerAddr: IP Address or URL of the MQTT Broker
            * mgmtTopic: Topic for the Coordinator to subscribe to
        '''
        self.broker = brokerAddr
        self.subbed_topic = mgmtTopic
        self.client = mqtt.Client()
        # Override the default callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        # Instantiate CommandInterpreter
        self.ci = CommandInterpreter()
        # Need to then connect to the broker, sub to the mgmt topic
        return

    def exec_client(self):
        '''
        Execute the MQTT Client; kickstart the system
        '''
        print "connecting to the client"
        self.client.connect(self.broker, 1883, 60)
        # Loop
        print "looping forever"
        #self.client.loop_start()
        self.client.loop_forever()

    def on_connect(self, client, data, flags, rc):
        '''
        Connect Callback: Subscribe to the requested topic
        '''
        print "Connected to client, about to subscribe"
        self.client.subscribe(self.subbed_topic)
        return

    def on_message(self, client, userdata, msg):
        '''
        Callback for the Receipt of a message
        Relay the message to the message parse, then
        Send to the command interpreter
        Encode response from the CI, publish back to the sender
        '''
        print "message received"
        # Send the message off to the parser
        msg_dict = mp.parse(msg.payload)
        print "message parsed"
        # Save the returned topic as the reply topic
        reply_topic = msg_dict['topic']
        # Send off to the command interpreter
        response_dict = self.ci.interpret(msg_dict)
        print "message Interpreted"
        # Relay the response to the parser
        response = mp.encode(response_dict)
        print response
        # Finally, send off to the Broker
        self.client.publish(reply_topic, response)
        # All done
        return
