import time
import os
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.box import ROUNDED
from rich.columns import Columns
from rich import print as rprint
from enum import Enum
import inquirer
from datetime import datetime

from google import genai
from google.genai.types import GenerateVideosConfig, Video

from dotenv import load_dotenv
import os
from . import ui_components as ui
from . import download
from .model_manager import model_manager
from .models_config import get_model_config

load_dotenv()


def get_value(param):
    """
    Helper function to get value from enum or string parameter.
    
    Args:
        param: Either an enum with .value attribute or a string
        
    Returns:
        The actual value (string)
    """
    return param.value if hasattr(param, 'value') else param


def get_default_gcs_uri() -> str:
    """
    Get the default GCS URI from environment variables.

    Returns:
        str: Default GCS URI for video output

    Raises:
        ValueError: If GCS bucket is not configured
    """
    bucket_name = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
    bucket_path = os.getenv("GOOGLE_CLOUD_STORAGE_PATH", "videos")

    if not bucket_name:
        raise ValueError(
            "GOOGLE_CLOUD_STORAGE_BUCKET environment variable is required. "
            "Please add it to your .env file."
        )

    # Ensure bucket path doesn't start with slash
    bucket_path = bucket_path.lstrip("/")

    return f"gs://{bucket_name}/{bucket_path}"


