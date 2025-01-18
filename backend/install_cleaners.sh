#!/bin/bash

# Get TTS installation path
TTS_PATH=$(python -c "import TTS; print(TTS.__path__[0])")

# Copy our cleaners.py to TTS installation
cp tts_override/TTS/tts/utils/text/cleaners.py "$TTS_PATH/tts/utils/text/cleaners.py"