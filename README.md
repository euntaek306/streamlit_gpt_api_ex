# streamlit_gpt_api_ex

# 가상환경 만들기 및 활성화
```
conda create -n gpt_env python=3.12
conda activate gpt_env
```

# 가상환경을 주피터 노트북에 등록하기
```
#jupyter lab에 가상환경 연동하기
- Jupyter 노트북에서 파이썬 코드를 실행할 수 있는 파이썬 커널
pip install ipykernel

- jupyter lab에 가상환경(llm_env) 등록하기
python -m ipykernel install --user --name gpt_env
```

# 기본 설치 라이브러리
```
- 환경변수 로딩 라이브러리(lib)
pip install python-dotenv

pip install openai

-이미지 처리시 필요
pip install Pillow

```

# 웹구현 라이브러리
```
pip install streamlit
```