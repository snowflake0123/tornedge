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


    def register(self, fs_x, fs_y, fh, fa, fp, image_path):
        conn     = sqlite3.connect(self.db_name)
        curs     = conn.cursor()
        fs_x_str = ",".join(map(str, fs_x))
        fs_y_str = ",".join(map(str, fs_y))
        fp_str   = ",".join(map(str, fp))
        try:
            curs.execute('''
                INSERT INTO paper (fs_x, fs_y, fh, fa, fp, image_path)
                VALUES ('%s', '%s', '%f', '%f', '%s', '%s')
            ''' % (fs_x_str, fs_y_str, fh, fa, fp_str, image_path))
            conn.commit()
        except sqlite3.OperationalError: self.show_error_message()
        conn.close()


    def get_all_features(self):
        conn = sqlite3.connect(self.db_name)
        curs = conn.cursor()
        res  = {}
        try:
            curs.execute('''
                SELECT * FROM paper
            ''')
            conn.commit()
            res = {row[0]:{'shape_x':row[1],
                           'shape_y':row[2],
                           'height':row[3],
                           'angle':row[4],
                           'position':row[5]
                           } for row in curs.fetchall()}
        except sqlite3.OperationalError: self.show_error_message()
        conn.close()
        return res


    def get_features_by_id(self, dbID):
        conn = sqlite3.connect(self.db_name)
        curs = conn.cursor()
        res  = ''
        try:
            curs.execute('''
                SELECT fs_x, fs_y, fh, fa, fp FROM paper
                WHERE id = %d
            ''' % dbID)
            conn.commit()
            res = curs.fetchone()
        except sqlite3.OperationalError: self.show_error_message()
        conn.close()
        return res


    def get_image_path(self, dbID):
        conn = sqlite3.connect(self.db_name)
        curs = conn.cursor()
        res  = ''
        try:
            curs.execute('''
                SELECT image_path FROM paper
                WHERE id = %d
            ''' % dbID)
            conn.commit()
            res = curs.fetchone()[0]
        except sqlite3.OperationalError: self.show_error_message()
        conn.close()
        return res
