from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# Create your models here.

class Registration_stu(models.Model):
    c =(
        ("AE","Architecture"),("BE","Biomedical"),("CE","Computer"),("CDDM","CDDM"),("Cvil","Cvil"),("EC","Electronics & Communication"),("IT","Information Technology")
    )
    eno = models.CharField(primary_key=True,max_length=20)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=20)
    repassword = models.CharField(max_length=20)
    branch = models.CharField(max_length=20, choices=c)
    
    def __str__(self):
        return str(self.eno)

class Alumni_Registration_stu(models.Model):
    c =(
        ("AE","Architecture"),("BE","Biomedical"),("CE","Computer"),("CDDM","CDDM"),("Cvil","Cvil"),("EC","Electronics & Communication"),("IT","Information Technology")
    )
    eno = models.CharField(primary_key=True,max_length=20)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=20)
    repassword = models.CharField(max_length=20)
    branch = models.CharField(max_length=20, choices=c)
    
    def __str__(self):
        return str(self.eno)
        
    
class MainRegistration_stu(models.Model):
    s =(
        (2020,2020),(2021,2021),(2022,2022),(2023,2023)
    )
    e =(
        (2023,2023),(2024,2024),(2025,2025),(2026,2026)
    )
    g =(
        ("Male","Male"),("Female","Female"),("Other","Other")
    )
    st=(
        ("pursuing","pursuing"),("completed","completed")
    )
    i=(
        ("yes","yes"),("no","no")
    )
    eno = models.ForeignKey("Registration_stu", on_delete=models.CASCADE,primary_key=True)
    fname=models.CharField(max_length=50)
    lname=models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/')
    email = models.EmailField(max_length=50)
    mobile= models.CharField(max_length=10)
    gender = models.CharField(max_length=10,choices=g)
    dob = models.DateField( auto_now=False, auto_now_add=False)
    location =models.CharField(max_length=20)
    bordname_10=models.CharField(max_length=20)
    percent_10 =models.IntegerField(max_length=3)
    passyear_10=models.IntegerField(max_length=4)
    bordname_12=models.CharField(max_length=20,null=True)
    percent_12 =models.CharField(max_length=20,null=True,blank=True)
    passyear_12=models.CharField(max_length=20,null=True,blank=True)
    qualification=models.CharField(max_length=20,default='Diploma')
    status=models.CharField(max_length=20,choices=st)
    start_year=models.IntegerField(max_length=4,choices=s)
    end_year=models.IntegerField(max_length=4,choices=e)
    interest=models.CharField( max_length=50,choices=i)
    
class Semester(models.Model):
    c =(
        ("Semeter_1","1st"),("Semeter_2","2nd"),("Semeter_3","3rd"),("Semeter_4","4th"),("Semeter_5","5th"),("Semeter_6","6th")
    )
    eno = models.ForeignKey("Registration_stu", on_delete=models.CASCADE,primary_key=True)
    total_block=models.BigIntegerField()
    cpi = models.DecimalField(max_digits=4, decimal_places=2)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2)
    spi1 =  models.DecimalField(max_digits=4, decimal_places=2)
    spi2 =  models.DecimalField(max_digits=4, decimal_places=2,null=True,blank=True)
    spi3 =  models.DecimalField(max_digits=4, decimal_places=2,null=True,blank=True)
    spi4 =  models.DecimalField(max_digits=4, decimal_places=2,null=True,blank=True)
    spi5 =  models.DecimalField(max_digits=4, decimal_places=2,null=True,blank=True)
    spi6 =  models.DecimalField(max_digits=4, decimal_places=2,null=True,blank=True)

    
    
    
    

class Company(models.Model):
    email_id = models.EmailField(primary_key=True ,max_length=254)
    password = models.CharField(max_length=20)
    fname= models.CharField(max_length=10)
    lname=models.CharField(max_length=10)
    mobile = models.CharField(max_length=20)
    
class Organization(models.Model):
   
    email_id = models.ForeignKey("Company", on_delete=models.CASCADE,primary_key=True)
    organization = models.CharField(max_length=50)
    description=models.CharField(max_length=250)
    logo =  models.ImageField(upload_to='logo/')
    website = models.CharField(max_length=50,null=True)
    instragram= models.CharField(max_length=50,null=True)
    linkedin= models.CharField(max_length=50,null=True)
    facebook = models.CharField(max_length=50,null=True)
    cin = models.CharField(max_length=50)
    document=models.FileField( upload_to='company/')
    
    
class Post_Vaccancy(models.Model):
    t = (
            ("Office","Office"),("Work From Home","Work From Home")
        )
    d =(
        ("1","1"),("2","2"),("3","3"),("4","4"),("5","5"),("6","6")
    )
    ds=(
        ("week","week"),("month","month")
    )
    sds=(
        ("week","week"),("month","month")
    )
    a =(
        ("Internship","Internship"),("Job","Job")
    )
   
    email_id = models.ForeignKey("Company", on_delete=models.CASCADE)
    organization = models.ForeignKey("Organization",on_delete=models.CASCADE)
    occupation = models.CharField(max_length=20,choices=a)
    profile_name = models.CharField(max_length=30)
    skill = models.CharField(max_length=250)
    type =models.CharField(max_length=30,choices=t)
    city = models.CharField(max_length=20)
    part_time = models.CharField(max_length=20,null=True)
    resposibility = models.CharField(max_length=1000)
    duration = models.CharField( max_length=50,choices=d)
    duration_scale =models.CharField(max_length=50,choices=ds)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    sduration_scale =models.CharField(max_length=50,choices=sds)
    application_deadline = models.DateField(auto_now=False, auto_now_add=False)
    availbilty = models.IntegerField()
    
