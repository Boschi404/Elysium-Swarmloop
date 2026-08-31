#!/usr/bin/env bash
# =============================================================================
# install.sh — Elysium Swarmloop Auto-Installer  v0.18.0
# =============================================================================
# Uso:
#   bash install.sh              # installa
#   bash install.sh --dry-run    # mostra solo cosa farebbe (nessuna scrittura)
#   bash install.sh --help
#
# Cosa fa:
#   1. Clona il repo in una cartella temporanea
#   2. Copia SOLO i file runtime della skill (WHITELIST):
#      SKILL.md, README.md, SETUP.md, scripts/*, references/*
#      -> MAI workspaces/, risultati/, benchmark, node_modules
#   3. Backup dei file esistenti prima di sovrascrivere (idempotente)
#   4. Verifica jq + testa il bootloader
#
# Compatibilità: Windows (git-bash), Linux, macOS.
# Percorsi: rispetta $HERMES_HOME se impostato; altrimenti usa il layout
# standard della piattaforma (%LOCALAPPDATA%\hermes su Windows, ~/.hermes altrove).
# Nessun git reset --hard nella cartella skill: gli aggiornamenti si fanno
# ri-eseguendo questo installer (idempotente).
# =============================================================================
set -euo pipefail

VERSION="0.18.0"
REPO_URL="https://github.com/Boschi404/Elysium-Swarmloop.git"
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

# ---- percorsi cross-platform -----------------------------------------------
if command -v python >/dev/null 2>&1; then
  PY_HOME="$(python -c "import os; print(os.path.abspath(os.path.expanduser('~')).replace(chr(92),'/'))" 2>/dev/null || true)"
else
  PY_HOME="$HOME"
fi
PY_HOME="${PY_HOME:-$HOME}"

detect_skills_dir() {
  # 1) $HERMES_HOME esplicito vince sempre
  if [[ -n "${HERMES_HOME:-}" ]]; then
    echo "${HERMES_HOME}/skills"
    return
  fi
  # 2) layout standard per piattaforma
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
      echo "$PY_HOME/AppData/Local/hermes/skills" ;;
    *)
      if [[ -d "$HOME/.hermes/skills" ]]; then
        echo "$HOME/.hermes/skills"
      elif [[ -d "$PY_HOME/AppData/Local/hermes/skills" ]]; then
        echo "$PY_HOME/AppData/Local/hermes/skills"
      else
        echo "$HOME/.hermes/skills"
      fi ;;
  esac
}

SKILLS_ROOT="$(detect_skills_dir)"
SKILL_DIR="$SKILLS_ROOT/autonomous-ai-agents/elysium-swarmloop"
HERMES_DB="$HOME/.hermes/hermes.db"
[[ -n "${HERMES_HOME:-}" ]] && HERMES_DB="$HERMES_HOME/hermes.db"
# Native temp dir (git-bash safe): mktemp -d returns an MSYS path that native
# git resolves differently from bash — use Python tempfile instead.
if command -v python >/dev/null 2>&1; then
  TMP_DIR="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))" 2>/dev/null || true)"
fi
TMP_DIR="${TMP_DIR:-$(mktemp -d 2>/dev/null || echo "${TMPDIR:-/tmp}/elysium-install-$$")}"

# ---- colori -----------------------------------------------------------------
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN=''; NC=''
pass()  { echo "  [OK]   $1"; }
fail()  { echo "  [FAIL] $1"; }
info()  { echo "  ->     $1"; }
warn()  { echo "  [WARN] $1"; }
title() { echo -e "\n== $1 =="; }

[[ "${1:-}" == "--help" || "${1:-}" == "-h" ]] && {
  sed -n '2,20p' "$0"; exit 0
}

echo ""
echo "======================================================="
echo "   Elysium Swarmloop Auto-Installer v$VERSION"
[[ "$DRY_RUN" == true ]] && echo "   MODE: DRY RUN (nessuna scrittura)"
echo "======================================================="
info "Skills dir rilevata: $SKILLS_ROOT"

# =============================================================================
# STEP 1 — CLONA REPO
# =============================================================================
title "Step 1/5 — Scarica la skill"
if [[ "$DRY_RUN" == true && -d "$TMP_DIR/SKILL.md" ]]; then :; fi
if git clone --depth=1 "$REPO_URL" "$TMP_DIR" 2>/dev/null; then
  pass "Repo clonato in $TMP_DIR"
else
  fail "Impossibile clonare $REPO_URL"
  exit 1
fi
[[ -f "$TMP_DIR/SKILL.md" ]] || { fail "SKILL.md non trovata nel clone"; exit 1; }

