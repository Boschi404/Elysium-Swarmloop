# BENCHMARK — piano di validazione post-refactor (v0.16.1)

Obiettivo: misurare che gli interventi sulla skill (Blocco A/B/C) non degradino il comportamento del loop. Senza questa misurazione, lo split/refactor lavora alla cieca.

## Metriche

| Metrica | Come misurarla | Soglia di successo |
|---------|----------------|--------------------|
| FPR (First Pass Rate) | % task subagent passati al primo colpo | Non degradata > 5% vs baseline |
| Tempo medio per task | Timestamp inizio→fine task | Riduzione ≥ 15% (meno token caricati) |
| Token consumati | Somma usage per sessione | Riduzione ≥ 25% dopo split |
| Retry per task | Conteggio retry / task totali | Non aumentato |
| e2e suite | `python scripts/e2e_test.py` | 251/251 sempre |

## Metodo (minimale, 3 task ripetibili)

1. **Baseline (pre-refactor):** eseguire 3 task campione dello stesso tipo (es. endpoint CRUD piccolo, fix bug isolato, analisi modulo) — 1 run ciascuno — registrare FPR, tempo, token, retry in una riga della tabella qui sotto.
2. **Dopo ogni blocco (A/B/C):** rieseguire GLI STESSI 3 task nello stesso ambiente, aggiungere riga.
3. Confronto riga per riga. Qualsiasi soglia violata → rollback (vedi sotto) e analisi.

## Registro misure

| Data | Versione | Task | FPR | Tempo medio | Token | Retry | Note |
|------|----------|------|-----|-------------|-------|-------|------|
| 2026-08-30 | v0.16.1 | (baseline da raccogliere) | - | - | - | - | Blocco A applicato, benchmark non ancora eseguito |

## Procedura di rollback

| Trigger | Azione |
|---------|--------|
| e2e < 251/251 dopo una modifica | `git revert <commit>` e re-run e2e |
| FPR degradata > 5% su 5+ task post-Blocco B | rollback al monolite: `git checkout e48eb80 -- SKILL.md` + re-run e2e |
| critic_gate (Blocco C) causa > 30% retry su 10 task | disattivare critic per Tier 3, ripristinare gate solo-script |
| Degradazione silenziosa sospetta (loop meno autonomo) | diff SKILL.md vs `e48eb80` e verifica sezioni caricate |

Lo stato pre-Blocco-A della standalone è il commit `e48eb80` (v0.16.0). Il backup del monorepo è `SKILL.v0.15.0.md` in `ffazecaldy/hermes-skills`.
