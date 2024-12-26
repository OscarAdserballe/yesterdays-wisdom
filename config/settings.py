"""
Global configuration settings for Yesterdays Wisdom
"""

# File processing settings
SUPPORTED_FILE_TYPES = [".txt", ".md", ".rst"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
MIN_FILE_SIZE = 250  # 250 bytes (otherwise probably inconsequential)
HASH_BASE_SIZE = 1024 # 1024 bytes of top and bottom of file for hashing

MAX_TOKEN_LIMIT = 1e7

LOCAL_FILES_PATH = "/Users/oscarjuliusadserballe/OneDrive"
PARSED_FILES_PATH = "/Users/oscarjuliusadserballe/OneDrive/5th Semester/Yesterdays Wisdom/cache_files"
INCLUDED_EXTENSIONS =   {
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".rtf", ".pptm", ".ppsx", ".odt", ".ods", ".odp", ".epub",
    ".md"
}
    
# LLM settings
EMBEDDING_MODEL = "text-mutilingual-embedding-002"
LLM_MODEL = "gemini-2.0-flash-exp"

