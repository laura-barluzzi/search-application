FROM python:3.6

ADD requirements.txt /app/requirements.txt

RUN pip3 install -r /app/requirements.txt

ADD enerknol/ /app/enerknol

WORKDIR /app

ENV FLASK_APP="/app/enerknol/app.py"

CMD ["flask", "run", "--port=5000", "--host=0.0.0.0"]

EXPOSE 5000
