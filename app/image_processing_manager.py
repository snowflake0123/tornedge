#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = 'Shion Tominaga'
__copyright__ = 'Copyright (c) 2019-2020 Miyata Lab.'


# Standard library imports.
import argparse
import logging
import os
import pathlib
import sys

# Related third party imports.
import cv2
import segmentation_models as sm
from tensorflow.keras.models import load_model

# Local application/library specific imports.
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir))
import feature_extraction.angle_feature_extractor as angle_feature_extractor
import feature_extraction.height_feature_extractor as height_feature_extractor
import feature_extraction.position_feature_extractor as position_feature_extractor
import feature_extraction.shape_feature_extractor as shape_feature_extractor
import preprocessing.angle_corrector as angle_corrector
import preprocessing.both_ends_of_tear_finder as both_ends_of_tear_finder
import preprocessing.image_binarizer as image_binarizer
import preprocessing.image_filter as image_filter
import preprocessing.piece_of_paper_part_extractor as piece_of_paper_part_extractor
import preprocessing.tear_extractor as tear_extractor


logger = logging.getLogger(__name__)


AVAILABLE_MAX_IMAGE_SIZE = (1080, 1440)
# AVAILABLE_MAX_IMAGE_SIZE = (2160, 2880)
# AVAILABLE_MAX_IMAGE_SIZE = (3024, 4032)


