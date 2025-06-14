from pathlib import Path

screenshot_file = Path("screencapture.jpg")
print(screenshot_file.lstat())
print(screenshot_file.lstat().st_mtime)
