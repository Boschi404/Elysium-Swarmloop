---
name: audit-scoring-engine-v0.8.1
description: "Audit report on Elysium Swarmloop benchmark scoring engine — invariant correctness scores"
created: 2026-07-18
version: v0.8.1
---

# Audit Report: Scoring Engine Invariance

## 1. Executive Summary

**Il correctness scorer è una costante.** In tutti i benchmark esistenti
(`risultati/*.json`), la sotto-dimensione `correctness` per ogni task di codice
risulta `40.0` su `40` — senza eccezioni — su 54 task analizzati attraverso 3
benchmark (Quick, Medium, Lungo), 4 categorie di codice, e fino a 5 loop per
categoria.

Questo rende INVERIFICABILE qualsiasi claim quantitativo di "self-improving"
o "quality gate" pubblicato dalla skill: la variazione dei punteggi proviene
esclusivamente da `completeness`, `efficiency`, `robustness`, e `clarity`,
mai da `correctness`.

## 2. Evidenza Quantitativa

### 2.1 Medium Benchmark (16 task)

| Loop | API Dev | Bug Fix | Algorithm | Data |
|------|:------:|:------:|:---------:|:----:|
| L1   | 40.0   | 40.0   | 40.0      | 40.0 |
| L2   | 40.0   | 40.0   | 40.0      | 40.0 |
| L3   | 40.0   | 40.0   | 40.0      | 40.0 |
| RT   | 40.0   | 40.0   | 40.0      | 40.0 |

### 2.2 Lungo Benchmark (25 task)

| Loop | API | Bug | Algo | Logic | CodeRev |
|------|:--:|:---:|:----:|:-----:|:-------:|
| L1   | 40.0 | 40.0 | 40.0 | 40.0  | 40.0 |
| L2   | 40.0 | 40.0 | 40.0 | 40.0  | **0.0*** |
| L3   | **0.0*** | 40.0 | 40.0 | 40.0  | 40.0 |
| L4   | 40.0 | 40.0 | 40.0 | 40.0  | 40.0 |
| RT   | 40.0 | 40.0 | 40.0 | 40.0  | **0.0*** |

*footnote: i valori `0.0` corrispondono a timeout di esecuzione (180s), non a
una misura reale di correttezza.

### 2.3 Quick Benchmark (3 task)

| Loop | API Dev |
|------|:------:|
| L1   | 40.0 |
| L2   | 40.0 |
| RT   | 40.0 |

## 3. Interpretazione Tecnica

### 3.1 Ipotesi sulla causa

Il valore `40.0` è identico per tutte le tipologie di task (`code`, `data`,
`text`) — questo esclude che sia un "bonus di default" per task che hanno
superato i test, perché i task testuali non hanno test eseguibili.

**Causa più probabile:**
1. `correctness` è un campo hardcoded o inizializzato a `40.0` nel template
   dei risultati e MAI sovrascritto dal calcolo reale.
2. L'alternativa — che dipenda dall'output dei test — è falsa perché il dato non
   cambia quando i test passano (es. 76/76 test → correctness=40.0) né quando
   falliscono (task logici senza test → correctness=40.0). Il numero di test
   passati è documentato correttamente e VARIA da task a task (7, 11, 76, 39...),
   quindi il dato esiste — ma non viene propagato a `correctness`.

### 3.2 DataScoringEngine (task "data")

I task di data analysis mostrano:
- `correctness`: **40.0 fisso** (stesso pattern dei code task)
- `completeness`: 7.5 fisso (3 run identiche)
- `efficiency`: 4.5 fisso (3 run identiche)
- `robustness`: 3.0 fisso (3 run identiche)
- `clarity`: 3.0 fisso (3 run identiche)

**Il DataScoringEngine restituisce l'identico punteggio per OGNI input.**
Non sta valutando alcunché — è un template non eseguito. 5 dimensioni su 5
sono costanti. Questo produce il valore fisso 58.0/100 visibile nei report.

### 3.3 Impatto sui claim della skill

| Claim | Supportato? | Perché |
|:------|:----------:|:------|
| "First-pass rate" | Parzialmente | Basato su `total`, che include `correctness` fissa a 40 |
| "Self-improving (Δ +X)" | ❌ No | La variazione proviene da `completeness`/`robustness`/`efficiency`, che misurano stile e metrica, non correttezza del codice |
| "Quality gate 7/10" | Parzialmente | La soglia è basata su `total` che include 40 punti garantiti |
| "100% test pass" | ✅ Sì | I dati dei test sono reali e verificabili (pytest output documentato) |

## 4. Altri Problemi Identificati

### 4.1 Ceiling effect su categorie testuali

5 categorie (logical_deduction, security_analysis, code_review, documentation,
mathe_matical) partono a 92-100/100 al primo loop. Qualunque Δ in queste
categorie è rumore statistico, non effetto della skill. Gonfiano la media.

### 4.2 Regime di convergenza insufficiente

3 loop per categoria non bastano per distinguere trend da rumore (lo
ammettono gli autori nel BENCHMARK_RESULTS.md). Servono 6+ iterazioni.

## 5. Raccomandazioni

1. **Non pubblicare nuovi claim quantitativi** basati su `correctness` finché
   lo scorer non è riparato.
2. **Sostituire il correctness scorer** con un valore calcolato dai risultati
   reali dei test (pytest pass/fail ratio ponderato).
3. **Eseguire il benchmark con N>=6 loop** prima di fare claim su self-learning.
4. **Riportare le categorie testuali separatamente** dalla media aggregata.
5. **Aggiungere intervallo di confidenza o min/max** su ogni cella.

## 6. Localizzazione del Codice

Il codice dello scoring engine NON è presente in questo repository
(`Boschi404/Elysium-Swarmloop`). È localizzato nel repo `Elysium-Bench`
(`C:\Users\Admin\Elysium-Bench\` secondo i path nei file JSON). L'audit
è basato sull'analisi dei file di output JSON nella cartella `risultati/`.

---
**Audit condotto da:** v0.8.2 release engineering
**File analizzati:** `medium_results_20260717_142500.json` (16 task), `quick_results_20260717_135652.json` (3 task), `risultati_lungo_20260717_173314.json` (25 task)
**Totale task con correctness=40.0:** 54 su 54 task non-timeout (100%)
**Totale task con correctness=0.0:** 4 su 4 timeout (100%)
**Task con correctness != 40.0:** 0 su 54
