#!/usr/bin/env bash
# Living-docs adoption installer.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/mpklu/living-doc/main/install/install.sh | bash
#   curl -fsSL .../install.sh -o install.sh && bash install.sh   # cautious path
#
# Flags:
#   --ref <tag|branch>   Methodology version to fetch (default: main)
#   --dry-run            Show what would be installed; write nothing
#   --force              Overwrite existing files (off by default — destructive)
#   --help               This message
#
# Designed to be idempotent: re-running on a populated repo is safe.
# Existing files are skipped with a clear notice unless --force.
#
# See knowledge/concepts/methodology/prompts.md and the install/README.md
# in the upstream repo for the methodology this encodes.

set -euo pipefail

# ──────────────────────────────────────────────────────────────────
# Constants & defaults
# ──────────────────────────────────────────────────────────────────
readonly REPO_OWNER="mpklu"
readonly REPO_NAME="living-doc"
REF="main"
DRY_RUN=0
FORCE=0
TARGET_DIR="$(pwd)"

# Filled in by detect_*
KIND=""           # greenfield | brownfield
HOOK_FRAMEWORK="" # pre-commit | husky | lefthook | none
HAS_GITHUB=0
GROUPS_TO_INSTALL=() # populated by mode selection

# Tmp staging dir; cleaned on exit
TMP_DIR=""
cleanup() { [[ -n "${TMP_DIR}" && -d "${TMP_DIR}" ]] && rm -rf "${TMP_DIR}"; }
trap cleanup EXIT

# ──────────────────────────────────────────────────────────────────
# Output helpers
# ──────────────────────────────────────────────────────────────────
if [[ -t 1 ]]; then
  C_RESET=$'\033[0m'; C_BOLD=$'\033[1m'; C_DIM=$'\033[2m'
  C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'; C_RED=$'\033[31m'; C_BLUE=$'\033[34m'
else
  C_RESET=""; C_BOLD=""; C_DIM=""; C_GREEN=""; C_YELLOW=""; C_RED=""; C_BLUE=""
fi

info()  { printf '%s\n' "$*"; }
ok()    { printf '%s✓%s %s\n' "$C_GREEN" "$C_RESET" "$*"; }
skip()  { printf '%s↷%s %s\n' "$C_DIM" "$C_RESET" "$*"; }
warn()  { printf '%s!%s %s\n' "$C_YELLOW" "$C_RESET" "$*" >&2; }
err()   { printf '%s✗%s %s\n' "$C_RED" "$C_RESET" "$*" >&2; }
hdr()   { printf '\n%s%s%s\n' "$C_BOLD" "$*" "$C_RESET"; }

die() { err "$*"; exit 1; }

# Prompt with default. Returns 0 for yes, 1 for no.
# Args: <prompt> <default Y|n>
ask() {
  local prompt="$1" default="${2:-Y}" reply
  local hint="[Y/n]"
  [[ "$default" == "n" ]] && hint="[y/N]"
  printf '%s %s ' "$prompt" "$hint"
  if ! read -r reply; then reply=""; fi
  reply="${reply:-$default}"
  case "$reply" in
    [yY]|[yY][eE][sS]) return 0 ;;
    [nN]|[nN][oO])     return 1 ;;
    q|Q|quit) info "Aborted."; exit 0 ;;
    *) ask "$prompt" "$default" ;;
  esac
}

# ──────────────────────────────────────────────────────────────────
# Args
# ──────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ref)      REF="$2"; shift 2 ;;
    --dry-run)  DRY_RUN=1; shift ;;
    --force)    FORCE=1; shift ;;
    --help|-h)
      sed -n '2,18p' "$0" 2>/dev/null | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) die "Unknown flag: $1 (try --help)" ;;
  esac
done

readonly RAW_BASE="https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/${REF}"

# ──────────────────────────────────────────────────────────────────
# Pre-flight
# ──────────────────────────────────────────────────────────────────
command -v curl >/dev/null 2>&1 || die "curl is required."

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/living-doc-install.XXXXXX")"

