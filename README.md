# Nutrition ASV

Site statique pour lire la synthèse **Nutrition ASV** et s’entraîner section par section. Chaque question a une seule bonne réponse : un passage du PDF. L’extrait affiché après la réponse est lui aussi repris tel quel. Les autres propositions sont fausses par rapport à la synthèse.

Le fichier source est `public/Nutrition_ASV_synthese.pdf`.

## Lancer en local

```bash
npm install
npm run dev
```

Ouvrir [http://127.0.0.1:43127/StudyWeb/](http://127.0.0.1:43127/StudyWeb/) si le serveur a été démarré avec ce port :

```bash
npm run dev -- --hostname 0.0.0.0 --port 43127
```

Sans argument, Next.js utilise le port 3000.

## Build statique

```bash
npm run build
```

Le site exporté est dans `out/`. Il est prévu pour un site projet :

`https://<user>.github.io/StudyWeb/`

`basePath` et `assetPrefix` valent `/StudyWeb` (voir `next.config.ts` et `.github/workflows/pages.yml`). Ce n’est pas un site utilisateur `https://<user>.github.io/`.

## GitHub Pages

1. Dans le dépôt : **Settings → Pages → Build and deployment → Source : GitHub Actions**.
2. Pousser la branche qui contient `.github/workflows/pages.yml`.
3. Le workflow installe, exécute `npm run build`, puis publie le dossier `out`.

Le workflow publie déjà avec `NEXT_PUBLIC_BASE_PATH: /StudyWeb`. Ne pas le vider : les pages et le PDF doivent être servis sous `/StudyWeb/`.

## Vérifier les extraits

`python3 scripts/build-bank.py` régénère `src/data/bank.json` et refuse toute formulation absente du PDF (`pdftotext` requis).
