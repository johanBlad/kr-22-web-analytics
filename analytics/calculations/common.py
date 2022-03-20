from typing import Dict, Iterable, List
import pandas as pd


def clean_url(url: str) -> str:
    return url.split("?")[0].split("#")[0]


def clean_urls(from_urls: Iterable[str]) -> List[str]:
    return [clean_url(e) for e in from_urls]


def prepare_data(df_raw):
    df_raw["hour"] = pd.to_datetime(df_raw["request_time"]).dt.hour

    df_raw["from_fb"] = df_raw["from_url"].map(lambda x: 1 if "fbclid=" in x else 0)
    df_raw["clean_url"] = df_raw["from_url"].map(clean_url)

    df_raw["event_number_reverse"] = (
        df_raw.sort_values(["request_time"], ascending=[False])
        .groupby(["session_id"])
        .cumcount()
        + 1
    )

    df_raw["first_session_event"] = df_raw["event_number"].map(
        lambda x: 1 if x == 1 else 0
    )
    df_raw["last_session_event"] = df_raw["event_number_reverse"].map(
        lambda x: 1 if x == 1 else 0
    )
    return df_raw


def calculate_page_stats(df, lim=10) -> Dict[str, int]:

    page_filter = ["about:srcdoc"]

    df_agg = df.rename(columns={"clean_url": "Sida"})
    page_statistics = (
        df_agg.query("Sida not in @page_filter")
        .groupby(by=["Sida"], as_index=True)
        .filter(lambda x: x.session_id.nunique() >= lim)
        .groupby(by=["Sida"], as_index=True)
        .agg(
            {
                "seconds_to_next_event_in_session": "median",
                "event_id": "count",
                "session_id": "nunique",
                "fingerprint": "nunique",
                "from_fb": sum,
                "first_session_event": sum,
                "last_session_event": sum,
            }
        )
        .sort_values(by="session_id", ascending=False)
    )

    page_statistics["score"] = round(
        100 * (page_statistics["last_session_event"] / page_statistics["event_id"]), 2
    )

    page_statistics["from_fb"] = page_statistics.from_fb.astype(int)
    page_statistics["first_session_event"] = page_statistics.first_session_event.astype(
        int
    )
    page_statistics["last_session_event"] = page_statistics.last_session_event.astype(
        int
    )

    page_statistics = page_statistics.rename(
        columns={
            "seconds_to_next_event_in_session": "Sidtid (median sekunder)",
            "event_id": "Sid-visningar (#)",
            "session_id": "Sessioner (#)",
            "fingerprint": "Unika Besökare (#)",
            "from_fb": "Från Facebook (#)",
            "first_session_event": "Första Sidan på Sessionen (#)",
            "last_session_event": "Sista Sidan på Sessionen (#)",
            "score": "Sannolikhet att Lämna Hemsidan (%)",
        }
    )

    return page_statistics


def calculate_session_stats(df) -> Dict[str, float]:
    session_event_count = (
        df.groupby(by=["session_id"], as_index=True)
        .count()["event_id"]
        .reset_index(name="event_count")
    )
    multiple_event_sessions = session_event_count.where(
        (session_event_count["event_count"] > 1)
    ).dropna()
    one_event_sessions = session_event_count.where(
        (session_event_count["event_count"] == 1)
    ).dropna()

    total_session_count = session_event_count["session_id"].count()
    one_event_sessions_count = one_event_sessions["session_id"].count()

    multiple_event_sessions_events = multiple_event_sessions.set_index(
        "session_id"
    ).join(df.set_index("session_id"), how="inner")
    session_max_min_time = multiple_event_sessions_events.groupby(
        by=["session_id"], as_index=True
    ).agg({"request_time": ["min", "max"], "event_count": ["mean"]})
    session_max_min_time["session_time"] = pd.to_datetime(
        session_max_min_time["request_time"]["max"]
    ) - pd.to_datetime(session_max_min_time["request_time"]["min"])

    session_stats = session_max_min_time[["session_time", "event_count"]].median()
    median_time_per_page = round(
        float(df["seconds_to_next_event_in_session"].dropna().median()), 2
    )

    return {
        "one_event_session_ratio": round(
            100 * (one_event_sessions_count / total_session_count), 2
        ),
        "avg_events_per_session": round(session_event_count["event_count"].mean(), 2),
        "avg_events_per_multievent_sessions": round(
            multiple_event_sessions["event_count"].mean(), 2
        ),
        "median_time_per_page": median_time_per_page,
        "median_session_time": round(
            float(
                (
                    session_stats["session_time"].dt.total_seconds()
                    + median_time_per_page
                )
            ),
            2,
        ),
    }
