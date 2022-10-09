#!/bin/sh

curl -G --data-urlencode "sender=$SMS_1_NUMBER" --data-urlencode "message_body=$SMS_1_TEXT" "http://localhost:5000/message/"

