"""
Animation utilities for AI Media Studio CLI
"""

import time
import itertools
from typing import List, Optional
from rich.console import Console
from rich.text import Text
from rich.live import Live
from rich.panel import Panel
from rich.align import Align


console = Console()


class VideoGenerationAnimation:
    """
    Animated display for video generation process
    """

    def __init__(self):
        self.frames = [
            "🎬 Analyzing prompt...",
            "🎨 Creating visual concepts...",
            "🎥 Rendering frames...",
            "✨ Applying AI magic...",
            "🎞️ Finalizing video...",
        ]
        self.spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def create_frame(self, step: int, spinner_frame: str) -> Panel:
        """
        Create an animation frame
        """
        current_step = step % len(self.frames)

        # Create progress dots
        dots = ""
        for i in range(len(self.frames)):
            if i < current_step:
                dots += "●"
            elif i == current_step:
                dots += "◉"
            else:
                dots += "○"
            if i < len(self.frames) - 1:
                dots += " "

        content = f"{spinner_frame} {self.frames[current_step]}\n\n[bold blue]{dots}[/bold blue]"

        return Panel(
            Align.center(content),
            title="[bold]Generating Video[/bold]",
            style="bright_blue",
            padding=(1, 2),
        )


def animated_text_reveal(text: str, delay: float = 0.02):
    """
    Reveal text character by character
    """
    revealed = ""
    with Live(console=console, refresh_per_second=30) as live:
        for char in text:
            revealed += char
            live.update(Text(revealed, style="bold cyan"))
            time.sleep(delay)


def loading_animation(message: str = "Loading", duration: float = 3.0):
    """
    Show a loading animation for a specified duration
    """
    spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    start_time = time.time()

    with Live(console=console, refresh_per_second=10) as live:
        while time.time() - start_time < duration:
            frame = next(spinner)
            live.update(Text(f"{frame} {message}...", style="bold blue"))
            time.sleep(0.1)


def success_animation():
    """
    Show a success animation
    """
    frames = [
        "✓",
        "[bold green]✓[/bold green]",
        "[bold green]✓ Success![/bold green]",
    ]

    with Live(console=console, refresh_per_second=10) as live:
        for frame in frames:
            live.update(Align.center(frame))
            time.sleep(0.3)


def typewriter_effect(text: str, style: str = "white", delay: float = 0.03):
    """
    Create a typewriter effect for text
    """
    console.print("", end="")
    for char in text:
        console.print(char, style=style, end="")
        time.sleep(delay)
    console.print()


class ProgressIndicator:
    """
    Custom progress indicator with percentage and ETA
    """

    def __init__(self, total_steps: int = 100):
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()

    def create_bar(self, width: int = 30) -> str:
        """
        Create a progress bar
        """
        filled = int((self.current_step / self.total_steps) * width)
        bar = "█" * filled + "░" * (width - filled)
        percentage = (self.current_step / self.total_steps) * 100

        # Calculate ETA
        elapsed = time.time() - self.start_time
        if self.current_step > 0:
            eta = (elapsed / self.current_step) * (self.total_steps - self.current_step)
            eta_str = f"{int(eta)}s"
        else:
            eta_str = "calculating..."

        return f"[bold blue]{bar}[/bold blue] {percentage:.0f}% | ETA: {eta_str}"

    def update(self, step: int):
        """
        Update progress
        """
        self.current_step = min(step, self.total_steps)
