#!/bin/bash

output_file="query.txt"
: > "$output_file"  # Clear output file

{
  echo "Repository structure:"
  echo '```'
  tree -a -I '.git'
  echo '```'

  for file in "$@"; do
    if [[ -f "$file" ]]; then
      echo
      echo "\`$file\`:"
      echo '```'
      cat "$file"
      echo '```'
    else
      echo
      echo "\`$file\`: (file not found or not a regular file)"
    fi
  done
} >> "$output_file"
