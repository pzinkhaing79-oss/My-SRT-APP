import streamlit as st
import google.generativeai as genai
import tempfile
import os
import time

# ---------------- UI DESIGN ---------------- #
st.set_page_config(page_title="Pro SRT & Thumbnail Gen", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0a192f; color: #e6f1ff; }
    .stButton>button { background-color: #ffd700; color: #0a192f; font-weight: bold; border-radius: 8px; width: 100%; padding: 10px; }
    h1, h2, h3 { color: #ffd700; text-align: center; }
    .download-btn { margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.write("### 🎬 Pro Video Analyzer: Multi-SRT & Thumbnail Gen")

# ---------------- INPUTS ---------------- #
api_key = st.text_input("သင်၏ Google AI Studio API Key ကို ထည့်ပါ", type="password")
uploaded_file = st.file_uploader("ဗီဒီယို သို့မဟုတ် အသံဖိုင် တင်ရန် (Upload)", type=['mp4', 'mkv', 'mov', 'mp3', 'wav'])

# ---------------- MAIN PROCESS ---------------- #
if st.button("အကုန်လုံးကို တစ်ခါတည်း ထုတ်ယူမည် (Generate All)"):
    if not api_key:
        st.error("⚠️ ကျေးဇူးပြု၍ API Key အရင်ထည့်ပေးပါ။")
    elif not uploaded_file:
        st.error("⚠️ ကျေးဇူးပြု၍ ဗီဒီယို သို့မဟုတ် အသံဖိုင် အရင်တင်ပေးပါ။")
    else:
        tmp_file_path = None
        
        try:
            with st.spinner("AI က ဗီဒီယိုကို လေ့လာပြီး SRT နှင့် Thumbnail များကို ဖန်တီးနေပါသည်... (ခဏစောင့်ပေးပါ)"):
                
                genai.configure(api_key=api_key.strip())
                
                # Gemini 3 Flash Preview Model ကို တိုက်ရိုက်အသုံးပြုခြင်း
                selected_model = "models/gemini-3-flash-preview"
                model = genai.GenerativeModel(selected_model)

                # ဖိုင်ကို ယာယီသိမ်းခြင်း
                file_ext = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_file_path = tmp.name

                # Google AI သို့ ဖိုင်တင်ခြင်း
                video_file = genai.upload_file(path=tmp_file_path)

                while video_file.state.name == "PROCESSING":
                    time.sleep(3)
                    video_file = genai.get_file(video_file.name)

                if video_file.state.name == "FAILED":
                    st.error("Google AI ဘက်မှ ဖိုင်ကို လက်ခံနိုင်ခြင်း မရှိပါ။")
                    st.stop()

                # အမိန့်ပေးစာ (Prompt) - SRT ၂ မျိုး နှင့် Thumbnail Prompt တောင်းခံခြင်း
                prompt = """
                Analyze this video/audio carefully. It contains spoken Chinese and/or English.
                Please perform the following 3 tasks and format your output EXACTLY with the tags provided below:

                [ORIGINAL_SRT]
                Generate a highly accurate SRT file in the original language (Chinese/English). Capture the natural flow of the speakers with precise timestamps.

                [BURMESE_SRT]
                Generate a professional, culturally natural Burmese translation of the video in SRT format with the exact same timestamps.

                [THUMBNAIL_PROMPTS]
                Based on the core story and most engaging scene of this video, write two high-quality, descriptive text-to-image AI prompts for a tool called "Nanobanana2".
                1. YouTube Prompt (16:9 aspect ratio): Focus on cinematic style, clear subject, and high contrast.
                2. TikTok Prompt (9:16 aspect ratio): Focus on vertical framing, eye-catching facial expressions, and vibrant colors.
                """
                
                response = model.generate_content([video_file, prompt])
                full_result = response.text
                
                # ရလဒ်များကို ခွဲထုတ်ခြင်း (Parsing)
                try:
                    # Original SRT ခွဲထုတ်ခြင်း
                    original_srt = full_result.split('[ORIGINAL_SRT]')[1].split('[BURMESE_SRT]')[0].strip()
                    
                    # Burmese SRT ခွဲထုတ်ခြင်း
                    burmese_srt = full_result.split('[BURMESE_SRT]')[1].split('[THUMBNAIL_PROMPTS]')[0].strip()
                    
                    # Thumbnail Prompts ခွဲထုတ်ခြင်း
                    thumbnail_prompts = full_result.split('[THUMBNAIL_PROMPTS]')[1].strip()
                    
                    st.success(f"အောင်မြင်စွာ လုပ်ဆောင်ပြီးစီးပါပြီ! (Model: {selected_model})")
                    
                    # ကော်လံ ၂ ခုခွဲ၍ ပြသခြင်း
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("### 🗣️ မူရင်းဘာသာစကား (Original SRT)")
                        st.text_area("Chinese/English SRT", original_srt, height=250)
                        st.download_button("📥 Original SRT ကို ဒေါင်းလုဒ်ဆွဲမည်", data=original_srt, file_name=f"{uploaded_file.name}_original.srt", mime="text/plain")
                        
                    with col2:
                        st.write("### 🇲🇲 မြန်မာဘာသာပြန် (Burmese SRT)")
                        st.text_area("Burmese Translated SRT", burmese_srt, height=250)
                        st.download_button("📥 Burmese SRT ကို ဒေါင်းလုဒ်ဆွဲမည်", data=burmese_srt, file_name=f"{uploaded_file.name}_burmese.srt", mime="text/plain")

                    st.markdown("---")
                    st.write("### 🎨 Nanobanana2 အတွက် Thumbnail Prompts များ")
                    st.info("အောက်ပါစာသားများကို Copy ကူး၍ Nanobanana2 သို့မဟုတ် မိမိအသုံးပြုနေကျ AI ပုံဆွဲ Tool များတွင် ထည့်သွင်းအသုံးပြုနိုင်ပါသည်။")
                    st.code(thumbnail_prompts, language="text")

                except IndexError:
                    st.warning("AI မှ မျှော်လင့်ထားသော ပုံစံအတိုင်း အပြည့်အစုံ မထုတ်ပေးပါ။ အောက်ပါအတိုင်း ရလဒ်အားလုံးကို ပြသထားပါသည်။")
                    st.text_area("Raw Output", full_result, height=400)

        except Exception as e:
            st.error(f"❌ အမှားအယွင်း ဖြစ်ပေါ်နေပါသည်: {str(e)}")
            
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

