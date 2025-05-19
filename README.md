# Voice-to-Diary Obsidian Note Generator

A Python application that converts voice recordings into formatted diary entries in Obsidian. The application uses OpenAI's Whisper for speech-to-text conversion and provides a simple interface for recording and processing audio into well-structured markdown notes.

## Features

- 🎤 Record audio directly from your microphone
- 🎯 High-quality transcription using OpenAI's Whisper
- 📝 Automatic text enhancement and formatting
- 📅 Organized diary entries with metadata
- 🔗 Automatic linking to related entries
- 🎵 Audio file management with unique timestamps
- 🌤️ Weather and location tracking (currently using dummy data)
- 🔄 Automatic cleanup of old recordings

## Requirements

- Python 3.8 or higher
- uv (Python package manager)
- OpenAI Whisper
- Obsidian vault
- Sound device support for recording

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/tts-to-obsidian-markdown.git
cd tts-to-obsidian-markdown
```

2. Install uv if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

4. Install dependencies:

```bash
uv sync
```

5. Download the spaCy model:

```bash
uv pip install spacy
python -m spacy download en_core_web_sm
```

6. Create a `config.yaml` file based on `config.yaml.example`:

```bash
cp config.yaml.example config.yaml
```

7. Edit `config.yaml` with your Obsidian vault path and preferences.

## Usage

### Recording and Processing

1. Start recording:

```bash
uv run python main.py record
```

- Press Enter to start recording
- Press Enter again to stop recording
- The audio will be automatically transcribed and processed

2. Process an existing audio file:

```bash
uv run python main.py process path/to/audio.wav
```

3. Transcribe an audio file without creating a note:

```bash
uv run python main.py transcribe path/to/audio.wav
```

4. Clean up old recordings:

```bash
uv run python main.py cleanup
```

### Configuration

The `config.yaml` file contains several important settings:

```yaml
audio:
  sample_rate: 16000
  channels: 1
  chunk_size: 1024
  max_duration: 300  # Maximum recording duration in seconds

transcription:
  model: "base.en"  # Whisper model to use
  language: "en"
  temperature: 0.0
  initial_prompt: "This is a diary entry."

obsidian:
  vault_path: "/path/to/your/vault"
  diary_folder: "diary"
  template_path: "templates/diary_template.md"

privacy:
  delete_audio_after_processing: false
  retention_days: 30
```

### Available Whisper Models

The application supports various Whisper models:

- `tiny.en`: Fastest, English-only
- `base.en`: Good balance of speed and accuracy, English-only
- `small.en`: Better accuracy, English-only
- `medium.en`: High accuracy, English-only
- `large-v3`: Best accuracy, multilingual

Choose the model based on your needs for speed vs. accuracy.

### Note Structure

Generated diary entries include:

- Date and time
- Recording duration
- Detected mood
- Identified topics
- Word count
- Weather (currently dummy data)
- Location (currently dummy data)
- Related entries from the past week
- Audio recording link

### Audio File Management

- Audio files are stored in `attachments/audio` within your Obsidian vault
- Files are named with epoch timestamps for uniqueness
- Old recordings can be automatically cleaned up based on retention policy

## Development

### Project Structure

```
tts-to-obsidian-markdown/
├── src/
│   └── tts_to_obsidian/
│       ├── audio/
│       │   └── recorder.py
│       ├── transcription/
│       │   └── whisper.py
│       ├── enhancement/
│       │   └── processor.py
│       ├── obsidian/
│       │   └── note_generator.py
│       └── utils/
│           └── helpers.py
├── templates/
│   └── diary_template.md
├── tests/
│   └── test_basic.py
├── config.yaml.example
├── requirements.txt
└── main.py
```

### Running Tests

```bash
uv run pytest tests/
```

## Troubleshooting

1. **No audio input detected**
   - Check your microphone settings
   - Ensure sounddevice is properly installed
   - Try running with `--debug` flag for more information

2. **Transcription issues**
   - Verify Whisper model is properly installed
   - Check audio file format (WAV recommended)
   - Try a different Whisper model size

3. **Obsidian integration problems**
   - Verify vault path in config.yaml
   - Check folder permissions
   - Ensure template file exists

4. **Package management issues**
   - Ensure uv is properly installed
   - Try running `uv sync --upgrade` to update dependencies
   - Check `requirements.txt` for any version conflicts

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
