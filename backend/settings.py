import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///zeusnet.db")
ZEUSNET_MODE = os.getenv("ZEUSNET_MODE", "SAFE")
