FROM python:3
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt install -y libgdal20 wait-for-it
RUN mkdir /code
WORKDIR /code
COPY REQUIREMENTS.txt /code/
RUN pip install -r REQUIREMENTS.txt
COPY . /code/
COPY ./settings_docker_testing.py /code/qgisfeedproject/qgisfeedproject/settings_local.py
COPY ./entrypoint_testing.sh /code/
