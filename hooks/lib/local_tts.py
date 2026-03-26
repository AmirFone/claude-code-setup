"""
Local TTS using macOS `say` command.
Zero external dependencies. Always works on macOS.
"""

import subprocess
import sys


# macOS voices - good defaults
VOICES = {
    "default": "Samantha",
    "male": "Daniel",
    "female": "Samantha",
}

DEFAULT_RATE = 400


def speak(message: str, rate: int = DEFAULT_RATE, voice: str = "", blocking: bool = False) -> None:
    if not message or not message.strip():
        return

    if sys.platform != "darwin":
        return

    cmd = ["say"]

    if rate != DEFAULT_RATE:
        cmd.extend(["-r", str(rate)])

    if voice:
        cmd.extend(["-v", voice])

    cmd.append(message.strip())

    try:
        if blocking:
            subprocess.run(cmd, capture_output=True, timeout=30)
        else:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
