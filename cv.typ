#set page(
  paper: "a4",
  margin: (
    bottom: 0.75in,
    rest: 0.5in
  ),
  footer: context {
    set text(size: 8pt, fill: gray.darken(50%))
    h(1fr)
    if counter(page).get().first() > 1 [Markov CV page #counter(page).display("1 of 1", both: true)]
    else [page #counter(page).display("1 of 1", both: true)]
  }
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
  // set text(bottom-edge: "descender")
  box(underline(stroke: 0.5pt + rgb("#abc6ce"), offset: 3pt)[#it])
}

#let updated = {
  set text(size: 9pt)
  [updated #datetime.today().display("[month repr:long] [year]")]
}

#let item(header, details, inset: 6mm) = {
  set par(spacing: 0.65em)
  header
  block(inset: (left: inset), details)
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
  [#metadata(none)#label("paper" + str(n))#h(-width - gap)#nn#h(gap)]
}

#let show-authors(authors) = context {
  layout(size => {
    let authors-display = authors.split(", ").map(x => "#box[" + x + "]").join(", ")
    let authors-size = measure(block(width: size.width, eval(authors-display, mode: "markup")))
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
      let pos = authors-temp.position((x) => x.starts-with("Markov NS"))
      if pos != none {
        let first-chunk = calc.ceil(total-authors / 2)
        let second-chunk = total-authors - first-chunk - 2
        if pos < total-authors - 2 and pos > first-chunk - 1 {
          first-chunk = pos + 1
          second-chunk = total-authors - first-chunk
        }
        if authors-temp.len() - pos <= total-authors - 2 and authors-temp.len() - pos >= first-chunk - 1 {
          second-chunk = authors-temp.len() - pos + 1
          first-chunk = total-authors - second-chunk
        }
        if pos > total-authors - 2 and authors-temp.len() - pos > total-authors - 2 {
          let first-chunk = calc.floor(total-authors / 3) - 1
          let second-chunk = first-chunk
          let third-chunk = total-authors - first-chunk - second-chunk
          let second-begin = calc.floor(pos - second-chunk / 2)
          let first-skipped = second-begin - first-chunk
          let second-skipped = authors-temp.len() - (second-begin + second-chunk) - third-chunk
          authors-display = (
            authors-temp.map(x => "#box[" + x + "]").slice(0, first-chunk).join(", ")
            + ", #box[#emph[#text(gray.darken(50%))[\[…" + str(first-skipped) + " more…\]]]], "
            + authors-temp.map(x => "#box[" + x + "]").slice(second-begin, count: second-chunk).join(", ")
            + ", #box[#emph[#text(gray.darken(50%))[\[…" + str(second-skipped) + " more…\]]]], "
            + authors-temp.map(x => "#box[" + x + "]").slice(-third-chunk).join(", ")
          )
        } else {
          let skipped = authors-temp.len() - first-chunk - second-chunk
          authors-display = (
            authors-temp.map(x => "#box[" + x + "]").slice(0, first-chunk).join(", ")
            + ", #box[#emph[#text(gray.darken(50%))[\[…" + str(skipped) + " more…\]]]], "
            + authors-temp.map(x => "#box[" + x + "]").slice(-second-chunk).join(", ")
          )
        }
      }
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

== Invited talks

#grid(
  columns: (1fr, auto),
  column-gutter: 1em,
  row-gutter: 1em,
  align: (left, right),
  item(
    [Distinct pathogen-specific host responses in patients with severe pneumonia.],
    [Systems Biology Consortium for Infectious Diseases Lecture Series.]
  ), [March 2025],
  item(
    [Host response in severe pneumonia is pathogen-specific.],
    [Systems Biology for Infectious Diseases Annual Meeting.]
  ), [September 2024],
  item(
    [Cellular and molecular biomarkers of successful responses to therapy in severe pneumonia, including COVID-19.],
    [CZI Single-Cell Biology 2022 Annual meeting. #link("https://fast.wistia.com/embed/channel/n9ne6nikz4?wchannelid=n9ne6nikz4&wmediaid=x46zqa026r")[Recording]]
  ), [November 2022],
  item(
    [Circuits between infected macrophages and T cells in SARS-CoV-2 pneumonia.],
    [American Thoracic Society Allergy, Immunology and Inflammation (AII) assembly journal club. #link("https://www.thoracic.org/members/assemblies/assemblies/aii/journal-club/circuits-between-infected-macrophages-and-t-cells-in-sars-cov-2-pneumonia.php")[Recording]]
  ), [June 2021]
)

== Awards and grants

#grid(
  columns: (1fr, auto),
  column-gutter: 1em,
  row-gutter: 1em,
  align: (left, right),
  item(
    [Driskill Research Award],
    []
  ), [2025],
  item(
    [American Heart Association Predoctoral Fellowship],
    [Machine learning approaches to predict outcomes and complications in ICU patients. 24PRE1196998 (\$67000)]
  ), [2024–2026],
  item(
    [Northwestern Institute on Complex Systems Data Science Fellow (\$12500)],
    []
  ), [2022]
)

== Work experience

#grid(
  columns: (1fr, auto),
  column-gutter: 1em,
  row-gutter: 1em,
  align: (left, right),
  item(
    [*Ph.D. researcher*, Division of Pulmonary and Critical Care Medicine,\
    Feinberg School of Medicine, Northwestern University, Chicago, USA],
    [- Led 4 large collaborative projects with 500+ patients and multimodal data to publication
    - Acquired external funding for my training (AHA predoctoral fellowship)
    - Authored and co-authored 18, including 4 first/co-first, publications or preprints
    - Led analysis of scRNAseq patient samples in the context of their clinical course with novel machine learning approach (clustering of patient-day representations and late fusion)
    - Identified cell population as a biomarker and potential therapeutic target of ILD in SSc (#link(label("paper26"))[Markov et al., #emph[bioRxiv], 2025])
    - Consulted 7 Northwestern grad students, postdocs and faculty on deep learning, data science and data visualization, including setting up and training in paw tracking on videos for mouse experiments],
    inset: 2.4mm
  ), [2022–present],
  item(
    [*Research data analyst, bioinformatics*, Division of Pulmonary and Critical Care Medicine,\
Feinberg School of Medicine, Northwestern University, Chicago, USA],
    [- Created data processing pipelines, data exploration and management infrastructure for the division
    - Delivered analytical insights from scRNAseq and other data to principal investigators for 7 publications
    - Formulated activated T cell#[#sym.arrow.l.r]macrophage circuit in #link(label("paper4"))[#emph[Nature] 2021], which supported successful clinical trials of Auxora in COVID-19 (NCT04345614)
    - Supported grant writing for U19, R01 and other NIH grants for the division, resulting in \$5M+ funding
    - Hired and trained incoming data analysts to grow the team and replace myself],
    inset: 2.4mm
  ), [2019–2022],
  item(
    [*Head of maintenance tools development group*, Yandex, Moscow, Russia],
    [- Managed a team of 6 engineers: hiring, mentoring, resolving conflicts, improving performance
    - Synthesized internal customers' needs into technical roadmaps for supporting web-services
    - Owned various web-services to improve employees' workflows],
    inset: 2.4mm
  ), [2014–2017],
  item(
    [*Full-stack software engineer*, Yandex, Moscow, Russia],
    [- Automated deploy workflows of system administrators for better consistency and transparency
    - Deployed and maintained various web-services to improve employees' workflows],
    inset: 2.4mm
  ), [2007–2014],
  item(
    [*Software engineer*, Art. Lebedev Studio, Moscow, Russia],
    [- Supported and developed Samsung Russia website, including new features and database management],
    inset: 2.4mm
  ), [2006–2007]
)

== Teaching experience

#grid(
  columns: (1fr, auto),
  column-gutter: 1em,
  row-gutter: 1em,
  align: (left, right),
  item(
    [Biological Science Teaching Assistant, Northwestern University],
    [- Presented weekly lecture recap and experimental objectives
    - Supervized lab sessions for 22 students
    - Graded assignments and provided detailed written feedback],
    inset: 2.4mm
  ), [2024],
  item(
    [Summer Students Program 2022 at Division of Pulmonary and Critical Care Medicine],
    [Co-mentored 1 college student in automated image analysis. Helped develop project goals,
methodology and results interpretation]
  ), [2022],
  item(
    [Summer Students Program 2020 at Division of Pulmonary and Critical Care Medicine],
    [Co-mentored a group of 4 college students on a bioinformatics project. Contributed to project's design,
teaching R programming environment, single-cell RNA-seq experimental technology and analysis]
  ), [2020],
  item(
    [Introduction to Python, Introduction to Pandas and Matplotlib],
    [Small introductory lecture series during Data Science Nights at NICO, Northwestern University]
  ), [2020],
  item(
    [Introduction to Programming, Newcastle University, Newcastle upon Tyne, UK],
    [Unofficial 5-lecture course for fellow students]
  ), [2017],
  item(
    [Introduction to Computer Science with Python 3, Yandex, Moscow, Russia],
    [Logical and mathematical problems with strict proofs for high-school students in python]
  ), [2013],
)

== Miscallaneous

#grid(
  columns: (1fr, auto),
  column-gutter: 1em,
  row-gutter: 1em,
  align: (left, right),
  item(
    [Open Problems for Single-Cell Analysis],
    [Initial jamboree contributor and label projection task leader. #link("https://openproblems.bio")]
  ), [2021–present],
  item(
    [Contributor to open-source software],
    [Seurat, CellBrowser, biopython, funkyheatmap, statannotations, scanpy, CellBender]
  ), [2018–present],
  item(
    [Programming languages],
    [Python, R, Java, C++, Ruby, Perl. Linux. Latex. HTML, JavaScript.\
    Github: #link("https://github.com/mxposed")]
  )
)
