"""Reference defaults must remain portable and preserve project edits."""
import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest

SKILL = pathlib.Path(__file__).resolve().parents[1] / 'comic-draft-studio'
sys.path.insert(0, str(SKILL / 'scripts'))
from build import build

class LayoutLibraryTests(unittest.TestCase):
    def test_defaults_and_user_override(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            build(root, True)
            path = root / '资料/布局参考.json'
            original = json.loads(path.read_text())
            self.assertEqual(len(original['entries']), 10)
            original['entries'][0]['application'] = '用户自己的修改'
            path.write_text(json.dumps(original, ensure_ascii=False))
            build(root, True)
            self.assertEqual(json.loads(path.read_text()), original)
            self.assertIn('用户自己的修改', (root / 'index.html').read_text())
            self.assertEqual(json.loads((root / '资料/选题库.json').read_text()), [])
            self.assertEqual(list((root / '资料/期次').glob('*.json')), [])
            # Older project without this new file receives defaults on ordinary build.
            path.unlink()
            build(root)
            self.assertEqual(len(json.loads(path.read_text())['entries']), 10)

if __name__ == '__main__':
    unittest.main()
