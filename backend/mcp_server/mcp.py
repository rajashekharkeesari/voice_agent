from fastmcp import FastMCP

from backend.mcp.doctor_tools import (
    register_doctor_tools
)

from backend.mcp.availability_tools import (
    register_availability_tools
)

from backend.mcp.appointment_tools import (
    register_appointment_tools
)

from backend.mcp.hospital_tools import (
    register_hospital_tools
)

from backend.mcp.patient_tools import (
    register_patient_tools  
)


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


# --------------------------------------------------
# Run MCP server
# --------------------------------------------------

if __name__ == "__main__":
     mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )