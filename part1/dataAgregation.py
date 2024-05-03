import pandas as pd
import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import wordnet

nltk.download("wordnet")
nltk.download("averaged_perceptron_tagger")
from nltk.corpus import stopwords

nltk.download("stopwords")
import seaborn as sns
import matplotlib.pyplot as plt


df = pd.read_csv("Data/nerResults.csv")
df["No Number Entity"] = df["Entity"].str.replace("\d+", "", regex=True)

stop_words = set(stopwords.words("english"))


# Function to remove stop words
def remove_stop_words(text):
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return " ".join(filtered_words)


# Apply the function to the 'Text' column
df["No Stop Words Entity"] = df["No Number Entity"].apply(remove_stop_words)

reset = False
if reset == True:

    # Initialize stemmer and lemmatizer
    stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()

    # Stemming
    stemmed_words = [stemmer.stem(word) for word in df["No Stop Words Entity"]]
    # print("Stemmed words:", stemmed_words)
    df["Stemmed Entity"] = stemmed_words

    # Lemmatization requires POS tags to be more effective
    def get_wordnet_pos(word):
        """Map POS tag to first character lemmatize() accepts"""
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {
            "J": wordnet.ADJ,
            "N": wordnet.NOUN,
            "V": wordnet.VERB,
            "R": wordnet.ADV,
        }

        return tag_dict.get(tag, wordnet.NOUN)

    # Lemmatization
    lemmatized_words = [
        lemmatizer.lemmatize(word, get_wordnet_pos(word))
        for word in df["No Stop Words Entity"]
    ]
    # print("Lemmatized words:", lemmatized_words)
    df["Lemmatized Entity"] = lemmatized_words
    print("Saving columns")
    df.to_csv("Data/nerResults.csv")

classifications = [
    "Gender",
    "Route",
    "Frequency",
    "Direction",
    "RelativeDate",
    "Dosage",
    "Form",
    "Modifier",
    "Drug_Ingredient",
    "External_body_part_or_region",
    "Strength",
    "Admission_Discharge",
    "Employment",
    "Test_Result",
    # "Smoking",
    "Drug_BrandName",
    "Internal_organ_or_component",
    # "Alcohol",
    "Clinical_Dept",
    "Duration",
    "Relationship_Status",
    "RelativeTime",
    "Date",
    "Time",
    "Age",
    "Race_Ethnicity",
    #
    # "Symptom",
    # "Hypertension",
    # "Diabetes",
    # "Hyperlipidemia",
    # "Heart_Disease",
    # "Obesity",
    # "Cerebrovascular_Disease",
    # "Disease_Syndrome_Disorder",
    # "Procedure",
    # "Death_Entity",
    # "Injury_or_Poisoning",
    # "Psychological_Condition",
    # "Medical_Device",
    # "VS_Finding",
]

df = df[~df["Classification"].isin(classifications)]
# df = df[df["Classification"] == "Test"]
# df = df[df["Stemmed Entity"].str.contains("pressure")]
# Convert counts to a DataFrame and reset index for better readability
df = (
    df.groupby(["Lemmatized Entity", "Classification"])
    .size()
    .reset_index(name="Counts")
)
df = df.sort_values(by="Counts", ascending=False)
print(df.columns)
print(df.head(50))
print(df.count())
print(df["Classification"].unique())

# Assuming 'data' is your DataFrame loaded with the top 20 entries
data = df.head(20)  # Adjust this line as per your actual DataFrame

# Create a barplot
sns.set_theme(style="whitegrid")
plt.figure(figsize=(14, 10))  # Adjust the figure size as needed
bar_plot = sns.barplot(
    x="Lemmatized Entity", y="Counts", hue="Classification", data=data
)

# Adding text labels for each bar
for p in bar_plot.patches:
    bar_plot.annotate(
        format(int(p.get_height())),  # Format the count with one decimal point
        (p.get_x() + p.get_width() / 2.0, p.get_height()),  # Position for the text
        ha="center",  # Center horizontally
        va="center",  # Center vertically within the bar
        xytext=(0, 9),  # Position text slightly above the top of the bar
        textcoords="offset points",
    )

# Additional options to fine-tune the plot
bar_plot.set_title("Most Common Lemmatized Words")
bar_plot.set_xlabel("Lemmatized Words")
bar_plot.set_ylabel("Counts")

# Rotate x-axis labels for better visibility
plt.xticks(rotation=45, ha="center")  # Ensure labels are centered relative to the bars

# Show the plot
plt.tight_layout()  # Adjust subplot parameters
plt.show()

exit()
# Set up the plot area
fig, ax = plt.subplots(figsize=(5, 2))  # Adjust the size as needed
ax.axis("tight")
ax.axis("off")  # Hide the axes

# Create the table
df = df.head(50)
the_table = ax.table(cellText=df.values, colLabels=df.columns, loc="center")

# Optionally, you can adjust the properties of the table
the_table.auto_set_font_size(False)
the_table.set_fontsize(12)  # Set the font size
the_table.scale(1.2, 1.2)
plt.show()


# Notebook for data extraction https://colab.research.google.com/drive/17vv6AhwOqzXrR2kAAabpCQ8F2Ek41KYY?usp=sharing
