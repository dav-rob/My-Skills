"""CLI regression checks; all writes and mock installs use a temporary home."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skillstrap.sh'
AGENTS = ['opencode', 'codex', 'claude-code', 'cursor', 'antigravity', 'antigravity-cli']

SHIM = r'''#!/usr/bin/env python3
import json, os, pathlib, shutil, subprocess, sys
args = sys.argv[1:]
state = pathlib.Path(os.environ['TEST_STATE'])
with (state / 'calls').open('a') as out:
    out.write(json.dumps([pathlib.Path(sys.argv[0]).name] + args) + '\n')
if pathlib.Path(sys.argv[0]).name == 'curl':
    if (state / 'download-fails').exists():
        sys.exit(1)
    shutil.copyfile(os.environ['TEST_SCRIPT'], args[args.index('-o') + 1])
elif args[:2] == ['repo', 'clone']:
    shutil.copytree(state / 'source', args[3], symlinks=True)
elif args[:2] == ['skill', 'publish']:
    if (state / 'invalid-format').exists():
        print('error: invalid description: DO_NOT_PRINT_UNTRUSTED_CONTENT')
        sys.exit(1)
elif args[:2] == ['skill', 'list']:
    rows = json.loads((state / 'rows.json').read_text())
    for name, path in rows:
        if pathlib.Path(path.replace('~/', os.environ['HOME'] + '/', 1)).exists():
            print(name + '\t' + path + '\ttest/source')
elif args[:2] == ['skill', 'install']:
    if (state / 'install-fails').exists():
        sys.exit(1)
elif args[:2] == ['auth', 'status'] or args == ['skill', '--help']:
    pass
else:
    sys.exit('unexpected shim arguments: ' + repr(args))
'''

class SkillstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='skillstrap-tests-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.home = self.base / 'home with spaces'
        self.home.mkdir()
        self.state = self.base / 'state'
        self.state.mkdir()
        (self.state / 'source').mkdir()
        (self.state / 'rows.json').write_text('[]')
        self.bin = self.base / 'bin'
        self.bin.mkdir()
        for command in ['gh', 'curl']:
            path = self.bin / command
            path.write_text(SHIM)
            path.chmod(0o755)
        self.env = dict(os.environ, HOME=str(self.home), PATH=str(self.bin) + ':' + os.environ['PATH'],
                        TMPDIR=str(self.base), TEST_STATE=str(self.state), TEST_SCRIPT=str(SCRIPT))

    def run_cli(self, *args, ok=True):
        result = subprocess.run([os.environ.get('TEST_SHELL', '/bin/sh'), str(SCRIPT), *args],
                                env=self.env, text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def calls(self):
        path = self.state / 'calls'
        return [json.loads(row) for row in path.read_text().splitlines()] if path.exists() else []

    def skill(self, name='safe', body='Use this skill to inspect a document.'):
        path = self.state / 'source' / 'skills' / name
        path.mkdir(parents=True, exist_ok=True)
        (path / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: Inspect documents.\n---\n{body}\n')
        return path

    def test_bootstrap_only_installs_command_and_is_idempotent(self):
        self.run_cli()
        original = (self.home / '.zshrc').read_text()
        self.run_cli()
        self.assertEqual((self.home / '.zshrc').read_text(), original)
        self.assertEqual(original.count('export PATH="$HOME/.local/bin:$PATH"'), 1)
        self.assertEqual((self.home / '.local/bin/skillstrap.sh').read_bytes(), SCRIPT.read_bytes())
        self.assertTrue(os.access(self.home / '.local/bin/skillstrap.sh', os.X_OK))
        self.assertTrue(all(call[0] == 'curl' for call in self.calls()))

    def test_bootstrap_reuses_existing_path_line(self):
        zshrc = self.home / '.zshrc'
        zshrc.write_text('export PATH="$HOME/.local/bin:$PATH"\n')
        self.run_cli()
        self.assertEqual(zshrc.read_text().count('export PATH="$HOME/.local/bin:$PATH"'), 1)

    def test_bootstrap_repairs_marker_without_path_line(self):
        zshrc = self.home / '.zshrc'
        zshrc.write_text('# >>> skillstrap >>>\n# <<< skillstrap <<<\n')
        self.run_cli()
        self.assertEqual(zshrc.read_text().count('export PATH="$HOME/.local/bin:$PATH"'), 1)

    def test_failed_download_preserves_installed_command(self):
        self.run_cli()
        installed = self.home / '.local/bin/skillstrap.sh'
        installed.write_text('old version\n')
        (self.state / 'download-fails').touch()
        self.run_cli(ok=False)
        self.assertEqual(installed.read_text(), 'old version\n')
        self.assertEqual(list(self.base.glob('skillstrap.*')), [])

    def test_empty_argument_is_not_bootstrap(self):
        self.run_cli('', ok=False)
        self.assertFalse(self.calls())

    def test_list_forwards_user_scope(self):
        self.run_cli('list')
        self.assertIn(['gh', 'skill', 'list', '--scope', 'user'], self.calls())

if __name__ == '__main__':
    unittest.main()
