#!usr/bin/python
#-*- coding: utf-8 -*-

import Tkinter as tk    #GUI
import time             
from math import *      #mathematical stuff
import numpy as np      #numpy array
from scipy.fftpack import fft, ifft
from scipy import interpolate


class window :
    '''
    The program window.
    '''
    SIZE = 300   #600*600px screen
    REFRESH = 30 #refresh every 30 miliseconds
    MAX_TRACERS = 1000
    
    def __init__(self) :
        self.root = tk.Tk()
        self.root.title('Epicycles --An Enternal...')
        self.points = []
        #`points` is something like `[x1, y1, x2, y2, ...]`
        self.canvas = tk.Canvas(self.root, width=window.SIZE*2, height=window.SIZE*2, bd=0, bg='antiqueWhite')
        self.canvas.pack(side=tk.LEFT)
        self.canvas.bind('<Button-1>', self.onclick)
        self.canvas.bind('<Button-3>', self.undo_click)
        #canvas (LMB =>add a point, RMB =>remove a point)
        self.canvas.create_line(0, window.SIZE, 2*window.SIZE, window.SIZE, fill='gray')
        self.canvas.create_line(window.SIZE, 0, window.SIZE, 2*window.SIZE, fill='gray')
        #axies
        
        self.show_lines = True
        self.show_points = True
        self.show_animation = False
        self.lines_id = self.canvas.create_line(0,0,0,0)
        self.points_id = []
        self.epicycles_id = []
        self.tracers_id = map(lambda x : 0, range(window.MAX_TRACERS))
        self.tn = 0
        
        #widgets
        self.frame_buttons = tk.Frame(self.root, width=100)
        self.button_calculate = tk.Button(self.frame_buttons, text='calculate')
        self.button_calculate.bind('<ButtonRelease-1>', self.calculate)
        self.button_calculate.pack(side=tk.TOP, fill=tk.X)
        self.button_animation = tk.Button(self.frame_buttons, text='show animation', state=tk.DISABLED)
        #disabled, not accessible until a calculation is done
        self.button_animation.bind('<ButtonRelease-1>', self.on_toggle_animation) 
        self.button_animation.pack(side=tk.TOP, fill=tk.X)
        self.frame_logs = tk.Frame(self.root, width=100)
        self.text_log = tk.Text(self.frame_logs, height = 20, width=40)
        self.scroll_log = tk.Scrollbar(self.frame_logs, command=self.text_log.yview)
        self.text_log.configure(yscrollcommand=self.scroll_log.set, font=('Sans',6))
        self.text_log.pack(side=tk.LEFT, fill=tk.X)
        self.scroll_log.pack(side=tk.RIGHT, fill=tk.Y)
        self.frame_logs.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
        #used for displaying interactive log
        self.button_lines = tk.Button(self.frame_buttons, text='toggle lines display')
        self.button_lines.bind('<ButtonRelease-1>', self.on_lines_display)
        self.button_lines.pack(side=tk.TOP, fill=tk.X)
        self.button_points = tk.Button(self.frame_buttons, text='toggle points display')
        self.button_points.bind('<ButtonRelease-1>', self.on_points_display)
        self.button_points.pack(side=tk.TOP, fill=tk.X)
        self.button_about = tk.Button(self.frame_buttons, text='About Epicycles & sclereid')
        self.button_about.pack(side=tk.TOP, fill=tk.X)
        self.frame_buttons.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.Y)
        #buttons
        self.drawing = False
        self.draw()
        self.root.mainloop()

    def on_lines_display(self, event) :
        if self.show_lines and len(self.points)>=4 :
            self.canvas.delete(self.lines_id)
        self.show_lines = not self.show_lines

    def on_points_display(self, event) :
        self.show_points = not self.show_points
        if self.show_points :
            for point_id in self.points_id :
                self.canvas.itemconfig(point_id, outline='orange')
        else :
            for point_id in self.points_id :
                self.canvas.itemconfig(point_id, outline='antiqueWhite')

    def on_toggle_animation(self, event) :
        self.show_animation = not self.show_animation
    
    def onclick(self, me) :
        self.points.append(me.x-window.SIZE)
        self.points.append(me.y-window.SIZE)
        self.points_id.append(self.canvas.create_oval(me.x-1, me.y-1, me.x+1, me.y+1, tag='p', outline='orange'))
        self.text_log.insert(tk.END, 'mouse clicking (%d, %d)\n' % (me.x-window.SIZE, me.y-window.SIZE))

    def undo_click(self, me) :
        if len(self.points)>0 :
            self.canvas.delete(self.points_id.pop())
            self.text_log.insert(tk.END, 'removed point at (%d, %d)\n' % (self.points.pop(), self.points.pop()))
        if len(self.points)==2 :
            self.canvas.delete(self.lines_id)
        
    def draw(self) :
        self.canvas.after(window.REFRESH, self.draw)
        if self.drawing :
            return
        self.drawing = True
        if self.show_animation :
            #paint epicycles
            N = len(self.n)
            tmp = (time.time()/N*4 - floor(time.time()/N*2/pi)*2.0*pi)
            x, y = 0.0, 0.0
            for k in range(N) :
                self.canvas.coords(self.epicycles_id[k], int(x-self.r[k])+window.SIZE, int(y-self.r[k])+window.SIZE, int(x+self.r[k])+window.SIZE, int(y+self.r[k])+window.SIZE)
                x += self.r[k]*cos(tmp*self.n[k]+self.p[k])
                y += self.r[k]*sin(tmp*self.n[k]+self.p[k])
            #test
            self.upload_tracers(int(x) + window.SIZE, int(y) + window.SIZE)
            #print '-'*50
            #time.sleep(1)
        if self.show_lines and len(self.points)>=4 :
            #paint lines （violently）
            self.canvas.delete(self.lines_id)
            self.lines_id = self.canvas.create_line(map(lambda x : x+window.SIZE, self.points), fill='gray70')
        self.drawing = False

    def upload_tracers(self, x, y) :
        if self.tracers_id[self.tn] == 0 :
            self.tracers_id[self.tn] = self.canvas.create_oval(x-1, y-1, x+1, y+1, fill='red')
        else :
            self.canvas.coords(self.tracers_id[self.tn], x-2, y-2, x+2, y+2)
        self.tn = (self.tn + 1) % window.MAX_TRACERS

    def calculate(self, event) :
        self.text_log.insert(tk.END, '%s\n' % array.__repr__())
        self.text_log.insert(tk.END, 'Interpolating points...\n')
        
        ax = np.append(self.points[::2], [self.points[0]])
        ay = np.append(self.points[1::2], [self.points[1]])
        tck, u = interpolate.splprep([ax, ay], s=0)
        unew = np.arange(0, 1.001, 0.001)
        out = interpolate.splev(unew, tck)
        array = out[0]/window.SIZE + out[1]*1.0j/window.SIZE
        
        self.text_log.insert(tk.END, 'Running ifft...\n')
        inv = ifft(array)
        self.text_log.insert(tk.END, '%s\n' % inv)
        self.text_log.insert(tk.END, 'Transforming&Looking for fine order...\n')
        self.r = []
        self.p = []
        self.n = []
        #the epcycle data
        _inv = []
        for i in range(len(inv)) :
            _inv.append((inv[i], i))
        #`_inv` is a tuple to hold the speed value while sorting
        for (z, n) in sorted(_inv, key=lambda _ : -abs(_[0])) :
            #if abs(z)*window.SIZE < 0.01 :
            #    break       #filter the circles which are too small
            self.r.append(abs(z)*window.SIZE)
            self.p.append(atan2(z.imag, z.real))
            self.n.append(n)
            self.epicycles_id.append(self.canvas.create_oval(0, 0, 0, 0))
            self.text_log.insert(tk.END, 'circle: r = %.4f, p = %3.4f, s = %d\n' % (self.r[-1], self.p[-1], n))
        self.text_log.insert(tk.END, 'Calulation done.\n\n\n\n')
        self.button_animation.configure(state=tk.NORMAL)
        

if __name__ == '__main__' :
    window()

