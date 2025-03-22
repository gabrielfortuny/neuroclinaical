FROM ollama/ollama

RUN apt-get update && apt-get install -y curl && apt-get clean

COPY entrypoint.sh /entrypoint.sh
COPY Modelfile /Modelfile

ENTRYPOINT ["/entrypoint.sh"]
