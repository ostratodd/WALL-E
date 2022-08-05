import pandas as pd
from genpipes import declare, compose
from collections.abc import Iterable

@declare.generator()
def data_to_be_processed(path:str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


@declare.processor(inputs=["col1"])
def filter_by(stream: Iterable[pd.DataFrame], col_to_filter:str, value:str):
    for df in stream:
        dff = df[df[col_to_filter] == value]
        yield dff

pipe = compose.Pipeline(steps=[
    ("fetching datasource from some csv file", data_to_be_processed, {}),
    ("performing some filtering based on col1", filter_by, {"value": "some_value"} )
])

output = pipe.run()
