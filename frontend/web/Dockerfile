FROM python:3.13.2-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_ENV=development
EXPOSE 5001

CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
