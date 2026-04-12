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
    .stButton>button { background-color: #ffd700; color: #0a192f; font-weight: bold; border-radius: 8px; width: 100%; padding: 12px; font-size: 16px; }
    h1, h2, h3 { color: #ffd700; text-align: center; }
    .status-text { color: #00ff00; font-weight: bold; font-size: 18px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.write("### 🎬 Pro Video Analyzer (Gemini 3 Flash & Perfect Sync)")

# ---------------- INPUTS ---------------- #
api_key = st.text_input("သင်၏ Google AI Studio API Key ကို ထည့်ပါ", type="password")
uploaded_file = st.file_uploader("ဗီဒီယို သို့မဟုတ် အသံဖိုင် တင်ရန် (15-20 Mins လက်ခံသည်)", type=['mp4', 'mkv', 'mov', 'mp3', 'wav'])

# ---------------- MAIN PROCESS ---------------- #
if st.button("စတင်လုပ်ဆောင်မည် (Start AI Processing)"):
    if not api_key:
        st.error("⚠️ ကျေးဇူးပြု၍ API Key အရင်ထည့်ပေးပါ။")
    elif not uploaded_file:
        st.error("⚠️ ကျေးဇူးပြု၍ ဗီဒီယို သို့မဟုတ် အသံဖိုင် အရင်တင်ပေးပါ။")
    else:
        tmp_file_path = None
        
        try:
            # UI တွင် ရာခိုင်နှုန်းနှင့် အဆင့်များကို ပြသရန်
            progress_bar = st.progress(0)
            status_text = st.markdown("<p class='status-text'>ပြင်ဆင်နေပါသည်... (0%)</p>", unsafe_allow_html=True)
            
            # ဘောက်စ်များ အဆင့်ဆင့်ပေါ်လာစေရန် Placeholders ဖန်တီးခြင်း
            col1, col2 = st.columns(2)
            with col1:
                orig_box = st.empty()
            with col2:
                trans_box = st.empty()
            
            thumb_box = st.empty()

            # 1. API ချိတ်ဆက်ခြင်း
            genai.configure(api_key=api_key.strip())
            
            # သတ်မှတ်ထားသည့် Gemini 3 Flash Preview Model ကို အသုံးပြုခြင်း
            selected_model = "models/gemini-3-flash-preview"
            model = genai.GenerativeModel(selected_model)

            # 2. ဖိုင်တင်ခြင်း (Upload Phase)
            status_text.markdown("<p class='status-text'>⏳ ဖိုင်ကို AI Server သို့ တင်နေပါသည်... (10%)</p>", unsafe_allow_html=True)
            progress_bar.progress(10)

            file_ext = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_file_path = tmp.name

            video_file = genai.upload_file(path=tmp_file_path)

            # 3. AI မှ ဗီဒီယိုကို လေ့လာခြင်း
            status_text.markdown("<p class='status-text'>🧠 AI မှ ဗီဒီယိုကို ကြည့်ရှုလေ့လာနေပါသည်... (25%)</p>", unsafe_allow_html=True)
            progress_bar.progress(25)
            
            while video_file.state.name == "PROCESSING":
                time.sleep(3)
                video_file = genai.get_file(video_file.name)

            if video_file.state.name == "FAILED":
                st.error("Google AI မှ ဖိုင်ကို လက်ခံနိုင်ခြင်း မရှိပါ။")
                st.stop()

            # 4. မူရင်း SRT ထုတ်ယူခြင်း (Original SRT Generation)
            status_text.markdown("<p class='status-text'>🗣️ မူရင်းဘာသာစကားဖြင့် အချိန်ကိုက် SRT ဖန်တီးနေပါသည်... (50%)</p>", unsafe_allow_html=True)
            progress_bar.progress(50)
            
            prompt_original = """
            You are an expert subtitler. Listen to this file.
            Generate a full and highly accurate SRT file in the original language (Chinese or English).
            CRITICAL: Use the exact SRT timestamp format (HH:MM:SS,MMM --> HH:MM:SS,MMM).
            Capture every spoken word accurately. Output ONLY the SRT content.
            """
            response_orig = model.generate_content([video_file, prompt_original])
            original_srt = response_orig.text
            
            # မူရင်း SRT ဘောက်စ်ကို အရင်ဆုံး ပြသပေးမည်
            with orig_box.container():
                st.write("### 🗣️ မူရင်းဘာသာစကား (Original SRT)")
                st.text_area("Chinese/English SRT", original_srt, height=350)
                st.download_button("📥 Original SRT ကို ဒေါင်းလုဒ်ဆွဲမည်", data=original_srt, file_name=f"{uploaded_file.name}_original.srt", mime="text/plain")

            # 5. မြန်မာဘာသာသို့ အချိန်ကိုက် ဘာသာပြန်ခြင်း (Exact Timestamp Sync)
            status_text.markdown("<p class='status-text'>🇲🇲 မူရင်းအချိန် (Timestamps) များနှင့် ကွက်တိကျအောင် မြန်မာလို ဘာသာပြန်နေပါသည်... (80%)</p>", unsafe_allow_html=True)
            progress_bar.progress(80)
            
            prompt_translation = f"""
            You are a professional translator. I will give you an SRT file.
            Translate the text into natural Burmese. 
            CRITICAL RULE: You MUST keep the EXACT same sequence numbers and EXACT same timestamps (HH:MM:SS,MMM --> HH:MM:SS,MMM). 
            Do NOT change or shift the timings. Only change the spoken text.
            Here is the SRT:
            {original_srt}
            """
            response_trans = model.generate_content([prompt_translation])
            burmese_srt = response_trans.text

            # မြန်မာ SRT ဘောက်စ်ကို ဒုတိယ ပြသပေးမည်
            with trans_box.container():
                st.write("### 🇲🇲 မြန်မာဘာသာပြန် (Burmese SRT)")
                st.text_area("Burmese Translated SRT", burmese_srt, height=350)
                st.download_button("📥 Burmese SRT ကို ဒေါင်းလုဒ်ဆွဲမည်", data=burmese_srt, file_name=f"{uploaded_file.name}_burmese.srt", mime="text/plain")

            # 6. Thumbnail Prompts များ ဖန်တီးခြင်း
            status_text.markdown("<p class='status-text'>🎨 Nanobanana2 အတွက် Thumbnail Prompts များ ဖန်တီးနေပါသည်... (95%)</p>", unsafe_allow_html=True)
            progress_bar.progress(95)
            
            prompt_thumb = """
            Based on the video content, create two descriptive text-to-image prompts for an AI image generator.
            1. YouTube Thumbnail (16:9)
            2. TikTok Thumbnail (9:16)
            """
            response_thumb = model.generate_content([video_file, prompt_thumb])
            thumbnail_prompts = response_thumb.text

            with thumb_box.container():
                st.markdown("---")
                st.write("### 🎨 Nanobanana2 အတွက် Thumbnail Prompts များ")
                st.code(thumbnail_prompts, language="text")

            # 7. အောင်မြင်စွာ ပြီးဆုံးခြင်း
            progress_bar.progress(100)
            status_text.markdown(f"<p class='status-text' style='color: gold;'>✅ {selected_model} ဖြင့် အရာအားလုံး အောင်မြင်စွာ လုပ်ဆောင်ပြီးစီးပါပြီ!</p>", unsafe_allow_html=True)
            st.balloons() # အောင်မြင်ကြောင်း ပူဖောင်းများ တက်လာမည်

        except Exception as e:
            st.error(f"❌ အမှားအယွင်း ဖြစ်ပေါ်နေပါသည်: {str(e)}")
            
        finally:
            # ယာယီဖိုင်ကို ရှင်းလင်းခြင်း
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

