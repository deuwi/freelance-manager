---
name: freelance-manager
description: Gestionnaire de décisions freelance pour micro-entrepreneur BNC (dev). Calcule via scripts Python (zéro jeton de calcul) la rentabilité d'une mission (TJM, net après cotisations 25,6 % + CFP), la trésorerie, le retrait mensuel safe, la distance aux seuils TVA (37 500 €) et plafond micro (83 600 €), et la répartition du temps (dev/contenu/prospection). Inclut aussi une référence stratégie (plateformes, canaux de prospection, modèles de revenus). Utiliser cette skill dès que l'utilisateur parle d'accepter ou refuser une mission, d'un TJM, d'une proposition client, de combien se payer ce mois-ci, de trésorerie, de cotisations URSSAF, de seuil TVA, de son point hebdo freelance, de comment répartir son temps, de où et comment trouver des missions, de quelles plateformes freelance utiliser, ou de comment gagner de l'argent en tant que dev indépendant — même sans mentionner explicitement "freelance manager".
---

# Freelance Manager

Aide à la décision pour freelance micro-entrepreneur (BNC libéral, SSI).
Principe : **les scripts calculent, Claude juge**. Ne jamais refaire à la main
un calcul que `fm.py` sait faire — lancer le script et interpréter sa sortie.

## Architecture

- `scripts/fm.py` — CLI unique, stdlib Python uniquement.
- `references/strategies.md` — à lire UNIQUEMENT quand la question porte sur
  trouver des missions, choisir une plateforme, prospecter, ou diversifier
  ses revenus. Toujours lancer `fm.py status` ET lire le profil utilisateur
  avant de conseiller : la bonne stratégie dépend du runway et du profil.
- Données dans `~/.freelance-manager/` (config.json, profil.md,
  missions.json, treso.json, temps.json). Créées par `fm.py init`. Toute
  l'information personnelle vit dans ce dossier, jamais dans la skill.
- `templates/config.json` — taux 2026 par défaut, objectifs à personnaliser.
- `templates/profil.md` — trame du profil utilisateur (stack, localisation,
  réseau, plateformes actives, marque contenu éventuelle).

## Premier lancement

```bash
python3 scripts/fm.py init
```

Puis demander à l'utilisateur, sans jamais inventer ces valeurs :

1. ses chiffres pour `config.json` (TJM cible et plancher, charges perso
   mensuelles, CA annuel cible) ;
2. son solde de trésorerie actuel (`fm.py treso set --montant N`) ;
3. de quoi remplir `~/.freelance-manager/profil.md` à partir de
   `templates/profil.md` (stack, localisation, réseau direct, plateformes
   actives, marque contenu éventuelle).

Si `profil.md` manque au moment d'une question stratégie, le créer à ce
moment-là en posant les questions.

## Cas d'usage → commande

| Situation | Commande |
|---|---|
| "On me propose une mission à X €/j pendant Y jours, je prends ?" | `fm.py mission eval --tjm X --jours Y [--delai-paiement N]` |
| Mission acceptée | `fm.py mission add --tjm X --jours Y --nom "..."` |
| Paiement reçu | `fm.py ca add --montant N --nom "..."` |
| Dépense pro | `fm.py depense add --montant N --label "..."` |
| "Combien je peux me verser ce mois-ci ?" | `fm.py retrait` |
| "Où j'en suis ?" / état général | `fm.py status` |
| Fin de journée / logging du temps | `fm.py temps log --cat dev --heures N` |
| "Je passe trop de temps sur quoi ?" | `fm.py temps report --semaines 4` |
| Point hebdo du lundi | `fm.py hebdo` |

Catégories de temps : dev, contenu, prospection, admin, veille. (Si
l'utilisateur n'a pas d'activité contenu, la catégorie reste simplement
inutilisée.)

## Rôle de Claude après le script

1. **mission eval** : le script donne un score et une recommandation
   mécanique. Claude ajoute le contexte que le script ignore : pipeline
   actuel, intérêt stratégique (techno, référence client, compatibilité avec
   les projets annexes déclarés au profil — contenu, produits, side
   projects), charge mentale, risque client. Si le score mécanique et le
   contexte divergent, le dire explicitement.
2. **retrait** : ne jamais recommander un retrait supérieur au chiffre du
   script. En dessous, oui, si un événement à venir le justifie.
3. **hebdo** : lire la sortie complète, en tirer 3 priorités max pour la
   semaine, formulées en une phrase chacune. Pas de paraphrase de tous les
   chiffres — l'utilisateur les a sous les yeux.
4. **temps report** : les écarts > 15 pts sont flaggés ⚠ par le script.
   Commenter uniquement les écarts flaggés.

## Règles

- Réponses courtes. La sortie du script fait foi, Claude n'ajoute que le
  jugement.
- Les taux (cotisations 25,6 %, CFP 0,2 %, VL 2,2 %, seuils TVA
  37 500/41 250 €, plafond 83 600 €) vivent dans config.json — vérifiés
  juillet 2026. En janvier, proposer une vérification sur urssaf.fr avant
  toute autre chose.
- Le profil (`profil.md`) est une donnée utilisateur au même titre que
  config.json : ne jamais y présupposer une stack, une région, un réseau ou
  une audience.
- Le calcul de retrait est prudentiel (provisions URSSAF + impôt + buffer).
  Ce n'est pas un conseil fiscal ni financier : pour les cas limites
  (dépassement de seuils, option versement libératoire, sortie du régime
  micro), recommander de vérifier auprès de l'URSSAF ou d'un
  expert-comptable.
- Ne jamais stocker de données bancaires (IBAN, identifiants) dans les
  fichiers de données.
