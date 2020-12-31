#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Shion Tominaga'
__copyright__ = 'Copyright (c) 2018-2019 Miyata Lab.'


# Standard library imports.
import io

# Related third party imports.
import cv2
import numpy as np
from PIL import Image


class ImageUtil():
    def adjust_imagesize(self, image_pil, adj_width, adj_height):
        if image_pil.size[0] > adj_width or image_pil.size[1] > adj_height:
            image_pil.thumbnail((adj_width, adj_height), Image.ANTIALIAS)
        return image_pil


    def fix_image_rotation(self, image_pil):
        # 画像の Orientation タグ値にしたがった処理
        # PIL における Rotate の角度は反時計回りが正
        convert_image = {
        1: lambda image: image,
        2: lambda image: image.transpose(Image.FLIP_LEFT_RIGHT),                              # 左右反転
        3: lambda image: image.transpose(Image.ROTATE_180),                                   # 180度回転
        4: lambda image: image.transpose(Image.FLIP_TOP_BOTTOM),                              # 上下反転
        5: lambda image: image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Pillow.ROTATE_90),  # 左右反転＆反時計回りに90度回転
        6: lambda image: image.transpose(Image.ROTATE_270),                                   # 反時計回りに270度回転
        7: lambda image: image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Pillow.ROTATE_270), # 左右反転＆反時計回りに270度回転
        8: lambda image: image.transpose(Image.ROTATE_90),                                    # 反時計回りに90度回転
        }
        exif = image_pil._getexif()

        try:
            orientation = exif.get(0x112, 1)
            fixed_image = convert_image[orientation](image_pil)
            return fixed_image
        except:
            return image_pil


    def convert_bin_to_numpy(self, image_binary):
        #バイナリーストリーム <- バイナリデータ
        image_binarystream = io.BytesIO(image_binary)

        #PILイメージ <- バイナリーストリーム
        image_pil = Image.open(image_binarystream)

        #PILイメージの向きを修正
        fixed_image_pil = self.fix_image_rotation(image_pil)

        #PILイメージの大きさを，アスペクト比を保ちつつ，幅が1080pixel以内，高さが1440pixel以内になるよう調整
        size_adjusted_image_pil = self.adjust_imagesize(fixed_image_pil, 1080, 1440)

        #numpy配列(RGBA) <- PILイメージ
        image_numpy_RGBA = np.asarray(size_adjusted_image_pil)

        #numpy配列(BGR) <- numpy配列(RGBA)
        image_numpy_bgr = cv2.cvtColor(image_numpy_RGBA, cv2.COLOR_RGBA2BGR)

        return image_numpy_bgr


    def output_binaryfiledata_to_file(self, binary_filedata, outfile_path):
        with open(outfile_path, "wb") as f:
            f.write(binary_filedata)
