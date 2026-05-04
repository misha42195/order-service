import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import func, desc
from sqlalchemy.orm import Session, joinedload

from database.models import Order, OrderItem, Product


def create_order(connection, user_id, product_id, quantity, total):
    """Создать заказ с гарантией ACID"""
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # BEGIN транзакции (автоматически)
            connection.set_isolation_level(
                psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE
            )
            # Указываем схему, чтобы база "увидела" таблицы
            cursor.execute("SET search_path TO shop")

            # Проверка баланса
            cursor.execute(
                "SELECT balance FROM users WHERE id = %s FOR UPDATE", (user_id,)
            )
            user = cursor.fetchone()
            if not user or user["balance"] < total:
                connection.rollback()
                raise ValueError("Недостаточно средств")

            # Создание заказа
            cursor.execute(
                """
                INSERT INTO orders (user_id, total, status)
                VALUES (%s, %s, 'pending')
                RETURNING id
                """,
                (user_id, total),
            )
            order_id = cursor.fetchone()["id"]

            # Добавление товара в заказ
            cursor.execute(
                """
                INSERT INTO order_items (order_id, product_id, quantity)
                VALUES (%s, %s, %s)
                """,
                (order_id, product_id, quantity),
            )

            # Обновление баланса
            cursor.execute(
                "UPDATE users SET balance = balance - %s WHERE id = %s",
                (total, user_id),
            )

            # Обновление инвентаря
            cursor.execute(
                "UPDATE products SET stock = stock - %s WHERE id = %s",
                (quantity, product_id),
            )

            # COMMIT транзакции
            connection.commit()
            return order_id

    except Exception as e:
        connection.rollback()
        raise e


# До оптимизации
def get_user_orders(
    connection,
    user_id,
):
    """Получить заказы пользователя(медленно без индекса)"""
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SET search_path TO shop")
        cursor.execute(
            """
            EXPLAIN ANALYZE
            SELECT * FROM orders WHERE user_id = %s
            """,
            (user_id,),
        )
        plan = cursor.fetchall()
        print("План запроса до индекса")
        for row in plan:
            print(row["QUERY PLAN"])
        cursor.execute(
            """
            SELECT * FROM orders WHERE user_id = %s
            """,
            (user_id,),
        )
        return cursor.fetchall()


# Создание индекса
def create_index(connection):
    """Создать индексы для оптимизации"""
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO shop")
        cursor.execute("""
                       CREATE INDEX
                           IF NOT EXISTS idx_orders_user_id
                           ON orders(user_id)""")
        cursor.execute("""
                       CREATE INDEX
                           IF NOT EXISTS idx_orders_date
                           ON orders(order_date)""")
        cursor.execute("""
                       CREATE INDEX
                           IF NOT EXISTS idx_order_items_product_id
                           ON order_items(product_id)
                       """)
        connection.commit()


# После оптимизации
def get_user_orders_optimized(connection, user_id):
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SET search_path TO shop")
            cursor.execute(
                """
                EXPLAIN ANALYZE
                SELECT * FROM orders where user_id = %s
                """,
                (user_id,),
            )
            plan = cursor.fetchall()
            print("План запроса после создания индекса:")
            for row in plan:
                print(row["QUERY PLAN"])

            cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user_id,))
            return cursor.fetchall()
    except psycopg2.Error as e:
        print(f"Ошибка получения данных {e}")
        return []


