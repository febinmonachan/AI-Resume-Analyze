import anthropic

from utils.json_parser import safe_parse_json


def analyze_resume(
    resume_text,
    api_key
):

    client = anthropic.Anthropic(
        api_key=api_key
    )

    system_prompt = """
You are an expert resume analyst.

Return ONLY valid JSON.

{
  "overall_score": 0,
  "summary": "",
  "sections": {},
  "strengths": [],
  "improvements": [],
  "keywords": []
}
"""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1500,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"""
Analyze this resume:

{resume_text}
"""
            }
        ]
    )

    raw = message.content[0].text

    return safe_parse_json(raw)
