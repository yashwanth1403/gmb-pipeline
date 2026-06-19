"""
logo_generator.py
Generates an SVG logo emblem for a car dealer using OpenAI,
saves it to <react_dir>/public/logos/<slug>.svg, returns the public path.
"""
import os
import re
from pathlib import Path
from openai import OpenAI


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _initials(name: str) -> str:
    words = name.split()
    if not words:
        return "CD"
    if len(words) == 1:
        return words[0][:2].upper()
    return (words[0][0] + words[1][0]).upper()


def generate_logo_svg(business_name: str, react_dir: Path) -> str:
    """
    Generate and cache an SVG logo emblem.
    Returns the public path string e.g. /logos/ur-car.svg
    """
    logos_dir = react_dir / "public" / "logos"
    logos_dir.mkdir(parents=True, exist_ok=True)

    slug = _slug(business_name)
    svg_path = logos_dir / f"{slug}.svg"

    if svg_path.exists():
        print(f"  ✅ logo SVG (cached) → {svg_path}")
        return f"/logos/{slug}.svg"

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    initials = _initials(business_name)

    prompt = f"""Create a clean SVG logo emblem for a car dealership called "{business_name}".

STRICT RULES:
- viewBox="0 0 80 80", NO width or height attributes on the root <svg>
- Circular background filled with deep navy #0f2a5c
- A simple white car silhouette icon centered in the circle, OR bold white initials "{initials}" (pick whichever looks better for this name)
- Optionally a thin accent ring or line using #3b82f6 (blue-500)
- Flat design, NO gradients, NO shadows, NO clipPath complexity
- Must be a self-contained valid SVG
- Return ONLY the raw SVG — no markdown fences, no explanation, nothing else"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=900,
        temperature=0.2,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    raw = re.sub(r"```[a-zA-Z]*\n?", "", raw).strip()
    raw = raw.rstrip("`").strip()

    # Extract the SVG block
    match = re.search(r"(<svg[\s\S]+?</svg>)", raw, re.IGNORECASE)
    svg_code = match.group(1) if match else raw

    if not svg_code.strip().startswith("<svg"):
        raise ValueError(f"LLM did not return valid SVG for '{business_name}':\n{raw[:300]}")

    svg_path.write_text(svg_code, encoding="utf-8")
    print(f"  ✅ logo SVG generated → {svg_path}")
    return f"/logos/{slug}.svg"
