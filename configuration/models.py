from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.
class Port(models.Model):
    portname = models.CharField(max_length=20,unique=True,blank=False)
    def __str__(self):
        return self.portname


class UART(models.Model):
    comport = models.OneToOneField(Port, blank=False, on_delete=models.CASCADE)
    baudrate = models.IntegerField(choices=((9600,"9600"), (115200,"115200")), blank=False)
    parity = models.CharField(max_length=10,choices=(("none","None"),("odd","Odd"),("even","Even")),blank=False)
    databit = models.IntegerField(choices=((5,'5'),(6,'6'),(7,'7'),(8,'8')),blank=False)
    stopbit = models.DecimalField(choices=((1.0,'1'),(1.5,'1.5'),(2.0,'2')),max_digits=4,decimal_places=1,blank=False)
    CTS = models.BooleanField()
    DTR = models.BooleanField()
    XON = models.BooleanField()
    def __str__(self):
        return self.comport.portname

    
class MqttSettings(models.Model):
    QOS_CHOICES = [
        (0, 'At most once (0)'),
        (1, 'At least once (1)'),
        (2, 'Exactly once (2)'),
    ]

    _id = models.AutoField(primary_key=True)
    server_name_alias = models.CharField(max_length=45, blank=False)
    host = models.CharField(max_length=45, blank=False)
    port = models.IntegerField(blank=False)
    username = models.CharField(max_length=45, blank=True)
    password = models.CharField(max_length=45, blank=True)
    qos = models.IntegerField(choices=QOS_CHOICES, default=0, blank=False)
    keepalive = models.IntegerField(default=60, blank=False)
    pub_topic = models.CharField(max_length=255, default='default/pub/topic', blank=False)  # added field with default
    sub_topic = models.CharField(max_length=255, default='default/sub/topic', blank=False)  # added field with default

    def save(self, *args, **kwargs):
        if not self.pk and MqttSettings.objects.exists():
            raise ValidationError("There can be only one MqttSettings instance")
        return super(MqttSettings, self).save(*args, **kwargs)

    def __str__(self):
        return self.server_name_alias

    class Meta:
        verbose_name = "Mqtt"
        verbose_name_plural = "Mqtt"

class HttpsSettings(models.Model):
    auth_token = models.CharField(max_length=100, null=True, blank=True)
    api_path = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.api_path if self.api_path else "No API Path"

    class Meta:
        verbose_name = "Https"
        verbose_name_plural = "Https"