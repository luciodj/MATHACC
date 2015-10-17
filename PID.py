#!usr/bin/env python
"""
Rocket Science PID-MATHACC demo
Author: Lucio Di Jasio
twitter: @luciodjs
url: https://flyingpic24.com/rocket
"""
import Tkinter as tk

KP = 0.89      # 0.89
KI = 0.028     # 0.028
KD = 0.15      # 0.15
SET_ALTITUDE = 250

WX = 640
WY = 480
IMG_OFFSET = 80
W_TANK = 20
X_RKT = 320
Y_GND = 450
Y_RKT = Y_GND - IMG_OFFSET

TARE = 30.0
FUEL = 70.0
DELTA_T = 0.01
FULL_WEIGHT = TARE + FUEL
GRAVITY = 9.81 * DELTA_T
MAX_THRUST = GRAVITY * 1.05 * FULL_WEIGHT
FUEL_BURN = FUEL / 6000     # enough fuel for 60 seconds at full burn


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
        self.integrate(error)
        derivative = (error - self.error)
        self.error = error
        return self.error * self.k_p + derivative * self.k_d + self.integral * self.k_i

    def integrate(self, error):
        'accumulate the error'
        self.integral += error

#
# rocket
#
class Rocket(object):
    'Rocketship '
    def __init__(self, canvas):
        self.canvas = canvas
        self.x = X_RKT
        self.y = 0
        self.v = 0
        self.weight = TARE
        self.draw_rocket()
        self.draw_fuel()
        self.pid = PID(KP, KI, KD)

    def update(self, thrust):
        'perform one step in the rocket physics simulation'
        if self.weight < TARE:
            thrust = 0  # out of gas
        acceleration = -GRAVITY + thrust * MAX_THRUST / self.weight
        self.v += acceleration
        self.y += self.v * 0.1  # scale 1 pixel = 10m
        if self.y < 0:
            self.v = self.y = 0
        self.redraw_rocket(thrust)
        self.weight -= FUEL_BURN * thrust
        self.redraw_fuel()

    def draw_rocket(self):
        'initial drawing of the rocket'
        self.img = tk.PhotoImage(file='rocket.gif')
        self.id = self.canvas.create_image(self.x, Y_RKT-self.y, image=self.img)
        self.xflame1 = self.x-25
        self.xflame2 = self.x+24
        self.flame1 = self.canvas.create_line(self.xflame1, Y_GND-self.y,
                                              self.xflame1, Y_GND-self.y,
                                              width=2, fill='red')
        self.flame2 = self.canvas.create_line(self.xflame2, Y_RKT-self.y,
                                              self.xflame2, Y_RKT-self.y,
                                              width=2, fill='red')

    def redraw_rocket(self, thrust):
        'update rocket position'
        self.canvas.coords(self.id, self.x, Y_RKT-self.y)
        self.canvas.coords(self.flame1,
                           self.xflame1, Y_GND-self.y,
                           self.xflame1, Y_GND-self.y+thrust*30)
        self.canvas.coords(self.flame2,
                           self.xflame2, Y_GND-self.y,
                           self.xflame2, Y_GND-self.y+thrust*30)

    def draw_fuel(self):
        'draw fuel tank and level'
        self.canvas.create_rectangle(WX-W_TANK, Y_GND-FUEL*4, WX, Y_GND, outline='white')
        self.tank = self.canvas.create_rectangle(WX-W_TANK, Y_GND-(self.weight-TARE)*4,
                                                 WX, Y_GND, outline='white', fill='white')

    def redraw_fuel(self):
        'update fuel level'
        self.canvas.coords(self.tank, WX-W_TANK, Y_GND-(self.weight-TARE)*4, WX, Y_GND)

    def refuel(self, percentage):
        'replenish the tank'
        self.weight = TARE + FUEL * percentage

#
# dialog window
#
class APPWindow(object):
    'main and only application window'
    def __init__(self):
        self.fire = 0
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
        graph.create_line(0, Y_GND-SET_ALTITUDE, X_RKT-50, Y_GND-SET_ALTITUDE, fill='white')

        #------- create the rocket --------------------------
        self.rocket = Rocket(self.graph)
        graph.bind('<Button-1>', self.cmd_fire)   # capture mouse button inside canvas

        #------- buttons   -----------------------------------
        tk.Button(win, text='Refuel',
                  command=self.cmd_refuel).grid(padx=10, pady=10, row=3, column=0)
        tk.Button(win, text='Close',
                  command=self.cmd_quit).grid(padx=10, pady=10, row=3, column=3)
        tk.Radiobutton(win, text='MATHACC', variable=self.use_pid,
                       value=True).grid(padx=10, pady=10, row=3, column=1)
        tk.Radiobutton(win, text='Manual', variable=self.use_pid,
                       value=False).grid(padx=10, pady=10, row=3, column=2)
        self.win.after(0, self.animation)

    #-------------------- Window methods
    def cmd_refuel(self):
        'refill the rocket tank to 100%'
        self.rocket.refuel(1.0)

    def cmd_quit(self):
        'exit application'
        self.win.quit()

    def cmd_fire(self, _):
        'turn on manual thrust to 100% for 1 second'
        self.fire = 1.0/DELTA_T

    def animation(self):
        'animation step'
        if self.use_pid.get():      # automatic
            thrust = self.pid.compute(SET_ALTITUDE - self.rocket.y)
            # valve control <0.0 - 1.0>
            if thrust < 0.0:
                thrust = 0.0
            elif thrust > 1.0:
                thrust = 1.0
        else:   # manual
            if self.fire > 0:
                self.fire -= 1
            thrust = 1.0 if self.fire > 0 else 0
        self.rocket.update(thrust)
        self.win.after(int(1000*DELTA_T), self.animation) # delay in ms

if __name__ == '__main__':
    APPWindow()
    tk.mainloop()
