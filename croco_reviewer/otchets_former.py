import json

class MRReportRenderer:
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.report = self._load_report()

    def _load_report(self):
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _render_items(self, title, items, key_name, key_desc, key_lines):
        if not items:
            return ""
        html = f'<div class="section-title">{title}:</div><ul>'
        for item in items:
            lines = f" (строки: {', '.join(map(str, item.get(key_lines, [])))})" if item.get(key_lines) else ""
            html += f"<li><strong>{item.get(key_name, '')}</strong>: {item.get(key_desc, '')}{lines}</li>"
        html += "</ul>"
        return html

    def _render_section(self, title, entries):
        if not entries:
            return ""
        html = f'<div class="section-title">{title}:</div><ul>'
        for e in entries:
            affected = ", ".join(e.get("affected_components", []))
            html += f"<li>{e.get('description', '')}<br><em>Затронутые компоненты:</em> {affected}</li>"
        html += "</ul>"
        return html

    def _generate_html(self):
        mr_blocks = ""
        for mr in self.report["results"]:
            problems_html = ""
            for level in ["critical", "regular", "minor"]:
                problems_html += self._render_items(
                    f"Проблемы ({level})",
                    mr.get("problems", {}).get(level, []),
                    "type", "description", "lines"
                )

            antipatterns_html = self._render_items("Антипаттерны", mr.get("antipatterns", []), "name", "description", "lines")
            positives_html = self._render_items("Положительные аспекты", mr.get("positives", []), "aspect", "lines", "lines")
            impacts_html = self._render_section("Влияние изменений", mr.get("impacts", []))

            mr_html = self.mr_template.format(
                mr_number=mr.get("mr_number", "N/A"),
                url=mr.get("url", "#"),
                complexity=mr.get("complexity", "не указано"),
                score=mr.get("score", "N/A"),
                problems_section=problems_html,
                antipatterns_section=antipatterns_html,
                positives_section=positives_html,
                impacts_section=impacts_html,
            )
            mr_blocks += mr_html

        metadata = self.report.get("metadata", {})
        return self.html_template.format(
            repo=metadata.get("repo", "N/A"),
            user=metadata.get("user", "N/A"),
            mean_score=metadata.get("mean_score", "N/A"),
            start=metadata.get("period", {}).get("start", "N/A"),
            end=metadata.get("period", {}).get("end", "N/A"),
            total=metadata.get("total", 0),
            mr_blocks=mr_blocks
        )

    def save_html(self, output_path="mr_report.html"):
        html_output = self._generate_html()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_output)
        print(f"Отчёт сохранён как {output_path}")

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
        <p><strong>Средний score:</strong> {mean_score}</p>
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


# Пример использования
if __name__ == "__main__":
    renderer = MRReportRenderer("mr_report.json")
    renderer.save_html("mr_report.html")
