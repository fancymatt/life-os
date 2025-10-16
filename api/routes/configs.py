"""
Configuration Routes

Endpoints for fetching agent configurations and story presets.
"""

import json
import aiofiles
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()


class ConfigItem(BaseModel):
    """Single configuration item"""
    config_id: str
    display_name: str
    description: str


class ConfigListResponse(BaseModel):
    """List of available configurations"""
    configs: List[ConfigItem]


@router.get("/agent_configs/{agent_type}", response_model=ConfigListResponse)
async def get_agent_configs(agent_type: str):
    """
    Get available configurations for an agent type

    Args:
        agent_type: One of 'story_planner', 'story_writer', 'story_illustrator'
    """
    valid_types = ['story_planner', 'story_writer', 'story_illustrator']
    if agent_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid agent type. Must be one of: {valid_types}")

    config_dir = Path(f"/app/configs/agent_configs/{agent_type}")

    if not config_dir.exists():
        return ConfigListResponse(configs=[])

    configs = []

    # Read all JSON files in the directory
    for config_file in config_dir.glob("*.json"):
        try:
            async with aiofiles.open(config_file, 'r') as f:
                content = await f.read()
                data = json.loads(content)

                configs.append(ConfigItem(
                    config_id=data.get('config_id', config_file.stem),
                    display_name=data.get('display_name', config_file.stem.replace('_', ' ').title()),
                    description=data.get('description', '')
                ))
        except Exception as e:
            print(f"Error reading config {config_file}: {e}")
            continue

    # Sort by config_id
    configs.sort(key=lambda x: x.config_id)

    return ConfigListResponse(configs=configs)


@router.post("/agent_configs/{agent_type}", response_model=dict)
async def create_agent_config(agent_type: str, data: dict):
    """
    Create a new configuration

    Args:
        agent_type: One of 'story_planner', 'story_writer', 'story_illustrator'
        data: Full configuration data (JSON) including config_id, display_name, description
    """
    valid_types = ['story_planner', 'story_writer', 'story_illustrator']
    if agent_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid agent type. Must be one of: {valid_types}")

    # Validate required fields
    if 'config_id' not in data:
        raise HTTPException(status_code=400, detail="Missing required field: config_id")
    if 'display_name' not in data:
        raise HTTPException(status_code=400, detail="Missing required field: display_name")

    config_id = data['config_id']
    config_dir = Path(f"/app/configs/agent_configs/{agent_type}")
    config_dir.mkdir(parents=True, exist_ok=True)

    config_path = config_dir / f"{config_id}.json"

    # Check if config already exists
    if config_path.exists():
        raise HTTPException(status_code=409, detail=f"Configuration already exists: {agent_type}/{config_id}")

    try:
        async with aiofiles.open(config_path, 'w') as f:
            await f.write(json.dumps(data, indent=2))

        return {
            "message": "Configuration created successfully",
            "agent_type": agent_type,
            "config_id": config_id,
            "path": str(config_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create configuration: {str(e)}")


@router.get("/agent_configs/{agent_type}/{config_id}", response_model=dict)
async def get_agent_config(agent_type: str, config_id: str):
    """
    Get full configuration details by ID

    Args:
        agent_type: One of 'story_planner', 'story_writer', 'story_illustrator'
        config_id: Configuration ID (e.g., 'default', 'character_focused')
    """
    valid_types = ['story_planner', 'story_writer', 'story_illustrator']
    if agent_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid agent type. Must be one of: {valid_types}")

    config_path = Path(f"/app/configs/agent_configs/{agent_type}/{config_id}.json")

    if not config_path.exists():
        raise HTTPException(status_code=404, detail=f"Configuration not found: {agent_type}/{config_id}")

    try:
        async with aiofiles.open(config_path, 'r') as f:
            content = await f.read()
            return json.loads(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read configuration: {str(e)}")


@router.put("/agent_configs/{agent_type}/{config_id}", response_model=dict)
async def update_agent_config(agent_type: str, config_id: str, data: dict):
    """
    Update an existing configuration

    Args:
        agent_type: One of 'story_planner', 'story_writer', 'story_illustrator'
        config_id: Configuration ID
        data: Full configuration data (JSON)
    """
    valid_types = ['story_planner', 'story_writer', 'story_illustrator']
    if agent_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid agent type. Must be one of: {valid_types}")

    config_path = Path(f"/app/configs/agent_configs/{agent_type}/{config_id}.json")

    if not config_path.exists():
        raise HTTPException(status_code=404, detail=f"Configuration not found: {agent_type}/{config_id}")

    try:
        # Ensure config_id in data matches the URL parameter
        data['config_id'] = config_id

        async with aiofiles.open(config_path, 'w') as f:
            await f.write(json.dumps(data, indent=2))

        return {
            "message": "Configuration updated successfully",
            "agent_type": agent_type,
            "config_id": config_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")


@router.delete("/agent_configs/{agent_type}/{config_id}", response_model=dict)
async def delete_agent_config(agent_type: str, config_id: str):
    """
    Delete a configuration

    Args:
        agent_type: One of 'story_planner', 'story_writer', 'story_illustrator'
        config_id: Configuration ID
    """
    valid_types = ['story_planner', 'story_writer', 'story_illustrator']
    if agent_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid agent type. Must be one of: {valid_types}")

    # Don't allow deleting the 'default' config
    if config_id == 'default':
        raise HTTPException(status_code=400, detail="Cannot delete the default configuration")

    config_path = Path(f"/app/configs/agent_configs/{agent_type}/{config_id}.json")

    if not config_path.exists():
        raise HTTPException(status_code=404, detail=f"Configuration not found: {agent_type}/{config_id}")

    try:
        config_path.unlink()
        return {
            "message": "Configuration deleted successfully",
            "agent_type": agent_type,
            "config_id": config_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete configuration: {str(e)}")
