from django.db import models

# Create your models here.

class Building(models.Model):
    Major = models.IntegerField()
    Minor = models.IntegerField()
    BldgNbr = models.IntegerField()
    Address = models.CharField(max_length=200)
    main_use = models.CharField(max_length=20)
    Number_of_Stories = models.IntegerField(default=1)
    Construction_Class = models.IntegerField()
    Year_built = models.IntegerField()
    Year_remodeled = models.IntegerField()
    Heating_System = models.IntegerField()
    Elevators = models.BooleanField()
    Tax_PIN = models.IntegerField()
    No_parking_gfa = models.FloatField()
    Property_Name = models.CharField(max_length=200)
    Site_Energy_kbtu = models.FloatField()
    Electricity_kwh = models.FloatField()
    Electricity_kbtu = models.FloatField()
    Natural_Gas_kbtu = models.FloatField()
    Steam_kbtu = models.FloatField()
    site_eui = models.FloatField()

    def __str__(self):
        return self.Property_Name


class ASHRAE_target(models.Model):
    main_use = models.CharField(max_length=20)
    target = models.IntegerField()

    def __str__(self):
        return self.main_use
