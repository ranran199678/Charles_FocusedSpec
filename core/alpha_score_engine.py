import logging
from typing import Dict, List, Optional
from datetime import datetime
import yaml
import os

def try_import(module_name: str, class_name: str):
    """ניסיון ייבוא דינמי של מודול"""
    try:
        module = __import__(module_name, fromlist=[class_name])
        class_obj = getattr(module, class_name)
        return lambda config=None: class_obj(config) if class_obj else None
    except Exception as e:
        logging.warning(f"לא ניתן לייבא {module_name}.{class_name}: {e}")
        return lambda config=None: None

class AlphaScoreEngine:
    """
    מנוע ציון אלפא - מחשב ציון כולל מכל הסוכנים
    """
    
    # משקלים של הסוכנים (רק סוכנים קיימים בפועל)
    AGENT_WEIGHTS = {
        "EnhancedAdvancedAnalyzer": 4,  # סוכן ניתוח טכני מתקדם - משקל גבוה
        "BullishPatternSpotter": 2,     # זיהוי תבניות בולשיות
        "ADXScoreAgent": 2,             # ניתוח מגמות
        "MACDMomentumDetector": 2,      # ניתוח מומנטום
        "ValuationDetector": 3,         # ניתוח הערכה
        "FinancialStabilityAgent": 3,   # יציבות פיננסית
        "NewsCatalystAgent": 2,         # חדשות קטליסטיות
        "SocialMediaHypeScanner": 1,    # מדיה חברתית
        "NLPAnalyzer": 2,               # ניתוח NLP
        "SentimentScorer": 2,           # ניתוח סנטימנט
        "EarningsSurpriseTracker": 2,   # הפתעות רווחים
        "AnalystRatingAgent": 2,        # דירוג אנליסטים
        "GeopoliticalRiskMonitor": 1,   # סיכונים גיאופוליטיים
        "EventScanner": 1,              # סורק אירועים
        "GapDetectorUltimate": 1,       # זיהוי פערים
        "CandlestickAgent": 1,          # ניתוח נרות
        "VolumeSpikeAgent": 1,          # זיהוי גל נפח
        "GoldenCrossDetector": 1,       # זיהוי צלב זהב
        "BollingerSqueeze": 1,          # ניתוח Bollinger
        "SupportZoneStrengthDetector": 1, # ניתוח אזורי תמיכה
        "TrendDetector": 1,             # זיהוי מגמות
        "TrendShiftAgent": 1,           # זיהוי שינויי מגמה
        "VReversalAgent": 1,            # זיהוי היפוכי V
        "ParabolicAgent": 1,            # זיהוי תנועות פרבוליות
        "ReturnForecaster": 1,          # חיזוי תשואות
        "GrowthScanner": 1,             # סריקת צמיחה
        "MidtermMomentumAgent": 1,      # מומנטום בינוני
        "MovingAveragePressureBot": 1,  # לחץ ממוצעים נעים
        "ATRScoreAgent": 1,             # ניתוח ATR
        "MultiAgentValidator": 1,       # אימות רב-סוכן
        "HighConvictionOrchestrator": 1, # אורכיסטרטור ביטחון גבוה
        "BreakoutRetestRecognizer": 1,  # זיהוי פריצות
    }

    def __init__(self, config=None):
        """אתחול מנוע הציון"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # טעינת קונפיגורציה
        self.cfg = self._load_config()
        
        # אתחול הסוכנים (מסונכרן לקבצים הקיימים)
        self.agents = {
            "EnhancedAdvancedAnalyzer": try_import('core.enhanced_advanced_analyzer', 'EnhancedAdvancedAnalyzer')(self.cfg.get("EnhancedAdvancedAnalyzer")),
            "BullishPatternSpotter": try_import('core.bullish_pattern_spotter', 'BullishPatternSpotter')(self.cfg.get("BullishPatternSpotter")),
            "ADXScoreAgent": try_import('core.adx_score_agent', 'ADXScoreAgent')(self.cfg.get("ADXScoreAgent")),
            "MACDMomentumDetector": try_import('core.macd_momentum_detector', 'MACDMomentumDetector')(self.cfg.get("MACDMomentumDetector")),
            "ValuationDetector": try_import('core.valuation_detector', 'ValuationDetector')(self.cfg.get("ValuationDetector")),
            "FinancialStabilityAgent": try_import('core.financial_stability_agent', 'FinancialStabilityAgent')(self.cfg.get("FinancialStabilityAgent")),
            "NewsCatalystAgent": try_import('core.news_catalyst_agent', 'NewsCatalystAgent')(self.cfg.get("NewsCatalystAgent")),
            "SocialMediaHypeScanner": try_import('core.social_media_hype_scanner', 'SocialMediaHypeScanner')(self.cfg.get("SocialMediaHypeScanner")),
            "NLPAnalyzer": try_import('core.nlp_analyzer', 'NLPAnalyzer')(self.cfg.get("NLPAnalyzer")),
            "SentimentScorer": try_import('core.sentiment_scorer', 'SentimentScorer')(self.cfg.get("SentimentScorer")),
            "EarningsSurpriseTracker": try_import('core.earnings_surprise_tracker', 'EarningsSurpriseTracker')(self.cfg.get("EarningsSurpriseTracker")),
            "AnalystRatingAgent": try_import('core.analyst_rating_agent', 'AnalystRatingAgent')(self.cfg.get("AnalystRatingAgent")),
            "GeopoliticalRiskMonitor": try_import('core.geopolitical_risk_monitor', 'GeopoliticalRiskMonitor')(self.cfg.get("GeopoliticalRiskMonitor")),
            "EventScanner": try_import('core.event_scanner', 'EventScanner')(self.cfg.get("EventScanner")),
            "GapDetectorUltimate": try_import('core.gap_detector_ultimate', 'GapDetectorUltimate')(self.cfg.get("GapDetectorUltimate")),
            "CandlestickAgent": try_import('core.candlestick_agent', 'CandlestickAgent')(self.cfg.get("CandlestickAgent")),
            "VolumeSpikeAgent": try_import('core.volume_spike_agent', 'VolumeSpikeAgent')(self.cfg.get("VolumeSpikeAgent")),
            "GoldenCrossDetector": try_import('core.golden_cross_detector', 'GoldenCrossDetector')(self.cfg.get("GoldenCrossDetector")),
            "BollingerSqueeze": try_import('core.bollinger_squeeze', 'BollingerSqueeze')(self.cfg.get("BollingerSqueeze")),
            "SupportZoneStrengthDetector": try_import('core.support_zone_strength_detector', 'SupportZoneStrengthDetector')(self.cfg.get("SupportZoneStrengthDetector")),
            "TrendDetector": try_import('core.trend_detector', 'TrendDetector')(self.cfg.get("TrendDetector")),
            "TrendShiftAgent": try_import('core.trend_shift_agent', 'TrendShiftAgent')(self.cfg.get("TrendShiftAgent")),
            "VReversalAgent": try_import('core.v_reversal_agent', 'VReversalAgent')(self.cfg.get("VReversalAgent")),
            "ParabolicAgent": try_import('core.parabolic_agent', 'ParabolicAgent')(self.cfg.get("ParabolicAgent")),
            "ReturnForecaster": try_import('core.return_forecaster', 'ReturnForecaster')(self.cfg.get("ReturnForecaster")),
            "GrowthScanner": try_import('core.growth_scanner', 'GrowthScanner')(self.cfg.get("GrowthScanner")),
            "MidtermMomentumAgent": try_import('core.midterm_momentum_agent', 'MidtermMomentumAgent')(self.cfg.get("MidtermMomentumAgent")),
            "MovingAveragePressureBot": try_import('core.moving_average_pressure_bot', 'MovingAveragePressureBot')(self.cfg.get("MovingAveragePressureBot")),
            "ATRScoreAgent": try_import('core.atr_score_agent', 'ATRScoreAgent')(self.cfg.get("ATRScoreAgent")),
            "MultiAgentValidator": try_import('core.multi_agent_validator', 'MultiAgentValidator')(self.cfg.get("MultiAgentValidator")),
            "HighConvictionOrchestrator": try_import('core.high_conviction_orchestrator', 'HighConvictionOrchestrator')(self.cfg.get("HighConvictionOrchestrator")),
            "BreakoutRetestRecognizer": try_import('core.breakout_retest_recognizer', 'BreakoutRetestRecognizer')(self.cfg.get("BreakoutRetestRecognizer")),
        }
        
        # הסרת סוכנים שלא נטענו
        self.agents = {k: v for k, v in self.agents.items() if v is not None}
        
        self.logger.info(f"AlphaScoreEngine אותחל עם {len(self.agents)} סוכנים")

    def _load_config(self) -> Dict:
        """טעינת קונפיגורציה מקובץ"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"לא ניתן לטעון קונפיגורציה: {e}")
        
        return {}

    def evaluate(self, symbol: str, price_data=None) -> Dict:
        """
        הערכת מניה על ידי כל הסוכנים
        """
        try:
            self.logger.info(f"מתחיל הערכה של {symbol}")
            
            agent_scores = {}
            agent_details = {}
            total_weight = 0
            weighted_sum = 0
            
            # הרצת כל הסוכנים
            for agent_name, agent in self.agents.items():
                try:
                    if agent is None:
                        continue
                        
                    self.logger.info(f"מריץ {agent_name} עבור {symbol}")
                    
                    # הרצת הסוכן
                    if hasattr(agent, 'analyze'):
                        # בדיקה אם הסוכן מקבל 2 או 3 פרמטרים
                        import inspect
                        sig = inspect.signature(agent.analyze)
                        
                        try:
                            if len(sig.parameters) == 2:
                                result = agent.analyze(symbol)
                            elif len(sig.parameters) == 3:
                                # התאמה לסוכנים ספציפיים
                                if agent_name == "TrendShiftAgent":
                                    # TrendShiftAgent ייתכן ודורש symbol ב-__init__
                                    try:
                                        agent = type(agent)('TEST')  # יצירת instance חדש
                                        result = agent.analyze(symbol, price_data)
                                    except:
                                        result = agent.analyze(symbol, price_data)
                                elif agent_name == "ParabolicAgent":
                                    # ParabolicAgent דורש price_df
                                    result = agent.analyze(symbol, price_data)
                                elif agent_name == "ADXScoreAgent":
                                    # ADXScoreAgent צריך עמודות קטנות
                                    if price_data is not None:
                                        adapted_data = price_data.copy()
                                        adapted_data.columns = [col.lower() for col in adapted_data.columns]
                                        result = agent.analyze(symbol, adapted_data)
                                    else:
                                        result = agent.analyze(symbol)
                                else:
                                    result = agent.analyze(symbol, price_data)
                            else:
                                # יותר מ-3 פרמטרים - נסה עם 2
                                result = agent.analyze(symbol)
                        except Exception as e:
                            self.logger.error(f"שגיאה בהרצת {agent_name}: {e}")
                            continue
                        
                        if isinstance(result, dict):
                            score = result.get('score', 50)
                            details = result.get('details', {})
                            explanation = result.get('explanation', '')
                            
                            agent_scores[agent_name] = score
                            agent_details[agent_name] = {
                                'score': score,
                                'details': details,
                                'explanation': explanation
                            }
                            
                            # חישוב משקל
                            weight = self.AGENT_WEIGHTS.get(agent_name, 1)
                            total_weight += weight
                            weighted_sum += score * weight
                            
                            self.logger.info(f"{agent_name}: ציון {score}, משקל {weight}")
                        else:
                            self.logger.warning(f"{agent_name} החזיר תוצאה לא תקינה")
                    
                except Exception as e:
                    self.logger.error(f"שגיאה ב-{agent_name}: {e}")
                    continue
            
            # חישוב ציון כולל
            final_score = int(weighted_sum / total_weight) if total_weight > 0 else 50
            
            # יצירת תוצאה
            result = {
                'symbol': symbol,
                'final_score': final_score,
                'agent_scores': agent_scores,
                'agent_details': agent_details,
                'total_weight': total_weight,
                'agents_count': len(agent_scores),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"הערכה הושלמה עבור {symbol}: ציון {final_score}")
            return result
            
        except Exception as e:
            self.logger.error(f"שגיאה בהערכה של {symbol}: {e}")
            return {
                'symbol': symbol,
                'final_score': 50,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_agent_status(self) -> Dict:
        """קבלת סטטוס הסוכנים"""
        return {
            'total_agents': len(self.AGENT_WEIGHTS),
            'loaded_agents': len(self.agents),
            'agent_weights': self.AGENT_WEIGHTS,
            'loaded_agent_names': list(self.agents.keys())
        }
