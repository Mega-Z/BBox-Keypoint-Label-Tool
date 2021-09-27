# -*- coding:utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        Object bounding box and keypoints label tool
# Purpose:     Label object bboxes and keypoints
# Author:      MegaZ
# Created:     09/19/2021

#
# -------------------------------------------------------------------------------
from __future__ import division
from tkinter import *
# import tkMessageBox
from PIL import Image, ImageTk
import os
import glob
import random

w0 = 1  # 图片原始宽度
h0 = 1  # 图片原始高度

# colors for the bboxes
point_colors = ['white', 'red', 'blue', 'green', 'yellow', 'magenta', 'cyan']
# image sizes for the examples
SIZE = 256, 256

# 指定缩放后的图像大小
DEST_SIZE = 500, 500

# total keypoint num
keypoint_num = 4
# output_dir
output_dir = r'./output'


class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width=TRUE, height=TRUE)

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
        self.STATE['point'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.pointID = None
        self.pointList = []
        self.hl = None
        self.vl = None
        self.selectidx = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text="Image Dir:")
        self.label.grid(row=0, column=0, sticky=E)
        self.entry = Entry(self.frame)
        self.entry.grid(row=0, column=1, sticky=W+E)
        self.ldBtn = Button(self.frame, text="Load", command=self.loadDir)
        self.ldBtn.grid(row=0, column=7, sticky=W+E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, width=DEST_SIZE[0], height=DEST_SIZE[1], cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        # press <Espace> to cancel current bbox
        self.parent.bind("<Escape>", self.cancelBBox)
        self.parent.bind("<Button-3>", self.nextPoint)
        self.parent.bind("s", self.cancelBBox)
        self.parent.bind("a", self.prevImage)  # press 'a' to go backforward
        self.parent.bind("d", self.nextImage)  # press 'd' to go forward
        self.mainPanel.grid(row=1, column=1, rowspan=6, columnspan=7, sticky=W+N)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text='Bounding boxes:')
        self.lb1.grid(row=0, column=8,  sticky=W+N)

        self.listbox = Listbox(self.frame, width=60, height=12)
        self.listbox.grid(row=1, column=8, rowspan=2, sticky=N+S)
        self.listbox.bind("<<ListboxSelect>>", self.listboxSelect)

        self.btnDel = Button(self.frame, text='DeleteBBox', command=self.delBBox)
        self.btnDel.grid(row=3, column=8, sticky=W+E+S)

        self.btnDel = Button(self.frame, text='AddBBox', command=self.addBBox)
        self.btnDel.grid(row=4, column=8, sticky=W+E+S)

        self.btnDel = Button(self.frame, text='DeleteKeypoint', command=self.clearKPnt)
        self.btnDel.grid(row=5, column=8, sticky=W+E+S)

        self.btnClear = Button(
            self.frame, text='ClearAll', command=self.clearBBox)
        self.btnClear.grid(row=6, column=8, sticky=W+E+S)

        # display mouse position
        self.disp = Label(self.frame, text='x: 0.00, y: 0.00')
        self.disp.grid(row=7, column=8, sticky=E+S)


        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row=7, column=1, columnspan=2, sticky=W+N)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev',
                              width=10, command=self.prevImage)
        self.prevBtn.pack(side=LEFT, padx=5, pady=3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>',
                              width=10, command=self.nextImage)
        self.nextBtn.pack(side=LEFT, padx=5, pady=3)
        self.progLabel = Label(self.ctrPanel, text="Progress:     /    ")
        self.progLabel.pack(side=LEFT, padx=5)
        self.tmpLabel = Label(self.ctrPanel, text="Go to Image No.")
        self.tmpLabel.pack(side=LEFT, padx=5)
        self.idxEntry = Entry(self.ctrPanel, width=5)
        self.idxEntry.pack(side=LEFT)
        self.goBtn = Button(self.ctrPanel, text='Go', command=self.gotoImage)
        self.goBtn.pack(side=LEFT)
        '''
        # example pannel for illustration
        self.egPanel = Frame(self.frame, border=10)
        self.egPanel.grid(row=1, column=0, rowspan=5, sticky=N)
        self.tmpLabel2 = Label(self.egPanel, text="Examples:")
        self.tmpLabel2.pack(side=TOP, pady=5)

        self.egLabels = []
        for i in range(3):
            self.egLabels.append(Label(self.egPanel))
            self.egLabels[-1].pack(side=TOP)'''


        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # for debugging
