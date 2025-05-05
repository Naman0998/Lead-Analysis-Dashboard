import pandas as pd

def calculate_budget_allocations(df, total_budget):
    # Normalize Converted column
    df['Converted'] = df['Converted'].astype(str).str.strip().str.upper()
    df['Converted'] = df['Converted'] == 'TRUE'

    # Filter only converted leads
    df_filtered = df[df['Converted'] == True]

    if df_filtered.empty:
        return pd.DataFrame(), 0, 0

    grouped = df_filtered.groupby('Lead Source').agg({
        'Cost': 'sum',
        'Converted Count': 'sum'
    }).reset_index()

    # Remove sources with 0 conversions to avoid division errors
    grouped = grouped[grouped['Converted Count'] > 0].copy()
    if grouped.empty:
        return pd.DataFrame(), 0, 0

    grouped['CPA'] = grouped['Cost'] / grouped['Converted Count']

    # Uniform allocation
    grouped['Uniform Allocation'] = total_budget / len(grouped)
    grouped['Uniform Predicted Conversions'] = grouped['Uniform Allocation'] / grouped['CPA']

    # Weighted allocation
    grouped['Weight'] = 1 / grouped['CPA']
    grouped['Weight Norm'] = grouped['Weight'] / grouped['Weight'].sum()
    grouped['Weighted Allocation'] = grouped['Weight Norm'] * total_budget
    grouped['Weighted Predicted Conversions'] = grouped['Weighted Allocation'] / grouped['CPA']

    return grouped, grouped['Uniform Predicted Conversions'].sum(), grouped['Weighted Predicted Conversions'].sum()



"""
def calculate_budget_allocations(df, total_budget):
    # Fix inconsistent capitalization
    df['Converted'] = df['Converted'].astype(str).str.strip().str.upper() == 'TRUE'

    # Filter converted
    df_filtered = df[df['Converted'] == True]

    # Safety check
    if df_filtered.empty:
        return pd.DataFrame(), 0, 0

    grouped = df_filtered.groupby('Lead Source').agg({
        'Cost': 'sum',
        'Converted Count': 'sum'
    }).reset_index()

    # Avoid division by zero
    grouped = grouped[grouped['Converted Count'] > 0].copy()
    if grouped.empty:
        return pd.DataFrame(), 0, 0

    grouped['CPA'] = grouped['Cost'] / grouped['Converted Count']

    # Uniform allocation
    grouped['Uniform Allocation'] = total_budget / len(grouped)
    grouped['Uniform Predicted Conversions'] = grouped['Uniform Allocation'] / grouped['CPA']

    # Weighted allocation
    grouped['Weight'] = 1 / grouped['CPA']
    grouped['Weight Norm'] = grouped['Weight'] / grouped['Weight'].sum()
    grouped['Weighted Allocation'] = grouped['Weight Norm'] * total_budget
    grouped['Weighted Predicted Conversions'] = grouped['Weighted Allocation'] / grouped['CPA']

    return grouped, grouped['Uniform Predicted Conversions'].sum(), grouped['Weighted Predicted Conversions'].sum()

"""