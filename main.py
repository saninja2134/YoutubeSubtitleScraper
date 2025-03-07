import os
import subprocess
import glob
import re
import uuid
from datetime import datetime

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the program header."""
    clear_screen()
    print("=" * 80)
    print("               YOUTUBE SUBTITLE DOWNLOADER - INTERACTIVE MODE")
    print("=" * 80)
    print()

def check_dependencies():
    """Check if yt-dlp and ffmpeg are installed and install if needed."""
    yt_dlp_installed = True
    ffmpeg_installed = True
    
    # Check yt-dlp
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        yt_dlp_installed = False
        print("yt-dlp is not installed or not found in PATH.")
        choice = input("Would you like to install it now? (y/n): ").lower()
        if choice == 'y':
            try:
                subprocess.run(["pip", "install", "yt-dlp"], check=True)
                print("yt-dlp installed successfully!")
                yt_dlp_installed = True
            except subprocess.CalledProcessError:
                print("Failed to install yt-dlp. Please install it manually with: pip install yt-dlp")
        else:
            print("yt-dlp is required for this program to work.")
    
    # Check ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        ffmpeg_installed = False
        print("\nFFmpeg is not installed or not found in PATH.")
        print("FFmpeg is required for subtitle conversion.")
        print("\nInstallation instructions:")
        if os.name == 'nt':  # Windows
            print("1. Download FFmpeg from https://ffmpeg.org/download.html")
            print("2. Extract the downloaded zip file")
            print("3. Add the bin folder to your system PATH")
            print("   OR place ffmpeg.exe in the same directory as this script")
        else:  # Linux/Mac
            print("1. Install using your package manager:")
            print("   - Ubuntu/Debian: sudo apt install ffmpeg")
            print("   - Fedora: sudo dnf install ffmpeg")
            print("   - macOS: brew install ffmpeg")
        
        choice = input("\nDo you want to continue without ffmpeg? Subtitles might not convert properly. (y/n): ").lower()
        if choice != 'y':
            return False
    
    return yt_dlp_installed

def clean_filename(filename):
    """
    Clean filename to remove invalid characters and ensure it's valid for both
    Windows and Unix file systems.
    """
    if not filename or filename.isspace():
        return "Unknown"
        
    # Replace invalid characters with underscores
    cleaned = re.sub(r'[\\/*?:"<>|]', "_", filename)
    # Replace multiple spaces with a single space
    cleaned = re.sub(r'\s+', " ", cleaned)
    # Trim to avoid excessively long filenames
    if len(cleaned) > 50:
        cleaned = cleaned[:50]
    # Final trim of whitespace
    cleaned = cleaned.strip()
    
    # Ensure we have a valid name
    if not cleaned or cleaned.isspace():
        return "Unknown"
    
    return cleaned

def parse_srt_to_text(file_path):
    """Parse an SRT file and extract just the text without timestamps."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            content = file.read()
            
        # Remove SRT timestamps and numbers
        lines = content.split('\n')
        parsed_text = []
        
        i = 0
        while i < len(lines):
            # Skip blank lines
            if not lines[i].strip():
                i += 1
                continue
                
            # Try to identify SRT index numbers
            if lines[i].strip().isdigit():
                i += 1  # Skip the number line
                
                # Skip timestamp line if it exists (contains --> pattern)
                if i < len(lines) and '-->' in lines[i]:
                    i += 1
                    
                # Collect subtitle text until we hit a blank line or another number
                text_lines = []
                while i < len(lines) and lines[i].strip() and not lines[i].strip().isdigit():
                    text_lines.append(lines[i].strip())
                    i += 1
                    
                if text_lines:
                    parsed_text.append(' '.join(text_lines))
            else:
                # If the format is irregular, just add the line
                if lines[i].strip() and '-->' not in lines[i]:
                    parsed_text.append(lines[i].strip())
                i += 1
                
        return '\n'.join(parsed_text)
    except Exception as e:
        return f"[Error parsing file: {str(e)}]"

