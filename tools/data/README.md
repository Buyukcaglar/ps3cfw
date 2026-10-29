# tools/data

`verify_retained.py` reads `lexar-retained-v1.json` from this folder: the paths, sizes and
SHA-256 values of the control files on the owner's drive. That file describes the owner's
drive contents and is not published. To use the tool on another drive, write a file with the
same structure (`controls`, `filler_files`, `samples`) from a known-good read of that drive.
