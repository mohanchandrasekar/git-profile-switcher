# 🚀 git-profile-switcher

### Manage multiple Git identities (work / personal) with one simple command.

![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)
![Python version](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS-lightgrey)
![Status](https://img.shields.io/badge/status-stable-brightgreen)

`git-profile-switcher` is a lightweight cross-platform tool that lets you instantly switch between multiple Git identities (e.g., **personal** and **work** accounts) without editing config files manually.

Ideal for developers, consultants, students, open-source contributors, and anyone using multiple GitHub/GitLab accounts on the same machine.

---

# ✨ Features

* ✔️ Switch Git identity with a single command
* ✔️ Separate profiles for **personal**, **work**, **school**, etc.
* ✔️ Automatically updates global Git `user.name` and `user.email`
* ✔️ Safe and non-intrusive (does not modify your repos)
* ✔️ Optional profile creation wizard
* ✔️ Linux GUI version (`git-profile-gui`) using Zenity
* ✔️ Clean folder-based profiles (`~/.config/git-profiles/...`)
* ✔️ Fully cross-platform (Linux + macOS)
* ✔️ Works with SSH key setups for multiple GitHub accounts

---

# 📦 Installation

### **Install from source (recommended during development)**

```bash
git clone https://github.com/mohanchandrasekar/git-profile-switcher.git
cd git-profile-switcher

python3 -m venv .venv
source .venv/bin/activate

pip install -e .
```

### (Coming soon) Install from PyPI

```bash
pip install git-profile-switcher
```

---

# 🛠 Quick Start

Initialize:

```bash
git-profile init
```

Create your first profiles:

```bash
git-profile create personal --activate
git-profile create work
```

Switch between them:

```bash
git-profile use work
git-profile use personal
```

Check current Git identity:

```bash
git-profile current
```

---

# 🗂 Profile Storage

Profiles are stored here:

```
~/.config/git-profiles/
  ├── personal.gitconfig
  ├── work.gitconfig
  └── <anyname>.gitconfig
```

A profile file looks like:

```ini
[user]
    name = Your Name
    email = you@example.com
[core]
    editor = nano
```

---

# 🔧 Commands

### **List available profiles**

```bash
git-profile list
```

### **Show profile contents**

```bash
git-profile show work
```

### **Create profile interactively**

```bash
git-profile create <name>
```

### **Create & activate immediately**

```bash
git-profile create work --activate
```

### **Interactively overwrite existing**

```bash
git-profile create work --force
```

---

# 🖥 GUI Mode (Linux Only)

Install Zenity:

```bash
sudo apt install zenity
```

Launch GUI profile switcher:

```bash
git-profile-gui
```

A popup window lets you choose between your configured identities.

---

# 🔑 Using Multiple SSH Keys (Optional)

If you use separate GitHub accounts for work vs personal, create keys:

```bash
ssh-keygen -t ed25519 -C "personal@example.com" -f ~/.ssh/id_ed25519_personal
ssh-keygen -t ed25519 -C "work@example.com"     -f ~/.ssh/id_ed25519_work
```

Configure SSH:

```ini
# ~/.ssh/config

Host github-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal

Host github-work
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_work
```

Use correct remotes:

```bash
git remote set-url origin git@github-personal:username/repo.git
git remote set-url origin git@github-work:company/repo.git
```

---

# 📸 Screenshots (coming soon)

You can add these files later:

```
docs/
  ├── images/
  │     ├── cli.png
  │     ├── profiles-folder.png
  │     └── gui.png
```

Example usage screenshots will go here.

---

# ⚙️ Architecture

```
git-profile-switcher/
  ├── src/git_profile_switcher/
  │     ├── cli.py        ← Core logic
  │     ├── gui.py        ← Zenity GUI wrapper
  │     └── __init__.py
  ├── README.md
  ├── LICENSE
  └── pyproject.toml
```

`git-profile use <name>` does:

1. Read profile file
2. Extract `[user]` → name + email
3. Set them using `git config --global`
4. Update snapshot at `~/.gitconfig-active`
5. Display active identity

---

# 🧪 Contributing

Pull requests are welcome!

Future roadmap:

* [ ] Windows support (PowerShell GUI)
* [ ] Profile-level SSH switching
* [ ] Automatic detection per repository
* [ ] GUI using Tkinter / PyQt
* [ ] Shell autocomplete
* [ ] Brew and Snap packages

---

# ⭐ Support

If this project saves you time or frustration:

👉 **Please star the repo!** ⭐

It helps visibility and encourages future improvements.

---

