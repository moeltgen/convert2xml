#!/usr/bin/python
# -*- coding: cp1252 -*-

# converts spss data files to DDI xml files 
# usage
# python convertspssxml.py -p <path> 
#
# needs global_vars.py present
#
# Version history
# V1.91 W. Zenk-Möltgen, 2022-07-12
#
#

pname = 'convertspssxml.py'
pdescription = 'Python script to create DDI XML files from SPSS Data Files'
pversion = '1.91'
pdate = '2022-07-12'
pauthor = 'W. Zenk-Möltgen'

import sys, getopt
import datetime
import os.path
#from plumbum import local
#from lxml import etree, isoschematron

#import pandas as pd
import pyreadstat
import html
import math

import global_vars as g

#import xml.etree.ElementTree as ET


def CLASS(*args): # class is a reserved word in Python
    return {"class":' '.join(args)}

def removeIllegalChars(text): 
    # try to cope with illegal chars 
    #
    # use from dsdmxmlexport.exe : CharCodesToHTML()
    # 'new 1.6.2 check for unicode invalid chars: All below #x20, except #x9 | #xA | #xD
    
    if g.cutillegalchars:
        newtext=''
        if text is not None: 
            for char in text:
                asc=ord(char) #gets ascii code of char
                if asc<32:
                    if asc==9 or asc==10 or asc==13:
                        newtext += char 
                else:
                    newtext += char 
    else:
        newtext=text
    
    return html.escape(str(newtext))

def getstudyexpectation(studyno, languagecount, varcount):

    studyexpectation = ''
    studyexpectation += '<StudyExpectation>\n'
    studyexpectation += ' <StudyNumber>' + studyno + '</StudyNumber>\n'
    studyexpectation += ' <NumberOfVariables>' + str(varcount) + '</NumberOfVariables>\n'
    studyexpectation += ' <NumberOfInterviewLanguages>' + str(languagecount) + '</NumberOfInterviewLanguages>\n'
    studyexpectation += '</StudyExpectation>\n'

    return studyexpectation
                        


def getfilefrompath(filewithpath):

    filewithoutpath = ''
    if not filewithpath=='':
        elements = filewithpath.split("\\")
        for element in elements:
            if not element == '':
                filewithoutpath = element
                
    return filewithoutpath
                        
def getpathfromfile(filewithpath):

    filewithoutpath = ''
    pathwithoutfile = ''
    if not filewithpath=='':
        elements = filewithpath.split("\\")
        for element in elements:
            if not element == '':
                filewithoutpath = element
        for element in elements:
            if not element == '' and not element == filewithoutpath:
                pathwithoutfile += element + "\\"
                
    return pathwithoutfile

   
