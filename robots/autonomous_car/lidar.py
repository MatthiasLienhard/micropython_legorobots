from servo import Servo
import time
from math import copysign
from vl53l0x import VL53L0X   
import uasyncio as asyncio


from array import array
#import warnings

class RingBuffer:
    def __init__(self, size=10):
        self.index=0 #points to the next
        self.buffer=array('H', size*[0]) #H=unsigned short (0-64k)
        self.laps=0
    
    def append(self, value):
        self.buffer[self.index]=value
        self.index+=1
        if self.index == len(self.buffer):
            self.index=0
            self.laps+=1

    def first_index(self):
        if self.laps==0:
            return 0
        else:
            return self.index
    
    def total_added(self):
        return self.laps*len(self)+self.index
    
    def __getitem__(self, key):
        maxkey=self.total_added()-1
        minkey=maxkey-len(self)+1
        if key> maxkey or key < minkey:
            raise ValueError('key <{}> out of accessible range [{},{}]'.format(key, minkey, maxkey))             
        return self.buffer[key % len(self.buffer)]

    def __setitem__(self, key, value):
        maxkey=self.total_added()-1
        minkey=maxkey-len(self)+1
        if key> maxkey or key < minkey:
            raise ValueError('key <{}> out of accessible range [{},{}]'.format(key, minkey, maxkey))             
        self.buffer[key % len(self.buffer)]=value
             
    def __len__(self):
        return len(self.buffer)
    
    def iter_n(self, n):
        if n>len(self):
            raise ValueError('request {} elements but only {} elements are buffered'.format(n, len(self)) )             
        start=self.index-n
        if start<0:
            if self.laps>0:
                for i in range(start+len(self), len(self) ):
                    yield self.buffer[i]
            else: 
                #warnings.warn("only {} elemets added so far".format(self.index)) #not supported in micropython
                print("WARNING: only {} elemets added so far".format(self.index))
            start=0
        for i in range(start,self.index):
            yield(self.buffer[i])

    def __bool__(self):
        return self.index>0 or self.laps>0

    def __iter__(self):
        if self.laps != 0:
            for i in range(self.index, len(self) ):
                yield(self.buffer[i])
        for i in range(self.index):
            yield(self.buffer[i])

    def __str__(self):
        return ','.join(map(str, self))

    def str_n(self, n):
        return ','.join(map(str, self.iter_n(n) ))

class Lidar():
    def __init__(self,servo, sensor):
        self.servo=servo
        self.sensor=sensor
        sensor.start()
        self.values=[RingBuffer() for _ in range(5)]
        self.timestamp=[0]*5
        self.period=[RingBuffer() for _ in range(5)]
        asyncio.get_event_loop().create_task(self.measure())
        
    async def measure(self):
        while True:
            for i in (0,2,4,3,1):
                self.servo.set((i-2)/2)
                await asyncio.sleep(.3)
                self.values[i].append(self.sensor.read())
                now=time.ticks_ms()                
                self.period[i].append(time.ticks_diff(now, self.timestamp[i]))
                self.timestamp[i]=now
                



