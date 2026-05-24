# logic.py
import numpy as np
from scipy.optimize import linprog
import json

def get_feed_data():
    # بدلاً من القاموس، سنقرأ من ملفك feeds_db.json
    with open('feeds_db.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def solve_formula(target_cp, target_me):
    data = get_feed_data()
    names = list(data.keys())
    c = [data[i]["Price"] for i in names]
    
    # قيود البروتين والطاقة والمجموع (100%)
    A_eq = [
        [data[i]["CP"] for i in names],
        [data[i]["ME"] for i in names],
        [1.0 for _ in names]
    ]
    b_eq = [target_cp, target_me, 100.0]
    
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=[(0, 100) for _ in names], method='highs')
    return res, names
