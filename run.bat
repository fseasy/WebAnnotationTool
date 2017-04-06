@ECHO off
chcp 936
set PATH=%PATH%;C:\Python27\Scripts\
set abs_path=%~dp0%server.py
set FLASK_APP=%abs_path%
set FLASK_DEBUG=1
flask run -h 127.0.0.1 -p 5000
PAUSE