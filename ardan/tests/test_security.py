import os
import pytest
from ardan.tools.file_tools import write_file, read_file, ToolResult

def test_path_sanitization_absolute():
    res = write_file("/tmp/evil.txt", "content")
    assert not res.success
    assert "Access denied" in res.error

def test_path_sanitization_traversal():
    res = write_file("../../evil.txt", "content")
    assert not res.success
    assert "Access denied" in res.error

def test_path_sanitization_read():
    res = read_file("/etc/passwd")
    assert not res.success
    assert "Access denied" in res.error
