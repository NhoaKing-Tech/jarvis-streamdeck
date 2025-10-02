#!/usr/bin/env bash
# Bash script to activate conda env and run jarvis script

# dirname "$0" gets the directory of the current script, which is jarvis-streamdeck/jarvis
# Load environment variables from config.env (located in jarvis/config directory)
source "$(dirname "$0")/config/config.env"

# Load conda
source ~/miniconda3/etc/profile.d/conda.sh

# Activate env (update this to your environment name, where you installed the dependencies, mainly pip install -e . for the StreamDeck package coming from the upstream repo)
conda activate jarvis-busybee

# Run script using PROJECTS_DIR from config.env (run as Python module)
cd "${PROJECTS_DIR}/jarvis-streamdeck"
exec python -m jarvis
