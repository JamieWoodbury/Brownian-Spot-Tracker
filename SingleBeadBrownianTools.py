'''This program was written for the Brownian motion experiment at the
University of Toronto. It was designed for the purpose of tracking a single
spot through a sequence of frames and then displaying, saving or plotting this
information. This program is distributed with the hope that it might be found
useful, but with no warranty, not even the implied warranty of usefulness for
a specific purpose. This file contains the supporting tools used by the main
program.

Author: Donald J Woodbury, University of Toronto'''

from Tkinter import *
from PIL import Image, ImageSequence, ImageDraw, ImageTk
from numpy import average
from pylab import plot, xlabel, ylabel, show, title

def points_below_threshold(image, threshold, bbox):
    '''Returns a list of the pixel indicies of all of the pixels in the image
    bounded by the bbox whose value is below the given threshold.'''

    pix = image.load()
    (xsize, ysize) = image.size

    points = []

    for x in xrange(max(0, bbox[0]), min(xsize, bbox[2])):
        for y in xrange(max(0, bbox[1]), min(ysize, bbox[3])):
            if pix[x,y] < threshold:
                points.append((x, y))
    
    return points

def draw_point(point, image):
    '''Returns a copy of the image 'image' with each point in the list 'points'
    drawn as a red pixel drawn on the image.'''

    image = image.convert('RGB')
    pix = image.load()

    for x in xrange(max(0, int(point[0]) - 2),\
                    min(int(point[0]) + 3, image.size[0])):
        for y in xrange(max(0, int(point[1]) - 2),\
                    min(int(point[1]) + 3, image.size[1])):
            pix[x, y] = (255, 0, 0)
    
    return image

def cluster_center(points):
    '''returns the vector average the (x,y) tuples in the list points.'''
    
    x, y = zip(*points)
    
    xavg = average(x)
    yavg = average(y)

    return [xavg, yavg]

class Plot_track:
    def __init__(self, track):
        '''Creates a Tkinter window that allows the user to enter the plot
        labels. Once the user accepts these values, a pylab plot is launched.'''

        self.track = track
        
        self.window = Tk()
        self.window.title("Plot Labels")

        self.title = StringVar(master = self.window)
        self.title.set('Spot Track')
        self.x_label = StringVar(master = self.window)
        self.x_label.set('x position (pix)')
        self.y_label = StringVar(master = self.window)
        self.y_label.set('y position (pix)')
        
        L1 = Label(self.window, text='Plot Title: ')
        L1.grid(row = 0, sticky = 'w')
        L2 = Label(self.window, text='x Label: ')
        L2.grid(row = 1, sticky = 'w')
        L3 = Label(self.window, text='y Label: ')
        L3.grid(row = 2, sticky = 'w')

        ask_title = Entry(self.window, textvariable=self.title, width= 40)
        ask_title.grid(row = 0, column = 1, columnspan = 3, )
        ask_x_label = Entry(self.window, textvariable=self.x_label, width= 40)
        ask_x_label.grid(row = 1, column = 1, columnspan = 3)
        ask_y_label = Entry(self.window, textvariable=self.y_label, width= 40)
        ask_y_label.grid(row = 2, column = 1, columnspan = 3)
        
        ask_ok = Button(self.window, text='Plot', command = self.Plot_graph)
        ask_ok.grid(row = 3, column = 1)
        ask_cancel = Button(self.window, text='Cancel', command = self.End_plot)
        ask_cancel.grid(row = 3, column = 2)

        self.window.protocol("WM_DELETE_WINDOW", self.End_plot)

        self.window.mainloop()
        
    def Plot_graph(self):
        '''launches a pylab plot of the track.'''
        self.window.destroy()

        x , y = zip(*self.track)
        
        plot(x, y)
        xlabel(self.x_label.get())
        ylabel(self.y_label.get())
        title(self.title.get())
        

        show()
    def End_plot(self):
        '''Closes the Tkinter window.'''
        self.window.destroy()
