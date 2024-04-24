import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# Read the data
data = pd.read_csv('patient_sh.csv', sep='|')

# Use the recommended method to replace NaN values
data['sh'] = data['sh'].fillna('')

# Extract the 'sh' column
documents = data['sh']

# Convert text data into a matrix of token counts
vectorizer = CountVectorizer(stop_words='english')
X = vectorizer.fit_transform(documents)

# Define the number of topics
num_topics = 5

# Apply LDA
lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
lda.fit(X)

# Function to display top n words for each topic


def display_topics(model, feature_names, num_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic %d:" % (topic_idx))
        print(" ".join([feature_names[i]
              for i in topic.argsort()[:-num_top_words - 1:-1]]))


# Display the topics
num_top_words = 5
print("Top words per topic:")
print()
feature_names = vectorizer.get_feature_names_out()
display_topics(lda, feature_names, num_top_words)
