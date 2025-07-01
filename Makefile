.PHONY: test
test:
	poetry run python examples/basic_usage.py

.PHONY: robotic
robotic:
	cd html && python -m http.server 8000