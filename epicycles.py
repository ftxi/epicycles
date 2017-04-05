#!usr/bin/python
# -*- coding: utf-8 -*-
#use fft2circle

from __future__ import division

try :                        #python 2.7
    import Tkinter as tk
    import tkFileDialog as filedialog
    import tkMessageBox as msgbox
except ImportError :         #python 3
    import tkinter as tk
    from tkinter import filedialog
    import tkinter.messagebox as msgbox

import ttk
from PIL import ImageTk, Image

try :
    import epi_core
    export_flag = True
except ImportError :
    export_flag = False

import time
from math import sin, cos, floor, pi, log
import numpy as np
import fft2circle
from scipy.interpolate import interp1d

def _scale(master, text, from_, to, default_, ref=lambda x : x, side=tk.LEFT, **kw) :
    '''
    Tkinter scale widget generator.
    '''
    frame = tk.Frame(master)
    label = tk.Label(frame, text='%s' % default_)
    sc = tk.Scale(frame, label=text, from_=from_, to=to, showvalue=0,
                  command=lambda *args : label.config(text='%s' % ref(sc.get())), **kw)
    sc.set(default_)
    sc.pack(side=tk.TOP)
    label.pack(side=tk.TOP)
    frame.pack(side=side)
    return lambda : ref(sc.get())

