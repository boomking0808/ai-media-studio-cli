"""
Model configuration definitions for AI Media Studio CLI.

This file contains all model specifications including capabilities,
supported options, and constraints for both video and image generation models.
"""

from typing import Dict, List, Union, Optional
from dataclasses import dataclass


@dataclass
class DurationConfig:
    """Duration configuration for video models."""

    min: int
    max: int
    default: int
    options: List[int]


@dataclass
class VideoModelCapabilities:
    """Capabilities and constraints for video generation models."""

    max_videos: int
    duration: DurationConfig
    aspect_ratios: List[str]
    resolutions: List[str]
    frame_rates: List[int]
    supports_image_to_video: bool = False
    supports_prompt_enhancement: bool = True
    supports_extend_video: bool = False


@dataclass
class ImageModelCapabilities:
    """Capabilities and constraints for image generation models."""

    max_images: int
    aspect_ratios: List[str]
    resolutions: List[str]
    supports_prompt_enhancement: bool = True
    styles: Optional[List[str]] = None


@dataclass
class ModelConfig:
    """Complete model configuration."""

    model_id: str
    type: str  # "video" or "image"
    display_name: str
    description: str
    capabilities: Union[VideoModelCapabilities, ImageModelCapabilities]
    api_model_name: str  # The actual model name used in API calls


# =============================================================================
# VIDEO MODELS CONFIGURATION
# =============================================================================

VIDEO_MODELS = {
    # Veo 2.0
    "veo2-001": ModelConfig(
        model_id="veo2-001",
        type="video",
        display_name="Veo 2.0 Generate 001",
        description="Stable text-to-video generation, supports up to 4 videos",
        api_model_name="veo-2.0-generate-001",
        capabilities=VideoModelCapabilities(
            max_videos=4,
            duration=DurationConfig(min=5, max=8, default=8, options=[5, 6, 7, 8]),
            aspect_ratios=["16:9", "9:16"],
            resolutions=["720p"],
            frame_rates=[24],
            supports_image_to_video=True,
            supports_prompt_enhancement=True,
            supports_extend_video=True,
        ),
    ),
    # Veo 3.0
    "veo3-001": ModelConfig(
        model_id="veo3-001",
        type="video",
        display_name="Veo 3.0 Generate 001",
        description="Stable text-to-video generation, supports up to 4 videos",
        api_model_name="veo-3.0-generate-001",
        capabilities=VideoModelCapabilities(
            max_videos=4,
            duration=DurationConfig(
                min=8, max=8, default=8, options=[8]  # Currently fixed at 8s
            ),
            aspect_ratios=["16:9"],  # Currently only widescreen
            resolutions=["720p", "1080p"],
            frame_rates=[24],
            supports_image_to_video=False,
            supports_prompt_enhancement=True,
            supports_extend_video=False,
        ),
    ),
    "veo3-preview": ModelConfig(
        model_id="veo3-preview",
        type="video",
        display_name="Veo 3.0 Generate Preview",
        description="Latest features with image-to-video support, up to 4 videos",
        api_model_name="veo-3.0-generate-preview",
        capabilities=VideoModelCapabilities(
            max_videos=4,
            duration=DurationConfig(min=8, max=8, default=8, options=[8]),
            aspect_ratios=["16:9"],  # Currently only widescreen
            resolutions=["720p", "1080p"],
            frame_rates=[24],
            supports_image_to_video=True,
            supports_prompt_enhancement=True,
            supports_extend_video=False,
        ),
    ),
}

# =============================================================================
# IMAGE MODELS CONFIGURATION (Future)
# =============================================================================

IMAGE_MODELS = {
    # Example configuration for future image models
    # "imagen-001": ModelConfig(
    #     model_id="imagen-001",
    #     type="image",
    #     display_name="Imagen 3.0",
    #     description="High-quality image generation",
    #     api_model_name="imagen-3.0-generate-001",
    #     capabilities=ImageModelCapabilities(
    #         max_images=8,
    #         aspect_ratios=["1:1", "16:9", "9:16", "4:3", "3:4"],
    #         resolutions=["512x512", "1024x1024", "1536x1536", "2048x2048"],
    #         supports_prompt_enhancement=True,
    #         styles=["photorealistic", "artistic", "cartoon", "sketch"],
    #     )
    # ),
}

# =============================================================================
# UNIFIED MODEL REGISTRY
# =============================================================================

ALL_MODELS = {
    **VIDEO_MODELS,
    **IMAGE_MODELS,
}


def get_model_config(model_id: str) -> Optional[ModelConfig]:
    """Get configuration for a specific model."""
    return ALL_MODELS.get(model_id)


def get_video_models() -> Dict[str, ModelConfig]:
    """Get all video generation models."""
    return {k: v for k, v in ALL_MODELS.items() if v.type == "video"}


def get_image_models() -> Dict[str, ModelConfig]:
    """Get all image generation models."""
    return {k: v for k, v in ALL_MODELS.items() if v.type == "image"}


def list_available_models() -> List[str]:
    """Get list of all available model IDs."""
    return list(ALL_MODELS.keys())


# =============================================================================
# MODEL VALIDATION HELPERS
# =============================================================================


def validate_model_options(model_id: str, **options) -> Dict[str, Union[bool, str]]:
    """
    Validate options against model capabilities.

    Returns:
        Dict with validation results and corrected values
    """
    config = get_model_config(model_id)
    if not config:
        return {"valid": False, "error": f"Unknown model: {model_id}"}

    result = {"valid": True, "corrections": {}}

    if config.type == "video":
        caps = config.capabilities

        # Validate number of videos
        if "number_of_videos" in options:
            if options["number_of_videos"] > caps.max_videos:
                result["corrections"]["number_of_videos"] = caps.max_videos

        # Validate duration
        if "duration_seconds" in options:
            duration = options["duration_seconds"]
            if duration not in caps.duration.options:
                result["corrections"]["duration_seconds"] = caps.duration.default

        # Validate aspect ratio
        if "aspect_ratio" in options:
            if options["aspect_ratio"] not in caps.aspect_ratios:
                result["corrections"]["aspect_ratio"] = caps.aspect_ratios[0]

        # Validate resolution
        if "resolution" in options:
            resolution_value = options["resolution"]
            # Convert CLI format (e.g., "1080") to model config format (e.g., "1080p")
            if not resolution_value.endswith("p"):
                resolution_value_with_p = f"{resolution_value}p"
            else:
                resolution_value_with_p = resolution_value

            if resolution_value_with_p not in caps.resolutions:
                result["corrections"]["resolution"] = caps.resolutions[0].rstrip("p")
            else:
                # Resolution is valid, no correction needed
                pass

    return result
