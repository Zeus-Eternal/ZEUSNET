#!/usr/bin/env python3
# gtk_launcher.py
import sys
import os

os.execv(sys.executable, ["python3", "frontend/main.py"])