class window:
    '''
    The program window.
    '''
    SIZE = 300
    REFRESH = 40  # refresh every 40 miliseconds
    MAX_TRACERS = 1000
    TRACER_SIZE = 2
    SPEED = 2.
    L_BIN = 1024
    LINED_CIRCLE_MIN = 5.
    MIN_CIRCLE_SIZE = 0.3

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
        self.show_animation = False
        self.lines_id = self.canvas.create_polygon(0, 0, 0, 0, fill='', outline='gray70')
        self.through_lines_id = []
        self.points_id = []
        self.epicycles_id = []
        self.tracers_id = [0] * window.MAX_TRACERS
        self.tn = 0
        self.sorted_flag = 1
        self.exporting = True
        # widgets
        self.frame_buttons = tk.Frame(self.root, width=100)
        self.button_settings = tk.Button(self.frame_buttons, 
                                         text='settings', command=self.on_settings)
        self.button_settings.pack(side=tk.TOP, fill=tk.X)
        
        self.button_image = tk.Button(self.frame_buttons,
                                          text='open an image', command=self.on_open_image)
        self.button_hide_image = tk.Button(self.frame_buttons,
                                          state=tk.DISABLED,
                                          text='hide image', command=self.on_hide_image)
        self.button_export = tk.Button(self.frame_buttons, state=tk.DISABLED,
                                       text='export...', command=self.on_export)
        self.button_image.pack(side=tk.TOP, fill=tk.X)
        self.button_hide_image.pack(side=tk.TOP, fill=tk.X)
        self.button_export.pack(side=tk.TOP, fill=tk.X)
        self.button_calculate = tk.Button(self.frame_buttons,
                                          text='calculate', command=self.calculate)
        self.button_calculate.pack(side=tk.TOP, fill=tk.X)
        self.button_animation = tk.Button(self.frame_buttons,
                                          text='show animation',
                                          state=tk.DISABLED, command=self.on_toggle_animation)
        self.button_animation.pack(side=tk.TOP, fill=tk.X)
        
        self.notebook = ttk.Notebook(self.root)
        
        self.frame_logs = tk.Frame(width=100)
        self.listbox_points = tk.Listbox(self.frame_logs, activestyle='dotbox', height=17)
        self.listbox_points.pack()
        self.notebook.add(self.frame_logs, text='points')
        
        self.frame_epicycles = tk.Frame(width=100)
        self.listbox_epicycles = tk.Listbox(self.frame_epicycles, activestyle='dotbox', height=17)
        self.listbox_epicycles.pack()
        
        self.notebook.add(self.frame_epicycles, text='epicycles')
        self.notebook.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
        
        self.button_lines = tk.Button(self.frame_buttons,
                                      text='toggle lines display', command=self.on_lines_display)
        self.button_lines.pack(side=tk.TOP, fill=tk.X)
        self.button_clear = tk.Button(self.frame_buttons,
                                      text='clear tracers', command=self.on_clear)
        self.button_clear.pack(side=tk.TOP, fill=tk.X)
        self.button_about = tk.Button(self.frame_buttons,
                                      text='About Epicycles & sclereid', command=self.on_about)
        self.button_about.pack(side=tk.TOP, fill=tk.X)
        self.frame_buttons.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.Y)
        self.drawing = False
        self.draw()
        self.root.mainloop()
        
    def on_settings(self) :
        tmp = self.show_animation
        self.show_animation = False
        
        top_settings = tk.Toplevel(self.root)
        speed = _scale(top_settings, 'speed', 1, 40, window.SPEED*5., lambda x : x/5.)
        lbin = _scale(top_settings, 'datas', 4, 20, log(window.L_BIN, 2), lambda x : 2**x)
        tracers = _scale(top_settings, 'tracers', 50, 2000, window.MAX_TRACERS)
        mincirc = _scale(top_settings, 'min circle size', 1, 16,
                         7-log(window.MIN_CIRCLE_SIZE, 2), lambda x : round(2**(7-x), 3))
        sorted_ = tk.IntVar()
        _sorted_ = tk.Checkbutton(top_settings, text='sort by radius',
                                      variable=sorted_, onvalue=1, offvalue=0)
        self.sorted_flag and _sorted_.select()
        _sorted_.pack(side=tk.TOP, fill=tk.X)
        
        def top_closing() :
            window.SPEED = speed()
            window.L_BIN = lbin()
            window.MAX_TRACERS = tracers()
            window.MIN_CIRCLE_SIZE = mincirc()
            self.sorted_flag = sorted_.get()
            self.on_clear()
            if tmp :
                self.calculate()
            self.show_animation = tmp
            top_settings.destroy()
        top_settings.protocol('WM_DELETE_WINDOW', top_closing)
        
    def on_export(self):
        filter_zero = tk.IntVar()
        top_export = tk.Toplevel(self.root)
        _filter_zero = tk.Checkbutton(top_export, text='filter static circle',
                                      variable=filter_zero, onvalue=1, offvalue=0)
        _filter_zero.select()
        frames = _scale(top_export, 'frames', 2, 50, 4, lambda x : x*100)
        fps = _scale(top_export, 'fps', 3, 9, 4, lambda x : x*8)
        progressbar = ttk.Progressbar(top_export, orient="horizontal", length=200)
        progresslabel = tk.Label(top_export,
                    text='Note: fps and frames modification are only avalible for mp4 option')
        def _update_progress(s) :
            progressbar.step()
            progresslabel.config(text=s)
        def refresh():
            if self.exporting :
                top_export.after(200, refresh)
            top_export.update()
            progressbar.update()
            progresslabel.update()
        def save_gif() :
            filename = filedialog.asksaveasfilename(parent=self.root,
                        defaultextension='.gif', initialfile='animation.gif')
            if not filename :
                return
            epi_core.gif(filename, window.SIZE, self.r, self.p, self.n, self.v,
                         window.LINED_CIRCLE_MIN, filter_zero=filter_zero.get())
        def save_mp4() :
            filename = filedialog.asksaveasfilename(parent=self.root,
                        defaultextension='.mp4', initialfile='animation.mp4')
            if not filename :
                return
            progressbar.config(maximum=frames()//5)
            top_export.focus_force()
            self.exporting = True
            refresh()
            epi_core.mp4(filename, window.SIZE, self.r, self.p, self.n, self.v,
                         window.LINED_CIRCLE_MIN, filter_zero=filter_zero.get(),
                         fps=fps(), frames=frames(), progresscallback=_update_progress)
            self.exporting = False
        _filter_zero.pack(side=tk.TOP, fill=tk.X)
        button_gif = tk.Button(top_export, text='export as gif', command=save_gif)
        button_mp4 = tk.Button(top_export, text='export as mp4', command=save_mp4)
        button_gif.pack(side=tk.TOP, fill=tk.X)
        button_mp4.pack(side=tk.TOP, fill=tk.X)
        progressbar.pack(side=tk.BOTTOM, fill=tk.X)
        progresslabel.pack(side=tk.BOTTOM, fill=tk.X)

    def on_lines_display(self) :
        if self.show_lines and len(self.points) >= 4:
            self.canvas.delete(self.lines_id)
        self.show_lines = not self.show_lines

    def on_toggle_animation(self):
        self.show_animation = not self.show_animation
        
    def on_open_image(self) :
        tmp = self.show_animation
        self.show_animation = False
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
        self.on_clear()
        self.show_animation = tmp
        
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
                        'Note:   This is a GPL licensed software.\n'
                        )
        self.show_animation = tmp
        
    
    def onclick(self, me) :
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
        self.listbox_points.insert(tk.END, 'point[%d] \tat (%3d, %3d)' 
                                 % (len(self.points)//2, me.x - window.SIZE, me.y - window.SIZE))

    def undo_click(self, me) :
        if len(self.points) > 0:
            self.canvas.delete(self.points_id.pop())
            self.points.pop()
            self.points.pop()
            self.listbox_points.delete(tk.END)
        if len(self.points) == 2:
            self.canvas.delete(self.lines_id)
            
    def on_clear(self) :
        map(lambda x : x and self.canvas.delete(x), self.tracers_id)
        self.tracers_id = [0] * window.MAX_TRACERS
        
    def draw(self) :
        self.canvas.after(window.REFRESH, self.draw)
        if self.drawing :
            return
        self.drawing = True
        if self.show_animation :
            N = len(self.n)
            _tmp = time.time()/N*window.SPEED*2
            tmp = (_tmp-floor(_tmp/2/pi)*2.0*pi)
            x, y = 0.0, 0.0
            _x, _y = 0.0, 0.0
            u = 0
            for k in range(N) :
                rotation = self.v[k]
                _x += self.r[k] * cos(rotation*tmp * self.n[k] + self.p[k])
                _y += self.r[k] * sin(rotation*tmp * self.n[k] + self.p[k])
                self.canvas.coords(self.epicycles_id[k], int(x - self.r[k]) + window.SIZE,\
                                   int(y - self.r[k]) + window.SIZE, int(x + self.r[k]) + window.SIZE,\
                                   int(y + self.r[k]) + window.SIZE)
                if self.r[k] > window.LINED_CIRCLE_MIN :
                    self.canvas.coords(self.through_lines_id[u], int(x) + window.SIZE,\
                                   int(y) + window.SIZE, int(_x) + window.SIZE,\
                                   int(_y) + window.SIZE)
                    u += 1
                x, y = _x, _y
                
            self.upload_tracers(int(x) + window.SIZE, int(y) + window.SIZE)
        if self.show_lines and len(self.points) >= 4 :
            self.canvas.delete(self.lines_id)
            self.lines_id = self.canvas.create_polygon(list(map(lambda z: z+window.SIZE, self.points)), fill='', outline='gray70')
        self.drawing = False

    def upload_tracers(self, x, y) :
        if not self.tn < window.MAX_TRACERS :
            self.tn = 0
        if self.tracers_id[self.tn] == 0 :
            self.tracers_id[self.tn] = self.canvas.create_oval(x - window.TRACER_SIZE, y - window.TRACER_SIZE, x + window.TRACER_SIZE, y + window.TRACER_SIZE, fill='red')
        else:
            self.canvas.coords(self.tracers_id[self.tn], x - window.TRACER_SIZE, y - window.TRACER_SIZE, x + window.TRACER_SIZE, y + window.TRACER_SIZE)
        self.tn = (self.tn + 1) % window.MAX_TRACERS

    def calculate(self) :
        if len(self.points) < 4 :
            return
        _z = (np.append(self.points[::2], [self.points[0]]) + \
                    np.append(self.points[1::2], [self.points[1]]) * 1.0j)/window.SIZE
        _t = np.arange(len(_z))
        f = interp1d(_t, _z)
        t = np.linspace(0, len(_z)-1, window.L_BIN)
        array = f(t)
        map(lambda x : self.canvas.delete(x), self.epicycles_id)
        self.epicycles_id = []
        map(lambda x : self.canvas.delete(x), self.through_lines_id)
        self.through_lines_id = []
        self.listbox_epicycles.delete(0, tk.END)
        acircle = fft2circle.get_circle_fft(array)
        self.r = []
        self.p = []
        self.n = []
        self.v = []
        self.max_through_lines = 0
        if self.sorted_flag :
            acircle = sorted(acircle, key=lambda _: -_[0])
        tmp = 0
        for k, (r, n, l, p) in enumerate(acircle) :
            if r * window.SIZE < window.MIN_CIRCLE_SIZE :
                tmp += 1
                continue  # filter the circles which are too small
            elif r * window.SIZE > window.LINED_CIRCLE_MIN :
                self.max_through_lines += 1
                self.through_lines_id.append(self.canvas.create_line(0, 0, 0, 0, fill='blue'))
            self.r.append(r * window.SIZE)
            self.p.append(p)
            self.n.append(n)
            self.v.append(l)
            self.epicycles_id.append(self.canvas.create_oval(0, 0, 0, 0))
            self.listbox_epicycles.insert(tk.END,
                            'circle[%d] radius=%3.3f phi=%3.3f frequency=%3d %sclockwise' 
                            % (k - tmp, self.r[-1], self.p[-1], n, l==1 and 'counter' or ''))
        export_flag and self.button_export.configure(state=tk.NORMAL)
        self.button_animation.configure(state=tk.NORMAL)

if __name__ == '__main__' :
    window()
