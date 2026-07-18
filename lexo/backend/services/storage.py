"""Local-disk object storage helper.

Writes under settings.upload_dir. Returns only storage_key strings to callers —
never credentials or absolute machine paths.
"""

from pathlib import Path

from config import settings


def _upload_root() -> Path:
    root = Path(settings.upload_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _safe_path(key: str) -> Path:
    """Resolve key under upload_dir; reject path traversal / absolute keys."""
    if not key or not str(key).strip():
        raise ValueError("storage key must be a non-empty relative path")
    key = str(key).strip().replace("\\", "/")
    if key.startswith("/") or key.startswith("../") or "/../" in f"/{key}/":
        raise ValueError("storage key must stay inside the upload directory")
    if Path(key).is_absolute():
        raise ValueError("storage key must be a relative path")

    root = _upload_root()
    target = (root / key).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError("storage key must stay inside the upload directory") from exc
    return target


def upload_file(data: bytes, key: str) -> str:
    """Write bytes to upload_dir/key. Returns the storage_key (same as key)."""
    path = _safe_path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return key


def read_file(key: str) -> bytes:
    """Read bytes for a previously stored key."""
    path = _safe_path(key)
    if not path.is_file():
        raise FileNotFoundError(f"No file for storage key: {key}")
    return path.read_bytes()


def delete_file(key: str) -> None:
    """Delete a stored file. Raises FileNotFoundError if missing."""
    path = _safe_path(key)
    if not path.is_file():
        raise FileNotFoundError(f"No file for storage key: {key}")
    path.unlink()


def get_signed_url(key: str) -> str:
    # TODO: local disk has no signed URLs; upload/serve routes should use read_file instead.
    # When S3-compatible storage is wired up, generate a short-lived URL here.
    raise NotImplementedError(
        "Signed URLs are not available with local-disk storage; use read_file instead."
    )
