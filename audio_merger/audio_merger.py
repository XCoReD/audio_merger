#!/usr/bin/env python3
import argparse
import os
import glob
from typing import List, Tuple, Optional
from pydub import AudioSegment, effects
from mutagen.easyid3 import EasyID3
from mutagen.oggvorbis import OggVorbis
from mutagen.id3 import ID3, TIT2, TALB
from unidecode import unidecode

extensions = ['mp3', 'wav', 'ogg']

def validate_files(files: List[str], working_folder: str) -> None:
    """Validate input audio files existence and format."""
    if not files:

        for ext in extensions:
            search_pattern = os.path.join(working_folder, f'*.{ext}')
            # Use glob to find files matching the pattern
            files_found = glob.glob(search_pattern)
            files.extend(files_found)
        
        if not files:
            raise ValueError("No input files provided, and no audio files are found in the working folder")
    
    for file in files:
        file_path = os.path.join(working_folder, file) if not os.path.isabs(file) else file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file.lower().endswith(tuple(extensions)):
            raise ValueError(f"File {file} is not a supported input audio file")

def get_file_path(filename: str, working_folder: str = None) -> str:
    """Construct full file path based on working folder."""
    return os.path.join(working_folder, filename) if working_folder else filename

def load_audio_file(file_path: str) -> Tuple[AudioSegment, Optional[str], Optional[str]]:
    """
    Load an audio file and extract its metadata.
    Returns: (AudioSegment, title, album)
    """
    title = None
    album = None
    audio = None
    
    if file_path.lower().endswith('.wav'):
        audio = AudioSegment.from_wav(file_path)
    elif file_path.lower().endswith('.mp3'):
        audio = AudioSegment.from_mp3(file_path)
        try:
            tags = EasyID3(file_path)
            title = tags.get("title", [None])[0]
            album = tags.get("album", [None])[0]
        except Exception:
            pass
    elif file_path.lower().endswith('.ogg'):
        audio = AudioSegment.from_ogg(file_path)
        try:
            tags = OggVorbis(file_path)
            title = tags.get("TITLE", [None])[0]
            album = tags.get("ALBUM", [None])[0]
        except Exception:
            pass
            
    return audio, title, album

def normalize_audio(audio: AudioSegment) -> AudioSegment:
    """Normalize audio to consistent format (stereo, 44.1 KHz)."""
    if audio.channels < 2:
        audio = audio.set_channels(2)
    audio.set_frame_rate(44100)
    return effects.normalize(audio)

def get_output_path(output_file: str, title: str = None) -> str:
    """Construct proper output file path with extension."""
    if not output_file.lower().endswith('.mp3'):
        if title:
            output_file += f" - {unidecode(title)}"
        output_file += ".mp3"
    return output_file

def save_metadata(output_path: str, title: Optional[str], album: Optional[str]) -> None:
    """Save metadata to the output MP3 file."""
    if not (title or album):
        return
        
    try:
        tags = EasyID3(output_path)
        tags.clear()
        if title:
            tags["title"] = title
        if album:
            tags["album"] = album
        tags.save(v2_version=3)
        print(f"Track title: {title}, album: {album}")
    except Exception as e:
        print(f"Warning: Could not save metadata: {str(e)}")

def merge_audio_files(input_files: List[str], output_file: str, working_folder: str = None) -> None:
    """
    Merge multiple audio files into a single MP3 file.
    Output format: Stereo, 44.1 KHz, CBR MP3 128 kbps
    """
    if not working_folder:
        working_folder = os.getcwd()


    try:
        # Create working folder if needed
        if working_folder and not os.path.exists(working_folder):
            os.makedirs(working_folder)
        
        # Validate input files
        validate_files(input_files, working_folder)

        # Load first file
        first_file = get_file_path(input_files[0], working_folder)
        merged_audio, title, album = load_audio_file(first_file)
        merged_audio = normalize_audio(merged_audio)
        
        # Merge remaining files
        for file in input_files[1:]:
            file_path = get_file_path(file, working_folder)
            audio, file_title, file_album = load_audio_file(file_path)
            
            # Use metadata from subsequent files if not found in first file
            if not title and file_title:
                title = file_title
            if not album and file_album:
                album = file_album
                
            audio = normalize_audio(audio)
            merged_audio += audio
        
        # Prepare output path and export
        output_path = get_file_path(get_output_path(output_file, title), working_folder)
        merged_audio.export(
            output_path,
            format="mp3",
            bitrate="128k"
        )
        
        # Save metadata
        save_metadata(output_path, title, album)
        
        print(f"Successfully merged {len(input_files)} files into: {output_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(
        description="Merge multiple source audio files into a single output MP3 file"
    )
    parser.add_argument("-o", type=str, default="output.mp3", help="Output MP3 file (default: output.mp3).")
    parser.add_argument("-w", type=str, default=None, help="Working folder for input and output files (optional).")
    parser.add_argument("input_files", nargs='?', default=[], help="List of input files.")
    
    args = parser.parse_args()    
    try:
        merge_audio_files(args.input_files, args.o or "output.mp3", args.w)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()