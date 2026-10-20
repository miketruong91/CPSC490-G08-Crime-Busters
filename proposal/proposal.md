# Project Proposal — Interactive Crime Map and Database

**Department of Computer Science**
**CPSC 490 Undergraduate Seminar in Computer Science — Proposal for Capstone Project**

**Group 〈N〉 — 〈Group Name〉** · Sponsor: 〈RTX-3 / EL-1 / SNX-n / independent〉
Authors: 〈Last, First (GitHub username)〉, 〈…〉
Date: 〈YYYY-MM-DD〉

> **This file is the proposal document, not a README.** Its section numbers,
> titles, and guidance are copied from the course Word template, so it
> converts cleanly for Canvas submission. Write continuous academic prose —
> no task lists, no emoji, no repo jargon.
>
> Each section below opens with the template's own guidance in a quote block.
> **Delete the quote blocks and every 〈bracket〉 before submitting.**
>
> **Getting this into the Word template for Canvas.** The template numbers
> its headings **automatically** (a multilevel list: top-level sections at
> level 1, *Related Work* and *Problem Statements* at level 2). The numbers
> typed below exist so the repo copy is readable and checkable — so when you
> move the text into Word, do not end up with both sets.
>
> The reliable route, and the one most teams should use: **open the course
> template and paste your prose section by section**, leaving Word's own
> numbering to do the numbering. Ten minutes, no surprises.
>
> If you prefer to convert, `pandoc` can do it (install with
> `winget install pandoc`):
>
>     pandoc proposal/proposal.md -o proposal.docx --reference-doc="CPSC 490 Project Proposal Template Fall 2026.docx"
>
> Then in Word: delete the typed `0.` / `1.` / `1.1` prefixes (Word re-adds
> them from the list), and set *Related Work* and *Problem Statements* to the
> template's level-2 heading so they number as 1.1 and 1.2. Check figure
> placement, then submit.
>
> **Formatting requirements — the submitted Word document is graded against
> these, explicitly:**
>
> - **Cover page: use the template's cover page, unchanged in layout.** Fill
>   in only its fields — project title, group number and name, sponsor,
>   authors, date — and keep the template's own placement, fonts and spacing
>   for it. The header block at the top of this file carries the same fields
>   so the paste is a transcription, not a redesign.
> - **Font: Times New Roman, 11-point.** Body text, headings and captions
>   take their size and style from the template's own styles — do not
>   restyle anything by hand.
> - **Line spacing: 1.5.** **Margins: 1.0 inch** on all four sides.
> - **Section format, numbering and indentation must match the Word template
>   exactly** — the multilevel-list numbering, heading levels, and paragraph
>   indentation are the template's, not yours. If your document's §1.1 looks
>   different from the template's §1.1, fix yours.
> - **Length: the Final Project Proposal Paper (due Sun Dec 20) must exceed
>   50 pages** under exactly this formatting — font, spacing and margins are
>   fixed above precisely so page count means the same thing for every team.
>   The Preview paper (due Sun Nov 29) is the same document part-way; it has
>   no minimum, but it is graded on the same formatting.
>
> A paste into the template inherits all of this automatically **if you paste
> as text and let Word's styles apply** (Home → Paste → *Keep Text Only*, or
> apply the template's styles after pasting). A pandoc conversion with
> `--reference-doc` inherits it too — but verify font, spacing and margins
> afterward rather than assuming.
>
> Either way, keep this Markdown copy current — it is what peer review and CI
> can actually read. If your team writes in Word instead, commit the `.docx`
> here as well.

---

## 0. Abstract

Crime happens everywhere, in every community. Access to crime data can help residents stay aware of and understand what's happening in the community. Although the data may be able to be accessed through specific agencies and departments, that data isn’t always shown in a way that’s easy for the public to visualize. The purpose of this project is to create an interactive application that organizes publicly available crime incident data and allows users to search for and view reported incidents of crime within an area. By showing the data through an interactive map, users can gain a better understanding of reported crime activity in their community. This can help users stay more informed about the crime happening in the areas that matter to them.
Our project has three main objectives. The first is to collect publicly available crime data from all possible and credible sources and organize it in a database. The second is to provide users with statistics and other useful information that can help with identifying possible patterns in crime activity. The third is to integrate an interactive map that allows users to explore incidents within a selected area. The expected outcome is a functional application that combines these three goals into one.
This proposal presents the initial design and development plan for our Crime Busters. The project will focus on creating an interactive application that organizes public crime data and makes the information easier for users to explore and understand. The initial goals and objectives will guide the development of key features, including searching, filtering, and viewing reported crime incidents. These goals will also be organized into epics and user stories to guide the team through future development sprints. As the project progresses, the system will be developed and tested incrementally, allowing the team to improve its functionality based on testing, feedback, and project requirements.

