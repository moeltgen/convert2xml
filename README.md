# convert2xml

Python scripts to convert stats file to DDI xml metadata

* use convertspssxml.py to read spss sav file and export DDI32 xml file

You can either specify a file with option -f \<file> or specify a whole directory with option -p \<path>.
Export formats are xml, txt, or json. The xml uses DDI 3.2 format. SPSS file encoding can be specified.

# Usage

Open a DOS Command Prompt and enter:

    python convertspssxml.py -f <file> -l <language>


# Options

usage1: 

    convertspssxml.py -p <path> -l <language>

usage2: 

    convertspssxml.py -f <file> -l <language>


for help use: 

    convertspssxml.py -h

usage1 with options:

    convertspssxml.py -p <path> [-l <language> -o <outputfile>] [-e <errorfile>] [-x <format>] [-g <encoding>] [-s] [-a]

usage2 with options: 

    convertspssxml.py -f <file> [-l <language> -o <outputfile>] [-e <errorfile>] [-x <format>] [-g <encoding>] [-s] [-a]

Options:
* -p path (required): path to be checked for SPSS Data Files
* -f file (required): file to be converted (SPSS Data File)

Further options:
* -l language: language code (default=de)
* -g encoding: file encoding, from ICONV list (default=UTF-8, may be ISO-8859-1, CP1252)
* -c or --cut: cut illegal chars, below ascii32
* -o outputfile: path and filename for storing the output (if not default should be used)
* -e errorfile: path and filename for storing detailed error information (if not default should be used)
* -x format: export format (default is xml, can also be txt or json, or combination like xmltxt for several)
* -m mdefile: write/append to metadata-expectations xml file mdefile
* -d or --mdefresh: create a fresh mdefile/delete existing before writing
* -s or --sub: use subdirectories (together with -p only)
* -a or --asub: use subdirectories (together with -p only) and use only those ending with Service

# Requires

Tested with Python 3.10.7

Uses pyreadstat


# Tests

You can run test2b.cmd to run the script for 4 example files in directory test2.
Result should be 4 xml files in directory out and 4 log files in directory log.

You can also run tryenc.cmd to run the script testing different encodings for file in directory test4.
Result should be a log file (tryenc_log.txt) showing which encodings worked and which not.

Note: Respondents have been deleted from the example SPSS files. Only metadata is available.

# Metadata Expectations

To check processing of studies and variables, GESIS uses a metadata-expectation file. It contains all
studies and number of variables for a given language. The script will create this file or append studies to it.
To start from scratch, the switch -d will delete the mde-file, and append the first study. Subsequent studies will 
be appended as well.

For studies with more than one language, the mde-file will contain more than one entry. To collapse this, so that 
a study exists only once and has the correct number of languages, you can call the script collapsemde.py.
The test2b.cmd contains an example. Output is the file md-expectation.xml.

