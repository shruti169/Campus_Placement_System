from django.contrib import admin
from .models import Registration_stu,Demo,MainRegistration_stu, Main_Info_Alumni,Post_Vaccancy,SelectedStudent,Alumni,Company,Semester,Organization,StudentRegistration,Specific_Stu,TpoRegistration,JobApplication,CompnayRegistration
# Register your models here.

admin.site.register(Registration_stu)
admin.site.register(MainRegistration_stu)
admin.site.register(Company)
admin.site.register(Organization)
admin.site.register(Post_Vaccancy)
admin.site.register(TpoRegistration)
admin.site.register(JobApplication)
admin.site.register(Specific_Stu)
admin.site.register(Semester)
admin.site.register(StudentRegistration)
admin.site.register(Alumni)
admin.site.register(CompnayRegistration)
admin.site.register(SelectedStudent)
admin.site.register(Main_Info_Alumni)
admin.site.register(Demo)