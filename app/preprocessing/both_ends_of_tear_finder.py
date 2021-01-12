#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Shion Tominaga'
__copyright__ = 'Copyright (c) 2020 Miyata Lab.'


# Standard library imports.
import logging
import sys

# Related third party imports.
import cv2
import numpy as np


logger = logging.getLogger(__name__)


class BothEndsOfTearFinder():
    def __init__(self, ipm):
        self.ipm = ipm
        self.DEBUG_FLAG   = self.ipm.get_debug_flag_status()
        self.IMAGE_WIDTH  = self.ipm.get_image_width()
        self.IMAGE_HEIGHT = self.ipm.get_image_height()


    def detect_corners(self, src_image):
        """
        Shi-Tomasiの手法を用いて画像中からN個のコーナーを検出する

        Parameters
        ----------
        src_image : numpy.ndarray
            元画像。画像の色空間はBGR。

        Returns
        -------
        corners : numpy.ndarray
            画像中から検出されたコーナー。格納順は "コーナーらしさ" の降順。
        """
        # Parameters
        MAX_CORNERS   = 500    # 検出するコーナーの最大個数
        QUALITY_LEVEL = 0.0001 # 検出するコーナーの質レベル
        MIN_DISTANCE  = 5      # 2つのコーナー間のユークリッド距離(単位:px?)の最小値

        image = src_image.copy()
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 画像中からコーナーらしき箇所を MAX_CORNERS 個検出
        corners = cv2.goodFeaturesToTrack(gray_image, MAX_CORNERS, QUALITY_LEVEL, MIN_DISTANCE)
        corners = np.int0(corners)

        if self.DEBUG_FLAG:
            corners_list = [[corner.ravel()[0], corner.ravel()[1]] for corner in corners]
            self.ipm.draw_circles(image, corners_list, 5, (0,0,255))
            cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_corners_detected.jpg', image)
            self.ipm.IMG_SAVE_CNT+=1

        return corners


    def detect_vertical_lines(self, src_image):
        """
        画像中から縦の直線を全て検出する

        Parameters
        ----------
        src_image : numpy.ndarray
            元画像。画像の色空間はBGR。

        Returns
        -------
        vertical_lines : list
            画像中から検出された縦直線群。
        """
        #Parameters
        THETA_TH     = 0.08
        THETA_MAX_TH = 0.2

        image      = src_image.copy()
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges      = cv2.Canny(gray_image, 0, 0, apertureSize=7, L2gradient=True)
        lines      = cv2.HoughLines(edges, 1, np.pi/400, 60)

        try:
            if lines is None: raise Exception
        except:
            logger.error('[%s] LineNotFoundError: Lines were not found in the image.' % sys._getframe().f_code.co_name)
            sys.exit()

        # 画像中の縦直線（左右の辺と思われる直線）の検出
        vertical_lines = []
        try:
            while len(vertical_lines) <= 15 and THETA_TH <= THETA_MAX_TH:
                for line in lines:
                    rho, theta = line[0]
                    if (theta < THETA_TH and theta > -THETA_TH) or (theta < np.pi+THETA_TH and theta > np.pi-THETA_TH):
                        vertical_lines.append(line)
                THETA_TH += 0.02
                if self.DEBUG_FLAG:
                    print('THETA_TH =', THETA_TH)
        except:
            logger.error('[%s] VerticalLineDetectionError: Vertical lines were not detected correctly in the image.' % sys._getframe().f_code.co_name)
            sys.exit()

        return vertical_lines


    def get_end_points_of_line(self, rho, theta):
        """
        直線の両端点の座標を取得する

        Parameters
        ----------
        rho : numpy.float32
            hough変換によって得られた直線の原点からの距離ρ。
        theta : numpy.float32
            hough変換によって得られた直線の傾きθ。

        Returns
        -------
        end_points_of_line : tuple
            直線の両端点の座標。
            ((x1, y1), (x2, y2)) のような2次元タプル。
        """
        a  = np.cos(theta)
        b  = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))

        end_points_of_line = ((x1, y1), (x2, y2))

        return end_points_of_line


    def line_exists_in_searching_area(self, l_or_r, end_points_of_line, search_area_num, search_width):
        """
        直線が探索中のエリア内に位置しているかを判定する

        Parameters
        ----------
        l_or_r : string
            紙片の左右どちらの辺について処理を行うか[left/right]で指定する。
        end_points_of_line : tuple
            直線の両端点の座標。((x1,y1),(x2,y2))。
        search_area_num : int
            画像の横幅を何個のエリアに分けて探索するかの値。
        search_width : int
            分けられたエリアのうち，画像の左/右端から何個のエリアを探索するかの値。

        Returns
        -------
        True/False : boolean
            直線が探索中のエリア内に位置しているかどうか。
        """
        x1 = end_points_of_line[0][0]
        x2 = end_points_of_line[1][0]
        if l_or_r == "left":
            if (x1 < self.ipm.IMAGE_WIDTH*search_width/search_area_num) or (x2 < self.ipm.IMAGE_WIDTH*search_width/search_area_num):
                return True
            return False
        elif l_or_r == "right":
            if (x1 >= self.ipm.IMAGE_WIDTH*(search_area_num-search_width)/search_area_num) or (x2 >= self.ipm.IMAGE_WIDTH*(search_area_num-search_width)/search_area_num):
                return True
            return False


    def extract_l_or_r_side_vlines(self, vlines, l_or_r):
        """
        縦直線群から，紙片の左/右の辺付近に引かれている縦直線のみを抽出する

        Parameters
        ----------
        vlines : list
            画像中から検出された縦直線群。
        l_or_r : string
            紙片の左右どちらの辺の縦直線を検出するかを[left/right]で指定する。

        Returns
        -------
        l_or_r_side_vlines : list
            左/右の辺付近に引かれている縦直線。
        """
        # Parameters
        LINE_NUM_TH = 10 # 左/右の辺付近の縦直線をLINE_NUM_TH本見つけるまで抽出し続ける

        l_or_r_side_vlines = []
        line_num           = 0
        search_area_num    = 10
        search_width       = 2

        while line_num < LINE_NUM_TH and search_width <= search_area_num:
            for vline in vlines:
                rho, theta = vline[0]
                end_points_of_vline = self.get_end_points_of_line(rho, theta)
                if (self.line_exists_in_searching_area(l_or_r, end_points_of_vline, search_area_num, search_width)):
                    l_or_r_side_vlines.append(vline)
                    line_num += 1
            search_width += 1

        return l_or_r_side_vlines


    def calc_dist_between_point_and_line(self, point, end_points_of_line):
        """
        ある点とある直線との距離を計算する

        Parameters
        ----------
        point : numpy.ndarray
            ある点。
        end_points_of_line : tuple
            ある直線。

        Returns
        -------
        dist_between_point_and_line : numpy.float64
            ある点とある直線との距離。
        """
        x, y   = point.ravel()
        end_point1, end_point2 = end_points_of_line
        x1, y1 = end_point1
        x2, y2 = end_point2
        u = np.array([x2 - x1, y2 - y1])
        v = np.array([x - x1, y - y1])
        dist_between_point_and_line = abs(np.cross(u, v) / np.linalg.norm(u))

        return dist_between_point_and_line


    def extract_candidates_of_end_of_tear(self, points, vlines):
        """
        破れ目の端の候補を抽出する

        Parameters
        ----------
        points : numpy.ndarray
            点の座標群。この中から破れ目の端の候補が抽出される。
        vlines : list
            破れ目の端付近に引かれた縦直線群。

        Returns
        -------
        end_candidates : list
            破れ目の端の候補の点群。
        """
        # Parameters
        LINE_NUM_TH      = 5
        PNT_LINE_DIST_TH = 7

        # 縦直線のうち任意の LINE_NUM_TH 本から PNT_LINE_DIST_TH px以内にある点を抽出
        end_candidates = []
        for point in points:
            line_num = 0
            for vline in vlines:
                rho, theta = vline[0]
                end_points_of_vline = self.get_end_points_of_line(rho, theta)
                dist = self.calc_dist_between_point_and_line(point, end_points_of_vline)
                if dist <= PNT_LINE_DIST_TH:
                    line_num += 1
            if line_num >= LINE_NUM_TH:
                x, y = point.ravel()
                end_candidates.append([x, y])

        if end_candidates == []:
            logger.warning('Warning: Candidates of end of tear were not found.')

        return end_candidates


    def find_highest_point(self, points):
        """
        点群の中で最も高い（＝y座標の値が小さい）位置にある点を探す

        Parameters
        ----------
        points : list
            点群。
            [[x_1,y_1], [x_2,y_2], ..., [x_n,y_n]] のような2次元リスト。

        Returns
        -------
        highest_point : list
            points の中で最も高い位置にある点。
            [x_h, y_h] のような1次元リスト。
        """
        try:
            highest_point = points[0]
        except IndexError:
            logger.error('[%s] IndexError: List index out of range.' % sys._getframe().f_code.co_name)
            sys.exit()

        for point in points:
            if point[1] < highest_point[1]:
                highest_point = point
        return highest_point


    def detect_both_ends_of_tear(self, preprocessed_image):
        """
        紙片の破れ目の両端点を探す

        Parameters
        ----------
        preprocessed_image : numpy.ndarray
            前処理後の画像。画像の色空間はBGR。

        Returns
        -------
        left_end : list
            紙片の破れ目の左端の点の座標。1次元リスト。
        right_end : list
            紙片の破れ目の右端の点の座標。1次元リスト。
        """
        image = preprocessed_image.copy()

        points = self.detect_corners(image)

        vlines = self.detect_vertical_lines(image)
        vlines_left  = self.extract_l_or_r_side_vlines(vlines, 'left')
        vlines_right = self.extract_l_or_r_side_vlines(vlines, 'right')

        left_end_candidates  = self.extract_candidates_of_end_of_tear(points, vlines_left)
        right_end_candidates = self.extract_candidates_of_end_of_tear(points, vlines_right)

        left_end  = self.find_highest_point(left_end_candidates)
        right_end = self.find_highest_point(right_end_candidates)

        if self.DEBUG_FLAG:
            self.ipm.draw_lines(image, vlines, (0,192,255), 1)
            self.ipm.draw_lines(image, vlines_left, (255,128,0), 1)
            self.ipm.draw_lines(image, vlines_right, (255,128,0), 1)
            self.ipm.draw_circles(image, left_end_candidates, 5, (0,192,255))
            self.ipm.draw_circles(image, right_end_candidates, 5, (0,192,255))
            self.ipm.draw_circles(image, left_end, 15, (0,0,255))
            self.ipm.draw_circles(image, right_end, 15, (0,0,255))
            cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_both_ends_of_tear_detected.jpg', image)
            self.ipm.IMG_SAVE_CNT+=1

        return left_end, right_end
