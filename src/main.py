"""
main.py
Orchestrates detection of sink, configuring system audio, authenticating to Spotify,
transferring playback, playing playlist, and setting volumes.
"""

# Standard libraries
import os
import logging
import time
import subprocess
import threading
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")


def play_youtube_video(url):
    """Play YouTube video audio using yt-dlp and mpv/vlc"""
    try:
        logging.info("Playing YouTube video: %s", url)

        # Try mpv first (more lightweight), fallback to vlc
        players = ["cvlc"]

        for player in players:
            try:
                cmd = [
                    "vlc",
                    "--intf",
                    "dummy",
                    "--no-video",
                    "--play-and-exit",
                    url,
                ]

                logging.info("Attempting to play with %s", player)
                result = subprocess.run(cmd, timeout=60, capture_output=True, text=True)

                if result.returncode == 0:
                    logging.info("YouTube video playback completed with %s", player)
                    return
                else:
                    logging.warning("%s failed: %s", player, result.stderr)

            except subprocess.TimeoutExpired:
                logging.warning("%s timed out after 60 seconds", player)
                continue
            except FileNotFoundError:
                logging.warning("%s not found, trying next player", player)
                continue
            except Exception as e:
                logging.warning("Error with %s: %s", player, e)
                continue

        logging.error("All players failed to play YouTube video")

    except Exception as e:
        logging.error("Error playing YouTube video: %s", e)


# Local helpers
try:
    from .spotify_client import (
        make_client,
        find_device,
        transfer_playback,
        start_playlist,
        set_spotify_volume,
    )
    from .pipewire import (
        detect_sink_by_friendly_name,
        set_default_sink,
        set_sink_volume_percent,
    )
except ImportError:
    from spotify_client import (
        make_client,
        find_device,
        transfer_playback,
        start_playlist,
        set_spotify_volume,
    )
    from pipewire import (
        detect_sink_by_friendly_name,
        set_default_sink,
        set_sink_volume_percent,
    )

# Configure logging to file and stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler("logs/play.log"), logging.StreamHandler()],
)


def main():
    # Play YouTube video first
    youtube_url = "./assets/l'internationale.mp3"
    play_youtube_video(youtube_url)

    # Read configuration from environment
    target_device = os.environ.get("TARGET_DEVICE_NAME", "gothgirlfriend")
    friendly_sink = os.environ.get("TARGET_SINK_FRIENDLY_NAME", "USB audio speakers")
    playlist_uri = os.environ.get("SPOTIFY_RACER_PLAYLIST_URI")
    if not playlist_uri:
        logging.error("SPOTIFY_RACER_PLAYLIST_URI not set in environment.")
        return

    logging.info("Detecting sink matching friendly name: %s", friendly_sink)
    sink = detect_sink_by_friendly_name(friendly_sink)
    if sink:
        logging.info("Found sink: %s; setting as default", sink)
        set_default_sink(sink)
        logging.info("Setting sink volume to 100%%")
        set_sink_volume_percent(sink, 100)
    else:
        logging.info(
            "Sink not found: %s; continuing without changing default sink",
            friendly_sink,
        )

    logging.info("Authenticating to Spotify")
    sp = make_client()

    logging.info("Looking for Spotify device: %s", target_device)
    device = find_device(sp, target_device)
    device_id = None
    if device:
        device_id = device.get("id")
        logging.info("Found device id: %s; transferring playback", device_id)
        transfer_playback(sp, device_id, play=True)
        logging.info("Setting Spotify volume to 100%% on device")
        set_spotify_volume(sp, 90, device_id)
    else:
        logging.info(
            "Device not found: %s; attempting to start playback on current active device",
            target_device,
        )
        # Try to start playback without specifying device; Spotify may use the last active device.
        set_spotify_volume(sp, 90, None)

    logging.info("Starting playlist: %s", playlist_uri)
    start_playlist(sp, playlist_uri, device_id if device else None)

    logging.info("All actions executed. Exiting.")


if __name__ == "__main__":
    main()
