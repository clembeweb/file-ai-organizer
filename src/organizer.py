
import hashlib, json, os, shutil, time
from pathlib import Path
from ai_utils import extract_text, cluster_texts, suggest_filename

DEFAULT_RULES = {
    "delete_extensions": [".tmp", ".bak", ".log"],
    "delete_older_than_days": 30,
    "group_by_extension": True,
    "group_by_content": False,
    "smart_rename": False
}

def sha1sum(path, chunk_size=65536):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            h.update(chunk)
    return h.hexdigest()

def scan_directory(root:str, rules:dict=None):
    """Returns list of actions suggested for files under root."""
    rules = (rules or DEFAULT_RULES).copy()
    actions = []
    seen_hash = {}
    texts = {}
    now = time.time()
    cutoff = now - rules['delete_older_than_days']*86400
    root_path = Path(root)
    if not root_path.exists():
        raise FileNotFoundError(root)
    for path in root_path.rglob('*'):
        if not path.is_file():
            continue
        try:
            h = sha1sum(path)
        except Exception:
            continue
        if h in seen_hash:
            actions.append({'action':'delete_duplicate','target':str(path),
                            'duplicate_of':str(seen_hash[h])})
            continue
        else:
            seen_hash[h]=path
        # temp files
        if path.suffix.lower() in rules['delete_extensions'] and path.stat().st_mtime < cutoff:
            actions.append({'action':'delete_temp','target':str(path),'reason':'old_temp_file'})
            continue
        # text extraction if content grouping or smart rename is enabled
        if rules.get('group_by_content') or rules.get('smart_rename'):
            text = extract_text(str(path))
            if text:
                texts[str(path)] = text
        # group by extension if content grouping is disabled
        if rules.get('group_by_extension') and not rules.get('group_by_content'):
            dst_folder = path.parent / path.suffix.lower().lstrip('.')
            if path.parent != dst_folder:
                proposed = dst_folder / path.name
                actions.append({'action':'move_to_extension_folder','target':str(path),'destination':str(proposed)})
    cluster_map = {}
    if rules.get('group_by_content'):
        cluster_map = cluster_texts(texts)
        if not rules.get('smart_rename'):
            for file_path, cluster_id in cluster_map.items():
                dst_folder = root_path / f"cluster_{cluster_id}"
                dest_path = dst_folder / Path(file_path).name
                actions.append({'action':'move_to_content_folder','target':file_path,'destination':str(dest_path)})
    if rules.get('smart_rename'):
        if not cluster_map and rules.get('group_by_content'):
            cluster_map = cluster_texts(texts)
        for file_path, text in texts.items():
            new_name = suggest_filename(text, file_path)
            if rules.get('group_by_content'):
                cluster_id = cluster_map.get(file_path, 0)
                dest_dir = root_path / f"cluster_{cluster_id}"
            elif rules.get('group_by_extension', True):
                dest_dir = Path(file_path).parent / Path(file_path).suffix.lower().lstrip('.')
            else:
                dest_dir = Path(file_path).parent
            dest_path = dest_dir / new_name
            actions.append({'action':'rename_file','target':file_path,'destination':str(dest_path)})
    return actions

def apply_actions(actions:list):
    """Apply the provided actions in place. Returns summary dict."""
    summary = {'deleted':0,'moved':0,'errors':0,'renamed':0}
    for act in actions:
        try:
            if act['action'].startswith('delete'):
                os.remove(act['target'])
                summary['deleted']+=1
            elif act['action'] in ('move_to_extension_folder', 'move_to_content_folder'):
                dst = Path(act['destination'])
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(act['target'], dst)
                summary['moved']+=1
            elif act['action'] == 'rename_file':
                dst = Path(act['destination'])
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(act['target'], dst)
                summary['moved']+=1
                summary['renamed']+=1
        except Exception as e:
            act['error']=str(e)
            summary['errors']+=1
    return summary
