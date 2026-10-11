#!/bin/sh
# Print a short, self-contained terminal session for previews and screenshots.
# It works in a throwaway Git repository and changes nothing else:
#
#     sh scripts/demo.sh
#
# Set DEMO_USER and DEMO_HOST to change the names shown in the prompt.

set -eu

user=${DEMO_USER:-$(id -un)}
host=${DEMO_HOST:-$(hostname -s 2>/dev/null || hostname)}
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cd "$work"

prompt() {
  printf '%s@%s %s %% %s' "$user" "$host" "${PWD##*/}" "${1:-}"
}

# Show a zsh-style prompt with a command line, then run a command.
step() {
  prompt "$1"
  printf '\n'
  shift
  "$@"
}

colors() {
  names="black red green yellow blue magenta cyan white"
  for base in 30 90; do
    if [ "$base" = 30 ]; then printf '%-8s' normal; else printf '%-8s' bright; fi
    i=0
    for name in $names; do
      printf '\033[%sm%-9s\033[0m' "$((base + i))" "$name"
      i=$((i + 1))
    done
    printf '\n'
  done
  printf '\033[1mbold\033[0m  \033[2mdim\033[0m  \033[3mitalic\033[0m  '
  printf '\033[4munderline\033[0m  \033[7minverse\033[0m  '
  printf '\033[32msuccess\033[0m  \033[33mwarning\033[0m  '
  printf '\033[34minfo\033[0m  \033[31merror\033[0m\n'
}

# Match the default macOS ls colors (LSCOLORS=exfxcxdxbxegedabagacad).
listing() {
  if ls --color=auto / >/dev/null 2>&1; then
    LS_COLORS='di=34:ln=35:so=32:pi=33:ex=31:bd=34;46:cd=34;43:su=30;41:sg=30;46:tw=30;42:ow=30;43' \
      ls -C --color=always
  else
    CLICOLOR_FORCE=1 ls -CG
  fi
}

# A fictional ledger project with one commit pending.
mkdir ledger && cd ledger
export GIT_AUTHOR_DATE='2026-01-05T09:30:00Z' GIT_COMMITTER_DATE='2026-01-05T09:30:00Z'
git init -q -b main
git config user.name Demo
git config user.email demo@example.com
git config color.ui always
mkdir src tests
printf 'opening  1200.00\nrent     -850.00\n' > ledger.txt
printf '#!/bin/sh\necho balance\n' > report.sh && chmod +x report.sh
printf '# Ledger\n' > README.md
git add . && git commit -q -m "Start the ledger"
printf 'notes\n' > tests/notes.md
git add tests && git commit -q -m "Add test notes"
printf 'opening  1200.00\nrent     -900.00\ncoffee     -4.50\n' > ledger.txt
printf 'draft\n' > draft.txt

clear 2>/dev/null || true
step 'sh terminal-colors.sh' colors
step 'git status -sb' git status -sb
step 'git diff' git diff
step 'git log --oneline --graph' git log --oneline --graph --decorate
step 'ls' listing
prompt
