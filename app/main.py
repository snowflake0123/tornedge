#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Shion Tominaga and Akihiro Miyata'
__copyright__ = 'Copyright (c) 2018-2020 Miyata Lab.'


# Standard library imports.
import argparse
import configparser as cp
import logging
import logging.config
import threading as th

# Local application/library specific imports.
import db
import server


logger = logging.getLogger(__name__)

LOG_CONF_FILE    = 'conf/log.conf'
SERVER_CONF_FILE = 'conf/server.conf'


class Env:
    def __init__(self, server_params, matcher_params, db_params):
        self.server_params  = server_params
        self.matcher_params = matcher_params
        self.db_handler = db.DBHandler(*db_params)


    def start(self):
        server_th = th.Thread(target=server_proc(self, self.server_params, self.matcher_params))
        server_th.setDaemon(True)
        server_th.start()


    def register_and_get_image_id(self, data):
        return self.db_handler.register_and_get_image_id(*data)


    def set_file_path_by_image_id(self, image_id, file_path):
        self.db_handler.set_file_path_by_image_id(image_id, file_path)


    def set_chat_room_id_by_image_id(self, image_id, chat_room_id):
        self.db_handler.set_chat_room_id_by_image_id(image_id, chat_room_id)


    def get_all_features(self):
        return self.db_handler.get_all_features()


    def get_features_file_path_exists(self):
        return self.db_handler.get_features_file_path_exists()


    def get_features_chat_room_id_exists(self):
        return self.db_handler.get_features_chat_room_id_exists()


    def get_features_by_image_id(self, image_id):
        return self.db_handler.get_features_by_image_id(image_id)


    def get_registered_date_by_image_id(self, image_id):
        return self.db_handler.get_registered_date_by_image_id(image_id)


    def get_file_path_by_image_id(self, image_id):
        return self.db_handler.get_file_path_by_image_id(image_id)


    def get_chat_room_id_by_image_id(self, image_id):
        return self.db_handler.get_chat_room_id_by_image_id(image_id)


    def register_chat_room_id(self, image_id):
        return self.db_handler.register_chat_room_id(image_id)


    def create_chat_room_db_table(self, chat_room_id):
        return self.db_handler.create_chat_room_db_table(chat_room_id)


    def init_chat_room_db_table(self, image_id, chat_room_id):
        return self.db_handler.init_chat_room_db_table(image_id, chat_room_id)


#----------------------------#
# Starts the server process. #
#----------------------------#
def server_proc(env, server_params, matcher_params):
    tearing_server = server.TearingServer(env, *server_params, matcher_params, server.TearingHandler)
    tearing_server.serve_forever()


if __name__ == "__main__":
    #-------------------------#
    # Loads logging settings. #
    #-------------------------#
    logging.config.fileConfig(LOG_CONF_FILE, disable_existing_loggers=False)
    logger.info('System start.')
    print('Starting...')

    #------------------------#
    # Loads server settings. #
    #------------------------#
    conf = cp.ConfigParser()
    conf.read(SERVER_CONF_FILE)
    # Server parameters.
    host = ''
    port = int(conf.get('general', 'port'))
    # Matcher parameters.
    weight_fs = float(conf.get('match', 'weight_fs'))
    digit     = int(conf.get('match', 'digit'))
    # DB parameters.
    dbName = conf.get('db', 'dbName')

    #--------------------------------#
    # Loads command line parameters. #
    #--------------------------------#
    parser = argparse.ArgumentParser(description='The main program of Tornedge.')
    parser.add_argument('--port',
                        type=int,
                        help='Server port')
    args = parser.parse_args()

    #--------------------------------------------------------------------#
    # Overwrites parameters if that are specified from the command line. #
    #--------------------------------------------------------------------#
    if args.port is not None:
        port = args.port

    #--------------------#
    # Starts the server. #
    #--------------------#
    logger.info('Port: %s' % port)
    logger.info('DB name: %s' % dbName)
    env = Env(['', port], [weight_fs, digit], [dbName])
    env.start()
