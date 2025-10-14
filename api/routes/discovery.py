"""
Discovery Routes

Endpoints for discovering available tools and capabilities.
"""

from fastapi import APIRouter, HTTPException
from typing import List

from api.models.responses import ToolInfo
from api.services import AnalyzerService, GeneratorService

router = APIRouter()


@router.get("/tools", response_model=List[ToolInfo])
async def list_tools():
    """
    List all available tools

    Returns a list of all analyzers and generators with their descriptions and costs.
    """
    analyzer_service = AnalyzerService()
    generator_service = GeneratorService()

    tools = []

    # Add analyzers
    for analyzer in analyzer_service.list_analyzers():
        tools.append(ToolInfo(**analyzer))

    # Add generators
    for generator in generator_service.list_generators():
        tools.append(ToolInfo(**generator))

    return tools


@router.get("/tools/{tool_name}", response_model=ToolInfo)
async def get_tool_info(tool_name: str):
    """
    Get information about a specific tool

    Returns detailed information about a tool including its description, cost, and average time.
    """
    analyzer_service = AnalyzerService()
    generator_service = GeneratorService()

    # Try to find in analyzers
    if analyzer_service.validate_analyzer(tool_name):
        info = analyzer_service.get_analyzer_info(tool_name)
        return ToolInfo(**info)

    # Try to find in generators
    if generator_service.validate_generator(tool_name):
        info = generator_service.get_generator_info(tool_name)
        return ToolInfo(**info)

    raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")
