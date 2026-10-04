from driverforge.cli import parser


def test_only_offline_reviewed_candidates_exposed():
    help_text = parser().format_help()
    assert "generate" not in help_text and "live" not in help_text
