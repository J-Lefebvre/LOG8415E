FROM python:3.10.0


RUN pip install requests==2.27.1

COPY send_requests.py send_requests.py

COPY constant.py constant.py

COPY lb_address.txt lb_address.txt


CMD [ "python",  "./send_requests.py" ]