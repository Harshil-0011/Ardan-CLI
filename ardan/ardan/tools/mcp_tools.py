import json
import subprocess
from typing import Dict, Any, List, Optional
from ardan.tools.file_tools import ToolResult

class MCPServer:
    def __init__(self, name: str, command: str, args: List[str] = None):
        self.name = name
        self.command = command
        self.args = args or []
        self.process: Optional[subprocess.Popen] = None

    def start(self):
        try:
            self.process = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
        except Exception as e:
            raise Exception(f"Failed to start MCP server {self.name}: {str(e)}")

    def call_tool(self, name: str, args: Dict[str, Any]) -> ToolResult:
        if not self.process:
            self.start()

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": args
            }
        }

        try:
            self.process.stdin.write(json.dumps(request) + "\n")
            response_line = self.process.stdout.readline()
            if not response_line:
                 return ToolResult(False, "", "MCP server disconnected.")

            response = json.loads(response_line)
            if "error" in response:
                 return ToolResult(False, "", response["error"].get("message", "Unknown MCP error"))

            result_content = response.get("result", {}).get("content", [])
            output = "\n".join([c.get("text", "") for c in result_content if c.get("type") == "text"])
            return ToolResult(True, output)
        except Exception as e:
            return ToolResult(False, "", str(e))

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None

class MCPManager:
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.tools: Dict[str, str] = {} # tool_name -> server_name

    def load_from_config(self, mcp_config: Dict[str, Any]):
        for name, cfg in mcp_config.items():
            server = MCPServer(name, cfg["command"], cfg.get("args", []))
            self.servers[name] = server
            # For simplicity, we assume we know which tools are on which server
            # or we would perform a 'tools/list' call here.
            for tool_name in cfg.get("tools", []):
                self.tools[tool_name] = name

    def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Optional[ToolResult]:
        server_name = self.tools.get(tool_name)
        if server_name:
            return self.servers[server_name].call_tool(tool_name, args)
        return None
