from plothole.config import PROJECT_ROOT, load_config


def test_config_valid():
    cfg = load_config()
    assert cfg["dataset"]["gt_mode"] in {"raw", "curated"}
    assert set(cfg["experiment"]["strategies"]) == {"zero_shot", "cot", "chunking"}


def test_semua_path_di_dalam_project():
    cfg = load_config()
    for path in cfg["paths"].values():
        assert PROJECT_ROOT in path.parents