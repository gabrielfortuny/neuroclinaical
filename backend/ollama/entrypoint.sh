#!/bin/bash
set -e

echo "Starting Ollama server..."
ollama serve

echo "Creating Ollama model..."
ollama create mymodel -f Modelfile

wait
