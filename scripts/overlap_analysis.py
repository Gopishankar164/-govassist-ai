import pandas as pd
import json

df_old = pd.read_csv(r"C:\Users\rithi\govassist-rag\Schemes.csv")
df_new = pd.read_csv(r"C:\Users\rithi\govassist-rag\indian_government_schemes.csv")

# Clean slugs for comparison
df_old['slug_clean'] = df_old['slug'].str.lower().str.strip()
df_new['slug_clean'] = df_new['slug'].str.lower().str.strip()

old_slugs = set(df_old['slug_clean'].dropna())
new_slugs = set(df_new['slug_clean'].dropna())

overlap = old_slugs.intersection(new_slugs)
new_unique = new_slugs - old_slugs
old_unique = old_slugs - new_slugs

report = {
    "total_old_schemes": len(df_old),
    "unique_old_slugs": len(old_slugs),
    "total_new_schemes": len(df_new),
    "unique_new_slugs": len(new_slugs),
    "overlap_count": len(overlap),
    "genuinely_new_schemes": len(new_unique),
    "schemes_only_in_old": len(old_unique),
}

with open("overlap_results.json", "w") as f:
    json.dump(report, f, indent=4)
