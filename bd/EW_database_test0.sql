CREATE TABLE EW_points_test(
    id INT IDENTITY(1,1) PRIMARY KEY,
    indice VARCHAR(30) NOT NULL,
    zona VARCHAR(30) NOT NULL,
    cantid_puntos_enc VARCHAR(30) NOT NULL,
    puntos_encont text NOT NULL,
	ult_detect_date date NOT NULL,
	ult_detect_time time(7) NOT NULL,
	celda VARCHAR(30) NOT NULL
	)
