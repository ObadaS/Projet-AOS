import bottle
import json
import requests
import datetime

from bs4 import BeautifulSoup
from decimal import *
from bottle import route, run, response, get, delete, put, post

#Une "constante" globale pour pouvoir ajouter un bouton qui nous ramene au menu principale
goBack = """</br><form action="/database/main">
    <button type="submit" formmethod="post">Go back to main menu</button>
    </form>
    """
####################################################################################
#                                   GET                                            #
####################################################################################
@get("/show/all/<a>") #Le <a> permet de prendre la valeur et de l'utiliser plus bas (Donne toutes les donnée dont la valeur est a)
def showAll(a) :
    data = json.loads(open("students.json").read())
    datafinal = list()

    if("Name" in a): #Cas special si on demande le nom, on n'affichera que ca au lieu d'afficher l'information demandé + le nom
        for x in range(0, len(data)):
            datafinal.append(data[x][a])

    else:
        for x in range(0, len(data)):
            datafinal.append("The value of " + str(a) + " for "+ str(data[x]["Name"]) + " is : "+ str(data[x][a])) #On doit convertir en str sinon ca peut renvoyer des int, ce que bottle n'aime pas afficher 

    dataformatter = '<br/><br/>'.join(map(str, datafinal))#Permet de convertire la list en une chaine caractere
    return dataformatter

@route("/show/template", method=['GET', 'POST']) #Montre le modèle a jour de la base de donnée
def showTemplate() :
    data = json.loads(open("students.json").read())
    temp = list()

    for i in data[0] :
        temp.append(i+"</br>")
    
    return ''.join(map(str, temp)), goBack


@get("/show/everything/<name>") #Donne toutes les informations de la personne Name
def showEverything(name) :
    data = json.loads(open("students.json").read())

    for x in range(0, len(data)):
        if(name in data[x]["Name"]):
            return data[x]

    response.status = 404
    return 'Name not found'

@get("/showRowNumber/<value>/<name>") #Pour avoir le row number de la personne ayant comme ID(value), 3(name) (exemple)
def showRowNumber(value, name) :
    data = json.loads(open("students.json").read())
    datafinal = list()

    for x in range(0, len(data)):
        if(name in data[x][value]):
            return str(x) #Il faut convertir x en character sinon bottle n'arrive pas a afficher le resultat

    response.status = 404
    return name +' not found'

@get("/count/all/<name>")#Retourne le nombre d'étudiants avec le meme nom name
def count(name):
    data = json.loads(open("students.json").read())
    count = 0

    for x in range(0, len(data)):
        if(name in data[x]["Name"]):
            count = count + 1

    return str(count) #Erreur si on renvoi un int, donc on convertie en str

####################################################################################
#                                   GET(to launch other verbs)                     #
####################################################################################
@route("/student/add", method=['GET', 'POST'])
def getAdd() :
    formulaireStudentAdd = """
    <form method='post' action='/student/add/results'>
    <input type='text'  name='name' placeholder='Name'/>
    <input type='submit' value='Validez !'/>
    </form>
    """
    return formulaireStudentAdd

@get("/student/modify/<number>/<value>/<new>") #Pour modifier la valeur Value de new dans le row number
def getModify(number, value, new) :
    return modify(number, value, new)

@get("/database/add/row/<key>/<value>") #Rajoute un couple clé/valeur a toutes les données dans le fichier students.json
def getrowAdd(key, value) :
    return rowAdd(key, value)

@get("/student/remove/<name>") #Efface toutes les informations de <name>
def getDelete(name) :
    return delete(name)
####################################################################################
#                                   POST                                           #
####################################################################################
@post("/student/add/results") #Rajoute un nouvel utilisateur
def add() :
    name = bottle.request.forms.get('name')
    data = json.loads(open("students.json").read())
    
    modèle = data[0]
    modèle = dict.fromkeys(modèle, 0) #Remet toutes les valeurs a 0
    modèle["ID"] = len(data)+1 #On veux que le ID soit unique a chaque personne, et augment de 1 a chaque fois que on rajoute quelqun
    modèle["Name"] = name

    with open('students.json') as f:
        data = json.load(f)

    data.append(modèle)

    with open('students.json', 'w') as f:
        json.dump(data, f)

    return 'Added ' + name, goBack

