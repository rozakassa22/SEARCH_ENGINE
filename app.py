import os
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import defaultdict
import math
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='.')

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# Directory containing the .txt files
directory = "."

# Initialize tokenizer, stopwords, and stemmer
tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
stopwords = set(stopwords.words('english'))
stemmer = PorterStemmer()

# Initialize inverted index
inverted_index = defaultdict(lambda: defaultdict(int))

# Collect filtered words from all documents
filtered_words = set()

# Iterate over each file in the directory
for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r') as file:
            # Read the contents
            contents = file.read()
            
            # Tokenize the contents
            tokens = tokenizer.tokenize(contents.lower())
            
            # Remove stopwords and stem the tokens
            filtered_tokens = [stemmer.stem(token) for token in tokens if token not in stopwords]
            
            # Add filtered tokens to the set
            filtered_words.update(filtered_tokens)

# Build the inverted index
for word in filtered_words:
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                # Read the contents
                contents = file.read()
                
                # Tokenize the contents
                tokens = tokenizer.tokenize(contents.lower())
                
                # Remove stopwords and stem the tokens
                filtered_tokens = [stemmer.stem(token) for token in tokens if token not in stopwords]
                
                # Count term frequency in the document
                frequency = filtered_tokens.count(word)
                
                if frequency > 0:
                    inverted_index[word][filename] = frequency

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    model = request.form['model']

    # Tokenize, filter, and stem the query
    query_tokens = [stemmer.stem(token) for token in tokenizer.tokenize(query.lower()) if token not in stopwords]

    matched_documents = {}

    if model == 'boolean':
        # Perform boolean search using the query and the inverted index
        for token in query_tokens:
            if token in inverted_index:
                for document, _ in inverted_index[token].items():
                    matched_documents[document] = True

    elif model == 'vector':
        # Calculate document scores using the vector model
        document_scores = defaultdict(float)

        for token in query_tokens:
            if token in inverted_index:
                idf = math.log(len(os.listdir(directory)) / (1 + len(inverted_index[token])))
                for document, frequency in inverted_index[token].items():
                    tf = frequency
                    document_scores[document] += tf * idf

        # Rank the documents based on scores
        sorted_results = sorted(document_scores.items(), key=lambda x: x[1], reverse=True)

        # Prepare the matched documents as a dictionary with document names and contents
        for document, _ in sorted_results:
            matched_documents[document] = True

    # Render the result.html template with the search results
    return render_template('result.html', query=query, matched_documents=matched_documents)

if __name__ == '__main__':
    app.run()