# Ar nosurge DX English Patch

An unofficial English localization patch for **Ar nosurge: Ode to an Unborn Star DX** on Windows. It imports dialogue and artwork from your US Vita Plus copy, adds an English launcher, and corrects Xbox button prompts and menu layout. The optional movie installer adds English text to 34 DX cinematics.

**[Download the portable Windows x64 ZIP](https://github.com/giasof/ArNosurge-DX-English-Patch/releases/latest/download/ArNosurge-DX-English-Patch-Windows-x64.zip)** · [Instructions en français](README.fr.md)

## Before you start

You need a compatible Japanese Windows installation of DX and a readable US Vita copy of **Ar nosurge Plus** (PCSE00707). Select the Vita folder containing `Data/PSVita/resources1.psarc`, or the folder containing the archive itself. An installed Vita3K app can be found under `ux0/app/PCSE00707` in its storage folder. Setup checks the archive before building any game files. Encrypted Vita backups must first be exported in readable form. The optional movie installer reads the original DX videos.

The portable ZIP includes everything the patch needs on a standard Windows 10 or 11 x64 installation. Setup works offline. The optional movies use Windows Media components. Windows N editions need the Windows Media Feature Pack for that option.

## Install

1. Extract the entire **ArNosurge-DX-English-Patch-Windows-x64.zip** to its own folder, close the game and its launcher, and open **Setup.exe**.
2. Under **Windows DX folder**, select the folder containing `ArnosurgeDX.exe`. **Check files** verifies the installation.
3. Under **US Vita Plus folder (PCSE00707)**, select your extracted US Vita game, then click **Install patch**. When Setup reports **Done**, open the game launcher and click **Play**. **Settings** includes borderless fullscreen, a 100–200% rendering scale and the Xbox confirm/back preference.
4. For English movie subtitles, select **Subtitle movies**. Only the DX folder is needed. Leave Setup open while it rebuilds the 1080p videos. If you already use the patch, keep its backup folder and run **Install patch** and **Subtitle movies** again. Setup skips files that are already up to date. The window displays progress.

The installer verifies source hashes and stages replacements before applying them. It saves the originals in `ArnosurgeDX-patch-backup` inside the game folder. Keep that folder. Click **Restore originals** to restore the files installed by this patch. After an interruption, rerun the installer to recover from its journal. Game progress and save slots are outside the installer's file list.

## Coverage and compatibility

- Version 1.4.0 reads 51,854 dialogue records from US Vita Plus across 2,241 event files. It keeps the DX event headers and adapts line breaks to the PC font. An additional 65 records already match DX.
- All three extra purification partners are included. Shurelia, Nelo and Sarly have 49 conversations each, plus six introduction scenes between them. Hardware-specific tutorial lines use DX controller prompts. Shared tutorial illustrations come from the Vita archive, and PC-specific instructional cards are rebuilt for DX.
- All 1,790 conversation choices are in English. The patch also translates 1,428 field dialogue entries and adjusts the choice window and NPC line breaks.
- Map destinations, districts, shops, 22 location descriptions and 30 Genometrics illustrations have English labels. The update also covers 35 encyclopedia help images, four glossary illustrations, prize cards, the animated DX title screen and all five credit rolls.
- The patch covers inventory, equipment, status, encyclopedia, battle results, synthesis, purification, history and other menu resources. It rebuilds 50 tutorial illustrations locally and adjusts the layout of entries unlocked later in the game.
- The patch translates Cass and Ion’s battle callouts, Song Magic affinities and availability, and the Cast Song command menu. It also fixes line breaks in 81 tutorial and system messages.
- On an Xbox controller, **A** activates the bottom command (including **Stampede**) and **B** guards during the enemy turn. The command icons match both at rest and when highlighted. The launcher’s confirm/back setting applies to menus.
- The mouse pointer hides while the game window is active and returns when you switch applications or minimize the game.
- English subtitles cover `opening`, `prologue`, `tm_felion_D` and `seq02` through `seq05`. Also included are the 18 Genometrics endings, five city arrivals and four fortunes. The city captions follow the moving nameplate. Fortune calligraphy is accompanied by an English subtitle. The installer checks stream profiles, frame counts, timestamps and original compressed audio after encoding.
- The game program and both data archives have reference SHA-256 hashes. The graphics archive also matched its reference in testing. Fonts, Windows components and encoder versions can affect the bytes of locally rendered files. The installer records their actual hashes for verification and restoration.
- All source hashes are listed in `patch/files.json`. A hash mismatch reports an unsupported or modified installation. The patch is version-specific. Some locked screens have been checked from their resources and still need visual testing in gameplay.

## Special K users

If a **Missing interface** dialog mentioning **SteamInput007** appears with Special K active, close the game and open its existing Special K profile at `Profiles/ArnosurgeDX.exe/SpecialK.ini`. Under `[Steam.Log]`, set `Silent=true`, then relaunch the game.

## Command line

From the extracted portable folder, substitute your own paths.

```powershell
.\Setup.cmd check --game "D:\Games\ArnosurgeDX"
.\Setup.cmd install --game "D:\Games\ArnosurgeDX" --vita "D:\Games\PCSE00707"
.\Setup.cmd movies --game "D:\Games\ArnosurgeDX"
.\Setup.cmd restore --game "D:\Games\ArnosurgeDX"
```

## Package contents and credits

**giasof** leads the project and tested the English menus, Xbox controls and cinematics in game. **OpenAI Codex** contributed as an AI coding assistant, developing the patch and portable installer and testing installation and restoration.

The release ZIP contains the patch instructions, timed subtitles and lettering masks, English launcher, Windows installer and the tools they use. The installer reads game files, artwork and movie streams from local game copies. The repository also contains the installer and launcher sources. [Portable tool versions, licenses and build instructions](third_party/PORTABLE.md)

The Gust XML codec comes from the Ar nosurge DX Korean translation project. Its original license is in `third_party/LICENSE-gust-xml.txt`. Ar nosurge and its original materials belong to their respective owners. [XML codec source](https://github.com/TAMTAMQ/Ar-nosurge-korean-translation-patch/blob/3b6cd6e469177edf39b44ca7091aa4c6d339dc6a/tools/decode_saves_xml_e.py)
