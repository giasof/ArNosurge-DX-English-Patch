"""Folder picker for the command-line installer."""
import shutil
import subprocess
import sys
from pathlib import Path
from tkinter import Tk, filedialog

def main():
    options = {"1":"check","2":"install","3":"movies","4":"restore"}
    print("Ar nosurge DX\n1  Check / Vérifier\n2  Install / Installer le patch"
          "\n3  Movie subtitles / Sous-titrer les cinématiques"
          "\n4  Restore original files / Restaurer les originaux")
    action=options.get(input("> ").strip())
    if not action:return 0
    root=Tk();root.withdraw()
    try:
        game=filedialog.askdirectory(title="DX installation / Dossier du jeu DX",mustexist=True)
        if not game:return 0
        args=[action,"--game",game]
        if action=="install":
            donor=filedialog.askdirectory(title="US Vita Plus (PCSE00707) / Dossier de la version Vita américaine",mustexist=True)
            if not donor:return 0
            args.extend(("--vita",donor))
        if action in ("install","movies"):
            name,flag=("gust_pak.exe","--gust") if action=="install" else ("ffmpeg.exe","--ffmpeg")
            path=shutil.which(name) or filedialog.askopenfilename(title="Select / Sélectionner "+name,filetypes=[(name,name)])
            if not path:return 0
            args.extend((flag,path))
    finally:root.destroy()
    return subprocess.run([sys.executable,"-B",str(Path(__file__).with_name("install.py")),*args]).returncode
if __name__=="__main__":sys.exit(main())
