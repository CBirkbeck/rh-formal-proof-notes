# Inside the formal proof: what may be new

Notes on results and arguments found inside the formal Lean proof of the Riemann hypothesis for Dirichlet
L-functions ([the source as published](https://github.com/leanprover-community/riemann-hypothesis/tree/40e56bab026552e089d7afcfeff08d2defb9c005)).
The site is at <https://cbirkbeck.github.io/rh-formal-proof-notes/>.

The proof is long, and along the way it proves many things that may be of interest in their own right. We have
collected some of them in two lists:

- **Results that may be of independent interest**: statements that we did not find in the literature, or found
  only in a weaker or different form.
- **Known theorems reached by another route**: places where the proof reaches a standard theorem, or a case of
  one, by an argument that may differ from the published proof.

Each item has a page with the statement as the Lean has it, links to the Lean declarations, a sketch of the
argument with its key steps, and a comparison with the literature as far as we could make one.

## How far to trust this

These notes were drafted with AI models and have not been refereed. Claude read the Lean source and compared each
statement or argument with published work; GPT Astra was then asked, independently, whether the comparison stands.
Each page was afterwards read again against the Lean source, and every citation was compared with its publisher
or arXiv record.

Where a page says that we did not find something in the literature, that is all it means. Nothing was compiled,
and each page says how much of the Lean source we read and what we did not check. In several places the Lean
statement is narrower than one might expect, or is an implication from named hypotheses; the pages say so.

The formal proof belongs to its author. We link to it and describe it in our own words, and copy none of it. The
"Show the Lean statement" toggles fetch a few lines from the proof's repository in your browser.

## Tell us what you know

This is the point of the site. Each page has three links:

- **This is known**: give the reference.
- **I think this is new**: say what is closest and why this is not it.
- **The summary is wrong**: say what it should say.

Each opens a short form here on GitHub, and the pages show how many readers answered each way. You can also
[propose an item](../../issues/new?template=new-item.yml) that is missing.

## Building the pages

`python3 build.py items _site` writes the site into `_site`. An item is one text file in `items/`: header lines
(`id`, `title`, `area`, `list`, `status`, optionally `second`, and one `lean:` line per linked declaration), then
the sections `Statement`, `Context`, `Comparison with the literature`, `References`, `Sketch of the proof`,
`Key steps` and `Caveats`. A workflow rebuilds and publishes the site when the items or the issues change.
