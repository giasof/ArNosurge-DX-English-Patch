# Installer le patch anglais d’Ar nosurge DX

Le jeu et le lanceur passent en anglais. Le patch se construit sur ton PC à partir de ta version **DX Windows japonaise** et de ta version **PS Vita Plus américaine PCSE00707** extraite. Tu peux installer les sous-titres des cinématiques séparément avec la version DX.

La version portable fonctionne hors ligne sur Windows 10 et 11 64 bits. Tous les outils du patch sont inclus dans le ZIP. Sur une édition Windows N, l’option des cinématiques utilise le composant Windows Media Feature Pack.

1. Télécharge **ArNosurge-DX-English-Patch-Windows-x64.zip**, extrais tout le ZIP dans un dossier et ouvre **Setup.exe** après avoir fermé le jeu et son lanceur. [Télécharger la version portable](https://github.com/giasof/ArNosurge-DX-English-Patch/releases/latest/download/ArNosurge-DX-English-Patch-Windows-x64.zip)
2. Dans **Windows DX folder**, sélectionne le dossier contenant `ArnosurgeDX.exe`. Clique sur **Check files** pour vérifier les fichiers.
3. Dans **US Vita Plus folder (PCSE00707)**, sélectionne le dossier Vita contenant `Data/PSVita/resources1.psarc`, ou le dossier contenant directement cette archive. Clique sur **Install patch**. Quand la fenêtre affiche **Done**, ouvre le lanceur et clique sur **Play**.
4. Pour ajouter les sous-titres anglais, clique sur **Subtitle movies**. Seul le dossier DX est nécessaire. Laisse la fenêtre ouverte pendant la reconstruction des sept vidéos 1080p.

**Mise à jour depuis les versions 1.0.0 à 1.2.0**

Conserve le dossier `ArnosurgeDX-patch-backup`. Ouvre le nouveau **Setup.exe**, sélectionne ton dossier DX actuel et le dossier Vita Plus américain, puis clique sur **Install patch**. Avant la mise à jour, **Check files** indique **update available** pour les fichiers à reconstruire. Les cinématiques déjà sous-titrées restent installées. **Restore originals** permet de revenir aux fichiers d’origine.

Si tu as déjà installé ton jeu dans Vita3K, tu trouveras son dossier sous `ux0/app/PCSE00707` dans le stockage de l’émulateur. Setup vérifie l’empreinte de l’archive. Si ta sauvegarde de cartouche ou du jeu numérique est encore chiffrée, prépare d’abord une copie lisible.

## Version 1.3.0

- L’installateur importe 51 854 répliques réparties dans 2 241 fichiers depuis Vita Plus. Les 65 autres entrées des fichiers de dialogues correspondent déjà à DX.
- Shurelia, Nelo et Sarly ont chacune 49 conversations de purification en anglais. Le patch inclut aussi les six scènes d’introduction et adapte les indications de boutons à DX.
- Les illustrations communes des tutoriels viennent de la Vita. Les fiches qui expliquent des commandes propres à DX sont reconstruites pour PC.

- Les bulles de Cass et Ion en combat, les affinités et la disponibilité des chants, ainsi que le menu **Cast Song** sont en anglais. Les retours à la ligne ont été corrigés dans 81 messages du tutoriel et du système.
- Sur une manette Xbox, **A** active la commande du bas, dont **Stampede**, et **B** déclenche la garde pendant le tour ennemi. Les icônes correspondent aux boutons, y compris quand elles sont surlignées. Le lanceur permet de choisir les boutons de confirmation et de retour dans les menus.
- Le curseur de la souris se masque quand le jeu est au premier plan. Il réapparaît avec **Alt+Tab** ou quand tu réduis le jeu.

Si tu utilises Special K et qu’une fenêtre **Missing interface** mentionne **SteamInput007**, ferme le jeu et ouvre son profil Special K existant dans `Profiles/ArnosurgeDX.exe/SpecialK.ini`. Dans la section `[Steam.Log]`, règle `Silent=true`, puis relance le jeu.

Les écrans verrouillés ont été contrôlés dans les ressources du jeu. Leur rendu reste à confirmer en partie. Les empreintes compatibles, les commandes d’installation et les crédits figurent dans le [README principal](README.md).

**giasof** pilote le projet et a testé en jeu les menus anglais, les commandes Xbox et les cinématiques. **OpenAI Codex** a contribué en tant qu’assistant de développement IA à la création du patch et de l’installateur portable, ainsi qu’aux tests d’installation et de restauration.
