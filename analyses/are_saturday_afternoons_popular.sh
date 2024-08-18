#! /bin/sh

csvsql \
    --no-inference \
    --query are_saturday_afternoons_popular.sql \
    ../data/output/checkouts.csv
