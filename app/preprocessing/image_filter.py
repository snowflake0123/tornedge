#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Shion Tominaga'
__copyright__ = 'Copyright (c) 2019 Miyata Lab.'


# Related third party imports.
import cv2


class ImageFilter():
    def __init__(self, ipm):
        self.ipm = ipm
        self.DEBUG_FLAG = self.ipm.get_debug_flag_status()


    def do_smoothing(self, src_image):
        """
        ガウシアンフィルタによる平滑化

        Parameters
        ----------
        src_image : numpy.ndarray
            元画像。画像の色空間はBGR。

        Returns
        -------
        smoothed_image : numpy.ndarray
            平滑化後の画像。画像の色空間はBGR。
        """
        # Parameters.
        KERNEL_SIZE = (15, 15) # カーネルサイズ。平均化する画素の周囲の大きさ。
        SIGMA_X     = 1        # x軸方向の標準偏差。

        image = src_image.copy()
        smoothed_image = cv2.GaussianBlur(image, KERNEL_SIZE, SIGMA_X)

        if self.DEBUG_FLAG:
            cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_gaussian_blurred.jpg', smoothed_image)
            self.ipm.IMG_SAVE_CNT += 1

        return smoothed_image


    def reduct_color(self, src_image):
        """
        Mean Shift法を用いた領域分割による減色処理

        Parameters
        ----------
        src_image : numpy.ndarray
            元画像。画像の色空間はBGR。

        Returns
        -------
        color_reducted_image : numpy.ndarray
            減色処理後の画像。画像の色空間はBGR。
        """
        # Parameters.
        SP = 5  # 空間窓の半径。
        SR = 20 # 色空間窓の半径。

        image = src_image.copy()
        color_reducted_image = cv2.pyrMeanShiftFiltering(image, SP, SR)

        if self.DEBUG_FLAG:
            cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_color_reducted.jpg', color_reducted_image)
            self.ipm.IMG_SAVE_CNT += 1

        return color_reducted_image
