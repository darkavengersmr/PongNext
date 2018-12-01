# -*- coding: cp1251 -*-
import pygame
import math
import random
import time
import threading
import numpy as np

num_x=8
num_y=6
num_g=18
num_r=10
num_k=3

brain=np.ones((num_x,num_y,num_g,num_r,num_k))

xmax=1600
ymax=900
pygame.init()
#sc = pygame.display.set_mode((xmax,ymax),pygame.FULLSCREEN)
sc = pygame.display.set_mode((xmax,ymax),pygame.RESIZABLE)

timer1=time.time()
pygame.display.update()
debug=0;

y_left=ymax/2
y_right=ymax/2
x_speed=0
y_speede=0
y_speed=0
ym=ymax/2
xm=xmax/2
graduc=random.random()*70+50
gol=0
u=0
timer2=time.time()
p1=0
p2=0
old_y_left=y_left
old_y_right=y_right
ugol_spawna=0
speedm=1.5
speedr=1.5
learn_i=0
learn_progress = 0
learn_time = 0
tmp4=0

def learn():
  global brain,learn_i
  ys=0
  learn_i+=1
  if y_speed<0: ys=0
  if y_speed==0: ys=1
  if y_speed>0: ys=2  
  brain[int(xm/(xmax/num_x+1))][int(ym/(ymax/num_y+1))][int(graduc/(360/num_g+1))][int((y_right+65)/(ymax/num_r+1))][int(ys)]+=1
  
def control():
  global y_speed,speedr,f,brain
  
  for event in pygame.event.get():
    y_speed=0     
    if event.type == pygame.QUIT: exit()     
    if event.type == pygame.KEYDOWN: 
      if pygame.key.get_pressed()[pygame.K_UP]:
        y_speed = -speedr
      if pygame.key.get_pressed()[pygame.K_DOWN]:
        y_speed = speedr
      if  event.key == pygame.K_s:
        f = open('brain.txt', 'w')
        print('save')
        for i in range(num_x):
          for i2 in range(num_y):
            for i3 in range(num_g):
              for i4 in range(num_r):
                for i5 in range(num_k):

                    
                  f.write(str(int(brain[i][i2][i3][i4][i5]))+'\n')
        f.close()
        
      if event.key == pygame.K_l:
        f = open('brain.txt', 'r')
        tmpbrain=0
        print('load')
        
        for i in range(num_x):
          for i2 in range(num_y):
            for i3 in range(num_g):
              for i4 in range(num_r):
                for i5 in range(num_k):                  

                  stringtmp=f.readline().rstrip()
                  #print(i,i2,i3,i4,i5,stringtmp)
                  brain[i][i2][i3][i4][i5]=int(stringtmp)                  
        
        
        f.close()
        
      if event.key == pygame.K_v:
        pygame.quit()
        
def clear():
  global sc,xmax,y_left,y_right,xm,ym
  pygame.draw.rect(sc, (255, 255, 255), (xmax-160, y_right, 30, 130))
  pygame.draw.rect(sc, (255, 255, 255), (160, y_left, 30, 130))    
  pygame.draw.rect(sc, (255, 255, 255), (xm,ym,30,30))
  pygame.display.update()
  
def draw():
  global sc,xmax,y_left,y_right,xm,ym
  pygame.draw.rect(sc, (0, 0, 0), (xmax-160, y_right, 30,130))
  pygame.draw.rect(sc, (0, 0, 0), (160, y_left, 30,130))    
  pygame.draw.rect(sc, (0,0,0), (xm, ym,30,30))
  
def move_ball():
  
    global ym,graduc,xm,speedm
    
    ym=ym-speedm*math.cos(math.radians(graduc))
    xm=xm+speedm*math.sin(math.radians(graduc))
    
def bounce_off_walls():
  
  global y_left,y_right,y_speed,ym,ymax,graduc,xm,xmax,gol,p1,ugol_spawna,p2

  y_right += y_speed    
  y_left=y_left+y_speede
  
  if y_left+130>=900:
    y_left=900-150
    
  if y_left<=0:
    y_left=5

  if y_right+130>=900:
    y_right=900-130
    
  if y_right<=0:
    y_right=0
    
  if ym>=ymax-30:
    ym=ymax-30
    graduc=180-graduc
    
  if ym<=0:
    ym=0              
    graduc=180-graduc
    
  if xm>=xmax-100:
    graduc=360-graduc
    gol=1
    p1+=1
    ugol_spawna=-90
    
  if xm<=100:
    graduc=360-graduc      
    gol=1
    p2+=1
    ugol_spawna=90
    
