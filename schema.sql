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
  receipt_id  INTEGER,
  name       VARCHAR(255),
  qty        INTEGER,
  unit_price DOUBLE PRECISION,
  price      DOUBLE PRECISION,

  FOREIGN KEY (receipt_id) REFERENCES Receipts(id)
);
