#!/usr/bin/env bash
# Wrapper to activate conda env and run Stream Deck script

# Load conda
source ~/miniconda3/etc/profile.d/conda.sh

# Activate env
conda activate jarvis-mamba

# Run script
exec python ~/Zenith/Jarvis/jarvis-streamdeck/run_jarvis.py
