"""
Setup for AI-Studio

Allows installation in editable mode for development.
"""

from setuptools import setup, find_packages

setup(
    name="ai-studio",
    version="0.1.0",
    packages=find_packages(include=["ai_capabilities", "ai_tools", "ai_workflows"]),
    install_requires=[
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "litellm>=1.0.0",
        "openai>=1.0.0",
        "pillow>=10.0.0",
        "jinja2>=3.1.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.12.0",
        ]
    },
    python_requires=">=3.9",
)
