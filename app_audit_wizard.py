
import streamlit as st
import openai
import uuid
from PIL import Image
import requests

# DeepLのAPIキーを取得
#DEEPL_API_KEY = st.secrets["DeepLAPI"]["deepl_api_key"]

# DeepLのAPIを呼び出す関数
#def translate_to_english(text):
#    url = "https://api-free.deepl.com/v2/translate"
#    headers = {"Content-Type": "application/x-www-form-urlencoded"}
#    data = {
#        "auth_key": DEEPL_API_KEY,
#        "text": text,
#        "target_lang": "EN",
#    }
#    response = requests.post(url, headers=headers, data=data)
#    return response.json()["translations"][0]["text"]

# サービス名を表示する
st.sidebar.title("Audit Wizard for GIAC")

# Create a unique key for the widget
unique_key = str(uuid.uuid4())

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role":"system","content":"You are the best of Internal Audit AI assistant in the world."}
    ]

if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

# チャットボットとやりとりする関数
def communicate(user_input, bot_response_placeholder, model):
    messages = [{"role":"system","content":""}]
    user_message = {"role": "user", "content": user_input}
    messages.append(user_message)

    # Temporary variable to store chunks
    complete_response = ""

    # Get the response from ChatCompletion in streaming mode
    for chunk in openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
        stream=True
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            # Accumulate content and update the bot's response in real time
            complete_response += content
            bot_response_placeholder.markdown(complete_response, unsafe_allow_html=True)

    # After all chunks are received, add the complete response to the chat history
    if complete_response:
        bot_message = {"role": "assistant", "content": complete_response}
        messages.append(bot_message)

    # Reset the messages after the chat
    messages = [{"role":"system","content":"You are the best of Internal Audit AI assistant in the world."}]

# サイドバーで機能を選択
selected_option = st.sidebar.selectbox(
    "Select Function", # 機能を選択してください
    ["Q&A", "Translation", "Audit Planning", "Inspection", "Data Analytics", "Risk Assessment", "RootCause Analysis","Continuous Monitoring"], # Continuous Monitoringを追加
    key="selectbox_key"  # 固定のキーを指定する
)

# モデルを選択
model = st.sidebar.selectbox(
    "Select Model", # モデルを選択してください
    ["gpt-3.5-turbo-16k", "gpt-4"],
    key="model_selectbox_key"  # 固定のキーを指定する
)

# 機能に応じたUIの表示
if selected_option == "Q&A":
    # Build the user interface
    st.title("Audit Wizard")

    # Create a placeholder for the user's input
    user_input = st.text_area("Enter your questions about internal audits or GRC. | 内部監査やGRCに関する質問を入力してください。", value=st.session_state.get("user_input_Q&A", ""))

    # Create a placeholder for the bot's responses
    bot_response_placeholder = st.empty()

    # Execute the communicate function when the user presses the 'Submit' button
    if st.button("Send message", key="send_button_Q&A"):
        st.session_state["user_input_Q&A"] = user_input
        communicate(st.session_state["user_input_Q&A"], bot_response_placeholder, model)

        # Clear the user input
        st.session_state["user_input_Q&A"] = ""


