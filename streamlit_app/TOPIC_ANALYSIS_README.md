# 🚀 Competitor Topic Analysis System

This system uses Gemini 2.5 Pro to analyze competitor content and identify topic gaps for Ergosign.

## 📁 Project Structure

```
root/
├── topic_extractor.py          # Main analysis engine
├── run_topic_analysis.py       # Simple script to run analysis
├── data/                       # CSV files folder
│   ├── ergosign.de_scraped_data.csv    # Main client data
│   ├── accenture.com_scraped_data.csv  # Competitor data
│   ├── cobeisfresh.com_scraped_data.csv # Competitor data
│   └── [other competitor CSV files]     # Additional competitors
└── outputs/                    # Generated analysis files
    ├── all_competitor_topics.txt       # All extracted topics
    └── ergosign_missing_topics.txt     # Gap analysis results
```

## 🎯 What This System Does

1. **Reads CSV Files**: Automatically processes all CSV files in the `data/` folder
2. **Extracts Topics**: Uses Gemini 2.5 Pro to extract 5 unique topics from each company's content
3. **Saves All Topics**: Creates `all_competitor_topics.txt` with all extracted topics
4. **Gap Analysis**: Compares competitor topics with Ergosign's topics
5. **Outputs Missing Topics**: Creates `ergosign_missing_topics.txt` with topics Ergosign should consider

## 🚀 How to Run

### Simple Method:
```bash
python run_topic_analysis.py
```

### Advanced Method:
```python
from topic_extractor import TopicExtractor

# Initialize the extractor
extractor = TopicExtractor()

# Run complete analysis
extractor.run_complete_analysis()
```

## 📊 Output Files

### `all_competitor_topics.txt`
Contains all topics extracted from each competitor, organized by company.

### `ergosign_missing_topics.txt`
Contains:
- Ergosign's current topics
- Topics that competitors cover but Ergosign doesn't
- Gap analysis summary

## 🔧 Requirements

- Python 3.8+
- All packages from `requirements.txt`
- Google API Key for Gemini 2.5 Pro (set as `GOOGLE_API_KEY` environment variable)
- CSV files in the `data/` folder

## 📋 CSV File Format

Your CSV files should contain text content in any columns. The system will automatically:
- Read all text columns
- Combine all content
- Extract meaningful topics using AI

Example CSV structure:
```csv
title,content,url,date
"Article Title","Article content here...","https://example.com","2024-01-01"
```

## 🎨 Features

- **AI-Powered Analysis**: Uses Gemini 2.5 Pro for intelligent topic extraction
- **Semantic Comparison**: Compares topics by meaning, not just exact text matches
- **Automated Processing**: Handles multiple CSV files automatically
- **Gap Analysis**: Identifies content opportunities for Ergosign
- **Detailed Reporting**: Generates comprehensive analysis reports

## 🔍 How It Works

1. **Content Reading**: Reads and combines all text content from CSV files
2. **Topic Extraction**: Uses AI prompts to extract 5 unique, meaningful topics per company
3. **Intelligent Deduplication**: Ensures topics are distinct and non-overlapping
4. **Semantic Analysis**: Compares topics by meaning to identify gaps
5. **Strategic Reporting**: Outputs actionable insights for content strategy

## 🎯 Use Cases

- **Content Strategy**: Identify new content topics to explore
- **Competitive Analysis**: Understand what competitors are focusing on
- **Market Research**: Discover trending topics in your industry
- **Content Planning**: Find content gaps in your current strategy

## 🔄 Customization

You can customize the analysis by modifying:
- `temperature` in TopicExtractor (creativity level)
- Topic extraction prompts in `extract_topics_from_text()`
- Number of topics per company
- Analysis criteria in `find_missing_topics()`

## 🚨 Troubleshooting

1. **No CSV files found**: Make sure CSV files are in the `data/` folder
2. **API errors**: Check your `GOOGLE_API_KEY` environment variable
3. **Empty topics**: Verify your CSV files contain text content
4. **Rate limiting**: The system includes error handling for API limits

## 📈 Example Output

```
🎉 ANALYSIS COMPLETE!
==============================
📄 All topics saved to: all_competitor_topics.txt
📄 Missing topics saved to: ergosign_missing_topics.txt
📊 Total companies analyzed: 4
📊 Total missing topics: 7

🔥 TOP MISSING TOPICS FOR ERGOSIGN:
   1. AI-Powered Design Tools
   2. Voice User Interface Design
   3. IoT Device Interfaces
   4. Mobile-First Strategy
   5. E-commerce UX Optimization
```

---

**Happy analyzing! 🚀**
