#!/bin/sh

#-----------------------------------------------------#
# Sender simulator for Tearing IF.                    #
# Written by Akihiro Miyata on 2018/02/26.            #
# Copyright (c) 2018 Miyata Lab. All rights reserved. #
#-----------------------------------------------------#

URL="http://localhost:56060/client/client.html"
SENDER_RECEIPT_DIR="./sender_receipt"
DEFAULT_IMG="default.jpg"

for receipt in `find ${SENDER_RECEIPT_DIR} -iname "*.jpg" | sort`
do
    img="default_"`basename ${receipt}`
    cp $DEFAULT_IMG $img

    res=`curl -s\
        -X POST \
        -F "type=sender" \
        -F "receipt=@${receipt}" \
        -F "image=@${img}" \
        ${URL}`

    rm $img

    if echo $res | grep -qi "success"; then
        echo "${receipt}: success"
    else
        echo "${receipt}: fail"
    fi
done
