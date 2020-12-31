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

# Local application/library specific imports.
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir))
sys.path.append('../')
import app.image_processing_manager as ipm
import app.engine as engine


logger = logging.getLogger(__name__)


MAX_IMAGE_SIZE = (1080, 1440)
# MAX_IMAGE_SIZE = (2160, 2880)

SRC_DIR     = './images'
SRC_SND_DIR = os.path.join(SRC_DIR, 'sender')
SRC_RCV_DIR = os.path.join(SRC_DIR, 'receiver')
DST_DIR     = './m_result'


class MatchingExperimenter():
    def __init__(self, src_dir, src_snd_dir, src_rcv_dir, dst_dir):
        self.src_dir     = src_dir
        self.src_snd_dir = src_snd_dir
        self.src_rcv_dir = src_rcv_dir
        self.dst_dir     = dst_dir


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
            image = cv2.resize(image, MAX_IMAGE_SIZE) # For test only.
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
                if key_a == key_b and val_a == val_b and key_a == val_a and key_b == val_b:
                    success += 1.0
        return success / len(matches_a) * 100


    def execute(self):
        self.matcher = engine.MatchingEngine(weight_fs=1.0, digit=3)
        # if not os.path.isfile('senders.pickle') or not os.path.isfile('receivers.pickle'):
        #     print('Start extracting features...')
        #     senders   = self.extract_features_in_dir(self.src_snd_dir)
        #     receivers = self.extract_features_in_dir(self.src_rcv_dir)
        #     with open('senders.pickle', mode='wb') as f:
        #         pickle.dump(senders, f)
        #     with open('receivers.pickle', mode='wb') as f:
        #         pickle.dump(receivers, f)
        # else:
        #     print('Loads features files...')
        #     with open('senders.pickle', mode='rb') as f:
        #         senders = pickle.load(f)
        #     with open('receivers.pickle', mode='rb') as f:
        #         receivers = pickle.load(f)
        print('Start extracting features...')
        senders   = self.extract_features_in_dir(self.src_snd_dir)
        receivers = self.extract_features_in_dir(self.src_rcv_dir)

        print('Start matching...')
        # 各Sender紙片を全Receiver紙片に対してマッチングさせる。
        print('Sender-Receivers')
        s_matches = {}
        for s_name, s_features in senders.items():
            matched_name = self.matcher.match(s_features, receivers, use_fh=True, use_fa=False, use_fp=False)
            s_matches[s_name] = matched_name
        # 各Receiver紙片を全Sender紙片に対してマッチングさせる。
        print('Receiver-Senders')
        r_matches = {}
        for r_name, r_features in receivers.items():
            matched_name = self.matcher.match(r_features, senders, use_fh=True, use_fa=False, use_fp=False)
            r_matches[r_name] = matched_name

        # 結果をファイル出力。
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = os.path.join(self.dst_dir, 'result_{}_{}.txt'.format(now, len(senders)))
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



if __name__ == '__main__':
    me = MatchingExperimenter(
        src_dir    =SRC_DIR,
        src_snd_dir=SRC_SND_DIR,
        src_rcv_dir=SRC_RCV_DIR,
        dst_dir    =DST_DIR
        )
    me.execute()
