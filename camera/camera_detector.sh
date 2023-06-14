#!/bin/bash

PATH=/home/odroid/.rknn/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin

# make available all env variables to make other process run
export CAMERA_ENV=/home/odroid/.rknn
export CAMERA_PATH=/home/odroid/projects/AutomatedHome/camera

# set up the environment
source $CAMERA_ENV/bin/activate
echo "*****" >> $CAMERA_PATH/cd.log
echo "Environment is:" $VIRTUAL_ENV >> $CAMERA_PATH/cd.log
sleep 30

# Start the program
pwd
cd /home/odroid/projects/AutomatedHome/camera
$CAMERA_ENV/bin/python3 $CAMERA_PATH/camera_detector.py
#$CAMERA_ENV/bin/python3 $CAMERA_PATH/camera_detector.py >> $CAMERA_PATH/cd.log 2>&1
