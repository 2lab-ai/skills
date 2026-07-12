---
name: markdown-converter
description: "Markitdown to Markdown: PDF, Office, HTML, data, OCR, audio, ZIP, YouTube."
---

**Source:** https://github.com/steipete/agent-scripts/tree/main/skills/markdown-converter (adopted 2026-05-16)
**적용 대상:** 지혁이 던지는 docx/pptx/xlsx/html/zip 등을 Markdown으로 변환. 기존 `pdf` 스킬은 PDF만 처리; markitdown은 Office/HTML/CSV/JSON/XML/EPub/audio/ZIP/YouTube까지 커버.

# Markdown Converter

Convert files to Markdown using `uvx markitdown` — no installation required.

## Basic Usage

```bash
# Convert to stdout
uvx markitdown input.pdf

# Save to file
uvx markitdown input.pdf -o output.md
uvx markitdown input.docx > output.md

# From stdin
cat input.pdf | uvx markitdown
```

## Supported Formats

- **Documents**: PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx, .xls)
- **Web/Data**: HTML, CSV, JSON, XML
- **Media**: Images (EXIF + OCR), Audio (EXIF + transcription)
- **Other**: ZIP (iterates contents), YouTube URLs, EPub

## Options

```bash
-o OUTPUT      # Output file
-x EXTENSION   # Hint file extension (for stdin)
-m MIME_TYPE   # Hint MIME type
-c CHARSET     # Hint charset (e.g., UTF-8)
-d             # Use Azure Document Intelligence
-e ENDPOINT    # Document Intelligence endpoint
--use-plugins  # Enable 3rd-party plugins
--list-plugins # Show installed plugins
```

## Examples

```bash
# Convert Word document
uvx markitdown report.docx -o report.md

# Convert Excel spreadsheet
uvx markitdown data.xlsx > data.md

# Convert PowerPoint presentation
uvx markitdown slides.pptx -o slides.md

# Convert with file type hint (for stdin)
cat document | uvx markitdown -x .pdf > output.md
```

## Notes

- Output preserves document structure: headings, tables, lists, links
- First run caches dependencies; subsequent runs are faster
- For complex PDFs (대용량/한글) → 기존 `pdf` 스킬 우선 사용. markitdown은 multi-format universal 변환에 사용.
- 결과는 보통 `SHARE/` 또는 `ARTIFACTS/`에 저장 (지혁 워크플로우).
