#!/usr/bin/env sh
# install_tk_deps.sh — installs Python3 + Tkinter (and pip) on common Linux distros

set -eu

SUDO=""
[ "$(id -u)" -ne 0 ] && SUDO="sudo"

info() { printf "\033[1;34m[INFO]\033[0m %s\n" "$*"; }
err()  { printf "\033[1;31m[ERR]\033[0m  %s\n" "$*" 1>&2; }

have() { command -v "$1" >/dev/null 2>&1; }

install_apt() {
  $SUDO apt-get update
  DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y python3 python3-tk python3-pip
}

install_dnf_yum() {
  if have dnf; then
    $SUDO dnf install -y python3 python3-tkinter python3-pip
  else
    $SUDO yum install -y python3 python3-tkinter python3-pip
  fi
}

install_pacman() {
  $SUDO pacman -Sy --noconfirm python tk python-pip
}

install_zypper() {
  $SUDO zypper --non-interactive refresh
  $SUDO zypper --non-interactive install python3 python3-tk python3-pip
}

install_apk() {
  # try native tkinter package first; fall back to tcl/tk pair
  $SUDO apk add --no-cache python3 py3-pip py3-tkinter 2>/dev/null || \
  $SUDO apk add --no-cache python3 py3-pip tcl tk
}

install_xbps() {
  $SUDO xbps-install -Sy python3 python3-pip python3-tkinter 2>/dev/null || \
  $SUDO xbps-install -Sy python3 python3-pip tk
}

detect_and_install() {
  if [ -f /etc/os-release ]; then
    . /etc/os-release
    ID_LIKE_LO=$(printf "%s" "${ID_LIKE:-}" | tr '[:upper:]' '[:lower:]')
    ID_LO=$(printf "%s" "${ID:-}" | tr '[:upper:]' '[:lower:]')
  else
    ID_LIKE_LO=""; ID_LO=""
  fi

  case "$ID_LO:$ID_LIKE_LO" in
    *debian*:*|*:*debian*|*ubuntu*:*|*:*ubuntu*|*linuxmint*:*|*pop*:*|*elementary*:* )
      info "Detected Debian/Ubuntu family"; install_apt ;;
    *fedora*:*|*rhel*:*|*centos*:*|*rocky*:*|*almalinux*:*|*:*rhel*|*:*fedora* )
      info "Detected RHEL/Fedora family"; install_dnf_yum ;;
    *arch*:*|*manjaro*:*|*:*arch* )
      info "Detected Arch/Manjaro"; install_pacman ;;
    *opensuse*:*|*suse*:*|*:*suse* )
      info "Detected openSUSE"; install_zypper ;;
    *alpine*:*|*:*alpine* )
      info "Detected Alpine"; install_apk ;;
    *void*:*|*:*void* )
      info "Detected Void Linux"; install_xbps ;;
    * )
      if have apt-get; then info "Using apt-get (heuristic)"; install_apt
      elif have dnf || have yum; then info "Using dnf/yum (heuristic)"; install_dnf_yum
      elif have pacman; then info "Using pacman (heuristic)"; install_pacman
      elif have zypper; then info "Using zypper (heuristic)"; install_zypper
      elif have apk; then info "Using apk (heuristic)"; install_apk
      elif have xbps-install; then info "Using xbps (heuristic)"; install_xbps
      else
        err "Unsupported distro: install Python 3 + Tkinter manually."
        exit 1
      fi
      ;;
  esac
}

verify() {
  info "Verifying tkinter import…"
  if python3 - <<'PY'
import sys
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    import subprocess, threading, re
except Exception as e:
    print("FAIL:", e); sys.exit(1)
print("OK: tkinter is available.")
PY
  then
    info "All set. You can run your Tk app."
  else
    err "tkinter import failed. If this is a headless server, ensure an X server (or Xvfb) is available."
    exit 1
  fi
}

detect_and_install
verify