# =============================================================================
# STEP 2 — COPIA WHITELIST IN HERMES (+ backup)
# =============================================================================
title "Step 2/5 — Copia file runtime (whitelist)"
WHITELIST_TOP="SKILL.md README.md SETUP.md"
copy_one() {
  local src="$1" dst="$2"
  if [[ -e "$dst" ]]; then
    cp "$dst" "$dst.bak-pre-$VERSION" && info "backup: $(basename "$dst").bak-pre-$VERSION"
  fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
}
for f in $WHITELIST_TOP; do
  if [[ "$DRY_RUN" == true ]]; then info "[dry-run] copierei $f"; else copy_one "$TMP_DIR/$f" "$SKILL_DIR/$f"; fi
done
for d in scripts references; do
  for src in "$TMP_DIR/$d"/*; do
    base="$(basename "$src")"
    if [[ "$DRY_RUN" == true ]]; then
      info "[dry-run] copierei $d/$base"
    else
      copy_one "$src" "$SKILL_DIR/$d/$base"
      [[ "$base" == *.sh ]] && chmod +x "$SKILL_DIR/$d/$base" 2>/dev/null || true
    fi
  done
done
if [[ "$DRY_RUN" != true ]]; then
  pass "Skill installata in $SKILL_DIR ($(wc -l < "$SKILL_DIR/SKILL.md") righe SKILL.md)"
fi
info "NOTA: workspaces/, risultati/ e benchmark NON vengono copiati (repo pulito)."
info "Aggiornamenti: ri-esegui questo installer (idempotente, con backup)."

# =============================================================================
# STEP 3 — VERIFICA CONFIG.YAML (via hermes config get)
# =============================================================================
title "Step 3/5 — Verifica config Hermes"
check_cfg() {
  local key="$1" expected="$2" got=""
  if command -v hermes >/dev/null 2>&1; then
    got="$(hermes config get "delegation.$key" 2>/dev/null | tail -1 || true)"
  fi
  if [[ "$got" == "$expected" ]]; then
    pass "delegation.$key = $got"
  elif [[ -z "$got" || "$got" == *"Error"* || "$got" == *"not found"* ]]; then
    warn "delegation.$key non leggibile — imposta con:"
    echo "         hermes config set delegation.$key $expected"
  else
    warn "delegation.$key = $got (atteso $expected):"
    echo "         hermes config set delegation.$key $expected"
  fi
}
check_cfg max_concurrent_children 100
check_cfg max_spawn_depth 2
check_cfg orchestrator_enabled true
check_cfg child_timeout_seconds 600

# =============================================================================
# STEP 4 — JQ (opzionale, per bootloader bash)
# =============================================================================
title "Step 4/5 — jq"
if command -v jq >/dev/null 2>&1; then
  pass "jq trovato: $(jq --version 2>/dev/null || echo '?')"
else
  warn "jq non trovato: il bootloader bash non funzionerà senza."
  info "Windows: curl -L -o /usr/bin/jq.exe https://github.com/jqlang/jq/releases/download/jq-1.7/jq-win64.exe && chmod +x /usr/bin/jq.exe"
  info "Linux/macOS: apt install jq | brew install jq"
fi

# =============================================================================
# STEP 5 — TEST BOOTLOADER
# =============================================================================
title "Step 5/5 — Test bootloader"
if command -v jq >/dev/null 2>&1 && [[ "$DRY_RUN" != true ]]; then
  cd "$SKILL_DIR"
  for pair in "Fix typo in config:1" "Build REST API for booking:3" "Build greenfield full-stack platform:4"; do
    goal="${pair%%:*}"; expected="${pair##*:}"
    tier="$(bash scripts/init-state.sh --json "$goal" 2>/dev/null | python -c "import sys,json; print(json.load(sys.stdin)['tier'])" 2>/dev/null || echo "?")"
    if [[ "$tier" == "$expected" ]]; then pass "tier detection: '$goal' -> T$tier"
    else fail "tier detection: '$goal' -> T$tier (atteso $expected)"; fi
  done
  rm -f .elysium-state.json .state.json 2>/dev/null || true
elif [[ "$DRY_RUN" == true ]]; then
  info "[dry-run] salto test bootloader"
else
  warn "jq assente: salto test bootloader (la skill funziona comunque)"
fi

# =============================================================================
# REPORT FINALE
# =============================================================================
rm -rf "$TMP_DIR" 2>/dev/null || true
echo ""
echo "======================================================="
if [[ "$DRY_RUN" == true ]]; then
  echo "  DRY RUN completato — nessuna modifica scritta."
else
  echo "  Elysium Swarmloop v$VERSION — Installazione completata"
  echo "  Skill: $SKILL_DIR"
fi
echo "======================================================="
echo ""
