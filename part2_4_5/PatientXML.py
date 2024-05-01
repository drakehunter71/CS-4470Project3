
'''
nice tutorial found here: https://www.datacamp.com/tutorial/python-xml-elementtree  
'''
#%%
import xml.etree.ElementTree as ET
import pandas as pd
import os
from fuzzywuzzy import fuzz
import re

class Patient(object):
    Patients = list()
    PatientDirectory = dict()
    DrugMap = dict()
    GenericMap = dict()
    OrganMap = dict()
    FuzzyMatches = set()

    PatientDrugs = {"patient":list(),
                    "drug":list(),
                    "category":list(),
                    "organ":list()}
    
    

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
        fuzzyDataframe = {"matchType":list(),
                              "oldValue":list(),
                              "newValue":list(),
                              "score":list()}
        
        for item in cls.FuzzyMatches:
            fuzzyDataframe["matchType"].append(item[0])
            fuzzyDataframe["oldValue"].append(item[1])
            fuzzyDataframe["newValue"].append(item[2])
            fuzzyDataframe["score"].append(item[3])

        return pd.DataFrame.from_dict(cls.FuzzyMatches)

    def __init__(self, **kwargs):
        self.records = self._buildElementTrees(kwargs["records"])
        self.id = self._getPatientId(kwargs["records"][0])
        self.drugsUsed = self._getMedicationsMapped()
        self.textDrugs = self._getTextMapped()
        self.allDrugs = self.drugsUsed | self.textDrugs
        self._updatePatientDrugs()
        Patient.Patients.append(self)
        Patient.PatientDirectory[self.id] = self
        
    def __repr__(self) -> str:
        return f"Patient: {self.id}\tRecords: {len(self.records)}\tNo.Drugs: {len(self.allDrugs)}"

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
        elif drug in ["statins", "statin", "ace", "ssi", "acei"]:
            return (drug, False)
        else:
            #store all candidate matches and return best match if there is at least one match
            matches = list()
            for k in map.keys():
                ratio = fuzz.ratio(k, drug)
                if (len(drug) >= 4 and ratio >= 90) or (len(drug) == 3 and ratio == 100):
                    matches.append(("full", drug, k, ratio))
            if len(matches) > 0:
                drugMatch = sorted(matches, key=lambda x: x[3], reverse=True)[0]
                self._updateFuzzyMatches(*drugMatch)
                return (drugMatch[2], True)
            
            partialMatches = list()
            for k in map.keys():
                if "/" not in k:
                    pRatio = fuzz.partial_ratio(k, drug)
                    if (len(drug) >= 4 and pRatio >= 90) or (len(drug) == 3 and pRatio == 100):
                        partialMatches.append(("partial", drug, k, pRatio))
            if len(partialMatches) > 0:
                drugMatch = sorted(partialMatches, key=lambda x: x[3], reverse=True)[0]
                self._updateFuzzyMatches(*drugMatch) 
                return (drugMatch[2], True)
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
        drugs = self.drugsUsed | self.textDrugs
        for drug in drugs:
            Patient.PatientDrugs["patient"].append(self.id)
            Patient.PatientDrugs["drug"].append(drug)
            Patient.PatientDrugs["category"].append(Patient.DrugMap[drug])
            Patient.PatientDrugs["organ"].append(Patient.OrganMap[Patient.DrugMap[drug]])
         
    def _updateFuzzyMatches(self, type, old, new, score):
        Patient.FuzzyMatches.add((type, old, new, score))

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
                    subMeds = [re.sub(r'\d|\.|,|(|)', '', sub) for sub in subMeds]
                    for drug in subMeds:
                        searchResult = self._findDrugMatch(drug, drugMap)
                        if searchResult[1]:
                            medications.append(searchResult[0])
        results = set([self._getBrandToGeneric(drug) for drug in medications]) 
        return self._splitCompoundDrugs(results)
    
    def _getTextMapped(self):
        r'''
        returns a set of drug texts
        text -> drug name
        '''
        query = "./TEXT"
        drugMap = Patient.DrugMap
        medications = list()

        for record in self.records:
            root = record.getroot()
            text = root.findall(query)
            for t in text:
                for drug in drugMap:
                    if drug in t.text.lower() and len(drug) > 4:
                        medications.append(drug)

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
# %% drug categories
import json

Patient.DrugMap = json.load( open( r"C:\Users\scots\OneDrive\Desktop\CS4470\project3\CS-4470Project3\part2_4_5\drugNames.json" ) )
Patient.GenericMap = json.load( open( r"C:\Users\scots\OneDrive\Desktop\CS4470\project3\CS-4470Project3\part2_4_5\genericToBrandName.json" ) )
Patient.OrganMap = json.load( open( r"C:\Users\scots\OneDrive\Desktop\CS4470\project3\CS-4470Project3\part2_4_5\organMap.json" ) )

r'''
json.dump(genericMap, open(r"C:\Users\scots\OneDrive\Desktop\CS4470\project3\genericToBrandName.json", "w"), 
         indent=4, separators=(",", ": "), sort_keys=True ) '''


#%%
import os
os.chdir(r"C:\Users\scots\OneDrive\Desktop\CS4470\project3\Project3Data\Project3_data")

test = Patient.AggregatePatientXmls(os.listdir())
for item in test:
    kwargs = {"records":item}
    patient = Patient(**kwargs)

#%%
Patient.GetFuzzyDataframe().to_csv(
    r"C:\Users\scots\OneDrive\Desktop\CS4470\project3\fuzzy.csv",
    index=False)

Patient.GetDrugDataframe().to_csv(
    r"C:\Users\scots\OneDrive\Desktop\CS4470\project3\drugs.csv",
    index=False)
# %%

results = sorted(Patient.Patients, key=lambda x: len(x.allDrugs), reverse=True)[:15]        
results2 = sorted(Patient.Patients, key=lambda x: len(x.allDrugs))[:15]  

# %%
df = Patient.GetDrugDataframe()
totalUniqueDrugs = len(df["drug"].value_counts())

#%%
import matplotlib.pyplot as plt 
import seaborn as sns

df2 = df.groupby("drug").size().sort_values(ascending=False).index.to_list()[:20]
df2 = df[df["drug"].isin(df2)]

ax = sns.countplot(data=df2, 
              hue="organ", 
              y="drug",
              stat="count", 
              order=df2["drug"].value_counts().index, 
              edgecolor="black")

vals = ax.get_xticks()
ax.set_xticklabels([f'{int(round(x/len(Patient.PatientDirectory.keys()),2)*100)}%' for x in vals])

plt.title(f"Top 20 patient drugs (n = {totalUniqueDrugs} unique drugs)")
plt.ylabel("Drug name")
plt.xlabel(f"Percentage of patients taking drug (n = {len(Patient.PatientDirectory.keys())} unique patients)")
plt.legend(title="Organ system")
plt.show()
# %%
numCategories = df.groupby("category").size().sort_values(ascending=False).index.to_list()
df3 = df[df["category"].isin(numCategories[:20])]

sns.set_style("whitegrid")
ax = sns.countplot(data=df3, 
              hue="organ", 
              y="category",
              stat="percent", 
              order=df3["category"].value_counts().index, 
              edgecolor="black")

vals = ax.get_xticks()
ax.set_xticklabels([f'{int(x)}%' for x in vals])

plt.title("Patient medications by drug category")
plt.ylabel("Drug category")
plt.xlabel(f"Percentage of all drugs (n = {len(df)})")
plt.legend(title="Organ system")
plt.show() 


# %%
