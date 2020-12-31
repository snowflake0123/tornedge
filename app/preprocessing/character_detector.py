#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Shion Tominaga'
__copyright__ = 'Copyright (c) 2020 Miyata Lab.'


# Related third party imports.
import cv2
import numpy as np
from pymatting import alpha
import pathlib
import sys
from tensorflow.keras.preprocessing.image import img_to_array

# Local application/library specific imports.
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir))
import morphology
import image_binarizer as binarizer


class CharacterDetector():
    # def __init__(self, ipm, ss_estimator):
    #     self.ipm = ipm
    #     self.morph = morphology.Morphology()
    #     self.binarizer = binarizer.ImageBinarizer()
    #     self.DEBUG_FLAG = self.ipm.get_debug_flag_status()
    #     self.IMAGE_WIDTH  = self.ipm.get_image_width()
    #     self.IMAGE_HEIGHT = self.ipm.get_image_height()
    def __init__(self):
        pass

    def execute(self):
        cv2.imread('.jpg')


if __name__ == '__main__':
    cd = CharacterDetector()
    cd.execute()
