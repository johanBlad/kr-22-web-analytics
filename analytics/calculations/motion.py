from typing import Dict
import pandas as pd

def filter_motion_events(df_all):
    motions = df_all[df_all['from_url'].str.contains('visa-motion/')].copy()
    motions['motion'] = motions['from_url'].map(lambda x: x.split('&')[0].split('?motion=')[-1])
    return motions[pd.to_numeric(motions['motion'], errors='coerce').notnull()]


def calculate_motion_stats(df) -> Dict[str, int]:

    motion_statistics = df.groupby(by=['motion'], as_index=True) \
        .agg({
            'seconds_to_next_event_in_session': 'median',
            'event_id': 'count',
            'session_id': 'nunique',
            'fingerprint': 'nunique',
        }).sort_values(by='session_id', ascending=False)

    motion_statistics = motion_statistics.rename(columns={
        'seconds_to_next_event_in_session': 'Sidtid (median sekunder)',
        'event_id': 'Sid-visningar (#)',
        'session_id': 'Sessioner (#)',
        'fingerprint': 'Unika Besökare (#)',
    })
    
    return motion_statistics