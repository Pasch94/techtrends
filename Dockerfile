FROM python:2.7

EXPOSE 3111

COPY ./techtrends /app
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    apparmor \
    apparmor-utils
RUN python -m pip install -r requirements.txt

CMD [ "/bin/bash", "-c", "python init_db.py; python app.py"]
