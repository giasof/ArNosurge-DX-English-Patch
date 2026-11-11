# Ar nosurge DX English Patch

An unofficial English localization patch for **Ar nosurge: Ode to an Unborn Star DX** on Windows. It imports dialogue and artwork from your US PS3 copy, adds an English launcher, and corrects Xbox button prompts and menu layout. Seven DX cinematics can also be rebuilt with English subtitles.

**[Download the portable Windows x64 ZIP](https://github.com/giasof/ArNosurge-DX-English-Patch/releases/latest/download/ArNosurge-DX-English-Patch-Windows-x64.zip)** · [Instructions en français](README.fr.md)

## Before you start

You need an unmodified, compatible Japanese Windows installation of DX and an extracted US PS3 copy (BLUS31478) for the main patch. The PS3 folder must have `Event`, `Saves` and `Data` directories inside `PS3_GAME/USRDIR`. You can also select `USRDIR` directly. The optional movie installer reads the original DX videos.

The portable ZIP includes everything the patch needs on a standard Windows 10 or 11 x64 installation. Setup works offline. The optional movies use Windows Media components. Windows N editions need the Windows Media Feature Pack for that option.

## Install

1. Extract the entire **ArNosurge-DX-English-Patch-Windows-x64.zip** to its own folder, close the game and its launcher, and open **Setup.exe**.
2. Under **Windows DX folder**, select the folder containing `ArnosurgeDX.exe`. **Check files** verifies the installation.
3. Under **US PS3 folder (main patch)**, select the extracted US PS3 game, then click **Install patch**. When Setup reports **Done**, open the game launcher and click **Play**. **Settings** includes borderless fullscreen, a 100–200% rendering scale and the Xbox confirm/back preference.
4. For English movie subtitles, select **Subtitle movies**. Only the DX folder is needed. Leave Setup open while it rebuilds the seven 1080p videos. The window displays progress.

If the previous release is installed, the new portable Setup recognizes its backup and installed files. An already patched game needs no reinstall to use this release.

The installer verifies source hashes and stages replacements before applying them. It saves the originals in `ArnosurgeDX-patch-backup` inside the game folder. Keep that folder. Click **Restore originals** to restore the files installed by this patch. After an interruption, rerun the installer to recover from its journal. Game progress and save slots are outside the installer's file list.

## Coverage and compatibility

- The dialogue patch reads 46,887 changed lines from matching PS3 records and applies DX-specific line wrapping. Some DX-only dialogue has no US PS3 counterpart and remains Japanese.
- The patch covers inventory, equipment, status, encyclopedia, battle results, synthesis, purification, history and other menu resources. It rebuilds 50 tutorial illustrations locally and adjusts the layout of entries unlocked later in the game.
- English subtitles cover `opening`, `prologue`, `tm_felion_D` and `seq02` through `seq05`. The installer checks stream profiles, frame counts, timestamps and original compressed audio after encoding.
- The game program and both data archives have reference SHA-256 hashes. The graphics archive also matched its reference in testing. Fonts, Windows components and encoder versions can affect the bytes of locally rendered files. The installer records their actual hashes for verification and restoration.
- All source hashes are listed in `patch/files.json`. A hash mismatch reports an unsupported or modified installation. The patch is version-specific. Some locked screens have been checked from their resources and still need visual testing in gameplay.

## Command line

From the extracted portable folder, substitute your own paths.

```powershell
.\Setup.cmd check --game "D:\Games\ArnosurgeDX"
.\Setup.cmd install --game "D:\Games\ArnosurgeDX" --ps3 "D:\Games\BLUS31478"
.\Setup.cmd movies --game "D:\Games\ArnosurgeDX"
.\Setup.cmd restore --game "D:\Games\ArnosurgeDX"
```

## Package contents and credits

**giasof** leads the project and tested the English menus, Xbox controls and cinematics in game. **OpenAI Codex** contributed as an AI coding assistant, developing the patch and portable installer and testing installation and restoration.

The release ZIP contains the patch instructions, timed subtitles and lettering masks, English launcher, Windows installer and the tools they use. The installer reads game files, artwork and movie streams from local game copies. The repository also contains the installer and launcher sources. [Portable tool versions, licenses and build instructions](third_party/PORTABLE.md)

The Gust XML codec comes from the Ar nosurge DX Korean translation project. Its original license is in `third_party/LICENSE-gust-xml.txt`. Ar nosurge and its original materials belong to their respective owners. [XML codec source](https://github.com/TAMTAMQ/Ar-nosurge-korean-translation-patch/blob/3b6cd6e469177edf39b44ca7091aa4c6d339dc6a/tools/decode_saves_xml_e.py)
