"""
Transcription module using Whisper directly
"""

import whisper
import numpy as np
import sounddevice as sd
from pathlib import Path
from typing import Dict, Any, Optional, List
import wave
import time
from queue import Queue
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhisperTranscriber:
    # Available Whisper models
    AVAILABLE_MODELS = [
        "tiny.en", "tiny",
        "base.en", "base",
        "small.en", "small",
        "medium.en", "medium",
        "large-v1", "large-v2", "large-v3",
        "large", "large-v3-turbo", "turbo"
    ]

    def __init__(
        self,
        model: str = "base.en",
        language: str = "en",
        temperature: float = 0.0,
        initial_prompt: str = "This is a diary entry.",
        device: str = "cpu",
    ):
        """
        Initialize Whisper transcriber
        
        Args:
            model: Whisper model size (tiny.en, base.en, small.en, medium.en, large-v3)
            language: Language code for transcription
            temperature: Sampling temperature (0.0 to 1.0)
            initial_prompt: Initial prompt for transcription
            device: Device to run model on ('cpu' or 'cuda')
        """
        self.model = self._validate_model(model)
        self.language = language
        self.temperature = temperature
        self.initial_prompt = initial_prompt
        self.device = device
        
        # Load Whisper model
        logger.info(f"Loading Whisper model: {self.model}")
        try:
            self.stt = whisper.load_model(self.model, device=device)
            logger.info(f"Successfully loaded model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to load model {self.model}: {str(e)}")
            raise RuntimeError(f"Failed to load Whisper model: {str(e)}")

    def _validate_model(self, model: str) -> str:
        """
        Validate and normalize model name
        
        Args:
            model: Model name to validate
            
        Returns:
            Validated model name
            
        Raises:
            ValueError: If model name is invalid
        """
        # Normalize model name
        model = model.lower().strip()
        
        # Check if model is in available models
        if model not in self.AVAILABLE_MODELS:
            raise ValueError(
                f"Invalid model name: {model}. "
                f"Available models are: {', '.join(self.AVAILABLE_MODELS)}"
            )
        
        return model

    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get duration of audio file in seconds"""
        with wave.open(str(audio_path), "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate)

    def _load_audio(self, audio_path: Path) -> np.ndarray:
        """Load audio file into numpy array"""
        with wave.open(str(audio_path), "rb") as wf:
            audio_data = wf.readframes(wf.getnframes())
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            return audio_np

    def transcribe(
        self,
        audio_path: Path,
        additional_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using Whisper
        
        Args:
            audio_path: Path to audio file
            additional_prompt: Additional context for transcription
            
        Returns:
            Dictionary containing transcription and metadata
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Prepare the prompt
        prompt = self.initial_prompt
        if additional_prompt:
            prompt = f"{prompt} {additional_prompt}"

        try:
            # Load and process audio
            logger.info(f"Loading audio file: {audio_path}")
            audio_np = self._load_audio(audio_path)
            duration = self._get_audio_duration(audio_path)
            logger.info(f"Audio duration: {duration:.2f} seconds")

            # Transcribe audio
            logger.info("Starting transcription...")
            result = self.stt.transcribe(
                audio_np,
                fp16=False,  # Set to True if using GPU
                language=self.language,
                temperature=self.temperature,
                initial_prompt=prompt
            )
            logger.info("Transcription completed successfully")

            return {
                "text": result["text"].strip(),
                "duration": duration,
                "language": self.language,
                "model": self.model,
                "metadata": {
                    "temperature": self.temperature,
                    "prompt": prompt,
                    "segments": result.get("segments", []),
                }
            }
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise RuntimeError(f"Failed to transcribe audio: {str(e)}")

    def record_audio(self, stop_event: threading.Event, data_queue: Queue) -> None:
        """
        Record audio from microphone
        
        Args:
            stop_event: Threading event to signal stop recording
            data_queue: Queue to store recorded audio data
        """
        def callback(indata, frames, time, status):
            if status:
                logger.warning(f"Audio recording status: {status}")
            data_queue.put(bytes(indata))

        with sd.RawInputStream(
            samplerate=16000,
            dtype="int16",
            channels=1,
            callback=callback
        ):
            while not stop_event.is_set():
                time.sleep(0.1)

    def get_available_models(self) -> List[str]:
        """Get list of available Whisper models"""
        return self.AVAILABLE_MODELS
