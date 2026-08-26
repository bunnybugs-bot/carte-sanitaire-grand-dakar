from django.contrib.gis.db import models


class Etablissement(models.Model):
    id = models.IntegerField(primary_key=True)
    amenity = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    quartier = models.CharField(max_length=150, blank=True, null=True)
    geom = models.PointField(srid=32628)

    class Meta:
        managed = False
        db_table = 'etablissement_sante_test'

    def __str__(self):
        return self.name or 'Établissement'


class Quartier(models.Model):
    id = models.IntegerField(primary_key=True)
    qrt_vlg_ha = models.CharField(max_length=150, blank=True, null=True, db_column='QRT_VLG_HA')
    reg = models.CharField(max_length=100, blank=True, null=True, db_column='REG')
    cav = models.CharField(max_length=100, blank=True, null=True, db_column='CAV')
    ccrca = models.CharField(max_length=100, blank=True, null=True, db_column='CCRCA')
    population = models.IntegerField(blank=True, null=True)
    geom = models.MultiPolygonField(srid=32628)

    class Meta:
        managed = False
        db_table = 'yoff'

    def __str__(self):
        return self.qrt_vlg_ha or 'Quartier'