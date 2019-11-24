import uos, machine, time

np = machine.Neopixel(machine.Pin(5), 4) 
np.set(0, 0xFF0000)
np.show()
import network
import gc

#connect
sta = network.WLAN(network.STA_IF)
sta.active(True)
wlan=list()
with open( 'credentials.txt','r') as f:
    # this file should contain ssid<space>pw, one per line
    line=f.readline().strip().split()
    while line:
        wlan.append(line)
        line=f.readline().strip().split()
if machine.wake_reason()[0] not in [4,6]:#Soft reset
    # this should help reconnecting... not sure whether it works or not
    # configuration below MUST match your home router settings!!
    print('configure wlan')
    sta.ifconfig(('192.168.178.53', '255.255.255.0', '192.168.178.1', '8.8.8.8'))
    
timeout=5000 #5 seconds
if not sta.isconnected():
    # try all wlans from the file
    # todo: scan first and check which can be seen
    for pw in wlan:    
        start = time.ticks_ms()
        while not sta.isconnected():
            sta.connect(*pw)
            print('connecting to wlan, ip is {}'.format(sta.ifconfig()[0]))
            for i in range(5):
                print('attempt {}, ip is {}'.format(i, sta.ifconfig()[0]))
                if sta.isconnected():
                    break
                time.sleep(.5)
                np.set(0, 0x000000)
                time.sleep(.5)
                np.set(0, 0xFF0000)
                
            if time.ticks_diff(time.ticks_ms(), start) > timeout:
                np.set(0,0xFF1000)
                np.show()  
                #raise TimeoutError
                break
        else: break

if not sta.isconnected():
    #todo: start station mode
    pass

print('starting telnet...')
network.telnet.start()

np.set(0,0x00FF00)  #green
np.show()  
time.sleep_ms(500)
np.set(0,0x001000)  #green (not as bright)
np.show()  

 

