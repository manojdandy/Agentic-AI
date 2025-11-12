"""
Test Data Loader
Utility for loading and managing test cases
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import json


class TestDataLoader:
    """
    Load and manage test cases from CSV files
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize test data loader
        
        Args:
            data_dir: Path to test-cases directory. 
                     If None, uses current file's location.
        """
        if data_dir is None:
            data_dir = Path(__file__).parent
        else:
            data_dir = Path(data_dir)
        
        self.data_dir = data_dir
        self.attacks_file = data_dir / 'attacks' / 'attack_test_cases.csv'
        self.legitimate_file = data_dir / 'legitimate' / 'legitimate_inputs.csv'
        self.edge_cases_file = data_dir / 'edge-cases' / 'edge_cases.csv'
        
        # Cache for loaded data
        self._attacks = None
        self._legitimate = None
        self._edge_cases = None
    
    def load_attacks(self, reload: bool = False) -> pd.DataFrame:
        """
        Load attack test cases
        
        Args:
            reload: Force reload even if cached
            
        Returns:
            DataFrame with attack test cases
        """
        if self._attacks is None or reload:
            self._attacks = pd.read_csv(self.attacks_file)
        return self._attacks.copy()
    
    def load_legitimate(self, reload: bool = False) -> pd.DataFrame:
        """
        Load legitimate test cases
        
        Args:
            reload: Force reload even if cached
            
        Returns:
            DataFrame with legitimate test cases
        """
        if self._legitimate is None or reload:
            self._legitimate = pd.read_csv(self.legitimate_file)
        return self._legitimate.copy()
    
    def load_edge_cases(self, reload: bool = False) -> pd.DataFrame:
        """
        Load edge cases
        
        Args:
            reload: Force reload even if cached
            
        Returns:
            DataFrame with edge cases
        """
        if self._edge_cases is None or reload:
            self._edge_cases = pd.read_csv(self.edge_cases_file)
        return self._edge_cases.copy()
    
    def load_all(self, reload: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Load all test cases
        
        Args:
            reload: Force reload even if cached
            
        Returns:
            Dictionary with 'attacks', 'legitimate', 'edge_cases' DataFrames
        """
        return {
            'attacks': self.load_attacks(reload),
            'legitimate': self.load_legitimate(reload),
            'edge_cases': self.load_edge_cases(reload)
        }
    
    def filter_by_category(self, 
                          dataset: str, 
                          category: str) -> pd.DataFrame:
        """
        Filter test cases by category
        
        Args:
            dataset: 'attacks', 'legitimate', or 'edge_cases'
            category: Category name to filter
            
        Returns:
            Filtered DataFrame
        """
        if dataset == 'attacks':
            df = self.load_attacks()
        elif dataset == 'legitimate':
            df = self.load_legitimate()
        elif dataset == 'edge_cases':
            df = self.load_edge_cases()
        else:
            raise ValueError(f"Unknown dataset: {dataset}")
        
        return df[df['category'] == category]
    
    def filter_by_severity(self, severity: str) -> pd.DataFrame:
        """
        Filter attacks by severity
        
        Args:
            severity: 'critical', 'high', 'medium', or 'low'
            
        Returns:
            Filtered DataFrame of attacks
        """
        attacks = self.load_attacks()
        return attacks[attacks['severity'] == severity]
    
    def filter_by_tags(self, 
                      dataset: str, 
                      tags: List[str],
                      match_all: bool = False) -> pd.DataFrame:
        """
        Filter test cases by tags
        
        Args:
            dataset: 'attacks', 'legitimate', or 'edge_cases'
            tags: List of tags to filter by
            match_all: If True, case must have ALL tags.
                      If False, case must have ANY tag.
            
        Returns:
            Filtered DataFrame
        """
        if dataset == 'attacks':
            df = self.load_attacks()
        elif dataset == 'legitimate':
            df = self.load_legitimate()
        elif dataset == 'edge_cases':
            df = self.load_edge_cases()
        else:
            raise ValueError(f"Unknown dataset: {dataset}")
        
        if match_all:
            # Must have all tags
            mask = df['tags'].apply(
                lambda x: all(tag in str(x) for tag in tags)
            )
        else:
            # Must have any tag
            mask = df['tags'].apply(
                lambda x: any(tag in str(x) for tag in tags)
            )
        
        return df[mask]
    
    def get_by_id(self, test_id: str) -> Optional[Dict]:
        """
        Get a specific test case by ID
        
        Args:
            test_id: Test ID (e.g., 'ATK-001', 'LEG-001', 'EDGE-001')
            
        Returns:
            Dict with test case data, or None if not found
        """
        # Determine dataset from ID prefix
        if test_id.startswith('ATK-'):
            df = self.load_attacks()
        elif test_id.startswith('LEG-'):
            df = self.load_legitimate()
        elif test_id.startswith('EDGE-'):
            df = self.load_edge_cases()
        else:
            return None
        
        # Find the test case
        matches = df[df['test_id'] == test_id]
        if len(matches) == 0:
            return None
        
        return matches.iloc[0].to_dict()
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about test data
        
        Returns:
            Dictionary with statistics
        """
        attacks = self.load_attacks()
        legitimate = self.load_legitimate()
        edge_cases = self.load_edge_cases()
        
        stats = {
            'total_cases': len(attacks) + len(legitimate) + len(edge_cases),
            'attacks': {
                'total': len(attacks),
                'by_category': attacks['category'].value_counts().to_dict(),
                'by_severity': attacks['severity'].value_counts().to_dict(),
                'by_action': attacks['expected_action'].value_counts().to_dict()
            },
            'legitimate': {
                'total': len(legitimate),
                'by_category': legitimate['category'].value_counts().to_dict()
            },
            'edge_cases': {
                'total': len(edge_cases),
                'by_category': edge_cases['category'].value_counts().to_dict()
            }
        }
        
        return stats
    
    def export_to_json(self, output_file: str):
        """
        Export all test cases to JSON format
        
        Args:
            output_file: Path to output JSON file
        """
        data = {
            'attacks': self.load_attacks().to_dict('records'),
            'legitimate': self.load_legitimate().to_dict('records'),
            'edge_cases': self.load_edge_cases().to_dict('records')
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Exported {len(data['attacks']) + len(data['legitimate']) + len(data['edge_cases'])} test cases to {output_file}")
    
    def create_test_suite(self, 
                         include_attacks: bool = True,
                         include_legitimate: bool = True,
                         include_edge_cases: bool = True,
                         sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Create a combined test suite
        
        Args:
            include_attacks: Include attack cases
            include_legitimate: Include legitimate cases
            include_edge_cases: Include edge cases
            sample_size: If provided, randomly sample this many from each category
            
        Returns:
            Combined DataFrame
        """
        dfs = []
        
        if include_attacks:
            attacks = self.load_attacks()
            if sample_size:
                attacks = attacks.sample(min(sample_size, len(attacks)))
            dfs.append(attacks)
        
        if include_legitimate:
            legitimate = self.load_legitimate()
            if sample_size:
                legitimate = legitimate.sample(min(sample_size, len(legitimate)))
            dfs.append(legitimate)
        
        if include_edge_cases:
            edge = self.load_edge_cases()
            if sample_size:
                edge = edge.sample(min(sample_size, len(edge)))
            dfs.append(edge)
        
        if not dfs:
            return pd.DataFrame()
        
        # Combine and shuffle
        combined = pd.concat(dfs, ignore_index=True)
        combined = combined.sample(frac=1).reset_index(drop=True)
        
        return combined


