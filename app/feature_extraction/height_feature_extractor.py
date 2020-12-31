#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Shion Tominaga'
__copyright__ = 'Copyright (c) 2020 Miyata Lab.'

# Standard library imports.
import logging
import sys

# Related third party imports.
import cv2


logger = logging.getLogger(__name__)


class HeightFeatureExtractor():
    def __init__(self, ipm):
        self.ipm = ipm
        self.DEBUG_FLAG = self.ipm.get_debug_flag_status()


    def search_lowest_coordinate(self, coordinates):
        """
        点の座標群の中から最も低い（＝y座標の値が大きい）点の座標を探す

        Parameters
        ----------
        coordinates : list
            座標群。
            [[x_1,y_1], [x_2,y_2], ..., [x_n,y_n]] のような2次元リスト。

        Returns
        -------
        lowest_coordinate : list
            coordinates の中で最も低い座標。
            [x_l, y_l] のような1次元リスト。
        """
        try:
            lowest_coordinate = coordinates[0]
        except IndexError:
            logger.error('[%s] IndexError: List index out of range.' % sys._getframe().f_code.co_name)
            sys.exit()

        for coordinate in coordinates:
            if coordinate[1] > lowest_coordinate[1]:
                lowest_coordinate = coordinate
        return lowest_coordinate


    def search_highest_coordinate(self, coordinates):
        """
        点の座標群の中から最も高い（＝y座標の値が小さい）点の座標を探す

        Parameters
        ----------
        coordinates : list
            座標群。
            [[x_1,y_1], [x_2,y_2], ..., [x_n,y_n]] のような2次元リスト。

        Returns
        -------
        lowest_coordinate : list
            coordinates の中で最も高い座標。
            [x_h, y_h] のような1次元リスト。
        """
        try:
            highest_coordinate = coordinates[0]
        except IndexError:
            logger.error('[%s] IndexError: List index out of range.' % sys._getframe().f_code.co_name)
            sys.exit()

        for coordinate in coordinates:
            if coordinate[1] < highest_coordinate[1]:
                highest_coordinate = coordinate
        return highest_coordinate


    def extract_height_feature(self, tear_coordinates, image_for_drawing):
        """
        fh(Height Feature)を抽出する

        Parameters
        ----------
        tear_coordinates : list
            破れ目を構成する点の座標群。
            [[x_1,y_1], [x_2,y_2], ..., [x_n,y_n]] のような2次元リスト。
        image_for_drawing : numpy.ndarray
            描画用の画像。画像の色空間はBGR。

        Returns
        -------
        fh : float
            fhの抽出結果。
        """
        image = image_for_drawing.copy()

        left_end  = tear_coordinates[0]
        right_end = tear_coordinates[-1]
        lowest_coordinate  = self.search_lowest_coordinate(tear_coordinates)
        highest_coordinate = self.search_highest_coordinate(tear_coordinates)

        fh = abs(lowest_coordinate[1] - highest_coordinate[1]) / abs(left_end[0] - right_end[0])
        fh = round(fh, 5)

        if self.DEBUG_FLAG:
            cv2.circle(image, tuple(left_end), 15, (0,255,0), -1)
            cv2.circle(image, tuple(right_end), 15, (0,255,0), -1)
            cv2.circle(image, tuple(lowest_coordinate), 15, (0,0,255), -1)
            cv2.circle(image, tuple(highest_coordinate), 15, (0,0,255), -1)

            cv2.line(image, tuple(left_end), (right_end[0], left_end[1]),(128,255,0), 4)
            cv2.line(image, tuple(highest_coordinate), (highest_coordinate[0], lowest_coordinate[1]),(128,0,255), 8)

            cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_height_feature.jpg', image)
            self.ipm.IMG_SAVE_CNT += 1

        return fh
