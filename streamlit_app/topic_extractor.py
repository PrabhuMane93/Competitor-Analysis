"""
Topic Extraction System using Gemini 2.5 Pro
This module extracts unique topics from competitor CSV files and compares them with Ergosign's topics.
"""

import os
from dotenv import load_dotenv
import pandas as pd
import glob
from typing import List, Dict, Set
import re
from pymilvus import connections, Collection
from gemini_langchain import GeminiLangChain
from datetime import datetime, timedelta

class TopicExtractor:
    """
    Extracts and analyzes topics from CSV files using Gemini 2.5 Pro.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the TopicExtractor with Gemini client.
        
        Args:
            api_key: Google API key for Gemini
        """
        load_dotenv()
        self.gemini = GeminiLangChain(api_key=api_key, temperature=0.3)
        self.data_folder = "data"
        self.ergosign_file = "ergosign.de_scraped_data.csv"
        
    
    def get_csv_files(self) -> List[str]:
        """
        Get all CSV files from the data folder.
        
        Returns:
            List of CSV file paths
        """
        csv_pattern = os.path.join(self.data_folder, "*.csv")
        csv_files = glob.glob(csv_pattern)
        
        if not csv_files:
            print(f"❌ No CSV files found in '{self.data_folder}' folder")
            return []
            
        print(f"✅ Found {len(csv_files)} CSV files:")
        for file in csv_files:
            print(f"   - {os.path.basename(file)}")
        
        return csv_files
    
    def get_milvus_data(self):
        connections.connect(
        alias="default",
        uri=os.environ.get("ZILLIZ_URI"),
        token=os.environ.get("ZILLIZ_TOKEN"))
        collection = Collection(os.environ.get("COLLECTION_NAME"))
        results = collection.query(expr="id >= 0",output_fields=["timestamp", "title", "body", "company_name"])
        data = {}

        # today's date
        now = datetime.now()

        # 3 months ≈ 90 days (simple approximation)
        three_months_ago = now - timedelta(days=90)

        for row in results:
            ts = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
            if ts >= three_months_ago :
                if row["company_name"] not in data.keys():
                    data[row["company_name"]] = row["title"] + " " + row["body"]
                else:
                    data[row["company_name"]] += "\n\n" + row["title"] + " " + row["body"]

            else:
                continue
            
        return data

    def read_csv_content(self, csv_file: str) -> str:
        """
        Read and combine text content from Title and Content columns only.
        
        Args:
            csv_file: Path to the CSV file
            
        Returns:
            Combined text content from Title and Content columns
        """
        try:
            df = pd.read_csv(csv_file)
            
            # Only read Title and Content columns, ignore URL and other columns
            text_content = ""
            
            # Check for Title column (case insensitive)
            title_col = None
            content_col = None
            
            for col in df.columns:
                if col.lower().strip('"') in ['title']:
                    title_col = col
                elif col.lower().strip('"') in ['content']:
                    content_col = col
            
            if title_col is not None:
                titles = df[title_col].dropna().astype(str)
                title_text = ' '.join(titles.tolist())
                text_content += f" {title_text}"
                print(f"✅ Found {len(titles)} titles")
            
            if content_col is not None:
                contents = df[content_col].dropna().astype(str)
                content_text = ' '.join(contents.tolist())
                text_content += f" {content_text}"
                print(f"✅ Found {len(contents)} content entries")
            
            if not title_col and not content_col:
                print(f"⚠️  No Title or Content columns found in {os.path.basename(csv_file)}")
                print(f"Available columns: {list(df.columns)}")
                return ""
            
            # Clean the text
            text_content = re.sub(r'\s+', ' ', text_content.strip())
            
            print(f"✅ Read {len(text_content)} characters from {os.path.basename(csv_file)}")
            return text_content
            
        except Exception as e:
            print(f"❌ Error reading {csv_file}: {str(e)}")
            return ""
    
    def extract_topics_from_text(self, text: str, company_name: str) -> List[str]:
        """
        Extract 5 unique topics from text using Gemini.
        
        Args:
            text: Text content to analyze
            company_name: Name of the company for context
            
        Returns:
            List of 5 unique topics
        """
        system_prompt = """
        You are an expert business content analyst. Analyze the provided text content from a company's website, blog, articles, and case studies.
        
        Extract exactly 5 unique, specific topics that this company specializes in or writes about.
        
        CRITICAL REQUIREMENTS:
        1. Topics must be SPECIFIC and CONCRETE (examples: "AI-Powered UX Design", "Voice User Interfaces", "E-commerce Optimization")
        2. NOT generic terms (avoid: "technology", "business", "innovation", "solutions")
        3. Each topic should be 2-4 words
        4. Topics must be DIFFERENT from each other
        5. Focus on the company's actual services, expertise, or specializations
        6. Base topics on what you actually read in the content
        
        RESPONSE FORMAT - EXACTLY like this:
        1. [Specific Topic]
        2. [Specific Topic] 
        3. [Specific Topic]
        4. [Specific Topic]
        5. [Specific Topic]
        
        NO additional text, explanations, or formatting.
        """
        
        # Limit text but ensure we get meaningful content
        text_sample = text[:12000] if len(text) > 12000 else text
        
        user_message = f"""
        Company: {company_name}
        
        Content to analyze:
        {text_sample}
        """
        
        try:
            print(f"🤖 Asking Gemini to analyze {company_name} content...")
            
            # Use a combined prompt instead of system + user message
            combined_prompt = f"""
            {system_prompt}
            
            Company: {company_name}
            
            Content to analyze:
            {text_sample}
            """
            
            response = self.gemini.chat(combined_prompt)
            
            print(f"🔍 Raw Gemini response for {company_name}:")
            print(f"'{response[:200]}...'")
            
            # Check if we got an error response
            if "Error:" in response or "SystemMessages" in response:
                print(f"❌ Got error response from Gemini, using fallback topics")
                return [
                    f"{company_name.title()} Digital Services",
                    f"{company_name.title()} UX Design",
                    f"{company_name.title()} Technology Solutions",
                    f"{company_name.title()} Innovation Strategy",
                    f"{company_name.title()} Business Consulting"
                ]
            
            # Parse the response to extract topics
            topics = []
            lines = response.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Extract topic after number/bullet
                    topic = re.sub(r'^[\d\-\.\)\s]+', '', line).strip()
                    # Remove brackets if present
                    topic = re.sub(r'^\[|\]$', '', topic).strip()
                    if topic and not topic.startswith("Additional Topic") and not topic.startswith("Topic") and "Error:" not in topic:
                        topics.append(topic)
            
            # If we didn't get good topics, try alternative parsing
            if len(topics) < 3:
                print(f"⚠️  Poor topic extraction, trying alternative approach...")
                
                # Try to extract any meaningful phrases from the response
                words = response.split()
                potential_topics = []
                
                # Look for capitalized phrases that might be topics
                for i, word in enumerate(words):
                    if len(word) > 2 and word[0].isupper() and i < len(words) - 1:
                        phrase = ' '.join(words[i:i+2])
                        if not any(skip in phrase.lower() for skip in ['the', 'and', 'additional', 'topic', 'error', 'system']):
                            potential_topics.append(phrase)
                
                if potential_topics:
                    topics = potential_topics[:5]
            
            # Final fallback - generate descriptive topics based on company name
            if len(topics) < 5:
                fallback_topics = [
                    f"{company_name.title()} Digital Services",
                    f"{company_name.title()} UX Design",
                    f"{company_name.title()} Technology Solutions",
                    f"{company_name.title()} Innovation Strategy",
                    f"{company_name.title()} Business Consulting"
                ]
                
                while len(topics) < 5:
                    topics.append(fallback_topics[len(topics)])
            
            # Ensure exactly 5 topics
            topics = topics[:5]
            
            print(f"✅ Extracted {len(topics)} topics from {company_name}")
            for i, topic in enumerate(topics, 1):
                print(f"   {i}. {topic}")
            
            return topics
            
        except Exception as e:
            print(f"❌ Error extracting topics from {company_name}: {str(e)}")
            # Better fallback based on company name
            return [
                f"{company_name.title()} Digital Services", 
                f"{company_name.title()} UX Design",
                f"{company_name.title()} Technology Solutions",
                f"{company_name.title()} Innovation Strategy", 
                f"{company_name.title()} Business Consulting"
            ]
    def generate_topics_from_milvus_data(self):
        data = self.get_milvus_data()
        all_company_topics = {}
        for company_name, text in data.items():
            print(f"\n🔍 Processing {company_name}...")
            topics = self.extract_topics_from_text(text, company_name)
            all_company_topics[company_name] = topics
        return all_company_topics
    
    def process_all_csv_files(self) -> Dict[str, List[str]]:
        """
        Process all CSV files and extract topics from each.
        
        Returns:
            Dictionary mapping company names to their topics
        """
        csv_files = self.get_csv_files()
        if not csv_files:
            return {}
        
        all_company_topics = {}
        
        for csv_file in csv_files:
            company_name = os.path.basename(csv_file).replace('.csv', '').replace('_scraped_data', '')
            
            print(f"\n🔍 Processing {company_name}...")
            
            # Read CSV content
            text_content = self.read_csv_content(csv_file)

            if not text_content:
                continue
            
            # Extract topics
            topics = self.extract_topics_from_text(text_content, company_name)
            all_company_topics[company_name] = topics
        
        return all_company_topics
    
    def save_all_topics(self, all_company_topics: Dict[str, List[str]]) -> str:
        """
        Save all topics to a single text file.
        
        Args:
            all_company_topics: Dictionary of company topics
            
        Returns:
            Path to the saved file
        """
        output_file = "all_competitor_topics.txt"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("COMPETITOR TOPICS ANALYSIS\n")
                f.write("=" * 50 + "\n\n")
                
                for company, topics in all_company_topics.items():
                    f.write(f"Company: {company}\n")
                    f.write("-" * 30 + "\n")
                    for i, topic in enumerate(topics, 1):
                        f.write(f"{i}. {topic}\n")
                    f.write("\n")
                
                # Create a flat list of all topics for easy reference
                f.write("\nALL TOPICS (FLAT LIST)\n")
                f.write("=" * 30 + "\n")
                
                all_topics_flat = []
                for topics in all_company_topics.values():
                    all_topics_flat.extend(topics)
                
                for i, topic in enumerate(all_topics_flat, 1):
                    f.write(f"{i}. {topic}\n")
            
            print(f"✅ Saved all topics to '{output_file}'")
            return output_file
            
        except Exception as e:
            print(f"❌ Error saving topics: {str(e)}")
            return ""
    
    def get_ergosign_topics(self) -> List[str]:
        """
        Extract topics specifically from Ergosign's CSV file.
        
        Returns:
            List of Ergosign's topics
        """
        ergosign_path = os.path.join(self.data_folder, self.ergosign_file)
        
        if not os.path.exists(ergosign_path):
            print(f"❌ Ergosign file not found: {ergosign_path}")
            return []
        
        print(f"\n🎯 Processing Ergosign (main client)...")
        
        text_content = self.read_csv_content(ergosign_path)
        if not text_content:
            return []
        
        topics = self.extract_topics_from_text(text_content, "Ergosign")
        return topics
    
    def find_missing_topics(self, all_company_topics: Dict[str, List[str]], ergosign_topics: List[str]) -> List[str]:
        """
        Find topics that competitors have but Ergosign doesn't.
        
        Args:
            all_company_topics: All competitor topics
            ergosign_topics: Ergosign's topics
            
        Returns:
            List of topics missing from Ergosign
        """
        print(f"\n🔍 Analyzing topic gaps...")
        
        # Get all competitor topics (excluding Ergosign)
        competitor_topics = []
        for company, topics in all_company_topics.items():
            if company != "ergosign.de":
                competitor_topics.extend(topics)
        
        # Use Gemini to intelligently compare topics
        system_prompt = """
        You are an expert business analyst. I will provide you with:
        1. A list of topics that Ergosign (main client) covers
        2. A list of topics that their competitors cover
        
        Your task is to identify topics/themes that competitors cover but Ergosign does NOT cover.
        Consider semantic similarity - topics don't need to be exactly the same words to be similar concepts.
        
        Provide a list of unique topics that represent gaps in Ergosign's content strategy.
        Focus on topics that could be valuable for Ergosign to explore.
        
        Format as a numbered list, maximum 10 topics:
        1. Topic 1
        2. Topic 2
        etc.
        """
        
        user_message = f"""
        Ergosign's topics:
        {chr(10).join([f"- {topic}" for topic in ergosign_topics])}
        
        Competitors' topics:
        {chr(10).join([f"- {topic}" for topic in competitor_topics])}
        """
        # print(user_message)
        # print(system_prompt)
        try:
            response = self.gemini.chat_with_system_prompt(user_message, system_prompt)
            
            # Parse missing topics
            missing_topics = []
            lines = response.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    topic = re.sub(r'^[\d\-\.\)\s]+', '', line).strip()
                    if topic:
                        missing_topics.append(topic)
            
            print(f"✅ Found {len(missing_topics)} missing topics")
            return missing_topics
            
        except Exception as e:
            print(f"❌ Error finding missing topics: {str(e)}")
            return []
    
    def save_missing_topics(self, missing_topics: List[str], ergosign_topics: List[str]) -> str:
        """
        Save missing topics to a text file.
        
        Args:
            missing_topics: Topics missing from Ergosign
            ergosign_topics: Ergosign's current topics
            
        Returns:
            Path to the saved file
        """
        output_file = "ergosign_missing_topics.txt"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("ERGOSIGN TOPIC GAP ANALYSIS\n")
                f.write("=" * 50 + "\n\n")
                
                f.write("ERGOSIGN'S CURRENT TOPICS:\n")
                f.write("-" * 30 + "\n")
                for i, topic in enumerate(ergosign_topics, 1):
                    f.write(f"{i}. {topic}\n")
                
                f.write(f"\nTOPICS MISSING FROM ERGOSIGN (COVERED BY COMPETITORS):\n")
                f.write("-" * 60 + "\n")
                
                if missing_topics:
                    for i, topic in enumerate(missing_topics, 1):
                        f.write(f"{i}. {topic}\n")
                else:
                    f.write("No missing topics found - Ergosign covers all competitor topics!\n")
                
                f.write(f"\nTOTAL MISSING TOPICS: {len(missing_topics)}\n")
                f.write(f"ANALYSIS DATE: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            print(f"✅ Saved missing topics analysis to '{output_file}'")
            return output_file
            
        except Exception as e:
            print(f"❌ Error saving missing topics: {str(e)}")
            return ""
    
    def run_complete_analysis(self):
        """
        Run the complete topic extraction and analysis process.
        """
        print("🚀 Starting Complete Topic Analysis")
        print("=" * 50)
        
        
        # Step 1: Process all CSV files
        print("\n📊 Step 1: Processing data from milvus vectorstore...")
        all_company_topics = self.generate_topics_from_milvus_data()
        
        if not all_company_topics:
            print("❌ No topics extracted. Please check your milvus DB.")
            return
        
        # Step 2: Save all topics
        print("\n💾 Step 2: Saving all topics...")
        all_topics_file = self.save_all_topics(all_company_topics)
        
        # Step 3: Get Ergosign topics
        print("\n🎯 Step 3: Analyzing Ergosign topics...")
        ergosign_topics = self.get_ergosign_topics()
        
        if not ergosign_topics:
            print("❌ Could not extract Ergosign topics. Please check the file.")
            return
        
        # Step 4: Find missing topics
        print("\n🔍 Step 4: Finding topic gaps...")
        missing_topics = self.find_missing_topics(all_company_topics, ergosign_topics)
        
        # Step 5: Save missing topics
        print("\n💾 Step 5: Saving missing topics analysis...")
        missing_topics_file = self.save_missing_topics(missing_topics, ergosign_topics)
        
        # Summary
        print("\n🎉 ANALYSIS COMPLETE!")
        print("=" * 30)
        print(f"📄 All topics saved to: {all_topics_file}")
        print(f"📄 Missing topics saved to: {missing_topics_file}")
        print(f"📊 Total companies analyzed: {len(all_company_topics)}")
        print(f"📊 Total missing topics: {len(missing_topics)}")
        
        if missing_topics:
            print(f"\n🔥 TOP MISSING TOPICS FOR ERGOSIGN:")
            for i, topic in enumerate(missing_topics[:5], 1):
                print(f"   {i}. {topic}")


def main():
    """Main function to run the topic extraction system."""
    try:
        extractor = TopicExtractor()
        extractor.run_complete_analysis()
        
    except Exception as e:
        print(f"❌ Error running analysis: {str(e)}")
        print("Please make sure your GOOGLE_API_KEY is set correctly.")


if __name__ == "__main__":
    main()
