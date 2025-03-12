CREATE TABLE "metadata" (
	"id"	INTEGER NOT NULL,
	"hash"	TEXT NOT NULL UNIQUE,
	"path"	TEXT NOT NULL UNIQUE,
	"album"	INTEGER,
	"camera_make"	TEXT,
	"camera_model"	TEXT,
	"date_taken"	TEXT,
	"latitude"	REAL,
	"location_name"	TEXT,
	"longitude"	REAL,
	"original_name"	TEXT,
	"title"	TEXT,
	"_modified"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