# loop over files in dir OR use single file 
def loopoverfiles(xdir, xfile, efile, report):
    import os
    count = 0
    
    try:
        g.loopstatus = "" #start new loopstatus
        
        if xfile!='': # use of single filename
            if not os.path.isfile(xfile):
                g.loopstatus += 'Error: File not found \n'
                return 
            if xfile.endswith('.SAV') or xfile.endswith('.sav'):
                if not xfile.endswith('.err.xml'):
                    mdir=getpathfromfile(xfile)
                    filename=getfilefrompath(xfile)
                    docheck(mdir, filename, efile, report) 
                    count += 1

        if xdir!='': # use of files in directory
            if not os.path.isdir(xdir):
                g.loopstatus += 'Error: Path not found \n'
                return
            if not g.subdirs and not g.subdirs2:
                for filename in os.listdir(xdir):
                    if filename.endswith('.SAV') or filename.endswith('.sav'):
                        if not filename.endswith('.err.xml'):
                            #print(filename)
                            
                            #automatic adjust language
                            savelanguage = g.language
                            if filename.endswith('_en.SAV') or filename.endswith('_en.sav'):
                                g.language = "en"
                                g.loopstatus += 'Automatically adjusted language to en for the following file: '+filename+'\n'
                            docheck(xdir, filename, efile, report) # use path on filename
                            count += 1
                            #with open(os.path.join('path/to/dir', filename)) as f:
                            #    content = f.read()
                            #break #temp exit after 1 file
                            g.language = savelanguage
            elif g.subdirs or g.subdirs2:
                for subdir, dirs, files in os.walk(xdir):
                    #print('subdir '+subdir)
                    if subdir.endswith('Service') or g.subdirs:
                        #print('subdir '+subdir)
                        for filename in files:
                            if filename.endswith('.SAV') or filename.endswith('.sav'):
                                #print(os.path.join(subdir, filename)+ ' todo')
                                #automatic adjust language
                                savelanguage = g.language
                                if filename.endswith('_en.SAV') or filename.endswith('_en.sav'):
                                    g.language = "en"
                                    g.loopstatus += 'Automatically adjusted language to en for the following file: '+filename+'\n'
                                docheck(subdir, filename, efile, report) # use path on filename
                                count += 1
                                #with open(os.path.join('path/to/dir', filename)) as f:
                                #    content = f.read()
                                #break #temp exit after 1 file
                                g.language = savelanguage

    
    except Exception as Argument:
        g.loopstatus += "ERROR in loopoverfiles: " + xdir + ", " + xfile + "\n   " + str(Argument) + "  \n"
        #print('ERROR in docheck: ' + xfile + ' \n  ' + str(Argument))
    
    finally:
        if count==0:
            g.loopstatus += 'Error: No files found \n'
        else:
            g.loopstatus += str(count) + ' files found \n'
        
        if not g.resultonly:
            print(g.loopstatus)
        g.outstatus += g.loopstatus

def checkifmissing(value, missingrange):
    #check value if it is missing according to missingrange
    # value is code
    # missingrange is meta.missing_ranges[var]
    
    check = False 
    if True: #value==9:
        #print("\n Check " + str(value))
        for miss in missingrange:
            #print(miss)
            
            for ms in miss.items():
                if ms[0]=="hi":
                    high=ms[1]
                if ms[0]=="lo":
                    low=ms[1]
            #print("Range " + str(low) + "-" + str(high))
            #if low.find("datetime")>0:
            if type(low) is datetime.date:
                print("Warning Datetime missing definition") #e.g. ZA5309
                return False
            else:
                if low=="inf":
                    if value<=high:
                        check = True
                elif high=="inf":
                    if value>=low:
                        check = True
                else:
                    if value>=low and value<=high:
                        check = True 
                #print("Range " + str(low) + "-" + str(high) + " : " + str(check))
            
    return check
    
    
    

