INSERT INTO SPR_KKM (ID_KKM, C_KKM, C_CDXLIB, C_VNDLIB)
             VALUES (100, 'HTTP', 'cdexphttp.dll', '');

INSERT INTO SPR_KKMPROP (ID_KKM, ID_PROP, C_NM, C_VL)
                 VALUES (100, 1, 'url', 'http://localhost:8080/cdx');

COMMIT WORK;
