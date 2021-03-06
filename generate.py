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

def occurrencesOf(input, substr):
    return input.count(substr)

env.filters['occurrencesOf'] = occurrencesOf

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
    
    data['plano']['conteudo_programatico'] = [x for x in data['plano']['conteudo_programatico'].split('\r\n') if x.strip()]

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
    
    # Bibliografia Básica
    cursor.execute("SELECT titulo.value as titulo, autores.value as autores, veiculo.value as veiculo, dadosadicionais.value as dadosadicionais, ano.value as ano FROM "
    "(SELECT ttif1.itemId, ttif2.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2, tiki_tracker_item_fields ttif3 "
    "WHERE "
        "ttif1.value={itemId} and "
        "ttif1.fieldId=62 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=63 and "
        "ttif3.itemId = ttif1.itemId and "
        "ttif3.fieldId=69 and "
        "ttif3.value='Básica' "
    ") titulo, "
    "(SELECT ttif1.itemId, ttif2.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2, tiki_tracker_item_fields ttif3 "
    "WHERE "
        "ttif1.value={itemId} and "
        "ttif1.fieldId=62 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=64 and "
        "ttif3.itemId = ttif1.itemId and "
        "ttif3.fieldId=69 and "
        "ttif3.value='Básica' "
    ") autores, "
    "(SELECT ttif1.itemId, ttif2.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2, tiki_tracker_item_fields ttif3 "
    "WHERE "
        "ttif1.value={itemId} and "
        "ttif1.fieldId=62 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=65 and "
        "ttif3.itemId = ttif1.itemId and "
        "ttif3.fieldId=69 and "
        "ttif3.value='Básica' "
    ") veiculo, "
    "(SELECT ttif1.itemId, ttif2.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2, tiki_tracker_item_fields ttif3 "
    "WHERE "
        "ttif1.value={itemId} and "
        "ttif1.fieldId=62 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=66 and "
        "ttif3.itemId = ttif1.itemId and "
        "ttif3.fieldId=69 and "
        "ttif3.value='Básica' "
    ") dadosadicionais, "
    "(SELECT ttif1.itemId, ttif2.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2, tiki_tracker_item_fields ttif3 "
    "WHERE "
        "ttif1.value={itemId} and "
        "ttif1.fieldId=62 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=67 and "
        "ttif3.itemId = ttif1.itemId and "
        "ttif3.fieldId=69 and "
        "ttif3.value='Básica' "
    ") ano "
    "WHERE autores.itemId=titulo.itemId and veiculo.itemId=titulo.itemId and dadosadicionais.itemId=titulo.itemId and ano.itemId=titulo.itemId".format(itemId=row['itemId']))
    data['bibliografia_basica'] = cursor.fetchall()
    
    # Bibliografia Complementar
    cursor.execute("SELECT titulo.value as titulo, autores.value as autores, veiculo.value as veiculo, dadosadicionais.value as dadosadicionais, ano.value as ano FROM "
    "(SELECT ttif1.itemId, ttif2.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2, tiki_tracker_item_fields ttif3 "
    "WHERE "
        "ttif1.value={itemId} and "
        "ttif1.fieldId=62 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=63 and "
        "ttif3.itemId = ttif1.itemId and "
        "ttif3.fieldId=69 and "
        "ttif3.value='Complementar' "
    ") titulo, "
    "(SELECT ttif1.itemId, ttif2.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2, tiki_tracker_item_fields ttif3 "
    "WHERE "
        "ttif1.value={itemId} and "
        "ttif1.fieldId=62 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=64 and "
        "ttif3.itemId = ttif1.itemId and "
        "ttif3.fieldId=69 and "
        "ttif3.value='Complementar' "
    ") autores, "
    "(SELECT ttif1.itemId, ttif2.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2, tiki_tracker_item_fields ttif3 "
    "WHERE "
        "ttif1.value={itemId} and "
        "ttif1.fieldId=62 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=65 and "
        "ttif3.itemId = ttif1.itemId and "
        "ttif3.fieldId=69 and "
        "ttif3.value='Complementar' "
    ") veiculo, "
    "(SELECT ttif1.itemId, ttif2.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2, tiki_tracker_item_fields ttif3 "
    "WHERE "
        "ttif1.value={itemId} and "
        "ttif1.fieldId=62 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=66 and "
        "ttif3.itemId = ttif1.itemId and "
        "ttif3.fieldId=69 and "
        "ttif3.value='Complementar' "
    ") dadosadicionais, "
    "(SELECT ttif1.itemId, ttif2.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2, tiki_tracker_item_fields ttif3 "
    "WHERE "
        "ttif1.value={itemId} and "
        "ttif1.fieldId=62 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=67 and "
        "ttif3.itemId = ttif1.itemId and "
        "ttif3.fieldId=69 and "
        "ttif3.value='Complementar' "
    ") ano "
    "WHERE autores.itemId=titulo.itemId and veiculo.itemId=titulo.itemId and dadosadicionais.itemId=titulo.itemId and ano.itemId=titulo.itemId".format(itemId=row['itemId']))
    data['bibliografia_complementar'] = cursor.fetchall()
    
    # Revisoes
    cursor.execute("SELECT versao.value as versao, elaboradopor.value as elaboradopor, aprovadopor.value as aprovadopor, dtaprovacao.value as dtaprovacao FROM "
    "(SELECT ttif1.itemId, ttif2.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2 "
    "WHERE "
        "ttif1.value={itemId} and "
        "ttif1.fieldId=74 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=70 "
    ") versao, "
    "(SELECT ttif1.itemId, ttif2.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2 "
    "WHERE "
        "ttif1.value={itemId} and "
        "ttif1.fieldId=74 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=71 "
    ") elaboradopor, "
    "(SELECT ttif1.itemId, ttif2.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2 "
    "WHERE "
        "ttif1.value={itemId} and "
        "ttif1.fieldId=74 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=72 "
    ") aprovadopor, "
    "(SELECT ttif1.itemId, ttif2.value FROM "
    "tiki_tracker_item_fields ttif1, tiki_tracker_item_fields ttif2 "
    "WHERE "
        "ttif1.value={itemId} and "
        "ttif1.fieldId=74 and "
        "ttif2.itemId = ttif1.itemId and "
        "ttif2.fieldId=73 "
    ") dtaprovacao "
    "WHERE elaboradopor.itemId=versao.itemId and aprovadopor.itemId=versao.itemId and dtaprovacao.itemId=versao.itemId".format(itemId=row['itemId']))
    data['revisoes'] = cursor.fetchall()

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
