#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MVPT-4 — Backend Flask
Portage de mvpt4.pyw vers une application web.
"""

import os
import sqlite3
import json
import datetime
import secrets
from flask import (Flask, render_template, request, jsonify,
                   redirect, url_for, send_file, abort)
import io

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "mvpt4.db"))

# ══════════════════════════════════════
#  DONNÉES NORMATIVES (identiques au .pyw)
# ══════════════════════════════════════

CORRECT_ANSWERS = {
    1:'A', 2:'C', 3:'C', 4:'C', 5:'C', 6:'C', 7:'D', 8:'C', 9:'B',
    10:'B', 11:'D', 12:'B', 13:'D', 14:'B', 15:'C', 16:'A', 17:'C', 18:'D',
    19:'B', 20:'D', 21:'A', 22:'A', 23:'D', 24:'B', 25:'D', 26:'B', 27:'D',
    28:'B', 29:'C', 30:'A', 31:'C', 32:'A', 33:'D', 34:'B', 35:'A', 36:'D',
    37:'C', 38:'D', 39:'C', 40:'D', 41:'A', 42:'C', 43:'A', 44:'B', 45:'C'
}

SECTIONS = {
    'disc': ('Discrimination visuelle', list(range(1, 10))),
    'fig':  ('Figure-fond',             list(range(10, 19))),
    'mem':  ('Mémoire visuelle',        list(range(19, 28))),
    'spat': ('Relations spatiales',     list(range(28, 37))),
    'clos': ('Closure visuelle',        list(range(37, 46))),
}

AGE_COLS = [
    ('4,0 - 4,2', 4.0, 4.3), ('4,3 - 4,5', 4.3, 4.6), ('4,6 - 4,8', 4.6, 4.9),
    ('4,9 - 4,11', 4.9, 5.0), ('5,0 - 5,2', 5.0, 5.3), ('5,3 - 5,5', 5.3, 5.6),
    ('5,6 - 5,8', 5.6, 5.9), ('5,9 - 5,11', 5.9, 6.0), ('6,0 - 6,2', 6.0, 6.3),
    ('6,3 - 6,5', 6.3, 6.6), ('6,6 - 6,8', 6.6, 6.9), ('6,9 - 6,11', 6.9, 7.0),
    ('7,0 - 7,2', 7.0, 7.3), ('7,3 - 7,5', 7.3, 7.6), ('7,6 - 7,8', 7.6, 7.9),
    ('7,9 - 7,11', 7.9, 8.0), ('8,0 - 8,2', 8.0, 8.3), ('8,3 - 8,5', 8.3, 8.6),
    ('8,6 - 8,8', 8.6, 8.9), ('8,9 - 8,11', 8.9, 9.0), ('9,0 -9,2', 9.0, 9.3),
    ('9,3 - 9,5', 9.3, 9.6), ('9,6 - 9,8', 9.6, 9.9), ('9,9 - 9,11', 9.9, 10.0),
    ('10,0 - 10,5', 10.0, 10.6), ('10,6 - 10,11', 10.6, 11.0),
    ('11,0 - 11,5', 11.0, 11.6), ('11,6 - 11,11', 11.6, 12.0),
    ('12,0 - 12,5', 12.0, 12.6), ('12,6 - 12,11', 12.6, 13.0),
    ('13,0 - 13,5', 13.0, 13.6), ('13,6 - 13,11', 13.6, 14.0),
    ('14,0 - 14,5', 14.0, 14.6), ('14,6 - 14,11', 14.6, 15.0),
    ('15,0 - 15,11', 15.0, 16.0), ('16,0 - 16,11', 16.0, 17.0),
    ('17,0 - 17,11', 17.0, 18.0), ('18,0 - 18,11', 18.0, 19.0),
    ('19,0 - 19,11', 19.0, 20.0), ('20,0 - 29,11', 20.0, 30.0),
    ('30,0 - 39,11', 30.0, 40.0), ('40,0 - 49,11', 40.0, 50.0),
    ('50,0- 59,11', 50.0, 60.0), ('60,0 - 64,11', 60.0, 65.0),
    ('65,0 - 69,11', 65.0, 70.0), ('70,0- 74,11', 70.0, 75.0),
    ('75,0 - 79,11', 75.0, 80.0), ('80,0 - 84,11', 80.0, 85.0),
    ('85,0 +', 85.0, 999.0),
]

NORM_TABLE = [
    [58,55,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
    [61,59,56,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
    [64,62,59,57,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
    [68,65,63,60,57,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
    [71,68,66,63,60,57,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
    [75,72,69,66,63,60,57,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
    [78,75,72,69,66,63,60,57,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
    [82,78,75,72,69,66,62,59,57,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
    [85,82,78,75,72,68,65,62,60,57,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
    [89,85,82,78,75,71,68,65,63,61,59,56,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,56],
    [92,88,85,81,78,74,71,69,66,64,62,60,57,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,57,58,60],
    [94,91,87,84,80,77,74,72,70,68,66,63,61,58,56,56,55,55,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,57,61,62,63],
    [96,93,90,86,83,80,77,75,73,71,69,67,65,63,61,60,59,58,57,57,57,56,56,56,56,56,56,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,56,60,65,65,66],
    [98,95,92,89,86,83,80,78,76,74,72,71,69,67,65,64,62,61,59,59,59,59,58,58,58,58,58,57,56,55,None,None,None,None,None,None,None,None,None,None,None,None,None,55,59,64,68,69,69],
    [99,97,94,91,88,86,83,81,79,77,75,74,72,71,69,68,66,65,63,63,62,62,61,61,60,60,59,59,58,58,57,56,None,None,None,None,None,None,None,None,None,None,None,58,62,67,72,72,72],
    [101,98,96,93,91,88,86,84,82,80,78,77,75,74,73,71,70,68,67,66,66,65,64,64,62,62,62,61,60,60,59,58,57,56,None,None,None,None,None,None,None,None,56,60,65,69,74,74,74],
    [102,100,98,95,93,91,88,86,84,82,80,79,78,77,75,74,73,72,70,70,69,68,67,66,65,64,64,63,62,62,61,60,59,58,57,None,None,None,None,None,None,None,58,63,67,72,76,76,76],
    [104,102,100,97,95,93,91,89,87,85,83,82,80,79,78,77,76,75,73,72,71,71,70,69,67,66,66,65,65,64,63,62,61,60,59,57,56,56,55,None,None,55,60,65,70,74,77,78,78],
    [106,104,102,100,97,95,93,91,89,87,85,84,83,81,80,79,78,77,76,75,74,73,72,72,70,69,68,67,67,66,65,64,63,62,61,59,57,57,57,56,56,56,61,66,71,75,78,80,80],
    [107,105,103,101,100,98,96,94,92,90,88,87,85,84,82,81,80,79,78,77,77,76,75,74,72,71,70,70,69,68,67,66,65,64,63,60,59,59,59,58,58,58,63,68,73,76,79,81,82],
    [108,107,105,103,102,100,98,96,94,92,91,89,88,86,84,83,82,81,80,80,79,78,77,77,75,74,73,72,71,70,69,68,67,66,65,62,61,61,61,60,59,59,64,69,74,77,80,82,84],
    [110,108,107,105,104,102,100,99,97,95,93,92,90,89,87,86,85,84,83,82,81,81,80,79,78,76,75,74,74,73,72,71,70,68,67,64,63,63,63,62,61,61,66,71,76,78,81,84,86],
    [111,110,108,107,106,104,103,101,99,97,96,94,93,91,90,88,87,86,85,84,84,83,82,82,80,79,78,77,76,75,74,73,72,70,69,66,65,65,65,64,63,63,68,73,77,79,82,85,88],
    [112,111,110,109,108,106,105,103,102,100,98,97,95,94,92,91,90,89,88,87,86,86,85,85,83,82,81,79,78,77,76,75,74,73,71,69,67,67,67,66,65,65,69,74,78,80,83,86,90],
    [114,113,112,111,110,109,108,106,104,103,101,99,98,96,95,94,93,91,90,90,89,88,88,87,86,84,83,82,81,79,78,77,76,75,73,71,69,69,69,68,67,67,71,75,79,81,84,88,92],
    [115,114,113,113,112,111,110,108,107,105,104,102,101,99,98,96,95,94,93,92,92,91,90,90,88,87,86,84,83,82,81,79,78,77,76,73,72,71,71,70,69,69,73,76,80,83,85,90,94],
    [117,116,115,115,114,113,112,111,109,108,106,105,103,102,100,99,98,97,96,95,94,94,93,92,91,89,88,87,85,84,83,82,81,79,78,75,74,74,74,72,71,71,75,78,81,84,87,92,96],
    [118,118,117,117,116,115,115,113,112,111,109,108,106,105,103,102,101,100,99,98,97,96,95,95,93,92,90,89,88,87,85,84,83,82,80,78,76,76,76,74,73,73,77,80,83,86,89,94,98],
    [120,119,119,118,118,117,117,116,114,113,112,111,109,108,106,105,104,103,102,101,100,99,98,97,95,94,93,91,90,89,88,86,85,84,83,80,79,79,78,77,76,76,79,82,84,88,91,96,100],
    [122,121,121,120,120,119,119,118,117,116,115,114,112,111,109,108,107,106,104,104,103,102,101,100,98,96,95,94,92,91,90,89,87,86,85,83,82,81,81,79,78,78,81,84,86,90,93,98,102],
    [124,123,123,122,122,121,121,120,119,118,117,116,115,114,112,111,110,109,107,106,105,104,103,102,100,99,97,96,95,94,92,91,90,89,88,85,84,84,83,82,80,81,84,86,88,92,96,100,104],
    [126,126,125,124,124,123,123,122,121,120,120,119,118,117,116,114,113,112,110,109,108,107,106,105,102,101,100,99,97,96,95,94,92,91,90,88,86,86,86,84,83,83,86,88,91,94,98,102,106],
    [129,128,128,127,126,126,125,124,123,123,122,121,120,119,118,117,116,115,113,112,111,110,108,108,105,104,102,101,100,99,97,96,95,94,92,90,88,88,88,86,85,86,88,91,93,97,100,104,108],
    [133,132,131,130,129,129,128,127,126,125,124,123,122,122,121,120,118,117,116,115,114,113,111,110,107,106,105,104,102,101,100,99,97,96,95,92,90,90,90,88,87,88,91,93,95,99,103,107,110],
    [136,136,135,134,133,132,131,130,129,128,127,126,125,124,123,122,121,120,119,118,117,115,114,113,110,109,107,106,105,104,103,101,100,98,97,94,92,92,92,91,90,90,93,95,98,101,105,109,113],
    [141,140,139,138,137,136,136,134,133,132,131,130,129,128,126,125,124,123,122,121,119,118,117,116,113,111,110,109,107,106,105,104,103,101,99,96,95,94,94,93,92,93,95,98,100,104,107,111,115],
    [146,144,143,143,142,141,140,139,138,137,136,135,133,132,131,129,128,126,125,124,122,121,120,119,116,114,113,111,110,109,108,106,105,104,102,99,97,97,97,95,94,95,98,100,103,106,110,114,118],
    [146,146,146,146,146,146,145,144,143,142,141,140,138,137,136,134,133,131,130,128,126,125,124,122,118,117,116,114,113,112,110,109,108,106,105,102,100,100,99,98,97,98,100,103,106,109,113,116,120],
    [146,146,146,146,146,146,146,146,146,146,146,145,143,142,141,139,138,136,135,133,131,130,129,127,123,120,119,118,116,115,113,112,111,109,108,105,103,103,102,101,100,100,103,106,108,112,116,119,122],
    [146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,144,143,141,140,138,136,135,134,132,128,125,123,121,120,118,117,116,114,113,111,108,107,106,105,104,103,103,106,109,112,115,119,122,125],
    [146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,145,143,141,140,139,137,132,130,128,126,124,122,121,120,118,117,115,112,111,110,109,107,105,106,109,112,115,118,121,125,129],
    [146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,145,144,142,137,135,132,131,129,127,126,125,123,121,119,116,115,114,113,111,110,111,113,116,119,122,125,130,134],
    [146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,141,140,137,136,134,132,131,130,128,126,124,121,119,118,118,116,115,116,118,120,123,126,130,135,139],
    [146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,145,142,141,139,137,136,135,132,131,129,126,124,123,122,121,120,121,123,125,128,131,135,140,143],
    [146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,144,142,141,140,137,136,134,131,129,128,127,126,125,126,128,130,133,136,140,145,146],
    [146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,146,145,142,141,139,136,134,133,132,131,130,131,133,135,138,141,144,146,None],
]

PCT_TABLE = {}
_pct_raw = [
    ('<55','<1',1,'<20',1,1),(56,'<1',1,20,1,1),(57,'<1',1,21,1,1),(58,'<1',1,21,2,1),
    (59,'<1',1,22,2,1),(60,'<1',1,23,2,1),(61,'<1',1,23,2,1),(62,1,1,24,2,1),
    (63,1,1,25,3,1),(64,1,1,26,3,1),(65,1,1,27,3,1),(66,1,2,27,3,1),(67,1,4,28,3,1),
    (68,2,5,29,4,1),(69,2,6,29,4,1),(70,2,8,30,4,1),(71,3,9,31,4,1),(72,3,11,31,4,1),
    (73,4,12,32,5,2),(74,4,13,33,5,2),(75,5,15,33,5,2),(76,5,16,34,5,2),(77,6,18,35,5,2),
    (78,7,19,35,6,2),(79,8,21,36,6,2),(80,9,22,37,6,2),(81,10,23,37,6,2),(82,11,25,38,6,3),
    (83,13,26,39,7,3),(84,14,28,39,7,3),(85,16,29,40,7,3),(86,18,30,41,7,3),(87,19,32,41,7,3),
    (88,21,33,42,8,3),(89,23,35,43,8,4),(90,25,36,43,8,4),(91,27,37,44,8,4),(92,30,39,45,8,4),
    (93,32,40,45,9,4),(94,34,42,46,9,4),(95,37,43,47,9,4),(96,39,44,47,9,5),(97,42,46,48,9,5),
    (98,45,47,49,10,5),(99,47,49,49,10,5),(100,50,50,50,10,5),(101,53,51,51,10,5),(102,55,53,51,10,5),
    (103,58,54,52,11,5),(104,61,56,53,11,6),(105,63,57,53,11,6),(106,66,58,54,11,6),(107,68,60,55,11,6),
    (108,70,61,55,12,6),(109,73,63,56,12,6),(110,75,64,57,12,6),(111,77,65,57,12,6),(112,79,67,58,12,7),
    (113,81,68,59,13,7),(114,83,70,59,13,7),(115,84,71,60,13,7),(116,86,72,61,13,7),(117,87,74,61,13,7),
    (118,88,75,62,14,8),(119,90,77,63,14,8),(120,91,78,63,14,8),(121,92,79,64,14,8),(122,93,81,65,14,8),
    (123,94,82,65,15,8),(124,95,84,66,15,8),(125,95,85,67,15,8),(126,96,87,67,15,9),(127,96,88,68,15,9),
    (128,97,89,69,16,9),(129,97,91,69,16,9),(130,98,92,70,16,9),(131,98,94,71,16,9),(132,98,95,71,16,9),
    (133,99,96,72,17,9),(134,99,98,73,17,9),(135,99,99,73,17,9),(136,99,99,74,17,9),(137,99,99,75,17,9),
    (138,99,99,75,18,9),(139,'>99',99,76,18,9),(140,'>99',99,77,18,9),(141,'>99',99,77,18,9),
    (142,'>99',99,78,18,9),(143,'>99',99,79,19,9),(144,'>99',99,79,19,9),(145,'>99',99,80,19,9),
    ('>145','>99',99,'>80',19,9),
]
for row in _pct_raw:
    PCT_TABLE[row[0]] = {'pct': row[1], 'nce': row[2], 'tscore': row[3], 'scaled': row[4], 'stanine': row[5]}

AGE_EQUIV = {
    0:'>3-0',12:'3-1',13:'3-4',14:'3-8',15:'4-2',16:'4-4',17:'4-6',18:'4-10',
    19:'5-1',20:'5-4',21:'5-7',22:'5-10',23:'6-4',24:'6-7',25:'7-2',26:'7-7',
    27:'8-4',28:'9-1',29:'9-10',30:'10-5',31:'11-5',32:'12-5',33:'13-5',34:'14-5',
    35:'14-11',36:'15-11',37:'17-0',38:'>18-0'
}

# ══════════════════════════════════════
#  LOGIQUE MÉTIER
# ══════════════════════════════════════

def get_age_col_index(age_decimal):
    for i, (_, mn, mx) in enumerate(AGE_COLS):
        if mn <= age_decimal < mx:
            return i
    return len(AGE_COLS) - 1

def get_standard_score(raw, col_idx):
    if raw < 0 or raw > 45:
        return None
    row = NORM_TABLE[raw]
    if col_idx >= len(row) or row[col_idx] is None:
        return 54
    return min(row[col_idx], 146)

def get_age_equiv(raw):
    if raw in AGE_EQUIV:
        return AGE_EQUIV[raw]
    if raw > 38:
        return '>18-0'
    if 0 < raw < 12:
        return '>3-0'
    keys = sorted(AGE_EQUIV.keys())
    for i in range(len(keys) - 1):
        if keys[i] < raw < keys[i+1]:
            return AGE_EQUIV[keys[i]]
    return '>3-0'

def parse_age_equiv(ae_str):
    s = str(ae_str).strip()
    prefix = s[0] if s and s[0] in '><' else ''
    s_clean = s.lstrip('><')
    parts = s_clean.split('-')
    try:
        y, m = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
        dec = y + m / 12
        est_plafond  = (prefix == '>' and dec >= 10)
        est_plancher = (prefix == '>' and dec < 10)
        return dec, est_plafond, est_plancher
    except:
        return None, False, False

def get_interpretation(ss, age_decimal=None, age_equiv_str=None):
    if age_decimal is not None and age_equiv_str is not None:
        ae_dec, ae_plafond, ae_plancher = parse_age_equiv(age_equiv_str)
        if ae_dec is not None:
            diff_months = (ae_dec - age_decimal) * 12
            age_y = int(age_decimal)
            age_m = round((age_decimal % 1) * 12)
            ae_y  = int(ae_dec)
            ae_m  = round((ae_dec % 1) * 12)
            age_str   = f"{age_y} ans {age_m} mois"
            ae_str_hr = f"{ae_y} ans {ae_m} mois"
            if ae_plafond:
                return ('Très supérieur', 'green',
                        f"L'âge équivalent dépasse le plafond de la table (>{ae_str_hr}) pour un âge réel de {age_str}. Performances nettement supérieures à la moyenne.")
            if ae_plancher:
                return ('Déficit très significatif', 'red',
                        f"L'âge équivalent est inférieur au plancher de la table (<{ae_str_hr}) pour un âge réel de {age_str}. Performances très en dessous de la moyenne.")
            if diff_months >= 24:
                return ('Très supérieur', 'green',
                        f"Âge équivalent : {ae_str_hr} pour un âge réel de {age_str}. Avance de {round(diff_months)} mois — performances nettement supérieures à la moyenne.")
            if diff_months >= 12:
                return ('Supérieur à la moyenne', 'green',
                        f"Âge équivalent : {ae_str_hr} pour un âge réel de {age_str}. Avance de {round(diff_months)} mois — performances au-dessus de la moyenne.")
            if diff_months >= -6:
                return ('Dans la moyenne', 'green',
                        f"Âge équivalent : {ae_str_hr} pour un âge réel de {age_str}. Performances conformes à la norme attendue ({'avance' if diff_months >= 0 else 'retard'} de {abs(round(diff_months))} mois).")
            if diff_months >= -12:
                return ('Moyenne basse', 'orange',
                        f"Âge équivalent : {ae_str_hr} pour un âge réel de {age_str}. Retard de {abs(round(diff_months))} mois — légèrement en dessous de la norme.")
            if diff_months >= -24:
                return ('Déficit modéré', 'orange',
                        f"Âge équivalent : {ae_str_hr} pour un âge réel de {age_str}. Retard de {abs(round(diff_months))} mois — performances en dessous de la moyenne.")
            if diff_months >= -36:
                return ('Déficit significatif', 'red',
                        f"Âge équivalent : {ae_str_hr} pour un âge réel de {age_str}. Retard de {abs(round(diff_months))} mois — performances nettement en dessous de la moyenne.")
            return ('Déficit très significatif', 'red',
                    f"Âge équivalent : {ae_str_hr} pour un âge réel de {age_str}. Retard de {abs(round(diff_months))} mois — performances très en dessous de la moyenne.")
    if ss <= 54: return ('Déficit très significatif', 'red', 'Performances très en dessous de la moyenne.')
    if ss < 70:  return ('Déficit significatif',      'red', 'Performances nettement en dessous de la moyenne.')
    if ss < 80:  return ('Déficit modéré',            'orange', 'Performances en dessous de la moyenne.')
    if ss < 90:  return ('Moyenne basse',             'orange', 'Légèrement en dessous de la norme.')
    if ss <= 110: return ('Dans la moyenne',          'green', 'Performances attendues pour cet âge.')
    if ss <= 120: return ('Supérieur à la moyenne',   'green', 'Performances au-dessus de la moyenne.')
    return            ('Très supérieur',              'green', 'Performances nettement supérieures à la moyenne.')

def parse_date(s):
    s = (s or '').strip()
    for fmt in ('%d/%m/%Y', '%Y-%m-%d'):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None

def calculate_age(dob_str, test_str):
    dob  = parse_date(dob_str)
    test = parse_date(test_str)
    if not dob or not test:
        return None
    y = test.year - dob.year
    m = test.month - dob.month
    if m < 0:
        y -= 1; m += 12
    return y, m, y + m / 12

def calculate_scores(answers, age_decimal):
    total_raw = 0
    sub_scores = {}
    for key, (label, items) in SECTIONS.items():
        s = sum(1 for n in items if answers.get(str(n)) == CORRECT_ANSWERS[n])
        sub_scores[key] = s
        total_raw += s

    col_idx = get_age_col_index(age_decimal)
    ss = get_standard_score(total_raw, col_idx)

    if ss <= 54:   pct_key = '<55'
    elif ss >= 146: pct_key = '>145'
    else:           pct_key = ss
    pct_data = PCT_TABLE.get(pct_key, PCT_TABLE.get('<55'))

    age_eq = get_age_equiv(total_raw)
    interp_label, interp_color, interp_text = get_interpretation(
        ss, age_decimal=age_decimal, age_equiv_str=age_eq)

    ss_display = '<55' if ss <= 54 else ('>145' if ss >= 146 else str(ss))

    return {
        'raw': total_raw,
        'standard_score': ss,
        'standard_score_display': ss_display,
        'age_col': AGE_COLS[col_idx][0],
        'percentile': pct_data['pct'],
        'nce': pct_data['nce'],
        'tscore': pct_data['tscore'],
        'scaled': pct_data['scaled'],
        'stanine': pct_data['stanine'],
        'age_equiv': age_eq,
        'interpretation_label': interp_label,
        'interpretation_color': interp_color,
        'interpretation_text': interp_text,
        'sub_scores': sub_scores,
    }

# ══════════════════════════════════════
#  BASE DE DONNÉES SQLITE
# ══════════════════════════════════════

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id          TEXT PRIMARY KEY,
                saved_at    TEXT NOT NULL,
                patient_name TEXT,
                dob         TEXT,
                testdate    TEXT,
                examiner    TEXT,
                notes       TEXT,
                answers     TEXT,
                raw_score   INTEGER,
                standard_score INTEGER
            )
        """)

