# Portable Windows components

The Windows x64 package carries its private interpreter, image library, archive tool and media tools in its own directory. Setup.exe and EnglishLauncher.exe are compiled from this project's C# sources. The Windows Media helper and its source are under `tools/`. All movie and game data are read from the player's copies.

| Component | Binary used for this build | Source and notices |
| --- | --- | --- |
| CPython 3.13.16 | [Official embeddable Windows x64 ZIP](https://www.python.org/ftp/python/3.13.16/python-3.13.16-embed-amd64.zip) | [CPython sources](https://github.com/python/cpython/tree/v3.13.16). The distribution includes `runtime/LICENSE.txt`. |
| Pillow 13.0.0 | [Official CPython 3.13 Windows x64 wheel](https://files.pythonhosted.org/packages/d7/ed/1b16fb66a37e1b9e41370b93b2c614c7da761a5b2a41dc333f7af4639962/pillow-13.0.0-cp313-cp313-win_amd64.whl) | [Pillow sources](https://github.com/python-pillow/Pillow/tree/13.0.0). See `runtime/pillow-13.0.0.dist-info/licenses/LICENSE`. |
| Gust Tools v1.58 | [Upstream Windows ZIP](https://github.com/VitaSmith/gust_tools/releases/download/v1.58/gust_tools.zip) | [Source revision](https://github.com/VitaSmith/gust_tools/tree/c69159d73a8204188c072ec87e476a3f40287f03). See `tools/gust/LICENSE.txt`. |
| FFmpeg 8.1.3, shared LGPL build | [FFmpeg-Builds Windows x64 ZIP](https://github.com/FFmpeg-Builds/FFmpeg-Builds/releases/download/autobuild-2026-11-11-12-39/ffmpeg-n8.1.3-35-gf1acb0a266-win64-lgpl-shared-8.1.zip) | [FFmpeg source revision](https://github.com/FFmpeg/FFmpeg/tree/f1acb0a2666c78d92688f4c3d2803a132f5590f6) and [build scripts, patches and dependency sources](https://github.com/FFmpeg-Builds/FFmpeg-Builds/tree/c9fe5114060e507409f7ee07edfd82efaf25d767). See `tools/ffmpeg/LICENSE.txt`. |

The release also provides a separate archive of the FFmpeg and Gust Tools source revisions and the FFmpeg build scripts. FFmpeg and ffprobe run as separate programs with their replaceable DLLs. The upstream FFmpeg build target is `win64 lgpl-shared 8.1`.

To assemble the portable ZIP, save the four binary downloads above as `python.zip`, `pillow.whl`, `gust_tools.zip` and `ffmpeg.zip` in one directory. On a Windows build machine with Python 3.11 or later, run `python tools/build_portable.py INPUTS OUTPUT.zip`. The script verifies their SHA-256 hashes before packaging.
