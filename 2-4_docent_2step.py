####### lib 설치 ##########
# pip install openai
# pip install streamlit
# pip install python-dotenv
###########################
# 실행 : streamlit run 2-4.docent.py
###########################

import base64
from io import BytesIO
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import os
from PIL import Image


# .env 파일 경로 지정 
load_dotenv(override=True)

# Open AI API 키 설정하기
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(
    api_key = OPENAI_API_KEY
)

# 이미지를 Base64로 변환하는 함수
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")  # PNG 형식으로 변환
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# 이미지 파일을 분석하여 설명을 반환하는 함수
def ai_describe(image_data, is_url=True):
    try:
        if is_url:
            image_content = {"type": "image_url", "image_url": {"url": image_data}}
        else:
            base64_image = encode_image(image_data)  # 이미지를 Base64로 변환
            image_content = {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 미술관 20년이상 경력을 보야한 전문 큐레이터입니다."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "이 이미지에 대해서 자세하게 설명해 주세요."},
                        image_content,
                    ],
                }
            ],
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"오류 발생: {str(e)}"

# 웹 앱 UI 설정
st.title("AI 도슨트: 이미지를 설명해드려요!")

# 선택 탭 추가
tab1, tab2 = st.tabs(["이미지 파일 업로드", "이미지 URL 입력"])

import streamlit.components.v1 as components

# OpenAI로 유사 이미지 생성 함수 추가
def generate_similar_images_simple(description):
    """해설 내용을 바탕으로 유사한 이미지 3개 생성"""
    try:
        # 해설에서 주요 키워드 추출
        main_subject = description.split('.')[0]  # 첫 문장 사용
        
        similar_images = []
        variations = [
            f"{main_subject}, different angle",
            f"{main_subject}, different lighting",
            f"{main_subject}, different perspective"
        ]
        
        for variation in variations:
            response = client.images.generate(
                model="dall-e-3",
                prompt=variation,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            similar_images.append(response.data[0].url)
        
        return similar_images
    except Exception as e:
        st.error(f"이미지 생성 실패: {e}")
        return []

with tab1:
    # 세션 상태 초기화
    if 'uploaded_images' not in st.session_state:
        st.session_state.uploaded_images = []
    
    # 저장된 모든 이미지와 해설 표시
    for idx, item in enumerate(st.session_state.uploaded_images):
        st.image(item['image'], width=300)
        
        # 해설과 복사 버튼
        col1, col2 = st.columns([20, 10])
        with col1:
            st.success(item['description'])
        with col2:
            # JavaScript로 클립보드 복사 기능 구현
            copy_js = f"""
                <script>
                function copyText{idx}() {{
                    const text = `{item['description'].replace('`', '').replace('"', '\\"').replace("'", "\\'")}`;
                    navigator.clipboard.writeText(text).then(function() {{
                        alert('해설이 복사되었습니다!');
                    }}, function(err) {{
                        console.error('복사 실패:', err);
                    }});
                }}
                </script>
                <button onclick="copyText{idx}()" 
                        style="padding: 5px 8px; font-size: 12px; cursor: pointer; 
                               border: 1px solid #ccc; border-radius: 3px; background: white;">
                    📋
                </button>
            """
            components.html(copy_js, height=40)
        
        # 추천 서비스 섹션
        if 'recommendations' in item:
            st.markdown("**🔍 유사한 이미지 추천**")
            rec_cols = st.columns(3)
            for rec_idx, rec_img in enumerate(item['recommendations']):
                with rec_cols[rec_idx]:
                    st.image(rec_img, use_container_width=True)
        
        st.markdown("---")
    
    # 새 이미지 업로드 영역 (항상 표시)
    uploaded_file = st.file_uploader("이미지를 업로드하세요", type=["jpg", "jpeg", "png"], key=f"uploader_{len(st.session_state.uploaded_images)}")
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, width=300)
        
        if st.button("해설", key=f"file_button_{len(st.session_state.uploaded_images)}"):
            with st.spinner("이미지 분석 및 유사 이미지 생성 중..."):
                result = ai_describe(image, is_url=False)
                
                # OpenAI로 유사 이미지 생성
                recommendations = generate_similar_images_simple(result)
                
                # 이미지, 해설, 추천을 세션에 저장
                st.session_state.uploaded_images.append({
                    'image': image,
                    'description': result,
                    'recommendations': recommendations
                })
            st.rerun()

with tab2:
    st.info("💡 이미지를 붙여넣은 후 박스 밖을 클릭하거나 'ctrl+c' 버튼을 눌러주세요.")
    # st.text("적용하려면 ctrl + enter를 눌러주세요")
    input_url = st.text_area("이미지 URL을 입력하세요", height=70)
    if input_url:
        st.image(input_url, width=300)
    
    if input_url:
        if st.button("해설", key="url_button"):
            result = ai_describe(input_url, is_url=True)
            # st.success(result)
            st.code(result, language=None)