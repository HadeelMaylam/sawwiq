import os
import streamlit as st
import requests
import anthropic
from io import BytesIO
import random

from dotenv import load_dotenv

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from langchain_community.utilities import GoogleSearchAPIWrapper

##############################
# تهيئة المفاتيح والـ API
##############################
# load_dotenv()  # تحميل المتغيرات من ملف .env

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
# Streamlit Secrets
ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
GOOGLE_CSE_ID = st.secrets["GOOGLE_CSE_ID"]


openai.api_key = OPENAI_API_KEY
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
google_search = GoogleSearchAPIWrapper(
    google_api_key=GOOGLE_API_KEY,
    google_cse_id=GOOGLE_CSE_ID
)

##############################
# إعداد واجهة الصفحة الافتراضية
##############################
st.set_page_config(page_title="سوّق", layout="centered")

##############################
# ضبط اتجاه النصوص إلى اليمين
##############################
st.markdown(
    """
    <style>
    body {
        direction: rtl;
        text-align: right;
        background-color: #ffffff !important;
        color: #000000;
    }
    .stButton > button {
        direction: rtl;
    }
    .stTextInput > div > div {
        text-align: right;
    }
    .stRadio > div {
        direction: rtl;
    }
    .stTextArea > label {
        text-align: right;
    }
    .stSelectbox > label {
        text-align: right;
    }
    .streamlit-expanderHeader {
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

##############################
# استخدام حالة الجلسة للتنقل
##############################
if "page" not in st.session_state:
    st.session_state.page = "home"

##################################################################
# الصفحة الأولى: الصفحة الرئيسية (Home) مع عرض الشعار والأزرار
##################################################################
def home_page():
    st.image("logo.pNg", width=1000)  # غيّر هذا المسار إن كان يختلف اسم الملف أو مكانه
    st.title("سوّق")
    st.markdown("### أداة تعمل بتقنيات الذكاء الاصطناعي لإنشاء محتوى تسويقي جذاب خلال ثواني")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("مستشارك التسويقي الذكي"):
            st.session_state.page = "marketing_advisor"  # الانتقال لصفحة التحليل
            st.rerun()

    with col2:
        if st.button("كتابة محتوى نصي"):
            st.session_state.page = "text_content"       # الانتقال لصفحة المحتوى النصي
            st.rerun()



##################################################################
##################################################################

##################################################################
# مثال لصفحة كتابة المحتوى النصي (text_content)
# (نفس فكرة marketing_content_section في الكود السابق)
##################################################################
def text_content_page():
    st.title("معلومات المحتوى التسويقي")

    if "content_type" not in st.session_state:
        st.session_state.content_type = "نشر خبر"
    if "event" not in st.session_state:
        st.session_state.event = "لا شيء"
    if "marketing_field" not in st.session_state:
        st.session_state.marketing_field = "التسويق الرقمي"
    if "target_audience" not in st.session_state:
        st.session_state.target_audience = []
    if "comments" not in st.session_state:
        st.session_state.comments = ""
    if "results" not in st.session_state:
        st.session_state.results = []
    if "show_regenerate_button" not in st.session_state:
        st.session_state.show_regenerate_button = False
    if "recommendation" not in st.session_state:
        st.session_state.recommendation = ""
    
    st.session_state.comments = st.text_area("أضف تفاصيل حول منتجك هنا:", value=st.session_state.comments)
    if st.button("توصية لاختيار نوع المحتوى التسويقي"):
        if st.session_state.comments:
            recommended_type = get_recommended_marketing_type(st.session_state.comments, 
                                                                 ["نشر خبر", "إعلان نصي", "سرد قصصي", "سرد تحفيزي", "محتوى تفصيلي", "محتوى مختصر", "أخرى"])
            st.session_state.recommendation = f"التوصية: أفضل نوع تسويقي لمنتجك هو '{recommended_type}'"
            st.success(st.session_state.recommendation)
        else:
            st.warning("يرجى إدخال وصف المنتج للحصول على التوصية.")
    # القوائم المنسدلة والاختيارات
    st.session_state.content_type = st.selectbox(
        "اختر نوع المحتوى التسويقي:",
        ["نشر خبر", "إعلان نصي", "سرد قصصي", "سرد تحفيزي", "محتوى تفصيلي", "محتوى مختصر", "أخرى"],
        index=["نشر خبر", "إعلان نصي", "سرد قصصي", "سرد تحفيزي", "محتوى تفصيلي", "محتوى مختصر", "أخرى"].index(st.session_state.content_type)
    )

    if st.session_state.content_type == "أخرى":
        st.session_state.content_type = st.text_input("أدخل نوع المحتوى التسويقي:", value=st.session_state.content_type)

    st.session_state.event = st.selectbox(
        "اختر المناسبة التي تريد التسويق لها:",
        ["يوم وطني", "عيد فطر", "عيد أضحى", "رمضان", "يوم التأسيس", "العطلة", "أخرى", "لا شيء"],
        index=["يوم وطني", "عيد فطر", "عيد أضحى", "رمضان", "يوم التأسيس", "العطلة", "أخرى", "لا شيء"].index(st.session_state.event)
    )

    if st.session_state.event == "أخرى":
        st.session_state.event = st.text_input("أدخل المناسبة:", value=st.session_state.event)

    st.session_state.marketing_field = st.selectbox(
        "اختر مجال التسويق:",
        ["التسويق الرقمي", "التسويق التقليدي", "تسويق المحتوى", 
         "التسويق عبر السوشيال ميديا", "التسويق عبر البريد الإلكتروني", "أخرى"],
        index=["التسويق الرقمي", "التسويق التقليدي", "تسويق المحتوى", 
               "التسويق عبر السوشيال ميديا", "التسويق عبر البريد الإلكتروني", "أخرى"].index(st.session_state.marketing_field)
    )

    if st.session_state.marketing_field == "أخرى":
        st.session_state.marketing_field = st.text_input("*أدخل مجال التسويق:", value=st.session_state.marketing_field)

    st.session_state.target_audience = st.multiselect(
        "*اختر الجمهور المستهدف:",
        ["الشركات", "الأفراد", "الشباب", "الأطفال", "الآباء", 
         "المهتمون بالتكنولوجيا", "المستثمرون", "أخرى"],
        default=st.session_state.target_audience
    )

    if "أخرى" in st.session_state.target_audience:
        custom_target_audience = st.text_input("أدخل جمهورًا مستهدفًا إضافيًا:")
        if custom_target_audience:
            st.session_state.target_audience = [audience for audience in st.session_state.target_audience if audience != "أخرى"] + [custom_target_audience]

    # st.session_state.comments = st.text_area("أضف تفاصيل حول منتجك هنا:", value=st.session_state.comments)
    # if st.button("توصية لاختيار نوع المحتوى التسويقي"):
    #     if st.session_state.comments:
    #         recommended_type = get_recommended_marketing_type(st.session_state.comments, 
    #                                                              ["نشر خبر", "إعلان نصي", "سرد قصصي", "سرد تحفيزي", "محتوى تفصيلي", "محتوى مختصر", "أخرى"])
    #         st.session_state.recommendation = f"التوصية: أفضل نوع تسويقي لمنتجك هو '{recommended_type}'"
    #         st.success(st.session_state.recommendation)
    #     else:
    #         st.warning("يرجى إدخال وصف المنتج للحصول على التوصية.")
    # col1, col2 = st.columns(2)
    # with col1:
    #     if st.button("توصية لاختيار نوع المحتوى التسويقي"):
    #         if st.session_state.comments:
    #             recommended_type = get_recommended_marketing_type(st.session_state.comments, 
    #                                                              ["نشر خبر", "إعلان نصي", "سرد قصصي", "سرد تحفيزي", "محتوى تفصيلي", "محتوى مختصر", "أخرى"])
    #             st.session_state.recommendation = f"التوصية: أفضل نوع تسويقي لمنتجك هو '{recommended_type}'"
    #             st.success(st.session_state.recommendation)
    #         else:
    #             st.warning("يرجى إدخال وصف المنتج للحصول على التوصية.")

    # with col2:
    if st.button("أرسل لسوّق"):
        if st.session_state.marketing_field and st.session_state.target_audience:
            summary_message = f"""
                النتائج:
                - مجال التسويق: {st.session_state.marketing_field}
                - الجمهور المستهدف: {', '.join(st.session_state.target_audience)}
                - نوع المحتوى التسويقي: {st.session_state.content_type}
                - المناسبة: {st.session_state.event}
                - الملاحظات: {st.session_state.comments}
                """
            st.markdown(summary_message)

                # توليد النص بناءً على المدخلات
            bot_response = model_text(
                    st.session_state.marketing_field,
                    st.session_state.target_audience,
                    st.session_state.content_type,
                    st.session_state.event,
                    st.session_state.comments,
                )
            st.session_state.bot_response = bot_response
            st.session_state.results.append(bot_response)

                # عرض النص التسويقي
            st.text_area("النص التسويقي المولد:", value=bot_response, height=200)

                # تفعيل زر إعادة التوليد بعد الإرسال الأول
            st.session_state.show_regenerate_button = True

    # زر إعادة التوليد (يظهر بعد الإرسال الأول)
    if st.session_state.show_regenerate_button:
        if st.button("🔄 إعادة التوليد"):
            if st.session_state.marketing_field and st.session_state.target_audience:
                bot_response = model_text(
                    st.session_state.marketing_field,
                    st.session_state.target_audience,
                    st.session_state.content_type,
                    st.session_state.event,
                    st.session_state.comments,
                )
                st.session_state.bot_response = bot_response
                st.session_state.results.append(bot_response)
                st.text_area("النص التسويقي المولد:", value=bot_response, height=200)

    # قسم النتائج السابقة
    st.subheader("النتائج السابقة")
    for i, result in enumerate(st.session_state.results, start=1):
        with st.expander(f"النتيجة {i}"):
            st.text_area("النص:", value=result, height=200)


def get_recommended_marketing_type(description, content_options):
    prompt = (
        f"أنت خبير في التسويق، بناءً على وصف المنتج التالي، "
        f"اختر أفضل نوع تسويق يناسبه من القائمة المقدمة:\n"
        f"وصف المنتج: {description}\n"
        f"الخيارات المتاحة: {', '.join(content_options)}\n"
        f"يرجى تقديم النوع الأنسب فقط دون تفاصيل إضافية."
    )
    try:
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}]
        )
        if response and hasattr(response, 'content'):
            return response.content[0].text.strip()
        else:
            return "تعذر تحديد النوع المناسب، الرجاء التحقق من المدخلات."
    except Exception as e:
        return f"حدث خطأ أثناء التوصية: {e}"

def model_text(marketing_field, target_audience, content_type, event, comments):
    user_message = (
        f"أجب كخبير تسويق. هدفك إنشاء نص تسويقي جذاب. "
        f"- مجال التسويق: {marketing_field}\n"
        f"- الجمهور المستهدف: {', '.join(target_audience) if target_audience else 'غير محدد'}\n"
        f"- نوع المحتوى التسويقي: {content_type}\n"
        f"- المناسبة: {event if event != 'لا شيء' else 'لا توجد مناسبة'}\n"
        f"- الملاحظات: {comments if comments else 'لا توجد ملاحظات'}\n"
    )
    try:
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": user_message}]
        )
        if response and hasattr(response, 'content'):
            return response.content[0].text
        else:
            return "تعذر توليد النص التسويقي."
    except Exception as e:
        return f"حدث خطأ أثناء توليد النص باستخدام Claude: {e}"

##################################################################
# صفحة مستشارك التسويقي الذكي (marketing_advisor)
# تحليل المحتوى من خلال البحث في جوجل + Claude
##################################################################
def marketing_advisor_page():
    st.title("مستشارك لتسويق منتجاتك بكل ذكاء")
    st.markdown("أدخل تفاصيل منتجك، وبقدم لك نصائح بناء على السوق العربي لليوم")

    product_name = st.text_input("أدخل اسم المنتج:")
    product_description = st.text_area("أدخل وصف المنتج:")

    if st.button("إرسال"):
        if product_name.strip() and product_description.strip():
            try:
                search_query = product_description

                with st.spinner("🔍  اقرأ لك السوق الآن ..."):
                    num = random.choice([5, 10, 7, 9,18])
                    search_results = google_search.results(search_query, num_results=num)

                # جلب الروابط من نتائج البحث
                urls = [result.get('link', '') for result in search_results]

                with st.spinner("📄 أحلل لك استراتجيات السوق.."):
                    # تشغيل الجلب غير المتزامن للروابط
                    page_contents = asyncio.run(fetch_all_content(urls))

                formatted_content = "\n\n".join(page_contents)

                # مثال توضيحي للاعتماد عليه في بناء النموذج
                example_content = """
                🌟 تمر العجوة الفاخر - مذاق الأجداد بنكهة حديثة

                **الوصف:**
                تمتع بمذاق تمر العجوة الفاخر، المقطوف بعناية من مزارع المدينة المنورة. يتميز بنكهته الغنية وقيمته الغذائية العالية.

                **المميزات التنافسية:**
                - طبيعي 100% بدون إضافات
                - حاصل على شهادة الجودة السعودية
                - طعم فريد وقوام ناعم
                - شحن سريع لجميع مناطق المملكة

                **الجمهور المستهدف:**
                - محبي التمور الفاخرة
                - المهتمون بالتغذية الصحية
                - الباحثون عن هدايا فاخرة

                **اقتراحات للحملات التسويقية:**
                1. **حملات موسمية:** عروض شهر رمضان
                2. **حملات رقمية:** فيديوهات عن فوائد التمر
                **شعار الحملة:** تمر العجوة – تراث أصيل، مذاق فريد
                """

                marketing_prompt = f"""
                اعتمد على المثال التالي لإنشاء محتوى تسويقي مشابه للمنتج التالي، 
                مع دراسة المحتوى المقدم واستنتاج استراتيجيات التسويق منه:

                **مثال:**
                {example_content}

                **المحتوى المستخرج من الإنترنت:**
                {formatted_content}

                **المطلوب:**
                - تحليل المحتوى المقدم واستخراج الاستراتيجيات التسويقية منه.
                - إنشاء محتوى تسويقي يشمل:
                  - وصف جذاب للمنتج.
                  - فوائد تنافسية.
                  - الجمهور المستهدف.
                  - اقتراحات للحملات التسويقية.
                  - شعار مناسب.

                يرجى التأكد من أن المحتوى يظهر بوضوح وبشكل منظم مع استخدام العناوين والقوائم.
                """

                with st.spinner("📝..."):
                    marketing_response = anthropic_client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1024,
                        messages=[{"role": "user", "content": marketing_prompt}]
                    )

                if marketing_response and hasattr(marketing_response, 'content'):
                    formatted_text = marketing_response.content[0].text
                else:
                    formatted_text = "تعذر جلب الاستجابة من Claude."

                # تحسين تنسيق النص
                formatted_text = formatted_text.replace("\n\n", "\n")

                st.markdown("### اقترح لك:")
                # st.markdown(formatted_text)
                st.markdown("""
    <style>
        .text-box {
            background-color: #F0F0F0; /* لون رصاصي فاتح */
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
            margin-bottom: 10px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.05);
            font-size: 16px;
            line-height: 1.6;
            color: #333;
        }
    </style>
