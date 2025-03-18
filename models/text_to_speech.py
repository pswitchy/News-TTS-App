# models/text_to_speech.py
"""Text-to-Speech module using gTTS and Transformers."""

import os
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
import re
from typing import Optional
import time
from gtts import gTTS
import soundfile as sf
import torch
from transformers import VitsModel, AutoTokenizer

from utils import translate_to_hindi, log_error
import config

class TextToSpeech:
    """Class for text-to-speech conversion to Hindi."""
    
    def __init__(self):
        """Initialize the TextToSpeech engine."""
        os.makedirs(config.TTS_OUTPUT_DIR, exist_ok=True)
        self._initialize_tts_engine()
    
    def _initialize_tts_engine(self):
        """Initialize TTS engines with fallback support."""
        self.tts_engines = []
        
        # Try to initialize Transformers model first
        try:
            self.transformers_model = VitsModel.from_pretrained("facebook/mms-tts-hin")
            self.transformers_tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-hin")
            self.tts_engines.append("transformers")
        except Exception as e:
            self.transformers_model = None
            log_error(e, "Transformers TTS initialization")
        
        # gTTS is always available as a fallback
        self.tts_engines.append("gtts")
    
    def generate(self, text: str, filename_prefix: str = "output") -> Optional[str]:
        """
        Generate Hindi TTS audio from text.
        
        Args:
            text: Text to convert to speech
            filename_prefix: Prefix for output file
            
        Returns:
            str: Path to generated audio file
        """
        try:
            # Create filename
            safe_prefix = re.sub(r'[^\w]', '_', filename_prefix)
            filename = f"{safe_prefix}_{int(time.time())}.mp3"
            filepath = os.path.join(config.TTS_OUTPUT_DIR, filename)
            
            # Translate to Hindi if needed
            if not re.search(r'[\u0900-\u097F]{10,}', text):
                hindi_text = translate_to_hindi(text)
            else:
                hindi_text = text
            
            # Try available engines in order
            for engine in self.tts_engines:
                try:
                    if engine == "transformers" and self.transformers_model:
                        return self._generate_with_transformers(hindi_text, filepath)
                    elif engine == "gtts":
                        return self._generate_with_gtts(hindi_text, filepath)
                except Exception as e:
                    log_error(e, f"{engine} TTS generation")
                    continue
            
            return None
            
        except Exception as e:
            log_error(e, "TTS generation")
            return None
    
    def _generate_with_transformers(self, text: str, filepath: str) -> str:
        """Generate speech using Transformers model."""
        inputs = self.transformers_tokenizer(text, return_tensors="pt")
        
        with torch.no_grad():
            output = self.transformers_model(**inputs)
        
        audio = output.audio[0].numpy().squeeze()
        sf.write(filepath, audio, self.transformers_model.config.sampling_rate)
        return filepath
    
    def _generate_with_gtts(self, text: str, filepath: str) -> str:
        """Generate speech using gTTS."""
        tts = gTTS(text=text, lang='hi', slow=False)
        tts.save(filepath)
        return filepath