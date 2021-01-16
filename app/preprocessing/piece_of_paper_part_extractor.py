#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Shion Tominaga'
__copyright__ = 'Copyright (c) 2019-2020 Miyata Lab.'

# Standard library imports.
import logging
import sys

# Related third party imports.
import cv2
import numpy as np


logger = logging.getLogger(__name__)


class PieceOfPaperPartExtractor():
    def __init__(self, ipm):
        self.ipm = ipm
        self.DEBUG_FLAG = self.ipm.get_debug_flag_status()


    def remove_char(self, src_bin_image):
        """
        画像中の紙片部分にある文字の除去

        Parameters
        ----------
        src_bin_image : numpy.ndarray
            元画像。白黒に2値化されている必要がある。画像の色空間はBGR。

        Returns
        -------
        char_removed_image : numpy.ndarray
            文字除去後の画像。画像の色空間はBGR。
        """
        # Parameters.
        REMOVE_CHAR_KERNEL = np.ones((40, 40), np.uint8)

        image = src_bin_image.copy()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        char_removed_image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, REMOVE_CHAR_KERNEL)
        if self.DEBUG_FLAG:
            cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_char_removed.jpg', char_removed_image)
            self.ipm.IMG_SAVE_CNT += 1

        char_removed_image = cv2.cvtColor(char_removed_image, cv2.COLOR_GRAY2BGR)

        return char_removed_image


    def extract_largest_white_area(self, src_bin_image):
        """
        画像中で輪郭が最も大きい白領域を取り出す

        Parameters
        ----------
        src_bin_image : numpy.ndarray
            元画像。白黒に2値化されている必要がある。画像の色空間はBGR。

        Returns
        -------
        largest_white_area_extracted_image : numpy.ndarray
            画像中の最大輪郭白領域抽出後の画像。画像の色空間はBGR。
        """
        # Parameters
        MIN_GRAY = np.array([0], np.uint8)
        MAX_GRAY = np.array([50], np.uint8)

        image = src_bin_image.copy()
        nega_posi_reversed_image = cv2.bitwise_not(image)
        threshold_gray = cv2.inRange(nega_posi_reversed_image, MIN_GRAY, MAX_GRAY)
        contours, hierachy = cv2.findContours(threshold_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        try:
            if contours == []: raise Exception
        except:
            logger.error('[%s] WhiteAreaNotFoundError: White areas were not found in the image.' % sys._getframe().f_code.co_name)
            sys.exit()

        # 画像中の全白領域から輪郭が最大の白領域を探す
        largest_area    = 0
        largest_contour = None
        for contour in contours:
            area = cv2.contourArea(contour)
            if largest_area < area:
                largest_area    = area
                largest_contour = contour

        # 輪郭が最大の白領域以外の白領域を黒く塗りつぶす
        black_background = np.zeros_like(image)
        largest_white_area_extracted_image = cv2.drawContours(black_background, [largest_contour], -1, (255,255,255), -1)

        if self.DEBUG_FLAG:
            cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_largest_white_area_extracted.jpg', largest_white_area_extracted_image)
            self.ipm.IMG_SAVE_CNT += 1

        return largest_white_area_extracted_image
