# Claimaro — Investor Deck Intake Questions

**Purpose:** answer these and the answers become the pre-seed deck. This is the input document; `claimaro-pitch-deck-outline.md` (Drive, Apr 29) is the output format. Every question below maps to a slide or an appendix item in that outline.

**How to use it:** answer by number, in whatever order. Short answers are fine — a number and a source beats a paragraph. Mark anything you don't know as `UNKNOWN` rather than guessing; a known gap is workable, a wrong number in a deck is not.

**Owners:** 🅑 = Brock, 🅕 = Frankie, 🅑🅕 = both should agree before it goes in.

---

## 0. Blockers — answer these first

These four gate everything else. The deck's valuation, and whether it's worth sending at all, turn on them.

1. 🅑🅕 **How many signed LOIs do we have today?** Not "interested," not "in conversation" — countersigned. Name each one, its member count, and the date signed. (The LOI template exists in Drive; this asks what came back.)
2. 🅑🅕 **If the answer to #1 is zero:** who are the top 5 prospects, what stage is each at, and what is the realistic date the first signature lands? The outline is blunt that three signed LOIs roughly doubles the valuation — if they're 60 days out, the raise probably should be too.
3. 🅑🅕 **Is MASRM a customer, a design partner, a pilot, or our own entity?** The GitHub org is `MASRM/claims-admin` and there's a MASRM doc in Drive, but the relationship is undefined in every investor-facing artifact. Investors will ask on the traction slide, and "it's complicated" is a bad answer live.
4. 🅑 **How much runway do we have right now, and what's the monthly burn?** Determines whether this is a $750K raise or a $1.5M raise, and whether we can afford to wait for LOIs.

---

## 1. Cover, identity, round

5. 🅑🅕 Which tagline are we using? Outline offers three: *"The operating system for healthshares"* / *"Modern claims infrastructure for share-based healthcare"* / *"Healthshare administration, finally built for 2026."*
6. 🅑🅕 Do we pitch as **Claimaro** or **NEXOPIC, INC.**? The SLA names NEXOPIC as licensor and Claimaro as the product. Investors need to know what entity they're buying into on slide 1, not in diligence.
7. 🅑 Founder titles as they should appear — CEO / CTO / co-founder?
8. 🅑🅕 Round label: "Pre-Seed — Q3 2026" or Q4? What's the target first-close date?
9. 🅑 Do we have a logo file and brand colors in a usable format, or does the deck need those built first?

## 2. Problem

10. 🅕 **How many healthshare operators have we actually talked to?** The outline has `[N]` and that number is the credibility of the entire problem slide.
11. 🅕 What are the three most quotable things an operator said about their current tooling? Verbatim, attributed by role if not by name ("ops director at a 40K-member ministry").
12. 🅕 **Where does the 60–120 day reimbursement figure come from?** Do we have a citable source, or is it operator anecdote? If anecdote, say so on the slide — an unsourced stat that a VC's associate can't verify is worse than a sourced smaller claim.
13. 🅕 What does a mid-size healthshare currently spend on admin labor — headcount and dollars? This is the number that makes the ROI case.
14. 🅑🅕 Which specific incumbent tools have we seen in the wild? The outline names Aptarro and NextGen; the competitive analysis names ShareBox, MPB Group, Paragon. Which have we actually confirmed in a real operator's stack?

## 3. Solution & product

