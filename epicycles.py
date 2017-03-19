#!usr/bin/python
# -*- coding: utf-8 -*-
#use fft2circle

from __future__ import division

try:                        #python 2.7
    import Tkinter as tk
    import tkFileDialog as filedialog
    import tkMessageBox as msgbox
except ImportError:         #python 3
    import tkinter as tk
    from tkinter import filedialog
    import tkinter.messagebox as msgbox

import ttk
from PIL import ImageTk, Image

import time
from math import sin, cos, floor, atan2, pi
import numpy as np
import fft2circle
from scipy.interpolate import interp1d


class window:
    '''
    The program window.
    '''
    SIZE = 300
    REFRESH = 40  # refresh every 40 miliseconds
    MAX_TRACERS = 1000
    TRACER_SIZE = 2
    SPEED = 2.
    L_BIN = 0.1  #插值间隔

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Epicycles --An Enternal...')
        self.points = []
        # `points` is something like `[x1, y1, x2, y2, ...]`
        self.canvas = tk.Canvas(self.root, width=window.SIZE * 2, height=window.SIZE * 2, bd=0, bg='antiqueWhite')
        self.canvas.pack(side=tk.LEFT)
        self.canvas.bind('<Button-1>', self.onclick)
        self.canvas.bind('<Button-2>', self.undo_click)
        self.canvas.bind('<Button-3>', self.undo_click)
        # canvas (LMB =>add a point, RMB =>remove a point)
        self.canvas.create_line(0, window.SIZE, 2 * window.SIZE, window.SIZE, fill='gray')
        self.canvas.create_line(window.SIZE, 0, window.SIZE, 2 * window.SIZE, fill='gray')
        # axies
        self.show_lines = True
        self.show_points = True
        self.show_animation = False
        self.lines_id = self.canvas.create_polygon(0, 0, 0, 0, fill='', outline='gray70')
        self.through_lines_id = []
        self.points_id = []
        self.epicycles_id = []
        self.tracers_id = list(map(lambda x: 0, range(window.MAX_TRACERS)))
        self.tn = 0
        # widgets
        self.frame_buttons = tk.Frame(self.root, width=100)
        self.button_image = tk.Button(self.frame_buttons,
                                          text='open an image', command=self.on_open_image)
        self.button_hide_image = tk.Button(self.frame_buttons,
                                           state=tk.DISABLED,
                                           text='hide image', command=self.on_hide_image)
        self.button_image.pack(side=tk.TOP, fill=tk.X)
        self.button_hide_image.pack(side=tk.TOP, fill=tk.X)
        self.button_calculate = tk.Button(self.frame_buttons,
                                          text='calculate', command=self.calculate)
        self.button_calculate.pack(side=tk.TOP, fill=tk.X)
        self.button_animation = tk.Button(self.frame_buttons,
                                          text='show animation',
                                          state=tk.DISABLED, command=self.on_toggle_animation)
        self.button_animation.pack(side=tk.TOP, fill=tk.X)
        
        self.notebook = ttk.Notebook(self.root)
        
        self.frame_logs = tk.Frame(width=100)
        self.listbox_points = tk.Listbox(self.frame_logs, activestyle='dotbox', height=20)
        self.listbox_points.pack()
        self.listbox_points_flag = 0 #0 stands for points
        '''
        self.label_n = tk.Label(self.frame_logs, text='-')
        self.label_n.pack(side=tk.BOTTOM)
        self.button_remove = tk.Button(self.frame_logs, text='remove', command=self.remove_item)
        self.button_remove.pack(side=tk.BOTTOM)
        '''
        self.notebook.add(self.frame_logs, text='points')
        
        self.frame_epicycles = tk.Frame(width=100)
        self.listbox_epicycles = tk.Listbox(self.frame_epicycles, activestyle='dotbox', height=20)
        self.listbox_epicycles.pack()
        
        self.notebook.add(self.frame_epicycles, text='epicycles')
        self.notebook.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
        
        self.button_lines = tk.Button(self.frame_buttons,
                                      text='toggle lines display', command=self.on_lines_display)
        self.button_lines.pack(side=tk.TOP, fill=tk.X)
        self.button_points = tk.Button(self.frame_buttons,
                                      text='toggle points display', command=self.on_points_display)
        self.button_points.pack(side=tk.TOP, fill=tk.X)
        self.button_about = tk.Button(self.frame_buttons,
                                      text='About Epicycles & sclereid', command=self.on_about)
        self.button_about.pack(side=tk.TOP, fill=tk.X)
        self.frame_buttons.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.Y)
        # buttons
        self.drawing = False
        self.draw()
        self.root.mainloop()

    def on_lines_display(self):
        if self.show_lines and len(self.points) >= 4:
            self.canvas.delete(self.lines_id)
        self.show_lines = not self.show_lines

    def on_points_display(self):
        self.show_points = not self.show_points
        if self.show_points:
            for point_id in self.points_id:
                self.canvas.itemconfig(point_id, outline='orange')
        else:
            for point_id in self.points_id:
                self.canvas.itemconfig(point_id, outline='')

    def on_toggle_animation(self):
        self.show_animation = not self.show_animation

    def refresh_listbox_points(self) :
        self.listbox_points.delete(0, tk.END)
        if self.listbox_points_flag == 0 :
            for n in range(len(self.points)//2):
                self.listbox_points.insert('point[%d] at (%3d, %3d)'
                                    % (n, self.points[2*n], self.points[2*n+1]))
            
        elif self.listbox_points_flag == 1 :    
            pass
        
    def on_open_image(self) :
        try :
            self.img_path = filedialog.askopenfilename(
                        parent=self.root,
                        title='select background image to open')
            with Image.open(self.img_path) as originimg :
                height, width = originimg.size
                size = min(height, width)
                img = originimg.crop((0, 0, size, size)).resize((window.SIZE*2, window.SIZE*2))
                tkimg = ImageTk.PhotoImage(img)
                self._label = tk.Label(image=tkimg)
                self._label.image = tkimg     #hack a refrance to make python2.7 happy                
                self._image = self.canvas.create_image(window.SIZE, window.SIZE, image=tkimg)
                self.button_hide_image.config(state=tk.NORMAL)
        except IOError :                    #exception when PIL cannot recognize the image
            msgbox.showerror('Invalid image file', 'Please select a photo,\n'
                             'e.g. example.tiff, juli.jpg, money.png', icon='warning')
        except AttributeError :             #exception when cancal open a file
            pass
        
    def on_hide_image(self) :
        self.canvas.delete(self._image)
        del self._label
        self.button_hide_image.config(state=tk.DISABLED)
    
    def on_about(self) :
        tmp = self.show_animation
        self.show_animation = False
        msgbox.showinfo('Epicycles', 
                        'A small program to display epicycles with given image.\n'
                        '\n'
                        'Authors:\n' 
                        'sclereid: https://github.com/sclereid\n'
                        'zyyztyy: https://github.com/zzyztyy\n'
                        '\n'
                        'Source:  https://github.com/sclereid/epicycles\n'
                        '\n'
                        'Note:   This is a MIT licensed software.\n')
        self.show_animation = tmp
        
    def remove_item(self) :
        if self.listbox_points_flag == 0 :
            pass
    
    def onclick(self, me):
        self.points.append(me.x - window.SIZE)
        self.points.append(me.y - window.SIZE)
        if len(self.points) > 2:
            self.canvas.delete(self.points_id.pop())
            self.points_id.append(
                self.canvas.create_oval(self.points[-4] - 1 + window.SIZE,
                                        self.points[-3] - 1 + window.SIZE,
                                        self.points[-4] + 1 + window.SIZE,
                                        self.points[-3] + 1 + window.SIZE, tag='p', outline='orange'))
        self.points_id.append(
            self.canvas.create_oval(me.x - 1, me.y - 1, me.x + 1, me.y + 1, tag='p', fill='red', outline='red'))
        if self.listbox_points_flag == 0 :
            self.listbox_points.insert(tk.END, 'point[%d] \tat (%3d, %3d)' 
                                 % (len(self.points)//2, me.x - window.SIZE, me.y - window.SIZE))

    def undo_click(self, me):
        if len(self.points) > 0:
            self.canvas.delete(self.points_id.pop())
            self.points.pop()
            self.points.pop()
            self.listbox_points.delete(tk.END)
        if len(self.points) == 2:
            self.canvas.delete(self.lines_id)

    def draw(self):
        self.canvas.after(window.REFRESH, self.draw)
        if self.drawing:
            return
        self.drawing = True
        if self.show_animation:
            N = len(self.n)
            tmp = (time.time() / N * 4 - floor(time.time() / N * 2 / pi) * 2.0 * pi) * window.SPEED
            x, y = 0.0, 0.0
            _x, _y = 0.0, 0.0
            for k in range(N):
                rotation = self.v[k]
                _x += self.r[k] * cos(rotation*tmp * self.n[k] + self.p[k])
                _y += self.r[k] * sin(rotation*tmp * self.n[k] + self.p[k])
                self.canvas.coords(self.epicycles_id[k], int(x - self.r[k]) + window.SIZE,\
                                   int(y - self.r[k]) + window.SIZE, int(x + self.r[k]) + window.SIZE,\
                                   int(y + self.r[k]) + window.SIZE)
                if k < self.max_through_lines :
                    self.canvas.coords(self.through_lines_id[k], int(x) + window.SIZE,\
                                   int(y) + window.SIZE, int(_x) + window.SIZE,\
                                   int(_y) + window.SIZE)
                x, y = _x, _y
                
            self.upload_tracers(int(x) + window.SIZE, int(y) + window.SIZE)
        if self.show_lines and len(self.points) >= 4:
            self.canvas.delete(self.lines_id)
            self.lines_id = self.canvas.create_polygon(list(map(lambda z: z+window.SIZE, self.points)), fill='', outline='gray70')
        self.drawing = False

    def upload_tracers(self, x, y):
        if self.tracers_id[self.tn] == 0:
            self.tracers_id[self.tn] = self.canvas.create_oval(x - window.TRACER_SIZE, y - window.TRACER_SIZE, x + window.TRACER_SIZE, y + window.TRACER_SIZE, fill='red')
        else:
            self.canvas.coords(self.tracers_id[self.tn], x - window.TRACER_SIZE, y - window.TRACER_SIZE, x + window.TRACER_SIZE, y + window.TRACER_SIZE)
        self.tn = (self.tn + 1) % window.MAX_TRACERS

    def calculate(self):
        _z = (np.append(self.points[::2], [self.points[0]]) + \
                    np.append(self.points[1::2], [self.points[1]]) * 1.0j)/window.SIZE
        _t = np.arange(len(_z))
        f = interp1d(_t, _z)
        t = np.linspace(0, len(_z)-1, 1024)       #1024 can be any positive number
        array = f(t)
        
        map(lambda x : self.canvas.delete(x), self.epicycles_id)
        self.epicycles_id = []
        map(lambda x : self.canvas.delete(x), self.through_lines_id)
        self.through_lines_id = []
        
        acircle = fft2circle.get_circle_fft(np.real(array), np.imag(array))
        self.r = []
        self.p = []
        self.n = []
        self.v = []
        # the epcycle data
        _inv = []
        self.max_through_lines = len(acircle)
        
        for i in range(len(acircle)):#设置i的取值范围，可以实现滤波功能，可选择添加交互
            _inv.append((acircle[i].radius*(cos(acircle[i].p)+acircle[i].rot*1j*sin(acircle[i].p)), acircle[i].rot, acircle[i].omg))
        
        for k, (z, l, n) in enumerate(sorted(_inv, key=lambda _: -abs(_[0]))):
            if abs(z) * window.SIZE < 0.3:
                break  # filter the circles which are too small
            self.r.append(abs(z) * window.SIZE)
            self.p.append(atan2(l*z.imag, z.real))
            self.n.append(n)
            self.v.append(l)
            self.epicycles_id.append(self.canvas.create_oval(0, 0, 0, 0))
            if abs(z) * window.SIZE < 5.:
                self.through_lines_id.append(self.canvas.create_line(0, 0, 0, 0, fill='blue'))
            elif k > 2 and self.r[-2] >= 5. :
                self.max_through_lines = k
            self.listbox_epicycles.insert(tk.END,
                            'circle[%d] radius=%3.3f phi=%3.3f frequency=%3d %sclockwise' 
                            % (k, self.r[-1], self.p[-1], n, l==1 and 'counter' or ''))
        
        self.button_animation.configure(state=tk.NORMAL)

if __name__ == '__main__':
    window()
