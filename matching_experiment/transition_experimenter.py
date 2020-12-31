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
import random
import re
import shutil
import sys

# Related third party imports.
import cv2

# Local application/library specific imports.
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir))
sys.path.append('../')
import app.image_processing_manager as ipm
import app.engine as engine
import matching_experimenter as me


logger = logging.getLogger(__name__)


SRC_DIR     = './images'
SRC_SND_DIR = os.path.join(SRC_DIR, 'sender')
SRC_RCV_DIR = os.path.join(SRC_DIR, 'receiver')
DST_DIR     = './t_result'
LOG_FILE    = os.path.join(DST_DIR, 'out.log')


class TransitionExperimenter():
    def __init__(self, src_dir, src_snd_dir, src_rcv_dir, dst_dir, begin, diff, end):
        self.src_dir     = src_dir
        self.src_snd_dir = src_snd_dir
        self.src_rcv_dir = src_rcv_dir
        self.dst_dir     = dst_dir
        self.begin = begin
        self.diff = diff
        self.end = end


    def mkdir(self, d, rm=False):
        if rm:
            # 既存の同名ディレクトリがあれば削除
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d)
        else:
            # 既存の同名ディレクトリがある場合は何もしない
            try: os.makedirs(d)
            except FileExistsError: pass


    def extract_imgids_in_dir(self, src_dir):
        files  = [filename for filename in os.listdir(src_dir) if not filename.startswith('.')]
        imgids = []
        for file in files:
            if os.path.isfile(os.path.join(src_dir, file)):
                filename = os.path.splitext(os.path.basename(file))[0]
                imgid    = re.search('[0-9]+', filename).group()
                imgids.append(imgid)
        return imgids


    def execute(self):
        imgids = self.extract_imgids_in_dir(self.src_snd_dir)

        # マッチングに使用する画像の選定処理
        num = self.begin
        while num <= self.end:
            # imgidをランダムにnum個抽出して，s/rそれぞれのディレクトリに対応する画像を保存
            num_dir = os.path.join(self.dst_dir, str(num))
            self.mkdir(num_dir, rm=True)
            self.mkdir(os.path.join(num_dir, 'sender'), rm=True)
            self.mkdir(os.path.join(num_dir, 'receiver'), rm=True)
            sampleids = random.sample(imgids, num)
            for sampleid in sampleids:
                shutil.copyfile(os.path.join(self.src_snd_dir, 'upper_' + str(sampleid) + '.jpg'),
                                os.path.join(num_dir, 'sender', 'upper_' + str(sampleid) + '.jpg')
                                )
                shutil.copyfile(os.path.join(self.src_rcv_dir, 'lower_' + str(sampleid) + '.jpg'),
                                os.path.join(num_dir, 'receiver', 'lower_' + str(sampleid) + '.jpg')
                                )
            num += self.diff

        # 選定した画像を使用してマッチングする処理
        num = self.begin
        while num <= self.end:
            num_dir = os.path.join(self.dst_dir, str(num))
            self.mkdir(os.path.join(num_dir, 'result'), rm=False)
            matcher = me.MatchingExperimenter(
                            src_dir=os.path.join(num_dir),
                            src_snd_dir=os.path.join(num_dir, 'sender'),
                            src_rcv_dir=os.path.join(num_dir, 'receiver'),
                            dst_dir=os.path.join(num_dir, 'result')
                        )
            matcher.execute()

            num += self.diff


if __name__ == '__main__':
    te = TransitionExperimenter(
            src_dir    =SRC_DIR,
            src_snd_dir=SRC_SND_DIR,
            src_rcv_dir=SRC_RCV_DIR,
            dst_dir    =DST_DIR,
            begin      =10,
            diff       =10,
            end        =500
        )
    te.execute()
