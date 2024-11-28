from pathlib import Path
import sys

if getattr(sys, 'frozen', False):
    IMAGE_DIRECTORY = Path(sys._MEIPASS) / 'stat_oarit' / 'images'
else:
    IMAGE_DIRECTORY = Path(__file__).parent

ARROW = IMAGE_DIRECTORY / 'arrow-resize-090.png'
DOCTOR = IMAGE_DIRECTORY / 'Doctor2.png'
IDCARD = IMAGE_DIRECTORY / 'ID Card2.png'
MAGNIFER = IMAGE_DIRECTORY / 'magnifier.png'
MEDICALFOLD = IMAGE_DIRECTORY / 'Medical Folder2.png'
SYMPTOM = IMAGE_DIRECTORY / 'Symptom List2.png'
ICON = IMAGE_DIRECTORY / 'stat_oarit_icon.png'


