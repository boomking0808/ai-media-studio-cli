"""
Model manager for dynamic CLI option generation and validation.

This module provides the interface between model configurations and the CLI,
generating appropriate options and prompts based on the selected model.
"""

from typing import List, Tuple, Any, Dict, Optional, Union
from enum import Enum
import inquirer
from rich.console import Console
from rich.panel import Panel

from .models_config import (
    get_model_config, 
    get_video_models, 
    get_image_models,
    validate_model_options,
    ModelConfig,
    VideoModelCapabilities,
    ImageModelCapabilities
)

console = Console()


class ModelManager:
    """Manages model configurations and dynamic option generation."""
    
    def __init__(self):
        self.video_models = get_video_models()
        self.image_models = get_image_models()
    
    def get_model_choices_for_cli(self, model_type: str = "video") -> List[Tuple[str, str]]:
        """
        Get model choices formatted for CLI help text.
        
        Args:
            model_type: "video" or "image"
            
        Returns:
            List of (display_text, model_id) tuples
        """
        models = self.video_models if model_type == "video" else self.image_models
        choices = []
        
        for model_id, config in models.items():
            display = f"{config.display_name} - {config.description}"
            choices.append((display, model_id))
            
        return choices
    
    def get_model_choices_for_interactive(self, model_type: str = "video") -> List[Tuple[str, str]]:
        """
        Get model choices formatted for interactive prompts.
        
        Args:
            model_type: "video" or "image"
            
        Returns:
            List of (display_text, model_id) tuples
        """
        models = self.video_models if model_type == "video" else self.image_models
        choices = []
        
        for model_id, config in models.items():
            if model_type == "video":
                caps = config.capabilities
                max_videos = f"up to {caps.max_videos} videos" if caps.max_videos > 1 else "1 video"
                duration_info = f"{caps.duration.min}-{caps.duration.max}s" if caps.duration.min != caps.duration.max else f"{caps.duration.default}s"
                features = []
                if caps.supports_image_to_video:
                    features.append("image-to-video")
                if caps.supports_prompt_enhancement:
                    features.append("prompt enhancement")
                if caps.supports_extend_video:
                    features.append("video extension")
                
                feature_text = f", {', '.join(features)}" if features else ""
                display = f"{config.display_name} - {max_videos}, {duration_info}{feature_text}"
            else:
                # Future image model display format
                display = f"{config.display_name} - {config.description}"
                
            choices.append((display, model_id))
            
        return choices
    
    def get_duration_options(self, model_id: str) -> Tuple[List[int], int]:
        """
        Get duration options for a video model.
        
        Returns:
            Tuple of (available_options, default_value)
        """
        config = get_model_config(model_id)
        if not config or config.type != "video":
            return [8], 8
            
        caps = config.capabilities
        return caps.duration.options, caps.duration.default
    
    def get_duration_choices_for_interactive(self, model_id: str) -> List[Tuple[str, str]]:
        """Get duration choices formatted for interactive prompts."""
        options, default = self.get_duration_options(model_id) 
        
        if len(options) == 1:
            # Only one option available, don't show choice
            return []
            
        choices = []
        for duration in options:
            visual = "▪" * duration
            display = f"{duration}s {visual}"
            choices.append((display, str(duration)))
            
        return choices
    
    def get_video_count_options(self, model_id: str) -> Tuple[int, int]:
        """
        Get video count options for a video model.
        
        Returns:
            Tuple of (max_videos, default_count)
        """
        config = get_model_config(model_id)
        if not config or config.type != "video":
            return 1, 1
            
        caps = config.capabilities
        return caps.max_videos, 1
    
    def get_video_count_choices_for_interactive(self, model_id: str) -> List[Tuple[str, str]]:
        """Get video count choices formatted for interactive prompts."""
        max_videos, _ = self.get_video_count_options(model_id)
        
        if max_videos == 1:
            # Only one video allowed, don't show choice
            return []
            
        choices = []
        for i in range(1, max_videos + 1):
            emoji = "🎬" * i
            plural = "" if i == 1 else "s"
            display = f"{i} video{plural} {emoji}"
            choices.append((display, str(i)))
            
        return choices
    
    def get_aspect_ratio_options(self, model_id: str) -> List[str]:
        """Get available aspect ratios for a model."""
        config = get_model_config(model_id)
        if not config:
            return ["16:9"]
            
        if config.type == "video":
            return config.capabilities.aspect_ratios
        else:
            return config.capabilities.aspect_ratios
    
    def get_resolution_options(self, model_id: str) -> List[str]:
        """Get available resolutions for a model."""
        config = get_model_config(model_id)
        if not config:
            return ["1080p"]
            
        return config.capabilities.resolutions
    
    def validate_and_correct_options(self, model_id: str, **options) -> Dict[str, Any]:
        """
        Validate options against model capabilities and return corrected values.
        
        Returns:
            Dict with validated/corrected option values
        """
        validation = validate_model_options(model_id, **options)
        
        if not validation["valid"]:
            console.print(f"[red]Error: {validation['error']}[/red]")
            return {}
        
        # Apply corrections and show warnings
        corrected_options = dict(options)
        if "corrections" in validation:
            for option, corrected_value in validation["corrections"].items():
                if option in options:
                    console.print(
                        f"[yellow]Warning: {option}={options[option]} not supported by {model_id}. "
                        f"Using {corrected_value} instead.[/yellow]"
                    )
                    corrected_options[option] = corrected_value
        
        return corrected_options
    
    def get_model_capabilities_summary(self, model_id: str) -> str:
        """Get a formatted summary of model capabilities."""
        config = get_model_config(model_id)
        if not config:
            return "Unknown model"
        
        if config.type == "video":
            caps = config.capabilities
            lines = [
                f"**{config.display_name}**",
                f"Type: Video Generation",
                f"Max Videos: {caps.max_videos}",
                f"Duration: {caps.duration.min}-{caps.duration.max} seconds",
                f"Aspect Ratios: {', '.join(caps.aspect_ratios)}",
                f"Resolutions: {', '.join(caps.resolutions)}",
                f"Frame Rates: {', '.join(map(str, caps.frame_rates))} FPS",
                f"Image-to-Video: {'Yes' if caps.supports_image_to_video else 'No'}",
                f"Prompt Enhancement: {'Yes' if caps.supports_prompt_enhancement else 'No'}",
                f"Video Extension: {'Yes' if caps.supports_extend_video else 'No'}",
            ]
        else:
            caps = config.capabilities
            lines = [
                f"**{config.display_name}**",
                f"Type: Image Generation",
                f"Max Images: {caps.max_images}",
                f"Aspect Ratios: {', '.join(caps.aspect_ratios)}",
                f"Resolutions: {', '.join(caps.resolutions)}",
                f"Prompt Enhancement: {'Yes' if caps.supports_prompt_enhancement else 'No'}",
            ]
            if caps.styles:
                lines.append(f"Styles: {', '.join(caps.styles)}")
        
        return "\n".join(lines)
    
    def show_model_info(self, model_id: str):
        """Display model capabilities in a formatted panel."""
        summary = self.get_model_capabilities_summary(model_id)
        panel = Panel(
            summary,
            title="[bold cyan]Model Capabilities[/bold cyan]",
            title_align="left",
            style="cyan"
        )
        console.print(panel)


# Global model manager instance
model_manager = ModelManager()