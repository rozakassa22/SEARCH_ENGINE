from flask import Flask, render_template, request
from contextlib import redirect_stdout
import pandas as pd

app = Flask(__name__)

terms = []
keys = []
vec_Dic = {}
dicti = {}
dummy_List = []


def filter(documents, rows, cols):
    for i in range(rows):
        for j in range(cols):
            if j == 0:
                keys.append(documents.loc[i].iat[j])
            else:
                dummy_List.append(documents.loc[i].iat[j])
                if documents.loc[i].iat[j] not in terms:
                    terms.append(documents.loc[i].iat[j])

        copy = dummy_List.copy()
        dicti.update({documents.loc[i].iat[0]: copy})
        dummy_List.clear()


def bool_Representation(dicti, rows, cols):
    terms.sort()

    for i in dicti:
        for j in terms:
            if j in dicti[i]:
                dummy_List.append(1)
            else:
                dummy_List.append(0)

        copy = dummy_List.copy()
        vec_Dic.update({i: copy})
        dummy_List.clear()


def query_Vector(query):
    qvect = []

    for i in terms:
        if i in query:
            qvect.append(1)
        else:
            qvect.append(0)

    return qvect


def prediction(q_Vect):
    dictionary = {}
    listi = []
    count = 0

    term_Len = len(terms)

    for i in vec_Dic:
        for t in range(term_Len):
            if q_Vect[t] == vec_Dic[i][t]:
                count += 1

        dictionary.update({i: count})
        count = 0

    for i in dictionary:
        listi.append(dictionary[i])

    listi = sorted(listi, reverse=True)

    ans = ' '
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            print("ranking of the documents")

            for count, i in enumerate(listi):
                key = check(dictionary, i)
                if count == 0:
                    ans = key

                print(key, "rank is", count+1)

                dictionary.pop(key)

            print(ans, "is the most relevant document for the given query")

    return ans


def check(dictionary, val):
    for key, value in dictionary.items():
        if val == value:
            return key


def process_query(query):
    documents = pd.read_csv('documents.txt')
    rows = len(documents)
    cols = len(documents.columns)
    filter(documents, rows, cols)
    bool_Representation(dicti, rows, cols)
    query = query.split(' ')
    q_Vect = query_Vector(query)
    result = prediction(q_Vect)
    return result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    result = process_query(query)
    return render_template('result.html', result=result)


if __name__ == '__main__':
    app.run()