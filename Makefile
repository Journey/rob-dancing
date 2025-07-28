.PHONY: test
test:
	poetry run python examples/basic_usage.py

# analyze audio file
.PHONY: analyze
analyze:
	poetry run python music/spectrum_analyzer.py

# start web server
.PHONY: web
web:
	cd web && python -m http.server 8000