def merge_subtitles(output_dir, final_output_file):
    """
    Merge all subtitle files in the output directory into a single text file.
    
    Args:
        output_dir (str): Directory containing subtitle files
        final_output_file (str): Path for the merged output file
    
    Returns:
        int: Number of subtitle files merged
    """
    print(f"\nMerging subtitle files into a single document...")
    print(f"Output file will be: {os.path.abspath(final_output_file)}")
    
    # Find all subtitle files recursively
    subtitle_files = []
    print("Scanning for subtitle files...")
    for ext in ['.srt', '.vtt', '.ass', '.lrc', '.ttml', '.sbv', '.json']:
        found = glob.glob(f"{output_dir}/**/*{ext}", recursive=True)
        if found:
            print(f"  Found {len(found)} {ext} files")
            subtitle_files.extend(found)
    
    total_files = len(subtitle_files)
    print(f"\nFound {total_files} total subtitle files to process")
    
    if not subtitle_files:
        print("No subtitle files found!")
        return 0
        
    print("\nProcessing and merging files:")
    print(f"[{'░' * 30}] 0%")
    
    count = 0
    with open(final_output_file, 'w', encoding='utf-8') as output:
        for i, srt_file in enumerate(subtitle_files):
            try:
                # Get video title from filename
                filename = os.path.basename(srt_file)
                video_title = os.path.splitext(filename)[0]
                
                # Add divider and video title
                output.write(f"\n\n{'=' * 80}\n")
                output.write(f"VIDEO: {video_title}\n")
                output.write(f"FILE: {srt_file}\n")
                output.write(f"{'=' * 80}\n\n")
                
                # Extract text from subtitle file
                subtitle_text = parse_srt_to_text(srt_file)
                output.write(subtitle_text)
                
                count += 1
                
                # Update progress bar
                progress = int((i + 1) / total_files * 30)
                percent = int((i + 1) / total_files * 100)
                progress_bar = f"[{'█' * progress}{'░' * (30-progress)}] {percent}%"
                
                # Clear line and update progress
                print(f"\r{progress_bar} - Processed {i+1}/{total_files} files", end='')
                
            except Exception as e:
                print(f"\nError processing {srt_file}: {str(e)}")
    
    print(f"\n\nSuccessfully merged {count} subtitle files into single document:")
    print(f"  {os.path.abspath(final_output_file)}")
    return count

