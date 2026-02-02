from json import dump, load
from pathlib import Path
from hashlib import md5
import subprocess  # 替换 os.system


def calculate_file_md5(file_path: Path, *, encoding: str = 'utf8') -> str:
    if not file_path.exists():
        raise FileNotFoundError
    with open(file_path, "r", encoding=encoding) as f:
        data = f.read()
    return md5(data.encode(encoding)).hexdigest()


def run_command(cmd_list):
    """运行命令并处理错误"""
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"命令执行失败: {' '.join(cmd_list)}")
            print(f"错误信息: {result.stderr}")
        return result.returncode
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return 1


def main() -> None:
    root = Path.cwd()

    cache_file = root / ".cache"

    if not cache_file.exists():
        cache_file.write_text("{}", encoding="utf-8")

    f = open(cache_file, "r", encoding="utf-8")
    cache: dict[str, str] = load(f)
    f.close()

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
    # 使用 subprocess.run 而不是 os.system
    return_code = run_command([
        str(rcc_file),
        str(resource_file),
        "-o",
        str(root / "resource_rc.py")
    ])
    if return_code == 0:
        print("Processing resource.qrc file completed")
    else:
        print("Failed to process resource.qrc file")

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
        new_md5 = calculate_file_md5(ui_file)
        if str(ui_file) not in cache or cache[str(ui_file)] != new_md5:
            print(f"Processing {ui_file.name}")
            # 使用 subprocess.run 而不是 os.system
            return_code = run_command([
                str(uic_file),
                str(ui_file),
                "-o",
                str(output_path)
            ])
            if return_code == 0:
                cache[str(ui_file)] = new_md5
            else:
                print(f"Failed to process {ui_file.name}")
        else:
            print(f"Using cached {ui_file.name}")

    print("Processing ui files completed")
    print("=" * 50)
    print("Generate file completed")

    with open(cache_file, "w", encoding="utf8") as f:
        dump(cache, f)


if __name__ == '__main__':
    main()