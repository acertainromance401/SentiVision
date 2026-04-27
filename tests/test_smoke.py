from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]


def test_repository_structure_smoke() -> None:
    required_paths = [
        ROOT / "README.md",
        ROOT / "LICENSE",
        ROOT / "CONTRIBUTING.md",
        ROOT / ".github" / "workflows" / "ci-matrix.yml",
        ROOT / ".github" / "workflows" / "build-test-deploy.yml",
        ROOT / "base_model" / "color_emotion_labeled_updated.csv",
        ROOT / "test" / "main_.py",
    ]

    for path in required_paths:
        assert path.exists(), f"Missing required path: {path}"


def test_python_scripts_parse_smoke() -> None:
    scripts = [
        ROOT / "test" / "main_.py",
        ROOT / "test" / "test_model_comparison.py",
    ]

    for script in scripts:
        source = script.read_text(encoding="utf-8")
        ast.parse(source)
