from gpiozero import TonalBuzzer
from gpiozero.tools import sin_values
import bletacloud

class Buzzer:
    def __init__(self, sNotifyUrl):
        self.oBuzzer = None
        self.sNotifyUrl = sNotifyUrl
        self.sMode = "OFF"
        bletacloud.receive(self.processMessage)

    def uploadStatus(self):
        mStatus = {
            "mode" : self.sMode
        }

        bletacloud.send(self.sNotifyUrl, mStatus)

    def processMessage(self, oMsg):
            oMessage = oMsg["payload"]

            if ("request" in oMessage and oMessage["request"] == "STATUS"):
                self.uploadStatus()
                return

            if ("pin" in oMessage):
                iPin = oMessage["pin"]
                if(iPin < 0 or iPin > 53):
                    print("Error: Pin out of range 0..53", flush=True)
                    return

                if(self.oBuzzer != None):
                    self.oBuzzer.close()
                    print("Closed TonalBuzzer.", flush=True)
                
                self.oBuzzer = TonalBuzzer(iPin)
                print("Created TonalBuzzer on pin " + str(iPin), flush=True)
                    
            if(self.oBuzzer == None):
                print("Warning: TonalBuzzer not initialized!", flush=True)
                return
            
            if("mode" in oMessage):
                sMode = oMessage["mode"]
                
                if(sMode == "OFF"):
                    self.oBuzzer.source = None
                    self.oBuzzer.stop()
                    print("Set TonalBuzzer to OFF", flush=True)
                elif(sMode == "ON"):
                    self.oBuzzer.source = sin_values()
                    print("Set TonalBuzzer to ON", flush=True)
                else:
                    print("Error: invalid mode!", flush=True)
                    return

                self.sMode = sMode

                self.uploadStatus()   
    
oBuzzer = Buzzer("fhtp://featurehub/system/net.featurehub.lp.apps.alarmsystem/buzzer/status")
