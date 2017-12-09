import json
from watson_developer_cloud import ToneAnalyzerV3

tone_analyzer = ToneAnalyzerV3(version='2017-09-26', username='f6f09fec-0cb6-49d9-8e20-7f72074df11a',
                               password='zohAscsqYXQl')

tone = tone_analyzer.tone('I am very happy\nIt is a good day.', tones='emotion', content_type='text/plain')

print(json.dumps(tone, indent=2))
