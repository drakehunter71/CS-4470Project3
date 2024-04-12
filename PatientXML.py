'''
nice tutorial found here: https://www.datacamp.com/tutorial/python-xml-elementtree
'''

import xml.etree.ElementTree as ET
import os

class Patient(object):
    Patients = list()
    PatientDirectory = dict()

    @classmethod
    def AggregatePatientXmls(cls, xmlFiles) -> list:
        patientRecords = list()
        currentPatientRecords = list()
        currentPatient = os.path.basename(xmlFiles[0]).split("-")[0]

        for file in xmlFiles:
            patient = os.path.basename(file).split("-")[0]

            if patient == currentPatient:
                currentPatientRecords.append(file)
            else:
                patientRecords.append(currentPatientRecords)
                currentPatient = patient
                currentPatientRecords = list()
                currentPatientRecords.append(file)

        patientRecords.append(currentPatientRecords)
        return patientRecords


    def __init__(self, **kwargs):
        self.records = self._buildElementTrees(kwargs["records"])
        self.id = self._getPatientId(kwargs["records"][0])
        Patient.Patients.append(self)
        Patient.PatientDirectory[self.id] = self

    def __repr__(self) -> str:
        return f"Patient: {self.id}\tRecords: {len(self.records)}"

    def _buildElementTrees(self, records) -> list:
        r'''
        returns a list of element trees built from the xml files of each patient record

        '''
        trees = [ET.parse(file) for file in records]
        return trees
    
    def _getPatientId(self, xmlPath) -> int:
        r'''
        split xml file path to retrieve patient id from base path#
        '''
        path = os.path.basename(xmlPath)
        id = int(path.split("-")[0])
        return id
    
    def GetTextFromTags(self) -> list:
        r'''
        returns a list of strings comprised of the texts in each patient record
        '''
        texts = list()
        for record in self.records:
            root = record.getroot()
            text = [string.text for string in root.findall("./TEXT")]
            texts.append(text[0].lower().strip())
        return texts
    
    def GetMedications(self, text = False) -> set:
        r'''
        returns a set of drug types or texts
        text -> drug name
        type -> drug class
        '''
        query = "./TAGS/MEDICATION/MEDICATION" if text else "./TAGS/MEDICATION"
        key = "text" if text else "type1"

        medications = list()
        for record in self.records:
            root = record.getroot()
            hasMeds = "MEDICATION" in [item.tag for item in root.iter()]
            if hasMeds:
                meds = [med.attrib for med in root.findall(query)]
                meds = [med[key].lower() for med in meds]
                medications.extend(meds)       
        return set(medications)
    