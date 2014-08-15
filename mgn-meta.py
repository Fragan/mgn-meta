#!/usr/bin/python3

import sys
print((sys.version))

if sys.version_info[0] < 3:
    print("This script requires Python version 3.x")
    sys.exit(1)

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
import codecs
import logging
from logging.handlers import RotatingFileHandler
import re
from threading import Timer
import json
import configparser

# In second
DEFAULT_TIME_TO_BACKUP = 300

LOG_LEVEL = logging.DEBUG
formatter = logging.Formatter('%(asctime)s - %(levelname)s -  %(name)s -> %(message)s')
file_handler = RotatingFileHandler('mgn-meta.log', 'a', 1048576, 1)
file_handler.setLevel(LOG_LEVEL)
file_handler.setFormatter(formatter)

steam_handler = logging.StreamHandler()
steam_handler.setLevel(LOG_LEVEL)

class Presentation():

    def __init__(self, main, controller, **kwargs):
        self.logger = logging.getLogger('Presentation')
        self.logger.setLevel(LOG_LEVEL)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(steam_handler)

        self.main = main
        self.controller = controller

        self.path = MTk.StringVar()

        self._init_view()
        self._bind_key()

    def _init_view(self):
        self.frame = MTk.Frame(self.main)
        self.frame.config(width=1280, height=720)
        self.frame.option_readfile('look-and-feel-options.ini')
        self.frame.pack()

        ##########
        self.browse_pnl = MTk.Frame(self.frame)
        self.browse_pnl.pack(anchor=MTk.N, expand=MTk.YES, fill=MTk.X)

        self.separator1 = MTk.Frame(self.frame, height=2, bd=1, relief=MTk.SUNKEN)
        self.separator1.pack(fill=MTk.X, padx=5, pady=5)

        self.edit_pnl = MTk.Frame(self.frame)
        self.edit_pnl.pack(anchor=MTk.S, expand=MTk.YES, fill=MTk.X)

        self.tools_pnl = MTk.Frame(self.edit_pnl)
        self.tools_pnl.pack(side=MTk.LEFT, fill=MTk.Y, padx=4)

        self.img_pnl = MTk.Frame(self.edit_pnl)
        self.img_pnl.pack(side=MTk.LEFT, fill=MTk.BOTH)

        ##########
        self.path_lbl = MTk.Label(self.browse_pnl, text="Gallery\'s path:", anchor=MTk.W)
        self.path_lbl.pack(anchor=MTk.NW, padx=4)

        self.path_txt_line = MTk.Entry(self.browse_pnl, textvariable=self.path)
        self.path_txt_line.pack(padx=4, side=MTk.LEFT, expand=MTk.YES, fill=MTk.X)

        self.browse_btn = MTk.Button(self.browse_pnl, text='Browse', command=self._browse)
        self.browse_btn.pack(padx=4, side=MTk.LEFT)

        ##########
        self.img_lbl = MTk.Label(self.img_pnl, text='none')
        self.img_lbl.pack(expand=MTk.YES)

        self.canvas = MTk.Canvas(self.img_pnl)
        self.canvas.config(width=917, height=588)

        ##
        self.sbar_v = MTk.Scrollbar(self.img_pnl, orient=MTk.VERTICAL)
        self.sbar_h = MTk.Scrollbar(self.img_pnl, orient=MTk.HORIZONTAL)

        self.sbar_v.config(command=self.canvas.yview)
        self.sbar_h.config(command=self.canvas.xview)

        self.canvas.config(yscrollcommand=self.sbar_v.set)
        self.canvas.config(xscrollcommand=self.sbar_h.set)

        self.sbar_v.pack(side=MTk.RIGHT, fill=MTk.Y)
        self.sbar_h.pack(side=MTk.BOTTOM, fill=MTk.X)

        self.canvas.pack(side=MTk.LEFT, expand=MTk.YES, fill=MTk.BOTH)

        self.ifile = Image.open('index.jpeg')
        self.picture = ImageTk.PhotoImage(self.ifile)
        self.image_on_canvas = self.canvas.create_image(0, 0, image=self.picture, anchor=MTk.NW)

        ##########
        self.gtitle_lbl = MTk.Label(self.tools_pnl, text="Gallery\'s title:", anchor=MTk.W)
        self.gtitle_lbl.pack(anchor=MTk.W)

        self.gtitle_fld = MTk.Entry(self.tools_pnl, width=40)
        self.gtitle_fld.pack(anchor=MTk.W)

        self.gcomment_lbl = MTk.Label(self.tools_pnl, text="Gallery\'s comment:", anchor=MTk.W)
        self.gcomment_lbl.pack(anchor=MTk.W)

        self.gcomment_fld = MTk.Text(self.tools_pnl, width=40, height=5)
        self.gcomment_fld.pack(anchor=MTk.W)

        self.gvalidate_btn = MTk.Button(self.tools_pnl, text='Validate', command=self._validate_gallery_info)
        self.gvalidate_btn.pack(anchor=MTk.E)

        ##
        self.separator2 = MTk.Frame(self.tools_pnl, height=2, bd=1, relief=MTk.SUNKEN)
        self.separator2.pack(fill=MTk.X, padx=5, pady=5)

        #####
        self.img_info_pnl = MTk.Frame(self.tools_pnl)
        self.img_info_pnl.pack(pady=4)

        ##
        self.ititle_lbl = MTk.Label(self.img_info_pnl, text="Image\'s title:", anchor=MTk.W)
        self.ititle_lbl.pack(anchor=MTk.W)

        self.ititle_fld = MTk.Entry(self.img_info_pnl, width=40)
        self.ititle_fld.pack(anchor=MTk.W)

        self.icomment_lbl = MTk.Label(self.img_info_pnl, text="Image\'s comment:", anchor=MTk.W)
        self.icomment_lbl.pack(anchor=MTk.W)

        self.icomment_fld = MTk.Text(self.img_info_pnl, width=40, height=5)
        self.icomment_fld.pack(anchor=MTk.W)

        ##
        self.img_btn_pnl = MTk.Frame(self.img_info_pnl)
        self.img_btn_pnl.pack(anchor=MTk.E)

        self.nxt_img_btn = MTk.Button(self.img_btn_pnl, text='Previous', command=self.controller.previous)
        self.nxt_img_btn.pack(side=MTk.LEFT)

        self.nxt_img_btn = MTk.Button(self.img_btn_pnl, text="Next", command=self.controller.next)
        self.nxt_img_btn.pack(side=MTk.LEFT)

        self.copy_img_btn = MTk.Button(self.img_btn_pnl, text='Copy', command=self._copy)
        self.copy_img_btn.pack(side=MTk.LEFT)

        self.paste_img_btn = MTk.Button(self.img_btn_pnl, text='Paste', command=self._paste)
        self.paste_img_btn.pack(side=MTk.LEFT)

        ##
        self.separator3 = MTk.Frame(self.tools_pnl, height=2, bd=1, relief=MTk.SUNKEN)
        self.separator3.pack(fill=MTk.X, padx=5, pady=5)

        self.generate_btn = MTk.Button(self.tools_pnl, text='Generate file', command=self._execute)
        self.generate_btn.pack(anchor=MTk.N)

    def _bind_key(self):
        self.frame.bind('<Control-Q>', self._quit)
        self.frame.bind('<Control-q>', self._quit)

        self.frame.bind('<Control-O>', self._browse)
        self.frame.bind('<Control-o>', self._browse)

        # Disable 'Enter' key in the Text widget
        self.gcomment_fld.bind("<Return>", lambda e: "break")
        self.icomment_fld.bind("<Return>", lambda e: "break")

    def _quit(self, event=MTk.NONE):
        print('--QUIT--')
        self.main.destroy()

    def _browse(self, event=MTk.NONE):
        self.path = Fd.askdirectory(title='Select a directory')

        # set the new path
        self.controller.clear()
        self.controller.set_path(self.path)

    def _validate_gallery_info(self):
        self.controller.set_gallery_info(self.gtitle_fld.get(), self.gcomment_fld.get(1.0, 1.65000))

    def _execute(self):
        self.controller.execute()
        Mb.showinfo('', 'Treatment completed')

    def _copy(self):
        self.controller.copy({ 'title': self.get_image_title(), 'description': self.get_image_comment() })

    def _paste(self):
        image_info = self.controller.paste()
        self.ititle_fld.delete(0, MTk.END)
        self.ititle_fld.insert(0, image_info['title'])
        self.icomment_fld.delete(0.0, MTk.END)
        self.icomment_fld.insert(0.0, image_info['description'])

    def update(self, subject):
        self.logger.debug('Update the presentation')

        # update path's textfield
        self.path_txt_line.delete(0, MTk.END)
        self.path_txt_line.insert(0, subject.get_path())

        # update gallery's textfields
        self.gtitle_fld.delete(0, MTk.END)
        self.gtitle_fld.insert(0, subject.get_gallery_title())

        self.gcomment_fld.delete(0.0, MTk.END)
        self.gcomment_fld.insert(0.0, subject.get_gallery_comment())

        # update images's textfields and label
        image_info = subject.get_image_info()
        self.logger.debug(image_info)
        self.img_lbl.configure(text=image_info['filename'])
        self.ititle_fld.delete(0, MTk.END)
        self.ititle_fld.insert(0, image_info['title'])
        self.icomment_fld.delete(0.0, MTk.END)
        self.icomment_fld.insert(0.0, image_info['description'])

        # update canvas
        self.ifile = Image.open(os.path.join(self.path, image_info['filename']))
        self.picture = ImageTk.PhotoImage(self.ifile)
        scale_w = 80
        scale_h = 80
        #self.picture.zoom(scale_w, scale_h)
        self.canvas.itemconfig(self.image_on_canvas, image=self.picture)

    def get_image_title(self):
        return self.ititle_fld.get()

    def get_image_comment(self):
        return self.icomment_fld.get(1.0, 1.65000)