def download_subtitles(url, is_channel=False, language="en", output_dir=None, format="srt", include_auto=True, merge_to_single_file=True, skip_conversion=False):
    """
    Download subtitles from YouTube video or channel.
    
    Args:
        url (str): URL of the YouTube video or channel
        is_channel (bool): Whether the URL is for a channel
        language (str): Language code for subtitles
        output_dir (str): Directory to save subtitles
        format (str): Subtitle format
        include_auto (bool): Whether to include auto-generated subtitles
        merge_to_single_file (bool): Whether to merge all subtitles into a single file
        skip_conversion (bool): Whether to skip subtitle format conversion (if ffmpeg isn't available)
    """
    # Create timestamp for the run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Use a safe naming approach for directories
    if is_channel:
        print(f"\nPreparing to download channel subtitles...")
        # Extract channel name from URL or use a safe default
        channel_id = url.split("/")[-1] if "/" in url else "channel"
        channel_id = channel_id.replace("@", "")
        base_dir_name = f"channel_{channel_id}"
    else:
        print(f"\nPreparing to download video subtitles...")
        base_dir_name = "video"
    
    # Set up safe output directory
    if output_dir is None:
        # Create a guaranteed unique directory using timestamp and UUID
        dir_uuid = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID for uniqueness
        output_dir = f"subtitles_{base_dir_name}_{timestamp}_{dir_uuid}"
    
    # Create output directory if it doesn't exist
    try:
        print(f"\nCreating output directory: {os.path.abspath(output_dir)}")
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        print(f"Error creating directory: {str(e)}")
        # Try a more basic name if there's an error
        output_dir = f"subtitles_{timestamp}"
        print(f"Trying alternate directory: {os.path.abspath(output_dir)}")
        os.makedirs(output_dir, exist_ok=True)
    
    # Prepare final merged file path with safe naming
    final_output_file = os.path.join(output_dir, f"all_subtitles_{timestamp}.txt")
    
    print(f"\n{'=' * 60}")
    print(f"DOWNLOAD INFORMATION")
    print(f"{'=' * 60}")
    print(f"Source: {url}")
    print(f"Type: {'Channel' if is_channel else 'Single Video'}")
    print(f"Language: {language}")
    print(f"Format: {format}")
    print(f"Include auto-generated subtitles: {'Yes' if include_auto else 'No'}")
    print(f"Output location: {os.path.abspath(output_dir)}")
    if merge_to_single_file and is_channel:
        print(f"Merged output file: {os.path.basename(final_output_file)}")
    print(f"{'=' * 60}")
    print("\nStarting download process...")
    print("This may take a while depending on the number of videos...\n")
    
    # Build command
    command = ["yt-dlp", "--write-sub"]
    
    if include_auto:
        command.append("--write-auto-sub")
        
    command.extend([
        f"--sub-lang={language}",
        "--skip-download"
    ])
    
    # Only add format conversion if we're not skipping it
    if not skip_conversion:
        command.extend([f"--convert-subs={format}"])
    else:
        print("Skipping subtitle format conversion (ffmpeg not available)")
        print("Subtitles will be downloaded in their original format (.vtt)")
        # Add warning about subtitle merging
        if merge_to_single_file:
            print("Note: Merging may not work properly with all subtitle formats")
    
    # Set output pattern
    if is_channel:
        # Use a simpler output template that won't cause issues
        command.extend(["-o", f"{output_dir}/%(id)s.%(ext)s"])
    else:
        command.extend(["-o", f"{output_dir}/%(id)s.%(ext)s"])
    
    # Add URL
    command.append(url)
    
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        
        # Print output in real-time
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        if process.returncode == 0:
            print(f"\n{'=' * 60}")
            print(f"DOWNLOAD COMPLETED SUCCESSFULLY")
            print(f"{'=' * 60}")
            
            # Count downloaded subtitle files
            subtitle_count = 0
            for ext in ['.srt', '.vtt', '.ass', '.lrc']:
                files = glob.glob(f"{output_dir}/**/*{ext}", recursive=True)
                subtitle_count += len(files)
            
            print(f"Downloaded subtitles for {subtitle_count} videos/files")
            print(f"Files saved to: {os.path.abspath(output_dir)}")
            
            # Merge subtitles if requested (for channels)
            if merge_to_single_file and subtitle_count > 0:
                merged_count = merge_subtitles(output_dir, final_output_file)
                if merged_count > 0:
                    print(f"\nSUMMARY:")
                    print(f"- Downloaded {subtitle_count} subtitle files")
                    print(f"- Merged {merged_count} videos into one document")
                    print(f"- Individual subtitle files location: {os.path.abspath(output_dir)}")
                    print(f"- Merged file location: {os.path.abspath(final_output_file)}")
            else:
                print(f"\nSUMMARY:")
                print(f"- Downloaded {subtitle_count} subtitle files")
                print(f"- Files location: {os.path.abspath(output_dir)}")
            
            print(f"{'=' * 60}")
            input("\nPress Enter to continue...")
            return True
        else:
            print(f"\nError: yt-dlp exited with code {process.returncode}")
            input("\nPress Enter to continue...")
            return False
    
    except Exception as e:
        print(f"Error: {str(e)}")
        input("\nPress Enter to continue...")
        return False

def get_language_choice():
    """Interactive menu for selecting subtitle language."""
    languages = {
        "1": ("en", "English"),
        "2": ("es", "Spanish"),
        "3": ("fr", "French"),
        "4": ("de", "German"),
        "5": ("it", "Italian"),
        "6": ("pt", "Portuguese"),
        "7": ("ru", "Russian"),
        "8": ("ja", "Japanese"),
        "9": ("ko", "Korean"),
        "10": ("zh-CN", "Chinese (Simplified)"),
        "11": ("all", "All available languages")
    }
    
    print_header()
    print("Select subtitle language:")
    print()
    
    for key, (code, name) in languages.items():
        print(f"{key}. {name} ({code})")
    
    print()
    print("0. Custom language code")
    
    while True:
        choice = input("\nEnter your choice (1-11, or 0 for custom): ")
        
        if choice == "0":
            custom_code = input("Enter custom language code (e.g., 'nl' for Dutch): ")
            return custom_code
        elif choice in languages:
            return languages[choice][0]
        else:
            print("Invalid choice. Please try again.")

def get_format_choice():
    """Interactive menu for selecting subtitle format."""
    formats = {
        "1": ("srt", "SubRip"),
        "2": ("vtt", "WebVTT"),
        "3": ("ass", "Advanced SubStation Alpha"),
        "4": ("lrc", "Lyric Text")
    }
    
    print_header()
    print("Select subtitle format:")
    print()
    
    for key, (code, name) in formats.items():
        print(f"{key}. {name} ({code})")
    
    while True:
        choice = input("\nEnter your choice (1-4): ")
        
        if choice in formats:
            return formats[choice][0]
        else:
            print("Invalid choice. Please try again.")

