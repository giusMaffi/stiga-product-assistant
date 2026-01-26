"""
Statistics Utilities for Analytics
Chi-square test per CTR comparison
"""
from scipy.stats import chi2_contingency
from typing import Dict, Tuple

def chi_square_ctr_test(period_a: Dict, period_b: Dict) -> Dict:
    """
    Chi-square test per confronto CTR tra due periodi
    
    Args:
        period_a: {'clicks': int, 'products_shown': int}
        period_b: {'clicks': int, 'products_shown': int}
    
    Returns:
        {
            'p_value': float,
            'is_significant': bool,
            'confidence': str,
            'chi2_statistic': float
        }
    """
    clicks_a = period_a.get('clicks', 0)
    shown_a = period_a.get('products_shown', 0)
    clicks_b = period_b.get('clicks', 0)
    shown_b = period_b.get('products_shown', 0)
    
    # Edge cases
    if shown_a == 0 or shown_b == 0:
        return {
            'p_value': 1.0,
            'is_significant': bool(False),
            'confidence': None,
            'chi2_statistic': 0.0,
            'error': 'Insufficient data for comparison'
        }
    
    # Contingency table: [[clicked, not_clicked], [clicked, not_clicked]]
    not_clicked_a = shown_a - clicks_a
    not_clicked_b = shown_b - clicks_b
    
    contingency_table = [
        [clicks_a, not_clicked_a],
        [clicks_b, not_clicked_b]
    ]
    
    try:
        chi2, p_value, dof, expected = chi2_contingency(contingency_table)
        
        # Determine confidence level
        if p_value < 0.01:
            confidence = '99%'
        elif p_value < 0.05:
            confidence = '95%'
        elif p_value < 0.10:
            confidence = '90%'
        else:
            confidence = None
        
        return {
            'p_value': round(p_value, 4),
            'is_significant': bool(p_value < 0.05),
            'confidence': confidence,
            'chi2_statistic': round(chi2, 2)
        }
    
    except Exception as e:
        return {
            'p_value': 1.0,
            'is_significant': bool(False),
            'confidence': None,
            'chi2_statistic': 0.0,
            'error': str(e)
        }


def calculate_delta(value_a: float, value_b: float, is_percentage: bool = False) -> Dict:
    """
    Calcola variazione tra due valori
    
    Args:
        value_a: Valore periodo A
        value_b: Valore periodo B
        is_percentage: Se True, calcola delta in punti percentuali (pp)
    
    Returns:
        {
            'absolute': float,  # Differenza assoluta
            'percent': float,   # Variazione percentuale (o pp se is_percentage=True)
            'direction': str    # 'increase', 'decrease', 'neutral'
        }
    """
    if value_a == 0:
        if value_b == 0:
            return {'absolute': 0, 'percent': 0, 'direction': 'neutral'}
        else:
            return {'absolute': value_b, 'percent': float('inf'), 'direction': 'increase'}
    
    absolute_delta = value_b - value_a
    
    if is_percentage:
        # Per percentuali (CTR), usa punti percentuali
        percent_delta = absolute_delta
    else:
        # Per conteggi, usa variazione percentuale
        percent_delta = (absolute_delta / value_a) * 100
    
    if absolute_delta > 0:
        direction = 'increase'
    elif absolute_delta < 0:
        direction = 'decrease'
    else:
        direction = 'neutral'
    
    return {
        'absolute': round(absolute_delta, 2),
        'percent': round(percent_delta, 2),
        'direction': direction
    }


def format_significance_badge(stats: Dict) -> str:
    """
    Formatta badge HTML per significatività statistica
    
    Args:
        stats: Output di chi_square_ctr_test()
    
    Returns:
        HTML badge string
    """
    if not stats.get('is_significant'):
        return ''
    
    confidence = stats.get('confidence', '95%')
    p_value = stats.get('p_value', 0)
    
    return f'<span class="significance-badge" title="p={p_value}, {confidence} confidence">✨ Significativo</span>'