""", unsafe_allow_html=True)
                formatted_text_html = formatted_text.replace("\n", "<br>")
# وضع النص داخل مربع رصاصي
                st.markdown(
    f"""
    <div class="text-box">
        {formatted_text_html }
    </div>
    """,
    unsafe_allow_html=True
)

                # st.markdown("### المصادر المستخدمة:")
                # for result in search_results:
                #     link = result.get('link', '#')
                #     title = result.get('title', 'عنوان غير متاح')
                #     if link and link != '#':
                #         st.link_button(f"{title}", link)
                #         # st.markdown(f"- [{title}]({link})")
                st.markdown("""
    <style>
        .source-container {
            border-radius: 12px;
            background-color: #F0F0F0; /* لون رصاصي فاتح للخلفية */
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.05);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .source-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .source-title {
            font-size: 16px;
            font-weight: bold;
            color: #000;
            margin: 0;
        }
        .source-url {
            font-size: 12px;
            color: #666;
            margin: 0;
        }
        .source-icon {
            font-size: 20px;
            margin-left: 8px;
        }
    </style>
""", unsafe_allow_html=True)
                st.markdown("<h3 style='text-align: right;'>📌 المصادر المستخدمة</h3>", unsafe_allow_html=True)
                for idx, result in enumerate(search_results, start=1):
                    st.markdown(
        f"""
        <div class="source-container">
            <div class="source-item">
                <span class="source-icon">🔗</span>
                <div>
                    <p class="source-title">{idx}. <a href="{result.get('link', '#')}" target="_blank" style="color: black; text-decoration: none;">{result.get('title', 'عنوان غير متاح')}</a></p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

            except Exception as e:
                st.error(f"❌ حدث خطأ: {e}")
        else:
            st.warning("⚠ الرجاء إدخال اسم المنتج ووصفه قبل الضغط على إرسال")



async def fetch_content_async(url):
    """جلب محتوى الصفحات بشكل غير متزامن (Async)"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    # نجلب 5 فقرات فقط
                    paragraphs = soup.find_all('p', limit=5)
                    return '\n'.join([p.get_text() for p in paragraphs])[:1500]
                else:
                    return f"❌ لم يتمكن من الوصول إلى {url} - حالة HTTP: {response.status}"
    except asyncio.TimeoutError:
        return f"⏳ انتهت مهلة الاتصال بالموقع: {url}"
    except Exception as e:
        return f"⚠️ خطأ أثناء جلب المحتوى من {url}: {e}"

async def fetch_all_content(urls):
    tasks = [fetch_content_async(url) for url in urls if url]
    results = await asyncio.gather(*tasks)
    return results

########################################
# توجيه الصفحات بناءً على session_state
########################################
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "marketing_advisor":
    marketing_advisor_page()
elif st.session_state.page == "text_content":
    text_content_page()
# elif st.session_state.page == "brand_design":
#     brand_design_page()
st.markdown("---")
st.markdown("Sawq Team, 2025")
