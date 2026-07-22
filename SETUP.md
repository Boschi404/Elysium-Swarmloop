# Elysium Swarmloop — Installazione Perfetta (v0.7.0)

Guida step-by-step per installare e configurare la skill in Hermes Agent.

---

## Requisiti

- **Hermes Agent** installato e funzionante
- **GitHub account** collegato a Hermes (per sync)
- **Windows** (la guida usa percorsi Windows)
- **Python 3.8+** (per e2e_test.py e session_manager.py)

---

## Step 1 — Installa la Skill

```bash
# Clona il repo
cd ~/Desktop
git clone https://github.com/Boschi404/Elysium-Swarmloop.git
```

Poi copia i file nella directory skills di Hermes:

```bash
mkdir -p ~/AppData/Local/hermes/skills/autonomous-agents/elysium-swarmloop/scripts
mkdir -p ~/AppData/Local/hermes/skills/autonomous-agents/elysium-swarmloop/references
cp Elysium-Swarmloop/SKILL.md ~/AppData/Local/hermes/skills/autonomous-agents/elysium-swarmloop/
cp Elysium-Swarmloop/scripts/* ~/AppData/Local/hermes/skills/autonomous-agents/elysium-swarmloop/scripts/
cp Elysium-Swarmloop/references/* ~/AppData/Local/hermes/skills/autonomous-agents/elysium-swarmloop/references/
```

---

## Step 2 — Configura Hermes (config.yaml)

Apri `~/AppData/Local/hermes/config.yaml` e **assicurati** che questi settaggi siano presenti:

```yaml
delegation:
  max_concurrent_children: 100   # massimo parallelismo
  max_async_children: 100        # stesso valore
  max_spawn_depth: 2             # orchestrator depth-2
  child_timeout_seconds: 600     # timeout generoso
  max_iterations: 50             # profondità ragionamento
  orchestrator_enabled: true     # abilita gerarchia
```

> **Critico**: senza questi settaggi, la skill usa una frazione della sua potenza. `max_spawn_depth: 2` e `orchestrator_enabled: true` sono necessari per depth-2 orchestration.

---

## Step 3 — Installa jq (Windows)

Il bootloader (`scripts/init-state.sh`) usa `jq` per costruire e leggere JSON.

```bash
# Crea directory bin se non esiste
mkdir -p ~/bin

# Scarica jq-win64.exe
curl -L -o "$HOME/bin/jq.exe" "https://github.com/jqlang/jq/releases/download/jq-1.7/jq-win64.exe"

# Rendi eseguibile
chmod +x "$HOME/bin/jq.exe"

# Aggiungi al PATH (permanente in ~/.bashrc)
export PATH="$HOME/bin:$PATH"
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc

# Verifica
jq --version
# → jq-1.7
```

---

## Step 4 — Inizializza il Pattern Store (SQLite)

Il pattern store salva le esecuzioni, i pattern di decomposizione, i pitfalls e le calibrazioni.

Via terminale Python (esegui una volta):

```bash
python -c "
import sqlite3, os
hermes_db = os.path.expanduser('~/.hermes/hermes.db')
pattern_sql = os.path.expanduser('~/AppData/Local/hermes/skills/autonomous-agents/elysium-swarmloop/references/pattern-store.sql')
conn = sqlite3.connect(hermes_db)
with open(pattern_sql, 'r') as f:
    conn.executescript(f.read())
conn.commit()
print('Pattern store inizializzato OK')
"
```

---

## Step 5 — Verifica il Bootloader

```bash
cd ~/AppData/Local/hermes/skills/autonomous-agents/elysium-swarmloop

# Test Tier 1 (quick fix)
bash scripts/init-state.sh --json "Fix typo in config"
# → {tier: 1, subagents: 3, threshold: 6}

# Test Tier 3 (API)
bash scripts/init-state.sh "Build REST API for booking"
# → Mostra stato completo con assessment

# Test Tier 4 (greenfield)
bash scripts/init-state.sh --json "Build greenfield full-stack platform"
# → {tier: 4, subagents: 80, threshold: 8}
```

---

## Step 6 — Verifica i Nuovi Script (v0.7.0)

```bash
cd ~/AppData/Local/hermes/skills/autonomous-agents/elysium-swarmloop

# Verifica che i nuovi script esistano
ls -la scripts/e2e_test.py scripts/session_manager.py
ls -la references/user_preferences.yaml

# Esegui il test E2E (opzionale, 35+ test)
python scripts/e2e_test.py
# → Dovrebbe mostrare risultati dei test across 4 scenari

# Verifica che user_preferences.yaml sia caricabile
python -c "import yaml; yaml.safe_load(open('references/user_preferences.yaml')); print('user_preferences.yaml OK')"
```

---

## Step 7 — Usa la Skill

Carica la skill in una sessione Hermes:

```
skill_view(name='elysium-swarmloop')
```

Poi ogni prompt viene elaborato dal loop autonomo:

| Se scrivi... | La skill fa... |
|-------------|---------------|
| `fixa il typo in config.yaml` | Tier 1 fast-path → esecuzione diretta |
| `aggiungi endpoint /users` | Tier 2 → 10 subagenti, decomposizione per funzione |
| `crea dashboard trading` | Tier 3 → 35 subagenti, ricerca + implementa |
| `costruisci piattaforma SaaS da zero` | Tier 4 → 80 subagenti, depth-2 orchestration |

---

## Troubleshooting

| Problema | Causa | Fix |
|----------|-------|-----|
| `jq: command not found` | jq non installato | Step 3 |
| `max_concurrent_children` non parte | config.yaml non aggiornato | Step 2 |
| Bootloader dà tier sbagliato | Keyword non riconosciuta | Aggiungi keyword in `detect_tier()` |
| Pattern store: tabella non trovata | Schema non eseguito | Step 4 |
| Loop non si attiva | Skill non caricata | `skill_view(name='elysium-swarmloop')` |
| Subagent non spawna | `orchestrator_enabled: false` | Step 2 |
| `e2e_test.py` fallisce | Dipendenze mancanti | `pip install pyyaml` |
| `session_manager.py` non trovato | Script non copiato | Step 1 (copia scripts/) |
| `user_preferences.yaml` non trovato | Reference non copiato | Step 1 (copia references/) |

---

## Checklist Finale

- [ ] Skill installata in Hermes (`skill_view` mostra il contenuto)
- [ ] `max_concurrent_children: 100` in config.yaml
- [ ] `max_spawn_depth: 2` in config.yaml
- [ ] `orchestrator_enabled: true` in config.yaml
- [ ] `jq` installato e funzionante (`jq --version`)
- [ ] Pattern store inizializzato (4 tabelle in hermes.db)
- [ ] Bootloader testato (Tier 1/3/4)
- [ ] Scripts v0.7.0 presenti (`scripts/e2e_test.py`, `scripts/session_manager.py`)
- [ ] References v0.7.0 presenti (`references/user_preferences.yaml`)
- [ ] E2E test superato (`python scripts/e2e_test.py`)
- [ ] GitHub repo sincronizzato (opzionale)
