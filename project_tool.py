#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║          PROJECT PACKER / UNPACKER TOOL                      ║
║          Pack & Unpack your entire project in one txt file   ║
║          Compatible with: Python 3.6+  |  No dependencies   ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────
#  ANSI COLOR CODES (works on Linux/macOS/Win10+)
# ─────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    MAGENTA= "\033[95m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    DIM    = "\033[2m"

def clr(text, color, bold=False):
    """Apply ANSI color to text."""
    b = C.BOLD if bold else ""
    return f"{b}{color}{text}{C.RESET}"

# ─────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────
OUTPUT_FILE = "full_project_code.txt"
SCRIPT_NAME = Path(__file__).name
UNPACK_DIR  = "unpacked_project"

# Folders to skip entirely
SKIP_DIRS = {
    "node_modules", ".git", ".next", "dist", "build",
    "__pycache__", ".venv", "venv", "env", ".env",
    ".idea", ".vscode", "coverage", ".cache", "tmp",
    "temp", ".pytest_cache", "eggs", ".eggs",
    "htmlcov", ".tox", "site-packages",
}

# File extensions to skip (binary / media / archives)
SKIP_EXTENSIONS = {
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico",
    ".svg", ".webp", ".tiff", ".tif", ".heic",
    # Video & Audio
    ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv",
    ".mp3", ".wav", ".ogg", ".aac", ".flac", ".m4a",
    # Archives
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".rar",
    ".7z", ".zst",
    # Binaries & Executables
    ".exe", ".dll", ".so", ".dylib", ".bin", ".obj",
    ".o", ".a", ".lib", ".pyc", ".pyd",
    # Fonts
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    # Databases
    ".sqlite", ".sqlite3", ".db",
    # Documents (optional — comment out if needed)
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    # Lock files (optional)
    # ".lock",
}

# Files to skip by exact name
SKIP_FILES = {
    OUTPUT_FILE,
    SCRIPT_NAME,
    ".DS_Store",
    "Thumbs.db",
}

FILE_SEPARATOR = "=" * 68
FILE_HEADER_TAG = "// File: "

# ─────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────
def print_banner():
    banner = f"""
{clr('╔══════════════════════════════════════════════════════╗', C.CYAN, bold=True)}
{clr('║', C.CYAN)}  {clr('PROJECT PACKER / UNPACKER TOOL', C.WHITE, bold=True)}{' ' * 22}{clr('║', C.CYAN)}
{clr('║', C.CYAN)}  {clr('Pack → Modify → Unpack → Rebuild 🚀', C.MAGENTA)}{' ' * 17}{clr('║', C.CYAN)}
{clr('╚══════════════════════════════════════════════════════╝', C.CYAN, bold=True)}"""
    print(banner)

def print_menu():
    print(clr("\n  Choose an operation:", C.WHITE, bold=True))
    print(clr("  ─────────────────────────────────────────────", C.DIM))
    print(f"  {clr('[1]', C.CYAN, bold=True)} {clr('Pack Project', C.WHITE, bold=True)}"
          f"   {clr('→ Collect all files into one txt', C.DIM)}")
    print(f"  {clr('[2]', C.GREEN, bold=True)} {clr('Unpack Project', C.WHITE, bold=True)}"
          f" {clr('→ Rebuild project from txt file', C.DIM)}")
    print(f"  {clr('[0]', C.RED,  bold=True)} {clr('Exit', C.WHITE, bold=True)}")
    print(clr("  ─────────────────────────────────────────────", C.DIM))

def get_project_root():
    return Path.cwd()

def should_skip_dir(name: str) -> bool:
    return name in SKIP_DIRS or name.startswith(".")

def should_skip_file(file_path: Path) -> bool:
    if file_path.name in SKIP_FILES:
        return True
    if file_path.suffix.lower() in SKIP_EXTENSIONS:
        return True
    # Skip hidden files
    if file_path.name.startswith("."):
        return True
    return False

def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024**2):.1f} MB"

