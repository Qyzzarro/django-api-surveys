exec \
python -m venv .env \
source ./.env/bin/activate \
pip install -r requirements.txt \
python manage.py makemigrations survey \
python manage.py makemigrations auth \
python manage.py migrate