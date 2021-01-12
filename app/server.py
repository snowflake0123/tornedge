#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Shion Tominaga, Kazuki Okugawa and Akihiro Miyata'
__copyright__ = 'Copyright (c) 2018-2021 Miyata Lab.'


# Standard library imports.
import cgi
import datetime as dt
import http.server as hs
import json
import logging
import os
import socketserver as scts
from urllib.parse import urlparse

# Local application/library specific imports.
import engine
import image
import image_processing_manager as ipm


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


    def register_and_get_image_id(self, data):
        return self.env.register_and_get_image_id(data)


    def set_file_path_by_image_id(self, image_id, file_path):
        self.env.set_file_path_by_image_id(image_id, file_path)


    def set_chat_room_id_by_image_id(self, image_id, chat_room_id):
        self.env.set_chat_room_id_by_image_id(image_id, chat_room_id)


    def get_all_features(self):
        return self.env.get_all_features()


    def get_features_file_path_exists(self):
        return self.env.get_features_file_path_exists()


    def get_features_chat_room_id_exists(self):
        return self.env.get_features_chat_room_id_exists()


    def get_features_by_image_id(self, image_id):
        return self.env.get_features_by_image_id(image_id)


    def get_registered_date_by_image_id(self, image_id):
        return self.env.get_registered_date_by_image_id(image_id)


    def get_file_path_by_image_id(self, image_id):
        return self.env.get_file_path_by_image_id(image_id)


    def get_chat_room_id_by_image_id(self, image_id):
        return self.env.get_chat_room_id_by_image_id(image_id)


    def register_chat_room_id(self, image_id):
        return self.env.register_chat_room_id(image_id)


    def create_chat_room_db_table(self, chat_room_id):
        return self.env.create_chat_room_db_table


    def init_chat_room_db_table(self, image_id, chat_room_id):
        return self.env.init_chat_room_db_table(image_id, chat_room_id)


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
        #----------------------#
        # debug_make_stub_data #
        #----------------------#
        if cmd == 'debug_create_stub_data':
            image = form['image'].value
            file_name = form['file'].filename
            file_data = form['file'].value
            try:
                registered_date = dt.datetime.now()

                # 紙片の特徴量を抽出する
                features = self.extract_features(image)

                # 特徴量をDBに保存し，image_idを取得
                file_path = ''
                chat_room_id = ''
                data = [registered_date, *features.values(), file_path, chat_room_id]
                image_id = int(self.server.register_and_get_image_id(data))

                # ファイルを保存, pathを取得してDBに格納
                self.save_content_file(file_name, file_data)
                file_path = './client_data/files/' + file_name
                self.server.set_file_path_by_image_id(image_id, file_path)

                # チャットルームIDを生成，DBに登録
                chat_room_id = self.server.get_chat_room_id_by_image_id(image_id)
                if chat_room_id == '':
                    # chat_room_idを作成し，DBのimage_idの行に値を登録
                    from datetime import datetime
                    from uuid import uuid4
                    chat_room_id = 'chat_room' + datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
                    chat_room_id =  chat_room_id.replace('-', '_')
                    self.server.set_chat_room_id_by_image_id(image_id, chat_room_id)
                    # chat_room_idを元にログを記録するファイルを作成
                    chat_log_file_path = './client_data/chat_logs/' + chat_room_id + '.csv'
                    # ログファイルの内容を初期化
                    with open(chat_log_file_path, 'w') as f:
                        print('%s, The chat room was created.' % image_id, file=f)

                # image_idとチャットルームidを返す
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'success',
                        'message': 'Successfully to create the stub data',
                        'image_id': image_id,
                        'chat_room_id': chat_room_id
                    }
                }

            except KeyError as e:
                print(e)
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'failure',
                        'message': 'Failed to create the stub data.',
                        'image_id': '',
                        'chat_room_id': ''
                    }
                }

        #--------------#
        # Upload_image #
        #--------------#
        elif cmd == 'upload_image':
            try:
                image = form['image'].value

                registered_date = dt.datetime.now()
                features = self.extract_features(image)
                file_path = ''
                chat_room_id = ''

                data = [registered_date, *features.values(), file_path, chat_room_id]

                image_id = self.server.register_and_get_image_id(data)

                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'success',
                        'message': 'The image has been uploaded.',
                        'image_id': image_id
                    }
                }
            except KeyError as e:
                print('[ERROR] Error occured in upload_image')
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'failure',
                        'message': 'Failed to upload image.',
                        'image_id': ''
                    }
                }

        #-------------#
        # upload_file #
        #-------------#
        elif cmd == 'upload_file':
            try:
                image_id = int(form['image_id'].value)
                file_name = form['file'].filename
                file_data = form['file'].value
                self.save_content_file(file_name, file_data)

                file_path = './client_data/files/' + file_name

                self.server.set_file_path_by_image_id(image_id, file_path)

                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'success',
                        'message': 'The File has been uploaded.',
                    }
                }
            except KeyError as e:
                print(e)
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'failure',
                        'message': 'Failed to upload image.',
                    }
                }

        #---------------#
        # download_file #
        #---------------#
        elif cmd == 'download_file':
            try:
                image_id = int(form['image_id'].value)
                # 特徴量を抽出する
                input_image_id_features = self.server.get_features_by_image_id(image_id)
                # file_pathが存在する紙片データを抜き出す
                candidates_features = self.server.get_features_file_path_exists()
                # マッチング処理を行う
                matched_image_id = self.server.matcher.match(input_image_id_features, candidates_features, use_fh=True)
                print('matched_image_id =', matched_image_id)

                file_path = self.server.get_file_path_by_image_id(matched_image_id)

                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'success',
                        'message': 'Successfully to download the file.',
                        'file_path': file_path
                    }
                }
            except KeyError as e:
                print(e)
                logger.error('Failed to download the file.');
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'failure',
                        'message': 'Failed to create the chat room.',
                        'file_path': '',
                    }
                }

        #------------------#
        # create_chat_room #
        #------------------#
        elif cmd == 'create_chat_room':
            try:
                image_id = int(form['image_id'].value.replace('\"', ''))

                chat_room_id = self.server.get_chat_room_id_by_image_id(image_id)
                if chat_room_id == '':
                    # chat_room_idを作成し，DBのimage_idの行に値を登録
                    from datetime import datetime
                    from uuid import uuid4
                    chat_room_id = 'chat_room' + datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
                    chat_room_id =  chat_room_id.replace('-', '_')
                    self.server.set_chat_room_id_by_image_id(image_id, chat_room_id)
                    # chat_room_idを元にログを記録するファイルを作成
                    chat_log_file_path = './client_data/chat_logs/' + chat_room_id + '.csv'
                    # ログファイルの内容を初期化
                    with open(chat_log_file_path, 'w') as f:
                        print('%s, The chat room was created.' % image_id, file=f)

                # chat_room_idを返す
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'success',
                        'message': 'Successfully to create the chat room.',
                        'chat_room_id': chat_room_id
                    }
                }
            except KeyError as e:
                print(e)
                logger.error('Failed to create the chat room.')
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'failure',
                        'message': 'Failed to create the chat room.',
                        'chat_room_id': '1',
                    }
                }

        #-----------------#
        # enter_chat_room #
        #-----------------#
        elif cmd == 'enter_chat_room':
            try:
                image_id = int(form['image_id'].value)
                # TODO:
                # image_idの紙片とchat_room_idに値がある紙片でマッチングさせる
                # 特徴量を抽出する
                input_image_id_features = self.server.get_features_by_image_id(image_id)
                # chat_room_idが存在する紙片データを抜き出す
                candidates_features = self.server.get_features_chat_room_id_exists()
                # マッチング処理を行う
                matched_image_id = self.server.matcher.match(input_image_id_features, candidates_features, use_fh=True)
                # マッチング相手のchat_room_idを返す
                partner_chat_room_id = self.server.get_chat_room_id_by_image_id(matched_image_id)
                # マッチング相手のchat_room_idを初期化する
                self.server.set_chat_room_id_by_image_id(matched_image_id, '')

                print('partner_chat_room_id = ', partner_chat_room_id)
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'success',
                        'message': 'Successfully to enter the chat room.',
                        'chat_room_id': partner_chat_room_id
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

        #-----------#
        # send chat #
        #-----------#
        elif cmd == 'send_chat':
            try:
                chat_room_id = form['chat_room_id'].value
                message = form['message'].value
                # メッセージの内容をログファイルに追記
                chat_log_file_path = './client_data/chat_logs/' + chat_room_id + '.csv'
                with open(chat_log_file_path, 'a') as f:
                    print(message, file=f)
                # 最新のログを取得
                with open(chat_log_file_path, 'r') as f:
                    chat_logs = f.readlines()
                    print('chat_logs:\n', chat_logs)
                    chat_logs = [line.rstrip('\n') for line in chat_logs]

                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'success',
                        'message': 'Successfully to Send the chat message.',
                        'chat_log': chat_logs
                    }
                }
            except KeyError as e:
                print(e)
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'failure',
                        'message': 'Failed to send the chat message.',
                        'chat_log': []
                    }
                }

        #-------------#
        # update_chat #
        #-------------#
        elif cmd == 'update_chat':
            try:
                chat_room_id = form['chat_room_id'].value
                # TODO:
                #   チャットルームIDのDBを参照して最新のチャットログを取得，配列に変換
                chat_log_file_path = './client_data/chat_logs/' + chat_room_id + '.csv';
                chat_logs = []
                with open(chat_log_file_path, 'r') as f:
                    chat_logs = f.readlines()
                    chat_logs = [line.rstrip('\n') for line in chat_logs]

                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'success',
                        'message': 'Successfully to update the chat log.',
                        'chat_log': chat_logs
                    }
                }
            except (KeyError, FileNotFoundError) as e:
                print(e)
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'failure',
                        'message': 'Failed to update the chat log.',
                        'chat_log': []
                    }
                }

        #----------------#
        # exit_chat_room #
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
            except KeyError as e:
                print(e)
                response_body = {
                    'cmd': cmd,
                    'data': {
                        'result': 'failure',
                        'message': 'Failed to exit the chat room.',
                    }
                }

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