elif selected_option == "Translation":
    st.title("Translation")

    # 右側の入力フォーム
    user_input = st.text_area("Enter the text you wish to translate and press the Send message button. | 翻訳したい文章を入力し、送信ボタンを押してください。", height=200, key="user_input_translation")

    # 追加：補足情報の入力フィールド
    additional_info = st.text_area("Please enter supplemental information. | 補足情報を入力してください。", "", key="additional_info")

    # Create a placeholder for the bot's responses
    bot_response_placeholder = st.empty()

    if st.button("Send message", key="send_button_translation"):
        if user_input.strip() == "":
            st.warning("データを入力してください。")
        else:
            initial_prompt = (
                "あなたは優秀な翻訳家です。あなたの役割は、英文を日本語に翻訳し、日本語のウェブサイト上で日本人の投資家向けに翻訳された間違いのない情報を提供することです。\n"
                "可能な限り原文に忠実に、漏れや間違いなく、自然な日本語に翻訳してください。\n"
                "＃指示\n"
                f"{user_input}を翻訳してください。\n"
                f"＃補足情報: {additional_info}"
                "＃注意してほしい点：所有格を無理に全部訳さない\n"
                "＃例①\n"
                "【英文】At some point, our kids will be out in the world and their self-esteem will be pivotal to their success. \n"
                "【悪い日本語訳の例】いつか私たちの子供たちが世界に飛び立った時、彼らの自尊心は成功の大きな要となるでしょう。 \n"
                "【良い日本語訳の例】いつか子供たちが世界に旅立ったとき、自尊心は成功の大きな要となるでしょう。\n"
                "＃例②\n"
                "【英文】The Company aims to nearly double its number of restaurants. \n"
                "【悪い日本語訳の例】その会社は自社のレストランの店舗数をほぼ倍にすることを目指している。 \n"
                "【良い日本語訳の例】その会社はレストランの店舗数をほぼ倍にすることを目指している。 \n"
                "＃注意してほしい点：複数形は状況によっては無理に訳さない\n"
                "＃例①\n"
                "【英文】The task of facilitating language learning for our children may seem complicated.\n"
                "【悪い日本語訳の例】子供たちに外国語を学ばせることは難しいように思うかもしれません。\n"
                "【良い日本語訳の例】子供に外国語を学ばせることは難しいように思うかもしれません。\n"
                "＃例②\n"
                "【原文】For parents, preparing a list of questions before an appointment is a good start as teachers are busy.\n"
                "【悪い日本語訳の例】教師たちは忙しいので親はあらかじめ質問したいことを書き出して面談に臨むといいでしょう。\n"
                "【良い日本語訳の例】教師は忙しいので親はあらかじめ質問したいことを書き出して面談に臨むといいでしょう。 \n"
                "＃注意してほしい点：「any」は「もし～なら」に分解したほうがいい場合もある\n"
                "＃例①\n"
                "【英文】Any accident should be reported to the supervisor immediately.\n"
                "【悪い日本語訳の例】どんな事故も上司に報告されなければならない。\n"
                "【良い日本語訳の例】事故があった場合は必ず上司に報告しなければならない。\n"
                "＃例②\n"
                "【原文】Any member who is in doubt should submit a copy of the medical certificate from their doctor. \n"
                "【悪い日本語訳の例】疑いのあるいずれのメンバーも、医師の診断書を提出しなければならない。\n"
                "【良い日本語訳の例】自然な訳文：メンバーは、疑いがある場合は必ず医師の診断書を提出しなければならない。 \n"
                "＃注意してほしい点：名詞を動詞に、動詞を名詞に変換したほうが良い場合もある\n"
                "＃例①：名詞句を動詞句に変換する場合\n"
                "【英文】Exposure to organophosphates can cause headache and diarrhea.\n"
                "【悪い日本語訳の例】有機リン酸への暴露は頭痛と下痢を引き起こすことがある。\n"
                "【良い日本語訳の例】有機リン酸に晒されると頭痛と下痢が生じることがある。\n"
                "＃例②：動詞を名詞に変換する場合の英和翻訳例\n"
                "【英文】The strong sales of Japanese comic books is attributable to the expansion of the international e-commerce market.\n"
                "【悪い日本語訳の例】日本のマンガの好調な売り上げは海外のＥコマース市場の拡大に起因する。\n"
                "【良い日本語訳の例】日本のマンガの売上が好調な理由として海外のＥコマース市場の拡大が挙げられる。 \n"
                "＃注意してほしい点：受動態を能動態に、能動態を受動態に変換したほうが良い場合もある\n"
                "＃例①：受動態を能動態に変換する場合\n"
                "#①‐a\n"
                "【英文】They wer examined by their respective family doctors.\n"
                "【悪い日本語訳の例】彼らはそれぞれかかりつけ医により診察された。\n"
                "【良い日本語訳の例】彼らはそれぞれかかりつけ医の診察を受けた。\n"
                "#①-b\n"
                "【原文】Any problem has to be resolved by employees.\n"
                "【悪い日本語訳の例】いかなる問題も従業員によって解決されなければならない。\n"
                "【良い日本語訳の例】いかなる問題も従業員が解決しなければならない。\n"
                "＃例②能動態を受動態に変換する場合\n"
                "【英文】How technology enables business model innovation.\n"
                "【悪い日本語訳の例】テクノロジーがいかにビジネスモデルのイノベーションを可能にしているか。\n"
                "【良い日本語訳の例】テクノロジーによりいかにビジネスモデルのイノベーションがもたらされるか。 \n"
                "＃注意してほしい点：使役動詞はかみ砕いて訳した方がいい場合が多い\n"
                "＃例①\n"
                "【英文】This combination of experience and innovation has made the company so successful. \n"
                "【悪い日本語訳の例】この経験とイノベーションの組み合わせがその企業を成功させた。 \n"
                "【良い日本語訳の例】この経験とイノベーションこそがその企業を成功に導いた要因だ。\n"
                "＃例②\n"
                "【原文】Professor Smith has made me want to become a teacher.\n"
                "【悪い日本語訳の例】スミス教授は私を先生になりたくさせた。\n"
                "【良い日本語訳の例】スミス教授に出会って私は先生になりたいと思った。\n"
                "＃注意してほしい点：「～ための」の「to」や「for」を訳し下げる\n"
                "＃例①\n"
                "【英文】Lisa had turned her head to observe the birds climbing into the blue sky. \n"
                "【悪い日本語訳の例】リサは鳥たちが青い空へと飛び立っていくのを見るために振り返った。\n"
                "【良い日本語訳の例】リサが振り返ると鳥たちが青い空へと飛び立っていくのが見えた。\n"
                "＃例②\n"
                "【英文】The application shall be submitted to the president for review. \n"
                "【悪い日本語訳の例】申込書は確認のために社長に提出されなければならない。\n"
                "【良い日本語訳の例】申込書を提出し社長の確認を受けなければならない。\n"
            )
            st.session_state["user_input"] = initial_prompt
            communicate(initial_prompt, bot_response_placeholder, model)

