with events_days_complete as (
    select *
    from "kr22_web_event_table"
    where date_day >= '2022-02-17'
        and date(date_day) < current_date
),
session_start_events as (
    select *,
        date_diff(
            'minute',
            from_iso8601_timestamp(
                lag(request_time) over (
                    partition by fingerprint,
                    date(from_iso8601_timestamp(request_time))
                    order by request_time asc
                )
            ),
            from_iso8601_timestamp(request_time)
        ) as inactivity_time
    from events_days_complete
),
session_starts as (
    select event_id,
        fingerprint,
        request_time as session_start_at,
        fingerprint || '-' || cast(
            date(from_iso8601_timestamp(request_time)) as varchar
        ) || '-' || cast(
            row_number() over (
                partition by fingerprint,
                date(from_iso8601_timestamp(request_time))
                order by request_time asc
            ) as varchar
        ) as session_id,
        coalesce(
            lead(request_time) over (
                partition by fingerprint
                order by request_time asc
            ),
            cast(
                date_add(
                    'day',
                    1,
                    date(from_iso8601_timestamp(request_time))
                ) as varchar
            )
        ) as next_session_start_at
    from session_start_events
    where inactivity_time is null
        or inactivity_time > 30
),
sessions as (
    select s.session_id,
        s.fingerprint,
        s.session_start_at,
        max(e.request_time) as session_end_at
    from session_starts as s
        join events_days_complete as e on s.fingerprint = e.fingerprint
        and e.request_time >= s.session_start_at
        and e.request_time < next_session_start_at
    group by 1,
        2,
        3
),
events_final as (
    select e.event_id,
        e.fingerprint,
        e.request_time,
        e.event_type,
        e.from_url,
        s.session_id,
        row_number() over (
            partition by session_id
            order by request_time asc
        ) as event_number,
        e.details,
        json_extract_scalar(e.user_data, '$.browser') as browser,
        json_extract_scalar(e.user_data, '$.device_type') as device_type,
        json_extract_scalar(e.user_data, '$.operating_system') as operating_system,
        json_extract_scalar(e.geoip, '$.city') as city,
        json_extract_scalar(json_extract(e.geoip, '$.country'), '$.name') as country,
        date_diff(
            'second',
            from_iso8601_timestamp(request_time),
            from_iso8601_timestamp(
                lead(e.request_time) over (partition by s.session_id order by request_time asc)
            )
        ) as seconds_to_next_event_in_session,
        extract(week from date(e.date_day)) as week,
        e.date_day
    from events_days_complete as e
        join sessions as s on e.fingerprint = s.fingerprint
        and e.request_time >= s.session_start_at
        and e.request_time <= s.session_end_at
)
select *
from events_final