app = typer.Typer(
    name="ai-studio",
    help="🎨 AI MEDIA STUDIO CLI - Professional Multi-Modal AI Media Generation by Abdulrahman Elsmmany",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()
client = genai.Client()


# Dynamic model choices
def get_available_models():
    """Get list of available model IDs."""
    return list(model_manager.video_models.keys())


# Static enums (these can be made dynamic later if needed)
class AspectRatio(str, Enum):
    widescreen = "16:9"
    portrait = "9:16"


class Resolution(str, Enum):
    hd_720 = "720"
    full_hd_1080 = "1080"


class FrameRate(str, Enum):
    fps_24 = "24"


def test_file_access(file_path: Path) -> bool:
    """
    Test if a file can be accessed and read.
    
    Args:
        file_path: Path to test
        
    Returns:
        True if file exists and is readable
    """
    try:
        return file_path.exists() and file_path.is_file() and file_path.stat().st_size > 0
    except (OSError, PermissionError):
        return False


def create_video_object(video_path: str) -> Video:
    """
    Create a Video object from either a GCS URI or local file path.

    Args:
        video_path: Either a GCS URI (gs://...) or local file path

    Returns:
        Video object with appropriate parameters

    Raises:
        FileNotFoundError: If local file doesn't exist
        ValueError: If file format is not supported
    """
    if video_path.startswith("gs://"):
        # GCS URI - use uri parameter
        return Video(uri=video_path)
    else:
        # Local file path - read and use video_bytes
        # Clean up the path: remove quotes and normalize
        cleaned_path = video_path.strip().strip('"').strip("'")
        file_path = Path(cleaned_path).resolve()  # resolve() normalizes the path

        if not test_file_access(file_path):
            # Try various path formats for Windows compatibility
            possible_paths = [
                Path(cleaned_path),
                Path(cleaned_path.replace("\\", "/")),
                Path(cleaned_path.replace("/", "\\")),
            ]
            
            # Try to find a working path
            working_path = None
            for try_path in possible_paths:
                try:
                    resolved_path = try_path.resolve()
                    if test_file_access(resolved_path):
                        working_path = resolved_path
                        break
                except (OSError, ValueError):
                    continue
            
            if working_path:
                file_path = working_path
                console.print(f"[green]✓ Found video at: {file_path}[/green]")
            else:
                # Create detailed error message
                error_msg = f"Video file not found or not accessible: {cleaned_path}\n\nTroubleshooting:\n"
                error_msg += f"• Check if the file exists\n"
                error_msg += f"• Ensure you have read permissions\n" 
                error_msg += f"• Try using forward slashes: {cleaned_path.replace(chr(92), '/')}\n"
                error_msg += f"• Remove quotes from the path\n"
                error_msg += f"\nTried these paths:\n"
                for i, try_path in enumerate(possible_paths, 1):
                    try:
                        resolved = try_path.resolve()
                        exists = resolved.exists() if resolved else False
                        error_msg += f"{i}. {resolved} (exists: {exists})\n"
                    except Exception as e:
                        error_msg += f"{i}. {try_path} (error: {e})\n"
                
                raise FileNotFoundError(error_msg)

        if not file_path.suffix.lower() in [".mp4", ".mov", ".avi", ".mkv"]:
            raise ValueError(
                f"Unsupported video format: {file_path.suffix}. Supported: .mp4, .mov, .avi, .mkv"
            )

        # Read video bytes
        with open(file_path, "rb") as f:
            video_bytes = f.read()

        # Determine MIME type
        mime_type = "video/mp4"  # Default
        if file_path.suffix.lower() == ".mov":
            mime_type = "video/quicktime"
        elif file_path.suffix.lower() == ".avi":
            mime_type = "video/x-msvideo"
        elif file_path.suffix.lower() == ".mkv":
            mime_type = "video/x-matroska"

        return Video(video_bytes=video_bytes, mime_type=mime_type)


def startup_callback():
    """
    Show branding on startup
    """
    if not hasattr(app, "_startup_shown"):
        console.print(ui.create_compact_header())
        console.print()
        console.print(ui.create_developer_footer())
        console.print()
        app._startup_shown = True


@app.callback()
def main():
    """
    AI MEDIA STUDIO CLI - Professional multi-modal AI media generation tool.

    Generate videos, images, and music with Google's AI models using simple text prompts.
    🎬 Videos • 🖼️ Images • 🎵 Music - All powered by AI.

    Created with ❤️ by Abdulrahman Elsmmany.
    """
    startup_callback()


@app.command()
def generate(
    prompt: str = typer.Option(
        ...,
        "--prompt",
        "-p",
        help="Video generation prompt. Follow Google's prompt guide for best results.",
        rich_help_panel="Generation Options",
    ),
    model: str = typer.Option(
        "veo-001",
        "--model",
        "-m",
        help="Choose video generation model (veo-001: stable, up to 4 videos | veo-preview: latest features, up to 2 videos)",
        rich_help_panel="Generation Options",
    ),
    aspect_ratio: AspectRatio = typer.Option(
        AspectRatio.widescreen,
        "--aspect-ratio",
        "-ar",
        help="Video aspect ratio (fixed at 16:9 for Veo 3 models)",
        rich_help_panel="Video Settings",
    ),
    resolution: Resolution = typer.Option(
        Resolution.full_hd_1080,
        "--resolution",
        "-r",
        help="Video resolution: 720p or 1080p",
        rich_help_panel="Video Settings",
    ),
    framerate: FrameRate = typer.Option(
        FrameRate.fps_24,
        "--framerate",
        "-fps",
        help="Video framerate (currently only 24 FPS supported)",
        rich_help_panel="Video Settings",
    ),
    number_of_videos: int = typer.Option(
        1,
        "--videos",
        "-n",
        min=1,
        max=4,
        help="Number of videos to generate (1-4 for veo-001, 1-2 for preview)",
        rich_help_panel="Generation Options",
    ),
    duration_seconds: int = typer.Option(
        8,
        "--duration",
        "-d",
        help="Video duration in seconds (fixed at 8s for Veo 3 models)",
        rich_help_panel="Video Settings",
    ),
    enhance_prompt: bool = typer.Option(
        True,
        "--enhance/--no-enhance",
        help="Enable prompt enhancement for better results",
        rich_help_panel="Generation Options",
    ),
    output_gcs_uri: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Google Cloud Storage URI for output videos (uses GOOGLE_CLOUD_STORAGE_BUCKET from .env if not specified)",
        rich_help_panel="Output Options",
    ),
    wait_for_completion: bool = typer.Option(
        True,
        "--wait/--no-wait",
        help="Wait for video generation to complete",
        rich_help_panel="Output Options",
    ),
    auto_download: bool = typer.Option(
        True,
        "--download/--no-download",
        help="Automatically download generated media to organized local folders",
        rich_help_panel="Output Options",
    ),
    download_folder: str = typer.Option(
        "downloaded_media",
        "--download-folder",
        "-d",
        help="Local folder name for downloaded media (created in project root, auto-organized by type)",
        rich_help_panel="Output Options",
    ),
    cleanup_gcs: bool = typer.Option(
        True,
        "--cleanup/--no-cleanup",
        help="Delete GCS files after successful download (saves storage costs)",
        rich_help_panel="Output Options",
    ),
    extend_video_path: Optional[str] = typer.Option(
        None,
        "--extend-video",
        "-ev",
        help="Path to existing video to extend - supports GCS URIs (gs://) or local file paths (only for models that support video extension)",
        rich_help_panel="Video Extension",
    ),
):
    """
    Generate videos using Google's Veo AI models with customizable options.

    [bold cyan]Examples:[/bold cyan]

    Basic usage:
    [dim]$ labsfx generate -p "a cat reading a book"[/dim]

    Advanced usage:
    [dim]$ labsfx generate -p "cinematic shot of a sunset over mountains" -m veo-3.0-generate-001 -ar 16:9 -r 1080 -n 2 -d 8[/dim]
    """

    # Validate model exists
    model_config = get_model_config(model)
    if not model_config:
        available_models = ", ".join(get_available_models())
        console.print(
            ui.create_error_panel(
                f"Unknown model: {model}. Available models: {available_models}"
            )
        )
        raise typer.Exit(1)

    # Validate video extension capability
    if extend_video_path and not model_config.capabilities.supports_extend_video:
        console.print(
            ui.create_error_panel(
                f"Model {model_config.display_name} does not support video extension. "
                f"Use a model with video extension support like veo2-001."
            )
        )
        raise typer.Exit(1)

    # Validate video file/URI if extending
    if extend_video_path:
        try:
            # This will validate the file exists and format is supported
            video_obj = create_video_object(extend_video_path)
        except (FileNotFoundError, ValueError) as e:
            console.print(ui.create_error_panel(str(e)))
            raise typer.Exit(1)

    # Set default GCS URI if not provided
    if not output_gcs_uri:
        try:
            output_gcs_uri = get_default_gcs_uri()
        except ValueError as e:
            console.print(ui.create_error_panel(str(e)))
            raise typer.Exit(1)

    # Validate and correct model-specific constraints
    corrected_options = model_manager.validate_and_correct_options(
        model,
        number_of_videos=number_of_videos,
        duration_seconds=duration_seconds,
        aspect_ratio=get_value(aspect_ratio),
        resolution=get_value(resolution),
    )

    # Apply corrections
    if "number_of_videos" in corrected_options:
        number_of_videos = corrected_options["number_of_videos"]
    if "duration_seconds" in corrected_options:
        duration_seconds = corrected_options["duration_seconds"]

    # Create configuration display
    config = {
        "Prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
        "Model": model_config.display_name,
        "Aspect Ratio": get_value(aspect_ratio),
        "Resolution": f"{get_value(resolution)}p",
        "Frame Rate": f"{get_value(framerate)} FPS",
        "Videos": str(number_of_videos),
        "Duration": f"{duration_seconds}s",
        "Enhance": "✓" if enhance_prompt else "✗",
    }

    # Add extension info if extending a video
    if extend_video_path:
        config["Extension"] = "✓ Extending existing video"
        if extend_video_path.startswith("gs://"):
            config["Source Video"] = extend_video_path.split("/")[
                -1
            ]  # Show filename from URI
        else:
            config["Source Video"] = Path(extend_video_path).name  # Show local filename

    # Display configuration
    config_panel = Panel(
        ui.create_config_table(config),
        title="[bold]Generation Configuration[/bold]",
        title_align="left",
        style="bright_blue",
    )
    console.print(config_panel)
    console.print()

    try:
        # Create status cards layout
        status_cards = Columns(
            [
                ui.create_status_card("Status", "Initializing", "◉", "yellow"),
                ui.create_status_card(
                    "Model", get_value(model).split("-")[-1].upper(), "🤖", "blue"
                ),
                ui.create_status_card("Videos", str(number_of_videos), "📹", "green"),
                ui.create_status_card(
                    "Duration", f"{duration_seconds}s", "⏱️", "magenta"
                ),
            ],
            equal=True,
            expand=True,
        )

        console.print(status_cards)
        console.print()

        config = GenerateVideosConfig(
            aspect_ratio=get_value(aspect_ratio),
            output_gcs_uri=output_gcs_uri,
            number_of_videos=number_of_videos,
            duration_seconds=duration_seconds,
            enhance_prompt=enhance_prompt,
        )

        # Prepare API call parameters
        api_params = {
            "model": model_config.api_model_name,
            "prompt": prompt,
            "config": config,
        }

        # Add video parameter if extending
        if extend_video_path:
            api_params["video"] = create_video_object(extend_video_path)

        operation = client.models.generate_videos(**api_params)

        # Handle operation ID - it might be a string or an object with a name attribute
        if hasattr(operation, "name"):
            operation_id = operation.name
        else:
            operation_id = str(operation)
        operation_panel = ui.create_operation_status_panel(operation_id, "in_progress")
        console.print(operation_panel)

        if wait_for_completion:
            with Progress(
                SpinnerColumn(style="bold blue"),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(style="blue"),
                TimeRemainingColumn(),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task(
                    "[bold blue]Generating video...[/bold blue]", total=100
                )

                start_time = time.time()
                while not getattr(operation, "done", False):
                    time.sleep(5)
                    try:
                        # Refresh operation status using the correct API method
                        operation = client.operations.get(operation)
                    except Exception as e:
                        console.print(
                            f"[red]Error refreshing operation status: {e}[/red]"
                        )
                        # Fallback: break out of loop after timeout
                        if elapsed > 300:  # 5 minutes timeout
                            console.print(
                                f"[yellow]Timeout: Operation taking longer than expected[/yellow]"
                            )
                            break

                    # Update progress based on time (rough estimate)
                    elapsed = time.time() - start_time
                    estimated_progress = min(
                        95, (elapsed / 120) * 100
                    )  # Assume ~2 min generation

                    progress.update(
                        task,
                        completed=estimated_progress,
                        description=f"[bold blue]Processing... [{int(elapsed)}s][/bold blue]",
                    )

                progress.update(
                    task,
                    completed=100,
                    description="[bold green]Complete![/bold green]",
                )

            if getattr(operation, "response", None):
                console.print()
                result = getattr(operation, "result", None)
                videos = []
                if result and hasattr(result, "generated_videos"):
                    videos = [video.video.uri for video in result.generated_videos]
                    console.print(ui.create_video_result_panel(videos))

                    # Summary statistics
                    console.print()
                    console.print(
                        Panel(
                            f"[bold green]✓[/bold green] Successfully generated {len(videos)} video(s) in {int(time.time() - start_time)} seconds",
                            style="green",
                        )
                    )

                    # Auto-download videos if enabled
                    if auto_download and videos:
                        console.print()
                        downloaded_videos = download.download_media(
                            videos, download_folder, cleanup_gcs, organize_by_type=True
                        )
                        download.print_download_summary(
                            downloaded_videos, len(videos), download_folder, organized=True
                        )

                    # Developer credit shown by calling function
                else:
                    console.print(ui.create_error_panel("No videos were generated"))

            else:
                error_msg = getattr(operation, "error", "Unknown error occurred")
                console.print(ui.create_error_panel(str(error_msg)))

        else:
            console.print(
                Panel(
                    f"[bold yellow]⏳[/bold yellow] Operation started in background\n\nOperation ID: [bold cyan]{operation_id}[/bold cyan]\n\nOperation will continue processing. Re-run with --wait to wait for completion.",
                    style="yellow",
                )
            )
            # Developer credit shown by calling function

    except Exception as e:
        console.print(ui.create_error_panel(str(e)))
        raise typer.Exit(1)


@app.command()
def interactive():
    """
    Interactive mode for video generation with guided prompts.

    [bold cyan]Features:[/bold cyan]
    • Step-by-step configuration
    • Prompt writing guidance
    • Visual parameter selection
    • Real-time validation
    """

    console.clear()
    console.print(ui.create_header())
    console.print()

    # Show prompt guide
    console.print(ui.create_prompt_guide_panel())
    console.print()

    # Get prompt with validation
    prompt = Prompt.ask(
        "[bold cyan]Enter your video prompt[/bold cyan]",
        default="",
    )

    if not prompt:
        console.print(ui.create_error_panel("Prompt cannot be empty!"))
        raise typer.Exit(1)

    console.print()
    console.print(
        Panel(
            f"[italic]{prompt}[/italic]", title="[bold]Your Prompt[/bold]", style="cyan"
        )
    )
    console.print()

    # Dynamic model selection  
    model_choices = model_manager.get_model_choices_for_interactive("video")
    questions = [
        inquirer.List(
            "model",
            message="Choose AI model",
            choices=model_choices,
            default=model_choices[0][1] if model_choices else "veo-001",
        ),
    ]
    model_answer = inquirer.prompt(questions)
    model = model_answer["model"]
    model_config = get_model_config(model)

    # Aspect ratio fixed at 16:9 for Veo 3 models
    aspect_ratio = AspectRatio.widescreen

    # Dynamic resolution selection based on model capabilities
    resolution_choices = []
    supported_resolutions = model_config.capabilities.resolutions
    
    # Create user-friendly choices based on model capabilities
    for res in supported_resolutions:
        if res == "720p":
            resolution_choices.append(("720p - HD (Faster generation)", "720"))
        elif res == "1080p":
            resolution_choices.append(("1080p - Full HD (Best quality)", "1080"))
    
    # Use the first supported resolution as default
    default_resolution = supported_resolutions[0].rstrip('p') if supported_resolutions else "720"
    
    questions = [
        inquirer.List(
            "resolution",
            message=f"Choose video quality (supported by {model_config.display_name})",
            choices=resolution_choices,
            default=default_resolution,
        ),
    ]
    res_answer = inquirer.prompt(questions)
    resolution = (
        Resolution.full_hd_1080
        if res_answer["resolution"] == "1080"
        else Resolution.hd_720
    )

    # Dynamic video count selection based on model
    video_choices = model_manager.get_video_count_choices_for_interactive(model)
    if video_choices:  # Only show choice if model supports multiple videos
        questions = [
            inquirer.List(
                "number_of_videos",
                message=f"Number of videos (max {model_config.capabilities.max_videos} for {model_config.display_name})",
                choices=video_choices,
                default="1",
            ),
        ]
        videos_answer = inquirer.prompt(questions)
        number_of_videos = int(videos_answer["number_of_videos"])
    else:
        number_of_videos = 1  # Only one video supported

    # Dynamic duration selection based on model
    duration_choices = model_manager.get_duration_choices_for_interactive(model)
    if duration_choices:  # Only show choice if model has multiple duration options
        questions = [
            inquirer.List(
                "duration",
                message="Video duration",
                choices=duration_choices,
                default=str(model_config.capabilities.duration.default),
            ),
        ]
        duration_answer = inquirer.prompt(questions)
        duration_seconds = int(duration_answer["duration"])
    else:
        # Use model default if only one option
        duration_seconds = model_config.capabilities.duration.default

    # Video extension option (only for models that support it)
    extend_video_path = None
    if model_config.capabilities.supports_extend_video:
        questions = [
            inquirer.List(
                "extend_mode",
                message="Video generation mode",
                choices=[
                    ("📹 Create new video - Generate from scratch", "new"),
                    ("➕ Extend video - Continue an existing video", "extend"),
                ],
                default="new",
            ),
        ]
        extend_answer = inquirer.prompt(questions)

        if extend_answer["extend_mode"] == "extend":
            console.print()
            console.print(
                Panel(
                    "[bold cyan]Video Extension Options:[/bold cyan]\n\n"
                    "• [bold]GCS URI:[/bold] gs://bucket/path/to/video.mp4\n"
                    "• [bold]Local file:[/bold] C:/path/to/video.mp4 or C:\\path\\to\\video.mp4\n\n"
                    "[yellow]💡 Tips for Windows paths:[/yellow]\n"
                    "• Use forward slashes: C:/Users/Name/video.mp4\n" 
                    "• Or escape backslashes: C:\\\\Users\\\\Name\\\\video.mp4\n"
                    "• Don't use quotes unless the path contains spaces\n"
                    "• If path has spaces, use quotes: \"C:/My Videos/video.mp4\"\n\n"
                    "[dim]Supported formats: .mp4, .mov, .avi, .mkv[/dim]",
                    title="[bold]How to Specify Video[/bold]",
                    style="cyan",
                )
            )
            console.print()

            extend_video_path = Prompt.ask(
                "[bold cyan]Enter video path (GCS URI or local file)[/bold cyan]",
                default="",
            )

            if not extend_video_path:
                console.print(
                    ui.create_error_panel(
                        "Video path cannot be empty for extension mode!"
                    )
                )
                raise typer.Exit(1)

            # Strip quotes from the path if present
            extend_video_path = extend_video_path.strip('"').strip("'")

            # Validate the video path
            try:
                console.print(f"[dim]Processing video path: {extend_video_path}[/dim]")
                video_obj = create_video_object(extend_video_path)
                if extend_video_path.startswith("gs://"):
                    console.print(
                        f"[green]✓ Using GCS video: {extend_video_path.split('/')[-1]}[/green]"
                    )
                else:
                    file_size = Path(extend_video_path).stat().st_size / (
                        1024 * 1024
                    )  # MB
                    console.print(
                        f"[green]✓ Using local video: {Path(extend_video_path).name} ({file_size:.1f} MB)[/green]"
                    )
            except (FileNotFoundError, ValueError) as e:
                console.print(ui.create_error_panel(str(e)))
                raise typer.Exit(1)

    # Enhancement option
    questions = [
        inquirer.List(
            "enhance",
            message="AI prompt enhancement",
            choices=[
                ("✨ Yes - Optimize my prompt for better results", True),
                ("✗ No - Use my exact prompt", False),
            ],
            default=True,
        ),
    ]
    enhance_answer = inquirer.prompt(questions)
    enhance_prompt = enhance_answer["enhance"]

    # Final summary
    console.print()
    summary_config = {
        "Prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
        "Model": model_config.display_name,
        "Aspect Ratio": get_value(aspect_ratio),
        "Resolution": f"{get_value(resolution)}p",
        "Videos": str(number_of_videos),
        "Duration": f"{duration_seconds}s",
        "Enhancement": "Enabled" if enhance_prompt else "Disabled",
    }

    # Add extension info if extending a video
    if extend_video_path:
        summary_config["Mode"] = "Video Extension"
        if extend_video_path.startswith("gs://"):
            summary_config["Source Video"] = extend_video_path.split("/")[
                -1
            ]  # Show filename from URI
        else:
            summary_config["Source Video"] = Path(
                extend_video_path
            ).name  # Show local filename

    summary_panel = Panel(
        ui.create_config_table(summary_config),
        title="[bold green]Ready to Generate[/bold green]",
        title_align="left",
        style="green",
    )
    console.print(summary_panel)
    
    # Interactive Review and Confirmation with Navigation
    while True:
        console.print()
        nav_choices = [
            ("🚀 Start Generation - Everything looks good!", "generate"),
            ("✏️ Change Prompt", "change_prompt"),
            ("🤖 Change Model", "change_model"), 
            ("🎬 Change Resolution", "change_resolution"),
            ("✨ Change Enhancement", "change_enhancement"),
            ("❌ Cancel", "cancel"),
        ]
        
        # Add conditional choices only if they have options
        if video_choices and len(video_choices) > 1:
            nav_choices.insert(-2, ("🔢 Change Video Count", "change_videos"))
        if duration_choices and len(duration_choices) > 1:
            nav_choices.insert(-2, ("⏱️ Change Duration", "change_duration"))
        
        questions = [
            inquirer.List(
                "action",
                message="Review your settings - What would you like to do?",
                choices=nav_choices,
                default="generate",
            ),
        ]
        
        action_answer = inquirer.prompt(questions)
        action = action_answer["action"]
        
        if action == "generate":
            break
        elif action == "cancel":
            console.print("[yellow]👋 Interactive mode cancelled.[/yellow]")
            raise typer.Exit(0)
        elif action == "change_prompt":
            console.print(ui.create_prompt_guide_panel())
            console.print()
            new_prompt = Prompt.ask(
                "[bold cyan]Enter your video prompt[/bold cyan]",
                default=prompt,
            )
            if new_prompt and new_prompt != prompt:
                prompt = new_prompt
                summary_config["Prompt"] = prompt[:50] + "..." if len(prompt) > 50 else prompt
                console.print(f"[green]✓ Prompt updated![/green]")
                console.print(Panel(
                    ui.create_config_table(summary_config),
                    title="[bold green]Updated Configuration[/bold green]",
                    style="green",
                ))
        elif action == "change_model":
            questions = [
                inquirer.List(
                    "model",
                    message="Choose AI model",
                    choices=model_choices,
                    default=model,
                ),
            ]
            new_model_answer = inquirer.prompt(questions)
            new_model = new_model_answer["model"]
            if new_model != model:
                model = new_model
                model_config = get_model_config(model)
                summary_config["Model"] = model_config.display_name
                console.print(f"[green]✓ Model updated to {model_config.display_name}![/green]")
                console.print("[yellow]⚠️ Resolution and duration options may have changed.[/yellow]")
                console.print(Panel(
                    ui.create_config_table(summary_config),
                    title="[bold green]Updated Configuration[/bold green]",
                    style="green",
                ))
        elif action == "change_resolution":
            # Refresh resolution choices for current model
            resolution_choices = []
            supported_resolutions = model_config.capabilities.resolutions
            for res in supported_resolutions:
                if res == "720p":
                    resolution_choices.append(("720p - HD (Faster generation)", "720"))
                elif res == "1080p":
                    resolution_choices.append(("1080p - Full HD (Best quality)", "1080"))
            
            questions = [
                inquirer.List(
                    "resolution",
                    message=f"Choose video quality (supported by {model_config.display_name})",
                    choices=resolution_choices,
                    default=get_value(resolution),
                ),
            ]
            new_res_answer = inquirer.prompt(questions)
            new_resolution = (
                Resolution.full_hd_1080
                if new_res_answer["resolution"] == "1080"
                else Resolution.hd_720
            )
            if new_resolution != resolution:
                resolution = new_resolution
                summary_config["Resolution"] = f"{get_value(resolution)}p"
                console.print(f"[green]✓ Resolution updated to {get_value(resolution)}p![/green]")
                console.print(Panel(
                    ui.create_config_table(summary_config),
                    title="[bold green]Updated Configuration[/bold green]",
                    style="green",
                ))
        elif action == "change_videos" and video_choices:
            questions = [
                inquirer.List(
                    "number_of_videos",
                    message=f"Number of videos (max {model_config.capabilities.max_videos})",
                    choices=video_choices,
                    default=str(number_of_videos),
                ),
            ]
            new_videos_answer = inquirer.prompt(questions)
            new_number_of_videos = int(new_videos_answer["number_of_videos"])
            if new_number_of_videos != number_of_videos:
                number_of_videos = new_number_of_videos
                summary_config["Videos"] = str(number_of_videos)
                console.print(f"[green]✓ Video count updated to {number_of_videos}![/green]")
                console.print(Panel(
                    ui.create_config_table(summary_config),
                    title="[bold green]Updated Configuration[/bold green]",
                    style="green",
                ))
        elif action == "change_duration" and duration_choices:
            questions = [
                inquirer.List(
                    "duration",
                    message="Video duration",
                    choices=duration_choices,
                    default=str(duration_seconds),
                ),
            ]
            new_duration_answer = inquirer.prompt(questions)
            new_duration_seconds = int(new_duration_answer["duration"])
            if new_duration_seconds != duration_seconds:
                duration_seconds = new_duration_seconds
                summary_config["Duration"] = f"{duration_seconds}s"
                console.print(f"[green]✓ Duration updated to {duration_seconds}s![/green]")
                console.print(Panel(
                    ui.create_config_table(summary_config),
                    title="[bold green]Updated Configuration[/bold green]",
                    style="green",
                ))
        elif action == "change_enhancement":
            questions = [
                inquirer.List(
                    "enhance",
                    message="AI prompt enhancement",
                    choices=[
                        ("✨ Yes - Optimize my prompt for better results", True),
                        ("✗ No - Use my exact prompt", False),
                    ],
                    default=enhance_prompt,
                ),
            ]
            new_enhance_answer = inquirer.prompt(questions)
            new_enhance_prompt = new_enhance_answer["enhance"]
            if new_enhance_prompt != enhance_prompt:
                enhance_prompt = new_enhance_prompt
                summary_config["Enhancement"] = "Enabled" if enhance_prompt else "Disabled"
                console.print(f"[green]✓ Enhancement {'enabled' if enhance_prompt else 'disabled'}![/green]")
                console.print(Panel(
                    ui.create_config_table(summary_config),
                    title="[bold green]Updated Configuration[/bold green]",
                    style="green",
                ))

    console.print()

    # Call generate with collected parameters
    generate(
        prompt=prompt,
        model=model,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        framerate=FrameRate.fps_24,
        number_of_videos=number_of_videos,
        duration_seconds=duration_seconds,
        enhance_prompt=enhance_prompt,
        output_gcs_uri=None,
        wait_for_completion=True,
        auto_download=True,
        download_folder="downloaded_media",
        cleanup_gcs=True,
        extend_video_path=extend_video_path,
    )

    # Show persistent developer credit after interactive completion
    console.print()
    console.print(ui.create_developer_footer())


@app.command()
def about():
    """
    Show information about AI Media Studio CLI
    """
    console.clear()
    console.print(ui.create_header())
    console.print()

    about_text = """[bold bright_magenta]AI MEDIA STUDIO CLI[/bold bright_magenta] - Version 2.0.0

🎨 Professional multi-modal AI media generation tool built on Google's AI models.

[bold cyan]✨ Multi-Modal Capabilities:[/bold cyan]
• 🎬 Generate videos from text prompts with Veo 2.0 & 3.0
• 🖼️ Create images with Google Imagen (coming soon)
• 🎵 Compose music with Google MusicLM (planned)
• 🎨 Support for multiple formats, resolutions, and styles
• 📹 Batch generation and processing workflows
• ➕ Video extension and continuation features
• 🖥️ Interactive and command-line modes
• ⚡ Real-time progress tracking with ETA
• 📁 Intelligent media organization and downloads

[bold cyan]🤖 Currently Available Models:[/bold cyan]
• [bold]Veo 2.0[/bold] - Most flexible video generation with 5-8s duration, video extension
• [bold]Veo 3.0 Generate 001[/bold] - Stable text-to-video with prompt enhancement
• [bold]Veo 3.0 Generate Preview[/bold] - Latest features with image-to-video

[bold cyan]🗺️ Coming Soon:[/bold cyan]
• [bold]Google Imagen[/bold] - High-quality image generation with style control
• [bold]Google MusicLM[/bold] - AI music composition and generation

[bold cyan]🔗 Links:[/bold cyan]
• Repository: https://github.com/Abdulrahman-Elsmmany/ai-media-studio-cli
• Issues: https://github.com/Abdulrahman-Elsmmany/ai-media-studio-cli/issues
• Developer: https://github.com/Abdulrahman-Elsmmany

[bold yellow]Created with ❤️  by Abdulrahman Elsmmany[/bold yellow]"""

    console.print(
        Panel(
            about_text,
            title="[bold]About AI Media Studio CLI[/bold]",
            style="bright_blue",
            padding=(1, 2),
            box=ROUNDED,
        )
    )

    console.print()
    console.print(ui.create_developer_footer())


if __name__ == "__main__":
    app()
