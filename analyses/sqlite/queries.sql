-- Return a list of the most popular item catagories, skipping
-- "Tools" and "Hand Tools"
--
-- Handy primer on the json_each syntax: https://sqlite.org/json1.html#examples_using_json_each_and_json_tree_
select
  json_each.value as item_type,
  json_group_array(distinct i."Item Type") item_types,
  count(1) as loans,
from
  loans l inner join items i on l."Item ID" = i."Item ID"
  inner join item_types it on i."Item Type" = it."Type", json_each(it."Full Hierarchy")
where json_each.value not in ('Tools', 'Hand Tools')
and l."Renewal" = ""
group by 1
order by 3 desc
limit 10;
-- Measuring & Layout Tools - Levels, Studfinders
-- Wrenches - Socket Sets
-- Cordless Power Tools - Cordless Drills 
-- Power Saws - all of them
-- Hammers & Mallets - eponymous ("Hammers & Mallets")
-- Sanders - all of them
-- Drills - corded drills

-- Return more details on a particular category of tools
select
  i."Item Type",
  count(distinct l."Username") as distinct_users
from
  loans l inner join items i on l."Item ID" = i."Item ID"
  inner join item_types it on i."Item Type" = it."Type", json_each(it."Full Hierarchy")
where json_each.value = 'Measuring & Layout Tools'
and l."Renewal" = ""
group by 1
order by 2 desc
limit 10;

-- Try level 3 hierarchies only - these usually correspond to "Tools > Hand Tools > Something"
select
  json_each.value as item_type,
  json_group_array(distinct i."Item Type") item_types,
  count(distinct l."Username") as distinct_users
from
  loans l inner join items i on l."Item ID" = i."Item ID"
  inner join item_types it on i."Item Type" = it."Type", json_each(it."Full Hierarchy")
where json_each.value not in ('Tools', 'Hand Tools')
and json_array_length(it."Full Hierarchy") = 3
group by 1
order by 3 desc
limit 10;

-- Create it in a format suitable for a d3.js nested treemap
--
-- Each element should be a tuple of name, children and value.  Only leaf
-- nodes (elements without children) should have a value. Example:
--
-- { name: "root", children: [ { name: "Tools", children: [ { name: "Hand Tools", value: "10" } ] } ] }
--
-- TODO: THIS DOESN'T DO ANYTHING USEFUL YET
with recursive
  example(parent_type, item_type, nesting_level) as (
    values(null, "root", 0)
    union all
    select
      e.item_type as parent_type, it.Type, e.nesting_level + 1
    from item_types it, example e
    where it."Parent Type" = e.item_type
  )
select * from example order by nesting_level asc, parent_type limit 10;

-- Try selecting for each item type, and including information on it's hierarchy
with lt(username, item_type) as (
  select
    l."Username",
    i."Item Type"
  from loans l inner join items i on l."Item ID" = i."Item ID"
)
select
  i."Item Type" as item_type,
  count(distinct lt.username) as distinct_users
from items i left join lt on i."Item Type" = lt.item_type
group by 1
order by 2 asc;

-- Unused items!
with lt(username, item_type) as (
  select
    l."Username",
    i."Item Type"
  from loans l inner join items i on l."Item ID" = i."Item ID"
)
select
  i."Item Type" as item_type,
  json_group_array(i."Name") as unloved_items,
  count(distinct lt.username) as distinct_users
from items i left join lt on i."Item Type" = lt.item_type
group by 1
having count(distinct lt.username) = 0;

-- More ideas for interesting reports
--
-- * Graph Item Type by variance to visually detect seasonality
-- * Treemap of most under-utilized categories (number of items in category with 0 loans)

-- Most checked out shelves. Location Codes were manually normalize in Nov 2021, so not much extra
-- processing should be required.
select
  i."Location Code" as location_code,
  count(distinct l."Username") as count
from items i inner join loans l on i."Item ID" = l."Item ID"
group by 1
order by 2 desc;

-- Zoom in on itmes in a particular group in case we want to change the Location Codes
select i."Item ID", i."Name", i."Location Code" from items i where replace(lower(i."Location Code"), " ", "") in ("backwall", "wayback");

-- See counts by month for a particular location code
select
  -- Dates are formatted "10/13/2021 8:25 PM".  This is incompatible with
  -- the built-in sqlite3 date and time functions, which expect YYYY-MM-DD HH:MM:SS.SSS.
  -- As a hack, extract the first two chars as the month, and remove the "/" to handle
  -- single digit months like "4/".
  --
  -- TODO: Proper dates
  cast(replace(substr("Checked Out", 1, 2), "/", "") as INTEGER) as month,
  i."Location Code" as location_code,
  count(1) as loan_count
from items i inner join loans l on i."Item ID" = l."Item ID"
where i."Location Code" in ("Far Back")
and l."Renewal" = ""
group by 1, 2
order by 1 asc;

-- Similar, but try to get the highest counts for a particular month.
--
-- For more info on date extraction see previous query.
select
  i."Location Code" as location_code,
  count(1) as loan_count
from items i inner join loans l on i."Item ID" = l."Item ID"
where cast(replace(substr("Checked Out", 1, 2), "/", "") as INTEGER) in (11, 12)
and l."Renewal" = ""
group by 1
order by 2 desc;


-- Similar, but try to get the larges concurrent checkouts for a given type.
--
-- See previous query for date logic.  This should give a sense of items that we way overuse.
-- TODO: Figure out how to pull a row for items with 0 loans.
with item_type_counts as (
  select
    i."Item Type" as item_type,
    count(1) as count
  from items i 
  where i."Status(es)" = ""
  and not exists (
    select 1 from loans l where l."Item Id" = i."Item Id" and
    -- Use late fees as a very hacky way to detect WAYYY overdue items until we have real dates.
    l."Checked In" = "" and cast(replace(l."Late Fees To Date", "$", "") as real) > 20
  )
  group by 1
),
loan_counts as (
  select
    cast(replace(substr(l."Checked Out", 1, 2), "/", "") as INTEGER) as month,
    i."Item Type" as item_type,
    count(1) as count 
  from items i inner join loans l on i."Item ID" = l."Item ID"
  where l."Renewal" = ""
  group by 1, 2
)
select
  i.item_type,
  -- This is the ratio between the max loans and the number of available items. 2x is a good ratio, gives
  -- us some room to grow.
  --
  -- Items with an excessive ratio (>2) that take up a lot of space are ripe for sale. Low ratio
  -- items might be things we ask for/focus on.
  i.count / max(l.count) as ratio,
  max(l.count) as most_out_at_a_time
from item_type_counts i left join loan_counts l on l.item_type = i.item_type
group by 1
order by 2 desc;
