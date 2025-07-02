#!/usr/bin/env python3
import re

# Translation mappings
translations = {
    'AI-Powered Assistance': 'Msaada wa Akili Bandia',
    'Get intelligent guidance for your child\'s growth and development journey': 'Pata mwongozo wa akili kuhusu ukuaji na maendeleo ya mtoto wako',
    'Smart Chat Assistant': 'Msaidizi wa Mazungumzo Mahiri',
    'Get instant, personalized answers about child nutrition, health, and development from our AI assistant.': 'Pata majibu ya papo hapo na ya kibinafsi kuhusu lishe ya mtoto, afya, na maendeleo kutoka kwa msaidizi wetu wa akili bandia.',
    'Start Conversation': 'Anza Mazungumzo',
    'Child Growth Insights': 'Maarifa ya Ukuaji wa Mtoto',
    'Available': 'Inapatikana',
    'Get AI-powered analysis of your children\'s growth patterns, trends, and personalized nutrition advice.': 'Pata uchambuzi wa akili bandia wa mifumo ya ukuaji wa watoto wako, mienendo, na ushauri wa lishe uliobinafsishwa.',
    'View Insights': 'Ona Maarifa',
    'Recommendations': 'Mapendekezo',
    'Analysis Error': 'Hitilafu ya Uchambuzi'
}

# Read the file
with open('locale/sw/LC_MESSAGES/django.po', 'r', encoding='utf-8') as f:
    content = f.read()

# Update translations
for english, swahili in translations.items():
    # Pattern to match msgid followed by empty msgstr
    pattern = f'msgid "{re.escape(english)}"\nmsgstr ""'
    replacement = f'msgid "{english}"\nmsgstr "{swahili}"'
    content = content.replace(pattern, replacement)

# Write back to file
with open('locale/sw/LC_MESSAGES/django.po', 'w', encoding='utf-8') as f:
    f.write(content)

print("Translations updated successfully!")
