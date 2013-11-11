#!/usr/bin/python3

import sys
print((sys.version))

if sys.version_info[0] < 3:
    print("This script requires Python version 3.x")
    sys.exit(1)

# if sys.platform == 'linux':
#     print("Found Linux distribution -")
# elif sys.platform == 'darwin':
#     print("Found Mac OSX distribution -")
#     # Add sys path for PIL
#     sys.path.append("/opt/local/Library/Frameworks/Python.framework/Versions/3.3/lib/python3.3/site-packages")

from PIL import Image, ImageTk

from cgitb import text
from distutils.cmd import Command
from tkinter import Canvas
from cgi import log
import glob
import os
import tkinter as MTk
import tkinter.filedialog as Fd
import tkinter.messagebox as Mb
from StringBuilder import StringBuilder
from Triple import Triple
import codecs
import logging
from logging.handlers import RotatingFileHandler
import re

LOG_LEVEL = logging.DEBUG
formatter = logging.Formatter('%(asctime)s - %(levelname)s -  %(name)s -> %(message)s')
file_handler = RotatingFileHandler('mgn-meta.log', 'a', 1048576, 1)
file_handler.setLevel(LOG_LEVEL)
file_handler.setFormatter(formatter)

steam_handler = logging.StreamHandler()
steam_handler.setLevel(LOG_LEVEL)

