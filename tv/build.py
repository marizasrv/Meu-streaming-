"""Build the single HTML file to copy into Tizen Studio. No npm dependencies."""
import json
from pathlib import Path
root = Path(__file__).resolve().parent
config = json.loads((root / 'src/config.json').read_text())
assert config['key'].startswith('sb_publishable_'), 'Only a publishable key belongs in the TV app.'
def literal(value):
    return json.dumps(value, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
data = 'var TV_CONFIG = ' + literal(config) + ';\nvar TV_CONTENT = ' + literal(json.loads((root / 'src/content.json').read_text())) + ';'
html = (root / 'src/shell.html').read_text().replace('/*__DATA__*/', data).replace('/*__APP__*/', (root / 'src/app.js').read_text())
(root / 'index.html').write_text(html)
print('Generated tv/index.html')