# check
def docheck(xdir, xfile, efile, report):
    
    try:
    #if True:
        #get study no 
        g.studyno = xfile[:6]
        
        ddifile = g.outdir + '\\' + g.studyno + "_" + g.language + "_CMMexport.xml" 
        g.ddixml = ""
        txtfile = g.outdir + '\\' + g.studyno + "_" + g.language + "_text.txt"
        jsonfile = g.outdir + '\\' + g.studyno + "_" + g.language + "_json.json"
        
        
        #init
        g.dditxt = ""
        g.ddijson = ""
        g.ddihead = ""
        g.ddivar = ""
        g.catsch = ""
        g.codlst = ""
        g.varlst = ""
        g.varcount = 0
        
        #read head, var... template files
        with open('example/head.xml') as f:
            g.ddihead = f.read()
        
        with open('example/var.xml') as f:
            g.ddivar = f.read()
        with open('example/codlst.xml') as f:
            g.ddicodlst = f.read()
        with open('example/cod.xml') as f:
            g.ddicod = f.read()
        with open('example/catsch.xml') as f:
            g.ddicatsch = f.read()
        with open('example/cat.xml') as f:
            g.ddicat = f.read()
            

        
        #insert study no 
        g.ddixml = g.ddihead 
        g.ddixml = g.ddixml.replace("XXXXXX", g.studyno)
        
           
        
        xdirfile = xdir
        if not xdirfile.endswith('\\'): xdirfile += '\\'
        xdirfile += xfile
        
        logfile =  g.logdir + '\\' + g.studyno + "_" + g.language + "_log.txt"
        g.logstatus = "" #start new logstatus
        g.logstatus += "Conversion of: " + xdirfile + " (" + g.language + ") \n"
        
        # read spss file with metadata only 
        #this requires: pip install pyreadstat
        # add support for different encoding:
        try:
                
            tryencoding=g.encoding
            #problem with ZA5676 pyerror: assertion failed 
            #tryencoding="UTF-16" # UTF-16, UTF-16BE, UTF-16LE, ISO-8859-1 to ISO-8859-16, CP1250 to CP1258, CP437, UCS-2, UCS-2LE, UCS-2BE, UCS-4, UCS-4LE, UCS-4BE, ASCII, UTF-7
            #only option is to open file in SPSS and save as a new file... will avoid severe error in pyreadstat 
            #print("try " + xdirfile + "  with " + tryencoding)            
            
            if report:
                flog = open(logfile, "w")
                flog.write("try " + xdirfile + "  with " + tryencoding + "\n")
                flog.close()
            
            df, meta = pyreadstat.read_sav(xdirfile, metadataonly=True, apply_value_formats=True, user_missing=True, encoding=tryencoding)
            #g.logstatus += "Open OK \n"
        except Exception as Argument:
            if type(Argument) == pyreadstat._readstat_parser.ReadstatError or type(Argument) == UnicodeDecodeError:
                
                if str(Argument) == "Unable to convert string to the requested encoding (invalid byte sequence)": #ReadstatError
                    if g.encoding == "UTF-8":
                        #print('Warning: Encoding problem, trying ISO-8859-1.')
                        if report:
                            flog = open(logfile, "a")
                            flog.write("try " + xdirfile + "  with ISO-8859-1" + "\n")
                            flog.close()

                        df, meta = pyreadstat.read_sav(xdirfile, metadataonly=True, apply_value_formats=True, user_missing=True, encoding="ISO-8859-1") 
                        g.logstatus += 'Warning: Encoding problem with UTF-8, used ISO-8859-1. \n'
                        
                        #looks like CP1252 makes less errors than ISO-8859-1
                        #print('Warning: Encoding problem, trying CP1252.')
                        #df, meta = pyreadstat.read_sav(xdirfile, metadataonly=True, apply_value_formats=True, user_missing=True, encoding="CP1252") 
                        #g.logstatus += 'Warning: Encoding problem with UTF-8, used CP1252. \n'
                        
                        #looks like UTF-16 is an option, too
                        #print('Warning: Encoding problem, trying UTF-16.')
                        #df, meta = pyreadstat.read_sav(xdirfile, metadataonly=True, apply_value_formats=True, user_missing=True, encoding="UTF-16") 
                        #g.logstatus += 'Warning: Encoding problem with UTF-8, used UTF-16. \n'
                    elif g.encoding == "ISO-8859-1":
                        #print('Warning: Encoding problem, trying UTF-8.')
                        if report:
                            flog = open(logfile, "a")
                            flog.write("try " + xdirfile + "  with UTF-8" + "\n")
                            flog.close()

                        df, meta = pyreadstat.read_sav(xdirfile, metadataonly=True, apply_value_formats=True, user_missing=True, encoding="UTF-8")
                        g.logstatus += 'Warning: Encoding problem with ISO-8859-1, used UTF-8. \n'

                    else:
                        g.logstatus += "ERROR in docheck: " + xfile + "\n   " + str(Argument) + " (Encoding problem) \n"
                elif str(Argument)[0:31] == "'utf-8' codec can't decode byte": #UnicodeDecodeError
                    if g.encoding == "UTF-8":
                        #looks like UTF-16 is an option, too
                        #problem with ZA5647 0xf6 is ö - nothing seems to work:
                        tryencoding="UTF-7" # UTF-16, UTF-16BE, UTF-16LE, ISO-8859-1 to ISO-8859-16, CP1250 to CP1258, CP437, UCS-2, UCS-2LE, UCS-2BE, UCS-4, UCS-4LE, UCS-4BE, ASCII, UTF-7
                        g.logstatus +=('Warning: Encoding problem, trying ' + tryencoding + '. \n')
                        if report:
                            flog = open(logfile, "a")
                            flog.write("try " + xdirfile + "  with " + tryencoding + "\n")
                            flog.close()
                        
                        df, meta = pyreadstat.read_sav(xdirfile, metadataonly=True, apply_value_formats=True, user_missing=True, encoding=tryencoding) 
                        g.logstatus += 'Warning: Encoding problem with UTF-8, used '+ tryencoding + '. \n'
                else:
                    g.logstatus += "ERROR in docheck: " + xfile + "\n   " + str(Argument) + "  \n"
            else:
                g.logstatus += "ERROR in docheck: " + xfile + "\n   " + str(Argument) + " " + str(type(Argument)) + " \n"
                
        
        #print(type(df))
        #print(type(meta))
        #print(meta.column_names_to_labels)
        #print(meta.missing_ranges)
        for var, varlabel in meta.column_names_to_labels.items():
            g.dditxt += var + " " + str(varlabel) + "\n"
            
            #todo prüfen: Variablen immer mit Kleinbuchstaben? - nein, ist korrekt, 3450 hat Großbuchstaben, 1053 hat Kleinbuchstaben
            
            #json zusammenbauen
            if g.ddijson!='': 
                g.ddijson +=',\n' #var separator
            g.ddijson += '    "'+var+'": {\n'
            g.ddijson += '      "label": ["'+str(varlabel)+'"],\n'
            jsonvaluelist=''
           
            ddivar = g.ddivar
            varID = g.studyno + '_Var' + var #VarID
            varID = varID.replace(".", "*") # . ersetzen durch * nur in ID 
            ddivar = ddivar.replace("__VarID__", varID) 
            
            ddivar = ddivar.replace("__FileName__", xfile) #new 1.6 include MetadataFromDataset
            
            varID = g.studyno + '_' + var + "_CodLis" #VarCodLisID
            varID = varID.replace(".", "*") 
            ddivar = ddivar.replace("__VarCodLisID__", varID) 
            
            ddivar = ddivar.replace("__VarName__", var)
            ddivar = ddivar.replace("__VarLabel__", removeIllegalChars(varlabel)) #not html.escape(str(varlabel))
            ddivar = ddivar.replace("__lang__", g.language)
            g.varlst += ddivar
            g.varcount += 1
            
            ddicodlst = g.ddicodlst
            ddicodlst = ddicodlst.replace("__VarCodLisID__", varID) 
            
            varID = g.studyno + '_' + var + "_CatSch" #VarCatSchID
            varID = varID.replace(".", "*") 
            ddicodlst = ddicodlst.replace("__VarCatSchID__", varID) 
            
            ddicatsch = g.ddicatsch
            ddicatsch = ddicatsch.replace("__VarCatSchID__", varID)
            
            #if var in meta.missing_ranges:
            #    if var=="V818":
            #        #print(meta.missing_ranges[var])
            #        x = checkifmissing(17, meta.missing_ranges[var])
                
            
            
            ddicodes = ""
            ddicats = ""
            if var in meta.variable_value_labels:
                if True: #var=="v176":
                    #print(var)
                    #print(meta.variable_value_labels[var])
                    for code, vallab in meta.variable_value_labels[var].items():
                        #check if code is missing
                        if var in meta.missing_ranges:
                            if True: #var=="V816":
                                if checkifmissing(code, meta.missing_ranges[var]):
                                    #print(meta.missing_ranges[var])
                                    codMiss = "true" # use text with small caps
                                else:
                                    codMiss = "false" # use text with small caps
                        else:
                            codMiss = "false" # use text with small caps
                        
                        #todo prüfen: Values immer float 1.0 mit Dezimalstellen??
                        # ist offenbar standard, daher hier Annahme: immer nur ganzzahlige Value Labels, wenn int(x)=x
                        
                        #support for string codes: 
                        bStrCode=False 
                        if type(code)!=float: #code is not standard float format
                            #print(' - ' + str(type(code)) + str(code) + "=" + str(vallab))
                            val=code 
                            bStrCode=True
                        else:
                            if not math.isnan(code):
                                val = int(code)
                                if code != val:
                                    val=code
                            else:
                                val="NaN"
                                g.logstatus += "ERROR: NaN in code value: " + var + ' in ' + g.studyno + "  \n"
                                break
                        if True: #option to include string codes: if     bSupportStringCodes or not bStrCode
                            if codMiss=="false":
                                g.dditxt += "   "+ str(val) + " - " + str(vallab) + "\n"
                            else:
                                g.dditxt += "   "+ str(val) + " M " + str(vallab) + "\n"
                                                
                            ddicod = g.ddicod #template
                            codID = g.studyno + '_' + var + '_' + str(val) + '_Cod' #CodeID
                            codID = codID.replace(".", "*") 
                            ddicod = ddicod.replace("__CodeID__", codID)
                            codID = g.studyno + '_' + var + '_' + str(val) + '_Cat' #CategoryID
                            codID = codID.replace(".", "*")  
                            ddicod = ddicod.replace("__CatID__", codID)
                            ddicod = ddicod.replace("__CodeValue__", str(val)) #value 
                            ddicodes += ddicod #anhängen
                            
                            ddicat = g.ddicat #template
                            ddicat = ddicat.replace("__CatID__", codID) #CategoryID 
                            ddicat = ddicat.replace("__CatLabel__",  removeIllegalChars(vallab)) #not html.escape(str(vallab)) #Catlabel
                            ddicat = ddicat.replace("__lang__", g.language)
                            ddicat = ddicat.replace("__CategoryMiss__", codMiss) #missing  
                            ddicats += ddicat #anhängen 
                            
                            #json codes und value labels
                            if jsonvaluelist!='': 
                                jsonvaluelist +=',\n'
                            jsonvaluelist += '        "'+str(val)+'": ["'+str(vallab)+'"]'

            #json codelist
            if jsonvaluelist=='': 
                jsonvaluelist ='[]' #empty codelist
            else:
                jsonvaluelist ='{\n'+jsonvaluelist+'\n      }' #codelist wrap
            g.ddijson += '      "values": '+jsonvaluelist+',\n'
            g.ddijson += '      "missing": [],\n'
            g.ddijson += '      "selected": [true]\n'
            g.ddijson += '    }'
                        
            #codes einsetzen  
            ddicodlst = ddicodlst.replace("__Codes__", ddicodes) 
            g.codlst += ddicodlst
            
            #cats einsetzen
            ddicatsch = ddicatsch.replace("__CatList__", ddicats) 
            g.catsch += ddicatsch 
            
            
        #write txt file  
        if g.formattxt:
            f = open(txtfile, "w", encoding="utf-8") # txt also needs utf-8
            f.write(g.dditxt)
            f.close()
            
        #write json file  
        g.ddijson = '{\n  "visible": {\n' + g.ddijson + '\n  }\n}\n'
        if g.formatjson:
            f = open(jsonfile, "w", encoding="utf-8") # json also needs utf-8
            f.write(g.ddijson)
            f.close()
            
            
        
        #insert __CategorySchemes__, __CodeLists__, __VariableList__
        g.ddixml = g.ddixml.replace("__CategorySchemes__", g.catsch)
        g.ddixml = g.ddixml.replace("__CodeLists__", g.codlst)
        g.ddixml = g.ddixml.replace("__VariableList__", g.varlst)
            
        #write xml file
        if g.formatxml:
            f = open(ddifile, "w", encoding="utf-8") # xml needs utf-8
            f.write(g.ddixml)
            f.close()
            
        is_valid = True 
            
        #g.logstatus += "\n"
        if is_valid:
            g.logstatus += "Result: Conversion passed \n"
            g.result="OK"
            g.mdexml+=getstudyexpectation(g.studyno, 1, g.varcount)
        else:
            g.logstatus += "Result: Conversion failed \n"
            g.result="Error"
            if not efile== '':
                g.logstatus += "(see errorfile for details)\n"
                
        # write to errorfile 
        if not efile== '':
            if not is_valid:
                f = open(efile, "wt") 
                f.write("error_report")
                f.close()
        # write logfile 
        
        
    except Exception as Argument:
        g.logstatus += "ERROR in docheck: " + xfile + "\n   " + str(Argument) + "  \n"
        #print('ERROR in docheck: ' + xfile + ' \n  ' + str(Argument))
                    
    finally:
        print(g.logstatus)
        g.outstatus += g.logstatus
        
        #append to logfile
        if report:
            flog = open(logfile, "a")
            flog.write(g.logstatus)
            flog.close()
