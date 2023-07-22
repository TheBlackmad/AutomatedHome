#!/usr/bin/bash

pkill -f 'camera_record.py'
pkill -f 'camera_detector.py'
pkill -f 'camera_rtsp.py'
pkill -f 'camera_capture.py'
pkill -f 'camera_main.py'

echo 'All processes killed!'
