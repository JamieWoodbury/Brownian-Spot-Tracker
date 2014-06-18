'''This program was written for the Brownian motion experiment at the
University of Toronto. It was designed for the purpose of tracking a single
spot through a sequence of frames and then displaying, saving or plotting this
information. This program is distributed with the hope that it might be found
useful, but with no warranty, not even the implied warranty of usefulness for
a specific purpose. This file contains the main elements of the program,
intended for use with the supporting Tools file.

Author: Donald J Woodbury, University of Toronto'''


from SingleBeadBrownianTools import *
from MultipleBeadBrownian import *
from Tkinter import *
from tkSimpleDialog import askstring
from tkFileDialog import asksaveasfilename, askopenfilename
from PIL import Image, ImageSequence, ImageDraw, ImageOps
from numpy import average
import os
import os.path

class Spot_Track:
    def __init__(self):
        '''Prompts the user to select an image sequence file and creates the
        Tkinter window with bindings, scrollbars and images.'''
        
        self.root = Tk()
        self.root.title('Spot Tracker')

        #Opening the Image Sequence
        if self.Open_im_seq() == -1:
            self.Close_window()
            return None
        
        #Parameters
        self.im_size = self.im_seq[0].size
        self.Tracking = False
        self.view_all_tracks = False

        #Results

        self.track = []
        self.frames = []
        
        #Building the Tkinter window
        self.Draw_canvas()
        self.Draw_sliders()

        #bindings
        self.Bindings()

        self.root.mainloop()

    def Draw_canvas(self):
        '''Creates the Tkinter window and populates it with the images from
        the user selected image sequence file.'''
        
        frame = Frame(self.root)
        frame.pack()
        
        self.label = Label(frame, text="Select Spot Location:", anchor = 'n')
        self.label.pack()
        
        self.canvas = Canvas(frame, width=self.im_size[0], height=self.im_size[1])
        self.canvas.pack()

        self.tkimg = ImageTk.PhotoImage(self.im_seq[0].convert('RGB'))

        self.im_id = self.canvas.create_image(0,0,image=self.tkimg,anchor="nw")

    def Open_im_seq(self):
        '''Opens the sequence of images used for analysis. When called, this
        function will open a file selection dialog in which the user may either
        select a Tiff/Gif animation file, or the first image in a sequence of
        images named as "ImagenameFramenumber.jpg"'''
        self.filename = askopenfilename(master = self.root,
                                   filetypes = [('All Files',\
                                                 ('*.jpg', '*.tif', '*.gif')),
                                                ('Jpeg','*.jpg'),
                                                ('Tiff','*.tif'), \
                                                ('GIF','*.gif')],\
                                   title="Open...")

        if len(self.filename) == 0:
            return -1

        self.im_seq = []

        if self.filename[-3:] == 'tif' or self.filename[-3:] == 'gif':
            im_seq = Image.open(self.filename)
            i = 0
            for frame in ImageSequence.Iterator(im_seq):
                im = ImageSequence.Iterator(im_seq)[i]
                self.im_seq.append(im.copy())
                i += 1
        else:
            directory, im_name = os.path.split(self.filename)
            im_num = int(''.join(s for s in im_name if s.isdigit()))
            im_name = ''.join(s for s in im_name if not s.isdigit())[:-4]
            
            while os.path.isfile(directory+'/'+im_name+str(im_num)+'.jpg'):
                image = Image.open(directory+'/'+im_name+str(im_num)+'.jpg')
                self.im_seq.append(image)
                im_num+=1

    def Open_new(self):
        '''Resets the program to its initial state and prompts the user to
        open a new image sequence.'''
        if self.Open_im_seq() == -1:
            return None
        self.Reset()

    #_________________Sliders__________________#

    def Draw_sliders(self):
        '''Defines the Sliders in the Tkinter window'''
        self.frame_number = IntVar()
        self.frame_number.set(0)
        self.frame_slider = Scale(self.root, command = self.Update_frame, \
                                  label="Frame Number:", \
                                  variable = self.frame_number,\
                                  length=self.im_size[0], orient=HORIZONTAL, \
                                  from_= 0, to=len(self.im_seq)-1)
        self.frame_slider.pack()

        self.threshold = IntVar()
        self.threshold.set(128)
        self.threshold_slider = Scale(self.root, variable = self.threshold, \
                                      label="Threshold:",length=self.im_size[0], \
                                      orient=HORIZONTAL, to=255)
        self.threshold_slider.pack()

        self.max_distance = IntVar()
        self.max_distance.set(30)
        self.max_dist_slider = Scale(self.root, variable = self.max_distance, \
                                     label='Maxiumum distance the spot may'+\
                                     ' travel between frames:',\
                                     length=self.im_size[0], orient=HORIZONTAL,\
                                     to=100)
        self.max_dist_slider.pack()

    def Update_frame(self, event):
        '''Updates the frame displayed when the frame_slider is moved. If
        no analysis has been performed, the raw images will be displayed.
        After the analysis, the spot location will be displayed.'''
        self.frame_num = min(self.frame_number.get(), len(self.im_seq)-1)
        if not self.Tracking:
            self.tkimg.paste(self.im_seq[self.frame_num])
        elif self.view_all_tracks_var.get():
            self.tkimg.paste(self.all_track_frames[self.frame_num-\
                                                   self.start_frame])
        else:
            self.tkimg.paste(self.frames[self.frame_num-self.start_frame])

    #_________________Menus__________________#

    def File_menu(self):
        '''Builds the File menu'''

        self.menu = Menu(self.root)
        
        self.filemenu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label="Open...",\
                                  command=self.Open_new)
        self.filemenu.add_command(label="Reset",\
                                  command=self.Reset)
        self.view_all_tracks_var = IntVar()
        self.filemenu.add_checkbutton(label="View All Tracks",\
                                  command=self.View_all_tracks,\
                                      variable = self.view_all_tracks_var)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Save Track to File",\
                                  command=self.Save_file)
        self.filemenu.add_command(label="Save Images",\
                                  command=self.Save_frames)
        self.filemenu.add_command(label="Plot",\
                                  command=self.Plot)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.Close_window)
        
        self.helpmenu = Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=self.helpmenu)

        self.root.config(menu=self.menu)

    def Reset(self):
        '''Resets the window back to its initial state.'''
        self.canvas.pack_forget()
        self.label.pack()
        self.canvas.pack()
        self.threshold_slider.pack()
        self.max_dist_slider.pack()
        self.frame_slider.config(from_ = 0, to = len(self.im_seq)-1)
        
        self.menu.delete(1,2)

        self.Tracking = 0
        self.view_all_tracks_var.set(0)

        self.Update_frame(0)
        self.track = []
        self.frames = []
        
        self.root.update()
        window_size = (int(self.root.winfo_reqwidth()),\
                       int(self.root.winfo_reqheight()))
        self.root.geometry("%dx%d" % window_size)

    def View_all_tracks(self):
        '''Finds and displays all spot tracks found within the image.'''
        if not self.view_all_tracks_var.get():
            self.frame_slider.config(to = self.end_frame)
            self.Update_frame(0)
            
        else:
            all_tracks = Multiple_Spot_Track(max_frames = 3,\
                                max_dist = self.max_distance.get(),\
                                threshold = self.threshold.get(),\
                                start_frame = self.start_frame, \
                                end_frame = None,\
                                im_seq = self.im_seq)
            self.all_track_frames = all_tracks.Draw_track()
            self.frame_slider.config(to = len(self.im_seq)-1)
            
            self.Update_frame(0)
        

    #______________Event Bindings_______________#
    
    def Bindings(self):
        '''Defines the bindings in the tkinter window.'''
        self.canvas.bind("<Button-1>", self.Start_tracking)
        self.root.protocol("WM_DELETE_WINDOW", self.Close_window)

    def Start_tracking(self, event):
        '''Initializes the parameters for Spot tracking. First it defines the
        initial location of the spot and the starting frame. It then removes
        both the the label and threshold slider (since neither are needed for
        displaying the spot track.) It then calls the Analysis function.'''
        if not self.Tracking:
            self.Tracking = 1
            
            self.starting_pos = (event.x, event.y)
            self.start_frame = self.frame_num

            self.label.pack_forget()
            self.threshold_slider.pack_forget()
            self.max_dist_slider.pack_forget()
            self.frame_slider.config(from_ = self.frame_num)
            self.File_menu()

            self.root.update()
            window_size = (int(self.root.winfo_reqwidth()),\
                           int(self.root.winfo_reqheight()))
            self.root.geometry("%dx%d" % window_size)

            self.Analysis()

    def Close_window(self):
        '''Closes the Tkinter window.'''
        self.root.destroy()

    #_____________Analysis______________#

    def Analysis(self):
        '''Creates two lists, one containing the location of the spot from the
        starting frame to three frames after it was last found in the window.
        The other containing the frames with the spot drawn on them.'''

        spot_found = True
        i = self.start_frame
        self.max_dist = self.max_distance.get()
        j = 1
        spot_loc = self.starting_pos

        print 'Tracking Spot...'

        while i < len(self.im_seq) and spot_found:
            frame = self.im_seq[i]
                
            bbox = [int(spot_loc[0]+0.5) - self.max_dist*j, \
                   int(spot_loc[1]+0.5) - self.max_dist*j, \
                   int(spot_loc[0]+0.5) + self.max_dist*j, \
                   int(spot_loc[1]+0.5) + self.max_dist*j]
                
            points = points_below_threshold(frame, self.threshold.get(), bbox)
                
            if points == []:
                j += 1 
                print 'Cannot find spot in frame %d' % i
                if j == 4:
                    spot_found = False
            else:
                spot_loc = cluster_center(points)
                j = 1

            (x, y) = (spot_loc[0], abs(spot_loc[1]-self.im_size[0]))
            frame = draw_point(spot_loc, frame)

            self.frames.append(frame)
            self.track.append((x, y))

            i += 1

        print 'Done.'

        self.end_frame = i-1

        self.frame_slider.config(to = self.end_frame)
        self.Update_frame(self.start_frame)

    #_______________Some Useful methods____________#

    def Save_file(self):
        '''Saves the x, y coordinates of the track to a tab delimated file.'''

        filename = asksaveasfilename(filetypes = [('Text File','*.txt')],\
                                     title="Save Track File As...",\
                                     master = self.root)
        
        t = 0
        if len(filename) > 0:
            framerate = askstring('Enter Frame Rate',\
                                  'Time between frames:',\
                                  initialvalue = '0.1', \
                                  parent = self.root)

        if len(filename) > 0 and framerate != None:
            print framerate
            track_file = open(filename, 'w')
            track_file.write('time(s)\tx pos\ty pos\n\n')
            for pos in self.track[:-3]:
                track_file.write('%.2f\t%.2f\t%.2f\n' % (t, pos[0],\
                                abs(pos[1]-self.im_size[1])))
                t += float(framerate)
            track_file.close()

    def Save_frames(self):
        '''Saves the frames showing the spot location to the user selected
        file and under the user selected name.'''
        directory = asksaveasfilename(master = self.root,\
                                      title="Save Track Images To...")
        if len(directory) > 0:
            i = 1
            for frame in self.frames[:-3]:
                frame.save(directory +'_' + str(i) + '.jpg')
                i += 1
            
    def Plot(self):
        '''Launches a pylab plot of the position of the spot in each frame.'''
        Plot_track(self.track)

if "__main__" == __name__:

    track = Spot_Track()
