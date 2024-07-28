FROM python:3.10.0
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY req.txt /code/req.txt

RUN pip install -r /code/req.txt

COPY . /code/
RUN python manage.py makemigrations
CMD ["uvicorn", "config.asgi:application", "--host", "--ws", "websockets"]