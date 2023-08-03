FROM python:3.1o

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

CMD ["python", "./main.py", "owobot/owo.toml"]
