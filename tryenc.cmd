@ECHO OFF
setlocal EnableDelayedExpansion 
REM
REM this DOS batch runs the convertspssxml.py script with different encodings on a certain file
REM
REM tryencoding: possible values 
REM CP1250 CP1251 CP1252 CP1253 CP1254 CP1255 CP1256 CP1257 CP1258
REM ISO-8859-1 ISO-8859-2 ISO-8859-3 ISO-8859-4 ISO-8859-5 ISO-8859-6 ISO-8859-7 ISO-8859-8 ISO-8859-9 ISO-8859-10 ISO-8859-11 ISO-8859-12 ISO-8859-13 ISO-8859-14 ISO-8859-15 ISO-8859-16
REM UTF-16 UTF-16BE UTF-16LE UCS-2 UCS-2LE UCS-2BE UCS-4 UCS-4LE UCS-4BE CP437 ASCII UTF-7
REM 
REM
REM This is the file to be tested 
SET f=C:\Users\moeltgen\Documents\python\convertspssxml\EDDI22\convert2xml\test4\ZA5676_v1-0-0_new.sav
REM 
SET logfile=tryenc_log.txt
REM
SET s=UTF-16 UTF-16BE UTF-16LE UCS-2 UCS-2LE UCS-2BE UCS-4 UCS-4LE UCS-4BE CP437 ASCII UTF-7
REM
echo results in %logfile%
echo results in %logfile% > %logfile%
echo file is %f%
echo file is %f% >> %logfile%
for %%H in (%s%) do (
	SET x=%%H
	echo !x!
	echo !x!>>%logfile%
	python convertspssxml.py -a -l de -f %f% -g !x!>> %logfile% 2>&1
	REM 
)