#!/usr/bin/env bash
# Wrapper to activate conda env and run Stream Deck script

# Load environment variables from config.env
source "$(dirname "$0")/config.env"

# Load conda
source ~/miniconda3/etc/profile.d/conda.sh

# Activate env (update this to your environment name)
conda activate jarvis-busybee

# Run script using PROJECTS_DIR from config.env
exec python "${PROJECTS_DIR}/jarvis-streamdeck/jarvis/run_jarvis.py"
