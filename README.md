[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=ahonnecke_consolo&metric=bugs)](https://sonarcloud.io/summary/new_code?id=ahonnecke_consolo)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=ahonnecke_consolo&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=ahonnecke_consolo)
[![Quality Gate
Status](https://sonarcloud.io/api/project_badges/measure?project=ahonnecke_consolo&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ahonnecke_consolo)

# Consolo

Utility for pseudo-mounting an AWS lambda filesystem locally.
Supports (as default) hot reloading.

## Examples

Start hot syncing
``` bash
consolo --profile-name dev  --function-name myProject  --path /src/code/myproject
```

Upload from local to cloud
``` bash
consolo --profile-name dev  --function-name myProject  --path /src/code/myproject --upload
```

Download from cloud to local
``` bash
consolo --profile-name dev  --function-name myProject  --path /src/code/myproject --download
```

## What do I do with my mouth
Pronounced "Con Solo", like "Han Solo".

![image](https://user-images.githubusercontent.com/419355/220446135-92ac6915-da21-4a29-8fd1-13bfe723433a.png)

## Installation

### Single file

`curl -s https://raw.githubusercontent.com/ahonnecke/consolo/main/install.sh | bash`

### Pip install

NOT CURRENTLY SUPPORTED

- TODO
  - Package for pip
  - Add to pypy
  - Refactor into multiple files

## TODO

- TESTING: Capture and deal with rapid multi-file changes
- List available functions
- AST files before upload
- Unit tests
- Follow logs while watching

## DONE

- Ignore new files added by pytest

## Usage

`consolo.py --profile-name dev-power --function-name myLambda --path /home/ahonnecke/src/my_lambda/`

## examples

``` bash
ahonnecke@antonym:~/src/v2x-messenger$ consolo.py \
  --profile-name dev-power \
  --function-name v2x-messenger__cipt-status-ingestion \
  --path /home/ahonnecke/src/v2x-messenger/lambdas/cipt_status_ingestion/
```

- With the profile 
 - `dev-power`
- Against the lambda 
 - v2x-messenger__cipt-status-ingestion`
- Mapped on top of the local directory
 - `/home/ahonnecke/src/v2x-messenger/lambdas/cipt_status_ingestion/`

![image](https://user-images.githubusercontent.com/419355/220725338-aa16369b-b27c-442d-b2e2-d60ca64cf7fc.png)

### publish

``` bash
pdm publish --username $PIP_USERNAME --password $PIP_PW
```