elif selected_option == "Audit Planning":
    st.title("Audit Planning")

    # チェックボックス
    checkboxes = ["Audit Outline","Audit Items and Focus","Assumed Risks", "Expected Controls", "Criteria", "Interview Items","Test of Design","Test of Effectiveness", "Audit evidence(document/data name)", "Department","Assumed Findings"] # 監査概要, 監査項目・着眼点, 想定されるリスク, 期待されるコントロール, 規準, インタビュー項目, デザインの有効性評価, 運用状況の有効性評価, 監査証拠（資料名・データ名）, 対象部門, 想定される発見事項
    selected_items = []
    for checkbox in checkboxes:
        if st.sidebar.checkbox(checkbox, key=f"checkbox_{checkbox}"):
            selected_items.append(checkbox)

    # 右側の入力フォーム
    theme = st.text_area("Enter the theme you wish to verify, select a menu from the left, and press the Send message button. | 検証したいテーマを入力し、左からメニューを選んで、送信ボタンを押してください。", "", key="theme_input")

    # 追加：補足情報の入力フィールド
    additional_info = st.text_area("Please enter supplemental information. | 補足情報を入力してください。", "", key="additional_info")

    # Create a placeholder for the bot's responses
    bot_response_placeholder = st.empty()

    if st.button("Send message", key="send_button_auditors_view"):
        if "Test of Design" in selected_items or "Test of Effectiveness" in selected_items:
            # ToD or ToE を選択した場合に送信するメッセージ
            initial_prompt = (
                "あなたは優秀な内部監査人です。\n"
                f"{theme}の有効性評価の方法を設計面と運用面のそれぞれから説明してください。\n"
                "運用の有効性評価は監査で検証すべきサンプルの件数も記載。件数はコントロールが実施される頻度に応じて決まる。\n"
                "例えばITコントロールの場合は1件サンプルを入手する。\n"
                "例えば人手によるマニュアルコントロールが日次または1日複数回実施される場合は50件サンプルを入手する。\n"
                "例えば人手によるマニュアルコントロールが不定期に実施される場合は25件のサンプルを入手する。\n"
                "例えば人手によるマニュアルコントロールが週次で実施される場合は5件のサンプルを入手する。\n"
                "例えば人手によるマニュアルコントロールが月次または四半期で実施される場合は3件のサンプルを入手する。\n"
                "例えば人手によるマニュアルコントロールが半期で実施される場合は2件のサンプルを入手する。\n"
                "例えば人手によるマニュアルコントロールが年次で実施される場合は1件のサンプルを入手する。\n"
                "以下は補足情報です。\n"
                f" {additional_info}"
            )
        else:
            # ToD や ToE を選択していない場合に送信するメッセージ
            initial_prompt = (
                "あなたは優秀な内部監査人です。\n"
                f"{theme}に関する「{'」「'.join(selected_items)}」について教えて。\n"
                "以下は補足情報です。\n"
                f"補足情報: {additional_info}"
               "以下は注意点です。\n"
                f"明確な公的なガイダンスや法令等がない場合はその旨を教えて。世の中に存在しない公的なガイダンスや法令等を教えたり、不正確な公的なガイダンスや法令等の名称を教えることは絶対にしないでください。\n"
            )

        st.session_state["user_input"] = initial_prompt
        communicate(initial_prompt, bot_response_placeholder, model)

