#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Shion Tominaga'
__copyright__ = 'Copyright (c) 2019-2020 Miyata Lab.'

# Standard library imports.
import pathlib
import sys

# Related third party imports.
import cv2
import numpy as np
# from pymatting import alpha
from tensorflow.keras.preprocessing.image import img_to_array

# Local application/library specific imports.
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir))
import morphology


class ImageBinarizer():
    def __init__(self, ipm, ss_estimator):
        self.ipm = ipm
        self.morph = morphology.Morphology()
        self.DEBUG_FLAG = self.ipm.get_debug_flag_status()
        self.IMAGE_WIDTH  = self.ipm.get_image_width()
        self.IMAGE_HEIGHT = self.ipm.get_image_height()

        # binarize (semantic segmentation)
        self.ss_estimator = ss_estimator
        self.est_input_size = (512, 512)

        # denoise
        self.CLOSE_DENOISE_KERNEL = np.ones((4, 4), np.uint8)
        self.OPEN_DENOISE_KERNEL  = np.ones((4, 4), np.uint8)


    def binarize(self, src_image, mode='semantic_segmentation'):
        """
        2値化処理

        Parameters
        ----------
        src_image : numpy.ndarray
            元画像。画像の色空間はBGR。

        Returns
        -------
        binarized_image : numpy.ndarray
            2値化後の画像。画像の色空間はBGR。
        """
        image = src_image.copy()

        if mode == 'basic_hsv':
            # 特定のHSV値の範囲に基づいた2値化
            # LOWER_HSV = np.array([  0,  0, 150], np.uint8) # 指定するHSV値の下限
            # UPPER_HSV = np.array([180, 45, 255], np.uint8) # 指定するHSV値の上限
            LOWER_HSV = np.array([  0,  0, 165], np.uint8) # 指定するHSV値の下限
            UPPER_HSV = np.array([180, 45, 255], np.uint8) # 指定するHSV値の上限

            image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            binarized_image = cv2.inRange(image, LOWER_HSV, UPPER_HSV)
            binarized_image = cv2.cvtColor(binarized_image, cv2.COLOR_GRAY2BGR)

            if self.DEBUG_FLAG:
                cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_hsv_binarized.jpg', binarized_image)
                self.ipm.IMG_SAVE_CNT += 1

        elif mode == 'semantic_segmentation':
            # Semantic Segmentation による2値化
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, self.est_input_size) # 推定モデルに入力するためリサイズ
            image = img_to_array(image) / 255 # 255で割って0〜1の範囲で正規化する
            image = np.expand_dims(image, axis=0)

            # 推定器を準備
            estimator = self.ss_estimator

            # 推定の実行
            pred = estimator.predict(image).squeeze()

            # 推定結果からマスク（2値化）画像を生成
            binarized_image = np.zeros(self.est_input_size, dtype=np.uint8)
            for row in range(len(pred)):
                for col in range(len(pred[0])):
                    if pred[row][col][0] < pred[row][col][1]:
                        binarized_image[row][col] = 255

            binarized_image = cv2.resize(binarized_image, (self.IMAGE_WIDTH, self.IMAGE_HEIGHT)) # 元の画像サイズにリサイズ
            binarized_image = cv2.cvtColor(binarized_image, cv2.COLOR_GRAY2BGR) # 画像の色空間をBGRに変換

            if self.DEBUG_FLAG:
                cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_ss_binarized.jpg', binarized_image)
                self.ipm.IMG_SAVE_CNT += 1

        return binarized_image


    def denoise(self, src_bin_image, bin_th=64, close_param=10):
        """
        2値化とモルフォロジー変換によるCLOSING（膨張からの収縮）処理を用いたノイズ除去

        Parameters
        ----------
        src_bin_image : numpy.ndarray
            元画像。白黒に2値化されている必要がある。画像の色空間はBGR。

        Returns
        -------
        denoised_image : numpy.ndarray
            ノイズ除去後の画像。画像の色空間はBGR。
        """
        image = src_bin_image.copy()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # グレースケール値が 64 未満の画素は 0 に，それ以外の画素は 255 にする。
        # image = np.where(image < bin_th, 0, 255).astype('uint8')
        # if self.DEBUG_FLAG:
        #     cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_re-binarization_denoised.jpg', image)
        #     self.ipm.IMG_SAVE_CNT += 1

        # CLOSING
        image = self.morph.closing(image, (close_param,close_param))
        if self.DEBUG_FLAG:
            cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_close-denoised.jpg', image)
            self.ipm.IMG_SAVE_CNT += 1

        denoised_image = image
        denoised_image = cv2.cvtColor(denoised_image, cv2.COLOR_GRAY2BGR)

        return denoised_image


    def generateTrimap(self, src_bin_image, param=20):
        bin_img  = src_bin_image.copy()
        gradient = self.morph.gradient(bin_img, (param,param))
        gray     = np.where(gradient == 255, 128, 255).astype(np.uint8)
        trimap   = cv2.bitwise_and(bin_img, gray)
        # trimap = cv2.resize(trimap, (3024,4032), interpolation=cv2.INTER_NEAREST)

        if self.DEBUG_FLAG:
            cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_trimap.jpg', trimap)
            self.ipm.IMG_SAVE_CNT += 1

        return trimap


    # def matting(self, src_image, src_bin_image, trimap_param=20):
    #     image     = cv2.cvtColor(src_image.copy(), cv2.COLOR_BGR2RGB)
    #     bin_image = cv2.cvtColor(src_bin_image.copy(), cv2.COLOR_BGR2GRAY)
    #     trimap    = self.generateTrimap(bin_image, param=trimap_param)

    #     image  = np.array(image) / 255.0
    #     trimap = np.array(trimap) / 255.0

    #     matted = np.clip(alpha.estimate_alpha_knn(image, trimap) * 255, 0, 255).astype('uint8')

    #     if self.DEBUG_FLAG:
    #         cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_matted.jpg', matted)
    #         self.ipm.IMG_SAVE_CNT += 1

    #     matted = cv2.cvtColor(matted, cv2.COLOR_GRAY2BGR)

    #     return matted