def session_to_dict(row):
    d = dict(row)
    if d.get('answers'):
        d['answers'] = json.loads(d['answers'])
    return d

# ══════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html',
                           sections=SECTIONS,
                           correct_answers=CORRECT_ANSWERS)

@app.route('/api/sessions', methods=['GET'])
def api_sessions():
    q      = request.args.get('q', '').lower()
    status = request.args.get('status', 'all')
    sort   = request.args.get('sort', 'date_desc')

    with get_db() as conn:
        rows = conn.execute("SELECT * FROM sessions").fetchall()

    sessions = [session_to_dict(r) for r in rows]

    if q:
        sessions = [s for s in sessions if
                    q in (s.get('patient_name') or '').lower() or
                    q in (s.get('dob') or '') or
                    q in (s.get('testdate') or '') or
                    q in (s.get('examiner') or '').lower()]

    if status == 'complete':
        sessions = [s for s in sessions if
                    sum(1 for v in (s.get('answers') or {}).values() if v != '—') >= 45]
    elif status == 'partial':
        sessions = [s for s in sessions if
                    sum(1 for v in (s.get('answers') or {}).values() if v != '—') < 45]

    sort_map = {
        'date_desc': lambda s: s.get('saved_at', ''),
        'date_asc':  lambda s: s.get('saved_at', ''),
        'name_asc':  lambda s: (s.get('patient_name') or '').lower(),
        'name_desc': lambda s: (s.get('patient_name') or '').lower(),
        'score_desc':lambda s: (s.get('standard_score') or 0),
        'score_asc': lambda s: (s.get('standard_score') or 0),
    }
    rev = sort.endswith('_desc')
    sessions.sort(key=sort_map.get(sort, sort_map['date_desc']), reverse=rev)

    return jsonify(sessions)

