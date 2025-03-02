FROM python:3.13.0-slim

WORKDIR ./app

COPY ./etc/base.txt .
RUN pip install --no-cache-dir -r ./etc/base.txt

COPY . .

CMD ["uvicorn", "--bind", ":5000", "app:app"]
