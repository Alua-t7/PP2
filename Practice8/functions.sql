-- Search by pattern
CREATE OR REPLACE FUNCTION search_phone_book(p_pattern TEXT)
RETURNS TABLE(name TEXT, surname TEXT, phone TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT phone_book.name, phone_book.surname, phone_book.phone
    FROM phonebook
    WHERE phone_book.name ILIKE '%' || p_pattern || '%'
       OR phone_book.surname ILIKE '%' || p_pattern || '%'
       OR phone_book.phone LIKE '%' || p_pattern || '%';
END;
$$ LANGUAGE plpgsql;

--Pagination query
CREATE OR REPLACE FUNCTION get_users_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(name TEXT, surname TEXT, phone TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT phone_book.name, phone_book.surname, phone_book.phone
    FROM phone_book
    ORDER BY name
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;
