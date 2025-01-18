import os
import gdown
from pathlib import Path

def download_model_files():
    """Download model files from Google Drive"""
    model_dir = Path("model")
    model_dir.mkdir(exist_ok=True)
    
    # Replace these with your Google Drive file IDs
    files = {
        'best_model.pth': '1bfdc4_-QS5IKw05LVXfAleKeEw7k6QaG',
        'config.json': '1yprwl5nGo-JMNqIS-NSlCTLyfgj-X6xD',
        'speakers.pth': '1ki2nlguHSHMYcSYV8SA1c8gWr05FPiju'
    }
    
    for filename, file_id in files.items():
        output_path = model_dir / filename
        if not output_path.exists():
            url = f'https://drive.google.com/uc?id={file_id}'
            gdown.download(url, str(output_path), quiet=False)

def ensure_model_files():
    """Ensure all model files are present"""
    required_files = ['best_model.pth', 'config.json', 'speakers.pth']
    model_dir = Path("model")
    
    # Check if all files exist locally
    all_files_exist = all((model_dir / f).exists() for f in required_files)
    
    if not all_files_exist:
        print("Downloading model files...")
        download_model_files()
    else:
        print("Model files already exist.")