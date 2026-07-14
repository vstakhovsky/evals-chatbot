"""
Generate synthetic queries for RAG evaluation.

v1 (legacy): Product of personas × scenarios × modifiers (150 queries)
v2 (current): Seed-based variant generation with controlled families

Usage:
    python generate_dataset.py           # v1 Cartesian product
    python generate_dataset.py --v2      # v2 variant generation
    python generate_dataset.py --v2 --smoke 10    # smoke test (10 seeds)
"""

import asyncio
import os
import csv
import json
import argparse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL"),
)

# =============================================================================
# v1: Cartesian product (legacy, kept for compatibility)
# =============================================================================

PERSONAS = [
    {
        "id": "berlin_expat_freelancer",
        "name": "Berlin Expat Freelancer",
        "description": "Software freelancer from Brazil living in Berlin, 3 years in DE, comfortable with English but occasional Portuguese/German mixed phrases, casual tech-savvy tone, uses euro/SEPA terminology, expects fast digital-first support.",
        "communication_style": "Casual, direct, some tech-savvy language ('app', 'instant transfer'), may mention 'Aufenthaltstitel' or 'Bundesamt', occasional German/Portuguese filler words ( 'acho', 'ja', 'doch')",
    },
    {
        "id": "spanish_student_erasmus",
        "name": "Spanish Student Erasmus",
        "description": "University student from Barcelona doing Erasmus in Amsterdam, 6 months abroad, uses informal language with Spanish-specific phrasing ('tengo', 'vale', 'ostra'), refers to 'pago colegiado' or 'Bizum', expects student-friendly explanations, some English grammar slips.",
        "communication_style": "Informal, uses Spanish punctuation (¡, ¿) sometimes, mentions 'uni', 'erasmus', 'mis padres', expects simple explanations, may use Spanish idioms translated directly",
    },
    {
        "id": "uk_small_business_owner",
        "name": "UK Small Business Owner",
        "description": "Shop owner in Manchester, 40s, lifelong Revolut user for business expenses, uses British English ('sort code', 'direct debit', 'HMRC'), practical tone focused on getting things done quickly, mentions 'VAT', 'tax return', 'suppliers'.",
        "communication_style": "British spelling (organisation, colour), mentions 'cheque', 'bank statement', 'HMRC', practical and solution-focused, expects clear step-by-step guidance",
    },
    {
        "id": "french_retiree_traveler",
        "name": "French Retiree Traveler",
        "description": "Retired teacher from Lyon, travels frequently in Europe, uses French phrasing ('comment faire', 'merci'), less comfortable with English tech terms, expects patient detailed explanations, mentions 'RIB', 'carte bleue', 'voyage'.",
        "communication_style": "Polite formal French tone ('bonjour', 's'il vous plaît'), may use French punctuation style, expects thorough explanations, mentions 'assurance voyage', 'retrait abroad'",
    },
    {
        "id": "polish_gig_courier",
        "name": "Polish Gig Courier",
        "description": "Food delivery courier in Warsaw, 25, uses Revolut for instant payouts, practical focus on money availability, mentions 'BLIK', 'przelew', may have minor English grammar errors, expects quick actionable answers.",
        "communication_style": "Direct, practical, minor grammar errors, mentions 'wypłata', 'przelew natychmiastowy', 'środki', focused on when money will be available",
    },
]

SCENARIOS = [
    {"id": "card_frozen_security", "name": "Card frozen after security check", "description": "User's card was blocked temporarily after a security review, needs to unfreeze it or understand what documents are required."},
    {"id": "topup_declined", "name": "Top-up declined", "description": "Money added to Revolut failed - bank declined the charge or there was an error, user wants to know why and how to fix it."},
    {"id": "source_of_funds_request", "name": "Source of funds request", "description": "Revolut is asking for proof of where money came from (salary, savings, etc.), user needs to understand what documents to upload."},
    {"id": "proof_address_rejected", "name": "Proof of address rejected", "description": "User uploaded a document for address verification but it was rejected, needs to know what format is accepted and why."},
    {"id": "chargeback_status", "name": "Chargeback dispute status", "description": "User raised a dispute for a transaction they didn't recognize, wants to check progress or expected timeline."},
    {"id": "close_account", "name": "Close the account", "description": "User wants to permanently close their Revolut account and withdraw remaining balance, needs to understand the process."},
]

