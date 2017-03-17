#!usr/bin/python
# -*- coding: utf-8 -*-
#use fft2circle

from __future__ import division

try:
    import Tkinter as tk  # GUI#2.7中为Tkinter，请注意版本
except ImportError:
    import tkinter as tk

import time
from math import sin, cos, floor, atan2, pi
import numpy as np
import fft2circle


class window:#要画出精细的图形，需要更多的圆和更快的刷新速度，现在配色对比度太低，需要改变
    #建议添加功能，采样前设置背景图片，方便勾勒轮廓
    #建议添加功能，画出连接圆心的连线，并使得圆和圆心连线都可选择隐藏
    #建议添加功能，重置窗口，清楚所有采样点和计算数据
    #建议添加功能，调整采样点次序，增删采样点
    #建议文本框显示采样点及次序，不显示计算过程
    '''
    The program window.
    '''
    SIZE = 300
    REFRESH = 40  # refresh every 40 miliseconds
    MAX_TRACERS = 1000
    TRACER_SIZE = 2
    SPEED = 2.
    
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
        self.button_calculate = tk.Button(self.frame_buttons, text='calculate')
        self.button_calculate.bind('<ButtonRelease-1>', self.calculate)
        self.button_calculate.pack(side=tk.TOP, fill=tk.X)
        self.button_animation = tk.Button(self.frame_buttons, text='show animation', state=tk.DISABLED)
        self.button_animation.bind('<ButtonRelease-1>', self.on_toggle_animation)
        self.button_animation.pack(side=tk.TOP, fill=tk.X)
        self.frame_logs = tk.Frame(self.root, width=100)
        self.text_log = tk.Text(self.frame_logs, height=20, width=40)
        self.scroll_log = tk.Scrollbar(self.frame_logs, command=self.text_log.yview)
        self.text_log.configure(yscrollcommand=self.scroll_log.set, font=('Sans', 6))
        self.text_log.pack(side=tk.LEFT, fill=tk.X)
        self.scroll_log.pack(side=tk.RIGHT, fill=tk.Y)
        self.frame_logs.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
        self.button_lines = tk.Button(self.frame_buttons, text='toggle lines display')
        self.button_lines.bind('<ButtonRelease-1>', self.on_lines_display)
        self.button_lines.pack(side=tk.TOP, fill=tk.X)
        self.button_points = tk.Button(self.frame_buttons, text='toggle points display')
        self.button_points.bind('<ButtonRelease-1>', self.on_points_display)
        self.button_points.pack(side=tk.TOP, fill=tk.X)
        self.button_about = tk.Button(self.frame_buttons, text='About Epicycles & sclereid')
        self.button_about.pack(side=tk.TOP, fill=tk.X)
        self.frame_buttons.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.Y)
        # buttons
        self.drawing = False
        self.draw()
        self.root.mainloop()

    def on_lines_display(self, event):
        if self.show_lines and len(self.points) >= 4:
            self.canvas.delete(self.lines_id)
        self.show_lines = not self.show_lines

    def on_points_display(self, event):
        self.show_points = not self.show_points
        if self.show_points:
            for point_id in self.points_id:
                self.canvas.itemconfig(point_id, outline='orange')
        else:
            for point_id in self.points_id:
                self.canvas.itemconfig(point_id, outline='antiqueWhite')

    def on_toggle_animation(self, event):
        self.show_animation = not self.show_animation

    def onclick(self, me):
        self.points.append(me.x - window.SIZE)
        self.points.append(me.y - window.SIZE)
        self.points_id.append(
            self.canvas.create_oval(me.x - 1, me.y - 1, me.x + 1, me.y + 1, tag='p', outline='orange'))
        self.text_log.insert(tk.END, 'mouse clicking (%d, %d)\n' % (me.x - window.SIZE, me.y - window.SIZE))

    def undo_click(self, me):
        if len(self.points) > 0:
            self.canvas.delete(self.points_id.pop())
            self.text_log.insert(tk.END, 'removed point at (%d, %d)\n' % (self.points.pop(), self.points.pop()))
        if len(self.points) == 2:
            self.canvas.delete(self.lines_id)

    def draw(self):
        #绘图似乎在以逆序运行，解出顺时针旋转实际以逆时针旋转，建议修改，并使得显示时经过点的次序与选择时相同
        self.canvas.after(window.REFRESH, self.draw)
        if self.drawing:
            return
        self.drawing = True
        if self.show_animation:
            # print 'animation running at %f' % tmp
            N = len(self.n)
            tmp = (time.time() / N * 4 - floor(time.time() / N * 2 / pi) * 2.0 * pi) * window.SPEED
            x = 0.0
            y = 0.0
            for k in range(N):
                rotation = self.v[k]#旋转方向参量
                # print (self.epicycles_id[k], int(x-self.r[k]), int(y-self.r[k]), int(x+self.r[k]), int(y+self.r[k]))
                self.canvas.coords(self.epicycles_id[k], int(x - self.r[k]) + window.SIZE,\
                                   int(y - self.r[k]) + window.SIZE, int(x + self.r[k]) + window.SIZE,\
                                   int(y + self.r[k]) + window.SIZE)
                x = x + self.r[k] * cos(rotation*tmp * self.n[k] + self.p[k])#增加了系数
                y = y + self.r[k] * sin(rotation*tmp * self.n[k] + self.p[k])#增加了系数
            # test
            self.upload_tracers(int(x) + window.SIZE, int(y) + window.SIZE)
            # print '-'*50
            # time.sleep(1)
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

    def calculate(self, event):
        self.text_log.insert(tk.END, 'Calculating position...\n')
        array = []
        array = self._inter()
        self.text_log.insert(tk.END, '%s\n' % self.points)
        self.text_log.insert(tk.END, 'Running IDFT...\n')
        acircle = fft2circle.get_circle_fft(np.real(array), np.imag(array))
        print(type(acircle))
        inv = acircle
        #inv, inrot = IDFT2(array)#inrot表示旋转方向的list
        self.text_log.insert(tk.END, 'Transforming&Looking for fine order...\n')
        self.r = []
        self.p = []
        self.n = []
        self.v = []
        # the epcycle data
        _inv = []
        for i in range(len(inv)):#设置i的取值范围，可以实现滤波功能，可选择添加交互
            _inv.append((acircle[i].radius*(cos(acircle[i].p)+acircle[i].rot*1j*sin(acircle[i].p)), acircle[i].rot, acircle[i].omg))
        # `_inv` is a tuple to hold the speed value while sorting
        for k, (z, l, n) in enumerate(sorted(_inv, key=lambda _: -abs(_[0]))):
            #sort使圆按大小排序，而非频率排序，会削弱物理内涵，不建议使用
            if abs(z) * window.SIZE < 0.3:#去掉半径较小的圆，可以提高效率，但前面排序更改后存在bug，需要改写
                break  # filter the circles which are too small
            self.r.append(abs(z) * window.SIZE)
            self.p.append(atan2(l*z.imag, z.real))#多了参数l
            self.n.append(n)
            self.v.append(l)#新增参量，表示旋转方向
            self.epicycles_id.append(self.canvas.create_oval(0, 0, 0, 0))
            self.text_log.insert(tk.END, 'circle %3d: r = %.4f, p = %3.4f, s = %d\n' % (k, self.r[-1], self.p[-1], n))
        self.text_log.insert(tk.END, 'Calulation done.\n\n\n\n')
        self.button_animation.configure(state=tk.NORMAL)

    def _inter(self):#对相邻采样点间采用线性插值,即插值点在一条直线上
        #建议采用r—theta插值模式，并把连接点之间的直线转为实际绘图会出现的曲线
        #建议在末点和首点间插值使曲线闭合，以避免不合适的误差
        lbin = 0.1#插值间隔
        new_point = []
        front = (self.points[0]+self.points[1]*1j)/window.SIZE
        behind = 0+0j
        for i in range(1, int(len(self.points)/2)):
            if i != 1:
                front = behind
            behind = (self.points[2*i]+self.points[2*i+1]*1j)/window.SIZE
            lenth = abs(front-behind)
            if lenth > lbin:
                #new = list(np.interp(range(int(lenth/lbin)), [0, lenth/lbin], [front, behind]))
                newreal = list(np.interp(range(int(lenth/lbin)), [0.0, lenth/lbin], [front.real, behind.real]))
                newimag = list(np.interp(range(int(lenth/lbin)), [0.0, lenth/lbin], [front.imag, behind.imag]))
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

