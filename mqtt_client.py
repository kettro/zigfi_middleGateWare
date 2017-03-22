# Imports
import paho.mqtt.client as mqtt
from command_interpreter import CommandInterpreter
from message_parser import MessageParser as mp


class MQTTClient:
    def __init__(self, brokerAddr, mgmtTopic):
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

    def exec_Client():
        self.client.connect(broker, 1883, 60)
        # Loop
        #self.client.loop_start()
        self.client.loop_forever()

    def on_connect(client, data, flags, rc):
        # Subscribe to the topic in subbed_topic
        self.client.subscribe(subbed_topic)
        # Do other stuff...?
        return

    def on_message(client, userdata, msg):
        # Send the message off to the parser
        msg_dict = mp.parse(msg)
        # Save the returned topic as the reply topic
        reply_topic = msg_dict['topic']
        # Send off to the command interpreter
        response_dict = self.ci.interpret(msg_dict)
        # Relay the response to the parser
        response = mp.encode(
            {'cmd': response['cmd'], 'response': response['reponse']})
        # Finally, send off to the Broker
        self.client.publish(reply_topic, response)
        # All done
        return
