--BikeToDrive_1_Accessoireverkoop;

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
