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

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

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
