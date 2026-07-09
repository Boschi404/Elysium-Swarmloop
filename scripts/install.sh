#!/usr/bin/env bash
# =============================================================================
# install.sh — Elysium Swarmloop Auto-Installer
# =============================================================================
# Esegue: bash install.sh
# Funziona su Windows (git-bash), Linux, macOS.
# Non richiede jq — usa Python per le parti JSON.
# =============================================================================
set -euo pipefail

VERSION="5.1.0"
REPO_URL="https://github.com/Boschi404/Elysium-Swarmloop.git"
HERMES_SKILLS_DIR="$HOME/AppData/Local/hermes/skills"
SKILL_DIR="$HERMES_SKILLS_DIR/autonomous-agents/elysium-swarmloop"
HERMES_CONFIG="$HOME/AppData/Local/hermes/config.yaml"
HERMES_DB="$HOME/.hermes/hermes.db"

# Convert HOME to Windows-style path (C:/Users/...) per git su Windows
WIN_HOME=$(python -c "import os; print(os.path.abspath(os.path.expanduser('$HOME')).replace('\\\\','/'))" 2>/dev/null || echo "$HOME")
TMP_DIR="$WIN_HOME/elysium-install-$$"

# Colori
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

pass()  { echo -e "  ${GREEN}✅ $1${NC}"; }
fail()  { echo -e "  ${RED}❌ $1${NC}"; }
info()  { echo -e "  ${CYAN}→ $1${NC}"; }
warn()  { echo -e "  ${YELLOW}⚠️  $1${NC}"; }
title() { echo -e "\n${CYAN}══ $1 ══${NC}"; }

# =============================================================================
# HELP
# =============================================================================
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat << EOF
Elysium Swarmloop Auto-Installer v$VERSION

Uso:  bash install.sh [--help]

Il script fa:
  1. Clona/aggiorna il repo
  2. Installa la skill in Hermes
  3. Verifica/configura config.yaml
  4. Inizializza il pattern store SQLite
  5. Installa jq (opzionale, solo per bootloader bash)
  6. Testa il bootloader
  7. Report finale
EOF
  exit 0
fi

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════╗"
echo "║   Elysium Swarmloop Auto-Installer v$VERSION    ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"

# =============================================================================
# STEP 1 — CLONA REPO
# =============================================================================
title "Step 1/6 — Scarica la skill"

if git clone --depth=1 "$REPO_URL" "$TMP_DIR" 2>&1; then
  pass "Repo clonato"
else
  fail "Impossibile clonare $REPO_URL. Controlla connessione."
  exit 1
fi

if [ ! -f "$TMP_DIR/SKILL.md" ]; then
  fail "SKILL.md non trovata nel repo clonato"
  ls -la "$TMP_DIR/" 2>/dev/null || true
  exit 1
fi

# =============================================================================
# STEP 2 — INSTALLA SKILL IN HERMES
# =============================================================================
title "Step 2/6 — Copia skill in Hermes"

mkdir -p "$SKILL_DIR/scripts" "$SKILL_DIR/references"
cp "$TMP_DIR/SKILL.md" "$SKILL_DIR/SKILL.md"
[ -f "$TMP_DIR/README.md" ] && cp "$TMP_DIR/README.md" "$SKILL_DIR/README.md" || true
[ -f "$TMP_DIR/SETUP.md" ]  && cp "$TMP_DIR/SETUP.md" "$SKILL_DIR/SETUP.md" || true

if [ -d "$TMP_DIR/scripts" ]; then
  cp -r "$TMP_DIR/scripts/"* "$SKILL_DIR/scripts/" 2>/dev/null || true
  chmod +x "$SKILL_DIR/scripts/"*.sh 2>/dev/null || true
fi

if [ -d "$TMP_DIR/references" ]; then
  cp -r "$TMP_DIR/references/"* "$SKILL_DIR/references/" 2>/dev/null || true
fi

