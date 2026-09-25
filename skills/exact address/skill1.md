---
name: exact-property-address
description: >
  Find the exact postal address and postcode of a UK residential property from a
  Rightmove, Zoopla, OnTheMarket, auction, or estate-agent listing. Use when the
  listing hides the house number/name, gives only a street or approximate map
  position, or when the user wants the address verified rather than guessed.
---

# Exact Property Address

## Goal

Resolve a UK property listing to the most precise defensible postal address:

**[House number/name], [Street], [Locality if needed], [Post town], [County if useful], [Postcode]**

The result must be evidence-based. Do not infer a house number merely from map position,
photo order, neighbouring numbers, or an approximate pin.

## Core method

Use a **pivot-and-verify** workflow:

1. Open the live property listing and collect every identifying clue.
2. Find the estate agent's own brochure, PDF, microsite, auction catalogue, or archived listing.
3. Extract any exact number/name or postcode exposed there.
4. Search that candidate address against independent records.
5. Cross-check physical/property details to prove it is the same property.
6. Report the address with a confidence level and the evidence trail.

The strongest version of this method is:

**live listing → agent brochure/PDF → exact candidate address → historical/official record → property-detail match**

This was the successful route for 107 Pickwick Road:
the current Rightmove listing led to the agent brochure, which exposed the exact address;
that address then led to the earlier auction catalogue/results, whose property description
matched the current listing.

## Step 1 — Extract clues from the live listing

Record:

- listing URL and property ID
- estate agent and branch
- displayed street/locality
- displayed postcode sector or full postcode
- asking price
- property type
- bedroom count
- tenure
- floor area and floorplan
- distinctive exterior details
- garden position/orientation if visible
- parking/garage
- nearby landmark, junction, school, pub, filling station, church, etc.
- listing date and reductions
- auctioneer / modern-method-of-auction provider if present
- EPC rating or EPC link
- downloadable brochure, floorplan, legal pack, or media links

Do not stop at the visible Rightmove text. Listing portals often suppress the house
number while the underlying agent collateral does not.

## Step 2 — Look for first-party collateral

Priority order:

1. Estate-agent brochure PDF
2. Estate-agent property page
3. Auction catalogue / auction result sheet
4. Auction legal pack
5. EPC document or EPC register result
6. Planning application documents
7. Previous estate-agent listing
8. Land Registry-derived sold-price record
9. Other property portals / archived copies
10. Search snippets and secondary property-data sites

Useful searches include combinations of:

- `"Rightmove property ID" agent`
- `"street name" "agent name" PDF`
- `"street name" auction`
- `"street name" "bedroom count" agent`
- exact listing title in quotes
- distinctive phrase copied from the description
- brochure filename / property reference if exposed
- postcode + property type + agent

### PDFs matter

Always inspect PDFs attached to or associated with the listing.

Agent PDFs frequently reveal:

- the full address on the cover
- the full address in a footer
- an internal property reference
- EPC address
- auction lot number
- legal-pack references

If a PDF is being analysed, inspect the actual PDF pages rather than relying only on a
search-engine snippet.

## Step 3 — Pivot on any exact clue

Once a possible house number/name appears, immediately search the complete candidate,
for example:

`"107 Pickwick Road" Corsham`

Then search variants:

- exact address in quotes
- address + postcode
- address + auction
- address + sold
- address + planning
- address + EPC
- address + estate agent

The objective is not merely to find the same string elsewhere; it is to find an
independent record that describes the same physical property.

## Step 4 — Verify identity

A candidate address is **confirmed** when at least one strong source exposes the exact
address and another source or the listing itself matches enough property attributes.

Compare:

- property type: terrace / semi / detached / bungalow / flat
- bedroom count
- floorplan geometry
- floor area
- front elevation
- position of front door/windows
- side access / end-of-terrace status
- garden shape
- garage/outbuilding
- parking arrangement
- neighbouring buildings
- distinctive internal layout
- tenure
- prior sale or auction timing

A historical listing with old decor but the same floorplan/exterior is especially strong.

## Evidence hierarchy

### Tier A — very strong

- current agent brochure explicitly stating the full address
- auction catalogue/legal pack explicitly stating the full address
- EPC certificate/register entry clearly tied to the property
- planning document clearly tied to the property
- Land Registry title/document where accessible

