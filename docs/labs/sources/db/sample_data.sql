-- Тестовые данные ИС кинотеатра
INSERT INTO main_ticketstatus (id, name) VALUES
 (gen_random_uuid(), 'Забронирован'), (gen_random_uuid(), 'Оплачен'), (gen_random_uuid(), 'Возвращён');
INSERT INTO main_genre (id, name) VALUES
 (gen_random_uuid(), 'Драма'), (gen_random_uuid(), 'Комедия'),
 (gen_random_uuid(), 'Фантастика'), (gen_random_uuid(), 'Мультфильм');
INSERT INTO main_hall (id, name, description) VALUES
 (gen_random_uuid(), 'Зал 1', 'Большой зал, Dolby Atmos'),
 (gen_random_uuid(), 'Зал 2', 'Малый зал');
INSERT INTO main_seat (id, hall_id, row_number, seat_number)
 SELECT gen_random_uuid(), h.id, r, s FROM main_hall h, generate_series(1,8) r, generate_series(1,12) s WHERE h.name='Зал 1';
INSERT INTO main_seat (id, hall_id, row_number, seat_number)
 SELECT gen_random_uuid(), h.id, r, s FROM main_hall h, generate_series(1,5) r, generate_series(1,8) s WHERE h.name='Зал 2';
INSERT INTO main_film (id, title, description, duration_minutes, age_rating, release_date, country, director) VALUES
 (gen_random_uuid(), 'Интерстеллар', 'Космическая драма', 169, 12, '2014-11-06', 'US', 'К. Нолан'),
 (gen_random_uuid(), 'Чебурашка', 'Семейная комедия', 113, 6, '2023-01-01', 'RU', 'Д. Дьяченко'),
 (gen_random_uuid(), 'Дюна: Часть вторая', 'Научная фантастика', 166, 12, '2024-02-29', 'US', 'Д. Вильнёв');
INSERT INTO main_film_genres (film_id, genre_id)
 SELECT f.id, g.id FROM main_film f, main_genre g
 WHERE (f.title='Интерстеллар' AND g.name IN ('Драма','Фантастика'))
    OR (f.title='Чебурашка' AND g.name='Комедия')
    OR (f.title='Дюна: Часть вторая' AND g.name='Фантастика');
INSERT INTO main_session (id, film_id, hall_id, start_time, price)
 SELECT gen_random_uuid(), f.id, h.id, t::timestamptz, p FROM (VALUES
  ('Интерстеллар','Зал 1','2026-10-15 18:00+03',450.00),
  ('Чебурашка','Зал 2','2026-10-15 12:00+03',300.00),
  ('Дюна: Часть вторая','Зал 1','2026-10-15 21:30+03',500.00)) v(ft,hn,t,p)
 JOIN main_film f ON f.title=v.ft JOIN main_hall h ON h.name=v.hn;
INSERT INTO main_customer (id, full_name, phone, email) VALUES
 (gen_random_uuid(), 'Петров Иван', '+79001234567', 'petrov@example.com'),
 (gen_random_uuid(), 'Сидорова Анна', '+79007654321', 'sidorova@example.com');
INSERT INTO main_ticket (id, session_id, seat_id, customer_id, status_id, price)
 SELECT gen_random_uuid(), s.id, st.id, c.id, ts.id, s.price
 FROM main_session s JOIN main_film f ON f.id=s.film_id
 JOIN main_seat st ON st.hall_id=s.hall_id AND st.row_number=5 AND st.seat_number IN (6,7)
 JOIN main_customer c ON c.full_name='Петров Иван'
 JOIN main_ticketstatus ts ON ts.name='Оплачен'
 WHERE f.title='Интерстеллар';