LINES=$(wc -l < "$SKILL_DIR/SKILL.md")
pass "SKILL.md installata ($LINES righe)"
[ -f "$SKILL_DIR/scripts/init-state.sh" ] && pass "Bootloader: scripts/init-state.sh"
[ -f "$SKILL_DIR/references/pattern-store.sql" ] && pass "Pattern store: references/pattern-store.sql"
[ -f "$SKILL_DIR/scripts/install.sh" ] && pass "Installer: scripts/install.sh"

# =============================================================================
# STEP 3 — VERIFICA CONFIG.YAML
# =============================================================================
title "Step 3/6 — Verifica config.yaml"
CONFIG_OK=true

check_config() {
  local key="$1"
  local expected="$2"
  if [ ! -f "$HERMES_CONFIG" ]; then
    CONFIG_OK=false
    return
  fi
  if grep -q "^${key}:\s*${expected}" "$HERMES_CONFIG" 2>/dev/null; then
    pass "  $key = $expected"
  elif grep -q "^${key}:" "$HERMES_CONFIG" 2>/dev/null; then
    warn "  $key non è $expected (trovato: $(grep "^${key}:" "$HERMES_CONFIG" | head -1 | sed 's/^[[:space:]]*//'))"
    CONFIG_OK=false
  else
    warn "  $key NON TROVATA"
    CONFIG_OK=false
  fi
}

if [ -f "$HERMES_CONFIG" ]; then
  check_config "  max_concurrent_children" "100"
  check_config "  max_spawn_depth" "2"
  check_config "  orchestrator_enabled" "true"
  
  if $CONFIG_OK; then
    pass "Config.yaml OK"
  else
    echo ""
    warn "Aggiungi a $HERMES_CONFIG nella sezione delegation:"
    echo "    max_concurrent_children: 100"
    echo "    max_spawn_depth: 2"
    echo "    orchestrator_enabled: true"
  fi
else
  warn "File $HERMES_CONFIG non trovato"
  CONFIG_OK=false
fi

