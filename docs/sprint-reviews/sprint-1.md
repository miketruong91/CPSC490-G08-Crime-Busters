# Sprint 1 review — Crime Busters (Group 08)

**Team working dates:** October 6–19, 2026 (**confirm with instructor**). **Evidence checked:** October 21, 2026, after the sprint boundary. The repository's original review template listed September 28–October 11; the team should confirm the official dates before submitting this retrospective. This report distinguishes work completed **during** the working dates from the subsequent cleanup completed October 20–21.

> **Evidence and limitations:** Based on the GitHub repository, Sprint 1 milestone, merged PRs, proposal, and CI. Meeting attendance, original story-point commitments, iteration counts, and individual non-GitHub contributions have **not** been verified. Team members must fill those fields from actual records rather than estimates. This is an AI-assisted draft awaiting peer review.

## Progress this sprint — the substance

**Proposal moved during October 6–19:**
- [PR #38](../../pull/38) is referenced below as [PR #38](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/38): Goal 2 objectives added to the proposal, merged October 6.
- [PR #40](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/40): Goal 1 objectives added, merged October 7. This PR documented objectives; it did **not** implement the Goal 1 data workflow.

**Repository setup during October 6–19:**
- [PR #41](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/41): team README merged to `main` on October 7. The later [PR #59](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/59) brought the team README to `develop` on October 21.

**After-boundary remediation (October 20–21, not retroactively counted as completed during October 6–19):**
- [PR #50](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/50): proposal abstract (§0), merged October 19 at 11:14 PM Pacific (October 20 UTC), **after the stated October 19 daytime boundary; exact boundary time requires confirmation**.
- [PR #52](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/52): §2 goals, objectives, and typed links, merged October 20.
- [PR #54](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/54): §1 introduction and related work, merged October 20.
- [PR #57](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/57): §4 resources and planned activities draft, merged October 21. Proposed diagrams and design details still require team verification.
- [PR #59](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/59): team README added to `develop`, merged October 21.
- [PR #55](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/55): selected-area filtering prototype, merged October 20 at 7:29 PM Pacific (October 21 UTC); not claimed as a Sprint 1 deliverable.
- [PR #61](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/61): frequency-analysis prototype, merged October 21; work belongs to a later goal/sprint.

**Prototype moved:** At the original sprint boundary, the available evidence supports proposal/repository progress, **not** a completed end-to-end crime map. Standalone filtering and analysis prototypes were merged afterward and use synthetic test data. No real-data/map/database integration is claimed.

## Velocity

| Metric | Original Sprint 1 boundary (October 19) | Remediation checkpoint (October 21) |
|---|---|---|
| Planned story points | **Unverified** — requires saved initial Sprint Plan | **Not a valid replacement** for original commitment |
| Completed story points | **Unverified** — requires story-level acceptance and original plan | **Not calculated** from task/PR labels |
| Planned stories | **Unverified** | — |
| Completed stories | **Unverified** | — |
| Sprint 1 milestone issue/PR records closed | **Not reconstructed from current board** | **7/7 records closed** in GitHub milestone (includes two PR records; five task issues) |

**Interpretation:** The 7/7 milestone count is a **post-boundary closure snapshot**, not Sprint 1 velocity. The milestone includes [PR #40](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/40) and [PR #59](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/59) as records alongside task issues #42, #49, #51, #53, and #58. Do not add task and PR points together as if they were independent user stories.

## Completed (merged PRs)

| Work item | Owner / PR author | Points | PR | When merged |
|---|---|---|---|---|
| Goal 2 objectives (documentation) | @miketruong91 | Not confirmed as a story-level completion | [#38](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/38) | Oct 6 |
| Goal 1 objectives (documentation) | @alexreyes1-ctrl | Not confirmed as a story-level completion | [#40](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/40) | Oct 7 |
| Team README on `main` | @alexreyes1-ctrl | Task #42 label `sp: 1`; not a user story | [#41](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/41) | Oct 7 |
| Abstract (§0) | @jmbchavez | Task #49 has no `sp:` label in milestone snapshot | [#50](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/50) | Oct 19 late evening Pacific |
| Goals and objectives (§2) | @alexreyes1-ctrl | Task #51 label `sp: 1` | [#52](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/52) | Oct 20 |
| Introduction / related work (§1) | @alexreyes1-ctrl | Task #53 label `sp: 2` | [#54](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/54) | Oct 20 |
| README on `develop` | @alexreyes1-ctrl | Task #58 label `sp: 1` | [#59](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/59) | Oct 21 |
| §4 draft | @miketruong91 | Issue #60 not in Sprint 1 milestone snapshot | [#57](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/57) | Oct 21 |

**Scope note:** This table is a retrospective of Sprint 1-related proposal/repository work, **not** a claim that every listed PR merged during the sprint. PRs merged October 20–21 are explicitly after-boundary remediation.

## Carried over — and why

| Work | Owner | Why not finished at the working sprint boundary | Decision |
|---|---|---|---|
| §0 abstract / task [#49](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/49) | @jmbchavez | Merged late on October 19; exact sprint cutoff time unverified | Count according to professor's actual cutoff |
| §1 introduction / related work [#53](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/53) | @alexreyes1-ctrl | PR #54 merged October 20 | Completed as after-boundary remediation |
| §2 goals / objectives [#51](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/51) | @alexreyes1-ctrl | PR #52 merged October 20 | Completed as after-boundary remediation |
| README in `develop` [#58](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/58) | @alexreyes1-ctrl | Original README PR #41 targeted `main`, not `develop` | Corrected in PR #59 on October 21 |
| §4 draft [#60](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/60) | @miketruong91 | Required proposal section was still scaffold text | Draft merged October 21; diagram/design verification remains |
| Dataset and map integration | Goal 1 / Goal 3 owners | No verified end-to-end integration at this checkpoint | Keep in later sprint tasks; do not mark complete |

## Loop health (docs/aidlc/loop-engineering.md §8)

| Metric | This sprint |
|---|---|
| Iterations to green, average per PR | **Not verified**; requires historical CI/PR run counts |
| Harness rules added (rows in harness log) | **Not verified**; team to compare historical commits and `docs/aidlc/harness-log.md` |

**Process observation:** The professor's feedback identified missing proposal sections, issue traceability, sprint assignments, and review evidence. After the feedback, the team filled proposal sections and corrected links. These are documented improvements, but do not prove that original sprint execution met the requirements.

## Prototype increment

During the original working sprint, the repository recorded proposal objectives and README progress. Following the boundary, the team merged:
- `prototype/area_filter.py` with synthetic-data tests (PR #55).
- `prototype/crime_frequency.py` with synthetic-data tests (PR #61).

At the October 21 checkpoint, GitHub Actions on the then-current `develop` commit `126f04f5276cfd1f8a99467c8e9478738b691662` reported **Repository harness: success** and **Prototype build & tests: success**. The PR-only description check was **skipped** on the `develop` push. This does not establish full application integration.

## Feedback we received, and what we did about it

| Feedback (source) | Response / evidence | Issue / PR |
|---|---|---|
| Instructor: Sprint 1 execution and issue chain were weak; proposal §2 and §4 needed work | §2 updated and typed links added; §4 draft added later | [#51](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/51), [PR #52](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/52), [PR #57](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/57) |
| Instructor: incomplete introduction / related work | Expanded §1 and cited related public-data products | [#53](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/53), [PR #54](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/54) |
| Instructor: issues need typed links and proper sprint/owner traceability | Typed issue links added to proposal; team reorganized project board (board assignments still require manual verification) | [PR #52](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/52), [PR #57](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/57) |
| Review workflow requires independent approvals | Reviewed PRs show approval events; verify individual review depth in PR conversations | [PR #52](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/52), [PR #54](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/54), [PR #57](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/pull/57) |

## Contribution snapshot

Repository-authored PRs provide only **partial** evidence of team contributions. Meeting attendance and non-GitHub work are unknown; do not infer zeros. This table is not an individual grade.

| Member | Meetings attended | Merged PRs identified in this retrospective | Issues closed | Reviews given |
|---|---|---|---|---|
| @alexreyes1-ctrl | **To verify** | #40, #41, #52, #54, #59 | **To verify** | **To verify** |
| @miketruong91 | **To verify** | #38, #55, #57, #61 | **To verify** | **To verify** |
| @jmbchavez | **To verify** | #50 | **To verify** | **To verify** |
| Adonay (confirm GitHub handle) | **To verify** | No authored PR confirmed in this selected set | **To verify** | **To verify** |

**Important:** The merged PR list spans October 6–21, not just Sprint 1. It excludes any work not identified in the selected evidence. Confirm review identities and participation with the team before submission.

## What we change next sprint

- Define and save the sprint's committed stories and story points **at the sprint start**; do not reconstruct commitment from later edits.
- Assign each issue to an owner and milestone; keep project board status and GitHub issue state synchronized.
- Use the required issue → implementation PR → independent review → merge workflow, including issue-closing references and complete AI-use disclosure.
- Record actual test commands/results, review evidence, and CI iterations as work happens.
- Finish missing proposal design diagrams and validate source-data assumptions before claiming integration.

## Final verification before submission

- [ ] Confirm official Sprint 1 start/end dates and whether late October 19 work counts.
- [ ] Team supplies real planned/completed **story** points from a preserved Sprint 1 plan.
- [ ] Team supplies attendance, review counts, and CI-loop metrics from records.
- [ ] Team checks author/reviewer contributions and corrects any omissions.
- [ ] Verify proposal §4's remaining design artifacts and professor's latest instructions.
- [ ] Teammate independently reviews this report and the associated PR.