elif selected_option == "Data Analytics":
    st.title("Data Analytics")

    # 長文が入力できるフィールド
    data = st.text_area("Please enter the data to be verified. | 検証するデータを入力してください", height=200, key="data_input")

    # 検証作業の内容を入力するフィールド
    verification = st.text_input("Please enter the details of your validation work | 検証作業の内容を入力してください", key="verification_input")

    # Create a placeholder for the bot's responses
    bot_response_placeholder = st.empty()

    # ボタンを押すと、初期プロンプトが生成され、communicate関数が実行される
    if st.button("Send message", key="send_button_data_analytics"):
        initial_prompt = (
            f"以下のデータについて「{verification}」を実施してください。。\n"
            f"\n{data}"
        )
        st.session_state["user_input"] = initial_prompt
        communicate(initial_prompt, bot_response_placeholder, model)

        # Clear the user input
        st.session_state["user_input"] = ""

elif selected_option == "Inspection":
    st.title("Inspection")

    # 入力フィールドを３つ表示
    input1 = st.text_area("Document | 文書")
    input2 = st.text_area("Criteria | クライテリア")

    # Create a placeholder for the bot's responses
    bot_response_placeholder = st.empty()

    # ボタンを押すと、初期プロンプトが生成され、communicate関数が実行される
    if st.button("Send message", key="send_button_review_procedure"):
        initial_prompt = (
            f"以下の文書について「{input2}」をクライテリアにして監査して。"
            "文書："
            f"\n{input1}\n"
        )
        st.session_state["user_input"] = initial_prompt
        communicate(initial_prompt, bot_response_placeholder, model)

        # Clear the user input
        st.session_state["user_input"] = ""

