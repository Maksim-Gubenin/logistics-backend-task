-- Информация о сумме товаров, заказанных под каждого клиента
SELECT
    c.name AS client_name,
    SUM(oi.quantity * oi.price_at_purchase) AS total_sum
FROM clients c
JOIN orders o ON c.id = o.client_id
JOIN order_items oi ON o.id = oi.order_id
GROUP BY c.id, c.name;

-- Количество дочерних элементов первого уровня для категорий
SELECT
    parent.name AS category_name,
    COUNT(child.id) AS children_count
FROM categories parent
LEFT JOIN categories child ON parent.id = child.parent_id
GROUP BY parent.id, parent.name;

-- ТОП-5 самых покупаемых товаров за последний месяц
CREATE OR REPLACE VIEW top_5_products_last_month AS
WITH RECURSIVE category_tree AS (
    SELECT id, name, id as root_id, name as root_name
    FROM categories
    WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, ct.root_id, ct.root_name
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT
    n.name AS product_name,
    ct.root_name AS root_category_name,
    SUM(oi.quantity) AS total_quantity
FROM order_items oi
JOIN orders o ON oi.order_id = o.id
JOIN nomenclatures n ON oi.nomenclature_id = n.id
JOIN category_tree ct ON n.category_id = ct.id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 month'
GROUP BY n.id, n.name, ct.root_name
ORDER BY total_quantity DESC
LIMIT 5;

-- Чтобы увидеть данные ТОП-5 самых покупаемых товаров..., нужно выполнить команду
SELECT * FROM top_5_products_last_month;`


-- Предложения по оптимизации
-- 1. Индексы: B-tree индексы на nomenclature_id, order_id и особенно на order_date
-- для быстрой фильтрации за месяц.
-- 2. Партиционирование: Если заказов тысячи в день, таблицу orders стоит
-- партиционировать по датам (по месяцам или кварталам).
-- 3. Materialized Views: Для отчетов типа ТОП-5 лучше использовать
--представления с обновлением по расписанию, чтобы не нагружать БД сложными JOIN.