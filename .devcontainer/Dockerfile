FROM python:3.13.2-slim

WORKDIR /workspaces/project/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
