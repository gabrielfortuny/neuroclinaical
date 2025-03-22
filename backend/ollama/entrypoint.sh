#!/bin/bash
set -e

echo "Starting Ollama server..."
ollama serve & pid=$!

sleep 5

echo "Creating Ollama model..."
ollama create mymodel -f Modelfile
echo "Created model!"

# wait for ollama process to finish
wait $pid
