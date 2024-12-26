import os
import hashlib
import asyncio
from tika import parser
import pytesseract
from pdf2image import convert_from_path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial
from typing import Optional
from pathlib import Path
import aiofiles
import psutil
from dataclasses import dataclass

from config.config_logger import logger
from config.settings import (
    INCLUDED_EXTENSIONS,
    HASH_BASE_SIZE,
    MIN_FILE_SIZE
)
from database.node import FileNode

@dataclass
class ResourceLimits:
    max_memory_percent: float = 75.0
    max_cpu_percent: float = 75.0
    max_concurrent_tika: int = 5
    max_concurrent_files: int = 10

class ResourceMonitor:
    """Monitor system resources and just ensuring that system
    resources are not exceeded."""
    def __init__(self, limits: ResourceLimits):
        self.limits = limits
        self._process = psutil.Process()
    
    def check_memory(self) -> bool:
        memeory_percent = psutil.virtual_memory().percent
        return memeory_percent < self.limits.max_memory_percent

    def check_cpu(self) -> bool:
        cpu_percent = psutil.cpu_percent()
        return cpu_percent < self.limits.max_cpu_percent

    async def wait_for_resources(self):
        # waiting for resources to be available
        while not (self.check_memory() and self.check_cpu()):
            await asyncio.sleep(1)

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
        limits: Optional[ResourceLimits] = None
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
        
        self.limits = limits or ResourceLimits()
        self.resource_monitor = ResourceMonitor(self.limits)
        self.tika_semaphore = asyncio.Semaphore(self.limits.max_concurrent_tika)
        self.file_semaphore = asyncio.Semaphore(self.limits.max_concurrent_files)
        # Limit concurrent file operations to prevent "too many open files"
        self.file_handle_semaphore = asyncio.Semaphore(50)  # Adjust this value based on system limits
        
        cpu_count = psutil.cpu_count(logical=False)
        self.process_pool = ProcessPoolExecutor(
            max_workers=max(1, cpu_count-1)
        )


    async def hash_file(self, file_path: Path) -> str:
        """Create a hash of the file based on its content and metadata."""
        file_stat = await asyncio.to_thread(os.stat, file_path)
        file_size = file_stat.st_size
        mod_time = file_stat.st_mtime # modification time invariant to changing file content
            
        # Read the entire content for small files, or first and last 1024 bytes for larger files
        async with self.file_handle_semaphore:
            async with aiofiles.open(file_path, 'rb') as f:
                if file_size <= 2*HASH_BASE_SIZE:  # If file is 2KB or smaller, read entire file
                    file_content = await f.read()
                else:
                    first_bytes = await f.read(HASH_BASE_SIZE)
                    await f.seek(-HASH_BASE_SIZE, 2)  # Seek to 1024 bytes from the end
                    last_bytes = await f.read()
                    file_content = first_bytes + last_bytes
        
        hash_input = f"{file_size}_{mod_time}_{file_content}"
        
        return hashlib.md5(hash_input.encode()).hexdigest()

    async def get_cached_content(self, file_hash):
        """Retrieve cached content if it exists."""
        cached_file_path = self.parsed_files_path / f"{file_hash}.txt"
        if await asyncio.to_thread(os.path.exists, cached_file_path):
            async with self.file_handle_semaphore:
                async with aiofiles.open(cached_file_path, 'r', encoding='utf-8') as f:
                    return await f.read()
        return None

    async def save_cached_content(self, file_hash, content):
        """Save parsed content to cache."""
        await asyncio.to_thread(os.makedirs, self.parsed_files_path, exist_ok=True)
        cached_file_path = self.parsed_files_path / f"{file_hash}.txt"
        async with self.file_handle_semaphore:
            async with aiofiles.open(cached_file_path, 'w', encoding='utf-8') as f:
                await f.write(content)

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
    

    async def parse_with_tika(self, file_path: Path) -> Optional[str]:
        """Async wrapper for Tika parsing"""

        try:
            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor() as executor:
                parsed_file = await loop.run_in_executor(
                    executor,
                    partial(parser.from_file, file_path,
                    requestOptions={'timeout': 180})
                )
                return parsed_file.get("content")
        except Exception as e:
            self.logger.debug(f"Failed parsing {file_path} with Tika. Error: {e}")
            return None


    async def parse_file(self, file_path) -> tuple[str, str]:
        """Parses a file using Tika, with a fallback to OCR if Tika fails."""
        file_hash = await self.hash_file(file_path)
        cached_content = await self.get_cached_content(file_hash)
        
        
        if cached_content:
            return file_hash, cached_content

        try:
            # making sure resources are available
            await self.resource_monitor.wait_for_resources()

            async with self.file_semaphore:
                async with self.tika_semaphore:
                    content = await self.parse_with_tika(file_path)
            
            if not content:
                content = await self.fallback_parse_file(file_path)
            
            content = content or ""
            await self.save_cached_content(file_hash, content)
            return file_hash, content
    
        except Exception as e:
            self.logger.error(f"Failed parsing {file_path}: {e}")
            content = await self.fallback_parse_file(file_path)
            content = content or ""
            await self.save_cached_content(file_hash, content)
            return file_hash, content

    async def should_process_file(self, file_path: Path) -> bool:
        """Check if the file should be processed based on its extension."""
        extension = file_path.suffix.lower()
        if extension not in self.include_extensions:
            return False
        file_stat = await asyncio.to_thread(os.stat, file_path)
        if file_stat.st_size < MIN_FILE_SIZE:
            return False
        return True

    async def file_to_node(
                    self,
                    file_path: Path,
                    ) -> FileNode | None:
        """Convert a file to a Node object with relevant fields filled out."""
        try:
            file_stats = os.stat(file_path)
            
            creation_time = datetime.fromtimestamp(file_stats.st_mtime)
            modification_time = datetime.fromtimestamp(file_stats.st_mtime)
            _, file_extension = os.path.splitext(file_path)
            file_type = file_extension.lstrip('.').lower()
            file_size = round(file_stats.st_size / 1024)  # Convert to KB and round
            
            hash, content = await self.parse_file(file_path)
            
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

    async def process_file(
            self,
            file_path: Path 
        ) -> FileNode | None:
        """Process a single file: parse its content if it should be processed and create a Node object."""
        if self.should_process_file(file_path):
            node = await self.file_to_node(file_path)
            return node
        else:
            self.logger.debug(f"Skipping file: {file_path}")
            return None

    async def traverse_directory(self) -> list[FileNode]:
        """Traverse the directory structure and process all valid files."""
        all_files = []
        for root, _, files in os.walk(self.local_files_path):
            for file in files:
                file_path = Path(root) / file
                all_files.append(file_path)

        self.logger.debug(f"Found {len(all_files)} files to process")

        valid_nodes = []
        chunk_size = 50  # Process files in chunks to prevent resource exhaustion
        
        for i in range(0, len(all_files), chunk_size):
            chunk = all_files[i:i + chunk_size]
            tasks = []
            
            # Create tasks for each file in the chunk
            for file_path in chunk:
                tasks.append(self.process_file(file_path))
            
            try:
                # Process chunk of files concurrently
                chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Handle results and any exceptions
                for result, file_path in zip(chunk_results, chunk):
                    if isinstance(result, Exception):
                        self.logger.error(f"Error processing {file_path}: {result}")
                        continue
                    if result:  # If we got a valid FileNode
                        self.processed_files.add(file_path)
                        valid_nodes.append(result)
                
                self.logger.debug(f"Processed chunk {i//chunk_size + 1}/{(len(all_files) + chunk_size - 1)//chunk_size}")
                
            except Exception as e:
                self.logger.error(f"Error processing chunk starting at index {i}: {e}")
                
            # Optional: Add a small delay between chunks to prevent system overload
            await asyncio.sleep(0.1)
                
        self.logger.info(f"Successfully processed {len(valid_nodes)} files out of {len(all_files)} total files")
        return valid_nodes
    
    async def gather_failed_files(self) -> list[Path]:
        """Identify files that failed to parse properly (have empty content in cache)."""
        failed_files = []
        
        for file_path in self.processed_files:
            file_hash = await self.hash_file(file_path)
            cache_path = self.parsed_files_path / f"{file_hash}.txt"
            
            try:
                if await asyncio.to_thread(os.path.exists, cache_path):
                    async with aiofiles.open(cache_path, 'r', encoding='utf-8') as f:
                        content = (await f.read()).strip()
                        if not content:  # If content is empty or just whitespace
                            failed_files.append(file_path)
                            self.logger.debug(f"Found failed parse: {file_path}")
            except Exception as e:
                self.logger.error(f"Error checking cache file for {file_path}: {e}")
                
        self.logger.info(f"Found {len(failed_files)} files that failed to parse properly")
        return failed_files

    async def clean_cache(self, dry_run: bool):
        """Clean cache files for files that are no longer being processed."""
        cache_files = set(await asyncio.to_thread(os.listdir, self.parsed_files_path))
        matched_caches = set()

        # Check each processed file
        for file_path in self.processed_files:
            file_hash = await self.hash_file(file_path)
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
                    await asyncio.to_thread(os.remove, self.parsed_files_path / cache_file)
                files_removed += 1
            except OSError as e:
                self.logger.error(f"Error removing cache file {cache_file}: {e}")
        
        self.logger.info(f"Cache cleaning completed. Removed {files_removed} outdated cache files.")

    async def run_async(self) -> list[FileNode]:
        """Run the entire file parsing process."""
        nodes = await self.traverse_directory()
        self.logger.info(f"File parsing completed. Processed {len(nodes)} files.")
        failed_files = await self.gather_failed_files()  # Add await here
        self.logger.warning(f"Failed files: {failed_files}")
        await self.clean_cache(dry_run=False)
        return nodes
    
    def run(self) -> list[FileNode]:
        """Synchronous wrapper for run_async."""
        try:
            return asyncio.run(self.run_async())
        except Exception as e:
            self.logger.error(f"Error in file processing: {e}")
            return []
