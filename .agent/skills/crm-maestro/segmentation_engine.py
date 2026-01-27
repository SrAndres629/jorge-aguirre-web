"""
CRM Maestro: RFM Segmentation Engine
Doctoral Level Implementation for Jorge Aguirre Flores Web
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple

class RFMEngine:
    """
    Advanced engine for calculating Recency, Frequency, and Monetary scores.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Expects a DataFrame with: ['user_id', 'transaction_date', 'amount']
        """
        self.data = data
        self.reference_date = datetime.now()
        
    def calculate_scores(self) -> pd.DataFrame:
        """
        Performs RFM analysis and returns a scored DataFrame.
        """
        rfm = self.data.groupby('user_id').agg({
            'transaction_date': lambda x: (self.reference_date - x.max()).days,
            'user_id': 'count',
            'amount': 'sum'
        })
        
        rfm.columns = ['recency', 'frequency', 'monetary']
        
        # Scoring (1-5, where 5 is best)
        # For Recency, lower is better
        rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
        rfm['f_score'] = pd.qcut(rfm['frequency'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        
        rfm['rfm_score'] = rfm[['r_score', 'f_score', 'm_score']].sum(axis=1)
        rfm['segment'] = rfm.apply(self._assign_segment, axis=1)
        
        return rfm

    def _assign_segment(self, row: pd.Series) -> str:
        """
        Assigns human-readable segments based on RFM logic.
        """
        score = row['rfm_score']
        r = int(row['r_score'])
        f = int(row['f_score'])
        
        if score >= 13: return "Champions"
        if score >= 10: return "Loyal Customers"
        if score >= 8: return "Potential Loyalists"
        if r >= 4 and f <= 2: return "New Customers"
        if r <= 2: return "At Risk"
        return "Hibernating"

    def get_segment_summary(self) -> Dict:
        """
        Returns an impact report for the Master Orchestrator.
        """
        rfm = self.calculate_scores()
        summary = rfm.groupby('segment').agg({
            'user_id': 'count',
            'monetary': 'mean',
            'recency': 'mean'
        }).to_dict()
        return summary

if __name__ == "__main__":
    # Internal Audit Test
    print("Running Internal CRM Audit...")
    # Mock data for verification
    test_data = pd.DataFrame([
        {'user_id': 1, 'transaction_date': datetime(2025, 12, 1), 'amount': 500},
        {'user_id': 2, 'transaction_date': datetime(2026, 1, 20), 'amount': 1500},
        {'user_id': 1, 'transaction_date': datetime(2026, 1, 25), 'amount': 200}
    ])
    engine = RFMEngine(test_data)
    print(engine.calculate_scores())
