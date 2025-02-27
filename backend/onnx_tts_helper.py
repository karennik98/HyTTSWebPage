import numpy as np
import onnxruntime as ort
import soundfile as sf
import json
import logging
from TTS.tts.configs.vits_config import VitsConfig
from TTS.tts.utils.text.tokenizer import TTSTokenizer

logger = logging.getLogger(__name__)

class ONNXTTSHelper:
    def __init__(self, model_path, config_path, speakers_file=None, use_cuda=False):
        """Initialize ONNX TTS Helper
        
        Args:
            model_path (str): Path to ONNX model
            config_path (str): Path to config file
            speakers_file (str, optional): Not used for ONNX model but kept for API compatibility
            use_cuda (bool, optional): Whether to use CUDA acceleration
        """
        # Load config
        logger.info("Loading config...")
        self.config = VitsConfig()
        with open(config_path, 'r') as f:
            self.config.from_dict(json.load(f))

        # Initialize tokenizer
        logger.info("Initializing tokenizer...")
        self.tokenizer = TTSTokenizer.init_from_config(self.config)[0]

        # Configure session options for memory optimization
        logger.info("Setting up optimized session options...")
        session_options = ort.SessionOptions()
        
        # Memory optimizations
        session_options.enable_mem_pattern = False
        session_options.enable_cpu_mem_arena = False
        
        # Reduce threads to lower memory usage
        session_options.intra_op_num_threads = 1
        session_options.inter_op_num_threads = 1
        
        # Graph optimizations
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        # Set execution mode to sequential
        session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        
        # Memory optimizations specific to reducing memory footprint
        # Set memory limits to encourage more conservative memory usage
        session_options.set_session_log_severity_level(3)  # Reduce logging
        
        # Load ONNX model with optimized session options
        logger.info(f"Loading ONNX model from {model_path} with memory optimizations...")
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if use_cuda else ['CPUExecutionProvider']
        
        # Set provider options for more memory-efficient operation
        provider_options = [{}]
        if not use_cuda:
            provider_options = [{'arena_extend_strategy': 'kSameAsRequested'}]
        
        self.session = ort.InferenceSession(
            model_path,
            sess_options=session_options,
            providers=providers,
            provider_options=provider_options
        )
        
        logger.info(f"ONNX model loaded. Inputs: {[input.name for input in self.session.get_inputs()]}")
        logger.info(f"ONNX model outputs: {[output.name for output in self.session.get_outputs()]}")

        # Speaker mapping - hardcoded for now, could be loaded from config if needed
        self.speaker_mapping = {
            'aram': 0,
            'narek': 1
        }

    def prepare_input(self, text, speaker_idx):
        """Prepare model inputs"""
        # Tokenize text
        text_ids = self.tokenizer.text_to_ids(text)
        text_len = len(text_ids)

        return {
            "text": np.array([text_ids], dtype=np.int64),
            "text_lengths": np.array([text_len], dtype=np.int64),
            "speaker_ids": np.array([speaker_idx], dtype=np.int64)
        }

    def generate_speech(self, text, speaker_name, speaker_idx):
        """Generate speech using the ONNX model
        
        Args:
            text (str): Text to synthesize
            speaker_name (str): Name of speaker (kept for API compatibility)
            speaker_idx (int): Index of the speaker
            
        Returns:
            numpy.ndarray: Generated waveform
        """
        try:
            logger.info(f"Generating speech for text: '{text[:50]}...'")
            logger.info(f"Using speaker_idx: {speaker_idx}")
            
            # Prepare input
            inputs = self.prepare_input(text, speaker_idx)
            
            # Run inference
            outputs = self.session.run(None, inputs)
            
            # Get waveform (first output, first batch item, first channel)
            waveform = outputs[0][0, 0]
            
            logger.info(f"Generated audio with shape {waveform.shape}")
            return waveform
            
        except Exception as e:
            logger.error(f"Speech generation failed: {str(e)}")
            raise Exception(f"Speech generation failed: {str(e)}")
            
    def save_audio(self, wav, output_path):
        """Save the generated audio to a file"""
        try:
            sf.write(output_path, wav, self.config.audio.sample_rate)
            logger.info(f"Audio saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save audio: {str(e)}")
            raise Exception(f"Failed to save audio: {str(e)}")