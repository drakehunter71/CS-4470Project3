import xml.etree.ElementTree as ET

# Load the XML file
tree = ET.parse("../data/100-02.xml")
root = tree.getroot()

# Find the TEXT element
text_element = root.find("TEXT")

# Check if the text contains "social history"
if "social history" in text_element.text.lower():
    print("The string 'social history' exists in the text.")
else:
    print("The string 'social history' does not exist in the text.")
