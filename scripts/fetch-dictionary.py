#!/usr/bin/env python3
"""Public-dictionary fetch entry point; install the local package first."""
import sys
from tujia_lex.cli import main

raise SystemExit(main(["fetch-dictionary", *sys.argv[1:]]))
