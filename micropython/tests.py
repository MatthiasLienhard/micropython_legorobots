import esp32_vl53l0x
import time

test=esp32_vl53l0x.VL53L0X(i2c)
while True:
print (test.range)
time.sleep(.1)
   

import ustruct

ref_spad_map=bytearray(i2c.readfrom_mem(41,0xB0,6))

i2c.writeto_mem(41, 0xB0, ref_spad_map)


i2c.writeto(41,ustruct.pack('B', 0xB0))
