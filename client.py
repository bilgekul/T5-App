import streamlit as st
import time
from transformers import T5Tokenizer 
from transformers import TFT5ForConditionalGeneration
from db import get_all_caching_data, set_caching_data, get_caching_data, del_caching_data
from stt import recognize_and_speak
import socket

st.set_page_config(
    page_title="T5  ENG-TR translator",
    page_icon="🌐",               
    layout="wide"                     
)

values = {}

@st.cache_data
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Soket oluşturmak için AF_NET ıpv4 ailesini, SOCK_DGRAM ise UDP protokolünü  temsil eder.
        s.connect(('8.8.8.8', 80)) # sokete her yerden bağlantı sağlaması için 8.8.8.8 ve 80 portundan erişim sağlıyoruz.
        ip_address = s.getsockname()[0] # Sokete bağlanan ilk adresi döndür.
        s.close() # soket bağlantı nesnesini kapatır.
        return ip_address
    except Exception as e:
        return 'unknown'
    
session_id = get_ip_address()

print("user session ipaddress:",session_id)

@st.cache_resource
def load_model_and_tokenizer():
    tokenizer = T5Tokenizer.from_pretrained("t5-small")
    model = TFT5ForConditionalGeneration.from_pretrained("t5-small-turkish-english-translator")
    return tokenizer, model

def processing_translate(text: str) -> str:
    tokenizer, model = load_model_and_tokenizer()
    pre = tokenizer(text, return_tensors="tf")
    outputs = model.generate(
        pre['input_ids'], 
        max_length=100,               
        min_length=10,               
        num_beams=10,                 
        no_repeat_ngram_size=2,       
        temperature=0.5,              
        top_k=50,                    
        top_p=0.95,                   
        early_stopping=True
    )
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    values["english"] = text
    values["turkish"] = translated_text
    set_caching_data(session_id,values)
    return translated_text

all_translations = get_all_caching_data(session_id)

filter_tr = ""
filter_eng =""
output = ""

with st.sidebar:
        st.markdown("""
            <h1>Translate history 🔄</h1>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            for i, translate in enumerate(all_translations):
                col1, col2 = st.columns([3, 1], gap="small")
                with col1:
                    if st.button(f"{translate['english']}", key=f"btn_{i}", type="primary"):
                        filter_tr = get_caching_data(session_id,translate["english"])
                        filter_eng = translate["english"]      
                with col2:
                    if st.button(f"X", key=f"del_{i}", type="secondary",use_container_width=True):
                        del_caching_data(session_id,translate["english"])
                        st.rerun()


col1, col2, col3 = st.columns([4, 4, 1], gap="large")

with col1:
    st.subheader("English (:uk:)",divider="grey")
    eng_txt = st.text_area(
        label="English",
        height=180,
        placeholder="Start typing text or paste a link.",
        label_visibility="hidden",
        key="eng_textarea",
        on_change= lambda: st.session_state.update({'text_changed': True}),
        value="" or filter_eng
    )
   
    button_placeholder = st.empty()
    with button_placeholder.container():
        if st.button("🎤"):
           with st.spinner("Speak into the microphone"):
            text = recognize_and_speak()
            if text:
                    output = processing_translate(text)
            else:
                    st.write("No text recognized. Please try again.")

if st.session_state.get("text_changed"):
    with st.spinner("Translating..."):
        input_value = st.session_state.get("eng_textarea", "")
        if input_value:  
            output = processing_translate(input_value)
            time.sleep(5) 
            st.session_state.text_changed = False

with col2:
    st.subheader("Turkish (:flag-tr:)",divider="grey")
    st.text_area(
        label="Turkish",
        height=180,
        placeholder="Translate",
        label_visibility="hidden",
        key="tr_textarea",
        value= (output or filter_tr)
    )

with col3:
    if st.button("X",type="primary"):
        st.session_state.text_area = ""
        st.balloons()
    

