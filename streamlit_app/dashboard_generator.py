import os
from dotenv import load_dotenv
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
from topic_extractor import TopicExtractor


class DashboardGenerator:
    def __init__(self):
        load_dotenv()
        self.dashboards_folder = "dashboards"
        self.ensure_dashboards_folder()
    
    def ensure_dashboards_folder(self):
        """Create dashboards folder if it doesn't exist."""
        if not os.path.exists(self.dashboards_folder):
            os.makedirs(self.dashboards_folder)
    
    def generate_dashboard_data(self) -> str:
        """Generate dashboard data and save to timestamped folder."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dashboard_folder = os.path.join(self.dashboards_folder, f"analysis_{timestamp}")
        os.makedirs(dashboard_folder, exist_ok=True)
        
        # Extract topics using existing TopicExtractor
        API_KEY = os.environ.get("GOOGLE_API_KEY")
        extractor = TopicExtractor(api_key=API_KEY)
        company_topics = extractor.generate_topics_from_milvus_data()
        ergosign_company_topics = extractor.get_ergosign_topics()

        if not company_topics:
            raise Exception("No topics extracted from CSV files")
        
        # Generate dashboard data
        dashboard_data = self._create_dashboard_data(company_topics, ergosign_company_topics)
        
        # Save data files
        self._save_dashboard_files(dashboard_folder, dashboard_data, timestamp)
        
        return dashboard_folder
    
    def _create_dashboard_data(self, company_topics: Dict[str, List[str]], ergosign_company_topics) -> Dict:
        """Create structured dashboard data from company topics."""
        # Get Ergosign topics (main company)
        ergosign_topics = set()
        competitor_topics = set()
        
        for topics in ergosign_company_topics:
                ergosign_topics.update(topics)

        for company, topics in company_topics.items():
                competitor_topics.update(topics)

        
        # Calculate gaps and coverage
        all_topics = ergosign_topics.union(competitor_topics)
        gaps = competitor_topics - ergosign_topics
        coverage = ergosign_topics.intersection(competitor_topics)
        
        # Create summary metrics
        total_companies = len(company_topics)
        total_topics = len(all_topics)
        gap_opportunities = len(gaps)
        coverage_percentage = round((len(coverage) / len(all_topics)) * 100, 1) if all_topics else 0
        
        # Topic distribution
        ergosign_percentage = round((len(ergosign_topics) / len(all_topics)) * 100) if all_topics else 0
        competitor_percentage = 100 - ergosign_percentage
        
        # Gap priority (simplified)
        high_priority_gaps = list(gaps)[:3] if len(gaps) >= 3 else list(gaps)
        medium_priority_gaps = list(gaps)[3:7] if len(gaps) > 3 else []
        
        return {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'companies_analyzed': total_companies,
                'total_topics': total_topics
            },
            'summary_metrics': {
                'companies_analyzed': total_companies,
                'topics_identified': total_topics,
                'gap_opportunities': gap_opportunities,
                'coverage_percentage': coverage_percentage
            },
            'topic_distribution': {
                'ergosign_percentage': ergosign_percentage,
                'competitor_percentage': competitor_percentage
            },
            'topics_by_company': {
                company: len(topics) for company, topics in company_topics.items()
            },
            'gap_analysis': {
                'high_priority': high_priority_gaps,
                'medium_priority': medium_priority_gaps,
                'total_gaps': len(gaps)
            },
            'detailed_data': {
                'ergosign_topics': list(ergosign_topics),
                'competitor_topics': list(competitor_topics),
                'coverage_topics': list(coverage),
                'gap_topics': list(gaps),
                'company_topics': company_topics
            }
        }
    
    def _save_dashboard_files(self, folder: str, data: Dict, timestamp: str):
        """Save dashboard data to multiple files."""
        # Main dashboard data (JSON)
        with open(os.path.join(folder, 'dashboard_data.json'), 'w') as f:
            json.dump(data, f, indent=2)
        
        # Summary metrics (CSV)
        summary_df = pd.DataFrame([data['summary_metrics']])
        summary_df.to_csv(os.path.join(folder, 'summary_metrics.csv'), index=False)
        
        # Topics by company (CSV)
        topics_df = pd.DataFrame([
            {'Company': company, 'Topic_Count': count, 'Topics': ', '.join(data['detailed_data']['company_topics'][company])}
            for company, count in data['topics_by_company'].items()
        ])
        topics_df.to_csv(os.path.join(folder, 'topics_by_company.csv'), index=False)
        
        # Gap analysis (CSV)
        gaps_data = []
        for gap in data['gap_analysis']['high_priority']:
            gaps_data.append({'Topic': gap, 'Priority': 'High'})
        for gap in data['gap_analysis']['medium_priority']:
            gaps_data.append({'Topic': gap, 'Priority': 'Medium'})
        
        if gaps_data:
            gaps_df = pd.DataFrame(gaps_data)
            gaps_df.to_csv(os.path.join(folder, 'gap_opportunities.csv'), index=False)
        
        # Metadata (TXT)
        with open(os.path.join(folder, 'analysis_info.txt'), 'w') as f:
            f.write(f"Ergosign Topic Gap Analysis Dashboard\n")
            f.write(f"Generated: {data['metadata']['timestamp']}\n")
            f.write(f"Companies Analyzed: {data['metadata']['companies_analyzed']}\n")
            f.write(f"Total Topics Identified: {data['metadata']['total_topics']}\n")
    
    def get_available_dashboards(self) -> List[Tuple[str, str]]:
        """Get list of available dashboard folders with timestamps."""
        dashboards = []
        if os.path.exists(self.dashboards_folder):
            for folder in os.listdir(self.dashboards_folder):
                if folder.startswith('analysis_'):
                    timestamp_str = folder.replace('analysis_', '')
                    try:
                        # Parse timestamp for display
                        dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        display_name = dt.strftime("%Y-%m-%d %H:%M:%S")
                        dashboards.append((folder, display_name))
                    except ValueError:
                        dashboards.append((folder, folder))
        
        return sorted(dashboards, key=lambda x: x[0], reverse=True)
    
    def load_dashboard_data(self, dashboard_folder: str) -> Dict:
        """Load dashboard data from specified folder."""
        data_path = os.path.join(self.dashboards_folder, dashboard_folder, 'dashboard_data.json')
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Dashboard data not found: {data_path}")
        
        with open(data_path, 'r') as f:
            return json.load(f)