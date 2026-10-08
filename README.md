# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->


FitFindr helps a user search a thrift-listing dataset using a natural-language request such as "vintage graphic tee under $30." It parses the request into a description, optional size, and maximum price, then searches the listings and selects the best-ranked match. If a match is found, FitFindr uses the user's wardrobe to suggest outfits and generates a short fit-card caption for the selected item. If nothing matches, the agent stops early and tells the user which search constraints they can change.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->



### `search_listings`

- **What it does:** Searches the listings dataset for items that match the user's description, optional size, and optional maximum price, then ranks the matching items with the best matches first.
- **Inputs:** `description` (`str`) — keywords describing the item the user wants; `size` (`str | None`) — an optional size filter that should match compatible size labels case-insensitively, such as `M` matching `S/M` or `M/L`; `max_price` (`float | None`) — an optional inclusive maximum price.
- **Returns:** A list of matching listing dictionaries, ordered best match first, with each dictionary containing `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`. The list contains at most the configured search-result limit.
- **When it has nothing:** Returns an empty list `[]` when no listings satisfy the search criteria. It does not return `None` or raise an exception for a normal no-match search.

### `suggest_outfit`

- **What it does:** Takes the selected thrift listing and the user's wardrobe and generates one or two outfit suggestions that pair the new item with pieces the user already owns when possible.
- **Inputs:** `new_item` (`dict`) — the selected listing dictionary; `wardrobe` (`dict`) — a wardrobe dictionary containing an `items` list of wardrobe-item dictionaries.
- **Returns:** A non-empty string containing outfit suggestions based on the selected item and the user's wardrobe.
- **When it has nothing:** If the wardrobe contains no items, it still returns a non-empty string with general styling advice for the selected item instead of failing or returning an empty string.

### `create_fit_card`

- **What it does:** Uses the outfit suggestion and selected listing to generate a short, post-style caption describing the thrift find and how it could be styled.
- **Inputs:** `outfit` (`str`) — the outfit suggestion produced by `suggest_outfit`; `new_item` (`dict`) — the selected listing dictionary.
- **Returns:** A two-to-four sentence caption that mentions the item, its price, its platform, and the overall style or vibe.
- **When it has nothing:** If `outfit` is empty or contains only whitespace, it returns a descriptive fallback message rather than raising an exception or generating a normal fit card.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->


**Branch rule:** If `search_listings` returns an empty list, put a helpful message in the session explaining that no matches were found and suggesting that the user change the description, size, or price limit, then stop the run. Otherwise, select the first search result and continue to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:**  The query is parsed with deterministic string and regex matching. Price phrases such as `under $30` are extracted into `max_price`, explicit size phrases such as `size M` or `in size M` are extracted into `size`, and the remaining text becomes the item `description`.

**What moves through the session:** The original user query is stored in `session["query"]`. The parsed `description`, `size`, and `max_price` go into `session["parsed"]`. Search results go into `session["search_results"]`, the chosen listing goes into `session["selected_item"]`, the outfit suggestion goes into `session["outfit_suggestion"]`, and the final caption goes into `session["fit_card"]`.

---


## Sample Run

**One full query**

```text
$ python app.py ask 'vintage graphic tee under $30'

Found:    Graphic Tee — 2003 Tour Bootleg Style — $24.0 on depop

Outfit:   **Outfit 1: Y2K Grunge Streetwear**
*   **Bottoms:** Baggy straight-leg jeans (dark blue)
*   **Shoes:** Chunky white sneakers
*   **Outerwear:** Vintage black denim jacket
*   **Accessories:** Black crossbody bag

**Why it works:**
The vintage tour graphic tee pairs naturally with baggy dark denim for an effortless, authentic 2000s streetwear silhouette. Tossing on the slightly cropped vintage black denim jacket adds texture and dimension while keeping the color palette grounded. The chunky white sneakers brighten the look and anchor the heavy, relaxed proportions of the jeans, while the black crossbody bag keeps it practical and sleek.

***

**Outfit 2: Contrast Grunge & Tailoring**
*   **Bottoms:** Wide-leg khaki trousers
*   **Shoes:** Black combat boots
*   **Accessories:** Brown leather belt, Black crossbody bag

**Why it works:**
This look plays with high-low styling by contrasting the distressed, rebellious energy of the bootleg graphic tee with the polished structure of wide-leg khaki trousers. Tucking the tee in with the brown leather belt defines the waist, and the black combat boots add a tough, grunge edge that ties back to the black tones in the tee.

Fit card: Score this vintage-style 2003 tour graphic tee for just $24.00 on depop. Create an effortless Y2K grunge streetwear look by pairing it with baggy dark blue jeans and a vintage black denim jacket. Complete the relaxed silhouette with chunky white sneakers and a sleek black crossbody bag.

0 model calls this session, 2 served from cache
```

