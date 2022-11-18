@ECHO OFF
ECHO Testing 2 languages, and more files
python convertspssxml.py -f test2\ZA0055_v2-1-0.sav -l de -o out\mytest1.out.log -e out\mytest1.err.log -m md-expectation.xml -d
python convertspssxml.py -f test2\ZA0055_v2-1-0_en.sav -l en -o out\mytest2.out.log -e out\mytest2.err.log -m md-expectation.xml
python convertspssxml.py -f test2\ZA1053.sav -l de -o out\mytest3.out.log -e out\mytest3.err.log -m md-expectation.xml
python convertspssxml.py -f test2\ZA3450_v2-0-0.sav -l en -o out\mytest4.out.log -e out\mytest4.err.log -m md-expectation.xml
python collapsemde.py