# self.setImage()
# self.loadDir()

    def loadDir(self):
        s = self.entry.get()
        self.parent.focus()

        # print('self.category =%d' % (self.category))

        self.imageDir = s
        # self.imageDir = os.path.join(r'./images', '%03d' % (self.category))
        print(self.imageDir)
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.jpg'))
        if len(self.imageList) == 0:
            print('No .jpg images found in the specified dir!')
            return
        else:
            print('num=%d' % (len(self.imageList)))

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

        # set up output dir
        self.outDir = output_dir
        # self.outDir = os.path.join(r'./labels', '%03d' % (self.category))
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        # load example bboxes
        self.egDir = r'F:\Z\code\BBox-Label-Tool-master\Examples\001'
        # self.egDir = os.path.join(r'./Examples', '%03d' % (self.category))
        # if not os.path.exists(self.egDir):
        #   return

        filelist = glob.glob(os.path.join(self.egDir, '*.jpg'))
        self.tmp = []
        self.egList = []
        random.shuffle(filelist)
        for (i, f) in enumerate(filelist):
            if i == 3:
                break
            im = Image.open(f)
            r = min(SIZE[0] / im.size[0], SIZE[1] / im.size[1])
            new_size = int(r * im.size[0]), int(r * im.size[1])
            self.tmp.append(im.resize(new_size, Image.ANTIALIAS))
            self.egList.append(ImageTk.PhotoImage(self.tmp[-1]))
            self.egLabels[i].config(
                image=self.egList[-1], width=SIZE[0], height=SIZE[1])

        self.loadImage()
        print('%d images loaded from %s' % (self.total, s))

    def loadImage(self):
        self.selectidx = None
        self.STATE['point'] = 0
        # load image
        imagepath = self.imageList[self.cur - 1]
        pil_image = Image.open(imagepath)

        # get the size of the image
        # 获取图像的原始大小
        global w0, h0
        w0, h0 = pil_image.size

        # 缩放到指定大小
        pil_image = pil_image.resize(
            (DEST_SIZE[0], DEST_SIZE[1]), Image.ANTIALIAS)

        #pil_image = imgresize(w, h, w_box, h_box, pil_image)
        self.img = pil_image

        self.tkimg = ImageTk.PhotoImage(pil_image)

        self.mainPanel.config(width=max(self.tkimg.width(), 500),
                              height=max(self.tkimg.height(), 500))
        self.mainPanel.create_image(0, 0, image=self.tkimg, anchor=NW)
        self.progLabel.config(text="%04d/%04d" % (self.cur, self.total))

        # load labels
        self.clearBBox()
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    bbox = [int(t.strip()) for t in line.split()]

                    # print("********************")
                    # print DEST_SIZE
                    #tmp = (0.1, 0.3, 0.5, 0.5)
                    # print("tmp[0,1,2,3]===%.2f, %.2f, %.2f, %.2f" % (
                        # float(tmp[0]), float(tmp[1]), float(tmp[2]), float(tmp[3])))
                    # print "%.2f,%.2f,%.2f,%.2f" %(tmp[0] tmp[1] tmp[2] tmp[3] )
                    # print("********************")

                    #tx = (10, 20, 30, 40)
                    # self.bboxList.append(tuple(tx))
                    self.bboxList.append(bbox)
                    tmp = bbox.copy()
                    for j, c in enumerate(tmp):
                        if j % 2 == 0:
                            tmp[j] = float(tmp[j])/w0
                        else:
                            tmp[j] = float(tmp[j])/h0

                    tx0 = int(tmp[0]*DEST_SIZE[0])
                    ty0 = int(tmp[1]*DEST_SIZE[1])
                    tx1 = int(tmp[2]*DEST_SIZE[0])
                    ty1 = int(tmp[3]*DEST_SIZE[1])
                    # print("tx0, ty0, tx1, ty1")
                    # print(tx0, ty0, tx1, ty1)
                    IdList = []
                    bboxId = self.mainPanel.create_rectangle(tx0, ty0, tx1, ty1,
                                                            width=2,
                                                            outline='violet')
                    IdList.append(bboxId)
                    string = '(%.2f,%.2f)-(%.2f,%.2f)' % (tmp[0], tmp[1], tmp[2], tmp[3])
                    point_num = (len(tmp)-4) // 2
                    for j in range(point_num):
                        if tmp[4+j*2] < 0:
                            IdList.append(None)
                            string += ' (%.2f,%.2f)' % (-1, -1)
                            continue
                        txi = int(tmp[4+j*2]*DEST_SIZE[0])
                        tyi = int(tmp[4+j*2+1]*DEST_SIZE[1])
                        point = self.mainPanel.create_oval(txi-3, tyi-3, txi+3, tyi+3, width=2, fill='black',
                                               outline=point_colors[(j+1) % (len(point_colors))])
                        IdList.append(point)
                        string += ' (%.2f,%.2f)' % (txi/DEST_SIZE[0], tyi/DEST_SIZE[1])
                    self.bboxIdList.append(IdList)
                    self.listbox.insert(END, string)
                    self.listbox.itemconfig(
                        len(self.bboxIdList) - 1, fg='black')

    def saveImage(self):
        # print "-----1--self.bboxList---------"
        print(self.bboxList)
        # print "-----2--self.bboxList---------"

        with open(self.labelfilename, 'w') as f:
            # f.write('%d\n' % len(self.bboxList))
            for bbox in self.bboxList:
                while len(bbox) < 4+keypoint_num*2:
                    bbox.append(-1)
                f.write(' '.join(map(str, bbox)) + '\n')
        print('Image No. %d saved' % (self.cur))

    def mouseClick(self, event):
        if self.STATE['point'] == 0:
            if self.STATE['click'] == 0:
                self.STATE['x'], self.STATE['y'] = event.x, event.y
            else:
                x1, x2 = min(self.STATE['x'], event.x), max(
                    self.STATE['x'], event.x)
                y1, y2 = min(self.STATE['y'], event.y), max(
                    self.STATE['y'], event.y)

                x1, x2 = int(x1 / DEST_SIZE[0] * w0), int(x2 / DEST_SIZE[0] * w0)
                y1, y2 = int(y1 / DEST_SIZE[1] * h0), int(y2 / DEST_SIZE[1] * h0)

                self.bboxList.append([x1, y1, x2, y2])
                self.bboxIdList.append([self.bboxId])
                self.bboxId = None
                self.listbox.insert(
                    END, '(%.2f,%.2f)-(%.2f,%.2f)' % (x1/w0, y1/h0, x2/w0, y2/h0))
                self.listbox.itemconfig(
                    len(self.bboxIdList) - 1, fg='black')
            self.STATE['click'] = 1 - self.STATE['click']
        else:
            sel = self.listbox.curselection()
            if len(sel) != 1:
                return
            xi, yi = event.x, event.y
            point = self.mainPanel.create_oval(xi-3, yi-3, xi+3, yi+3, width=2, fill='black',
                                               outline=point_colors[self.STATE['point'] % (len(point_colors))])

            idx = int(sel[0])
            string = self.listbox.get(idx)
            if self.STATE['point'] == 1 and len(self.bboxIdList[idx]) >= keypoint_num+1:
                self.clearKPnt()
                string = string[:23]
                self.bboxList[idx] = self.bboxList[idx][:4]
            string += ' (%.2f,%.2f)' % (xi/DEST_SIZE[0], yi/DEST_SIZE[1])
            self.bboxList[idx].append(int(xi/DEST_SIZE[0]*w0))
            self.bboxList[idx].append(int(yi/DEST_SIZE[1]*h0))
            self.bboxIdList[idx].append(point)
            self.listbox.delete(idx)
            self.listbox.insert(idx, string)
            self.listbox.select_set(idx)
            if self.STATE['point'] >= keypoint_num:
                self.STATE['point'] = 0
            else:
                self.STATE['point'] += 1


    def mouseMove(self, event):
        self.disp.config(text='x: %.2f, y: %.2f' %
                         (event.x/DEST_SIZE[0], event.y/DEST_SIZE[1]))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(
                0, event.y, self.tkimg.width(), event.y, width=2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(
                event.x, 0, event.x, self.tkimg.height(), width=2)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'],
                                                          event.x, event.y,
                                                          width=2,
                                                          outline='violet')
        elif self.STATE['point'] != 0:
            if self.pointID:
                self.mainPanel.delete(self.pointID)
            self.pointID = self.mainPanel.create_oval(event.x-5, event.y-5, event.x+5, event.y+5, width=2, fill='black',
                                               outline=point_colors[self.STATE['point'] % (len(point_colors))])
        sel = self.listbox.curselection()
        if len(sel) == 1 and self.STATE['click'] == 0:
            idx = int(sel[0])
            self.STATE['point'] = (len(self.bboxIdList[idx])-1) % keypoint_num + 1


    def listboxSelect(self, event):
        sel = self.listbox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        if self.selectidx is not None:
            self.mainPanel.delete(self.bboxIdList[self.selectidx][0])
            bbox = self.bboxList[self.selectidx]
            x0 = int(bbox[0] * DEST_SIZE[0]/w0)
            y0 = int(bbox[1] * DEST_SIZE[1]/h0)
            x1 = int(bbox[2] * DEST_SIZE[0]/w0)
            y1 = int(bbox[3] * DEST_SIZE[1]/h0)
            rect = self.mainPanel.create_rectangle(x0, y0, x1, y1, width=2,
                                                          outline='violet')
            self.bboxIdList[self.selectidx][0] = rect
        self.mainPanel.delete(self.bboxIdList[idx][0])
        bbox = self.bboxList[idx]
        x0 = int(bbox[0] * DEST_SIZE[0]/w0)
        y0 = int(bbox[1] * DEST_SIZE[1]/h0)
        x1 = int(bbox[2] * DEST_SIZE[0]/w0)
        y1 = int(bbox[3] * DEST_SIZE[1]/h0)
        rect = self.mainPanel.create_rectangle(x0, y0, x1, y1, width=2,
                                               outline='lime')
        self.bboxIdList[idx][0] = rect
        self.selectidx = idx

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def nextPoint(self, event):
        print("next")
        sel = self.listbox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        string = self.listbox.get(idx)
        if self.STATE['point'] == 1 and len(self.bboxIdList[idx]) >= keypoint_num + 1:
            self.clearKPnt()
            string = string[:23]
            self.bboxList[idx] = self.bboxList[idx][:4]
        string += ' (%.2f,%.2f)' % (-1, -1)
        self.bboxList[idx].append(-1)
        self.bboxList[idx].append(-1)
        self.bboxIdList[idx].append(None)
        self.listbox.delete(idx)
        self.listbox.insert(idx, string)
        self.listbox.select_set(idx)
        if self.STATE['point'] >= keypoint_num:
            self.STATE['point'] = 0
        else:
            self.STATE['point'] += 1

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        self.selectidx = None
        self.STATE['point'] = 0
        for item in self.bboxIdList[idx]:
            self.mainPanel.delete(item)
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)
        if self.pointID:
            self.mainPanel.delete(self.pointID)

    def addBBox(self):
        if self.selectidx is not None:
            self.mainPanel.delete(self.bboxIdList[self.selectidx][0])
            bbox = self.bboxList[self.selectidx]
            x0 = int(bbox[0] * DEST_SIZE[0]/w0)
            y0 = int(bbox[1] * DEST_SIZE[1]/h0)
            x1 = int(bbox[2] * DEST_SIZE[0]/w0)
            y1 = int(bbox[3] * DEST_SIZE[1]/h0)
            rect = self.mainPanel.create_rectangle(x0, y0, x1, y1, width=2,
                                                          outline='violet')
            self.bboxIdList[self.selectidx][0] = rect
        self.listbox.select_clear(0, END)
        self.STATE['point'] = 0
        self.selectidx = None
        if self.pointID:
            self.mainPanel.delete(self.pointID)


    def clearKPnt(self):
        sel = self.listbox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        for point in self.bboxIdList[idx][1:]:
            self.mainPanel.delete(point)
        self.bboxIdList[idx] = self.bboxIdList[idx][:1]
        string = self.listbox.get(idx)
        string = string[:23]
        self.bboxList[idx] = self.bboxList[idx][:4]
        self.listbox.delete(idx)
        self.listbox.insert(idx, string)
        self.listbox.select_set(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            for item in self.bboxIdList[idx]:
                self.mainPanel.delete(item)
        self.STATE['point'] = 0
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []
        if self.pointID:
            self.mainPanel.delete(self.pointID)

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
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.cur = idx
            self.loadImage()

    def imgresize(w, h, w_box, h_box, pil_image):
        '''
        resize a pil_image object so it will fit into
        a box of size w_box times h_box, but retain aspect ratio
        '''
        f1 = 1.0*w_box/w  # 1.0 forces float division in Python2
        f2 = 1.0*h_box/h
        factor = min([f1, f2])
        # print(f1, f2, factor) # test
        # use best down-sizing filter
        width = int(w*factor)
        height = int(h*factor)
        return pil_image.resize((width, height), Image.ANTIALIAS)


if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.mainloop()
