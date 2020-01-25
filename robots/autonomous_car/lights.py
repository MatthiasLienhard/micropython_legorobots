
import uasyncio as asyncio

import uos, machine, time

class LightBar():
    def __init__(self, np_pin=5, n=4):
        self.n=n
        self.np = machine.Neopixel(machine.Pin(np_pin), n) 
        asyncio.get_event_loop().create_task(self.kitt())

    async def kitt(self):
        while True:
            for pos in list(range(10*(self.n+2)))+list(range(10*(self.n+2),0,-1)): #position of brightest 
                for i in range(1,self.n+1):
                    c=max(0,255-abs(i*10-pos)*10)* 0x0010000
                    self.np.set(i,c)
                await asyncio.sleep(.01)
