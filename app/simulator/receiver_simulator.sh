#!/bin/sh

#-----------------------------------------------------#
# Receiver simulator for Tearing IF.                  #
# Written by Akihiro Miyata on 2018/03/04.            #
# Copyright (c) 2018 Miyata Lab. All rights reserved. #
#-----------------------------------------------------#

URL="http://localhost:56060/client/client.html"
RECEIVER_RECEIPT_DIR="./receiver_receipt"

for receipt in `find ${RECEIVER_RECEIPT_DIR} -iname "*.jpg" | sort`
do
    res=`curl -s\
        -X POST \
        -F "type=receiver" \
        -F "receipt=@${receipt}" \
        -F "image=" \
        ${URL}`

    if echo $res | grep -qi "imagename"; then
        img=`echo $res | sed -e 's/\(.*\)imagename": "\(.*\)".*/\2/'`
        echo "${receipt}: "$img
    else
        echo "${receipt}: fail"
    fi
done
