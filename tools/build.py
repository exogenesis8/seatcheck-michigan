#!/usr/bin/env python3
"""Build everything that gets handed out.

    python3 tools/build.py

Outputs in dist/:
  website/index.html                         The student website. Upload this folder to Netlify Drop or GitHub Pages.
  SeatCheck-Michigan.html                    The same app as one file. Double-click to open; works without hosting.
  SeatCheck-Michigan-Instructor-Package.zip  Everything above plus the full project (AI version + source),
                                             with START-HERE.md on top. This is what you give a trainer.

No build includes your real API key: the package gets an empty .env template.
"""
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
DATA_TAG = '<script src="data/carseat-recalls.js"></script>'
PKG = "SeatCheck-Michigan-Instructor-Package"

# Files that make up the full project inside the package (paths relative to ROOT).
PROJECT_FILES = [
    "index.html", "data/carseat-recalls.js", "agent.py", "server.py", "requirements.txt",
    "README.md", "INSTRUCTOR-GUIDE.md", "tools/build.py", "tools/update_recalls.py", ".gitignore",
    "docs/index.html", "docs/.nojekyll",
]
ENV_TEMPLATE = """# Paste your Anthropic API key after the = sign, save, then restart the server.
# Get one at https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=paste-your-key-here
"""


def standalone_html():
    """index.html with the recall data inlined and the AI section switched off."""
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    data_js = (ROOT / "data" / "carseat-recalls.js").read_text(encoding="utf-8")
    if DATA_TAG not in html:
        raise SystemExit("index.html no longer loads data/carseat-recalls.js the expected way")
    inline = (
        "<script>window.SEATCHECK_STANDALONE = true;</script>\n"
        "<script>\n" + data_js.replace("</script", "<\\/script") + "\n</script>"
    )
    return html.replace(DATA_TAG, inline)


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "website").mkdir(parents=True)

    page = standalone_html()
    (DIST / "website" / "index.html").write_text(page, encoding="utf-8")
    # GitHub Pages publishes the docs/ folder of the repository.
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "index.html").write_text(page, encoding="utf-8")
    (ROOT / "docs" / ".nojekyll").write_text("")
    (DIST / "SeatCheck-Michigan.html").write_text(page, encoding="utf-8")

    zip_path = DIST / f"{PKG}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(ROOT / "INSTRUCTOR-GUIDE.md", f"{PKG}/START-HERE.md")
        z.writestr(f"{PKG}/Student-Website/index.html", page)
        z.writestr(f"{PKG}/Standalone-File/SeatCheck-Michigan.html", page)
        for rel in PROJECT_FILES:
            z.write(ROOT / rel, f"{PKG}/Full-Project/{rel}")
        z.writestr(f"{PKG}/Full-Project/.env", ENV_TEMPLATE)  # template only, never the real key

    # Safety net: refuse to ship anything that looks like a real Anthropic key.
    key_marker = "sk-" + "ant-"
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        leaked = [n for n in names if key_marker in z.read(n).decode("utf-8", "ignore")]
    if leaked:
        zip_path.unlink()
        raise SystemExit(f"Stopped: {', '.join(leaked)} contains what looks like an API key. Package not created.")
    print(f"Website:            dist/website/index.html")
    print(f"Standalone file:    dist/SeatCheck-Michigan.html ({len(page) // 1024} KB)")
    print(f"Instructor package: dist/{PKG}.zip ({zip_path.stat().st_size // 1024} KB, {len(names)} files)")


if __name__ == "__main__":
    main()
