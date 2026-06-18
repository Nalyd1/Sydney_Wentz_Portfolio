"""
generate_pages.py
-----------------
Scans every PDF in pdfs/fiction/, pdfs/poetry/, pdfs/essays/
and generates:
  - A reading page at works/<genre>/<slug>.html  (embeds the PDF + extracted text)
  - A rebuilt works.html index listing all works

PDF filename convention (the only "rule" for uploading):
  <genre>_<Title-With-Dashes>[_YYYY].pdf

Examples:
  fiction_The-Blue-Hour.pdf
  poetry_Cartography-of-a-Leaving_2024.pdf
  essays_On-Silence-as-a-Mother-Tongue_2025.pdf

The genre prefix is used only as a fallback — the folder the PDF lives in
takes priority (pdfs/fiction/ → Fiction, etc.).
"""

import os
import re
import json
from pathlib import Path
from datetime import date

try:
    from PyPDF2 import PdfReader
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).parent.parent
PDFS_DIR   = ROOT / "pdfs"
WORKS_DIR  = ROOT / "works"
WORKS_HTML = ROOT / "works.html"
META_FILE  = ROOT / "scripts" / "works_meta.json"   # optional hand-edited overrides

GENRE_MAP = {
    "fiction": "Fiction",
    "poetry":  "Poetry",
    "essays":  "Essay",
    "essay":   "Essay",
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def parse_filename(pdf_path: Path, folder_genre: str):
    """
    Returns (title, genre, year, slug) from a PDF path.
    Filename format: [genre_]Title-Words[_YYYY].pdf
    """
    stem = pdf_path.stem  # e.g. "fiction_The-Blue-Hour_2026"

    # Extract year if present
    year_match = re.search(r"_(\d{4})$", stem)
    year = year_match.group(1) if year_match else str(date.today().year)
    stem = re.sub(r"_\d{4}$", "", stem)

    # Strip leading genre prefix if present
    genre_prefix_match = re.match(r"^(fiction|poetry|essays?|essay)_", stem, re.I)
    if genre_prefix_match:
        stem = stem[len(genre_prefix_match.group(0)):]

    # Convert dashes/underscores to spaces → Title Case
    title = re.sub(r"[-_]+", " ", stem).strip()
    title = " ".join(w.capitalize() for w in title.split())

    genre = GENRE_MAP.get(folder_genre.lower(), folder_genre.capitalize())
    slug  = slugify(title)

    return title, genre, year, slug


def extract_text(pdf_path: Path, max_chars: int = 8000) -> str:
    """Extract plain text from the first several pages of a PDF."""
    if not HAS_PDF:
        return ""
    try:
        reader = PdfReader(str(pdf_path))
        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
            if sum(len(t) for t in text_parts) > max_chars:
                break
        raw = "\n\n".join(text_parts)[:max_chars]
        # Collapse excessive blank lines
        raw = re.sub(r"\n{3,}", "\n\n", raw).strip()
        return raw
    except Exception as e:
        print(f"  ⚠  Could not extract text from {pdf_path.name}: {e}")
        return ""


def text_to_html_paragraphs(text: str) -> str:
    """Convert plain text blocks into <p> tags."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return "\n".join(f"      <p>{p}</p>" for p in paragraphs)


def excerpt(text: str, length: int = 180) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    if len(clean) <= length:
        return clean
    return clean[:length].rsplit(" ", 1)[0] + "…"


# ── HTML Templates ────────────────────────────────────────────────────────────

def render_reading_page(title, genre, year, pdf_rel, text_html, slug) -> str:
    depth = "../../"   # works/<genre>/<slug>.html → root
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} — Sydney Wentz</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Lato:wght@300;400&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{depth}css/style.css" />
</head>
<body class="reading-page">

  <nav class="nav">
    <a href="{depth}index.html" class="nav-name">Sydney Wentz</a>
    <div class="nav-links">
      <a href="{depth}works.html">← All Works</a>
    </div>
  </nav>

  <article class="reading-article">
    <header class="reading-header">
      <span class="reading-genre">{genre}</span>
      <h1 class="reading-title">{title}</h1>
      <p class="reading-byline">by Sydney Wentz · {year}</p>
      <div class="reading-ornament" aria-hidden="true">❧</div>
    </header>

    <!-- Embedded PDF viewer -->
    <div class="pdf-viewer">
      <iframe
        src="{depth}{pdf_rel}"
        title="{title} — PDF"
        class="pdf-frame"
        loading="lazy"
      ></iframe>
      <a href="{depth}{pdf_rel}" class="pdf-download" download>
        ↓ Download PDF
      </a>
    </div>

    <!-- Extracted text (shown if PDF can't render, hidden otherwise via JS) -->
    <div class="reading-body reading-fallback" id="text-fallback" hidden>
{text_html}
    </div>

    <footer class="reading-footer">
      <div class="reading-ornament" aria-hidden="true">❧</div>
      <a href="{depth}works.html" class="btn btn-ghost">← Back to Works</a>
    </footer>
  </article>

  <footer class="footer">
    <p class="footer-copy">© {year} Sydney Wentz · Built with words and GitHub Pages</p>
  </footer>

  <script>
    // Show text fallback if the PDF iframe fails to load
    const frame = document.querySelector('.pdf-frame');
    if (frame) {{
      frame.addEventListener('error', () => {{
        document.getElementById('text-fallback').hidden = false;
      }});
    }}
  </script>

</body>
</html>
"""


def render_works_html(works: list) -> str:
    """Rebuild the full works.html from the list of work dicts."""

    def work_row(w):
        return f"""
    <article class="work-row" data-genre="{w['genre_key']}">
      <div class="work-meta">
        <span class="work-genre">{w['genre']}</span>
        <span class="work-date">{w['year']}</span>
      </div>
      <div class="work-body">
        <h2 class="work-title"><a href="{w['html_rel']}">{w['title']}</a></h2>
        <p class="work-desc">{w['excerpt']}</p>
      </div>
      <a href="{w['html_rel']}" class="work-read">Read →</a>
    </article>"""

    rows = "\n".join(work_row(w) for w in sorted(works, key=lambda x: x["year"], reverse=True))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Works — Sydney Wentz</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Lato:wght@300;400&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="css/style.css" />
</head>
<body>

  <nav class="nav">
    <a href="index.html" class="nav-name">Sydney Wentz</a>
    <div class="nav-links">
      <a href="works.html" class="active">Works</a>
      <a href="about.html">About</a>
      <a href="mailto:swentz702@icloud.com">Contact</a>
    </div>
  </nav>

  <div class="page-header">
    <h1 class="page-title">Works</h1>
    <p class="page-sub">All writing, across all forms.</p>
  </div>

  <div class="filter-bar">
    <button class="filter-btn active" data-genre="all">All</button>
    <button class="filter-btn" data-genre="fiction">Fiction</button>
    <button class="filter-btn" data-genre="poetry">Poetry</button>
    <button class="filter-btn" data-genre="essay">Essay</button>
  </div>

  <main class="works-list">
{rows}
  </main>

  <footer class="footer">
    <p class="footer-quote"><em>"The story is always bigger than the telling."</em></p>
    <p class="footer-copy">© {date.today().year} Sydney Wentz · Built with words and GitHub Pages</p>
  </footer>

  <script src="js/filter.js"></script>
</body>
</html>
"""


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    # Load optional hand-edited metadata overrides
    meta_overrides = {}
    if META_FILE.exists():
        with open(META_FILE) as f:
            meta_overrides = json.load(f)

    all_works = []

    for genre_folder in ("fiction", "poetry", "essays"):
        src_dir  = PDFS_DIR / genre_folder
        out_dir  = WORKS_DIR / genre_folder
        out_dir.mkdir(parents=True, exist_ok=True)

        if not src_dir.exists():
            continue

        for pdf_path in sorted(src_dir.glob("*.pdf")):
            print(f"Processing: {pdf_path.name}")

            title, genre, year, slug = parse_filename(pdf_path, genre_folder)

            # Apply any manual overrides keyed by original filename
            overrides = meta_overrides.get(pdf_path.name, {})
            title = overrides.get("title", title)
            genre = overrides.get("genre", genre)
            year  = overrides.get("year",  year)
            slug  = overrides.get("slug",  slug) or slugify(title)
            desc  = overrides.get("description", "")

            # Relative paths (from repo root)
            pdf_rel  = f"pdfs/{genre_folder}/{pdf_path.name}"
            html_rel = f"works/{genre_folder}/{slug}.html"
            html_out = ROOT / html_rel

            # Extract text for fallback + excerpt
            raw_text  = extract_text(pdf_path)
            text_html = text_to_html_paragraphs(raw_text)
            ex        = desc if desc else excerpt(raw_text)

            # Write reading page
            page_html = render_reading_page(title, genre, year, pdf_rel, text_html, slug)
            html_out.write_text(page_html, encoding="utf-8")
            print(f"  ✓ {html_rel}")

            genre_key = "essay" if genre == "Essay" else genre.lower()
            all_works.append({
                "title":     title,
                "genre":     genre,
                "genre_key": genre_key,
                "year":      year,
                "slug":      slug,
                "html_rel":  html_rel,
                "excerpt":   ex or f"A {genre.lower()} by Sydney Wentz.",
            })

    if all_works:
        WORKS_HTML.write_text(render_works_html(all_works), encoding="utf-8")
        print(f"\n✓ Rebuilt works.html with {len(all_works)} works.")
    else:
        print("\nNo PDFs found. Upload PDFs to pdfs/fiction/, pdfs/poetry/, or pdfs/essays/")


if __name__ == "__main__":
    main()
