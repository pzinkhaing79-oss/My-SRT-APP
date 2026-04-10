import streamlit as st
import google.generativeai as genai
import tempfile
import os
import time

# --- 1. Page & UI Configuration ---
st.set_page_config(page_title="မြန်မာ SRT ဖန်တီးမှုစနစ်", page_icon="🎬", layout="centered")

# Custom CSS for Deep Blue & Gold Theme, 20px Rounded Corners
st.markdown("""
    <style>
    /* Dark Mode Deep Blue Background */
    .stApp {
        background-color: #0A1128; 
        color: #FFFFFF;
    }
    
    /* Header Style */
    h1 {
        text-align: center;
        color: #FFD700; /* Gold */
        font-weight: bold;
        text-shadow: 0px 4px 10px rgba(255, 215, 0, 0.3);
    }

    /* File Uploader Style */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #162447;
        border: 2px dashed #FFD700;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.4);
    }

    /* Preview Box (Code Editor Style) */
    .stTextArea textarea {
        background-color: #1E1E2E !important; 
        color: #A6E22E !important; 
        font-family: 'Courier New', Courier, monospace !important;
        border-radius: 20px !important;
        border: 1px solid #414868 !important;
        box-shadow: inset 0px 4px 8px rgba(0, 0, 0, 0.5) !important;
        padding: 15px !important;
    }

    /* Large Vibrant Download Button */
    .stDownloadButton button {
        background-color: #FFD700 !important;
        color: #0A1128 !important;
        border-radius: 20px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        width: 100% !important;
        padding: 15px 0px !important;
        border: none !important;
        box-shadow: 0px 6px 15px rgba(255, 215, 0, 0.4) !important;
        transition: 0.3s;
    }
    .stDownloadButton button:hover {
        background-color: #FFEA00 !important;
        transform: translateY(-2px);
    }
    
    /* Input Box for API Key */
    .stTextInput input {
        border-radius: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. Header ---
st.markdown("<h1>🎬 ဗီဒီယိုမှ မြန်မာစာတန်းထိုး ပြောင်းလဲရန်</h1>", unsafe_allow_html=True)

# --- 3. API Key Setup ---
api_key = st.text_input("သင်၏ Google AI Studio API Key ကို ထည့်ပါ", type="password")

if api_key:
    genai.configure(api_key=api_key)

    # --- 4. File Upload ---
    uploaded_file = st.file_uploader("ဗီဒီယို သို့မဟုတ် အသံဖိုင် တင်ရန် (Upload Video/Audio)", type=['mp4', 'mp3', 'wav', 'mov'])

    if uploaded_file is not None:
        if st.button("SRT ထုတ်ယူမည် (Generate SRT)"):
            with st.spinner("⏳ စာတန်းထိုး ပြုလုပ်နေပါသည်... ခဏစောင့်ပါ..."):
                try:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
                        temp_file.write(uploaded_file.read())
                        temp_file_path = temp_file.name

                    # Upload to Gemini using File API
                    video_file = genai.upload_file(path=temp_file_path)

                    # Wait for Gemini to process the video
                    while video_file.state.name == "PROCESSING":
                        time.sleep(2)
                        video_file = genai.get_file(video_file.name)

                    if video_file.state.name == "FAILED":
                        st.error("ဗီဒီယို ဖတ်ယူခြင်း မအောင်မြင်ပါ။")
                    else:
                        # Use Gemini 1.5 Flash for Speed
                        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                        
                        # Professional Prompt for Myanmar SRT
                        prompt = "You are a professional Video-to-Myanmar SRT generator. Listen to the speech, accurately transcribe it, and translate it into natural Myanmar (Burmese) language. Output ONLY in a professional SRT format with precise timestamps. No extra text or conversation."
                        
                        response = model.generate_content([video_file, prompt])
                        srt_content = response.text

                        st.success("✅ အောင်မြင်စွာ ပြုလုပ်ပြီးပါပြီ")

                        # Preview Box (Code Editor Style)
                        st.text_area("SRT Preview:", value=srt_content, height=300)

                        # Vibrant Download Button
                        st.download_button(
                            label="📥 SRT ဒေါင်းလုဒ်ဆွဲမည်",
                            data=srt_content,
                            file_name="myanmar_subtitle.srt",
                            mime="text/plain"
                        )

                    # Clean up
                    os.remove(temp_file_path)

                except Exception as e:
                    st.error(f"အမှားအယွင်းဖြစ်ပေါ်နေပါသည်: {e}")
else:
    st.info("💡 စတင်ရန်အတွက် အထက်တွင် API Key ကို ဦးစွာထည့်သွင်းပါ။")
