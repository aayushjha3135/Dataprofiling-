# chat_agent.py
import pandas as pd

def simple_rule_based_answer(question: str, df: pd.DataFrame, profile: dict):
    q = question.lower()
    if ("null" in q and "count" in q) or ("how many" in q and "null" in q):
        for col in df.columns:
            if col.lower() in q:
                cnt = int(df[col].isna().sum())
                return f"Column '{col}' has {cnt} null values out of {len(df)} rows."
        null_summary = {c: int(df[c].isna().sum()) for c in df.columns}
        top = sorted(null_summary.items(), key=lambda x: x[1], reverse=True)[:5]
        return "Top null counts: " + ", ".join([f"{c}: {n}" for c, n in top])

    if "outlier" in q or "outliers" in q:
        out = []
        for c, meta in profile['columns_overview'].items():
            if isinstance(meta, dict) and meta.get('outliers') and meta['outliers'].get('count',0) > 0:
                out.append(f"{c}({meta['outliers']['count']})")
        if out:
            return "Columns with outliers: " + ", ".join(out)
        return "No numeric outliers detected by IQR method."

    if "unique" in q or "distinct" in q:
        for col in df.columns:
            if col.lower() in q:
                return f"Column '{col}' has {df[col].nunique(dropna=True)} distinct values."

    return ("I can answer queries like 'how many nulls in <column>', 'which columns have outliers', "
            "'which columns are numeric', or 'generate PBL for <column>'.\n"
            "Please be specific with column names for exact answers.")

def answer_question_about_df(question: str, df: pd.DataFrame, profile: dict):
    return simple_rule_based_answer(question, df, profile)
