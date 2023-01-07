CREATE TABLE "metadata" (
	"id"	INTEGER UNIQUE,
	"path"	TEXT UNIQUE,
	"hash"	TEXT UNIQUE,
	"metadata"	TEXT,
	"created"	INTEGER,
	"modified"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
