#!/usr/bin/python
# -*- coding: cp1252 -*-

# settings for collapsing mde file
#
# Version V1.1
# W. Zenk-Möltgen, 2022-04-19
#

import os.path
from plumbum import local
from lxml import etree, isoschematron
import xml.etree.ElementTree as ET


def collapse():

    #output 
    printresult = False
    outresult = True
    
    #mde file
    xfile = "mde-file.xml"

    msg = 'Collapse file: ' + xfile
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
    
    #print('mdexml:\n')
    #print(mdexml)
    #print('\n')
    
    
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
                
    if printresult:                
        for key, value in stu.items():
            print(f"{key}: {value} langs - {stv[key]} vars ")
    
    if outresult: 
        newmdexml = head
        for key, value in stu.items():
            #print(f"{key}: {value} langs - {stv[key]} vars ")
            newmdexml += "<StudyExpectation>\n"
            newmdexml += " <StudyNumber>" + str(key) + "</StudyNumber>\n"
            newmdexml += " <NumberOfVariables>" + str(stv[key]) + "</NumberOfVariables>\n"
            newmdexml += " <NumberOfInterviewLanguages>" + str(value) + "</NumberOfInterviewLanguages>\n"
            newmdexml += "</StudyExpectation>\n"
        newmdexml += tail 
    
        #write collapsed file 
        #mymdexml = etree.tostring(xml_doc).decode('utf-8')
        #yfile = "md-expectation-collapsed.xml"
        yfile = "md-expectation.xml"
        f = open(yfile, "w")
        f.write(newmdexml)
        f.close()
        
        msg = 'Written to file: ' + yfile
        print(msg)        
    
    return 
    

#call it
collapse()
