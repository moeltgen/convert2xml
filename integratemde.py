#!/usr/bin/python
# -*- coding: cp1252 -*-

# settings for integrating 2 mde files
#
# Version V1.0
# W. Zenk-Möltgen, 2022-04-11
#

import os.path
from plumbum import local
from lxml import etree, isoschematron
import xml.etree.ElementTree as ET


def integrate():

    #output 
    printresult = True
    outresult = True
    
    #mde files
    xfile = "mde-file.xml"
    x2file = "md-expectation.xml"

    msg = 'Integrate file: ' + xfile + '\n'
    msg += 'Integrate file: ' + x2file
    print(msg)        
    
    #load the file and create root node 
    #with open(os.path.join('path/to/dir', filename)) as f:
    with open(local.path(xfile)) as f:
        content = f.read()

    head = '<MetadataExpectation \n xmlns="gesis:metadata-expectation:v1" \n'
    head += ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \n'
    head += ' xsi:schemaLocation="gesis:metadata-expectation:v1 metadata-expectation-v1.xsd"> \n'
    tail = '</MetadataExpectation>'
    
    mdexml = head + content + tail 
        
    
    stu = {} # empty dict for studies with langs
    stv = {} # empty dict for studies with vars
    
    #parse the xml
    #xml_doc = etree.fromstring(mdexml)
    root = etree.fromstring(mdexml) 
    xml_doc = etree.ElementTree(root)
    if root is not None:
        
        ##create prefixmap for lxml access to elements: ddiprofile is always this namespace
        prefixmap = {}
        prefixmap["g"]="gesis:metadata-expectation:v1"
        
        xpath="//g:StudyExpectation"
        elmnt = xml_doc.xpath(xpath, namespaces=prefixmap)
                
        if elmnt is not False and elmnt is not None:
            for e in elmnt: # each StudyExpectation 
                studyno = ''
                studyvars = 0
                studylangs = 0
                studies = e.findall(".//g:StudyNumber", namespaces=prefixmap) 
                for study in studies:
                    #print(study.text)
                    studyno = study.text
                    break
                variables = e.findall(".//g:NumberOfVariables", namespaces=prefixmap) 
                for variable in variables:
                    #print(variable.text)
                    studyvars = int(variable.text)
                    break
                languages = e.findall(".//g:NumberOfInterviewLanguages", namespaces=prefixmap) 
                for language in languages:
                    #print(language.text)
                    studylangs = int(language.text)
                    break
                
                if not studyno=='' and studyvars>0 and studylangs>0:
                    #check if exists
                    if stu.get(studyno):
                        #increase langs
                        stu[studyno]=stu[studyno]+studylangs
                        if not stv[studyno]==studyvars:
                            print('Warning: NumberOfVariables do not match for ' + studyno)
                        #else:
                        #    print('OK: NumberOfVariables do match for ' + studyno)
                    else:
                        #add new
                        stu[studyno]=studylangs
                        stv[studyno]=studyvars

    #load the 2nd file and create root node: This is the DSDM-expectation file with root and timestamp 
    #with open(local.path(x2file)) as f2:
    #    content2 = f2.read()
        
    #parse the xml
    #load file directly
    
    xml_doc = etree.parse(x2file) 
    if root is not None:
        
        ##create prefixmap for lxml access to elements: ddiprofile is always this namespace
        prefixmap = {}
        prefixmap["g"]="gesis:metadata-expectation:v1"
        
        xpath="//g:StudyExpectation"
        elmnt = xml_doc.xpath(xpath, namespaces=prefixmap)
                
        if elmnt is not False and elmnt is not None:
            for e in elmnt: # each StudyExpectation 
                studyno = ''
                studyvars = 0
                studylangs = 0
                studies = e.findall(".//g:StudyNumber", namespaces=prefixmap) 
                for study in studies:
                    #print(study.text)
                    studyno = study.text
                    break
                variables = e.findall(".//g:NumberOfVariables", namespaces=prefixmap) 
                for variable in variables:
                    #print(variable.text)
                    studyvars = int(variable.text)
                    break
                languages = e.findall(".//g:NumberOfInterviewLanguages", namespaces=prefixmap) 
                for language in languages:
                    #print(language.text)
                    studylangs = int(language.text)
                    break
                
                if not studyno=='' and studyvars>0 and studylangs>0:
                    #check if exists: This is by definition not possible, either DSDM or SPSS output should exist
                    if stu.get(studyno):
                        print('Warning: DSDM export found for ' + studyno + ', but SPSS export already there!')
                        #increase langs
                        stu[studyno]=stu[studyno]+studylangs
                        if not stv[studyno]==studyvars:
                            print('Warning: NumberOfVariables do not match for ' + studyno)
                        #else:
                        #    print('OK: NumberOfVariables do match for ' + studyno)
                    else:
                        #add new
                        stu[studyno]=studylangs
                        stv[studyno]=studyvars
        
        # get timestamp from DSDM export file 
        timestamp=''
        xpath="//g:Timestamp"
        elmnt = xml_doc.xpath(xpath, namespaces=prefixmap)
        if elmnt is not False and elmnt is not None:
            for e in elmnt: # each  
                timestamp = '<Timestamp>' + e.text + '</Timestamp>\n'
        
        # get RepositoryExpectation from DSDM export file 
        repoexp = '<RepositoryExpectation>\n'
        xpath="//g:RepositoryExpectation"
        elmnt = xml_doc.xpath(xpath, namespaces=prefixmap)
        if elmnt is not False and elmnt is not None:
            for e in elmnt: # each 
                # NumberOfStudies
                nstud = e.findall(".//g:NumberOfStudies", namespaces=prefixmap) 
                for n in nstud:
                    repoexp += ' <NumberOfStudies>' + n.text + '</NumberOfStudies>\n'
                # NumberOfLanguages
                nstud = e.findall(".//g:NumberOfLanguages", namespaces=prefixmap) 
                for n in nstud:
                    repoexp += ' <NumberOfLanguages>' + n.text + '</NumberOfLanguages>\n'
        repoexp += '</RepositoryExpectation>\n'
                       
        
    if printresult:                
        for key, value in stu.items():
            print(f"{key}: {value} langs - {stv[key]} vars ")
    
    if outresult: 
        newmdexml = '<?xml version="1.0" encoding="utf-8"?>\n'
        newmdexml += head
        newmdexml += timestamp
        newmdexml += repoexp
        for key, value in stu.items():
            #print(f"{key}: {value} langs - {stv[key]} vars ")
            newmdexml += "<StudyExpectation>\n"
            newmdexml += " <StudyNumber>" + str(key) + "</StudyNumber>\n"
            newmdexml += " <NumberOfVariables>" + str(stv[key]) + "</NumberOfVariables>\n"
            newmdexml += " <NumberOfInterviewLanguages>" + str(value) + "</NumberOfInterviewLanguages>\n"
            newmdexml += "</StudyExpectation>\n"
        newmdexml += tail 
    
        #write integrated file 
        #mymdexml = etree.tostring(xml_doc).decode('utf-8')
        #yfile = "md-expectation-integrated.xml"
        yfile = "md-expectation-integrated.xml"
        f = open(yfile, "w")
        f.write(newmdexml)
        f.close()
        
        msg = 'Written to file: ' + yfile
        print(msg)        
    
    return 
    

#call it
integrate()
