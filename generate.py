#!/usr/bin/python3

import mysql.connector
import subprocess
import shutil
import os

from jinja2 import Template, Environment, FileSystemLoader

def copyDirectory(src, dest):
    try:
        shutil.copytree(src, dest)
    # Directories are the same
    except shutil.Error as e:
        print('Directory not copied. Error: %s' % e)
    # Any error saying that the directory doesn't exist
    except OSError as e:
        print('Directory not copied. Error: %s' % e)

env = Environment(
    loader=FileSystemLoader('./')
)

template = env.get_template("template/main.tex.tmpl")
os.makedirs('tmp')
os.makedirs('output')

cnx = mysql.connector.connect(user='ads', password='ads',
                              host='127.0.0.1',
                              database='ads')

cursor = cnx.cursor(dictionary=True, buffered=True)
cursor.execute("SELECT itemId FROM tiki_tracker_items where trackerId=11")

for row in cursor:
    cursor = cnx.cursor(dictionary=True, buffered=True)
    cursor.execute("SELECT "
    "codigo.value as codigo, "
    "nome.value as nome, "
    "carga_horaria.value as carga_horaria, "
    "professor.value as professor, "
    "ementa.value as ementa, "
    "objetivos_gerais.value as objetivos_gerais, "
    "objetivos_especificos.value as objetivos_especificos, "
    "conteudo_programatico.value as conteudo_programatico, "
    "metodo.value as metodo, "
    "recursos.value as recursos, "
    "pre_requisitos.value as pre_requisitos, "
    "semestre.value as semestre "
    "FROM "
    "(SELECT itemId, value FROM tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=45) codigo "
    "INNER JOIN "
    "(SELECT itemId, value FROM tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=46) nome "
    "INNER JOIN "
    "(SELECT itemId, value FROM tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=47) carga_horaria "
    "INNER JOIN "
    "(SELECT itemId, value FROM tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=97) professor "
    "INNER JOIN "
    "(SELECT itemId, value FROM tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=49) ementa "
    "INNER JOIN "
    "(SELECT itemId, value FROM tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=50) objetivos_gerais "
    "INNER JOIN "
    "(SELECT itemId, value FROM tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=51) objetivos_especificos "
    "INNER JOIN "
    "(SELECT itemId, value FROM tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=53) conteudo_programatico "
    "INNER JOIN "
    "(SELECT itemId, value FROM tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=54) metodo "
    "INNER JOIN "
    "(SELECT itemId, value FROM tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=55) recursos "
    "INNER JOIN "
    "(SELECT itemId, value FROM tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=57) pre_requisitos "
    "INNER JOIN "
    "(SELECT itemId, value FROM tiki_tracker_item_fields WHERE itemId={itemId} and fieldId=96) semestre".format(itemId=row['itemId']))
    data = {}
    data['plano'] = cursor.fetchone()
    print("Generating " + data['plano']['codigo'])

    # Pre-requisitos
    data['pre_requisitos'] = []
    if data['plano']['pre_requisitos']:
        cursor.execute("SELECT CONCAT(ttif1.value, ' - ', ttif2.value) as pre_requisito FROM "
        "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2 WHERE "
        "ttif1.itemId in ({CodPreReqs}) and ttif1.fieldId=45 and "
        "ttif2.itemId=ttif1.itemId and ttif2.fieldId=46".format(CodPreReqs=data['plano']['pre_requisitos']))
        data['pre_requisitos'] = cursor.fetchall()

    # Avaliacoes
    cursor.execute("SELECT tipo.value as tipo, qtde.value as qtde, peso.value as peso FROM "
    "(SELECT ttif1.itemId, ttif3.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2, tiki_tracker_item_fields ttif3 "
    "WHERE "
        "ttif1.value={itemId} and "
        "ttif1.fieldId=56 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=59 and "
        "ttif3.itemId = ttif2.value "
    ") tipo, "
    "(SELECT ttif2.itemId, ttif2.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2 "
    "WHERE "
        "ttif1.fieldId=56 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=60 "
    ") qtde, "
    "(SELECT ttif2.itemId, ttif2.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2 "
        "WHERE "
        "ttif1.fieldId=56 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=61 "
    ") peso "
    "WHERE qtde.itemId=tipo.itemId and peso.itemId=tipo.itemId".format(itemId=row['itemId']))
    data['avaliacoes'] = cursor.fetchall()

    copyDirectory('template', "tmp/" + data['plano']['codigo'])
    with open("tmp/" + data['plano']['codigo'] + "/" + data['plano']['codigo'] + ".tex", "w") as fh:
        fh.write(template.render(data))
    os.chdir("tmp/" + data['plano']['codigo'])
    proc = subprocess.Popen(['pdflatex', data['plano']['codigo'] + ".tex"], stdout=subprocess.PIPE)
    proc.communicate()
    shutil.move(data['plano']['codigo'] + ".pdf", "../../output/")
    os.chdir("../../")

shutil.rmtree("tmp")
cnx.close()
