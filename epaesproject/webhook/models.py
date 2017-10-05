from django.db import models


class Mensajes(models.Model):
    id_msj = models.AutoField(primary_key=True)
    tipo_msj = models.ForeignKey('TiposMsj', models.DO_NOTHING, db_column='tipo_msj')
    contenido = models.CharField(max_length=200)
    orden_msj = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'mensajes'


class TiposMsj(models.Model):
    id_tipo = models.AutoField(primary_key=True)
    tipo_msj = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'tipos_msj'
