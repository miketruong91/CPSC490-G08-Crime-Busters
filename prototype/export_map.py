"""Export the combined map as HTML that opens without a Flask server."""
import argparse
import json
from pathlib import Path
from app import app


def export(output):
    response = app.test_client().get('/api/map-incidents')
    if response.status_code != 200:
        raise RuntimeError('Build or select a working combined database first')
    data = json.dumps(response.json, ensure_ascii=True).replace('<', '\\u003c')
    page = app.test_client().get('/').get_data(as_text=True)
    page = page.replace('<script src="https://unpkg.com/leaflet',
        '<script>window.CRIME_BUSTERS_DATA=' + data + ';</script>\n<script src="https://unpkg.com/leaflet', 1)
    Path(output).write_text(page, encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('multi-city-map.html'))
    export(parser.parse_args().output)
