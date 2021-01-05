#!/bin/sh

#-------------------------------------------------------------#
# Image Data Registerer for Tornedge.                         #
# Written by Akihiro Miyata and Shion Tominaga on 2018/02/26. #
# Copyright (c) 2018-2021 Miyata Lab. All rights reserved.    #
#-------------------------------------------------------------#

URL="http://localhost:56060/"
REGISTER_IMAGE_DIR="./register_image"
DEFAULT_FILE="default.jpg"

for image in `find ${REGISTER_IMAGE_DIR} -iname "*.jpg" | sort`
do
    file="default_"`basename ${image}`
    cp $DEFAULT_FILE $file

    res=`curl -s\
        -X POST \
        -F "cmd=debug_create_stub_data" \
        -F "image=@${image}" \
        -F "file=@${file}" \
        ${URL}`

    rm $file

    if echo $res | grep -qi "success"; then
        echo "${image}: success"
    else
        echo "${image}: fail"
    fi
done