@post("/database/add/row/<key>/<value>") #Rajoute un row à toutes les données dans le fichier students.json
def rowAdd(key, value) :
    jsonFile = open("students.json", "r")
    data = json.load(jsonFile)
    jsonFile.close()

    for x in range(len(data)):
        data[x][key] = value

    jsonFile = open("students.json", "w")
    json.dump(data, jsonFile)
    jsonFile.close()

    return "Le row "+ str(key)+" à été rajouté avec la valeur "+str(value)+" avec succes" #TypeError vu que on veux "concatenate" des valeurs non str (les key et value) à des valeurs str
####################################################################################
#                                   PUT                                            #
####################################################################################
@put("/student/modify/<number>/<value>/<new>") #Pour modifier la valeur Value a New dans le row Number
def modify(number, value, new) :
    
    jsonFile = open("students.json", "r")
    data = json.load(jsonFile)
    jsonFile.close()

    if(int(number) > len(data)):
        response.status = 404
        return "Row "+number+" not found"

    data[int(number)][value] = new

    jsonFile = open("students.json", "w")
    json.dump(data, jsonFile)
    jsonFile.close()
    return value + " has been successfully changed to "+new

####################################################################################
#                                   DELETE                                         #
####################################################################################
@delete("/student/remove/<name>") #Efface toutes les informations de <name>
def delete(name) :

    jsonFile = open("students.json", "r")
    data = json.load(jsonFile)
    jsonFile.close()

    for x in range(0, len(data)):
        if(name in data[x]["Name"]):
            del data[x]
            temp = x
            break
        if(x == (len(data)-1)):
            response.status = 404
            return name +' not found'
    
    for x in range(temp, len(data)):
        data[x]["ID"] = x+1

    jsonFile = open("students.json", "w")
    json.dump(data, jsonFile)
    jsonFile.close()
    return 'All the informations related to '+name+' has been deleted'


####################################################################################
#                                   "UI"                                           #
####################################################################################
@route("/database/main", method=['GET', 'POST']) #Pour charger la page principal qui nous donne les options decrit plus bas, au lieu de devoir utiliser les URL pour lancer les fonctions.
def mainHTML():

    formulaire = """
    <form action="/show/all">
    <button type="submit" formmethod="post">Donne toutes les donées de la valeur entré</button>
    </form>

    <form action="/show/everything">
    <button type="submit" formmethod="post">Pour donnée toutes les informations de l'étudiant</button>
    </form>

    <form action="/showRowNumber">
    <button type="submit" formmethod="post">Pour chercher le row number</button>
    </form>

    <form action="/student/modify">
    <button type="submit" formmethod="post">Pour modifier la valeur d'une case d'un étudiant</button>
    </form>

    <form action="/count/all" method="post">
    <button type="submit" formmethod="post">Pour compter le nombre d'étudiant ayant le meme nom</button>
    </form>

    <form action="/student/add">
    <button type="submit" formmethod="post">Rajoute un nouvel étudiant</button>
    </form>

    <form action="/student/remove">
    <button type="submit" formmethod="post">Pour effacer un étudiant</button>
    </form>

    <form action="/database/add/row/">
    <button type="submit" formmethod="post">Pour rajouter une nouvelle clé dans le Database (pour tous les étudiants)</button>
    </form>

    <form action="/show/template">
    <button type="submit" formmethod="post">Montre le modèle à jour</button>
    </form>

    <form action="/professor/published">
    <button type="submit" formmethod="post">Cherche les publication d'un professeur</button>
    </form>
    
    <form action="/students/train">
    <button type="submit" formmethod="post">Cherche le prochain train</button>
    </form>
    """
   
    formatt = "<h1 style=color:green;>::Server.py:: Choisir l'option desirer</h1>"
    
    return formatt + formulaire


@post("/show/all") 
def postShowALL():

    a = bottle.request.forms.get('a')
    if(a is None):
        formulaireshowAll = """
        <form  action="/show/all" method='post'>
        <input type='text'  name='a' placeholder='Choisir une valeur dans la liste a afficher'/>
        <input type='submit' value='Validez !'/>
        </form>
        """
        informationPossible = """
        <b>Informations possible pour la case Value : </b>
        <ul>
        <li>ID</li>
        <li>Name</li>
        <li>Gender</li>
        <li>Class</li>
        <li>Seat</li>
        <li>Club</li>
        <li>Student ID</li>
        <li>Phone Number</li>
        <li>GPA</li>
        <li>Strength</li>
        <li>Color</li>
        <li>Eyes</li>
        <li>EyeType</li>
        <li>Random Data</li>
        <li>Accessory</li>
        <li>ScheduleTime</li>
        <li>ScheduleDestination</li>
        <li>ScheduleAction</li>
        <li>Info</li>
        <li>Hairstyle</li>
        </ul>
        """
        return formulaireshowAll, informationPossible
    else:
        return showAll(a), goBack

