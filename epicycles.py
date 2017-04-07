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
import threading
import webbrowser
from math import sin, cos, floor, pi, log
import numpy as np
import fft2circle
from scipy.interpolate import interp1d, splprep, splev

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
    MIN_SIZE = 100
    SIZE = 320
    REFRESH = 40  # refresh every 40 miliseconds
    MAX_TRACERS = 1000
    TRACER_SIZE = 2
    SPEED = 2.
    L_BIN = 1024
    LINED_CIRCLE_MIN = 5.
    MIN_CIRCLE_SIZE = 0.3
    PROGRESSCALLBACKFREQ = 5
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Epicycles --An Enternal...')
        self.root.resizable(0, 0)
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
        self.on_settings_opened = False
        self.on_export_opened = False
        self.on_about_opened = False
        self.interpolation = 1
        # 0 stands for none, 1 stands for linear, 2 stands for splev
        # widgets
        self.frame_buttons = tk.Frame(self.root, width=150)
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
        self.button_clear_all = tk.Button(self.frame_buttons,
                                      text='clear everything', command=self.on_clear_all)
        self.button_clear_all.pack(side=tk.TOP, fill=tk.X)
        self.button_about = tk.Button(self.frame_buttons,
                                      text='About Epicycles & sclereid', command=self.on_about)
        self.button_about.pack(side=tk.TOP, fill=tk.X)
        self.frame_buttons.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.Y)
        self.drawing = False
        self.draw()
        self.root.mainloop()
    
    def on_settings(self) :
        if self.on_settings_opened :
            return
        self.on_settings_opened = True
        tmp = self.show_animation
        self.show_animation = False
        top_settings = tk.Toplevel(self.root)
        top_settings.resizable(0, 0)
        top_settings.title('Settings')
        speed = _scale(top_settings, 'speed', 1, 40, window.SPEED*5., lambda x : x/5.)
        lbin = _scale(top_settings, 'datas', 4, 20, log(window.L_BIN, 2), lambda x : 2**x)
        tracers = _scale(top_settings, 'tracers', 50, 2000, window.MAX_TRACERS)
        mincirc = _scale(top_settings, 'min circle size', 1, 16,
                         7-log(window.MIN_CIRCLE_SIZE, 2), lambda x : round(2**(7-x), 3))
        sorted_ = tk.IntVar()
        _sorted_ = tk.Checkbutton(top_settings, text='sort by radius',
                                      variable=sorted_, onvalue=1, offvalue=0)
        self.sorted_flag and _sorted_.select()
        
        interp_ = tk.IntVar()
        _interp_ = tk.LabelFrame(top_settings, text='Interpolation')
        for i, text in enumerate(['none', 'linear', 'spline']) :
            __btn = tk.Radiobutton(_interp_, text=text, variable=interp_, value=i)
            self.interpolation == i and __btn.select()
            __btn.pack(anchor=tk.W)
        _interp_.pack(side=tk.TOP, fill=tk.X)
        _sorted_.pack(side=tk.TOP, fill=tk.X)
        def top_closing() :
            window.SPEED = speed()
            window.L_BIN = lbin()
            window.MAX_TRACERS = tracers()
            window.MIN_CIRCLE_SIZE = mincirc()
            self.sorted_flag = sorted_.get()
            self.interpolation = interp_.get()
            self.on_clear()
            if tmp :
                self.calculate()
            self.show_animation = tmp
            top_settings.destroy()
            self.on_settings_opened = False
        top_settings.protocol('WM_DELETE_WINDOW', top_closing)
        
    def on_export(self):
        if self.on_export_opened :
            return
        self.on_export_opened = True
        filter_zero = tk.IntVar()
        top_export = tk.Toplevel(self.root)
        top_export.resizable(0, 0)
        top_export.title('Export')
        frame_widgets = tk.Frame(top_export)
        _filter_zero = tk.Checkbutton(frame_widgets, text='filter static circle',
                                      variable=filter_zero, onvalue=1, offvalue=0)
        _filter_zero.select()
        frames = _scale(frame_widgets, 'frames', 2, 50, 4, lambda x : x*100)
        fps = _scale(frame_widgets, 'fps', 3, 9, 4, lambda x : x*8)
        progressbar = ttk.Progressbar(top_export, orient="horizontal", length=400)
        progresslabel = tk.Label(top_export,
                    text='Note: fps and frames modification\n are only avalible for mp4 option')
        self.export_flag = False
        self.kill_flag = False
        def _update_progress(s) :
            if self.kill_flag :
                self.kill_flag = False
                raise KeyboardInterrupt
            if s == epi_core.FINISH_STRING :
                self.export_flag = False
            if self.on_export_opened :  #sometimes the user have closed the window in advance
                progressbar.step()
                progresslabel.config(text=s)
                top_export.update()
                progressbar.update()
                progresslabel.update()
        def save_gif() :
            filename = filedialog.asksaveasfilename(parent=top_export,
                        defaultextension='.gif', initialfile='animation.gif')
            if not filename :
                return
            t = threading.Thread(target = lambda : epi_core.gif(filename, window.SIZE, self.r, self.p, self.n, self.v,
                         line_min=window.LINED_CIRCLE_MIN, frames=320, filter_zero=filter_zero.get()))
            progressbar.config(maximum=2)
            button_gif.configure(state=tk.DISABLED)
            button_mp4.configure(state=tk.DISABLED)
            t.run()
        def save_mp4() :
            filename = filedialog.asksaveasfilename(parent=top_export,
                        defaultextension='.mp4', initialfile='animation.mp4')
            if not filename :
                return
            top_export.focus_force()
            self.exporting = True
            t = threading.Thread(target = lambda : epi_core.mp4(filename, window.SIZE, self.r, self.p, self.n, self.v,
                         line_min=window.LINED_CIRCLE_MIN, filter_zero=filter_zero.get(),
                         fps=fps(), frames=frames(), progresscallback=_update_progress,
                         progresscallbackfreq = window.PROGRESSCALLBACKFREQ))
            progressbar.config(maximum=frames()*2//5 + 2)
            button_gif.configure(state=tk.DISABLED)
            button_mp4.configure(state=tk.DISABLED)
            self.export_flag = True
            t.run()
        def top_closing() :
            if self.export_flag :
                if msgbox.askyesno(message='Export progress not finished, \n'
                    'exit anyway?') :
                    self.kill_flag = True
                else :
                    return
            top_export.destroy()
            self.on_export_opened = False
        _filter_zero.pack(side=tk.TOP, anchor=tk.W)
        button_gif = tk.Button(frame_widgets, text='export as gif', command=save_gif)
        button_mp4 = tk.Button(frame_widgets, text='export as mp4', command=save_mp4)
        button_gif.pack(side=tk.TOP, fill=tk.X)
        button_mp4.pack(side=tk.TOP, fill=tk.X)
        frame_widgets.pack(side=tk.TOP)
        progressbar.pack(side=tk.BOTTOM, fill=tk.X)
        progresslabel.pack(side=tk.BOTTOM, fill=tk.X)
        top_export.protocol('WM_DELETE_WINDOW', top_closing)

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
        if self.on_about_opened :
            return
        self.on_about_opened = True
        top_about = tk.Toplevel(self.root)
        top_about.title('About Epicycles')
        def hyperlinklabel(master, s, link, **kw) :
            u = tk.Label(master, text=s, foreground='blue', cursor='hand', anchor=tk.W, **kw)
            u.bind('<Button-1>', lambda event : webbrowser.open_new(link))
            return u
        frame_description = tk.LabelFrame(top_about, text='Description:')
        tk.Label(frame_description, text='A small program to display epicycles with given image.', anchor=tk.W).pack()
        hyperlinklabel(frame_description, 'Introduction', r'https://sclereid.github.io/epicycles').pack()
        hyperlinklabel(frame_description, 'Source on GitHub', r'https://github.com/sclereid/epicycles').pack()
        frame_description.pack(side=tk.TOP, fill=tk.X)
        frame_credits = tk.LabelFrame(top_about, text='Credits:')
        tk.Label(frame_credits, text='Authors are:', anchor=tk.W).pack()
        hyperlinklabel(frame_credits, 'sclereid', r'https://github.com/sclereid').pack()
        hyperlinklabel(frame_credits, 'zyyztyy', r'https://github.com/zzyztyy').pack()
        frame_credits.pack(side=tk.TOP, fill=tk.X)
        frame_license = tk.LabelFrame(top_about, text='License:')
        tk.Label(frame_license, text='You should have received a copy of the GNU \n'
                 'General Public License along with this program, \n'
                 'if not, see :', anchor=tk.W).pack()
        hyperlinklabel(frame_license, r'http://www.gnu.org/licenses/', r'http://www.gnu.org/licenses/').pack()
        frame_license.pack(side=tk.TOP, fill=tk.X)
        def top_closing() :
            self.on_about_opened = False
            top_about.destroy()
        top_about.protocol('WM_DELETE_WINDOW', top_closing)
    
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

    def undo_click(self, *args) :
        if len(self.points) > 0:
            self.canvas.delete(self.points_id.pop())
            self.points.pop()
            self.points.pop()
            self.listbox_points.delete(tk.END)
        if len(self.points) == 2:
            self.canvas.delete(self.lines_id)
            
    def on_clear(self) :
        for x in self.tracers_id :
            x and self.canvas.delete(x)
        self.tracers_id = [0] * window.MAX_TRACERS
    
    def on_clear_all(self) :
        tmp = self.show_animation
        self.show_animation = False
        if msgbox.askyesno('Are you sure?', "By clicking 'yes', \n"
                           "all your current work will be abandont.") :
            for x in self.epicycles_id :
                self.canvas.delete(x)
            self.epicycles_id = []
            for x in self.through_lines_id :
                self.canvas.delete(x)
            self.through_lines_id = []
            self.listbox_epicycles.delete(0, tk.END)
            while len(self.points) > 0 :
                self.undo_click()
        else :
            self.show_animation = tmp
        self.on_clear()
        
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
            self.lines_id = self.canvas.create_polygon([z + window.SIZE for z in self.points], fill='', outline='gray70')
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
        self.show_animation = False
        self.on_clear()
        for x in self.epicycles_id :
            self.canvas.delete(x)
        self.epicycles_id = []
        for x in self.through_lines_id :
            self.canvas.delete(x)
        self.through_lines_id = []
        self.listbox_epicycles.delete(0, tk.END)
        if self.interpolation == 1 :
            _z = (np.append(self.points[::2], [self.points[0]]) + \
                        np.append(self.points[1::2], [self.points[1]]) * 1.0j)/window.SIZE
            _t = np.arange(len(_z))
            f = interp1d(_t, _z)
            t = np.linspace(0, len(_z)-1, window.L_BIN)
            array = f(t)
        elif self.interpolation == 2 :
            try :
                ax = np.append(self.points[::2], [self.points[0]])
                ay = np.append(self.points[1::2], [self.points[1]])
                tck, u = splprep([ax, ay], s=0)
                unew = np.linspace(0, 1, window.L_BIN)
                out = splev(unew, tck)
                array = out[0]/window.SIZE + out[1]*1.0j/window.SIZE
            except SystemError:
                msgbox.showerror('Error', 'Bad input points: \n'
                                 'Did you click somewhere more than once?\n'
                                 'Try change input points or use another interpolation algorithm.',
                                 icon='error')
                self.button_animation.configure(state=tk.DISABLED)
                return
        else :
            array = np.append(self.points[::2], [self.points[0]])/window.SIZE + \
                np.append(self.points[1::2], [self.points[1]])/window.SIZE*1.0j
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
