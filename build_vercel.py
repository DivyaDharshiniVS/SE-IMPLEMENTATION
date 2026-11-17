#!/usr/bin/env python3
"""
build_vercel.py - Static Stlite Export Builder for Vercel Deployment
Delegates to build_netlify to compile the WebAssembly distribution into public/
"""

from build_netlify import build

if __name__ == "__main__":
    build()
