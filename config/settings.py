from pathlib import Path
"""
Global configuration settings for Yesterdays Wisdom
"""

# File processing settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MIN_FILE_SIZE = 250  # 250 bytes (otherwise probabl inconsequential)
HASH_BASE_SIZE = 1024 # 1024 bytes of top and bottom of file for hashing

MAX_TOKEN_LIMIT = 1e7

LOCAL_FILES_PATH = Path("/Users/oscarjuliusadserballe/Google Drive/My Drive").expanduser().resolve()
PARSED_FILES_PATH = Path("/Users/oscarjuliusadserballe/Projects/Yesterdays Wisdom/cache_files").expanduser().resolve()
INCLUDED_EXTENSIONS =   {
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".rtf", ".pptm", ".ppsx", ".odt", ".ods", ".odp", ".epub",
    ".md"
}
    
# LLM settings
EMBEDDING_MODEL = "text-mutilingual-embedding-002"
LLM_MODEL = "gemini-2.0-flash-exp"

# Notes storage settings
NOTES_PATH = Path("~/Google Drive/My Drive/Handwritten Notes/").expanduser().resolve()
OBSIDIAN_VAULT_PATH = Path("~/Google Drive/My Drive/Obsidian/").expanduser().resolve()



