#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Shion Tominaga'
__copyright__ = 'Copyright (c) 2020 Miyata Lab.'


# Standard library imports.
import datetime
import glob
import logging
import os
import pathlib
import pickle
import re
import sys

# Related third party imports.
import cv2
import numpy as np

# Local application/library specific imports.
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir))
sys.path.append('../')
import app.image_processing_manager as ipm
import app.engine as engine


logger = logging.getLogger(__name__)


MAX_IMAGE_SIZE = (1080, 1440)
# MAX_IMAGE_SIZE = (1440, 1920)

SRC_DIR     = './images'
SRC_SND_DIR = os.path.join(SRC_DIR, 'sender')
SRC_RCV_DIR = os.path.join(SRC_DIR, 'receiver')
DST_DIR     = './m_result'
LOG_FILE    = os.path.join(DST_DIR, 'out.log')


class MatchingExperimenter():
    def __init__(self, src_dir, src_snd_dir, src_rcv_dir, dst_dir, log_file):
        self.src_dir     = src_dir
        self.src_snd_dir = src_snd_dir
        self.src_rcv_dir = src_rcv_dir
        self.dst_dir     = dst_dir
        self.log_file    = log_file


    def extract_features(self, src_img):
        self.ipm = ipm.ImageProcessingManager(src_img, debug=False)
        features = self.ipm.extract_features(src_img)
        return features


    def extract_features_in_dir(self, src_dir):
        files   = glob.glob(os.path.join(src_dir, "*"))
        results = {}
        for file in files:
            print('Loads {}'.format(file))
            name  = os.path.splitext(os.path.basename(file))[0]
            image = cv2.imread(file)
            image = cv2.resize(image, MAX_IMAGE_SIZE)
            # try:
            #     features = self.extract_features(image)
            # except IndexError:
            #     results[name] = {'fe':}
            # else:
            #     results[name] = features
            features = self.extract_features(image)
            results[name] = features
        return results


    def calc_success_rate(self, matches, dst=sys.stdout):
        success = 0.0
        for a, b in matches.items():
            result = 'x'
            a = re.search('[0-9]+', a).group() if a is not None else None
            b = re.search('[0-9]+', b).group() if b is not None else None
            if a == b and a is not None and b is not None:
                result = 'o'
                success += 1.0
            print('{}-{}: {}'.format(a, b, result), file=dst)
        return success / len(matches) * 100


    def calc_both_success_rate(self, matches_a, matches_b):
        success = 0.0
        for key_a, val_a in matches_a.items():
            key_a = re.search('[0-9]+', key_a).group() if key_a is not None else None
            val_a = re.search('[0-9]+', val_a).group() if val_a is not None else None
            for key_b, val_b in matches_b.items():
                key_b = re.search('[0-9]+', key_b).group() if key_b is not None else None
                val_b = re.search('[0-9]+', val_b).group() if val_b is not None else None
                if key_a == key_b and val_a == val_b:
                    success += 1.0
        return success / len(matches_a) * 100


    # def print_ratio_features(self, fhs, dst=sys.stdout):
    #     for a, b in fhs.items():
    #         a = re.search('[0-9]+', a).group() if a is not None else None
    #         b = re.search('[0-9]+', b).group() if b is not None else None
    #         print('{}-{}: {}'.format(a, b, result), file=dst)


    def execute(self):
        self.matcher = engine.MatchingEngine(weight_fs=1.0, digit=3)
        if not os.path.isfile('senders.pickle') or not os.path.isfile('receivers.pickle'):
            print('Start extracting features...')
            senders   = self.extract_features_in_dir(SRC_SND_DIR)
            receivers = self.extract_features_in_dir(SRC_RCV_DIR)
            with open('senders.pickle', mode='wb') as f:
                pickle.dump(senders, f)
            with open('receivers.pickle', mode='wb') as f:
                pickle.dump(receivers, f)
        else:
            print('Loads features files...')
            with open('senders.pickle', mode='rb') as f:
                senders = pickle.load(f)
            with open('receivers.pickle', mode='rb') as f:
                receivers = pickle.load(f)

        print('Start matching...')
        # 各Sender紙片を全Receiver紙片に対してマッチングさせる。
        print('Sender-Receivers')
        s_matches = {}
        s_fhs = {}
        s_fms = {}
        # s_fas = {}
        for s_name, s_features in senders.items():
            matched_name = self.matcher.match(s_features, receivers, use_fh=True, use_fa=False, use_fp=False)
            s_matches[s_name] = matched_name

            s_top_x      = s_features['shape_x'][np.argmin(s_features['shape_y'])]
            s_bottom_x   = s_features['shape_x'][np.argmax(s_features['shape_y'])]
            s_top_y      = min(s_features['shape_y'])
            s_bottom_y   = max(s_features['shape_y'])
            s_leftend_x  = s_features['shape_x'][0]
            s_rightend_x = s_features['shape_x'][-1]
            s_leftend_y  = s_features['shape_y'][0]
            s_rightend_y = s_features['shape_y'][-1]
            s_middle_x   = s_features['shape_x'][int(len(s_features['shape_x']) / 2.0)]
            s_middle_y   = s_features['shape_y'][int(len(s_features['shape_y']) / 2.0)]
            s_width  = abs(s_leftend_x - s_rightend_x)
            s_fh_t_b = abs(s_top_y - s_bottom_y) / s_width
            s_fh_t_l = abs(s_top_y - s_leftend_y) / s_width
            s_fh_t_r = abs(s_top_y - s_rightend_y) / s_width
            s_fh_b_l = abs(s_bottom_y - s_leftend_y) / s_width
            s_fh_b_r = abs(s_bottom_y - s_rightend_y) / s_width
            s_fh_l_r = abs(s_leftend_y - s_rightend_y) / s_width

            r_top_x      = receivers[matched_name]['shape_x'][np.argmin(receivers[matched_name]['shape_y'])]
            r_bottom_x   = receivers[matched_name]['shape_x'][np.argmax(receivers[matched_name]['shape_y'])]
            r_top_y      = min(receivers[matched_name]['shape_y'])
            r_bottom_y   = max(receivers[matched_name]['shape_y'])
            r_leftend_x  = receivers[matched_name]['shape_x'][0]
            r_rightend_x = receivers[matched_name]['shape_x'][-1]
            r_leftend_y  = receivers[matched_name]['shape_y'][0]
            r_rightend_y = receivers[matched_name]['shape_y'][-1]
            r_middle_x   = receivers[matched_name]['shape_x'][int(len(receivers[matched_name]['shape_x']) / 2.0)]
            r_middle_y   = receivers[matched_name]['shape_y'][int(len(receivers[matched_name]['shape_y']) / 2.0)]
            r_width  = abs(r_leftend_x - r_rightend_x)
            r_fh_t_b = abs(r_top_y - r_bottom_y) / r_width
            r_fh_t_l = abs(r_top_y - r_leftend_y) / r_width
            r_fh_t_r = abs(r_top_y - r_rightend_y) / r_width
            r_fh_b_l = abs(r_bottom_y - r_leftend_y) / r_width
            r_fh_b_r = abs(r_bottom_y - r_rightend_y) / r_width
            r_fh_l_r = abs(r_leftend_y - r_rightend_y) / r_width

            s_fhs[s_name] = [matched_name, abs(s_fh_t_b - r_fh_t_b),
                                           abs(s_fh_t_l - r_fh_t_l),
                                           abs(s_fh_t_r - r_fh_t_r),
                                           abs(s_fh_b_l - r_fh_b_l),
                                           abs(s_fh_b_r - r_fh_b_r),
                                           abs(s_fh_l_r - r_fh_l_r),]

            s_fms[s_name] = [matched_name, abs(s_top_y - s_middle_y), abs(s_bottom_y - s_middle_y), abs(r_top_y - r_middle_y), abs(r_bottom_y - r_middle_y)]
            # s_fas[s_name] = [matched_name, abs(s_features['angle'] - receivers[matched_name]['angle'])]

        # 各Receiver紙片を全Sender紙片に対してマッチングさせる。
        print('Receiver-Senders')
        r_matches = {}
        r_fhs = {}
        r_fms = {}
        # r_fas = {}
        for r_name, r_features in receivers.items():
            matched_name = self.matcher.match(r_features, senders, use_fh=True, use_fa=False, use_fp=False)
            r_matches[r_name] = matched_name

            r_top_x      = r_features['shape_x'][np.argmin(r_features['shape_y'])]
            r_bottom_x   = r_features['shape_x'][np.argmax(r_features['shape_y'])]
            r_top_y      = min(r_features['shape_y'])
            r_bottom_y   = max(r_features['shape_y'])
            r_leftend_x  = r_features['shape_x'][0]
            r_rightend_x = r_features['shape_x'][-1]
            r_leftend_y  = r_features['shape_y'][0]
            r_rightend_y = r_features['shape_y'][-1]
            r_middle_x   = r_features['shape_x'][int(len(r_features['shape_x']) / 2.0)]
            r_middle_y   = r_features['shape_y'][int(len(r_features['shape_y']) / 2.0)]
            r_width  = abs(r_leftend_x - r_rightend_x)
            r_fh_t_b = abs(r_top_y - r_bottom_y) / r_width
            r_fh_t_l = abs(r_top_y - r_leftend_y) / r_width
            r_fh_t_r = abs(r_top_y - r_rightend_y) / r_width
            r_fh_b_l = abs(r_bottom_y - r_leftend_y) / r_width
            r_fh_b_r = abs(r_bottom_y - r_rightend_y) / r_width
            r_fh_l_r = abs(r_leftend_y - r_rightend_y) / r_width

            s_top_x      = senders[matched_name]['shape_x'][np.argmin(senders[matched_name]['shape_y'])]
            s_bottom_x   = senders[matched_name]['shape_x'][np.argmax(senders[matched_name]['shape_y'])]
            s_top_y      = min(senders[matched_name]['shape_y'])
            s_bottom_y   = max(senders[matched_name]['shape_y'])
            s_leftend_x  = senders[matched_name]['shape_x'][0]
            s_rightend_x = senders[matched_name]['shape_x'][-1]
            s_leftend_y  = senders[matched_name]['shape_y'][0]
            s_rightend_y = senders[matched_name]['shape_y'][-1]
            s_middle_x   = senders[matched_name]['shape_x'][int(len(senders[matched_name]['shape_x']) / 2.0)]
            s_middle_y   = senders[matched_name]['shape_y'][int(len(senders[matched_name]['shape_y']) / 2.0)]
            s_width  = abs(s_leftend_x - s_rightend_x)
            s_fh_t_b = abs(s_top_y - s_bottom_y) / s_width
            s_fh_t_l = abs(s_top_y - s_leftend_y) / s_width
            s_fh_t_r = abs(s_top_y - s_rightend_y) / s_width
            s_fh_b_l = abs(s_bottom_y - s_leftend_y) / s_width
            s_fh_b_r = abs(s_bottom_y - s_rightend_y) / s_width
            s_fh_l_r = abs(s_leftend_y - s_rightend_y) / s_width

            r_fhs[r_name] = [matched_name, abs(r_fh_t_b - s_fh_t_b),
                                           abs(r_fh_t_l - s_fh_t_l),
                                           abs(r_fh_t_r - s_fh_t_r),
                                           abs(r_fh_b_l - s_fh_b_l),
                                           abs(r_fh_b_r - s_fh_b_r),
                                           abs(r_fh_l_r - s_fh_l_r),]

            r_fms[r_name] = [matched_name, abs(r_top_y - r_middle_y), abs(r_bottom_y - r_middle_y), abs(s_top_y - s_middle_y), abs(s_bottom_y - s_middle_y)]
            # r_fas[r_name] = [matched_name, abs(r_features['angle'] - senders[matched_name]['angle'])]

        # 結果をファイル出力。
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = os.path.join(current_dir, 'result/result_{}.txt'.format(now))
        with open(result_file, 'w') as f:
            print('#==========#', file=f)
            print('#  RESULT  #', file=f)
            print('#==========#', file=f)
            # Both
            both_success_rate = self.calc_both_success_rate(s_matches, r_matches)
            print('Both Success: {}%'.format(both_success_rate), file=f)
            print('', file=f)
            print('', file=f)
            # Sender
            print('Sender-Receivers', file=f)
            s_success_rate = self.calc_success_rate(s_matches, dst=f)
            print('Success: {}%'.format(s_success_rate), file=f)
            print('', file=f)
            # Receiver
            print('Receiver-Senders', file=f)
            r_success_rate = self.calc_success_rate(r_matches, dst=f)
            print('Success: {}%'.format(r_success_rate), file=f)

            # Ratio Feature Result
            # print('', file=f)
            # print('', file=f)
            # print('#================#', file=f)
            # print('#  RATIO RESULT  #', file=f)
            # print('#================#', file=f)
            # # Sender
            # print('Sender-Receivers', file=f)
            # for k, v in s_fhs.items():
            #     print('{}-{} > fh_t_b:{:.4f} fh_t_l:{:.4f} fh_t_r:{:.4f} fh_b_l:{:.4f} fh_b_r:{:.4f} fh_l_r:{:.4f}'.format(k, v[0], v[1], v[2], v[3], v[4], v[5], v[6]), file=f)
            # print('', file=f)
            # # Receiver
            # print('Receiver-Senders', file=f)
            # for k, v in r_fhs.items():
            #     print('{}-{} > fh_t_b:{:.4f} fh_t_l:{:.4f} fh_t_r:{:.4f} fh_b_l:{:.4f} fh_b_r:{:.4f} fh_l_r:{:.4f}'.format(k, v[0], v[1], v[2], v[3], v[4], v[5], v[6]), file=f)

            # Middle Feature Result
            print('', file=f)
            print('', file=f)
            print('#=================#', file=f)
            print('#  MIDDLE RESULT  #', file=f)
            print('#=================#', file=f)
            # Sender
            print('Sender-Receivers', file=f)
            for k, v in s_fms.items():
                print('{}-{} > fm_a:{:.4f} fm_b:{:.4f} abs(fm_a-fm_b):{:.4f}'.format(k, v[0], v [1]*v[3], v[2]*v[4], abs(v[1]*v[3] - v[2]*v[4])), file=f)
            print('', file=f)
            # Receiver
            print('Receiver-Senders', file=f)
            for k, v in r_fms.items():
                print('{}-{} > fm_a:{:.4f} fm_b:{:.4f} abs(fm_a-fm_b):{:.4f}'.format(k, v[0], v[1]*v[3], v[2]*v[4], abs(v[1]*v[3] - v[2]*v[4])), file=f)




if __name__ == '__main__':
    me = MatchingExperimenter(
        src_dir     = SRC_DIR,
        src_snd_dir = SRC_SND_DIR,
        src_rcv_dir = SRC_RCV_DIR,
        dst_dir     = DST_DIR,
        log_file    = LOG_FILE
        )
    me.execute()
