FROM python:3.11-bullseye

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

ADD https://raw.githubusercontent.com/tiangolo/uvicorn-gunicorn-docker/master/docker-images/start.sh /start.sh
RUN chmod +x /start.sh

ADD https://raw.githubusercontent.com/tiangolo/uvicorn-gunicorn-docker/master/docker-images/gunicorn_conf.py /gunicorn_conf.py

ADD https://raw.githubusercontent.com/tiangolo/uvicorn-gunicorn-docker/master/docker-images/start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

COPY main.py /app/main.py
WORKDIR /app/

ENV PYTHONPATH=/app

EXPOSE 80

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Uvicorn
CMD ["/start.sh"]