# ──────────────────────────────────────────────────────────────────
# Detection
# ──────────────────────────────────────────────────────────────────
detect_kind() {
  # Bias toward brownfield when ambiguous; greenfield only when the
  # signals are clear.
  local commit_count=0 source_files=0
  if [[ -d .git ]]; then
    commit_count="$(git rev-list --count HEAD 2>/dev/null || echo 0)"
  fi
  # Count "real" source files (exclude common docs/config noise).
  source_files="$(find . -maxdepth 4 -type f \
    \( -name '*.py' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' \
       -o -name '*.jsx' -o -name '*.go' -o -name '*.rs' -o -name '*.rb' \
       -o -name '*.java' -o -name '*.kt' -o -name '*.swift' \
       -o -name '*.c' -o -name '*.cpp' -o -name '*.h' -o -name '*.hpp' \
       -o -name '*.cs' -o -name '*.php' -o -name '*.scala' \) \
    -not -path './.git/*' -not -path './node_modules/*' -not -path './vendor/*' \
    2>/dev/null | head -5 | wc -l | tr -d ' ')"

  if [[ "$commit_count" -le 2 && "$source_files" -le 1 ]]; then
    KIND="greenfield"
  else
    KIND="brownfield"
  fi
}

detect_hook_framework() {
  if [[ -f .pre-commit-config.yaml ]]; then HOOK_FRAMEWORK="pre-commit"
  elif [[ -d .husky ]];                then HOOK_FRAMEWORK="husky"
  elif [[ -f lefthook.yml ]];           then HOOK_FRAMEWORK="lefthook"
  else                                       HOOK_FRAMEWORK="pre-commit"  # sensible default
  fi
}

detect_github() {
  HAS_GITHUB=0
  if [[ -d .github ]]; then HAS_GITHUB=1; return; fi
  if git remote get-url origin 2>/dev/null | grep -q github.com; then HAS_GITHUB=1; fi
}

# ──────────────────────────────────────────────────────────────────
# Manifest fetch + parse
# ──────────────────────────────────────────────────────────────────
fetch() {
  # Args: <url> <dest>
  local url="$1" dest="$2"
  if ! curl -fsSL "$url" -o "$dest"; then
    die "Failed to fetch ${url}"
  fi
}

# Manifest entries become 4 parallel arrays (bash 3.2: no associative arrays).
MANIFEST_GROUPS=()
MANIFEST_SRCS=()
MANIFEST_DESTS=()
MANIFEST_MODES=()