@post("/show/everything")
def postShowEverything():

    name = bottle.request.forms.get('name')
    if(name is None):
        formulaireShowEverything = """
        <form  action="/show/everything" method='post'>
        <input type='text'  name='name' placeholder='Name'/>
        <input type='submit' value='Validez !'/>
        </form>
        """
        return formulaireShowEverything
    else:
        return showEverything(name)

@post("/showRowNumber")
def postShowRowNumber():

    value = bottle.request.forms.get('value')
    name = bottle.request.forms.get('name')
    if(name is None): #Pas Besoin de tester les deux valeur, si une a changer, l'autre a forcement changer
        formulaireShowRowNumber = """
        <form  action="/showRowNumber" method='post'>
        <input type='text'  name='value' placeholder='La valeur'/>
        <input type='text'  name='name' placeholder='Name'/>
        <input type='submit' value='Validez !'/>
        </form>
        """
        informationPossible = """
        <b>Informations possible pour la case Value : </b>
        <ul>
        <li>ID</li>
        <li>Name</li>
        <li>Gender</li>
        <li>Class</li>
        <li>Seat</li>
        <li>Club</li>
        <li>Student ID</li>
        <li>Phone Number</li>
        <li>GPA</li>
        <li>Strength</li>
        <li>Color</li>
        <li>Eyes</li>
        <li>EyeType</li>
        <li>Random Data</li>
        <li>Accessory</li>
        <li>ScheduleTime</li>
        <li>ScheduleDestination</li>
        <li>ScheduleAction</li>
        <li>Info</li>
        <li>Hairstyle</li>
        </ul>
        """
        return formulaireShowRowNumber, informationPossible
    else:
        return showRowNumber(value, name), goBack

@post("/count/all")
def postCountAll():

    name = bottle.request.forms.get('name')
    if(name is None):
        formulaireCountAll = """
        <form  action="/count/all" method='post'>
        <input type='text'  name='name' placeholder='Le nom de l'étudiant/>
        <input type='submit' value='Validez !'/>
        </form>
        """
        return formulaireCountAll
    else:
        return count(name), goBack

@post("/student/modify")
def postModify():

    number = bottle.request.forms.get('number')
    value = bottle.request.forms.get('value')
    new = bottle.request.forms.get('new')

    if(number is None):
        formulaireModify = """
        <form  action="/student/modify" method='post'>
        <input type='text'  name='number' placeholder='Number'/>
        <input type='text'  name='value' placeholder='Value'/>
        <input type='text'  name='new' placeholder='New'/>
        <input type='submit' value='Validez !'/>
        </form>
        """
        informationPossible = """
        <b>Informations possible pour la case Value : </b>
        <ul>
        <li>ID</li>
        <li>Name</li>
        <li>Gender</li>
        <li>Class</li>
        <li>Seat</li>
        <li>Club</li>
        <li>Student ID</li>
        <li>Phone Number</li>
        <li>GPA</li>
        <li>Strength</li>
        <li>Color</li>
        <li>Eyes</li>
        <li>EyeType</li>
        <li>Random Data</li>
        <li>Accessory</li>
        <li>ScheduleTime</li>
        <li>ScheduleDestination</li>
        <li>ScheduleAction</li>
        <li>Info</li>
        <li>Hairstyle</li>
        </ul>
        """
        return formulaireModify, informationPossible
    else:
        return modify(number, value, new), goBack


@post("/database/add/row/")
def postAddRow():
    
    key = bottle.request.forms.get('key')
    value = bottle.request.forms.get('value')
    
    if(key is None):
        formulaireRowAdd = """
        <form  action="/database/add/row/" method='post'>
        <input type='text'  name='key' placeholder='Le nom de la clé'/>
        <input type='text'  name='value' placeholder='La valeur de la clé'/>
        <input type='submit' value='Validez !'/>
        </form>
        """
        return formulaireRowAdd
    else:
        return rowAdd(key, value), goBack

