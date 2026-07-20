# freelance-manager

Skill Claude + CLI Python pour piloter une activité de freelance dev en
micro-entreprise (BNC libéral, France).

Principe : **les scripts calculent, Claude juge.** Tous les calculs
(rentabilité mission, trésorerie, retrait mensuel, seuils TVA et plafond
micro, répartition du temps) tournent en local via un CLI Python sans aucune
dépendance externe. Claude n'intervient que pour l'interprétation — ce qui
réduit fortement la consommation de jetons.

## Fonctionnalités

- **Évaluation de mission** : TJM × jours → CA, prélèvements (cotisations
  25,6 % + CFP 0,2 % + versement libératoire optionnel), net par jour, score
  et recommandation (accepter / négocier / refuser) selon tes objectifs.
- **Trésorerie** : encaissements, dépenses, solde, runway.
- **Retrait mensuel safe** : solde − provision URSSAF − provision impôt −
  buffer de sécurité, lissé sur le net moyen des 3 derniers mois.
- **Seuils** : distance au seuil TVA (37 500 € / 41 250 € majoré) et au
  plafond micro (83 600 €), avec alerte sur projection annuelle.
- **Temps** : logging par catégorie (dev, contenu, prospection, admin,
  veille) et écarts vs répartition cible.
- **Point hebdo** : `fm.py hebdo` sort tout en un bloc compact.
- **Référence stratégie** (`references/strategies.md`) : canaux de
  prospection, plateformes, modèles de revenus — chargée par Claude
  uniquement quand la question s'y prête.

## Installation

### Comme skill Claude

Importer le dossier (ou le `.skill` packagé) dans Claude Code / Claude.ai,
puis en conversation : « initialise mon freelance manager ».

### En CLI autonome

```bash
python3 scripts/fm.py init
# éditer ~/.freelance-manager/config.json (TJM cible, charges perso...)
python3 scripts/fm.py treso set --montant 8500
python3 scripts/fm.py mission eval --tjm 400 --jours 20
python3 scripts/fm.py retrait
python3 scripts/fm.py hebdo
```

Python ≥ 3.8, stdlib uniquement. Les données restent en local dans
`~/.freelance-manager/` (jamais dans le repo).

## Taux et seuils

Les taux 2026 (vérifiés juillet 2026) vivent dans
`templates/config.json` — rien n'est codé en dur. À revérifier chaque
janvier sur [urssaf.fr](https://www.urssaf.fr).

## Avertissement

Outil d'aide à la décision personnel. Ce n'est ni un conseil fiscal, ni un
conseil comptable ou financier. Pour les situations limites (dépassement de
seuils, option versement libératoire, sortie du régime micro), consulter
l'URSSAF ou un expert-comptable.

## Licence

MIT — voir [LICENSE](LICENSE).
