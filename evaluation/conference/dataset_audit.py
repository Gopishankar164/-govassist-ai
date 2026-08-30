import json
import pandas as pd
from pathlib import Path
import numpy as np

def audit_dataset(csv_path: str) -> dict:
    path = Path(csv_path)
    if not path.exists():
        return {"error": "File not found"}
        
    df = pd.read_csv(path)
    
    # Basic counts
    row_count = len(df)
    col_count = len(df.columns)
    
    # Missing values
    missing = df.isnull().sum().to_dict()
    missing_pct = (df.isnull().sum() / row_count * 100).to_dict()
    
    # Identifiers
    id_col = 'scheme_id' if 'scheme_id' in df.columns else 'scheme_name'
    if id_col in df.columns:
        unique_schemes = int(df[id_col].nunique())
        duplicate_schemes = int(row_count - unique_schemes)
    else:
        unique_schemes = row_count
        duplicate_schemes = 0
        
    # Categories / States
    categories = int(df['category'].nunique()) if 'category' in df.columns else 0
    states = int(df['state'].nunique()) if 'state' in df.columns else 0
    ministries = int(df['ministry'].nunique()) if 'ministry' in df.columns else 0
    
    # Coverages
    def coverage(col_name):
        if col_name not in df.columns: return 0.0
        return float((df[col_name].notnull().sum() / row_count) * 100)

    url_cov = coverage('official_url')
    eligibility_cov = coverage('eligibility')
    desc_cov = coverage('scheme_short_title') or coverage('description')
    
    return {
        "filename": path.name,
        "path": str(path.absolute()),
        "rows": row_count,
        "columns": col_count,
        "unique_schemes": unique_schemes,
        "duplicate_rows": duplicate_schemes,
        "fields": list(df.columns),
        "missing_values": missing,
        "missing_percentage": missing_pct,
        "categories_count": categories,
        "states_count": states,
        "ministries_count": ministries,
        "official_url_coverage": url_cov,
        "eligibility_coverage": eligibility_cov,
        "description_coverage": desc_cov
    }

def main():
    root = Path(__file__).resolve().parent.parent.parent
    old_ds = root / "Schemes.csv"
    new_ds = root / "Merged_Schemes.csv"
    
    audit_old = audit_dataset(str(old_ds))
    audit_new = audit_dataset(str(new_ds))
    
    output = {
        "old_dataset": audit_old,
        "new_dataset": audit_new
    }
    
    out_dir = root / "evaluation" / "conference" / "metrics"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "dataset_audit.json", "w", encoding='utf-8') as f:
        json.dump(output, f, indent=4)
        
    # Write MD report
    report_dir = root / "evaluation" / "conference" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "dataset_audit.md"
    with open(report_path, "w", encoding='utf-8') as f:
        f.write("# Dataset Audit Report\n\n")
        f.write("## Old Dataset (data/Schemes.csv)\n")
        f.write(f"- Rows: {audit_old.get('rows')}\n")
        f.write(f"- Unique Schemes: {audit_old.get('unique_schemes')}\n")
        f.write(f"- Missing URL %: {audit_old.get('missing_percentage', {}).get('official_url', 100):.2f}%\n")
        f.write(f"- Eligibility Coverage: {audit_old.get('eligibility_coverage', 0):.2f}%\n\n")
        
        f.write("## New Dataset (Merged_Schemes.csv)\n")
        f.write(f"- Rows: {audit_new.get('rows')}\n")
        f.write(f"- Unique Schemes: {audit_new.get('unique_schemes')}\n")
        f.write(f"- Missing URL %: {audit_new.get('missing_percentage', {}).get('official_url', 100):.2f}%\n")
        f.write(f"- Eligibility Coverage: {audit_new.get('eligibility_coverage', 0):.2f}%\n")

if __name__ == "__main__":
    main()
