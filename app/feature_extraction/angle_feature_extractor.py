#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Shion Tominaga'
__copyright__ = 'Copyright (c) 2020 Miyata Lab.'

# Standard library imports.
import logging
import sys

# Related third party imports.
import cv2
import math
import numpy as np


logger = logging.getLogger(__name__)


class AngleFeatureExtractor():
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


    def search_most_left_white_pixel(self, bin_image, coordinate):
        """
        画像中の指定座標と同じ高さで最も左にある（＝x座標の値が小さい）白い画素の座標を探す

        Parameters
        ----------
        bin_image : numpy.ndarray
            白(255,255,255)と黒(0,0,0)の2値画像。画像の色空間はBGR。
        coordinate : list
            画像中の特定の座標。
            [x, y]のような1次元リスト。

        Returns
        -------
        most_left_coordinate : list
            画像中の指定座標と同じ高さで最も左にある白い画素の座標。
            [x, y] のような1次元リスト。
        """
        image = bin_image.copy()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        x = coordinate[0]
        y = coordinate[1]

        # print('image.shape = {}'.format(image.shape))

        for col in range(x):
            # print('curr = [{}, {}]'.format(col, y))
            # print('image[y][col] = {}'.format(image[y][col]))
            if image[y][col] != 0:
                return [col, y]

        logger.error('[%s] Warning: Most left white pixel is not found.' % sys._getframe().f_code.co_name)
        return coordinate


    # 2点の座標から傾きと切片を求める関数
    # def calc_slope_intercept(self, ndarray1, ndarray2):
    #     x1, y1 = ndarray1.flatten()
    #     x2, y2 = ndarray2.flatten()
    #     if x1 - x2 == 0:
    #         x1 += 0.00000001
    #     slope = (y1 - y2) / (x1 - x2)
    #     intercept = y1 - slope * x1
    #     return (slope, intercept)


    def calcAngleFrom3Pnts(self, coord1, coord2, coord3):
        x1, y1 = coord1
        x2, y2 = coord2
        x3, y3 = coord3
        ax = x2 - x1 if x2 - x1 != 0 else sys.float_info.epsilon
        ay = y2 - y1 if y2 - y1 != 0 else sys.float_info.epsilon
        bx = x2 - x3 if x2 - x3 != 0 else sys.float_info.epsilon
        by = y2 - y3 if y2 - y3 != 0 else sys.float_info.epsilon
        cos = (ax * bx + ay * by) / (math.sqrt(ax**2 + ay**2) * math.sqrt(bx**2 + by**2))
        arccos = math.acos(round(cos, 10)) # 小数第10位に丸める
        angle = math.degrees(arccos)
        return angle


    def extract_angle_feature(self, tear_coordinates, edge_detected_image, image_for_drawing):
        """
        fa(angle Feature)を抽出する

        Parameters
        ----------
        tear_coordinates : list
            破れ目を構成する点の座標群。
            [[x_1,y_1], [x_2,y_2], ..., [x_n,y_n]] のような2次元リスト。
        edge_detected_image : numpy.ndarray
            エッジ検出後の画像。画像の色空間はBGR。
        image_for_drawing : numpy.ndarray
            描画用の画像。画像の色空間はBGR。

        Returns
        -------
        fa : float
            faの抽出結果。
        """
        image = image_for_drawing.copy()

        middle_coordinate      = tear_coordinates[int(len(tear_coordinates) / 2)]
        lowest_coordinate      = self.search_lowest_coordinate(tear_coordinates)
        lowest_left_coordinate = self.search_most_left_white_pixel(edge_detected_image, lowest_coordinate)

        # l_c_slope = self.calc_slope_intercept(lowest_left_coordinate, lowest_coordinate)
        fa = self.calcAngleFrom3Pnts(middle_coordinate, lowest_left_coordinate, lowest_coordinate)

        if self.DEBUG_FLAG:
            cv2.circle(image, tuple(middle_coordinate), 15, (0,255,255), -1)
            cv2.circle(image, tuple(lowest_coordinate), 15, (0,255,255), -1)
            cv2.circle(image, tuple(lowest_left_coordinate), 15, (0,255,0), -1)

            cv2.line(image, tuple(middle_coordinate), tuple(lowest_left_coordinate),(0,0,255), 8)
            cv2.line(image, tuple(lowest_coordinate), tuple(lowest_left_coordinate),(0,0,255), 8)

            cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_angle_feature.jpg', image)
            self.ipm.IMG_SAVE_CNT += 1

        return fa
