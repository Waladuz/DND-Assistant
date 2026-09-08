-- Run once against an existing assets.db with the application closed.
-- Safe to rerun: quantities are merged before duplicate item records are removed.
-- Keep original coin IDs; correct their values and make them weightless.
BEGIN IMMEDIATE;

-- Preserve inventory quantities, including when a player has no original stack.
CREATE TEMP TABLE coin_inventory_merge AS
SELECT characterId,
       CASE itemId WHEN 194 THEN 188 WHEN 195 THEN 189 WHEN 196 THEN 190
                   ELSE itemId END AS itemId,
       isEquipped, SUM(amount) AS amount
FROM inventory
WHERE itemId IN (188, 189, 190, 194, 195, 196)
GROUP BY characterId,
         CASE itemId WHEN 194 THEN 188 WHEN 195 THEN 189 WHEN 196 THEN 190
                     ELSE itemId END,
         isEquipped;

DELETE FROM inventory WHERE itemId IN (188, 189, 190, 194, 195, 196);
INSERT INTO inventory (characterId, itemId, isEquipped, amount)
SELECT characterId, itemId, isEquipped, amount FROM coin_inventory_merge;
DROP TABLE coin_inventory_merge;

UPDATE equipment
SET item_id = CASE item_id WHEN 194 THEN 188 WHEN 195 THEN 189 WHEN 196 THEN 190 END
WHERE item_id IN (194, 195, 196);
UPDATE map_loot
SET item_id = CASE item_id WHEN 194 THEN 188 WHEN 195 THEN 189 WHEN 196 THEN 190 END
WHERE item_id IN (194, 195, 196);

UPDATE items
SET weight = 0,
    baseValue = CASE id WHEN 188 THEN 1 WHEN 189 THEN 10 WHEN 190 THEN 100 END
WHERE id IN (188, 189, 190);

DELETE FROM items WHERE id IN (194, 195, 196);
COMMIT;
