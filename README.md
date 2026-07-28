# 📝 MD to HTML Converter

A lightweight, dependency-free Markdown to HTML converter with a clean CLI. Convert single files, entire directories, or watch files for changes — all with beautiful default styling.

## Features

- ✅ **Zero dependencies** — Pure Python, works out of the box
- ✅ **Full Markdown support** — Headers, lists, links, images, code blocks, blockquotes, tables, horizontal rules
- ✅ **Batch conversion** — Convert an entire directory of `.md` files at once
- ✅ **Table of contents** — Auto-generate a clickable TOC from headers
- ✅ **Beautiful default CSS** — Clean, responsive, dark-mode aware styling
- ✅ **Custom CSS** — Bring your own stylesheet
- ✅ **Watch mode** — Auto-rebuild on file changes (requires `watchdog`)
- ✅ **Anchor links** — Every header gets an ID for deep linking

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/md-to-html.git
cd md-to-html
```

No dependencies required for basic usage!

```bash
# Optional: for watch mode
pip install watchdog
```

## Usage

### Convert a single file

```bash
python md_to_html.py README.md
# Output: README.html
```

### With styling and table of contents

```bash
python md_to_html.py README.md --styled --toc
```

### Specify output file

```bash
python md_to_html.py README.md -o docs/index.html
```

### Batch convert a directory

```bash
python md_to_html.py docs/ -o site/
# Converts all .md files in docs/ to .html in site/
```

### Watch mode (auto-rebuild on save)

```bash
python md_to_html.py README.md --watch --styled
```

### Custom CSS

```bash
python md_to_html.py README.md --css my-theme.css
```

## Supported Markdown

| Syntax | Result |
|--------|--------|
| `# Header` | `<h1>` with auto-anchor |
| `**bold**` | `<strong>` |
| `*italic*` | `<em>` |
| `` `code` `` | `<code>` |
| ```` ```python ```` | Syntax-highlighted `<pre><code>` |
| `> quote` | `<blockquote>` |
| `- item` / `1. item` | `<ul>` / `<ol>` |
| `[text](url)` | `<a href>` |
| `![alt](img.png)` | `<img>` |
| `---` | `<hr>` |
| `~~strikethrough~~` | `<del>` |

## Project Structure

```
md-to-html/
├── md_to_html.py          # Main converter + CLI
├── sample.md              # Example markdown file
├── requirements.txt       # Optional dependencies
├── .gitignore
└── README.md
```

## Running Tests

```bash
python -m pytest tests/
```

## Why build this?

Most Markdown converters pull in heavy dependencies. This project demonstrates:
- **Regex parsing** and text processing
- **CLI design** with `argparse`
- **File I/O** and directory traversal
- **HTML generation** and templating
- **Clean code architecture** (parser + renderer separation)

## License

MIT
