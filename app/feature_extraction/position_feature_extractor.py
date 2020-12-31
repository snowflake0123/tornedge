#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Shion Tominaga'
__copyright__ = 'Copyright (c) 2019 Miyata Lab.'

# Standard library imports.
import logging
import sys

# Related third party imports.
import cv2


logger = logging.getLogger(__name__)


class PositionFeatureExtractor():
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


    def extract_position_feature(self, tear_coordinates, image_for_drawing):
        """
        fp(Position Feature)を抽出する

        Parameters
        ----------
        tear_coordinates : list
            破れ目を構成する点の座標群。
            [[x_1,y_1], [x_2,y_2], ..., [x_n,y_n]] のような2次元リスト。
        image_for_drawing : numpy.ndarray
            特徴点描画用の画像。画像の色空間はBGR。

        Returns
        -------
        fp : list
            fpの抽出結果。
            [a_1, a_2, ..., a_n] のような1次元リスト。
        """
        image = image_for_drawing.copy()

        left_end  = tear_coordinates[0]
        right_end = tear_coordinates[-1]
        lowest_coordinate  = self.search_lowest_coordinate(tear_coordinates)
        highest_coordinate = self.search_highest_coordinate(tear_coordinates)
        fp = []

        # 1.破れ目の左の端点が，破れ目の右の端点より高い（Y座標が小さい）位置に存在するか？
        if left_end[1] < right_end[1]:
            fp.append(1)
        else:
            fp.append(0)

        # 2.破れ目上で最も低い位置にある（y座標が大きい）点が，破れ目上で最も高い位置にある（y座標が小さい）点よりも左に存在するか？
        if lowest_coordinate[0] < highest_coordinate[0]:
            fp.append(1)
        else:
            fp.append(0)

        if self.DEBUG_FLAG:
            self.ipm.draw_circles(image, left_end, 15, (0,0,255))
            self.ipm.draw_circles(image, right_end, 15, (0,0,255))
            self.ipm.draw_circles(image, lowest_coordinate, 15, (255,128,0))
            self.ipm.draw_circles(image, highest_coordinate, 15, (255,128,0))
            cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_position_feature.jpg', image)
            self.ipm.IMG_SAVE_CNT+=1

        return fp
