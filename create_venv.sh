#!/usr/bin/env bash

virtualenv -p python3 venv

source venv/bin/activate

pip install pytest tox coverage ipdb pytest-cov

