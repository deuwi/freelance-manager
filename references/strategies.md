# Stratégies — Trouver des missions & générer du revenu (dev indépendant)

Référence à lire quand l'utilisateur demande où trouver des missions, quelles
plateformes utiliser, ou comment diversifier ses revenus. Croiser
systématiquement avec deux sources :

1. `fm.py status` (trésorerie, runway, pipeline) — l'urgence financière ;
2. `~/.freelance-manager/profil.md` — stack, localisation, réseau,
   plateformes actives, marque contenu éventuelle.

Si `profil.md` n'existe pas, le créer à partir de `templates/profil.md` en
posant les questions à l'utilisateur. Ne jamais supposer sa stack, sa
localisation, son réseau ou l'existence d'une audience.

## 1. Canaux par ordre de rentabilité (effort vs TJM)

1. **Réseau direct / anciens collègues et clients** — TJM le plus haut, zéro
   commission. Premier réflexe : les contacts listés au profil (anciens
   employeurs, ex-collègues, clients passés, ESN locales).
2. **LinkedIn inbound** — long terme mais composé. Si le profil mentionne une
   présence LinkedIn ou une marque contenu déjà construite, les posts
   réguliers servent aussi la prospection ; sinon, canal à bâtir avant d'en
   attendre des missions.
3. **Plateformes avec pré-tri** (Comet, Crème de la Crème, FreelanceRepublik,
   LeHibou) — missions qualifiées envoyées au freelance, moins de tri à faire,
   TJM corrects. Sélection à l'entrée.
4. **Marketplaces ouvertes** (Malt, Freelance-Informatique) — volume élevé,
   concurrence élevée. Malt : réactivité = ranking ; n'y compter que si le
   profil y est à jour et maintenu actif (voir « plateformes actives » du
   profil). Freelance-Informatique : missions longues 3-12 mois via ESN, bon
   plan B régularité.
5. **Plateformes internationales** (Upwork, Contra) — pertinent uniquement si
   TJM local insuffisant ; concurrence mondiale, facturation en devise,
   anglais requis.

Règle : 2-3 canaux actifs maximum en même temps. Un canal "actif" = profil à
jour + réponse < 24 h + relances.

## 2. Choix de plateforme selon la situation (lire fm.py status d'abord)

| Situation (status) | Priorité |
|---|---|
| Runway < 3 mois | Malt + Freelance-Informatique (volume, vite) + réseau direct en parallèle |
| Runway 3-6 mois | Plateformes pré-tri (Comet, LeHibou) + LinkedIn outbound ciblé |
| Runway > 6 mois | LinkedIn inbound + montée en TJM + produits (voir §4) |

## 3. Playbook prospection hebdo (à caler dans temps: prospection)

- 5 candidatures/relances ciblées par semaine, pas plus, mais soignées.
- Chaque candidature : 3 lignes personnalisées max, un lien portfolio, un TJM
  annoncé (ne pas laisser "à discuter" — filtre les clients faibles).
- Relance unique à J+7. Pas de deuxième relance.
- Tracker les réponses dans missions.json (statut "piste") pour mesurer le
  taux de conversion par canal.

## 4. Modèles de revenus dev indépendant (du plus sûr au plus spéculatif)

1. **Régie (TJM)** — cœur du revenu. Objectif : 10-15 j facturés/mois, le
   reste pour les projets annexes déclarés au profil (contenu, produits).
2. **Forfait** — rentable uniquement avec périmètre verrouillé par écrit et
   acompte 30 %. Sinon refuser : le risque de dérive est sur le freelance.
3. **Maintenance / TMA récurrente** — petits contrats mensuels (200-500 €/mois)
   sur des projets livrés. Revenu lissé, très bon pour le calcul de retrait.
4. **Produits & contenu** — uniquement si le profil mentionne une marque ou
   une audience existante : lead magnet → liste email → produits payants
   (formations, templates, outils). Horizon long ; ne pas compter dessus dans
   les projections `fm.py` tant que < 100 €/mois régulier. Sans audience au
   profil, ne pas pousser ce modèle avant une régie stable.
5. **Side products SaaS/outils** — uniquement sur du temps excédentaire, une
   fois la régie stabilisée. Valider la demande avant de coder.

Règle des priorités : la régie finance tout le reste. Si `temps report`
montre prospection < cible ET runway < 6 mois, la prospection passe devant le
contenu, quel que soit le plan éditorial.

## 5. Signaux d'alerte côté client (à vérifier avant mission add)

- TJM négocié à la baisse dès le premier échange → pression continue ensuite.
- Périmètre flou + forfait → refuser ou passer en régie.
- Délai de paiement > 45 j → impact trésorerie (fm.py mission eval le score).
- Pas de contrat écrit / bon de commande → ne pas démarrer.

## 6. Rôle de Claude sur ces questions

- Ancrer chaque conseil dans les chiffres réels (`fm.py status`) et le profil
  réel (`profil.md`) plutôt que des généralités.
- Les commissions, volumes et positionnements des plateformes évoluent :
  pour un choix engageant (inscription payante, exclusivité), vérifier l'état
  actuel par une recherche web avant de confirmer.
- Ne pas promettre de résultats ("tu trouveras une mission en X semaines") :
  donner des fourchettes et des taux de conversion réalistes à mesurer.
