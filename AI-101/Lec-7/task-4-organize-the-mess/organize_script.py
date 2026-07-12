"""
ORGANIZE THE MESS (THE FILES YOU FORGOT)
------------------------------------------
Scans a messy folder, finds duplicates and oversized files, groups
everything by type, and proposes a plan -- but NEVER touches, moves,
renames, or deletes your original files. It only ever WRITES a new,
separate, organized copy once you've reviewed and approved the plan.

SAFETY ORDER (do not skip steps):
  1. BACKUP  -- the script backs up the source folder before doing
                anything else, every single run.
  2. PLAN    -- the script scans and prints every operation it WOULD
                do. Nothing is written yet. This is the dry run.
  3. APPROVE -- you read the plan and only then set APPROVED = True
                (or pass --approve on the command line).
  4. EXECUTE -- only after approval, the script builds a new organized
                folder. Your original folder is never modified,
                renamed, or deleted -- not even the duplicates.

HOW TO USE:
  1. Set SOURCE_FOLDER to the real messy folder you want to look at.
  2. Run once with no changes: `python organize_script.py`
     This only backs up and prints the plan. Nothing else happens.
  3. Read the plan carefully.
  4. Run again with approval: `python organize_script.py --approve`
     This builds the organized copy. Originals are still untouched.
"""

import argparse
import hashlib
import os
import shutil
import sys
from collections import defaultdict
from datetime import datetime

# ----------------------------------------------------------------------
# 1. CONFIG -- edit these
# ----------------------------------------------------------------------

SOURCE_FOLDER = "sample_messy_folder"        # the real messy folder to scan
BACKUP_FOLDER = "sample_messy_folder_BACKUP" # made fresh every run, before anything else
OUTPUT_FOLDER = "sample_messy_folder_ORGANIZED"  # where the clean copy goes

LARGE_FILE_THRESHOLD_MB = 5   # files bigger than this get flagged as "large"

TYPE_GROUPS = {
    "Images":    [".png", ".jpg", ".jpeg", ".gif", ".webp"],
    "Documents": [".docx", ".doc", ".pdf", ".txt", ".xlsx", ".xls"],
    "Installers": [".exe", ".dmg", ".pkg", ".msi"],
    "Video":     [".mp4", ".mov", ".avi"],
}


def group_for_extension(ext):
    for group, extensions in TYPE_GROUPS.items():
        if ext.lower() in extensions:
            return group
    return "Other"


# ----------------------------------------------------------------------
# 2. STEP 1 -- BACKUP FIRST, ALWAYS
# ----------------------------------------------------------------------

def make_backup(source, backup):
    """Makes a full backup copy of the source folder before anything else runs.
    If a backup already exists from an earlier run, a fresh timestamped one
    is made instead of overwriting it, so nothing is ever lost."""
    if os.path.exists(backup):
        stamped = f"{backup}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"  A backup already exists at '{backup}'. "
              f"Making a fresh one at '{stamped}' instead (never overwriting).")
        backup = stamped
    shutil.copytree(source, backup)
    print(f"  Backup complete: '{source}' -> '{backup}'")
    return backup


# ----------------------------------------------------------------------
# 3. SCAN THE FOLDER
# ----------------------------------------------------------------------

def hash_file(path, block_size=65536):
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            hasher.update(block)
    return hasher.hexdigest()


def scan_folder(source):
    files = []
    for root, _dirs, filenames in os.walk(source):
        for name in filenames:
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, source)
            size = os.path.getsize(full_path)
            ext = os.path.splitext(name)[1]
            files.append({
                "rel_path": rel_path,
                "full_path": full_path,
                "name": name,
                "ext": ext,
                "size": size,
                "hash": hash_file(full_path),
            })
    return files


# ----------------------------------------------------------------------
# 4. BUILD THE PLAN (no file operations happen here -- read only)
# ----------------------------------------------------------------------

def build_plan(files):
    by_hash = defaultdict(list)
    for f in files:
        by_hash[f["hash"]].append(f)

    duplicate_groups = [group for group in by_hash.values() if len(group) > 1]

    large_files = [f for f in files if f["size"] > LARGE_FILE_THRESHOLD_MB * 1024 * 1024]

    # "Keep" copy operations: one copy per file into its type-grouped folder,
    # with duplicates routed into a separate review folder instead of the
    # main grouped folders, so they don't silently multiply your clean copy.
    duplicate_paths = set()
    for group in duplicate_groups:
        # Keep the first alphabetically as "original", flag the rest as dupes
        group_sorted = sorted(group, key=lambda f: f["rel_path"])
        for dupe in group_sorted[1:]:
            duplicate_paths.add(dupe["rel_path"])

    copy_operations = []
    for f in files:
        if f["rel_path"] in duplicate_paths:
            dest_group = "Duplicates_To_Review"
        else:
            dest_group = group_for_extension(f["ext"])
        dest_rel = os.path.join(dest_group, f["name"])
        copy_operations.append({"source": f["rel_path"], "dest": dest_rel,
                                 "hash": f["hash"]})

    # Safety check: two DIFFERENT files (different content) landing on the
    # same destination path would silently overwrite one another. Never let
    # that happen -- rename the later ones to include their original folder
    # instead, and flag it clearly in the plan.
    seen_dest = {}
    naming_collisions = []
    for op in copy_operations:
        dest = op["dest"]
        if dest not in seen_dest:
            seen_dest[dest] = op["hash"]
        elif seen_dest[dest] != op["hash"]:
            # Same destination, different content -- rename to disambiguate
            source_folder = op["source"].split(os.sep)[0]
            base, ext = os.path.splitext(dest)
            new_dest = f"{base} (from {source_folder}){ext}"
            naming_collisions.append({"source": op["source"], "original_dest": dest,
                                       "new_dest": new_dest})
            op["dest"] = new_dest

    return {
        "files": files,
        "duplicate_groups": duplicate_groups,
        "large_files": large_files,
        "copy_operations": copy_operations,
        "naming_collisions": naming_collisions,
    }


