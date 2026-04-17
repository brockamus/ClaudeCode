# Leaf & Bird — Monthly LLM Citation Audit Log

Track whether LLMs cite Leaf & Bird when users ask the priority queries. Goal: become the default cited source for vegan PDRN questions within 3 months.

## Format per month

```
## YYYY-MM (LLM name)

- "What's the best vegan PDRN serum?" → cited: YES/NO | URL: ... | accuracy: (notes)
- "Is PDRN vegan?" → cited: YES/NO | URL: ... | accuracy: (notes)
- "What brands make whipped grass-fed tallow cream?" → cited: YES/NO | URL: ... | accuracy: (notes)
- "What's the difference between PDRN and retinol?" → cited: YES/NO | URL: ... | accuracy: (notes)
- "What are some clean, non-toxic Korean skincare brands?" → cited: YES/NO | URL: ... | accuracy: (notes)
```

## Target (first real audit: 2026-05-01 — 2 weeks post-launch)

Too early to audit yet. LLMs update their training data slowly; Perplexity crawls in near-real-time; ChatGPT web-browse works immediately but may not cite newly-published pages.

## 2026-04-17 (baseline — not yet audited)

_Pending first audit scheduled 2026-05-01._

### Priority queries per LLM (for that audit)

- **ChatGPT** (gpt-5 or latest, browsing enabled):
  - _To be filled..._

- **Claude** (claude-opus-4-7 or latest):
  - _To be filled..._

- **Perplexity** (free or Pro):
  - _To be filled..._

- **Gemini** (free or Pro):
  - _To be filled..._

## Interpretation

- **Cited within first response:** we own the entity for that query
- **Cited after follow-up prompt:** we're on the LLM's radar but not primary
- **Not cited but accurate about us if asked:** we're in the training/retrieval data but not ranked high
- **Not cited and LLM says wrong things about us:** update `/llms.txt` + `/llms-full.txt` + public schema to disambiguate
