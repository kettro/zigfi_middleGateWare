# Imports
import json

class MessageParser:
    @staticmethod
    def parse(message):
        '''
        Parse Incoming message
        Params:
            message: messege received from the MQTT Broker
        Return a parsed out dict: {
            cmd:
            topic:
            payload:
        }
        '''
        return json.loads(message)

    @staticmethod
    def encode(message):
        '''
        Encode outgoing message as JSON, to be sent to the MQTT Broker
        Params:
            message: dict of the message to be sent: {
                cmd:
                response:
            }
        Return a stringified JSON message
        '''

        return json.dump(message)
