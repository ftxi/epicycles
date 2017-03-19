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

#import ttk
from PIL import ImageTk, Image

import time
from math import sin, cos, floor, atan2, pi
import numpy as np
import fft2circle


class window:
    #要画出精细的图形，需要更多的圆和更快的刷新速度，现在配色对比度太低，需要改变
    #建议添加功能，采样前设置背景图片，方便勾勒轮廓
    #建议添加功能，画出连接圆心的连线，并使得圆和圆心连线都可选择隐藏
    #建议添加功能，重置窗口，清楚所有采样点和计算数据
    #建议添加功能，调整采样点次序，增删采样点
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
        self.lines_id = self.canvas.create_line(0, 0, 0, 0)
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
        
        self.frame_logs = tk.Frame(self.root, width=100)
        #self.text_log = tk.Text(self.frame_logs, height=20, width=40)
        self.listbox = tk.Listbox(self.frame_logs, activestyle='dotbox', height=20)
        self.scroll_log = tk.Scrollbar(self.frame_logs, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.scroll_log.set,  font=('Sans', 10))
        self.listbox.pack(side=tk.LEFT, fill=tk.X)
        self.listbox_flag = 0 #0 stands for points
        '''
        self.label_n = tk.Label(self.frame_logs, text='-')
        self.label_n.pack(side=tk.BOTTOM)
        self.button_remove = tk.Button(self.frame_logs, text='remove', command=self.remove_item)
        self.button_remove.pack(side=tk.BOTTOM)
        '''
        #self.text_log.configure(yscrollcommand=self.scroll_log.set, font=('Sans', 6))
        #self.text_log.pack(side=tk.LEFT, fill=tk.X)
        self.scroll_log.pack(side=tk.LEFT, fill=tk.Y)
        self.frame_logs.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
        
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
                self.canvas.itemconfig(point_id, outline='antiqueWhite')

    def on_toggle_animation(self):
        self.show_animation = not self.show_animation

    def refresh_listbox(self) :
        self.listbox.delete(0, tk.END)
        if self.listbox_flag == 0 :
            for n in range(len(self.points)//2):
                self.listbox.insert('point[%d] \tat (%3d, %3d)'
                                    % (n, self.points[2*n], self.points[2*n+1]))
            
        elif self.listbox_flag == 1 :    
            pass
        
    def on_open_image(self) :
        self.img_path = filedialog.askopenfilename(
                #filetypes=[('all files', '.*')],
                parent=self.root,
                title='select background image to open')
        #print(self.img_path)
        try :
            with Image.open(self.img_path) as pilimg :
                #print(pilimg)
                img = ImageTk.PhotoImage(pilimg)
                self._label = tk.Label(image=img)
                self._label.image = img
                self._image = self.canvas.create_image(100, 100, image=img)
                self.button_hide_image.config(state=tk.NORMAL)
        except IOError:
            msgbox.showerror('Invalid image file', 'Please select a photo,\n'
                             'such as example.jpg, example.png', icon='warning')
        
    def on_hide_image(self) :
        self.canvas.delete(self._image)
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
        if self.listbox_flag == 0 :
            pass
    
    def onclick(self, me):
        self.points.append(me.x - window.SIZE)
        self.points.append(me.y - window.SIZE)
        self.points_id.append(
            self.canvas.create_oval(me.x - 1, me.y - 1, me.x + 1, me.y + 1, tag='p', outline='orange'))
        if self.listbox_flag == 0 :
            self.listbox.insert(tk.END, 'point[%d] \tat (%3d, %3d)' 
                                 % (len(self.points)//2, me.x - window.SIZE, me.y - window.SIZE))

    def undo_click(self, me):
        if len(self.points) > 0:
            self.canvas.delete(self.points_id.pop())
            self.points.pop()
            self.points.pop()
            self.listbox.delete(tk.END)
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
            x = 0.0
            y = 0.0
            for k in range(N):
                rotation = self.v[k]#旋转方向参量
                self.canvas.coords(self.epicycles_id[k], int(x - self.r[k]) + window.SIZE,\
                                   int(y - self.r[k]) + window.SIZE, int(x + self.r[k]) + window.SIZE,\
                                   int(y + self.r[k]) + window.SIZE)
                x = x + self.r[k] * cos(rotation*tmp * self.n[k] + self.p[k])
                y = y + self.r[k] * sin(rotation*tmp * self.n[k] + self.p[k])
            self.upload_tracers(int(x) + window.SIZE, int(y) + window.SIZE)
        if self.show_lines and len(self.points) >= 4:
            self.canvas.delete(self.lines_id)
            self.lines_id = self.canvas.create_line(list(map(lambda z: z+window.SIZE, self.points)), fill='gray70')
        self.drawing = False

    def upload_tracers(self, x, y):
        if self.tracers_id[self.tn] == 0:
            self.tracers_id[self.tn] = self.canvas.create_oval(x - window.TRACER_SIZE, y - window.TRACER_SIZE, x + window.TRACER_SIZE, y + window.TRACER_SIZE, fill='red')
        else:
            self.canvas.coords(self.tracers_id[self.tn], x - window.TRACER_SIZE, y - window.TRACER_SIZE, x + window.TRACER_SIZE, y + window.TRACER_SIZE)
        self.tn = (self.tn + 1) % window.MAX_TRACERS

    def calculate(self):
        array = []
        array = self._inter()
        acircle = fft2circle.get_circle_fft(np.real(array), np.imag(array))
        self.r = []
        self.p = []
        self.n = []
        self.v = []
        # the epcycle data
        _inv = []
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
        self.button_animation.configure(state=tk.NORMAL)

    def _inter(self) :
        #对相邻采样点间采用线性插值,即插值点在一条直线上
        #建议采用r—theta插值模式，并把连接点之间的直线转为实际绘图会出现的曲线
        #建议在末点和首点间插值使曲线闭合，以避免不合适的误差
        new_point = []
        front = (self.points[0]+self.points[1]*1j)/window.SIZE
        behind = 0+0j
        for i in range(1, int(len(self.points)/2)) :
            if i != 1 :
                front = behind
            behind = (self.points[2*i]+self.points[2*i+1]*1j)/window.SIZE
            lenth = abs(front-behind)
            if lenth > window.L_BIN :
                newreal = list(np.interp(range(int(lenth/window.L_BIN)), [0.0, lenth/window.L_BIN], [front.real, behind.real]))
                newimag = list(np.interp(range(int(lenth/window.L_BIN)), [0.0, lenth/window.L_BIN], [front.imag, behind.imag]))
                new = []
                for i in range(len(newreal)) :
                    new.append(newreal[i] + newimag[i] * 1.0j)
            else:
                new = [front]
            new_point = new_point + new
        new_point.append(behind)
        return new_point

if __name__ == '__main__':
    window()
