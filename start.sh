#!/bin/bash

# Load variables from .env
set -a
source .env
set +a

# Check if variables are set
if [[ -z "$SSH_USERNAME" || -z "$SSH_REMOTE_IP" ]]; then
  echo "Missing SSH_USERNAME or SSH_REMOTE_IP in .env"
  exit 1
fi

# Starts the reverse SSH tunnel
ssh -i ~/.ssh/id_rsa -N -R 11434:localhost:11434 $REMOTE_USER@$REMOTE_HOST
