# freelance-manager

![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Dependencies](https://img.shields.io/badge/dependencies-none-lightgrey)

Skill Claude + CLI Python pour piloter une activité de freelance dev en
micro-entreprise (BNC libéral, France).

Principe : **les scripts calculent, Claude juge.** Tous les calculs
(rentabilité mission, trésorerie, retrait mensuel, seuils TVA et plafond
micro, répartition du temps) tournent en local via un CLI Python sans aucune
dépendance externe. Claude n'intervient que pour l'interprétation, ce qui
réduit fortement la consommation de jetons.

> Outil d'aide à la décision personnel. Ni conseil fiscal, ni conseil
> comptable ou financier. Voir la section Avertissement.

## Le problème

Un freelance en micro-entreprise pilote son activité au doigt mouillé :
il regarde son solde bancaire, oublie que 25,8 % (cotisations et CFP)
partent à l'URSSAF au trimestre suivant, ne sait pas s'il peut accepter une
mission à 350 €/jour, et découvre le seuil de TVA en le franchissant.

Les tableurs marchent, mais personne ne les tient à jour. Les logiciels
de compta répondent à la question du comptable, pas à celle du freelance :
"est-ce que je prends cette mission, et combien je peux me virer ce mois-ci ?"

## À quoi ça ressemble

```
$ python3 scripts/fm.py hebdo
==================================================
STATUS — 2026-07-21
  CA encaissé 2026  : 0 € (cible 45 000 €, 0.0 %)
  Projection fin d'année : 0 €
  Seuil TVA (37 500 €)   : reste 37 500 €
  Plafond micro (83 600 €) : OK
  Trésorerie : 8 500 € | runway 5.7 mois
  Provisions à garder : URSSAF 0 € + impôt 0 € + buffer 4 500 €
--------------------------------------------------
RETRAIT MENSUEL SAFE
  Solde trésorerie        : 8 500 €
  - Provision URSSAF      : 0 €
  - Provision impôt       : 0 €
  - Buffer sécurité       : 4 500 € (3 mois × 1 500 €)
  = Disponible            : 4 000 €
  Net moyen mensuel (3 m) : 0 €
  → RETRAIT CONSEILLÉ     : 4 000 €
--------------------------------------------------
TEMPS — 1 dernière(s) semaine(s) — total 0 h
  Aucune entrée. Logger avec : fm.py temps log --cat dev --heures N
--------------------------------------------------
MISSIONS EN COURS
==================================================
```

Sortie sur une installation neuve, avant toute saisie. Les chiffres de
trésorerie et de cible viennent de `config.json`.

## Pourquoi un CLI plutôt que du calcul par le modèle

Un LLM qui calcule des cotisations produit une réponse plausible, pas une
réponse juste, et elle change d'une session à l'autre. Ici les taux et les
formules vivent dans du Python déterministe : même entrée, même sortie,
vérifiable ligne par ligne.

Claude n'est appelé que là où il est bon : lire un résultat, le croiser avec
ton profil, et trancher. Effet de bord, une évaluation de mission coûte
quelques centaines de jetons au lieu de plusieurs milliers.

## Fonctionnalités

- **Évaluation de mission** : TJM multiplié par le nombre de jours, puis CA,
  prélèvements (cotisations 25,6 % + CFP 0,2 % + versement libératoire
  optionnel), net par jour, score et recommandation (accepter / négocier /
  refuser) selon tes objectifs.
- **Trésorerie** : encaissements, dépenses, solde, runway.
- **Retrait mensuel safe** : solde moins provision URSSAF, moins provision
  impôt, moins buffer de sécurité, lissé sur le net moyen des 3 derniers mois.
- **Seuils** : distance au seuil TVA (37 500 € / 41 250 € majoré) et au
  plafond micro (83 600 €), avec alerte sur projection annuelle.
- **Temps** : logging par catégorie (dev, contenu, prospection, admin,
  veille) et écarts vs répartition cible.
- **Point hebdo** : `fm.py hebdo` sort tout en un bloc compact.
- **Référence stratégie** (`references/strategies.md`) : canaux de
  prospection, plateformes, modèles de revenus. Chargée par Claude uniquement
  quand la question s'y prête, et croisée avec `fm.py status` et ton profil
  (`profil.md`).

## Installation

### Comme skill Claude

Importer le dossier (ou le `.skill` packagé) dans Claude Code ou Claude.ai,
puis en conversation : "initialise mon freelance manager". Claude lance
`fm.py init`, puis te demande tes chiffres (config.json) et de quoi remplir
ton profil (profil.md).

### En CLI autonome

```bash
python3 scripts/fm.py init
# éditer ~/.freelance-manager/config.json (TJM cible, charges perso...)
# éditer ~/.freelance-manager/profil.md (stack, réseau, plateformes actives...)
python3 scripts/fm.py treso set --montant 8500
python3 scripts/fm.py mission eval --tjm 400 --jours 20
python3 scripts/fm.py retrait
python3 scripts/fm.py hebdo
```

Python 3.8 ou supérieur, stdlib uniquement. Les données restent en local dans
`~/.freelance-manager/`, jamais dans le repo.

## Personnalisation

La skill ne contient aucune donnée personnelle : tout ce qui t'est propre
vit dans `~/.freelance-manager/`, créé par `fm.py init` à partir de
`templates/`.

- `config.json`, le quantitatif : TJM cible et plancher, charges perso
  mensuelles, CA annuel cible, taux et seuils.
- `profil.md`, le qualitatif : stack, localisation, réseau direct,
  plateformes actives, marque contenu éventuelle. La référence stratégie
  s'appuie dessus au lieu de valeurs codées en dur.

La skill est donc réutilisable telle quelle par n'importe quel freelance
dev : forke, lance `init`, remplis tes deux fichiers.

## Taux et seuils

Les taux 2026 (vérifiés juillet 2026) vivent dans `templates/config.json`.
Rien n'est codé en dur. À revérifier chaque janvier sur
[urssaf.fr](https://www.urssaf.fr).

## Avertissement

Outil d'aide à la décision personnel. Ce n'est ni un conseil fiscal, ni un
conseil comptable ou financier. Pour les situations limites (dépassement de
seuils, option versement libératoire, sortie du régime micro), consulter
l'URSSAF ou un expert-comptable.

## Licence

MIT, voir [LICENSE](LICENSE).
