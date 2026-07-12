#!/usr/bin/env python3
"""Migration script: Fix retrieved_articles format and add extracted_context to eval results"""
import pandas as pd
import ast

print("🔄 Migrating CSVs to fix display formats...")

# Fix synthetic_rag_outputs.csv
print("\n1. Fix retrieved_articles format in synthetic_rag_outputs.csv")
rag_df = pd.read_csv('data/synthetic_rag_outputs.csv')

def parse_retrieved_articles(raw):
    """Parse stringified list of dicts and format as pipe-joined titles"""
    try:
        if pd.isna(raw) or raw == '':
            return 'N/A', 'N/A'
        articles = ast.literal_eval(raw)
        if not articles:
            return 'N/A', 'N/A'
        titles = [a.get('title', 'N/A') for a in articles]
        scores = [f"{a.get('score', 0):.3f}" for a in articles]
        return ' | '.join(titles), ' | '.join(scores)
    except:
        return raw, 'N/A'

# Create new columns
rag_df['retrieved_articles_parsed'], rag_df['retrieval_scores'] = zip(
    *rag_df['retrieved_articles'].apply(parse_retrieved_articles)
)

# Drop old column and reorder
rag_df = rag_df.drop(columns=['retrieved_articles'])
rag_df = rag_df[[
    'persona', 'scenario', 'modifier', 'query', 'answer',
    'extracted_context', 'retrieved_articles_parsed', 'retrieval_scores'
]]
rag_df = rag_df.rename(columns={'retrieved_articles_parsed': 'retrieved_articles'})

# Save
rag_df.to_csv('data/synthetic_rag_outputs.csv', index=False)
print(f"   ✅ Fixed {len(rag_df)} rows in synthetic_rag_outputs.csv")
print(f"   Sample retrieved_articles: {rag_df['retrieved_articles'].iloc[0][:100]}...")

# Fix synthetic_eval_results.csv - add extracted_context if missing
print("\n2. Add extracted_context to synthetic_eval_results.csv")
eval_df = pd.read_csv('data/synthetic_eval_results.csv')

if 'extracted_context' not in eval_df.columns:
    print("   Merging extracted_context from rag_outputs...")
    # Create key for merging
    eval_df['_key'] = eval_df['persona'] + '|' + eval_df['scenario'] + '|' + eval_df['modifier'] + '|' + eval_df['query']
    rag_df['_key'] = rag_df['persona'] + '|' + rag_df['scenario'] + '|' + rag_df['modifier'] + '|' + rag_df['query']

    # Merge
    eval_df = eval_df.merge(
        rag_df[['_key', 'extracted_context']],
        on='_key',
        how='left'
    )
    eval_df = eval_df.drop(columns=['_key'])

    # Reorder columns
    judge_cols = [c for c in eval_df.columns if 'judge_' in c]
    other_cols = [c for c in eval_df.columns if c not in judge_cols]
    eval_df = eval_df[other_cols + judge_cols]

    eval_df.to_csv('data/synthetic_eval_results.csv', index=False)
    print(f"   ✅ Added extracted_context to {len(eval_df)} rows")
else:
    print("   ✅ extracted_context already exists")

print("\n✅ Migration complete!")
# Migrate CSVs to human-readable format
# One-time migration script for v1→v2 display format