@post("/student/remove")
def postREMOVE():

    name = bottle.request.forms.get('name')
    if(name is None):
        formulaireStudentAdd = """
        <form  action="/student/remove" method='post'>
        <input type='text'  name='name' placeholder='Name'/>
        <input type='submit' value='Validez !'/>
        </form>
        """
        return formulaireStudentAdd
    else:
        return delete(name), goBack

####################################################################################
#                                   API externe                                    #
####################################################################################
@route("/professor/published", method=['GET', 'POST'])#Permet de chercher les ouvrages publié par un professeur
def Prof() :
    formulaire = """
    <form method='post' action='/professor/published/results'>
    <input type='text'  name='url' placeholder='Nom & Prenom ?'/>
    <input type='text'  name='Date' placeholder='Date de publication ?'/>
    <input type='text'  name='Information' placeholder='information ?' />
    <input type='submit' value='Validez !'/>
    </form>
    """
    
    informationPossible = """
    <ul>
    <li>author : Les auteurs</li>
    <li>title : Le titre</li>
    <li>pages : Nombre de pages </li>
    <li>volume : </li>
    <li>journal : Pour les publication Journal </li>
    <li>editor : Pour les publication Editeur </li>
    <li>informal : Pour les publication Informel </li>
    <li>conference : Pour les Conference </li>
    <li>number : </li>
    <li>ee : </li>
    <li>url : </li>
    </ul>
    """
    textFormulaire = "<h1 style=color:green;>Entrer le Nom & Prenom et une date pour  afficher les informations que vous avez choisi de cette date</h1>" + formulaire
    informationPossibles = "<b>Informations possible (Entrer 0 dans le champ Date si vous voulez tout afficher, sans tenir compte de la date) : </b>" + informationPossible
    return  textFormulaire, informationPossibles

@post("/professor/published/results")
def resultatProf() :
    information = bottle.request.forms.get('Information')
    nomPrenom = bottle.request.forms.get('url')
    Date = bottle.request.forms.get('Date')
    url = "https://dblp.uni-trier.de/search/author?q=" + nomPrenom #https://dblp.uni-trier.de/search/author?q=
    page = requests.get(url) #Prend le contenu de la page web URL et la met dans page.
    soup = BeautifulSoup(page.text, 'html.parser')
    soup = soup.find_all("li", class_="select-on-click") #retourne une liste
    length = len(soup) #calcule la taille de soup
    soup2 = list(soup) #Can also use the following : soup2 = soup[:]
    b = 1 #necessaire pour regler le probleme de la liste qui change en temps reel
    listInformation = list() #Pour avoir une liste vide a utiliser plus tard dans une boucle

    if("infor" in information.lower()): #Pour faciliter la reconaisance des differents ecritures (Anglais VS Francais)
        information = "informal"
    elif("edit" in information.lower()):
        information = "editor"
    elif("conf" in information.lower()):
        information = "conference"
    elif("jour" in information.lower()):
        information = "journal"

    #Nettoye la list pour enlever tous les elements contenant le terme HTTPS
    for x in range(1, length): #On commence a 1 pour sauter la premier valeur qui est inutile pour nous (et qui fais des erreurs)
        contenuVoulu = soup[x].getText()
        if("https" in contenuVoulu):
            soup2.pop(b) #pop permet d'enlever une valeur de la list se trouvant a l'indice b
        else :
            b = b + 1

    length2 = len(soup2)
    for x in range(1, length2):#Boucle principal pour avoir les informations que nous cherchons
        urlPart1 = "https://dblp.uni-trier.de/rec/xml/"
        urlPart2 =  soup2[x].getText()
        url2 = urlPart1 + urlPart2 + ".xml"
        page2 = requests.get(url2)
        tempSoup = BeautifulSoup(page2.text, 'html.parser')
        if Date in tempSoup.find("year") or Date == "0":
            if (tempSoup.find("journal") or tempSoup.find("booktitle") or tempSoup.find(information)) : #Pour ne pas ajoute un element vide dans la list (qui renvera "none")
                if("informal" in information):
                    if(tempSoup.find("journal") and tempSoup.find("article", attrs={"publtype": "informal"})):#Balise puis class
                        listInformations = ' & '.join(map(str, tempSoup.find_all("journal"))) #Permet de prendre plusieurs balise s'il le faut (comme pour les auteurs)
                        listInformation.append(listInformations)
                elif("journal" in information):
                    if(tempSoup.find("journal") and not tempSoup.find("article", attrs={"publtype": "informal"})):
                        listInformations = ' & '.join(map(str, tempSoup.find("journal")))
                        listInformation.append(listInformations)
                elif("editor" in information):
                    if(tempSoup.find("booktitle") and tempSoup.find("publisher")):
                        listInformations = ' & '.join(map(str, tempSoup.find("booktitle")))
                        listInformation.append(listInformations)
                elif("conference" in information):
                    if(tempSoup.find("booktitle") and not tempSoup.find("publisher")):
                        listInformations = ' & '.join(map(str, tempSoup.find("booktitle")))
                        listInformation.append(listInformations)
                else:
                    listInformations = ' & '.join(map(str, tempSoup.find_all(information)))
                    listInformation.append(listInformations)

    count = len(listInformation)
    contenuInformation = '<br/>'.join(map(str, listInformation)) #Permet de convertire la list en une chaine caractere, la balise br permet de sauter de ligne

    contenuInformation2 = contenuInformation.replace("<"+information+">", "")#Pour enlever les "balises" avant et apres le text qui nous interesse
    contenuInformationFinal= contenuInformation2.replace("</"+information+">", "")

    descriptifNomPrenom = "<h1 style=color:green;>Vous avez rentrer le Nom et Prenom suivant :  " + nomPrenom + "</h1>"
    separateur = "<h2 style=color:green;>---------------------</h2>"
    typeDate = "<h3 style=color:green;>La date choisi est : " + Date
    typeDate0 = "<h3 style=color:green;>Vous avez choisi de tout afficher "
    typeinformation = "<h3 style=color:green;>Le type d'information choisi est : " + information + "</h3>"
    totalAfficher = "<h3 style=color:green;>Total : " + str(count) + "</h3>" #Le str est necessaire, sinon ca renvoi une erreur (concatenate str et int)

    if(Date == "0"): #Le message change legerement si l'utilisateur rentre 0 comme date
        return descriptifNomPrenom + typeDate0 + typeinformation + separateur + contenuInformationFinal +  totalAfficher, goBack
    else:
        return descriptifNomPrenom + typeDate + typeinformation + separateur + contenuInformationFinal + totalAfficher, goBack

