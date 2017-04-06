chcp 936
REM set abs_path=%~dp0%server.py
REM set FLASK_APP=%abs_path%
set FLASK_APP=server.py
set FLASK_DEBUG=1
flask run -h 127.0.0.1 -p 5000