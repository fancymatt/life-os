"""
Tool Configuration Service

Helper functions for loading tool configurations.
Separated from routes to avoid circular imports in RQ workers.
"""

from pathlib import Path
from typing import Dict, Any
import yaml
import aiofiles

from api.config import settings


async def load_models_config() -> Dict[str, Any]:
    """
    Load models.yaml configuration with overrides

    Returns merged config of base models.yaml + user overrides
    """
    # Load base config (read-only)
    base_config_path = settings.base_dir / "configs" / "models.yaml"
    async with aiofiles.open(base_config_path, 'r') as f:
        content = await f.read()
        base_config = yaml.safe_load(content)

    # Load overrides (writable)
    overrides_path = settings.base_dir / "data" / "tool_configs" / "overrides.yaml"
    if overrides_path.exists():
        async with aiofiles.open(overrides_path, 'r') as f:
            content = await f.read()
            overrides = yaml.safe_load(content) or {}

            # Merge overrides into base config
            if 'defaults' in overrides:
                base_config.setdefault('defaults', {}).update(overrides['defaults'])
            if 'tool_settings' in overrides:
                base_config.setdefault('tool_settings', {}).update(overrides['tool_settings'])

    return base_config
