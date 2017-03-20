#!/usr/bin/env python

import mysql.connector
from jinja2 import Template, Environment, FileSystemLoader

env = Environment(
    loader=FileSystemLoader('./')
)

template = env.get_template("main.tex")

cnx = mysql.connector.connect(user='ads', password='ads',
                              host='127.0.0.1',
                              database='ads')

cursor = cnx.cursor(dictionary=True, buffered=True)
cursor.execute("select itemId from tiki_tracker_items where trackerId=11")

for row in cursor:
    cursor = cnx.cursor(dictionary=True, buffered=True)
    cursor.execute("select "
    "codigo.value as codigo, "
    "nome.value as nome, "
    "carga_horaria.value as carga_horaria, "
    "ementa.value as ementa, "
    "objetivos_gerais.value as objetivos_gerais, "
    "objetivos_especificos.value as objetivos_especificos, "
    "conteudo_programatico.value as conteudo_programatico, "
    "metodo.value as metodo, "
    "recursos.value as recursos, "
    "pre_requisitos.value as pre_requisitos, "
    "semestre.value as semestre "
    "FROM "
    "(select itemId, value from tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=45) codigo "
    "INNER JOIN "
    "(select itemId, value from tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=46) nome "
    "INNER JOIN "
    "(select itemId, value from tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=47) carga_horaria "
    "INNER JOIN "
    "(select itemId, value from tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=49) ementa "
    "INNER JOIN "
    "(select itemId, value from tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=50) objetivos_gerais "
    "INNER JOIN "
    "(select itemId, value from tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=51) objetivos_especificos "
    "INNER JOIN "
    "(select itemId, value from tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=53) conteudo_programatico "
    "INNER JOIN "
    "(select itemId, value from tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=54) metodo "
    "INNER JOIN "
    "(select itemId, value from tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=55) recursos "
    "INNER JOIN "
    "(select itemId, value from tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=57) pre_requisitos "
    "INNER JOIN "
    "(select itemId, value from tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=96) semestre".format(itemId=row['itemId']))
    data = cursor.fetchone()
    print(template.render(data))

cnx.close()
