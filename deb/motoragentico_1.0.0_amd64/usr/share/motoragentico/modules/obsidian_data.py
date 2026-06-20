import re
from pathlib import Path
from datetime import datetime, timezone, timedelta


def _parse_frontmatter(text: str) -> dict:
    tags = []
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            fm = text[3:end]
            m = re.search(r"tags:\s*\[([^\]]+)\]", fm)
            if m:
                tags = [t.strip().strip('"\'') for t in m.group(1).split(",")]
            else:
                for line in fm.split("\n"):
                    if line.strip().startswith("- "):
                        tags.append(line.strip()[2:].strip())
    inline = re.findall(r"#([\w/-]+)", text)
    tags.extend(inline)
    return {"tags": list(set(tags))}


def scan_vault(vault_path: str) -> dict:
    root = Path(vault_path).expanduser()
    if not root.exists():
        return {"error": f"Vault no encontrado en: {vault_path}", "files": []}

    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(days=90)
    files = []
    tag_counts: dict[str, int] = {}
    total_words = 0

    for md_file in root.rglob("*.md"):
        try:
            stat = md_file.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            words = len(content.split())
            fm = _parse_frontmatter(content)

            for tag in fm["tags"]:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

            total_words += words
            files.append({
                "name": md_file.name,
                "path": str(md_file.relative_to(root)),
                "size_bytes": stat.st_size,
                "words": words,
                "modified": mtime,
                "tags": fm["tags"],
                "is_stale": mtime < stale_cutoff,
                "days_since_edit": (now - mtime).days,
            })
        except Exception:
            continue

    files.sort(key=lambda f: f["modified"], reverse=True)
    stale = [f for f in files if f["is_stale"]]
    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:15]

    return {
        "error": None,
        "total_files": len(files),
        "total_words": total_words,
        "stale_count": len(stale),
        "stale_files": stale[:20],
        "recent_files": files[:10],
        "all_files": files,
        "top_tags": top_tags,
    }
