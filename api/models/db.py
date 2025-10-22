"""
SQLAlchemy Database Models

Defines database schema for all entities using SQLAlchemy 2.0+ async API.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Text, Integer, Float, Boolean, DateTime, JSON,
    ForeignKey, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base


# ============================================================================
# User and Authentication
# ============================================================================

class User(Base):
    """User account"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    characters = relationship("Character", back_populates="owner", cascade="all, delete-orphan")
    clothing_items = relationship("ClothingItem", back_populates="owner", cascade="all, delete-orphan")
    board_games = relationship("BoardGame", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


# ============================================================================
# Character Entity
# ============================================================================

class Character(Base):
    """Character entity for story generation and image generation"""
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Visual descriptions
    visual_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    physical_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    personality: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Reference image
    reference_image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Detailed appearance fields (from character_appearance_analyzer)
    age: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    skin_tone: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    face_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hair_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    # Note: Using 'meta' instead of 'metadata' (reserved by SQLAlchemy)
    meta: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # User relationship
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    owner = relationship("User", back_populates="characters")

    # Indexes for common queries
    __table_args__ = (
        Index("ix_character_user_id_name", "user_id", "name"),
    )

    def __repr__(self):
        return f"<Character(id='{self.character_id}', name='{self.name}')>"


# ============================================================================
# Clothing Item Entity
# ============================================================================

class ClothingItem(Base):
    """Clothing item entity for outfit analysis"""
    __tablename__ = "clothing_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # Item details
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    item: Mapped[str] = mapped_column(String(500), nullable=False)
    fabric: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Source and preview images
    source_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    preview_image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # User relationship
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    owner = relationship("User", back_populates="clothing_items")

    # Indexes for common queries
    __table_args__ = (
        Index("ix_clothing_user_category", "user_id", "category"),
    )

    def __repr__(self):
        return f"<ClothingItem(id='{self.item_id}', category='{self.category}', item='{self.item}')>"


# ============================================================================
# Board Game Entity
# ============================================================================

class BoardGame(Base):
    """Board game entity for game management and Q&A"""
    __tablename__ = "board_games"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # Game details
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    bgg_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    designer: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    publisher: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Player count and playtime
    player_count_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    player_count_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    playtime_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    playtime_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Complexity rating
    complexity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Metadata
    # Note: Using 'meta' instead of 'metadata' (reserved by SQLAlchemy)
    meta: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # User relationship
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    owner = relationship("User", back_populates="board_games")

    # Indexes for common queries
    __table_args__ = (
        Index("ix_boardgame_user_name", "user_id", "name"),
        Index("ix_boardgame_bgg_id", "bgg_id"),
    )

    def __repr__(self):
        return f"<BoardGame(id='{self.game_id}', name='{self.name}')>"


# ============================================================================
# Outfit Entity (Placeholder for future implementation)
# ============================================================================

class Outfit(Base):
    """Outfit entity - combination of clothing items"""
    __tablename__ = "outfits"

    id: Mapped[int] = mapped_column(primary_key=True)
    outfit_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # Outfit details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Style classification
    style_genre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    formality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Clothing items (stored as JSON array of item IDs)
    clothing_item_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    # Source image
    source_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    preview_image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Metadata
    # Note: Using 'meta' instead of 'metadata' (reserved by SQLAlchemy)
    meta: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # User relationship
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)

    def __repr__(self):
        return f"<Outfit(id='{self.outfit_id}', name='{self.name}')>"


# ============================================================================
# Story Entities (Future implementation for persistent stories)
# ============================================================================

class Story(Base):
    """Story entity - generated stories"""
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(primary_key=True)
    story_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # Story content
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Story metadata
    character_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("characters.character_id"), nullable=True, index=True)
    theme: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    story_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Metadata
    # Note: Using 'meta' instead of 'metadata' (reserved by SQLAlchemy)
    meta: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # User relationship
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)

    # Relationships
    scenes = relationship("StoryScene", back_populates="story", cascade="all, delete-orphan", order_by="StoryScene.scene_number")

    def __repr__(self):
        return f"<Story(id='{self.story_id}', title='{self.title}')>"


class StoryScene(Base):
    """Story scene entity - individual scenes within a story"""
    __tablename__ = "story_scenes"

    id: Mapped[int] = mapped_column(primary_key=True)
    scene_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # Scene content
    story_id: Mapped[str] = mapped_column(String(50), ForeignKey("stories.story_id"), nullable=False, index=True)
    scene_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Scene metadata
    action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    illustration_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    illustration_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Metadata
    # Note: Using 'meta' instead of 'metadata' (reserved by SQLAlchemy)
    meta: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    story = relationship("Story", back_populates="scenes")

    # Indexes for common queries
    __table_args__ = (
        Index("ix_scene_story_number", "story_id", "scene_number"),
    )

    def __repr__(self):
        return f"<StoryScene(story_id='{self.story_id}', scene_number={self.scene_number}, title='{self.title}')>"


# ============================================================================
# Favorite Entity
# ============================================================================

class Favorite(Base):
    """User favorite preset"""
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True)

    # User relationship
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Favorite details
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    preset_id: Mapped[str] = mapped_column(String(100), nullable=False)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Indexes and constraints
    __table_args__ = (
        Index("ix_favorite_user_category", "user_id", "category"),
        Index("ix_favorite_unique", "user_id", "category", "preset_id", unique=True),
    )

    def __repr__(self):
        return f"<Favorite(user_id={self.user_id}, category='{self.category}', preset_id='{self.preset_id}')>"


# ============================================================================
# Composition Entity
# ============================================================================

class Composition(Base):
    """Saved preset composition"""
    __tablename__ = "compositions"

    id: Mapped[int] = mapped_column(primary_key=True)
    composition_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    # Composition details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    presets: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # User relationship
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)

    # Indexes
    __table_args__ = (
        Index("ix_composition_user_id", "user_id"),
        Index("ix_composition_name", "name"),
    )

    def __repr__(self):
        return f"<Composition(id='{self.composition_id}', name='{self.name}')>"
