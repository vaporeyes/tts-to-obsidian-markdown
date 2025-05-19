#!/bin/bash

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install spaCy model
python -m spacy download en_core_web_sm

# Create necessary directories
mkdir -p recordings
mkdir -p templates

# Copy example config if it doesn't exist
if [ ! -f config.yaml ]; then
    cp config.yaml.example config.yaml
    echo "Created config.yaml from template. Please edit it with your settings."
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed. Please install it from https://ollama.ai"
    echo "After installation, run: ollama pull whisper"
else
    # Pull Whisper model
    echo "Pulling Whisper model..."
    ollama pull whisper
fi

echo "Setup complete! Please edit config.yaml with your Obsidian vault path and other settings."
echo "To start using the application, run: python main.py" 