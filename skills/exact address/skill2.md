---
name: exact-address
description: >
  Identify the exact postal address and postcode of a UK property from a
  Rightmove or other property-listing URL when the public listing suppresses
  the house number/name. Use a staged evidence-first investigation, escalating
  from cheap text/index searches to structured property records, historical
  listings, PDFs, visual matching, mapping and legal/title evidence. Prefer
  precision over forced answers: return unresolved if the evidence does not
  support a unique property.
---

# Exact Address

## Goal

Given a UK residential property listing URL, identify the property's exact postal
address:

`<flat/unit/house number or name> <street>, <locality/town>, <county if useful>, <full postcode>`

The listing may deliberately display only a street, village, postcode district,
or approximate map pin.

This skill is designed for **very high precision**. A target such as 99.5%
should be interpreted as precision among addresses the skill claims are
confirmed, not as a requirement to invent an answer for 99.5% of listings.
If a unique address cannot be supported, return `UNRESOLVED` with the remaining
candidates and the cheapest next evidence source.

## Core principles

1. **Never infer a house number from the map pin alone.**
   Rightmove and agent coordinates can be approximate or wrong.

2. **Exploit listing fingerprints before doing expensive visual work.**
   Bedroom count, property type, floor area, floorplan geometry, bathroom count,
   EPC rating, tenure, council-tax band, parking, extensions, room dimensions,
   unusual wording, agent, listing date and image filenames often identify a
   historical listing cheaply.

3. **Search for the listing ID and unique text before searching generically.**
   Search engines often index mirrors, old agent pages and PDFs that expose more
   than the current portal page.

4. **Once the full postcode is known, enumerate candidates.**
   Do not keep searching the whole town. Build the finite set of addresses in
   that postcode/street, then eliminate them.

5. **Treat historical listings as fingerprints, not proof by themselves.**
   A previous listing is strong only if the physical property matches.

6. **Prefer direct evidence over inference.**
   An agent brochure saying "10 Oldbury Prior" beats a geometric guess that the
   tenth door from the corner is number 10.

7. **Require independent corroboration before claiming CONFIRMED.**
   The exception is a near-conclusive legal/official document that unambiguously
   belongs to the current listing and is itself cross-linked to the listing.

8. **Do not repeat low-yield searches.**
   Every search should either reveal a new identifier, shrink the candidate set,
   or test a specific candidate.

9. **Use OCR only as a last resort.**
   Native text extraction, search indexing, PDF text, and direct visual reading
   are cheaper and usually more accurate.

10. **Record disconfirming evidence.**
    A candidate with the right postcode but wrong terrace position, floor area,
    layout, extension, or sale history should be explicitly eliminated.

---

# Investigation ladder

Run the following stages in order. Stop as soon as the confidence rule is met.

## Stage 0 — Parse the supplied listing

**Cost: minimal**

Open the listing and extract a compact fingerprint:

- portal and listing/property ID;
- displayed address;
- full postcode if exposed anywhere;
- estate agent and branch;
- asking price;
- added/reduced date;
- property type: detached / semi / end terrace / mid terrace / flat / cottage;
- bedrooms, bathrooms and receptions;
- tenure;
- council-tax band;
- EPC rating;
- floor area;
- room dimensions;
- unusual features;
- parking/garage;
- front/rear/side orientation clues;
- garden form;
- extensions, conservatories, loft conversions, outbuildings;
- service/estate charge;
- wording that looks copied from the agent;
- brochure / EPC / floorplan / legal-document links;
- agent's own property reference if exposed;
- image filenames or media identifiers;
- coordinates, but mark them `APPROXIMATE ONLY`.

Also inspect the page's structured/embedded data if available. Property portals
often retain values in JSON or page metadata that are not prominent in the UI.

### Output of Stage 0

Create an internal record similar to:

```text
listing_id: 93004896
display_address: Oldbury Prior, Calne
postcode: SN11 0AF
agent: Atwell Martin
type: mid-terrace
beds: 2
baths: 1
features:
  - two double bedrooms
  - four-piece bathroom
  - communal front garden
  - enclosed rear garden
  - allocated parking
  - modern kitchen
epc: C
```

