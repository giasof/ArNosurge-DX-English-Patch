# Installer le patch anglais d’Ar nosurge DX

Le jeu et le lanceur passent en anglais. Le patch se construit sur ton PC à partir de ta version **DX Windows japonaise** et de ta version **PS3 américaine BLUS31478** extraite. Tu peux installer les sous-titres des cinématiques séparément avec la version DX.

1. Télécharge le ZIP de la version publiée et extrais-le dans un dossier à part. [Télécharger le patch](https://github.com/giasof/ArNosurge-DX-English-Patch/releases/latest)
2. Installe Python 3.12 64 bits avec Tkinter. Dans PowerShell, exécute `py -3 -m pip install Pillow==13.0.0`. Télécharge et extrais Gust Tools pour obtenir `gust_pak.exe`. [Python pour Windows](https://www.python.org/downloads/windows/) · [Gust Tools](https://github.com/VitaSmith/gust_tools/releases)
3. Ferme le jeu et son lanceur. Ouvre **Setup.cmd**, choisis **1** et sélectionne le dossier qui contient `ArnosurgeDX.exe`. Le contrôle compare tes fichiers aux versions prises en charge.
4. Ouvre de nouveau **Setup.cmd** et choisis **2**. Sélectionne le dossier DX, le dossier du jeu PS3 contenant `PS3_GAME` (ou directement `USRDIR`), puis `gust_pak.exe`. Une fois l’installation vérifiée, ouvre le lanceur et clique sur **Play**.
5. Pour les sous-titres, choisis **3**. Il te faut une version Windows de FFmpeg avec les filtres `ass` et `removelogo`, et `ffprobe.exe` à côté de `ffmpeg.exe`. Les sept vidéos sont réencodées en 1080p en conservant les pistes audio DX. [Télécharger FFmpeg](https://ffmpeg.org/download.html)

**Pour revenir aux fichiers d’origine**, ferme le jeu et choisis **4**. Les originaux se trouvent dans `ArnosurgeDX-patch-backup` à la racine de l’installation. Conserve ce dossier. Les sauvegardes de partie sont indépendantes du patch.

Certaines répliques propres à DX restent en japonais. Les écrans verrouillés ont été contrôlés dans les ressources du jeu. Leur rendu reste à confirmer en partie. Les empreintes compatibles, les commandes d’installation et les crédits figurent dans le [README principal](README.md).
