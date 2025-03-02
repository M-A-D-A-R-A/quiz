FROM python:3.13.0-slim

WORKDIR /globetrotter

COPY microservice/etc/base.txt .
RUN pip install --no-cache-dir -r microservice/etc/base.txt

COPY . .

CMD ["uvicorn", "--bind", ":5000", "microservice.app:app"]