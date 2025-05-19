# Voice-to-Diary Obsidian Note Generator

A Python application that converts voice recordings into well-structured Obsidian diary entries. This tool processes audio input (either through microphone recording or file upload), transcribes it using Whisper via Ollama, enhances the text, and saves it as a properly formatted Obsidian note.

## Features

- 🎤 Audio input via microphone recording or file upload (mp3, wav, m4a)
- 🎯 High-quality transcription using Whisper Tiny via Ollama
- ✨ Text enhancement and structuring
- 📝 Automatic Obsidian note generation with proper formatting
- 🏷️ Smart tagging and metadata generation
- 🔒 Local processing for privacy
- ⚙️ Customizable settings and templates

## Requirements

- Python 3.9+
- Ollama with Whisper model
- macOS (optimized for M-series chips)
- Obsidian installed with a vault configured

## Installation

1. Clone this repository:

```bash
git clone https://github.com/vaporeyes/tts-to-obsidian-markdown.git
cd tts-to-obsidian-markdown
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Install Ollama and the Whisper model:

```bash
# Install Ollama from https://ollama.ai
ollama pull whisper
```

## Configuration

1. Create a `config.yaml` file in the project root (see `config.yaml.example` for template)
2. Set your Obsidian vault path and other preferences
3. Configure any additional settings as needed

## Usage

1. Start the application:

```bash
python main.py
```

2. Choose your input method:
   - Record audio directly
   - Upload an audio file

3. Wait for processing (typically under 30 seconds for 5-minute recordings)

4. Review and edit the transcription if needed

5. Save to your Obsidian vault

## Privacy

- All processing is done locally
- No audio data is uploaded to external services
- Option to delete audio files after processing
- Configurable data retention policies

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
