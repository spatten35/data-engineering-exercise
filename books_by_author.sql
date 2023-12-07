-- Write a SQL query (or Python equivalent) to aggregate:
-- - The number of books written each year by an author.
-- - The average number of books written by an author per year.
with books_by_yr as (
    SELECT
        a.authorskey as author_key
        b.publish_date.year as year_written,
        count(distinct bookskey) over(partition by a.authorskey, publish_date.year) as num_books_by_year
    FROM authors a
        join bridge br
            on a.authorskey = br.authorskey
        join books b
            on br.bookskey = b.bookskey
)
select
    author_key,
    year_written,
    num_books_by_year,
    average(num_books_by_year) over(partition by author_key)
from books_by_yr