#!/bin/bash

output_file="query.txt"
: > "$output_file"  # Clear output file

{
  echo "Repository structure:"
  echo '```'
  tree -a -I '.git|tests/*|env|.github|__pycache__|*.egg-info|tests|.pytest_cache|query.txt|.DS_Store|fonts|favicon_io'
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
