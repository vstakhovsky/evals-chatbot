"""
Generate synthetic queries for RAG evaluation.

Product of personas × scenarios × modifiers gives systematic coverage.
Run as: python generate_dataset.py
Or import from notebook: from generate_dataset import generate_queries
"""

import asyncio
import os
import csv
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL"),
)

# Seeds: fresh personas, scenarios, modifiers (not copied from reference repo)
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
    {
        "id": "card_frozen_security",
        "name": "Card frozen after security check",
        "description": "User's card was blocked temporarily after a security review, needs to unfreeze it or understand what documents are required.",
    },
    {
        "id": "topup_declined",
        "name": "Top-up declined",
        "description": "Money added to Revolut failed - bank declined the charge or there was an error, user wants to know why and how to fix it.",
    },
    {
        "id": "source_of_funds_request",
        "name": "Source of funds request",
        "description": "Revolut is asking for proof of where money came from (salary, savings, etc.), user needs to understand what documents to upload.",
    },
    {
        "id": "proof_address_rejected",
        "name": "Proof of address rejected",
        "description": "User uploaded a document for address verification but it was rejected, needs to know what format is accepted and why.",
    },
    {
        "id": "chargeback_status",
        "name": "Chargeback dispute status",
        "description": "User raised a dispute for a transaction they didn't recognize, wants to check progress or expected timeline.",
    },
    {
        "id": "close_account",
        "name": "Close the account",
        "description": "User wants to permanently close their Revolut account and withdraw remaining balance, needs to understand the process.",
    },
]

MODIFIERS = [
    {
        "id": "neutral",
        "name": "Neutral",
        "description": "Normal state, just asking the question calmly.",
    },
    {
        "id": "angry_after_waiting",
        "name": "Angry after waiting",
        "description": "Frustrated tone, has been waiting for response or resolution, uses stronger language ('finally', 'ridiculous', 'unacceptable').",
    },
    {
        "id": "anxious_about_money",
        "name": "Anxious about money",
        "description": "Worried about funds being stuck or lost, mentions urgent bills, rent, or payments due, nervous tone.",
    },
    {
        "id": "in_a_hurry_before_trip",
        "name": "In a hurry before trip",
        "description": "Traveling soon, needs immediate resolution, mentions 'leaving tomorrow', 'flight in 4 hours', 'abroad', short and urgent.",
    },
    {
        "id": "confused_non_native_english",
        "name": "Confused non-native English",
        "description": "Struggling with English, uses simpler vocabulary, may repeat phrases for clarity, expresses confusion about technical terms.",
    },
]

PROMPT = """Generate exactly one customer query for a Revolut support dialog window.
This is not a chat transcript: the customer sends one message, and support gives one answer.

Requirements:
- write only the customer's message, with no labels, quotes, markdown, or answer
- make it realistic for Revolut support and suitable for a single answer
- follow the persona's language, tone, slang, and typical typos
- use the scenario as the main support issue
- apply the modifier naturally
- keep it concise: 1-3 sentences, one support request
- do not invent real personal data, account numbers, emails, or phone numbers
- don't mix several languages in a single message

Persona:
{persona}

Scenario:
{scenario}

Modifier:
{modifier}
"""

# Generation settings
MAX_ROWS = None  # Set to a small int (e.g., 25) for testing, None for full dataset
SEM_CONCURRENCY = 8
SAVE_EVERY = 25
OUTPUT_PATH = "data/synthetic_queries.csv"


async def generate_query(persona, scenario, modifier, semaphore):
    """Generate one query for a given persona × scenario × modifier combination."""
    async with semaphore:
        persona_text = f"{persona['name']}. {persona['description']}. Communication style: {persona['communication_style']}"
        scenario_text = f"{scenario['name']}: {scenario['description']}"
        modifier_text = f"{modifier['name']}: {modifier['description']}"

        prompt = PROMPT.format(
            persona=persona_text,
            scenario=scenario_text,
            modifier=modifier_text,
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        query = response.choices[0].message.content.strip()
        # Remove any markdown quotes if present
        query = query.strip('"').strip("'")

        return {
            "persona": persona["id"],
            "scenario": scenario["id"],
            "modifier": modifier["id"],
            "query": query,
        }


async def generate_queries(
    output_path=OUTPUT_PATH,
    max_rows=MAX_ROWS,
    concurrency=SEM_CONCURRENCY,
    save_every=SAVE_EVERY,
):
    """Generate all queries as Cartesian product of personas × scenarios × modifiers."""
    os.makedirs("data", exist_ok=True)

    # Build all combinations
    all_combinations = []
    for persona in PERSONAS:
        for scenario in SCENARIOS:
            for modifier in MODIFIERS:
                all_combinations.append((persona, scenario, modifier))

    if max_rows:
        all_combinations = all_combinations[:max_rows]

    print(f"Generating {len(all_combinations)} queries...")

    # Check existing file to resume
    existing = set()
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["persona"], row["scenario"], row["modifier"])
                existing.add(key)
        print(f"Resuming: {len(existing)} already generated")

    # Filter out already generated
    todo = [c for c in all_combinations if (c[0]["id"], c[1]["id"], c[2]["id"]) not in existing]
    print(f"Remaining to generate: {len(todo)}")

    if not todo:
        print("All queries already generated!")
        return

    # Setup CSV
    file_exists = os.path.exists(output_path)
    with open(output_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["persona", "scenario", "modifier", "query"]
        )
        if not file_exists:
            writer.writeheader()

    semaphore = asyncio.Semaphore(concurrency)

    for i, (persona, scenario, modifier) in enumerate(tqdm(todo, desc="Generating")):
        try:
            result = await generate_query(persona, scenario, modifier, semaphore)
            with open(output_path, "a", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["persona", "scenario", "modifier", "query"]
                )
                writer.writerow(result)

            # Incremental save every N queries
            if (i + 1) % save_every == 0:
                pass  # Already writing each row immediately

        except Exception as e:
            print(f"Error generating query: {e}")
            continue

    print(f"Done! Queries saved to {output_path}")


if __name__ == "__main__":
    asyncio.run(generate_queries())
