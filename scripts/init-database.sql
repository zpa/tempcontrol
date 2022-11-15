CREATE TABLE Measurement (
       id INTEGER PRIMARY KEY,
       timestamp TEXT NOT NULL,
       temperature REAL,
       humidity REAL
       );

CREATE TABLE State (
       id INTEGER PRIMARY KEY,
       timestamp TEXT NOT NULL,
       stateId INT NOT NULL,
       param INT,
       requester TEXT NOT NULL
       );

CREATE TABLE Healthcheck (
       id INTEGER PRIMARY KEY,
       timestamp TEXT NOT NULL,
       result TEXT NOT NULL
       );

INSERT INTO State(timestamp,stateId,requester) VALUES('2022-01-01 00:00:00',1,'creator');
INSERT INTO Healthcheck(timestamp,result) VALUES('2022-01-01 00:00:00','OK');

