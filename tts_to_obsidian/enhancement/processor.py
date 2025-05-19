"""
Text enhancement module for processing and structuring transcriptions
"""

import re
from datetime import datetime
from typing import Dict, Any, List, Tuple
import spacy
from dateutil import parser
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

class TextEnhancer:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")
        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download("stopwords")

        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy model...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

        self.stop_words = set(stopwords.words("english"))

    def _clean_text(self, text: str) -> str:
        """Clean up text by removing filler words and fixing common issues"""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text).strip()
        
        # Fix common punctuation issues
        text = re.sub(r"\s+([.,!?])", r"\1", text)
        text = re.sub(r"([.,!?])\s+", r"\1 ", text)
        
        # Fix capitalization at start of sentences
        sentences = sent_tokenize(text)
        sentences = [s[0].upper() + s[1:] for s in sentences]
        text = " ".join(sentences)
        
        return text

    def _detect_dates(self, text: str) -> List[Tuple[str, datetime]]:
        """Detect and parse dates mentioned in text"""
        dates = []
        doc = self.nlp(text)
        
        for ent in doc.ents:
            if ent.label_ == "DATE":
                try:
                    parsed_date = parser.parse(ent.text, fuzzy=True)
                    dates.append((ent.text, parsed_date))
                except (ValueError, TypeError):
                    continue
        
        return dates

    def _identify_topics(self, text: str) -> List[str]:
        """Identify main topics from text"""
        doc = self.nlp(text)
        topics = []
        
        # Extract noun phrases and named entities
        for chunk in doc.noun_chunks:
            if not any(word.text.lower() in self.stop_words for word in chunk):
                topics.append(chunk.text)
        
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE", "EVENT"]:
                topics.append(ent.text)
        
        return list(set(topics))

    def _detect_emotion(self, text: str) -> Dict[str, float]:
        """Detect emotional tone of text (basic implementation)"""
        # This is a very basic implementation
        # In a real application, you might want to use a more sophisticated
        # emotion detection model or API
        positive_words = {"happy", "joy", "excited", "great", "wonderful", "love"}
        negative_words = {"sad", "angry", "upset", "terrible", "hate", "awful"}
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        total = len(words)
        
        if total == 0:
            return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}
        
        return {
            "positive": positive_count / total,
            "negative": negative_count / total,
            "neutral": (total - positive_count - negative_count) / total
        }

    def enhance(self, transcription: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance transcription with additional processing
        
        Args:
            transcription: Dictionary containing raw transcription and metadata
            
        Returns:
            Enhanced transcription with additional metadata
        """

        
        # Clean up text
        cleaned_text = self._clean_text(transcription)
        
        # Detect dates
        dates = self._detect_dates(cleaned_text)
        
        # Identify topics
        topics = self._identify_topics(cleaned_text)
        
        # Detect emotion
        emotions = self._detect_emotion(cleaned_text)
        
        # Structure into paragraphs
        sentences = sent_tokenize(cleaned_text)
        paragraphs = []
        current_paragraph = []
        
        for sentence in sentences:
            current_paragraph.append(sentence)
            if len(current_paragraph) >= 3:  # Arbitrary paragraph size
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []
        
        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))
        
        return {
            "original_text": transcription,
            "cleaned_text": cleaned_text,
            "paragraphs": paragraphs,
            "dates": dates,
            "topics": topics,
            "emotions": emotions,
            "metadata": {
                "word_count": len(cleaned_text.split()),
                "sentence_count": len(sentences),
                "paragraph_count": len(paragraphs),
            }
        } 