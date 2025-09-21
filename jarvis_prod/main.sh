#!/usr/bin/env bash
# Bash script to activate conda env and run jarvis script

# Load environment variables from config.env (located in config directory)
source "$(dirname "$0")/config/config.env"

# Load conda
source ~/miniconda3/etc/profile.d/conda.sh

# Activate env (update this to your environment name)
conda activate jarvis-busybee

# Run script using PROJECTS_DIR from config.env (use main.py entry point)
exec python "${PROJECTS_DIR}/jarvis-streamdeck/jarvis/main.py"
