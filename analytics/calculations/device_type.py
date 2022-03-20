from calculations.common import calculate_session_stats
import matplotlib.pyplot as plt
import seaborn as sns

def plot_device_pie_chart(desktop_mobile_stats):
    fig, ax = plt.subplots(1, 2, figsize=(15, 10))
    colors = sns.color_palette('pastel')
    ax[0].pie(
        desktop_mobile_stats["Sidvisningar"],
        labels=desktop_mobile_stats.index,
        colors=colors[0 : len(desktop_mobile_stats)],
        autopct="%.0f%%",
    )
    ax[0].set_title("All trafik över mobil och dator")
    ax[1].pie(
        desktop_mobile_stats["Sessioner"],
        labels=desktop_mobile_stats.index,
        colors=colors[2 : len(desktop_mobile_stats) + 2],
        autopct="%.0f%%",
    )
    ax[1].set_title("Sessioner över mobil och dator")


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
    desktop_mobile_stats = desktop_mobile_stats.rename(
        columns={
            "event_id": "Sidvisningar",
            "session_id": "Sessioner",
            "fingerprint": "Unika Besökare",
            "from_fb": "Från Facebook",
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
