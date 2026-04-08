-- BikeToDrive Data Warehouse
-- Star schema: Dimensies en feiten
PRAGMA foreign_keys = ON;

-- Dimensies
CREATE TABLE Datum (
	datum DATE,
	jaar INT NOT NULL,
	maand INT NOT NULL,
	kwartaal INT NOT NULL,

	PRIMARY KEY(datum)
);

CREATE TABLE Klant (
	klantnr INT,
	naam VARCHAR(45),
	adres VARCHAR(100),
	woonplaats VARCHAR(45),
	geslacht CHAR(1),
	geboortedatum DATE,
	leeftijdsklasse VARCHAR(20),

	PRIMARY KEY(klantnr)
);

CREATE TABLE Filiaal (
	filiaalnr INT,
	naam VARCHAR(45),
	adres VARCHAR(100),
	provincie VARCHAR(20),

	PRIMARY KEY(filiaalnr)
);

CREATE TABLE Monteur (
	monteurnr INT,
	naam VARCHAR(45),
	woonplaats VARCHAR(45),
	uurloon FLOAT,
	loonklasse VARCHAR(20),

	PRIMARY KEY(monteurnr)
);

CREATE TABLE Leverancier (
	leveranciernr INT,
	naam VARCHAR(45),
	adres VARCHAR(100),
	woonplaats VARCHAR(45),

	PRIMARY KEY(leveranciernr)
);

CREATE TABLE Accessoire (
	accessoirenr INT,
	naam VARCHAR(45),
	soort VARCHAR(45),
	standaardprijs FLOAT,
	inkoopprijs FLOAT,
	prijsklasse VARCHAR(20),

	PRIMARY KEY(accessoirenr)
);

CREATE TABLE Fabrikant (
	fabrikantnr INT,
	naam VARCHAR(45),
	adres VARCHAR(100),
	plaats VARCHAR(45),

	PRIMARY KEY(fabrikantnr)
);

CREATE TABLE Fiets (
	fietsnr INT,
	soort VARCHAR(45),
	merk VARCHAR(45),
	type VARCHAR(45),
	kleur VARCHAR(20),
	standaardprijs FLOAT,
	inkoopprijs FLOAT,
	prijsklasse VARCHAR(20),

	PRIMARY KEY(fietsnr)
);

-- Feiten
CREATE TABLE Accessoire_Verkoop (
	accessoire_verkoopnr INT,
	datum DATE NOT NULL,
	klantnr INT NOT NULL,
	monteurnr INT NOT NULL,
	filiaalnr INT NOT NULL,
	accessoirenr INT NOT NULL,
	leveranciernr INT NOT NULL,
	aantal INT NOT NULL,
	verkoopprijs FLOAT NOT NULL,
	omzet FLOAT NOT NULL,
	inkoopwaarde FLOAT NOT NULL,
	brutowinst FLOAT NOT NULL,

	PRIMARY KEY(accessoire_verkoopnr),
	FOREIGN KEY(datum) REFERENCES Datum(datum),
	FOREIGN KEY(klantnr) REFERENCES Klant(klantnr),
	FOREIGN KEY(monteurnr) REFERENCES Monteur(monteurnr),
	FOREIGN KEY(filiaalnr) REFERENCES Filiaal(filiaalnr),
	FOREIGN KEY(accessoirenr) REFERENCES Accessoire(accessoirenr),
	FOREIGN KEY(leveranciernr) REFERENCES Leverancier(leveranciernr)
);

CREATE TABLE Fiets_Verkoop (
	fiets_verkoopnr INT,
	datum DATE NOT NULL,
	klantnr INT NOT NULL,
	monteurnr INT NOT NULL,
	filiaalnr INT NOT NULL,
	fietsnr INT NOT NULL,
	fabrikantnr INT NOT NULL,
	aantal INT NOT NULL,
	verkoopprijs FLOAT NOT NULL,
	omzet FLOAT NOT NULL,
	inkoopwaarde FLOAT NOT NULL,
	brutowinst FLOAT NOT NULL,

	PRIMARY KEY(fiets_verkoopnr),
	FOREIGN KEY(datum) REFERENCES Datum(datum),
	FOREIGN KEY(klantnr) REFERENCES Klant(klantnr),
	FOREIGN KEY(monteurnr) REFERENCES Monteur(monteurnr),
	FOREIGN KEY(filiaalnr) REFERENCES Filiaal(filiaalnr),
	FOREIGN KEY(fietsnr) REFERENCES Fiets(fietsnr),
	FOREIGN KEY(fabrikantnr) REFERENCES Fabrikant(fabrikantnr)
);

CREATE TABLE Onderhoud (
	onderhoudnr INT,
	datum DATE NOT NULL,
	monteurnr INT NOT NULL,
	filiaalnr INT NOT NULL,
	fietsnr INT NOT NULL,
	fabrikantnr INT NOT NULL,
	starttijd TIME,
	eindtijd TIME,
	duur_minuten INT,
	arbeidskosten FLOAT,

	PRIMARY KEY(onderhoudnr),
	FOREIGN KEY(datum) REFERENCES Datum(datum),
	FOREIGN KEY(monteurnr) REFERENCES Monteur(monteurnr),
	FOREIGN KEY(filiaalnr) REFERENCES Filiaal(filiaalnr),
	FOREIGN KEY(fietsnr) REFERENCES Fiets(fietsnr),
	FOREIGN KEY(fabrikantnr) REFERENCES Fabrikant(fabrikantnr)
);
