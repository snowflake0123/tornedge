#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import image_processing_manager as ipm
import image
import engine
from urllib.parse import urlparse
import socketserver as scts
import os
import logging
import json
import http.server as hs
import datetime as dt
import cgi
__author__ = 'Shion Tominaga and Akihiro Miyata'
__copyright__ = 'Copyright (c) 2018-2020 Miyata Lab.'


# Standard library imports.

# Local application/library specific imports.


logger = logging.getLogger(__name__)


class TearingServer(scts.ThreadingMixIn, scts.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, env, host, port, matcher_params, handler):
        scts.TCPServer.__init__(self, (host, port), handler)
        self.env = env
        self.matcher = engine.MatchingEngine(*matcher_params)
        self.image_util = image.ImageUtil()
        logger.info('Server start (port: %d)' % port)
        print('Serving at port: %d' % port)

    def register(self, data):
        self.env.register(data)

    def get_all_features(self):
        return self.env.get_all_features()

    def get_features_by_id(self, db_id):
        return self.env.get_features_by_id(db_id)

    def get_image_path(self, db_id):
        return self.env.get_image_path(db_id)


class TearingHandler(hs.SimpleHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        request_file_path = url.path.strip('/')

        if not os.path.exists(request_file_path):
            self.path = '/client/ionic/index.html'

        return hs.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        os.environ['REQUEST_METHOD'] = 'POST'
        form = cgi.FieldStorage(self.rfile, self.headers)
        cmd = form['cmd'].value
        print('[info] Recieve data from client------')
        print('cmd: ', cmd)
        #--------------#   
        # Upload_image #
        #--------------#
        if cmd == 'upload_image':
            try:
                image = form['image'].value
                
                #紙片の特徴量を抽出
                features =  self.extract_features(image)

                # TODO:
                #  抽出した特徴量をDBに登録
                #  image_idを返してもらう

                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'success',
                        'message': 'The image has been uploaded.',
                        'image_id': '1'
                    }
                }
            except KeyError as e:
                print('[ERROR] Error occured in upload_image')
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'failure',
                        'message': 'Failed to upload image.',
                        'image_id': '1'
                    }
                }
        #-------------#
        # Upload_file #
        #-------------#
        elif cmd == 'upload_file':
            try:
                image_id = int(form['image_id'])
                file_name = form['file'].filename
                file_data = form['file'].value
                self.save_content_file(file_name, file_data)

                # TODO:file_pathをDBに保存する
                file_path = './client_data/files/' + file_name

                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'success',
                        'message': 'The image has been uploaded.',
                        'image_id': '1'
                    }
                }
            except:
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'failure',
                        'message': 'Failed to upload image.',
                        'image_id': '1'
                    }
                }

        #--------------#
        # receive_file #
        #--------------#
        elif cmd == 'download_file':
            try:
                image_id = int(form['image_id'].value)
                # TODO:
                #  image_idの紙片とfile_pathがある紙片とでマッチング処理をする
                #  マッチング相手のfile_pathの値を返す
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'success',
                        'message': 'Successfully to download the file.',
                        'file_path': './client_data/files/a.png'
                    }
                }
            except:
                logger.error('Failed to download the file.');
                reponse_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'failure',
                        'message': 'Failed to create the chat room.',
                        'chat_room_id': '1',
                    }
                }

        #------------------#
        # Create_chat_room #
        #------------------#
        elif cmd == 'create_chat_room':
            try:
                image_id = int(form['image_id'])
                # TODO:
                #  image_idの行のchat_room_idを決定，代入
                #  chat_room_idを元にDBのテーブル or ファイルを作成
                #  chat_room_idを返す
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'success',
                        'message': 'Successfully to create the chat room.',
                        'chat_room_id': '1'
                    }
                }
            except:
                logger.error('Failed to create the chat room.')
                reponse_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'failure',
                        'message': 'Failed to create the chat room.',
                        'chat_room_id': '1',
                    }
                }

        #-----------------#
        # Enter_chat_room #
        #-----------------#
        elif cmd == 'enter_chat_room':
            try:
                image_id = int(form['image_id'].value)
                # TODO:
                #  image_idの紙片とchat_room_idに値がある紙片でマッチングさせる
                #  マッチング相手のchat_room_idを返す 
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'success',
                        'message': 'Successfully to enter the chat room.',
                        'chat_room_id': '1'
                    }
                }
            except:
                logger.error('Failed to create the chat room.')
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'failure',
                        'message': 'Failed to enter the chat room.',
                        'chat_room_id': '1'
                    }
                }

        #----------------#
        # Exit_chat_room #
        #----------------#
        elif cmd == 'exit_chat_room':
            try:
                image_id = int(form['image_id'].value)
                # image_idの行のchat_room_idを削除する
                # chat_room_idのDBテーブル or ファイルを削除する
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'success',
                        'message': 'Successfully to exit the chat room.',
                    }
                }
            except:
                console.log('[ERROR] Error occured in exit_chat_room')
                logger.error('Error occured in exit_chat_room')
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'failure',
                        'message': 'Failed to exit the chat room.',
                    }
                }

        # client_type = form['type'].value
        # client_receiptname = form['receipt'].filename
        # client_receiptdata = form['receipt'].value
        # client_imagename = form['image'].filename
        # client_imagedata = form['image'].value

        # logger.info('Receipt name: %s' % client_receiptname)
        # print('Receipt name: %s' % client_receiptname)

        #--------#
        # Sender #
        #--------#
        # if client_type == 'sender':
        #     if client_receiptdata == 'undefined' or client_imagedata == 'undefined':
        #         response_body = self.make_message_response_body(
        #             '[ERROR] Receipt/image is not attached.')
        #     else:
        #         # Saves the content image.
        #         client_imagename = dt.datetime.now().strftime(
        #             '%Y%m%d_%H%M%S%f_') + client_imagename
        #         self.save_content_image(client_imagename, client_imagedata)

        #         # Calculates the receipt features and stores them into the DB.
        #         features = self.extract_features(client_receiptdata)
        #         logger.info('Sender receipt features: fs_x = %s, fs_y = %s, fh = %f, fa = %f, fp = %s' % (features['shape_x'],
        #                                                                                                   features['shape_y'],
        #                                                                                                   features['height'],
        #                                                                                                   features['angle'],
        #                                                                                                   features['position']))
        #         self.server.register((features['shape_x'],
        #                               features['shape_y'],
        #                               features['height'],
        #                               features['angle'],
        #                               features['position'],
        #                               client_imagename))
        #         response_body = self.make_message_response_body(
        #             'Upload success.')

        # #----------#
        # # Receiver #
        # #----------#
        # elif client_type == 'receiver':
        #     if client_receiptdata == 'undefined':
        #         response_body = self.make_message_response_body(
        #             '[ERROR] Receipt is not attached.')
        #     else:
        #         # Calculates the receipt features.
        #         features = self.extract_features(client_receiptdata)
        #         logger.info('Receiver receipt features: fs_x = %s, fs_y = %s, fh = %f, fa = %f, fp = %s' % (features['shape_x'],
        #                                                                                                     features['shape_y'],
        #                                                                                                     features['height'],
        #                                                                                                     features['angle'],
        #                                                                                                     features['position']))

        #         # Gets the matched receipt ID.
        #         candidates = self.server.get_all_features()
        #         matched_id = self.server.matcher.match(
        #             features, candidates, use_fp=True)

        #         # Makes the response that contains the matched image name.
        #         matched_image_name = self.server.get_image_path(matched_id)
        #         matched_features = self.server.get_features_by_id(matched_id)
        #         logger.info('Matched image name: %s' % matched_image_name)
        #         logger.info(
        #             'Matched receipt features: fs_x = %s, fs_y = %s, fh = %f, fa = %f, fp = %s' % matched_features)
        #         imagepath = './client_data/files/' + matched_image_name
        #         response = {'imagepath': imagepath,
        #                     'imagename': matched_image_name}
        #         response_body = json.dumps(response)
        #         print('Matched Image Name: %s' % matched_image_name)

        #--------------#
        # Invalid role #
        #--------------#
        else:
            response_body = self.make_message_response_body(
                '[ERROR] Client type is invalid.')

        #-------------------------#
        # Responds to the client. #
        #-------------------------#
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_body).encode('utf-8'))
       
        print('[info] Send data to client------\n', response_body)

    def save_content_file(self, file_name, file_data):
        outfile_path = './client_data/files/' + file_name
        self.server.image_util.output_binaryfiledata_to_file(
            file_data, outfile_path)

    def extract_features(self, receipt_data):
        # レシート画像をバイナリデータからnumpy配列(BGR)に変換
        img_numpy_bgr = self.server.image_util.convert_bin_to_numpy(
            receipt_data)

        # 特徴量の抽出
        self.ipm = ipm.ImageProcessingManager(img_numpy_bgr, debug=False)
        features = self.ipm.extract_features(img_numpy_bgr)

        return features

    def make_message_response_body(self, msg):
        response = {'message': msg}
        return response
