.PHONY: test
test:
	poetry run python examples/basic_usage.py

.PHONY: web
web:
	cd web && python -m http.server 8000