class ImageProcessingManager():
    # Preload the estimator for binarization only once here.
    ss_estimator = load_model(os.path.join(current_dir, 'preprocessing/ss_model.h5'), custom_objects={
                              'binary_focal_loss_plus_dice_loss': sm.losses.binary_focal_dice_loss,
                              'iou_score': sm.metrics.IOUScore(),
                              'f1-score': sm.metrics.FScore()})

    def __init__(self, image, debug=False):
        self.DEBUG_FLAG = debug

        self.IMAGE_WIDTH = image.shape[1]
        self.IMAGE_HEIGHT = image.shape[0]
        self.DRAWING_RATE = int(
            self.IMAGE_WIDTH / AVAILABLE_MAX_IMAGE_SIZE[0])  # 円・直線などの図形の描画比率
        self.IMG_SAVE_CNT = 0

        self.img_filter = image_filter.ImageFilter(self)
        self.img_binarizer = image_binarizer.ImageBinarizer(
            self, self.ss_estimator)
        self.angle_corrector = angle_corrector.AngleCorrector(self)
        self.p_o_p_part_extractor = piece_of_paper_part_extractor.PieceOfPaperPartExtractor(
            self)
        self.both_ends_of_tear_finder = both_ends_of_tear_finder.BothEndsOfTearFinder(
            self)
        self.tear_extractor = tear_extractor.TearExtractor(self)

        self.fs_extractor = shape_feature_extractor.ShapeFeatureExtractor(self)
        self.fh_extractor = height_feature_extractor.HeightFeatureExtractor(
            self)
        self.fa_extractor = angle_feature_extractor.AngleFeatureExtractor(self)
        self.fp_extractor = position_feature_extractor.PositionFeatureExtractor(
            self)

    def get_debug_flag_status(self):
        """
        self.DEBUG_FLAGの値を返す

        Parameters
        ----------
        (None)

        Returns
        -------
        self.DEBUG_FLAG : boolean
            デバッグを行うかどうかのフラグ。
        """
        return self.DEBUG_FLAG

    def get_image_width(self):
        """
        self.IMAGE_WIDTHの値を返す

        Parameters
        ----------
        (None)

        Returns
        -------
        self.IMAGE_WIDTH : int
            入力画像の幅（px）。
        """
        return self.IMAGE_WIDTH

    def get_image_height(self):
        """
        self.IMAGE_HEIGHTの値を返す

        Parameters
        ----------
        (None)

        Returns
        -------
        self.IMAGE_HEIGHT : int
            入力画像の高さ（px）。
        """
        return self.IMAGE_HEIGHT

    def do_preprocessing(self, src_image):
        """
        紙片画像 image に前処理を施し，特徴量の抽出に必要な要素を取り出す

        Parameters
        ----------
        image : numpy.ndarray
            紙片画像。画像の色空間はBGR。

        Returns
        -------
        tear_coordinates : list
            紙片の破れ目の座標群。2次元リスト。
            格納順は左端から右端。
        preprocessed_image : numpy.ndarray
            前処理後の画像。画像の色空間はBGR。
        """
        image = src_image.copy()

        if self.DEBUG_FLAG:
            cv2.imwrite(str(self.IMG_SAVE_CNT).zfill(
                2) + '_original.jpg', image)
            self.IMG_SAVE_CNT += 1

        image = self.img_filter.do_smoothing(image)
        image = self.img_filter.reduct_color(image)
        basic_bin_image = self.img_binarizer.binarize(image, mode='basic_hsv')
        bin_image = self.img_binarizer.binarize(
            image, mode='semantic_segmentation')
        bin_image = self.p_o_p_part_extractor.extract_largest_white_area(
            bin_image)
        # bin_image = self.img_binarizer.matting(src_image, bin_image, trimap_param=20)
        bin_image, left_end, right_end = self.angle_corrector.correct_angle(
            bin_image)
        # bin_image = self.img_binarizer.denoise(bin_image, bin_th=64, close_param=5)
        # bin_image = self.p_o_p_part_extractor.remove_char(bin_image)
        preprocessed_image = bin_image

        # left_end, right_end = self.both_ends_of_tear_finder.detect_both_ends_of_tear(preprocessed_image)
        tear_coordinates, edge_detected_image = self.tear_extractor.extract_tear(
            preprocessed_image, left_end, right_end)

        return tear_coordinates, edge_detected_image, preprocessed_image

    def do_feature_extraction(self, tear_coordinates, edge_detected_image, image_for_drawing):
        """
        前処理によって得られた要素を用いて，各種特徴量の抽出処理を行う

        Parameters
        ----------
        tear_coordinates : list
            紙片の破れ目の座標群。2次元リスト。
            格納順は左端から右端。
        edge_detected_image : numpy.ndarray
            エッジ検出後の画像。画像の色空間はBGR。
        image_for_drawing : numpy.ndarray
            特徴量抽出時に利用した要素を描画し，確認するための画像。画像の色空間はBGR。

        Returns
        -------
        features : dict
            各種特徴量の名称を key ，各種特徴量の値を value とする辞書。
        """
        shape_feature_x, shape_feature_y = self.fs_extractor.extract_shape_feature(
            tear_coordinates, image_for_drawing, skip=50)
        height_feature = self.fh_extractor.extract_height_feature(
            tear_coordinates, image_for_drawing)
        angle_feature = self.fa_extractor.extract_angle_feature(
            tear_coordinates, edge_detected_image, image_for_drawing)
        position_feature = self.fp_extractor.extract_position_feature(
            tear_coordinates, image_for_drawing)

        features = {}
        features['shape_x'] = shape_feature_x
        features['shape_y'] = shape_feature_y
        features['height'] = height_feature
        features['angle'] = angle_feature
        features['position'] = position_feature

        # --- For debug only. ---
        # fa_image = image_for_drawing.copy()
        # if self.DEBUG_FLAG:
        #     self.draw_circles(fa_image, tear_coordinates[int(len(tear_coordinates) / 2)], 5, (0,0,255))
        #     cv2.imwrite(str(self.IMG_SAVE_CNT).zfill(2) + '_angle_feature.jpg', fa_image)
        #     self.IMG_SAVE_CNT += 1
        # --- For debug only. ---

        return features

    def extract_features(self, image):
        """
        紙片画像に前処理を施し，特徴量を抽出する

        Parameters
        ----------
        image : numpy.ndarray
            特徴量を抽出する紙片画像。画像の色空間はBGR。

        Returns
        -------
        features : dict
            各種特徴量の名称を key ，各種特徴量の値を value とする辞書。
        """
        tear_coordinates, edge_detected_image, preprocessed_image = self.do_preprocessing(
            image)
        features = self.do_feature_extraction(
            tear_coordinates, edge_detected_image, preprocessed_image)
        return features

    def draw_lines(self, image, lines, color, weight):
        """
        image の任意指定箇所に直線を描画する。破壊的メソッド。

        Parameters
        ----------
        image : numpy.ndarray
            直線を描画する画像。画像の色空間はBGR。
        lines : list
            描画する直線群。
        color : tuple
            描画する直線の色。
            Blue, Green, Red の順で，BGR値を (255,255,255) のように指定する。
        weight : int
            描画する直線の太さ。1以上で指定する。

        Returns
        -------
        (None)
        """
        for line in lines:
            rho, theta = line[0]
            end_points_of_line = self.both_ends_of_tear_finder.get_end_points_of_line(
                rho, theta)
            end_point1, end_point2 = end_points_of_line
            cv2.line(image, end_point1, end_point2,
                     color, weight * self.DRAWING_RATE)

    def draw_circles(self, image, circles, size, color):
        """
        image の任意指定箇所に円を描画する。破壊的メソッド。

        Parameters
        ----------
        image : numpy.ndarray
            円を描画する画像。画像の色空間はBGR。
        circles : tuple/list
            描画する円の座標。
            ((x1,y1),(x2,y2))のように2次元tuple/listで渡せば，複数個描画することも可能。
        size : int
            描画する円のサイズ。1以上で指定する。
        color : tuple
            描画する円の塗りつぶしの色。
            Blue, Green, Red の順で，BGR値を (255,255,255) のように指定する。

        Returns
        -------
        (None)
        """
        if type(circles[0]) is list:
            circles = [tuple(circle) for circle in circles]
            circles = tuple(circles)
        elif type(circles) is list:
            circles = (tuple(circles),)
        elif type(circles) is tuple and type(circles[0]) is not tuple:
            circles = (circles,)

        for circle in circles:
            cv2.circle(image, circle, size * self.DRAWING_RATE, color, -1)


if __name__ == '__main__':
    #--------------------------------#
    # Loads command line parameters. #
    #--------------------------------#
    parser = argparse.ArgumentParser(
        description='The program of feature extraction from a piece of paper image.')
    parser.add_argument('-i', '--image',
                        default='image.jpg',
                        help='Image file name')
    args = parser.parse_args()
    imagename = args.image

    #----------------------#
    # Opens an image file. #
    #----------------------#
    try:
        image = cv2.imread(imagename)
        image = cv2.resize(image, AVAILABLE_MAX_IMAGE_SIZE)
    except:
        logger.error('[%s] FileOpenError: ' + imagename +
                     ' could not be found.' % sys._getframe().f_code.co_name)
        sys.exit()

    #------------------------#
    # Does Image Processing. #
    #------------------------#
    ipm = ImageProcessingManager(image, debug=True)
    features = ipm.extract_features(image)

    #-----------------#
    # Prints results. #
    #-----------------#
    for key, value in features.items():
        print(key, '=', value)
