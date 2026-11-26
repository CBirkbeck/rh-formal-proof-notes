# Inside the formal proof: what may be new

Notes on results and arguments found inside the formal Lean proof of the Riemann hypothesis for Dirichlet
L-functions ([the source as published](https://github.com/leanprover-community/riemann-hypothesis/tree/40e56bab026552e089d7afcfeff08d2defb9c005)).

The proof is long, and along the way it proves many things. Some look as if they may be of interest in their own
right. This site lists them in two groups:

- **Results that may be of independent interest**: statements that a comparison with the literature did not find
  in print, or found only in a weaker or different form.
- **Known theorems reached by another route**: places where the proof supplies a standard theorem, or a case of
  one, by an argument that may differ from the published proof.

Each item has a page with the statement as the Lean states it, links to the Lean declarations, a plain-language
account of how the formal proof goes with its key steps, and what the checks found in the literature.

## Who wrote this, and how far to trust it

Every page was written by AI models. A first model (Claude) read the Lean source and compared the statement or
the argument with published work. A second model (GPT Astra) was then asked, independently, whether the claim of
novelty stands and what prior art it knows. Both opinions are shown. Neither is a specialist's judgement:
"not found in the literature" means that a search did not find it, and nothing more. Nothing was compiled; the
pages say how far down each proof was read.

The formal proof belongs to its author. These pages link to it and describe it in other words; they copy none
of it.

## Tell us what you know

This is the point of the site. On each item's page there are three links:

- **This is known**: give the reference.
- **I think this is new**: say what is closest and why this is not it.
- **The summary is wrong**: say what it should say.

Each opens a short form here on GitHub. The pages show how many readers answered each way. You can also
[propose an item](../../issues/new?template=new-item.yml) that is missing.

## Building the pages

`python3 build.py items _site` writes the site into `_site`. An item is one text file in `items/`: header lines
(`id`, `title`, `area`, `list`, the two opinions, and one `lean:` line per linked declaration), then sections
headed `## Statement`, `## What the checks found`, `## How the formal proof goes`, `## Key steps` and so on.
A workflow rebuilds and publishes the site when the items or the issues change.
