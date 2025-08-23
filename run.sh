#!/usr/bin/env bash
uvicorn src.diagnostics.main:app --host 0.0.0.0 --port 8000 --reload
