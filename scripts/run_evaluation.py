import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.evaluation import run_evaluation
import json
print(json.dumps(run_evaluation(), indent=2))
