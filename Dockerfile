from python:3.8-alpine

COPY requirements.txt /

RUN pip install -r requirements.txt
RUN pip install gunicorn
COPY . /

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "api:create_app()"]

