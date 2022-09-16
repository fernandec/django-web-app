from django.shortcuts import render
from listings.models import Photo 
from listings.models import Repertoire
from listings.forms import YearForm
# Create your views here.

# my functions -------
from PIL import Image
from PIL.ExifTags import TAGS
from os import walk
import os
import locale
import time
from pathlib import Path
#------------------

def miniature(path_image):
    # resize and crop photo given by its path in format 500x400
    # returns the resized and cropped photo
    from PIL import Image
    import os

    with Image.open(path_image) as im:
        w = im.width
        h = im.height

        #calcul rapport de réduction en W et en H
        r_w = w/500
        r_h = h/400
        if r_w > r_h:
            r_size = (int(w//r_h), 400)
                # calcul du tuple pour le crop
            l_c = int( (r_size[0] - 500)//2) # left corner
            u = 0   # upper
            r_c = 500 + l_c  # Right corner
            l =  400 #lower
        else:
            r_size = (500, int(h // r_w) )
                # calcul du tuple pour le crop
            l_c = 0                            # left corner
            u = int( (r_size[1] - 400)//2  )   # upper
            r_c = 500                          # Right corner
            l =  400 + u                       #lower

        try:
            im_resized = im.resize( r_size )
        except:
            with open ('log_err.log','a') as log:
                log.write(path_image + '          exception in image.resize()\n')
            return None

        try:
            orientation = im._getexif()[0x112]
            if orientation == 6:
                im_resized =im_resized.rotate(-90)
            elif orientation == 8:
                im_resized =im_resized.rotate(90)
            elif orientation == 3:
                im_resized =im_resized.rotate(180)
        except :
            print("problème dans les données EXIF")

        try:
            im_crop = im_resized.crop( (l_c,  u, r_c, l)   )
        except:
            with open ('log_err.log','a') as log:
                log.write(path_image + '          exception in image.crop()\n')
            return None
    return im_crop



#----------------
def audit_db(request):
    # -*- coding: utf-8 -*- 
    # Cette fonction vérifie que les objets 'photo' de la DB ont bien une photo dans le répertoire 'mes-images' 
    # et un miniature dans le répertoire 'Mes-images_min'

    locale.setlocale(locale.LC_TIME,'')
    nb_obj = 0
    nb_min = 0
    nb_photo = 0
    photos = Photo.objects.all()
    for photo in photos:
        pa = os.path.join(photo.Path,photo.FileName)
        pa_mini= '/home/bf/projects/django-web-app/gallery/listings/static/listings' + pa.replace('Mes-images','Mes-images_min')
        ###pa_mini= pa.replace('Mes-images','Mes-images_min')

        #if  not Path.is_file(Path(pa)):
        if  not Path(pa).exists():
            # Supprimer la photo de la DB
            photo.delete()
            nb_obj += 1

            # s'il existe une miniature associée à l'objet on la supprime
            if  Path(pa_mini ).exists():
                os.remove(pa.replace('Mes-images','Mes-images_min'))
            with open ('/home/bf/projects/django-web-app/gallery/listings/static/listings/tools_for_gallery/log_audit.log', 'a', encoding='utf-8') as log:
                log.write(time.strftime('%A %d/%m/%Y %H:%M:%S') + pa + '     ' + '    photo supprimee de la db\n')
                #log.write(pa +  '    photo supprimee de la db\n')

        else:
            nb_photo += 1
            if not Path(pa_mini).exists():
                min = miniature(pa)
                min.save( pa_mini)
                nb_min += 1
                with open ('/home/bf/projects/django-web-app/gallery/listings/static/listings/tools_for_gallery/log_audit.log', 'a', encoding='utf-8') as log:
                    log.write(time.strftime('%A %d/%m/%Y %H:%M:%S') + pa_mini + '     ' + '    miniature crée\n')

    resultat = f"Path= {pa}\n Résultat de l'audit: nombre d'objet photo supprimés de la base: {nb_obj}.\n Nombre de miniatures crées: {nb_min}\nNombre total de photos:{nb_photo} "
    done = 2

    return render(request,
            'listings/gallery_admin.html',
            {'done':done, 'resultat': resultat})






"""
structure des données EXIF pour la partie GPS:
34853 GPSInfo=    {
    1: GPSLatitudeRef       'N', 
    2: GPSLatitude          (43.0, 29.0, 27.0851), 
    3: GPSLongitudeRef      'W', 
    4: GPSLongitude         (0.0, 46.0, 57.8495), 
    5: GPSAltitudeRef       0: Above sea level  1: Below sea level b'\x00', 6: 117.5, 
    6: DateGPSAltitude
    7: GPSTimeStamp         (12.0, 49.0, 26.0), 
    27:GPSProcessingMethod  b'ASCII\x00\x00\x00CELLID\x00', 
    29:GPSDateStamp         '2022:04:09'
    }

"""

def get_exif(fn, photo):
    # fonction qui renseigne l'objet 'photo'
    # à partir des données EXIF de la photo donnée par le path 'fn'
    ret = {}
    try:
        i = Image.open(fn)
        info = i._getexif()
    except:
        with open ('/home/bf/log_err.log','a') as log:
            log.write(fn + '          fichier non lisible\n') 
        return False

    if info is None:
        with open ('/home/bf/log_info.log','a') as log:
            log.write(fn + '          pas de données EXIF\n')
        return False

    for tag, value in info.items():
        decoded = TAGS.get(tag, 'void')
        if hasattr(Photo, decoded):                             # on ne mémorise que les data qui sont dans la classe Photo
            if type(value) == str and decoded[:4] == "Date" :   # si c'est une date ->changement du format de la date
                value = value[:10].replace(':', '-') + value[10:]
                if value[:4] != '0000':                         # format de date valide ?
                    setattr(photo, decoded, value)
            else :
                setattr(photo,decoded, value)

    # Traitement des données GPS
    if 34853 in info and 29 in info[34853]:
        #Get Latitude and Longitude
        lat = info[34853][2]
        lon = info[34853][4]

        #Convert to degrees
        lat=float(lat[0]+(lat[1]/60)+(lat[2]/(3600)))
        lon=float(lon[0]+(lon[1]/60)+(lon[2]/(3600)))

        #Negative if LatitudeRef:S or LongitudeRef:W
        if info[34853][1]=='S':
            lat=-lat
        if info[34853][3]=='W':
            lon=-lon
        photo.GPSLat = lat
        photo.GPSLon  = lon
        if 5 in info[34853]:
            if  info[34853][5] ==  0 :
                photo.GPSAlt = -info[34853][6]
            else:
                photo.GPSAlt =  info[34853][6]

            photo.DateGPS =  info[34853][29].replace(':', '-')
    else:
        with open ('/home/bf/log_info-gps.log','a') as log:
            log.write(fn + '          pas de données GPS\n')
    return True
# --------------------
# mémorisation des fichiers déjà migrés dans le fichier pkl_file stocké dans le répertoire source

def migrate(source,destination, destination_min):


    new_file=[]  # liste des nouveaux fihiers à engistrer dans la database
    new_rep = [] # Liste des nouveaux répertoires crées à enregistrer dans la database

    #exploration des répertoires
    from os import walk
    from shutil import copyfile
    import pickle
    import os
    if os.path.exists(source + '/' + 'pkl_file'):
        with open(source + '/' + 'pkl_file', 'rb') as file:
            listeFichier= pickle.load(file)
    else:
        listeFichier=[]

    for fich in list( walk(source) )[0][2]:  # seul les fichiers du répertoire racine nous intéressent
        p=fich.find('_')+1 # recherche du caractère "_" qui est juste avant la date
        rep = fich[p:p+4] + '-' + fich[p+4 : p+6]
        if os.path.splitext(fich)[1].lower() == '.jpg' or os.path.splitext(fich)[1].lower() == '.mp4':
            # si le fichier n'a pas déjà été transféré
            if fich not in listeFichier and not os.path.exists(destination + '/' + rep + '/' + fich):
                if not os.path.exists(destination + '/' + rep):
                    #créer le répertoire s'il n'existe pas déjà
                    os.makedirs(destination + '/' + rep)
                    os.makedirs(destination_min + '/' + rep)
                    new_rep.append(destination + '/' + rep)
                # copier le fichier
                try:
                    copyfile(source + '/' + fich, destination + '/' + rep + '/' + fich)
                    listeFichier.append(fich) #memorise les noms des fichiers copiés
                    new_file.append(destination + '/' + rep + '/' + fich)  # mémorise le fichier avec son path complet
                    # création de la minitaure:
                    min = miniature(source + '/' + fich)
                    min.save( destination_min + '/' + rep + '/' + fich)
                except :
                    with open ('/home/bf/projects/django-web-app/gallery/listings/static/listings/tools_for_gallery/log_err.log','a') as log:
                        log.write(fich + '          fichier non lisible\n')

    with open(source + '/' + 'pkl_file', 'wb') as file:
            pickle.dump(listeFichier,file)

    return new_file, new_rep
    # new_file liste des nouveaux fichiers à engistrer dans la database (avec le path complet)
    # new_rep Liste des nouveaux répertoires crées à enregistrer dans la database


#---------------------
# Cette fonction purge la database (tables Repertoire et table Photo
#  et recrée les objet Repertoire et Photo à partir du contnu du répertoire "im_root"
def db_create(request):
    import os

    # purge de la base
    Photo.objects.all().delete()
    Repertoire.objects.all().delete()


    im_root = '/var/www/Mes-images' 
    ###im_root = '/home/bf/projects/django-web-app/gallery/listings/static/listings/var/www/Mes-images'
    file_list =[]
    for tup in walk(im_root):   # tup = ( repertoire, [sous-repertoires], [fichiers] )
        rep = tup[0]
        if rep[-1] == '/':   # on enleve le dernier '/' s'il y en a un
            rep = rep[:-1]

        # Traitement des répertoires
        repertoire= Repertoire()
        repertoire.Path = rep
        repertoire.Name= rep[ rep.rfind('/')+1:] # on tronque le path pour ne garder que le nom du repertoire (pas de '/')
        if rep != im_root:
            repertoire.Parent_directory = Repertoire.objects.get(Path=rep[:rep.rfind('/')])
        repertoire.save(force_insert=True)

        # Traitement des images
        for file in  tup[2]:
            photo = Photo()
            if os.path.splitext(file)[1].lower() == '.jpg': 
                get_exif(rep + "/" + file, photo )
                photo.Path = rep
                photo.FileName = file
                #photo.repertoire= Repertoire.objects.get(Path=rep)
                photo.repertoire= repertoire
                photo.save(force_insert=True)
            elif  os.path.splitext(file)[1].lower() != '.db' and  os.path.splitext(file)[1].lower() != '.exe':
                 with open ('/home/bf/log_videos.log','a') as log:
                     log.write(rep + "/"  + file + '\n')

    request.session['step'] =  48
    request.session['nb'] = 48 
    photos = Photo.objects.order_by('Path')[: request.session.get('step')]
    return render(request,
            'listings/show_gallery.html',
            {'photos': photos })


def gallery(request):
    #photos = Photo.objects.all()
    request.session['step'] =  48
    request.session['nb'] = 48 
    photos = Photo.objects.order_by('Path')[: request.session.get('step')]
    for phot in photos:
        phot.Path = phot.Path.replace('Mes-images', 'Mes-images_min')
    return render(request,
            'listings/show_gallery.html',
            {'photos': photos })

def gallery_next(request):
    #photos = Photo.objects.all()
    i = request.session.get('nb')
    nb = i + request.session.get('step')
    if nb > len(Photo.objects.all()):
        nb = len(Photo.objects.all())
 
    request.session['nb'] = nb
    photos = Photo.objects.order_by('Path')[i:nb]
    for photo in photos:
        photo.Path = photo.Path.replace('Mes-images', 'Mes-images_min')
    return render(request,
            'listings/show_gallery.html',
            {'photos': photos })

def gallery_previous(request):
    i = request.session.get('nb')
    nb = i - request.session.get('step')
    if nb < 0 :
        nb = 0
 
    request.session['nb'] = nb
    photos = Photo.objects.order_by('Path')[nb:i]
    for photo in photos:
        photo.Path = photo.Path.replace('Mes-images', 'Mes-images_min')
    return render(request,
            'listings/show_gallery.html',
            {'photos': photos })




def gallery_detail(request,id):
    from PIL import Image
    from PIL.ExifTags import GPSTAGS

    photo = Photo.objects.get(id=id)
    # recherche des données de géolocalisation
    im = Image.open(photo.Path + '/' + photo.FileName)
    exif_table = im._getexif()

    if exif_table is not None and 34853 in exif_table and len(exif_table[34853]) >= 6 :
        gps_info={}
        for k, v in exif_table[34853].items():
            geo_tag=GPSTAGS.get(k)
            gps_info[geo_tag]=v

        #Get Latitude and Longitude
        lat=gps_info['GPSLatitude']
        lon=gps_info['GPSLongitude']

        #Convert to degrees
        lat=float(lat[0]+(lat[1]/60)+(lat[2]/(3600)))
        lon=float(lon[0]+(lon[1]/60)+(lon[2]/(3600)))

        #Negative if LatitudeRef:S or LongitudeRef:W
        if gps_info['GPSLatitudeRef']=='S':
            lat=-lat
        if gps_info['GPSLongitudeRef']=='W':
            lon=-lon
        zoom  ='18'
        fin = 'https://www.openstreetmap.org/note/new?lat=' + str(lat) + '&lon=' + str(lon)+'#map=' + zoom + '/' + str(lat) + '/' + str(lon)
    else:
        fin = None
    # fin de traitement géolocalisation

    return render(request,
            'listings/gallery_detail.html',
            {'photo': photo,'fin':fin}
            )

def gallery_year(request):

    if request.method == 'POST':

        form = YearForm(request.POST)
        if form.is_valid():
            # on recherche dans la base quel est le rang de la première image de l'année concernée
            photos = Photo.objects.order_by('Path')
            for index, photo in enumerate( photos):
                if photo.Path[20:24] == str(form.cleaned_data['year']):
                    request.session['nb'] = index + request.session['step']
                    photos = Photo.objects.order_by('Path')[index : index + request.session['step'] ]
                    for photo in photos:
                        photo.Path = photo.Path.replace('Mes-images', 'Mes-images_min')
                    return render(request,
                        'listings/show_gallery.html',
                        {'photos':photos})
    else:
        form = YearForm()
    return render(request,
            'listings/year.html',
            {'form':form})


def gallery_admin(request):
    done= 0
    return render(request,
        'listings/gallery_admin.html',
        {'done':done})

def migrate_tel_bruno(request):

    import os
    source= "/var/www/Tel-Bruno"        # répertoire des photos à migrer
    ###source= "/home/bf/projects/django-web-app/gallery/listings/static/listings/var/www/Tel-Bruno"        # répertoire des photos à migrer
    destination="/var/www/Mes-images"   # répertoire cible
    ###destination="/home/bf/projects/django-web-app/gallery/listings/static/listings/var/www/Mes-images"   # répertoire cible
    destination_min=   "/home/bf/projects/django-web-app/gallery/listings/static/listings/var/www/Mes-images_min"

    # Migration
    new_file, new_rep = migrate(source,destination, destination_min)
    # Data Base: enregistrement des nouveaux répertoires
    for rep in new_rep:
        repertoire = Repertoire()  # intancie un objet répertoire
        repertoire.Path = rep
        repertoire.Name = rep[rep.rfind('/') + 1:]
        repertoire.save(force_insert=True)

    # DataBase enregistrement des nouvelles photos
    for file in new_file:
        photo = Photo() # instancie un objet photo
        if os.path.splitext(file)[1].lower() == '.jpg'or os.path.splitext(file)[1].lower() == '.avi':
            get_exif(file, photo )
            photo.Path = file[:file.rfind('/')] 
            photo.FileName= file[file.rfind('/')+1:]
            photo.repertoire = Repertoire.objects.get(Path=photo.Path) # one to many link
            photo.save(force_insert=True)

    done = 2
    return render(request,'listings/gallery_admin.html',{'done':done})

def migrate_tel_marie(request):

    import os
    source= "/var/www/Tel-Marie"        # répertoire des photos à migrer
    ###source= "/home/bf/projects/django-web-app/gallery/listings/static/listings/var/www/Tel-Marie"
    destination="/var/www/Mes-images"   # répertoire cible
    ###destination="/home/bf/projects/django-web-app/gallery/listings/static/listings/var/www/Mes-images"
    destination_min=   "/home/bf/projects/django-web-app/gallery/listings/static/listings/var/www/Mes-images_min"

    # Migration
    new_file, new_rep = migrate(source,destination, destination_min)
    # Data Base: enregistrement des nouveaux répertoires
    for rep in new_rep:
        repertoire = Repertoire()  # intancie un objet répertoire
        repertoire.Path = rep
        repertoire.Name = rep[rep.rfind('/') + 1:]
        repertoire.save(force_insert=True)

    # DataBase enregistrement dess nouvelles photos
    for file in new_file:
        photo = Photo() # instancie un objet photo
        if os.path.splitext(file)[1].lower() == '.jpg'or os.path.splitext(file)[1].lower() == '.avi':
            get_exif( file, photo )
            photo.Path = file[:file.rfind('/')]
            photo.FileName= file[file.rfind('/')+1:]
            photo.repertoire =  Repertoire.objects.get(Path=photo.Path) # one to many link
            photo.save(force_insert=True)

    done = 1
    return render(request,'listings/gallery_admin.html',{'done':done})
