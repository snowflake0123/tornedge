#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Shion Tominaga'
__copyright__ = 'Copyright (c) 2019-2020 Miyata Lab.'

# Related third party imports.
import cv2


class ShapeFeatureExtractor():
    def __init__(self, ipm):
        self.ipm = ipm
        self.DEBUG_FLAG = self.ipm.get_debug_flag_status()


    def extract_pixels_every_fixed_number(self, pixel_coordinates, fixed_num):
        """
        fsから一定ピクセルごとにピクセルを抽出する

        Parameters
        ----------
        pixel_coordinates : list
            破れ目を構成する点の座標群。
            [[x_1,y_1], [x_2,y_2], ..., [x_n,y_n]] のような2次元リスト。
        fixed_num : int
            配列から何ピクセルごとに抽出するのかの値。

        Returns
        -------
        extracted_pixel_coordinates : list
            fsから一定ピクセルごとにピクセルを抽出した結果。
            [a_1, a_2, ..., a_n] のような1次元リスト。
        """
        extracted_pixel_coordinates = []
        pixel_extract_interval      = fixed_num
        skipped_pixel               = 0

        for i in range(len(pixel_coordinates)):
            skipped_pixel += 1
            if i % pixel_extract_interval == 0:
                extracted_pixel_coordinates.append(pixel_coordinates[i])
                skipped_pixel = 0

        if skipped_pixel != 0:
            extracted_pixel_coordinates.append(pixel_coordinates[-1])

        return extracted_pixel_coordinates


    def extract_shape_feature(self, tear_coordinates, image_for_drawing, skip=50):
        """
        fs(Shape Feature)を抽出する

        Parameters
        ----------
        tear_coordinates : list
            破れ目を構成する点の座標群。
            [[x_1,y_1], [x_2,y_2], ..., [x_n,y_n]] のような2次元リスト。
        image_for_drawing : numpy.ndarray
            描画用の画像。画像の色空間はBGR。

        Returns
        -------
        fs_x : list
            x座標についてのfsの抽出結果。
            [dx_1, dx_2, ..., dx_n] のような1次元リスト。
        fs_y : list
            y座標についてのfsの抽出結果。
            [dy_1, dy_2, ..., dy_n] のような1次元リスト。
        """
        image = image_for_drawing.copy()

        # extracted_tear_coordinates = self.extract_pixels_every_fixed_number(tear_coordinates, skip)
        fs_x = []
        fs_y = []

        # if len(extracted_tear_coordinates) <= 1:
        #     fs_x.append(0)
        #     fs_y.append(0)
        # else:
        #     for i in range(len(extracted_tear_coordinates)-1):
        #         fs_x.append(extracted_tear_coordinates[i][0] - extracted_tear_coordinates[i+1][0])
        #         fs_y.append(extracted_tear_coordinates[i][1] - extracted_tear_coordinates[i+1][1])

        for i in range(len(tear_coordinates)):
            fs_x.append(tear_coordinates[i][0])
            fs_y.append(tear_coordinates[i][1])

        if self.DEBUG_FLAG:
            self.ipm.draw_circles(image, tear_coordinates, 10, (0,0,255))
            cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_shape_feature.jpg', image)
            self.ipm.IMG_SAVE_CNT+=1
        # if self.DEBUG_FLAG:
        #     self.ipm.draw_circles(image, extracted_tear_coordinates, 10, (0,0,255))
        #     cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_shape_feature.jpg', image)
        #     self.ipm.IMG_SAVE_CNT+=1

        return fs_x, fs_y
