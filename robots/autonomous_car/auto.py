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
