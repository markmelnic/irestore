FROM python:3.7-alpine
WORKDIR /var/www/irestore
ENV FLASK_APP=wsgi.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apk update && apk add bash
RUN apk add --no-cache gcc musl-dev linux-headers postgresql-dev mysql-dev
COPY requirements.txt requirements.txt
RUN pip install psycopg2
RUN pip install mysqlclient
RUN pip install -r requirements.txt
RUN pip install gunicorn
EXPOSE 8000
COPY . .
RUN ["chmod", "+x", "./gunicorn.sh"]
ENTRYPOINT ["./gunicorn.sh"]
