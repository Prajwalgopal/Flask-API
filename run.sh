mkdir -p /tmp/email
pip3 install -r requirements.txt
export FN_AUTH_REDIRECT_URI=http://localhost:8040/google/auth
export FN_BASE_URI=http://localhost:8040/
export FN_CLIENT_ID=43626433463-nb7535im2lu0jc6urlh4jmjt0vio6bq4.apps.googleusercontent.com
export FN_CLIENT_SECRET=QOg-KSYKxBHsbtvST9mdLoa2

export FLASK_APP=app.py
export FLASK_DEBUG=1
export FN_FLASK_SECRET_KEY=da7MRQjAOs3R9f5qWGnaacJDY6VjTG

python3 -m flask run -p 8040