#! /usr/bin/env python3
"""
Inverted Pendulum PID demo
Author: Lucio Di Jasio
twitter: @luciodjs
url: https://flyingpic24.com
"""
import tkinter as tk
import math
import random

KP = 0.70       
KI = 0.20      
KD = 0.40       

WX = 640        # pixel
WY = 480        

W_GRAPH = 100    # width pixel
N_POINTS = WY-60  # n points in chart 
X_GRAPH =  W_GRAPH/2 
G_SCALE = (W_GRAPH/2) / 10  # scaling of points on the  graph

X_ORG = WX/2    # pixel
Y_GND = WY-30   # pixel
SCALE = 400     # pixel/m

WEIGHT  = 0.300 # kg
LENGTH  = 0.30  # m
DELTA_T = 0.01  # s
GRAVITY = -9.81 # m/s2
TORQUE  = 1000  # kgm/s2
KICK    = 0.2   # m

class Sim(object):
    fire = False
    
class PID(object):
    'Proportional Integral and Derivative controller'
    k_p = 1.0
    k_i = 0
    k_d = 0

    def __init__(self, k_p, k_i, k_d):
        self.set(k_p, k_i, k_d)
        self.integral = 0
        self.error = 0

    def set(self, k_p, k_i, k_d):
        PID.k_p = k_p * DELTA_T
        PID.k_i = k_i * DELTA_T * DELTA_T
        PID.k_d = k_d


    def compute(self, error):
        'perform a step in the simulation'
        self.integral += error 
        derivative = (error - self.error)
        self.error = error
        return self.error * PID.k_p + derivative * PID.k_d + self.integral * PID.k_i
       
def update_pid(value):
    PID.set(PID, app.Kp.get(), app.Ki.get(), app.Kd.get())

#
# pendulum
#
class Pendulum(object):
    'an inverted pendulum on a moving base '
    def __init__(self, canvas, graph):
        self.canvas = canvas
        self.graph = graph
        self.vb = 0 # base speed fixed for now
        self.x = 0  
        self.tx = 0
        self.vtx = 0
        self.ty = LENGTH
        self.vx = 0  # horziontal speed 
        self.a = (math.pi/2)  # -90 deg, start vertical
        self.stick = self.canvas.create_line( X_ORG, Y_GND, X_ORG, Y_GND, width=2, fill='red')
        self.top = self.canvas.create_oval(X_ORG-5, Y_GND-5, X_ORG+5, Y_GND+5, fill='red')
        self.points = []
        self.npoints = 0
        self.F = 0
        self.gline = None
        self.pid = PID(KP, KI, KD) 
        self.draw()

    def update(self):
        'perform one step in the physics simulation'
        pid = self.pid.compute(math.pi/2 - self.a)    # compute error as the angle diff from vertical

        # integrate forces
        self.vtx += -GRAVITY * math.cos(self.a) * DELTA_T   # gravity component
        self.vx += self.F / WEIGHT * math.sin(self.a) * DELTA_T # base velocity

        # integrations
        self.tx += self.vtx * DELTA_T
        self.x += self.vx * DELTA_T

        dx = self.tx - self.x

        # checks 
        if abs(dx) > LENGTH: 
            self.ty = 0
            dx = LENGTH * dx/abs(dx)
            self.tx = self.x + LENGTH * dx/abs(dx)
        else : 
            self.ty = math.sqrt(LENGTH * LENGTH - dx * dx)
        self.a = math.acos(dx / LENGTH)
        
        if self.x < -WX/SCALE  or self.x > WX/SCALE: 
            Sim.fire = False
        if self.a > math.pi or self.a < 0:
            Sim.fire = False
         
        # updates
        self.F = pid * TORQUE

        # add to chart
        self.points.append(pid * X_GRAPH*10)

    def draw(self):
        'draw the pendulum'
        px = X_ORG + self.tx * SCALE
        py = Y_GND - self.ty * SCALE
        self.canvas.coords(self.stick, px, py, X_ORG + self.x * SCALE, Y_GND)
        self.canvas.coords(self.top, px-5, py-5, px+5, py+5)

        'draw graph(s)'
        self.graph.delete(self.gline)
        series = []
        n = len(self.points)
        if n > N_POINTS : self.points.pop(0)
        if n > 1 :
            for i,x in enumerate(self.points):
                series.append( (X_GRAPH + x * G_SCALE, Y_GND-n+i))
            self.gline = self.graph.create_line(series, fill='green')

