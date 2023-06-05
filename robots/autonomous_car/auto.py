import d1motor
from servo import Servo
import time
import machine
from math import copysign
from machine import I2C, Pin, PWM
#from esp32_vl53l0x import VL53L0X   
from vl53l0x import VL53L0X   
import random
#i2c = I2C(-1,Pin(22), Pin(21), freq=100000)



class autonomous_car:
    def __init__(self, i2c,servo,  min_speed=30, max_speed=100):
        self.m0= d1motor.Motor(0, i2c)
        self.m1= d1motor.Motor(1, i2c)
        self.m0.frequency(10000) # 10khz -> quiet
        self.m1.frequency(10000) # 10khz -> quiet
        self.dist_sensor=VL53L0X(i2c)
        self.dist_sensor.start()
        self.dist=self.dist_sensor.read()
        #self.pause_pin=Pin(pause_pin, machine.Pin.IN, machine.Pin.PULL_UP) #its pulled low by a cable in operating mode
        #esp32.wake_on_ext0(pin = self.pause_pin, level = esp32.WAKEUP_ALL_LOW)
        #does not work because of exposed pins
        self.servo = servo
        self.current_speed=0
        self.actual_speed=0
        self.min_speed=min_speed
        self.max_speed=max_speed
        

    
    def drive(self, speed=None):
        if speed is None:
            speed=self.current_speed
        if abs(speed) > 0:
            mspeed=round(self.min_speed+abs(speed)*(self.max_speed-self.min_speed)/100)            
            self.m0.speed(int(copysign(mspeed, speed)))
            self.m1.speed(int(copysign(mspeed, speed)))
        else:    
            self.m0.sleep()
            self.m1.sleep()

    def print_status(self, msg):
        print('{}d={}, motor speed={}%,direction={},  real speed={}'.format(
            msg,
            self.dist,
            round(self.current_speed),
            round(self.servo.position*10), 
            round(self.actual_speed,2)))

    def drive_autonomous(self, accel=10):
        now=prev=time.ticks_ms()
        d_prev=self.dist
        target_speed=0
        cycle_count=0
        try:
            while True:
                now=time.ticks_ms()  
                if(now-prev>100):              
                    try:            
                        self.dist=self.dist_sensor.read()#sometimes the reading fails
                    except: # todo: what error is expected?
                        print('dist sensor error')
                        d=d_prev
                    #calculate actual speed
                    self.actual_speed=(d_prev-self.dist)/(now-prev)     #(mm/ms==m/s)   
                    d_prev=self.dist
                    prev=now

                if self.dist>1000:
                    self.dist=1000                
                if self.dist<300:            
                    #turn around
                    #self.direction=random.randrange(-1,2,2)
                    self.m0.brake() 
                    self.m1.brake()
                    self.servo.set(1)
                    self.current_speed=-20
                    self.print_status('<- ')
                    self.drive()         
                    time.sleep(1)
                    self.servo.set(self.servo.position*-1)
                    self.current_speed=20
                    self.drive()
                    time.sleep(1)
                    self.servo.set(0)
                else:
                    target_speed=self.dist/10-20
                    if target_speed>self.current_speed:
                        self.current_speed+=copysign(accel,target_speed-self.current_speed) #beware overshooting
                    else:
                        self.current_speed=target_speed
                    #if cycle_count % 10 ==0:
                    self.print_status('-> ')        
                    self.drive()

                time.sleep(.1)#update 10/second
                cycle_count+=1
        except KeyboardInterrupt: #catch keybord interrupt and others
            self.m0.brake()
            self.m1.brake()
            raise            
        
import d1motor
from servo import Servo
import time
import machine
from math import copysign
from machine import I2C, Pin, PWM
import random
import uasyncio as asyncio



class autonomous_car:
    def __init__(self, lidar, lights,servo, i2c, min_speed=20, max_speed=50):
        self.m0= d1motor.Motor(0, i2c)
        self.m1= d1motor.Motor(1, i2c)
        self.m0.frequency(10000) # 10khz -> quiet
        self.m1.frequency(10000) # 10khz -> quiet
        self.lidar=lidar
        self.lights=lights
        self.servo = servo
        self.current_speed=0
        self.actual_speed=0
        self.min_speed=min_speed
        self.max_speed=max_speed
        asyncio.get_event_loop().create_task(self.drive_autonomous())

    
    def drive(self, speed=None):
        if speed is None:
            speed=self.current_speed
        if abs(speed) > 0:
            mspeed=round(self.min_speed+abs(speed)*(self.max_speed-self.min_speed)/100)            
            self.m0.speed(int(copysign(mspeed, speed)))
            self.m1.speed(int(copysign(mspeed, speed)))
        else:    
            self.m0.sleep()
            self.m1.sleep()

    def print_status(self, msg):
        print('{}d={}, motor speed={}%,direction={},  real speed={}'.format(
            msg,
            [next(v.iter_n(1)) for v in self.lidar.values],
            round(self.current_speed),
            round(self.servo.position*10), 
            round(self.actual_speed,2)))

    async def drive_autonomous(self, accel=10):        
        target_speed=0
        while self.lidar.values[2].index<2:
            await asyncio.sleep(1)
        try:
            while True:                
                dist=list(self.lidar.values[2].iter_n(2)) #last two readings
                self.actual_speed=(dist[0]-dist[1])/next(self.lidar.period[2].iter_n(1))     #(mm/ms==m/s)   
                    
                if dist[-1]>1000:
                    dist[-1]=1000                
                if dist[-1]<300:            
                    #turn around
                    #self.direction=random.randrange(-1,2,2)
                    self.m0.brake() 
                    self.m1.brake()
                    self.servo.set(1)
                    self.current_speed=-20
                    self.print_status('<- ')
                    self.drive()         
                    await asyncio.sleep(1)
                    self.servo.set(self.servo.position*-1)
                    self.current_speed=20
                    self.drive()
                    await asyncio.sleep(1)
                    self.servo.set(0)
                else:
                    target_speed=(dist[-1]/10)
                    if target_speed>self.current_speed:
                        self.current_speed+=copysign(accel,target_speed-self.current_speed) #beware overshooting
                    else:
                        self.current_speed=target_speed
                    #if cycle_count % 10 ==0:
                    self.print_status('-> ')        
                    self.drive()

                await asyncio.sleep(.2)#update 10/second
        except KeyboardInterrupt: #catch keybord interrupt
            self.m0.brake()
            self.m1.brake()
            raise            
        except : #catch others
            self.m0.brake()
            self.m1.brake()
            raise           
