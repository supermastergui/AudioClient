#  Copyright (c) 2026 Half_nothing
#  SPDX-License-Identifier: MIT
from os import system
from pathlib import Path


def main() -> None:
    root = Path.cwd()
    scripts = root / ".venv" / "Scripts"
    if not scripts.exists():
        print("Please run this script in the root directory of the project")
        return

    rcc_file = scripts / "pyside6-rcc.exe"
    if not rcc_file.exists():
        print("pyside6-rcc.exe not found")
        return
    resource_file = root / "resource.qrc"
    if not resource_file.exists():
        print("resource.qrc not found")
        return

    print("=" * 50)
    print("Processing resource.qrc file")
    system(f"{rcc_file} {resource_file} -o {root / 'resource_rc.py'}")
    print("Processing resource.qrc file completed")

    ui_file_folder = root / "src" / "ui" / "form"

    if not ui_file_folder.exists():
        print("ui folder not found")
        return

    uic_file = scripts / "pyside6-uic.exe"
    if not uic_file.exists():
        print("pyside6-uic.exe not found")
        return

    output_folder = ui_file_folder / "generate"
    output_folder.mkdir(exist_ok=True)

    print("=" * 50)
    print("Processing ui files")

    for ui_file in ui_file_folder.glob("*.ui"):
        output_path = output_folder / (ui_file.stem + ".py")
        print(f"Processing {ui_file.name}")
        system(f"{uic_file} {ui_file} -o {output_path}")

    print("Processing ui files completed")
    print("=" * 50)
    print("Generate file completed")


if __name__ == '__main__':
    main()
