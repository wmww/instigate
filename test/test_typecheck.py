from unittest import TestCase
import shutil
import os
import subprocess

class TestTypecheck(TestCase):
    def test_typechecks(self) -> None:
        reset_color = '\x1b[0m'
        mypy = shutil.which('mypy')
        assert mypy is not None, 'could not find mypy executable'
        project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        assert os.path.isfile(os.path.join(project_path, 'LICENSE')), project_path + ' does not contain LICENSE'
        os.environ['MYPY_FORCE_COLOR'] = '1'
        result = subprocess.run([mypy, project_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if result.returncode != 0:
            raise RuntimeError('`$ mypy ' + project_path + '` failed:\n\n' + reset_color + result.stdout)