#
# dialog window
#
class APPWindow(object):
    'main and only application window'
    def __init__(self):
        Sim.fire = False
        self.pid = PID(KP, KI, KD)
        win = tk.Tk()
        win.title('This is Rocket Science')
        win.protocol('WM_DELETE_WINDOW', self.cmd_quit) # intercept Ctrl_Q and Close Window button
        self.win = win
        self.Kp = tk.DoubleVar()
        self.Kp.set(KP)
        self.Ki = tk.DoubleVar()
        self.Ki.set(KI)
        self.Kd = tk.DoubleVar()
        self.Kd.set(KD)

        #------- draw plane canvas ----------------------------
        brd = 2
        self.brd = brd
        tk_rgb = "#%02x%02x%02x" % (55, 132, 191) # book cover color
        plane = tk.Canvas(win, width=WX, height=WY, relief='flat', bd=brd, bg=tk_rgb)
        plane.grid(padx=10, row=2, columnspan=3)
        self.plane = plane

        #------- draw reference lines
        plane.create_line(0, Y_GND, WX, Y_GND, fill='white')
        plane.create_line(X_ORG, Y_GND, X_ORG, Y_GND + 5, fill='white')

        #------- draw graph canvas ----------------------------
        graph = tk.Canvas(win, width=W_GRAPH, height=WY, relief='flat', bg='black')
        graph.grid(padx=10, row=2, column=3)
        self.graph = graph

        #------- create the pendulum --------------------------
        self.pendulum = Pendulum(plane, graph)
        plane.bind('<Button-1>', self.cmd_fire)   # capture mouse button inside plane

        #------- buttons   -----------------------------------
        tk.Button(win, text='Kick',
                  command=self.cmd_reset).grid(padx=10, pady=10, row=3, column=0)
        tk.Button(win, text='Close',
                  command=self.cmd_quit).grid(padx=10, pady=10, row=3, column=3)
        tk.Scale(win, label='Kp', variable=self.Kp, from_=0.0, to=1.0, resolution=0.05, 
                command=update_pid).grid(padx=10, sticky='NS', pady=10, row=2, column=4)
        tk.Scale(win, label='Ki', variable=self.Ki, from_=0.0, to=1.0, resolution=0.05, 
                command=update_pid).grid(padx=10, sticky='NS', pady=10, row=2, column=5)
        tk.Scale(win, label='Kd', variable=self.Kd, from_=0.0, to=1.0, resolution=0.05, 
                command=update_pid).grid(padx=10, sticky='NS', pady=10, row=2, column=6)
        # start the loop
        self.win.after(0, self.animation)

    #-------------------- Window methods
         
    def cmd_reset(self):
        'reposition the pendulum upright'
        self.pendulum.x = 0
        self.pendulum.tx = random.random() * KICK *2  - KICK
        self.pendulum.ty = LENGTH
        self.pendulum.vx = 0
        self.pendulum.vtx = 0
        self.pendulum.draw()
        self.pendulum.pid.integral = 0
        self.pendulum.pid.error = 0
        Sim.fire = False

    def cmd_quit(self):
        'exit application'
        self.win.quit()

    def cmd_fire(self, _):
        'start simulation'
        Sim.fire = True

    def animation(self):
        'animation step'
        if Sim.fire :
            self.pendulum.update()
            self.pendulum.draw()
        self.win.after(int(1000*DELTA_T), self.animation) # delay in ms

if __name__ == '__main__':
    app = APPWindow()
    tk.mainloop()
