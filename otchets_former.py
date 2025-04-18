import json

# Загрузи сюда свой dict, например из JSON-файла или напрямую
with open('mr_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

html_template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Отчёт по Merge Request'ам</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2, h3 {{ color: #333; }}
        .mr-block {{ border: 1px solid #ccc; padding: 15px; margin-bottom: 25px; border-radius: 10px; }}
        .score {{ font-weight: bold; color: #2e8b57; }}
        .section-title {{ font-weight: bold; margin-top: 10px; }}
        ul {{ padding-left: 20px; }}
        li {{ margin-bottom: 5px; }}
    </style>
</head>
<body>
    <h1>Анализ Merge Request'ов</h1>
    <p><strong>Репозиторий:</strong> {repo}</p>
    <p><strong>Автор:</strong> {user}</p>
    <p><strong>Период:</strong> {start} — {end}</p>
    <p><strong>Всего MR:</strong> {total}</p>
    <hr>
    {mr_blocks}
</body>
</html>
"""

mr_template = """
<div class="mr-block">
    <h2>MR #{mr_number}</h2>
    <p><a href="{url}" target="_blank">Ссылка на коммит</a></p>
    <p><strong>Сложность:</strong> {complexity} | <span class="score">Оценка: {score}</span></p>

    {problems_section}
    {antipatterns_section}
    {positives_section}
    {impacts_section}
</div>
"""

def render_items(title, items, key_name, key_desc, key_lines):
    if not items:
        return ""
    html = f'<div class="section-title">{title}:</div><ul>'
    for item in items:
        lines = f" (строки: {', '.join(map(str, item[key_lines]))})" if item.get(key_lines) else ""
        html += f"<li><strong>{item[key_name]}</strong>: {item[key_desc]}{lines}</li>"
    html += "</ul>"
    return html

def render_section(title, entries):
    if not entries:
        return ""
    html = f'<div class="section-title">{title}:</div><ul>'
    for e in entries:
        affected = ", ".join(e.get("affected_components", []))
        html += f"<li>{e['description']}<br><em>Затронутые компоненты:</em> {affected}</li>"
    html += "</ul>"
    return html

def generate_html(report):
    mr_blocks = ""
    for mr in report["results"]:
        problems_html = ""
        for level in ["critical", "regular", "minor"]:
            problems_html += render_items(
                f"Проблемы ({level})",
                mr["problems"].get(level, []),
                "type", "description", "lines"
            )

        antipatterns_html = render_items("Антипаттерны", mr["antipatterns"], "name", "description", "lines")
        positives_html = render_items("Положительные аспекты", mr["positives"], "aspect", "lines", "lines")
        impacts_html = render_section("Влияние изменений", mr["impacts"])

        mr_html = mr_template.format(
            mr_number=mr["mr_number"],
            url=mr["url"],
            complexity=mr["complexity"],
            score=mr["score"],
            problems_section=problems_html,
            antipatterns_section=antipatterns_html,
            positives_section=positives_html,
            impacts_section=impacts_html,
        )
        mr_blocks += mr_html

    return html_template.format(
        repo=report["metadata"]["repo"],
        user=report["metadata"]["user"],
        start=report["metadata"]["period"]["start"],
        end=report["metadata"]["period"]["end"],
        total=report["metadata"]["total"],
        mr_blocks=mr_blocks
    )

# Сохраняем HTML в файл
html_output = generate_html(report)
with open("mr_report.html", "w", encoding="utf-8") as f:
    f.write(html_output)

print("Отчёт сохранён как mr_report.html")
