USE DATABASE HOTEL_DB;

CREATE TABLE SILVER_HOTEL_BOOKINGS (
booking_id VARCHAR,
hotel_id VARCHAR,
hotel_city VARCHAR,
customer_id VARCHAR,
customer_name VARCHAR,
customer_email VARCHAR,
check_in_date DATE,
check_out_date DATE,
room_type VARCHAR,
num_guests INTEGER,
total_amount FLOAT,
currency VARCHAR,
booking_status VARCHAR
);

-- finding missing or invalid emails records
SELECT customer_email 
FROM BRONZE_HOTEL_BOOKING
WHERE NOT (customer_email LIKE '%@%.%')
    OR customer_email IS NULL;

-- negative amounts are noted in data which is not possible.
SELECT total_amount
FROM BRONZE_HOTEL_BOOKING
WHERE TRY_TO_NUMBER(total_amount) < 0;

-- CHECK OUT DATE AND CHECK OUT DATE INCONSISTENCY
SELECT check_in_date, check_out_date
FROM BRONZE_HOTEL_BOOKING
WHERE TRY_TO_DATE(check_out_date) < TRY_TO_DATE(check_in_date);

-- type errors in booking status
SELECT DISTINCT booking_status
FROM BRONZE_HOTEL_BOOKING;

-- Inserting Cleaned data to Silver layer
INSERT INTO SILVER_HOTEL_BOOKINGS
SELECT
    booking_id,
    hotel_id,
    INITCAP(TRIM(hotel_city)) AS hotel_city,
    customer_id,
    INITCAP(TRIM(customer_name)) AS customer_name,
    CASE
        WHEN customer_email LIKE '%@%.%' THEN LOWER(TRIM(customer_email))
        ELSE NULL
    END AS customer_email,
    TRY_TO_DATE(NULLIF(check_in_date, '')) AS check_in_date,
    TRY_TO_DATE(NULLIF(check_out_date, '')) AS check_out_date,
    room_type,
    num_guests,
    ABS(TRY_TO_NUMBER(total_amount)) AS total_amount,
    currency,
    CASE
        WHEN LOWER(booking_status) in ('confirmeeed', 'confirmd') THEN 'Confirmed'
        ELSE booking_status
    END AS booking_status
    FROM BRONZE_HOTEL_BOOKING
    WHERE
        TRY_TO_DATE(check_in_date) IS NOT NULL
        AND TRY_TO_DATE(check_out_date) IS NOT NULL
        AND TRY_TO_DATE(check_out_date) >= TRY_TO_DATE(check_in_date);

-- viewing the silver layer
SELECT * FROM SILVER_HOTEL_BOOKINGS;

