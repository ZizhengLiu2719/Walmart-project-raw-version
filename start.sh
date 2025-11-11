#!/bin/bash
# === Detect terminal emulator ===
TERMINAL_CMD="${TERMINAL:-${XDG_CURRENT_DESKTOP:+x-terminal-emulator}}"
TERMINAL_CMD="${TERMINAL_CMD:-x-terminal-emulator}"

if ! command -v "$TERMINAL_CMD" >/dev/null 2>&1; then
  for term in alacritty kitty gnome-terminal konsole xfce4-terminal xterm wezterm; do
    if command -v "$term" >/dev/null 2>&1; then
      TERMINAL_CMD="$term"
      break
    fi
  done
fi

# === Launch Data Providers ===
(
  cd DataProviders || exit
  "$TERMINAL_CMD" -e bash -c "echo 'Starting Data Providers'; python3 build.py; exec bash" &
)

# === Launch DataFusion ===
(
  cd DataFusion || exit
  "$TERMINAL_CMD" -e bash -c "echo 'Running DataFusion'; npm run dev; exec bash" &
)

# === Launch Frontend ===
(
  cd Frontend_Demo || exit
  "$TERMINAL_CMD" -e bash -c "echo 'Running Frontend'; streamlit run main.py; exec bash" &
)
