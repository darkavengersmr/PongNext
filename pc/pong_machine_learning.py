# -*- coding: cp1251 -*-
import pygame
import math
import random
import time
import threading
import numpy as np

rebound=0

num_x=8
num_y=6
num_g=18
num_r=10
num_k=3

num_hist = 400

brain=np.ones((num_x,num_y,num_g,num_r,num_k))   
history_left=np.ones((num_hist,5))
history_right=np.ones((num_hist,5))
reboundchetleft=0
reboundchetright=0
xmax=1600
ymax=900
pygame.init()
error=0
P=0.02
#sc = pygame.display.set_mode((xmax,ymax),pygame.FULLSCREEN)
sc = pygame.display.set_mode((xmax,ymax),pygame.RESIZABLE)
timer1=time.time()
pygame.display.update()
debug=1;

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
speedm=2
speedr=2
learn_i=0
tmp4=0
tmp4_2=0
  
def control():
  global y_speed,speedr,f,brain
  
  for event in pygame.event.get():
    y_speed=0     
    if event.type == pygame.QUIT: exit()     
    if event.type == pygame.KEYDOWN: 
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
                  brain[i][i2][i3][i4][i5]=int(stringtmp)                  
        f.close()
        
      if event.key == pygame.K_v:
        pygame.quit()
        
def clear():
  global sc,xmax,y_left,y_right,xm,ym
  pygame.draw.rect(sc, (255, 255, 255), (xmax-160, y_right, 30, 130))
  pygame.draw.rect(sc, (255, 255, 255), (160, y_left, 30, 130))    
  pygame.draw.rect(sc, (255,255,255), (xm, ym,30,30))
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
    gol=2
    p2+=1
    ugol_spawna=90
    
def timing():
  
  global vr,timer2,P,graduc,tmp4,learn_i
  

  if time.time()-timer2>=10:
    print(int(100*reboundchetleft/(reboundchetleft+p2+1)),int(100*reboundchetright/(reboundchetright+p1+1)), learn_i)
    P=random.random()
    timer2=time.time()
    #if debug==0:
    #  print(learn_i,tmp4)
    
  graduc = (graduc + 3600) % 360    
    
def attack():
  
  global reboundchetleft,reboundchetright,rebound,xm,ym,y_left,timer1,graduc,old_y_left,y_right,old_y_right,speedm
  
  if xm<=170 and xm>=160 and  ym>=y_left-30 and ym<=y_left+130 and time.time()-timer1>=0.5:
    rebound=1
    reboundchetleft+=1
    
    timer1=time.time()
    graduc=360-graduc
    if debug==0:
      print(graduc)
    
    if graduc>90:
      graduc=math.degrees(math.atan((speedm*math.sin(math.radians(graduc-90)))/(speedm*math.cos(math.radians(graduc-90)) - 2*(old_y_left-y_left))))
      graduc += 90
      if debug==0:
        print(graduc)
    else:
      graduc=math.degrees(math.atan((speedm*math.sin(math.radians(graduc)))/(speedm*math.cos(math.radians(graduc)) - 2*(old_y_left-y_left))))
      if debug==0:
        print(graduc)
      
    if(graduc>=160):
      a=160
      
    if(graduc<=20):
      graduc=20
      
  if xm>=xmax-170 and xm<=xmax-160 and ym>=y_right-30 and ym<=y_right+130 and time.time()-timer1>=0.5:
    rebound=2
    reboundchetright+=1
    
    timer1=time.time()
    graduc=360-graduc
    if debug==0:
      print(graduc)
    
    if graduc>270:
      graduc=math.degrees(math.atan((speedm*math.sin(math.radians(graduc-270)))/(speedm*math.cos(math.radians(graduc-270)) - 0.5*(old_y_right-y_right))))
      graduc += 270
      if debug==0:
        print(graduc)
    else:
      if graduc >180:  
        graduc=math.degrees(math.atan((speedm*math.sin(math.radians(graduc-180)))/(speedm*math.cos(math.radians(graduc-180)) - 0.5*(old_y_right-y_right))))
        graduc += 180
        if debug==0:
          print(graduc)
        
    if(graduc>=340):
      graduc=340
      
    if(graduc<=200):
      graduc=200
      
