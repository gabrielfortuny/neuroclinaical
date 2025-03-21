FROM python:3.13.2-slim

RUN apt-get update && apt-get install -y curl && apt-get clean

WORKDIR /workspace/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
