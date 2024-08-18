WITH times_decomposed AS (
    SELECT
        STRFTIME('%Y', "Checked Out") AS year,
        CASE
            -- Note that different implementations of SQL have different
            -- day-of-week text values. Watch out!
            WHEN STRFTIME('%w', "Checked Out") = '0' THEN 'Sunday'
            WHEN STRFTIME('%w', "Checked Out") = '2' THEN 'Tuesday'
            WHEN STRFTIME('%w', "Checked Out") = '3' THEN 'Wednesday'
            WHEN STRFTIME('%w', "Checked Out") = '6' THEN 'Saturday'
        END AS dow,
        STRFTIME('%H', "Checked Out") AS hour,
        STRFTIME('%M', "Checked Out") AS minute
    -- This dataset already excludes renewals!
    FROM checkouts
),
dow_and_minutes AS (
    SELECT
        dow,
        -- Cannot do this math in the same `SELECT` as `dow`, `hour`,
        -- and `minute` are created, which is why this is in a second,
        -- separate common table expression
        CASE
            WHEN dow = 'Sunday' THEN (hour - 16) * 60 + minute
            WHEN dow = 'Tuesday' THEN (hour - 18) * 60 + minute
            WHEN dow = 'Wednesday' THEN (hour - 18) * 60 + minute
            WHEN dow = 'Saturday' THEN (hour - 9) * 60 + minute
        END AS minutes_after_opening
    FROM times_decomposed
    WHERE
        -- Analyze only post-pandemic hours, although could be even more
        -- precise by limiting to _just_ hours starting October 2021,
        -- when the most recent schedule change occurred. This'd only
        -- matter when comparing one day to another, though, not hours
        -- _within_ a day.
        CAST(year AS INTEGER) > 2020 AND
        (dow = 'Sunday' OR dow = 'Tuesday' OR dow = 'Wednesday' OR dow = 'Saturday') AND
        -- Ignore checkouts that happen outside of CHTL hours
        minutes_after_opening >= 0 AND
        minutes_after_opening <= 60 * 3 - 1
)
SELECT
    *,
    CAST(ROUND(minutes_after_opening / 30 + 0.5) AS INTEGER) AS half_hour
FROM dow_and_minutes
ORDER BY
    dow,
    minutes_after_opening
;