# Example usage
if __name__ == "__main__":
    # Initialize loader
    loader = TestDataLoader()
    
    # Load all data
    print("Loading test data...")
    attacks = loader.load_attacks()
    legitimate = loader.load_legitimate()
    edge_cases = loader.load_edge_cases()
    
    print(f"\nLoaded:")
    print(f"  - {len(attacks)} attack cases")
    print(f"  - {len(legitimate)} legitimate cases")
    print(f"  - {len(edge_cases)} edge cases")
    print(f"  - {len(attacks) + len(legitimate) + len(edge_cases)} total")
    
    # Get statistics
    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    
    stats = loader.get_statistics()
    
    print("\nAttacks by Category:")
    for cat, count in sorted(stats['attacks']['by_category'].items()):
        print(f"  {cat:25s}: {count:3d}")
    
    print("\nAttacks by Severity:")
    for sev, count in sorted(stats['attacks']['by_severity'].items()):
        print(f"  {sev:10s}: {count:3d}")
    
    print("\nLegitimate by Category (top 10):")
    leg_cats = stats['legitimate']['by_category']
    for cat, count in sorted(leg_cats.items(), key=lambda x: -x[1])[:10]:
        print(f"  {cat:25s}: {count:3d}")
    
    # Filter examples
    print("\n" + "="*60)
    print("FILTER EXAMPLES")
    print("="*60)
    
    # Critical attacks
    critical = loader.filter_by_severity('critical')
    print(f"\nCritical attacks: {len(critical)}")
    print(critical[['test_id', 'payload']].head(3))
    
    # Jailbreak attacks
    jailbreaks = loader.filter_by_category('attacks', 'jailbreak')
    print(f"\nJailbreak attacks: {len(jailbreaks)}")
    
    # Cases with specific tags
    encoding_attacks = loader.filter_by_tags('attacks', ['encoding'])
    print(f"\nEncoding attacks: {len(encoding_attacks)}")
    
    # Get specific test
    print("\n" + "="*60)
    print("SPECIFIC TEST CASE")
    print("="*60)
    
    test_case = loader.get_by_id('ATK-001')
    if test_case:
        print(f"\nTest ID: {test_case['test_id']}")
        print(f"Category: {test_case['category']}")
        print(f"Severity: {test_case['severity']}")
        print(f"Payload: {test_case['payload']}")
        print(f"Expected Detection: {test_case['expected_detection']}")
        print(f"Expected Risk Score: {test_case['expected_risk_score']}")
    
    # Create test suite
    print("\n" + "="*60)
    print("TEST SUITE CREATION")
    print("="*60)
    
    # Quick test suite (10 from each)
    quick_suite = loader.create_test_suite(sample_size=10)
    print(f"\nQuick test suite: {len(quick_suite)} cases")
    
    # Full test suite
    full_suite = loader.create_test_suite()
    print(f"Full test suite: {len(full_suite)} cases")
    
    # Export to JSON
    print("\n" + "="*60)
    print("EXPORT")
    print("="*60)
    
    output_path = loader.data_dir / 'all_test_cases.json'
    loader.export_to_json(str(output_path))
    print(f"\nExported to: {output_path}")

