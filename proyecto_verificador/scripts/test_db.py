from database import guardar_verificacion

datos_db = {
    'titulo': 'Gary Rodriguez: Si las exportaciones caen o se frenan debido el arancel impuesto por EEUU habra menos dolares y menos empleo',
    'contenido': 'El presidente de los Estados Unidos ha fijado un arancel del 10% a los productos...',
    'veredicto': 'No determinado',
    'confianza': 0.8
}

print('Llamando a guardar_verificacion...')
res = guardar_verificacion('texto', datos_db)
print('Resultado de guardar_verificacion:', res)
