#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p ./logs
mkdir -p ./secrets/
touch ./logs/play.log

echo "[SETUP] Installing Poetry dependencies..."
poetry install --no-root

mkdir -p logs ~/.config/systemd/user




SERVICE_FILE="./service/spotify-autoplay.service"
CURRENT_DIR="$(pwd)"

# Escape slashes for sed
ESCAPED_DIR=$(printf '%s\n' "$CURRENT_DIR" | sed 's/[\/&]/\\&/g')

# Replace WorkingDirectory line
sed -i "s|^WorkingDirectory=.*|WorkingDirectory=$ESCAPED_DIR|" "$SERVICE_FILE"

echo "[SETUP] Succesfully setup service CWD as $(pwd)"


echo "[SETUP] Installing systemd user service and timer..."
cp service/spotify-autoplay.service ~/.config/systemd/user/
cp service/spotify-autoplay.timer ~/.config/systemd/user/

systemctl --user daemon-reload
systemctl --user enable --now spotify-autoplay.timer

echo "[SETUP COMPLETE]"
echo "Timer is active. Check with: systemctl --user list-timers spotify-autoplay*"
