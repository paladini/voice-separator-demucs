import os
import uuid
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import tempfile
import logging

from demucs import pretrained
from demucs.apply import apply_model
from demucs.audio import AudioFile
import torch
from pydub import AudioSegment
import torchaudio

# Configure logging
logger = logging.getLogger(__name__)

# Use only the basic working model
DEFAULT_MODEL = 'mdx_extra_q'
# Define available stems and their configurations
AVAILABLE_STEMS = {
    'drums': {'index': 0, 'name': 'Drums', 'icon': '🥁'},
    'bass': {'index': 1, 'name': 'Bass', 'icon': '🎸'},
    'other': {'index': 2, 'name': 'Other', 'icon': '🎵'},
    'vocals': {'index': 3, 'name': 'Vocals', 'icon': '🎤'},
    'instrumental': {'name': 'Instrumental', 'icon': '🎹'}  # Combination of drums + bass + other
}


class AudioSeparator:
    def __init__(self, output_dir: str = "static/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure GPU optimizations
        if torch.cuda.is_available():
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
        
        # Always use the basic working model
        self.model_name = DEFAULT_MODEL
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Load the model
        try:
            logger.info(f"🔄 Loading basic model '{self.model_name}'...")
            self.model = pretrained.get_model(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"✅ Model loaded: {self.model_name}")
            logger.info(f"Device: {self.device}")
            if torch.cuda.is_available():
                logger.info(f"GPU detected: {torch.cuda.get_device_name()}")
                
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            raise Exception(f"Failed to load model: {e}")

    def separate_stems(
        self, 
        input_file_path: str, 
        selected_stems: List[str] = None
    ) -> Dict[str, str]:
        """
        Separates audio into selected stems using the Demucs model.
        
        Args:
            input_file_path: Path to the input audio file
            selected_stems: List of stems to extract. If None, extracts only 'vocals'
            
        Returns:
            Dict with relative paths to the generated files
            
        Raises:
            ValueError: If the input file is invalid or stems are invalid
            Exception: For other errors during processing
        """
        try:
            # Validate input
            if not os.path.exists(input_file_path):
                raise ValueError(f"File not found: {input_file_path}")
            
            # If not specified, use only vocals by default
            if selected_stems is None:
                selected_stems = ['vocals']
            
            # Validate selected stems
            invalid_stems = [stem for stem in selected_stems if stem not in AVAILABLE_STEMS]
            if invalid_stems:
                raise ValueError(f"Invalid stems: {invalid_stems}. Available: {list(AVAILABLE_STEMS.keys())}")
            
            # Generate unique ID for output files
            unique_id = str(uuid.uuid4())[:8]
            
            logger.info(f"Processing stems: {selected_stems}")
            
            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                logger.info("Loading audio file...")
                # Load the audio
                audio_file = AudioFile(input_file_path)
                wav_data = audio_file.read()
                
                # Apply model for separation
                logger.info("Starting audio separation...")
                
                # Ensure wav_data is on the correct device
                if wav_data.device != torch.device(self.device):
                    wav_data = wav_data.to(self.device)
                
                logger.info(f"Input tensor: {wav_data.shape}, device: {wav_data.device}, dtype: {wav_data.dtype}")
                
                # Always use simple separation
                logger.info("🔄 Processing with basic model...")
                
                with torch.amp.autocast('cuda', enabled=torch.cuda.is_available()):
                    sources = apply_model(
                        self.model, 
                        wav_data, 
                        device=self.device, 
                        progress=True,
                        segment=10,
                        overlap=0.25
                    )
                
                # Normalize tensor format simply
                logger.info(f"Original format: {sources.shape}")
                
                # If tensor has 4 dimensions [batch, sources, channels, length], remove batch
                if len(sources.shape) == 4 and sources.shape[0] == 1:
                    sources = sources[0]
                    logger.info(f"Batch removed: {sources.shape}")
                
                # Check if we have format [sources, channels, length]
                if len(sources.shape) != 3:
                    raise ValueError(f"Unexpected format: {sources.shape}. Expected: [sources, channels, length]")
                
                num_sources, num_channels, audio_length = sources.shape
                logger.info(f"✅ Tensor processed: {num_sources} sources, {num_channels} channels, {audio_length} samples")
                
                # Check if we have the expected number of stems
                if num_sources < 4:
                    raise ValueError(f"Model returned {num_sources} sources. Expected: 4 (drums, bass, other, vocals)")
                
                # Process each selected stem
                result_paths = {}
                
                for stem in selected_stems:
                    logger.info(f"🎵 Processing stem: {stem}")
                    
                    if stem == 'instrumental':
                        # Instrumental is the combination of drums + bass + other
                        audio_data = sources[0] + sources[1] + sources[2]
                        filename = f"instrumental_{unique_id}.mp3"
                    else:
                        # Individual stem
                        stem_index = AVAILABLE_STEMS[stem]['index']
                        audio_data = sources[stem_index]
                        filename = f"{stem}_{unique_id}.mp3"
                    
                    # Move to CPU and ensure correct format
                    audio_data = audio_data.cpu()
                    if audio_data.dtype == torch.float16:
                        audio_data = audio_data.float()
                    
                    # Save temporary WAV file
                    wav_path = temp_path / f"{stem}_{unique_id}.wav"
                    sample_rate = getattr(self.model, 'samplerate', 44100)
                    torchaudio.save(str(wav_path), audio_data, sample_rate=sample_rate)
                    
                    # Convert to MP3
                    mp3_path = self.output_dir / filename
                    audio_segment = AudioSegment.from_wav(str(wav_path))
                    audio_segment.export(
                        str(mp3_path), 
                        format="mp3", 
                        bitrate="192k",
                        parameters=["-q:a", "4"]
                    )
                    
                    # Add to result
                    result_paths[stem] = f"static/output/{filename}"
                    logger.info(f"✅ Stem {stem} processed: {filename}")
                
                logger.info("✅ Separation completed successfully!")
                
                # Clear GPU cache
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                return result_paths
                
        except Exception as e:
            logger.error(f"Error during separation: {str(e)}")
            raise Exception(f"Error during audio separation: {str(e)}")

    def _normalize_tensor_format(self, sources):
        """
        Normalizes tensor format - ULTRA SIMPLE version.
        """
        logger.info(f"Tensor shape: {sources.shape}")
        
        # Only remove batch dimension if necessary
        if len(sources.shape) == 4:
            sources = sources.squeeze(0)
        
        if len(sources.shape) != 3:
            raise ValueError(f"Invalid tensor format: {sources.shape}")
        
        return sources
        if len(sources.shape) != 3:
            raise ValueError(f"Unexpected format: {sources.shape}. Expected 3D after batch removal.")
        
        return sources

    def _needs_full_separation(self, selected_stems: List[str]) -> bool:
        """
        Checks if full separation is needed or if it can be optimized.
        
        Returns:
            True if all 4 stems need to be separated
            False if it can be optimized for specific stems
        """
        # TEMPORARILY FORCE FULL SEPARATION FOR ALL MODELS
        # This ensures maximum stability and avoids tensor errors
        logger.info(f"🔒 Forcing full separation to ensure stability (model: {self.model_name})")
        return True
        
        # The code below can be enabled in the future when optimization is 100% stable
        """
        # More complex models always need full separation
        complex_models = ['htdemucs', 'htdemucs_ft']
        if self.model_name in complex_models:
            logger.info(f"Model {self.model_name} requires full separation")
            return True
        
        # For MDX models, can optimize in specific cases
        # If only wants vocals, can optimize
        if selected_stems == ['vocals']:
            return False
            
        # If only wants instrumental, can optimize (= not vocals)
        if selected_stems == ['instrumental']:
            return False
            
        # If wants vocals + instrumental, can optimize
        if set(selected_stems) == {'vocals', 'instrumental'}:
            return False
            
        # For other cases, needs full separation
        return True
        """

    def _separate_optimized(self, wav_data, selected_stems: List[str]):
        """
        Optimized separation for specific cases using vocals-only model.
        """
        logger.info("🚀 Using OPTIMIZED separation (vocals only)")
        
        # For optimized cases, use specific vocals model if available
        # For now, use the complete model but with faster processing
        with torch.amp.autocast('cuda', enabled=torch.cuda.is_available()):
            sources = apply_model(
                self.model, 
                wav_data, 
                device=self.device, 
                progress=True,
                segment=15,  # Larger segments for vocals
                overlap=0.1   # Less overlap for speed
            )
        
        # Normalize tensor format using robust method
        sources = self._normalize_tensor_format(sources)
        
        # Check if we have the expected number of stems
        num_sources, num_channels, audio_length = sources.shape
        if num_sources < 4:
            raise ValueError(f"Model returned {num_sources} sources (optimized). Expected: 4 (drums, bass, other, vocals)")
            
        return sources

    @staticmethod
    def get_available_stems() -> Dict[str, Dict[str, str]]:
        """Returns information about available stems."""
        return AVAILABLE_STEMS

    def estimate_processing_time(self, selected_stems: List[str]) -> str:
        """
        Estimates processing time based on selected stems and current model.
        """
        # Factors based on model
        model_speed_factor = {
            'mdx_extra_q': 1.0,    # Faster
            'mdx': 1.5,            # Moderate
            'htdemucs': 2.5,       # Slow
            'htdemucs_ft': 4.0     # Very slow
        }
        
        # Factor based on device
        device_factor = 1.0 if torch.cuda.is_available() else 2.0
        
        # Factor based on stem selection
        stem_factor = 1.0
        if len(selected_stems) == 1 and selected_stems[0] == 'vocals':
            stem_factor = 1.0  # Optimized
        elif len(selected_stems) == 1 and selected_stems[0] == 'instrumental':
            stem_factor = 1.0  # Optimized
        elif len(selected_stems) == 2 and 'vocals' in selected_stems and 'instrumental' in selected_stems:
            stem_factor = 1.2  # Karaoke
        elif len(selected_stems) <= 2:
            stem_factor = 1.5  # Few stems
        else:
            stem_factor = 2.0  # Multiple stems
        
        # Calculate estimated time in seconds
        base_time = 30  # Base time for mdx_extra_q + GPU + vocals
        total_factor = model_speed_factor.get(self.model_name, 2.0) * device_factor * stem_factor
        estimated_seconds = base_time * total_factor
        
        # Convert to friendly description
        if estimated_seconds <= 60:
            return "very fast (30-60 seconds)"
        elif estimated_seconds <= 120:
            return "fast (1-2 minutes)"
        elif estimated_seconds <= 180:
            return "moderate (2-3 minutes)"
        elif estimated_seconds <= 300:
            return "slow (3-5 minutes)"
        else:
            return "very slow (5+ minutes)"
    
    def _cleanup_gpu_memory(self):
        """Clears GPU cache to free memory."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()


# Global separator instance (singleton)
_audio_separator_instance = None

def get_audio_separator():
    """Returns singleton instance of the separator."""
    global _audio_separator_instance
    
    if _audio_separator_instance is None:
        _audio_separator_instance = AudioSeparator()
    
    return _audio_separator_instance

# Compatibilidade
audio_separator = get_audio_separator()


def separate_audio(input_file_path: str, selected_stems: List[str] = None) -> Dict[str, str]:
    """
    Convenience function to separate audio into selected stems.
    """
    separator = get_audio_separator()
    return separator.separate_stems(input_file_path, selected_stems)


# Maintain compatibility with old function
def separate_vocals(input_file_path: str) -> Tuple[str, str]:
    """
    Legacy function for compatibility. Separates only vocals and instrumental.
    Optimized for maximum speed.
    """
    separator = get_audio_separator()
    result = separator.separate_stems(input_file_path, ['vocals', 'instrumental'])
    return result['vocals'], result['instrumental']
