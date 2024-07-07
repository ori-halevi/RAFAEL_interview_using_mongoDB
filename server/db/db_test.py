from pymongo import MongoClient
import re

client = MongoClient('mongodb://localhost:27017/')
db = client.amazon_review
test_collection = db.test


def get_all_positive_reviews():
    reviews = test_collection.find({"row.label": 1})
    return format_reviews(reviews)


def get_all_negative_reviews():
    reviews = test_collection.find({"row.label": 0})
    return format_reviews(reviews)


def get_all_reviews():
    reviews = test_collection.find()
    return format_reviews(reviews)


# Returns reviews containing specific words. # ~ O(N) ~
def get_pos_or_neg_reviews(words_list: list, binary_pos_or_neg: int) -> list:
    """
    Retrieve reviews based on specified words and sentiment (positive or negative).

    Args:
        words_list (list): List of words to search for in reviews.
        binary_pos_or_neg (int): Binary indicator for sentiment (1 for positive, 0 for negative).

    Returns:
        list: List of formatted reviews matching the criteria.

    Example:
        get_pos_or_neg_reviews(['good', 'great'], 1)  # Retrieves positive reviews containing 'good' or 'great'.
    """
    # Create regular queries (regex) for each word in the list. ~ O(N) ~
    regex_queries = [{"row.title": {"$regex": r"\b" + re.escape(w) + r"\b", "$options": "i"}} for w in words_list] + \
                    [{"row.content": {"$regex": r"\b" + re.escape(w) + r"\b", "$options": "i"}} for w in words_list]
    # Creating the final query with all conditions
    query = {
        "row.label": binary_pos_or_neg,
        "$or": regex_queries
    }
    reviews = test_collection.find(query)  # ~ O(N) ~
    return format_reviews(reviews)


def get_positive_reviews(words_list: list) -> list:
    if words_list:  # Did the user ask for specific word to be included?
        return get_pos_or_neg_reviews(words_list, 1)
    return get_all_positive_reviews()


def get_negative_reviews(words_list: list) -> list:
    if words_list:  # Did the user ask for specific word to be included?
        return get_pos_or_neg_reviews(words_list, 0)
    return get_all_negative_reviews()


def format_reviews(reviews):  # ~ O(N) ~
    """
    Format MongoDB query results into a list of dictionaries with specific fields.

    Args:
        reviews (pymongo.cursor.Cursor): Cursor object containing MongoDB query results.

    Returns:
        list: List of dictionaries, each representing a formatted review with 'label', 'title', and 'content' fields.

    Example:
        format_reviews(reviews)  # Returns a list of reviews formatted with 'label', 'title', and 'content':
        [{'label': 1,'title': 'some title','content': 'some long content'}]
    """
    formatted_reviews = []
    for review in reviews:
        formatted_reviews.append({
            "label": "positive" if review['row']['label'] == 1 else "negative",
            "title": review['row']['title'],
            "content": review['row']['content']
        })
    return formatted_reviews
