import unittest
from pathlib import Path


class WebCpampExampleTests(unittest.TestCase):
    def test_cpamp_example_uses_configured_server(self):
        index_html = (Path(__file__).resolve().parents[1] / "web" / "index.html").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            'id="cpa_remote_base" type="text" placeholder="http://140.240.40.240:18317"',
            index_html,
        )
        self.assertIn(
            'href="http://140.240.40.240:18317/management.html"',
            index_html,
        )


if __name__ == "__main__":
    unittest.main()
