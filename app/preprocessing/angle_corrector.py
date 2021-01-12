#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Shion Tominaga'
__copyright__ = 'Copyright (c) 2020 Miyata Lab.'

# Related third party imports.
import cv2
import numpy as np


class AngleCorrector:
    def __init__(self, ipm):
        self.ipm = ipm
        self.DEBUG_FLAG = self.ipm.get_debug_flag_status()


    # 膨張処理を行う関数
    def dilation(self, gray_img):
        kernel     = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
        result_img = cv2.dilate(gray_img, kernel, iterations=15)
        return result_img


    # グレー画像中から白領域の輪郭を探す関数
    def find_contour(self, gray_img):
        ret, thresh = cv2.threshold(gray_img, 127, 255, 0)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnt = max(contours, key=lambda x: cv2.contourArea(x)) # 最大面積の白領域輪郭
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt,True), True)
        return approx


    # 白領域の輪郭の座標群から左辺の上下端，右辺の上下端の座標を抽出する関数
    def extract_4points(self, approx):
        approx = approx.reshape([-1, 2]) # 配列の余分な括弧を削除
        approx = approx[np.argsort(approx[:, 0])] # 0列目を基準に行を降順ソート
        l_pts = approx[:2]
        r_pts = approx[-2:]
        ltp, lbp = l_pts[np.argsort(l_pts[:, 1])] # y座標で降順ソート
        rtp, rbp = r_pts[np.argsort(r_pts[:, 1])] # y座標で降順ソート
        return ltp, lbp, rtp, rbp


    # 2点の座標から傾きと切片を求める関数
    def calc_slope_intercept(self, ndarray1, ndarray2):
        x1, y1 = ndarray1.flatten()
        x2, y2 = ndarray2.flatten()
        if x1 - x2 == 0:
            x1 += 0.00000001
        slope = (y1 - y2) / (x1 - x2)
        intercept = y1 - slope * x1
        return (slope, intercept)


    # 2点を通る直線における画像の上端と下端での座標を求める関数
    def calc_extension_points(self, ndarray1, ndarray2):
        points = np.empty((0, 2)) # 2列の空numpy配列を作成
        ys = [0, self.ipm.get_image_height()] # 画像の上端と下端のy座標
        slope, intercept = self.calc_slope_intercept(ndarray1, ndarray2)
        for y in ys:
            x = int((y - intercept) / slope)
            points = np.append(points, np.array([[x, y]]), axis=0)
        return points


    # y=ax+b と y=cx+d の2直線の交点の座標を求める関数
    def calc_cross_point(self, a, b, c, d):
        x = int((d - b) / (a - c))
        y = int((a * d - b * c) / (a - c))
        return np.array([x, y])


    # 適切に射影変換を行うための4点の座標を求める関数
    def calc_projective_transformation_points(self, approx, ltp, lbp, rtp, rbp):
        approx = approx.reshape([-1, 2])          # 配列の余分な括弧を削除
        approx = approx[np.argsort(approx[:, 1])] # 0列目を基準に行を降順ソート
        app_min_y = approx[0]

        b_slope, b_intercept = self.calc_slope_intercept(lbp, rbp)
        l_slope, l_intercept = self.calc_slope_intercept(ltp, lbp)
        r_slope, r_intercept = self.calc_slope_intercept(rtp, rbp)
        t_slope = b_slope * -1
        t_intercept = app_min_y[1] + b_slope * app_min_y[0]

        l_cross_point = self.calc_cross_point(t_slope, t_intercept, l_slope, l_intercept)
        r_cross_point = self.calc_cross_point(t_slope, t_intercept, r_slope, r_intercept)
        pt_points = np.array([l_cross_point, r_cross_point, lbp, rbp])
        return pt_points


    # 射影変換を行う関数
    def projective_transformation(self, img, points):
        points_w_sorted = points[np.argsort(points[:, 0])] # 0列目を基準に行を降順ソート
        points_h_sorted = points[np.argsort(points[:, 1])] # 1列目を基準に行を降順ソート
        left_end   = points_w_sorted[1][0]
        right_end  = points_w_sorted[-2][0]
        top_end    = points_h_sorted[1][1]
        bottom_end = points_h_sorted[-2][1]
        p_before = np.float32(points)
        p_after  = np.float32([[left_end,top_end], [right_end,top_end], [left_end,bottom_end], [right_end,bottom_end]])
        M = cv2.getPerspectiveTransform(p_before, p_after)
        pt_img = cv2.warpPerspective(img, M, (self.ipm.get_image_width(), self.ipm.get_image_height()))
        return pt_img
        # w = self.ipm.get_image_width()
        # h = self.ipm.get_image_height()
        # p_before = np.float32(points)
        # p_after  = np.float32([[0,0], [w,0], [0,h], [w,h]])
        # M = cv2.getPerspectiveTransform(p_before, p_after)
        # pt_img = cv2.warpPerspective(img, M, (w, h))
        # return pt_img


    def correct_angle(self, src_image):
        b_image = src_image.copy()
        b_gray_img = cv2.cvtColor(b_image, cv2.COLOR_BGR2GRAY)
        dil_img  = self.dilation(b_gray_img)
        b_approx = self.find_contour(dil_img)
        ltp, lbp, rtp, rbp = self.extract_4points(b_approx)
        pt_points = self.calc_projective_transformation_points(b_approx, ltp, lbp, rtp, rbp)

        angle_corrected_image = self.projective_transformation(b_image, pt_points)

        # Find left/right end point.
        # a_image = angle_corrected_image.copy()
        # a_gray_img = cv2.cvtColor(a_image, cv2.COLOR_BGR2GRAY)
        # a_approx = self.find_contour(a_gray_img)
        # left_end, _, right_end, _ = self.extract_4points(a_approx)

        #---------#
        # Drawing #
        #---------#
        if self.DEBUG_FLAG:
            # Draw extention points.
            ex_points_left  = self.calc_extension_points(ltp, lbp)
            ex_points_right = self.calc_extension_points(rtp, rbp)
            ex_points = np.concatenate([ex_points_left, ex_points_right])[[0,2,1,3], :]
            for point in ex_points:
                cv2.circle(b_image, tuple(np.int32(point)), 20, (0,255,0), -1)
            # Draw extended line.
            cv2.line(b_image, tuple(np.int32(ex_points[0])), tuple(np.int32(ex_points[2])),(0,255,0), 8)
            cv2.line(b_image, tuple(np.int32(ex_points[1])), tuple(np.int32(ex_points[3])),(0,255,0), 8)

            # Draw ltp, lbp, rtp, rbp.
            cv2.circle(b_image, tuple(np.int32(ltp)), 15, (255,0,128), -1)
            cv2.circle(b_image, tuple(np.int32(lbp)), 15, (255,0,128), -1)
            cv2.circle(b_image, tuple(np.int32(rtp)), 15, (255,0,128), -1)
            cv2.circle(b_image, tuple(np.int32(rbp)), 15, (255,0,128), -1)

            # Draw left_end, right_end.
            # cv2.circle(a_image, tuple(np.int32(left_end)),  10, (0,0,255), -1)
            # cv2.circle(a_image, tuple(np.int32(right_end)), 10, (0,0,255), -1)

            # 射影変換元の4点とそれを結ぶ線分を描画
            for point in pt_points:
                cv2.circle(b_image, tuple(np.int32(point)), 10, (0,128,255), -1)
            cv2.line(b_image, tuple(pt_points[0]), tuple(pt_points[1]),(0,128,255), 3)
            cv2.line(b_image, tuple(pt_points[0]), tuple(pt_points[2]),(0,128,255), 3)
            cv2.line(b_image, tuple(pt_points[3]), tuple(pt_points[1]),(0,128,255), 3)
            cv2.line(b_image, tuple(pt_points[3]), tuple(pt_points[2]),(0,128,255), 3)

            cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_angle_corrected_01.jpg', b_image)
            self.ipm.IMG_SAVE_CNT += 1
            cv2.imwrite(str(self.ipm.IMG_SAVE_CNT).zfill(2) + '_angle_corrected_02.jpg', angle_corrected_image)
            self.ipm.IMG_SAVE_CNT += 1

        return angle_corrected_image, ltp, rtp
