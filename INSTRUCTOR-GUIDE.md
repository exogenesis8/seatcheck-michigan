# SeatCheck Michigan: Instructor Guide

SeatCheck Michigan helps parents and caregivers check a child's car seat in one place:

- Car seat recalls (NHTSA)
- Vehicle recalls (NHTSA)
- Car seat expiration
- Whether the seat fits the child under Michigan law
- Seating position checks
- Step-by-step install checklists

Students use it in a web browser on a phone or laptop. There is nothing to install.

> **Important:** SeatCheck organizes public information from NHTSA and the State of Michigan. It does not replace
> the car seat manual, the vehicle owner's manual, or a hands-on check by a certified Child Passenger Safety
> Technician (CPST). Have a CPST review the install steps and Michigan law wording before using it to teach.

---

## What's in this package

| Folder | What it is | Who uses it |
|---|---|---|
| `Student-Website/` | The app, ready to put online | You upload it once; students open the link |
| `Standalone-File/` | The same app as a single file | Laptops with no website; a backup if the internet is down |
| `Full-Project/` | Everything: source, recall-data updater, and the AI research version | You, for updates and the AI demo |

---

## 1. Put the student app online (one time, about 5 minutes)

Students get one link (or a QR code on your slide) that works on any phone or laptop.

**Easiest: Netlify Drop (free)**

1. Go to **app.netlify.com/drop** and create a free account. Without an account, the site is deleted after a short time.
2. Drag the **`Student-Website`** folder onto the page.
3. Netlify gives you a link like `https://something-random.netlify.app`. You can rename it under **Site configuration → Change site name**, for example `seatcheck-michigan`.
4. Open the link on your phone to confirm it works.
5. Make a QR code for your slides. Any free QR code generator works, or use your phone's Share menu.

**Alternative: GitHub Pages.** Create a repository, upload `Student-Website/index.html`, then turn on
**Settings → Pages**. Use this if your organization already uses GitHub.

**To update the site later,** drag the new `Student-Website` folder onto your site's **Deploys** page in Netlify.

---

## 2. No website? Use the standalone file

Copy `Standalone-File/SeatCheck-Michigan.html` to each laptop, or email or AirDrop it. Double-click it to open it in a browser.

- **Works on:** Mac, Windows and Chromebook laptops.
- **Not reliable on phones.** iPhones and most Android phones won't run a downloaded web page. For phones, use the website.
- **Needs internet only for** vehicle recalls and VIN lookups. Everything else works offline.

---

## 3. Running a class

**Suggested flow.** Each student or group works through the four steps on the left side of the screen. The safety report on the right updates as they type.

1. **Child.** Enter age (or birth date), weight and height.
2. **Car seat.** Enter the type, brand, model, model number and manufacture date from the seat's label. Press **Check car seat recalls**.
3. **Vehicle.** Enter the VIN, or the year, make and model. Choose the seating position and install method. Press **Check vehicle recalls**.
4. **Safety report.** Read it together. Red items are problems to fix, yellow items need checking, and green items are OK.

**Practice cases to try in class:**

| Case | Enter | What the report should show |
|---|---|---|
| Infant, recalled seat | 8 months, 18 lb, 27 in; infant seat with base; Britax B-Safe Gen 2, made May 2022; 2019 Honda CR-V, 2nd row center, lower anchors, "No" lower anchors at this spot | Recall 26C006000 (handle screw), no lower anchors in the center, and 2019 CR-V recalls |
| Toddler turned too early | 1 year 6 months, 24 lb, 32 in; forward-facing harness; front passenger seat | Too young to forward-face; children under 13 ride in back; attach the top tether |
| Booster too soon | 4 years, 38 lb, 40 in; high-back booster | Under 5 must use a harness seat |
| Big kid | 9 years, 70 lb, 54 in; backless booster, 2nd row | Booster OK, the 5-step seat belt test, and the head restraint rule |

**Privacy.** The app stores nothing online. Anything a student saves stays in that student's own browser on that device. No accounts and no data collection.

**Printing.** The **Print** button prints the safety report. It works in the website and the standalone file.

---

## 4. Keeping recall data current

Car seat recalls are built into the app. Vehicle recalls are always live. Refresh the car seat recalls every month or two, or whenever NHTSA announces a big car seat recall.

You need Python 3, which macOS usually has. In a terminal, from the `Full-Project` folder:

```bash
python3 tools/update_recalls.py
python3 tools/build.py
```

Then upload the new `dist/website` folder to Netlify (section 1), and hand out the new `dist/SeatCheck-Michigan.html` if you use the standalone file. The footer of the app shows the date the recall data was last updated.

---

## 5. The AI research agent (instructor laptop only)

The full project includes an AI agent. It reads the car seat manual, the manufacturer's site and the vehicle owner's manual, then reports:

- exact seat limits
- the expiration rule
- where the lower anchors and tether anchors are in that vehicle
- install steps from the manual

Every fact links to its source. Use it to research seats before class or to demo it. **Don't give it to students:** it runs on your laptop with your own paid API key.

**One-time setup (Mac)**, from the `Full-Project` folder in a terminal:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**Add your API key:** create one at **console.anthropic.com** under Settings → API Keys. This needs a payment method; a Claude.ai subscription doesn't include it. Open the `.env` file in `Full-Project`, replace `paste-your-key-here` with the key, and save. Never share that file.

**Start it:**

```bash
.venv/bin/python server.py
```

Open **http://localhost:8766**. Fill in steps 1–3, then press **Research this seat & vehicle** in step 4.

- Each research run takes 1–3 minutes and costs roughly $0.50–$3.
- The child's name and the seat's serial number are never sent.
- Check anything important against the manual itself, using the source links.

*(Windows: use `py -m venv .venv`, then `.venv\Scripts\pip install -r requirements.txt` and `.venv\Scripts\python server.py`.)*

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "Couldn't reach NHTSA" | Check the internet connection. NHTSA's service is sometimes down for a few minutes. |
| No vehicle recalls found, but you expected some | Pick the model from the suggestion list so it matches NHTSA's spelling, or use the VIN. |
| A car seat recall didn't match | Try the model number from the label instead of the name. The report always links to nhtsa.gov/recalls for a manual search. |
| AI agent says "No valid Anthropic API key" | Check the key in `.env`, then stop the server (Ctrl+C) and start it again. |
| Standalone file opens as text on a phone | Expected. Use the website link on phones. |
