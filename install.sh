#!/usr/bin/env bash
# This installation script assumes that ~/bin/ is already in your path

CONSOLO="https://raw.githubusercontent.com/ahonnecke/consolo/main/consolo.py"
DEST="${HOME}/bin/consolo"

pip install argdantic boto3 requests watchdog zipfile && \
curl $CONSOLO --output "$DEST" && \
chmod +x "$DEST"
