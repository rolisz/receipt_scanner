CREATE TABLE IF NOT EXISTS Receipts
(
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  company VARCHAR(255),
  address VARCHAR(255),
  total   DOUBLE PRECISION,
  date    DATETIME
);

CREATE TABLE IF NOT EXISTS Items
(
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       VARCHAR(255),
  qty        INTEGER,
  unit_price DOUBLE PRECISION,
  price      DOUBLE PRECISION
);

CREATE TABLE ReceiptItems
(
  receipt_id INTEGER,
  item_id    INTEGER,

  PRIMARY KEY (receipt_id, item_id),
  FOREIGN KEY (receipt_id) REFERENCES Receipts (id),
  FOREIGN KEY (item_id) REFERENCES Items (id)
)