load_manifest() {
  local manifest="${TMP_DIR}/manifest.txt"
  fetch "${RAW_BASE}/install/manifest.txt" "$manifest"

  # Parse: group:src -> dest (mode)
  local line group rest src dest mode
  while IFS= read -r line || [[ -n "$line" ]]; do
    # Strip trailing CR (Windows line endings just in case)
    line="${line%$'\r'}"
    # Skip blanks/comments
    [[ -z "${line// }" ]] && continue
    [[ "$line" =~ ^[[:space:]]*# ]] && continue

    group="${line%%:*}"
    rest="${line#*:}"
    src="${rest%% -> *}"
    rest="${rest#* -> }"
    dest="${rest%% (*}"
    mode="${rest#*(}"
    mode="${mode%)*}"

    # Substitute {kind}
    src="${src//\{kind\}/$KIND}"
    dest="${dest//\{kind\}/$KIND}"

    MANIFEST_GROUPS+=("$group")
    MANIFEST_SRCS+=("$src")
    MANIFEST_DESTS+=("$dest")
    MANIFEST_MODES+=("$mode")
  done < "$manifest"
}

# ──────────────────────────────────────────────────────────────────
# Mode selection
# ──────────────────────────────────────────────────────────────────
select_groups_recommended() {
  GROUPS_TO_INSTALL=(core cli "hook-${HOOK_FRAMEWORK}" prompts)
  if [[ "$HAS_GITHUB" -eq 1 ]]; then
    GROUPS_TO_INSTALL+=(action)
  fi
}

select_groups_custom() {
  GROUPS_TO_INSTALL=()
  ask "  core    — CLAUDE.md, knowledge/, schema (the minimum)?" Y && GROUPS_TO_INSTALL+=(core)
  ask "  cli     — scripts/drift-check + scripts/validate-articles (zero-dep Python)?" Y && GROUPS_TO_INSTALL+=(cli)

  local hook_label="$HOOK_FRAMEWORK"
  [[ -z "$hook_label" ]] && hook_label="pre-commit (no existing config detected)"
  if ask "  hook    — pre-commit hook for the same-task rule (detected: $hook_label)?" Y; then
    GROUPS_TO_INSTALL+=("hook-${HOOK_FRAMEWORK}")
  fi

  local action_hint="GitHub remote not detected — skip unless this will become a GitHub repo"
  [[ "$HAS_GITHUB" -eq 1 ]] && action_hint="GitHub remote detected"
  if ask "  action  — PR-time GitHub Action ($action_hint)?" $([[ "$HAS_GITHUB" -eq 1 ]] && echo Y || echo n); then
    GROUPS_TO_INSTALL+=(action)
  fi

  ask "  prompts — paste-able Claude prompt to bootstrap your first 3 articles?" Y && GROUPS_TO_INSTALL+=(prompts)
}

# ──────────────────────────────────────────────────────────────────
# Plan + execute
# ──────────────────────────────────────────────────────────────────
group_selected() {
  # Args: <group>
  local g
  for g in "${GROUPS_TO_INSTALL[@]}"; do
    [[ "$g" == "$1" ]] && return 0
  done
  return 1
}

# For each manifest entry whose group is selected, decide action and print.
# Returns 0 if there's any work to do, 1 if nothing.
print_plan() {
  local i src dest mode group action exists
  local any=0
  for i in "${!MANIFEST_GROUPS[@]}"; do
    group="${MANIFEST_GROUPS[$i]}"
    group_selected "$group" || continue

    src="${MANIFEST_SRCS[$i]}"
    dest="${MANIFEST_DESTS[$i]}"
    mode="${MANIFEST_MODES[$i]}"

    exists=0
    [[ -e "$dest" ]] && exists=1

    if [[ "$exists" -eq 1 && "$FORCE" -eq 0 ]]; then
      case "$mode" in
        *merge*) action="merge-needed" ;;
        *)       action="skip-exists"  ;;
      esac
    else
      action="write"
    fi

    case "$action" in
      write)         printf '  %s+%s write   %s\n' "$C_GREEN"  "$C_RESET" "$dest"; any=1 ;;
      skip-exists)   printf '  %s↷%s skip    %s %s(already exists)%s\n' "$C_DIM" "$C_RESET" "$dest" "$C_DIM" "$C_RESET" ;;
      merge-needed)  printf '  %s~%s merge   %s %s(exists; will print snippet, won'\''t overwrite)%s\n' "$C_YELLOW" "$C_RESET" "$dest" "$C_DIM" "$C_RESET"; any=1 ;;
    esac
  done
  [[ "$any" -eq 1 ]]
}

execute_plan() {
  local i src dest mode group exists target_parent staged
  for i in "${!MANIFEST_GROUPS[@]}"; do
    group="${MANIFEST_GROUPS[$i]}"
    group_selected "$group" || continue

    src="${MANIFEST_SRCS[$i]}"
    dest="${MANIFEST_DESTS[$i]}"
    mode="${MANIFEST_MODES[$i]}"

    exists=0
    [[ -e "$dest" ]] && exists=1

    if [[ "$exists" -eq 1 && "$FORCE" -eq 0 ]]; then
      case "$mode" in
        *merge*)
          warn "  $dest already exists — printing snippet for manual merge:"
          printf '%s---8<--- BEGIN %s ---8<---%s\n' "$C_DIM" "$src" "$C_RESET"
          curl -fsSL "${RAW_BASE}/${src}" || warn "  (failed to fetch snippet)"
          printf '%s---8<--- END %s ---8<---%s\n' "$C_DIM" "$src" "$C_RESET"
          ;;
        *)
          skip "$dest (already exists)"
          ;;
      esac
      continue
    fi

    if [[ "$DRY_RUN" -eq 1 ]]; then
      ok "would write $dest"
      continue
    fi

    target_parent="$(dirname "$dest")"
    [[ "$target_parent" != "." ]] && mkdir -p "$target_parent"

    staged="${TMP_DIR}/staged-${i}"
    if ! curl -fsSL "${RAW_BASE}/${src}" -o "$staged"; then
      err "  failed to fetch ${src} from ${RAW_BASE}/${src}"
      continue
    fi
    mv "$staged" "$dest"
    case "$mode" in *exec*) chmod +x "$dest" ;; esac
    ok "wrote $dest"
  done
}