Do not begin visual geolocation until this text fingerprint has been exploited.

---

## Stage 1 — Listing-ID and exact-string search

**Cost: very low; usually highest return per token**

Run exact searches in this order:

```text
"<LISTING_ID>"
"rightmove.co.uk/properties/<LISTING_ID>"
"<LISTING_ID>" address
"<LISTING_ID>" postcode
"<LISTING_ID>" "<AGENT>"
```

Then search one or two **distinctive phrases** copied exactly from the
description, ideally 6–14 words:

```text
"<DISTINCTIVE PHRASE>"
"<DISTINCTIVE PHRASE>" "<STREET OR TOWN>"
```

Good phrases are property-specific, such as:

- an unusual bathroom description;
- a boiler age;
- a peculiar garden/parking arrangement;
- unusual room wording;
- a distinctive agent sentence.

Avoid generic phrases such as `"two bedroom terraced house"`.

Search useful filenames if present:

```text
"<IMAGE_FILENAME>"
"<BROCHURE_FILENAME>"
"<AGENT_REFERENCE>"
```

### What Stage 1 often finds

- the agent's own listing;
- Zoopla / OnTheMarket / PrimeLocation or other portal mirrors;
- stale or historical copies;
- search snippets containing a number omitted from the live page;
- a brochure PDF;
- a previous listing with the same photos;
- an auction catalogue;
- a property-history page.

If any result contains an exact address, **do not stop**. Record it as a
candidate and corroborate it.

---

## Stage 2 — Agent page and brochure/document extraction

**Cost: low**

Open the estate agent's own page and all linked documents.

Priority:

1. brochure;
2. particulars / full details;
3. EPC link;
4. floorplan;
5. auction catalogue;
6. legal pack;
7. downloadable sales particulars.

For HTML/PDF text, search for:

```text
address
postcode
property reference
council tax
EPC
tenure
floor area
```

A brochure often contains the exact postal address even when Rightmove hides it.

### PDF rule

Use native PDF text extraction first.

Only render/screenshot the pages likely to contain useful visual evidence:

- cover page;
- front-elevation photo;
- floorplan;
- title/legal-search pages;
- pages containing site plans.

Use OCR only if the PDF is scanned and native text is unavailable.

### Strong evidence

- exact address printed in agent particulars;
- exact address in auction particulars;
- legal-search address;
- title-register address;
- clearly visible door number in a brochure photograph.

---

## Stage 3 — Find the full postcode and enumerate the address universe

**Cost: low**

If the current listing exposes only a street or postcode district, obtain the
**full postcode** before trying to identify the number.

Useful sources:

- Rightmove "nearby sold prices" / house-price pages;
- Royal Mail Postcode Finder;
- GeoPlace FindMyAddress;
- EPC register;
- council-tax valuation list;
- agent page or brochure;
- indexed property-history sites.

Once the full postcode is known, enumerate all plausible addresses in that
postcode/street.

Useful address-enumeration sources:

- Royal Mail Postcode Finder (PAF-backed);
- GeoPlace FindMyAddress (official address + UPRN + map location);
- GOV.UK / VOA Council Tax valuation list;
- EPC register;
- HM Land Registry-derived sold-price lists;
- Rightmove house-price pages;
- reputable property-history mirrors.

### Important

A postcode can include many properties, flats, aliases and building names.
Treat the result as a **candidate set**, not the answer.

For flats, enumerate every flat/unit UPRN where possible.

For rural properties, collect both:
- postal address;
- known aliases / building names.

---

## Stage 4 — Candidate elimination using structured property fingerprints

**Cost: low to medium**

Compare the current listing to each candidate.

The most useful attributes are:

- detached / semi / end terrace / mid terrace / flat;
- bedroom count;
- floor area;
- EPC rating and EPC floor area;
- age band / construction period;
- tenure;
- council-tax band;
- last sale date and price;
- number of storeys;
- extension/conservatory evidence;
- room dimensions;
- parking/garage;
- garden form;
- built form from EPC;
- service/estate charge;
- unusual heating/fuel type.

