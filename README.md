# SeatCheck Michigan

A single-page app that puts car seat recalls, expiration, Michigan law, and install guidance in one report.

## Run it

One-time setup (installs the Anthropic SDK for the research agent):

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Add your Anthropic API key (from console.anthropic.com/settings/keys): open the `.env` file in this folder,
replace `paste-your-key-here` with the key, and save. The server reads it on start and never serves that file. Then start the app:

```bash
.venv/bin/python server.py
```

Open http://localhost:8766. Without a key, everything works except the research agent.

## Builds and handoff

```bash
python3 tools/build.py
```

| Output | What it is |
|---|---|
| `dist/website/` | The student website (no AI). Upload the folder to Netlify Drop or GitHub Pages. |
| `dist/SeatCheck-Michigan.html` | The same app as one file. Double-click to open; best on laptops. |
| `dist/SeatCheck-Michigan-Instructor-Package.zip` | What you give a trainer: the website, the standalone file, and the full project (AI version + source), with `INSTRUCTOR-GUIDE.md` on top as `START-HERE.md`. Contains an empty `.env` template, never your key. |

Re-run the build after changing `index.html` or refreshing the recall data.

## What it does

| Goal | How |
|---|---|
| Car seat recalls | Searches NHTSA's child-restraint recall records (built into `data/carseat-recalls.js`) by brand, model, model number, and manufacture date. NHTSA's live API doesn't cover car seats, so the app uses NHTSA's bulk recall file instead. |
| Vehicle recalls | Live NHTSA API by year/make/model; VIN decoding via NHTSA vPIC. Flags recalls that involve seats, belts, anchors, or passenger/side airbags. |
| Expiration | Uses the label's "do not use after" date, or manufacture date + useful life. If only the manufacture date is known, it shows the typical 6–10 year window and a manufacturer lookup link. |
| Michigan law | Current Michigan rules (michigan.gov): rear-facing to 2, harness to 5, booster to 4'9" or 8, back seat under 13. Checks the chosen seat type and the seat's weight/height limits against the child. |
| Install guidance | A checklist for each seat type, install method (lower anchors or seat belt), and seating position: front-seat airbag, center seat without anchors, 3rd row, the 65 lb lower-anchor limit, and the top tether. |
| Research agent | `agent.py`: Claude (Opus 5.5) searches the web and reads the manufacturer's site, the car seat manual and the vehicle owner's manual. It returns the expiration rule, the serial-number lookup page, seat limits, lower-anchor and tether locations, center-seat rules and manual install steps, each with a source link. "Use these limits" copies the seat limits into the app's checks. |
| Manuals | Generates searches for the exact car seat manual, install videos for that seat in that vehicle, and the vehicle owner's manual section on LATCH and tethers. |

Children's profiles are saved only in this browser (localStorage).

## Refresh the car seat recall data

NHTSA updates the recall file daily. To pull the latest data:

```bash
python3 tools/update_recalls.py
```

## Limits

- The research agent costs roughly $0.50–$3 per run at Opus 5.5 rates (mostly from reading manual PDFs) and takes 1–3 minutes. It can't fill in manufacturers' serial-number forms, so the serial number isn't sent; it finds the lookup page instead.
- If Opus declines a request, the API automatically retries it on a fallback model (`fallbacks: "default"` in `agent.py`).
- No manufacturer offers a public serial-number API, so expiration-by-serial is a link to the manufacturer, not an automatic lookup.
- Vehicle recall results cover the model. Only a VIN check on nhtsa.gov or checktoprotect.org shows whether a recall is still open on a specific car.
- This tool doesn't replace the car seat manual, the vehicle owner's manual, or a check by a certified CPST.
