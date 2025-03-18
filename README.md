# News Summarization and Text-to-Speech Application

## Overview
This is a web-based application that extracts key details from multiple news articles related to a given company, performs sentiment analysis, conducts a comparative analysis, and generates a text-to-speech (TTS) output in Hindi. The tool allows users to input a company name and receive a structured sentiment report along with an audio output.

### Key Features:
1. **News Extraction**: Extracts titles, summaries, and metadata from at least 10 unique news articles.
2. **Sentiment Analysis**: Classifies article content as Positive, Negative, or Neutral.
3. **Comparative Analysis**: Compares sentiment across articles to derive insights.
4. **Text-to-Speech**: Converts the summarized content into Hindi speech using an open-source TTS model.
5. **Web Interface**: Built using Streamlit for user interaction.
6. **API Integration**: Backend APIs for communication between frontend and backend.
7. **Deployment**: Deployed on Hugging Face Spaces for easy access.

---

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [API Documentation](#api-documentation)
4. [Project Structure](#project-structure)
5. [Models Used](#models-used)
6. [Assumptions & Limitations](#assumptions--limitations)
7. [Deployment](#deployment)
8. [Evaluation](#evaluation)
9. [Bonus Features](#bonus-features)
10. [Contributing](#contributing)
11. [License](#license)

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Pip (Python package manager)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/news-tts-app.git
   cd news-tts-app
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download NLTK resources:
   ```python
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
   ```

5. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Add your NewsAPI key (if using):
     ```env
     NEWSAPI_KEY=your_api_key_here
     ```

---

## Usage

### Running the Application
1. Start the FastAPI backend:
   ```bash
   python api.py
   ```
   The API will run at `http://localhost:8000`.

2. Start the Streamlit frontend:
   ```bash
   streamlit run app.py
   ```
   The web interface will open in your browser at `http://localhost:8501`.

### Input
- Enter a company name (e.g., "Tesla") in the input field.
- Click "Analyze News" to fetch and process articles.
- Click "Generate Audio" to create a Hindi TTS summary.

### Output
- **Structured Report**:
  - Article titles, summaries, sentiment, and topics.
  - Comparative sentiment analysis.
  - Final sentiment summary.
- **Hindi TTS**: Playable audio file summarizing the report.

---

## API Documentation

### Endpoints
1. **GET `/news/{company}`**:
   - Fetches and analyzes news articles for the given company.
   - Parameters:
     - `company`: Name of the company.
     - `max_articles`: Maximum number of articles to fetch (default: 10).
   - Example:
     ```bash
     curl -X GET "http://localhost:8000/news/Tesla?max_articles=10"
     ```

2. **GET `/audio/{company}`**:
   - Generates Hindi TTS for the company's news summary.
   - Parameters:
     - `company`: Name of the company.
     - `max_articles`: Maximum number of articles to include in the summary (default: 5).
   - Example:
     ```bash
     curl -X GET "http://localhost:8000/audio/Tesla?max_articles=5"
     ```

3. **GET `/companies`**:
   - Returns a list of sample companies for testing.
   - Example:
     ```bash
     curl -X GET "http://localhost:8000/companies"
     ```

---

## Project Structure

```
news_tts_app/
├── api.py                  # FastAPI backend
├── app.py                  # Streamlit frontend
├── config.py               # Configuration settings
├── models/                 # Core functionality
│   ├── news_extractor.py   # News extraction logic
│   ├── sentiment_analyzer.py # Sentiment analysis
│   ├── text_to_speech.py   # TTS generation
│   └── comparative_analyzer.py # Comparative analysis
├── utils.py                # Utility functions
├── requirements.txt        # Dependencies
├── .env                    # Environment variables
├── README.md               # Project documentation
└── output/                 # Generated audio files
```

---

## Models Used

1. **News Extraction**:
   - BeautifulSoup (`bs4`) for web scraping.
   - Newspaper3k for article parsing.

2. **Sentiment Analysis**:
   - NLTK's VADER for sentiment classification.

3. **Text-to-Speech**:
   - Hugging Face's `facebook/mms-tts-hin` for Hindi TTS.
   - gTTS as a fallback.

4. **Translation**:
   - Hugging Face's `Helsinki-NLP/opus-mt-en-hi` for English-to-Hindi translation.

---

## Assumptions & Limitations

### Assumptions:
- News articles are available in English.
- The application focuses on non-JS websites for scraping.
- Users have a stable internet connection for API calls.

### Limitations:
- Scraping may fail for websites with dynamic content.
- Translation quality depends on the input text.
- TTS generation may be slow for long texts.

---

## Deployment

### Hugging Face Spaces
1. Create a new Space on Hugging Face.
2. Upload the project files.
3. Add the following environment variables in the Space settings:
   - `NEWSAPI_KEY` (if using NewsAPI).
4. Deploy the Space.

### Access the Application
- Visit the Hugging Face Space URL to use the application.

---

## Evaluation

### Correctness
- The application accurately extracts and processes news articles.
- Sentiment analysis and TTS generation work as expected.

### Efficiency
- Optimized for performance with caching and parallel processing.

### Robustness
- Handles errors gracefully (e.g., no articles found, API failures).

### Deployment
- Accessible via Hugging Face Spaces.

### Code Quality
- Follows PEP8 guidelines.
- Well-documented and maintainable.

---

## Bonus Features

1. **Querying System**:
   - Users can query specific topics or keywords from the analyzed articles.
   - Example: "Show articles about Tesla's stock performance."

2. **Detailed Analysis Reporting**:
   - Visualizations (e.g., bar charts, word clouds).
   - Exportable reports in JSON or CSV format.

---

## Contributing

Contributions are welcome! Follow these steps:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Video Demo
[Link to video demo explaining how the application works]
