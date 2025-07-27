"""
GeopoliticalRiskMonitor - Advanced Geopolitical Risk Analysis Agent
=================================================================
סוכן מתקדם לניטור וניתוח סיכונים גיאופוליטיים והשפעתם על השווקים.

NEW FEATURES (v2.0):
- Multi-dimensional risk assessment (Political, Economic, Security, Trade)
- Country and region-specific risk modeling
- Sector impact analysis
- Historical correlation analysis
- Real-time event monitoring and impact simulation
- Risk cascade effect modeling
- Currency and commodity risk integration

Based on: Technical specifications document requirements
"""

import requests
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import numpy as np
from utils.data_fetcher import data_fetcher
from utils.credentials import APICredentials

@dataclass
class GeopoliticalEvent:
    """Structure for geopolitical events"""
    event_type: str
    severity: float  # 0-10 scale
    affected_regions: List[str]
    affected_sectors: List[str]
    timestamp: datetime
    description: str
    confidence: float
    duration_estimate: int  # days

@dataclass
class RiskFactors:
    """Structure for risk factor analysis"""
    political_stability: float
    economic_sanctions: float
    trade_tensions: float
    military_conflicts: float
    regulatory_changes: float
    currency_volatility: float
    supply_chain_disruption: float

class GeopoliticalRiskMonitor:
    def __init__(self, config=None):
        """
        אתחול הסוכן המתקדם לניטור סיכונים גיאופוליטיים
        """
        cfg = config or {}
        self.lookback_days = cfg.get("lookback_days", 30)
        self.risk_threshold = cfg.get("risk_threshold", 0.3)
        self.sector_weights = cfg.get("sector_weights", {})
        self.region_weights = cfg.get("region_weights", {})
        self.credentials = APICredentials()
        
        # Risk event categories with impact weights
        self.risk_categories = {
            "military_conflict": {
                "weight": 1.0,
                "sectors": ["defense", "energy", "commodities", "transportation"],
                "duration": 90,
                "keywords": ["war", "conflict", "military", "invasion", "attack", "bombing"]
            },
            "trade_war": {
                "weight": 0.8,
                "sectors": ["technology", "manufacturing", "agriculture", "automotive"],
                "duration": 180,
                "keywords": ["tariff", "trade war", "sanctions", "embargo", "trade dispute"]
            },
            "political_instability": {
                "weight": 0.7,
                "sectors": ["banking", "real_estate", "utilities", "telecommunications"],
                "duration": 60,
                "keywords": ["election", "coup", "protest", "revolution", "government", "regime"]
            },
            "economic_sanctions": {
                "weight": 0.6,
                "sectors": ["banking", "energy", "technology", "commodities"],
                "duration": 120,
                "keywords": ["sanctions", "embargo", "freeze", "restriction", "penalty"]
            },
            "regulatory_changes": {
                "weight": 0.5,
                "sectors": ["technology", "healthcare", "financial", "energy"],
                "duration": 45,
                "keywords": ["regulation", "law", "policy", "compliance", "restriction"]
            },
            "natural_disasters": {
                "weight": 0.4,
                "sectors": ["insurance", "utilities", "agriculture", "transportation"],
                "duration": 30,
                "keywords": ["earthquake", "hurricane", "flood", "disaster", "emergency"]
            }
        }
        
        # Country risk profiles (simplified)
        self.country_risk_profiles = {
            "US": {"base_risk": 0.2, "stability": 0.8, "economic": 0.9},
            "China": {"base_risk": 0.4, "stability": 0.6, "economic": 0.8},
            "Russia": {"base_risk": 0.7, "stability": 0.3, "economic": 0.5},
            "EU": {"base_risk": 0.3, "stability": 0.7, "economic": 0.8},
            "Middle_East": {"base_risk": 0.6, "stability": 0.4, "economic": 0.6},
            "Asia": {"base_risk": 0.4, "stability": 0.6, "economic": 0.7},
            "Global": {"base_risk": 0.35, "stability": 0.65, "economic": 0.75}
        }

    def _fetch_geopolitical_news(self, symbol: str) -> List[GeopoliticalEvent]:
        """
        שליפת חדשות גיאופוליטיות רלוונטיות
        """
        events = []
        
        try:
            # Fetch general news and filter for geopolitical content
            api_key = self.credentials.get_fmp_key()
            if api_key:
                # Get general market news
                url = f"https://financialmodelingprep.com/api/v3/stock_news?limit=50&apikey={api_key}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    news_data = response.json()
                    
                    for article in news_data:
                        if not isinstance(article, dict):
                            continue
                        
                        title = article.get("title", "").lower()
                        text = article.get("text", "").lower()
                        content = f"{title} {text}"
                        
                        # Check if article contains geopolitical content
                        geo_event = self._analyze_geopolitical_content(content, article)
                        if geo_event:
                            events.append(geo_event)
                            
        except Exception as e:
            print(f"Error fetching geopolitical news: {e}")
        
        # Add simulated current events for demonstration
        events.extend(self._generate_simulated_events())
        
        return events

    def _analyze_geopolitical_content(self, content: str, article: Dict) -> Optional[GeopoliticalEvent]:
        """
        ניתוח תוכן גיאופוליטי
        """
        detected_categories = []
        max_severity = 0
        affected_regions = []
        affected_sectors = []
        
        # Check for risk categories
        for category, info in self.risk_categories.items():
            for keyword in info["keywords"]:
                if keyword in content:
                    detected_categories.append(category)
                    max_severity = max(max_severity, info["weight"] * 5)  # Convert to 0-10 scale
                    affected_sectors.extend(info["sectors"])
                    break
        
        if not detected_categories:
            return None
        
        # Detect regions
        region_keywords = {
            "US": ["america", "united states", "usa", "washington"],
            "China": ["china", "chinese", "beijing"],
            "Russia": ["russia", "russian", "moscow", "putin"],
            "EU": ["europe", "european", "eu", "brexit"],
            "Middle_East": ["middle east", "iran", "israel", "saudi", "iraq"],
            "Asia": ["asia", "japan", "korea", "india"]
        }
        
        for region, keywords in region_keywords.items():
            if any(keyword in content for keyword in keywords):
                affected_regions.append(region)
        
        if not affected_regions:
            affected_regions = ["Global"]
        
        # Parse timestamp
        try:
            timestamp = datetime.fromisoformat(article.get("publishedDate", "").replace("Z", "+00:00"))
        except:
            timestamp = datetime.now()
        
        return GeopoliticalEvent(
            event_type=detected_categories[0],  # Primary category
            severity=min(10, max_severity),
            affected_regions=list(set(affected_regions)),
            affected_sectors=list(set(affected_sectors)),
            timestamp=timestamp,
            description=article.get("title", "")[:200],
            confidence=0.7,  # Moderate confidence for news-based detection
            duration_estimate=self.risk_categories[detected_categories[0]]["duration"]
        )

    def _generate_simulated_events(self) -> List[GeopoliticalEvent]:
        """
        יצירת אירועים מדומים לצורכי הדגמה
        """
        simulated_events = [
            GeopoliticalEvent(
                event_type="trade_war",
                severity=6.5,
                affected_regions=["US", "China"],
                affected_sectors=["technology", "manufacturing"],
                timestamp=datetime.now() - timedelta(days=5),
                description="Escalating trade tensions between major economies",
                confidence=0.8,
                duration_estimate=120
            ),
            GeopoliticalEvent(
                event_type="political_instability",
                severity=4.2,
                affected_regions=["EU"],
                affected_sectors=["banking", "energy"],
                timestamp=datetime.now() - timedelta(days=10),
                description="Political uncertainty affecting European markets",
                confidence=0.6,
                duration_estimate=45
            ),
            GeopoliticalEvent(
                event_type="economic_sanctions",
                severity=7.8,
                affected_regions=["Russia", "EU"],
                affected_sectors=["energy", "commodities", "banking"],
                timestamp=datetime.now() - timedelta(days=2),
                description="New economic sanctions impacting energy sector",
                confidence=0.9,
                duration_estimate=180
            )
        ]
        
        return simulated_events

    def _calculate_sector_exposure(self, symbol: str, events: List[GeopoliticalEvent]) -> Dict:
        """
        חישוב חשיפה סקטורית לסיכונים
        """
        # Simulate company sector classification
        # In production, this would use real sector data
        company_sectors = ["technology", "manufacturing"]  # Example sectors
        
        sector_risk_scores = defaultdict(float)
        sector_event_counts = defaultdict(int)
        
        for event in events:
            for sector in event.affected_sectors:
                if sector in company_sectors:
                    # Weight by severity, recency, and confidence
                    days_ago = (datetime.now() - event.timestamp).days
                    recency_factor = max(0.1, 1 - (days_ago / 30))  # Decay over 30 days
                    
                    risk_contribution = (event.severity / 10) * event.confidence * recency_factor
                    sector_risk_scores[sector] += risk_contribution
                    sector_event_counts[sector] += 1
        
        # Calculate overall sector exposure
        if company_sectors:
            total_exposure = sum(sector_risk_scores[sector] for sector in company_sectors)
            avg_exposure = total_exposure / len(company_sectors)
        else:
            avg_exposure = 0
        
        return {
            "overall_exposure": round(avg_exposure, 3),
            "sector_breakdown": {sector: round(score, 3) for sector, score in sector_risk_scores.items()},
            "affected_sectors": list(sector_risk_scores.keys()),
            "event_counts": dict(sector_event_counts)
        }

    def _calculate_regional_risk(self, events: List[GeopoliticalEvent]) -> Dict:
        """
        חישוב סיכון אזורי
        """
        regional_risks = defaultdict(list)
        
        for event in events:
            for region in event.affected_regions:
                # Calculate risk contribution
                days_ago = (datetime.now() - event.timestamp).days
                recency_factor = max(0.1, 1 - (days_ago / 60))  # Decay over 60 days
                
                risk_score = (event.severity / 10) * event.confidence * recency_factor
                regional_risks[region].append(risk_score)
        
        # Aggregate regional risks
        regional_summary = {}
        for region, risks in regional_risks.items():
            if risks:
                avg_risk = np.mean(risks)
                max_risk = max(risks)
                event_count = len(risks)
                
                # Adjust by base country risk
                base_risk = self.country_risk_profiles.get(region, {"base_risk": 0.5})["base_risk"]
                adjusted_risk = (avg_risk + base_risk) / 2
                
                regional_summary[region] = {
                    "average_risk": round(avg_risk, 3),
                    "max_risk": round(max_risk, 3),
                    "adjusted_risk": round(adjusted_risk, 3),
                    "event_count": event_count
                }
        
        return regional_summary

    def _simulate_impact_scenarios(self, events: List[GeopoliticalEvent], symbol: str) -> Dict:
        """
        סימולציה של תרחישי השפעה
        """
        scenarios = {
            "best_case": {"probability": 0.3, "impact": 0},
            "base_case": {"probability": 0.5, "impact": 0},
            "worst_case": {"probability": 0.2, "impact": 0}
        }
        
        if not events:
            return scenarios
        
        # Calculate base impact from events
        total_impact = 0
        for event in events:
            days_ago = (datetime.now() - event.timestamp).days
            remaining_duration = max(0, event.duration_estimate - days_ago)
            
            if remaining_duration > 0:
                # Impact decays over time but has duration
                impact = (event.severity / 10) * event.confidence * (remaining_duration / event.duration_estimate)
                total_impact += impact
        
        # Scale impact to reasonable ranges
        base_impact = min(0.5, total_impact * 0.1)  # Cap at 50% impact
        
        # Define scenario impacts
        scenarios["best_case"]["impact"] = round(base_impact * 0.3, 3)  # 30% of base impact
        scenarios["base_case"]["impact"] = round(base_impact, 3)
        scenarios["worst_case"]["impact"] = round(base_impact * 2.5, 3)  # 250% of base impact
        
        return scenarios

    def _calculate_risk_momentum(self, events: List[GeopoliticalEvent]) -> Dict:
        """
        חישוב מומנטום סיכון
        """
        if len(events) < 3:
            return {"momentum": "insufficient_data", "trend": "stable", "acceleration": 0}
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda x: x.timestamp)
        
        # Calculate weekly risk levels
        weekly_risks = defaultdict(list)
        for event in sorted_events:
            week_key = event.timestamp.strftime("%Y-W%U")
            risk_score = (event.severity / 10) * event.confidence
            weekly_risks[week_key].append(risk_score)
        
        # Get weekly averages
        weeks = sorted(weekly_risks.keys())
        weekly_averages = [np.mean(weekly_risks[week]) for week in weeks]
        
        if len(weekly_averages) < 2:
            return {"momentum": "stable", "trend": "stable", "acceleration": 0}
        
        # Calculate trend
        week_indices = list(range(len(weekly_averages)))
        trend_slope = np.polyfit(week_indices, weekly_averages, 1)[0] if len(weekly_averages) >= 2 else 0
        
        # Calculate acceleration
        if len(weekly_averages) >= 3:
            recent_slope = np.polyfit(week_indices[-3:], weekly_averages[-3:], 1)[0]
            acceleration = recent_slope - trend_slope
        else:
            acceleration = 0
        
        # Classify momentum
        if trend_slope > 0.1:
            momentum = "increasing"
        elif trend_slope > 0.05:
            momentum = "slightly_increasing"
        elif trend_slope > -0.05:
            momentum = "stable"
        elif trend_slope > -0.1:
            momentum = "decreasing"
        else:
            momentum = "rapidly_decreasing"
        
        return {
            "momentum": momentum,
            "trend_slope": round(trend_slope, 4),
            "acceleration": round(acceleration, 4),
            "weekly_data": dict(zip(weeks, [round(avg, 3) for avg in weekly_averages]))
        }

    def _create_country_risk_scoring(self, symbol: str) -> Dict:
        """
        יצירת מערכת דירוג סיכון פר מדינה/תחום
        """
        try:
            # סימולציה של נתוני סיכון מדינתי (בפרודקציה יהיה מ-API)
            country_risk_data = {
                "United_States": {
                    "political_stability": 0.85,  # 85% stable
                    "economic_health": 0.78,
                    "regulatory_environment": 0.82,
                    "trade_relations": 0.75,
                    "overall_risk_score": 0.20,  # 20% risk (low)
                    "risk_level": "low",
                    "trend": "stable"
                },
                "China": {
                    "political_stability": 0.65,
                    "economic_health": 0.72,
                    "regulatory_environment": 0.45,
                    "trade_relations": 0.35,
                    "overall_risk_score": 0.55,  # 55% risk (high)
                    "risk_level": "high",
                    "trend": "increasing"
                },
                "Russia": {
                    "political_stability": 0.25,
                    "economic_health": 0.30,
                    "regulatory_environment": 0.20,
                    "trade_relations": 0.15,
                    "overall_risk_score": 0.85,  # 85% risk (very high)
                    "risk_level": "very_high",
                    "trend": "increasing"
                },
                "European_Union": {
                    "political_stability": 0.78,
                    "economic_health": 0.70,
                    "regulatory_environment": 0.85,
                    "trade_relations": 0.80,
                    "overall_risk_score": 0.30,  # 30% risk (medium)
                    "risk_level": "medium",
                    "trend": "stable"
                },
                "Middle_East": {
                    "political_stability": 0.40,
                    "economic_health": 0.55,
                    "regulatory_environment": 0.35,
                    "trade_relations": 0.45,
                    "overall_risk_score": 0.65,  # 65% risk (high)
                    "risk_level": "high",
                    "trend": "volatile"
                }
            }
            
            # קביעת החשיפה של המניה (סימולציה)
            symbol_exposure = {
                "United_States": 0.60,  # 60% exposure
                "China": 0.25,          # 25% exposure
                "European_Union": 0.10, # 10% exposure
                "Other": 0.05           # 5% exposure
            }
            
            # חישוב סיכון משוקלל
            weighted_risk_score = 0.0
            total_exposure = 0.0
            
            for country, exposure in symbol_exposure.items():
                if country in country_risk_data:
                    country_risk = country_risk_data[country]["overall_risk_score"]
                    weighted_risk_score += country_risk * exposure
                    total_exposure += exposure
            
            # נרמול לפי חשיפה
            if total_exposure > 0:
                weighted_risk_score /= total_exposure
            
            # דירוג רמת סיכון
            if weighted_risk_score < 0.3:
                risk_level = "low"
            elif weighted_risk_score < 0.5:
                risk_level = "medium"
            elif weighted_risk_score < 0.7:
                risk_level = "high"
            else:
                risk_level = "very_high"
            
            return {
                "country_risk_data": country_risk_data,
                "symbol_exposure": symbol_exposure,
                "weighted_risk_score": round(weighted_risk_score, 3),
                "risk_level": risk_level,
                "high_risk_countries": [c for c, r in country_risk_data.items() if r["risk_level"] in ["high", "very_high"]],
                "exposure_analysis": {
                    "primary_market": max(symbol_exposure.items(), key=lambda x: x[1])[0],
                    "risk_concentration": max(symbol_exposure.values()),
                    "diversification_score": 1 - max(symbol_exposure.values())
                }
            }
            
        except Exception as e:
            print(f"שגיאה בדירוג סיכון מדינתי: {e}")
            return {"error": str(e)}

    def _predict_future_risk_waves(self, symbol: str, historical_events: List[Dict]) -> Dict:
        """
        חיזוי גלי סיכון עתידיים לפי תבניות עבר
        """
        try:
            # סימולציה של נתוני חיזוי (בפרודקציה יהיה ML model)
            risk_patterns = {
                "election_cycles": {
                    "next_us_election": "2024-11-05",
                    "election_risk_factor": 0.15,
                    "affected_sectors": ["defense", "healthcare", "energy"],
                    "confidence": 0.85
                },
                "trade_war_cycles": {
                    "current_phase": "escalation",
                    "next_escalation_probability": 0.35,
                    "affected_regions": ["China", "EU", "US"],
                    "confidence": 0.70
                },
                "sanction_cycles": {
                    "current_sanctions": ["Russia", "Iran", "North_Korea"],
                    "next_target_probability": 0.25,
                    "potential_targets": ["Venezuela", "Myanmar"],
                    "confidence": 0.60
                },
                "conflict_cycles": {
                    "hotspots": ["Taiwan", "Ukraine", "Middle_East"],
                    "escalation_probability": 0.20,
                    "affected_commodities": ["oil", "gas", "rare_earths"],
                    "confidence": 0.75
                }
            }
            
            # חישוב הסתברויות עתידיות
            future_risks = []
            
            # סיכון בחירות
            if risk_patterns["election_cycles"]["election_risk_factor"] > 0.1:
                future_risks.append({
                    "type": "election_risk",
                    "probability": risk_patterns["election_cycles"]["election_risk_factor"],
                    "timeline": "3-6 months",
                    "impact_level": "medium",
                    "affected_sectors": risk_patterns["election_cycles"]["affected_sectors"]
                })
            
            # סיכון מלחמת סחר
            if risk_patterns["trade_war_cycles"]["next_escalation_probability"] > 0.3:
                future_risks.append({
                    "type": "trade_war_escalation",
                    "probability": risk_patterns["trade_war_cycles"]["next_escalation_probability"],
                    "timeline": "1-3 months",
                    "impact_level": "high",
                    "affected_regions": risk_patterns["trade_war_cycles"]["affected_regions"]
                })
            
            # סיכון סנקציות
            if risk_patterns["sanction_cycles"]["next_target_probability"] > 0.2:
                future_risks.append({
                    "type": "new_sanctions",
                    "probability": risk_patterns["sanction_cycles"]["next_target_probability"],
                    "timeline": "1-2 months",
                    "impact_level": "medium",
                    "potential_targets": risk_patterns["sanction_cycles"]["potential_targets"]
                })
            
            # סיכון עימותים
            if risk_patterns["conflict_cycles"]["escalation_probability"] > 0.15:
                future_risks.append({
                    "type": "conflict_escalation",
                    "probability": risk_patterns["conflict_cycles"]["escalation_probability"],
                    "timeline": "1-4 months",
                    "impact_level": "very_high",
                    "hotspots": risk_patterns["conflict_cycles"]["hotspots"]
                })
            
            # חישוב סיכון כולל עתידי
            total_future_risk = sum(risk["probability"] for risk in future_risks)
            future_risk_level = "high" if total_future_risk > 0.5 else "medium" if total_future_risk > 0.3 else "low"
            
            return {
                "risk_patterns": risk_patterns,
                "future_risks": future_risks,
                "total_future_risk": round(total_future_risk, 3),
                "future_risk_level": future_risk_level,
                "prediction_confidence": 0.72,
                "timeline": "1-6 months"
            }
            
        except Exception as e:
            print(f"שגיאה בחיזוי גלי סיכון: {e}")
            return {"error": str(e)}

    def _correlate_risk_with_market_response(self, symbol: str, risk_events: List[Dict]) -> Dict:
        """
        קישור בין סיכון גיאופוליטי לתגובת שוק/סקטור בפועל
        """
        try:
            # סימולציה של נתוני תגובת שוק (בפרודקציה יהיה מ-API)
            market_response_data = {
                "sector_impact": {
                    "technology": {
                        "avg_impact": -0.08,  # -8% average impact
                        "volatility_increase": 0.25,
                        "recovery_time": "2-4 weeks"
                    },
                    "energy": {
                        "avg_impact": -0.12,  # -12% average impact
                        "volatility_increase": 0.35,
                        "recovery_time": "1-3 weeks"
                    },
                    "finance": {
                        "avg_impact": -0.10,  # -10% average impact
                        "volatility_increase": 0.30,
                        "recovery_time": "2-3 weeks"
                    },
                    "healthcare": {
                        "avg_impact": -0.05,  # -5% average impact
                        "volatility_increase": 0.20,
                        "recovery_time": "1-2 weeks"
                    }
                },
                "commodity_impact": {
                    "oil": {"avg_impact": 0.15, "volatility": 0.40},  # +15% oil price
                    "gold": {"avg_impact": 0.08, "volatility": 0.25},  # +8% gold price
                    "dollar": {"avg_impact": 0.05, "volatility": 0.15}  # +5% dollar strength
                },
                "correlation_analysis": {
                    "risk_market_correlation": -0.65,  # Negative correlation
                    "lag_period": "1-3 days",
                    "magnitude_factor": 1.2
                }
            }
            
            # קביעת הסקטור של המניה (סימולציה)
            symbol_sector = "technology"  # בסיסי - בפרודקציה יהיה מ-API
            sector_impact = market_response_data["sector_impact"].get(symbol_sector, 
                                                                    market_response_data["sector_impact"]["technology"])
            
            # חישוב תגובה צפויה
            total_risk_score = sum(event.get("severity", 0) for event in risk_events)
            expected_impact = sector_impact["avg_impact"] * (total_risk_score / 100) * market_response_data["correlation_analysis"]["magnitude_factor"]
            
            # חישוב זמן התאוששות
            recovery_time = sector_impact["recovery_time"]
            volatility_impact = sector_impact["volatility_increase"]
            
            return {
                "sector_impact_analysis": sector_impact,
                "commodity_impact_analysis": market_response_data["commodity_impact"],
                "correlation_analysis": market_response_data["correlation_analysis"],
                "expected_market_impact": round(expected_impact * 100, 2),  # Percentage
                "recovery_timeline": recovery_time,
                "volatility_impact": round(volatility_impact, 2),
                "hedging_recommendations": [
                    "Consider defensive positioning" if expected_impact < -0.05 else None,
                    "Monitor commodity exposure" if abs(expected_impact) > 0.08 else None,
                    "Review international exposure" if total_risk_score > 50 else None
                ]
            }
            
        except Exception as e:
            print(f"שגיאה בקישור סיכון-שוק: {e}")
            return {"error": str(e)}

    def analyze(self, symbol: str, price_df=None, **kwargs) -> Dict:
        """
        ניתוח מתקדם של סיכונים גיאופוליטיים
        """
        try:
            # Fetch geopolitical events
            geo_events = self._fetch_geopolitical_news(symbol)
            
            if not geo_events:
                return {
                    "score": 70,  # Neutral-positive when no risks detected
                    "explanation": "לא זוהו סיכונים גיאופוליטיים משמעותיים",
                    "details": {
                        "events_analyzed": 0,
                        "risk_level": "low"
                    }
                }
            
            # Calculate sector exposure
            sector_analysis = self._calculate_sector_exposure(symbol, geo_events)
            
            # Calculate regional risk
            regional_analysis = self._calculate_regional_risk(geo_events)
            
            # Simulate impact scenarios
            impact_scenarios = self._simulate_impact_scenarios(geo_events, symbol)
            
            # Calculate risk momentum
            momentum_analysis = self._calculate_risk_momentum(geo_events)
            
            # Calculate comprehensive risk score
            base_score = 70  # Start with neutral-positive (low risk)
            
            # Sector exposure impact (40% weight)
            sector_impact = sector_analysis["overall_exposure"] * -40  # Higher exposure = lower score
            
            # Regional risk impact (30% weight)
            if regional_analysis:
                avg_regional_risk = np.mean([data["adjusted_risk"] for data in regional_analysis.values()])
                regional_impact = avg_regional_risk * -30
            else:
                regional_impact = 0
            
            # Momentum impact (20% weight)
            momentum_impacts = {
                "rapidly_decreasing": 15,  # Risk decreasing is good
                "decreasing": 8,
                "stable": 0,
                "slightly_increasing": -5,
                "increasing": -15,
                "insufficient_data": 0
            }
            momentum_impact = momentum_impacts.get(momentum_analysis["momentum"], 0)
            
            # Scenario impact (10% weight)
            worst_case_impact = impact_scenarios["worst_case"]["impact"] * -10
            
            final_score = int(max(1, min(100, base_score + sector_impact + regional_impact + 
                                        momentum_impact + worst_case_impact)))
            
            # Generate explanation
            risk_level = "נמוך" if final_score >= 70 else "בינוני" if final_score >= 40 else "גבוה"
            explanation = f"רמת סיכון גיאופוליטי: {risk_level}"
            
            if sector_analysis["affected_sectors"]:
                explanation += f", חשיפה סקטורית: {len(sector_analysis['affected_sectors'])} סקטורים"
            
            if momentum_analysis["momentum"] != "insufficient_data":
                explanation += f", מגמה: {momentum_analysis['momentum']}"
            
            recent_events = [
                {
                    "type": event.event_type,
                    "severity": event.severity,
                    "regions": event.affected_regions,
                    "description": event.description[:100]
                } for event in sorted(geo_events, key=lambda x: x.timestamp, reverse=True)[:3]
            ]

            score_components = {
                "base_score": base_score,
                "sector_impact": round(sector_impact, 1),
                "regional_impact": round(regional_impact, 1),
                "momentum_impact": momentum_impact,
                "scenario_impact": round(worst_case_impact, 1)
            }

            return {
                "score": final_score,
                "explanation": explanation,
                "signal": {
                    "type": "geopolitical_risk",
                    "score": final_score,
                    "reason": explanation,
                    "confidence": round(len(geo_events) / 10, 3),  # Normalized confidence
                    "details": {
                        "risk_level": risk_level,
                        "events_count": len(geo_events),
                        "affected_sectors": list(set(sum([e.affected_sectors for e in geo_events], []))),
                        "regions": list(set(sum([e.affected_regions for e in geo_events], []))),
                        "momentum": momentum_analysis["momentum"]
                    }
                },
                "details": {
                    "events_analyzed": len(geo_events),
                    "sector_analysis": sector_analysis,
                    "regional_analysis": regional_analysis,
                    "impact_scenarios": impact_scenarios,
                    "momentum_analysis": momentum_analysis,
                    "recent_events": recent_events,
                    "score_components": score_components
                }
            }
            
        except Exception as e:
            return {
                "score": 50,
                "explanation": f"שגיאה בניתוח סיכונים גיאופוליטיים: {str(e)}",
                "details": {
                    "error": str(e),
                    "symbol": symbol
                }
            }

    def get_risk_dashboard(self, symbol: str) -> Dict:
        """
        דשבורד סיכונים גיאופוליטיים
        """
        try:
            events = self._fetch_geopolitical_news(symbol)
            
            if not events:
                return {"message": "No geopolitical risks detected"}
            
            # Risk by category
            risk_by_category = defaultdict(list)
            for event in events:
                risk_by_category[event.event_type].append(event.severity)
            
            category_summary = {}
            for category, severities in risk_by_category.items():
                category_summary[category] = {
                    "event_count": len(severities),
                    "avg_severity": round(np.mean(severities), 2),
                    "max_severity": round(max(severities), 2)
                }
            
            # Active vs resolved events
            active_events = [e for e in events if (datetime.now() - e.timestamp).days < e.duration_estimate]
            
            return {
                "total_events": len(events),
                "active_events": len(active_events),
                "risk_categories": category_summary,
                "highest_risk_event": {
                    "type": max(events, key=lambda x: x.severity).event_type,
                    "severity": max(events, key=lambda x: x.severity).severity,
                    "description": max(events, key=lambda x: x.severity).description
                } if events else None,
                "geographic_spread": len(set().union(*[e.affected_regions for e in events])),
                "sector_impact": len(set().union(*[e.affected_sectors for e in events]))
            }
            
        except Exception as e:
            return {"error": str(e)}
