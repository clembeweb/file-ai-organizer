
import hashlib, json, os, shutil, time
from pathlib import Path

DEFAULT_RULES = {
    "delete_extensions": [".tmp", ".bak", ".log"],
    "delete_older_than_days": 30,
    "group_by_extension": True
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
        # group by extension
        if rules.get('group_by_extension'):
            dst_folder = path.parent / path.suffix.lower().lstrip('.')
            if path.parent != dst_folder:
                proposed = dst_folder / path.name
                actions.append({'action':'move_to_extension_folder','target':str(path),'destination':str(proposed)})
    return actions

def apply_actions(actions:list):
    """Apply the provided actions in place. Returns summary dict."""
    summary = {'deleted':0,'moved':0,'errors':0}
    for act in actions:
        try:
            if act['action'].startswith('delete'):
                os.remove(act['target'])
                summary['deleted']+=1
            elif act['action']=='move_to_extension_folder':
                dst = Path(act['destination'])
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(act['target'], dst)
                summary['moved']+=1
        except Exception as e:
            act['error']=str(e)
            summary['errors']+=1
    return summary
