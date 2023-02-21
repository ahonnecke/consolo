#!/usr/bin/env bash
# This installation script assumes that ~/bin/ is already in your path

CONSOLO="https://raw.githubusercontent.com/ahonnecke/consolo/e15cb77e534a3d37c2d78b0001f414e38078e738/consolo.py"


pip install argdantic boto3 requests watchdog zipfile
curl $CONSOLO --output ~/bin/consolo

chmod +x ~/bin/consolo
