import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "kaggle_job.py"
spec = importlib.util.spec_from_file_location("kaggle_job", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class KaggleJobTests(unittest.TestCase):
    def test_find_cli_returns_existing_file(self):
        cli = module.find_cli()
        self.assertTrue(Path(cli).is_file())

    def test_parse_kernel_ref(self):
        text = (
            "Kernel version 1 successfully pushed.  Please check progress at "
            "https://www.kaggle.com/code/example/demo-kernel"
        )
        self.assertEqual(
            module.parse_kernel_ref(text, "fallback/kernel"),
            "example/demo-kernel",
        )

    def test_parse_kernel_ref_fallback(self):
        self.assertEqual(
            module.parse_kernel_ref("no URL", "fallback/kernel"),
            "fallback/kernel",
        )


if __name__ == "__main__":
    unittest.main()
