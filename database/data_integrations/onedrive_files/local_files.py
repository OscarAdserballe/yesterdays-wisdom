import os
import hashlib
from tika import parser
import pytesseract
from pdf2image import convert_from_path
from datetime import datetime
import glob

from config.config_logger import logger
from database.node import Node

class FileParser:
    def __init__(self, local_files_path, parsed_files_path):
        self.local_files_path = local_files_path
        self.parsed_files_path = parsed_files_path
        self.logger = logger
        self.processed_files = set()
        
        self.include_extensions = {
            ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
             ".rtf", ".pptm", ".ppsx", ".odt", ".ods", ".odp", ".epub"
        }
        # min. file size to be processed at 250 bytes
        self.min_file_size = 250


    def hash_file(self, file_path):
        """Create a hash of the file based on its content and metadata."""
        file_stat = os.stat(file_path)
        file_size = file_stat.st_size
        mod_time = file_stat.st_mtime # modification time invariant to changing file content
            
        # Read the entire content for small files, or first and last 1024 bytes for larger files
        with open(file_path, 'rb') as f:
            if file_size <= 2048:  # If file is 2KB or smaller, read entire file
                file_content = f.read()
            else:
                first_bytes = f.read(1024)
                f.seek(-1024, 2)  # Seek to 1024 bytes from the end
                last_bytes = f.read()
                file_content = first_bytes + last_bytes
        
        hash_input = f"{file_size}_{mod_time}_{file_content}"
        
        return hashlib.md5(hash_input.encode()).hexdigest()

    def get_cached_content(self, file_hash):
        """Retrieve cached content if it exists."""
        cached_file_path = os.path.join(self.parsed_files_path, f"{file_hash}.txt")
        if os.path.exists(cached_file_path):
            with open(cached_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def save_cached_content(self, file_hash, content):
        """Save parsed content to cache."""
        cached_file_path = os.path.join(self.parsed_files_path, f"{file_hash}.txt")
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

    def parse_file(self, file_path):
        """Parses a file using Tika, with a fallback to OCR if Tika fails."""
        file_hash = self.hash_file(file_path)
        cached_content = self.get_cached_content(file_hash)
        
        if cached_content:
            return cached_content

        try:
            parsed_file = parser.from_file(file_path, requestOptions={'timeout': 180})
            content = parsed_file['content'] or ""
            
            if not content:
                content = self.fallback_parse_file(file_path)
            
            self.save_cached_content(file_hash, content)
            return content
        except Exception as e:
            self.logger.debug(f"Failed parsing {file_path} with Tika. Error: {e}")
            content = self.fallback_parse_file(file_path)
            self.save_cached_content(file_hash, content)
            return content

    def should_process_file(self, file_path):
        """Check if the file should be processed based on its extension."""
        _, extension = os.path.splitext(file_path.lower())
        if extension not in self.include_extensions:
            return False
        if os.stat(file_path).st_size < self.min_file_size:
            return False
        return True

    def file_to_node(
                    self,
                    file_path: str,
                    ) -> Node:
        """Convert a file to a Node object with relevant fields filled out."""
        try:
            file_stats = os.stat(file_path)
            
            creation_time = datetime.fromtimestamp(file_stats.st_mtime)
            modification_time = datetime.fromtimestamp(file_stats.st_mtime)
            _, file_extension = os.path.splitext(file_path)
            file_type = file_extension.lstrip('.').lower()
            file_size = round(file_stats.st_size / 1024)  # Convert to KB and round
            
            content = self.parse_file(file_path)
            
            node = Node(
                content=content,
                file_creation_date=creation_time,
                modification_date=modification_time,
                filetype=file_type,
                location="Local Files",
                path=os.path.abspath(file_path),
                file_size=file_size  
            )
            self.logger.debug(f"Processed file and created Node: {file_path}")
            
            return node
        except Exception as e:
            self.logger.exception(f"Error processing file {file_path}: {str(e)}")
            return None

    def process_file(
            self,
            file_path: str
        ) -> Node:
        """Process a single file: parse its content if it should be processed and create a Node object."""
        if self.should_process_file(file_path):
            node = self.file_to_node(file_path)
            return node
        else:
            self.logger.debug(f"Skipping file: {file_path}")
            return None

    def traverse_directory(self):
        """Traverse the directory structure and process all valid files."""
        nodes = []
        for root, _, files in os.walk(self.local_files_path):
            for file in files:
                file_path = os.path.join(root, file)
                node = self.process_file(file_path)
                if node:
                    self.processed_files.add(file_path)
                    nodes.append(node)
        return nodes
    
    def gather_failed_files(self):
        """Identify files that failed to parse properly (have empty content in cache)."""
        failed_files = []
        
        for file_path in self.processed_files:
            file_hash = self.hash_file(file_path)
            cache_path = os.path.join(self.parsed_files_path, f"{file_hash}.txt")
            
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

    def clean_cache(self, dry_run:bool):
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
                if not dry_run: os.remove(os.path.join(self.parsed_files_path, cache_file))
                files_removed += 1
            except OSError as e:
                self.logger.error(f"Error removing cache file {cache_file}: {e}")
        
        self.logger.info(f"Cache cleaning completed. Removed {files_removed} outdated cache files.")

    def run(self):
        """Run the entire file parsing process."""
        nodes = self.traverse_directory()
        self.logger.info(f"File parsing completed. Processed {len(nodes)} files.")
        failed_files = self.gather_failed_files()
        self.logger.warning(f"Failed files: {failed_files}")
        self.clean_cache(dry_run=False)
        return nodes