### Particularly useful sources

#### EPC Register
Search by postcode/street. It can expose:
- full address;
- property type;
- built form;
- total floor area;
- age band;
- heating/fuel;
- EPC rating.

Use EPC attributes to eliminate candidates, not merely to confirm a postcode.

#### Council Tax valuation list
Search by postcode/address. Useful for:
- confirming that an exact postal unit exists;
- distinguishing flats or suffixed numbers;
- council-tax band matching.

#### HM Land Registry / sold-price data
Useful for:
- exact address;
- property type;
- tenure;
- sale dates and prices.

A candidate's sale chronology can be a powerful fingerprint if a historical
listing is known.

#### GeoPlace FindMyAddress / UPRN
Useful for:
- official address spelling;
- house/flat identifiers;
- UPRN;
- precise official location;
- aliases and awkward developments.

UPRN is especially valuable for flats, conversions, new builds and confusing
mews/courtyard addresses.

---

## Stage 5 — Historical-listing reconstruction

**Cost: medium; extremely productive**

For each surviving candidate, search:

```text
"<FULL CANDIDATE ADDRESS>"
"<FULL CANDIDATE ADDRESS>" property
"<FULL CANDIDATE ADDRESS>" "for sale"
"<FULL CANDIDATE ADDRESS>" "<AGENT>"
"<HOUSE NUMBER> <STREET>" "<POSTCODE>"
"<STREET>" "<LAST SOLD PRICE>"
```

Also search the street plus distinctive features:

```text
"<STREET>" "<FLOOR AREA>" 
"<STREET>" "<UNUSUAL FEATURE>"
"<STREET>" "<ROOM DIMENSION>"
```

Look for:

- previous Rightmove listings;
- Zoopla / OnTheMarket / PrimeLocation records;
- agent archives;
- old PDF brochures;
- auction catalogues/results;
- historical image filenames;
- property portals that retained old descriptions.

### Fingerprint matching

A historical listing is likely to be the same dwelling if several of these
match:

- identical floorplan geometry;
- exact room dimensions;
- same windows/doors/stair position;
- same bathroom placement;
- same parking arrangement;
- same communal/private garden arrangement;
- same extension/conservatory;
- same distinctive interior architectural features;
- same external elevation;
- same square footage.

Decor and furniture can change. Structural geometry is much stronger evidence.

---

## Stage 6 — Planning, building-control, conservation and development records

**Cost: medium**

Use the local planning authority when:

- the property has an extension, conservatory, loft conversion or altered access;
- several neighbouring houses have similar layouts;
- it is a conversion/new build;
- the road numbering is unclear;
- a house name may have changed.

Search:

```text
"<STREET>" planning
"<CANDIDATE ADDRESS>" planning
site:<LOCAL-COUNCIL-DOMAIN> "<STREET>"
site:<LOCAL-COUNCIL-DOMAIN> "<CANDIDATE ADDRESS>"
```

Planning systems often expose:

- exact site address;
- plans/elevations;
- plot position;
- applicant documents;
- old/new naming;
- extensions;
- parking/drop-kerb layouts;
- new-build plot-to-postal-number mappings.

Also inspect:

- conservation-area appraisals;
- listed-building records;
- developer plans;
- street naming and numbering documents;
- planning committee reports.

Planning records are particularly effective for odd rural addresses and
developments where the marketing name differs from the postal address.

---

## Stage 7 — Auction and conveyancing evidence

**Cost: medium to high; often near-conclusive**

If the property is or was auctioned, search the auctioneer, iamsold and major
auction aggregators using the street, postcode and old asking/guide price.

Look for:

- auction catalogue;
- lot particulars;
- legal pack;
- title register;
- title plan;
- special conditions of sale;
- TA6 / TA10;
- local-authority search;
- drainage/water search;
- EPC;
- conveyance/transfer;
- lease.

These documents commonly reveal the exact address and title number.

