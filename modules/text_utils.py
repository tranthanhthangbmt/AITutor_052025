import re
from bs4 import BeautifulSoup
import streamlit as st
import fitz  # pip install pymupdf

def clean_html_to_text(text):
    """
    Xóa HTML tags và trả về văn bản thuần túy.
    """
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

def format_mcq_options(text):
    """
    Tách các lựa chọn A. B. C. D. thành dòng riêng biệt.
    """
    text = re.sub(r'\s*A\.', r'\nA.', text)
    text = re.sub(r'\s*B\.', r'\nB.', text)
    text = re.sub(r'\s*C\.', r'\nC.', text)
    text = re.sub(r'\s*D\.', r'\nD.', text)
    return text

def convert_to_mathjax(text):
    """
    Bọc biểu thức trong dấu ngoặc thành \( ... \) nếu phù hợp.
    """
    def is_inline_math(expr):
        math_keywords = ["=", "!", r"\\times", r"\\div", r"\\cdot", r"\\frac", "^", "_",
                         r"\\ge", r"\\le", r"\\neq", r"\\binom", "C(", "C_", "n", "k"]
        return any(kw in expr for kw in math_keywords)

    def wrap_inline(match):
        expr = match.group(1).strip()
        return f"\\({expr}\\)" if is_inline_math(expr) else match.group(0)

    return re.sub(r"\\(([^()]+)\\)", wrap_inline, text)

def convert_to_mathjax1(text):
    """
    Phiên bản nâng cao: bảo vệ biểu thức đúng, tự động bọc biểu thức chưa được gói.
    """
    protected_patterns = [
        r"\\\\\([^\(\)]+?\\\\\)",
        r"\\\\\[[^\[\]]+?\\\\\]",
        r"\$\$[^\$]+\$\$",
        r"`[^`]+?`"
    ]

    def protect_existing(expr):
        return re.sub('|'.join(protected_patterns), lambda m: f"{{{{PROTECTED:{m.group(0)}}}}}", expr)

    def restore_protected(expr):
        return re.sub(r"\{\{PROTECTED:(.+?)\}\}", lambda m: m.group(1), expr)

    def is_math_expression(expr):
        math_keywords = ["=", "!", r"\\times", r"\\div", r"\\cdot", r"\\frac", "^", "_",
                         r"\\ge", r"\\le", r"\\neq", r"\\binom", "C(", "C_", "n!", "A_", "C_"]
        return any(kw in expr for kw in math_keywords)

    def wrap_likely_math(match):
        expr = match.group(0).strip()
        return f"\\({expr}\\)" if is_math_expression(expr) else expr

    text = protect_existing(text)
    text = re.sub(r"(?<!\\)(\b[^()\n]{1,50}\([^()]+\)[^()\n]{0,50})", wrap_likely_math, text)
    text = restore_protected(text)
    return text

def convert_parentheses_to_latex(text):
    """
    Chuyển biểu thức trong ( ) thành \( ... \) nếu có từ khóa toán học.
    """
    def is_math_expression(expr):
        math_keywords = ["=", "!", r"\\times", r"\\div", r"\\cdot", r"\\frac", "^", "_",
                         r"\\ge", r"\\le", r"\\neq", r"\\binom", "C(", "C_", "n", "k"]
        return any(keyword in expr for keyword in math_keywords) or re.fullmatch(r"[a-zA-Z0-9_+\-*/\\s(),]+", expr)

    return re.sub(r"\\(([^()]+)\\)",
                  lambda m: f"\\({m.group(1).strip()}\\)" if is_math_expression(m.group(1)) else m.group(0),
                  text)

#Hàm xử lý Heading từ PDF 
def extract_headings_with_levels(pdf_path):
    doc = fitz.open(pdf_path)
    headings = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    line_text = ""
                    font_sizes = set()

                    for span in line["spans"]:
                        line_text += span["text"].strip()
                        font_sizes.add(span["size"])

                    if line_text:
                        max_font = max(font_sizes)
                        if max_font > 12:
                            if max_font > 18:
                                level = 0
                            elif max_font > 15:
                                level = 1
                            else:
                                level = 2
                            headings.append((level, line_text))
    return headings

def generate_sidebar_radio_from_headings(headings):
    options = ["__none__"]
    labels = ["-- Chọn mục để bắt đầu --"]

    # ✅ Ký hiệu phân cấp rõ ràng và đẹp mắt
    prefix_symbols = ["", "➤ ", "  • ", "   → ", "    ◦ "]
    #prefix_symbols = ["", "- ", "  - ", "   - ", "    - "]

    for idx, (level, text) in enumerate(headings):  # ✅ sửa lỗi thiếu dấu phẩy
        symbol = prefix_symbols[min(level, len(prefix_symbols) - 1)]
        label = f"{symbol}📌 {text}"
        options.append(f"{idx}")
        labels.append(label)

    selected_raw = st.radio(
        "Chọn mục để học:",
        options=options,
        format_func=lambda x: labels[options.index(x)],
        key="selected_heading_radio"
    )

    if selected_raw != "__none__":
        idx = int(selected_raw)
        selected_heading = headings[idx]
        st.session_state["selected_part_for_discussion"] = {
            "level": selected_heading[0],
            "tieu_de": selected_heading[1]
        }
        st.session_state["force_ai_to_ask"] = True
        
#Hiển thị st.radio() từ headings có thụt đầu dòng:
# def generate_sidebar_radio_from_headings(headings):
#     options = ["__none__"]
#     labels = ["-- Chọn mục để bắt đầu --"]

#     for idx, (level, text) in enumerate(headings):
#         indent = " " * level  # dùng em-space để đẹp hơn dấu cách
#         label = f"{indent}📌 {text}"
#         options.append(f"{idx}")  # chỉ số duy nhất
#         labels.append(label)

#     selected_raw = st.radio(
#         "Chọn mục để học:",
#         options=options,
#         format_func=lambda x: labels[options.index(x)],
#         key="selected_heading_radio"
#     )

#     if selected_raw != "__none__":
#         idx = int(selected_raw)
#         selected_heading = headings[idx]
#         st.session_state["selected_part_for_discussion"] = {
#             "level": selected_heading[0],
#             "tieu_de": selected_heading[1]
#         }
#         st.session_state["force_ai_to_ask"] = True
        
#Hiển thị st.radio() từ headings có thụt đầu dòng:
# def generate_sidebar_radio_from_headings(headings):
#     options = ["__none__"]
#     labels = ["-- Chọn mục để bắt đầu --"]

#     # ✅ Ký hiệu phân cấp rõ ràng và đẹp mắt
#     prefix_symbols = ["", "➤ ", "  • ", "   → ", "    ◦ "]

#     for idx, (level text) in enumerate(headings):
#         symbol = prefix_symbols[min(level, len(prefix_symbols) - 1)]
#         label = f"{symbol}📌 {text}"
#         options.append(f"{idx}")
#         labels.append(label)

#     selected_raw = st.radio(
#         "Chọn mục để học:",
#         options=options,
#         format_func=lambda x: labels[options.index(x)],
#         key="selected_heading_radio"
#     )

#     if selected_raw != "__none__":
#         idx = int(selected_raw)
#         selected_heading = headings[idx]
#         st.session_state["selected_part_for_discussion"] = {
#             "level": selected_heading[0],
#             "tieu_de": selected_heading[1]
#         }
#         st.session_state["force_ai_to_ask"] = True

