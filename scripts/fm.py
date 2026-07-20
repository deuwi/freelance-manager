#!/usr/bin/env python3
"""fm.py — Freelance Manager CLI (micro-entrepreneur BNC).

Tous les calculs déterministes : rentabilité mission, trésorerie,
retrait safe, seuils TVA/plafond micro, répartition du temps.
Zéro dépendance externe (stdlib uniquement).

Données stockées dans ~/.freelance-manager/ (créé par `fm.py init`).

Usage :
  fm.py init [--data-dir PATH]
  fm.py config show
  fm.py mission eval --tjm 350 --jours 20 [--delai-paiement 30] [--nom "Client X"]
  fm.py mission add  --tjm 350 --jours 20 --nom "Client X" [--debut 2026-08-01]
  fm.py mission list
  fm.py ca add --montant 4200 [--date 2026-07-15] [--nom "Client X"]
  fm.py depense add --montant 89 --label "Hébergement" [--date 2026-07-10]
  fm.py treso set --montant 8500
  fm.py retrait
  fm.py status
  fm.py temps log --cat dev --heures 6 [--date 2026-07-20]
  fm.py temps report [--semaines 4]
  fm.py hebdo
"""

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

DATA_DIR = Path(os.environ.get("FM_DATA_DIR", Path.home() / ".freelance-manager"))
TEMPLATES = Path(__file__).resolve().parent.parent / "templates"

FILES = {
    "config": "config.json",
    "missions": "missions.json",
    "treso": "treso.json",
    "temps": "temps.json",
}


# ---------- utilitaires ----------

def load(name):
    p = DATA_DIR / FILES[name]
    if not p.exists():
        sys.exit(f"ERREUR: {p} introuvable. Lance d'abord: fm.py init")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(name, data):
    p = DATA_DIR / FILES[name]
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def eur(x):
    return f"{x:,.0f} €".replace(",", " ")


def pct(x):
    return f"{x * 100:.1f} %"


def today():
    return date.today()


def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date() if s else today()


def taux_total(cfg):
    r = cfg["regime"]
    t = r["taux_acre"] if r.get("acre") else r["taux_cotisations"]
    t += r["taux_cfp"]
    if r.get("versement_liberatoire"):
        t += r["taux_vl"]
    return t


def ca_encaisse_annee(treso, annee=None):
    annee = annee or today().year
    return sum(
        e["montant"] for e in treso.get("encaissements", [])
        if parse_date(e["date"]).year == annee
    )


# ---------- commandes ----------

def cmd_init(args):
    data_dir = Path(args.data_dir) if args.data_dir else DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)
    created = []
    defaults = {
        "config.json": None,  # copié depuis template
        "missions.json": {"missions": []},
        "treso.json": {"solde": 0, "solde_date": str(today()),
                       "encaissements": [], "depenses": [],
                       "cotisations_payees": []},
        "temps.json": {"entrees": []},
    }
    for fname, default in defaults.items():
        target = data_dir / fname
        if target.exists():
            continue
        if fname == "config.json":
            src = TEMPLATES / "config.json"
            target.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            with open(target, "w", encoding="utf-8") as f:
                json.dump(default, f, ensure_ascii=False, indent=2)
        created.append(fname)
    if created:
        print(f"Initialisé dans {data_dir} : {', '.join(created)}")
        print("Étape suivante : édite config.json (TJM cible, charges perso) "
              "puis `fm.py treso set --montant <solde actuel>`.")
    else:
        print(f"Déjà initialisé ({data_dir}). Rien à faire.")


def cmd_config_show(args):
    print(json.dumps(load("config"), ensure_ascii=False, indent=2))


