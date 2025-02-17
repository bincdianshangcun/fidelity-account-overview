from pathlib import Path
tests_directory = Path(__file__).resolve().parent
prj_top_dir = tests_directory.parent

import sys
if str(prj_top_dir) not in sys.path:
    sys.path.insert(1,str(prj_top_dir))

