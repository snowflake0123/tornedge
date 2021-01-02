#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__    = 'Akihiro Miyata and Shion Tominaga'
__copyright__ = 'Copyright (c) 2018-2020 Miyata Lab.'


# Standard library imports.
import logging
import sqlite3
import sys


logger = logging.getLogger(__name__)


class DBHandler():
    def __init__(self, db_name):
        self.db_name = db_name


    def show_error_message(self):
        logger.error('[%s] DatabaseError: DB is not initialized.' % sys._getframe().f_code.co_name)
        print('Use ./conf/init_db.sh .')


    #=================#
    # Register Method #
    #=================#
    def register_and_get_image_id(self, registered_date, fs_x, fs_y, fh, fa, fp, file_path, chat_room_id):
        conn     = sqlite3.connect(self.db_name)
        curs     = conn.cursor()
        res      = -1
        fs_x_str = ",".join(map(str, fs_x))
        fs_y_str = ",".join(map(str, fs_y))
        fp_str   = ",".join(map(str, fp))
        try:
            curs.execute('''
                INSERT INTO paper (registered_date, fs_x, fs_y, fh, fa, fp, file_path, chat_room_id)
                VALUES ('%s', '%s', '%s', '%f', '%f', '%s', '%s', '%s')
            ''' % (registered_date, fs_x_str, fs_y_str, fh, fa, fp_str, file_path, chat_room_id))
            res = curs.lastrowid
            conn.commit()
        except sqlite3.OperationalError: self.show_error_message()
        conn.close()
        return res


    #=============#
    # Set Methods #
    #=============#
    def set_file_path_by_image_id(self, image_id, file_path):
        conn = sqlite3.connect(self.db_name)
        curs = conn.cursor()
        try:
            curs.execute('''
                UPDATE paper
                SET file_path = '%s'
                WHERE image_id = %d
            ''' % (file_path, image_id))
            conn.commit()
        except sqlite3.OperationalError: self.show_error_message()
        conn.close()


    def set_chat_room_id_by_image_id(self, image_id, chat_room_id):
        conn = sqlite3.connect(self.db_name)
        curs = conn.cursor()
        try:
            curs.execute('''
                UPDATE paper
                SET chat_room_id = '%s'
                WHERE image_id = %d
            ''' % (chat_room_id, image_id))
            conn.commit()
        except sqlite3.OperationalError: self.show_error_message()
        conn.close()


    #=============#
    # Get Methods #
    #=============#
    def get_all_features(self):
        conn = sqlite3.connect(self.db_name)
        curs = conn.cursor()
        res  = {}
        try:
            curs.execute('''
                SELECT * FROM paper
            ''')
            conn.commit()
            res = {row[0]:{'shape_x':row[2],
                           'shape_y':row[3],
                           'height':row[4],
                           'angle':row[5],
                           'position':row[6]
                           } for row in curs.fetchall()}
        except sqlite3.OperationalError: self.show_error_message()
        conn.close()
        return res


    def get_features_file_path_exists(self):
        conn = sqlite3.connect(self.db_name)
        curs = conn.cursor()
        res = ''
        try:
            curs.execute('''
                SELECT * FROM paper
                WHERE file_path != ''
            ''')
            conn.commit()
            res = {row[0]: {'shape_x': row[2],
                            'shape_y': row[3],
                            'height': row[4],
                            'angle': row[5],
                            'position': row[6]
                            } for row in curs.fetchall()}
        except sqlite3.OperationalError: self.show_error_message()
        conn.close()
        return res


    def get_features_chat_room_id_exists(self):
        conn = sqlite3.connect(self.db_name)
        curs = conn.cursor()
        res = ''
        try:
            curs.execute('''
                SELECT * FROM paper
                WHERE chat_room_id != ''
            ''')
            conn.commit()
            res = {row[0]: {'shape_x': row[2],
                            'shape_y': row[3],
                            'height': row[4],
                            'angle': row[5],
                            'position': row[6]
                            } for row in curs.fetchall()}
        except sqlite3.OperationalError: self.show_error_message()
        conn.close()
        return res


    def get_features_by_image_id(self, image_id):
        conn = sqlite3.connect(self.db_name)
        curs = conn.cursor()
        res  = ''
        try:
            curs.execute('''
                SELECT * FROM paper
                WHERE image_id = %d
            ''' % image_id)
            conn.commit()
            res = curs.fetchone()
            res = {'shape_x': list(map(float, res[2].split(','))),
                   'shape_y': list(map(float, res[3].split(','))),
                   'height': res[4],
                   'angle': res[5],
                   'position': list(map(int, res[6].split(',')))
                   }
        except sqlite3.OperationalError as e:
            print(e)
            self.show_error_message()
        conn.close()
        return res


    def get_registered_date_by_image_id(self, image_id):
        conn = sqlite3.connect(self.db_name)
        curs = conn.cursor()
        res  = ''
        try:
            curs.execute('''
                SELECT registered_date FROM paper
                WHERE image_id = %d
            ''' % image_id)
            conn.commit()
            res = curs.fetchone()[0]
        except sqlite3.OperationalError: self.show_error_message()
        conn.close()
        return res


    def get_file_path_by_image_id(self, image_id):
        conn = sqlite3.connect(self.db_name)
        curs = conn.cursor()
        res  = ''
        try:
            curs.execute('''
                SELECT file_path FROM paper
                WHERE image_id = %d
            ''' % image_id)
            conn.commit()
            res = curs.fetchone()[0]
        except sqlite3.OperationalError: self.show_error_message()
        conn.close()
        return res


    def get_chat_room_id_by_image_id(self, image_id):
        conn = sqlite3.connect(self.db_name)
        curs = conn.cursor()
        res  = ''
        try:
            curs.execute('''
                SELECT chat_room_id FROM paper
                WHERE image_id = %d
            ''' % image_id)
            conn.commit()
            res = curs.fetchone()[0]
        except sqlite3.OperationalError: self.show_error_message()
        conn.close()
        return res


    def create_chat_room_db_table(self, chat_room_id):
        conn = sqlite3.connect(self.db_name)
        cur  = conn.cursor()
        table_name = chat_room_id
        try:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS %s(image_id INTEGER, text TEXT);
            ''')
            conn.commit()
        except sqlite3.OperationalError as e:
            print(e)
            self.show_error_message()
