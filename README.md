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

``` bash
pip install consolo
```

``` bash
ahonnecke@antonym:~/src/consolo$ pip install --upgrade consolo
Requirement already satisfied: consolo in /home/ahonnecke/.pyenv/versions/3.8.13/lib/python3.8/site-packages (0.2.3)
Collecting consolo
  Downloading consolo-0.2.5-py3-none-any.whl (6.6 kB)
Requirement already satisfied: argdantic>=0.3.0 in /home/ahonnecke/.pyenv/versions/3.8.13/lib/python3.8/site-packages (from consolo) (0.3.0)
Requirement already satisfied: requests>=2.28.2 in /home/ahonnecke/.pyenv/versions/3.8.13/lib/python3.8/site-packages (from consolo) (2.28.2)
Requirement already satisfied: watchdog>=2.3.1 in /home/ahonnecke/.pyenv/versions/3.8.13/lib/python3.8/site-packages (from consolo) (2.3.1)
Requirement already satisfied: boto3>=1.26.87 in /home/ahonnecke/.pyenv/versions/3.8.13/lib/python3.8/site-packages (from consolo) (1.26.87)
Requirement already satisfied: pydantic>=1.10.0 in /home/ahonnecke/.pyenv/versions/3.8.13/lib/python3.8/site-packages (from argdantic>=0.3.0->consolo) (1.10.4)
Requirement already satisfied: s3transfer<0.7.0,>=0.6.0 in /home/ahonnecke/.pyenv/versions/3.8.13/lib/python3.8/site-packages (from boto3>=1.26.87->consolo) (0.6.0)
Requirement already satisfied: botocore<1.30.0,>=1.29.87 in /home/ahonnecke/.pyenv/versions/3.8.13/lib/python3.8/site-packages (from boto3>=1.26.87->consolo) (1.29.87)
Requirement already satisfied: jmespath<2.0.0,>=0.7.1 in /home/ahonnecke/.pyenv/versions/3.8.13/lib/python3.8/site-packages (from boto3>=1.26.87->consolo) (1.0.1)
Requirement already satisfied: charset-normalizer<4,>=2 in /home/ahonnecke/.pyenv/versions/3.8.13/lib/python3.8/site-packages (from requests>=2.28.2->consolo) (2.1.1)
Requirement already satisfied: urllib3<1.27,>=1.21.1 in /home/ahonnecke/.pyenv/versions/3.8.13/lib/python3.8/site-packages (from requests>=2.28.2->consolo) (1.26.14)
Requirement already satisfied: certifi>=2017.4.17 in /home/ahonnecke/.pyenv/versions/3.8.13/lib/python3.8/site-packages (from requests>=2.28.2->consolo) (2022.12.7)
Requirement already satisfied: idna<4,>=2.5 in /home/ahonnecke/.pyenv/versions/3.8.13/lib/python3.8/site-packages (from requests>=2.28.2->consolo) (3.4)
Requirement already satisfied: python-dateutil<3.0.0,>=2.1 in /home/ahonnecke/.pyenv/versions/3.8.13/lib/python3.8/site-packages (from botocore<1.30.0,>=1.29.87->boto3>=1.26.87->consolo) (2.8.2)
Requirement already satisfied: typing-extensions>=4.2.0 in /home/ahonnecke/.pyenv/versions/3.8.13/lib/python3.8/site-packages (from pydantic>=1.10.0->argdantic>=0.3.0->consolo) (4.4.0)
Requirement already satisfied: six>=1.5 in /home/ahonnecke/.pyenv/versions/3.8.13/lib/python3.8/site-packages (from python-dateutil<3.0.0,>=2.1->botocore<1.30.0,>=1.29.87->boto3>=1.26.87->consolo) (1.16.0)
Installing collected packages: consolo
  Attempting uninstall: consolo
    Found existing installation: consolo 0.2.3
    Uninstalling consolo-0.2.3:
      Successfully uninstalled consolo-0.2.3
Successfully installed consolo-0.2.5
ahonnecke@antonym:~/src/consolo$ consolo --help
usage: consolo [-h] --profile-name TEXT --function-name TEXT --path TEXT [--upload | --no-upload] [--download | --no-download] [--create | --no-create] [--verbose | --no-verbose]

optional arguments:
  -h, --help            show this help message and exit
  --profile-name TEXT   (required)
  --function-name TEXT  (required)
  --path TEXT           (required)
  --upload
  --no-upload
  --download
  --no-download
  --create
  --no-create
  --verbose
  --no-verbose
```

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
