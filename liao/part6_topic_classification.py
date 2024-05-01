import pandas as pd
import os
import random
'''
#Script that copies 150 random files from data into a new folder called random_xml_files

def get_random_xml_files(directory):
    xml_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            xml_files.append(filename)
            
    # randomly select 150 files
    random_files = random.sample(xml_files, 150)
    return random_files

random_files = get_random_xml_files('../data/')
# store copies of the 150 random files in a new folder called 'random_xml_files'
if not os.path.exists('./random_xml_files'):
    os.makedirs('./random_xml_files')

for filename in random_files:
    src = os.path.join('../data/', filename)
    dst = os.path.join('./random_xml_files/', filename)
    os.system(f'cp {src} {dst}')

print('150 random files copied to ./random_xml_files/')
'''

import os
from xml.etree import ElementTree as ET

'''

#Clean the text in the XML files by removing everything outside the <TEXT><![CDATA[ ]]></TEXT> element
def remove_non_text(xml_string):
  """
  This function removes everything from the XML string that's not within the `<TEXT><![CDATA[ ]]></TEXT>` element.

  Args:
      xml_string: The XML string to be processed.

  Returns:
      A new string containing only the content within the `<TEXT><![CDATA[ ]]></TEXT>` element.
  """
  root = ET.fromstring(xml_string)
  text_element = root.find('TEXT')
  if text_element is not None:
    return text_element.text
  else:
    return ""


def process_folder(folder_path):
  """
  This function processes all XML files in a folder and removes everything outside the `<TEXT><![CDATA[ ]]></TEXT>` element, saving the cleaned text to a new .txt file.

  Args:
      folder_path: The path to the folder containing the XML files.
  """
  for filename in os.listdir(folder_path):
    if filename.endswith(".xml"):
      file_path = os.path.join(folder_path, filename)
      with open(file_path, 'r', encoding='utf-8') as f:
        xml_data = f.read()
      cleaned_text = remove_non_text(xml_data)

      # Create the new filename with .txt extension
      # Get filename without extension and add .txt
      txt_filename = os.path.splitext(filename)[0] + ".txt"
      txt_filepath = os.path.join(folder_path, txt_filename)
      
      # get rid of all "\n" characters that are back to back
      
      cleaned_text = cleaned_text.replace("\n\n", "\n")
        

      # Save the cleaned text to the new file
      with open(txt_filepath, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)

    # put this file in a new folder called 'cleaned_text_files'
    if not os.path.exists('./cleaned_text_files'):
      os.makedirs('./cleaned_text_files')
      
    # move the cleaned text file to the new folder
    os.system(f'mv {txt_filepath} ./cleaned_text_files')


folder_path = "./random_xml_files/"
process_folder(folder_path)

'''

df = pd.read_csv('ai_perf.csv', sep="|")

# get all 2nd column values in df whose 2nd column is not "no" and store them in a list
gpt_sh = []
for i in range(len(df)):
    if df.iloc[i, 1] != "no":
        gpt_sh.append(df.iloc[i, 1])

# get all 3rd column values in df whose 3rd column is not "no" and store them in a list
llama_sh = []
for i in range(len(df)):
    if df.iloc[i, 2] != "no":
        llama_sh.append(df.iloc[i, 2])
        
print(llama_sh)