# 新しい機能「Risk Assessment」のUIを追加
elif selected_option == "Risk Assessment":
    st.title("Risk Assessment")

    # サイドバーのチェックボックス
    checkboxes = ["Audit Universe","Bottom-UP","Top-Down","Annual Audit Plan"] # 監査ユニバース, ボトムアップ, トップダウン, 年度監査計画書
    selected_items = []
    for checkbox in checkboxes:
        if st.sidebar.checkbox(checkbox, key=f"checkbox_offsite_{checkbox}"):
            selected_items.append(checkbox)

    # 右側の入力フィールド
    company_info = st.text_area("Please enter the company information. | 会社の情報を入力してください。", "", key="company_info_input")

    # 右側の入力フィールド
    external_env_target = st.text_area("Please enter the status of the external environment. | 外部環境の状況を入力してください", "", key="monitoring_target_input")

    # 監査ユニバースの入力フィールド
    audit_universe = st.text_area("Please enter the audit universe. | 監査ユニバースを入力してください", "", key="audit_universe")

    # 追加：補足情報の入力フィールド
    additional_info = st.text_area("Please enter supplemental information. | 補足情報を入力してください。", "", key="additional_info")

    # Create a placeholder for the bot's responses
    bot_response_placeholder = st.empty()

    # Execute the communicate function when the user presses the 'Submit' button
    if st.button("Send message", key="send_button_offsite_monitoring"):

        # Build the initial prompt based on selected checkboxes
        initial_prompt_parts = ["あなたは優秀な内部監査人で、会社のリスクを特定・評価するエキスパートです。"]
        if "Audit Universe" in selected_items:
            initial_prompt_parts.append(
                f"{company_info}の監査ユニバース（事業、業務、プロジェクト等）教えて。出力は１段階のインデントで短く記載して。\n"
            )
        if "Top-Down" in selected_items:
            initial_prompt_parts.append(
                "以下を踏まえたマクロリスクアセスメント（PEST分析）をしてください。一部想像が含まれても構いません。\n"
                f"会社の情報:\n{company_info}\n"
                f"外部環境の状況:\n{external_env_target}\n"
                f"補足情報:\n{additional_info}\n"
            )
        if "Bottom-UP" in selected_items:
          initial_prompt_parts.append(
                "以下を参考にして組織全体を対象にしたRisk Assessmentを実施して下さい。\n"
                "縦軸に監査ユニバースを記載してください。\n"
                "横軸にはInherent RiskとしてStrategy Risk・Governance Risk・Market Risk・Credit Risk・Liquidity Risk・Operational Risk・HR Risk・Compliance Risk・IT Risk・Security Risk・Outsourcing Risk・BCP Riskの順で列を表示して、それぞれを3/2/1で評価し、最終列にTotalを記載）、Control（Satisfactory/Needs Improvement/Weakの3段階で評価）、Residual Risk（H/M/Lの3段階で評価）、Priority、Audit Timingを記載してください。最終行に縦軸のTotalも記載してください。\n" # 戦略リスク・ガバナンスリスク・市場リスク・信用リスク・流動性リスク・オペリスク・人材リスク・コンプライアンスリスク,ITリスク・セキュリティリスク・外部委託リスク・事業継続リスク
                "Inherent Risk、Control、Residual Riskの評価の定義を記載してください。何をもって3/2/1などに評価するかを定性的・定量的な観点から記載してください。Inherent Riskであれば財務的な影響度、コンプライアンス的な影響度、レピュテーション的な影響度といった観点があります。Controlであれば、規程類の整備状況、自主点検の結果、直近の監査結果といった観点があります。"
                "Inherent Riskについては、表のそれぞれのセルについて、なぜその評価結果としたのかできるだけ詳しく説明してください。"
                "出力の最後にSummary of Evaluationを詳しく記載して下さい。"
                f"Audit Universe:\n{audit_universe}\n"
                f"補足情報:\n{additional_info}\n"
                "表形式で出力してください。"
            )
        if "Annual Audit Plan" in selected_items:
            initial_prompt_parts.append(
                "###以下の内容を踏まえた年度監査計画書を作成してください。\n"
                f"Company Information：\n{company_info}\n"
                f"Audit Area：\n{audit_universe}\n"
                "###出力形式\n"
                "・Basic Policy\n"
                "・Key Audit Areas and Key Focus Points\n"
                "・Resources（業務監査チーム5名、システム監査チーム2名、コンプライアンス監査チーム3名、企画グループ2名それぞれに必要な年間工数（時間）を記載。1人当たりの年間工数は1770時間換算とする。全員分の総合計も表示。）\n"
                "・Schedule（縦軸に監査名を記載して。横軸に12か月分のスケジュールを記載して。1つの監査は3か月で終了するようにして。監査期間には●を記載して。表形式で出力して。）\n"
            )
        # Combine the parts into a single string
        initial_prompt = "\n".join(initial_prompt_parts)

        # Store the initial prompt in the session state
        st.session_state["user_input"] = initial_prompt

        # Execute the communication
        communicate(initial_prompt, bot_response_placeholder, model)

        # Clear the user input
        st.session_state["user_input"] = ""

