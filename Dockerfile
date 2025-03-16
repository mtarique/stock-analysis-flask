# STAGE-1 Large image
FROM python:3.10 AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

# STAGE-2 Small image
FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/

COPY . .

ENTRYPOINT [ "python", "app.py" ]