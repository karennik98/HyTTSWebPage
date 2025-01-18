import gradio as gr
from TTS.utils.synthesizer import Synthesizer
import os
import warnings
import shutil
import model_loader

# Suppress warnings
warnings.filterwarnings("ignore")

# Debug function to check file contents
def debug_file_contents(filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        print(f"\nContents of {filepath}:")
        print(content)
        return True
    except Exception as e:
        print(f"Error reading {filepath}: {str(e)}")
        return False

# Replace cleaners
print("\nInstalling Armenian cleaners...")
try:
    import TTS
    tts_path = TTS.__path__[0]
    cleaner_dest = os.path.join(tts_path, "tts", "utils", "text", "cleaners.py")
    
    # Debug: Print paths
    print(f"Source cleaner path: armenian_cleaners.py")
    print(f"Destination cleaner path: {cleaner_dest}")
    
    # Debug: Check if source exists
    if not os.path.exists("armenian_cleaners.py"):
        print("ERROR: armenian_cleaners.py not found!")
    else:
        print("Source cleaner file exists")
        
    # Copy the file
    shutil.copy("armenian_cleaners.py", cleaner_dest)
    print("Cleaner file copied successfully")
    
    # Verify the copy
    if debug_file_contents(cleaner_dest):
        print("Cleaner file contents verified")
    
    # Reload the cleaners module
    import importlib
    import TTS.tts.utils.text.cleaners as cleaners
    importlib.reload(cleaners)
    
    # Verify armenian_cleaners exists
    if hasattr(cleaners, 'armenian_cleaners'):
        print("armenian_cleaners function found in module")
    else:
        print("ERROR: armenian_cleaners function not found in module!")
        
except Exception as e:
    print(f"Error installing cleaners: {str(e)}")
    raise

# Download model files if they don't exist
print("Checking model files...")


model_loader.ensure_model_files()

# Initialize model
try:
    synthesizer = Synthesizer(
        tts_checkpoint="model/best_model.pth",
        tts_config_path="model/config.json",
        tts_speakers_file="model/speakers.pth",
        use_cuda=False
    )
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    raise

def text_to_speech(text, speaker):
    try:
        # Map speaker names to indices
        speaker_mapping = {
            'aram': 0,
            'narek': 1
        }
        speaker_idx = speaker_mapping[speaker]
        
        # Generate speech
        wav = synthesizer.tts(
            text=text,
            speaker_name=speaker,
            speaker_id=speaker_idx,
            noise_scale=0.3,
            length_scale=1.0,
            noise_scale_dp=0.3
        )
        
        # Create temporary file path
        output_path = "output.wav"
        synthesizer.save_wav(wav, output_path)
        
        return output_path
        
    except Exception as e:
        raise gr.Error(f"Error generating speech: {str(e)}")

# Create Gradio interface
demo = gr.Interface(
    fn=text_to_speech,
    inputs=[
        gr.Textbox(
            label="Armenian Text", 
            placeholder="Մուտքագրեք հայերեն տեքստ...",
            lines=3
        ),
        gr.Dropdown(
            choices=["aram", "narek"], 
            label="Speaker",
            value="aram"
        )
    ],
    outputs=gr.Audio(label="Generated Speech"),
    title="Armenian Text-to-Speech",
    description="Convert Armenian text to speech using multiple speakers.",
    examples=[
        ["Բարև, ինչպես ես?", "aram"],
        ["Իմ անունը Կարեն է:", "narek"],
        ["Ես սիրում եմ երաժշտություն:", "aram"],
    ]
)

if __name__ == "__main__":
    # Launch with public access and additional configurations
    demo.launch(
        share=True,  # This makes it public
        server_name="0.0.0.0",  # Allows external access
        server_port=7860,  # Default port
        show_error=True  # Shows detailed error messages
    )