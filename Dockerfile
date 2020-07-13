FROM python:3.7.8

RUN apt-get update && \
	apt-get install -y python3-lxml poppler-utils && \
	pip install pdf-diff

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT [ "bin/start.sh"]