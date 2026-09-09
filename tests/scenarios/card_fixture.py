"""Generate the two isolated card-consumption projects; never send externally."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
INPUTS = Path(__file__).with_name('communication')


def create(base):
    for kind in ('nontechnical', 'technical'):
        target = (base / kind).resolve()
        target.mkdir(parents=True, exist_ok=False)
        (target / 'candidate.md').write_bytes((INPUTS / 'facts.md').read_bytes())
        brief = {'name': 'Archive Import', 'goal': 'Import local photos with clear results.',
                 'scope': ['Local import'], 'sources': ['candidate.md']}
        with tempfile.TemporaryDirectory(prefix='card-input-') as temp:
            path = Path(temp) / 'brief.json'
            path.write_text(json.dumps(brief))
            subprocess.run([sys.executable, str(ROOT / 'skills/cybercorp/scripts/cybercorp.py'),
                            str(target), '--brief', str(path)], check=True)
        (target / 'docs/corp/owner-communication.md').write_bytes((INPUTS / (kind + '.md')).read_bytes())
        print(target)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('base', type=Path)
    create(parser.parse_args().base)
