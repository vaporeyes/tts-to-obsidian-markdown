"""
Utility functions for the Voice-to-Diary application
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
from datetime import datetime
import shutil

def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config file (default: config.yaml in current directory)
        
    Returns:
        Dictionary containing configuration
    """
    if config_path is None:
        config_path = Path("config.yaml")
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path) as f:
        return yaml.safe_load(f)

def ensure_directory(path: Path):
    """Ensure directory exists, create if it doesn't"""
    path.mkdir(parents=True, exist_ok=True)

def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string"""
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def cleanup_old_files(directory: Path, pattern: str, days: int):
    """
    Clean up old files matching pattern in directory
    
    Args:
        directory: Directory to clean
        pattern: File pattern to match (e.g., "*.wav")
        days: Delete files older than this many days
    """
    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
    
    for file in directory.glob(pattern):
        if file.stat().st_mtime < cutoff:
            file.unlink()

def get_audio_duration(file_path: Path) -> float:
    """Get duration of audio file in seconds"""
    import wave
    
    with wave.open(str(file_path), "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / float(rate)

def copy_to_obsidian_media(file_path: Path, obsidian_vault: Path) -> Path:
    """
    Copy file to Obsidian media folder
    
    Args:
        file_path: Path to file to copy
        obsidian_vault: Path to Obsidian vault
        
    Returns:
        Path to copied file in Obsidian media folder
    """
    media_folder = obsidian_vault / "media"
    media_folder.mkdir(exist_ok=True)
    
    dest_path = media_folder / file_path.name
    shutil.copy2(file_path, dest_path)
    
    return dest_path

def get_weather_info() -> Optional[Dict[str, Any]]:
    """
    Get current weather information (placeholder)
    In a real implementation, this would use a weather API
    """
    return "sunny"

def get_location_info() -> Optional[Dict[str, Any]]:
    """
    Get current location information (placeholder)
    In a real implementation, this would use a geolocation service
    """
    return "clarksville"