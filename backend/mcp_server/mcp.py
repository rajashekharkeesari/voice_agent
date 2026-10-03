from fastmcp import FastMCP

from backend.mcp_server.doctor_tools import register_doctor_tools
from backend.mcp_server.availability_tools import register_availability_tools
from backend.mcp_server.appointment_tools import register_appointment_tools
from backend.mcp_server.hospital_tools import register_hospital_tools
from backend.mcp_server.patients_tools import register_patient_tools
from backend.mcp_server.state_tools import register_state_tools

# --------------------------------------------------
# Central MCP server
# --------------------------------------------------
mcp = FastMCP("Hospital MCP")

# --------------------------------------------------
# Register all tools
# --------------------------------------------------
register_doctor_tools(mcp)
register_availability_tools(mcp)
register_appointment_tools(mcp)
register_hospital_tools(mcp)
register_patient_tools(mcp)
register_state_tools(mcp)

# --------------------------------------------------
# Run MCP server
# --------------------------------------------------
if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000,
    )
