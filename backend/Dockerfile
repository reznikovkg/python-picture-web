FROM python:3.10.7

RUN pip install --upgrade pip

WORKDIR /back

COPY ./* .

RUN pip install -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]