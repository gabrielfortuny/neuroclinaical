#!/bin/bash
set -e

echo "⏳  Copying GGUF files into /root/.ollama/models…"

cp /tmp/ollama/models/seizure.gguf        /root/.ollama/models/
cp /tmp/ollama/models/drug.gguf           /root/.ollama/models/
cp /tmp/ollama/Modelfile                 /root/.ollama/models/
cp /tmp/ollama/drug-modelfile            /root/.ollama/models/
cp /tmp/ollama/seizure-modelfile         /root/.ollama/models/

echo "✅  seizure.gguf & drug.gguf copied."

echo "🚀  Starting Ollama server…"
ollama serve & 
pid=$!

# wait a moment for the API to come up
sleep 5

echo "📦  Creating Ollama models…"
cd /root/.ollama/models
ollama create mymodel      -f Modelfile
ollama create drugmodel    -f drug-modelfile
ollama create seizuremodel -f seizure-modelfile
echo "✅  Models registered."

# keep the server alive
wait $pid
