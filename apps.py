import subprocess
import difflib
from speech import speak

APPS = {
    "notepad": "notepad",
    "calculator": "calc",
    "cmd": "cmd",
    "powershell": "powershell",
    "explorer": "explorer",

    "chrome": "start chrome",
    "edge": "start msedge",
    "firefox": "start firefox",

    "vscode": "start code",
    "vlc": "start vlc",

    "spotify": "start shell:AppsFolder\\SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify",
    "whatsapp": "start shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!WhatsApp",
    "discord": "start shell:AppsFolder\\Discord.Discord_79j3eq4aw64v6!Discord",
}

def find_best_app_match(app_name):
    matches = difflib.get_close_matches(
        app_name.lower(), APPS.keys(), n=1, cutoff=0.5
    )
    return APPS[matches[0]] if matches else None

def open_app(app_command):
    try:
        subprocess.Popen(
            app_command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        speak("Opening application")
        return True
    except:
        speak("I couldn't open that application")
        return False
