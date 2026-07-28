#!/usr/bin/env python3
"""
MD to HTML Converter
A lightweight, dependency-free Markdown to HTML converter with CLI.
"""

import argparse
import re
import sys
import os
from pathlib import Path
from typing import Optional
from html import escape


class MarkdownConverter:
    """Convert Markdown text to HTML."""

    def __init__(self, options: Optional[dict] = None):
        self.options = options or {}
        self.toc_entries = []

    def convert(self, text: str) -> str:
        """Convert markdown text to full HTML document."""
        self.toc_entries = []
        text = self._normalize(text)
        text = self._convert_code_blocks(text)
        text = self._convert_blockquotes(text)
        text = self._convert_headers(text)
        text = self._convert_horizontal_rules(text)
        text = self._convert_lists(text)
        text = self._convert_paragraphs(text)
        text = self._convert_inline(text)
        return text

    def convert_file(self, filepath: str) -> str:
        """Read a markdown file and convert it."""
        with open(filepath, "r", encoding="utf-8") as f:
            return self.convert(f.read())

    def _normalize(self, text: str) -> str:
        """Normalize line endings and whitespace."""
        text = text.replace("\r\n", "\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _convert_code_blocks(self, text: str) -> str:
        """Convert fenced code blocks and inline code."""
        # Fenced code blocks (```language)
        def replace_code_block(match):
            lang = match.group(1) or ""
            code = match.group(2)
            code = escape(code.rstrip("\n"))
            lang_attr = f' class="language-{lang}"' if lang else ""
            return f"<pre><code{lang_attr}>{code}</code></pre>"

        text = re.sub(
            r"```(\w*)?\n(.*?)```",
            replace_code_block,
            text,
            flags=re.DOTALL,
        )

        # Inline code
        text = re.sub(
            r"`([^`]+)`",
            lambda m: f"<code>{escape(m.group(1))}</code>",
            text,
        )
        return text

    def _convert_blockquotes(self, text: str) -> str:
        """Convert blockquote lines."""
        lines = text.split("\n")
        result = []
        in_quote = False
        quote_lines = []

        for line in lines:
            if line.startswith("> "):
                if not in_quote:
                    in_quote = True
                    quote_lines = []
                quote_lines.append(line[2:])
            elif line.startswith(">"):
                if not in_quote:
                    in_quote = True
                    quote_lines = []
                quote_lines.append(line[1:])
            else:
                if in_quote:
                    content = "\n".join(quote_lines)
                    content = self._convert_inline(content)
                    result.append(f"<blockquote>\n<p>{content}</p>\n</blockquote>")
                    in_quote = False
                    quote_lines = []
                result.append(line)

        if in_quote:
            content = "\n".join(quote_lines)
            content = self._convert_inline(content)
            result.append(f"<blockquote>\n<p>{content}</p>\n</blockquote>")

        return "\n".join(result)

    def _convert_headers(self, text: str) -> str:
        """Convert ATX-style headers (# to ######)."""
        def replace_header(match):
            level = len(match.group(1))
            content = match.group(2).strip()
            anchor = self._slugify(content)
            self.toc_entries.append((level, content, anchor))
            return f"<h{level} id="{anchor}">{content}</h{level}>"

        text = re.sub(
            r"^(#{1,6})\s+(.+)$",
            replace_header,
            text,
            flags=re.MULTILINE,
        )
        return text

    def _convert_horizontal_rules(self, text: str) -> str:
        """Convert horizontal rules."""
        text = re.sub(r"^\s*---\s*$", "<hr>", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*\*\*\*\s*$", "<hr>", text, flags=re.MULTILINE)
        return text

    def _convert_lists(self, text: str) -> str:
        """Convert unordered and ordered lists."""
        lines = text.split("\n")
        result = []
        in_ul = False
        in_ol = False
        ul_items = []
        ol_items = []

        for line in lines:
            ul_match = re.match(r"^(\s*)[-*+]\s+(.+)$", line)
            ol_match = re.match(r"^(\s*)\d+\.\s+(.+)$", line)

            if ul_match:
                if in_ol:
                    result.append(self._wrap_ol(ol_items))
                    in_ol = False
                    ol_items = []
                if not in_ul:
                    in_ul = True
                    ul_items = []
                ul_items.append(ul_match.group(2))
            elif ol_match:
                if in_ul:
                    result.append(self._wrap_ul(ul_items))
                    in_ul = False
                    ul_items = []
                if not in_ol:
                    in_ol = True
                    ol_items = []
                ol_items.append(ol_match.group(2))
            else:
                if in_ul:
                    result.append(self._wrap_ul(ul_items))
                    in_ul = False
                    ul_items = []
                if in_ol:
                    result.append(self._wrap_ol(ol_items))
                    in_ol = False
                    ol_items = []
                result.append(line)

        if in_ul:
            result.append(self._wrap_ul(ul_items))
        if in_ol:
            result.append(self._wrap_ol(ol_items))

        return "\n".join(result)

    def _wrap_ul(self, items: list) -> str:
        lis = "\n".join(f"<li>{self._convert_inline(item)}</li>" for item in items)
        return f"<ul>\n{lis}\n</ul>"

    def _wrap_ol(self, items: list) -> str:
        lis = "\n".join(f"<li>{self._convert_inline(item)}</li>" for item in items)
        return f"<ol>\n{lis}\n</ol>"

    def _convert_paragraphs(self, text: str) -> str:
        """Wrap remaining text blocks in <p> tags."""
        blocks = text.split("\n\n")
        result = []
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            # Skip already-converted blocks
            if block.startswith("<") and not block.startswith("<code>"):
                result.append(block)
                continue
            result.append(f"<p>{block}</p>")
        return "\n\n".join(result)

    def _convert_inline(self, text: str) -> str:
        """Convert inline elements: bold, italic, links, images."""
        # Images: ![alt](url "title")
        text = re.sub(
            r"!\[([^\]]*)\]\(([^\s)]+)(?:\s+"([^"]*)")?\)",
            lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}"'
            + (f' title="{m.group(3)}"' if m.group(3) else "")
            + ">",
            text,
        )

        # Links: [text](url "title")
        text = re.sub(
            r"\[([^\]]+)\]\(([^\s)]+)(?:\s+"([^"]*)")?\)",
            lambda m: f'<a href="{m.group(2)}"'
            + (f' title="{m.group(3)}"' if m.group(3) else "")
            + f">{m.group(1)}</a>",
            text,
        )

        # Bold + italic: ***text***
        text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", text)
        # Bold: **text**
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        # Italic: *text* or _text_
        text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
        text = re.sub(r"_(.+?)_", r"<em>\1</em>", text)

        # Strikethrough: ~~text~~
        text = re.sub(r"~~(.+?)~~", r"<del>\1</del>", text)

        return text

    def _slugify(self, text: str) -> str:
        """Create URL-friendly anchor from header text."""
        slug = re.sub(r"[^\w\s-]", "", text.lower())
        slug = re.sub(r"[\s-]+", "-", slug)
        return slug.strip("-")

    def generate_toc(self) -> str:
        """Generate a table of contents from headers."""
        if not self.toc_entries:
            return ""

        lines = ['<nav class="toc">', "<h2>Table of Contents</h2>", "<ul>"]
        for level, content, anchor in self.toc_entries:
            indent = "  " * (level - 1)
            lines.append(f'{indent}<li><a href="#{anchor}">{content}</a></li>')
        lines.append("</ul>")
        lines.append("</nav>")
        return "\n".join(lines)


def wrap_html(content: str, title: str = "Document", css: Optional[str] = None, toc: str = "") -> str:
    """Wrap HTML content in a full document structure."""
    css_block = f"<style>\n{css}\n</style>" if css else ""
    toc_block = f"\n{toc}\n" if toc else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
{css_block}
</head>
<body>
<div class="container">
{toc_block}
{content}
</div>
</body>
</html>"""


def get_default_css() -> str:
    """Return default stylesheet."""
    return """
:root {
  --bg: #fafafa;
  --fg: #1a1a1a;
  --muted: #666;
  --border: #e0e0e0;
  --accent: #2563eb;
  --code-bg: #f4f4f5;
}
* { box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: var(--bg);
  color: var(--fg);
  line-height: 1.7;
  margin: 0;
  padding: 0;
}
.container {
  max-width: 720px;
  margin: 0 auto;
  padding: 48px 24px;
}
h1, h2, h3, h4, h5, h6 {
  font-weight: 600;
  line-height: 1.3;
  margin-top: 2em;
  margin-bottom: 0.5em;
}
h1 { font-size: 2em; border-bottom: 2px solid var(--border); padding-bottom: 0.3em; }
h2 { font-size: 1.5em; border-bottom: 1px solid var(--border); padding-bottom: 0.3em; }
h3 { font-size: 1.25em; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
p { margin: 0 0 1em 0; }
ul, ol { margin: 0 0 1em 0; padding-left: 1.5em; }
li { margin-bottom: 0.25em; }
blockquote {
  border-left: 4px solid var(--accent);
  margin: 1em 0;
  padding: 0.5em 1em;
  background: var(--code-bg);
  border-radius: 0 6px 6px 0;
}
blockquote p { margin: 0; }
code {
  background: var(--code-bg);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: "SF Mono", Monaco, "Cascadia Code", monospace;
  font-size: 0.9em;
}
pre {
  background: var(--code-bg);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1em 0;
}
pre code { background: none; padding: 0; }
img { max-width: 100%; height: auto; border-radius: 6px; }
hr { border: none; border-top: 1px solid var(--border); margin: 2em 0; }
.toc {
  background: var(--code-bg);
  padding: 20px 24px;
  border-radius: 10px;
  margin-bottom: 2em;
}
.toc h2 { margin-top: 0; font-size: 1.1em; }
.toc ul { list-style: none; padding-left: 0; margin: 0; }
.toc li { margin-bottom: 0.3em; }
.toc a { color: var(--muted); }
.toc a:hover { color: var(--accent); }
@media (prefers-color-scheme: dark) {
  :root { --bg: #0f0f0f; --fg: #e5e5e5; --muted: #888; --border: #333; --code-bg: #1a1a1a; }
}
""".strip()


def batch_convert(input_dir: str, output_dir: str, options: dict) -> int:
    """Convert all .md files in a directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    md_files = list(input_path.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {input_dir}")
        return 0

    converter = MarkdownConverter(options)
    css = get_default_css() if options.get("styled") else None
    count = 0

    for md_file in md_files:
        html_content = converter.convert_file(str(md_file))
        toc = converter.generate_toc() if options.get("toc") else ""
        title = md_file.stem.replace("-", " ").replace("_", " ").title()
        full_html = wrap_html(html_content, title=title, css=css, toc=toc)

        out_file = output_path / (md_file.stem + ".html")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(full_html)
        print(f"  ✓ {md_file.name} → {out_file.name}")
        count += 1

    return count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to HTML.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file.md                          # Convert single file
  %(prog)s file.md -o output.html           # Specify output
  %(prog)s file.md --toc --styled           # With TOC and CSS
  %(prog)s docs/ -o site/                   # Batch convert directory
  %(prog)s file.md --css custom.css         # Use custom stylesheet
        """,
    )
    parser.add_argument("input", help="Input markdown file or directory")
    parser.add_argument("-o", "--output", help="Output file or directory")
    parser.add_argument("--toc", action="store_true", help="Generate table of contents")
    parser.add_argument("--styled", action="store_true", help="Include default CSS styling")
    parser.add_argument("--css", metavar="FILE", help="Path to custom CSS file")
    parser.add_argument("--title", help="HTML document title (default: filename)")
    parser.add_argument("--watch", action="store_true", help="Watch file for changes and auto-convert")

    args = parser.parse_args()
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)

    options = {"toc": args.toc, "styled": args.styled}

    # Custom CSS
    css = None
    if args.css:
        with open(args.css, "r", encoding="utf-8") as f:
            css = f.read()
    elif args.styled:
        css = get_default_css()

    # Batch conversion
    if input_path.is_dir():
        output_dir = args.output or str(input_path / "html")
        print(f"Converting .md files in '{input_path}' → '{output_dir}'")
        count = batch_convert(str(input_path), output_dir, options)
        print(f"\nDone. {count} file(s) converted.")
        return

    # Single file
    if args.watch:
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            print("Watch mode requires 'watchdog'. Install: pip install watchdog", file=sys.stderr)
            sys.exit(1)

        class MDHandler(FileSystemEventHandler):
            def on_modified(self, event):
                if event.src_path == str(input_path.resolve()):
                    self._convert()

            def _convert(self):
                converter = MarkdownConverter(options)
                html_content = converter.convert_file(str(input_path))
                toc = converter.generate_toc() if args.toc else ""
                title = args.title or input_path.stem.replace("-", " ").title()
                out_path = Path(args.output) if args.output else input_path.with_suffix(".html")
                full_html = wrap_html(html_content, title=title, css=css, toc=toc)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(full_html)
                print(f"  ✓ Rebuilt → {out_path}")

        handler = MDHandler()
        handler._convert()
        observer = Observer()
        observer.schedule(handler, str(input_path.parent), recursive=False)
        observer.start()
        print(f"Watching {input_path}... (Ctrl+C to stop)")
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
        return

    # Single file conversion
    converter = MarkdownConverter(options)
    html_content = converter.convert_file(str(input_path))
    toc = converter.generate_toc() if args.toc else ""
    title = args.title or input_path.stem.replace("-", " ").title()

    out_path = Path(args.output) if args.output else input_path.with_suffix(".html")
    full_html = wrap_html(html_content, title=title, css=css, toc=toc)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"✓ Converted: {input_path} → {out_path}")


if __name__ == "__main__":
    main()
