from typer.main import get_command

from authtwin import __version__
from authtwin.cli_all import BRAND, app
from sric.cli_style import build_banner


def test_authtwin_brand_identity() -> None:
    banner = build_banner(BRAND)
    product = banner.index(f"AuthTwin :: v{__version__}")
    developer = banner.index("Developer: IsdarlinM")
    description = banner.index("Model authorization behavior")
    assert product < developer < description
    assert "IsdarlinM ::" not in banner


def test_no_color_option_is_registered() -> None:
    command = get_command(app)
    assert any("--no-color" in getattr(param, "opts", ()) for param in command.params)