@route("/students/train", method=['GET', 'POST'])#Permet de trouve les horaires des prochains train departant une gare donnée par l'utilisateur
def getnextTrain() :
    formulaire = """
    <form method='post' action='/students/train/next'>
    <input size="45" type='text'  name='nomgare' placeholder='Nom de la Gare (Ne prend que Nom ou Code)'/>
    <input size="45" type='text'  name='zip_code' placeholder='Code Postal (Ne prend que Nom ou Code)'/>
    <input size="45" type='text'  name='stop_id' placeholder='stop_id'/>
    <input size="45" type='time'  name='heure'/>
    <input size="45" type='date'  name='date'/>
    <input type='submit' value='Validez !'/>
    </form>
    """
    informationPossible = """
    <ul>
    <li>Il ne faut entrer que le code postal ou le nom de la gare</li>
    <li>Le nom est plus precis que le code postal</li>
    <li>La case stop_id est optionel, elle contourne le nom de la gare et le code postal</li>
    </ul>
    """

    textFormulaire = "<h1 style=color:green;>Entrer le nom d'une gare OU le code postal, puis une date et une heure pour afficher les prochains train  quittant la gare</h1>" + formulaire
    informationPossibles = '<b>Informations (Pour afficher toutes les gares : Ecriver "all0" dans la case Nom, ou "all" dans la case code postal): </b>' + informationPossible
    return textFormulaire + informationPossibles

