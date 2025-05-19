#!/usr/bin/env python3
"""
Voice-to-Diary Obsidian Note Generator
Main application entry point
"""

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
import yaml
from dotenv import load_dotenv
import time
from datetime import datetime
import requests
import sys

# Import our modules
from tts_to_obsidian.audio.recorder import AudioRecorder
from tts_to_obsidian.transcription.whisper import WhisperTranscriber
from tts_to_obsidian.enhancement.processor import TextEnhancer
from tts_to_obsidian.obsidian.note_generator import ObsidianNoteGenerator
from tts_to_obsidian.utils.helpers import (
    load_config,
    ensure_directory,
    format_duration,
    cleanup_old_files,
)

# Initialize Typer app and Rich console
app = typer.Typer(help="Voice-to-Diary Obsidian Note Generator")
console = Console()

# Load environment variables
load_dotenv()

def check_ollama_server() -> bool:
    """Check if Ollama server is running and accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def check_whisper_model() -> bool:
    """Check if Whisper model is available"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        models = response.json().get("models", [])
        return any(model["name"] == "large" for model in models)
    except (requests.exceptions.ConnectionError, KeyError):
        return False

def ensure_ollama_ready():
    """Ensure Ollama is running and Whisper model is available"""
    if not check_ollama_server():
        console.print("[red]Error: Ollama server is not running![/red]")
        console.print("Please start Ollama by running: ollama serve")
        sys.exit(1)
    
    if not ensure_ollama_ready():
        console.print("[yellow]Whisper model not found. Pulling model...[/yellow]")
        try:
            import subprocess
            subprocess.run(["ollama", "pull", "whisper"], check=True)
            console.print("[green]Whisper model pulled successfully![/green]")
        except subprocess.CalledProcessError:
            console.print("[red]Error: Failed to pull Whisper model![/red]")
            console.print("Please run: ollama pull whisper")
            sys.exit(1)

def load_config() -> dict:
    """Load configuration from config.yaml"""
    config_path = Path("config.yaml")
    if not config_path.exists():
        console.print("[red]Error: config.yaml not found![/red]")
        console.print("Please create a config.yaml file based on config.yaml.example")
        raise typer.Exit(1)
    
    with open(config_path) as f:
        return yaml.safe_load(f)

def process_audio(
    audio_path: Path,
    config: dict,
    show_progress: bool = True
) -> Path:
    """
    Process audio file through the entire pipeline
    
    Args:
        audio_path: Path to audio file
        config: Configuration dictionary
        show_progress: Whether to show progress indicators
        
    Returns:
        Path to created Obsidian note
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        disable=not show_progress
    ) as progress:
        # Initialize components
        transcriber = WhisperTranscriber(
            model=config["transcription"]["model"],
            language=config["transcription"]["language"],
            temperature=config["transcription"]["temperature"],
            initial_prompt=config["transcription"]["initial_prompt"],
        )
        
        enhancer = TextEnhancer()
        
        note_generator = ObsidianNoteGenerator(
            vault_path=config["obsidian"]["vault_path"],
            diary_folder=config["obsidian"]["diary_folder"],
            template_path=config["obsidian"]["template_path"],
        )
        
        # Transcribe audio
        progress.add_task("Transcribing audio...", total=None)
        try:
            transcription = transcriber.transcribe(audio_path)
            console.print(f"[green]Transcription successful![/green]")
            console.print(f"[yellow]Transcribed text: {transcription['text'][:100]}...[/yellow]")
        except Exception as e:
            console.print(f"[red]Error during transcription: {str(e)}[/red]")
            console.print("[yellow]Please ensure Whisper model is properly installed.[/yellow]")
            raise typer.Exit(1)
        
        # Enhance text
        progress.add_task("Enhancing text...", total=None)
        enhanced = enhancer.enhance(transcription["text"])
        console.print(f"[green]Text enhancement complete![/green]")
        
        # Create Obsidian note
        progress.add_task("Creating Obsidian note...", total=None)
        note_path = note_generator.create_note(
            enhanced_transcription={
                "text": transcription["text"],
                "duration": transcription["duration"],
                "mood": enhanced.get("mood", "Neutral"),
                "topics": enhanced.get("topics", []),
                "word_count": len(transcription["text"].split()),
            },
            recording_path=audio_path if not config["privacy"]["delete_audio_after_processing"] else None
        )
        
        # Clean up audio if configured
        if config["privacy"]["delete_audio_after_processing"]:
            audio_path.unlink()
        
        return note_path

@app.command()
def record():
    """Start recording audio from microphone"""
    # ensure_ollama_ready()
    config = load_config()
    
    # Initialize recorder
    recorder = AudioRecorder(
        sample_rate=config["audio"]["sample_rate"],
        channels=config["audio"]["channels"],
        chunk_size=config["audio"]["chunk_size"],
        max_duration=config["audio"]["max_duration"],
    )
    
    console.print("[green]Starting recording... Press Ctrl+C to stop[/green]")
    
    try:
        recorder.start_recording()
        while recorder.is_recording():
            time.sleep(0.1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping recording...[/yellow]")
        audio_path = recorder.stop_recording()
        console.print(f"[green]Recording saved to: {audio_path}[/green]")
        
        # Process the recording
        note_path = process_audio(audio_path, config)
        console.print(f"[green]Diary entry created: {note_path}[/green]")

@app.command()
def transcribe(file_path: Path):
    """Transcribe an audio file to text"""
    ensure_ollama_ready()
    
    if not file_path.exists():
        console.print(f"[red]Error: File {file_path} not found![/red]")
        raise typer.Exit(1)
    
    config = load_config()
    
    # Initialize transcriber
    transcriber = WhisperTranscriber(
        model=config["transcription"]["model"],
        language=config["transcription"]["language"],
        temperature=config["transcription"]["temperature"],
        initial_prompt=config["transcription"]["initial_prompt"],
    )
    
    # Transcribe file
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        progress.add_task("Transcribing audio...", total=None)
        try:
            result = transcriber.transcribe(file_path)
        except Exception as e:
            console.print(f"[red]Error during transcription: {str(e)}[/red]")
            console.print("[yellow]Please ensure Ollama is running and the Whisper model is available.[/yellow]")
            raise typer.Exit(1)
    
    # Display result
    console.print("\n[bold]Transcription:[/bold]")
    console.print(result["text"])

@app.command()
def process(file_path: Path):
    """Process an audio file and create an Obsidian note"""
    ensure_ollama_ready()
    
    if not file_path.exists():
        console.print(f"[red]Error: File {file_path} not found![/red]")
        raise typer.Exit(1)
    
    config = load_config()
    note_path = process_audio(file_path, config)
    console.print(f"[green]Diary entry created: {note_path}[/green]")

@app.command()
def cleanup():
    """Clean up old audio files"""
    config = load_config()
    recordings_dir = Path("recordings")
    
    if not recordings_dir.exists():
        console.print("[yellow]No recordings directory found.[/yellow]")
        return
    
    days = config["privacy"]["retention_days"]
    console.print(f"Cleaning up files older than {days} days...")
    
    cleanup_old_files(recordings_dir, "*.wav", days)
    cleanup_old_files(recordings_dir, "*.mp3", days)
    cleanup_old_files(recordings_dir, "*.m4a", days)
    
    console.print("[green]Cleanup complete![/green]")

def main():
    """Main entry point"""
    try:
        config = load_config()
        app()
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    main()
