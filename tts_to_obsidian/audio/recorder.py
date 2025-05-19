"""
Audio recording module for capturing microphone input
"""

import sounddevice as sd
import numpy as np
from pathlib import Path
import wave
import threading
import queue
from typing import Optional, Callable
from datetime import datetime

class AudioRecorder:
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        max_duration: int = 300,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.max_duration = max_duration
        self.recording = False
        self.audio_queue = queue.Queue()
        self.recording_thread: Optional[threading.Thread] = None
        self.callback: Optional[Callable] = None

    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream"""
        if status:
            print(f"Status: {status}")
        self.audio_queue.put(indata.copy())

    def start_recording(self, callback: Optional[Callable] = None):
        """Start recording audio"""
        if self.recording:
            raise RuntimeError("Already recording")

        self.recording = True
        self.callback = callback
        self.audio_queue = queue.Queue()

        def recording_thread():
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=self._audio_callback,
                blocksize=self.chunk_size,
            ):
                while self.recording:
                    sd.sleep(100)

        self.recording_thread = threading.Thread(target=recording_thread)
        self.recording_thread.start()

    def stop_recording(self) -> Path:
        """Stop recording and save to file"""
        if not self.recording:
            raise RuntimeError("Not recording")

        self.recording = False
        if self.recording_thread:
            self.recording_thread.join()

        # Save recorded audio to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"recordings/{timestamp}.wav")
        output_path.parent.mkdir(exist_ok=True)

        # Convert queue data to numpy array
        audio_data = []
        while not self.audio_queue.empty():
            audio_data.append(self.audio_queue.get())
        
        if not audio_data:
            raise RuntimeError("No audio data recorded")

        audio_data = np.concatenate(audio_data, axis=0)

        # Save as WAV file
        with wave.open(str(output_path), "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(self.sample_rate)
            wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())

        if self.callback:
            self.callback(output_path)

        return output_path

    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self.recording 