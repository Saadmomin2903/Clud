"""
Test script to check if Flask is properly installed.
"""

try:
    from flask import Flask
    from flask_login import LoginManager
    print("Flask and Flask-Login are properly installed!")
except ImportError as e:
    print(f"Error importing Flask: {e}")
