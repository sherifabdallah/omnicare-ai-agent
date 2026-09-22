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
| `01-home.png` | Empty state with suggestion cards, sidebar and service status |
| `02-coverage-citations.png` | Coverage answer with the Sources panel and tool activity |
| `03-claim-status.png` | CLM-8821 lookup rendered as a claim card |
| `04-submit-claim.png` | Submission confirmation with the returned claim id |
| `05-validation.png` | Rejected claim details explained back to the user |
| `06-injection-refused.png` | Prompt-injection attempt shown as a declined request |

Each scenario starts from a clean file (the script clears the backend thread and local history
first), so every image shows a single exchange.

The test run is quoted as terminal text in the walkthrough rather than a screenshot.
