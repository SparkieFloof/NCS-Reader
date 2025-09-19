##NCS Reader
##Overview

NCS Reader is a desktop tool written in Python with Tkinter for inspecting and editing .ncs files.
It is designed to help reverse-engineer, analyze, and manipulate binary record-based files by providing multiple synchronized views of the file contents:

File Browser – Load a single .ncs file or multiple files at once.

JSON View – Structured representation of parsed data with heuristically guessed field names and metadata.

Table View – Tabular display of records, with detailed breakdown of offsets, raw values, and interpreted data.

Hex Editor – Split view of raw bytes in hex (left) and ASCII (right), with editable support.

The tool includes multiple specialized parsers (e.g., for activity, aim_assist_parameters, etc.) that attempt to interpret file contents based on record sizes and known structures. If no specific parser matches, a Generic Parser provides a fallback.

Features

##📂 File Management

Load single .ncs files or select multiple at once.

Displays only filenames (not full paths) in the sidebar for cleaner navigation.

##🧩 Parsers

Auto-detection of file type and record sizes.

Specialized parsers for known .ncs structures.

Fallback generic parser for unknown or unsupported files.

Each parser supports:

parse(filepath | bytes) → returns raw + structured JSON

to_bytes(data) → reconstructs back into .ncs binary

##🔍 Detailed Views

JSON View: Rich structured representation with guessed field names, offsets, sizes, and raw values.

Table View: Detailed row-by-row representation of records.

Hex View: Editable hex/ASCII split, useful for low-level inspection.

##✏️ Editing & Saving

Edit JSON and save changes as Edited_<filename>.json.

Edit binary contents in hex and save as Edited_<filename>.ncs.

Parsers reconstruct binary with to_bytes() when saving edited JSON.

##🎨 UI/UX

Dark mode enabled by default (with toggle option in settings).

Scrollbars for JSON, table, and hex views for easier navigation.

Toolbar for quick actions (Save JSON, Save NCS, Toggle Theme).

##How to Run
##Requirements

Python 3.9+ (tested on 3.12).

Standard library only (no external dependencies required).

Running

Extract the project ZIP.

Open a terminal in the project folder.

Run:

python main.py


Alternatively, double-click main.py (if .py files are associated with Python on your system).

##Limitations

##⚠ Experimental Parsing

Field names and structures are heuristically guessed; correctness is not guaranteed.

Not all .ncs file variants are covered; unknown formats fall back to generic parser.

##⚠ Editing JSON

Saving back to .ncs relies on to_bytes() implementations.

If the structure guess is wrong, the recompiled file may differ from the original.

Hex editing is always safer when exact preservation is required.

##⚠ UI Constraints

Tkinter UI is functional but not highly modern (compared to Qt/GTK).

Large .ncs files may render slowly in JSON or table views.

##⚠ Cross-Platform Notes

Designed for Windows but should work on Linux/macOS with Python 3.9+.

Double-click execution (main.py) may not work on all systems without configuring Python launcher.

License

This project is provided for educational and research purposes only.
Not intended for commercial use or redistributing proprietary .ncs files.