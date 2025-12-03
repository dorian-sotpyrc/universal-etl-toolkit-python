from universal_etl import ETLPipeline, dict_filter, dict_rename


def test_basic_pipeline():
    def extract():
        return [{"a": 1, "b": 2}]

    captured = {}

    def load(rows):
        items = list(rows)
        assert items == [{"x": 1}]
        captured["rows"] = items

    pipeline = ETLPipeline(
        extract=extract,
        transforms=[
            dict_filter(["a"]),
            dict_rename({"a": "x"}),
        ],
        load=load,
        name="test_pipeline",
    )

    pipeline.run()
    assert "rows" in captured
