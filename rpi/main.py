#!/usr/bin/env python3

from flask import Flask, render_template, Response
import serial, time, cv2, threading, math, socket
import numpy as np
from imutils.video import WebcamVideoStream

sock = socket.socket()
sock.connect(('192.168.32.209', 9090))

font = cv2.FONT_HERSHEY_SIMPLEX

x_ball = 320
y_ball = 240

oldx_ball = 320
oldy_ball = 240

time_vector_ball = time.time()
fps_main = 0
time_fps_main = time.time()
i_fps_main = 0

x_ball_array = [320]
y_ball_array = [240]

e_ball = 0
e_time_ball = 0
see_ball = 1
not_see_ball = 1

point_goal_left = 0
point_goal_right = 0
point_goal_right_old = 0
point_goal_left_old = 0
time_goal = time.time()

y_my_racket = 0
y_cos = 0

x_racket = 0
y_racket = 0

drav_racket = []
drav_con = []
drav_ball = []
drav_area = []
drav_control_ball = []

sock_medium_send = 0
K = 0.3

game_frame_xmin = 0
game_frame_xmax = 640

game_frame_ymin = 40
game_frame_ymax = 450

game_area_xmin = 0
game_area_xmax = 0

game_area_ymin = 0
game_area_ymax = 0

cap = WebcamVideoStream(src=0).start()
frame = cap.read()
hsv = cv2.cvtColor(frame[game_frame_ymin:game_frame_ymax, :, :], cv2.COLOR_BGR2HSV)
frame_gray = cv2.inRange(hsv, (0, 0, 250), (255, 255, 255))
_, con, hierarchy = cv2.findContours(frame_gray.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for cnt in con:
    if(cnt is not None):
        area = cv2.contourArea(cnt)
        if(area>=500 and area <= 1500):
            drav_con.append(cnt)
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            if((box[0, 0] + box[2, 0])/2 > 480):
                game_frame_xmax = int((box[0, 0] + box[2, 0])/2) + 5
            if((box[0, 0] + box[2, 0])/2 < 120):
                game_frame_xmin = int((box[0, 0] + box[2, 0])/2) - 5

if(game_frame_xmin < 0): game_frame_xmin = 0

game_area_xmin = 0
game_area_xmax = game_frame_xmax - game_frame_xmin
game_area_ymin = 0
game_area_ymax = game_frame_ymax - game_frame_ymin

print(game_frame_xmin, game_frame_xmax)

cv2.imwrite('/var/www/html/frame.png', frame)

def intersection_of_lines(x1, y1, x2, y2, x3, y3, x4, y4):
    X = ((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4))/(((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))+0.1)
    Y = ((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/(((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))+0.1)
    return int(X), int(Y)

def control_ball(oldx, oldy, x, y, vl):
    if(x == oldx or y == oldy or vl>=5): return -1
    Xu, Yu = intersection_of_lines(x, y, oldx, oldy, 0, 0, 100, 0)
    Xr, Yr = intersection_of_lines(x, y, oldx, oldy, game_area_xmax, 0, game_area_xmax, 100)
    Xd, Yd = intersection_of_lines(x, y, oldx, oldy, 0, game_area_ymax, 100, game_area_ymax)
    Xl, Yl = intersection_of_lines(x, y, oldx, oldy, 20, 0, 20, 100)

    if((y - oldy) < 0 and Xu>=game_area_xmin and Xu<=game_area_xmax and Yu>=game_area_ymin and Yu<=game_area_ymax):
        drav_control_ball.append( ((oldx, oldy), (Xu, Yu)) )
        return control_ball(Xu, Yu, Xu+(x-oldx), Yu-(y-oldy), vl+1)
    elif((x - oldx) > 0 and Xr>=game_area_xmin and Xr<=game_area_xmax and Yr>=game_area_ymin and Yr<=game_area_ymax):
        drav_control_ball.append( ((oldx, oldy), (Xr, Yr)) )
        return Yr
    elif((y - oldy) > 0 and Xd>=game_area_xmin and Xd<=game_area_xmax and Yd>=game_area_ymin and Yd<=game_area_ymax):
        drav_control_ball.append( ((oldx, oldy), (Xd, Yd)) )
        return control_ball(Xd, Yd, Xd+(x-oldx), Yd-(y-oldy), vl+1)
    elif((x - oldx) < 0 and Xl>=game_area_xmin and Xl<=game_area_xmax and Yl>=game_area_ymin and Yl<=game_area_ymax):
        drav_control_ball.append( ((oldx, oldy), (Xl, Yl)) )
        return control_ball(Xl, Yl, Xl-(x-oldx), Yl+(y-oldy), vl+1)

def image2jpeg(image):
    ret, jpeg = cv2.imencode('.jpg', image)
    return jpeg.tobytes()

def camera2inet():
    global x_cos, y_cos
    print("Start inet thread")
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')

    def gen():
        while True:
            frame_inet = cv2.inRange(hsv, (0, 0, 250), (255, 255, 255))
            frame_inet = cv2.cvtColor(frame_inet, cv2.COLOR_GRAY2RGB)

            cv2.putText(frame_inet, "X,Y Racket - " + str(x_racket) + " : " + str(y_racket), (5,25), font, 0.3, (0,255,255), 1, cv2.LINE_AA)
            cv2.putText(frame_inet, "X,Y,E Ball - " + str(x_ball) + " : " + str(y_ball) + " : " + str(e_ball) + "%", (5,35), font, 0.3, (0,255,255), 1, cv2.LINE_AA)
            cv2.putText(frame_inet, "FPSMain - " + str(fps_main), (5,45), font, 0.3, (0,255,255), 1, cv2.LINE_AA)

            for i in drav_racket: cv2.drawContours(frame_inet, [i], 0, (255,0,0), 2)

            #cv2.line(frame_inet, (int(game_area_xmax/2-50), 0), (int(game_area_xmax/2-50), game_area_xmax), (0, 0, 255), 1)
            #cv2.line(frame_inet, (int(game_area_xmax/2+50), 0), (int(game_area_xmax/2+50), game_area_xmax), (0, 0, 255), 1)

            cv2.rectangle(frame_inet, (oldx_ball-3, oldy_ball-3), (oldx_ball+3, oldy_ball+3), (50,150,0),3)
            cv2.rectangle(frame_inet, (game_area_xmax-20, int(y_my_racket)-30), (game_area_xmax-5, int(y_my_racket)+30), (0,255,0),3)
            #cv2.rectangle(frame_inet, (game_area_xmax-5, y_cos-15), (game_area_xmax ,y_cos+15), (0,255,0),2)

            for i in drav_ball: cv2.drawContours(frame_inet, [i], 0, (0,0,255), 2)
            for i in drav_control_ball:
                t1, t2 = i
                cv2.line(frame_inet, t1, t2, (0, 255,0), 1)

            frameinet = image2jpeg(frame_inet)
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frameinet + b'\r\n\r\n')
    def gen_cl():
        while True:
            frame_inet = frame[game_frame_ymin:game_frame_ymax, :, :]
            frameinet = image2jpeg(frame_inet)
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frameinet + b'\r\n\r\n')
    @app.route('/video')
    def video():
        return Response(gen(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    @app.route('/video_cl')
    def video_cl():
        return Response(gen_cl(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    app.run(host='0.0.0.0', debug=False,threaded=True)

pr1 = threading.Thread(target=camera2inet)
pr1.daemon = True
pr1.start()

while 1:
    frame = cap.read()
    hsv = cv2.cvtColor(frame[game_frame_ymin:game_frame_ymax, game_frame_xmin:game_frame_xmax, :], cv2.COLOR_BGR2HSV)
    frame_gray = cv2.inRange(hsv, (0, 0, 250), (255, 255, 255))
    _, con, hierarchy = cv2.findContours(frame_gray.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    drav_racket.clear()
    drav_con.clear()
    drav_ball.clear()
    drav_area.clear()
    drav_control_ball.clear()

    cos = control_ball(oldx_ball, oldy_ball, x_ball, y_ball, 1)

    if(cos is not None and cos != -1):
        y_cos = cos

    y_my_racket = y_my_racket*0.95 + y_cos*0.05

    #if(y_racket > y_cos+25):
    #    sock_medium_send = sock_medium_send*K + 1*(1-K)
    #elif(y_racket < y_cos-25):
    #    sock_medium_send = sock_medium_send*K + -1*(1-K)
    #else: sock_medium_send = 0
    #send_on_ev3 = ""
    #if(sock_medium_send > 0.8): send_on_ev3 = "U"
    #elif(sock_medium_send < -0.8): send_on_ev3 = "D"
    #else: send_on_ev3 = "N"
    #send_on_ev3 += str(point_goal_left) + str(point_goal_right)
    #sock.send(send_on_ev3.encode())

    send_on_ev3 = ""
    if(y_racket > y_my_racket+20): send_on_ev3 = "U"
    elif(y_racket < y_my_racket-20): send_on_ev3 = "D"
    else: send_on_ev3 = "N"
    if(point_goal_right_old != point_goal_right):
        send_on_ev3 += "R"
        point_goal_right_old = point_goal_right
    elif(point_goal_left_old != point_goal_left):
        send_on_ev3 += "L"
        point_goal_left_old = point_goal_left
    else:
        send_on_ev3 += "N"
    sock.send(send_on_ev3.encode())

    for cnt in con:
        if(cnt is not None):
            area = cv2.contourArea(cnt)
            if(area>=500 and area <= 1500):
                drav_con.append(cnt)
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                if((box[0, 0] + box[1, 0])/2 > 480):
                    drav_racket.append(np.int0(box))
                    x_racket = int((box[0, 0] + box[2, 0])/2)
                    y_racket = int((box[0, 1] + box[2, 1])/2)
            if(area>=20 and area <= 400):
                drav_con.append(cnt)
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                drav_ball.append(np.int0(box))
                x_ball = int((box[0, 0] + box[2, 0])/2)
                y_ball = int((box[0, 1] + box[2, 1])/2)
                if(len(x_ball_array) > 20):
                    for i in range(len(x_ball_array)):
                        if(i != len(x_ball_array)-1):
                            x_ball_array[i] = x_ball_array[i+1]
                            y_ball_array[i] = y_ball_array[i+1]
                        else:
                            x_ball_array[i] = x_ball
                            y_ball_array[i] = y_ball
                else:
                    x_ball_array.append(x_ball)
                    y_ball_array.append(y_ball)

                oldx_ball = x_ball_array[0]
                oldy_ball = y_ball_array[0]
                see_ball+=1
            else:
                not_see_ball+=1

            e_ball = int(not_see_ball/(not_see_ball+see_ball)*100)

            if(time.time() - e_time_ball > 5):
                see_ball = 1
                not_see_ball = 1
                e_time_ball = time.time()
    if(x_ball > (game_area_xmax/2-50) and x_ball < (game_area_xmax/2+50) and time.time()-time_goal > 2):
        for i in x_ball_array:
            if(i > (game_area_xmax-30)):
                time_goal = time.time()
                point_goal_left_old = point_goal_left
                point_goal_left += 1
                print(point_goal_left, ":", point_goal_right)
                break
            elif(i < 30):
                time_goal = time.time()
                point_goal_right_old = point_goal_right
                point_goal_right += 1
                print(point_goal_left, ":", point_goal_right)
                break
    if(time.time() - time_fps_main > 5):
        time_fps_main = time.time()
        fps_main = i_fps_main/5
        i_fps_main = 0
    i_fps_main += 1