### Confidence

A legal pack that can be tied unambiguously to the current listing is normally
conclusive on the postal identity, subject to checking that the lot has not
been subdivided, renamed or converted since the document date.

---

## Stage 8 — Visual matching

**Cost: high; use only after candidate set is small**

Use listing and historical photos to compare:

- door number/name plaque;
- front elevation;
- number of bays/windows;
- roof shape/chimneys;
- party-wall position;
- brick/stone/render pattern;
- porch;
- meter boxes;
- path/driveway;
- garden walls/fences;
- neighbouring elevations;
- road signs;
- utility poles;
- distinctive trees;
- rear-boundary geometry.

### Preferred order

1. Directly read a visible number/plaque with vision.
2. Compare current photo with candidate's historical photo.
3. Compare photo with street imagery.
4. Use image search/reverse-image-style search if available.
5. OCR a tiny, unreadable plaque only as a final attempt.

Never accept a number merely because it "looks like" a blurred digit.
Use visual evidence to confirm a candidate generated by other evidence.

---

## Stage 9 — Geospatial reconciliation

**Cost: high**

Use maps only after the candidate list is constrained.

Compare:

- listing pin;
- GeoPlace/UPRN location;
- building footprints;
- road geometry;
- plot shape;
- rear access;
- parking courts;
- communal gardens;
- corner/end/mid-terrace position;
- orientation from sun/windows if truly needed.

Possible mapping sources include:

- GeoPlace FindMyAddress;
- Ordnance Survey/open UPRN coordinates;
- council planning maps;
- OpenStreetMap;
- street imagery;
- aerial imagery.

### Critical warning

A Rightmove pin may be approximate or mis-positioned. If an authoritative
address/UPRN and the listing pin disagree, investigate the pin rather than
forcing the address to fit it.

---

## Stage 10 — Special-case public records

**Cost: high / situational**

Use only when the property itself gives a reason.

Examples:

- Companies House registered-office records for a building that has been used
  as a company address;
- licensing/HMO registers;
- business-rates records for mixed-use or former-commercial property;
- local-news/property articles;
- historic maps and conservation records;
- probate/auction notices;
- developer marketing plans.

These are corroborating sources, not an invitation to research the private
occupant. Stay focused on the property identity.

---

## Stage 11 — Paid / authoritative title verification

**Cost: highest monetary cost; use only if still necessary**

For England and Wales, HM Land Registry can provide:

- property summary;
- title register;
- title plan.

Search by address/location.

If the address cannot be found under the expected description, consider that
it may be registered under a different/older address or need an index-map
search.

Use paid title material when:

- two candidate properties remain plausible;
- the user needs legal certainty;
- the listing is a boundary/parcel rather than a normal dwelling;
- a conversion/flat numbering issue cannot be resolved from public records.

Do not buy/search titles indiscriminately for every candidate if cheaper
evidence can narrow the set first.

---

# Confidence model

Use evidence classes, not vibes.

## Class A — Direct / near-conclusive

Examples:
- exact address in current agent brochure;
- exact address in current auction/legal pack;
- title register tied to the listing;
- exact address printed in a document linked directly from the listing;
- clearly legible house number in the listing photo plus matching official
  postcode/address.

## Class B — Strong independent match

Examples:
- previous listing at an exact address with identical floorplan/structural
  photos;
- exact-address EPC with matching floor area, built form and rating;
- exact-address historical listing with matching room dimensions and exterior;
- auction record matching the current property's distinctive physical
  fingerprint.

## Class C — Supporting

Examples:
- matching property type;
- matching council-tax band;
- matching tenure;
- plausible sold-price history;
- map adjacency;
- similar asking price;
- same bedroom count.

Class C evidence is useful for elimination but is rarely sufficient to identify
a house number.

## Suggested score

Use this only as a discipline, not as a substitute for reasoning:

- Class A: +8
- Class B: +5
- strong supporting match: +2
- weak supporting match: +1
- major contradiction: −8
- structural contradiction: reject candidate

### Claim thresholds

