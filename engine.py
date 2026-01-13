from __future__ import annotations

import logging
from logger import setup_logger

# Initialize logger once
log = setup_logger().getChild("engine")


def _log(msg: str):
    log.debug(msg)


_undo_stack = []

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Tuple

from core import CATEGORY_MAP, build_name_normal, build_name_advanced


@dataclass
class RenameOperation:
    old_path: Path
    new_path: Path
    category: str


@dataclass
class RenamePlan:
    operations: List[RenameOperation]
    conflicts: List[str]
    skipped: List[str]


# ---------------------------------------------------------
# Helper: find files for a single category
# ---------------------------------------------------------
def _find_category_files(folder: Path, category_key: str, recursive: bool) -> List[Path]:
    log.debug(f"[SCAN] Category={category_key} | recursive={recursive}")

    exts = CATEGORY_MAP.get(category_key, [])
    exts = [e.lower() for e in exts]

    matched: List[Path] = []

    if recursive:
        for path in sorted(folder.rglob("*")):
            if path.is_file() and path.suffix.lower() in exts:
                matched.append(path)
    else:
        for path in sorted(folder.iterdir()):
            if path.is_file() and path.suffix.lower() in exts:
                matched.append(path)

    log.debug(f"[SCAN] Found {len(matched)} files for category '{category_key}'")
    return matched


# ---------------------------------------------------------
# Build plan for a single category
# ---------------------------------------------------------
def _build_single_category_plan(
    folder: Path,
    category_key: str,
    cfg: Dict,
    recursive: bool,
    selected_files: List[str] | None = None,
) -> RenamePlan:

    conflicts: List[str] = []
    skipped: List[str] = []
    ops: List[RenameOperation] = []

    files = _find_category_files(folder, category_key, recursive)
    log.debug(f"[PLAN] Building plan for category='{category_key}' | files={len(files)}")

    if not files:
        return RenamePlan([], [f"No '{category_key}' files found."], [])

    # If selective renaming is enabled, filter files
    if selected_files:
        files = [f for f in files if f.name in selected_files]

    counter = cfg["start"]
    new_path_counts: Dict[Path, int] = {}

    for file_path in files:
        base_name = file_path.stem
        ext = file_path.suffix

        # Build new base name
        if cfg["advanced_mode"] and cfg["advanced_text"]:
            new_base = build_name_advanced(
                pattern=cfg["advanced_text"],
                original_name=base_name,
                index=counter,
                padding=cfg["padding"],
                prefix=cfg["prefix"],
                suffix=cfg["suffix"],
                category=category_key,
                folder=str(file_path.parent),
            )
        else:
            new_base = build_name_normal(
                original_name=base_name,
                index=counter,
                padding=cfg["padding"],
                prefix=cfg["prefix"],
                suffix=cfg["suffix"],
                category=category_key,
                folder=str(file_path.parent),
            )

        new_path = file_path.parent / (new_base + ext)

        # Skip pure no-op renames
        old_norm = str(file_path).lower()
        new_norm = str(new_path).lower()

        if old_norm == new_norm:
            skipped.append(f"No-op (unchanged): {file_path.name}")
            log.debug(f"[PLAN] Skipped no-op: {file_path.name}")
        else:
            ops.append(RenameOperation(file_path, new_path, category_key))
            new_path_counts[new_path] = new_path_counts.get(new_path, 0) + 1
            log.debug(f"[PLAN] New name: {file_path.name} → {new_path.name}")

        counter += 1

    # Internal conflicts (same category)
    for target, count in new_path_counts.items():
        if count > 1:
            conflicts.append(
                f"Internal conflict in '{category_key}': {count} files want '{target.name}'"
            )
            log.debug(f"[PLAN] Internal conflict: {count} files want '{target.name}'")

    return RenamePlan(ops, conflicts, skipped)


# ---------------------------------------------------------
# Build a unified multi-category plan
# ---------------------------------------------------------
def build_multi_plan(
    folder: str,
    config: Dict,
    recursive: bool,
    selected_files: List[str] | None = None,
) -> RenamePlan:

    log.info(f"[PLAN] Building multi-category plan | folder={folder} | recursive={recursive}")

    base_folder = Path(folder)
    if not base_folder.is_dir():
        return RenamePlan([], [f"Folder does not exist: {folder}"], [])

    all_ops: List[RenameOperation] = []
    all_conflicts: List[str] = []
    all_skipped: List[str] = []

    # -----------------------------------------------------
    # Per-category processing
    # -----------------------------------------------------
    for category_key, cfg in config.items():

        # Log category state BEFORE skipping
        log.debug(f"[PLAN] Category '{category_key}' enabled={cfg.get('enabled')}")

        if not cfg.get("enabled", False):
            continue

        subplan = _build_single_category_plan(
            base_folder, category_key, cfg, recursive, selected_files
        )

        # Log subplan details
        log.debug(
            f"[PLAN] Subplan for '{category_key}': "
            f"ops={len(subplan.operations)} "
            f"conflicts={len(subplan.conflicts)} "
            f"skipped={len(subplan.skipped)}"
        )

        all_ops.extend(subplan.operations)
        all_conflicts.extend(subplan.conflicts)
        all_skipped.extend(subplan.skipped)

    # -----------------------------------------------------
    # Cross-category conflict detection
    # -----------------------------------------------------
    target_counts: Dict[Path, int] = {}
    for op in all_ops:
        target_counts[op.new_path] = target_counts.get(op.new_path, 0) + 1

    for target, count in target_counts.items():
        if count > 1:
            log.error(f"[PLAN] Cross-category conflict: {count} files want '{target.name}'")
            all_conflicts.append(
                f"Cross-category conflict: {count} files want '{target.name}'"
            )

    return RenamePlan(all_ops, all_conflicts, all_skipped)


