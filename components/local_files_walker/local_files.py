import os
import hashlib
from tika import parser
import pytesseract
from pdf2image import convert_from_path
from datetime import datetime
from typing import Optional
from pathlib import Path
from tqdm import tqdm

from config.config_logger import logger
from config.settings import (
    INCLUDED_EXTENSIONS,
    HASH_BASE_SIZE, MIN_FILE_SIZE, LOCAL_FILES_PATH,
    PARSED_FILES_PATH,
)
from database.node import FileNode

class FileParser:
    """A file processing system that parses local files with caching capabilities.
    
    This parser walks through a directory structure, processes compatible files,
    and maintains a cache of processed content to avoid redundant parsing.
    
    Caching Strategy:
        - Files are identified by a hash of their size, modification time, and partial content
        - Based on first and last 1024 bytes of the file -> therefore changes in the middle of the text may be missed!
        - Cached results are stored as .txt files in parsed_files_path
        - Cache files are named as {file_hash}.txt
        - Cache is automatically cleaned of orphaned entries during processing
    
    File Processing:
        - Only processes files with extensions defined in INCLUDED_EXTENSIONS
        - Ignores files smaller than min_file_size (default: 250 bytes)
        - Uses Apache Tika for primary parsing
        - Falls back to OCR (using Tesseract) for failed parse attempts
        
    Attributes:
        local_files_path (str): Root directory to scan for files
        parsed_files_path (str): Directory where cached parsed content is stored
        processed_files (set): Tracks files processed in current run
        min_file_size (int): Minimum file size in bytes to process (default: 250)
        include_extensions (set): File extensions that will be processed

    Returns (run-function) nodes with following attributes filled out:
        node = Node(
            content=content,
            file_creation_date=creation_time,
            modification_date=modification_time,
            filetype=file_type,
            location="Local Files",
            path=os.path.abspath(file_path),
            file_size=file_size  
        )
    """
    
    def __init__(
        self,
        local_files_path: str,
        parsed_files_path: str,
    ):
        """Initialize the FileParser.
        
        Args:
            local_files_path: Directory path containing files to process
            parsed_files_path: Directory path for storing cached parsed content
        limits: Optional resource limits configuration
        """
        self.local_files_path = Path(local_files_path)
        self.parsed_files_path = Path(parsed_files_path)
        self.logger = logger
        self.processed_files = set()
        self.include_extensions = INCLUDED_EXTENSIONS

    def hash_file(self, file_path: Path) -> str:
        """Create a hash of the file based on its content and metadata."""
        file_stat = os.stat(file_path)
        file_size = file_stat.st_size
        mod_time = file_stat.st_mtime # modification time invariant to changing file content
            
        # Read the entire content for small files, or first and last 1024 bytes for larger files
        with open(file_path, 'rb') as f:
            if file_size <= 2*HASH_BASE_SIZE:  # If file is 2KB or smaller, read entire file
                file_content = f.read()
            else:
                first_bytes = f.read(HASH_BASE_SIZE)
                f.seek(-HASH_BASE_SIZE, 2)  # Seek to 1024 bytes from the end
                last_bytes = f.read()
                file_content = first_bytes + last_bytes
        
        hash_input = f"{file_size}_{mod_time}_{file_content}"
        
        return hashlib.md5(hash_input.encode()).hexdigest()

    def get_cached_content(self, file_hash):
        """Retrieve cached content if it exists."""
        cached_file_path = self.parsed_files_path / f"{file_hash}.txt"
        if os.path.exists(cached_file_path):
            with open(cached_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def save_cached_content(self, file_hash, content):
        """Save parsed content to cache."""
        os.makedirs(self.parsed_files_path, exist_ok=True)
        cached_file_path = self.parsed_files_path / f"{file_hash}.txt"
        with open(cached_file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def fallback_parse_file(self, file_path):
        """Fallback function to parse a file using OCR if the parser fails."""
        try:
            # Convert PDF to images to use OCR
            images = convert_from_path(file_path)
            text = ""
            for image in images:
                # OCR
                text += pytesseract.image_to_string(image)
            return text
        except Exception as e:
            self.logger.error(f"Error in both parsing and fallback parsing for {file_path}: {e}\nReturning empty string.")
            return ""

    def parse_with_tika(self, file_path: Path) -> Optional[str]:
        """Wrapper for Tika parsing"""
        try:
            # note, parser.from_file() has to be called with a string, not a Path object
            parsed_file = parser.from_file(str(file_path), requestOptions={'timeout': 180})
            return parsed_file.get("content")
        except Exception as e:
            self.logger.debug(f"Failed parsing {file_path} with Tika. Error: {e}")
            return None

    def parse_file(self, file_path) -> tuple[str, str]:
        """Parses a file using Tika, with a fallback to OCR if Tika fails."""
        file_hash = self.hash_file(file_path)
        cached_content = self.get_cached_content(file_hash)
        
        if cached_content:
            return file_hash, cached_content

        try:
            content = self.parse_with_tika(file_path)
            
            if not content:
                content = self.fallback_parse_file(file_path)
            
            content = content or ""
            self.save_cached_content(file_hash, content)
            return file_hash, content
    
        except Exception as e:
            self.logger.error(f"Failed parsing {file_path}: {e}")
            content = self.fallback_parse_file(file_path)
            content = content or ""
            self.save_cached_content(file_hash, content)
            return file_hash, content

    def should_process_file(self, file_path: Path) -> bool:
        """Check if the file should be processed based on its extension."""
        extension = file_path.suffix.lower()
        if extension not in self.include_extensions:
            return False
        file_stat = os.stat(file_path)
        if file_stat.st_size < MIN_FILE_SIZE:
            return False
        return True

    def file_to_node(self, file_path: Path) -> FileNode | None:
        """Convert a file to a Node object with relevant fields filled out."""
        try:
            file_stats = os.stat(file_path)
            
            creation_time = datetime.fromtimestamp(file_stats.st_mtime)
            modification_time = datetime.fromtimestamp(file_stats.st_mtime)
            _, file_extension = os.path.splitext(file_path)
            file_type = file_extension.lstrip('.').lower()
            file_size = round(file_stats.st_size / 1024)  # Convert to KB and round
            
            hash, content = self.parse_file(file_path)
            
            node = FileNode(
                primary_id=hash,
                content=content,
                file_size=file_size,  
                file_creation_time=creation_time,
                file_modification_time=modification_time,
                filetype=file_type,
                location="Local Files",
                path=os.path.abspath(file_path),
            )
            self.logger.debug(f"Processed file and created Node: {file_path}")
            
            return node
        except Exception as e:
            self.logger.exception(f"Error processing file {file_path}: {str(e)}")
            return None

    def process_file(self, file_path: Path) -> FileNode | None:
        """Process a single file: parse its content if it should be processed and create a Node object."""
        if self.should_process_file(file_path):
            node = self.file_to_node(file_path)
            return node
        else:
            self.logger.debug(f"Skipping file: {file_path}")
            return None

    def traverse_directory(self) -> list[FileNode]:
        """Traverse the directory structure and process all valid files."""
        all_files = []
        for root, _, files in os.walk(self.local_files_path):
            for file in files:
                file_path = Path(root) / file
                all_files.append(file_path)

        self.logger.debug(f"Found {len(all_files)} files to process")

        valid_nodes = []
        
        for file_path in tqdm(all_files, desc="Processing files"):
            try:
                result = self.process_file(file_path)
                if result:
                    self.processed_files.add(file_path)
                    valid_nodes.append(result)
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                
        self.logger.info(f"Successfully processed {len(valid_nodes)} files out of {len(all_files)} total files")
        return valid_nodes
    
    def gather_failed_files(self) -> list[Path]:
        """Identify files that failed to parse properly (have empty content in cache)."""
        failed_files = []
        
        for file_path in self.processed_files:
            file_hash = self.hash_file(file_path)
            cache_path = self.parsed_files_path / f"{file_hash}.txt"
            
            try:
                if os.path.exists(cache_path):
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:  # If content is empty or just whitespace
                            failed_files.append(file_path)
                            self.logger.debug(f"Found failed parse: {file_path}")
            except Exception as e:
                self.logger.error(f"Error checking cache file for {file_path}: {e}")
                
        self.logger.info(f"Found {len(failed_files)} files that failed to parse properly")
        return failed_files

    def clean_cache(self, dry_run: bool) -> None:
        """Clean cache files for files that are no longer being processed."""
        cache_files = set(os.listdir(self.parsed_files_path))
        matched_caches = set()

        # Check each processed file
        for file_path in self.processed_files:
            file_hash = self.hash_file(file_path)
            cache_name = f"{file_hash}.txt"
            if cache_name in cache_files:
                matched_caches.add(cache_name)
            else:
                self.logger.debug(f"Removing outdated cache file: {file_path}")
        
        # Remove unmatched cache files
        files_removed = 0
        for cache_file in cache_files - matched_caches:
            try:
                if not dry_run:
                    os.remove(self.parsed_files_path / cache_file)
                files_removed += 1
            except OSError as e:
                self.logger.error(f"Error removing cache file {cache_file}: {e}")
        
        self.logger.info(f"Cache cleaning completed. Removed {files_removed} outdated cache files.")

    def run(self) -> list[FileNode]:
        """Run the entire file parsing process."""
        try:
            nodes = self.traverse_directory()
            self.logger.info(f"File parsing completed. Processed {len(nodes)} files.")
            failed_files = self.gather_failed_files()
            self.logger.warning(f"Failed files: {failed_files}")
            self.clean_cache(dry_run=True)
            return nodes
        except Exception as e:
            self.logger.error(f"Error in file processing: {e}")
            return []

if __name__ == "__main__":
    logger.info(os.getcwd())
    file_parser = FileParser(LOCAL_FILES_PATH, PARSED_FILES_PATH)
    processed_nodes = file_parser.run()
