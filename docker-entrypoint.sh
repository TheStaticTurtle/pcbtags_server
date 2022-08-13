Xvfb :99 -screen 0 640x480x8 -nolisten tcp &
uvicorn "main:app" --host "0.0.0.0" --port 80
