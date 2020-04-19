import pytest
import tarfile
from pathlib import Path

from pytest_mock import MockFixture
from ignite.engine import Engine

from smtools.torch.handlers import archive


@pytest.mark.parametrize("compress", [True, False])
def test_archive(tmp_path: Path, mocker: MockFixture, compress: bool):
    # Setup
    # files to archive
    contents = {
        "model_123.pth": "This is a PyTorch model cehckpoint.",
        "args.yml": "This is a arguemnts yaml file.",
    }
    for name, content in contents.items():
        (tmp_path / name).write_text(content)

    # trainer mock
    trainer = mocker.MagicMock(spec=Engine)
    trainer.iteration = 123

    # Execute
    out_name = "model.tar"
    if compress:
        out_name + ".gz"
    out_file = tmp_path / out_name

    archive(
        trainer=trainer,
        patterns=[f"{tmp_path}/model_*.pth", f"{tmp_path}/args.yml"],
        out_file=out_file,
        compress=compress,
    )

    # Check
    assert out_file.exists()

    with tarfile.open(out_file, "r") as t:
        t.extractall(tmp_path)

        model_dir = tmp_path / "model"
        assert model_dir.is_dir()

        for name, content in contents.items():
            file_ = model_dir / name
            assert file_.exists()
            assert file_.read_text() == content
