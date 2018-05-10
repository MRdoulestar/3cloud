#!/bin/sh

socat tcp-l:7777,fork exec:"python waf.py" &
if [ $? eq 0 ];then
echo "Start success"
fi
