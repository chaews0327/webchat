FROM python:3.10.2

WORKDIR /webchat

COPY ./webchat /webchat/webchat/
COPY ./requirements.txt /webchat/

RUN pip install --upgrade pip
RUN pip install -r /webchat/requirements.txt

CMD ["python", "/webchat/webchat/main.py"]