def _eval_mission(cfg, treso, tjm, jours, delai_paiement=30):
    t = taux_total(cfg)
    r = cfg["regime"]
    obj = cfg["objectifs"]
    ca = tjm * jours
    net = ca * (1 - t)
    net_jour = net / jours if jours else 0

    ca_ytd = ca_encaisse_annee(treso)
    ca_apres = ca_ytd + ca

    verdict = []
    score = 0

    # TJM vs objectifs
    if tjm >= obj["tjm_cible"]:
        score += 3
        verdict.append(f"TJM {eur(tjm)} >= cible ({eur(obj['tjm_cible'])}) : OK")
    elif tjm >= obj["tjm_plancher"]:
        score += 1
        verdict.append(f"TJM {eur(tjm)} sous la cible mais >= plancher "
                       f"({eur(obj['tjm_plancher'])}) : acceptable si autre intérêt "
                       "(référence, techno, long terme)")
    else:
        score -= 3
        verdict.append(f"TJM {eur(tjm)} < plancher ({eur(obj['tjm_plancher'])}) : "
                       "ALERTE, refuser ou renégocier")

    # Seuil TVA
    if ca_apres > r["seuil_tva_majore"]:
        score -= 1
        verdict.append(f"CA annuel après mission ({eur(ca_apres)}) > seuil TVA majoré "
                       f"({eur(r['seuil_tva_majore'])}) : TVA due dès le dépassement, "
                       "facturer en HT+TVA ou lisser sur l'année suivante")
    elif ca_apres > r["seuil_tva"]:
        verdict.append(f"CA annuel après mission ({eur(ca_apres)}) > seuil TVA de base "
                       f"({eur(r['seuil_tva'])}) : TVA l'année suivante si confirmé, "
                       "anticiper la facturation TTC")
    else:
        marge = r["seuil_tva"] - ca_apres
        verdict.append(f"Marge avant seuil TVA : {eur(marge)}")

    # Plafond micro
    if ca_apres > r["plafond_micro"]:
        score -= 2
        verdict.append(f"DÉPASSEMENT plafond micro ({eur(r['plafond_micro'])}) : "
                       "risque de sortie du régime si 2 ans consécutifs")

    # Délai de paiement
    if delai_paiement > 45:
        score -= 1
        verdict.append(f"Délai de paiement {delai_paiement} j : long, impact trésorerie")

    reco = "ACCEPTER" if score >= 3 else ("À NÉGOCIER / ÉVALUER" if score >= 0 else "REFUSER")

    return {
        "ca_facture": ca,
        "prelevements": ca * t,
        "taux_prelevements": t,
        "net_estime": net,
        "net_par_jour": net_jour,
        "ca_annuel_apres": ca_apres,
        "score": score,
        "recommandation": reco,
        "points": verdict,
    }


def cmd_mission_eval(args):
    cfg, treso = load("config"), load("treso")
    res = _eval_mission(cfg, treso, args.tjm, args.jours, args.delai_paiement)
    nom = f" — {args.nom}" if args.nom else ""
    print(f"ÉVALUATION MISSION{nom}")
    print(f"  CA facturé      : {eur(res['ca_facture'])} ({args.jours} j × {eur(args.tjm)})")
    print(f"  Prélèvements    : {eur(res['prelevements'])} ({pct(res['taux_prelevements'])})")
    print(f"  Net estimé      : {eur(res['net_estime'])} soit {eur(res['net_par_jour'])}/jour")
    print(f"  CA annuel après : {eur(res['ca_annuel_apres'])}")
    print(f"  Score           : {res['score']:+d}  →  {res['recommandation']}")
    for p in res["points"]:
        print(f"  - {p}")


def cmd_mission_add(args):
    missions = load("missions")
    missions["missions"].append({
        "nom": args.nom,
        "tjm": args.tjm,
        "jours": args.jours,
        "debut": args.debut or str(today()),
        "statut": "en_cours",
        "ajoute_le": str(today()),
    })
    save("missions", missions)
    print(f"Mission ajoutée : {args.nom} ({args.jours} j × {eur(args.tjm)})")


def cmd_mission_list(args):
    for m in load("missions")["missions"]:
        print(f"  [{m['statut']}] {m['nom']} — {m['jours']} j × {eur(m['tjm'])} "
              f"= {eur(m['tjm'] * m['jours'])} (début {m['debut']})")


def cmd_ca_add(args):
    treso = load("treso")
    treso["encaissements"].append({
        "date": str(parse_date(args.date)),
        "montant": args.montant,
        "nom": args.nom or "",
    })
    treso["solde"] = treso.get("solde", 0) + args.montant
    save("treso", treso)
    print(f"Encaissement enregistré : {eur(args.montant)} "
          f"(solde : {eur(treso['solde'])})")


def cmd_depense_add(args):
    treso = load("treso")
    treso["depenses"].append({
        "date": str(parse_date(args.date)),
        "montant": args.montant,
        "label": args.label,
    })
    treso["solde"] = treso.get("solde", 0) - args.montant
    save("treso", treso)
    print(f"Dépense enregistrée : {eur(args.montant)} — {args.label} "
          f"(solde : {eur(treso['solde'])})")


def cmd_treso_set(args):
    treso = load("treso")
    treso["solde"] = args.montant
    treso["solde_date"] = str(today())
    save("treso", treso)
    print(f"Solde trésorerie fixé à {eur(args.montant)}")


