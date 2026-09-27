CREATE DATABASE HOTEL_DB;

CREATE OR REPLACE FILE FORMAT FF_CSV
    TYPE = 'CSV'
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1
    NULL_IF = ('NULL', 'null', '');

--creating a stage (a place where temporary files are stored)
CREATE OR REPLACE STAGE STAGE_HOTEL_BOOKINGS
    FILE_FORMAT = FF_CSV;

CREATE TABLE BRONZE_HOTEL_BOOKING (
booking_id STRING,
hotel_id STRING,
hotel_city STRING,
customer_id STRING,
customer_name STRING,
customer_email STRING,
check_in_date STRING,
check_out_date STRING,
room_type STRING,
num_guests STRING,
total_amount STRING,
currency STRING,
booking_status STRING
);

COPY INTO BRONZE_HOTEL_BOOKING 
FROM @STAGE_HOTEL_BOOKINGS
FILE_FORMAT = (FORMAT_NAME = FF_CSV)
ON_ERROR = 'CONTINUE';

SELECT * FROM BRONZE_HOTEL_BOOKING
LIMIT 50;



