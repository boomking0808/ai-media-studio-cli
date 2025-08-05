"""
UI components for AI Media Studio CLI
"""

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.box import ROUNDED, DOUBLE
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from typing import List, Dict, Any


console = Console()


def create_header():
    """
    Create professional branded header for AI Media Studio CLI
    """
    # Create large ASCII art for AI MEDIA STUDIO CLI (properly aligned)
    header_art_text = """
╔═════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                     ║
║     █████  ██       ███    ███ ███████ ██████  ██  █████                            ║
║    ██   ██ ██       ████  ████ ██      ██   ██ ██ ██   ██                           ║
║    ███████ ██       ██ ████ ██ █████   ██   ██ ██ ███████                           ║
║    ██   ██ ██       ██  ██  ██ ██      ██   ██ ██ ██   ██                           ║
║    ██   ██ ██       ██      ██ ███████ ██████  ██ ██   ██                           ║
║                                                                                     ║
║    ███████ ████████ ██    ██ ██████  ██  ██████      ██████ ██      ██              ║
║    ██         ██    ██    ██ ██   ██ ██ ██    ██    ██      ██      ██              ║
║    ███████    ██    ██    ██ ██   ██ ██ ██    ██    ██      ██      ██              ║
║         ██    ██    ██    ██ ██   ██ ██ ██    ██    ██      ██      ██              ║
║    ███████    ██     ██████  ██████  ██  ██████      ██████ ███████ ██              ║
║                                                                                     ║
╚═════════════════════════════════════════════════════════════════════════════════════╝
"""

    # Create Text objects with proper styling
    header_art = Text()
    header_art.append(header_art_text, style="bold bright_magenta")

    subtitle = Text()
    subtitle.append(
        "🎨 Professional Multi-Modal AI Media Generation Tool 🚀",
        style="bold bright_cyan",
    )

    tagline = Text()
    tagline.append(
        "Generate Videos 🎬 • Create Images 🖼️  • Compose Music 🎵",
        style="bold bright_green",
    )

    developer_credit = Text()
    developer_credit.append("Created with ❤️  by ", style="bold yellow")
    developer_credit.append(
        "Abdulrahman Elsmmany",
        style="bold bright_red link https://github.com/Abdulrahman-Elsmmany",
    )

    content = Text()
    content.append(header_art)
    content.append("\n\n")
    content.append(subtitle)
    content.append("\n")
    content.append(tagline)
    content.append("\n\n")
    content.append(developer_credit)

    header_panel = Panel(
        Align.center(content), box=DOUBLE, style="bright_blue", padding=(1, 2)
    )

    return header_panel


def create_compact_header():
    """
    Create a compact header for startup/general use
    """
    header_text = Text()
    header_text.append("AI MEDIA STUDIO CLI", style="bold bright_magenta")

    subtitle = Text()
    subtitle.append("🎨 Multi-Modal AI Media Generation", style="bold bright_cyan")

    tagline = Text()
    tagline.append("Videos 🎬 • Images 🖼️ • Music 🎵", style="dim bright_green")

    developer_credit = Text()
    developer_credit.append("by ", style="dim")
    developer_credit.append("Abdulrahman Elsmmany", style="bold bright_red")

    content = Text()
    content.append(header_text)
    content.append("\n")
    content.append(subtitle)
    content.append("\n")
    content.append(tagline)
    content.append("\n")
    content.append(developer_credit)

    return Panel(
        Align.center(content),
        box=ROUNDED,
        style="bright_blue",
        padding=(1, 2),
    )


def create_status_card(
    title: str, value: str, icon: str = "▸", style: str = "cyan"
) -> Panel:
    """
    Create a status card for displaying information
    """
    content = f"{icon} [bold {style}]{value}[/bold {style}]"
    return Panel(
        content,
        title=f"[bold]{title}[/bold]",
        title_align="left",
        box=ROUNDED,
        padding=(0, 1),
        style=style,
    )


def create_config_table(config: Dict[str, Any]) -> Table:
    """
    Create a configuration table
    """
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 2),
        expand=False,
    )

    table.add_column("Property", style="dim", width=20)
    table.add_column("Value", style="bold")

    for key, value in config.items():
        table.add_row(key, str(value))

    return table


