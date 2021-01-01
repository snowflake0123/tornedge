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

        if form['cmd'] == 'create_chat_room':
            try:
                image_id = int(form['image_id'])
                response_body = ({
                    'cmd': form['cmd'],
                    'data': {
                        'result': 'success',
                        'message': 'Successfully to create the chat room.'
                    }
                })
            except:
                logger.error('Failed to create the chat room.')
                reponse_body = ({
                    'cmd': form['cmd'],
                    'data': {
                        'result': 'failure',
                        'message': 'Failed to create the chat room.'
                    }
                })

        client_type = form['type'].value
        client_receiptname = form['receipt'].filename
        client_receiptdata = form['receipt'].value
        client_imagename = form['image'].filename
        client_imagedata = form['image'].value

        logger.info('Receipt name: %s' % client_receiptname)
        print('Receipt name: %s' % client_receiptname)

        #--------#
        # Sender #
        #--------#
        if client_type == 'sender':
            if client_receiptdata == 'undefined' or client_imagedata == 'undefined':
                response_body = self.make_message_response_body(
                    '[ERROR] Receipt/image is not attached.')
            else:
                # Saves the content image.
                client_imagename = dt.datetime.now().strftime(
                    '%Y%m%d_%H%M%S%f_') + client_imagename
                self.save_content_image(client_imagename, client_imagedata)

                # Calculates the receipt features and stores them into the DB.
                features = self.extract_features(client_receiptdata)
                logger.info('Sender receipt features: fs_x = %s, fs_y = %s, fh = %f, fa = %f, fp = %s' % (features['shape_x'],
                                                                                                          features['shape_y'],
                                                                                                          features['height'],
                                                                                                          features['angle'],
                                                                                                          features['position']))
                self.server.register((features['shape_x'],
                                      features['shape_y'],
                                      features['height'],
                                      features['angle'],
                                      features['position'],
                                      client_imagename))
                response_body = self.make_message_response_body(
                    'Upload success.')

        #----------#
        # Receiver #
        #----------#
        elif client_type == 'receiver':
            if client_receiptdata == 'undefined':
                response_body = self.make_message_response_body(
                    '[ERROR] Receipt is not attached.')
            else:
                # Calculates the receipt features.
                features = self.extract_features(client_receiptdata)
                logger.info('Receiver receipt features: fs_x = %s, fs_y = %s, fh = %f, fa = %f, fp = %s' % (features['shape_x'],
                                                                                                            features['shape_y'],
                                                                                                            features['height'],
                                                                                                            features['angle'],
                                                                                                            features['position']))

                # Gets the matched receipt ID.
                candidates = self.server.get_all_features()
                matched_id = self.server.matcher.match(
                    features, candidates, use_fp=True)

                # Makes the response that contains the matched image name.
                matched_image_name = self.server.get_image_path(matched_id)
                matched_features = self.server.get_features_by_id(matched_id)
                logger.info('Matched image name: %s' % matched_image_name)
                logger.info(
                    'Matched receipt features: fs_x = %s, fs_y = %s, fh = %f, fa = %f, fp = %s' % matched_features)
                imagepath = './client_data/images/' + matched_image_name
                response = {'imagepath': imagepath,
                            'imagename': matched_image_name}
                response_body = json.dumps(response)
                print('Matched Image Name: %s' % matched_image_name)

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
        self.send_header('Content-length', len(response_body))
        self.end_headers()
        self.wfile.write(response_body.encode('utf-8'))

    def save_content_image(self, image_name, image_data):
        outfile_path = './client_data/images/' + image_name
        self.server.image_util.output_binaryfiledata_to_file(
            image_data, outfile_path)

    def extract_features(self, receipt_data):
        # レシート画像をバイナリデータからnumpy配列(BGR)に変換
        img_numpy_bgr = self.server.image_util.convert_bin_to_numpy(
            receipt_data)

        # 特徴量の抽出
        self.ipm = ipm.ImageProcessingManager(img_numpy_bgr, debug=True)
        features = self.ipm.extract_features(img_numpy_bgr)

        return features

    def make_message_response_body(self, msg):
        response = {'message': msg}
        return json.dumps(response)