def _provisions(cfg, treso):
    """Provisions à conserver : cotisations non payées + impôt + buffer perso."""
    t = taux_total(cfg)
    ca_ytd = ca_encaisse_annee(treso)
    cotis_payees = sum(c["montant"] for c in treso.get("cotisations_payees", [])
                       if parse_date(c["date"]).year == today().year)
    prov_cotis = max(0, ca_ytd * t - cotis_payees)
    prov_impot = 0 if cfg["regime"].get("versement_liberatoire") \
        else ca_ytd * cfg["perso"]["provision_impot_pct"]
    buffer = cfg["perso"]["charges_perso_mensuelles"] * cfg["perso"]["buffer_mois"]
    return prov_cotis, prov_impot, buffer


def cmd_retrait(args):
    cfg, treso = load("config"), load("treso")
    solde = treso.get("solde", 0)
    prov_cotis, prov_impot, buffer = _provisions(cfg, treso)
    dispo = solde - prov_cotis - prov_impot - buffer

    # Lissage : net moyen des 3 derniers mois
    t = taux_total(cfg)
    cutoff = today() - timedelta(days=90)
    ca_3m = sum(e["montant"] for e in treso.get("encaissements", [])
                if parse_date(e["date"]) >= cutoff)
    net_moyen_mensuel = ca_3m * (1 - t) / 3

    retrait = max(0, min(dispo, net_moyen_mensuel)) if net_moyen_mensuel > 0 \
        else max(0, dispo)

    print("RETRAIT MENSUEL SAFE")
    print(f"  Solde trésorerie        : {eur(solde)}")
    print(f"  - Provision URSSAF      : {eur(prov_cotis)}")
    print(f"  - Provision impôt       : {eur(prov_impot)}")
    print(f"  - Buffer sécurité       : {eur(buffer)} "
          f"({cfg['perso']['buffer_mois']} mois × "
          f"{eur(cfg['perso']['charges_perso_mensuelles'])})")
    print(f"  = Disponible            : {eur(dispo)}")
    print(f"  Net moyen mensuel (3 m) : {eur(net_moyen_mensuel)}")
    print(f"  → RETRAIT CONSEILLÉ     : {eur(retrait)}")
    if dispo < 0:
        print("  ALERTE : trésorerie sous le niveau de sécurité. Retrait déconseillé.")


def cmd_status(args):
    cfg, treso = load("config"), load("treso")
    r, obj = cfg["regime"], cfg["objectifs"]
    t = taux_total(cfg)
    ca_ytd = ca_encaisse_annee(treso)
    jours_ecoules = (today() - date(today().year, 1, 1)).days + 1
    projection = ca_ytd / jours_ecoules * 365 if jours_ecoules else 0
    prov_cotis, prov_impot, buffer = _provisions(cfg, treso)
    solde = treso.get("solde", 0)
    charges = cfg["perso"]["charges_perso_mensuelles"]
    runway = solde / charges if charges else 0

    print(f"STATUS — {today()}")
    print(f"  CA encaissé {today().year}  : {eur(ca_ytd)} "
          f"(cible {eur(obj['ca_annuel_cible'])}, "
          f"{pct(ca_ytd / obj['ca_annuel_cible']) if obj['ca_annuel_cible'] else 'n/a'})")
    print(f"  Projection fin d'année : {eur(projection)}")
    marge_tva = r["seuil_tva"] - ca_ytd
    etat_tva = "DÉPASSÉ" if ca_ytd > r["seuil_tva"] else f"reste {eur(marge_tva)}"
    print(f"  Seuil TVA ({eur(r['seuil_tva'])})   : {etat_tva}")
    print(f"  Plafond micro ({eur(r['plafond_micro'])}) : "
          f"{'DÉPASSÉ' if ca_ytd > r['plafond_micro'] else 'OK'}")
    print(f"  Trésorerie : {eur(solde)} | runway {runway:.1f} mois")
    print(f"  Provisions à garder : URSSAF {eur(prov_cotis)} + impôt {eur(prov_impot)} "
          f"+ buffer {eur(buffer)}")
    if projection > r["seuil_tva"] and ca_ytd <= r["seuil_tva"]:
        print(f"  ⚠ Projection > seuil TVA : anticiper le passage TTC.")


