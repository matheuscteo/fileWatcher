import hashlib
import os

def get_ctx_file_meta(ctx_file_path):
    """Returns ctx file content, last modified time and checksum"""
    ctx_file_path
    if not ctx_file_path.exists():
        return None, None, None

    ctx_content = ctx_file_path.read_text()
    ctx_last_modified =  os.path.getmtime(ctx_file_path)
    ctx_checksum = hashlib.sha256(ctx_content.encode()).hexdigest()

    return ctx_content, ctx_last_modified, ctx_checksum
