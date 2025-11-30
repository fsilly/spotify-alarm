"""
spotify_client.py
Provides Spotify authentication and playback-control helpers.
"""

# Import required libraries.
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import os
import time
from typing import Optional

# Scopes required for controlling playback and reading devices.
SCOPE = "user-modify-playback-state user-read-playback-state user-read-currently-playing"

def make_client():
    """
    Create and return a Spotipy client using environment-based credentials.
    """
    # Read required environment variables for OAuth
    client_id = os.environ.get("SPOTIPY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.environ.get("SPOTIPY_REDIRECT_URI")
    username = os.environ.get("SPOTIFY_USERNAME")

    # Create OAuth manager
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=SCOPE,
        username=username,
        cache_path="./secrets/cache-spotify-" + (username or "default")
    )

    # Create client
    sp = Spotify(auth_manager=auth_manager)
    return sp

def find_device(sp: Spotify, target_name: str):
    """
    Return device dict matching the provided target_name, or None if not found.
    """
    # Request user's devices
    devices = sp.devices().get("devices", [])
    for d in devices:
        # Compare case-insensitively against device name
        if d.get("name") and d["name"].lower() == target_name.lower():
            return d
    # If exact match not found, try contains match
    for d in devices:
        if d.get("name") and target_name.lower() in d["name"].lower():
            return d
    return None

def transfer_playback(sp: Spotify, device_id: str, play: bool = True):
    """
    Transfer playback to device_id. play=True to start immediate transfer.
    """
    sp.transfer_playback(device_id=device_id, force_play=play)

def start_playlist(sp: Spotify, playlist_uri: str, device_id: Optional[str] = None):
    """
    Start playback of the given playlist URI on the given device_id (optional).
    """
    # Use start-playback with context_uri
    sp.start_playback(device_id=device_id, context_uri=playlist_uri)

def set_spotify_volume(sp: Spotify, percent: int, device_id: Optional[str] = None):
    """
    Set Spotify volume to given percent for device_id (0-100).
    """
    sp.volume(percent, device_id=device_id)
