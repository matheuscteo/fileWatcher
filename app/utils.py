import hashlib
import os

<<<<<<< HEAD
def get_file_meta(file_path):
    """Returns ctx file content, last modified time and checksum"""
    file_path
    if not file_path.exists():
        return None, None, None

    content = file_path.read_text()
    last_modified =  os.path.getmtime(file_path)
    checksum = hashlib.sha256(content.encode()).hexdigest()

    return content, last_modified, checksum
=======
def get_ctx_file_meta(ctx_file_path):
    """Returns ctx file content, last modified time and checksum"""
    ctx_file_path
    if not ctx_file_path.exists():
        return None, None, None

    ctx_content = ctx_file_path.read_text()
    ctx_last_modified =  os.path.getmtime(ctx_file_path)
    ctx_checksum = hashlib.sha256(ctx_content.encode()).hexdigest()

    return ctx_content, ctx_last_modified, ctx_checksum
>>>>>>> 0a0a7ba446ff064dcf1d889e022b915c703ba8d3
