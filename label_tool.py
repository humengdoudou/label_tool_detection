#
# This is the python code for object bounding box label tool
#
# I use the BBox-Label-Tool by labelling image as the following format in txt:
#
# 4
# coat 43 93 254 375
# pants 58 365 216 665
# shoes 26 663 90 717
# shoes 176 665 236 719
#
# the first line number 4 is the total object num in one image,
# the rest 4 lines represents each bbox coordinate as (class, top_x, top_y, button_x, button_y)
#
# the original version BBox-Label-Tool from github is not very convenient to use for the following reasons:
# 1. the bounding box list does not show the class label of each bbox;
# 2. the class label can even be empty for each bbox, and can be saved in .txt file without reporting error;
# 3. once click prev/next button, the labelled image need to be label again for the default class label residual
#    by the last image
# 4. lack of a button to reset the class label, which causes the default class will always been assigned to the image;
#
# I fixed the above 4 shortage and make it easier to label the bbox;
#
# IMPORTANT: before labelling an object, set the class tag like "coat", "pants" first,
#            afterwards label the object coordinates
#
# reference:
# 1 https://github.com/puzzledqs/BBox-Label-Tool
#
# Author: hzhumeng01 2018-01-23


from __future__ import division
from Tkinter import *
import tkMessageBox
from PIL import Image, ImageTk
import os
import glob
import random

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

# colors for the bboxes
COLORS = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green', 'black']

# image sizes for the examples, but never use
SIZE = 256, 256

# detection class label list
# classLabels = ['mat', 'door', 'sofa', 'chair', 'table', 'bed', 'ashcan', 'shoe']
classLabels = ['coat', 'pants', 'glasses', 'hat', 'shoes', 'bag']