# ---------------------------------------------------------
# Validate plan against filesystem
# ---------------------------------------------------------
def validate_plan(plan: RenamePlan) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    log.debug(f"[VALIDATE] Validating plan with {len(plan.operations)} operations")

    if not plan.operations:
        return False, ["No rename operations in plan."]

    old_paths = {op.old_path for op in plan.operations}

    for op in plan.operations:
        if op.new_path.exists() and op.new_path not in old_paths:
            log.error(f"[VALIDATE] Target exists: {op.new_path}")
            errors.append(f"Target already exists: {op.new_path}")

    # Log conflicts explicitly
    for conflict in plan.conflicts:
        log.error(f"[VALIDATE] Conflict: {conflict}")

    errors.extend(plan.conflicts)

    return (len(errors) == 0), errors


# ---------------------------------------------------------
# Execute plan
# ---------------------------------------------------------
def execute_plan(plan: RenamePlan) -> Tuple[int, List[str]]:
    """
    Execute the rename plan.
    - Performs all renames in order
    - Returns (count, failures)
    - Pushes the plan onto the undo stack ONLY if all renames succeed
    """
    import os
    global _undo_stack

    # Stable ordering
    plan.operations.sort(key=lambda op: op.old_path.name.lower())
    log.info(f"[EXECUTE] Starting rename | operations={len(plan.operations)}")

    renamed_count = 0
    failures: List[str] = []

    for op in plan.operations:
        try:
            os.rename(op.old_path, op.new_path)
            renamed_count += 1
            log.debug(f"[EXECUTE] {op.old_path} → {op.new_path}")
        except OSError as e:
            msg = f"Failed: {op.old_path} → {op.new_path}: {e}"
            failures.append(msg)
            log.error(f"[EXECUTE] {msg}")

    _log(f"Renamed {renamed_count}/{len(plan.operations)} files.")

    # Only push to undo stack if everything succeeded
    if renamed_count == len(plan.operations):
        _undo_stack.append(plan)
        log.debug(f"[EXECUTE] Undo stack size after push: {len(_undo_stack)}")
    else:
        _log("Not pushing to undo stack due to failures.")

    log.info(f"[EXECUTE] Completed | renamed={renamed_count} | failures={len(failures)}")
    return renamed_count, failures


# ---------------------------------------------------------
# Undo last successful rename (multi-level undo)
# ---------------------------------------------------------
def undo_last_rename() -> Tuple[int, List[str]]:
    """
    Undo the last rename operation if possible.
    Supports multi-level undo via the undo stack.
    """
    import os
    global _undo_stack

    if not _undo_stack:
        return 0, ["No undo available."]

    last_plan = _undo_stack.pop()
    log.info("[UNDO] Undo requested")
    log.debug(f"[UNDO] Undo stack size before pop: {len(_undo_stack) + 1}")

    # Keep ordering consistent
    last_plan.operations.sort(key=lambda op: op.old_path.name.lower())

    # Reverse operations
    reversed_ops = [
        RenameOperation(
            old_path=op.new_path,
            new_path=op.old_path,
            category=op.category,
        )
        for op in last_plan.operations
    ]

    undo_plan = RenamePlan(
        operations=reversed_ops,
        conflicts=[],
        skipped=[],
    )

    # Validate undo plan
    ok, errors = validate_plan(undo_plan)

    if not ok:
        _log("Undo validation failed:")
        for err in errors:
            _log(f"  {err}")
            log.error(f"[UNDO] Validation failed: {err}")
        return 0, errors

    # Execute undo
    renamed_count = 0
    failures: List[str] = []

    for op in undo_plan.operations:
        try:
            os.rename(op.old_path, op.new_path)
            renamed_count += 1
        except OSError as e:
            msg = f"Failed: {op.old_path} → {op.new_path}: {e}"
            _log(f"Undo failed: {msg}")
            log.error(f"[UNDO] {msg}")
            failures.append(msg)

    _log(f"Undo restored {renamed_count}/{len(undo_plan.operations)} files.")
    log.info(f"[UNDO] Restored {renamed_count}/{len(undo_plan.operations)} files")

    return renamed_count, failures
