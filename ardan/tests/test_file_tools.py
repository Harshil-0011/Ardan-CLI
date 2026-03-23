import unittest
import os
from ardan.tools.file_tools import write_file, read_file, delete_file

class TestFileTools(unittest.TestCase):
    def test_write_read_delete(self):
        path = "test_unit.txt"
        content = "test content"
        res = write_file(path, content)
        self.assertTrue(res.success)
        res = read_file(path)
        self.assertEqual(res.output, content)
        delete_file(path)

if __name__ == "__main__":
    unittest.main()
