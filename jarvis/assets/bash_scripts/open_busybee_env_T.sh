#!/usr/bin/env bash
gnome-terminal -- bash -l -c '
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate busybee
    cd ~/Zenith/busybee
    echo ">>> ENV: $CONDA_DEFAULT_ENV <<<"
    which python
    exec bash -i
'
