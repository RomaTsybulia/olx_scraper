FROM python:3.9-slim

RUN apt-get update && apt-get install -y cron

COPY . /app
RUN chmod -R 0644 /app
RUN pip install -r /app/requirements.txt

RUN mkdir /app/prices
RUN chmod -R +x /app/prices

COPY cronjob /etc/cron.d/cronjob
RUN chmod +x /etc/cron.d/cronjob
RUN crontab /etc/cron.d/cronjob

RUN touch /var/log/cron.log
CMD service cron start && tail -f /var/log/cron.log
