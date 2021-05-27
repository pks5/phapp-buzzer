from gpiozero import TonalBuzzer
from gpiozero.tools import sin_values
import json
import sys
import time

class Buzzer:
    def __init__(self, notify_url=None):
        self.tonal_buzzer = None
        self.notify_url = notify_url
        self.prev_state = None
        
    def send(self, data):
        payload = {
            "headers": {
                "to": self.notify_url
            },
            "body": data
        }
        print("<<" + json.dumps(payload), flush=True)

    def receive(self):
        for line in sys.stdin:
            sMessage = line[:-1]
            
            if(sMessage[0:3] == '>>{'):
                message = json.loads(sMessage[2:])
                try:
                    self.process(message)
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(e)

    def process(self, message):
        message_body = message["body"]

        if("action" in message_body):
            action = message_body["action"]
        
            if(action == "STATUS"):
                self.send({'state' : self.prev_state})
                return

            if (action == "INIT"):
                pin_nr = message_body["pin"]
                if(pin_nr < 0 or pin_nr > 53):
                    print("Error: Pin out of range 0..53", flush=True)
                    return

                if(self.tonal_buzzer != None):
                    self.tonal_buzzer.close()
                    print("Closed TonalBuzzer.", flush=True)
                
                self.tonal_buzzer = TonalBuzzer(pin_nr)
                print("Created TonalBuzzer on pin " + str(pin_nr), flush=True)
                    
        if(self.tonal_buzzer == None):
            print("Warning: TonalBuzzer not initialized!", flush=True)
            return
            
        if("mode" in message_body):
            mode = message_body["mode"]
            
            if(mode == "OFF"):
                self.tonal_buzzer.source = None
                self.tonal_buzzer.stop()
                print("Set TonalBuzzer to OFF", flush=True)
            elif(mode == "ON"):
                self.tonal_buzzer.source = sin_values()
                print("Set TonalBuzzer to ON", flush=True)
            else:
                print("Error: invalid mode!", flush=True)
                return

            if('skip_state' not in message_body):
                self.prev_state = message_body
                self.send({'state' : message_body}) 
    
buzzer = Buzzer()

try:
    buzzer.receive()
except KeyboardInterrupt:
    print('Good Bye!')
finally:
    print("cleanup")
