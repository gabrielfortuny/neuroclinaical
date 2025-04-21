#!/bin/bash
set -e

echo "Starting Ollama server..."
ollama serve & pid=$!

sleep 5

echo "Creating Ollama model..."
ollama create mymodel -f Modelfile
echo "Created model!"

# Create newModelfile in the current directory
#echo "Creating newModelfile..."
#cat > /root/newModelfile << EOF
#FROM /root/.ollama/models/newModel.gguf
#PARAMETER temperature 0.7
#PARAMETER num_predict 512
#EOF

#echo "Registering newModel"
#ollama create newModel -f /root/newModelfile

# wait for ollama process to finish
wait $pid