## 1. Introduction

Crime data is gathered by law enforcement agencies to document theft, burglary, vandalism, assault, and other reported criminal activity. Some of this information is shared with the public through crime reports, online databases, and other resources. However, crime datasets can contain large numbers of records distributed across different sources. This can make it difficult for users to search the information and understand reported crime activity within a particular area.

The Interactive Crime Map and Database project aims to make crime data easier to discover, filter, and interpret. The proposed system will use selected publicly available crime records and store them in a structured database. Users will be able to view incidents on an interactive map and search or filter the information by location, crime type, date, and time. This will provide a more organized way to explore the selected records.

A central feature of the project is allowing users to select a location and define a custom search radius around it. The system will identify incidents within that radius and provide summaries of crime type, frequency, date, and time. For example, users could examine whether certain reported crime types appear more frequently on particular days or during particular time periods.

The application will combine data organization, geographic searching, filtering, statistical summaries, and crime visualization. Existing applications offer overlapping capabilities, as discussed in Section 1.1. Our project will focus on implementing and testing these functions together for selected public datasets, allowing users to view incidents and summaries for the same area and search criteria.

### 1.1 Related Work

Public crime information is available through municipal applications and broader crime-mapping platforms. We compared Costa Mesa's Police Incidents Viewer, Fullerton's Calls for Service application, and LexisNexis Community Crime Map. The comparison considers their published information, geographic scope, analytical features, and relevance to our planned application.

| Existing approach | What it does | Pros | Cons | Why ours differs |
|---|---|---|---|---|
| Costa Mesa Police Incidents Viewer [1] | Presents police calls for service through geographic layers organized by incident category and recent time periods, including the past 24 hours, 3 days, 7 days, and 14 days. | Official municipal source with geographic information and a structured ArcGIS service. | The documented layers focus on recent Costa Mesa activity; calls include non-crime categories and require careful interpretation. | Our project plans to standardize selected records in a database and connect custom-radius searches with category and time summaries. |
| Fullerton Police Calls for Service [2] | Publishes call records with incident numbers, call descriptions, timestamps, and block-level locations. | Official local source with details useful for examining individual calls. | Calls include non-crime activity, and block-level locations limit geographic precision. | Our project plans to connect selected records with map-based exploration, combined filters, and summaries for a selected area. |
| LexisNexis Community Crime Map [3], [4] | Provides agency-supplied crime information through maps, grids, charts, and analytics, with neighborhood reports and anonymous tips. | Combines geographic and statistical views and receives data directly from law enforcement agencies. | Public information depends on what agencies choose to share; privacy processing limits some location and personal details. | Our project has a narrower scope focused on implementing and testing a documented data-processing workflow, radius searches, filters, and summaries for selected datasets. |

The municipal applications provide local police activity information, while Community Crime Map combines incident mapping with analytical views. This comparison shows that maps and statistics alone do not distinguish our proposal. Our project will focus on connecting data standardization, custom-radius searches, combined filters, and summaries of the same selected incidents in a smaller application. We will evaluate whether these functions return consistent and correct results using documented test datasets.

Calls for service must also be distinguished from confirmed crimes. If a selected source contains both crime-related and other service activity, our data-processing rules will document how those categories are interpreted and included.

### 1.2 Problem Statements

**P1 — Inconsistent data formats:** Publicly available records may use different field names, date and time formats, and incident categories across sources. These differences make records difficult to organize and compare consistently.

**P2 — Difficulty interpreting selected-area activity:** Individual incident records do not directly summarize crime-type frequencies or changes over time within an area selected by the user. Users must perform additional analysis to identify these patterns.

**P3 — Difficulty narrowing records to an area of interest:** Users need to identify records relevant to a chosen location, distance, crime type, date, and time period. Reviewing broader collections of records makes this task more difficult.