@app.route('/api/sessions/<sid>', methods=['GET'])
def api_session_get(sid):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone()
    if not row:
        abort(404)
    return jsonify(session_to_dict(row))

@app.route('/api/sessions', methods=['POST'])
def api_session_save():
    data = request.json
    sid = data.get('id') or str(int(datetime.datetime.now().timestamp() * 1000))
    now = datetime.datetime.now().isoformat()
    answers_json = json.dumps(data.get('answers', {}))

    with get_db() as conn:
        existing = conn.execute("SELECT id FROM sessions WHERE id = ?", (sid,)).fetchone()
        if existing:
            conn.execute("""
                UPDATE sessions SET saved_at=?, patient_name=?, dob=?, testdate=?,
                examiner=?, notes=?, answers=?, raw_score=?, standard_score=?
                WHERE id=?
            """, (now, data.get('patient_name'), data.get('dob'), data.get('testdate'),
                  data.get('examiner'), data.get('notes'), answers_json,
                  data.get('raw_score'), data.get('standard_score'), sid))
        else:
            conn.execute("""
                INSERT INTO sessions (id, saved_at, patient_name, dob, testdate,
                examiner, notes, answers, raw_score, standard_score)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (sid, now, data.get('patient_name'), data.get('dob'), data.get('testdate'),
                  data.get('examiner'), data.get('notes'), answers_json,
                  data.get('raw_score'), data.get('standard_score')))

    return jsonify({'id': sid, 'saved_at': now})

@app.route('/api/sessions/<sid>', methods=['DELETE'])
def api_session_delete(sid):
    with get_db() as conn:
        conn.execute("DELETE FROM sessions WHERE id = ?", (sid,))
    return jsonify({'deleted': sid})

@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    data    = request.json
    dob     = data.get('dob', '')
    testdate= data.get('testdate', '')
    answers = data.get('answers', {})

    age_result = calculate_age(dob, testdate)
    if not age_result:
        return jsonify({'error': 'Dates invalides'}), 400

    y, m, age_decimal = age_result
    result = calculate_scores(answers, age_decimal)
    result['age_years']  = y
    result['age_months'] = m
    result['age_decimal']= round(age_decimal, 4)
    return jsonify(result)

@app.route('/api/export')
def api_export():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM sessions ORDER BY saved_at DESC").fetchall()
    sessions = [session_to_dict(r) for r in rows]
    buf = io.BytesIO(json.dumps(sessions, ensure_ascii=False, indent=2).encode('utf-8'))
    buf.seek(0)
    filename = f"mvpt4_sessions_{datetime.date.today().isoformat()}.json"
    return send_file(buf, mimetype='application/json',
                     as_attachment=True, download_name=filename)

@app.route('/api/import', methods=['POST'])
def api_import():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier'}), 400
    f = request.files['file']
    try:
        imported = json.load(f)
        arr = imported if isinstance(imported, list) else [imported]
        added = 0
        with get_db() as conn:
            ids = {r[0] for r in conn.execute("SELECT id FROM sessions")}
            for s in arr:
                if s.get('id') not in ids:
                    conn.execute("""
                        INSERT INTO sessions (id, saved_at, patient_name, dob, testdate,
                        examiner, notes, answers, raw_score, standard_score)
                        VALUES (?,?,?,?,?,?,?,?,?,?)
                    """, (s['id'], s.get('saved_at', ''), s.get('patient_name'),
                          s.get('dob'), s.get('testdate'), s.get('examiner'),
                          s.get('notes'), json.dumps(s.get('answers', {})),
                          s.get('raw_score'), s.get('standard_score')))
                    added += 1
        return jsonify({'imported': added})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/rapport/<sid>')
def rapport(sid):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone()
    if not row:
        abort(404)
    s = session_to_dict(row)
    answers = s.get('answers', {})
    age_result = calculate_age(s.get('dob', ''), s.get('testdate', ''))
    result = None
    if age_result:
        _, _, age_decimal = age_result
        result = calculate_scores(answers, age_decimal)
    return render_template('rapport.html', session=s, result=result, sections=SECTIONS)

# ══════════════════════════════════════
#  POINT D'ENTRÉE
# ══════════════════════════════════════

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
