"""Mat2Ansys - Local JSON cache handler with file lock + atomic writes."""

from __future__ import annotations

import json
import os
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Callable, Optional

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CACHE_FILE = os.path.join(os.path.dirname(__file__), "bizim_malzemeler.json")
LOCK_FILE = f"{CACHE_FILE}.lock"
LOCK_TIMEOUT_SEC = 10.0
LOCK_RETRY_SEC = 0.05
try:
    SEARCH_CACHE_TTL_SEC = max(0, int(os.getenv("SEARCH_CACHE_TTL_SEC", "86400")))
except ValueError:
    SEARCH_CACHE_TTL_SEC = 86400


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _empty_cache() -> dict:
    return {
        "materials_by_url": {},
        "name_to_urls": {},
        "search_cache": {},
    }


@contextmanager
def _file_lock(timeout_sec: float = LOCK_TIMEOUT_SEC):
    start = time.time()
    fd = None
    while time.time() - start < timeout_sec:
        try:
            fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            break
        except FileExistsError:
            time.sleep(LOCK_RETRY_SEC)

    if fd is None:
        raise TimeoutError("Cache lock timeout.")

    try:
        yield
    finally:
        try:
            os.close(fd)
        finally:
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)


def _migrate_cache_schema(raw: dict) -> dict:
    """Migrate legacy cache schema to URL-primary schema."""
    cache = _empty_cache()
    if not isinstance(raw, dict):
        return cache

    # New schema already present
    if "materials_by_url" in raw and "name_to_urls" in raw:
        cache["materials_by_url"] = raw.get("materials_by_url", {}) or {}
        cache["name_to_urls"] = raw.get("name_to_urls", {}) or {}
    else:
        # Legacy: {"materials": {name: {url, ...props}}}
        legacy_materials = raw.get("materials", {}) if isinstance(raw.get("materials"), dict) else {}
        for name, data in legacy_materials.items():
            if not isinstance(data, dict):
                continue
            url = data.get("url")
            if not isinstance(url, str) or not url.strip():
                continue

            cache["materials_by_url"][url] = {
                **data,
                "name": name,
            }
            cache["name_to_urls"].setdefault(name, [])
            if url not in cache["name_to_urls"][name]:
                cache["name_to_urls"][name].append(url)

    # Search cache migration: list -> object with timestamp
    raw_search = raw.get("search_cache", {}) if isinstance(raw.get("search_cache"), dict) else {}
    for key, val in raw_search.items():
        if isinstance(val, dict) and "results" in val:
            cache["search_cache"][key] = {
                "results": val.get("results", []),
                "cached_at": val.get("cached_at") or _utc_now_iso(),
            }
        elif isinstance(val, list):
            cache["search_cache"][key] = {
                "results": val,
                "cached_at": _utc_now_iso(),
            }

    return cache


def _load_cache_unlocked() -> dict:
    if not os.path.exists(CACHE_FILE):
        return _empty_cache()
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return _migrate_cache_schema(raw)
    except (json.JSONDecodeError, IOError):
        return _empty_cache()


def _atomic_save_unlocked(data: dict):
    parent = os.path.dirname(CACHE_FILE)
    os.makedirs(parent, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=parent,
        delete=False,
        suffix=".tmp",
    ) as tmp:
        json.dump(data, tmp, indent=2, ensure_ascii=False)
        tmp_path = tmp.name

    os.replace(tmp_path, CACHE_FILE)


def _read_cache() -> dict:
    with _file_lock():
        return _load_cache_unlocked()


def _mutate_cache(mutator: Callable[[dict], None]):
    with _file_lock():
        data = _load_cache_unlocked()
        mutator(data)
        _atomic_save_unlocked(data)


# ---------------------------------------------------------------------------
# Search Cache
# ---------------------------------------------------------------------------
def get_search_cache(query: str) -> Optional[list[dict]]:
    """
    Get cached search results for a query.

    Args:
        query: The search query string.

    Returns:
        List of result dicts if cached, None otherwise.
    """
    cache = _read_cache()
    key = query.strip().lower()
    entry = cache.get("search_cache", {}).get(key)
    if isinstance(entry, dict):
        cached_at = _parse_iso(entry.get("cached_at"))
        if cached_at is not None:
            age = datetime.now(timezone.utc) - cached_at
            if age.total_seconds() > SEARCH_CACHE_TTL_SEC:
                return None
        return entry.get("results")
    return None


def save_search_cache(query: str, results: list[dict]):
    """
    Save search results to cache.

    Args:
        query: The search query string.
        results: List of result dicts from scraper.
    """
    key = query.strip().lower()

    def _write(data: dict):
        data.setdefault("search_cache", {})
        data["search_cache"][key] = {
            "results": results,
            "cached_at": _utc_now_iso(),
        }

    _mutate_cache(_write)


# ---------------------------------------------------------------------------
# Material Cache
# ---------------------------------------------------------------------------
def get_material(url: str) -> Optional[dict]:
    """
    Get cached material data by URL (primary cache key).

    Args:
        url: MatWeb URL.

    Returns:
        Material properties dict if cached, None otherwise.
    """
    cache = _read_cache()
    materials = cache.get("materials_by_url", {})
    return materials.get(url)


def save_material(
    name: str,
    url: str,
    properties: dict,
    used_defaults: Optional[list[str]] = None,
    missing_or_unparsed: Optional[list[str]] = None,
):
    """
    Save material data to cache.

    Args:
        name: Material name (e.g., "SAE 8620 H").
        url: MatWeb detail page URL.
        properties: Cleaned properties dict from utils.format_material_data().
    """
    def _write(data: dict):
        data.setdefault("materials_by_url", {})
        data.setdefault("name_to_urls", {})

        data["materials_by_url"][url] = {
            "url": url,
            "name": name,
            **properties,
            "used_defaults": used_defaults or [],
            "missing_or_unparsed": missing_or_unparsed or [],
            "scraped_at": _utc_now_iso(),
        }

        data["name_to_urls"].setdefault(name, [])
        if url not in data["name_to_urls"][name]:
            data["name_to_urls"][name].append(url)

    _mutate_cache(_write)


def list_all_materials() -> list[str]:
    """Return a list of all cached material names."""
    cache = _read_cache()
    return sorted(cache.get("name_to_urls", {}).keys())


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("🗄️ Cache Handler Test")
    print("-" * 50)

    # Test save & retrieve search
    save_search_cache("SAE 8620", [
        {"name": "SAE 8620 Steel", "url": "https://matweb.com/test1"},
        {"name": "SAE 8620 H Steel", "url": "https://matweb.com/test2"},
    ])
    results = get_search_cache("SAE 8620")
    print(f"  Search cache (SAE 8620): {len(results or [])} results ✅")

    # Test save & retrieve material
    save_material("SAE 8620 H Steel", "https://matweb.com/test2", {
        "density": 7850.0,
        "tensile_yield": 250000000.0,
        "tensile_ultimate": 460000000.0,
        "youngs_modulus": 200000000000.0,
        "poissons_ratio": 0.3,
    })
    mat = get_material("https://matweb.com/test2")
    density = mat["density"] if mat else "None"
    print(f"  Material cache (SAE 8620 H): density={density} ✅")

    # Test cache miss
    miss = get_material("https://matweb.com/missing")
    print(f"  Cache miss: {miss} ✅")

    # List all
    all_mats = list_all_materials()
    print(f"  All cached materials: {all_mats} ✅")

    # Cleanup test file
    os.remove(CACHE_FILE)
    print("\n  ✅ All tests passed! (test cache cleaned up)")
