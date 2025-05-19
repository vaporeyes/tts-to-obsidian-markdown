"""
Basic tests for Voice-to-Diary application
"""

import pytest
from pathlib import Path
from src.tts_to_obsidian.audio.recorder import AudioRecorder
from src.tts_to_obsidian.transcription.whisper import WhisperTranscriber
from src.tts_to_obsidian.enhancement.processor import TextEnhancer
from src.tts_to_obsidian.obsidian.note_generator import ObsidianNoteGenerator
from src.tts_to_obsidian.utils.helpers import load_config, ensure_directory

@pytest.fixture
def config():
    """Load test configuration"""
    return load_config(Path("config.yaml"))

@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory for test files"""
    return tmp_path

def test_audio_recorder(temp_dir):
    """Test audio recorder initialization"""
    recorder = AudioRecorder()
    assert recorder.sample_rate == 16000
    assert recorder.channels == 1
    assert recorder.chunk_size == 1024
    assert not recorder.is_recording()

def test_whisper_transcriber():
    """Test Whisper transcriber initialization"""
    transcriber = WhisperTranscriber()
    assert transcriber.model == "whisper"
    assert transcriber.language == "en"
    assert transcriber.temperature == 0.0

def test_text_enhancer():
    """Test text enhancer initialization and basic functionality"""
    enhancer = TextEnhancer()
    
    # Test text cleaning
    text = "  hello,  world!  "
    cleaned = enhancer._clean_text(text)
    assert cleaned == "Hello, world!"
    
    # Test emotion detection
    emotions = enhancer._detect_emotion("I am happy today")
    assert emotions["positive"] > 0

def test_obsidian_note_generator(temp_dir):
    """Test Obsidian note generator"""
    generator = ObsidianNoteGenerator(
        vault_path=str(temp_dir),
        diary_folder="test_diary"
    )
    
    # Test note creation
    enhanced_transcription = {
        "text": "Test diary entry",
        "paragraphs": ["Test paragraph"],
        "topics": ["test"],
        "emotions": {"positive": 0.7, "negative": 0.1, "neutral": 0.2},
        "metadata": {
            "duration": 30,
            "word_count": 3
        }
    }
    
    note_path = generator.create_note(enhanced_transcription)
    assert note_path.exists()
    assert note_path.suffix == ".md"
    
    # Test content
    content = note_path.read_text()
    assert "Test diary entry" in content
    assert "#test" in content

def test_helpers(temp_dir):
    """Test helper functions"""
    # Test directory creation
    test_dir = temp_dir / "test"
    ensure_directory(test_dir)
    assert test_dir.exists()
    assert test_dir.is_dir()
    
    # Test duration formatting
    from src.tts_to_obsidian.utils.helpers import format_duration
    assert format_duration(65) == "1m 5s"
    assert format_duration(3665) == "1h 1m 5s"
    assert format_duration(45) == "45s" 