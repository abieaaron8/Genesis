from pathlib import Path

from dotenv import load_dotenv


# Load the package-local runtime configuration before any backend submodule
# reads provider settings at import time.
load_dotenv(Path(__file__).resolve().parent / ".env")