@post("/students/train/next")
def nextTrain() :
    #AAAAMMJJTHHMMSS (Année, mois, jour, heure, minutes, secondes)
    nomGare = bottle.request.forms.nomgare #Pour gerer les accents
    zipCode = bottle.request.forms.get('zip_code')
    stop_ID = bottle.request.forms.get('stop_id')
    time = bottle.request.forms.get('heure').replace(":","")#Le replace n'as pas l'air d'etre necessaire, ca fonctionne sans, pour time et Date
    Date = bottle.request.forms.get('date').replace("-","")
    dateFinal = Date+"T"+time
    depart = list()

    garesUrl = "https://api.sncf.com/v1/coverage/sncf/stop_areas?start_page="
    token_SNCF = "cad2e443-b6b1-48f6-a219-364caf4ba689" #token special, il faut s'inscrire sur SNCF pour en avoir un
    jsonURL = requests.get(garesUrl+"0", auth=(token_SNCF, '')) #auth permet de s'identifier aupres du lien fourni, sinon ca ne fonctionne pas
    dataSNCF_Url = jsonURL.json() #pour les coordonnes d'une gare, il y'a 121 pages en total, environ 3000 gares
    nbPages = Decimal(dataSNCF_Url["pagination"]["total_result"] / dataSNCF_Url["pagination"]["items_per_page"]).quantize(Decimal('1')) #On ne veux que la parti entiere du chiffre
    resultatFinal = list()
    vide = True
    nomGareFormatter = 0
    zip = False #zip et nom servent a savoir quel type de return sera utiliser plus bas (pour savoir quel type de message afficher au final)
    nom = False

    '''
    #A ne lancer que une seul fois, il faut ensuite le mettre en commentaire
    for x in range(0, int(nbPages)+1):
        print("Telechargement de la page : "+str(x))
        jsonURLTemp = requests.get(garesUrl + str(x) , auth=(token_SNCF, ''))
        dataSNCF_UrlTemp = jsonURLTemp.json()
        with open('SNCF/data'+str(x)+'.json', 'w') as outfile:
            json.dump(dataSNCF_UrlTemp, outfile)

    return "Fichiers telecharger", goBack
    '''
    

    if(not stop_ID): #On ne rentre que si on a pas stop_ID
        #Ces boucles vont chercher le stop_areaID, necessaire pour continuer a utiliser l'API SNCF
        if(len(nomGare)==0): #Si c'est 0, l'utilisateur a rentrer un code Zip au lieu d'un nom
            zip = True
            for x in range(0, int(nbPages)+1):#Le premier for pour parcourir toutes les pages
                print("x : "+str(x))
                dataSNCF_Temp1 = open("SNCF/data"+str(x)+".json").read()
                dataSNCF_Temp = json.loads(dataSNCF_Temp1)
                if(dataSNCF_Temp["pagination"]["items_on_page"]==0):
                    break
                tempSave = len(dataSNCF_Temp["stop_areas"])
                for y in range(0, tempSave):
                    if("administrative_regions" in dataSNCF_Temp["stop_areas"][y]): #Pour les cas ou "administrative_regions" n'existe pas
                        for z in range(0,len(dataSNCF_Temp["stop_areas"][y]["administrative_regions"])):
                            if(str(zipCode) in str(dataSNCF_Temp["stop_areas"][y]["administrative_regions"][z]["zip_code"]) or "all" in zipCode.lower()): #Ca trouve quelque chose
                                vide = False
                                nomGareFormatter = dataSNCF_Temp["stop_areas"][y]["label"]+" / "+dataSNCF_Temp["stop_areas"][y]["administrative_regions"][0]["label"]
                                stop_areaID = dataSNCF_Temp["stop_areas"][y]["id"]
                                resultatFinal.append(dataSNCF_Temp["stop_areas"][y]["label"]+" / "+dataSNCF_Temp["stop_areas"][y]["administrative_regions"][0]["label"])
                                resultatFinal.append(dataSNCF_Temp["stop_areas"][y]["id"])
                                resultatFinal.append("Page : "+str(x))
                                resultatFinal.append("<br/>")
        else:
            nom = True
            for x in range(0, int(nbPages)+1):
                print("x : "+str(x))
                dataSNCF_Temp1 = open("SNCF/data"+str(x)+".json").read()
                dataSNCF_Temp = json.loads(dataSNCF_Temp1)
                if(dataSNCF_Temp["pagination"]["items_on_page"]==0):
                    break
                tempSave = len(dataSNCF_Temp["stop_areas"])
                for y in range(0, tempSave):
                    contenuSimplifier = ''.join(e for e in dataSNCF_Temp["stop_areas"][y]["label"] if e.isalnum())#Permet d'enlever les espaces et carateres speciaux
                    if(''.join(e for e in nomGare if e.isalnum()).lower() in contenuSimplifier.lower() or "all0" in nomGare.lower()): #Ca a trouver quelque chose
                        vide = False
                        if("administrative_regions" in dataSNCF_Temp["stop_areas"][y]):#Pour proteger des erreur : key not found
                            resultatFinal.append(dataSNCF_Temp["stop_areas"][y]["label"]+" / "+dataSNCF_Temp["stop_areas"][y]["administrative_regions"][0]["label"])
                            nomGareFormatter = dataSNCF_Temp["stop_areas"][y]["label"]+" / "+dataSNCF_Temp["stop_areas"][y]["administrative_regions"][0]["label"]
                            if(len(dataSNCF_Temp["stop_areas"][y]["administrative_regions"][0]["zip_code"])==0):
                                resultatFinal.append("Pas de code postal donné")
                            else:
                                resultatFinal.append("Code Postal : "+str(dataSNCF_Temp["stop_areas"][y]["administrative_regions"][0]["zip_code"]))
                        else:
                            nomGareFormatter = dataSNCF_Temp["stop_areas"][y]["label"]
                            resultatFinal.append(dataSNCF_Temp["stop_areas"][y]["label"])
                        stop_areaID = dataSNCF_Temp["stop_areas"][y]["id"]
                        resultatFinal.append(dataSNCF_Temp["stop_areas"][y]["id"])
                        resultatFinal.append("Page : "+str(x))
                        resultatFinal.append("<br/>")
    else:
        stop_areaID = stop_ID
        vide = False


    contenuGare = '<br/>'.join(map(str, resultatFinal))#Permet de convertire la list en une chaine caractere

    descriptifNomGare = "<h1 style=color:green;>Vous avez rentrer la gare suivante : " + str(nomGareFormatter) + "</h1>"
    videTextNom = "<h3 style=color:green;>Aucune gare trouver sous le nom de :  " + str(nomGare) + "</h3>"
    videTextZip = "<h3 style=color:green;>Aucune gare trouver sous le nom de :  " + str(zipCode) + "</h3>"
    saut = "<br/>"
    ambigue = "<h3 style=color:green;>Plusieurs gare trouver pour : </h3><b><h3>" +str(nomGare)+str(zipCode)+ "</h3></b><h3 style=color:green;>Veuillez rentrer un nom plus precis </h3>"
    toutAfficher = "<h3 style=color:green;>Vous avez decider de tout afficher : </h3>"

    if(nom and vide==True): #Aucun resultat, quitte le programe
        return videTextNom, goBack
    elif(zip and vide==True):
        return videTextZip, goBack
    elif("all0" in nomGare.lower() or "all" in zipCode.lower()): #Affiche tout puis quitte le programe
        return toutAfficher + saut + contenuGare, goBack
    elif(len(resultatFinal)>6): #Seulement s'il y'a plus que une gare dans la list, quitte le programe
        return ambigue + contenuGare +saut, goBack

    #Ensuite on va essayer d'afficher tous les trains qui s'en vont de la gare selectionner : https://api.sncf.com/v1/coverage/sncf/stop_areas/stop_area:OCE:SA:87686006/departures?from_datetime=20180615T111900
    urlDepartures = "https://api.sncf.com/v1/coverage/sncf/stop_areas/"+stop_areaID+"/departures?from_datetime="+dateFinal
    urlRequest = requests.get(urlDepartures, auth=(token_SNCF, ''))
    dataDepartures = urlRequest.json()
    

    if("error" in dataDepartures): #Affiche les erreur et quitte le program (S'il y'a des erreurs)
        return "Erreur : " + dataDepartures["error"]["message"], goBack

    if(len(dataDepartures["departures"])==0): #Pour le cas ou il n'y a pas de prochain train
        response.status = 505
        return 'No departing trains'

    nomGareFormatter2 = dataDepartures["departures"][0]["stop_point"]["label"]
    descriptifNomGare2 = "<h1 style=color:green;>Vous avez rentrer la gare suivante : " + str(nomGareFormatter2) + "</h1>"

    for x in range(0, len(dataDepartures["departures"])):
        depart.append("Direction : "+ dataDepartures["departures"][x]["display_informations"]["direction"])
        depart.append("Nom Train : "+ dataDepartures["departures"][x]["display_informations"]["commercial_mode"]+" " + dataDepartures["departures"][x]["display_informations"]["code"])
        depart.append("Heure de Depart : "+str(datetime.datetime.strptime(dataDepartures["departures"][x]["stop_date_time"]["departure_date_time"].replace("T", ""),'%Y%m%d%H%M%S')))
        depart.append("<br/>")

    contenuDepart = '<br/>'.join(map(str, depart))
    return descriptifNomGare2 + saut + contenuDepart, goBack
    #'''

bottle.run(bottle.app(), host='localhost', port=8080)
