import re

def clean(text):
    return re.sub(r"\s+", "", text or "")

def highlight(text, terms):
    if not text:
        return ""
    for term in terms:
        if term in text:
            text = text.replace(term, f"<span style='color:red'>{term}</span>")
    return text

def parse_law_xml(xml_data, terms, unit):
    import xml.etree.ElementTree as ET
    tree = ET.fromstring(xml_data)
    articles = tree.findall(".//조문")

    # 🐞 디버그 출력
    print(f"[DEBUG] ▶ terms: {terms}")
    print(f"[DEBUG] ▶ unit: {unit}")
    print(f"[DEBUG] ▶ 조문 수: {len(articles)}")

    def match_logic(text):
        cleaned = clean(text)
        include = [t for t in terms if not t.startswith('-') and t in cleaned]
        exclude = [t[1:] for t in terms if t.startswith('-')]

        # 🐞 디버그 출력
        print(f"[DEBUG] ▶ 검사 중 텍스트: {cleaned}")
        print(f"[DEBUG] ▶ 포함 조건: {include}")
        print(f"[DEBUG] ▶ 제외 조건: {exclude}")

        if all(i in cleaned for i in include) and not any(e in cleaned for e in exclude):
            return True
        return False

    results = []
    for article in articles:
        jo = article.findtext("조번호", "").strip()
        title = article.findtext("조문제목", "") or ""
        content = article.findtext("조문내용", "") or ""
        항들 = article.findall("항")

        조출력 = False
        항목들 = []

        if unit == "조" and match_logic(title + content):
            조출력 = True

        for 항 in 항들:
            항번호 = 항.findtext("항번호", "").strip()
            항내용 = 항.findtext("항내용", "") or ""
            text_to_check = 항내용

            for 호 in 항.findall("호"):
                text_to_check += 호.findtext("호내용", "") or ""
                for 목 in 호.findall("목"):
                    text_to_check += 목.findtext("목내용", "") or ""

            if unit == "항" and match_logic(text_to_check):
                조출력 = True

            항목들.append((항번호, text_to_check))

        if unit == "법률":
            for 항번호, text in 항목들:
                if match_logic(text):
                    조출력 = True

        if 조출력:
            html = f"<b>제{jo}조 {title}</b> "
            if 항목들:
                html += "<br>"
                for 항번호, text in 항목들:
                    if match_logic(text):
                        html += f"  ⓞ{항번호} {highlight(text, terms)}<br>"
            else:
                html += highlight(content, terms)
            results.append(html)

    print(f"[DEBUG] ▶ 최종 결과 조문 수: {len(results)}")
    return results
