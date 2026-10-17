from mcp.server import MCPServer
import pandas as pd

mcp = MCPServer("Demo")

# Read csv datasets into the dataframe objects
# df_purchase_orders = pd.read_csv('po_golden.csv', sep=',')
#

@mcp.tool()
def get_all_invoices() -> list[dict]:
    """"Fetches all available invoices."""
    df_invoices = pd.read_csv('invoices_golden.csv', sep=',')
    return df_invoices.to_dict(orient='records')


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"


@mcp.prompt()
def summarize(text: str) -> str:
    """Summarize a piece of text in one sentence."""
    return f"Summarize the following text in one sentence:\n\n{text}"