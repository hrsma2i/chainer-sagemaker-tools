from typing import List
from pathlib import Path
import tarfile


def archive(patterns: List[str], out_file: Path, compress: bool = True):
    paths: List[Path] = list()
    for pattern in patterns:
        paths += list(Path("/").glob(pattern.lstrip("/")))

    out_name_wo_suffix = out_file.name.split(".")[0]
    # out_dir/model.tar.gz -> model

    with tarfile.open(out_file, "w:gz" if compress else "w") as t:
        for path in paths:
            t.add(str(path), arcname=f"{out_name_wo_suffix}/{path.name}")
