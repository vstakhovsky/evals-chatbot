"""
LLM-as-a-judge evaluation functions.

Each judge returns a binary verdict (bool) + reasoning string.
Judges evaluate: relevancy, conciseness, helpfulness, correctness, legal compliance, redirects.

Usage from notebook:
    from judges import judge_relevancy, judge_not_excessive, judge_is_helpful, judge_no_false_info, judge_legally_correct, judge_redirects_when_unknown
"""

import asyncio
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL"),
)


async def _generate_judge_output(prompt, schema_title, schema_description):
    """Shared helper for structured judge output."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "judge_output",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "verdict": {
                            "type": "boolean",
                            "title": schema_title,
                            "description": schema_description,
                        },
                        "reasoning": {
                            "type": "string",
                            "title": "Reasoning",
                            "description": "Brief explanation for the verdict (1-2 sentences).",
                        },
                    },
                    "required": ["verdict", "reasoning"],
                    "additionalProperties": False,
                },
            },
        },
        temperature=0.0,
    )
    parsed = response.choices[0].message.content
    import json

    data = json.loads(parsed)
    return data["verdict"], data["reasoning"]


async def judge_relevancy(query, answer, context):
    """Does the answer directly address the user's actual support issue?"""
    prompt = f"""Metric: Relevancy
Question to answer: Does the assistant's answer directly address the user's actual support issue?

Criteria for TRUE:
- Answer addresses the core question or problem the user is asking about
- Answer is on-topic and relevant to the user's query

Criteria for FALSE:
- Answer talks about something unrelated to the user's question
- Answer is generic and doesn't address the specific issue

User query:
{query}

Assistant answer:
{answer}

Context (retrieved articles):
{context}
"""
    return await _generate_judge_output(
        prompt,
        "Is Relevant",
        "True if answer directly addresses user's issue, False otherwise",
    )


async def judge_not_excessive(query, answer, context):
    """No extra information beyond what the query needs."""
    prompt = f"""Metric: Not Excessive
Question to answer: Does the answer contain only the necessary information, no more?

Criteria for TRUE:
- Answer is concise and sticks to what the user asked for
- No tangential details, warnings, or edge cases unless relevant to the query

Criteria for FALSE:
- Answer includes unnecessary information, off-topic details, or excessive warnings
- Answer is much longer than needed to address the question

User query:
{query}

Assistant answer:
{answer}

Context (retrieved articles):
{context}
"""
    return await _generate_judge_output(
        prompt,
        "Is Not Excessive",
        "True if answer is appropriately concise, False if it contains unnecessary extra information",
    )


async def judge_is_helpful(query, answer, context):
    """Contains concrete steps or call to action when relevant."""
    prompt = f"""Metric: Helpful
Question to answer: Is the answer helpful for resolving the user's issue?

Criteria for TRUE:
- Answer provides concrete steps, actions, or guidance the user can follow
- If the issue is resolvable, answer explains how to resolve it
- If information is missing, answer admits it and redirects appropriately

Criteria for FALSE:
- Answer is vague and doesn't provide actionable guidance
- Answer states something can't be done without explanation or alternative
- Answer is unhelpful or dismissive

User query:
{query}

Assistant answer:
{answer}

Context (retrieved articles):
{context}
"""
    return await _generate_judge_output(
        prompt,
        "Is Helpful",
        "True if answer provides helpful, actionable guidance, False otherwise",
    )


async def judge_no_false_info(query, answer, context):
    """CRITICAL: Nothing contradicting or absent from provided context."""
    prompt = f"""Metric: No False Information (CRITICAL)
Question to answer: Does the answer contain ONLY information that is either (a) explicitly stated in the provided context, or (b) generally factual and consistent with the context?

Criteria for TRUE:
- All factual claims in the answer are supported by the provided context
- No information contradicts or goes beyond what the context says
- If the context doesn't contain the answer, the assistant admits it

Criteria for FALSE:
- Answer includes factual claims not found in the context
- Answer contradicts information in the context
- Answer guesses or makes up information not in the provided articles

User query:
{query}

Assistant answer:
{answer}

Context (retrieved articles):
{context}
"""
    return await _generate_judge_output(
        prompt,
        "No False Information",
        "True if answer contains only information from context or general facts, False if it invents or contradicts context",
    )


async def judge_legally_correct(query, answer, context):
    """No financial advice, no toxic content, no competitor mentions."""
    prompt = f"""Metric: Legally Correct and Safe
Question to answer: Is the answer legally safe and appropriate?

Criteria for TRUE:
- No financial advice (no investment recommendations, no tax advice)
- No toxic, offensive, or discriminatory content
- No mentions of competitors (no recommending other banks or services)

Criteria for FALSE:
- Answer includes financial advice or recommendations
- Answer is toxic, offensive, or inappropriate
- Answer mentions or recommends competitors or alternatives to Revolut

User query:
{query}

Assistant answer:
{answer}

Context (retrieved articles):
{context}
"""
    return await _generate_judge_output(
        prompt,
        "Legally Correct",
        "True if answer is legally safe and appropriate, False otherwise",
    )


async def judge_redirects_when_unknown(query, answer, context):
    """When context lacks the answer, bot admits it and redirects to Help Center."""
    prompt = f"""Metric: Redirects When Unknown
Question to answer: When the provided context doesn't contain the answer, does the assistant admit it and redirect to the Help Center?

Criteria for TRUE:
- Context does not contain the answer AND assistant admits it doesn't know and redirects to Help Center
- Context contains the answer (this judge passes automatically regardless of answer quality)

Criteria for FALSE:
- Context clearly lacks the answer but assistant tries to guess or invents information
- Assistant should redirect but doesn't

User query:
{query}

Assistant answer:
{answer}

Context (retrieved articles):
{context}
"""
    return await _generate_judge_output(
        prompt,
        "Redirects Appropriately",
        "True if assistant admits lack of knowledge and redirects when context doesn't contain answer, False if it guesses",
    )
