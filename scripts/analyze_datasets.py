import pandas as pd
import json

def analyze_dataset(path, name):
    df = pd.read_csv(path)
    report = {
        "dataset": name,
        "path": path,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_scheme_names": int(df.duplicated(subset=['scheme_name']).sum()) if 'scheme_name' in df.columns else (int(df.duplicated(subset=['Scheme Name']).sum()) if 'Scheme Name' in df.columns else None),
    }
    
    scheme_col = 'scheme_name' if 'scheme_name' in df.columns else ('Scheme Name' if 'Scheme Name' in df.columns else None)
    if scheme_col:
        report["unique_scheme_count"] = df[scheme_col].nunique()
    
    return df, report

df_old, report_old = analyze_dataset(r"C:\Users\rithi\govassist-rag\Schemes.csv", "Old Dataset")
df_new, report_new = analyze_dataset(r"C:\Users\rithi\govassist-rag\indian_government_schemes.csv", "New Dataset")

with open("audit_results.json", "w") as f:
    json.dump({"old": report_old, "new": report_new}, f, indent=4)

print("Analysis complete")
