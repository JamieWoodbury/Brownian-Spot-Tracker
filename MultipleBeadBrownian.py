'''This program was written for the Brownian motion experiment at the
University of Toronto. It was designed for the purpose of tracking a multiple
spots through a sequence of frames and then displaying or saving this
information. This program is distributed with the hope that it might be found
useful, but with no warranty, not even the implied warranty of usefulness for
a specific purpose. This file contains the main elements of the program,
intended for use with the supporting Tools file.

Author: Donald J Woodbury, University of Toronto'''

from Tkinter import *
from tkFileDialog import asksaveasfilename, askopenfilename
from math import sqrt
from PIL import Image, ImageDraw, ImageTk, ImageSequence, ImageOps
from scipy.misc import fromimage
from numpy import array, nonzero, zeros, arange, swapaxes, argwhere

class Multiple_Spot_Track:
    def __init__(self, max_frames = 3, max_dist = 40, threshold = 128, \
                 start_frame = 0, end_frame = None, im_seq = None):
        '''Prompts the user to select an image sequence file and the performs
        a multiple bead spot tracking algorithm on the images therein. There
        are two objects meant to be accesed by the user:

        MST.frames :    Contains the images from the original sequence with
                        the location, and trails, of each of the found spots
                        drawn on them.

        MST.tracks :    Contains the information about the location of each of
                        the spot tracks within the image. The object is a list
                        of lists, each list containing the track information
                        and each sublist containing items written in the format
                        (index, (x_location, y_location)), indicating the
                        location of that spot in each frame.

        To make these two objects more usable, the user is provided with a few
        useful methods that can either save, or display MST.frames.

        To initialize this class, the user may configure the algorithm using
        several parameters:

        max_frames :    Defines the maximum number of frames that may separate
                        two tracks in order for them to be considered joined.
                        If the tracks are fragmented, it is possible that this
                        parameter should be increased.

        max_dist :      Similar to max frames, but defining the maximum distance
                        between the start of one track and the end of another
                        for them to be considered joined.

        threshold :     Integer from 0-255. The value a pixel must be for it to
                        be considered a spot. If the contrast is 100%, any value
                        above zero will work.

        start_frame :   Integer, the index of the first image in the image
                        sequence to be analysed.

        end_frame :     Integer, the index of the last image in the image
                        sequence to be analysed.'''

        #Opening the Image Sequence

        self.im_seq = im_seq

        if im_seq == None:
            root = Tk()
            filename = askopenfilename(master = root,
                                       filetypes = [('Tiff','*.tif'), \
                                                    ('GIF','*.gif')],\
                                       title="Open...")
            root.destroy()

            im_seq = Image.open(filename)
            self.im_seq = []
            i = 0
            for frame in ImageSequence.Iterator(im_seq):
                im = ImageSequence.Iterator(im_seq)[i]
                self.im_seq.append(ImageSequence.Iterator(im_seq)[i].copy())
                i += 1

        #Parameters
        self.im_size = self.im_seq[0].size

        self.threshold = threshold
        self.max_frames = max_frames
        self.max_distance = max_dist

        self.start_frame = start_frame
        if end_frame == None:
            self.end_frame = len(self.im_seq)
        else:
            self.end_frame = end_frame

        #Analysis

        self.frames = []
        self.tracks = []

        self.Find_spots()
        self.Track_spots()
        self.Eliminate_short_tracks()

    #___________________Analysis__________________#

    def Find_spots(self):
        '''For each frame in the image sequence, the spots are located and
        defined in a list of lists, each sublist containing all spots found
        in a given frame.'''

        self.spots = []
        for frame in self.im_seq[self.start_frame:self.end_frame]:

            points = threshold2(frame, self.threshold)
            grouped_points = group_points(points)
            centers = center_of_clusters(grouped_points)

            self.spots.append(centers)

    def Track_spots(self):
        '''Takes the information about the location of the spots from the
        Find_spots method and relates the information about the spots to yeild
        the tracks of each individual spot, defined in the list of lists
        self.tracks.'''
        
        i = self.start_frame
        for centers in self.spots:
            for track in self.tracks:
                
                [index, (x0, y0)] = track[-1]
                if index > i-1 or index < i-(self.max_frames+1):
                    continue
                
                j = 0
                for (x1,y1) in centers:
                    if distance((x1,y1), (x0, y0)) < self.max_distance:
                        track.append((i, (x1,y1)))
                        del centers[j]
                        break
                    j+=1

            for center in centers:
                self.tracks.append([(i, center)])

            i += 1

    def Eliminate_short_tracks(self):
        '''Removes all elements in self.tracks that have two or less entries.
        ensures that short blips in the images are not considered.'''
        k = 0         
        while k < len(self.tracks):
            if len(self.tracks[k]) < 3:
                del self.tracks[k]
                k -= 1
            k+=1
            
    def Draw_track(self):
        '''Draws the track of each spot on the images and returns them on the
        list self.frames.'''
        for i in xrange(self.start_frame, self.end_frame):
            frame = draw_chain(self.tracks, self.im_seq[i], i)
            self.frames.append(frame)

        return self.frames

