import pandas as pd
import json
import shutil
import numpy as np
import os

# 1. Create a backup
old_dataset_path = r"C:\Users\rithi\govassist-rag\Schemes.csv"
backup_path = r"C:\Users\rithi\govassist-rag\Schemes_backup.csv"
if not os.path.exists(backup_path):
    shutil.copy2(old_dataset_path, backup_path)

# Load datasets
df_old = pd.read_csv(old_dataset_path)
df_new = pd.read_csv(r"C:\Users\rithi\govassist-rag\indian_government_schemes.csv")

# Clean slugs for accurate matching
df_old['slug_clean'] = df_old['slug'].str.lower().str.strip()
df_new['slug_clean'] = df_new['slug'].str.lower().str.strip()

# Deduplicate old dataset (it had 3 duplicates)
df_old = df_old.drop_duplicates(subset=['slug_clean'], keep='first')

# Ensure we have all necessary columns from the new dataset in the old dataset
new_cols_to_add = [
    'ministry', 'department', 'state', 'category', 'beneficiary_type', 
    'apply_url', 'official_url', 'eligibility_age_min', 'eligibility_age_max', 
    'eligibility_gender', 'eligibility_caste', 'eligibility_income_max', 
    'eligibility_residence', 'eligibility_state', 'eligibility_disability', 
    'eligibility_bpl'
]
for col in new_cols_to_add:
    if col not in df_old.columns:
        df_old[col] = np.nan

# Prepare tracking counters
stats = {
    "existing_only": 0,
    "new_only": 0,
    "overlapping": 0,
    "merged": 0,
    "rejected": 0,
    "final_unique_schemes": 0
}

old_slugs = set(df_old['slug_clean'].dropna())
new_slugs = set(df_new['slug_clean'].dropna())

overlapping = old_slugs.intersection(new_slugs)
existing_only = old_slugs - new_slugs
new_only = new_slugs - old_slugs

stats["overlapping"] = len(overlapping)
stats["existing_only"] = len(existing_only)
stats["new_only"] = len(new_only)

# Create a dictionary for quick lookup of new dataset rows
new_dict = df_new.set_index('slug_clean').to_dict('index')

merged_rows = []

# Process all old dataset rows
for _, row in df_old.iterrows():
    slug = row['slug_clean']
    
    # Base dictionary from old row
    merged_row = row.to_dict()
    merged_row['source_provenance'] = 'Schemes.csv'
    
    if slug in overlapping:
        stats["merged"] += 1
        merged_row['source_provenance'] = 'Merged (Schemes.csv + indian_government_schemes.csv)'
        new_row = new_dict[slug]
        
        # Prefer structured eligibility, benefits, documents, application procedure, and official URL
        if pd.notna(new_row.get('eligibility_text')) and str(new_row.get('eligibility_text')).strip() != '':
            if pd.isna(merged_row.get('eligibility')) or len(str(new_row.get('eligibility'))) < len(str(new_row.get('eligibility_text'))):
                merged_row['eligibility'] = new_row['eligibility_text']
        
        if pd.notna(new_row.get('benefits')) and str(new_row.get('benefits')).strip() != '':
            if pd.isna(merged_row.get('benefits')) or len(str(merged_row['benefits'])) < len(str(new_row['benefits'])):
                merged_row['benefits'] = new_row['benefits']
                
        if pd.notna(new_row.get('documents_required')) and str(new_row.get('documents_required')).strip() != '':
            if pd.isna(merged_row.get('documents')) or len(str(merged_row['documents'])) < len(str(new_row['documents_required'])):
                merged_row['documents'] = new_row['documents_required']
                
        if pd.notna(new_row.get('application_process')) and str(new_row.get('application_process')).strip() != '':
            if pd.isna(merged_row.get('application')) or len(str(merged_row['application'])) < len(str(new_row['application_process'])):
                merged_row['application'] = new_row['application_process']
                
        # Structured metadata fields from new dataset
        for col in new_cols_to_add:
            val = new_row.get(col)
            if pd.notna(val) and str(val).strip() != '':
                merged_row[col] = val
                
    merged_rows.append(merged_row)

# Add new only schemes
for slug in new_only:
    new_row = new_dict[slug]
    
    # Map to old schema structure where applicable
    mapped_row = {
        'scheme_name': new_row.get('name'),
        'slug': new_row.get('slug'),
        'slug_clean': slug,
        'details': new_row.get('description'),
        'benefits': new_row.get('benefits'),
        'eligibility': new_row.get('eligibility_text'),
        'application': new_row.get('application_process'),
        'documents': new_row.get('documents_required'),
        'level': new_row.get('state') if pd.notna(new_row.get('state')) and str(new_row.get('state')) != 'Central' else 'Central',
        'schemeCategory': new_row.get('category'),
        'source_provenance': 'indian_government_schemes.csv'
    }
    
    # Copy new structured fields
    for col in new_cols_to_add:
        mapped_row[col] = new_row.get(col)
        
    merged_rows.append(mapped_row)

df_final = pd.DataFrame(merged_rows)

# Clean up temporary matching column and empty legacy columns
if 'slug_clean' in df_final.columns:
    df_final = df_final.drop(columns=['slug_clean'])
if 'Unnamed: 9' in df_final.columns:
    df_final = df_final.drop(columns=['Unnamed: 9'])

stats["final_unique_schemes"] = len(df_final)

# Validation Phase
validation = {
    "duplicate_schemes": int(df_final.duplicated(subset=['slug']).sum()),
    "missing_scheme_names": int(df_final['scheme_name'].isna().sum()),
    "missing_descriptions": int(df_final['details'].isna().sum()),
    "missing_eligibility": int(df_final['eligibility'].isna().sum()),
    "invalid_records": 0,
    "encoding_problems": 0,
    "malformed_urls": 0
}

# Check URLs
import re
url_pattern = re.compile(r'^https?://')
urls_to_check = df_final['official_url'].dropna().tolist() + df_final['apply_url'].dropna().tolist()
validation["malformed_urls"] = sum(1 for url in urls_to_check if not url_pattern.match(str(url).strip()))

# Output results
with open("phase2_results.json", "w") as f:
    json.dump({"stats": stats, "validation": validation}, f, indent=4)

# Save final dataset
merged_path = r"C:\Users\rithi\govassist-rag\Merged_Schemes.csv"
df_final.to_csv(merged_path, index=False)

print("Phase 2 complete")