# =============================================================================
# STEP 4 — INIZIALIZZA PATTERN STORE SQLITE
# =============================================================================
title "Step 4/6 — Inizializza pattern store SQLite"
if [ -f "$HERMES_DB" ] && [ -f "$SKILL_DIR/references/pattern-store.sql" ]; then
  PYTHON_CODE=$(cat << 'PYEOF'
import sqlite3, sys, os
db_path = os.path.expanduser(r'~/.hermes/hermes.db')
home = os.path.expanduser('~').replace('\\', '/')
sql_path = home + '/AppData/Local/hermes/skills/autonomous-agents/elysium-swarmloop/references/pattern-store.sql'
try:
    conn = sqlite3.connect(db_path)
    with open(sql_path, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('executions','decomposition_patterns','pitfalls','calibrations')")
    tables = [r[0] for r in cur.fetchall()]
    conn.close()
    print('OK:' + ','.join(tables))
except Exception as e:
    print('ERR:' + str(e))
PYEOF
)
  RESULT=$(python -c "$PYTHON_CODE" 2>&1 || true)
  if [[ "$RESULT" == OK:* ]]; then
    TABLES="${RESULT#OK:}"
    pass "Pattern store SQLite: $TABLES"
  else
    warn "Pattern store: ${RESULT#ERR:}"
  fi
elif [ ! -f "$HERMES_DB" ]; then
  warn "hermes.db non trovato — salto inizializzazione"
else
  warn "pattern-store.sql non trovato"
fi

# =============================================================================
# STEP 5 — VERIFICA/INSTALLA jq (OPZIONALE)
# =============================================================================
title "Step 5/6 — jq (opzionale, serve al bootloader bash)"
if command -v jq &>/dev/null; then
  JQ_VER=$(jq --version 2>/dev/null || echo "?")
  pass "jq già installato ($JQ_VER)"
else
  warn "jq non trovato. Il bootloader bash non funzionerà."
  info "Installa jq: curl -L -o /usr/bin/jq.exe https://github.com/jqlang/jq/releases/download/jq-1.7/jq-win64.exe"
  info "Oppure: la skill funziona anche senza (bootloader è solo un helper)"
fi

# =============================================================================
# STEP 6 — TEST BOOTLOADER
# =============================================================================
title "Step 6/6 — Test bootloader"
if command -v jq &>/dev/null && [ -f "$SKILL_DIR/scripts/init-state.sh" ]; then
  cd "$SKILL_DIR"
  
  echo -e "  ${CYAN}Tier 1 (quick fix):${NC}"
  OUTPUT=$(bash scripts/init-state.sh --json "Fix typo in config" 2>/dev/null || true)
  TIER=$(echo "$OUTPUT" | python -c "import sys,json; print(json.load(sys.stdin)['tier'])" 2>/dev/null || echo "?")
  [ "$TIER" = "1" ] && pass "Tier detection: 1 (quick fix)" || warn "Tier: $TIER (atteso: 1)"
  
  echo -e "  ${CYAN}Tier 3 (API):${NC}"
  OUTPUT=$(bash scripts/init-state.sh --json "Build REST API for booking" 2>/dev/null || true)
  TIER=$(echo "$OUTPUT" | python -c "import sys,json; print(json.load(sys.stdin)['tier'])" 2>/dev/null || echo "?")
  [ "$TIER" = "3" ] && pass "Tier detection: 3 (API)" || warn "Tier: $TIER (atteso: 3)"
  
  echo -e "  ${CYAN}Tier 4 (greenfield):${NC}"
  OUTPUT=$(bash scripts/init-state.sh --json "Build greenfield full-stack platform" 2>/dev/null || true)
  TIER=$(echo "$OUTPUT" | python -c "import sys,json; print(json.load(sys.stdin)['tier'])" 2>/dev/null || echo "?")
  [ "$TIER" = "4" ] && pass "Tier detection: 4 (greenfield)" || warn "Tier: $TIER (atteso: 4)"
  
  rm -f "$SKILL_DIR/.state.json" 2>/dev/null || true
else
  info "Salto test: installa jq per testare il bootloader"
fi

# =============================================================================
# REPORT FINALE
# =============================================================================
echo ""
echo -e "${CYAN}══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Elysium Swarmloop v$VERSION — Installazione completata${NC}"
echo -e "${CYAN}══════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${CYAN}📁 Skill:${NC}     $SKILL_DIR"
echo -e "  ${CYAN}📄 SKILL.md:${NC}  $(wc -l < "$SKILL_DIR/SKILL.md") righe"
echo -e "  ${CYAN}📜 Bootloader:${NC} $(test -f "$SKILL_DIR/scripts/init-state.sh" && echo '✔️ Presente' || echo '❌ Manca')"
echo -e "  ${CYAN}🗄️  Pattern store:${NC} $(test -f "$SKILL_DIR/references/pattern-store.sql" && echo '✔️ Presente' || echo '❌ Manca')"
echo -e "  ${CYAN}⚙️  Config:${NC}     $( $CONFIG_OK && echo '✔️ OK' || echo '⚠️  Da sistemare')"
echo -e "  ${CYAN}🔧 jq:${NC}         $(command -v jq &>/dev/null && echo '✔️ Installato' || echo '⚪ Opzionale')"
echo ""

if ! $CONFIG_OK; then
  echo -e "  ${YELLOW}⚠️  AZIONE RICHIESTA:${NC}"
  echo -e "  ${YELLOW}  Apri $HERMES_CONFIG${NC}"
  echo -e "  ${YELLOW}  e assicurati che nella sezione delegation ci sia:${NC}"
  echo "    max_concurrent_children: 100"
  echo "    max_spawn_depth: 2"
  echo "    orchestrator_enabled: true"
  echo ""
fi

echo -e "  ${CYAN}Per usare la skill in Hermes:${NC}"
echo -e "  ${CYAN}  skill_view(name='elysium-swarmloop')${NC}"
echo ""

# Pulisci
python -c "import shutil; shutil.rmtree('$TMP_DIR', ignore_errors=True)" 2>/dev/null || true
info "Temporanei puliti"
echo ""
