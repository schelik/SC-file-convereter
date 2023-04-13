
## Installer Configuration:
- pyinstaller --onefile --add-data "logo.png;." app.py
- pyinstaller --onefile --name "SC File Converter" app.py --add-data "logo.png;." --icon="C:\Users\Semih\Desktop\Projects\SC-file-convereter\logo.ico" -w


## TODO:
- fix the bug where when you select a line and deselect the highlighted line stays there even though the content is disabled
- update status individually for each file (not all at once)
- sort by different columns (name, size, date, etc.)
- turn path into a clickable link
- ~~Multithreading implemented, now its so much faster than a single thread execution~~
