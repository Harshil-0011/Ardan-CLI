import unittest
from ardan.tools.file_tools import write_file, read_file, delete_file, ToolResult
import os

class TestFileTools(unittest.TestCase):
    def test_write_read_delete(self):
        path = "test_file.txt"
        content = "hello ardan"

        # Test write
        res = write_file(path, content)
        if not res.success:
             print(f"Error: {res.error}")
        self.assertTrue(res.success)
        self.assertTrue(os.path.exists(path))

        # Test read
        res = read_file(path)
        self.assertTrue(res.success)
        self.assertEqual(res.output, content)

        # Test delete
        res = delete_file(path)
        self.assertTrue(res.success)
        self.assertFalse(os.path.exists(path))

if __name__ == "__main__":
    unittest.main()
