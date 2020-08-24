FROM ubuntu:latest
  
WORKDIR /app


COPY . .

RUN apt-get update
RUN apt-get install python3 -y

RUN apt-get install python3-pip -y
RUN pip3 install requests
RUN pip3 install jinja2
RUN pip3 install Flask
RUN pip3 install werkzeug
RUN pip3 install flask-session
RUN pip3 install msal
RUN pip3 install apiclient
RUN pip3 install google-api-python-client
RUN pip3 install flask_cors
RUN pip3 install authlib

RUN pip3 install -r requirements.txt

RUN export FN_AUTH_REDIRECT_URI=http://localhost:8040/google/auth
RUN export FN_BASE_URI=http://localhost:8040/
RUN export FN_CLIENT_ID=43626433463-nb7535im2lu0jc6urlh4jmjt0vio6bq4.apps.googleusercontent.com
RUN export FN_CLIENT_SECRET=QOg-KSYKxBHsbtvST9mdLoa2

RUN export FLASK_APP=app.py
RUN export FLASK_DEBUG=1
RUN export FN_FLASK_SECRET_KEY=da7MRQjAOs3R9f5qWGnaacJDY6VjTG

CMD ["python3", "-m", "flask", "run", "-p", "8040"]