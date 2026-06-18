# Sydney Wentz — Writer Portfolio

A warm literary portfolio that lives on GitHub Pages. **No coding needed to add new work.**

---

## ✦ How to add a new piece (the only thing you'll ever need to do)

### Step 1 — Name your PDF correctly

Rename your PDF file before uploading, using dashes instead of spaces:

```
The-Blue-Hour.pdf              ← fiction
Cartography-of-a-Leaving.pdf   ← poetry
On-Silence_2024.pdf            ← essays (you can add the year if you want)
```

**No special characters, no spaces, dashes only.**

---

### Step 2 — Go to the right folder on github.com

Open your repository, then navigate to one of these folders:

| What you're uploading | Folder to open |
|-----------------------|----------------|
| Fiction / short story | `pdfs/fiction/` |
| Poetry                | `pdfs/poetry/`  |
| Essay                 | `pdfs/essays/`  |

---

### Step 3 — Upload the PDF

1. Click **"Add file"** → **"Upload files"**
2. Drag your PDF into the box (or click to browse)
3. Scroll down to the **"Commit changes"** section
4. Leave everything as-is and click **"Commit changes"**

That's it. ✓

---

### Step 4 — Wait about 60 seconds

GitHub will automatically:
- Read your PDF
- Create a beautiful reading page for it
- Add it to the Works index

You can watch it happen under the **Actions** tab. A green ✓ means it's live.

---

## ✦ Optional: Add a custom description

If you want to write your own description (instead of the auto-extracted text), open `scripts/works_meta.json` in GitHub and add an entry:

```json
{
  "The-Blue-Hour.pdf": {
    "title": "The Blue Hour",
    "year": "2026",
    "description": "A woman returns to her childhood home to find that the house has been quietly waiting."
  }
}
```

Save it, and the next time a PDF is uploaded the description will be used.

---

## ✦ Updating your bio / About page

Open `about.html` in GitHub, click the pencil ✏️ icon to edit, and change the text between the `<p>` tags. Commit when done.

To add a photo, upload an image file to the repo and replace the portrait section in `about.html` with:
```html
<img src="your-photo.jpg" alt="Sydney Wentz" class="portrait-img" />
```

---

## ✦ Site structure (for reference)

```
pdfs/
  fiction/    ← drop fiction PDFs here
  poetry/     ← drop poetry PDFs here
  essays/     ← drop essay PDFs here

works/        ← auto-generated HTML pages (don't edit manually)
works.html    ← auto-generated index (don't edit manually)

index.html    ← home page (edit to update featured works)
about.html    ← bio page (edit freely)
css/          ← visual styles
scripts/      ← the automation that powers everything
.github/      ← GitHub Actions config
```
