#!/bin/bash
set -e

echo "Checking for Modelfiles..."

MODEL_HASH_DIR="/root/.ollama/model_hashes"
mkdir -p "$MODEL_HASH_DIR"

for model_dir in /models/*; do
  if [ -d "$model_dir" ]; then
    modelfile="$model_dir/Modelfile"
    if [ -f "$modelfile" ]; then
      model_name=$(basename "$model_dir")
      hash_file="$MODEL_HASH_DIR/$model_name.hash"
      new_hash=$(sha256sum "$modelfile" | awk '{print $1}')

      if [ -f "$hash_file" ]; then
        old_hash=$(cat "$hash_file")
        if [ "$old_hash" = "$new_hash" ]; then
          echo "Skipping model: $model_name (no changes)"
          continue
        else
          echo "Modelfile changed for $model_name. Rebuilding..."
        fi
      else
        echo "Building model: $model_name"
      fi

      ollama create "$model_name" -f "$modelfile"
      echo "$new_hash" > "$hash_file"
    else
      echo "Skipping $model_dir — no Modelfile found."
    fi
  fi
done

echo "Model setup complete. Installed models:"
ollama list

echo "Launching Ollama..."
exec ollama serve
