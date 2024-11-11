--{'model_code': 'chinook customers', 'db_conf': 'Chinook', 'name': 'Partners',
--'where': ["name like 'B%'", "name not like 'B%'"]}
SELECT LastName AS name, LastName AS id, State AS state
, PostalCode AS zip, email AS email, Address AS street
, City AS city, Phone AS phone, Country AS country
-- , Company, Fax, SupportRepId
FROM customers
order by LastName
