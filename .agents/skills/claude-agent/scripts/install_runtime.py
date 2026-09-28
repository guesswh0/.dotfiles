import argparse
import os
from pathlib import Path
import subprocess
import sys
import venv


def main():
    if sys.version_info < (3, 11):
        raise SystemExit("Python 3.11 or newer is required")
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-dir", type=Path, default=root / ".venv")
    runtime = parser.parse_args().runtime_dir.expanduser().resolve()
    venv.EnvBuilder(with_pip=True).create(runtime)
    environment = {**os.environ, "PIP_DISABLE_PIP_VERSION_CHECK": "1"}
    subprocess.run(
        [
            str(runtime / "bin" / "python"),
            "-m",
            "pip",
            "install",
            "--no-cache-dir",
            "-r",
            str(root / "scripts" / "requirements.txt"),
        ],
        check=True,
        env=environment,
    )
    print("Runtime installed:", runtime)


if __name__ == "__main__":
    main()
