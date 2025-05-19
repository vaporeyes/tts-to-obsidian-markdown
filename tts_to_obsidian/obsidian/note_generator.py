"""
Obsidian note generation module
"""

from pathlib import Path
from datetime import datetime
import yaml
from typing import Optional, Dict, Any
import shutil
import re
import time

class ObsidianNoteGenerator:
    def __init__(
        self,
        vault_path: str,
        diary_folder: str = "diary",
        template_path: Optional[str] = None,
    ):
        """
        Initialize Obsidian note generator
        
        Args:
            vault_path: Path to Obsidian vault
            diary_folder: Folder name for diary entries
            template_path: Path to note template
        """
        self.vault_path = Path(vault_path)
        self.diary_folder = diary_folder
        self.template_path = Path(template_path) if template_path else None
        
        # Create diary folder if it doesn't exist
        self.diary_path = self.vault_path / diary_folder
        self.diary_path.mkdir(parents=True, exist_ok=True)
        
        # Create audio folder for recordings
        self.audio_path = self.vault_path / "attachments" / "audio"
        self.audio_path.mkdir(parents=True, exist_ok=True)

    def _get_weather(self) -> str:
        """Get current weather (dummy implementation)"""
        return "Sunny, 72°F"

    def _get_location(self) -> str:
        """Get current location (dummy implementation)"""
        return "Home Office"

    def _get_related_entries(self, current_date: datetime) -> str:
        """
        Find related diary entries based on date proximity
        
        Args:
            current_date: Current entry date
            
        Returns:
            Markdown formatted list of related entries
        """
        related_entries = []
        
        # Look for entries within the last 7 days
        for i in range(1, 8):
            check_date = current_date.replace(day=current_date.day - i)
            entry_path = self.diary_path / f"{check_date.strftime('%Y-%m-%d')}.md"
            if entry_path.exists():
                related_entries.append(f"- [[{check_date.strftime('%Y-%m-%d')}]]")
        
        return "\n".join(related_entries) if related_entries else "No recent entries"

    def _copy_audio_file(self, recording_path: Path) -> str:
        """
        Copy audio file to vault attachments and return markdown link
        
        Args:
            recording_path: Path to audio recording
            
        Returns:
            Markdown link to audio file
        """
        if not recording_path:
            return "No audio recording"
            
        # Create filename with epoch timestamp and random suffix
        epoch = int(time.time() * 1000)  # milliseconds since epoch
        new_filename = f"diary_{epoch}{recording_path.suffix}"
        new_path = self.audio_path / new_filename
        
        # Copy file to vault
        shutil.copy2(recording_path, new_path)
        
        # Return markdown link
        return f"![[{new_filename}]]"

    def create_note(
        self,
        enhanced_transcription: Dict[str, Any],
        recording_path: Optional[Path] = None,
    ) -> Path:
        """
        Create a new diary entry in Obsidian vault
        
        Args:
            enhanced_transcription: Enhanced transcription data
            recording_path: Path to audio recording
            
        Returns:
            Path to created note
        """
        # Get current date and time
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        
        # Prepare note content
        if self.template_path and self.template_path.exists():
            with open(self.template_path) as f:
                template = f.read()
        else:
            template = """
# Diary Entry - {date}

## Metadata
- Time: {time}
- Duration: {duration}
- Mood: {mood}
- Topics: {topics}
- Word Count: {word_count}
- Weather: {weather}
- Location: {location}

## Content
{content}

## Related Entries
{related_entries}

## Audio Recording
{audio_link}
"""
        
        # Get additional metadata
        weather = self._get_weather()
        location = self._get_location()
        related_entries = self._get_related_entries(now)
        audio_link = self._copy_audio_file(recording_path) if recording_path else "No audio recording"
        
        # Format note content
        content = template.format(
            date=date_str,
            time=time_str,
            duration=enhanced_transcription.get("duration", "Unknown"),
            mood=enhanced_transcription.get("mood", "Neutral"),
            topics=", ".join(enhanced_transcription.get("topics", [])),
            word_count=enhanced_transcription.get("word_count", 0),
            content=enhanced_transcription.get("text", ""),
            weather=weather,
            location=location,
            related_entries=related_entries,
            audio_link=audio_link
        )
        
        # Create note file
        note_path = self.diary_path / f"{date_str}.md"
        with open(note_path, "w") as f:
            f.write(content)
        
        return note_path 