FROM python:3.10.2

WORKDIR /webchat

COPY . /webchat/

RUN pip install --upgrade pip
COPY ./requirements.txt /webchat/
RUN pip install -r requirements.txt

CMD ["python", "main.py"]