CREATE TABLE IF NOT EXISTS Users (
  userId INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('user','checker'))
);

CREATE TABLE IF NOT EXISTS Rumour (
  rumourId TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  source TEXT NOT NULL,
  createdAt TEXT NOT NULL,
  credibility REAL NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('normal','panic')),
  verdict TEXT NOT NULL CHECK(verdict IN ('unknown','true','false')),
  checkedAt TEXT
);

CREATE TABLE IF NOT EXISTS Report (
  reportId INTEGER PRIMARY KEY AUTOINCREMENT,
  reporterId INTEGER NOT NULL,
  rumourId TEXT NOT NULL,
  reportedAt TEXT NOT NULL,
  reportType TEXT NOT NULL CHECK(reportType IN ('distortion','incite','fake')),
  note TEXT,
  UNIQUE(reporterId, rumourId),
  FOREIGN KEY(reporterId) REFERENCES Users(userId),
  FOREIGN KEY(rumourId) REFERENCES Rumour(rumourId)
);
