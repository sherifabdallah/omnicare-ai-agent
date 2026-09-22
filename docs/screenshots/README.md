# Screenshots for WALKTHROUGH.md

These images are **generated, not hand-staged**: `scripts/capture_screenshots.py` drives the
running app with Playwright, sends each scenario through the real chat endpoint and photographs
the result, so they can be regenerated whenever the UI changes.

```bash
docker compose up -d --build          # needs a real LLM key in .env
pip install playwright && playwright install chromium
python scripts/capture_screenshots.py
```

| File | Scenario |
|---|---|
| `01-home.png` | Letterhead with line status, suggested-correspondence index, empty case file |
| `02-coverage-citations.png` | Burst-pipe coverage answer, cited passage highlighted, ledger row |
| `03-claim-status.png` | CLM-8821 lookup with the APPROVED stamp |
| `04-submit-claim.png` | Submission confirmation with the returned claim id |
| `05-validation.png` | Rejected claim details explained back to the user |
| `06-injection-refused.png` | Prompt-injection attempt stamped REFUSED |

Each scenario starts from a clean file (the script clears the backend thread and local history
first), so every image shows a single exchange.

The test run is quoted as terminal text in the walkthrough rather than a screenshot.