class Presentation(MTk.Frame):

    def __init__(self, controller, **kwargs):
        self.logger = logging.getLogger('Presentation')
        self.logger.setLevel(LOG_LEVEL)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(steam_handler)

        self.controller = controller

        self.frame = MTk.Tk()
        MTk.Frame.__init__(self, self.frame, width=1280, height=720, **kwargs)
        self.frame.option_readfile("look-and-feel-options.ini")
        self.path = MTk.StringVar()

        self._initView()
        self._bindKey()

    def _initView(self):
        self.frame.wm_title("MiniGal Nano++ metadata generator")
        self.pack()

        ##########
        self.browse_pnl = MTk.Frame(self)
        self.browse_pnl.pack(anchor=MTk.N, expand=MTk.YES, fill=MTk.X)

        self.separator1 = MTk.Frame(self, height=2, bd=1, relief=MTk.SUNKEN)
        self.separator1.pack(fill=MTk.X, padx=5, pady=5)

        self.edit_pnl = MTk.Frame(self)
        self.edit_pnl.pack(anchor=MTk.S, expand=MTk.YES, fill=MTk.X)

        self.tools_pnl = MTk.Frame(self.edit_pnl)
        self.tools_pnl.pack(side=MTk.LEFT, fill=MTk.Y, padx=4)

        self.img_pnl = MTk.Frame(self.edit_pnl)
        self.img_pnl.pack(side=MTk.LEFT, fill=MTk.BOTH)

        ##########
        self.path_lbl = MTk.Label(self.browse_pnl, text="Gallery\'s path:", anchor=MTk.W, fg="black")
        self.path_lbl.pack(anchor=MTk.NW, padx=4)

        self.path_txt_line = MTk.Entry(self.browse_pnl, textvariable=self.path)
        self.path_txt_line.pack(padx=4, side=MTk.LEFT, expand=MTk.YES, fill=MTk.X)

        self.browse_btn = MTk.Button(self.browse_pnl, text="Browse", command=self._browse)
        self.browse_btn.pack(padx=4, side=MTk.LEFT)

        ##########
        self.img_lbl = MTk.Label(self.img_pnl, text="none")
        self.img_lbl.pack(expand=MTk.YES)

        self.canvas = MTk.Canvas(self.img_pnl)
        self.canvas.config(width=917, height=588)

        ##
        self.sbarV = MTk.Scrollbar(self.img_pnl, orient=MTk.VERTICAL)
        self.sbarH = MTk.Scrollbar(self.img_pnl, orient=MTk.HORIZONTAL)

        self.sbarV.config(command=self.canvas.yview)
        self.sbarH.config(command=self.canvas.xview)

        self.canvas.config(yscrollcommand=self.sbarV.set)
        self.canvas.config(xscrollcommand=self.sbarH.set)

        self.sbarV.pack(side=MTk.RIGHT, fill=MTk.Y)
        self.sbarH.pack(side=MTk.BOTTOM, fill=MTk.X)

        self.canvas.pack(side=MTk.LEFT, expand=MTk.YES, fill=MTk.BOTH)

        ##########
        self.gtitle_lbl = MTk.Label(self.tools_pnl, text="Gallery\'s title:", anchor=MTk.W, fg="black")
        self.gtitle_lbl.pack(anchor=MTk.W)

        self.gtitle_fld = MTk.Entry(self.tools_pnl, width=40)
        self.gtitle_fld.pack(anchor=MTk.W)

        self.gcomment_lbl = MTk.Label(self.tools_pnl, text="Gallery\'s comment:", anchor=MTk.W, fg="black")
        self.gcomment_lbl.pack(anchor=MTk.W)

        self.gcomment_fld = MTk.Text(self.tools_pnl, width=40, height=5)
        self.gcomment_fld.pack(anchor=MTk.W)

        self.gvalidate_btn = MTk.Button(self.tools_pnl, text="Validate", command=self._validateGalleryInfo)
        self.gvalidate_btn.pack(anchor=MTk.E)

        ##
        self.separator2 = MTk.Frame(self.tools_pnl, height=2, bd=1, relief=MTk.SUNKEN)
        self.separator2.pack(fill=MTk.X, padx=5, pady=5)

        #####
        self.img_info_pnl = MTk.Frame(self.tools_pnl)
        self.img_info_pnl.pack(pady=4)

        ##
        self.ititle_lbl = MTk.Label(self.img_info_pnl, text="Image\'s title:", anchor=MTk.W, fg="black")
        self.ititle_lbl.pack(anchor=MTk.W)

        self.ititle_fld = MTk.Entry(self.img_info_pnl, width=40)
        self.ititle_fld.pack(anchor=MTk.W)

        self.icomment_lbl = MTk.Label(self.img_info_pnl, text="Image\'s comment:", anchor=MTk.W, fg="black")
        self.icomment_lbl.pack(anchor=MTk.W)

        self.icomment_fld = MTk.Text(self.img_info_pnl, width=40, height=5)
        self.icomment_fld.pack(anchor=MTk.W)

        ##
        self.img_btn_pnl = MTk.Frame(self.img_info_pnl)
        self.img_btn_pnl.pack(anchor=MTk.E)

        self.nxt_img_btn = MTk.Button(self.img_btn_pnl, text="Previous", command=self.controller.previous)
        self.nxt_img_btn.pack(side=MTk.LEFT)

        self.nxt_img_btn = MTk.Button(self.img_btn_pnl, text="Next", command=self.controller.next)
        self.nxt_img_btn.pack(side=MTk.LEFT)

        ##
        self.separator3 = MTk.Frame(self.tools_pnl, height=2, bd=1, relief=MTk.SUNKEN)
        self.separator3.pack(fill=MTk.X, padx=5, pady=5)

        self.generate_btn = MTk.Button(self.tools_pnl, text="Generate file", command=self._execute)
        self.generate_btn.pack(anchor=MTk.N)

    def _bindKey(self):
        self.frame.bind('<Control-Q>', self._quit)
        self.frame.bind('<Control-q>', self._quit)

        self.frame.bind('<Control-O>', self._browse)
        self.frame.bind('<Control-o>', self._browse)

        # Disable 'Enter' key in the Text widget
        self.gcomment_fld.bind("<Return>", lambda e: "break")
        self.icomment_fld.bind("<Return>", lambda e: "break")

    def mainloop(self):
        self._canvasMainloop()
        self.frame.mainloop()
        self.frame.destroy()

    def _canvasMainloop(self):
        ifile = Image.open("index.jpeg")
        picture = ImageTk.PhotoImage(ifile)
        self.image_on_canvas = self.canvas.create_image(0, 0, image=picture, anchor=MTk.NW)
        self.canvas.mainloop()
        self.canvas.destroy()

    def _quit(self, event=MTk.NONE):
        self.frame.destroy()

    def _browse(self, event=MTk.NONE):
        self.path = Fd.askdirectory(title="Select a directory")

        # set the new path
        self.controller.clear()
        self.controller.setPath(self.path)

    def _validateGalleryInfo(self):
        self.controller.setGalleryInfo(self.gtitle_fld.get(), self.gcomment_fld.get(1.0, 1.65000))

    def _execute(self):
        self.controller.execute()
        Mb.showinfo("", "Treatment completed")

    def update(self, subject):
        self.logger.debug("Update the presentation")

        # update path's textfield
        self.path_txt_line.delete(0, MTk.END)
        self.path_txt_line.insert(0, subject.getPath())

        # update gallery's textfields
        self.gtitle_fld.delete(0, MTk.END)
        self.gtitle_fld.insert(0, subject.getGalleryTitle())

        self.gcomment_fld.delete(0.0, MTk.END)
        self.gcomment_fld.insert(0.0, subject.getGalleryComment())

        # update images's textfields and label
        imageInfo = subject.getImageInfo()
        self.logger.debug((imageInfo.toString()))
        self.img_lbl.configure(text=imageInfo.getLeft())
        self.ititle_fld.delete(0, MTk.END)
        self.ititle_fld.insert(0, imageInfo.getMidle())
        self.icomment_fld.delete(0.0, MTk.END)
        self.icomment_fld.insert(0.0, imageInfo.getRight())

        # update canvas
        ifile = Image.open(os.path.join(self.path, imageInfo.getLeft()))
        picture = ImageTk.PhotoImage(ifile)
        self.canvas.itemconfig(self.image_on_canvas, image=picture)
        self.update()

    def getImageTitle(self):
        return self.ititle_fld.get()

    def getImageComment(self):
        return self.icomment_fld.get(1.0, 1.65000)

