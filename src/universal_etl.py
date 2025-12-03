"""Universal ETL toolkit core (under 100 lines)."""

from typing import Callable, Iterable, Any, List, Dict

Extractor = Callable[[], Iterable[Dict[str, Any]]]
Transform = Callable[[Dict[str, Any]], Dict[str, Any]]
Loader = Callable[[Iterable[Dict[str, Any]]], None]


class ETLPipeline:
    """Tiny, composable ETL pipeline.

    Example:
        pipeline = ETLPipeline(extract=..., transforms=[...], load=...)
        pipeline.run()
    """

    def __init__(
        self,
        extract: Extractor,
        transforms: List[Transform] | None = None,
        load: Loader | None = None,
        name: str = "default",
    ) -> None:
        self.name = name
        self.extract = extract
        self.transforms = transforms or []
        if load is None:
            raise ValueError("Loader function is required")
        self.load = load

    def add_transform(self, fn: Transform) -> None:
        self.transforms.append(fn)

    def run(self) -> None:
        records = self.extract()
        for t in self.transforms:
            records = (t(r) for r in records)
        self.load(records)


def dict_filter(keys: List[str]) -> Transform:
    """Keep only a subset of keys on each record."""

    def _inner(row: Dict[str, Any]) -> Dict[str, Any]:
        return {k: row.get(k) for k in keys}

    return _inner


def dict_rename(mapping: Dict[str, str]) -> Transform:
    """Rename keys on each record via a mapping dict."""

    def _inner(row: Dict[str, Any]) -> Dict[str, Any]:
        return {mapping.get(k, k): v for k, v in row.items()}

    return _inner
