cd ./backend
source hy_web/bin/activate
uvicorn app:app --reload --host 0.0.0.0 --port 8000
