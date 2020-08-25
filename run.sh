mkdir -p /tmp/email
pip3 install -r requirements.txt
export FN_AUTH_REDIRECT_URI=http://localhost:8040/google/auth
export FN_BASE_URI=http://localhost:8040/
export FN_CLIENT_ID=
export FN_CLIENT_SECRET=

export FLASK_APP=app.py
export FLASK_DEBUG=1
export FN_FLASK_SECRET_KEY=

python3 -m flask run -p 8040
