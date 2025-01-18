from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import tempfile
import base64
from tts_helper import TTSHelper
import uvicorn
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    logger.info("Initializing TTS Helper...")
    # Model paths
    MODEL_PATH = os.path.join("model", "best_model.pth")
    CONFIG_PATH = os.path.join("model", "config.json")
    SPEAKERS_FILE = os.path.join("model", "speakers.pth")

    # Initialize TTS Helper
    tts_helper = TTSHelper(
        model_path=MODEL_PATH,
        config_path=CONFIG_PATH,
        speakers_file=SPEAKERS_FILE,
        use_cuda=False
    )
    logger.info("TTS Helper initialized successfully!")
except Exception as e:
    logger.error(f"Error initializing TTS Helper: {str(e)}")
    raise

class TTSRequest(BaseModel):
    text: str
    speaker_name: str

# Speaker mapping
SPEAKER_MAPPING = {
    'aram': 0,
    'narek': 1
}

@app.post("/api/synthesize")
async def synthesize(request: TTSRequest):
    try:
        logger.info(f"Received synthesis request for speaker: {request.speaker_name}")
        speaker_idx = SPEAKER_MAPPING.get(request.speaker_name)
        if speaker_idx is None:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid speaker. Available speakers: {list(SPEAKER_MAPPING.keys())}"
            )

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            # Generate and save audio
            wav = tts_helper.generate_speech(
                text=request.text,
                speaker_name=request.speaker_name,
                speaker_idx=speaker_idx
            )
            tts_helper.save_audio(wav, tmp_file.name)
            
            # Read and encode audio
            with open(tmp_file.name, "rb") as audio_file:
                audio_data = base64.b64encode(audio_file.read()).decode()
            
            # Clean up
            os.unlink(tmp_file.name)
            
            return {
                "success": True,
                "audio": audio_data
            }
            
    except Exception as e:
        logger.error(f"Error in synthesis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/speakers")
async def get_speakers():
    return {"speakers": list(SPEAKER_MAPPING.keys())}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")