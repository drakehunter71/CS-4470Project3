import re
import os
from xml.etree import ElementTree as ET


def extract_social_history(xml_file):
    with open(xml_file, 'r') as f:
        xml_content = f.read()

    # Attempt to find the "Social history" section using regex
    social_history_pattern = re.compile(
        r'(?i)SOCIAL HISTORY (?:AND FAMILY HISTORY)?\s*:(.*?)(REVIEW|PHYSICAL|LABORATORY|THERAPY|CONSULTATIONS|FINAL|DISPOSITION)', re.DOTALL)
    match = social_history_pattern.search(xml_content)

    # Check if we got it
    if match:
        social_history = match.group(1).strip()
        return social_history

    # Otherwise, because the XML format is fairly unstructured sometimes when it comes to how social history is represented, we try this regex
    else:
        social_history_pattern = re.compile(
            r'(?i)SOCIAL HISTORY\s*:(.*?)(?=FAMILY HISTORY|REVIEW|PHYSICAL|LABORATORY|THERAPY|CONSULTATIONS|FINAL|DISPOSITION)', re.DOTALL)
        match = social_history_pattern.search(xml_content)

        # Check if we got it this time
        if match:
            social_history = match.group(1).strip()
            return social_history

        # If we still didn't find it, womp womp
        else:
            return None

# process all xml files in data directory
def process_xml_files(directory):
    social_histories = []
    total_files = 0
    files_with_social_history = 0

    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            total_files += 1
            xml_file = os.path.join(directory, filename)
            social_history = extract_social_history(xml_file)
            if social_history:
                files_with_social_history += 1
                social_histories.append((filename, social_history))

    return social_histories, total_files, files_with_social_history


# project3_data i called data
directory = './data/'
social_histories, total_files, files_with_social_history = process_xml_files(
    directory)

# Print results
print("Total XML files:", total_files)
print("XML files with social history:", files_with_social_history)
print("List of social histories found:")
for filename, social_history in social_histories:
    print(filename + ":", social_history)
