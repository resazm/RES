import streamlit as st
import requests
from PIL import Image
import pytesseract
import io
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import platform
import shutil

# --- OSに応じたTesseractパスの設定 ---
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# --- Tesseractインストール確認 ---
if not shutil.which(pytesseract.pytesseract.tesseract_cmd if platform.system() == "Windows" else "tesseract"):
    st.error("❌ Tesseract OCR が見つかりません。環境に応じてインストールまたはPATH設定を確認してください。")

# ページ設定
st.set_page_config(
    page_title="Webページ画像OCRアプリ",
    page_icon="🔍",
    layout="wide"
)

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_images_from_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        img_tags = soup.find_all('img')
        image_urls = []
        for img in img_tags:
            src = img.get('src')
            if src:
                absolute_url = urljoin(url, src)
                alt_text = img.get('alt', '')
                image_urls.append({
                    'url': absolute_url,
                    'alt': alt_text,
                    'width': img.get('width', ''),
                    'height': img.get('height', '')
                })
        return image_urls
    except Exception as e:
        st.error(f"画像の抽出に失敗しました: {str(e)}")
        return []

def download_image(image_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        if not response.headers.get('content-type', '').startswith('image/'):
            return None, f"画像ではありません: {response.headers.get('content-type')}"
        image = Image.open(io.BytesIO(response.content))
        return image, None
    except Exception as e:
        return None, f"画像取得失敗: {str(e)}"

def perform_ocr(image, lang='jpn+eng'):
    try:
        config = '--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, lang=lang, config=config)
        return text.strip()
    except Exception as e:
        return f"OCRエラー: {str(e)}"


st.title("🔍 Webページ画像OCRアプリ")
st.markdown("指定したWebページの画像からテキストを抽出します")

    # サイドバー設定
st.header("設定")
lang_options = {
    "日本語 + 英語": "jpn+eng",
    "日本語のみ": "jpn",
    "英語のみ": "eng"
}

ocr_lang = lang_options[st.selectbox("OCRの言語", list(lang_options.keys()))]
min_width = st.number_input("最小画像幅 (px)", 0, 10000, 100, step=10)
min_height = st.number_input("最小画像高さ (px)", 0, 10000, 100, step=10)


with st.expander("❓ 使い方"):
    st.markdown("""
    1. WebページのURLを入力し「ページを解析」をクリック  
    2. 表示された画像からOCR処理したい画像を選択  
    3. 「選択した画像をOCR処理」をクリック  
    """)



page_url = st.text_input("WebページのURL", placeholder="https://example.com")



if st.button("ページを解析", type="primary"):
    if not is_valid_url(page_url):
        st.error("有効なURLを入力してください")

    with st.spinner("Webページを解析中..."):
        image_list = extract_images_from_page(page_url)
    if not image_list:
        st.error("画像が見つかりませんでした")

    st.success(f"{len(image_list)}件の画像を検出しました")
    st.session_state.image_list = image_list
    st.session_state.page_url = page_url


if 'image_list' in st.session_state:
    st.subheader("📸 抽出された画像一覧")
    selected_images = []
    cols = st.columns(3)

    for i, img in enumerate(st.session_state.image_list):
        col = cols[i % 3]
        with col:
            image, error = download_image(img['url'])
            if image:
                if image.width >= min_width and image.height >= min_height:
                    if st.checkbox(f"画像 {i+1}", key=f"chk_{i}", help=img['url']):
                        selected_images.append({'image': image, 'info': img, 'index': i+1})
                    st.image(image, caption=f"{image.width}x{image.height}", use_column_width=True)
                else:
                    st.caption(f"画像 {i+1} は小さすぎて除外")
            else:
                st.warning(f"画像 {i+1}: {error}")


    if selected_images:
        st.subheader("📝 OCR処理")
        if st.button("選択した画像をOCR処理"):
            results = []
            progress = st.progress(0)
            for idx, sel in enumerate(selected_images):
                text = perform_ocr(sel['image'], lang=ocr_lang)
                results.append({'index': sel['index'], 'text': text, 'image': sel['image'], 'url': sel['info']['url']})
                progress.progress((idx + 1) / len(selected_images))
                time.sleep(0.1)
            st.success("OCR完了！")

            all_text = ""
            for res in results:
                with st.expander(f"画像 {res['index']} の結果"):
                    st.image(res['image'], caption=f"画像 {res['index']}", use_column_width=True)
                    st.text_area("抽出テキスト", res['text'], height=200)
                    all_text += f"\n--- 画像 {res['index']} ---\n{res['text']}\n"

            if all_text.strip():
                st.download_button("📥 結果をテキストで保存", data=all_text, file_name="ocr_result.txt", mime="text/plain")
    else:
        st.info("OCR処理する画像を選択してください")

st.markdown("---")
st.markdown("Powered by [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)")

