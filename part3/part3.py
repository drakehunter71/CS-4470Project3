import os
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
    patients = set()

    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            total_files += 1
            if filename[:3] not in patients:
                patients.add(filename[:3])

            xml_file = os.path.join(directory, filename)
            social_history = extract_social_history(xml_file)
            if social_history:
                count_files_with_social_history += 1
                social_histories.append(filename)
            else:
                no_social_histories.append(filename)

    return social_histories, no_social_histories, total_files, count_files_with_social_history, len(patients)


def get_patients_with_social_history():
    # each patient is associated by their first three digits in each xml file, what we can do is parse out the first 3 digits of each file name that appears in social_histories and store it in a set
    patients = set()
    for sh in social_histories:
        patients.add(sh[:3])

    patients_no_sh = set()
    for nsh in no_social_histories:
        if nsh[:3] not in patients:
            patients_no_sh.add(nsh[:3])

    return len(patients), len(patients_no_sh)


'''
Runner code
'''
directory = '../data/'
social_histories, no_social_histories, total_files, count_files_with_social_history, total_patients = get_socialhistories(
    directory)

# Print results
print('Total files:', total_files)
print('Count files with social history:', count_files_with_social_history)
social_histories.sort()
print('Files with social history:', social_histories)
num_patients_with_sh, num_patients_no_sh = get_patients_with_social_history()
print('Number of patients with social history:', num_patients_with_sh)
print('Number of patients without social history:', num_patients_no_sh)
print('Total number of patients:', total_patients)


# sort no_social_histories and print them
# no_social_histories.sort()
# print('Files without social history:', no_social_histories)