class LabelTool():
    def __init__(self, master):

        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width=False, height=False)

        # initialize global state
        self.imageDir = ''
        self.imageList = []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None
        self.currentClass = ''

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text="Image Dir:")
        self.label.grid(row=0, column=0, sticky=E)
        self.entry = Entry(self.frame)
        self.entry.grid(row=0, column=1, sticky=W + E)
        self.ldBtn = Button(self.frame, text="Load", command=self.loadDir)
        self.ldBtn.grid(row=0, column=2, sticky=W + E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind("s", self.cancelBBox)
        self.parent.bind("a", self.prevImage)  # press 'a' to go backforward
        self.parent.bind("d", self.nextImage)  # press 'd' to go forward
        self.mainPanel.grid(row=1, column=1, rowspan=4, sticky=W + N)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text='Bounding boxes:')
        self.lb1.grid(row=1, column=2, sticky=W + N)
        self.listbox = Listbox(self.frame, width=22, height=8)
        self.listbox.grid(row=2, column=2, sticky=N)
        self.btnDel = Button(self.frame, text='Delete', command=self.delBBox)
        self.btnDel.grid(row=3, column=2, sticky=W + E + N)
        self.btnClear = Button(self.frame, text='ClearAll', command=self.clearBBox)
        self.btnClear.grid(row=4, column=2, sticky=W + E + N)

        # select class type
        self.classPanel = Frame(self.frame)
        self.classPanel.grid(row=5, column=1, columnspan=10, sticky=W + E)

        label_class = Label(self.classPanel, text='class:')
        label_class.grid(row=5, column=1, sticky=W + N)
        self.classbox = Listbox(self.classPanel, width=4, height=2)
        self.classbox.grid(row=5, column=2)

        for each in range(len(classLabels)):
            function = 'select' + classLabels[each]
            # print classLabels[each]
            btnMat = Button(self.classPanel, text=classLabels[each], command=getattr(self, function))
            btnMat.grid(row=5, column=each + 3)

        label_imgname = Label(self.classPanel, text='img_name:')
        label_imgname.grid(row=5, column=3 + len(classLabels), sticky=W + N)
        self.imgnamebox = Listbox(self.classPanel, width=20, height=2)
        self.imgnamebox.grid(row=5, column=4 + len(classLabels))

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row=6, column=1, columnspan=2, sticky=W + E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width=10, command=self.prevImage)
        self.prevBtn.pack(side=LEFT, padx=5, pady=3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width=10, command=self.nextImage)
        self.nextBtn.pack(side=LEFT, padx=5, pady=3)
        self.progLabel = Label(self.ctrPanel, text="Progress:     /    ")
        self.progLabel.pack(side=LEFT, padx=5)
        self.tmpLabel = Label(self.ctrPanel, text="Go to Image Name: ")
        self.tmpLabel.pack(side=LEFT, padx=5)
        self.idxEntry = Entry(self.ctrPanel, width=5)
        self.idxEntry.pack(side=LEFT)
        self.goBtn = Button(self.ctrPanel, text='Go', command=self.gotoImage)
        self.goBtn.pack(side=LEFT)

        # clear label, add by hzhumeng01
        self.btnClearLabel = Button(self.ctrPanel, text='ClearLabel', width=7, command=self.clearLabel)
        self.btnClearLabel.pack(side=LEFT)

        # example pannel for illustration
        self.egPanel = Frame(self.frame, border=10)
        self.egPanel.grid(row=1, column=0, rowspan=5, sticky=N)
        self.tmpLabel2 = Label(self.egPanel, text="Examples:")
        self.tmpLabel2.pack(side=TOP, pady=5)
        self.egLabels = []
        for i in range(3):
            self.egLabels.append(Label(self.egPanel))
            self.egLabels[-1].pack(side=TOP)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side=RIGHT)

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(10, weight=1)


    def loadDir(self, dbg=False):
        if not dbg:
            s = self.entry.get()
            self.parent.focus()
            self.category = int(s)
        else:
            s = r'D:\workspace\python\labelGUI'

        # get image list
        self.imageDir = os.path.join(r'./JPEGImages', '%d' % (self.category))
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.jpg'))    # with the specified exts
        if len(self.imageList) == 0:
            print 'No .JPEG images found in the specified dir!'
            return

        # set up output dir
        self.outDir = os.path.join(r'./Labels', '%d' % (self.category))
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        labeledPicList = glob.glob(os.path.join(self.outDir, '*.txt'))

        for label in labeledPicList:
            data = open(label, 'r')
            if '0\n' == data.read():
                data.close()
                continue
            data.close()
            picture = label.replace('Labels', 'Images').replace('.txt', '.jpg')
            if picture in self.imageList:
                self.imageList.remove(picture)

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)
        self.loadImage()
        print '%d images loaded from %s' % (self.total, s)

    def loadImage(self):

        # load image
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)
        self.imgSize = self.img.size
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width=max(self.tkimg.width(), 100), height=max(self.tkimg.height(), 100))   # for the gui size
        self.mainPanel.create_image(0, 0, image=self.tkimg, anchor=NW)
        self.progLabel.config(text="%04d/%04d" % (self.cur, self.total))

        # load labels
        self.clearBBox()
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        bbox_cnt = 0

        # show name
        self.imgnamebox.delete(0, END)
        self.imgnamebox.insert(0, self.imagename)

        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
                        bbox_cnt = int(line.strip())
                        continue

                    bboxList_single = [t.strip() for t in line.split()]
                    tmp_rectangle = []
                    for item in bboxList_single[1:]: # the first element in bboxList_single is the class label string
                        tmp_rectangle.append(int(item))

                    ## print tmp
                    self.bboxList.append(tuple(bboxList_single))
                    tmpId = self.mainPanel.create_rectangle(tmp_rectangle[0], tmp_rectangle[1], \
                                                            tmp_rectangle[2], tmp_rectangle[3], \
                                                            width=2, \
                                                            outline=COLORS[(len(self.bboxList) - 1) % len(COLORS)])

                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, '%s (%d, %d) -> (%d, %d)' % (str(bboxList_single[0]), tmp_rectangle[0], tmp_rectangle[1], tmp_rectangle[2], tmp_rectangle[3]))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])

    def saveImage(self):

        # if os.path.exists(self.labelfilename) and len(self.bboxList) == 0:
        if len(self.bboxList) == 0:
            print 'No callibrations in exist file %s, and no need to save empty callibrations' % (self.labelfilename)
            return None

        for bbox in self.bboxList:
            if isinstance(bbox[0], int):  # the first element in bbox should be a class label string, but not a digit
                print "you need to set a class label to the bbox"
                return None

        with open(self.labelfilename, 'w') as f:
            f.write('%d\n' % len(self.bboxList))
            for bbox in self.bboxList:
                f.write(' '.join(map(str, bbox)) + '\n')    # bboxList already include classname string

        print 'Image No. %d saved' % (self.cur)

    def mouseClick(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
            # self.STATE['x'], self.STATE['y'] = self.imgSize[0], self.imgSize[1]
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            if x2 > self.imgSize[0]:
                x2 = self.imgSize[0]
            if y2 > self.imgSize[1]:
                y2 = self.imgSize[1]
            self.bboxList.append((self.currentClass, x1, y1, x2, y2))  # bboxList already include classname string
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, '%s (%d, %d) -> (%d, %d)' % (str(self.currentClass), x1, y1, x2, y2))  # for showing the claa label
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
        self.STATE['click'] = 1 - self.STATE['click']

    def mouseMove(self, event):
        self.disp.config(text='x: %d, y: %d' % (event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width=2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width=2)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                          event.x, event.y, \
                                                          width=2, \
                                                          outline=COLORS[len(self.bboxList) % len(COLORS)])

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []
        self.currentClass = ''
        self.classbox.delete(0, END)

    # add for clear the label
    def clearLabel(self):
        self.currentClass = ''
        self.classbox.delete(0, END)

    def selectcoat(self):
        self.currentClass = 'coat'
        self.classbox.delete(0, END)
        self.classbox.insert(0, 'coat')
        self.classbox.itemconfig(0, fg=COLORS[0])

    def selectpants(self):
        self.currentClass = 'pants'
        self.classbox.delete(0, END)
        self.classbox.insert(0, 'pants')
        self.classbox.itemconfig(0, fg=COLORS[0])

    def selectglasses(self):
        self.currentClass = 'glasses'
        self.classbox.delete(0, END)
        self.classbox.insert(0, 'glasses')
        self.classbox.itemconfig(0, fg=COLORS[0])

    def selecthat(self):
        self.currentClass = 'hat'
        self.classbox.delete(0, END)
        self.classbox.insert(0, 'hat')
        self.classbox.itemconfig(0, fg=COLORS[0])

    def selectshoes(self):
        self.currentClass = 'shoes'
        self.classbox.delete(0, END)
        self.classbox.insert(0, 'shoes')
        self.classbox.itemconfig(0, fg=COLORS[0])

    def selectbag(self):
        self.currentClass = 'bag'
        self.classbox.delete(0, END)
        self.classbox.insert(0, 'bag')
        self.classbox.itemconfig(0, fg=COLORS[0])

    def prevImage(self, event=None):
        self.saveImage()
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event=None):
        self.saveImage()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    def gotoImage(self):

        # by imgname
        index = -1
        imgname_search = str(self.idxEntry.get())
        for (i, imgpath) in enumerate(self.imageList):
            imagename = os.path.split(imgpath)[-1].split('.')[0]
            if imgname_search in imagename:
                index = i + 1
                break

        if 1 <= index and index <= self.total:
            self.saveImage()
            self.cur = index
            self.loadImage()

if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    #root.geometry('800x500+0+0')
    root.mainloop()