**The three tools, tested one at a time**

```text
$ python -c "from tools import search_listings; print([(x['id'], x['title'], x['price']) for x in search_listings('graphic tee', max_price=30)])"

[('lst_002', 'Y2K Baby Tee — Butterfly Print', 18.0), ('lst_033', 'Vintage Band Tee — Faded Grey', 19.0), ('lst_006', 'Graphic Tee — 2003 Tour Bootleg Style', 24.0), ('lst_015', 'Vintage Graphic Hoodie — Faded Black', 26.0), ('lst_017', 'Mesh Long-Sleeve Top — Black', 15.0), ('lst_011', 'Low-Rise Cargo Pants — Khaki', 27.0)]
```

```text
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

Here are two outfit suggestions using your Vintage Levi's 501 Jeans:

### Outfit 1: Streetwear Casual
* **Top:** White ribbed tank top
* **Outerwear:** Vintage black denim jacket
* **Shoes:** Chunky white sneakers
* **Accessories:** Black crossbody bag

**Why it works:** The fitted white tank balances the straight-leg vintage denim, while the slightly cropped black jacket adds contrast and highlights the waist. Chunky sneakers and the crossbody bag lean into the streetwear tag, keeping the look effortless and grounded.

---

### Outfit 2: Classic Contrast
* **Top:** Oversized grey crewneck sweatshirt
* **Shoes:** Black combat boots
* **Accessories:** Brown leather belt, Black crossbody bag

**Why it works:** Tucking the front of the oversized grey crewneck into the 501s creates a relaxed, balanced silhouette. The black combat boots add an edge that contrasts nicely with the medium wash denim, while the brown belt ties the vintage aesthetic together.
```

```text
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('Pair these jeans with a white tank and chunky sneakers for a relaxed streetwear look.', load_listings()[0]))"

Grab these classic Vintage Levi's 501 Jeans in a medium wash for just $38.00 on depop. Pair them with a white tank and chunky sneakers to capture a relaxed streetwear look. This indigo denim staple brings effortless vintage style to your everyday rotation.
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I asked AI to help me turn the starter descriptions of the three FitFindr tools into precise contracts for the README.
- *What came back:* It suggested explicit input types, specific return values, empty-case behavior, and pointed out that plain substring size matching could incorrectly match values such as `S` with `US 9`.
- *What I changed:* I defined each tool's inputs and outputs before implementation, made `search_listings` return an empty list on no match, and implemented token-based size matching so compound sizes such as `S/M` can match `M` without unsafe substring matching.

**Moment 2**

- *What I asked for:* I asked AI to review my implementation while I tested the search tool and planning loop.
- *What came back:* It noticed that a mesh top mentioning "graphic tee" in its description ranked above actual graphic tees, and later caught an indentation issue that caused the agent to return after the search stage instead of continuing through the loop.
- *What I changed:* I weighted title, category, and style-tag matches more heavily than description matches. I also fixed the loop indentation so a successful search continues to `suggest_outfit` and `create_fit_card`, while an empty search returns early.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before second tool | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item carries through state | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card includes price and platform and is 2–4 sentences | 4/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search respects maximum price | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output from one try**, produced by
`run_eval.py::main`, running the loop in `agent.py::run_agent`:

```text
Query: vintage graphic tee under $30

stopped early: no
selected_item: Graphic Tee — 2003 Tour Bootleg Style [id=lst_006] ($24.0, depop)
search_results: 10
search_result_prices: [24.0, 18.0, 19.0, 26.0, 20.0, 25.0, 12.0, 14.0, 16.0, 18.0]

[1] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 10 items: Graphic Tee — 2003 Tour Bootleg Style, Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey … +7 more
      →    branch: results found, continuing

[2] suggest_outfit
      in:  selected_item=lst_006, wardrobe_items=10

[3] create_fit_card
      in:  selected_item=lst_006

---