**CONFIRMED**
- one Class A item + one independent corroborating item; or
- two independent Class B items plus supporting evidence;
- no unresolved structural contradiction.

**VERY HIGH CONFIDENCE**
- score >= 10;
- at least two independent source families;
- no direct Class A source, but one candidate overwhelmingly fits.

**PROBABLE**
- best candidate, but evidence is not strong enough to claim exact identity.

**UNRESOLVED**
- multiple candidates survive or evidence conflicts.

For an automated system targeting ~99.5% precision, only return the exact
address automatically at `CONFIRMED`. Escalate or abstain otherwise.

---

# Independence rules

Two pages copying the same agent feed are **one source family**, not two
independent confirmations.

Examples:

- Rightmove + Zoopla identical agent text = usually one underlying source.
- Agent brochure + portal mirror of that brochure = one source family.
- Agent brochure + EPC register = independent.
- Agent brochure + HM Land Registry = independent.
- Historical agent listing + current listing can be partially independent only
  if the historical material predates and structurally fingerprints the house.
- Three scraped property sites all derived from Land Registry = one underlying
  dataset.

Count the underlying evidence source, not the number of URLs.

---

# Search-query cookbook

Use quoted strings aggressively.

## Listing identity

```text
"<RIGHTMOVE_ID>"
"rightmove.co.uk/properties/<RIGHTMOVE_ID>"
"<RIGHTMOVE_ID>" "<AGENT>"
"<RIGHTMOVE_ID>" brochure
```

## Agent material

```text
"<STREET>" "<AGENT>"
"<STREET>" "<AGENT>" brochure
site:<AGENT_DOMAIN> "<STREET>"
site:<AGENT_DOMAIN> "<STREET>" filetype:pdf
"<AGENT_REFERENCE>"
```

## Distinctive description

```text
"<6-14 WORD DISTINCTIVE PHRASE>"
"<DISTINCTIVE PHRASE>" "<TOWN>"
```

## Candidate address

```text
"<FULL CANDIDATE ADDRESS>"
"<FULL CANDIDATE ADDRESS>" "for sale"
"<FULL CANDIDATE ADDRESS>" EPC
"<FULL CANDIDATE ADDRESS>" planning
"<FULL CANDIDATE ADDRESS>" auction
```

## Image/media identifiers

```text
"<IMAGE_FILENAME>"
"<MEDIA_ID>"
```

## Planning

```text
site:<COUNCIL_DOMAIN> "<STREET>"
site:<COUNCIL_DOMAIN> "<CANDIDATE ADDRESS>"
"<STREET>" "<POSTCODE>" planning
```

## Auction

```text
"<STREET>" auction
"<POSTCODE>" auction
"<STREET>" legal pack
"<CANDIDATE ADDRESS>" iamsold
```

---

# Candidate table

Keep an internal table once there is more than one plausible address.

```text
Candidate | Type | EPC area | Tax | Last sale | Layout/photo | Direct doc | Status
10 ...    | mid  | 62 m²    | C   | match     | strong       | brochure   | KEEP
12 ...    | end  | 70 m²    | C   | mismatch  | mismatch     | none       | REJECT
14 ...    | mid  | 55 m²    | B   | unknown   | weak         | none       | REJECT
```

Do not let the first plausible candidate anchor the investigation.

---

# Special cases

## Flats and converted houses

Prioritise:

1. UPRN;
2. Royal Mail/PAF-form address;
3. Council Tax entry;
4. EPC unit address;
5. lease/title plan;
6. floor level and window orientation.

Do not collapse `Flat 2, 14 High Street` into `14 High Street`.

## New builds

Marketing plot numbers are not postal addresses.

Search:

- developer site plan;
- planning application;
- street naming and numbering;
- GeoPlace/UPRN;
- Royal Mail;
- new-dwelling EPC;
- Land Registry after first registration.

Explicitly map:

`Plot 37 -> 12 Example Close, AB1 2CD`

## Named rural properties

House names may have changed.

Use:

- GeoPlace aliases;
- Royal Mail;
- planning history;
- title register;
- historic sales particulars;
- conservation/listed-building records.

