import hashlib
import os
from pathlib import Path


async def fetch_file_data(file_path: Path, with_content=False):
    attempts = 3
    data = {"checksum": None, "content": None, "last_modified": None}
    for _ in range(attempts):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                data["checksum"] = hashlib.sha256(content.encode()).hexdigest()
                data["last_modified"] = os.path.getmtime(file_path)
            if with_content:
                data["content"] = content
            return data

        except (OSError, IOError) as e:
            logging.warning(f"Error reading file {file_path}, retrying... {e}")
            await asyncio.sleep(0.1)
    return data
