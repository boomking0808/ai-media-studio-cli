"""
Media download functionality for AI Media Studio CLI.
Supports downloading and organizing videos, images, and audio files.
"""

import os
import aiohttp
import asyncio  
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Set
from urllib.parse import urlparse, parse_qs
from rich.console import Console
from rich.progress import Progress, DownloadColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.panel import Panel
from . import ui_components as ui

try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

console = Console()

# Media type mappings based on file extensions
MEDIA_TYPES = {
    'videos': {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp'},
    'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp', '.ico'},
    'audios': {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus'}
}

def get_media_type(file_extension: str) -> str:
    """
    Determine media type based on file extension.
    
    Args:
        file_extension: File extension (including dot, e.g., '.mp4')
    
    Returns:
        Media type ('videos', 'images', 'audios') or 'unknown'
    """
    file_extension = file_extension.lower()
    for media_type, extensions in MEDIA_TYPES.items():
        if file_extension in extensions:
            return media_type
    return 'unknown'

def create_media_folders(base_dir: Path) -> Dict[str, Path]:
    """
    Create organized folder structure for different media types.
    
    Args:
        base_dir: Base directory to create folders in
        
    Returns:
        Dictionary mapping media types to their folder paths
    """
    folders = {}
    for media_type in MEDIA_TYPES.keys():
        folder_path = base_dir / media_type
        folder_path.mkdir(exist_ok=True)
        folders[media_type] = folder_path
    
    # Create unknown folder for unrecognized file types
    unknown_folder = base_dir / 'unknown'
    unknown_folder.mkdir(exist_ok=True)
    folders['unknown'] = unknown_folder
    
    return folders


def delete_gcs_file(gcs_uri: str) -> bool:
    """
    Delete a file from Google Cloud Storage.
    
    Args:
        gcs_uri: GCS URI in format gs://bucket/path/file.ext
        
    Returns:
        True if deletion was successful, False otherwise
    """
    if not GCS_AVAILABLE:
        console.print("[red]Google Cloud Storage client not available[/red]")
        return False
    
    try:
        # Parse GCS URI
        if not gcs_uri.startswith("gs://"):
            return False  # Not a GCS URI
            
        # Extract bucket and blob path
        path_parts = gcs_uri.replace("gs://", "").split("/", 1)
        if len(path_parts) != 2:
            console.print(f"[red]Invalid GCS URI format: {gcs_uri}[/red]")
            return False
            
        bucket_name, blob_path = path_parts
        
        # Initialize GCS client and delete the blob
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        blob.delete()
        console.print(f"[green]🗑️ Deleted from GCS: {blob_path}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Failed to delete {gcs_uri}: {e}[/red]")
        return False


def convert_gcs_uri_to_signed_url(gcs_uri: str, expiration_hours: int = 1) -> Optional[str]:
    """
    Convert a GCS URI to a signed URL for download.
    
    Args:
        gcs_uri: GCS URI in format gs://bucket/path/file.ext
        expiration_hours: Hours until the signed URL expires
        
    Returns:
        Signed URL string or None if conversion fails
    """
    if not GCS_AVAILABLE:
        console.print("[red]Google Cloud Storage client not available. Install with: pip install google-cloud-storage[/red]")
        return None
    
    try:
        # Parse GCS URI
        if not gcs_uri.startswith("gs://"):
            return gcs_uri  # Not a GCS URI, return as-is
            
        # Extract bucket and blob path
        path_parts = gcs_uri.replace("gs://", "").split("/", 1)
        if len(path_parts) != 2:
            console.print(f"[red]Invalid GCS URI format: {gcs_uri}[/red]")
            return None
            
        bucket_name, blob_path = path_parts
        
        # Initialize GCS client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        # Generate signed URL
        from datetime import datetime, timedelta
        expiration = datetime.utcnow() + timedelta(hours=expiration_hours)
        
        signed_url = blob.generate_signed_url(
            expiration=expiration,
            method="GET",
        )
        
        console.print(f"[green]✓ Generated signed URL for: {blob_path}[/green]")
        return signed_url
        
    except Exception as e:
        console.print(f"[red]Failed to generate signed URL for {gcs_uri}: {e}[/red]")
        return None


async def download_media_file(session: aiohttp.ClientSession, url: str, filepath: Path, description: str) -> bool:
    """
    Download a single file from URL to local filesystem.
    
    Args:
        session: aiohttp client session
        url: URL to download from
        filepath: Local path to save file
        description: Description for progress display
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            
            # Get file size if available
            total_size = int(response.headers.get('content-length', 0))
            
            # Create download progress
            with Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(bar_width=50),
                DownloadColumn(),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(description, total=total_size)
                
                # Download in chunks
                with open(filepath, 'wb') as file:
                    async for chunk in response.content.iter_chunked(8192):
                        file.write(chunk)
                        progress.update(task, advance=len(chunk))
                        
        return True
    except Exception as e:
        console.print(f"[red]❌ Failed to download {filepath.name}:[/red] {str(e)}")
        return False


async def download_media_async(media_uris: List[str], output_dir: Optional[str] = None, cleanup_gcs: bool = True, organize_by_type: bool = True) -> List[Tuple[str, Path]]:
    """
    Download multiple media files concurrently with automatic organization.
    
    Args:
        media_uris: List of media URIs (GCS or signed URLs)
        output_dir: Optional output directory name (created in project root)
        cleanup_gcs: Whether to delete GCS files after successful download (default: True)
        organize_by_type: Whether to organize files into videos/images/audios folders (default: True)
        
    Returns:
        List of tuples (original_uri, local_path) for successful downloads
    """
    # Create output directory
    if output_dir:
        download_dir = Path(output_dir)
    else:
        download_dir = Path("downloaded_media")
    
    download_dir.mkdir(exist_ok=True)
    
    # Create organized folder structure if requested
    if organize_by_type:
        media_folders = create_media_folders(download_dir)
        console.print(Panel(
            f"[bold cyan]📁 Downloading media to organized folders in:[/bold cyan] {download_dir.absolute()}\n"
            f"[dim]• videos/ - Video files (.mp4, .avi, .mov, etc.)\n"
            f"• images/ - Image files (.jpg, .png, .gif, etc.)\n"
            f"• audios/ - Audio files (.mp3, .wav, .flac, etc.)[/dim]",
            style="cyan"
        ))
    else:
        console.print(Panel(
            f"[bold cyan]📁 Downloading media to:[/bold cyan] {download_dir.absolute()}",
            style="cyan"
        ))
    
    # Prepare download tasks
    download_tasks = []
    file_mapping = []
    
    async with aiohttp.ClientSession() as session:
        for i, uri in enumerate(media_uris, 1):
            # Extract filename from URI or create one
            if uri.startswith("gs://"):
                # Extract path from GCS URI
                path_parts = uri.replace("gs://", "").split("/", 1)
                if len(path_parts) > 1:
                    filename = Path(path_parts[1]).name
                else:
                    filename = f"media_{i}"
            else:
                # Try to extract filename from URL
                parsed = urlparse(uri)
                filename = Path(parsed.path).name
                if not filename:
                    filename = f"media_{i}"
            
            # Determine media type and target folder
            file_extension = Path(filename).suffix.lower()
            if organize_by_type:
                media_type = get_media_type(file_extension)
                target_folder = media_folders.get(media_type, media_folders['unknown'])
                filepath = target_folder / filename
            else:
                filepath = download_dir / filename
            
            description = f"Media {i}/{len(media_uris)}: {filename}"
            
            # Convert GCS URIs to signed URLs for download
            download_url = uri
            if uri.startswith("gs://"):
                console.print(f"[cyan]🔗 Converting GCS URI to signed URL...[/cyan]")
                signed_url = convert_gcs_uri_to_signed_url(uri)
                if signed_url:
                    download_url = signed_url
                else:
                    console.print(f"[red]❌ Failed to convert GCS URI: {uri}[/red]")
                    continue
            
            task = download_media_file(session, download_url, filepath, description)
            download_tasks.append(task)
            file_mapping.append((uri, filepath))
        
        # Download all files concurrently
        results = await asyncio.gather(*download_tasks)
    
    # Filter successful downloads
    successful_downloads = [
        mapping for mapping, success in zip(file_mapping, results) if success
    ]
    
    # Clean up GCS files after successful downloads
    if cleanup_gcs and successful_downloads:
        console.print(f"\n[cyan]🧹 Cleaning up GCS files...[/cyan]")
        cleanup_count = 0
        for original_uri, _ in successful_downloads:
            if original_uri.startswith("gs://"):
                if delete_gcs_file(original_uri):
                    cleanup_count += 1
        
        if cleanup_count > 0:
            console.print(f"[green]✓ Cleaned up {cleanup_count} GCS file(s)[/green]")
    
    return successful_downloads


def download_media(media_uris: List[str], output_dir: Optional[str] = None, cleanup_gcs: bool = True, organize_by_type: bool = True) -> List[Tuple[str, Path]]:
    """
    Synchronous wrapper for downloading media files with automatic organization.
    
    Args:
        media_uris: List of media URIs (GCS or signed URLs)
        output_dir: Optional output directory name (created in project root)
        cleanup_gcs: Whether to delete GCS files after successful download (default: True)
        organize_by_type: Whether to organize files into videos/images/audios folders (default: True)
        
    Returns:
        List of tuples (original_uri, local_path) for successful downloads
    """
    return asyncio.run(download_media_async(media_uris, output_dir, cleanup_gcs, organize_by_type))

# Legacy function for backward compatibility
def download_videos(video_uris: List[str], output_dir: Optional[str] = None, cleanup_gcs: bool = True) -> List[Tuple[str, Path]]:
    """
    Legacy function for downloading videos only. Use download_media() for new code.
    
    Args:
        video_uris: List of video URIs (GCS or signed URLs)
        output_dir: Optional output directory name (created in project root)
        cleanup_gcs: Whether to delete GCS files after successful download (default: True)
        
    Returns:
        List of tuples (original_uri, local_path) for successful downloads
    """
    return download_media(video_uris, output_dir, cleanup_gcs, organize_by_type=False)


def print_download_summary(downloads: List[Tuple[str, Path]], total_media: int, download_folder: str = "downloaded_media", organized: bool = True):
    """
    Print a summary of downloaded media files using UI components.
    
    Args:
        downloads: List of successful downloads (uri, local_path)
        total_media: Total number of media files attempted
        download_folder: Name of the download folder
        organized: Whether files were organized by type
    """
    success_count = len(downloads)
    
    # Show download status panel
    console.print(ui.create_download_status_panel(success_count, total_media, download_folder))
    
    # Show individual file details if any were downloaded
    if downloads:
        if organized:
            # Group by media type for organized display
            by_type = {'videos': [], 'images': [], 'audios': [], 'unknown': []}
            for _, local_path in downloads:
                parent_name = local_path.parent.name
                if parent_name in by_type:
                    by_type[parent_name].append(local_path.name)
                else:
                    by_type['unknown'].append(local_path.name)
            
            console.print(f"\n[bold green]Downloaded files by type:[/bold green]")
            for media_type, files in by_type.items():
                if files:
                    console.print(f"  [bold cyan]{media_type.title()}:[/bold cyan]")
                    for filename in files:
                        console.print(f"    • {filename}")
        else:
            console.print(f"\n[bold green]Downloaded files:[/bold green]")
            for _, local_path in downloads:
                console.print(f"   • {local_path.name}")
        
        console.print("[dim]Files are ready to use![/dim]")

# Legacy function for backward compatibility
def print_video_download_summary(downloads: List[Tuple[str, Path]], total_videos: int, download_folder: str = "downloaded_videos"):
    """Legacy function for video download summaries. Use print_download_summary() for new code."""
    return print_download_summary(downloads, total_videos, download_folder, organized=False)