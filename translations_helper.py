#!/usr/bin/env python3
"""
Helper script to add comprehensive Swahili translations to the .po file
"""

translations = {
    # Base Template
    "Stunting Project": "Mradi wa Mapungufu ya Ukuaji",
    "Account Settings": "Mipangilio ya Akaunti",
    "Log out": "Toka",
    "Login": "Ingia",
    
    # Dashboard Main
    "Welcome Back, %(name)s!": "Karibu Tena, %(name)s!",
    "Your child's health journey continues here. Track growth, get insights, and access AI-powered assistance.": "Safari ya afya ya mtoto wako inaendelea hapa. Fuatilia ukuaji, pata muelekeo, na pata msaada wa AI.",
    
    # Growth Tracking
    "Growth Tracking": "Ufuatiliaji wa Ukuaji",
    "Monitor your child's development": "Fuatilia maendeleo ya mtoto wako",
    "New Measurement": "Kipimo Kipya",
    "Latest Measurement": "Kipimo cha Hivi Karibuni",
    "Child Name": "Jina la Mtoto",
    "Birth Date": "Tarehe ya Kuzaliwa",
    "Healthy Growth": "Ukuaji Mzuri",
    "Your child is growing well and meeting developmental milestones.": "Mtoto wako anakua vizuri na anafuata hatua za maendeleo.",
    "Needs Attention": "Inahitaji Umakini",
    "Consider consulting with healthcare providers for guidance.": "Fikiria kushauriana na watoa huduma za afya kwa mwongozo.",
    "No measurements recorded yet": "Hakuna vipimo vilivyorekodiwa bado",
    "Start tracking your child's growth today!": "Anza kufuatilia ukuaji wa mtoto wako leo!",
    
    # Quick Actions
    "Quick Actions": "Vitendo vya Haraka",
    "Manage your account settings": "Dhibiti mipangilio ya akaunti yako",
    "Edit Profile": "Hariri Wasifu",
    "Update your personal information": "Sasisha taarifa zako za kibinafsi",
    "Change Password": "Badilisha Nywila",
    "Update your security credentials": "Sasisha utambulisho wako wa usalama",
    "Log Out": "Toka",
    "Sign out of your account": "Toka kwenye akaunti yako",
    
    # Food Analysis
    "Food Image Analysis": "Uchambuzi wa Picha ya Chakula",
    "Upload a food image to get instant nutritional information and recommendations": "Pakia picha ya chakula kupata taarifa za lishe na mapendekezo mara moja",
    "Upload Food Image": "Pakia Picha ya Chakula",
    "Click to browse or drag and drop your food image here": "Bofya kutafuta au buruta na dondosha picha ya chakula hapa",
    "Supported: JPEG, PNG, GIF (Max 10MB)": "Zinazotumika: JPEG, PNG, GIF (Kwa juu ya MB 10)",
    "Remove": "Ondoa",
    "Select Image to Analyze": "Chagua Picha ya Kuchabuzi",
    "Analyzing Image...": "Inachambua Picha...",
    "Our AI is identifying the food and gathering nutritional information": "AI yetu inagundua chakula na kukusanya taarifa za lishe",
    "Food Identification": "Utambulishaji wa Chakula",
    "Nutritional Information": "Taarifa za Lishe",
}

print("Swahili translations ready to be added to the .po file:")
for english, swahili in translations.items():
    print(f'msgid "{english}"')
    print(f'msgstr "{swahili}"')
    print()
