// Event listener for the search button
document.getElementById('search-button').addEventListener('click', function() {
    const wordInclude = document.getElementById('search-word').value;
    const sentimentFilter = document.getElementById('sentiment-filter').value;
    fetchReviews(wordInclude, sentimentFilter);
});

// Event listener for the export button
document.getElementById('export-button').addEventListener('click', function() {
    exportToExcel();
});

// Variable to store the last fetched data
let lastFetchedData = null;

// Function to fetch reviews based on word inclusion and sentiment filter
async function fetchReviews(wordInclude, sentimentFilter) {
    try {
        const url = new URL('http://127.0.0.1:5000/reviews');
        const params = { word_include: wordInclude, pos_neg_all: sentimentFilter };
        url.search = new URLSearchParams(params).toString();

        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        displayReviews(data.positive_reviews.concat(data.negative_reviews));
        
        const positive_popular_words = await popularWords(data.positive_reviews);
        const negative_popular_words = await popularWords(data.negative_reviews);
            
        displayPopularWords(positive_popular_words, negative_popular_words);
        console.log(data.similar_words);

        // Save the fetched data including popular words
        lastFetchedData = {
            ...data,
            positive_popular_words,
            negative_popular_words
        };

        document.getElementById('export-button').disabled = false;

    } catch (error) {
        console.error('Failed to fetch reviews. Please try again later.');
        console.error('Error fetching reviews:', error);
        alert('Failed to fetch reviews. Please try again later.'); // Error message to user 
    }
}

// Function to display reviews in the table
function displayReviews(reviews) {
    const tbody = document.querySelector('#reviews-table tbody');
    tbody.innerHTML = '';

    reviews.forEach(review => {
        const row = document.createElement('tr');
        const labelCell = document.createElement('td');
        const titleCell = document.createElement('td');
        const contentCell = document.createElement('td');
        
        labelCell.textContent = review.label === "negative" ? 'Negative' : 'Positive';
        titleCell.textContent = review.title;
        contentCell.textContent = review.content;

        row.appendChild(labelCell);
        row.appendChild(titleCell);
        row.appendChild(contentCell);

        tbody.appendChild(row);
    });
}

// Function to display popular words in the lists
function displayPopularWords(positiveWords, negativeWords) {
    const positiveWordsList = document.getElementById('positive-words-list');
    const negativeWordsList = document.getElementById('negative-words-list');

    positiveWordsList.innerHTML = '';
    negativeWordsList.innerHTML = '';

    positiveWords.forEach(word => {
        const listItem = document.createElement('li');
        listItem.textContent = `${word[0]} (${word[1]})`;
        positiveWordsList.appendChild(listItem);
    });

    negativeWords.forEach(word => {
        const listItem = document.createElement('li');
        listItem.textContent = `${word[0]} (${word[1]})`;
        negativeWordsList.appendChild(listItem);
    });
}

// Function to load stop words from a JSON file
async function loadStopWords() {
    try {
        const response = await fetch('./data/stop_words.json');
        const data = await response.json();
        return new Set(data.stop_words);
    } catch (error) {
        console.error('Error loading stop words:', error);
        return new Set();
    }
}

// Function to count the popular words in the reviews
async function popularWords(reviews) {
    const punctuation = new Set('!()-[]{};:\'"\\,<>./?@#$%^&*_~');
    let wordCounter = {};

    const stopWords = await loadStopWords();

    reviews.forEach(review => {
        const words = review.title.split(/\s+/).concat(review.content.split(/\s+/));

        words.forEach(word => {
            word = word.toLowerCase().trim();
            if (!stopWords.has(word) && !punctuation.has(word)) {
                if (wordCounter[word]) {
                    wordCounter[word] += 1;
                } else {
                    wordCounter[word] = 1;
                }
            }
        });
    });

    const sortedWords = Object.entries(wordCounter).sort((a, b) => b[1] - a[1]);
    return sortedWords;
}

// Function to export the fetched data to an Excel file
function exportToExcel() {
    const reviews = lastFetchedData.positive_reviews.concat(lastFetchedData.negative_reviews)
    // Are there any reviews to export?
    if (reviews.length === 0) {
        alert('No data to export');
        return;
    }

    reviews.map(review => ({
        Label: review.label === "negative" ? 'Negative' : 'Positive',
        Title: review.title,
        Content: review.content
    }));

    const positiveWords = lastFetchedData.positive_popular_words.map(word => ({
        Word: word[0],
        Count: word[1]
    }));

    const negativeWords = lastFetchedData.negative_popular_words.map(word => ({
        Word: word[0],
        Count: word[1]
    }));

    const reviewsSheet = XLSX.utils.json_to_sheet(reviews);
    const positiveWordsSheet = XLSX.utils.json_to_sheet(positiveWords);
    const negativeWordsSheet = XLSX.utils.json_to_sheet(negativeWords);

    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, reviewsSheet, 'Reviews');
    XLSX.utils.book_append_sheet(workbook, positiveWordsSheet, 'Positive Words');
    XLSX.utils.book_append_sheet(workbook, negativeWordsSheet, 'Negative Words');

    XLSX.writeFile(workbook, 'reviews.xlsx');
}
