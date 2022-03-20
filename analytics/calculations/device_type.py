from calculations.common import calculate_session_stats


def calculate_desktop_mobile_stats(all_events):
    desktop_events = all_events[
        all_events.where((all_events["device_type"] == "desktop")).device_type.notna()
    ]
    mobile_events = all_events[
        all_events.where((all_events["device_type"] == "mobile")).device_type.notna()
    ]
    desktop_session_stats = calculate_session_stats(desktop_events)
    mobile_session_stats = calculate_session_stats(mobile_events)

    desktop_mobile_stats = all_events.groupby(by="device_type").agg(
        {
            "event_id": "count",
            "session_id": "nunique",
            "fingerprint": "nunique",
            "from_fb": sum,
        }
    )

    desktop_mobile_stats.insert(
        len(desktop_mobile_stats.columns),
        "Andel Sessioner med endast ett sidbesök",
        [
            desktop_session_stats["one_event_session_ratio"],
            mobile_session_stats["one_event_session_ratio"],
        ],
    )
    desktop_mobile_stats.insert(
        len(desktop_mobile_stats.columns),
        "Snitt sidvisningar per session",
        [
            desktop_session_stats["avg_events_per_session"],
            mobile_session_stats["avg_events_per_session"],
        ],
    )
    desktop_mobile_stats.insert(
        len(desktop_mobile_stats.columns),
        "Median Sid-tid",
        [
            desktop_session_stats["median_time_per_page"],
            mobile_session_stats["median_time_per_page"],
        ],
    )
    desktop_mobile_stats.insert(
        len(desktop_mobile_stats.columns),
        "Median Sessions-tid",
        [
            desktop_session_stats["median_session_time"],
            mobile_session_stats["median_session_time"],
        ],
    )

    return desktop_mobile_stats