15. 🅑 Which modules are **live in production today** vs. built-but-dark vs. roadmap? List them one by one. The outline's solution slide lists seven capability areas and the deck must not imply all seven are shipped if they aren't.
16. 🅑 Is there a live tenant with real members and real claims flowing? How many of each?
17. 🅑 **Is there AI in the product today, and what does it actually do?** The outline explicitly warns against AI-washing on the "Why Now" slide. If AI-assisted adjudication is real, we lead with it; if it's roadmap, it comes out of the slide.
18. 🅑 Which four screenshots do we show? Outline says four, not twelve. Candidates: dashboard, claims review queue, enrollment flow, fee schedules, agency panel.
19. 🅑 Do we have a 60-second demo video, or does one need recording? (It's on the pre-pitch checklist.)
20. 🅑 What's genuinely hard to copy here — where would a competent competitor need 12+ months? Adjudication logic for the share model? The multi-tenant/per-tenant-DB architecture? Something else? This is the defensibility answer and it comes up in every first meeting.

## 4. Market

21. 🅑🅕 **We have two contradictory market sizings and must pick one.** The deck outline says $270–540M TAM at $15–30 PMPM. The April competitive analysis says $18–48M/year TAM at $1.00–2.50 PMPM. That's a 10x spread on the same market. Which is right, and what's the defensible bridge between them?
22. 🅑🅕 Member count: outline says ~1.5M, competitive analysis says 1.5–2M. What number do we stand behind and what's the source?
23. 🅕 Is the ~30% YoY growth claim sourced or estimated? The competitive analysis says the market "stabilized post-ACA mandate repeal," which directly contradicts it. One of these is wrong and an investor who reads both will catch it.
24. 🅕 Org count: outline says 100+, competitive analysis says 80–120. Source?
25. 🅑🅕 Which adjacent market is the real expansion story — DPC, self-funded employer plans, or captive insurance? Pick one to make concrete; listing three reads as "we haven't decided."

## 5. Business model & pricing

26. 🅑🅕 **Which pricing is current?** Three live versions exist: the April competitive analysis ($499–$2,499/mo + $1.00–1.50 PMPM), Frankie's sheet's "New Proposed pricing" ($3,500–$95,000/mo + $0.75–5.00 PMPM), and the deck outline ($10–25 PMPM). These are not reconcilable and the deck needs exactly one.
27. 🅑🅕 What have we actually quoted to a real prospect, in writing? That's the number to build the model on, whatever the spreadsheets say.
28. 🅑 Confirm COGS. Frankie's sheet has $1,079/month total (Vercel $390, Supabase $599, SendGrid $90) — but that looks like platform-wide cost, not per-customer, and per-tenant Supabase projects mean it scales with customers. What's the real marginal cost of one more tenant?
29. 🅑 What's the "Partner 20%" line in the pricing sheet — channel commission, revenue share, referral fee? It's 20% of gross and investors will ask what it buys.
30. 🅑🅕 Is the white-label agency model (the differentiator called out in the competitive analysis as unique in this market) in the pitch, or are we going direct-to-healthshare only? It's the strongest wedge in that document and it appears nowhere in the deck outline.
31. 🅑 Are implementation fees recognized up front or amortized? Affects how ARR is presented.
32. 🅑🅕 Contract length we're actually signing — 12, 24, or 36 months?

## 6. Traction

33. 🅑 Date the platform went live.
34. 🅑🅕 Combined member count across all LOI/pilot customers.
35. 🅑🅕 Combined ARR potential of that pipeline, using the pricing settled in #26.
36. 🅑🅕 Pilot or first-paid go-live date.
37. 🅕 Any signed advisors from Liberty, Zion, Sedera, CHM, Samaritan, or similar? Names and what they've agreed to.
38. 🅑 Any revenue at all today — pilots, consulting, adjacent work?
39. 🅕 Do we have three operators willing to take an investor reference call? Named. (Pre-pitch checklist item; usually the last thing that gets done and the first thing a serious investor asks for.)

## 7. Competition

40. 🅑🅕 Has anyone demoed ShareBox or gotten a real quote from them? They're the only true head-to-head competitor and everything we've written about their pricing is estimated.
41. 🅑 Have we lost a deal to anyone yet? To whom, and why? A real loss story is more credible than a clean 2x2.
42. 🅑🅕 The competitive analysis positions us as the low-cost option ($1.00–1.50 PMPM vs. ShareBox's estimated $3–8). The deck outline positions us at $10–25 PMPM as premium. **Which are we?** This is the same contradiction as #26 and it changes the whole competition slide.
43. 🅑 What stops a large healthshare (Medi-Share, CHM) from just building this internally? They have the budget. What's the honest answer?

## 8. Team

44. 🅕 **Frankie's background — the outline leaves it entirely blank.** Healthshare, healthcare, insurance, or operational experience: what specifically, where, how long, and what does it let us do that a generic team couldn't?
45. 🅑 Brock's one-line credibility statement. Draft has "agency operator, automation/CRM, Atlas project" — what are the concrete client examples we can name publicly?
46. 🅑🅕 What's the founder-market-fit story in one sentence? Why us and not two other engineers?
47. 🅑🅕 Equity split, and is it vesting on a standard 4-year/1-year-cliff schedule? Investors check this before they check the product.
48. 🅑🅕 Is anyone full-time? If not, when does that change, and does this round fund it?
49. 🅑🅕 Any advisors already committed? Name + one line each.

## 9. The ask

50. 🅑🅕 Round size — the outline suggests $750K–1.5M. What number, and what does it buy that a smaller one doesn't?
51. 🅑🅕 Valuation cap. Outline suggests $6–12M for pre-seed healthtech with LOIs. Where do we sit, given the honest answer to #1?
52. 🅑 Post-money SAFE confirmed, or is a priced round on the table?
53. 🅑🅕 Use of funds across the four buckets — engineering, GTM, compliance/legal, runway. Rough percentages.
54. 🅑 What milestones does this round hit? Outline proposes 3–5 paid customers, $30K MRR, Series A readiness. Realistic given the actual pipeline?
55. 🅑 Has any money gone in already — founder capital, friends and family, notes? How much, on what terms?
56. 🅑🅕 Is anyone soft-committed today?

## 10. Vision

57. 🅑🅕 Which closing framing — "every healthshare in America runs on Claimaro" or "healthshare is what fintech was in 2013, waiting for its Plaid"? Or something of our own.
58. 🅑🅕 What's the five-year number we're claiming, and is it consistent with the market sizing in #21?

## 11. Appendix / diligence

59. 🅑 Does an 18-month financial model exist in a form we can send? (Frankie's sheet has tier math, not a model — no hiring plan, no burn, no ramp.)
60. 🅑 Cap table — current and post-round. Formation docs clean? Delaware C-corp per the SLA, but is the cap table papered?
61. 🅑🅕 State-by-state healthshare regulatory map — do we have one, or does it need building? It's appendix A2 and it's the question a healthtech investor asks that a generalist doesn't.
62. 🅑 **HIPAA/compliance status for the data room.** The Aug 22 pack (risk assessment, incident response, security officer designation, workforce training) covers most of the checklist item — but it's marked DRAFT pending signature, and the risk assessment flags unsigned BAAs with Vercel, Supabase, and Mailgun as risk R-1 (residual: High). Are those signed now? An investor doing real diligence will find R-1.
63. 🅑 SOC 2 — started, planned, or not on the roadmap? What do we say when asked?
64. 🅑 What's the honest risks-and-mitigations slide (appendix A8)? Suggested candidates: regulatory change to healthshare status, customer concentration, the Aliera-style collapse risk in the category, two-person team. What else keeps us up at night?
65. 🅑 Is the data room built (Notion or DocSend), and who owns assembling it?

---

## Already answered — confirm rather than re-derive

These come out of existing docs. Read and correct; don't re-answer from scratch.

| Topic | What we have | Source |
| --- | --- | --- |
| Product scope | 7 module areas: enrollment, claims, payments, member services, CRM/marketing, implementation | LOI template §1 |
| Legal entity | NEXOPIC, INC., Delaware C-corp, Massillon OH | SLA |
| Security controls | 13 verified controls: per-tenant DB isolation, TOTP MFA, PII masking with audited reveals, 6-year audit archival, anomaly detection | Risk assessment §2 |
| Infrastructure | Vercel + Supabase (per-tenant projects, AWS us-east-2), Mailgun, Stripe/NMI/Authorize.net | Risk assessment §1 |
| Known security gaps | 7+ risks; R-1 unsigned BAAs and R-2 credential-stuffing exposure are the two an investor would care about | Risk assessment §3 |
| Competitor list | ShareBox, MPB Group, Paragon (direct); HealthEdge, QNXT, Javelina, Plexis, VBA (adjacent) | Competitive analysis §2 |
| Target VC list | Rock Health, Flare Capital seed, BoxGroup, Bling Capital + `Potential VCs` doc | Deck outline; Drive |

## Contradictions to resolve before anything is sent

Four numbers appear in more than one place with more than one value. Each needs a single answer.

1. **PMPM pricing** — $1.00–1.50 (competitive analysis) vs. $0.75–5.00 (pricing sheet) vs. $10–25 (deck outline). → Q26, Q42
2. **TAM** — $18–48M (competitive analysis) vs. $270–540M (deck outline). → Q21
3. **Market growth** — "~30% YoY since 2019" (deck outline) vs. "stabilized post-ACA mandate repeal" (competitive analysis). → Q23
4. **Major ministry member counts** — Liberty at ~100K (deck outline) vs. ~200K (competitive analysis); Medi-Share ~350K vs. ~400K. → Q22

A VC associate doing 30 minutes of work will find these. Better we do.
