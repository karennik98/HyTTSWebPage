from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import tempfile
import base64
from onnx_tts_helper import ONNXTTSHelper
import uvicorn
import logging

from model_loader import ensure_model_files

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure model files are available
ensure_model_files()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize TTS Helper outside the try block to make it available globally
tts_helper = None

try:
    logger.info("Initializing ONNX TTS Helper...")
    # Model paths
    MODEL_PATH = os.path.join("model", "model.onnx")  # Make sure this matches your actual file name
    CONFIG_PATH = os.path.join("model", "config.json")
    SPEAKERS_FILE = os.path.join("model", "speakers.pth")

    # Initialize ONNX TTS Helper
    tts_helper = ONNXTTSHelper(
        model_path=MODEL_PATH,
        config_path=CONFIG_PATH,
        speakers_file=SPEAKERS_FILE,
        use_cuda=False
    )
    logger.info("ONNX TTS Helper initialized successfully!")
except Exception as e:
    logger.error(f"Error initializing ONNX TTS Helper: {str(e)}")
    # Don't raise here, allow the app to start even if model loading fails
    # We'll handle this in the route handlers

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
        if tts_helper is None:
            raise HTTPException(status_code=503, detail="TTS service not initialized")
            
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
    return {"status": "healthy", "model_loaded": tts_helper is not None}

# Root route to ensure the app is responding
@app.get("/")
async def root():
    return {"message": "TTS API is running", "status": "ok"}

# This is critical for Render to detect the application
if __name__ == "__main__":
    # Get the port from environment variable with a fallback to 8000
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")