### Tier B — strong corroboration

- previous agent listing with exact address
- auction results sheet
- sold-price record with matching property
- agent archive page
- council document

### Tier C — supporting only

- property-data aggregators
- Google/search snippets
- postcode directories
- business/local directories
- cached snippets

### Tier D — clues, not proof

- approximate portal map pin
- Street View visual matching alone
- numbering sequence
- neighbouring sale records
- image geolocation
- assumptions based on odd/even numbering

Never present a Tier D inference as an exact address.

## Confidence rules

### Confirmed

Use when:

- a Tier A source states the exact address, and
- the current listing/property details match.

### High confidence

Use when:

- two independent Tier B sources agree, and
- physical details strongly match,
- but no Tier A source is available.

### Probable

Use when:

- there is one plausible source plus strong circumstantial matching,
- but the exact address is not independently verified.

If only probable, say so explicitly. Do not silently upgrade it to fact.

## Handling conflicting evidence

If sources disagree:

1. Prefer first-party/current legal or agent documents over aggregators.
2. Check whether the property has been renumbered, renamed, subdivided, or merged.
3. Check whether a listing is for a rear/side dwelling, annex, cottage, flat, or new-build
   plot sharing a street address.
4. Compare floorplans and external photos.
5. Report the conflict rather than choosing whichever result appears first.

Common traps:

- Rightmove pin is approximate.
- A street can cross postcode boundaries.
- A named house can later acquire a number.
- Auction catalogues occasionally describe a property incorrectly.
- “Semi-detached” vs “end terrace” can change between agents.
- Search engines may conflate neighbouring properties.

## Renovation / flip tracing

When the user suspects a refurbishment or flip, continue after resolving the address.

Search the exact address for:

- previous auction listing
- previous Rightmove/Zoopla/OnTheMarket listing
- auction catalogue and result
- sold-price history
- planning applications
- EPC history
- old floorplans/photos

Capture:

- prior purchase date
- prior purchase price
- auction guide and actual result separately
- previous condition
- obvious scope of works
- relisting date
- initial post-renovation asking price
- subsequent reductions

Do not call an auction guide price a purchase price.

Prefer, in order:

1. published auction result
2. Land Registry completed-sale price
3. agent statement of sold price
4. secondary sold-price database

If the Land Registry record has not yet appeared, state that the auction result is the
best currently available evidence.

## Search tactics when the address stays hidden

Try each of these:

### Agent-property reference

Search the agent's internal reference found in HTML, brochure filename, floorplan, or PDF.

### Description fingerprint

Copy a distinctive 6–12 word phrase from the listing and search it in quotes.
Agents often syndicate the same description to their own site or auction catalogue.

### Image/floorplan fingerprint

Look for the same hero image or floorplan on the agent site, auction site, or old portal
listing. Use this only to locate a record; verify with textual evidence afterward.

### EPC pivot

Use the street/postcode/property type to find an EPC candidate, then verify floor area,
property form, heating, and date.

### Auction pivot

For auction properties search:

- agent name + street
- auctioneer + street
- month/year + auction catalogue
- lot number if known
- legal pack index

Auction PDFs often disclose exact addresses even where portals do not.

### Planning pivot

Search the local planning authority for:

- street name
- distinctive recent works
- extensions
- dropped kerb
- tree work
- conversion

Planning records can expose exact house numbers and site plans.

## Output format

Keep the answer concise but show why the address is trustworthy.

Use:

**Exact address:**  
[full address]

**Confidence:** Confirmed / High / Probable

**Why:**  
A short explanation naming the strongest source and the corroborating match.

If relevant:

**Previous sale / renovation history:**  
- [date] — [price/result and source type]
- [date] — [relisted price]
- brief note distinguishing sale price, auction guide, and asking price

Then mention any discrepancy worth knowing, such as property type, numbering, or postcode.

## Behaviour rules

- Search broadly before concluding the number cannot be found.
- Prefer original documents over SEO property sites.
- Open agent brochures and auction catalogues.
- Verify exact-address claims with property-specific details.
- Never fabricate a house number.
- Never treat an approximate map marker as proof.
- Never confuse asking price, auction guide, reserve, bid, and completed sale price.
- State uncertainty plainly.
- When a user provides a listing URL, work from that listing first rather than asking them
  to restate the street or property details.
