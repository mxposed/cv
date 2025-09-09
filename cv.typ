#set page(
  paper: "a4",
  margin: (
    rest: 0.5in
  )
)

#set text(font: "Avenir", size: 10pt)

#show heading: it => {
  let size = 14pt + 1pt * (3 - it.level)
  set text(weight: "regular", font: "Quattrocento", size: size)
  if it.level == 1 or it.level == 3 or it.level == 4 {
    it
  } else {
    grid(
      columns: (5mm, auto, 1fr),
      column-gutter: 1mm,
      align: horizon,
      line(length: 100%, stroke: 0.5pt + gray, start: (0em, 0.2em)),
      it,
      line(length: 100%, stroke: 0.5pt + gray, start: (0em, 0.2em))
    )
  }
}

#show link: it => {
  set text(bottom-edge: "descender")
  box(
    stroke: (bottom: 0.5pt + rgb("#abc6ce")),
    baseline: 3pt
  )[#it]
}

#let updated = {
  set text(size: 9pt)
  [updated #datetime.today().display("[month repr:long] [year]")]
}

#let item(header, details) = {
  set par(spacing: 0.5em)
  header
  block(inset: (left: 6mm), details)
}

#let item-with-date(header, details, date) = {
  box(grid(
    columns: (1fr, auto),
    column-gutter: 3em,
    align: (left, right),
    item(header, details), date
  ))
}

#let paper-n(n) = context {
  let nn = [#text(font: "PT Mono", size: 7pt, fill: gray.darken(50%))[#if n < 10 { [0#n] } else { [#n] }]]
  let width = measure(nn).width
  let gap = 1.5mm
  [#h(-width - gap)#nn#h(gap)]
}

#let show-authors(authors) = context {
  layout(size => {
    let authors-display = authors
    let authors-size = measure(block(width: size.width, eval(authors, mode: "markup")))
    let line-height = measure([A]).height
    let two-line-height = measure([A\ A]).height
    let line-space-height = two-line-height - line-height
    // [#authors-size.height]
    // [#line-space-height]
    // [#two-line-height]
    let num-lines = calc.ceil(authors-size.height / line-space-height)
    if num-lines > 3 {
      let authors-temp = authors.split(", ")
      let approx-authors-per-line = calc.floor(authors-temp.len() / num-lines)
      let total-authors = approx-authors-per-line * 3
      let first-chunk = calc.ceil(total-authors / 2)
      let second-chunk = total-authors - first-chunk
      authors-display = authors-temp.slice(0, first-chunk).join(", ") + ", […], " + authors-temp.slice(-second-chunk).join(", ")
    }
    [#eval(authors-display, mode: "markup")]
  })
}


= Nikolay S. Markov
#link("mailto:nikolai.markov@northwestern.edu") | #link("https://mxposed.github.io")[mxposed.github.io] | #link("https://scholar.google.com/citations?user=-E-79qkAAAAJ&hl=en")[Google Scholar profile] #h(1fr) #updated

== Education

#grid(
  columns: (1fr, auto),
  column-gutter: 1em,
  row-gutter: 1em,
  align: (left, right),
  item(
    [*Ph.D. in Computational Biology*, Northwestern University, Chicago, USA],
    [Driskill Graduate Program in Life Sciences\
    Advisors: Dr. Alexander Misharin, Dr. Rosemary Braun.
    ]
  ), [2022–2025 (expected in December)],
  item(
    [*M.S. in Bioinformatics*, Newcastle University, Newcastle upon Tyne, UK],
    [_With distinction_\
    Advisors: Dr. Jaume Bacardit (Newcastle University),\
    #h(44pt) Dr. Alexander Misharin (Northwestern University).
    ]
  ), [2017–2018]
)
#item-with-date(
  [Undergraduate coursework in Biology, Moscow State University, Moscow, Russia],
  [Genetics major],
  [2003–2006]
)

== Publications
#v(-1.6em)#h(60%)#box(fill: white)[#text(size: 9pt)[#h(1mm) (\*denotes equal contribution) #h(1mm)]]

#show "Markov NS": strong("Markov NS", delta: 500)
#let pubs = json("publications/filtered_publications.json")
#let n_preprints = pubs.at("preprints").len()
#let n_articles = pubs.at("articles").len()

#if n_preprints > 0 {
  [#v(-1em)]
  [==== 1. Preprints #text(size: 10pt, font: "PT Mono", fill: gray.darken(50%))[(#n_preprints)]]
  for pub in pubs.at("preprints") {
    item-with-date(
      [#paper-n(pub.rank)#eval(pub.title, mode: "markup"). #emph[#pub.journal]. #link(pub.url)[#pub.doi]],
      show-authors(pub.authors),
      pub.year
    )
    v(0.2em)
  }
}

==== 2. Peer-reviewed research articles #text(size: 10pt, font: "PT Mono", fill: gray.darken(50%))[(#n_articles)]
#for pub in pubs.at("articles") {
  item-with-date(
    [#paper-n(pub.rank)#eval(pub.title, mode: "markup"). #emph[#strong(pub.journal, delta: 200)] #pub.details. #link(pub.url)[#pub.doi]],
    show-authors(pub.authors),
    pub.year
  )
  v(0.2em)
}
