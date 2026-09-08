// Pandoc Typst template for resume PDFs.
//
// === Knobs you'll probably want to tweak ===
//   font-body     line ~26   primary typeface (and fallback chain)
//   size-body     line ~27   body font size
//   accent        line ~29   the accent color used for name, headings, rules
//   page margins  line ~35   tighten/loosen page edges
//
// === Markdown conventions this template expects ===
//   YAML frontmatter:  name: ...    contact: City · Phone · Email
//   ## Section         → section header (small caps, accent rule underneath)
//   ### Job entry      → "Title | Org, Location | Dates" (3-part pipe-split)
//                        OR plain "Company, Location" (single-string company header)
//   #### Subsection    → small bold subsection within a job entry
//   - bullet           → tight list with breathing room
//
//   **Role** | Dates   → paragraph starting with bold + " | " right-aligns
//                        the part after " | " as muted italic. Use this for
//                        promotion-ladder role lines under a company.

#let font-body  = ("Inter", "Helvetica Neue", "Arial")
#let size-body  = 10pt
#let size-name  = 24pt

#let accent     = rgb("#2c4d8b")  // deep blue — change to taste
#let ink        = rgb("#1f2937")  // body text color (very dark slate, not pure black)
#let muted      = rgb("#5b6470")  // muted grey for secondary info
#let rule-color = rgb("#2c4d8b").lighten(65%)

#set page(
  paper: "us-letter",
  margin: (x: 0.7in, top: 0.5in, bottom: 0.5in),
)

#set text(
  font: font-body,
  size: size-body,
  fill: ink,
)

#set par(leading: 0.65em, justify: false, spacing: 0.85em)

$if(letter)$
// Cover letters are prose, so give paragraphs room to breathe.
#set par(spacing: 1.3em)
$endif$

#set list(indent: 0.9em, body-indent: 0.4em, spacing: 0.65em)

// --- Helpers -----------------------------------------------------------------

#let content-to-string(c) = {
  if type(c) == str { c }
  else if c == none { "" }
  else if type(c) == content {
    if c.has("text") { c.text }
    else if c.has("children") { c.children.map(content-to-string).join("") }
    else if c.has("body") { content-to-string(c.body) }
    else { "" }
  } else { "" }
}

// --- Heading show rules ------------------------------------------------------

// ## Section header
#show heading.where(level: 2): it => {
  block(above: 1.4em, below: 0.65em)[
    #set text(size: 10pt, weight: "semibold", fill: accent, tracking: 0.12em)
    #upper(it.body)
    #v(0.15em)
    #line(length: 100%, stroke: 0.6pt + rule-color)
  ]
}

// ### Job entry — supports "Title | Org, Location | Dates"
// Falls through to a bolder company-name style when there are no pipes,
// which is appropriate for a multi-role entry under one company.
#show heading.where(level: 3): it => {
  let raw = content-to-string(it.body)
  let parts = raw.split("|").map(s => s.trim())
  if parts.len() >= 3 {
    block(above: 1em, below: 0.5em)[
      #set text(size: size-body)
      #text(weight: "bold")[#parts.at(0)] #h(0.4em)
      #text(fill: muted)[· #parts.at(1)]
      #h(1fr)
      #text(style: "italic", fill: muted)[#parts.at(2)]
    ]
  } else if parts.len() == 2 {
    block(above: 1em, below: 0.5em)[
      #set text(size: size-body)
      #text(weight: "bold")[#parts.at(0)]
      #h(1fr)
      #text(style: "italic", fill: muted)[#parts.at(1)]
    ]
  } else {
    // Single-string heading — treat as company/org marker for a multi-role entry.
    block(above: 1.3em, below: 0.55em)[
      #set text(size: 11pt, weight: "bold", fill: accent)
      #it.body
    ]
  }
}

// #### Sub-section within a job entry (e.g. "Accomplishments", "Key Responsibilities")
#show heading.where(level: 4): it => {
  block(above: 1.0em, below: 0.5em)[
    #set text(size: size-body, weight: "semibold", fill: accent, tracking: 0.03em)
    #it.body
  ]
}

// ##### Sub-sub-section (e.g. "Leadership & Function Ownership", "macOS Platform Engineering")
#show heading.where(level: 5): it => {
  block(above: 0.7em, below: 0.25em)[
    #set text(size: size-body, weight: "bold", fill: ink)
    #it.body
  ]
}

// --- Role-line helper -------------------------------------------------------
//
// Called from the generated Typst source after build.sh post-processes
// "**Title** | Dates" markdown paragraphs into `#role-line[Title][Dates]`.
// Bold title on the left, italic muted dates flush right.

#let role-line(title, dates) = block(above: 0.75em, below: 0.65em)[
  #text(weight: "bold")[#title] #h(1fr) #text(style: "italic", fill: muted)[#dates]
]

// --- Entry-heading helpers ---------------------------------------------------
//
// Called from the generated Typst source after build.sh post-processes a
// level-3 "Title | Dates" or "Title | Org, Location | Dates" heading line
// into #entry-heading[...][...] / #entry-heading-3[...][...][...], BEFORE
// Typst ever parses that line as a native heading. Each bracketed argument
// is rich content Typst already parsed itself (from the #foo[...] call
// syntax) -- never round-tripped through content-to-string() -- so spaces
// adjacent to em-dashes/parens/umlauts in the title are never lost (see
// GitHub issue #1). Visual style mirrors the level-3 heading show-rule's
// 2-part and >=3-part branches below.

#let entry-heading(title, dates) = block(above: 1em, below: 0.5em)[
  #set text(size: size-body)
  #text(weight: "bold")[#title]
  #h(1fr)
  #text(style: "italic", fill: muted)[#dates]
]

#let entry-heading-3(title, org-location, dates) = block(above: 1em, below: 0.5em)[
  #set text(size: size-body)
  #text(weight: "bold")[#title] #h(0.4em)
  #text(fill: muted)[· #org-location]
  #h(1fr)
  #text(style: "italic", fill: muted)[#dates]
]

// Subtle links.
#show link: it => text(fill: accent)[#it]

// --- Header (name + contact) — centered -------------------------------------

$if(name)$
#align(center)[
  #text(size: size-name, weight: "semibold", fill: accent, tracking: 0.02em)[$name$]
]
$endif$
$if(contact)$
#v(-0.2em)
#align(center)[
  #text(size: 9.5pt, fill: muted)[$contact$]
]
$endif$
$if(name)$
#v(0.4em)
#line(length: 100%, stroke: 0.6pt + rule-color)
#v(0.1em)
$endif$

// --- Body --------------------------------------------------------------------

$body$
