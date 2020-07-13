#!/bin/bash

set -ex

# Pick up PORT if available else fallback to 8000
PORT=${PORT:-8000}

uvicorn main:app --host 0.0.0.0 --port $PORT
