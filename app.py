import streamlit as st
import google.generativeai as genai
import tempfile
import os
import time

# ---------------- UI DESIGN ---------------- #
st.set_page_config(page_title="Ultimate SRT & Caption Gen", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0a192f; color: #e6f1ff; }
    .stButton>button { background-color: #ffd700; color: #0a192f; font-weight: bold; border-radius: 8px; width: 100%; padding: 12px; font-size: 16px; }
    h1, h2, h3 { color: #ffd700; text-align: center; }
    .status-text { color: #00ff00; font-weight: bold; font-size: 18px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.write("### 🎬 Ultimate Video Analyzer (SRT, Table & Captions)")

# ---------------- INPUTS ---------------- #
api_key = st.text_input("သင်၏ Google AI Studio API Key ကို ထည့်ပါ", type="password")
uploaded_file = st.file_uploader("ဗီဒီယို သို့မဟုတ် အသံဖိုင် တင်ရန်", type=['mp4', 'mkv', 'mov', 'mp3', 'wav'])

# ---------------- MAIN PROCESS ---------------- #
if st.button("အကုန်လုံးကို တစ်ခါတည်း ထုတ်ယူမည် (Generate All)"):
    if not api_key:
        st.error("⚠️ ကျေးဇူးပြု၍ API Key အရင်ထည့်ပေးပါ။")
    elif not uploaded_file:
        st.error("⚠️ ကျေးဇူးပြု၍ ဗီဒီယို သို့မဟုတ် အသံဖိုင် အရင်တင်ပေးပါ။")
    else:
        tmp_file_path = None
        
        try:
            progress_bar = st.progress(0)
            status_text = st.markdown("<p class='status-text'>ပြင်ဆင်နေပါသည်... (0%)</p>", unsafe_allow_html=True)
            
            genai.configure(api_key=api_key.strip())
            
            # Gemini 3 Flash Preview Model
            selected_model = "models/gemini-3-flash-preview"
            model = genai.GenerativeModel(selected_model)

            status_text.markdown("<p class='status-text'>⏳ ဖိုင်ကို AI Server သို့ တင်နေပါသည်... (20%)</p>", unsafe_allow_html=True)
            progress_bar.progress(20)

            file_ext = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_file_path = tmp.name

            video_file = genai.upload_file(path=tmp_file_path)

            status_text.markdown("<p class='status-text'>🧠 AI မှ ဗီဒီယိုကို အသေးစိတ် ကြည့်ရှုလေ့လာနေပါသည်... (40%)</p>", unsafe_allow_html=True)
            progress_bar.progress(40)
            
            while video_file.state.name == "PROCESSING":
                time.sleep(3)
                video_file = genai.get_file(video_file.name)

            if video_file.state.name == "FAILED":
                st.error("Google AI မှ ဖိုင်ကို လက်ခံနိုင်ခြင်း မရှိပါ။")
                st.stop()

            status_text.markdown("<p class='status-text'>✨ စာတန်းထိုး၊ ဇယား နှင့် Captions များ ဖန်တီးနေပါသည်... (80%)</p>", unsafe_allow_html=True)
            progress_bar.progress(80)
            
            # အသေးစိတ် ညွှန်ကြားထားသော Prompt
            complex_prompt = """
            Analyze this video/audio carefully from start to finish without missing any dialogue.
            Perform the following 3 tasks and format your output EXACTLY with the tags provided below:

            [TABLE_DATA]
            Create a Markdown table with 3 columns: "Speaker", "Original Chinese", and "Myanmar Translation". 
            Ensure every spoken sentence is included.

            [BURMESE_SRT]
            Generate a professional Burmese SRT file.
            CRITICAL RULES:
            1. Timestamps MUST be exact in '00:00:00,000 --> 00:00:00,000' format. Make sure the timestamps do not exceed the actual video length (e.g., no 1-hour timestamps for a short video).
            2. Format for TikTok/Vertical videos: Keep sentences short and divide them into a maximum of TWO lines per subtitle block.
            3. DO NOT include Speaker Names in the SRT.
            4. Translate every single word completely from start to end without leaving anything out.

            [SOCIAL_MEDIA_CAPTIONS]
            Provide direct-copy captions for social media. Format exactly like this:
            
            TikTok Copy:
            [Write a very short, engaging Burmese caption]
            [Exactly 5 relevant hashtags]

            Facebook Copy:
            [Write a longer, detailed, and engaging Burmese caption explaining the video]
            [10 or more relevant hashtags]
            """
            
            response = model.generate_content([video_file, complex_prompt])
            full_result = response.text
            
            progress_bar.progress(100)
            status_text.markdown("<p class='status-text' style='color: gold;'>✅ အရာအားလုံး အောင်မြင်စွာ လုပ်ဆောင်ပြီးစီးပါပြီ!</p>", unsafe_allow_html=True)
            st.balloons()

            # ရလဒ်များကို ခွဲထုတ်ခြင်း
            try:
                table_data = full_result.split('[TABLE_DATA]')[1].split('[BURMESE_SRT]')[0].strip()
                burmese_srt = full_result.split('[BURMESE_SRT]')[1].split('[SOCIAL_MEDIA_CAPTIONS]')[0].strip()
                social_media = full_result.split('[SOCIAL_MEDIA_CAPTIONS]')[1].strip()
                
                st.markdown("---")
                st.write("### 📊 စကားပြော၊ တရုတ် နှင့် မြန်မာဘာသာပြန် ဇယား (Table)")
                st.markdown(table_data)

                st.markdown("---")
                st.write("### 🇲🇲 TikTok အတွက် မြန်မာစာတန်းထိုး (Mmsub SRT)")
                st.info("💡 စာကြောင်းတိုတိုဖြင့်၊ ပြောသူအမည်မပါဘဲ အချိန်အတိအကျထုတ်ပေးထားပါသည်။")
                st.text_area("Burmese SRT Preview", burmese_srt, height=300)
                st.download_button("📥 Mmsub SRT ကို ဒေါင်းလုဒ်ဆွဲမည်", data=burmese_srt, file_name=f"{uploaded_file.name}_mmsub.srt", mime="text/plain")

                st.markdown("---")
                st.write("### 📱 Social Media အတွက် Captions များ (Direct Copy)")
                st.info("အောက်ပါစာသားများကို Copy ကူး၍ TikTok နှင့် Facebook တွင် တိုက်ရိုက်တင်နိုင်ပါသည်။")
                st.text_area("TikTok & Facebook Copy", social_media, height=250)

            except IndexError:
                st.warning("⚠️ AI မှ မျှော်လင့်ထားသော ပုံစံအတိုင်း အပြည့်အစုံ မထုတ်ပေးပါ။ အောက်ပါအတိုင်း ရလဒ်အားလုံးကို ပြသထားပါသည်။")
                st.text_area("Raw Output", full_result, height=500)

        except Exception as e:
            st.error(f"❌ အမှားအယွင်း ဖြစ်ပေါ်နေပါသည်: {str(e)}")
            
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

