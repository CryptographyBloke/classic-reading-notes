#!/usr/bin/env python3
"""Optional DOCX -> PDF -> PNG preview using LibreOffice and Poppler."""
import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description="Render DOCX pages for manual visual review")
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output-dir", type=Path, default=Path("previews"))
    p.add_argument("--dpi", type=int, default=140)
    a = p.parse_args()
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    pdftoppm = shutil.which("pdftoppm")
    if not soffice or not pdftoppm:
        p.exit(2, "Install LibreOffice and Poppler, or use your agent's DOCX renderer.\n")
    if not a.input.is_file():
        p.exit(2, f"Document not found: {a.input}\n")
    a.output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        temp = Path(tmp)
        profile = (temp / "lo-user-profile").resolve().as_uri()
        r = subprocess.run([soffice, "-env:UserInstallation="+profile,
                            "--headless", "--convert-to", "pdf", "--outdir",
                            str(temp), str(a.input.resolve())],
                           capture_output=True, text=True)
        pdf = temp / (a.input.stem+".pdf")
        if r.returncode or not pdf.exists():
            p.exit(2, f"LibreOffice conversion failed: {r.stderr or r.stdout}\n")
        prefix = a.output_dir / a.input.stem
        r = subprocess.run([pdftoppm, "-png", "-r", str(a.dpi), str(pdf),
                            str(prefix)], capture_output=True, text=True)
        if r.returncode:
            p.exit(2, f"PNG generation failed: {r.stderr}\n")
    pages = sorted(a.output_dir.glob(a.input.stem+"-*.png"))
    if not pages:
        p.exit(2, "No PNGs created.\n")
    for img in pages:
        print(img.resolve())
    print(f"Rendered {len(pages)} page(s). Inspect every page before delivery.")


if __name__ == "__main__":
    main()
