#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Shion Tominaga'
__copyright__ = 'Copyright (c) 2020 Miyata Lab.'

# Standard library imports.
# None

# Related third party imports.
import cv2
import numpy as np

# Local application/library specific imports.
#None


class Morphology():
    def init(self):
        pass


    def erosion(self, img, kernel=(5,5)):
        img = img.copy()
        kernel  = np.ones(kernel, np.uint8)
        erosion = cv2.erode(img, kernel, iterations=1)
        return erosion


    def dilation(self, img, kernel=(5,5)):
        img = img.copy()
        kernel   = np.ones(kernel, np.uint8)
        dilation = cv2.dilate(img,kernel,iterations=1)
        return dilation


    def opening(self, img, kernel=(5,5)):
        img = img.copy()
        kernel  = np.ones(kernel, np.uint8)
        opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        return opening


    def closing(self, img, kernel=(5,5)):
        img = img.copy()
        kernel  = np.ones(kernel, np.uint8)
        closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        return closing


    def gradient(self, img, kernel=(5,5)):
        img = img.copy()
        kernel   = np.ones(kernel, np.uint8)
        gradient = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)
        return gradient
