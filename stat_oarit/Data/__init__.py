from pathlib import Path
import sys

if getattr(sys, 'frozen', False):
    DATA_DIRECTORY = Path(sys.executable).parent / 'lib/stat_oarit/Data'
else:
    DATA_DIRECTORY = Path(__file__).parent

EMPLOYEES = DATA_DIRECTORY / 'employees.csv'
PATIENTS = DATA_DIRECTORY / 'patients.csv'
SCHEDULE = DATA_DIRECTORY / 'schedule.csv'


