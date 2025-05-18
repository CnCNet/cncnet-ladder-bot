FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "-m", "src.bot.bot"]