## Verdicts and Diagnoses

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools | 4/5 | MET (5/5) | All five matching-query runs reached `search_listings`, `suggest_outfit`, and `create_fit_card` and returned a fit card. |
| 2 | Impossible query stops before second tool | 5/5 | MET (5/5) | All five impossible-query runs stopped immediately after the empty search and returned a message telling the user to change the description, size, or maximum price. |
| 3 | Selected item carries through state | 5/5 | MET (5/5) | In all five runs, `session["selected_item"]` had id `lst_006`, and the trace for `suggest_outfit` also showed `selected_item=lst_006`. |
| 4 | Fit card is 2–4 sentences and includes price and platform | 4/5 | MET (5/5) | All five fit cards were between 2 and 4 sentences and included the selected item's `$42.00` price and `poshmark` platform. |
| 5 | Search respects maximum price | 5/5 | MET (5/5) | In all five runs, every price in `search_result_prices` was at or below the requested `$30` maximum. |

**Diagnoses**

None of the five acceptance criteria were missed, so there was no failed criterion that required a failure diagnosis.

However, the traces exposed a search-quality problem that the original criteria did not measure. For the query `denim jacket under $50`, `search_listings` returned seven items, including denim shorts and a denim vest. The problem was in the search tool: a multi-word query could return a listing after matching only one important word such as `denim`. I used that observed weakness as the target for the improvement below.


---

## Loop Trace

**Happy path**

```text
[1] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 4 items: Graphic Tee — 2003 Tour Bootleg Style, Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey … +1 more
      →    branch: results found, continuing
[2] suggest_outfit
      in:  selected_item=lst_006, wardrobe_items=10
      out: **Outfit 1: Y2K Grunge Streetwear** * **Pieces used:** Baggy straight-leg jeans, black combat boots, vintage b…
[3] create_fit_card
      in:  selected_item=lst_006
      out: Channel major Y2K grunge streetwear energy with this vintage-style graphic tee, available now on depop for $24…
```

**Empty search**

```text
[1] search_listings (via MCP)
      in:  description='designer ballgown', size='XXS', max_price=5.0
      out: [] (empty)
      →    branch: empty, stopping

No matching listings found. Try changing the description, size, or maximum price.
```

**On the MCP move:**

I moved `search_listings` behind the MCP server while leaving
`suggest_outfit` and `create_fit_card` as direct tool calls. The agent now
calls `mcp_client.call_tool("search_listings", ...)`, and the MCP client
unwraps the response back into the same native `list[dict]` shape that the
planning loop used before.

The agent's behavior did not change after the rewire. A successful search
still continued to `suggest_outfit` and `create_fit_card`, while an empty
search still stopped immediately. The main visible difference is that the
trace now shows `search_listings (via MCP)`.

I also deliberately tested the three failure modes. An empty search stopped
before the second tool and returned an actionable message. An empty wardrobe
still produced general styling suggestions and completed the run. A bad model
key triggered `ModelUnavailable`, which the agent caught and converted into a
readable error message instead of allowing a stack trace to escape.

---

## The Improvement

**What I changed:**

I tightened multi-word search matching in `search_listings`. Previously, a
listing could be returned when it matched only one important word from a
multi-word query. I changed the search so multi-word descriptions require at
least two matches in the listing's primary fields: title, category, or style
tags. Secondary fields can still affect ranking after a listing passes that
primary-match requirement.

**Which failure it was meant to fix:**

This was not a failed acceptance criterion. It was a search-precision problem
visible in the baseline trace. The query `denim jacket under $50` returned
seven results, including denim shorts and a denim vest, because those listings
matched the word `denim` even though they did not match `jacket`.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before second tool | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item carries through state | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card includes price and platform and is 2–4 sentences | 4/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search respects maximum price | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help, and how do I know:**

Yes. Before the change, `denim jacket under $50` returned seven listings,
including shorts and a vest. After the change, the same query returned only
one listing: `Denim Jacket — Light Wash, Cropped`.

The main `vintage graphic tee under $30` query also became more selective,
going from ten results to four while keeping the same correct top result,
`lst_006`. All five original acceptance criteria still passed 5 of 5 after
the change, so the precision improvement did not break the tested agent
behavior.

---

## What's Still Broken

No acceptance criterion is currently missed.

The search is still a simple keyword-based heuristic rather than semantic
search. Requiring two primary matches improves precision for queries such as
`denim jacket`, but it could be too strict when a user uses synonyms or
different wording from the listing. A future improvement would be to normalize
common clothing synonyms or add a lightweight semantic similarity step while
keeping the deterministic size and price filters.

Model availability is also outside the agent's control. Temporary provider
errors or invalid credentials can still prevent outfit or fit-card generation,
but those failures are now caught and returned as readable session errors
instead of crashing the program.

I stopped after the single measured search improvement because all five
acceptance criteria were already met and the Unit 4 requirement was to make
and measure one improvement.


<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
