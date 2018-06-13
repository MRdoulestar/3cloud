#!/bin/sh

pid=`ps aux|grep log_handler|awk '{print $2}'|sed -n '1p;1q'`
kill -9 $pid
