from pathlib import Path
from logger import setup_logger
log = setup_logger()

# ---------------------------------------------------------
# Category → extensions
# ---------------------------------------------------------

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".bmp", ".tiff", ".heif"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
GIF_EXTS   = {".gif"}
AUDIO_EXTS = {".mp3", ".wav", ".aac", ".flac"}
DOCUMENT_EXTS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".odt", ".rtf", ".md", ".epub"
}

CATEGORY_MAP = {
    "image": IMAGE_EXTS,
    "video": VIDEO_EXTS,
    "gif": GIF_EXTS,
    "audio": AUDIO_EXTS,
    "document": DOCUMENT_EXTS,
}

# ---------------------------------------------------------
# Normal Mode
# ---------------------------------------------------------
def build_name_normal(
    original_name: str,
    index: int,
    padding: int,
    prefix: str,
    suffix: str,
    category: str,
    folder: str,
):
    """
    Normal Mode: prefix + padded index + suffix
    """
    log.debug(f"[NAME_NORMAL] {original_name} → prefix='{prefix}' index={index} padding={padding} suffix='{suffix}'")

    if padding > 0:
        num_str = f"{index:0{padding}d}"
    else:
        num_str = str(index)

    return f"{prefix}{num_str}{suffix}"


# ---------------------------------------------------------
# Advanced Mode
# ---------------------------------------------------------
def build_name_advanced(
    pattern: str,
    original_name: str,
    index: int,
    padding: int,
    prefix: str,
    suffix: str,
    category: str,
    folder: str,
):
    """
    Advanced Mode: user-defined pattern with variables.

    Supported variables:
        {original}      → original filename without extension
        {num}           → index (un-padded)
        {num_padded}    → index with padding
        {prefix}        → prefix text
        {suffix}        → suffix text
        {category}      → category key (image, video, etc.)
        {folder}        → parent folder path
    """
    log.debug(f"[NAME_ADV] pattern='{pattern}' original='{original_name}' index={index} padded='{num_padded}'")

    # Build padded index
    if padding > 0:
        num_padded = f"{index:0{padding}d}"
    else:
        num_padded = str(index)

    return pattern.format(
        original=original_name,
        num=index,
        num_padded=num_padded,
        prefix=prefix,
        suffix=suffix,
        category=category,
        folder=folder,
    )