def timing():
  
  global vr,timer2,P,graduc,tmp4,learn_progress,learn_time
  

  if time.time()-timer2>=10:
    P=random.random()
    timer2=time.time()
    if debug==0:
      l_sum = 0      
      for i in range(num_x):
          for i2 in range(num_y):
            for i3 in range(num_g):
              for i4 in range(num_r):
                if brain[i][i2][i3][i4][0] + brain[i][i2][i3][i4][1] + brain[i][i2][i3][i4][2] > 3:
                  l_sum += 1
      try:
          learn_time = 0.75* learn_time + 0.25 * 100*10/(l_sum/(num_x*num_y*num_g*(360-40-40)/360*num_r)*100 - learn_progress)/60
          print(int(l_sum/(num_x*num_y*num_g*(360-40-40)/360*num_r)*100),"%", int(learn_time), "min")
      except ZeroDivisionError:
          print(int(l_sum/(num_x*num_y*num_g*(360-40-40)/360*num_r)*100),"%","no progress")
      learn_progress = l_sum/(num_x*num_y*num_g*(360-40-40)/360*num_r)*100
    
  graduc = (graduc + 3600) % 360    
    
def attack():
  
  global xm,ym,y_left,timer1,graduc,old_y_left,y_right,old_y_right,speedm
  
  if xm<=170 and xm>=160 and  ym>=y_left-30 and ym<=y_left+130 and time.time()-timer1>=0.5:
    timer1=time.time()
    graduc=360-graduc
    #if debug==0:
    #  print(graduc)
    
    if graduc>90:
      graduc=math.degrees(math.atan((speedm*math.sin(math.radians(graduc-90)))/(speedm*math.cos(math.radians(graduc-90)) - 2*(old_y_left-y_left))))
      graduc += 90
      #if debug==0:
      #  print(graduc)
    else:
      graduc=math.degrees(math.atan((speedm*math.sin(math.radians(graduc)))/(speedm*math.cos(math.radians(graduc)) - 2*(old_y_left-y_left))))
      #if debug==0:
      #  print(graduc)
      
    if(graduc>=160):
      a=160
      
    if(graduc<=20):
      graduc=20
      
  if xm>=xmax-170 and xm<=xmax-160 and ym>=y_right-30 and ym<=y_right+130 and time.time()-timer1>=0.5:
    timer1=time.time()
    graduc=360-graduc
    #if debug==0:
    #  print(graduc)
    
    if graduc>270:
      graduc=math.degrees(math.atan((speedm*math.sin(math.radians(graduc-270)))/(speedm*math.cos(math.radians(graduc-270)) - 0.5*(old_y_right-y_right))))
      graduc += 270
      #if debug==0:
      #  print(graduc)
    else:
      if graduc >180:  
        graduc=math.degrees(math.atan((speedm*math.sin(math.radians(graduc-180)))/(speedm*math.cos(math.radians(graduc-180)) - 0.5*(old_y_right-y_right))))
        graduc += 180
        #if debug==0:
        #  print(graduc)
        
    if(graduc>=340):
      graduc=340
      
    if(graduc<=200):
      graduc=200

def restart():

  global xm,ym,graduc,ugol_spawna

  found = 0
  while found == 0:
    i = int(random.random()*num_x)
    i2 = int(random.random()*num_y)
    i3 = int(random.random()*num_g)
    i4 = int((y_right+65)/(ymax/num_r+1))
      
    if found == 0 and brain[i][i2][i3][i4][0] + brain[i][i2][i3][i4][1] + brain[i][i2][i3][i4][2] == 3:
      xm=(i+0.5)*xmax/num_x
      ym=(i2+0.5)*ymax/num_y
      graduc=(i3+0.5)*360/num_g
      if graduc < 20 or graduc > 340 or graduc > 160 and graduc < 200:
        graduc=ugol_spawna+random.random()*100-50
      print ("+1")
      found = 1
      
def bot():
  
  global gol,xm,ym,graduc,ugol_spawna,p1,p2,P,y_left,u,error,u,old_y_left,old_y_right,y_right,y_speede,ymax,xmax,tmp4

  if gol==1:
    gol=0
    xm=xmax/2
    ym=ymax/2
    graduc=ugol_spawna+random.random()*100-50
    print(str(p1)+":"+str(p2))

    #restart()
        
  tmp1=brain[int((xmax-xm)/(xmax/num_x+1))][int((ymax-ym)/(ymax/num_y+1))][int(((graduc+180+3600)%360)/(360/num_g+1))][int((ymax-(y_left+65))/(ymax/num_r+1))][0]
  tmp2=brain[int((xmax-xm)/(xmax/num_x+1))][int((ymax-ym)/(ymax/num_y+1))][int(((graduc+180+3600)%360)/(360/num_g+1))][int((ymax-(y_left+65))/(ymax/num_r+1))][1]
  tmp3=brain[int((xmax-xm)/(xmax/num_x+1))][int((ymax-ym)/(ymax/num_y+1))][int(((graduc+180+3600)%360)/(360/num_g+1))][int((ymax-(y_left+65))/(ymax/num_r+1))][2]
  tmp4=random.random()*(tmp1+tmp2+tmp3)

  if(tmp4<tmp1):
    y_left+=speedr
    
  if(tmp4>tmp1+tmp2):
    y_left-=speedr
    
#  y_left=y_left+u
  old_y_left=float(y_left)
  old_y_right=float(y_right)    

while 1:
    learn()
    timing()  
    draw()
    control()
    move_ball()
    attack()
    bounce_off_walls()
    bot() 
    clear()