class Demo(models.Model):    
    email= models.ForeignKey("Company", on_delete=models.CASCADE)
    name = models.ForeignKey("Organization",on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    presenter  = models.CharField(max_length=220)
    topic = models.CharField(max_length=230)
    location= models.CharField(max_length=250)
    contact =models.CharField(max_length=230)
    date = models.DateTimeField(auto_now=False, auto_now_add=False)
    duration = models.CharField(max_length=20,null=True)
    approved = models.BooleanField(default=False)
    disapproved = models.CharField(max_length=50,null=True,blank=True)
    
        
class JobApplication(models.Model):
    student_eno = models.ForeignKey(Registration_stu, on_delete=models.CASCADE)    
    email_id = models.ForeignKey(Company, on_delete=models.CASCADE)     
    org_name = models.CharField(max_length=50)
    profile_name =models.CharField(max_length=50)
    salary =models.CharField(max_length=50)
    

  
class Specific_Stu(models.Model):
    eno =models.CharField(max_length=50)       
    
    
class TpoRegistration(models.Model):
     c =(
        ("AE","Architecture"),("BE","Biomedical"),("CE","Computer"),("CDDM","CDDM"),("Cvil","Cvil"),("EC","Electronics & Communication"),("IT","Information Technology")
    )
     eno = models.BigIntegerField(primary_key=True,max_length=20)
     fname = models.CharField(max_length=50)
     lname = models.CharField(max_length=50)
     email = models.EmailField(max_length=50)
     password = models.CharField(max_length=20)
     repassword = models.CharField(max_length=20)
     branch = models.CharField(max_length=20, choices=c)
     
class  StudentRegistration(models.Model):
    eno_id = models.CharField(max_length=20)
    email = models.EmailField()
    approved = models.BooleanField(default=False)     

class  ApproveAlumniRegistration(models.Model):
    eno_id = models.CharField(max_length=20)
    email = models.EmailField()
    approved = models.BooleanField(default=False) 
    
class  CompnayRegistration(models.Model):
    email_id = models.EmailField()
    organization = models.CharField(max_length=50)
    description=models.CharField(max_length=250)
    logo =  models.ImageField(upload_to='logo/')
    cin = models.CharField(max_length=50)
    document=models.FileField( upload_to='company/')
    approved = models.BooleanField(default=False)         
    
    
class Alumni(models.Model):
    s =(
        (2020,2020),(2021,2021),(2022,2022),(2023,2023)
    )
    e =(
        (2023,2023),(2024,2024),(2025,2025),(2026,2026)
    )
    g =(
        ("Male","Male"),("Female","Female"),("Other","Other")
    )
    st=(
        ("pursuing","pursuing"),("completed","completed")
    )
    i=(
        ("yes","yes"),("no","no")
    ) 
    eno = models.CharField(max_length=20,primary_key=True)
    fname=models.CharField(max_length=50)
    lname=models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/')
    email = models.EmailField(max_length=50)
    mobile= models.CharField(max_length=10)
    gender = models.CharField(max_length=10,choices=g)
    dob = models.DateField( auto_now=False, auto_now_add=False)
    location =models.CharField(max_length=20)
    bordname_10=models.CharField(max_length=20)
    percent_10 =models.IntegerField(max_length=3)
    passyear_10=models.IntegerField(max_length=4)
    bordname_12=models.CharField(max_length=20,null=True)
    percent_12 =models.CharField(max_length=20,null=True,blank=True)
    passyear_12=models.CharField(max_length=20,null=True,blank=True)
    qualification=models.CharField(max_length=20,default='Diploma')
    status=models.CharField(max_length=20,choices=st)
    start_year=models.IntegerField(max_length=4,choices=s)
    end_year=models.IntegerField(max_length=4,choices=e)
    interest=models.CharField( max_length=50,choices=i) 
    graduation_year = models.IntegerField() 
  
class Main_Info_Alumni(models.Model):
    
    i=(
        ("yes","yes"),("no","no")
    ) 
    eno = models.ForeignKey("Alumni", on_delete=models.CASCADE,primary_key=True)
    placed_company=models.CharField(max_length=50,choices=i)
    company = models.CharField(max_length=50) 
    btech=models.CharField(max_length=50,choices=i)
      
  
    
class SelectedStudent(models.Model): 
   eno = models.ForeignKey("Registration_stu", on_delete=models.CASCADE)
   email_id = models.ForeignKey("Organization", on_delete=models.CASCADE)
   profile_name =models.CharField(max_length=50)
   salary =models.CharField(max_length=50)