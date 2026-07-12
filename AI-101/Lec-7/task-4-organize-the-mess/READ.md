# Task 4: Organize the Mess (The Files You Forgot)

Scans a genuinely messy folder, finds duplicates and oversized files,
and groups everything by type — but only ever by *copying* into a new
folder. Originals are never moved, renamed, or deleted, not even the
duplicates.

## Files

- `sample_messy_folder/` — a stand-in for a real Downloads/Documents
  folder: duplicate invoices, a resume saved twice under different
  names, duplicate screenshots, half-finished drafts, an old-project
  folder with a filename collision, and one oversized video file.
- `organize_script.py` — the script itself.

Two more folders appear the first time you *run* the script, and are
intentionally not shipped pre-built:
- `sample_messy_folder_BACKUP/` — full backup, made automatically
  before anything else happens.
- `sample_messy_folder_ORGANIZED/` — the new, organized copy (only
  created after you approve the plan).

## The brief (what "clean" means here)

- Find **duplicates** — same content, regardless of filename.
- Flag **large files** — anything over 5 MB.
- **Group by type** — Images, Documents, Installers, Video, Other.
- Catch **naming collisions** — two *different* files that happen to
  share a filename should never silently overwrite each other.

## Safety order this script follows

1. **Backup first.** Every run starts by copying the entire source
   folder to a backup, before any scanning or planning happens. If a
   backup already exists, a fresh timestamped one is made instead of
   overwriting it.
2. **Plan only (dry run).** Running the script with no flags scans the
   folder and prints every single operation it *would* do — every
   duplicate, every large file, every proposed copy — and then stops.
   Nothing is written.
3. **You approve.** Only re-running with `--approve` triggers step 4.
4. **Execute — as copies, never in place.** The organized version is
   built in a brand-new folder. The original folder is never touched:
   not moved, not renamed, not deleted. Duplicates are copied into a
   `Duplicates_To_Review` folder rather than deleted automatically, so
   the decision to actually remove anything stays with you.

## How to run

```
# Step 1: see the full plan, nothing happens yet
python organize_script.py

# Step 2: read the plan carefully

# Step 3: only once you're satisfied, actually build the organized copy
python organize_script.py --approve
```

## What the dry run found on the sample folder

- **19 files, 6.20 MB total**
- **5 duplicate files** (identical content, different names/locations):
  meeting notes copied twice, a vacation photo saved under two names,
  an invoice downloaded twice, a resume saved under two filenames, and
  a screenshot copied once more.
- **1 large file**: `random/big_video_export.mp4` at 6.20 MB.
- **1 naming collision**: two *different* files both named
  `notes_meeting_apr.txt` (one in `Documents/`, one in `old_project/`)
  — the script automatically renamed the second on copy instead of
  letting it overwrite the first.
- Everything else grouped cleanly into Documents / Images / Installers
  / Video.

Verified after running with `--approve`: all 19 original files were
confirmed byte-for-byte identical before and after — the script only
ever wrote to the new `_ORGANIZED` folder.
