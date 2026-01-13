SHELL := /bin/bash

dev:
	-lsof -ti:5000 | xargs kill -9
	source venv/bin/activate && python run.py
