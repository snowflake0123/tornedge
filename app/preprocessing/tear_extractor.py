#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Shion Tominaga'
__copyright__ = 'Copyright (c) 2020 Miyata Lab.'


# Standard library imports.
import math

# Related third party imports.
import cv2
import numpy as np

# Local application/library specific imports.
import morphology


class TearExtractor():
    def __init__(self, ipm):
        self.ipm = ipm
        self.morph = morphology.Morphology()
        self.DEBUG_FLAG = self.ipm.get_debug_flag_status()


    def detect_edge_by_canny_method(self, src_image):
        """
        Canny法を用いて画像中のエッジを検出する

        Parameters
        ----------
        src_image : numpy.ndarray
            元画像。画像の色空間はBGR。

        Returns
        -------
        edge_detected_image : numpy.ndarray
            エッジ検出後の画像。画像の色空間はBGR。
        """
        image               = src_image.copy()
        gray_image          = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edge_detected_image = cv2.Canny(gray_image, 0, 0, apertureSize=7, L2gradient=True)
        edge_detected_image = cv2.cvtColor(edge_detected_image, cv2.COLOR_GRAY2BGR)

        edge_detected_image = self.morph.closing(edge_detected_image, (3,3))

        if self.DEBUG_FLAG:
            cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_edge_detected(canny).jpg', edge_detected_image)
            self.ipm.IMG_SAVE_CNT+=1

        return edge_detected_image


    def extract_white_pixel_coordinates(self, src_bin_image):
        """
        2値画像中から白いピクセルの座標を全て抽出する

        Parameters
        ----------
        src_bin_image : numpy.ndarray
            白(255,255,255)と黒(0,0,0)の2値画像。画像の色空間はBGR。

        Returns
        -------
        white_pixel_coordinates : list
            画像中から抽出された白いピクセルの座標群。
        """
        image             = src_bin_image.copy()
        gray_image        = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        is_white_in_grayimage = (gray_image >= 128)

        gray_image_width  = gray_image.shape[1]
        gray_image_height = gray_image.shape[0]

        white_pixel_coordinates = []
        for y in range(0, gray_image_height):
            for x in range(0, gray_image_width):
                if is_white_in_grayimage[y, x]:
                    white_pixel_coordinates.append([x, y])

        return white_pixel_coordinates


    def find_closest_pixel_to_end_of_tear(self, pixel_coordinates, end_of_tear):
        """
        ピクセル群から，破れ目の端に最も近いピクセルを探す

        Parameters
        ----------
        pixel_coordinates : list
            探す対象となるピクセル群の座標群。2次元リスト。
        end_of_tear : list
            破れ目の端の座標。1次元リスト。

        Returns
        -------
        nearest_coord : list
            破れ目の端に最も近いピクセル。1次元リスト。
        """
        min_dist      = float('inf')
        nearest_coord = [0, 0]

        for coordinate in pixel_coordinates:
            dist = math.sqrt( (coordinate[0] - end_of_tear[0]) ** 2 + \
                              (coordinate[1] - end_of_tear[1]) ** 2 )
            if dist < min_dist:
                min_dist      = dist
                nearest_coord = coordinate

        return nearest_coord


    def chase_white_pixels(self, edge_detected_image, start_pixel, goal_pixel):
        """
        白いピクセルを追跡し，追跡中に通過した白ピクセルの座標群を返す

        Parameters
        ----------
        edge_detected_image : numpy.ndarray
            エッジ検出後の画像。画像の色空間はBGR。
        start_pixel : list
            追跡を開始する白ピクセルの座標。[s_x,s_y] のような1次元リスト。
        goal_pixel : list
            追跡を終了する白ピクセルの座標。[g_x,g_y] のような1次元リスト。

        Returns
        -------
        passed_pixels : list
            追跡中に通過した白ピクセルの座標群。2次元リスト。
        """
        image           = edge_detected_image.copy()
        gray_image      = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        curr_pixel      = start_pixel
        passed_pixels   = []
        mistaken_pixels = []

        while not np.allclose(curr_pixel, goal_pixel) and curr_pixel[0] <= goal_pixel[0]:
            if gray_image.item(curr_pixel[1], curr_pixel[0]) >= 128:
                # Checks right pixel.
                if gray_image.item(curr_pixel[1], curr_pixel[0]+1) >= 128 and \
                              [curr_pixel[0]+1, curr_pixel[1]] not in passed_pixels and \
                              [curr_pixel[0]+1, curr_pixel[1]] not in mistaken_pixels:
                    passed_pixels.append(curr_pixel)
                    curr_pixel = [curr_pixel[0]+1, curr_pixel[1]]

                # Checks upper right pixel.
                elif gray_image.item(curr_pixel[1]-1, curr_pixel[0]+1) >= 128 and \
                                [curr_pixel[0]+1, curr_pixel[1]-1] not in passed_pixels and \
                                [curr_pixel[0]+1, curr_pixel[1]-1] not in mistaken_pixels:
                    passed_pixels.append(curr_pixel)
                    curr_pixel = [curr_pixel[0]+1, curr_pixel[1]-1]

                # Checks lower right pixel.
                elif gray_image.item(curr_pixel[1]+1, curr_pixel[0]+1) >= 128 and \
                                [curr_pixel[0]+1, curr_pixel[1]+1] not in passed_pixels and \
                                [curr_pixel[0]+1, curr_pixel[1]+1] not in mistaken_pixels:
                    passed_pixels.append(curr_pixel)
                    curr_pixel = [curr_pixel[0]+1, curr_pixel[1]+1]

                # Checks upper pixel.
                elif gray_image.item(curr_pixel[1]-1, curr_pixel[0]) >= 128 and \
                                [curr_pixel[0], curr_pixel[1]-1] not in passed_pixels and \
                                [curr_pixel[0], curr_pixel[1]-1] not in mistaken_pixels:
                    passed_pixels.append(curr_pixel)
                    curr_pixel = [curr_pixel[0], curr_pixel[1]-1]

                # Checks lower pixel.
                elif gray_image.item(curr_pixel[1]+1, curr_pixel[0]) >= 128 and \
                                [curr_pixel[0], curr_pixel[1]+1] not in passed_pixels and \
                                [curr_pixel[0], curr_pixel[1]+1] not in mistaken_pixels:
                    passed_pixels.append(curr_pixel)
                    curr_pixel = [curr_pixel[0], curr_pixel[1]+1]

                # Checks upper left pixel.
                elif gray_image.item(curr_pixel[1]-1, curr_pixel[0]-1) >= 128 and \
                                [curr_pixel[0]-1, curr_pixel[1]-1] not in passed_pixels and \
                                [curr_pixel[0]-1, curr_pixel[1]-1] not in mistaken_pixels:
                    passed_pixels.append(curr_pixel)
                    curr_pixel = [curr_pixel[0]-1, curr_pixel[1]-1]

                # Checks lower left pixel.
                elif gray_image.item(curr_pixel[1]+1, curr_pixel[0]-1) >= 128 and \
                                [curr_pixel[0]-1, curr_pixel[1]+1] not in passed_pixels and \
                                [curr_pixel[0]-1, curr_pixel[1]+1] not in mistaken_pixels:
                    passed_pixels.append(curr_pixel)
                    curr_pixel = [curr_pixel[0]-1, curr_pixel[1]+1]

                # Checks left pixel.
                elif gray_image.item(curr_pixel[1], curr_pixel[0]-1) >= 128 and \
                                [curr_pixel[0]-1, curr_pixel[1]] not in passed_pixels and \
                                [curr_pixel[0]-1, curr_pixel[1]] not in mistaken_pixels:
                    passed_pixels.append(curr_pixel)
                    curr_pixel = [curr_pixel[0]-1, curr_pixel[1]]

                # Miss correction.
                else:
                    mistaken_pixels.append(curr_pixel)
                    curr_pixel = passed_pixels[-1]
                    del passed_pixels[-1]

        return passed_pixels


    def extract_tear(self, preprocessed_image, left_end, right_end):
        """
        紙片の破れ目部分の輪郭を抽出する

        Parameters
        ----------
        preprocessed_image : numpy.ndarray
            前処理後の画像。画像の色空間はBGR。
        left_end : list
            紙片の破れ目の左端の点の座標。1次元リスト。
        right_end : list
            紙片の破れ目の右端の点の座標。1次元リスト。

        Returns
        -------
        tear_coordinates : list
            紙片の破れ目の輪郭を構成する点群の座標群。2次元リスト。
        edge_detected_image : numpy.ndarray
            エッジ検出後の画像。画像の色空間はBGR。
        """
        image               = preprocessed_image.copy()
        edge_detected_image = self.detect_edge_by_canny_method(image)

        white_pixel_coordinates    = self.extract_white_pixel_coordinates(edge_detected_image)
        closest_pixel_to_left_end  = self.find_closest_pixel_to_end_of_tear(white_pixel_coordinates, left_end)
        closest_pixel_to_right_end = self.find_closest_pixel_to_end_of_tear(white_pixel_coordinates, right_end)

        tear_coordinates = self.chase_white_pixels(edge_detected_image, closest_pixel_to_left_end, closest_pixel_to_right_end)

        if self.DEBUG_FLAG:
            # canny_img = np.zeros(image.shape)
            # self.ipm.draw_circles(canny_img, white_pixel_coordinates, 3, (0,0,255))
            # cv2.imwrite('canny_red.jpg', canny_img)
            self.ipm.draw_circles(image, tear_coordinates, 5, (0,0,255))
            cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_tear_extracted.jpg', image)
            self.ipm.IMG_SAVE_CNT+=1

        return tear_coordinates, edge_detected_image
