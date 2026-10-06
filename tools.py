"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings
import re




_STOPWORDS = {
    "a", "an", "and", "the", "for", "with", "under", "over",
    "in", "of", "to", "looking", "want", "need", "find"
}


def _keywords(text: str) -> set[str]:
    """Return useful lowercase words for simple keyword matching."""
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return {
        word
        for word in words
        if word not in _STOPWORDS and len(word) > 1
    }


def _size_tokens(size: str) -> set[str]:
    """Normalize a size string into comparable size tokens."""
    cleaned = re.sub(r"\([^)]*\)", " ", size or "").upper()
    parts = [part.strip() for part in cleaned.split("/")]

    tokens = set()

    for part in parts:
        part = " ".join(part.split())
        if not part:
            continue

        tokens.add(part)

        # "US 8" should also be comparable with a user asking for "8".
        shoe_match = re.fullmatch(r"(?:US|UK|EU)\s*(\d+(?:\.\d+)?)", part)
        if shoe_match:
            tokens.add(shoe_match.group(1))

        # "W30 L30" should also expose "W30".
        waist_match = re.match(r"(W\d+)", part)
        if waist_match:
            tokens.add(waist_match.group(1))

    return tokens


def _size_matches(wanted: str, listing_size: str) -> bool:
    """Return True when the requested size is compatible with the listing."""
    wanted_tokens = _size_tokens(wanted)
    listing_tokens = _size_tokens(listing_size)

    if any(token.startswith("ONE SIZE") for token in listing_tokens):
        return True

    return bool(wanted_tokens & listing_tokens)



# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    listings = load_listings()
    query_words = _keywords(description)

    scored = []

    for listing in listings:
        if max_price is not None and listing["price"] > max_price:
            continue

        if size is not None and not _size_matches(size, listing["size"]):
            continue

        primary_text = " ".join([
            listing["title"],
            listing["category"],
            " ".join(listing["style_tags"]),
        ])

        secondary_text = " ".join([
            listing["description"],
            " ".join(listing["colors"]),
            listing["brand"] or "",
        ])

        primary_matches = len(query_words & _keywords(primary_text))
        secondary_matches = len(query_words & _keywords(secondary_text))

        score = (3 * primary_matches) + secondary_matches

        if score > 0:
            scored.append((score, listing))

    scored.sort(
        key=lambda pair: (-pair[0], pair[1]["price"])
    )

    return [
        listing
        for _, listing in scored[:config.SEARCH_RESULT_LIMIT]
    ]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = wardrobe.get("items", [])

    item_summary = (
        f"Item: {new_item['title']}\n"
        f"Category: {new_item['category']}\n"
        f"Colors: {', '.join(new_item['colors'])}\n"
        f"Style tags: {', '.join(new_item['style_tags'])}\n"
    )

    if not items:
        prompt = f"""
{item_summary}

The user has no saved wardrobe items yet.
Suggest one or two concise ways they could style this item using general
clothing categories, colors, and aesthetics.
""".strip()
    else:
        wardrobe_lines = []

        for item in items:
            line = (
                f"- {item['name']} | category: {item['category']} | "
                f"colors: {', '.join(item['colors'])} | "
                f"styles: {', '.join(item['style_tags'])}"
            )

            if item.get("notes"):
                line += f" | notes: {item['notes']}"

            wardrobe_lines.append(line)

        wardrobe_text = "\n".join(wardrobe_lines)

        prompt = f"""
{item_summary}

The user's wardrobe:
{wardrobe_text}

Suggest one or two outfits using the new item and pieces from this wardrobe.
Name the wardrobe pieces you chose and briefly explain why they work together.
Do not invent items the user owns.
""".strip()

    return generate(
        prompt,
        system=(
            "You are FitFindr's outfit-planning tool. Give concise, specific "
            "styling suggestions grounded in the item and wardrobe provided."
        ),
    )


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return "A fit card cannot be created until an outfit suggestion is available."

    prompt = f"""
Selected item: {new_item['title']}
Price: ${new_item['price']:.2f}
Platform: {new_item['platform']}
Colors: {', '.join(new_item['colors'])}
Style tags: {', '.join(new_item['style_tags'])}

Outfit suggestion:
{outfit}

Write a social-style fit caption in 2 to 4 sentences.
Mention the selected item, its exact price (${new_item['price']:.2f}),
and the platform ({new_item['platform']}) once each.
Describe the overall vibe of the outfit.
Do not invent facts about the listing.
""".strip()

    return generate(
        prompt,
        system=(
            "You are FitFindr's fit-card writer. Write short, natural captions "
            "using only the facts supplied. Keep every caption between 2 and "
            "4 sentences."
        ),
    )   
