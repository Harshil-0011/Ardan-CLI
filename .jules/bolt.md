## 2025-05-22 - Optimized Dependency Scanning
**Learning:** Regex-based scanning of codebase for imports is both fragile and slow as it processes all files linearly and misses edge cases. Project structure often includes deep directories like `.git` or `node_modules` that shouldn't be scanned.
**Action:** Use `ast.parse` for precision and prune `os.walk` to avoid unnecessary directories. Skip large files that are likely build artifacts or data.
