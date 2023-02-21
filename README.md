# Consolo

Utility for pseudo-mounting an AWS lambda filesystem locally.
Supports (as default) hot reloading.

## What do I do with my mouth
Pronounced "Con Solo", like "Han Solo".

![image](https://user-images.githubusercontent.com/419355/220446135-92ac6915-da21-4a29-8fd1-13bfe723433a.png)

## Installation

### Single file

`curl -s https://raw.githubusercontent.com/ahonnecke/consolo/main/install.sh | bash`

### Pip install

TODO: remove this TODO

## TODO

- On imaging a lambda, save the manifest of downloaded files locally.
  - get file list from the archive
  - save file list as manifest

- packaging for pip
- AST files before upload
- Follow logs while watching
- tests
