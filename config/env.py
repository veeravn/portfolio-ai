import os

AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://veerav-ai.openai.azure.com/")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "gpt-4.1")
REPO_OWNER    = "veeravn"
REPO_NAME     = "veeravn.github.io"
API_BASE      = "https://api.github.com"
DEFAULT_BRANCH= "master"
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", DEFAULT_BRANCH)
GITHUB_REPO   = os.getenv("GITHUB_REPO", "veeravn/veeravn.github.io")
GITHUB_TOKEN  = os.getenv("GITHUB_TOKEN")
