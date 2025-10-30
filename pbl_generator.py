# pbl_generator.py
import pandas as pd
import re

def infer_length_rules(series):
    s = series.dropna().astype(str)
    if s.empty:
        return None
    lengths = s.map(len)
    min_l = int(lengths.min())
    max_l = int(lengths.max())
    typical = int(lengths.mode().iloc[0]) if not lengths.mode().empty else None
    return {'min':min_l, 'max':max_l, 'typical':typical}

def is_numeric_only(series, threshold=0.98):
    s = series.dropna().astype(str)
    if s.empty: return False
    frac = (s.str.fullmatch(r'\d+')).mean()
    return frac >= threshold

def is_alpha_only(series, threshold=0.98):
    s = series.dropna().astype(str)
    if s.empty: return False
    frac = (s.str.fullmatch(r'[A-Za-z ]+')).mean()
    return frac >= threshold

def generate_pbl_for_column(series, col_name=None):
    rules = []
    null_allowed = series.isna().sum() > 0
    if not null_allowed:
        rules.append("Nulls are NOT allowed.")
    else:
        rules.append("Nulls are allowed.")

    if is_numeric_only(series):
        rules.append("Only numeric characters allowed.")
        lengths = infer_length_rules(series)
        if lengths:
            rules.append(f"Character length between {lengths['min']} and {lengths['max']}.")
        rules.append("No special characters or alphabets allowed.")
    elif is_alpha_only(series):
        rules.append("Alphabetic characters allowed only.")
    else:
        s = series.dropna().astype(str)
        sample = s.head(50).tolist()
        if any(re.search(r'@', v) for v in sample):
            rules.append("Email format expected (contains '@').")
        if any(re.fullmatch(r'\+?\d[\d\-\s]{6,}', v) for v in sample):
            rules.append("Phone number like pattern detected.")
        lengths = infer_length_rules(series)
        if lengths:
            rules.append(f"Recommended character length between {lengths['min']} and {lengths['max']}.")
        rules.append("Avoid special characters unless required (/, -, : etc).")

    if series.nunique(dropna=True) == len(series.dropna()):
        rules.append("Values are unique — consider as candidate key.")
    else:
        distinct_ratio = series.nunique(dropna=True) / max(1, len(series))
        if distinct_ratio < 0.02:
            rules.append("Low cardinality — likely categorical; map to lookup table or enumerations.")

    return rules