MODIFIERS = [
    {"id": "neutral", "name": "Neutral", "description": "Normal state, just asking the question calmly."},
    {"id": "angry_after_waiting", "name": "Angry after waiting", "description": "Frustrated tone, has been waiting for response or resolution, uses stronger language ('finally', 'ridiculous', 'unacceptable')."},
    {"id": "anxious_about_money", "name": "Anxious about money", "description": "Worried about funds being stuck or lost, mentions urgent bills, rent, or payments due, nervous tone."},
    {"id": "in_a_hurry_before_trip", "name": "In a hurry before trip", "description": "Traveling soon, needs immediate resolution, mentions 'leaving tomorrow', 'flight in 4 hours', 'abroad', short and urgent."},
    {"id": "confused_non_native_english", "name": "Confused non-native English", "description": "Struggling with English, uses simpler vocabulary, may repeat phrases for clarity, expresses confusion about technical terms."},
]

# Import prompts from centralized registry
from prompts import PROMPT_REGISTRY

# Legacy v1 CSV output removed — use benchmark/cases.jsonl instead


async def generate_query_v1(persona, scenario, modifier, semaphore):
    """Generate one query for v1 Cartesian product."""
    async with semaphore:
        persona_text = f"{persona['name']}. {persona['description']}. Communication style: {persona['communication_style']}"
        scenario_text = f"{scenario['name']}: {scenario['description']}"
        modifier_text = f"{modifier['name']}: {modifier['description']}"

        synthetic_prompt = PROMPT_REGISTRY["synthetic_generation"]["template"]
        prompt = synthetic_prompt.format(persona=persona_text, scenario=scenario_text, modifier=modifier_text)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        query = response.choices[0].message.content.strip().strip('"').strip("'")

        return {"persona": persona["id"], "scenario": scenario["id"], "modifier": modifier["id"], "query": query}


async def generate_queries_v1(output_path=V1_OUTPUT_PATH, max_rows=None, concurrency=8, save_every=25):
    """v1: Generate Cartesian product of personas × scenarios × modifiers."""
    os.makedirs("data", exist_ok=True)

    all_combinations = []
    for persona in PERSONAS:
        for scenario in SCENARIOS:
            for modifier in MODIFIERS:
                all_combinations.append((persona, scenario, modifier))

    if max_rows:
        all_combinations = all_combinations[:max_rows]

    print(f"Generating {len(all_combinations)} queries (v1)...")

    # Check existing
    existing = set()
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["persona"], row["scenario"], row["modifier"])
                existing.add(key)
        print(f"Resuming: {len(existing)} already generated")

    todo = [c for c in all_combinations if (c[0]["id"], c[1]["id"], c[2]["id"]) not in existing]
    print(f"Remaining to generate: {len(todo)}")

    if not todo:
        print("All queries already generated!")
        return

    # Setup CSV
    file_exists = os.path.exists(output_path)
    with open(output_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["persona", "scenario", "modifier", "query"])
        if not file_exists:
            writer.writeheader()

    semaphore = asyncio.Semaphore(concurrency)

    for i, (persona, scenario, modifier) in enumerate(todo):
        if i > 0 and i % 25 == 0:
            print(f"  Progress: {i}/{len(todo)} queries generated...")
        try:
            result = await generate_query_v1(persona, scenario, modifier, semaphore)
            with open(output_path, "a", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["persona", "scenario", "modifier", "query"])
                writer.writerow(result)
        except Exception as e:
            print(f"Error generating query: {e}")
            continue

    print(f"Done! Queries saved to {output_path}")


# =============================================================================
# v2: Seed-based variant generation
# =============================================================================

SEEDS_PATH = "benchmark/seed_cases.jsonl"
V2_OUTPUT_PATH = "benchmark/v2_cases.jsonl"