class Controller():

    def __init__(self):
        super(Controller, self).__init__()

        self.logger = logging.getLogger('Controller')
        self.logger.setLevel(LOG_LEVEL)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(steam_handler)

        self.logger.info("New MGN instance")

        self.abstraction = Abstraction()
        self.presentation = Presentation(self)
        self.abstraction.attach(self.presentation)

    def mainloop(self):
        self.presentation.mainloop()

    def previous(self):
        self.logger.debug("Event: previous")
        self.abstraction.setImageInfo(self.presentation.getImageTitle(), self.presentation.getImageComment())
        self.abstraction.previous()

    def next(self):
        self.logger.debug("Event: next")
        self.abstraction.setImageInfo(self.presentation.getImageTitle(), self.presentation.getImageComment())
        self.abstraction.next()

    def clear(self):
        self.abstraction.clear()

    def setPath(self, path):
        self.logger.info("Gallery path: {0}".format(path))
        self.abstraction.setPath(path)

    def setGalleryInfo(self, gtitle, gcomment):
        self.abstraction.setGalleryInfo(gtitle, gcomment)

    def execute(self):
        self.logger.debug("File generation")
        self.abstraction.execute()

class Abstraction():

    def __init__(self):
        super(Abstraction, self).__init__()

        self.logger = logging.getLogger('Abstraction')
        self.logger.setLevel(LOG_LEVEL)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(steam_handler)

        self.observers = list()
        self.path = ""
        self.gtitle = ""
        self.gcomment = ""
        self.images = []
        self.index = 0

    def attach(self, observer):
        self.logger.debug("Attach observer")
        self.observers.append(observer)

    def detach(self, observer):
        self.logger.debug("Detach observer")
        self.observers.remove(observer)

    def updateObservers(self):
        self.logger.debug("Update observer")
        for observer in self.observers:
            observer.update(self)

    def clear(self):
        self.path = ""
        self.gtitle = ""
        self.gcomment = ""
        self.images = []
        self.index = 0

    ##
    # Set the path of the gallery and get or build the metadata.txt file
    #
    def setPath(self, path):
        self.path = path
        if self._checkMetadataFile():
            self._retrieveMetadataFromFile()
            self._updateImagesList()
        else:
            self._prepareNewMetadataFile()

        self.images.sort(key=lambda imageName: imageName.getLeft())

        self.updateObservers()

    ##
    # Internal usage
    #
    def _checkMetadataFile(self):
        return os.path.exists(os.path.join(self.path, 'metadata.txt'))

    ##
    # Internal usage
    #
    def _prepareNewMetadataFile(self):
        os.chdir(self.path)
        for file in glob.glob("*.jpg"):
            self._addImage(file)

    ##
    # Internal usage
    #
    def _addImage(self, file):
        image = Triple()
        image.setLeft(file).setMidle("Empty").setRight("Empty")
        self.images.append(image)

    ##
    # Internal usage
    #
    def _retrieveMetadataFromFile(self):
        try:
            metadataFile = open(os.path.join(self.path, 'metadata.txt'), encoding='ISO-8859-1')

            # parsing metadata.txt
            for line in metadataFile:
                # gallery metadatas
                if line.startswith("title|"):
                    match = re.search(r"title\|(.*)\@(.*)", line)
                    if match:
                        self.gtitle = match.group(1)
                        self.gcomment = match.group(2)
                else:
                    # image metadadas
                    match = re.search(r"(.*)\|(.*)::(.*)", line)
                    if match:
                        image = Triple()
                        image.setLeft(match.group(1)).setMidle(match.group(2)).setRight(match.group(3))
                        self.images.append(image)

        except IOError as e:
            self.logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
        finally:
            metadataFile.close()

    ##
    # Internal usage
    #
    # Add or remove image from metadata.txt depending the images contains in directory
    #
    def _updateImagesList(self):
        self.logger.debug("Check image files and update metadata.txt")
        imagesContainsInDirectory = []
        os.chdir(self.path)
        for file in glob.glob("*.jpg"):
            imagesContainsInDirectory.append(file)

        tmpimages = []

        # FIXME: find an efficient way to check the files

        self.logger.debug("First pass")
        for imagem in self.images:
            imageml = imagem.getLeft()
            tmpimages.append(imageml)

            if (imageml in imagesContainsInDirectory):
                self.logger.debug("{0}: nothing to do".format(imageml))
            else:
                self.logger.debug("{0}: remove the photo from metadata.txt".format(imageml))
                self.images.remove(imagem)

        self.logger.debug("Second pass")
        for imaged in imagesContainsInDirectory:
            if (imaged in tmpimages):
                self.logger.debug("{0}: nothing to do".format(imaged))
            else:
                self.logger.debug("{0}: add the photo in metadata.txt".format(imaged))
                self.addImage(imaged)

    def getPath(self):
        return self.path

    def setGalleryInfo(self, gtitle, gcomment):
        self.gtitle = gtitle
        self.gcomment = gcomment
        self.logger.info("Gallery\'s name: [{0}] - Gallery's comment: [{1}]".format(self.gtitle, self.gcomment))

    def getGalleryTitle(self):
        return self.gtitle

    def getGalleryComment(self):
        return self.gcomment

    def setImageInfo(self, ititle, icomment):
        self.images[self.index].setMidle(ititle).setRight(icomment)

    def getImageInfo(self):
        return self.images[self.index]

    def next(self):
        if (self.index < len(self.images)-1):
            self.index += 1
            self.updateObservers()
        else:
            Mb.showinfo("", "All images reads")

    def previous(self):
        if (self.index > 0):
            self.index -= 1
            self.updateObservers()
        else:
            Mb.showinfo("", "This is already the first image")

    def execute(self):
        sb = StringBuilder()
        sb.append("title|").append(self.gtitle).append("@").append(self.gcomment).append("\n")

        os.chdir(self.path)
        for image in self.images:
            sb.append(image.getLeft().__str__()).append("|").append(image.getMidle().__str__()).append("::")
            sb.append(image.getRight().__str__()).append("\n")

        print(sb.toString())
        try:
            outputFile = codecs.open(os.path.join(self.path, 'metadata.txt'), 'w', 'ISO-8859-1')
            outputFile.write(sb.toString())
        except IOError as e:
            self.logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
        finally:
            outputFile.close()


###########################
# Launch the main frame
###########################
if __name__ == '__main__':
    controller = Controller()
    controller.mainloop()