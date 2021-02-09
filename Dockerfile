FROM python:3.8.3-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

ENTRYPOINT ["python","tridatu.py"]
CMD ["local"]
