# KOReader MD5 — Calibre Plugin

A [calibre](https://calibre-ebook.com/) plugin that computes KOReader-compatible partial MD5 hashes for your ebook files and stores the result in a custom column to be used by KOReader sync.

## Why?

[KOReader](https://koreader.rocks/) identifies books by a partial MD5 hash of the file. If you want to sync reading progress, highlights, or other metadata between calibre and KOReader and you use KOReaderSync it may need to match on md5 so your calibre entry has to have the same md5 KOReader uses. This plugin will fill in that column for KOReader sync to match

## Features

- Computes the same partial MD5 hash that KOReader uses internally
- Stores the hash in a user-configured custom column
- Two hashing modes:
  - **Exported** (default) — hashes the file as calibre would send it to a device (with embedded metadata). Use this if you send books via calibre or calibre-web.
  - **Raw** — hashes the file exactly as stored in your calibre library. Use this if you sideload the unchanged epub directly.
- Configurable preferred format (EPUB, PDF, etc.)
- Toolbar button, dropdown menu, and right-click context menu
- Keyboard shortcut support (assign via Preferences → Shortcuts)

## Installation

### From ZIP file

1. Download the latest `KoreaderMD5.zip` from [Releases](https://github.com/CloudyMcFox/calibre-koreader-md5/releases)
2. In calibre: **Preferences → Plugins → Load plugin from file**
3. Select the ZIP file
4. Restart calibre

### From command line

```bash
calibre-customize -a KoreaderMD5.zip
```

## Setup

1. Use the column you created for KOReaderSync for md5 or  a new one: (**Preferences → Add your own columns**):
   - Type: "Text, column shown in the Tag browser"
   - Lookup name: e.g., `koreader_md5`
2. Open plugin settings (**Preferences → Plugins → KOReader MD5 → Customize**)
3. Select your custom column, preferred format, and hash mode
4. Select books and click the KOReader MD5 toolbar button (or right-click → KOReader MD5)

## How It Works

KOReader uses a partial MD5 algorithm that reads 1024-byte chunks at exponentially increasing offsets throughout the file, rather than hashing the entire file. This plugin ports that exact algorithm to Python so the hashes match.

## Building from Source

```powershell
# Package into a ZIP (requires PowerShell)
$files = @('__init__.py','ui.py','main.py','config.py','plugin-import-name-koreader_md5.txt')
# Use System.IO.Compression to preserve images/ path
```

Or simply zip all `.py` files + `plugin-import-name-koreader_md5.txt` + `images/icon.png` into a ZIP.

## License

GPL v3 — same as calibre.

## Author

Ryan Offir
