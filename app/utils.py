import hashlib
import os

def get_file_meta(file_path):
    """Returns ctx file content, last modified time and checksum"""
    file_path
    if not file_path.exists():
        return None, None, None

    content = file_path.read_text()
    last_modified =  os.path.getmtime(file_path)
    checksum = hashlib.sha256(content.encode()).hexdigest()

    return content, last_modified, checksum
