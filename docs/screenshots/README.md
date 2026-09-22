# Screenshots for WALKTHROUGH.md

Capture these at http://localhost:3000 after `docker compose up --build` with a valid LLM key
(a 1440px-wide window shows the two-column layout):

| File | What to capture |
|---|---|
| `01-home.png` | Letterhead with line status, the suggested-correspondence index, empty case file |
| `02-coverage-citations.png` | Burst-pipe answer with `cites policy passage [1]`, the highlighted passage and the ledger row |
| `03-claim-status.png` | CLM-8821 reply with the APPROVED stamp and its ledger row |
| `04-submit-claim.png` | Submission confirmation with the RECEIVED stamp and claim id |
| `05-validation.png` | The assistant explaining rejected claim details; ledger row marked ✕ |
| `06-injection-refused.png` | The REFUSED stamp on a prompt-injection attempt |
| `07-tests.png` | Terminal output of `pytest -q` |
