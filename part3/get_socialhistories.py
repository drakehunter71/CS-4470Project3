import os
import re
import xml.etree.ElementTree as ET

def extract_social_history(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    text_element = root.find("TEXT")

    social_history_names = ["sohx", "social history", "shx", "sh:"]
    if any(name in text_element.text.lower() for name in social_history_names):
        return True
    else:
        return False

def get_socialhistories(directory):
    social_histories = []
    no_social_histories = []
    total_files = 0
    count_files_with_social_history = 0

    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            total_files += 1
            xml_file = os.path.join(directory, filename)
            social_history = extract_social_history(xml_file)
            if social_history:
                count_files_with_social_history += 1
                social_histories.append(filename)
            else:
                no_social_histories.append(filename)

    return social_histories, no_social_histories,total_files, count_files_with_social_history

directory = '../data/'
social_histories, no_social_histories, total_files, count_files_with_social_history = get_socialhistories(
    directory)

# Print results
print('Total files:', total_files)
print('Count files with social history:', count_files_with_social_history)
print('Files with social history:', social_histories)
# sort no_social_histories and print them
# no_social_histories.sort()
# print('Files without social history:', no_social_histories)