@ECHO OFF
ECHO Testing 2 languages, and more files
python convertspssxml.py -f test2\ZA0055_v2-1-0.sav -l de 
python convertspssxml.py -f test2\ZA0055_v2-1-0_en.sav -l en 
python convertspssxml.py -f test2\ZA1053.sav -l de 
python convertspssxml.py -f test2\ZA3450_v2-0-0.sav -l en 
python collapsemde.py