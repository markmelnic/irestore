FROM python:3.7-alpine
WORKDIR /var/www/irestore
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apk update && apk add bash
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8000
COPY . .
RUN ["chmod", "+x", "./gunicorn.sh"]
ENTRYPOINT ["./gunicorn.sh"]