# Variant families: short_mobile, typo_noisy, non_native, emotional, missing_context, incorrect_assumption
VARIANT_FAMILIES = [
    {
        "id": "short_mobile",
        "name": "Short mobile",
        "description": "Very brief (5-8 words), mobile-first phrasing, missing context, urgent tone.",
        "prompt_instruction": "Rewrite this query as a very brief mobile message (5-8 words max). User is in a rush, typing on a phone, omits context. Keep the core question but make it short and urgent.",
    },
    {
        "id": "typo_noisy",
        "name": "Typo noisy",
        "description": "Contains typos, minor grammar errors, autocorrect artifacts, casual but messy.",
        "prompt_instruction": "Rewrite this query with realistic typos, minor grammar errors, and autocorrect artifacts. Keep it readable but messy like someone typing quickly on mobile.",
    },
    {
        "id": "non_native",
        "name": "Non-native English",
        "description": "From speaker of English as second language, grammar slips, translated idioms, word order issues.",
        "prompt_instruction": "Rewrite this query as if written by a non-native English speaker. Include minor grammar slips, awkward phrasing, or idioms translated directly from their native language.",
    },
    {
        "id": "emotional",
        "name": "Emotional",
        "description": "Frustrated, angry, or anxious tone, stronger language, emotional context.",
        "prompt_instruction": "Rewrite this query with strong emotion (frustration, anger, or anxiety). Use stronger language, emotional markers, and show the user's state clearly.",
    },
    {
        "id": "missing_context",
        "name": "Missing context",
        "description": "Vague about details, omits important information, assumes knowledge.",
        "prompt_instruction": "Rewrite this query to be deliberately vague about important details. The user omits context or assumes support knows their situation.",
    },
]

VARIANT_PROMPT_SIMPLE = """Original query: {original_query}

{variant_instruction}

Rewrite this query for a Revolut support context. Keep the same core question and meaning.

Generate only the rewritten query, no labels or explanations.
"""

SPLITS = {"train": 0.5, "dev": 0.2, "test": 0.3}  # Group-aware split ratios


def assign_splits(seeds):
    """Assign splits to seeds BEFORE variant generation (group-aware)."""
    import random
    random.seed(42)  # Deterministic

    # Group by seed_id
    seed_groups = {}
    for seed in seeds:
        seed_id = seed.get("seed_id")
        if seed_id not in seed_groups:
            seed_groups[seed_id] = []
        seed_groups[seed_id].append(seed)

    # Assign split per group
    split_ratios = list(SPLITS.items())
    for seed_id, group in seed_groups.items():
        # Shuffle and pick split based on cumulative ratios
        rand = random.random()
        cumulative = 0.0
        for split_name, ratio in split_ratios:
            cumulative += ratio
            if rand <= cumulative:
                for seed in group:
                    seed["split"] = split_name
                break

    return seeds


def get_variant_families(seed):
    """Determine which variant families apply to a seed."""
    difficulty = seed.get("difficulty", "direct")
    risk_level = seed.get("risk_level", "low")

    families = []

    # All seeds get short_mobile
    families.append("short_mobile")

    # Answer-cases: max 2 additional families (strict budget control)
    if risk_level == "low":
        # Only add additional families for 50% of low-risk seeds
        import random
        random.seed(hash(seed["seed_id"]) % 1000)  # Deterministic but pseudo-random

        if difficulty == "direct":
            # Direct cases: 50% get typo_noisy, 30% get non_native
            r = random.random()
            if r < 0.5:
                families.append("typo_noisy")
            if r < 0.3:
                families.append("non_native")
        else:
            # Ambiguous/noisy cases: only 30% get one additional family
            if random.random() < 0.3:
                families.append("typo_noisy")

    # Critical: exactly 2 variants (emotional + non_native)
    elif risk_level == "critical":
        families.extend(["emotional", "non_native"])
    # Unknown: only 1 variant (short_mobile only)
    elif difficulty == "unknown":
        pass  # No additional families

    return families


