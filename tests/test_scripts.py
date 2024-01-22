from adepoplan_backend import scripts


class Test_merge_dict:
    def test_copies_values_when_flat_dict(self):
        conf = dict(A=1, B=2)
        default = dict(A=3, C=4)
        result = scripts.merge_dict(default, conf)
        assert result == dict(A=1, B=2, C=4)

    def test_copies_values_when_nested_dict(self):
        conf = dict(A=dict(a=1, b=2, d=dict(e=5)), B=24)
        default = dict(A=dict(a=3, c=4, d=6), C=44)
        result = scripts.merge_dict(default, conf)
        assert result == dict(
            A=dict(a=1, b=2, c=4, d=dict(e=5)),
            B=24,
            C=44,
        )
