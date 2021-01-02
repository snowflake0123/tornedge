#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Shion Tominaga, Kenro Go and Akihiro Miyata'
__copyright__ = 'Copyright (c) 2018-2020 Miyata Lab.'


# Standard library imports.
import logging

# Related third party imports.
from fastdtw import fastdtw


logger = logging.getLogger(__name__)


class MatchingEngine():
    def __init__(self, weight_fs, digit):
        self.weight_fs = weight_fs
        self.digit     = digit


    def normalization(self, data):
        min_val = min(data)
        max_val = max(data)
        denominator = float(max_val - min_val)
        if denominator != 0:
            for i in range(len(data)):
                data[i] = round(float(data[i] - min_val) / denominator, self.digit)
        else:
            for i in range(len(data)):
                data[i] = 0.0


    def is_fh_matched(self, input_fh, candidates_fh):
        fh_threshold = 0.2
        if abs(input_fh - candidates_fh) < fh_threshold:
            return True
        return False


    def is_fa_matched(self, input_fa, candidates_fa):
        fa_threshold = 10.0
        if abs(input_fa - candidates_fa) < fa_threshold:
            return True
        return False


    def is_fp_matched(self, input_fp, candidates_fp):
        for i in range(len(input_fp)):
            if input_fp[i] != candidates_fp[i]: return False
        return True


    def reverse_list(self, org_list):
        reversed_list = org_list.copy()
        reversed_list.reverse()
        return reversed_list


    def multiply_minus(self, org_list):
        minus_list = org_list.copy()
        minus_list = [i * -1 for i in minus_list]
        return minus_list


    def derivative(self, arr):
        if len(arr) == 0:
            raise Exception("Incorrect input. Must be an array with more than 1 element.")
        d_arr = []
        for i in range(1, len(arr) - 1):
            d_arr.append(((arr[i] - arr[i - 1]) + ((arr[i + 1] - arr[i - 1]) / 2)) / 2)
        return d_arr


    def match(self, features, candidates, use_fh=True, use_fa=False, use_fp=False):
        # Calculates feature similarities.
        logger.info('use_fh: {}'.format(use_fh))
        print('Use Fh: {}'.format(use_fh))
        logger.info('use_fa: {}'.format(use_fa))
        print('Use Fa: {}'.format(use_fa))
        logger.info('use_fp: {}'.format(use_fp))
        print('Use Fp: {}'.format(use_fp))

        ids, fs_similarity = [], []
        for candidate_id, candidate_features in candidates.items():
            input_fh = features['height']
            candidates_fh = float(candidate_features['height']) if type(candidate_features['height']) is str else candidate_features['height']
            if use_fh and not self.is_fh_matched(input_fh, candidates_fh):
                continue

            input_fa = features['angle']
            candidates_fa = float(candidate_features['angle']) if type(candidate_features['angle']) is str else candidate_features['angle']
            if use_fa and not self.is_fa_matched(input_fa, candidates_fa):
                continue

            input_fp = features['position']
            candidates_fp = list(map(float, candidate_features['position'].split(','))) if type(candidate_features['position']) is str else candidate_features['position']
            if use_fp and not self.is_fp_matched(input_fp, candidates_fp):
                continue

            ids.append(candidate_id)
            input_fs_x      = self.reverse_list(features['shape_x'])
            input_fs_y      = self.multiply_minus(self.reverse_list(features['shape_y']))
            candidates_fs_x = list(map(float, candidate_features['shape_x'].split(','))) if type(candidate_features['shape_x']) is str else candidate_features['shape_x']
            candidates_fs_y = list(map(float, candidate_features['shape_y'].split(','))) if type(candidate_features['shape_y']) is str else candidate_features['shape_y']

            # Calibration.
            input_fs_x      = [i - input_fs_x[0] for i in input_fs_x]
            input_fs_y      = [i - input_fs_y[0] for i in input_fs_y]
            candidates_fs_x = [i - candidates_fs_x[0] for i in candidates_fs_x]
            candidates_fs_y = [i - candidates_fs_y[0] for i in candidates_fs_y]

            # Derivative DTW.
            input_fs_x_d      = self.derivative(input_fs_x)
            input_fs_y_d      = self.derivative(input_fs_y)
            candidates_fs_x_d = self.derivative(candidates_fs_x)
            candidates_fs_y_d = self.derivative(candidates_fs_y)
            # fs_x_similarity = 1.0 / fastdtw(input_fs_x, candidates_fs_x)[0]
            # fs_y_similarity = 1.0 / fastdtw(input_fs_y, candidates_fs_y)[0]
            fs_x_similarity = 1.0 / fastdtw(input_fs_x_d, candidates_fs_x_d)[0]
            fs_y_similarity = 1.0 / fastdtw(input_fs_y_d, candidates_fs_y_d)[0]

            # Weights for fs.
            FS_X_WEIGHT = 1
            FS_Y_WEIGHT = 1

            fs_similarity.append(fs_x_similarity * FS_X_WEIGHT + fs_y_similarity * FS_Y_WEIGHT)
            print('candidate ID    =', candidate_id)
            print('fs_x_similarity =', fs_x_similarity * FS_X_WEIGHT)
            print('fs_y_similarity =', fs_y_similarity * FS_Y_WEIGHT)
            print('')

        logger.info('shape_scores = {}'.format(fs_similarity))

        if fs_similarity == []:
            max_id    = None
            max_score = None
            print('[WARNING] No match was found.')
        else:
            # Normalizes score similarities (range: 0-1).
            self.normalization(fs_similarity)
            logger.info('shape_norm_scores = {}'.format(fs_similarity))

            # Finds the ID of which score is the highest.
            max_id    = ids[0]
            max_score = 0.0
            for i in range(len(ids)):
                score = self.weight_fs * fs_similarity[i]
                print('ID:', ids[i])
                print('Score =', score)
                if max_score < score:
                    max_id    = ids[i]
                    max_score = score
        print('')
        logger.info('max_id = {}, max_score = {}'.format(max_id, max_score))
        print('MAX ID = {}, MAX Score = {}'.format(max_id, max_score))

        return max_id
