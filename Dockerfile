FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

RUN \
	apt-get update && \
	apt-get install -y apt-utils && \
	apt-get install -y gunicorn && \
	apt-get install -y python3-dev && \
	apt-get install -y python3-setuptools && \
	apt-get install -y python3-pip && \
	apt-get install -y libxml2-dev && \
	apt-get install -y libxslt-dev && \
	apt-get install -y supervisor && \
	apt-get install -y redis-server && \
	apt-get install -y locales





#RUN echo "LC_ALL=\"tr_TR.UTF-8\"" >> /etc/default/locale
#RUN locale-gen tr_TR.UTF-8
#RUN update-locale LANG=tr_TR.UTF-8
#ENV LANG tr_TR.UTF-8
#ENV LANGUAGE tr_TR:en
#ENV LC_ALL tr_TR.UTF-8



ADD requirements.txt /home/propars/requirements.txt
RUN pip3 install -r /home/propars/requirements.txt



ADD deploy/supervisor_celery.conf /etc/supervisor/conf.d/celery.conf
ADD deploy/supervisor_gunicorn.conf /etc/supervisor/conf.d/gunicorn.conf
ADD deploy/supervisor_redis.conf /etc/supervisor/conf.d/redis.conf



ADD deploy/redis.conf /etc/redis/redis.conf
RUN chown redis:redis /etc/redis/redis.conf
RUN chown -R redis:redis /var/lib/redis


RUN useradd -m propars
RUN chown -R propars:propars /home/propars

ADD prpassman /home/propars/prpassman
ENV DJANGO_SETTINGS_MODULE prpassman.production_settings
ENV PYTHONPATH /home/propars/prpassman
RUN python3 /home/propars/prpassman/manage.py collectstatic -l --noinput


CMD  supervisord --nodaemon