class Controller():

    def __init__(self, main):
        super(Controller, self).__init__()

        self.logger = logging.getLogger('Controller')
        self.logger.setLevel(LOG_LEVEL)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(steam_handler)

        self.logger.info('New MGN instance')
        self.logger.info("Time between each backup: {0}s".format(DEFAULT_TIME_TO_BACKUP))

        self.abstraction = Abstraction()
        self.presentation = Presentation(main, self)
        self.abstraction.attach(self.presentation)

    def previous(self):
        self.logger.debug('Event: previous')
        self._check_is_validate()
        self.abstraction.set_image_info(self.presentation.get_image_title(), self.presentation.get_image_comment())
        self.abstraction.previous()

    def next(self):
        self.logger.debug('Event: next')
        self._check_is_validate()
        self.abstraction.set_image_info(self.presentation.get_image_title(), self.presentation.get_image_comment())
        self.abstraction.next()

    def clear(self):
        self.abstraction.clear()

    def set_path(self, path):
        self.logger.info("Gallery path: {0}".format(path))
        self.abstraction.set_path(path)

    def set_gallery_info(self, gtitle, gcomment):
        self.abstraction.set_gallery_info(gtitle, gcomment)
        self.set_validate(True)

    def copy(self, image_info):
        self.abstraction.set_buffer(image_info)

    def paste(self):
        return self.abstraction.get_buffer()

    def execute(self):
        self.logger.debug('File generation')
        self.abstraction.set_image_info(self.presentation.get_image_title(), self.presentation.get_image_comment())
        self.abstraction.execute()

    def _check_is_validate(self):
        validate = self.abstraction.is_validate()
        if ~validate:
            print('not validate')

