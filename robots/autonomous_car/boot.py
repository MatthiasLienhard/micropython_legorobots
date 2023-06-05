import uos, machine, time
import network
import gc
import uasyncio as asyncio

async def connect():
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
        sta.ifconfig(('192.168.178.35', '255.255.255.0', '192.168.178.1', '8.8.8.8'))
    timeout=5000 #5 seconds
    if not sta.isconnected():
        # try all wlans from the file
        # todo: scan first and check which can be seen
        for pw in wlan:    
            start = time.ticks_ms()
            while not sta.isconnected():
                if time.ticks_diff(time.ticks_ms(), start) > timeout:
                    break
                sta.connect(*pw)
                print('connecting to wlan, ip is {}'.format(sta.ifconfig()[0]))
                await asyncio.sleep(1)
            else: break

    if not sta.isconnected():
        #todo: start station mode
        pass

    print('starting telnet...')
    network.telnet.start()

asyncio.get_event_loop().create_task(connect()) 

