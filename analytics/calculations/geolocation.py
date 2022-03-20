import pandas as pd
from typing import List

def aggregate_location(df_unique_users, aggregate_column: str, cut_off: int = 10):
    df_agg_count = (
        df_unique_users.groupby([aggregate_column], as_index=True)
        .count()[["fingerprint"]]
        .sort_values(["fingerprint"], ascending=False)
    )

    df_excluded_count = df_agg_count[cut_off:]["fingerprint"].sum()
    df_included = df_agg_count[:cut_off]

    df_with_others = pd.concat(
        [
            df_included,
            pd.DataFrame(df_excluded_count, columns=["fingerprint"], index=["Andra"]),
        ]
    )

    return df_with_others


def aggregate_location_per_day(df_unique_users, aggregate_column: str, df_index: List[str]):

    df_other = df_unique_users.copy()
    df_other[aggregate_column] = df_other[aggregate_column].map(
        lambda x: "Andra" if x not in df_index else x
    )

    df_agg_per_day = (
        df_other.groupby([aggregate_column, "date_day"], as_index=True)
        .count()[["fingerprint"]]
        .sort_values(["date_day", "fingerprint"], ascending=[True, False])
        .reset_index()
    )
    return df_agg_per_day
