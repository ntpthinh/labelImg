#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import codecs
from libs.constants import DEFAULT_ENCODING

TSV_EXT = '.tsv'
ENCODE_METHOD = DEFAULT_ENCODING

class PICKWriter:
    def __init__(self, foldername, filename, databaseSrc='Unknown', localImgPath=None):
        self.foldername = foldername
        self.filename = filename
        self.databaseSrc = databaseSrc
        self.boxlist = []
        self.localImgPath = localImgPath
        self.verified = False

    def addBndBox(self, x1, y1, x2, y2, x3, y3, x4, y4, text,  label):
        bndbox = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'x3': x3, 'y3': y3, 'x4': x4, 'y4': y4, 'text': text,
                  'label': label}
        self.boxlist.append(bndbox)

    def BndBox2PICKLine(self, box):
        return box['x1'], box['y1'], box['x2'], box['y2'], box['x3'], box['y3'], box['x4'], box['y4'], box['text'], box['label']

    def save(self, targetFile=None):

        out_file = None #Update yolo .txt

        if targetFile is None:
            out_file = open(self.filename + TSV_EXT, 'w', encoding=ENCODE_METHOD)
        else:
            out_file = codecs.open(targetFile, 'w', encoding=ENCODE_METHOD)

        for box in self.boxlist:
            x1, y1, x2, y2, x3, y3, x4, y4, text, label = self.BndBox2PICKLine(box)
            out_file.write("%d,%d,%d,%d,%d,%d,%d,%d,%s,%s\n" % (x1, y1, x2, y2, x3, y3, x4, y4, text, label))

        out_file.close()


class PICKReader:

    def __init__(self, filepath, image, classListPath=None):
        # shapes type:
        # [labbel, [(x1,y1), (x2,y2), (x3,y3), (x4,y4)], color, color, difficult]
        self.shapes = []
        self.filepath = filepath

        if classListPath is None:
            dir_path = os.path.dirname(os.path.realpath(self.filepath))
            self.classListPath = os.path.join(dir_path, "classes.txt")
        else:
            self.classListPath = classListPath

        # print (filepath, self.classListPath)

        classesFile = open(self.classListPath, 'r')
        self.classes = classesFile.read().strip('\n').split('\n')

        # print (self.classes)

        self.verified = False
        # try:
        self.parseYoloFormat()
        # except:
            # pass

    def getShapes(self):
        return self.shapes

    def addShape(self, x1, y1, x2, y2, x3, y3, x4, y4, text, label):

        points = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        self.shapes.append((label, points, None, None))

    def yoloLine2Shape(self, classIndex, xcen, ycen, w, h):
        label = self.classes[int(classIndex)]

        xmin = max(float(xcen) - float(w) / 2, 0)
        xmax = min(float(xcen) + float(w) / 2, 1)
        ymin = max(float(ycen) - float(h) / 2, 0)
        ymax = min(float(ycen) + float(h) / 2, 1)

        xmin = int(self.imgSize[1] * xmin)
        xmax = int(self.imgSize[1] * xmax)
        ymin = int(self.imgSize[0] * ymin)
        ymax = int(self.imgSize[0] * ymax)

        return label, xmin, ymin, xmax, ymax

    def parseYoloFormat(self):
        bndBoxFile = open(self.filepath, 'r')
        for bndBox in bndBoxFile:
            classIndex, xcen, ycen, w, h = bndBox.strip().split(',')
            label, xmin, ymin, xmax, ymax = self.yoloLine2Shape(classIndex, xcen, ycen, w, h)

            # Caveat: difficult flag is discarded when saved as yolo format.
            self.addShape(label, xmin, ymin, xmax, ymax, False)