class Abstraction():

    def __init__(self):
        super(Abstraction, self).__init__()

        self.logger = logging.getLogger('Abstraction')
        self.logger.setLevel(LOG_LEVEL)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(steam_handler)

        self.options = self._parse_options()
        self.observers = []
        self.path = ''
        self.metadata = {
            'title': '',
            'description': '',
            'images': []
        }

        self.buffer = { 'title': '', 'description': '' }

        self.index = 0
        self.backup_number = 1

        self.validate = True

        self._timed_backup()

    def _parse_options(self):
        opts = configparser.ConfigParser()
        opts.read('config.ini')
        return opts

    def get_options(self):
        return self.options

    def attach(self, observer):
        self.logger.debug('Attach observer')
        self.observers.append(observer)

    def detach(self, observer):
        self.logger.debug('Detach observer')
        self.observers.remove(observer)

    def update_observers(self):
        self.logger.debug('Update observer')
        for observer in self.observers:
            observer.update(self)

    def clear(self):
        self.path = ''
        self.metadata = {
            'title': '',
            'description': '',
            'images': []
        }
        self.index = 0

    ##
    # Set the path of the gallery and get or build the metadata.txt file
    #
    def set_path(self, path):
        self.path = path
        if self._check_metadata_file():
            self._retrieve_metadata_from_file()
            self._update_images_list()
        else:
            self._prepare_new_metadata_file()

        self.metadata['images'].sort(key=lambda image_name: image_name['filename'])

        self.update_observers()

    ##
    # Internal usage
    #
    def _check_metadata_file(self):
        return os.path.exists(os.path.join(self.path, 'metadata.txt'))

    ##
    # Internal usage
    #
    def _prepare_new_metadata_file(self):
        os.chdir(self.path)
        for file in glob.glob("*.jpg"):
            self._add_image(file)

    ##
    # Internal usage
    #
    def _add_image(self, file):
        self.metadata['images'].append({ 'filename': file, 'title': '', 'description': '' })

    ##
    # Internal usage
    #
    def _retrieve_metadata_from_file(self):
        # FIXME: json then txt then nothing
        self._retrieve_metadata_from_file_json()

    def _retrieve_metadata_from_file_json(self):
        with open(os.path.join(self.path, 'metadata.json'), encoding=self.options['abstraction']['encoding']) as metadata_file:
            self.metadata = json.load(metadata_file)

    def _retrieve_metadata_from_file_txt(self):
        try:
            metadata_file = open(os.path.join(self.path, 'metadata.txt'), encoding=self.options['abstraction']['encoding'])

            # parsing metadata.txt
            for line in metadata_file:
                # gallery metadata
                if line.startswith('title|'):
                    match = re.search(r"title\|(.*)\@(.*)", line)
                    if match:
                        self.metadata['title'] = match.group(1)
                        self.metadata['description'] = match.group(2)
                else:
                    # image metadada
                    match = re.search(r"(.*)\|(.*)::(.*)", line)
                    if match:
                        self.metadata['images'].append({ 'filename': match.group(1), 'title': match.group(2), 'description': match.group(3) })

        except IOError as e:
            self.logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
        finally:
            metadata_file.close()

    ##
    # Internal usage
    #
    # Add or remove image from metadata.txt depending the images contains in directory
    #
    def _update_images_list(self):
        self.logger.debug('Check image files and update metadata.txt')
        images_contains_in_directory = []
        os.chdir(self.path)
        for file in glob.glob("*.jpg"):
            images_contains_in_directory.append(file)

        tmp_images = []

        # FIXME: find an efficient way to check the files

        self.logger.debug('First pass')
        for imagem in self.metadata['images']:
            imageml = imagem['filename']
            tmp_images.append(imageml)

            if (imageml in images_contains_in_directory):
                self.logger.debug("{0}: nothing to do".format(imageml))
            else:
                self.logger.debug("{0}: remove the photo from metadata.txt".format(imageml))
                self.images.remove(imagem)

        self.logger.debug('Second pass')
        for imaged in images_contains_in_directory:
            if (imaged in tmp_images):
                self.logger.debug("{0}: nothing to do".format(imaged))
            else:
                self.logger.debug("{0}: add the photo in metadata.txt".format(imaged))
                self._add_image(imaged)

    def get_path(self):
        return self.path

    def set_gallery_info(self, gtitle, gcomment):
        self.metadata['title'] = gtitle
        self.metadata['description'] = gcomment
        self.logger.info("Gallery\'s name: [{0}] - Gallery's comment: [{1}]".format(gtitle, gcomment))

    def get_gallery_title(self):
        return self.metadata['title']

    def get_gallery_comment(self):
        return self.metadata['description']

    def set_image_info(self, ititle, icomment):
        image = self.metadata['images'][self.index]
        image['title'] = ititle
        image['description'] = icomment

    def get_image_info(self):
        return self.metadata['images'][self.index]

    def next(self):
        if (self.index < len(self.metadata['images'])-1):
            self.index += 1
            self.update_observers()
        else:
            Mb.showinfo('', 'All images reads')

    def previous(self):
        if (self.index > 0):
            self.index -= 1
            self.update_observers()
        else:
            Mb.showinfo('', 'This is already the first image')

    def execute(self, file=''):
        method = 'execute_' + self.options['abstraction']['output_format']
        if not file:
            getattr(self, method)()
        else:
            getattr(self, method)(file)

    def execute_json(self, file='metadata.json'):
        print(json.dumps(self.metadata, indent=2, ensure_ascii=False))
        self._write(file, json.dumps(self.metadata, indent=2, ensure_ascii=False))

    def execute_txt(self, file='metadata.txt'):
        sb = StringBuilder()
        sb.append('title|').append(self.metadata['title']).append('@').append(self.metadata['description']).append("\n")

        os.chdir(self.path)
        for image in self.metadata['images']:
            sb.append(image['filename'].__str__()).append('|').append(image['title'].__str__()).append('::')
            sb.append(image['description'].__str__()).append("\n")

        print(sb.to_s())
        self._write(file, sb.to_s())

    def _write(self, file, data):
        try:
            output_file = codecs.open(os.path.join(self.path, file), 'w', self.options['abstraction']['encoding'])
            output_file.write(data)
        except IOError as e:
            self.logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
        finally:
            output_file.close()

    ##
    #
    # This is a routine to backup current edition of metadata.txt
    #
    def _timed_backup(self):
        timer = Timer(DEFAULT_TIME_TO_BACKUP, self._timed_backup)
        timer.setDaemon(True)
        timer.start()
        if (self.metadata['title'] != ""):
            backup = 'backup_'+self.backup_number.__str__()+'.txt'
            self.logger.info('Perform backup: '+backup)
            self.execute(backup)
            self.backup_number += 1

    def is_validate(self):
        return self.validate

    def set_validate(self, boolean):
        self.validate = boolean

    def set_buffer(self, image_info):
        self.logger.info('Define buffer: '+image_info.__str__())
        self.buffer = image_info

    def get_buffer(self):
        self.logger.info('Buffer:'+self.buffer.__str__())
        return self.buffer

###########################
# Launch the main frame
###########################
if __name__ == '__main__':
    root = MTk.Tk()
    root.wm_title("MiniGal Nano++ metadata generator")
    controller = Controller(root)
    root.mainloop()
