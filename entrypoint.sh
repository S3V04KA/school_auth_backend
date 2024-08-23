# /bin/sh

python -m alembic upgrade head
python app/main.py