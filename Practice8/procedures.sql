-- Insert or update single user
CREATE OR REPLACE PROCEDURE upsert_user(p_name TEXT, p_surname TEXT, p_phone TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phone_book WHERE name = p_name AND surname = p_surname) THEN
        UPDATE phone_book
        SET phone = p_phone
        WHERE name = p_name AND surname = p_surname;
    ELSE
        INSERT INTO phone_book(name, surname, phone)
        VALUES (p_name, p_surname, p_phone);
    END IF;
END;
$$;

--Insert many users with validation
CREATE OR REPLACE PROCEDURE upsert_many_users(users JSON)
LANGUAGE plpgsql AS $$
DECLARE
    u JSON;
    v_name TEXT;
    v_surname TEXT;
    v_phone TEXT;
BEGIN
    FOR u IN SELECT * FROM json_array_elements(users) LOOP
        v_name := u->>'name';
        v_surname := u->>'surname';
        v_phone := u->>'phone';
        -- проверка телефона (только цифры и +)
        IF v_phone ~ '^\+?\d+$' THEN
            CALL upsert_user(v_name, v_surname, v_phone);
        ELSE
            RAISE NOTICE 'Некорректный телефон: % % %', v_name, v_surname, v_phone;
        END IF;
    END LOOP;
END;
$$;

--Delete by name or phone
CREATE OR REPLACE PROCEDURE delete_user(p_name TEXT DEFAULT NULL, p_phone TEXT DEFAULT NULL)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM phone_book
    WHERE (p_name IS NOT NULL AND (name || ' ' || surname) = p_name)
       OR (p_phone IS NOT NULL AND phone = p_phone);
END;
$$;