def create_video_result_panel(videos: List[str]) -> Panel:
    """
    Create a panel for video results
    """
    content = ""
    for i, video_uri in enumerate(videos, 1):
        content += f"[bold green]✓[/bold green] Video {i}: [link]{video_uri}[/link]\n"

    return Panel(
        content.strip(),
        title="[bold green]Generated Videos[/bold green]",
        title_align="left",
        box=ROUNDED,
        style="green",
        padding=(1, 2),
    )


def create_download_status_panel(
    success_count: int, total_count: int, download_folder: str
) -> Panel:
    """
    Create a panel for download status
    """
    if success_count == total_count:
        status_icon = "✅"
        status_text = "All downloads successful"
        style = "green"
    elif success_count > 0:
        status_icon = "⚠️"
        status_text = f"Partial success: {success_count}/{total_count} downloaded"
        style = "yellow"
    else:
        status_icon = "❌"
        status_text = "All downloads failed"
        style = "red"

    content = f"[bold]{status_icon} {status_text}[/bold]\n\n"
    content += f"📂 Download location: [cyan]{download_folder}[/cyan]"

    return Panel(
        content,
        title="[bold]Download Status[/bold]",
        title_align="left",
        box=ROUNDED,
        style=style,
        padding=(1, 2),
    )


def create_error_panel(error_message: str) -> Panel:
    """
    Create an error panel
    """
    return Panel(
        f"[bold red]⚠ Error[/bold red]\n\n{error_message}",
        box=ROUNDED,
        style="red",
        padding=(1, 2),
    )


def create_prompt_guide_panel() -> Panel:
    """
    Create a panel with prompt guidelines
    """
    guidelines = """[bold cyan]Prompt Writing Tips:[/bold cyan]

• [bold]Subject:[/bold] Describe who or what (person, animal, object)
• [bold]Context:[/bold] Add background and setting details  
• [bold]Action:[/bold] Specify what's happening in the scene
• [bold]Style:[/bold] Include visual style (cinematic, cartoon, realistic)
• [bold]Camera:[/bold] Add camera motion (close-up, wide shot, pan)

[dim]Example: "A cinematic close-up of a cat reading a book in a cozy library, 
warm lighting, slow zoom out"[/dim]"""

    return Panel(
        guidelines,
        title="[bold]Video Prompt Guide[/bold]",
        title_align="left",
        box=ROUNDED,
        style="cyan",
        padding=(1, 2),
    )


def create_operation_status_panel(operation_id: str, status: str) -> Panel:
    """
    Create a panel for operation status
    """
    status_icon = (
        "⏳" if status == "in_progress" else "✓" if status == "completed" else "✗"
    )
    status_color = (
        "yellow"
        if status == "in_progress"
        else "green" if status == "completed" else "red"
    )

    content = f"""[bold]Operation ID:[/bold] [cyan]{operation_id}[/cyan]
[bold]Status:[/bold] [{status_color}]{status_icon} {status.replace('_', ' ').title()}[/{status_color}]"""

    return Panel(
        content,
        title="[bold]Operation Status[/bold]",
        title_align="left",
        box=ROUNDED,
        style=status_color,
        padding=(1, 2),
    )


def create_developer_footer():
    """
    Create a persistent footer showing developer credit that appears throughout the app
    """
    footer_text = Text()
    footer_text.append("AI Media Studio CLI ", style="bold bright_cyan")
    footer_text.append("• ", style="bright_white")
    footer_text.append("Created with ❤️  by ", style="bright_yellow")
    footer_text.append("Abdulrahman Elsmmany", style="bold bright_red")

    return Panel(
        Align.center(footer_text),
        box=ROUNDED,
        style="bright_blue",
        padding=(0, 1),
        height=3,
    )


def print_welcome_message():
    """
    Print welcome message with branding
    """
    console.clear()
    console.print(create_header())
    console.print()

    welcome_text = """Welcome to [bold]AI Media Studio CLI[/bold] - Your AI-powered video generation tool!
    
Generate stunning videos with Google's Veo AI models using simple text prompts.
    
[bold cyan]Quick Start:[/bold cyan]
  • Use [bold]labsfx generate[/bold] for quick video generation
  • Use [bold]labsfx interactive[/bold] for guided experience
  • Use [bold]labsfx --help[/bold] to see all commands"""

    console.print(
        Panel(
            welcome_text,
            box=ROUNDED,
            padding=(1, 2),
            style="bright_blue",
        )
    )
