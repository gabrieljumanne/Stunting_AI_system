import os
import sys
import django

sys.path.append('/home/i-castorosa-098/Desktop/stunting_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stunting_project.settings')
django.setup()

from ai_assitance.utilis import load_chatbot_models

print('Loading the models (using HuggingFace cache)...')
models = load_chatbot_models()
print('Models loaded successfully!')

print('HuggingFace Cache Location:', os.path.expanduser('~/.cache/huggingface/'))
print('Cache contents:')
os.system('ls -la ~/.cache/huggingface/hub/ | head -n 10')