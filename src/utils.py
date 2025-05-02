import os

def is_flatpak():
    """
    Detect if the current process is running inside a Flatpak sandbox.
    Returns True if in Flatpak, False otherwise.
    """
    return os.path.exists('/.flatpak-info')
