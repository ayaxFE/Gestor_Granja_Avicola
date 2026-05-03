# config.py

# Configuración de la nueva base de datos en Clever Cloud
DB_CONFIG = {
    "host": "bequh7ra6ej2pvevxazd-mysql.services.clever-cloud.com",
    "user": "uhgiebxr0zbymzuf",
    "password": "w0IIMSjfCFFQcMjal1UQ",
    "database": "bequh7ra6ej2pvevxazd",
    "port": 3306
}

# Kilos de alimento teóricos que consume UN (1) pollo por fase
CONSUMO_TEORICO_POR_AVE = {
    "F1": 0.25,   # 0.25 kg/ave (Días 1 a 7)
    "F2": 0.85,   # 0.85 kg/ave (Días 8 a 21)
    "F3": 1.0,    # 1.0 kg/ave (Días 22 a 28)
    "F4": 1.5,    # 1.5 kg/ave (Días 29 a 35)
    "F5": "A_DEMANDA"  # Día 35 hasta terminar (se calcula sin límite teórico fijo)
}

# Configuración del negocio (alertas)
UMBRAL_MORTALIDAD = 5  # Porcentaje que dispara una alerta