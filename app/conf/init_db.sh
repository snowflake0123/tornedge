#!/bin/sh

DB_FILE="../tearing.db"
SCHEMA="tearing.schema"

if [ -f $DB_FILE ]
then
    rm -i $DB_FILE
fi
sqlite3 $DB_FILE < $SCHEMA
