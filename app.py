import streamlit as st
import google.generativeai as genai
import tempfile
import os
import time

# ---------------- UI DESIGN ---------------- #
st.set_page_config(page_title="Burmese SRT Gen", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #0a192f; color: #e6f1ff; }
    .stButton>button { background-color: #ffd700; color: #0a192f; font-weight: bold; border-radius: 8px; width: 100%; padding: 10px; }
    h1 { color: #ffd700; text-align: center; text-shadow: 2px 2px 4px #000; }
    </style>
    """, unsafe_allow_html=True)

st.write("### 🎬 ဗီဒီယိုမှ မြန်မာစာတန်းထိုး ပြောင်းလဲရန်")

# ---------------- INPUTS ---------------- #
api_key = st.text_input("သင်၏ Google AI Studio API Key ကို ထည့်ပါ", type="password")
uploaded_file = st.file_uploader("ဗီဒီယို သို့မဟုတ် အသံဖိုင် တင်ရန် (Upload)", type=['mp4', 'mkv', 'mov', 'mp3', 'wav'])

# ---------------- MAIN PROCESS ---------------- #
if st.button("SRT ထုတ်ယူမည် (Generate SRT)"):
    if not api_key:
        st.error("⚠️ ကျေးဇူးပြု၍ API Key အရင်ထည့်ပေးပါ။")
    elif not uploaded_file:
        st.error("⚠️ ကျေးဇူးပြု၍ ဗီဒီယို သို့မဟုတ် အသံဖိုင် အရင်တင်ပေးပါ။")
    else:
        # ဖိုင်ကို ယာယီသိမ်းဆည်းမည့် လမ်းကြောင်း ကြိုတင်သတ်မှတ်ခြင်း
        tmp_file_path = None
        
        try:
            with st.spinner("AI က ဖိုင်ကို စစ်ဆေးပြီး အလုပ်လုပ်နေပါသည်... (ဖိုင်ကြီးပါက အနည်းငယ် ကြာနိုင်ပါသည်)"):
                
                # 1. API Configuration (Space ဖြတ်ပေးခြင်း)
                genai.configure(api_key=api_key.strip())
                
                # 2. Model အလိုအလျောက် ရွေးချယ်ခြင်း
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                if "models/gemini-1.5-flash" in available_models:
                    selected_model = "models/gemini-1.5-flash"
                elif "models/gemini-1.5-pro" in available_models:
                    selected_model = "models/gemini-1.5-pro"
                elif len(available_models) > 0:
                    selected_model = available_models[0]
                else:
                    st.error("သင့် API Key ဖြင့် အသုံးပြုနိုင်သော Model မရှိပါ။")
                    st.stop()

                model = genai.GenerativeModel(selected_model)

                # 3. ဖိုင်ပျောက်ဆုံးမှု မဖြစ်စေရန် သေချာစွာ ယာယီသိမ်းခြင်း
                file_ext = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_file_path = tmp.name # လမ်းကြောင်းကို မှတ်သားထားမည်

                # 4. Google AI သို့ ဖိုင်တင်ခြင်း
                video_file = genai.upload_file(path=tmp_file_path)

                # 5. ဖိုင်ကို AI မှ Process လုပ်ရန် စောင့်ဆိုင်းခြင်း
                while video_file.state.name == "PROCESSING":
                    time.sleep(3)
                    video_file = genai.get_file(video_file.name)

                if video_file.state.name == "FAILED":
                    st.error("Google AI ဘက်မှ ဖိုင်ကို လက်ခံနိုင်ခြင်း မရှိပါ။")
                    st.stop()

                # 6. စာတန်းထိုး ထုတ်ရန် ခိုင်းစေခြင်း
                prompt = """
                Listen to this audio/video carefully. Extract the speech and provide a highly accurate, 
                professional Burmese translation. Format the output strictly as a standard SRT file 
                with accurate timestamps. Do NOT include any other text except the SRT content.
                """
                
                response = model.generate_content([video_file, prompt])
                srt_content = response.text
                
                # 7. ရလဒ်ပြသခြင်း နှင့် Download
                st.success(f"အောင်မြင်စွာ လုပ်ဆောင်ပြီးစီးပါပြီ! (အသုံးပြုခဲ့သော Model: {selected_model})")
                st.text_area("SRT Preview (မြည်းစမ်းရန်)", srt_content, height=300)
                st.download_button(
                    label="📥 SRT ဖိုင်ကို ဒေါင်းလုဒ်ဆွဲမည်",
                    data=srt_content,
                    file_name=f"{uploaded_file.name}.srt",
                    mime="text/plain"
                )

        except Exception as e:
            st.error(f"❌ အမှားအယွင်း ဖြစ်ပေါ်နေပါသည်: {str(e)}")
            
        finally:
            # 8. ဖုန်း Storage မပြည့်အောင် ယာယီဖိုင်ကို အလိုအလျောက် ပြန်ဖျက်ခြင်း
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
