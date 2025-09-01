# Raspberry Pi 5 Development Environment Setup

This guide explains how to configure your Raspberry Pi 5 and set up a Python development environment with a virtual environment (`venv`), Git integration, and VS Code.

---

## 1. Configure Your Raspberry Pi 5

- Set up your Raspberry Pi 5 with Raspberry Pi OS.
- Connect to Wi-Fi and ensure you have internet access.
- Update your system:
  ```bash
  sudo apt update
  sudo apt upgrade
  ```

## 2. Choose Your Browser

- We recommend Firefox for browsing GitHub and documentation:
  ```bash
  sudo apt install firefox-esr
  ```

## 3. Install VS Code

- Install VS Code using the package manager:
  ```bash
  sudo apt install code
  ```

## 4. Connect to Git

- Install Git if it's not already present:
  ```bash
  sudo apt install git
  ```
- Configure your Git identity:
  ```bash
  git config --global user.name "Your Name"
  git config --global user.email "you@example.com"
  ```

## 5. Generate an SSH Key and Add to GitHub

- Open a terminal.
- Generate a new SSH key:
  ```bash
  ssh-keygen -t ed25519 -C "you@example.com"
  ```
- Copy the public key:
  ```bash
  cat ~/.ssh/id_ed25519.pub
  ```
- Go to [GitHub SSH settings](https://github.com/settings/keys).
- Click "New SSH key", paste your key, and save.

## 6. Clone the Repository

- In your terminal, run:
  ```bash
  git clone git@github.com:ejm22/WRO-FE-XX.git
  ```

## 7. Open the Project in VS Code and Install Python Extension

- Open VS Code and open the folder manually.
- Go to Extensions (Ctrl+Shift+X) and install the "Python" extension by Microsoft.

## 8. Create and Activate a Virtual Environment (with System Packages)

- Create a virtual environment that has access to system packages:
  ```bash
  python3 -m venv XX_2025_venv --system-site-packages
  ```
- Navigate to the directory containing your `pyproject.toml`:
  ```bash
  cd WRO-FE-XX/code
  ```
- Activate the virtual environment:
  ```bash
  source XX_2025_venv/bin/activate
  ```

## 9. Select the Python Interpreter

- In VS Code, press `Ctrl+Shift+P` and type `Python: Select Interpreter`.
- Choose the interpreter from the `XX_2025_venv/bin` directory.

## 10. Install Your Project and Dependencies

- Our project has a `pyproject.toml` file. This file describes our project’s dependencies and settings (similar to `package.json` in Node.js projects). It is used by modern Python tools to manage packages.
- Install your project in "editable" mode so changes are picked up automatically:
  ```bash
  pip install -e .
  ```

## 11. Uninstall Numpy (Required for Picamera2 Compatibility)

- Picamera2 requires an older version of numpy, but OpenCV installs the newest version by default. Uninstall numpy to let Picamera2 install the correct version:
  ```bash
  pip uninstall numpy
  ```

## 12. Run Your Code

- You can now run the Python scripts. If you aren't in the right directory, navigate to the correct one.
  ```bash
  cd WRO-FE-XX/code/XX_2025_package
  ```

- Then, run the code !
  ```bash
  python main.py
  ```

---

**You're all set!** Your Raspberry Pi 5 is now configured for Python development with Git and VS Code with team Double-X's code !
