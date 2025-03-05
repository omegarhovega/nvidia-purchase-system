import os
import subprocess
import threading
import sys
import importlib.util
from pathlib import Path
from logger import logger

# Check if playsound is installed, if not, install it
if importlib.util.find_spec("playsound") is None:
    logger.info("Installing playsound module...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playsound==1.2.2"])
        logger.info("Successfully installed playsound module")
    except Exception as e:
        logger.error(f"Failed to install playsound module: {e}")
        # Continue execution, we'll fall back to other methods

def get_sound_path(sound_name):
    """
    Gets the full path to a sound file in the shared/assets/sounds directory.
    
    Args:
        sound_name: Name of the sound file (e.g., 'alert_down.mp3')
    
    Returns:
        str: Full path to the sound file
    """
    # Get the base directory (parent of cookie-prep)
    base_dir = Path(__file__).resolve().parent.parent.parent
    return os.path.join(base_dir, "shared", "assets", "sounds", sound_name)

def play_sound(sound_name, blocking=True):
    """
    Plays a sound file, with option to block until completion.
    
    Args:
        sound_name: Name of the sound file (e.g., 'alert_down.mp3')
        blocking: Whether to block until the sound finishes playing
    """
    sound_path = get_sound_path(sound_name)
    
    if not os.path.exists(sound_path):
        logger.error(f"Sound file not found: {sound_path}")
        return
    
    def _play_sound():
        try:
            # Try to use playsound first
            try:
                from playsound import playsound
                playsound(sound_path, block=True)
                logger.info(f"Sound played with playsound: {sound_path}")
                return
            except (ImportError, Exception) as e:
                logger.warning(f"Failed to use playsound module: {e}")
                
            # Fallback methods by platform
            if sys.platform == 'win32':
                # Use simple command-line method for Windows
                try:
                    powershell_cmd = f"powershell -c (New-Object System.Media.SoundPlayer '{sound_path}').PlaySync();"
                    subprocess.run(powershell_cmd, shell=True, check=True)
                    logger.info(f"Sound played with PowerShell: {sound_path}")
                    return
                except Exception as e:
                    logger.warning(f"Failed to play with PowerShell: {e}")
                    
                # Try winsound as a last resort
                try:
                    import winsound
                    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                    logger.info(f"Played system asterisk sound using winsound")
                    return
                except Exception as e:
                    logger.warning(f"Failed to play with winsound: {e}")
                    
            elif sys.platform == 'darwin':
                # macOS - use afplay
                subprocess.run(["afplay", sound_path], check=True)
                logger.info(f"Sound played with afplay: {sound_path}")
                return
            else:
                # Linux - use mplayer or other available players
                players = [
                    ["mplayer", sound_path],
                    ["mpg123", sound_path],
                    ["mpg321", sound_path],
                    ["aplay", sound_path],
                ]
                
                for player in players:
                    try:
                        subprocess.run(player, check=True)
                        logger.info(f"Sound played with {player[0]}: {sound_path}")
                        return
                    except (subprocess.SubprocessError, FileNotFoundError):
                        continue
            
            logger.warning(f"Could not find a suitable method to play sound on this system")
                
        except Exception as e:
            logger.error(f"Failed to play sound '{sound_path}': {e}")
    
    if blocking:
        _play_sound()
    else:
        threading.Thread(target=_play_sound).start()

def play_error_alert():
    """Plays the error alert sound (alert_down.mp3)"""
    play_sound("alert_down.mp3")
