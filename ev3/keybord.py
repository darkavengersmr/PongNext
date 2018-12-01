#!/usr/bin/env python3

from ev3dev.ev3 import *
import socket, time
import threading
from PIL import Image, ImageDraw, ImageFont

sock = socket.socket()
sock.bind(('', 9090))
sock.listen(100)

motor = LargeMotor('outC')
motor.reset()

lcd = Screen()
btn = Button()

Pos_medium = 0
K = 0.3
Pos = 0
u = 0
e = 0
Pk = 20

goal_left = 0
goal_right = 0
goal_left_new = 0
goal_right_new = 0

beep = False

connect = None

def write():
    global goal_left, goal_right

    lcd.clear()
 
    f = ImageFont.truetype('FreeMonoBold.ttf', 70)
    lcd.draw.text((0, 30), str(goal_left), font=f)

    f = ImageFont.truetype('FreeMonoBold.ttf', 40)
    lcd.draw.text((78, 30), ":", font=f)

    f = ImageFont.truetype('FreeMonoBold.ttf', 70)
    if(goal_right < 10): lcd.draw.text((135, 30), str(goal_right), font=f)
    else: lcd.draw.text((90, 30), str(goal_right), font=f)

    lcd.update()

def socket_():
  global Pos_medium, K, Pos, goal_left_new, goal_right_new, connect
  Sound.beep()  
  while connect is None: pass
  Sound.beep()
  while True:
    data = connect.recv(2)
    str_in = data.decode("utf-8")
    if(len(str_in) == 2 and (str_in[0] == "D" or str_in[0] == "U" or str_in[0] == "N")):
        if(str_in[0] == "D"):
            Pos = 15
        elif(str_in[0] == "U"):
            Pos = -15 
        elif(str_in[0] == "N"):
            Pos = 0
        if(str_in[1] == "L"): 
            #Sound.beep()
            goal_left_new += 1
        elif(str_in[1] == "R"): 
            goal_right_new += 1 
            #Sound.beep()

def new_socket():
  global connect
  while True:
      c, a = sock.accept()
      connect = c

def beep_():
  global beep
  while True:
      if(beep == True): 
          Sound.beep()
          beep = False

t = threading.Thread(target=socket_)
t.start()

t0 = threading.Thread(target=beep_)
t0.start()

t1 = threading.Thread(target=new_socket)
t1.start()

write()

while 1:
    e = Pos - motor.position
    u = e*Pk
    motor.run_forever(speed_sp=u)

    if(btn.backspace): 
        while (abs(0-motor.position) > 1):
            e = 0 - motor.position
            u = e*Pk
            if(u < -900): u = -900
            if(u > 900): u = 900
            motor.run_forever(speed_sp=int(u))
        motor.stop(stop_action="brake")
        exit()

    if(goal_left != goal_left_new or goal_right != goal_right_new):
        beep = True
        goal_right = goal_right_new
        goal_left = goal_left_new
        write()
        print(goal_left, ":", goal_right)
