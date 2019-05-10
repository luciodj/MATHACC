#! /usr/bin/env python3 

from PID import PID, DELTA_T, APPWindow

def test_prop():
    pid = PID(1, 0, 0)
    assert(pid.compute(10) == 10*DELTA_T)

def test_integral():
    pid = PID(0, 1, 0)
    pid.integrate(10) 
    assert(pid.integral == 10)

def test_derivative():
    pid = PID(0, 0, 1)
    out = pid.compute(10)
    assert(pid.error == 10)
    assert(out == 10)

def test_window_init():
    assert(APPWindow())
    # cannot call tk.mainloop because that is a blocking call
    