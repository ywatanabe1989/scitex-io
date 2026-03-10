#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-15 23:21:31 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_modules/_sqlite3.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# SQLite3 class inline - simple wrapper
import sqlite3
class SQLite3:
    """Simple SQLite3 wrapper."""
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
    def __enter__(self):
        return self.conn
    def __exit__(self, *args):
        self.conn.close()

_load_db_sqlite3 = SQLite3

# EOF
