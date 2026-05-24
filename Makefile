.PHONY: test
test:
	poetry run pytest music/dancer/__test__/ -v

# Run the basic usage example
.PHONY: example
example:
	poetry run python examples/basic_usage.py

# Analyze an audio file and visualise spectrum
.PHONY: analyze
analyze:
	poetry run python -c "from music.analyzer.spectrum_analyzer import analyze_audio_spectrum; analyze_audio_spectrum('$(AUDIO)', show_plots=True)"

# Generate dance choreography from an audio file
# Usage: make dance AUDIO=path/to/song.mp3
.PHONY: dance
dance:
	poetry run python -m music $(AUDIO) --output web/data/dance.json

# Start the web visualisation server
.PHONY: web
web:
	cd web && python -m http.server 8000