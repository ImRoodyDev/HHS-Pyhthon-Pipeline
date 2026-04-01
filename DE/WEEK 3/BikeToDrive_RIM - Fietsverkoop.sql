--BikeToDrive_2_Fietsverkoop;

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
