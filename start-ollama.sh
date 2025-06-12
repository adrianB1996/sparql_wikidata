#!/bin/sh
# Start Ollama in background
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
until curl -s -f http://localhost:11434/api/version > /dev/null 2>&1; do
  sleep 1
done

# Pull base SPARQL model if not already present
echo "Ensuring qwen2.5 model is available..."
curl -s -X POST http://localhost:11434/api/pull -d '{"name":"dagbs/qwen2.5-coder-1.5b-instruct-abliterated:latest"}'

# Pull Qwen model for results interpretation
echo "Ensuring qwen base model is available for results interpretation..."
curl -s -X POST http://localhost:11434/api/pull -d '{"name":"qwen:1.7b"}'

# Create custom models from Modelfiles
echo "Creating custom models from Modelfiles..."

# Create SPARQL helper model
if [ -f /Modelfile ]; then
  echo "Found Modelfile for SPARQL, creating custom model 'sparql-helper'..."
  ollama rm sparql-helper 2>/dev/null || true
  ollama create sparql-helper -f /Modelfile
  
  # Verify model creation
  echo "Verifying SPARQL helper model..."
  if ollama list | grep -q "sparql-helper"; then
    echo "✅ SPARQL helper model successfully created!"
  else
    echo "❌ Failed to create SPARQL helper model"
  fi
else
  echo "❌ Error: Modelfile for SPARQL not found"
fi

# Create results interpreter model
if [ -f /Modelfile_qwen ]; then
  echo "Found Modelfile for Qwen, creating custom model 'results-interpreter'..."
  ollama rm results-interpreter 2>/dev/null || true
  ollama create results-interpreter -f /Modelfile_qwen
  
  # Verify model creation
  echo "Verifying results interpreter model..."
  if ollama list | grep -q "results-interpreter"; then
    echo "✅ Results interpreter model successfully created!"
  else
    echo "❌ Failed to create results interpreter model"
    # Add debugging information
    echo "Available models:"
    ollama list
    echo "File exists check:"
    ls -la /Model*
  fi
else
  echo "❌ Error: Modelfile for Qwen not found at path: /Modelfile_qwen"
  echo "Listing available files:"
  ls -la /
fi

# Keep the container running with the main Ollama process
wait $OLLAMA_PID
