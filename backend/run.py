#!/usr/bin/env python3
"""Run the backend server.

Usage:
    python run.py
    python run.py --port 8000
    python run.py --reload
"""

import argparse
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Run the tapusAI backend server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    print(f"Starting tapusAI backend at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop\n")

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
