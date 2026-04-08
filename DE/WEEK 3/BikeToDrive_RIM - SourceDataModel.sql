PRAGMA foreign_keys = ON;

-- BikeToDrive_1_Accessoireverkoop
CREATE TABLE Accessoire_Verkoop_Leverancier (
	leveranciernr INT,
	naam VARCHAR(45),
	adres VARCHAR(100),
	woonplaats VARCHAR(45),

	PRIMARY KEY(leveranciernr)
);

CREATE TABLE Accessoire_Verkoop_Accessoire (
	accessoirenr INT,
	naam VARCHAR(45),
	standaardprijs FLOAT,
	inkoopprijs FLOAT,
	soort VARCHAR(45),
	leverancier INT NOT NULL,

	PRIMARY KEY(accessoirenr),
	FOREIGN KEY(leverancier) REFERENCES Accessoire_Verkoop_Leverancier(leveranciernr)
);

CREATE TABLE Accessoire_Verkoop_Filiaal (
	filiaalnr INT,
	naam VARCHAR(45),
	adres VARCHAR(100),
	provincie VARCHAR(20),

	PRIMARY KEY(filiaalnr)
);

CREATE TABLE Accessoire_Verkoop_Monteur (
	monteurnr INT,
	naam VARCHAR(45),
	woonplaats VARCHAR(45),
	uurloon FLOAT,
	filiaal INT NOT NULL,

	PRIMARY KEY(monteurnr),
	FOREIGN KEY(filiaal) REFERENCES Accessoire_Verkoop_Filiaal(filiaalnr)
);

CREATE TABLE Accessoire_Verkoop_Klant (
	klantnr INT,
	naam VARCHAR(45),
	adres VARCHAR(100),
	woonplaats VARCHAR(45),	
	geslacht CHAR(1),
	geboortedatum DATE,

	PRIMARY KEY(klantnr)
);

CREATE TABLE Accessoire_Verkoop (
	accessoire_verkoopnr INT,
	datum DATE,
	aantal INT,
	verkoopprijs FLOAT,
	klant INT NOT NULL,
	accessoire INT NOT NULL,
	monteur INT NOT NULL,

	PRIMARY KEY(accessoire_verkoopnr),
	FOREIGN KEY(klant) REFERENCES Accessoire_Verkoop_Klant(klantnr),
	FOREIGN KEY(accessoire) REFERENCES Accessoire_Verkoop_Accessoire(accessoirenr),
	FOREIGN KEY(monteur) REFERENCES Accessoire_Verkoop_Monteur(monteurnr)
);

--BikeToDrive_2_Fietsverkoop
CREATE TABLE Fiets_Verkoop_Fabrikant (
	fabrikantnr INT,
	naam VARCHAR(45),
	adres VARCHAR(100),
	plaats VARCHAR(45),

	PRIMARY KEY(fabrikantnr)
);

CREATE TABLE Fiets_Verkoop_Fiets (
	fietsnr INT,
	soort VARCHAR(45),
	merk VARCHAR(45),
	type VARCHAR(45),
	standaardprijs FLOAT,
	inkoopprijs FLOAT,
	kleur VARCHAR(20),
	fabrikant INT NOT NULL,

	PRIMARY KEY(fietsnr),
	FOREIGN KEY(fabrikant) REFERENCES Fiets_Verkoop_Fabrikant(fabrikantnr)
);

CREATE TABLE Fiets_Verkoop_Filiaal (
	filiaalnr INT,
	naam VARCHAR(45),
	adres VARCHAR(100),
	provincie VARCHAR(20),

	PRIMARY KEY(filiaalnr)
);

CREATE TABLE Fiets_Verkoop_Monteur (
	monteurnr INT,
	naam VARCHAR(45),
	woonplaats VARCHAR(45),
	uurloon FLOAT,
	filiaal INT NOT NULL,

	PRIMARY KEY(monteurnr),
	FOREIGN KEY(filiaal) REFERENCES Fiets_Verkoop_Filiaal(filiaalnr)
);

CREATE TABLE Fiets_Verkoop_Klant (
	klantnr INT,
	naam VARCHAR(45),
	adres VARCHAR(100),
	woonplaats VARCHAR(45),	
	geslacht CHAR(1),
	geboortedatum DATE,

	PRIMARY KEY(klantnr)
);

