FROM python:3.12

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r ./requirements.txt

COPY ./entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//g' /app/entrypoint.sh

COPY . .

ENTRYPOINT ["/bin/sh","/app/entrypoint.sh"]
CMD ["gunicorn", "--bind 0.0.0.0:8000", "backend.wsgi"]