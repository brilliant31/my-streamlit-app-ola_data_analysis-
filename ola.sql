CREATE DATABASE OLA;
USE ola;
CREATE TABLE rides (
    booking_id VARCHAR(20) PRIMARY KEY,                       -- unique ID for each booking
    booking_status VARCHAR(50),                               -- e.g., Success, Canceled By Driver
    customer_id VARCHAR(20),
    vehicle_type VARCHAR(50),
    pickup_location VARCHAR(100),
    drop_location VARCHAR(100),
    v_tat DECIMAL(8,2),                                      -- vehicle turnaround time
    c_tat DECIMAL(8,2),                                      -- customer turnaround time
    canceled_rides_by_customer VARCHAR(255),                 -- e.g., No, Driver is not moving towards pickup location
    canceled_rides_by_driver VARCHAR(255),                   -- e.g., No, Personal & Car related issue
    incomplete_rides VARCHAR(50),                             -- e.g., No
    incomplete_rides_reason VARCHAR(255),                    -- e.g., Not Applicable
    booking_value DECIMAL(10,2),
    payment_method VARCHAR(50),
    ride_distance DECIMAL(8,2),
    driver_ratings DECIMAL(3,2),
    customer_rating DECIMAL(3,2),
    vehicle_images VARCHAR(255),                              -- path or URL of images
    ride_datetime DATETIME,
    ride_hour INT,                                           -- derived from ride_datetime
    ride_day VARCHAR(20),                                    -- e.g., Monday
    ride_month INT,                                          -- 7 (from your CSV)
    tat_efficiency DECIMAL(5,2),
    ride_distance_bucket VARCHAR(50)                         -- e.g., Short, Medium, Long, Not Applicable
);

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/ola_clean.csv'
INTO TABLE rides
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(booking_id, booking_status, customer_id, vehicle_type, pickup_location, drop_location,
v_tat, c_tat, canceled_rides_by_customer, canceled_rides_by_driver, incomplete_rides, 
incomplete_rides_reason, booking_value, payment_method, ride_distance, driver_ratings, 
customer_rating, vehicle_images, ride_datetime, ride_hour, ride_day, ride_month, tat_efficiency, ride_distance_bucket);

SELECT * FROM rides;
SELECT COUNT(*) AS total_rows FROM rides;

#1. Retrieve all successful bookings:
CREATE OR REPLACE VIEW vw_successful_bookings AS
SELECT *
FROM rides
WHERE booking_status = 'Success';

SELECT * FROM vw_successful_bookings;

#2. Find the average ride distance for each vehicle type:
CREATE OR REPLACE VIEW vw_avg_distance_by_vehicle AS
SELECT 
    vehicle_type,
    ROUND(AVG(ride_distance), 2) AS avg_ride_distance
FROM rides
WHERE booking_status = 'Success'
GROUP BY vehicle_type;

SELECT * FROM vw_avg_distance_by_vehicle;

#3. Get the total number of cancelled rides by customers:
CREATE OR REPLACE VIEW vw_cancelled_by_customer AS
SELECT 
    COUNT(*) AS total_cancelled_by_customer
FROM rides
WHERE booking_status = 'Canceled By Customer';

SELECT * FROM vw_cancelled_by_customer;

 #4. List the top 5 customers who booked the highest number of rides:
 CREATE OR REPLACE VIEW vw_top_5_customers AS
SELECT 
    customer_id,
    COUNT(*) AS total_rides
FROM rides
GROUP BY customer_id
ORDER BY total_rides DESC
LIMIT 5;

SELECT * FROM vw_top_5_customers;

#5. Get the number of rides cancelled by drivers due to personal and car-related issues:
CREATE OR REPLACE VIEW vw_driver_cancel_personal_car AS
SELECT 
    COUNT(*) AS total_driver_cancelled
FROM rides
WHERE booking_status = 'Canceled By Driver'
  AND canceled_rides_by_driver = 'Personal & Car related issue';

SELECT * FROM vw_driver_cancel_personal_car;

#6. Find the maximum and minimum driver ratings for Prime Sedan bookings:
CREATE OR REPLACE VIEW vw_prime_sedan_drivers_ratings AS
SELECT
    MAX(driver_ratings) AS max_driver_rating,
    MIN(driver_ratings) AS min_driver_rating
FROM rides
WHERE vehicle_type='Prime Sedan'
AND booking_status='Success';

SELECT * FROM vw_prime_sedan_drivers_ratings;

#7. Retrieve all rides where payment was made using UPI:
CREATE OR REPLACE VIEW vw_upi_payments AS
SELECT * 
FROM rides
WHERE payment_method='UPI';

SELECT * FROM vw_upi_payments

#  8. Find the average customer rating per vehicle type:
CREATE OR REPLACE VIEW vw_avg_customer_rating AS
SELECT vehicle_type,ROUND(AVG(customer_rating),2) AS avg_customer_rating
FROM rides
WHERE booking_status='Success'
GROUP BY vehicle_type;

SELECT * FROM vw_avg_customer_rating;

#9. Calculate the total booking value of rides completed successfully:
CREATE OR REPLACE VIEW vw_total_booking_value AS
SELECT 
    SUM(booking_value) AS total_booking_value
FROM rides
WHERE booking_status = 'Success';

SELECT * FROM vw_total_booking_value;

#10. List all incomplete rides along with the reason

CREATE OR REPLACE VIEW vw_incomplete_rides AS
SELECT 
    booking_id,
    booking_status,
    customer_id,
    vehicle_type,
    pickup_location,
    drop_location,
    incomplete_rides,
    incomplete_rides_reason,
    ride_datetime
FROM rides
WHERE booking_status = 'Driver Not Found'
   OR incomplete_rides <> 'No';


 SELECT * FROM vw_incomplete_rides;