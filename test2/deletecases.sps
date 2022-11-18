* Encoding: UTF-8.

* Delete all cases, only metadata is needed.
GET
  FILE=
    'C:\Users\moeltgen\Documents\python\convertspssxml\EDDI22\convert2xml\test2\ZA0055_v2-1-0.sav'.
DATASET NAME DataSet3 WINDOW=FRONT.

SELECT IF za_nr=999999.
EXECUTE.
SAVE OUTFILE='C:\Users\moeltgen\Documents\python\convertspssxml\EDDI22\convert2xml\test2\ZA0055_v2-1-0.sav'
  /COMPRESSED.
