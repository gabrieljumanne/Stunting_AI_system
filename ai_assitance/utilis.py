#using Huggingface caching built-in system 
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    M2M100ForConditionalGeneration,  # Correct model class
    M2M100Tokenizer  # Correct tokenizer class
)

#global variable to store ALL MODELS 
_LOADED_MODELS = None 

def load_chatbot_models():
    """
    Load chatbot models using HuggingFace's built-in caching.
    Models are downloaded once and cached automatically in ~/.cache/huggingface/
    """
    global _LOADED_MODELS
    
    # If models already loaded in this process, return them
    if _LOADED_MODELS is not None:
        return _LOADED_MODELS
        
    print("Loading models...")
    
    # Download and load DialoGPT (uses HuggingFace's built-in caching)
    dialogpt_model_name = "microsoft/DialoGPT-medium"
    dialogpt_model = AutoModelForCausalLM.from_pretrained(dialogpt_model_name)
    dialogpt_tokenizer = AutoTokenizer.from_pretrained(dialogpt_model_name)

    # Load M2M100 models for translation (uses HuggingFace's built-in caching)
    m2m_model_name = "facebook/m2m100_418M"
    marian_sw_en_model = M2M100ForConditionalGeneration.from_pretrained(m2m_model_name)
    marian_sw_en_tokenizer = M2M100Tokenizer.from_pretrained(m2m_model_name)
    marian_en_sw_model = M2M100ForConditionalGeneration.from_pretrained(m2m_model_name)
    marian_en_sw_tokenizer = M2M100Tokenizer.from_pretrained(m2m_model_name)

    # Set language codes for the tokenizers
    marian_sw_en_tokenizer.src_lang = "sw"
    marian_sw_en_tokenizer.tgt_lang = "en"
    marian_en_sw_tokenizer.src_lang = "en"
    marian_en_sw_tokenizer.tgt_lang = "sw"
    
    print("Models loaded successfully!")
    
    # Store in global variable to avoid reloading within same process
    _LOADED_MODELS = {
        'dialogpt_model': dialogpt_model,
        'dialogpt_tokenizer': dialogpt_tokenizer,
        'marian_sw_en_model': marian_sw_en_model,
        'marian_sw_en_tokenizer': marian_sw_en_tokenizer,
        'marian_en_sw_model': marian_en_sw_model,
        'marian_en_sw_tokenizer': marian_en_sw_tokenizer,
    }
    
    return _LOADED_MODELS