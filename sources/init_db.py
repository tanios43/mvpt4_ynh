#!/usr/bin/env python3
"""Initialise la base SQLite — appelé par le script d'install YunoHost."""
import sys
import os

if len(sys.argv) < 2:
    print("Usage: init_db.py <chemin/vers/mvpt4.db>")
    sys.exit(1)

db_path = sys.argv[1]
os.environ['DB_PATH'] = db_path

# Importer app pour déclencher init_db()
sys.path.insert(0, os.path.dirname(__file__))
from app import init_db
init_db()
print(f"Base de données initialisée : {db_path}")
