worker: python grant_checker.py
web: gunicorn grant_checker.py:app --bind 0.0.0.0:$PORT
web: python grant_checker.py:app
