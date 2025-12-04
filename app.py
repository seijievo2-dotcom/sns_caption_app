iimport os
import json
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="SNS Caption Generator", page_icon="✨")
st.title("SNS キャプション自動生成アプリ ✨")

st.write("投稿内容をもとに、SNSに最適化したキャプションを自動生成します。")

platform = st.selectbox(
    "投稿プラットフォームを選択してください",
    ["Instagram", "Threads", "TikTok", "YouTube Shorts", "X(Twitter)"]
)

tone = st.selectbox(
    "キャプションのトーンを選択してください",
    ["カジュアル", "ビジネス", "情熱的", "ユーモア", "シンプル", "エモーショナル"]
)

content = st.text_area("投稿内容の説明を入力してください", height=150)

# ====== OpenAI Client ======
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("APIキーが設定されていません。Secretsを確認してください。")
    st.stop()

client = OpenAI(api_key=api_key)

generated_caption = None  # 後でコピー用に保持

if st.button("キャプションを生成する"):
    if not content.strip():
        st.warning("投稿内容を入力してください。")
    else:
        with st.spinner("生成中..."):
            prompt = f"""
あなたはSNSマーケティングの専門家です。
以下の条件に基づき、SNS投稿用のキャプションを生成してください。

- プラットフォーム: {platform}
- トーン: {tone}
- 投稿内容: {content}

制約:
1. 最初に目を引く一文を入れる
2. ハッシュタグを5〜10個含める
3. 日本語で書く
4. {platform}に最適化した表現で
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "あなたはコピーライティングとSNS戦略のプロです。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
            )

            generated_caption = response.choices[0].message.content

            st.subheader("生成されたキャプション")
            st.text_area(
                "キャプション（編集も可能です）",
                value=generated_caption,
                height=200,
                key="generated_caption_area",
            )
            st.success("生成完了！✨")

            # コピー用ボタン
            if st.button("このキャプションをコピー"):
                # text_area の内容を取得（ユーザーが編集している可能性もあるのでこちらを優先）
                text_to_copy = st.session_state.get("generated_caption_area", generated_caption or "")

                if text_to_copy.strip():
                    # JS でクリップボードへコピー
                    escaped = json.dumps(text_to_copy)  # JS用に安全にエスケープ
                    st.markdown(
                        f"""
                        <script>
                        navigator.clipboard.writeText({escaped}).then(function() {{
                            console.log("Copied to clipboard");
                        }});
                        </script>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.success("クリップボードにコピーしました ✅")
                else:
                    st.warning("コピーするキャプションがありません。")
