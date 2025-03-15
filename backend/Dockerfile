FROM python:3.13.2-slim

WORKDIR /workspaces/project/backend
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["sh", "-c", "cd /workspaces/project/backend && if [ \"$FLASK_ENV\" = 'production' ]; then gunicorn -b 0.0.0.0:5000 app:app; else flask run --host=0.0.0.0 --port=5000 --debug; fi"]
