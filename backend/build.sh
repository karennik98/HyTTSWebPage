#!/bin/bash

# Install requirements
pip install -r requirements.txt

# Install our custom cleaners
chmod +x install_cleaners.sh
./install_cleaners.sh