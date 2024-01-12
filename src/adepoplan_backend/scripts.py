def main():
    import adepoplan_backend.report
    txt = adepoplan_backend.report.load_report_template()
    with open('report.html', 'w', encoding='utf-8') as fp:
        fp.write(txt)
