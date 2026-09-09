"""Generate two independently passing partial PRs without an integrated CLI."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from delivery_fixture import create, run


def setup(target):
    create(target)
    target = target.resolve()
    baseline = run(target, 'rev-parse', 'main')
    variants = {
        'reader': (
            'import csv\n\ndef read_rows(source):\n    return list(csv.DictReader(source))\n',
            '''import io
import unittest
from reader import read_rows
class ReaderTest(unittest.TestCase):
    def test_quoted_category(self):
        self.assertEqual(read_rows(io.StringIO('category,amount\\n"Food, home",1.20\\n')), [{'category': 'Food, home', 'amount': '1.20'}])
'''),
        'totals': (
            'from decimal import Decimal\n\ndef totals(rows):\n    result = {}\n    for row in rows:\n        key = row["category"]\n        result[key] = result.get(key, Decimal(0)) + Decimal(row["amount"])\n    return result\n',
            '''import unittest
from decimal import Decimal
from totals import totals
class TotalsTest(unittest.TestCase):
    def test_exact_sum(self):
        self.assertEqual(totals([{'category': 'Food', 'amount': '0.1'}, {'category': 'Food', 'amount': '0.2'}]), {'Food': Decimal('0.3')})
''')}
    for name, (source, test) in variants.items():
        branch = 'codex/partial-' + name
        run(target, 'switch', '-c', branch, baseline)
        (target / (name + '.py')).write_text(source)
        (target / 'tests').mkdir(exist_ok=True)
        (target / 'tests' / ('test_' + name + '.py')).write_text(test)
        checks = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests'],
                                cwd=target, capture_output=True, text=True, check=True)
        run(target, 'add', name + '.py', 'tests')
        run(target, 'commit', '-m', 'Synthetic partial ' + name)
        sha = run(target, 'rev-parse', 'HEAD')
        run(target, 'push', 'shared', branch)
        body = 'This partial implementation has no integrated CLI. Actual local check at ' + sha + ': python3 -m unittest discover -s tests\n' + checks.stderr
        with tempfile.TemporaryDirectory() as temp:
            payload = Path(temp) / 'pr.json'
            payload.write_text(json.dumps({'title': 'Partial ' + name, 'body': body, 'head': sha, 'branch': branch}))
            subprocess.run([str(target / 'tools/gh'), 'api', '--method', 'POST',
                            'repos/fixture/receipt-desk/pulls', '--input', str(payload)], check=True)
    run(target, 'checkout', '--detach', baseline)
    print('Fixed default baseline:', baseline)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('target', type=Path)
    setup(parser.parse_args().target)
