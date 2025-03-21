FROM ollama/ollama

COPY entrypoint.sh /entrypoint.sh
COPY models/ /models/
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
