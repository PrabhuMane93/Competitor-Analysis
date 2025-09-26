"""
Simple script to run the topic extraction analysis.
This is the main entry point for the topic analysis system.
"""
import os
from topic_extractor import TopicExtractor
from dotenv import load_dotenv

def main():
    """
    Run the complete topic analysis process.
    """
    print("🚀 GEMINI TOPIC EXTRACTION SYSTEM")
    print("=" * 50)
    print("This system will:")
    print("1. Read all CSV files from the 'data' folder")
    print("2. Extract 5 unique topics from each company using Gemini 2.5 Pro")
    print("3. Save all topics to 'all_competitor_topics.txt'")
    print("4. Compare with Ergosign's topics")
    print("5. Output missing topics to 'ergosign_missing_topics.txt'")
    print("\n" + "=" * 50)
    
    load_dotenv()
    # Load environment variables
    API_KEY = os.environ.get("GOOGLE_API_KEY")
    
    # Initialize and run the extractor
    extractor = TopicExtractor(api_key=API_KEY)
    extractor.run_complete_analysis()

if __name__ == "__main__":
    main()
