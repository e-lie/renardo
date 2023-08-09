# Bundling renardo (FoxDot fork) using pyinstaller

Python developpement environnements can be really hard for beginners : installing FoxDot in the classic way can be completely out of reach for many people.

This repository tries to solve this problem by bundling renardo (all parts of it, since renardo splits FoxDot into several parts) in a pyinstaller based autonomous binary for Linux, MacOS and Windows.

## Usage

```bash
mkdir renardooo
cd renardooo
git clone https://github.com/e-lie/renardo_bundle.git
cd renardo_bundle
bash bundle_linux.sh # bundle_macos
```