async def generate_variant_with_number(seed, family_id, variant_num, semaphore):
    """Generate one variant for a seed with explicit variant number."""
    async with semaphore:
        family = next((f for f in VARIANT_FAMILIES if f["id"] == family_id), None)
        if not family:
            return None

        # Simple prompt without complex formatting
        prompt = f"""Original query: {seed['query']}

{family['prompt_instruction']}

Rewrite this query for a Revolut support context. Keep the same core question and meaning.

Generate only the rewritten query, no labels or explanations."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )

        variant_query = response.choices[0].message.content.strip().strip('"').strip("'")

        # Build variant case_id with explicit number
        case_id = f"{seed['seed_id']}_variant_{family_id}_{variant_num}"

        return {
            "case_id": case_id,
            "seed_id": seed["seed_id"],
            "query": variant_query,
            "topic": seed["topic"],
            "expected_action": seed["expected_action"],
            "risk_level": seed["risk_level"],
            "expected_article": seed.get("expected_article"),
            "required_facts": seed.get("required_facts", []),
            "difficulty": seed["difficulty"],
            "source": f"synthetic_variant_{family_id}",
            "split": seed["split"],  # Inherit split from seed
        }


async def generate_variants_v2(seeds, output_path=V2_OUTPUT_PATH, max_seeds=None, concurrency=8):
    """v2: Generate variants from seeds."""
    print(f"Generating variants for {len(seeds)} seeds (v2)...")

    if max_seeds:
        seeds = seeds[:max_seeds]
        print(f"Smoke mode: limited to {max_seeds} seeds")

    # Assign splits BEFORE generation
    seeds = assign_splits(seeds)

    # Build variant generation tasks
    tasks = []
    for seed in seeds:
        families = get_variant_families(seed)
        for family_id in families:
            tasks.append((seed, family_id))

    print(f"Total variants to generate: {len(tasks)}")

    # Check existing
    existing = set()
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    existing.add(obj["case_id"])
                except:
                    pass
        print(f"Resuming: {len(existing)} variants already generated")

    # Populate used_case_ids from existing variants
    used_case_ids = {}
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    case_id = obj.get("case_id", "")
                    # Extract seed_id and family_id from case_id
                    parts = case_id.split("_variant_")
                    if len(parts) >= 3:
                        seed_id = "_".join(parts[:-2])  # Everything before "_variant_"
                        family_id = parts[-2]  # Second-to-last part
                        seed_key = (seed_id, family_id)
                        # Extract variant number
                        try:
                            variant_num = int(parts[-1])
                            used_case_ids[seed_key] = max(used_case_ids.get(seed_key, 0), variant_num)
                        except ValueError:
                            pass
                except:
                        pass

    # Filter out already generated using used_case_ids
    todo = []
    for seed, family_id in tasks:
        seed_key = (seed['seed_id'], family_id)
        if seed_key not in used_case_ids:
            todo.append((seed, family_id))

    print(f"Remaining to generate: {len(todo)}")

    if not todo:
        print("All variants already generated!")
        return

    semaphore = asyncio.Semaphore(concurrency)

    # Generate variants
    variants = []
    for i, (seed, family_id) in enumerate(todo):
        if i > 0 and i % 25 == 0:
            print(f"  Progress: {i}/{len(todo)} variants generated...")

        try:
            # Get next variant number for this seed/family
            seed_key = (seed['seed_id'], family_id)
            if seed_key not in used_case_ids:
                used_case_ids[seed_key] = 1
            else:
                used_case_ids[seed_key] += 1

            # Generate variant with proper case_id
            variant = await generate_variant_with_number(seed, family_id, used_case_ids[seed_key], semaphore)
            if variant:
                variants.append(variant)
        except Exception as e:
            print(f"Error generating variant for {seed['case_id']} ({family_id}): {e}")
            continue

    # Write to file
    with open(output_path, "a", encoding="utf-8") if os.path.exists(output_path) else open(output_path, "w", encoding="utf-8") as f:
        for variant in variants:
            f.write(json.dumps(variant, ensure_ascii=False) + "\n")

    print(f"Done! {len(variants)} variants saved to {output_path}")


def load_seeds():
    """Load seeds from benchmark/seed_cases.jsonl."""
    seeds = []
    with open(SEEDS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                seeds.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return seeds


async def main():
    parser = argparse.ArgumentParser(description="Generate synthetic queries for RAG evaluation")
    parser.add_argument("--v2", action="store_true", help="Use v2 variant generation")
    parser.add_argument("--smoke", type=int, metavar="N", help="Smoke mode: generate variants for N seeds only")
    args = parser.parse_args()

    if args.v2:
        # v2: Seed-based variant generation
        seeds = load_seeds()
        print(f"Loaded {len(seeds)} seeds from {SEEDS_PATH}")

        max_seeds = args.smoke if args.smoke else None
        await generate_variants_v2(seeds, max_seeds=max_seeds)

        # Print summary
        print("\n" + "=" * 80)
        print("VARIANT GENERATION COMPLETE")
        print("=" * 80)
        print(f"Seeds processed: {len(seeds) if not max_seeds else max_seeds}")
        print(f"Expected total variants: ~{len(seeds) * 2.5:.0f} (2-3 per seed)")
        print(f"Output: {V2_OUTPUT_PATH}")

    else:
        # v1: Cartesian product (legacy)
        await generate_queries_v1()


if __name__ == "__main__":
    asyncio.run(main())
