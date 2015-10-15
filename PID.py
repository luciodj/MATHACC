#!usr/bin/env python
#
# Rocket Science PID-MATHACC demo
#
from Tkinter import *

KP = 0.89      # 0.89
KI = 0.028     # 0.028
KD = 0.15      # 0.15
SET_ALTITUDE = 250

X_POS = 320
Y_POS = 450
TARE = 30.0
FUEL = 70.0
FULL_WEIGHT = TARE + FUEL
GRAVITY = 9.81
MAX_THRUST = GRAVITY * 1.05 * FULL_WEIGHT
FUEL_BURN = FUEL / 6000     # enough fuel for 60 seconds at full burn


class PID():
    def __init__( self, Kp, Ki, Kd):
        self.Kp = Kp/100
        self.Ki = Ki/10000
        self.Kd = Kd
        self.integral = 0
        self.error = 0

    def compute( self, error):
        self.integral += error
        self.derivative = (error - self.error)
        self.error = error
        pid = self.error * self.Kp + self.derivative * self.Kd + self.integral * self.Ki
        return pid
#
# rocket
#
class Rocket():
    def __init__( self, canvas):
        self.canvas = canvas
        self.usePID = BooleanVar()
        self.usePID.set( False)
        self.x = X_POS
        self.y = 0
        self.v = 0
        self.fire = 0
        self.thrust = 0.0
        self.weight = TARE # FULL_WEIGHT
        self.drawRocket()
        self.drawFuel()
        self.pid = PID( KP, KI, KD)

    def update( self):
        if self.usePID.get():
            output = self.pid.compute( SET_ALTITUDE - self.y )
            # valve control
            if output < 0: self.thrust = 0.0
            elif output > 1: self.thrust = 1.0
            else: self.thrust = output

        else:   # manual 
            if self.fire >  0: self.fire -= 1 
            self.thrust = 1.0 if self.fire > 0 else 0
        
        if self.weight < TARE: 
            self.thrust = 0  # out of gas
        
        acceleration = -GRAVITY + self.thrust * MAX_THRUST / self.weight 
        self.v += acceleration *.001
        self.y += self.v
        if self.y < 0 : 
            self.v = self.y = 0
        self.updateRocket()
        self.updateFuel()

    def drawRocket( self):
        self.img = PhotoImage( file='rocket.gif')
        self.id = self.canvas.create_image( self.x, Y_POS-self.y-80, image=self.img )
        self.xflame1 = self.x-25
        self.xflame2 = self.x+24
        self.flame1 = self.canvas.create_line( self.xflame1, Y_POS-self.y-80, 
                                          self.xflame1, Y_POS-self.y-80+self.thrust, width=2, fill='red')
        self.flame2 = self.canvas.create_line( self.xflame2, Y_POS-self.y-80, 
                                          self.xflame2, Y_POS-self.y-80+self.thrust, width=2, fill='red')

    def updateRocket( self):
        self.canvas.coords( self.id, self.x, Y_POS-self.y-80)
        self.canvas.coords( self.flame1, self.xflame1, Y_POS-self.y, 
                                         self.xflame1, Y_POS-self.y+self.thrust*30)
        self.canvas.coords( self.flame2, self.xflame2, Y_POS-self.y, 
                                         self.xflame2, Y_POS-self.y+self.thrust*30)

    def drawFuel( self):
        self.canvas.create_rectangle( 620, Y_POS-FUEL*4, 640, Y_POS, outline='white')
        self.tank = self.canvas.create_rectangle( 620, Y_POS-(self.weight-TARE)*4, 
                                                  640, Y_POS, outline='white', fill='white')

    def updateFuel( self):
        self.weight -= FUEL_BURN * self.thrust
        self.canvas.coords( self.tank, 620, Y_POS-(self.weight-TARE)*4, 640, Y_POS)

    def cmdFire( self, e):
        self.fire = 100    # turn on burner for 1s

#
# dialog window 
#
class APPWindow():

    def __init__(self, parent = None, name=''):
        win = Tk()
        win.title( 'This is Rocket Science')
        win.protocol( 'WM_DELETE_WINDOW', self.cmdQuit) # intercept Ctrl_Q and Close Window button
        self.win = win

        wx = 640; wy = 480
        self.wx = wx; self.wy = wy

        #------- draw canvas ----------------------------
        brd = 2
        self.brd = brd
        tk_rgb = "#%02x%02x%02x" % (55, 132, 191)
        graph = Canvas( win, width=wx, height=wy, relief='flat', bd=brd, bg=tk_rgb)
        graph.grid( padx=10, row=2, columnspan=4)
        self.graph = graph

        #------- draw reference lines
        graph.create_line(  0, Y_POS, 640, Y_POS, fill='white')
        graph.create_line(  0, Y_POS-SET_ALTITUDE, 
                          250, Y_POS-SET_ALTITUDE, fill='white')

        #------- create the rocket --------------------------
        self.rocket = Rocket( self.graph)
        graph.bind( '<Button-1>', self.rocket.cmdFire)   # capture mouse button inside canvas

        #------- buttons   -----------------------------------
        Button( win, text='Refuel', takefocus=YES, command=self.cmdRefuel).grid( padx=10, pady=10, row=3, column=0)
        Button( win, text='Close',  takefocus=NO,  command=self.cmdQuit  ).grid( padx=10, pady=10, row=3, column=3)
        Radiobutton( win, text='MATHACC',takefocus=YES, variable=self.rocket.usePID, value=True ).grid( padx=10, pady=10, row=3, column=1)
        Radiobutton( win, text='Manual', takefocus=YES, variable=self.rocket.usePID, value=False).grid( padx=10, pady=10, row=3, column=2)

        self.win.after( 0, self.animation)

    #-------------------- Window methods
    def cmdRefuel( self):
        self.rocket.weight = FULL_WEIGHT    

    def cmdQuit( self):
        self.win.quit()

    def animation( self):
        self.rocket.update()
        self.win.after( 10, self.animation)

if __name__ == '__main__': 
    APPWindow()
    mainloop()
