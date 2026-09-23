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
| `07-dark-mode.png` | The claim lookup again in the dark theme |

Each scenario runs in its own browser context with the backend thread reset first, so every
image shows exactly one exchange and cannot inherit the previous scenario's transcript.

The test run is quoted as terminal text in the walkthrough rather than a screenshot.