"""
План запроса до индекса
Seq Scan on orders
(cost=0.00..194.04 rows=1 width=31)
(actual time=0.006..0.515 rows=4 loops=1)
  Filter: (user_id = 1)
  Rows Removed by Filter: 9999
Planning Time: 0.203 ms
Execution Time: 0.565 ms
[RealDictRow({'id': 1, 'user_id': 1, 'total': Decimal('2798.21'), 'status': 'completed', 'order_date': datetime.datetime(2026, 3, 10, 15, 43, 38, 553244)}), RealDictRow({'id': 10001, 'user_id': 1, 'total': Decimal('111.00'), 'status': 'pending', 'order_date': datetime.datetime(2026, 3, 10, 15, 43, 38, 553244)}), RealDictRow({'id': 10002, 'user_id': 1, 'total': Decimal('111.00'), 'status': 'pending', 'order_date': datetime.datetime(2026, 3, 10, 15, 43, 38, 553244)}), RealDictRow({'id': 10003, 'user_id': 1, 'total': Decimal('111.00'), 'status': 'pending', 'order_date': datetime.datetime(2026, 3, 10, 15, 47, 53, 776957)})]
None
План запроса после создания индекса:
Index Scan using idx_orders_user_id on orders
(cost=0.29..8.30 rows=1 width=31)
(actual time=0.016..0.020 rows=4 loops=1)
  Index Cond: (user_id = 1)
Planning Time: 0.161 ms
Execution Time: 0.033 ms
[RealDictRow({'id': 1, 'user_id': 1, 'total': Decimal('2798.21'), 'status': 'completed', 'order_date': datetime.datetime(2026, 3, 10, 15, 43, 38, 553244)}), RealDictRow({'id': 10001, 'user_id': 1, 'total': Decimal('111.00'), 'status': 'pending', 'order_date': datetime.datetime(2026, 3, 10, 15, 43, 38, 553244)}), RealDictRow({'id': 10002, 'user_id': 1, 'total': Decimal('111.00'), 'status': 'pending', 'order_date': datetime.datetime(2026, 3, 10, 15, 43, 38, 553244)}), RealDictRow({'id': 10003, 'user_id': 1, 'total': Decimal('111.00'), 'status': 'pending', 'order_date': datetime.datetime(2026, 3, 10, 15, 47, 53, 776957)})]
"""


# models.py
# connection.py
def get_user_order_items(session: Session, user_id: int):
    """Получить заказы пользователя через ORM с оптимизацией"""
    orders = (
        session.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .filter(Order.user_id == user_id)
        .all()
    )
    print(orders)
    if orders:
        return orders
    return None


def get_order_statistics(session: Session):
    """Получить статистику по заказам пользователей"""
    try:
        statistic = (
            session.query(
                Order.user_id,
                func.count(Order.id).label("order_count"),
                func.sum(Order.total).label("total_sum"),
            )
            .group_by(Order.user_id)
            .order_by(desc("total_sum"))
            .all()
        )
        return statistic
    except Exception as e:
        print(f"Ошибка при получении статистики: {e}")


def get_user_order_history(session: Session, user_id):
    """Получить историю заказов пользователя с информацией о товарах"""
    try:
        orders_history = (
            session.query(
                Order.id.label("order_id"),
                Order.order_date,
                Product.name.label("product_name"),
                OrderItem.quantity,
            )
            .join(OrderItem, Order.id == OrderItem.order_id)
            .join(Product, Product.id == OrderItem.product_id)
            .where(Order.user_id == user_id)
            .order_by(desc(Order.order_date))
        ).all()

        return orders_history
    except Exception as e:
        print(f"Ошибка получения данных: {e}")
        return []


def get_top_products(session: Session, limit=5):
    """Получить топ товаров по количеству продаж"""
    try:
        top_products = (
            session.query(
                Product.id,
                Product.name,
                func.sum(OrderItem.quantity).label("total_sold"),
            )
            .join(OrderItem, Product.id == OrderItem.product_id)
            .group_by(Product.id)
            .group_by(Product.name)
            .order_by(desc("total_sold"))
            .limit(limit)
        ).all()
        return top_products
    except Exception as e:
        print(f"Ошибка получения топ товаров: {e}")
        return []


def get_product_with_name(session: Session, name):
    """Получить товар по названию"""
    try:
        return session.query(Product).filter(Product.name == name).all()
    except Exception as e:
        print(f"Ошибка получения товаров по имени: {e}")
        return []


def get_orders_with_products(session: Session, user_id):
    """Получить заказы пользователя с товарами"""
    try:
        order_with_products = (
            session.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(Order.user_id == user_id)
            .all()
        )
        return order_with_products
    except Exception as e:
        print(f"Ошибка при получении заказов: {e}")
        return []