CREATE TABLE Fiets_Verkoop (
	fiets_verkoopnr INT,
	datum DATE,
	aantal INT,
	verkoopprijs FLOAT,
	klant INT NOT NULL,
	fiets INT NOT NULL,
	monteur INT NOT NULL,

	PRIMARY KEY(fiets_verkoopnr),
	FOREIGN KEY(klant) REFERENCES Fiets_Verkoop_Klant(klantnr),
	FOREIGN KEY(fiets) REFERENCES Fiets_Verkoop_Fiets(fietsnr),
	FOREIGN KEY(monteur) REFERENCES Fiets_Verkoop_Monteur(monteurnr)
);

-- BikeToDrive_3_Onderhoud
CREATE TABLE Onderhoud_Fabrikant (
	fabrikantnr INT,
	naam VARCHAR(45),
	adres VARCHAR(100),
	plaats VARCHAR(45),

	PRIMARY KEY(fabrikantnr)
);

CREATE TABLE Onderhoud_Fiets (
	fietsnr INT,
	soort VARCHAR(45),
	merk VARCHAR(45),
	type VARCHAR(45),
	standaardprijs FLOAT,
	inkoopprijs FLOAT,
	kleur VARCHAR(20),
	fabrikant INT NOT NULL,

	PRIMARY KEY(fietsnr),
	FOREIGN KEY(fabrikant) REFERENCES Onderhoud_Fabrikant(fabrikantnr)
);

CREATE TABLE Onderhoud_Filiaal (
	filiaalnr INT,
	naam VARCHAR(45),
	adres VARCHAR(100),
	provincie VARCHAR(20),

	PRIMARY KEY(filiaalnr)
);

CREATE TABLE Onderhoud_Monteur (
	monteurnr INT,
	naam VARCHAR(45),
	woonplaats VARCHAR(45),
	uurloon FLOAT,
	filiaal INT NOT NULL,

	PRIMARY KEY(monteurnr),
	FOREIGN KEY(filiaal) REFERENCES Onderhoud_Filiaal(filiaalnr)
);

CREATE TABLE Onderhoud (
	onderhoudnr INT,
	datum DATE,
	starttijd TIME,
	eindtijd TIME,
	fiets INT NOT NULL,
	monteur INT NOT NULL,

	PRIMARY KEY(onderhoudnr),
	FOREIGN KEY(fiets) REFERENCES Onderhoud_Fiets(fietsnr),
	FOREIGN KEY(monteur) REFERENCES Onderhoud_Monteur(monteurnr)
);

--BikeToDrive_4_Accessoire_inkoop
CREATE TABLE Accessoire_Inkoop_Leverancier (
	leveranciernr INT,
	naam VARCHAR(45),
	adres VARCHAR(100),
	woonplaats VARCHAR(45),

	PRIMARY KEY(leveranciernr)
);

CREATE TABLE Accessoire_Inkoop_Accessoire (
	accessoirenr INT,
	naam VARCHAR(45),
	standaardprijs FLOAT,
	inkoopprijs FLOAT,
	soort VARCHAR(45),
	leverancier INT NOT NULL,

	PRIMARY KEY(accessoirenr),
	FOREIGN KEY(leverancier) REFERENCES Accessoire_Inkoop_Leverancier(leveranciernr)
);

CREATE TABLE Accessoire_Inkoop (
	inkoopnr INT,
	inkoopmaand INT,
	inkoopjaar INT,
	aantal INT,
	accessoire INT NOT NULL,

	PRIMARY KEY(inkoopnr),
	FOREIGN KEY(accessoire) REFERENCES Accessoire_Inkoop_Accessoire(accessoirenr)
);

-- BikeToDrive_5_Fiets_Inkoop
CREATE TABLE Fiets_Inkoop_Fabrikant (
	fabrikantnr INT,
	naam VARCHAR(45),
	adres VARCHAR(100),
	plaats VARCHAR(45),

	PRIMARY KEY(fabrikantnr)
);

CREATE TABLE Fiets_Inkoop_Fiets (
	fietsnr INT,
	soort VARCHAR(45),
	merk VARCHAR(45),
	type VARCHAR(45),
	standaardprijs FLOAT,
	inkoopprijs FLOAT,
	kleur VARCHAR(20),
	fabrikant INT NOT NULL,

	PRIMARY KEY(fietsnr),
	FOREIGN KEY(fabrikant) REFERENCES Fiets_Inkoop_Fabrikant(fabrikantnr)
);

CREATE TABLE Fiets_Inkoop (
	inkoopnr INT,
	inkoopmaand INT,
	inkoopjaar INT,
	aantal INT,
	fiets INT NOT NULL,

	PRIMARY KEY(inkoopnr),
	FOREIGN KEY(fiets) REFERENCES Fiets_Inkoop_Fiets(fietsnr)
);
