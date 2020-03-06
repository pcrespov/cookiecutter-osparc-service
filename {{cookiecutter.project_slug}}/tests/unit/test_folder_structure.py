# pylint:disable=unused-variable
# pylint:disable=unused-argument
# pylint:disable=redefined-outer-name

from pathlib import Path
import pytest

expected_files = (
    ".cookiecutterrc",
    "metadata:metadata.yml",
    "docker/entrypoint.sh",
    "tools/run_creator.py",
    "tools/update_compose_labels.py",
    "requirements.in",
    "requirements.txt",
    "src/Dockerfile",
    "Makefile",
    "VERSION_KERNEL",
    "VERSION_INTEGRATION",
    "README.md"
)

@pytest.mark.parametrize("expected_path", expected_files)
def test_path_in_repo(expected_path: str, project_slug_dir: Path):

    if ":" in expected_path:
        folder, glob = expected_path.split(":")
        folder_path = project_slug_dir / folder
        assert folder_path.exists()
        assert any(folder_path.glob(glob))
    else:
        assert  (project_slug_dir/expected_path).exists()
