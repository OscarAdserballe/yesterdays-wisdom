import pytest
import asyncio
import os
from pathlib import Path
import aiofiles
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from components.local_files_walker.local_files import FileParser, ResourceLimits, ResourceMonitor
from database.node import FileNode

@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory with some test files."""
    # Create test directory structure
    test_files = tmp_path / "test_files"
    cache_dir = tmp_path / "cache"
    test_files.mkdir()
    cache_dir.mkdir()
    
    # Create some test files
    (test_files / "test1.pdf").write_text("Test content 1")
    (test_files / "test2.txt").write_text("Test content 2")
    (test_files / "test3.docx").write_text("Test content 3")
    (test_files / "ignored.xyz").write_text("Should be ignored")
    
    # Create a subdirectory with files
    subdir = test_files / "subdir"
    subdir.mkdir()
    (subdir / "test4.pdf").write_text("Test content 4")
    
    return {
        'root': tmp_path,
        'files_dir': test_files,
        'cache_dir': cache_dir
    }

@pytest.fixture
def file_parser(temp_dir):
    """Create a FileParser instance with test directories."""
    return FileParser(
        local_files_path=str(temp_dir['files_dir']),
        parsed_files_path=str(temp_dir['cache_dir']),
        limits=ResourceLimits()
    )

@pytest.mark.asyncio
async def test_traverse_directory_finds_all_valid_files(file_parser, temp_dir):
    """Test that traverse_directory finds all valid files."""
    nodes = await file_parser.traverse_directory()
    
    # Count files with valid extensions in test directory
    valid_files = [f for f in temp_dir['files_dir'].rglob('*') 
                  if f.suffix.lower() in file_parser.include_extensions]
    
    assert len(nodes) == len(valid_files)
    assert all(isinstance(node, FileNode) for node in nodes)

@pytest.mark.asyncio
async def test_process_file_creates_valid_node(file_parser, temp_dir):
    """Test that process_file creates a valid FileNode for a valid file."""
    test_file = temp_dir['files_dir'] / "test1.pdf"
    
    # Process the file
    node = await file_parser.process_file(test_file)
    
    assert isinstance(node, FileNode)
    assert node.path == str(test_file.absolute())
    assert node.filetype == "pdf"
    assert isinstance(node.file_creation_time, datetime)
    assert isinstance(node.file_modification_time, datetime)

@pytest.mark.asyncio
async def test_process_file_skips_invalid_extensions(file_parser, temp_dir):
    """Test that process_file skips files with invalid extensions."""
    invalid_file = temp_dir['files_dir'] / "ignored.xyz"
    
    # Process the file
    node = await file_parser.process_file(invalid_file)
    
    assert node is None

@pytest.mark.asyncio
async def test_hash_file_consistency(file_parser, temp_dir):
    """Test that hash_file produces consistent results for the same file."""
    test_file = temp_dir['files_dir'] / "test1.pdf"
    
    hash1 = await file_parser.hash_file(test_file)
    hash2 = await file_parser.hash_file(test_file)
    
    assert hash1 == hash2
    assert isinstance(hash1, str)
    assert len(hash1) > 0

@pytest.mark.asyncio
async def test_cache_operations(file_parser, temp_dir):
    """Test cache save and retrieve operations."""
    test_content = "Test cache content"
    test_hash = "test_hash_123"
    
    # Save to cache
    await file_parser.save_cached_content(test_hash, test_content)
    
    # Retrieve from cache
    cached_content = await file_parser.get_cached_content(test_hash)
    
    assert cached_content == test_content

@pytest.mark.asyncio
async def test_traverse_directory_handles_errors(file_parser):
    """Test that traverse_directory properly handles and logs errors."""
    with patch.object(file_parser, 'process_file', side_effect=Exception("Test error")):
        nodes = await file_parser.traverse_directory()
        
        assert isinstance(nodes, list)
        assert len(nodes) == 0  # Should return empty list on error

@pytest.mark.asyncio
async def test_resource_monitor(file_parser):
    """Test that ResourceMonitor properly checks system resources."""
    monitor = file_parser.resource_monitor
    
    # Test resource checks
    assert isinstance(monitor.check_memory(), bool)
    assert isinstance(monitor.check_cpu(), bool)
    
    # Test wait_for_resources doesn't hang
    with patch.object(monitor, 'check_memory', return_value=True), \
         patch.object(monitor, 'check_cpu', return_value=True):
        await monitor.wait_for_resources()

@pytest.mark.asyncio
async def test_concurrent_file_processing(file_parser, temp_dir):
    """Test that multiple files can be processed concurrently."""
    test_files = [
        temp_dir['files_dir'] / "test1.pdf",
        temp_dir['files_dir'] / "test2.txt",
        temp_dir['files_dir'] / "test3.docx"
    ]
    
    tasks = [file_parser.process_file(f) for f in test_files]
    results = await asyncio.gather(*tasks)
    
    assert len(results) == len(test_files)
    assert all(isinstance(r, FileNode) or r is None for r in results)

if __name__ == '__main__':
    pytest.main([__file__])

