from adepoplan_backend import report


class Test_load_report_template:
    def test_starts_with_html_tag(self):
        result = report.load_report_template()
        assert result.startswith("<html>")
