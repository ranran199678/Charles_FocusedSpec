import sys
sys.path.append('.')

# בדיקת סוכנים פשוטה
print("=== בדיקת סוכנים פשוטה ===")

# בדיקת סוכנים שפיתחנו
agents_to_test = [
    ("core.nlp_analyzer", "NLPAnalyzer"),
    ("core.event_scanner", "EventScanner"),
    ("core.macro_trend_scanner", "MacroTrendScanner"),
    ("core.social_media_hype_scanner", "SocialMediaHypeScanner"),
    ("core.adx_score_agent", "ADXScoreAgent"),
    ("core.rsi_sniffer", "RSICompressionSniffer"),
    ("core.volume_tension_meter", "VolumeTensionMeter"),
    ("core.parabolic_agent", "ParabolicAgent"),
    ("core.breakout_retest_recognizer", "BreakoutRetestRecognizer"),
    ("core.support_zone_strength_detector", "SupportZoneStrengthDetector"),
]

working_agents = []
broken_agents = []

for module_path, class_name in agents_to_test:
    try:
        module = __import__(module_path, fromlist=[class_name])
        agent_class = getattr(module, class_name)
        agent = agent_class()
        
        # בדיקה פשוטה
        result = agent.analyze("AAPL")
        score = result.get("score", 0)
        
        if score > 1:
            working_agents.append((class_name, score))
            print(f"✅ {class_name}: {score}/100")
        else:
            broken_agents.append(class_name)
            print(f"❌ {class_name}: ציון נמוך ({score})")
            
    except Exception as e:
        broken_agents.append(class_name)
        print(f"❌ {class_name}: שגיאה - {str(e)[:50]}...")

print(f"\n=== סיכום ===")
print(f"סוכנים עובדים: {len(working_agents)}")
print(f"סוכנים לא עובדים: {len(broken_agents)}")

if working_agents:
    print(f"\nסוכנים עובדים:")
    for name, score in sorted(working_agents, key=lambda x: x[1], reverse=True):
        print(f"  {name}: {score}/100")

if broken_agents:
    print(f"\nסוכנים לא עובדים:")
    for name in broken_agents:
        print(f"  {name}")

print(f"\n=== סיום בדיקה ===") 