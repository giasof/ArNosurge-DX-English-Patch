# Ar nosurge DX English Patch

An unofficial English localization patch for **Ar nosurge: Ode to an Unborn Star DX** on Windows. It imports dialogue and artwork from your US PS3 copy, adds an English launcher, and corrects Xbox button prompts and menu layout. Seven DX cinematics can also be rebuilt with English subtitles.

**[Download the patch](https://github.com/giasof/ArNosurge-DX-English-Patch/releases/latest)** · [Instructions en français](README.fr.md)

## Before you start

You need an unmodified, compatible Japanese Windows installation of DX and an extracted US PS3 copy (BLUS31478) for the main patch. The PS3 folder must have `Event`, `Saves` and `Data` directories inside `PS3_GAME/USRDIR`. You can also select `USRDIR` directly. The optional movie installer reads the original DX videos.

1. Install 64-bit Python with Tkinter. The tested version is Python 3.12. Install Pillow in the same Python environment with `py -3 -m pip install Pillow==13.0.0`. [Python for Windows](https://www.python.org/downloads/windows/) · [Pillow documentation](https://pillow.readthedocs.io/en/stable/)
2. Extract the Windows release of Gust Tools and keep `gust_pak.exe` handy. The installer asks you to select it. [Gust Tools releases](https://github.com/VitaSmith/gust_tools/releases)
3. For movie subtitles, obtain a Windows FFmpeg build with the `ass` and `removelogo` filters. Keep `ffmpeg.exe` and `ffprobe.exe` together. The movie encoder uses Windows Media components. [FFmpeg downloads](https://ffmpeg.org/download.html)

## Install

1. Extract the patch ZIP to its own folder. Close the game and the launcher.
2. Double-click **Setup.cmd**. Choose **1** to check the files, then run it again and choose **2** to install. Select the DX folder, the US PS3 folder and `gust_pak.exe`.
3. To install movie subtitles, run **Setup.cmd** again and choose **3**. Select the DX folder and `ffmpeg.exe`. Encoding all seven 1080p movies takes time. Progress appears in the console.
4. Launch the game normally. **Settings** opens the configuration window and **Play** starts the game. The launcher includes borderless fullscreen, a 100–200% rendering scale and the Xbox confirm/back preference.

The installer verifies source hashes and stages replacements before applying them. It saves the originals in `ArnosurgeDX-patch-backup` inside the game folder. Keep that folder. Choose **4** to restore the files installed by this patch. After an interruption, rerun the installer to recover from its journal. Game progress and save slots are outside the installer's file list.

## Coverage and compatibility

- The dialogue patch reads 46,887 changed lines from matching PS3 records and applies DX-specific line wrapping. Some DX-only dialogue has no US PS3 counterpart and remains Japanese.
- The patch covers inventory, equipment, status, encyclopedia, battle results, synthesis, purification, history and other menu resources. It rebuilds 50 tutorial illustrations locally and adjusts the layout of entries unlocked later in the game.
- English subtitles cover `opening`, `prologue`, `tm_felion_D` and `seq02` through `seq05`. The installer checks stream profiles, frame counts, timestamps and original compressed audio after encoding.
- The game program and both data archives have reference SHA-256 hashes. The graphics archive also matched its reference in testing. Fonts, Windows components and encoder versions can affect the bytes of locally rendered files. The installer records their actual hashes for verification and restoration.
- All source hashes are listed in `patch/files.json`. A hash mismatch reports an unsupported or modified installation. The patch is version-specific. Some locked screens have been checked from their resources and still need visual testing in gameplay.

## Command line

Run these commands from the extracted patch directory. Substitute your own paths.

```powershell
py -3 install.py check --game "D:\Games\ArnosurgeDX"
py -3 install.py install --game "D:\Games\ArnosurgeDX" --ps3 "D:\Games\BLUS31478" --gust "D:\Tools\gust_pak.exe"
py -3 install.py movies --game "D:\Games\ArnosurgeDX" --ffmpeg "D:\Tools\FFmpeg\bin\ffmpeg.exe"
py -3 install.py restore --game "D:\Games\ArnosurgeDX"
```

## Package contents and credits

`patch/` contains binary differences, hashes, layout edits and instructions for reading dialogue from local PS3 files. `subtitles/` contains timed English text and lettering masks. The English launcher is compiled locally from C# using the Windows .NET Framework compiler. The only executable shipped in the patch is the small Windows Media encoder helper, with its C++ source in `tools/`.

The Gust XML codec comes from the Ar nosurge DX Korean translation project. Its original license is in `third_party/LICENSE-gust-xml.txt`. Gust Tools and FFmpeg are separate projects. Ar nosurge and its original materials belong to their respective owners. [XML codec source](https://github.com/TAMTAMQ/Ar-nosurge-korean-translation-patch/blob/3b6cd6e469177edf39b44ca7091aa4c6d339dc6a/tools/decode_saves_xml_e.py)