## Mews, courtyards and private roads

The displayed road can differ from the official postal street.

Use UPRN/official-address records and planning/site plans before relying on map
labels.

## Auctions

Go to the legal pack early. It is often cheaper overall than prolonged portal
searching.

## Renovations / flips

Search the current listing fingerprint and previous auction/sale history.
Before/after listings can reveal the exact address and acquisition price.

---

# Worked pattern: Rightmove 93004896

This case illustrates the intended workflow.

1. The current listing supplied:
   `Oldbury Prior, Calne, SN11 0AF`, agent Atwell Martin, two-bedroom
   mid-terrace, four-piece bathroom, allocated parking, communal front garden.

2. Listing-ID and distinctive-feature searches found current mirrors and older
   Oldbury Prior listings.

3. Historical particulars were compared using structural/property fingerprints:
   bedroom count, terrace form, four-piece bathroom, communal garden, parking,
   floor area/layout and photographs.

4. An older brochure/front photograph exposed the house number `10`.

5. The candidate was then cross-checked against address/property-history
   records showing `10 Oldbury Prior, Calne, SN11 0AF` as a terraced/freehold
   property with a compatible sale history.

Result:

`10 Oldbury Prior, Calne, Wiltshire, SN11 0AF`

The important point is that the visible `10` was not used alone: it was tied to
the same physical dwelling and independently corroborated by address/property
records.

---

# Failure handling

If the address is not confirmed:

1. state the full postcode/street if known;
2. list the remaining candidate numbers/names;
3. say which evidence eliminated the others;
4. identify the **single cheapest next step** most likely to resolve it.

Example:

```text
UNRESOLVED

The listing is definitely within SN13 9XX and candidates are 14 and 16 Example
Road. Both match the property type and EPC area. The front-elevation evidence is
insufficient to distinguish them.

Cheapest next step: search the local planning portal for the conservatory shown
in the rear photograph, then compare the approved plan to the floorplan.
```

Never fill the gap with a guessed number.

---

# Final-answer format

Keep the user-facing answer short even if the investigation was long.

```text
**10 Oldbury Prior
Calne
Wiltshire
SN11 0AF**

Confidence: **Confirmed**

Why:
- [direct source] identifies No. 10 / exact address;
- [independent source] confirms the exact postal address;
- the structural fingerprint matches the current listing.
```

If useful, add one sentence about any address alias, misleading map pin, or
plot-vs-postal-number issue.

Do not dump every failed search unless the user asks for the investigation log.

---

# Preferred source hierarchy

When evidence conflicts, generally prefer:

1. current legal/title material tied to the property;
2. GeoPlace / official UPRN and Royal Mail postal identity;
3. current agent brochure/direct agent particulars;
4. EPC / Council Tax / planning records;
5. HM Land Registry transaction/title information;
6. prior agent brochures and historical listings;
7. portal mirrors;
8. reputable property-history aggregators;
9. map pins / automated valuations / modelled property attributes.

This hierarchy is not absolute. A stale title address can coexist with a newer
postal alias, and a current agent can make a typo. Resolve conflicts by tracing
which source actually identifies the physical dwelling.

---

# Efficiency rules

To keep the investigation computationally cheap:

- run 3–5 precise searches in parallel rather than 20 broad ones;
- extract new identifiers from each successful result;
- pivot immediately to exact candidate searches once the postcode is known;
- parse document text before viewing pages as images;
- screenshot only the PDF pages that matter;
- do not use OCR on ordinary listing photos;
- do not inspect every house on a street visually if structured data can
  eliminate most candidates;
- do not use paid Land Registry documents until public evidence has narrowed
  the candidate set;
- stop when the `CONFIRMED` rule is satisfied.

The optimal strategy is a funnel:

`listing -> identifiers -> full postcode -> candidate universe -> structured elimination -> historical fingerprint -> direct evidence -> independent confirmation`

That funnel is both cheaper and more reliable than starting with Street View or
manual house-by-house visual geolocation.
