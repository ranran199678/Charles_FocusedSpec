from core.event_scanner import EventScanner

scanner = EventScanner()
result = scanner.analyze('INTC')

print(f"New Score: {result['score']}")
print(f"Summary: {result['summary']}")

# חישוב ידני לבדיקה
events = result['events']
print(f"\nEvents breakdown:")
for category, event_list in events.items():
    if event_list:
        print(f"{category}: {len(event_list)} events")
        # הדפסת כותרות החדשות
        for i, event in enumerate(event_list[:2]):  # רק 2 הראשונים
            print(f"  {i+1}. {event.get('title', 'No title')}") 