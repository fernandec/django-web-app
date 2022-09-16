from django.db import models
class Repertoire(models.Model):
    Name= models.CharField(max_length= 50,null=True)
    Path= models.CharField(max_length = 100,null=True)
    Parent_directory=  models.ForeignKey('self', null=True, blank = True, on_delete=models.CASCADE, related_name='children')
    test= models.CharField(max_length= 50, null=True, blank = True )

class Photo(models.Model):
    FileName =          models.CharField(max_length=100)
    Path =              models.CharField(max_length=100)
    ImageWidth =        models.IntegerField(null=True)
    ImageLength =       models.IntegerField(null=True)
    DateTime =          models.DateTimeField(null=True)
    GPSLat =            models.FloatField(default=43.48883602764395)
    GPSLon =            models.FloatField(default=-1.5224230678904995)
    GPSAlt =            models.IntegerField( null = True)
    DateTimeDigitized = models.DateTimeField(null=True)
    DateTimeOriginal =  models.DateTimeField(null=True)
    DateGPS =           models.DateField(null=True)
    ExifImageWidth =    models.IntegerField(null=True)
    ExifImageHeight =   models.IntegerField(null=True)
    repertoire= models.ForeignKey(Repertoire, null=True, blank = True, on_delete=models.CASCADE)