| Problem | Addressed by |
|---|---|
| P1 — Inconsistent data formats | Goal 1: Establish a reliable and structured crime data foundation; Objectives 1.1–1.3 |
| P2 — Difficulty interpreting selected-area activity | Goal 2: Identify possible crime patterns; Objectives 2.1–2.2 |
| P3 — Difficulty narrowing records to an area of interest | Goal 3: Integrate an interactive map for exploring incidents within a selected area; Objectives 3.1–3.3 |

## 2. Goals and Objectives

### Goal 1: Establish a reliable and structured crime data foundation for the application.
[[epic:#3]](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/3)

- **Objective 1.1:** Collect publicly available crime records containing crime type, location, date, and time, with the data source and minimum record count to be confirmed after reviewing available datasets.
  [[story:#4]](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/4)

- **Objective 1.2:** Organize collected crime records into a consistent format for crime type, location, date, and time, verifying that each record meets the documented format or is flagged for correction.
  [[story:#5]](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/5)

- **Objective 1.3:** Store standardized crime records in the database and verify that the stored record count and retrieved information match the records loaded.
  [[story:#28]](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/28)

### Goal 2: Identify possible crime patterns.
[[epic:#14]](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/14)

- **Objective 2.1:** Analyze crime incidents within the selected area by crime type, date, and time, verifying that the frequency counts match manually calculated results from a test dataset.
  [[story:#15]](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/15)

- **Objective 2.2:** Provide the total incident count, counts by crime type, and charts summarizing crime activity in the selected area, with displayed values matching the corresponding database query results.
  [[story:#16]](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/16)

### Goal 3: Integrate an interactive map that allows users to explore crime incidents within a selected area.
[[epic:#12]](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/12)

- **Objective 3.1:** Display crime incidents as interactive map markers showing available crime type, date, and time details, with the response-time target and test dataset size to be confirmed after selecting the dataset.
  [[story:#13]](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/13)

- **Objective 3.2:** Allow users to search and filter crime incidents by location, crime type, date range, and time period, verifying that individual and combined filters return the expected records from a test dataset.
  [[story:#21]](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/21)

- **Objective 3.3:** Allow users to select a location and adjust a custom search radius, verifying with known test locations that incidents inside or on the boundary are included and incidents outside the radius are excluded.
  [[story:#22]](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/22)
  
## 3. Proposed Approaches

> Describe your proposed approach to solve the problem, specifying how you
> will achieve the stated goals. List some possible strategies.

〈Your approach — **clear and concise**. State the strategy you chose, the
alternatives you considered, and the reasoning that decided between them.
Think of this as the argument, not the manual: a reader should finish this
section understanding *what* you will do and *why that* rather than the
alternatives.〉

**Keep the details out of this section.** Tooling, platforms, frameworks,
DBMS choices, environment setup, diagrams, and the work breakdown all belong
in §4 (Required Environment, Resources, and Planned Activities). If a
sentence here names a version number, a library, or a configuration, it
probably belongs in §4 — leave a pointer instead ("the implementation stack
is detailed in §4").

〈A few paragraphs, or a short list of candidate strategies with one line of
trade-off each. If it runs past a page, you are writing §4.〉

## 4. Required Environment, Resources, and Planned Activities

> Review the required and available resources and environment to complete
> your project. For example, server, platform, software tools, operating
> systems, DBMS, or any required skills.
>
> Describe the expected activities to achieve the stated goals, e.g.,
> software development process.

〈Your environment, resources, and planned activities.〉

**Diagrams belong in this section.** Include at minimum a high-level
architecture diagram and a system (context) diagram; add the ER/EER model and
a data-flow diagram where they help the reader understand what you are
building and what it depends on. Draw them with any graphical tool
(Lucidchart, draw.io, Miro, Mermaid, ERDPlus, Figma), keep the authoritative
copies in `docs/design/` with both editable source and exported image, and
reference them here.

〈Number every figure, caption it, and point at it from the prose — "Figure 1
shows the three deployment tiers and the trust boundary between them." A
figure the text never mentions is decoration. See `docs/design/DIAGRAMS.md`
for tools, conventions, and the rule that every box and arrow must be
verified against reality.〉

### Specification and design documents

**Every specification and design document the team writes is listed here**
with the objective it serves. This section is the index of the project's
technical detail: §3 holds the argument, §4 holds the documents that make it
buildable. CI gate G9 fails if a document exists in `docs/specs/` or
`docs/design/` that this section does not link.

| Document | Kind | Covers | Issues |
|---|---|---|---|
| 〈docs/specs/account-management.md〉 | specification | 〈account management requirements〉 | 〈#n, #n〉 |
| 〈docs/design/architecture.md〉 | design | 〈system architecture + data model〉 | 〈#n〉 |

〈The scaffold ships `docs/specs/example-spec.md` and
`docs/design/example-design.md` as worked examples — read them, then delete
them once you have your own, and list yours here.〉

〈Replace these rows with your own. Each document names its epic and stories
in its own first lines too (gate G2), so the trail runs both ways.〉

### Planned activities — the work items

The goals and objectives live in §2 as epics and user stories. **This section
links every *other* work item: features, enhancements, bugs, tasks, and
sub-tasks** — the concrete activities that deliver those objectives. CI gate
G8 fails if such an issue exists that this section does not link.

| Issue | Type | Activity | Parent | Owner | Sprint |
|---|---|---|---|---|---|
| 〈#n〉 | 〈task〉 | 〈stand up the prototype login endpoint〉 | 〈#story〉 | 〈owner〉 | 〈Sprint 1〉 |
| 〈#n〉 | 〈feature/enhancement/bug/task/sub-task〉 | 〈…〉 | 〈#story〉 | 〈…〉 | 〈…〉 |

〈Replace these rows with your own, and keep the table current as you file new
issues — with §2 it gives a reader every planned activity in one place, each
traceable to the objective it serves.〉

## 5. Project Outcomes

> Describe the outcomes or deliverables, e.g., final project report, user
> manuals, source code, data or database files, etc.
>
> Note: the deliverables always include the team GitHub repository, which
> must already contain prototype v0 (a thin end-to-end proof-of-concept,
> however small, running when this proposal is submitted). Briefly describe
> what your v0 demonstrates and how to run it.

〈**One or two paragraphs** explaining the project outcome overall — what will
exist when the project is finished, and what it will let someone do. Keep it
prose, not a checklist; name the deliverables inside the paragraphs, and say
briefly what prototype v0 demonstrates today and how to run it.〉

## 6. Project Timeline

> Identifies tasks (project objectives) to be performed, milestones to be
> met, and the estimated number of hours for each task.

〈**This is the plan for CPSC 491 next semester — the implementation timeline,
not this semester's proposal work.** Identify the tasks (your objectives from
§2), the milestones, and the estimated hours for each, in the order they will
be built. State the assumptions it rests on (sponsor availability, data
access, hardware).〉

| Task (objective) | Milestone | Owner | Est. hours | Spring phase |
|---|---|---|---|---|
| 〈…〉 | 〈…〉 | 〈…〉 | 〈…〉 | 〈…〉 |
| 〈…〉 | 〈…〉 | 〈…〉 | 〈…〉 | 〈…〉 |

〈Do **not** put this fall's four proposal sprints here — those live on the
project board and in `docs/sprint-reviews/`. This section answers "how does
the system actually get built next semester?"〉

## 7. AI Usage

> Per the course AI policy (see the syllabus, Use of AI Tools), disclose the
> AI tools used in preparing this proposal and the prototype: which tools,
> for what tasks (e.g., code generation, test writing, debugging,
> diagramming), and approximately what fraction of each artifact was
> AI-assisted.
>
> Reminder: the prose of this proposal must be your own writing. You remain
> fully responsible for the correctness of all AI-assisted work, including
> the prototype code.

〈Your disclosure. Naming the tool is not disclosure — name what it drafted,
what fraction of each artifact was AI-assisted, and how you verified it.〉

## 8. References

- [1] City of Costa Mesa, “PoliceIncidents (MapServer),” ArcGIS REST Services Directory.
https://apps.costamesaca.gov/gis1/rest/services/PoliceIncidents/MapServer
Accessed: October 20, 2026.

- [2] City of Fullerton, “Fullerton Police Calls for Service.”
https://www2.cityoffullerton.com/webdata/apps/cfs/
Accessed: October 20, 2026.

- [3] LexisNexis Risk Solutions, “Community Crime Map.”
https://risk.lexisnexis.com/products/community-crime-map
Accessed: October 20, 2026.

- [4] LexisNexis Risk Solutions, “Crime Analytics and Mapping.”
https://risk.lexisnexis.com/law-enforcement-and-public-safety/crime-analytics-and-mapping
Accessed: October 20, 2026.
