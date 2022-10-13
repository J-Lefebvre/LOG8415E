FROM python:3.10.0


COPY requirements.txt requirements.txt

RUN pip install requests==2.27.1

COPY send_requests.py send_requests.py

COPY constant.py constant.py

CMD [ "python",  "./send_requests.py" ]