# Continuous MonitoringのUIを追加
elif selected_option == "Continuous Monitoring":
    st.title("Continuous Monitoring")

    # サイドバーのチェックボックス
    checkboxes = ["Monitoring Item", "Documents and data to be obtained", "Abnormal values or trends to be detected"] # モニタリング項目, 入手すべき資料やデータ, 検知すべき異常値や傾向
    selected_items = []
    for checkbox in checkboxes:
        if st.sidebar.checkbox(checkbox, key=f"checkbox_offsite_{checkbox}"):
            selected_items.append(checkbox)

    # 右側の入力フィールド
    monitoring_target = st.text_input("Please enter monitoring targets. | モニタリング対象を入力してください。", "", key="monitoring_target_input")

    # 追加：補足情報の入力フィールド
    additional_info = st.text_area("Please enter supplemental information. | 補足情報を入力してください。", "", key="additional_info")

    # Create a placeholder for the bot's responses
    bot_response_placeholder = st.empty()

    # Execute the communicate function when the user presses the 'Submit' button
    if st.button("Send message", key="send_button_offsite_monitoring"):
        initial_prompt = (
            "あなたは優秀な内部監査人で、継続的モニタリングのエキスパートです。\n"
            f"「{monitoring_target}」をモニタリング対象とした時の"
            f"「{'」「'.join(selected_items)}」について教えてください。\n"
            f"補足情報: {additional_info}\n"
        )
        st.session_state["user_input"] = initial_prompt
        communicate(initial_prompt, bot_response_placeholder, model)

        # Clear the user input
        st.session_state["user_input"] = ""

        # Continuous MonitoringのUIを追加

elif selected_option == "RootCause Analysis":
    st.title("RootCause Analysis")

    # サイドバーのチェックボックス
    checkboxes = ["Problem Fact", "Cause Analysis", "Improvement Suggestions"] # 問題の事実, 原因分析, 改善提案
    selected_items = []
    for checkbox in checkboxes:
        if st.sidebar.checkbox(checkbox, key=f"checkbox_offsite_{checkbox}"):
            selected_items.append(checkbox)

    # 右側の入力フィールド
    fact_info = st.text_area("Please enter the nature of the problem or issue you have discovered. | 発見した問題・課題の内容を入力してください。", "", key="fact_info_input")

    # 追加：補足情報の入力フィールド
    additional_info = st.text_area("Please enter supplemental information. | 補足情報を入力してください。", "", key="additional_info")

    # Create a placeholder for the bot's responses
    bot_response_placeholder = st.empty()

    # Execute the communicate function when the user presses the 'Submit' button
    if st.button("Send message", key="send_button_offsite_monitoring"):

        # Build the initial prompt based on selected checkboxes
        initial_prompt_parts = ["あなたは優秀な内部監査人で、問題や発見の発見・把握や根本原因分析のエキスパートです。"]
        if "Problem Fact" in selected_items:
            initial_prompt_parts.append(
                f"「・{fact_info}\n・{additional_info}\n」を踏まえ、問題の事実を詳しく記載してください。一部想像が含まれても構いません。想定・示唆される潜在的なリスクにも言及してください。\n"
                "文章は能動態かつ過去形で記載してください。語調は「ですます調」ではなく「である調」で記載してください。\n"
            )
        if "Cause Analysis" in selected_items:
            initial_prompt_parts.append(
                f"「・{fact_info}\n・{additional_info}\n」を踏まえ、以下の３つの観点から原因を分析してください。\n"
                "直接原因（問題を引き起こした直接の原因）\n"
                "背景原因（直接原因を防止できなかった間接的な原因）\n"
                "根本原因（背景原因が認識されていながら放置されるに至った真因）\n"
                "原因の記載にあたっては、箇条書きで挙げつつ、原因を特定または推察した理由をできるだけ詳しく具体的に記載してください。\n"
                "語調は「ですます調」ではなく「である調」で記載してください。\n"
            )
        if "Improvement Suggestions" in selected_items:
            initial_prompt_parts.append(
                f"「・{fact_info}\n・{additional_info}\n」を踏まえ、改善提案を作成してください"
            )
        # Combine the parts into a single string
        initial_prompt = "\n".join(initial_prompt_parts)

        # Store the initial prompt in the session state
        st.session_state["user_input"] = initial_prompt

        # Execute the communication
        communicate(initial_prompt, bot_response_placeholder, model)

        # Clear the user input
        st.session_state["user_input"] = ""
