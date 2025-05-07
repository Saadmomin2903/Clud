"""
Command-line interface for Function Cloud (FC).
"""

import os
import sys
import argparse
import json
from typing import Optional, List, Dict, Any

from function_cloud.auth import FCAuth


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the Function Cloud CLI.
    
    Args:
        args (List[str], optional): Command-line arguments.
        
    Returns:
        int: Exit code.
    """
    parser = argparse.ArgumentParser(description="Function Cloud CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Token commands
    token_parser = subparsers.add_parser("token", help="Token management")
    token_subparsers = token_parser.add_subparsers(dest="token_command", help="Token command to run")
    
    # Generate token
    generate_parser = token_subparsers.add_parser("generate", help="Generate a new token")
    
    # Validate token
    validate_parser = token_subparsers.add_parser("validate", help="Validate a token")
    validate_parser.add_argument("token", help="Token to validate")
    
    # Revoke token
    revoke_parser = token_subparsers.add_parser("revoke", help="Revoke a token")
    revoke_parser.add_argument("token", help="Token to revoke")
    
    # Web commands
    web_parser = subparsers.add_parser("web", help="Web interface")
    web_parser.add_argument("--host", default="127.0.0.1", help="Host to run the web interface on")
    web_parser.add_argument("--port", type=int, default=5000, help="Port to run the web interface on")
    web_parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    # Parse arguments
    args = parser.parse_args(args)
    
    # Initialize authentication
    auth = FCAuth()
    
    # Handle commands
    if args.command == "token":
        if args.token_command == "generate":
            token = auth.generate_token()
            print(f"Generated token: {token}")
            return 0
        elif args.token_command == "validate":
            valid = auth.validate_token(args.token)
            if valid:
                print("Token is valid")
                return 0
            else:
                print("Token is invalid")
                return 1
        elif args.token_command == "revoke":
            revoked = auth.revoke_token(args.token)
            if revoked:
                print("Token revoked")
                return 0
            else:
                print("Token not found")
                return 1
        else:
            token_parser.print_help()
            return 1
    elif args.command == "web":
        try:
            from function_cloud.web import create_app
        except ImportError:
            print("Web dependencies not installed. Install with 'pip install function-cloud[web]'")
            return 1
        
        # Set environment variables
        os.environ.setdefault("FC_SECRET_KEY", os.urandom(24).hex())
        
        # Create and run the app
        app = create_app()
        app.run(host=args.host, port=args.port, debug=args.debug)
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
