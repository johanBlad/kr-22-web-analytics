from datetime import datetime
import pandas as pd


def aggregate_web_traffic_daily(df_all):
    # CALC: Sidvisningar, Sessioner, Unika Besökare över Datum
    df_total_events_per_day = df_all.groupby(by=["date_day"], as_index=True).count()[
        "event_id"
    ]
    df_sessions_per_day = (
        df_all.where((df_all["event_number"] == 1))
        .groupby(by=["date_day"], as_index=True)
        .count()["session_id"]
    )
    df_unique_users_per_day = df_all.groupby(
        by=["date_day"], as_index=True
    ).fingerprint.nunique()
    date_days = sorted(df_all["date_day"].unique())
    weekdays = [datetime.strptime(e, "%Y-%m-%d").date().weekday() for e in date_days]

    return pd.DataFrame(
        {
            "Datum": date_days,
            "Veckodag": weekdays,
            "Sidvisningar": df_total_events_per_day,
            "Sessioner": df_sessions_per_day,
            "Unika Besökare": df_unique_users_per_day,
        }
    )


def aggregate_web_traffic_hourly(df_all):
    df_mean_events_per_hour = (
        df_all.groupby(by=["date_day", "hour"], as_index=True)
        .count()
        .groupby(by=["hour"], as_index=True)
        .mean()["event_id"]
    )
    df_mean_sessions_per_hour = (
        df_all.where((df_all["event_number"] == 1))
        .groupby(by=["date_day", "hour"], as_index=True)
        .count()
        .groupby(by=["hour"], as_index=True)
        .mean()["session_id"]
    )

    return pd.DataFrame(
        {
            "Timme": range(24),
            "Sidvisningar": df_mean_events_per_hour,
            "Sessioner": df_mean_sessions_per_hour,
        }
    )


def aggregate_web_traffic_weekday(date_preproc):
    weekdays_map = {
        0: "Måndag",
        1: "Tisdag",
        2: "Onsdag",
        3: "Torsdag",
        4: "Fredag",
        5: "Lördag",
        6: "Söndag",
    }

    weekday_agg = date_preproc.groupby(by=["Veckodag"], as_index=True).agg(
        {
            "Sidvisningar": ["median", "mean"],
            "Sessioner": ["median", "mean"],
            "Unika Besökare": ["median", "mean"],
        }
    )

    return pd.DataFrame(
        {
            "Veckodag": [e for e in weekdays_map.values()],
            "Sidvisningar": weekday_agg["Sidvisningar"]["median"],
            "Sessioner": weekday_agg["Sessioner"]["median"],
        }
    )


def calculate_social_media_correlation(
    df_sessions_per_day,
    df_facebook_reach,
    df_facebook_pageviews,
    df_instagram_reach,
    df_instagram_pageviews,
    date_days,
):
    # CALC: Sessioner Hemsida korrelation Facebook, Instagram Räckvidd

    social_media_preproc = pd.DataFrame(
        {
            "Hemsida Sessioner": list(df_sessions_per_day),
            "Facebook Räckvidd": df_facebook_reach["reach"],
            "Instagram Räckvidd": df_instagram_reach["reach"],
            "Facebook Sidvisningar": df_facebook_pageviews["pageviews"],
            "Instagram Sidvisningar": df_instagram_pageviews["pageviews"],
        }
    )
    social_media_norm = (
        social_media_preproc - social_media_preproc.mean()
    ) / social_media_preproc.std()
    social_media_norm["Datum"] = date_days

    facebook_correlation = social_media_norm.drop(
        columns=["Instagram Räckvidd", "Instagram Sidvisningar"]
    )
    instagram_correlation = social_media_norm.drop(
        columns=["Facebook Räckvidd", "Facebook Sidvisningar"]
    )

    return {"facebook": facebook_correlation, "instagram": instagram_correlation}
