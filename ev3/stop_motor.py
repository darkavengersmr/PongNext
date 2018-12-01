#!/usr/bin/env python3

from ev3dev.ev3 import *

mC = LargeMotor('outC')
Sound.beep().wait()
mC.stop(stop_action="brake")
Sound.beep().wait()
