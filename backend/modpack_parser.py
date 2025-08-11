import os
import json
from typing import List, Dict, Any, Tuple


def _strip_ns(identifier: str) -> str:
    if not identifier:
        return identifier
    return identifier.split(":", 1)[-1]


def _parse_shaped_recipe(recipe_json: Dict[str, Any]) -> Tuple[List[List[str]], Dict[str, str], str, int]:
    """Parse a shaped crafting recipe JSON into a 3x3 grid of labels.
    Returns (grid, key_map, result_id, result_count)
    """
    pattern = recipe_json.get("pattern", [])
    key = recipe_json.get("key", {})
    result = recipe_json.get("result", {})

    # Handle both legacy and modern result schema
    if isinstance(result, dict):
        result_id = result.get("item") or result.get("id") or "unknown"
        result_count = result.get("count", 1)
    elif isinstance(result, str):
        result_id = result
        result_count = 1
    else:
        result_id = "unknown"
        result_count = 1

    # Build symbol -> label map
    symbol_to_label: Dict[str, str] = {}
    for sym, spec in key.items():
        if isinstance(spec, dict):
            # spec may be {"item":"ns:id"} or {"tag":"ns:tag"}
            item = spec.get("item") or spec.get("id") or spec.get("tag") or ""
            label = _strip_ns(item).replace("_", " ")[:10]
            symbol_to_label[sym] = label
        else:
            symbol_to_label[sym] = str(spec)

    # Normalize to 3 rows of length 3
    rows = [list(r) for r in pattern]
    while len(rows) < 3:
        rows.append([" "])
    rows = rows[:3]
    norm_rows: List[List[str]] = []
    for r in rows:
        if len(r) < 3:
            r = r + [" "] * (3 - len(r))
        else:
            r = r[:3]
        norm_rows.append(r)

    grid: List[List[str]] = [[None for _ in range(3)] for _ in range(3)]
    for i in range(3):
        for j in range(3):
            sym = norm_rows[i][j]
            if sym == " " or sym is None:
                grid[i][j] = None
            else:
                grid[i][j] = symbol_to_label.get(sym, sym)

    return grid, symbol_to_label, result_id, result_count


def _collect_recipe_docs(recipes_root: str) -> Tuple[List[Dict[str, Any]], int]:
    docs: List[Dict[str, Any]] = []
    count = 0
    for root, _, files in os.walk(recipes_root):
        for fn in files:
            if not fn.endswith('.json'):
                continue
            fpath = os.path.join(root, fn)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                rtype = data.get("type", "")
                # Shaped crafting recipes (common types)
                if 'crafting_shaped' in rtype or 'minecraft:crafting_shaped' in rtype:
                    grid, keymap, result_id, result_count = _parse_shaped_recipe(data)
                    text = f"Shaped recipe for {_strip_ns(result_id)} x{result_count}: keys={keymap}"
                    docs.append({
                        'type': 'recipe',
                        'subtype': 'crafting_shaped',
                        'result_id': result_id,
                        'result_count': result_count,
                        'grid': grid,
                        'source': fpath,
                        'text': text
                    })
                    count += 1
                else:
                    # Other recipe types -> store brief text for search context
                    result = data.get('result')
                    rid = None
                    if isinstance(result, dict):
                        rid = result.get('item') or result.get('id')
                    elif isinstance(result, str):
                        rid = result
                    text = f"Recipe type={rtype} result={_strip_ns(rid) if rid else 'unknown'}"
                    docs.append({
                        'type': 'recipe',
                        'subtype': 'other',
                        'result_id': rid or 'unknown',
                        'source': fpath,
                        'text': text
                    })
                    count += 1
            except Exception:
                # Ignore malformed recipe files
                continue
    return docs, count


def _collect_mod_list(mods_dir: str) -> Tuple[List[Dict[str, Any]], int]:
    docs: List[Dict[str, Any]] = []
    count = 0
    if not os.path.isdir(mods_dir):
        return docs, count
    try:
        for fn in sorted(os.listdir(mods_dir)):
            if fn.lower().endswith('.jar'):
                text = f"Installed mod jar: {fn}"
                docs.append({'type': 'mod', 'source': os.path.join(mods_dir, fn), 'text': text})
                count += 1
    except Exception:
        pass
    return docs, count


def _collect_kubejs(kubejs_dir: str) -> Tuple[List[Dict[str, Any]], int]:
    docs: List[Dict[str, Any]] = []
    count = 0
    if not os.path.isdir(kubejs_dir):
        return docs, count
    for root, _, files in os.walk(kubejs_dir):
        for fn in files:
            if not fn.endswith(('.js', '.txt', '.md')):
                continue
            fpath = os.path.join(root, fn)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(2000)
                content_clean = content[:300].replace('\n', ' ')
                text = f"kubejs script: {os.path.relpath(fpath, kubejs_dir)} => {content_clean}"
                docs.append({'type': 'kubejs', 'source': fpath, 'text': text})
                count += 1
            except Exception:
                continue
    return docs, count


def scan_modpack(modpack_path: str) -> Dict[str, Any]:
    """Scan a modpack directory and return docs suitable for RAG.
    Returns { 'docs': [...], 'stats': {...} }
    """
    docs: List[Dict[str, Any]] = []
    stats = {'recipes': 0, 'mods': 0, 'kubejs': 0}

    if not modpack_path or not os.path.isdir(modpack_path):
        return {'docs': [], 'stats': stats}

    # recipes under data/**/recipes
    data_dir = os.path.join(modpack_path, 'data')
    if os.path.isdir(data_dir):
        rdocs, rcount = _collect_recipe_docs(data_dir)
        docs.extend(rdocs)
        stats['recipes'] = rcount

    # mods list
    mdocs, mcount = _collect_mod_list(os.path.join(modpack_path, 'mods'))
    docs.extend(mdocs)
    stats['mods'] = mcount

    # kubejs scripts
    kdocs, kcount = _collect_kubejs(os.path.join(modpack_path, 'kubejs'))
    docs.extend(kdocs)
    stats['kubejs'] = kcount

    return {'docs': docs, 'stats': stats}

