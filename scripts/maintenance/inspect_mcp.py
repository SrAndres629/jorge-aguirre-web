
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Test")
print("Attributes of FastMCP:")
for attr in dir(mcp):
    print(attr)
