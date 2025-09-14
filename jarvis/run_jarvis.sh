#!/usr/bin/env bash
# Wrapper to activate conda env and run Stream Deck script

# Load conda
source ~/miniconda3/etc/profile.d/conda.sh

# Activate env
conda activate jarvis-busybee

# Run script
exec python ~/Zenith/jarvis-streamdeck/jarvis/run_jarvis.py
