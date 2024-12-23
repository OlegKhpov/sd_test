FROM python:3.11

RUN apt-get update

WORKDIR /project

COPY ./src ./
COPY ./requirements.txt ./
COPY ./commands ./commands
RUN chmod +x ./commands/api.sh

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["bash"]