# main 

def main(argv):
   
   now = datetime.datetime.now()
   outdatetime = (now.strftime("%Y-%m-%d %H:%M:%S"))
   
   outputfile = ''
   errorfile = ''
   mdefile= ''
   freshmdefile=False #do not delete mdefile
   g.language = "de" # default language
   
   
   g.formatxml = True # default export format is xml
   g.formattxt = False 
   g.formatjson = False # added with V1.5 
   
   g.subdirs = False 
   g.subdirs2 = False 
   
   g.cutillegalchars = False
   
   g.encoding = "UTF-8"  #default file encoding. may also be ISO-8859-1, CP1252 (ICONV compatible)
   
   xpath = ''
   xfile = ''
   usagenote = 'usage1: convertspssxml.py -p <path> -l <language> \n'
   usagenote += 'usage2: convertspssxml.py -f <file> -l <language> \n'
   usagenote += 'for help use: convertspssxml.py -h \n' 
   
   # check parameters
   try:
      opts, args = getopt.getopt(argv,"hx:f:l:p:o:e:g:m:dsac",["format=", "file=", "path=","language=","outputfile=","errorfile=", "encoding=", "mdefresh", "mdefile=", "sub", "asub", "cut"])
   except getopt.GetoptError:
      print(usagenote)
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print(usagenote)
         print('usage1 with options: convertspssxml.py -p <path> [-l <language> -o <outputfile>] [-e <errorfile>] [-x <format>] [-g <encoding>] [-s] [-a] \n')
         print('usage2 with options: convertspssxml.py -f <file> [-l <language> -o <outputfile>] [-e <errorfile>] [-x <format>] [-g <encoding>] [-s] [-a]\n')
         
         print('Options:')
         print(' -p path (required): path to be checked for SPSS Data Files')
         print(' -f file (required): file to be converted (SPSS Data File)')
         print('\n')
         print(' -l language: language code (default=de)')
         print(' -g encoding: file encoding, from ICONV list (default=UTF-8, may be ISO-8859-1, CP1252)')
         print(' -c or --cut: cut illegal chars, below ascii32')
         
         print(' -o outputfile: path and filename for storing the output (if not default should be used)')
         print(' -e errorfile: path and filename for storing detailed error information (if not default should be used)')
         print(' -x format: export format (default is xml, can also be txt or json, or combination like xmltxt for several)')
         print(' -m mdefile: write/append to metadata-expectations xml file mdefile')
         print(' -d or --mdefresh: create a fresh mdefile/delete existing before writing')
         print(' -s or --sub: use subdirectories (together with -p only)')
         print(' -a or --asub: use subdirectories (together with -p only) and use only those ending with Service')
         print('\n')
         print(' -h : show this help ')
         print('\n')
         print(' This script converts SPSS Data Files in path to DDI XML metadata files. ')
         print(' Use the -p option for path. ')
         sys.exit()
         
      
      elif opt in ("-p", "--path"):
         xpath = arg
      elif opt in ("-f", "--file"):
         xfile = arg
      elif opt in ("-o", "--outputfile"):
         outputfile = arg
      elif opt in ("-e", "--errorfile"):
         errorfile = arg
      elif opt in ("-l", "--language"):
         g.language = arg
      elif opt in ("-g", "--encoding"):
         g.encoding = arg
      elif opt in ("-m", "--mdefile"):
         mdefile = arg      
      elif opt in ("-d", "--mdefresh"):
         freshmdefile = True      
      elif opt in ("-s", "--sub"):
         g.subdirs = True 
      elif opt in ("-a", "--asub"):
         g.subdirs2 = True 
      elif opt in ("-c", "--cut"):
         g.cutillegalchars = True 
      elif opt in ("-x", "--format"):
         g.formatxml = False #reset default 
         if "xml" in arg:
            g.formatxml = True
         if "txt" in arg:
            g.formattxt = True
         if "json" in arg:
            g.formatjson = True 
            
      

   # show header output
   outheader = '#############################################################\n'
   outheader += '### ' + pname + ' \n'
   outheader += '### ' + pdescription + ' \n'
   outheader += '### Version ' + pversion + ' ' + pdate + ' \n'
   outheader += '### Author: ' + pauthor + ' \n'
   outheader += '###\n'
   outheader += '### ' + outdatetime + '\n'
   outheader += '###\n'
   outheader += '#############################################################\n'
   if not g.resultonly:
       print(outheader)
   
   
   #flag for starting 
   runthevalidation=True
   g.outstatus=''
   
   # show parameter messages and run        
   if xpath== '' and xfile=='':
       g.outstatus += 'Error: specify path or file \n'
       runthevalidation=False

   if not runthevalidation:
       print(g.outstatus)
       print(usagenote)
       sys.exit()


   #do this only if at least path is specified and found:
   f_xmlfile = 'convertspssxml' #getfilefrompath(xmlfile)
  
       
   #set standard output 
   if mdefile== '':
       mdefile = "mde-file.xml"

   if outputfile== '':
       outputfile = f_xmlfile + ".out.txt"
   
   if outputfile== '':
       g.outstatus += 'No output file \n'
   else:
       g.outstatus += 'Output file is '+ outputfile + '\n'

   #set standard error file
   if errorfile== '':
       errorfile = f_xmlfile + ".err.xml"
   
   if errorfile== '':
       g.outstatus += 'No errorfile \n'
   else:
       g.outstatus += 'Errorfile is '+ errorfile + '\n'
    
   if g.subdirs:
       g.outstatus += 'Use subdirectories \n'
   if g.subdirs2:
       g.outstatus += 'Use subdirectories (only ending with Service) \n'
       
   if xpath!='':
       g.outstatus += 'Path is '+ xpath + '\n'
   if xfile!='':
       g.outstatus += 'File is '+ xfile + '\n'
   
   g.outstatus += 'Language is '+ g.language + '\n'
   
   if g.cutillegalchars:
       g.outstatus += 'Cut illegal chars is on \n'
   if g.formatxml:
       g.outstatus += 'Export format is XML \n'
   if g.formattxt:
       g.outstatus += 'Export format is TXT \n'
   if g.formatjson:
       g.outstatus += 'Export format is JSON \n'
       
   
   if g.encoding!= 'UTF-8':
       g.outstatus += 'File encoding is ' + g.encoding + ' \n'
       
   g.outstatus += '\n'
      
   g.outdir = ".\\out" #was xpath before
   g.logdir = ".\\log"
   
   
   #delete mdefile if option freshmdefile is set 
   g.mdexml = "" #reset 
   if not mdefile=='' and freshmdefile:
    if os.path.exists(mdefile):
        os.remove(mdefile)
        g.outstatus += 'mdefile removed: ' + mdefile + '\n'
   
   ####################
   #run conversion
   ####################
   g.outstatus += 'Start conversion \n'
   if not g.resultonly:
        print(g.outstatus)
   report = True
   loopoverfiles(xpath, xfile, errorfile, report)
   
   
   # mdefile
   if not mdefile=='':
        g.outstatus += 'write to mdefile: ' + mdefile + '\n'
        if not g.resultonly:
            print('write to mdefile: ' + mdefile)
        f = open(mdefile, "a") #append
        f.write(g.mdexml)
        f.close()
        
        # to integrate mdefile over studies: run collapsemde.py
        
 

   if not g.resultonly:
       #print(g.outstatus)
       if not outputfile== '':
            f = open(outputfile, "w")
            f.write(outheader)
            f.write(g.outstatus)
            f.close()
   #else:
   #    print(g.result)
       
    

   sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])
