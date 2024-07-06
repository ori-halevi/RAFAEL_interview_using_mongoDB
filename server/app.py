""" Python 3.10.11 """
from flask import Flask, request, jsonify
from flask_cors import CORS
import gensim
from db.db_test import get_all_positive_reviews as get_test_positive_reviews, \
    get_all_negative_reviews as get_test_negative_reviews, get_positive_reviews as get_test_positive_reviews, \
    get_negative_reviews as get_test_negative_reviews
from db.db_train import get_all_positive_reviews as get_train_positive_reviews, \
    get_all_negative_reviews as get_train_negative_reviews, get_positive_reviews as get_train_positive_reviews, \
    get_negative_reviews as get_train_negative_reviews

#  Create Flask object
app = Flask(__name__)
CORS(app)  # Allow access from any sources

# Load glove model
try:
    print("Starting loading glove model...")
    glove_model = gensim.models.KeyedVectors.load_word2vec_format('data/glove.6B.300d.txt', binary=False)
    print("Done loading glove model")
except Exception as e:
    print(f"Error loading glove model: {e}")
    glove_model = None


def get_reviews_by_sentiment(similar_words, sentiment):
    if sentiment == 'positive':
        return get_test_positive_reviews(similar_words) + get_train_positive_reviews(similar_words)
    elif sentiment == 'negative':
        return get_test_negative_reviews(similar_words) + get_train_negative_reviews(similar_words)
    else:
        return get_test_positive_reviews(similar_words) + get_train_positive_reviews(similar_words) + \
               get_test_negative_reviews(similar_words) + get_train_negative_reviews(similar_words)

# Create get route for reviews
@app.route('/reviews', methods=['GET'])
def get_reviews():  # Returns JSON
    word_include = request.args.get('word_include', '')
    pos_neg_all = request.args.get('pos_neg_all', 'all')

    query = word_include.lower()
    similar_words = [query]

    if word_include:  # Did the user ask for specific word to be included?

        try:
            similar_words += [word for word, similarity in glove_model.most_similar(word_include, topn=5)]
        except KeyError:
            # If the word is not in the model, a search will run only for the original word
            pass
        except Exception as error:  # Handle any other exceptions, including if glove_model is None
            print(f"An error occurred: {error}")
            # Handle the case where glove_model is None or any other unexpected errors


    positive_reviews, negative_reviews = [], []

    if pos_neg_all == 'positive':
        positive_reviews = get_reviews_by_sentiment(similar_words, 'positive')
    elif pos_neg_all == 'negative':
        negative_reviews = get_reviews_by_sentiment(similar_words, 'negative')
    else:
        positive_reviews = get_reviews_by_sentiment(similar_words, 'positive')
        negative_reviews = get_reviews_by_sentiment(similar_words, 'negative')

    # Returns result to the client in json form
    return jsonify({
        'positive_reviews': positive_reviews,
        'negative_reviews': negative_reviews,
        'similar_words': similar_words
    })

# Handle errors
@app.errorhandler(Exception)
def handle_error(e):
    return jsonify(error=str(e)), 500


if __name__ == '__main__':
    app.run(debug=False)