def bot_and_restar():
  
  global learn_i,sc,rebound,brain,history_left,history_ryght,gol,xm,ym,graduc,ugol_spawna,p1,p2,P,tmp4_2,y_left,u,error,u,old_y_left,old_y_right,y_right,y_speede,ymax,xmax,tmp4
  
  if gol>0:
    
    xm=xmax/2
    ym=ymax/2
    graduc=ugol_spawna+random.random()*100-50

    if gol==1:
      if brain[int(history_left[num_hist-2][0])][int(history_left[num_hist-2][1])][int(history_left[num_hist-2][2])][int(history_left[num_hist-2][3])][int(history_left[num_hist-2][4])]>1:
     
        brain[int(history_left[num_hist-2][0])][int(history_left[num_hist-2][1])][int(history_left[num_hist-2][2])][int(history_left[num_hist-2][3])][int(history_left[num_hist-2][4])]-=0
    if gol==2:
      if brain[int(history_right[num_hist-2][0])][int(history_right[num_hist-2][1])][int(history_right[num_hist-2][2])][int(history_right[num_hist-2][3])][int(history_right[num_hist-2][4])]>1:

        brain[int(history_right[num_hist-2][0])][int(history_right[num_hist-2][1])][int(history_right[num_hist-2][2])][int(history_right[num_hist-2][3])][int(history_right[num_hist-2][4])]-=0
    gol=0           
  if rebound>0:
    if rebound==1:
      for i in range(num_hist):
        brain[int(history_left[i][0])][int(history_left[i][1])][int(history_left[i][2])][int(history_left[i][3])][int(history_left[i][4])]+=1
        learn_i += 1
    if rebound==2:
      for i in range(num_hist):
        brain[int(history_right[i][0])][int(history_right[i][1])][int(history_right[i][2])][int(history_right[i][3])][int(history_right[i][4])]+=1
        learn_i += 1
    rebound=0  
  tmp1=brain[int((xmax-xm)/(xmax/num_x+1))][int((ymax-ym)/(ymax/num_y+1))][int(((graduc+180+3600)%360)/(360/num_g+1))][int((ymax-y_left)/(ymax/num_r+1))][0]
  tmp2=brain[int((xmax-xm)/(xmax/num_x+1))][int((ymax-ym)/(ymax/num_y+1))][int(((graduc+180+3600)%360)/(360/num_g+1))][int((ymax-y_left)/(ymax/num_r+1))][1]
  tmp3=brain[int((xmax-xm)/(xmax/num_x+1))][int((ymax-ym)/(ymax/num_y+1))][int(((graduc+180+3600)%360)/(360/num_g+1))][int((ymax-y_left)/(ymax/num_r+1))][2]
  tmp4=random.random()*(tmp1+tmp2+tmp3)
  for i in range(num_hist-1):
    history_left[i][0]=history_left[i+1][0]
    history_left[i][1]=history_left[i+1][1]
    history_left[i][2]=history_left[i+1][2]
    history_left[i][3]=history_left[i+1][3]
    history_left[i][4]=history_left[i+1][4]       
  if(tmp4<tmp1):
    y_left+=speedr
    history_left[num_hist-1][0]= int((xmax-xm)/(xmax/num_x+1)) 
    history_left[num_hist-1][1]= int((ymax-ym)/(ymax/num_y+1))
    history_left[num_hist-1][2]= int(((graduc+180+3600)%360)/(360/num_g+1))
    history_left[num_hist-1][3]= int((ymax-y_left)/(ymax/num_r+1))
    history_left[num_hist-1][4]=0
  elif(tmp4>tmp1+tmp2):
    y_left-=speedr
    history_left[num_hist-1][0]= int((xmax-xm)/(xmax/num_x+1))
    history_left[num_hist-1][1]= int((ymax-ym)/(ymax/num_y+1))
    history_left[num_hist-1][2]= int(((graduc+180+3600)%360)/(360/num_g+1))
    history_left[num_hist-1][3]= int((ymax-y_left)/(ymax/num_r+1))
    history_left[num_hist-1][4]=2
  else:
    history_left[num_hist-1][0]= int((xmax-xm)/(xmax/num_x+1))
    history_left[num_hist-1][1]= int((ymax-ym)/(ymax/num_y+1))
    history_left[num_hist-1][2]= int(((graduc+180+3600)%360)/(360/num_g+1))
    history_left[num_hist-1][3]= int((ymax-y_left)/(ymax/num_r+1))
    history_left[num_hist-1][4]=1    
  tmp1_2=brain[int(xm/(xmax/num_x+1))][int(ym/(ymax/num_y+1))][int((graduc/(360/num_g+1)))][int(y_right/(ymax/num_r+1))][2]
  tmp2_2=brain[int(xm/(xmax/num_x+1))][int(ym/(ymax/num_y+1))][int((graduc/(360/num_g+1)))][int(y_right/(ymax/num_r+1))][1]
  tmp3_2=brain[int(xm/(xmax/num_x+1))][int(ym/(ymax/num_y+1))][int((graduc/(360/num_g+1)))][int(y_right/(ymax/num_r+1))][0]
  tmp4_2=random.random()*(tmp1_2+tmp2_2+tmp3_2)
  for i in range(num_hist-1):
    history_right[i][0]=history_right[i+1][0]
    history_right[i][1]=history_right[i+1][1]
    history_right[i][2]=history_right[i+1][2]
    history_right[i][3]=history_right[i+1][3]
    history_right[i][4]=history_right[i+1][4] 
  if(tmp4_2<tmp1_2):
    y_right+=speedr
    history_right[num_hist-1][0]= int(xm/(xmax/num_x+1))
    history_right[num_hist-1][1]= int(ym/(ymax/num_y+1))
    history_right[num_hist-1][2]= int(graduc/(360/num_g+1))
    history_right[num_hist-1][3]= int(y_right/(ymax/num_r+1))
    history_right[num_hist-1][4]=2    
  elif(tmp4_2>tmp1_2+tmp2_2):
    y_right-=speedr
    history_right[num_hist-1][0]= int(xm/(xmax/num_x+1))
    history_right[num_hist-1][1]= int(ym/(ymax/num_y+1))
    history_right[num_hist-1][2]= int(graduc/(360/num_g+1))
    history_right[num_hist-1][3]= int(y_right/(ymax/num_r+1))
    history_right[num_hist-1][4]=0  
  else:
    history_right[num_hist-1][0]= int(xm/(xmax/num_x+1))
    history_right[num_hist-1][1]= int(ym/(ymax/num_y+1))
    history_right[num_hist-1][2]= int(graduc/(360/num_g+1))
    history_right[num_hist-1][3]= int(y_right/(ymax/num_r+1))
    history_right[num_hist-1][4]=1                                
#  y_left=y_left+u
  old_y_left=float(y_left)
  old_y_right=float(y_right)    

while 1:
    timing()  
    draw()
    control()
    move_ball()
    attack()
    bounce_off_walls()
    bot_and_restar() 
    clear()


