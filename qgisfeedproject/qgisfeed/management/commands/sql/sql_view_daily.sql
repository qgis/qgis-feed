-- Taken from https://stackoverflow.com/posts/35179515/revisions
create or replace function create_jsonb_flat_view
    (table_name text, view_name text, regular_columns text, json_column text)
    returns text language plpgsql as $$
declare
    cols text;
begin
    execute format ($ex$
        select string_agg(format('%2$s->>%%1$L "%%1$s"', key), ', ')
        from (
            select distinct key
            from %1$s, jsonb_each(%2$s)
            order by 1
            ) s;
        $ex$, table_name, json_column)
    into cols;
    execute format($ex$
        drop view if exists %4$s;
        create view %4$s as
        select %2$s, %3$s from %1$s
        $ex$, table_name, regular_columns, cols, view_name);
    return cols;
end $$;

select create_jsonb_flat_view('qgisfeed_dailyqgisuservisit', 'daily_platform', 'id, date', 'platform');
select create_jsonb_flat_view('qgisfeed_dailyqgisuservisit', 'daily_country', 'id, date', 'country');
select create_jsonb_flat_view('qgisfeed_dailyqgisuservisit', 'daily_qgis_version', 'id, date', 'qgis_version');
