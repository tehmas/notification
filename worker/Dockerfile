FROM python:3.8.5

COPY . /usr/src/app
WORKDIR  /usr/src/app

RUN pip install -r requirements.txt

CMD ["python", "-u", "run.py"]