#!/usr/bin/python3

import sys
from cgitb import text
from distutils.cmd import Command
from symbol import try_stmt
from test import list_tests
from tkinter import Canvas
from cgi import log
print((sys.version))

if sys.version_info[0] < 3:
    print("This script requires Python version 3.x")
    sys.exit(1)

import glob
import os
import tkinter as MTk
import tkinter.filedialog as Fd
import tkinter.messagebox as Mb
from StringBuilder import StringBuilder
from Triple import Triple
import codecs
from PIL import Image, ImageTk
import logging
from logging.handlers import RotatingFileHandler
import re

LOG_LEVEL = logging.DEBUG
formatter = logging.Formatter('%(asctime)s - %(levelname)s -  %(name)s :: %(message)s')
file_handler = RotatingFileHandler('mgn-meta.log', 'a', 10485760, 1)
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
        MTk.Frame.__init__(self, self.frame, width=768, height=576, **kwargs)
        self.path = MTk.StringVar()

        self.initView()

    def initView(self):
        self.frame.wm_title("MiniGal Nano++ metadata generator")
        self.pack()

        ##########
        self.browse_pnl = MTk.Frame(self)
        self.browse_pnl.pack(anchor="n")

        self.edit_pnl = MTk.Frame(self)
        self.edit_pnl.pack(anchor="s")

        self.tools_pnl = MTk.Frame(self.edit_pnl)
        self.tools_pnl.grid(row=0, column=0)

        self.img_pnl = MTk.Frame(self.edit_pnl)
        self.img_pnl.grid(row=0, column=1)

        ##########
        self.path_lbl = MTk.Label(self.browse_pnl, text="Gallery\'s path:", anchor="w", fg="black")
        self.path_lbl.grid(row=0, column=0, columnspan=2, padx=4, sticky='EW')

        self.path_txt_line = MTk.Entry(self.browse_pnl, textvariable=self.path, width=90)
        self.path_txt_line.grid(column=0, row=1, sticky='EW')

        self.browse_btn = MTk.Button(self.browse_pnl, text="Browse", command=self.browse)
        self.browse_btn.grid(row=1, column=1, sticky='EW')

        ##########
        self.img_lbl = MTk.Label(self.img_pnl, text="none")
        self.img_lbl.pack()

        self.canvas = MTk.Canvas(self.img_pnl, bg="grey")
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
        self.gtitle_lbl = MTk.Label(self.tools_pnl, text="Gallery\'s title:", anchor="w", fg="black")
        self.gtitle_lbl.pack()

        self.gtitle_fld = MTk.Entry(self.tools_pnl, width=40)
        self.gtitle_fld.pack()

        self.gcomment_lbl = MTk.Label(self.tools_pnl, text="Gallery\'s comment:", anchor="w", fg="black")
        self.gcomment_lbl.pack()

        self.gcomment_fld = MTk.Entry(self.tools_pnl, width=40)
        self.gcomment_fld.pack()

        self.gvalidate_btn = MTk.Button(self.tools_pnl, text="Validate", command=self.validateGalleryInfo)
        self.gvalidate_btn.pack()

        #####
        self.img_info_pnl = MTk.Frame(self.tools_pnl)
        self.img_info_pnl.pack(pady=10)

        ##
        self.ititle_lbl = MTk.Label(self.img_info_pnl, text="Image\'s title:", anchor="w", fg="black")
        self.ititle_lbl.pack()

        self.ititle_fld = MTk.Entry(self.img_info_pnl, width=40)
        self.ititle_fld.pack()

        self.icomment_lbl = MTk.Label(self.img_info_pnl, text="Image\'s comment:", anchor="w", fg="black")
        self.icomment_lbl.pack()

        self.icomment_fld = MTk.Entry(self.img_info_pnl, width=40)
        self.icomment_fld.pack()

        ##
        self.img_btn_pnl = MTk.Frame(self.img_info_pnl)
        self.img_btn_pnl.pack()

        self.nxt_img_btn = MTk.Button(self.img_btn_pnl, text="Previous", command=self.controller.previous)
        self.nxt_img_btn.grid(row=0, column=0, sticky='EW')

        self.nxt_img_btn = MTk.Button(self.img_btn_pnl, text="Next", command=self.controller.next)
        self.nxt_img_btn.grid(row=0, column=1, sticky='EW')

        ##
        self.generate_btn = MTk.Button(self.tools_pnl, text="Generate file", command=self.execute)
        self.generate_btn.pack(anchor="n")


    def mainloop(self):
        self.frame.mainloop()
        self.frame.destroy()

    def browse(self):
        self.path = Fd.askdirectory(title="Select a directory")

        # set the new path
        self.controller.clear()
        self.controller.setPath(self.path)

    def validateGalleryInfo(self):
        self.controller.setGalleryInfo(self.gtitle_fld.get(), self.gcomment_fld.get())

    def execute(self):
        self.controller.execute()
        Mb.showinfo("", "Treatment completed")

    def update(self, subject):
        self.logger.debug("Update the presentation")

        # update path's textfield
        self.path_txt_line.delete(0, 65000)
        self.path_txt_line.insert(0, subject.getPath())

        # update gallery's textfields
        self.gtitle_fld.delete(0, 65000)
        self.gtitle_fld.insert(0, subject.getGalleryTitle())

        self.gcomment_fld.delete(0, 65000)
        self.gcomment_fld.insert(0, subject.getGalleryComment())

        # update images's textfields and label
        imageInfo = subject.getImageInfo()
        self.logger.debug((imageInfo.toString()))
        self.img_lbl.configure(text=imageInfo.getLeft())
        self.ititle_fld.delete(0, 65000)
        self.ititle_fld.insert(0, imageInfo.getMidle())
        self.icomment_fld.delete(0, 65000)
        self.icomment_fld.insert(0, imageInfo.getRight())

        # update canvas
        ifile = Image.open(os.path.join(self.path, imageInfo.getLeft()))
        picture = ImageTk.PhotoImage(ifile)
        self.canvas.delete(MTk.ALL)
        self.canvas.create_image(0, 0, image=picture, anchor = MTk.NW)
        self.canvas.mainloop()

    def getImageTitle(self):
        return self.ititle_fld.get()

    def getImageComment(self):
        return self.icomment_fld.get()

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
        if self.checkMetadataFile():
            self.retrieveMetadataFromFile()
            self.updateImagesList()
        else:
            self.prepareNewMetadataFile()

        self.images.sort(key=lambda imageName: imageName.getLeft())

        self.updateObservers()

    ##
    # Internal usage
    #
    def checkMetadataFile(self):
        return os.path.exists(os.path.join(self.path, 'metadata.txt'))

    ##
    # Internal usage
    #
    def prepareNewMetadataFile(self):
        os.chdir(self.path)
        for file in glob.glob("*.jpg"):
            self.addImage(file)

    ##
    # Internal usage
    #
    def addImage(self, file):
        image = Triple()
        image.setLeft(file).setMidle("Empty").setRight("Empty")
        self.images.append(image)

    ##
    # Internal usage
    #
    def retrieveMetadataFromFile(self):
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
    def updateImagesList(self):
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
        if (self.index >= 0):
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