def get_auto_subtitle_choice():
    """Ask whether to include auto-generated subtitles."""
    print_header()
    print("Include auto-generated subtitles?")
    print()
    print("1. Yes (recommended)")
    print("2. No (manual subtitles only)")
    
    while True:
        choice = input("\nEnter your choice (1-2): ")
        
        if choice == "1":
            return True
        elif choice == "2":
            return False
        else:
            print("Invalid choice. Please try again.")

def get_merge_choice():
    """Ask whether to merge subtitles into a single file."""
    print_header()
    print("Merge all subtitles into a single text file?")
    print()
    print("1. Yes - Create one combined text file with all subtitles")
    print("2. No - Keep individual subtitle files only")
    
    while True:
        choice = input("\nEnter your choice (1-2): ")
        
        if choice == "1":
            return True
        elif choice == "2":
            return False
        else:
            print("Invalid choice. Please try again.")

def get_url_and_type():
    """Get URL and determine if it's a channel or video."""
    print_header()
    print("Enter the YouTube URL:")
    url = input("\n> ").strip()
    
    print("\nIs this a channel or a video?")
    print("1. Channel (download subtitles from all videos)")
    print("2. Single video")
    
    while True:
        choice = input("\nEnter your choice (1-2): ")
        
        if choice == "1":
            return url, True
        elif choice == "2":
            return url, False
        else:
            print("Invalid choice. Please try again.")

def get_output_directory():
    """Ask if user wants to specify an output directory."""
    print_header()
    print("Where would you like to save the subtitles?")
    print()
    print("1. Use default directory (automatic naming)")
    print("2. Specify a custom directory")
    
    while True:
        choice = input("\nEnter your choice (1-2): ")
        
        if choice == "1":
            return None
        elif choice == "2":
            custom_dir = input("Enter custom directory path: ").strip()
            return custom_dir
        else:
            print("Invalid choice. Please try again.")

def show_main_menu():
    """Show the main menu and handle user choices."""
    while True:
        print_header()
        print("MAIN MENU:")
        print()
        print("1. Download YouTube Subtitles")
        print("2. About This Tool")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            # Check for required dependencies
            if not check_dependencies():
                input("\nPress Enter to continue...")
                continue
                
            # Check if ffmpeg is available for subtitle conversion
            ffmpeg_available = True
            try:
                subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                ffmpeg_available = False
                
            url, is_channel = get_url_and_type()
            language = get_language_choice()
            format = get_format_choice()
            include_auto = get_auto_subtitle_choice()
            
            # Only ask about merging for channels
            merge_to_single_file = True
            if is_channel:
                merge_to_single_file = get_merge_choice()
                
            output_dir = get_output_directory()
            
            # Confirmation screen
            print_header()
            print("DOWNLOAD CONFIRMATION:")
            print()
            print(f"URL: {url}")
            print(f"Type: {'Channel' if is_channel else 'Single Video'}")
            print(f"Language: {language}")
            print(f"Format: {format}")
            print(f"Include auto-generated subtitles: {'Yes' if include_auto else 'No'}")
            if is_channel:
                print(f"Merge into single file: {'Yes' if merge_to_single_file else 'No'}")
            print(f"Output directory: {'Default (auto-named)' if output_dir is None else output_dir}")
            print()
            
            confirm = input("Start download? (y/n): ").lower()
            if confirm == "y":
                # Pass skip_conversion=True if ffmpeg is not available
                download_subtitles(url, is_channel, language, output_dir, format, 
                                include_auto, merge_to_single_file, 
                                skip_conversion=not ffmpeg_available)
        
        elif choice == "2":
            print_header()
            print("ABOUT THIS TOOL:")
            print()
            print("This interactive tool helps you download subtitles from YouTube videos or")
            print("entire channels. It uses yt-dlp, a powerful fork of youtube-dl with")
            print("additional features and frequent updates.")
            print()
            print("Features:")
            print("- Download subtitles from single videos or entire channels")
            print("- Support for multiple languages and subtitle formats")
            print("- Option to include auto-generated subtitles")
            print("- Merge all channel subtitles into a single searchable text file")
            print("- Customizable output directory")
            print()
            input("Press Enter to return to the main menu...")
        
        elif choice == "3":
            print("\nThank you for using YouTube Subtitle Downloader!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        show_main_menu()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Exiting...")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        input("\nPress Enter to exit...")