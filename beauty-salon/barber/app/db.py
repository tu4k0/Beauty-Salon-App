import os

import psycopg2
from psycopg2.extras import RealDictCursor
CONNECTION = None
CONNECTION_CREEDS = os.environ.get('DB_ACCESS')


CUR_TYPE_MAP = {
    'one': 'fetchone',
    'all': 'fetchall',
    'many': 'fetchmany'
}


def db_save(query):
    cursor = connection = None
    try:
        connection = psycopg2.connect(CONNECTION_CREEDS)
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
    except Exception as error:
        print('Gog en error while db connecction', error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


def db_get(query, cur_type='one'):
    data = cursor = connection = None
    try:
        connection = psycopg2.connect(CONNECTION_CREEDS)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        data = getattr(cursor, CUR_TYPE_MAP[cur_type])()
    except Exception as error:
        print('Gog en error while db connecction', error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
    return data


def create_db():
    query = """
    CREATE TABLE Category (id integer primary key not null, name varchar(40));
    CREATE TABLE Status (id integer primary key not null, name varchar(40));
    CREATE TABLE Role (id integer primary key not null, name varchar(40));
    CREATE TABLE Buser (id serial primary key not null, name varchar(20), last_name varchar(20), surname varchar(20), phone varchar(20), login varchar(30), password varchar(30), Role_id integer not null references Role(id));
    CREATE TABLE Border (id serial primary key not null, Buser_id integer NOT null references Buser(id), Status_id integer NOT null references Status(id), created_at date , payment_type varchar(20), time timestamp , price integer );
    CREATE TABLE Service (id integer primary key not null, Category_id integer NOT null REFERENCES Category(id), sname varchar(40) , room varchar (10), master varchar (60), price integer , time integer );
    CREATE TABLE Cart (id serial primary key not null, Buser_id integer NOT null  references Buser(id), Status_id integer not null references Status(id));
    CREATE TABLE Service_cart_rel (id serial primary key not null, Service_id integer NOT null  REFERENCES Service(id), Cart_id integer NOT null  references Cart(id));
    CREATE TABLE Order_cart_rel (id serial primary key not null, Cart_id integer NOT null references Cart(id), Border_id integer NOT null references Border(id));
    --hook
    CREATE FUNCTION order_created()
    RETURNS trigger AS
        $BODY$
            BEGIN
                    update Border set created_at=NOW();
                    RETURN NULL;
            END;
        $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;
    CREATE trigger order_created
    AFTER insert ON border
    EXECUTE PROCEDURE order_created();
    """
    db_save(query)


def fill_db():
    query = f"""
        INSERT INTO Role (id, name) VALUES (1, 'manager'), (2, 'user');
        INSERT INTO Status (id, name) VALUES  (1, 'Cозданный'), (2, 'В реализации'), (3, 'Отклонен'), (4, 'Завершен'), (5, 'Оплачен'),  (6, 'active'), (7, 'processed');
        INSERT INTO Category (id, name) VALUES (1, 'Стрижка'), (2, 'Косметология'), (3, 'Массаж'), (4, 'Маникюр и Педикюр');
        INSERT INTO Buser (name , last_name, surname, phone, login, password, Role_id) VALUES ('admin', 'admin', 'admin', '+380501395526', 'admin', '3edc$RFV', 1);
        INSERT INTO Service (id, Category_id,  sname, room, master, price, time) VALUES
            (1, 1, 'Женская cтрижка', '2 каб.', 'Белозерова Е.Е.', 120, 60),
            (2, 1, 'Мужская cтрижка', '3 каб.', 'Иванова Е.Г.', 100, 50),
            (3, 1, 'Детская cтрижка', '5 каб.', 'Корикова С.В.', 80, 40),
            (4, 2, 'Чистка лица', '1 каб.', 'Богомолова М.А.', 200, 60),
            (5, 2, 'Эпиляция', '1 каб.', 'Богомолова М.А.', 150, 40),
            (6, 2, 'Пилинг', '1 каб.', 'Богомолова М.А.', 200, 50),
            (7, 3, 'Спортивный массаж', '4 каб.', 'Приходько К.К.', 200, 60),
            (8, 3, 'Балийский массаж', '4 каб.', 'Клименко Я.Я.', 300, 80),
            (9, 3, 'Ароматический массаж', '4 каб.', 'Приходько К.К.', 250, 50),
            (10, 3, 'Антицеллюлитный массаж', '4 каб.', 'Клименко Я.Я.', 200, 70),
            (11, 4, 'Наращивание ногтей', '6 каб.', 'Деревянко В.В.', 200, 60),
            (12, 4, 'Покрытие гель лаком', '6 каб.', 'Деревянко В.В.', 300, 80),
            (13, 4, 'Аппаратный педикюр', '6 каб.', 'Деревянко В.В.', 250, 50),
            (14, 4, 'Классический педикюр', '7 каб.', 'Деревянко В.В.', 200, 70);
    """
    db_save(query)