def threshold2(frame, threshold):
    '''Returns a list of the pixel indicies of all of the pixels in the image
    whose value is below the given threshold. Requires 'im_array' to be a 2D
    bitmap array of numbers (for our purposes these numbers represent an
    8-bit image and therefore take on values from 0-255.)'''

    points = []

    frame = frame.point(lambda p: p < threshold)

    im_array = fromimage(frame).astype('float')

    try:
        B = argwhere(im_array)
        (ystart, xstart), (ystop, xstop) = B.min(0), B.max(0) + 1 
        cropped_array = im_array[ystart:ystop, xstart:xstop]
            
        p = array(nonzero(cropped_array)).swapaxes(0,1)

        for (y,x) in p:
            points.append((xstart+x,ystart+y))
    except ValueError:
        pass
        
    return points

def group_points(points):
    '''Returns a list of lists of tuples, each containing the points in the list
    of tuples 'points' that are adjacent to eachother.'''

    points_list = points[:]
    
    groups = []

    while len(points_list) > 0:
        
        new_group = [points_list[0]]
        del points_list[0]
        i = 0
        while len(new_group) > i:
            (x, y) = new_group[i]
            j = 0
            while j < len(points_list):
                point = points_list[j]
                if x-2 < point[0] < x+2 and y-2 < point[1] < y+2:
                    new_group.append(point)
                    del points_list[j]
                    j -= 1 
                j += 1
            i += 1
        groups.append(new_group)

    return groups

def find_center2(tups):
    '''Take in a list of 2-tuples. Find the center of the coordinates those
       2-tuples represent and return the center as a 2-tuple of floats.'''

    x, y = 0, 0
    for t in tups:
        x, y = x + t[0], y + t[1]
    x, y = float(x) / len(tups), float(y) / len(tups)

    return (x, y)

def center_of_clusters(groups):
    '''Returns a list of the vector average of each list of tuples in the list
    groups.'''

    centers = []

    for group in groups:
        center = find_center2(group)
        centers.append(center)

    return centers

def distance((x1, y1),(x2, y2)):
    '''Returns the distance between the two tuples representing cartesian
    coordinates.'''
    
    dist = ((x1-x2)**2+(y1-y2)**2)**0.5
    
    return dist

def draw_chain(paths, image, index):
    '''Returns a copy of the image 'image' with each path in the list 'paths'
    drawn up to the the given index.'''

    im = image.copy().convert('RGB')
    
    draw = ImageDraw.Draw(im)
    
    num_paths = len(paths)
    d = 2

    i = 0
    for path in paths:
        points = []
        for point in path:
            if point[0] <= index:
                points.append(point[1])
            if point[0] == index:
                x, y = point[1]
                draw.rectangle((x-d, y-d, x+d, y+d), fill =\
                    (255-(255*i)/num_paths, 0, (255*i)/num_paths))
        
        draw.line(points, fill =(255-(255*i)/num_paths, 0, (255*i)/num_paths))
        i += 1
    
    return im