def cmd_temps_log(args):
    cfg = load("config")
    cats = cfg["temps"]["categories"]
    if args.cat not in cats:
        sys.exit(f"ERREUR: catégorie inconnue '{args.cat}'. Choix : {', '.join(cats)}")
    temps = load("temps")
    temps["entrees"].append({
        "date": str(parse_date(args.date)),
        "cat": args.cat,
        "heures": args.heures,
    })
    save("temps", temps)
    print(f"Temps loggé : {args.heures} h — {args.cat}")


def cmd_temps_report(args):
    cfg, temps = load("config"), load("temps")
    cutoff = today() - timedelta(weeks=args.semaines)
    entrees = [e for e in temps["entrees"] if parse_date(e["date"]) >= cutoff]
    total = sum(e["heures"] for e in entrees)
    cible = cfg["temps"]["repartition_cible"]
    print(f"TEMPS — {args.semaines} dernière(s) semaine(s) — total {total:.0f} h")
    if not total:
        print("  Aucune entrée. Logger avec : fm.py temps log --cat dev --heures N")
        return
    for cat in cfg["temps"]["categories"]:
        h = sum(e["heures"] for e in entrees if e["cat"] == cat)
        reel = h / total
        c = cible.get(cat, 0)
        ecart = reel - c
        flag = " ⚠" if abs(ecart) > 0.15 else ""
        print(f"  {cat:<12} {h:5.1f} h  {pct(reel):>7}  (cible {pct(c)}, "
              f"écart {ecart * 100:+.0f} pts){flag}")


def cmd_hebdo(args):
    """Rapport compact pour le point hebdo — pensé pour être lu par Claude."""
    print("=" * 50)
    cmd_status(args)
    print("-" * 50)
    cmd_retrait(args)
    print("-" * 50)
    args.semaines = 1
    cmd_temps_report(args)
    print("-" * 50)
    print("MISSIONS EN COURS")
    cmd_mission_list(args)
    print("=" * 50)


# ---------- parseur ----------

def main():
    p = argparse.ArgumentParser(prog="fm.py", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init")
    s.add_argument("--data-dir")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("config")
    s2 = s.add_subparsers(dest="sub", required=True)
    x = s2.add_parser("show")
    x.set_defaults(func=cmd_config_show)

    s = sub.add_parser("mission")
    s2 = s.add_subparsers(dest="sub", required=True)
    x = s2.add_parser("eval")
    x.add_argument("--tjm", type=float, required=True)
    x.add_argument("--jours", type=float, required=True)
    x.add_argument("--delai-paiement", type=int, default=30)
    x.add_argument("--nom", default="")
    x.set_defaults(func=cmd_mission_eval)
    x = s2.add_parser("add")
    x.add_argument("--tjm", type=float, required=True)
    x.add_argument("--jours", type=float, required=True)
    x.add_argument("--nom", required=True)
    x.add_argument("--debut")
    x.set_defaults(func=cmd_mission_add)
    x = s2.add_parser("list")
    x.set_defaults(func=cmd_mission_list)

    s = sub.add_parser("ca")
    s2 = s.add_subparsers(dest="sub", required=True)
    x = s2.add_parser("add")
    x.add_argument("--montant", type=float, required=True)
    x.add_argument("--date")
    x.add_argument("--nom")
    x.set_defaults(func=cmd_ca_add)

    s = sub.add_parser("depense")
    s2 = s.add_subparsers(dest="sub", required=True)
    x = s2.add_parser("add")
    x.add_argument("--montant", type=float, required=True)
    x.add_argument("--label", required=True)
    x.add_argument("--date")
    x.set_defaults(func=cmd_depense_add)

    s = sub.add_parser("treso")
    s2 = s.add_subparsers(dest="sub", required=True)
    x = s2.add_parser("set")
    x.add_argument("--montant", type=float, required=True)
    x.set_defaults(func=cmd_treso_set)

    s = sub.add_parser("retrait")
    s.set_defaults(func=cmd_retrait)

    s = sub.add_parser("status")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("temps")
    s2 = s.add_subparsers(dest="sub", required=True)
    x = s2.add_parser("log")
    x.add_argument("--cat", required=True)
    x.add_argument("--heures", type=float, required=True)
    x.add_argument("--date")
    x.set_defaults(func=cmd_temps_log)
    x = s2.add_parser("report")
    x.add_argument("--semaines", type=int, default=4)
    x.set_defaults(func=cmd_temps_report)

    s = sub.add_parser("hebdo")
    s.add_argument("--semaines", type=int, default=1)
    s.set_defaults(func=cmd_hebdo)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
