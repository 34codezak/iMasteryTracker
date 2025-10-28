# Compatibility shim for Reflex: Reflex expects a module named <app_name>.<app_name>
# We forward that to your existing app.py
from .app import app
