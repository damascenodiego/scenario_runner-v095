import pygame
import time
import evdev

from evdev import ecodes, InputDevice, ff

# Find first EV_FF capable event device
for name in evdev.list_devices():
    device = InputDevice(name)
    print(name)
    if ecodes.EV_FF in device.capabilities():
    	for k,v in device.capabilities(verbose=True, absinfo=True).items():
    		print(k,v)
    	print()
        break

print(device)

evtdev = InputDevice(device.path)

# for val in range(65535,0,-1000):
for val in range(0,65535,1):
	#evtdev.write(ecodes.EV_FF, ecodes.FF_AUTOCENTER, val)
	ev=evdev.InputEvent(0L,0L,ecodes.EV_FF, ecodes.FF_AUTOCENTER, val)
	evtdev.write_event(ev)
	#ev=evdev.InputEvent(0L,0L,0, 0, 0)
	#evtdev.write_event(evdev.events.SynEvent(ev))
	time.sleep( 1 )


evtdev.write(ecodes.EV_FF, ecodes.FF_AUTOCENTER, 0)
evtdev.write(ecodes.EV_FF, ecodes.FF_AUTOCENTER, 65535)

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
	print(device.path, device.name, device.phys)
