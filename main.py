import asyncio
import sys
import random
import pandas as pd

from pathlib import Path
from copilot import CopilotClient
from copilot.session import PermissionHandler
from copilot.tools import define_tool
from copilot.session_events import SessionEventType
from pydantic import BaseModel, Field

# Defined the parameters used by a tool
class GetInvoicesByPo(BaseModel):
    purchase_order: str = Field(description="The identifier of the purchase order for which to get matching invoices")

def create_get_invoices_for_po_tool(df: pd.DataFrame):
    @define_tool(description="Get invoices matching the purchase order")
    async def get_invoices_for_po(params: GetInvoicesByPo) -> list[dict]:
        matching_invoices = df[df["po_number"] == params.purchase_order]
        return matching_invoices.to_dict(orient="records")

    return get_invoices_for_po

def create_get_all_pos_tool(df: pd.DataFrame):
    @define_tool(description="Get all purchase orders")
    async def get_all_pos() -> list[dict]:
        return df.to_dict(orient='records')

    return get_all_pos

def create_get_all_invoices_tool(df: pd.DataFrame):
    @define_tool(description="Get all invoices")
    async def get_all_invoices() -> list[dict]:
        return df.to_dict(orient='records')

    return get_all_invoices



async def main():
    
    get_invoices_for_po_tool = create_get_invoices_for_po_tool(df_invoices)
    get_all_pos_tool = create_get_all_pos_tool(df_purchase_orders)
    get_all_invoices_tool = create_get_all_invoices_tool(df_invoices)
    tools = [get_invoices_for_po_tool, get_all_pos_tool, get_all_invoices_tool]

    client = CopilotClient(
        telemetry={
            "otlp_endpoint": "http://localhost:4318",
            "otlp_protocol": "http/protobuf",
            "exporter_type": "otlp-http",
            "source_name": "ando-procurement-assistant",
            "capture_content": True,
    },
)

    await client.start()

    session = await client.create_session(on_permission_request=PermissionHandler.approve_all, model="auto", streaming=True, tools=tools)

    def handle_event(event):
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(event.data.delta_content)
            sys.stdout.flush()

    session.on(handle_event)

    print("Procurement assistant (type 'exit' to quit)")

    while True:
        try:
            user_input = input("You: ")
        except EOFError:
            break

        if user_input.lower() == "exit":
            break

        sys.stdout.write("Assistant: ")
        await session.send_and_wait(user_input)
        print("\n")

    await client.stop()

asyncio.run(main())