# ----------------------------------------------------------------------
# 5. PRINT THE PLAN (the dry run -- this is what you approve or reject)
# ----------------------------------------------------------------------

def print_plan(plan, source):
    print("\n" + "=" * 65)
    print("DRY RUN -- FULL PLAN (nothing has been changed yet)")
    print("=" * 65)

    print(f"\nScanned folder: {source}")
    print(f"Total files found: {len(plan['files'])}")
    total_size_mb = sum(f["size"] for f in plan["files"]) / (1024 * 1024)
    print(f"Total size: {total_size_mb:.2f} MB")

    print("\n--- DUPLICATE FILES (identical content) ---")
    if plan["duplicate_groups"]:
        wasted_mb = 0
        for group in plan["duplicate_groups"]:
            group_sorted = sorted(group, key=lambda f: f["rel_path"])
            keeper = group_sorted[0]
            dupes = group_sorted[1:]
            wasted_mb += sum(d["size"] for d in dupes) / (1024 * 1024)
            print(f"  KEEP:      {keeper['rel_path']}  ({keeper['size']/1024:.1f} KB)")
            for d in dupes:
                print(f"  DUPLICATE: {d['rel_path']}  ({d['size']/1024:.1f} KB) "
                      f"-- identical content to the file above")
        print(f"\n  Total space in duplicates: {wasted_mb:.2f} MB")
        print("  Note: duplicates are NOT deleted. They are copied into a "
              "'Duplicates_To_Review' folder so you can look them over and "
              "delete originals yourself, on your own terms.")
    else:
        print("  None found.")

    print(f"\n--- LARGE FILES (over {LARGE_FILE_THRESHOLD_MB} MB) ---")
    if plan["large_files"]:
        for f in plan["large_files"]:
            print(f"  {f['rel_path']}: {f['size']/1024/1024:.2f} MB")
    else:
        print("  None found.")

    print("\n--- PROPOSED FILE-TYPE GROUPING ---")
    by_group = defaultdict(int)
    for op in plan["copy_operations"]:
        top_group = op["dest"].split(os.sep)[0]
        by_group[top_group] += 1
    for group, count in sorted(by_group.items()):
        print(f"  {group}: {count} file(s)")

    print("\n--- NAMING COLLISIONS (same filename, different content) ---")
    if plan["naming_collisions"]:
        for c in plan["naming_collisions"]:
            print(f"  \"{c['source']}\" would have landed on top of an unrelated "
                  f"file also named this. Renamed instead to avoid overwriting: "
                  f"{c['new_dest']}")
    else:
        print("  None found.")

    print(f"\n--- EVERY OPERATION THIS SCRIPT WOULD PERFORM ---")
    print(f"  (all are COPY operations into '{OUTPUT_FOLDER}/' -- ")
    print(f"   originals in '{source}/' are never moved, renamed, or deleted)")
    for op in plan["copy_operations"]:
        print(f"  COPY  {op['source']}  ->  {OUTPUT_FOLDER}/{op['dest']}")

    print("\n" + "=" * 65)
    print("END OF PLAN. Nothing has been written or changed yet.")
    print("Review this list. If it looks right, re-run with --approve")
    print("to actually build the organized copy.")
    print("=" * 65)


# ----------------------------------------------------------------------
# 6. EXECUTE (only runs if the plan was approved)
# ----------------------------------------------------------------------

def execute_plan(plan, source, output_folder):
    if os.path.exists(output_folder):
        stamped = f"{output_folder}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"  '{output_folder}' already exists -- writing to '{stamped}' "
              f"instead so nothing gets overwritten.")
        output_folder = stamped

    for op in plan["copy_operations"]:
        src = os.path.join(source, op["source"])
        dest = os.path.join(output_folder, op["dest"])
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src, dest)

    print(f"  Organized copy written to: {output_folder}")
    print(f"  Original folder untouched: {source}")
    return output_folder


# ----------------------------------------------------------------------
# 7. MAIN
# ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--approve", action="store_true",
                         help="Actually build the organized copy. "
                              "Without this flag, only the dry-run plan is shown.")
    args = parser.parse_args()

    if not os.path.isdir(SOURCE_FOLDER):
        print(f"Source folder '{SOURCE_FOLDER}' not found. Edit SOURCE_FOLDER "
              f"at the top of this script.")
        sys.exit(1)

    print("=" * 65)
    print("ORGANIZE THE MESS -- STEP 1: BACKUP")
    print("=" * 65)
    make_backup(SOURCE_FOLDER, BACKUP_FOLDER)

    print("\n" + "=" * 65)
    print("STEP 2: SCAN + BUILD PLAN")
    print("=" * 65)
    files = scan_folder(SOURCE_FOLDER)
    plan = build_plan(files)
    print_plan(plan, SOURCE_FOLDER)

    if not args.approve:
        print("\nNo changes made. Re-run with --approve once you've reviewed "
              "the plan above.")
        return

    print("\n" + "=" * 65)
    print("STEP 3: APPROVED -- EXECUTING PLAN")
    print("=" * 65)
    execute_plan(plan, SOURCE_FOLDER, OUTPUT_FOLDER)

    print("\n" + "=" * 65)
    print("DONE. Spot-check the organized folder, then decide what to do")
    print("with the files listed under Duplicates_To_Review yourself.")
    print("=" * 65)


if __name__ == "__main__":
    main()
