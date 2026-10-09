import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CLITests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-m', 'ad_opsec_auditor', *map(str, args)], cwd=ROOT,
                              capture_output=True, text=True, timeout=10)

    def test_validate_and_schema(self):
        result = self.run_cli('validate', 'examples/safe.synthetic.json')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('no live infrastructure', result.stdout)
        self.assertEqual(json.loads(self.run_cli('schema').stdout)['title'], 'AD OPSEC normalized snapshot v1')

    def test_audit_exit_codes_and_formats(self):
        for name, code in [('safe', 0), ('risky', 1), ('incomplete', 3)]:
            with self.subTest(fixture=name):
                result = self.run_cli('audit', f'examples/{name}.synthetic.json')
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(len(json.loads(result.stdout)['results']), 9)
                markdown = self.run_cli('audit', f'examples/{name}.synthetic.json', '--format', 'markdown')
                self.assertEqual(markdown.returncode, code)
                self.assertIn('# AD OPSEC', markdown.stdout)
                self.assertIn('No live AD', markdown.stdout)

    def test_no_traceback_or_input_echo(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.json'
            for raw in ['{"password":"DO_NOT_ECHO_SECRET"}', '{"x":', '{"x":NaN}']:
                path.write_text(raw, encoding='utf-8')
                result = self.run_cli('audit', path)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, '')
                self.assertNotIn('Traceback', result.stderr)
                self.assertNotIn('DO_NOT_ECHO_SECRET', result.stderr)
        self.assertEqual(self.run_cli('validate', '/nonexistent/opsec-input.json').returncode, 2)

    def test_output_exclusive_and_input_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'report.json'
            source = Path(directory) / 'input.json'
            original = (ROOT / 'examples/safe.synthetic.json').read_bytes()
            source.write_bytes(original)
            result = self.run_cli('audit', source, '--output', destination)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, '')
            saved = destination.read_bytes()
            self.assertEqual(json.loads(saved)['summary']['pass'], 9)
            self.assertEqual(self.run_cli('audit', source, '--output', destination).returncode, 2)
            self.assertEqual(destination.read_bytes(), saved)
            self.assertEqual(self.run_cli('audit', source, '--output', source).returncode, 2)
            self.assertEqual(source.read_bytes(), original)
            if os.name == 'posix':
                self.assertEqual(destination.stat().st_mode & 0o777, 0o600)

    @unittest.skipUnless(os.name == 'posix', 'POSIX symlink/FIFO behavior')
    def test_symlink_output_and_fifo_input_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            alias = Path(directory) / 'alias'
            alias.symlink_to(ROOT / 'examples/safe.synthetic.json')
            self.assertEqual(self.run_cli('audit', 'examples/safe.synthetic.json', '--output', alias).returncode, 2)
            fifo = Path(directory) / 'fifo'
            os.mkfifo(fifo)
            self.assertEqual(self.run_cli('validate', fifo).returncode, 2)

    def test_no_network_or_execution_primitives(self):
        import ast
        forbidden = {'socket', 'requests', 'urllib', 'http', 'subprocess', 'ctypes'}
        for path in (ROOT / 'ad_opsec_auditor').glob('*.py'):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertFalse({a.name.split('.')[0] for a in node.names} & forbidden, path)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    self.assertNotIn(node.module.split('.')[0], forbidden, path)
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    self.assertNotIn(node.func.id, {'eval', 'exec', 'compile'}, path)
