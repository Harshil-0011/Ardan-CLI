import unittest
import os
from ardan.tools.deps_tools import scan_imports


class TestDepsTools(unittest.TestCase):
    def test_scan_imports(self):
        # Create a dummy python file with imports
        with open("dummy_imports.py", "w") as f:
            f.write("import os\nfrom typing import List\nimport requests\n")

        res = scan_imports(".")
        self.assertTrue(res.success)
        # Check if basic imports are found (os, typing are stdlib, requests is external)
        self.assertIn("os", res.output)
        self.assertIn("typing", res.output)
        self.assertIn("requests", res.output)

        os.remove("dummy_imports.py")


if __name__ == "__main__":
    unittest.main()
