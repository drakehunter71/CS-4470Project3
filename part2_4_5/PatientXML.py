'''
nice tutorial found here: https://www.datacamp.com/tutorial/python-xml-elementtree
'''

import xml.etree.ElementTree as ET
import pandas as pd
import os
from fuzzywuzzy import fuzz

class Patient(object):
    Patients = list()
    PatientDirectory = dict()
    DrugMap = dict()
    GenericMap = dict()
    OrganMap = dict()

    PatientDrugs = {"patient":list(),
                    "drug":list(),
                    "category":list(),
                    "organ":list()}
    
    FuzzyMatches = {"matchType":list(),
                    "oldValue":list(),
                    "newValue":list(),
                    "score":list()}

    @classmethod
    def AggregatePatientXmls(cls, xmlFiles) -> list:
        r'''
        Makes a list of xmls for each patient id# and returns a list of those list for downstream object construction
        '''
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

    @classmethod
    def GetDrugDataframe(cls) -> pd.DataFrame:
        return pd.DataFrame.from_dict(cls.PatientDrugs)
    
    @classmethod
    def GetFuzzyDataframe(cls) -> pd.DataFrame:
        return pd.DataFrame.from_dict(cls.FuzzyMatches)

    def __init__(self, **kwargs):
        self.records = self._buildElementTrees(kwargs["records"])
        self.id = self._getPatientId(kwargs["records"][0])
        self.drugsUsed = self._getMedicationsMapped()
        self._updatePatientDrugs()
        Patient.Patients.append(self)
        Patient.PatientDirectory[self.id] = self
        
    def __repr__(self) -> str:
        return f"Patient: {self.id}\tRecords: {len(self.records)}\tNo.Drugs: {len(self.drugsUsed)}"

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
    
    def _findDrugMatch(self, drug, map) -> tuple:
        r'''
        Maps drug names to keys in a predefined drug-category mapping. First, a direct match to a dictionary is
        assessed. If no match, a partial or fuzzy match is checked with the key directly being returned in place of the 
        drug. If there is still no match, the drug is returned with a False boolean member.
        '''
        if drug in map.keys():
            return (drug, True)
        else:
            for k in map.keys():
                ratio = fuzz.ratio(k, drug)
                if (len(drug) >= 5 and ratio >= 80) or (len(drug) == 3 and ratio == 100) or (len(drug) == 4 and ratio >= 90):
                    self._updateFuzzyMatches("full", drug, k, ratio)
                    return (k, True)
            for k in map.keys():
                if "/" not in k:
                    pRatio = fuzz.partial_ratio(k, drug)
                    if (len(drug) >= 5 and pRatio >= 80) or (len(drug) == 3 and pRatio == 100) or (len(drug) == 4 and pRatio >= 90):
                        self._updateFuzzyMatches("partial", drug, k, pRatio)    
                        return (k, True)
        return (drug, False)
    
    def _getBrandToGeneric(self, drug):
        r'''
        returns a generic drug if there is a mapping, otherwise returns input
        '''
        genericMap = Patient.GenericMap
        try:
            return genericMap[drug]
        except:
            return drug
        
    def _splitCompoundDrugs(self, drugs) -> set:
        r'''
        Split compound drugs into two separate drugs. Returns the update set minus the compound
        glyburide/metformin would be returned as glyburide and metformin separately.
        '''
        newDrugs = set()
        compounds = set()
        for drug in drugs:
            if "/" in drug:
                newDrugs.update(drug.split("/"))
                compounds.add(drug)
        return (newDrugs | drugs) - compounds
        
    def _updatePatientDrugs(self):  
        for drug in self.drugsUsed:
            Patient.PatientDrugs["patient"].append(self.id)
            Patient.PatientDrugs["drug"].append(drug)
            Patient.PatientDrugs["category"].append(Patient.DrugMap[drug])
            Patient.PatientDrugs["organ"].append(Patient.OrganMap[Patient.DrugMap[drug]])
         
    def _updateFuzzyMatches(self, type, old, new, score):
        Patient.FuzzyMatches["matchType"].append(type)
        Patient.FuzzyMatches["oldValue"].append(old)
        Patient.FuzzyMatches["newValue"].append(new)
        Patient.FuzzyMatches["score"].append(score)
        
    def _getMedicationsMapped(self):
        r'''
        returns a set of drug texts
        text -> drug name
        '''
        query = "./TAGS/MEDICATION"
        key = "text"
        drugMap = Patient.DrugMap
        medications = list()

        for record in self.records:
            root = record.getroot()
            #check for medication tags in the record
            hasMeds = "MEDICATION" in [item.tag for item in root.iter()]
            if hasMeds:
                meds = root.findall(query)
                #iterate through the children of the medication tags and break after a mapping is successful
                for med in meds:
                    subMeds = [sub.attrib for sub in med]
                    subMeds = [sub[key].lower().strip() for sub in subMeds]
                    for drug in subMeds:
                        searchResult = self._findDrugMatch(drug, drugMap)
                        if searchResult[1]:
                            medications.append(searchResult[0])
        results = set([self._getBrandToGeneric(drug) for drug in medications]) 
        return self._splitCompoundDrugs(results)
     
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