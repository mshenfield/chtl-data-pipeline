WITH times_decomposed AS (
    SELECT
        STRFTIME('%Y', "Checked Out") AS year,
        STRFTIME('%m', "Checked Out") AS month,
        STRFTIME('%d', "Checked Out") AS day,
        CASE
            -- Note that different implementations of SQL have different
            -- day-of-week text values. Watch out!
            WHEN STRFTIME('%w', "Checked Out") = '0' THEN 'Sunday'
            WHEN STRFTIME('%w', "Checked Out") = '1' THEN 'Monday'
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
        (hour - 9) * 60 + minute AS minutes_after_opening
    FROM times_decomposed
    WHERE
        -- Analyze only the 1.5 months during which the Saturday
        -- afternoon shift was open
        CAST(year AS INTEGER) = 2020 AND
        (
            CAST(month AS INTEGER) = 2 OR
            (
                CAST(month AS INTEGER) = 3 AND
                CAST(day AS INTEGER) < 13
            )
        ) AND
        -- Only output Saturday data
        dow = 'Saturday' AND
        -- Ignore checkouts that happen outside of CHTL hours
        minutes_after_opening >= 0 AND
        minutes_after_opening <= 60 * 5 - 1
),
with_half_hour AS (
    SELECT
        *,
        CAST(ROUND(minutes_after_opening / 30 + 0.5) AS INTEGER) AS half_hour
    FROM dow_and_minutes
    ORDER BY half_hour
)
SELECT
    half_hour,
    COUNT(*)
FROM with_half_hour
GROUP BY half_hour;
