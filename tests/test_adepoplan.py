from adepoplan_backend import scripts
import pytest
from pathlib import Path


@pytest.mark.end_to_end
def test_can_build_report():
    outfile = Path('report.html')
    outfile.unlink(missing_ok=True)

    scripts.main()
    assert Path(outfile).exists()
