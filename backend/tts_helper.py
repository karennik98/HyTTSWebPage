from TTS.utils.synthesizer import Synthesizer

class TTSHelper:
    def __init__(self, model_path, config_path, speakers_file, use_cuda=False):
        self.synthesizer = Synthesizer(
            tts_checkpoint=model_path,
            tts_config_path=config_path,
            tts_speakers_file=speakers_file,
            use_cuda=use_cuda
        )
        
    def generate_speech(self, text, speaker_name, speaker_idx):
        """
        Generate speech using the loaded model
        """
        try:
            wav = self.synthesizer.tts(
                speaker_name=speaker_name,
                text=text,
                speaker_id=speaker_idx
            )
            return wav
        except Exception as e:
            raise Exception(f"Speech generation failed: {str(e)}")
            
    def save_audio(self, wav, output_path):
        """
        Save the generated audio to a file
        """
        try:
            self.synthesizer.save_wav(wav, output_path)
        except Exception as e:
            raise Exception(f"Failed to save audio: {str(e)}")