# ─────────────────────────────────────────────
#  TREE BUILDER
# ─────────────────────────────────────────────
def build_tree(root: Path, prefix: str = "", is_last: bool = True) -> list:
    lines = []
    try:
        entries = sorted(root.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    except PermissionError:
        return lines

    entries = [
        e for e in entries
        if not (e.is_dir() and should_skip_dir(e.name))
        and not (e.is_file() and should_skip_file(e))
    ]

    for i, entry in enumerate(entries):
        is_last_entry = (i == len(entries) - 1)
        connector = "└── " if is_last_entry else "├── "
        lines.append(prefix + connector + entry.name + ("/" if entry.is_dir() else ""))
        if entry.is_dir():
            extension = "    " if is_last_entry else "│   "
            lines.extend(build_tree(entry, prefix + extension, is_last_entry))
    return lines

# ─────────────────────────────────────────────
#  PACK — MODE 1
# ─────────────────────────────────────────────
def pack_project():
    root = get_project_root()
    project_name = root.name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_path = root / OUTPUT_FILE

    print(clr(f"\n📂 Scanning: {root}", C.CYAN))
    print(clr("   Building project tree...", C.DIM))

    # Build tree
    tree_lines = build_tree(root)
    tree_str = f"{project_name}/\n" + "\n".join(tree_lines)

    # Collect all files
    all_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Remove skipped dirs in-place to prevent descent
        dirnames[:] = [
            d for d in sorted(dirnames)
            if not should_skip_dir(d)
        ]
        for fname in sorted(filenames):
            fpath = Path(dirpath) / fname
            if not should_skip_file(fpath):
                all_files.append(fpath)

    if not all_files:
        print(clr("⚠️  No files found to pack!", C.YELLOW))
        return

    print(clr(f"   Found {len(all_files)} file(s) to pack.", C.DIM))

    # Write output file
    total_size = 0
    packed_count = 0
    errors = []

    try:
        with open(output_path, "w", encoding="utf-8", errors="replace") as out:
            # ── Header ──────────────────────────────────
            out.write(FILE_SEPARATOR + "\n")
            out.write(f" PROJECT : {project_name}\n")
            out.write(f" PACKED  : {timestamp}\n")
            out.write(f" FILES   : {len(all_files)}\n")
            out.write(FILE_SEPARATOR + "\n\n")

            # ── Project Tree ────────────────────────────
            out.write("PROJECT STRUCTURE:\n")
            out.write(FILE_SEPARATOR + "\n")
            out.write(tree_str + "\n")
            out.write(FILE_SEPARATOR + "\n\n")

            # ── File Contents ───────────────────────────
            for fpath in all_files:
                rel = fpath.relative_to(root)
                rel_str = rel.as_posix()

                try:
                    content = fpath.read_text(encoding="utf-8", errors="replace")
                    file_size = fpath.stat().st_size

                    out.write(FILE_SEPARATOR + "\n")
                    out.write(f"{FILE_HEADER_TAG}{rel_str}\n")
                    out.write(FILE_SEPARATOR + "\n")
                    out.write(content)
                    if not content.endswith("\n"):
                        out.write("\n")
                    out.write("\n")

                    total_size += file_size
                    packed_count += 1
                    print(f"   {clr('📄', C.BLUE)} {clr(rel_str, C.DIM)}"
                          f"  {clr(format_size(file_size), C.YELLOW)}")

                except Exception as e:
                    errors.append((rel_str, str(e)))
                    print(f"   {clr('⚠️  Skip (error):', C.YELLOW)} {rel_str} → {e}")

    except IOError as e:
        print(clr(f"\n❌ Cannot write output file: {e}", C.RED, bold=True))
        return

    # ── Summary ────────────────────────────────────
    print()
    print(clr("  " + "─" * 50, C.DIM))
    print(clr(f"  ✅  Pack complete!", C.GREEN, bold=True))
    print(clr(f"  📄  Output  → {OUTPUT_FILE}", C.CYAN))
    print(clr(f"  🗂️   Files   → {packed_count} packed", C.WHITE))
    print(clr(f"  📦  Total   → {format_size(total_size)}", C.WHITE))
    if errors:
        print(clr(f"  ⚠️   Errors  → {len(errors)} file(s) skipped", C.YELLOW))
    print(clr("  " + "─" * 50, C.DIM))

# ─────────────────────────────────────────────
#  UNPACK — MODE 2
# ─────────────────────────────────────────────
def unpack_project():
    root = get_project_root()
    source_path = root / OUTPUT_FILE

    print(clr(f"\n🔍 Looking for: {OUTPUT_FILE}", C.CYAN))

    if not source_path.exists():
        print(clr(f"\n❌ File not found: {OUTPUT_FILE}", C.RED, bold=True))
        print(clr(f"   Run Pack Project (option 1) first.", C.DIM))
        return

    file_size = format_size(source_path.stat().st_size)
    print(clr(f"   ✓ Found! Size: {file_size}", C.GREEN))

    # Ask for output directory
    print(clr(f"\n📁 Output directory: {clr(UNPACK_DIR, C.YELLOW)}", C.WHITE))
    target_root = root / UNPACK_DIR

    if target_root.exists():
        print(clr(f"   ⚠️  Directory already exists — files will be overwritten!", C.YELLOW))

    confirm = input(clr("   Proceed? (yes / no): ", C.WHITE)).strip().lower()
    if confirm not in ("yes", "y"):
        print(clr("   ✗ Cancelled.", C.RED))
        return

    # Parse and write files
    restored_count = 0
    errors = []
    current_file_path = None
    current_lines = []

    def flush_file():
        """Write buffered lines to the current file."""
        nonlocal restored_count
        if current_file_path is None:
            return
        try:
            full_path = target_root / current_file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text("".join(current_lines), encoding="utf-8")
            restored_count += 1
            rel = Path(current_file_path).as_posix()
            print(f"   {clr('📄', C.GREEN)} {clr(rel, C.DIM)}")
        except Exception as e:
            errors.append((str(current_file_path), str(e)))
            print(clr(f"   ⚠️  Error writing {current_file_path}: {e}", C.YELLOW))

    print(clr("\n📦 Unpacking files...\n", C.CYAN))

    try:
        with open(source_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith(FILE_HEADER_TAG):
                    # Save previous file
                    flush_file()
                    # Start new file
                    rel_path_str = line[len(FILE_HEADER_TAG):].strip()
                    current_file_path = rel_path_str
                    current_lines = []
                elif line.startswith("=" * 10):
                    # Separator — skip
                    continue
                else:
                    if current_file_path is not None:
                        current_lines.append(line)

        # Flush last file
        flush_file()

    except IOError as e:
        print(clr(f"\n❌ Cannot read {OUTPUT_FILE}: {e}", C.RED, bold=True))
        return

    # ── Summary ────────────────────────────────────
    print()
    print(clr("  " + "─" * 50, C.DIM))
    print(clr(f"  ✅  Unpack complete!", C.GREEN, bold=True))
    print(clr(f"  📁  Location → ./{UNPACK_DIR}/", C.CYAN))
    print(clr(f"  🗂️   Restored → {restored_count} file(s)", C.WHITE))
    if errors:
        print(clr(f"  ⚠️   Errors  → {len(errors)} file(s) failed", C.YELLOW))
        for fp, err in errors:
            print(clr(f"       • {fp}: {err}", C.DIM))
    print(clr("  " + "─" * 50, C.DIM))

# ─────────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────────
def main():
    # Enable ANSI on Windows
    if sys.platform == "win32":
        os.system("")

    print_banner()

    while True:
        print_menu()
        try:
            choice = input(clr("  → Enter your choice: ", C.WHITE, bold=True)).strip()
        except (KeyboardInterrupt, EOFError):
            print(clr("\n\n  Bye! 👋", C.CYAN))
            sys.exit(0)

        if choice == "1":
            pack_project()
        elif choice == "2":
            unpack_project()
        elif choice == "0":
            print(clr("\n  Bye! 👋\n", C.CYAN))
            sys.exit(0)
        else:
            print(clr("  ❌  Invalid choice. Please enter 1, 2, or 0.", C.RED))

        print()
        again = input(clr("  ↩  Return to menu? (Enter to continue / q to quit): ",
                          C.DIM)).strip().lower()
        if again in ("q", "quit", "exit", "0"):
            print(clr("\n  Bye! 👋\n", C.CYAN))
            sys.exit(0)

if __name__ == "__main__":
    main()
