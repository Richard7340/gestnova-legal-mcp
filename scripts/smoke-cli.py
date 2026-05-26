"""CLI to invoke any tool by name with JSON args.

Usage:
    uv run python scripts/smoke-cli.py ping '{}'
    uv run python scripts/smoke-cli.py listJurisdictions '{}'
"""
import asyncio
import json
import sys

from gestnova_legal.server import build_server


async def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    tool_name = sys.argv[1]
    args = json.loads(sys.argv[2])
    server = build_server()
    result = await server.call_tool(tool_name, args)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
