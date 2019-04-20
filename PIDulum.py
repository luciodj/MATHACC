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

KP = 0.89       
KI = 0.028      
KD = 0.15       

WX = 640        # pixel
WY = 480        

W_GRAPH = 100    # width pixel
N_POINTS = 256  # n points in chart 
X_GRAPH = WX - W_GRAPH/2 
X_SCALE = (W_GRAPH/2) / 10  # scaling of points on the vertical graph

X_ORG = 320     # pixel
Y_GND = 450     # pixel
SCALE = 800     # pixel/m

WEIGHT  = 0.300 # kg
LENGTH  = 0.30  # m
DELTA_T = 0.01  # s
GRAVITY = -9.81 # m/s2

fire = False

class PID(object):
    'Proportional Integral and Derivative controller'
    def __init__(self, k_p, k_i, k_d):
        self.k_p = k_p * DELTA_T
        self.k_i = k_i * DELTA_T * DELTA_T
        self.k_d = k_d
        self.integral = 0
        self.error = 0

    def compute(self, error):
        'perform a step in the simulation'
        self.integral += error 
        derivative = (error - self.error)
        self.error = error
        return self.error * self.k_p + derivative * self.k_d + self.integral * self.k_i
       

#
# pendulum
#
class Pendulum(object):
    'an inverted pendulum on a moving base '
    def __init__(self, canvas):
        self.canvas = canvas
        self.vb = 0 # base speed fixed for now
        self.x = X_ORG  
        self.a = (math.pi/2) + 0.01 # -90 deg, start vertical
        self.va = 0  # angular velocity
        self.vx = 0  # horziontal speed 
        self.vy = 0  # vertical speed
        # self.pid = PID(KP, KI, KD)
        self.pendulum = self.canvas.create_line( X_ORG, Y_GND, X_ORG, Y_GND, width=2, fill='red')
        self.top = self.canvas.create_oval(X_ORG-5, Y_GND-5, X_ORG+5, Y_GND+5, fill='red')
        self.canvas.create_rectangle(WX-W_GRAPH, Y_GND - N_POINTS, WX, Y_GND, outline='green', fill='black')
        self.points = []
        self.npoints = 0
        self.gline = None
        self.draw()

    def update(self):
        'perform one step in the physics simulation'
        self.va += GRAVITY * math.cos(self.a) / LENGTH * DELTA_T   # gravity component
        # self.vx += self.vb * DELTA_T    # horiz base component

        # integrations
        self.a += self.va * DELTA_T

        # checks 
        if self.a > math.pi : 
            self.a = math.pi
            self.va = -self.va * .9
        if self.a < 0 : 
            self.a = 0
            self.va = -self.va * .9
        
        # add to chart
        self.points.append(self.va)

    def draw(self):
        'initial drawing of the pendulum'
        x = X_ORG + LENGTH * math.cos(self.a) * SCALE
        y = Y_GND - LENGTH * math.sin(self.a) * SCALE
        self.canvas.coords(self.pendulum, x, y, X_ORG, Y_GND)
        self.canvas.coords(self.top, x-5, y-5, x+5, y+5)

        'draw graph(s)'
        self.canvas.delete(self.gline)
        series = []
        n = len(self.points)
        if n > N_POINTS : self.points.pop(0)
        if n > 1 :
            for i,x in enumerate(self.points):
                series.append( (X_GRAPH + x * X_SCALE, Y_GND-n+i))
            self.gline = self.canvas.create_line(series, fill='green')

        # print('Va =', self.va)

        
#
# dialog window
#
class APPWindow(object):
    'main and only application window'
    def __init__(self):
        self.fire = False
        self.pid = PID(KP, KI, KD)
        win = tk.Tk()
        win.title('This is Rocket Science')
        win.protocol('WM_DELETE_WINDOW', self.cmd_quit) # intercept Ctrl_Q and Close Window button
        self.win = win
        self.use_pid = tk.BooleanVar()
        self.use_pid.set(False)

        #------- draw canvas ----------------------------
        brd = 2
        self.brd = brd
        tk_rgb = "#%02x%02x%02x" % (55, 132, 191) # book cover color
        graph = tk.Canvas(win, width=WX, height=WY, relief='flat', bd=brd, bg=tk_rgb)
        graph.grid(padx=10, row=2, columnspan=4)
        self.graph = graph

        #------- draw reference lines
        graph.create_line(0, Y_GND, WX, Y_GND, fill='white')
        # graph.create_line(0, Y_GND-SET_ALTITUDE, X_RKT-50, Y_GND-SET_ALTITUDE, fill='white')

        #------- create the rocket --------------------------
        self.pendulum = Pendulum(self.graph)
        graph.bind('<Button-1>', self.cmd_fire)   # capture mouse button inside canvas

        #------- buttons   -----------------------------------
        tk.Button(win, text='Reset',
                  command=self.cmd_reset).grid(padx=10, pady=10, row=3, column=0)
        tk.Button(win, text='Close',
                  command=self.cmd_quit).grid(padx=10, pady=10, row=3, column=3)
        # tk.Radiobutton(win, text='MATHACC', variable=self.use_pid,
                    #    value=True).grid(padx=10, pady=10, row=3, column=1)
        # tk.Radiobutton(win, text='Manual', variable=self.use_pid,
                    #    value=False).grid(padx=10, pady=10, row=3, column=2)
        self.win.after(0, self.animation)

    #-------------------- Window methods
    def cmd_reset(self):
        'reposition the pendulum upright'
        self.pendulum.a = math.pi/2 + random.random() * 0.2 - 0.1
        self.pendulum.va = 0
        self.pendulum.draw()

    def cmd_quit(self):
        'exit application'
        self.win.quit()

    def cmd_fire(self, _):
        'start simulation'
        self.fire = True

    def animation(self):
        'animation step'
        # if self.use_pid.get():      # automatic
            # thrust = self.pid.compute(SET_ALTITUDE - self.rocket.y)
            # valve control <0.0 - 1.0>
            # if thrust < 0.0:
                # thrust = 0.0
            # elif thrust > 1.0:
                # thrust = 1.0
        # else:   # manual
            # if self.fire > 0:
                # self.fire -= 1
            # thrust = 1.0 if self.fire > 0 else 0
        if self.fire :
            self.pendulum.update()
            self.pendulum.draw()
        self.win.after(int(1000*DELTA_T), self.animation) # delay in ms

if __name__ == '__main__':
    APPWindow()
    tk.mainloop()