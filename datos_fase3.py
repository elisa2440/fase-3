
import urllib2
import requests
from datetime import date
import json

req = urllib2.Request('ftp://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-extended-latest')
response = urllib2.urlopen(req)
the_page = response.readlines()

sumaReservados = 0
sumaDisponibles = 0
sumaAsignados = 0
sumaAllocados = 0
cantISPNuevo = 0
cantiEUNuevo = 0
cantISPNuevoA = 0
cantEUNuevoA = 0
cantidadesISP = {}
cantidadesEU = {}
meses = ["201703", "201704", "201705", "201706", "201707", "201708", "201709", "201710", "201711", "201712", "201801", "201802", "201803", "201804", "201805", "201806", "201807", "201808", "201809", "201810", "201811", "201812"]

# Fetch data from FTP file
for i in the_page[4:len(the_page)-1]:
    status = i.split("|")[6]
    tipo = i.split("|")[2]
    if str(status) == "reserved" and str(tipo)=="ipv4":
        sumaReservados = sumaReservados+int(i.split("|")[4])
    if str(status).split("\n")[0] == "available" and str(tipo)=="ipv4":
        sumaDisponibles = sumaDisponibles+int(i.split("|")[4])
    if str(status) == "assigned" and str(tipo)=="ipv4":
        fecha = i.split("|")[5]
        if int(fecha) >= 20170215:
            sumaAsignados = sumaAsignados+int(i.split("|")[4])
    if str(status) == "allocated" and str(tipo)=="ipv4":
        fecha = i.split("|")[5]
        if int(fecha) >= 20170215:
            sumaAllocados = sumaAllocados+int(i.split("|")[4])

for d in meses:
    cantidadesEU[d] = []
    cantidadesISP[d] = []
    for i in the_page[4:len(the_page)-1]:
        status = i.split("|")[6]
        tipo = i.split("|")[2]
        if str(status) == "assigned" and str(tipo) == "ipv4":
            fecha = i.split("|")[5]
            if str(fecha).startswith(d):
                cantidadesEU[d].append(int(i.split("|")[4]))
        if str(status) == "allocated" and str(tipo) == "ipv4":
            fecha = i.split("|")[5]
            if str(fecha).startswith(d):
                cantidadesISP[d].append(int(i.split("|")[4]))

print cantidadesEU

a = open("nuevo.txt", "w")
b = open("asig.txt", "w")
a.write("Fecha,cantidadISPNuevo,cantidadEUNuevo,total\n")
a.write("2017-02,25600,256,25856\n")
b.write("Fecha,cantidadISPNuevo,cantidadEUNuevo,total\n")
b.write("2017-02,25,1,26\n")
for d in meses:
    sumaISP = sum(cantidadesISP[d])
    sumaEU = sum(cantidadesEU[d])
    asigEU = len(cantidadesEU[d])
    asigISP = len(cantidadesISP[d])
    if sumaISP != 0 and sumaEU != 0:
        a.write(d[0:4]+"-"+d[4:6]+","+str(sumaISP)+","+str(sumaEU)+","+str(sumaEU+sumaISP)+"\n")
        b.write(d[0:4]+"-"+d[4:6] + "," + str(asigISP) + "," + str(asigEU) + "," + str(asigEU + asigISP) + "\n")
a.close()
b.close()



# Total allocated blocks minus 40704 ips from fase 2
sumaAsigTot = sumaAsignados + sumaAllocados - 40704

sumaPreAprobados = 0

s = requests.get("http://lacnic.net/cgi-bin/lacnic/range_requests_data")
data = s.json()['preApproved']

# Fetch pre-approved blocks
for i in data:
    prefijo = i['size'][0]
    cantidad = 2**(32-int(prefijo.split("/")[1]))
    sumaPreAprobados = sumaPreAprobados + cantidad


# Revoked and returned blocks are reserved blocks minus /15 for Critical Infrastructures and pre-approved blocks
sumaDevRev = sumaReservados-2**(32-15)-sumaPreAprobados

print sumaReservados

# Available blocks are available blocks in FTP file plus pre-approved blocks plus revoked and reserved blocks (*)
sumaDisponibles = sumaDisponibles + sumaPreAprobados

f = open("new_pie.txt", "w")
f.write("alloc,assig,libres,rev_dev,inf_critica\n\n")
f.write(str(sumaAllocados-40704)+","+str(sumaAsignados)+","+str(sumaDisponibles)+","+str(sumaDevRev)+","+str(2**(32-15)))
f.close()

# (*)
sumaDisponibles = sumaDisponibles + sumaDevRev

# Total blocks for fase 3 are available plus allocated blocks plus IC
sumaTotal = sumaDisponibles + sumaAsigTot + 2**(32-15)

hoy = date.today()

st = {
    "data" : {
        "asignadas" : format(sumaAsigTot,',d').replace(',','.'),
        "disponibles" : format(sumaDisponibles,',d').replace(',','.'),
        "totales" : format(sumaTotal,',d').replace(',','.'),
        "devueltos/revocados" : format(sumaDevRev,',d').replace(',','.'),
        "actualizado" : str(hoy),
	"infraestructura_critica" : str(2**(32-15))
    }
}

dump = json.dumps(st, indent=4, separators=(',', ':'))
t = open("datos_fase3.json", "w")
t.write(dump)
t.close()
