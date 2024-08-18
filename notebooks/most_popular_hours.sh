#! /bin/sh

csvsql \
    --no-inference \
    --query most_popular_hours.sql \
    ../output/checkouts.csv
