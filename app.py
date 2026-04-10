import streamlit as st
import google.generativeai as genai
import time

# UI Header & Custom CSS (Deep Blue & Gold Theme)
st.set_page_config(page_title="Burmese SRT Gen", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #0a192f; color: #e6f1ff; }
    .stButton>button { background-color: #ffd700; color: #0a192f; font-weight: bold; border-radius: 8px; }
    h1 { color: #ffd700; text-align: center; text-shadow: 2px 2px 4px #000; }
    </style>
    """, unsafe_allow_html=True)

st.write("### 🎬 ဗီဒီယိုမှ မြန်မာစာတန်းထိုး ပြောင်းလဲရန်")

# API Key Input
api_key = st.text_input("သင်၏ Google AI Studio API Key ကို ထည့်ပါ", type="password")

# File Upload
uploaded_file = st.file_uploader("ဗီဒီယို သို့မဟုတ် အသံဖိုင် တင်ရန် (Upload)", type=['mp4', 'mkv', 'mov', 'mp3', 'wav'])

if st.button("SRT ထုတ်ယူမည် (Generate SRT)"):
    if not api_key:
        st.error("ကျေးဇူးပြု၍ API Key အရင်ထည့်ပေးပါ")
    elif not uploaded_file:
        st.error("ကျေးဇူးပြု၍ ဖိုင်အရင်တင်ပေးပါ")
    else:
        try:
            with st.spinner("အလုပ်လုပ်နေပါသည်... ခဏစောင့်ပေးပါ..."):
                # Configure API
                genai.configure(api_key=api_key.strip())
                
                # အကောင်းဆုံး Model ကို အလိုအလျောက် ရှာဖွေခြင်း
                # Flash model ကို အရင်ရှာမည်၊ မတွေ့ပါက Pro ကို သုံးမည်
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                selected_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in available_models else available_models[0]
                
                model = genai.GenerativeModel(selected_model)

                # Upload to Google AI
                file_data = uploaded_file.read()
                temp_file = genai.upload_file(uploaded_file.name)
                
                # File အဆင်သင့်ဖြစ်အောင် စောင့်ခြင်း
                while temp_file.state.name == "PROCESSING":
                    time.sleep(2)
                    temp_file = genai.get_file(temp_file.name)

                # Prompt for SRT
                prompt = """
                Extract the speech from this file and generate a high-quality Burmese subtitle in SRT format. 
                Ensure the timestamps are accurate and the Burmese translation is natural and professional.
                Output ONLY the SRT content.
                """
                
                response = model.generate_content([temp_file, prompt])
                
                # Result
                srt_content = response.text
                st.text_area("SRT Preview", srt_content, height=300)
                
                st.download_button(
                    label="SRT ဖိုင်ကို ဒေါင်းလုဒ်ဆွဲမည်",
                    data=srt_content,
                    file_name=f"{uploaded_file.name}.srt",
                    mime="text/plain"
                )
                st.success("အောင်မြင်စွာ လုပ်ဆောင်ပြီးစီးပါပြီ!")

        except Exception as e:
            st.error(f"အမှားအယွင်း ဖြစ်ပေါ်နေပါသည်: {str(e)}")