# ──────────────────────────────────────────────────────────────────
# Summary
# ──────────────────────────────────────────────────────────────────
print_summary() {
  hdr "✓ Living-docs methodology installed."

  info ""
  info "${C_BOLD}Next steps${C_RESET}"

  if group_selected prompts; then
    local prompt_action
    if [[ "$KIND" == "brownfield" ]]; then
      prompt_action="scan the repo and write 3 thin articles"
    else
      prompt_action="ask anchor questions, then write 3 articles"
    fi
    cat <<EOF

  1. Open Claude (Claude Code, claude.ai, or any Claude tool) in this directory.
  2. Open ${C_BOLD}LIVING_DOCS_FIRST_PROMPT.md${C_RESET}, copy the section below the '---'.
  3. Paste into Claude. It'll ${prompt_action} in knowledge/concepts/.
  4. Review the articles, then commit.
  5. Delete LIVING_DOCS_FIRST_PROMPT.md once done — it's single-use scaffolding.
EOF
  else
    cat <<'EOF'

  1. Open CLAUDE.md and replace any {{Project Name}} placeholders.
  2. Read LIVING_DOCS_OVERVIEW.md (10 min) at:
       https://github.com/mpklu/living-doc/blob/main/LIVING_DOCS_OVERVIEW.md
  3. Write your first 3 thin concept articles in knowledge/concepts/.
EOF
  fi

  info ""
  info "${C_BOLD}Also installed${C_RESET}"
  group_selected cli && info "  - scripts/drift-check + scripts/validate-articles (run anytime)"
  case " ${GROUPS_TO_INSTALL[*]} " in
    *" hook-pre-commit "*) info "  - .pre-commit-config.yaml — run: ${C_DIM}pre-commit install${C_RESET}" ;;
    *" hook-husky "*)      info "  - .husky/pre-commit — run: ${C_DIM}husky install${C_RESET} if not already" ;;
    *" hook-lefthook "*)   info "  - lefthook.yml — run: ${C_DIM}lefthook install${C_RESET}" ;;
  esac
  group_selected action && info "  - .github/workflows/living-docs-drift-check.yml — active on next PR"

  info ""
  info "${C_BOLD}Suggested first commit${C_RESET}"
  info "  ${C_DIM}git add -A && git commit -m 'adopt living-docs methodology'${C_RESET}"
  info ""
  info "${C_DIM}Methodology pinned to:${C_RESET} ${REF}"
  info "${C_DIM}Re-run safe.${C_RESET} Existing files are skipped unless --force."
  info ""
}

# ──────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────
main() {
  hdr "Living-docs methodology installer"
  info "${C_DIM}Pinning to ${REF} from ${REPO_OWNER}/${REPO_NAME}.${C_RESET}"
  [[ "$DRY_RUN" -eq 1 ]] && warn "Dry-run mode: no files will be written."

  hdr "1. Detecting environment"
  detect_kind
  detect_hook_framework
  detect_github

  info "  Project type:    ${C_BOLD}${KIND}${C_RESET}"
  info "  Hook framework:  ${HOOK_FRAMEWORK}${HAS_GITHUB:+ (default if no preference)}"
  info "  GitHub remote:   $([[ $HAS_GITHUB -eq 1 ]] && echo yes || echo no)"
  info ""
  ask "Detection looks right?" Y || die "Aborted. Re-run when ready, or override with --kind."

  hdr "2. Loading manifest"
  load_manifest
  ok "Loaded ${#MANIFEST_GROUPS[@]} entries from manifest.txt"

  hdr "3. Choose install mode"
  info "  ${C_BOLD}1)${C_RESET} Recommended setup (everything appropriate for this repo)"
  info "  ${C_BOLD}2)${C_RESET} Pick options one at a time"
  if ask "Use recommended setup?" Y; then
    select_groups_recommended
  else
    info ""
    info "  ${C_BOLD}Choose what to install${C_RESET}"
    select_groups_custom
  fi

  if [[ ${#GROUPS_TO_INSTALL[@]} -eq 0 ]]; then
    die "Nothing selected. Aborted."
  fi

  hdr "4. Plan"
  info "  Groups: ${GROUPS_TO_INSTALL[*]}"
  info ""
  if ! print_plan; then
    info ""
    warn "Nothing to do — every target already exists. Use --force to overwrite."
    exit 0
  fi
  info ""
  ask "Proceed?" Y || die "Aborted."

  hdr "5. Installing"
  execute_plan

  print_summary
}

main "$@"
