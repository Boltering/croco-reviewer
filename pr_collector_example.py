from pr_collector import GitHubPRDiffCollector

collector = GitHubPRDiffCollector()

"""
diffs - это список всех коммитов, чтобы взять только дивы нужно от элемента списка взять diff['patch'],
ну или [diff['patch'] for diff in diffs]
"""
diffs = collector.collect_pr_diffs(
    repo="subsurface/libdc",
    username="torvalds",
    start_date="2023-01-01",
    end_date="2023-12-31"
)


# Из файла может быть более читабельный вид
if diffs:
    collector.save_diffs_to_file(diffs, "linux_pr_diffs.txt")
