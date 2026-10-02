import pandas as pd
import json

df_final = pd.read_csv(r"C:\Users\rithi\govassist-rag\Merged_Schemes.csv")

validation = {
    "total_records": len(df_final),
    "unique_schemes": df_final['slug'].nunique(),
    "duplicate_count": int(df_final.duplicated(subset=['slug']).sum()),
    "missing_names": int(df_final['scheme_name'].isna().sum()),
    "missing_descriptions": int(df_final['details'].isna().sum()),
    "missing_eligibility": int(df_final['eligibility'].isna().sum()),
}

import re
url_pattern = re.compile(r'^https?://')
urls_to_check = df_final['official_url'].dropna().tolist() + df_final['apply_url'].dropna().tolist()
validation["malformed_urls"] = sum(1 for url in urls_to_check if not url_pattern.match(str(url).strip()))
validation["missing_official_urls"] = int(df_final['official_url'].isna().sum())

with open("dataset_validation.json", "w") as f:
    json.dump(validation, f, indent=4)
