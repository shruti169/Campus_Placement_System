from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from datetime import datetime
from datetime import date
import pdfkit
from django.db import connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import Http404
from django.shortcuts import render,redirect,reverse,get_object_or_404
from .models import Registration_stu,Alumni,Demo,Main_Info_Alumni,SelectedStudent,MainRegistration_stu,Semester,Organization,Post_Vaccancy,Company,JobApplication,Specific_Stu,TpoRegistration,StudentRegistration,CompnayRegistration
# Create your views here.

def home(request):
    internships = Post_Vaccancy.objects.all()
    organizations = Organization.objects.all()
    student_id = request.session.get('student_id', None)
    context = {'internships': internships, 'organizations': organizations, 'student_id': student_id}
    connection.close() 
    return render(request,'home.html',context)

def contact(request):
     return render(request,'contact.html')


def rules(request):
    return render(request,'rules.html')


#student-------------------

@never_cache
def student(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        alumni = MainRegistration_stu.objects.filter(eno=username)
        users = StudentRegistration.objects.filter(eno_id=username)
        pswd = Registration_stu.objects.filter(password=password)
        
        if users.exists() and pswd.exists() and alumni.exists():
            my_data = get_object_or_404(MainRegistration_stu, eno_id=username)
            my_data1 = get_object_or_404(Registration_stu, eno=username)
            my_data2 = get_object_or_404(Semester, eno=username)
            
            request.session['student_id'] = username
            request.session['role'] = 'student'
            context = {
                'my_data': my_data,
                'my_data2': my_data2,
                'my_data1': my_data1,
                'student_id': username,
            }
            return render(request, 'stuedntdashbord.html', context)
        
        else:
            try:
                my_data = Alumni.objects.get(eno=username)
                if pswd.exists():
                    my_data1 = get_object_or_404(Registration_stu, eno=username)
                    my_data2 = get_object_or_404(Semester, eno=username)
                    request.session['student_id'] = username
                    request.session['role'] = 'alumni'
                    
                    try:
                        my_data3 = Main_Info_Alumni.objects.get(eno=username)
                    except Main_Info_Alumni.DoesNotExist:
                        my_data3 = None

                    context = {
                        'my_data': my_data,
                        'my_data2': my_data2,
                        'my_data1': my_data1,
                        'student_id': username,
                        'my_data3': my_data3
                    }
                    return render(request, 'alumni_dashboard.html', context)
                
                else:
                    messages.error(request, 'Invalid username or password')
            
            except Alumni.DoesNotExist:
                messages.error(request, 'Invalid username or password')
    
    return render(request, 'student.html')


def registration(request):
    if request.method == "POST":
        eno = request.POST.get('eno')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        branch = request.POST.get('branch')

        # Check if eno already exists
        if Registration_stu.objects.filter(eno=eno).exists():
            error_message = "Enrollment number already exists."
            return render(request, 'registration.html', {'error_message': error_message})

        myuser = Registration_stu(eno=eno, email=email, password=password, repassword=repassword, branch=branch)
        
        try:
            myuser.full_clean()
        except ValidationError as e:
            # Handle validation error here
            pass

        myuser.save()
        print(eno)
        print('user created')

        # Registration goes to tpo

        tpo_approval_request = StudentRegistration.objects.create(
            eno_id=eno,
            email=myuser.email,
            approved=False
        )
        
        return render(request, 'registration_success.html')
    else:
        return render(request, 'registration.html')

def registration_success(request):
    return render(request,'registration_success.html')

def approve_registration(request, request_id):
    registration_request = StudentRegistration.objects.get(id=request_id)
    registration_request.approved = True
    registration_request.save()
    
     # Send the approval email
    subject = 'Registration Request Approved'
    message = 'Your registration request has been approved. Welcome!'
    from_email = 'shrutimaurya169@gmail.com'  # Replace with your email address
    to_email = registration_request.email
    
        # Render the email template
    email_template = 'approval_email.html'  # Path to your email template
    email_context = {
        'eno': registration_request.eno_id,
        'email_id' : registration_request.email,
        'registration_request': registration_request,
        'semester_link': 'http://127.0.0.1:8000/mainregistration'  # Replace with the actual URL of your semester.html page
    }
    email_html = render_to_string(email_template, email_context)
    email_text = strip_tags(email_html)
    
    # Send the email
    send_mail(subject, email_text, from_email, [to_email], html_message=email_html) 
   
    return redirect('my_dashboard')



def disapprove_registration(request, request_id):
    registration_request = get_object_or_404(StudentRegistration, id=request_id)
    registration_request.delete()
    
    student_info = get_object_or_404(Registration_stu, eno=registration_request.eno_id)
    student_info.delete()
    
    # Send the disapproval email
    subject = 'Registration Request Disapproved'
    message = 'Your registration request has been disapproved. Please contact the TPO.'
    from_email = 'shrutimaurya169@gmail.com'  # Replace with your email address
    to_email = registration_request.email

    send_mail(subject, message, from_email, [to_email])

    # Redirect to the appropriate page or display a success message
    return redirect('my_dashboard')  # Redirect to the TPO dashboard or any other desired page
    
def approval_email(request):
    return render(request,'approval_email.html')


def mainregistration(request,eno,email_id):
   if request.method == "POST" and request.FILES.get('image'):
        eno_id = request.POST.get('eno_id')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        gender = request.POST.get('gender')
        image = request.FILES['image']
        mobile = request.POST.get('mobile')
        dob = request.POST.get('dob')
        email = request.POST.get('email')
        location = request.POST.get('location')
        percent_10 = request.POST.get('percent_10')
        passyear_10 = request.POST.get('passyear_10')
        bordname_10 =request.POST.get('bordname_10')
        percent_12 = request.POST.get('percent_12')
        passyear_12 = request.POST.get('passyear_12')
        bordname_12 =request.POST.get('bordname_12')
        status = request.POST.get('status')
        start_year = request.POST.get('start_year')
        end_year = request.POST.get('end_year')
        interest =request.POST.get('interest')
        myuser = MainRegistration_stu(eno_id=eno_id, email=email, mobile=mobile,gender=gender,location=location,dob=dob,lname=lname,fname=fname,image=image,status=status,start_year=start_year,end_year=end_year,passyear_10=passyear_10,percent_10=percent_10,bordname_10=bordname_10,passyear_12=passyear_12,percent_12=percent_12,bordname_12=bordname_12,interest=interest)
        myuser.save()
        print('data stored in main_Registration table')
        
        year_of_joining = int(start_year)
        current_year = datetime.now().year
        if current_year - year_of_joining > 3:
            # Move student to the alumni table
            graduation_year = year_of_joining + 3
            alumni = Alumni(eno=eno_id, email=email, mobile=mobile,gender=gender,location=location,dob=dob,lname=lname,fname=fname,image=image,status=status,start_year=start_year,end_year=end_year,passyear_10=passyear_10,percent_10=percent_10,bordname_10=bordname_10,passyear_12=passyear_12,percent_12=percent_12,bordname_12=bordname_12,interest=interest,graduation_year=graduation_year)
            alumni.save()
            
            MainRegistration_stu.objects.filter(eno_id=eno_id).delete()
            
        my_var = myuser.eno_id
        my_var2 = myuser.email
        print(my_var2)
        print('user created')
        return render(request, 'semester.html',{'my_var':my_var}) 
   else:
        return render(request,'mainregistration.html',{'eno': eno ,'email_id': email_id})
    
    
def semester(request):
    print('call')
    if request.method == "POST":
        eno_id = request.POST.get('eno_id')
        main_registration = Registration_stu.objects.get(eno=eno_id)
        total_block = request.POST.getlist('block')
        count = len(total_block)
        cpi = request.POST.get('cpi')
        cgpa = request.POST.get('cgpa')
        spi1 = request.POST.get('spi1')
        spi2 = request.POST.get('spi2')
        if spi2 == '':
            spi2 = None
        spi3 = request.POST.get('spi3')
        if spi3 == '':
            spi3 = None
        spi4 = request.POST.get('spi4')
        if spi4 == '':
            spi4 = None
        spi5 = request.POST.get('spi5')
        if spi5 == '':
            spi5 = None
        spi6 = request.POST.get('spi6')
        if spi6 == '':
            spi6 = None
        
        semester1 = Semester(eno=main_registration, total_block=count, cgpa=cgpa, cpi=cpi, spi1=spi1, spi2=spi2, spi3=spi3, spi4=spi4, spi5=spi5, spi6=spi6)
        semester1.save()
        print('user created')
        
        return render(request, 'student.html', {'eno': eno_id})
    else:
        return render(request, 'semester.html')
    
def stuedntdashbord(request):
    return render(request, 'stuedntdashbord.html')


@never_cache
def profile(request, student_id):
    try:
        # Try to fetch data from MainRegistration_stu
        student_data = MainRegistration_stu.objects.get(eno_id=student_id)
        student_data2 = Registration_stu.objects.get(eno=student_id)
        student_data1 = Semester.objects.get(eno=student_id)
        role = request.session.get('role', None)
        print(role)
        context = {
            'student_data': student_data,
            'student_data1': student_data1,
            'student_data2': student_data2
        }
        return render(request, 'profile.html', context)
    except MainRegistration_stu.DoesNotExist:
        try:
            # Try to fetch data from Alumni
            student_data = Alumni.objects.get(eno=student_id)
            student_data2 = Registration_stu.objects.get(eno=student_id)
            student_data1 = Semester.objects.get(eno=student_id)
            student_data3 = Main_Info_Alumni.objects.get(eno=student_id)
            context = {
                'student_data': student_data,
                'student_data1': student_data1,
                'student_data2': student_data2,
                'student_data3':student_data3
            }
            return render(request, 'profile.html', context)
        except Alumni.DoesNotExist:
            raise Http404("Student data not found.")

def student_edit(request):
        try:
            student_id=request.session.get('student_id')
            print(student_id)
            role = request.session.get('role', None)
            print(role)
            student_data = MainRegistration_stu.objects.get(eno_id=student_id)
            student_data2 = Registration_stu.objects.get(eno=student_id)
            student_data1 = Semester.objects.get(eno=student_id)
            update_message = ''
            
            
            if request.method == 'POST':
                is_updated = False
               
                
                if student_data.fname != request.POST.get('fname'):
                    student_data.fname = request.POST.get('fname')
                    is_updated = True
                if student_data.lname != request.POST.get('lname'):
                    student_data.lname = request.POST.get('lname')
                    is_updated = True
                print(student_data.lname)
                if  student_data.start_year !=request.POST.get('start_year'):
                    student_data.start_year =request.POST.get('start_year')
                    is_updated = True
                print(student_data.start_year)    
                if  student_data.end_year !=request.POST.get('end_year'):
                    student_data.end_year =request.POST.get('end_year')
                    is_updated = True     
                print(student_data.end_year)
                dob = request.POST.get('dob')
                if dob:
                    try:
                        parsed_date = datetime.strptime(dob, '%Y-%m-%d').date()
                        if student_data.dob != parsed_date:
                            student_data.dob = parsed_date
                            is_updated = True
                            print(student_data.dob)
                        # Continue with further processing or save the parsed_date to the database
                    except ValueError:
                        raise ValidationError('Invalid date format. Please provide a valid date in YYYY-MM-DD format.')
                else:
                    # Handle the case where the date field is empty
                    # You can raise a validation error or handle it in a way that suits your application
                    raise ValidationError('Date field cannot be empty.')
                
                if  student_data.location !=request.POST.get('location'):
                    student_data.location =request.POST.get('location')
                    is_updated = True

                if  student_data.percent_10 !=request.POST.get('percent_10'):
                    student_data.percent_10 =request.POST.get('percent_10')
                    is_updated = True
                    print(student_data.percent_10)
                if  student_data.passyear_10 !=request.POST.get('passyear_10'):
                    student_data.passyear_10 =request.POST.get('passyear_10')
                    is_updated = True
                if   student_data.bordname_10  !=request.POST.get('bordname_10'):
                    student_data.bordname_10  =request.POST.get('bordname_10')
                    is_updated = True
                if  student_data.percent_12!= request.POST.get('percent_12'):
                    student_data.percent_12 = request.POST.get('percent_12')
                    is_updated = True
                if  student_data.passyear_12 != request.POST.get('passyear_12'):
                    student_data.passyear_12 = request.POST.get('passyear_12')
                    is_updated = True
                if  student_data.bordname_12 !=request.POST.get('bordname_12'):
                    student_data.bordname_12 =request.POST.get('bordname_12')
                    is_updated = True    
                if  student_data.status !=request.POST.get('status'):
                    student_data.status =request.POST.get('status')
                    is_updated = True    
                if  student_data.interest !=request.POST.get('interest'):
                    student_data.interest =request.POST.get('interest')
                    is_updated = True  
                if  student_data.mobile !=request.POST.get('moblie'):
                    student_data.mobile =request.POST.get('moblie')
                    is_updated = True 
                if 'image' in request.FILES:
                    if student_data.image != request.FILES['image']:
                        student_data.image = request.FILES['image']
                        is_updated = True    
                if  student_data2.branch !=request.POST.get('branch'):
                    student_data2.branch =request.POST.get('branch')
                    is_updated = True
                if  student_data1.cpi !=request.POST.get('cpi'):
                    student_data1.cpi =request.POST.get('cpi')
                    is_updated = True  
                if  student_data1.spi1 !=request.POST.get('spi1'):
                    student_data1.spi1 =request.POST.get('spi1')
                    if student_data1.spi2 == 'None':
                            student_data1.spi2 = None
                    is_updated = True  
                if  student_data1.spi2 !=request.POST.get('spi2'):
                    student_data1.spi2 =request.POST.get('spi2')
                    if student_data1.spi2 == 'None':
                            student_data1.spi2 = None
                    is_updated = True 
                if  student_data1.spi3 !=request.POST.get('spi3'):
                    student_data1.spi3 =request.POST.get('spi3')
                    if student_data1.spi3 == 'None':
                            student_data1.spi3 = None
                    is_updated = True 
                if  student_data1.spi4 !=request.POST.get('spi4'):
                    student_data1.spi4 =request.POST.get('spi4')
                    if student_data1.spi4 == 'None':
                            student_data1.spi4 = None
                    is_updated = True 
                if  student_data1.spi5 !=request.POST.get('spi5'):
                    student_data1.spi5 =request.POST.get('spi5')
                    if student_data1.spi5 == 'None':
                            student_data1.spi5 = None
                    is_updated = True 
                if  student_data1.spi6 !=request.POST.get('spi6'):
                    student_data1.spi6 =request.POST.get('spi6')
                    if student_data1.spi6 == 'None':
                            student_data1.spi6 = None
                    is_updated = True 
                
                total_block = request.POST.getlist('block')
                print(total_block)
                count = len(total_block)
                print(count)
                total_block_count = count
                print(total_block_count)           
                if student_data1.total_block != total_block_count:
                    student_data1.total_block = total_block_count
                    s = student_data1.save()
                    print(s)
                             
                if is_updated:    
                    student_data.save()
                    student_data2.save()
                    student_data1.save()
                    update_message = "Data updated successfully."
                    print('update')
                else:
                # No update message
                    update_message = ""    
            context = {
                    'student_data': student_data,
                    'student_data1': student_data1,
                    'student_data2': student_data2,
                    'update_message': update_message 
                }    
            return render(request, 'student_edit.html', context)
        except MainRegistration_stu.DoesNotExist:
            try:    
                student_data = Alumni.objects.get(eno=student_id)
                student_data2 = Registration_stu.objects.get(eno=student_id)
                student_data1 = Semester.objects.get(eno=student_id)
                my_data3 = Main_Info_Alumni.objects.get(eno=student_id)
                print(my_data3)
                update_message = ''
            
            
                if request.method == 'POST':
                    is_updated = False
                
                    
                    if student_data.fname != request.POST.get('fname'):
                        student_data.fname = request.POST.get('fname')
                        is_updated = True
                    if student_data.lname != request.POST.get('lname'):
                        student_data.lname = request.POST.get('lname')
                        is_updated = True
                        print(student_data.lname)
                    if  student_data.start_year !=request.POST.get('start_year'):
                        student_data.start_year =request.POST.get('start_year')
                        is_updated = True
                        print(student_data.start_year)    
                    if  student_data.end_year !=request.POST.get('end_year'):
                        student_data.end_year =request.POST.get('end_year')
                        is_updated = True     
                        print(student_data.end_year)
                    dob = request.POST.get('dob')
                    if dob:
                        try:
                            parsed_date = datetime.strptime(dob, '%Y-%m-%d').date()
                            if student_data.dob != parsed_date:
                                student_data.dob = parsed_date
                                is_updated = True
                                print(student_data.dob)
                            # Continue with further processing or save the parsed_date to the database
                        except ValueError:
                            raise ValidationError('Invalid date format. Please provide a valid date in YYYY-MM-DD format.')
                    else:
                        # Handle the case where the date field is empty
                        # You can raise a validation error or handle it in a way that suits your application
                        raise ValidationError('Date field cannot be empty.')
                    
                    if  student_data.location !=request.POST.get('location'):
                        student_data.location =request.POST.get('location')
                        is_updated = True

                    if  student_data.percent_10 !=request.POST.get('percent_10'):
                        student_data.percent_10 =request.POST.get('percent_10')
                        is_updated = True
                        print(student_data.percent_10)
                    if  student_data.passyear_10 !=request.POST.get('passyear_10'):
                        student_data.passyear_10 =request.POST.get('passyear_10')
                        is_updated = True
                    if   student_data.bordname_10  !=request.POST.get('bordname_10'):
                        student_data.bordname_10  =request.POST.get('bordname_10')
                        is_updated = True
                    if  student_data.percent_12!= request.POST.get('percent_12'):
                        student_data.percent_12 = request.POST.get('percent_12')
                        is_updated = True
                    if  student_data.passyear_12 != request.POST.get('passyear_12'):
                        student_data.passyear_12 = request.POST.get('passyear_12')
                        is_updated = True
                    if  student_data.bordname_12 !=request.POST.get('bordname_12'):
                        student_data.bordname_12 =request.POST.get('bordname_12')
                        is_updated = True    
                    if  student_data.status !=request.POST.get('status'):
                        student_data.status =request.POST.get('status')
                        is_updated = True    
                    if  student_data.interest !=request.POST.get('interest'):
                        student_data.interest =request.POST.get('interest')
                        is_updated = True  
                    if  student_data.mobile !=request.POST.get('moblie'):
                        student_data.mobile =request.POST.get('moblie')
                        is_updated = True 
                    if 'image' in request.FILES:
                        if student_data.image != request.FILES['image']:
                            student_data.image = request.FILES['image']
                            is_updated = True    
                    if  student_data2.branch !=request.POST.get('branch'):
                        student_data2.branch =request.POST.get('branch')
                        is_updated = True
                    if  student_data1.cpi !=request.POST.get('cpi'):
                        student_data1.cpi =request.POST.get('cpi')
                        is_updated = True  
                    if  student_data1.spi1 !=request.POST.get('spi1'):
                        student_data1.spi1 =request.POST.get('spi1')
                        is_updated = True  
                    if  student_data1.spi2 !=request.POST.get('spi2'):
                        student_data1.spi2 =request.POST.get('spi2')
                        if student_data1.spi2 == 'None':
                            student_data1.spi2 = None
                        is_updated = True 
                    if  student_data1.spi3 !=request.POST.get('spi3'):
                        student_data1.spi3 =request.POST.get('spi3')
                        if student_data1.spi3 == 'None':
                            student_data1.spi3 = None
                        is_updated = True 
                    if  student_data1.spi4 !=request.POST.get('spi4'):
                        student_data1.spi4 =request.POST.get('spi4')
                        if student_data1.spi4 == 'None':
                            student_data1.spi4 = None
                        is_updated = True 
                    if  student_data1.spi5 !=request.POST.get('spi5'):
                        student_data1.spi5 =request.POST.get('spi5')
                        if student_data1.spi5 == 'None':
                            student_data1.spi5 = None
                        is_updated = True 
                    if  student_data1.spi6 !=request.POST.get('spi6'):
                        student_data1.spi6 =request.POST.get('spi6')
                        if student_data1.spi6 == 'None':
                            student_data1.spi6 = None
                        is_updated = True 
                    
                    total_block = request.POST.getlist('block')
                    print(total_block)
                    count = len(total_block)
                    print(count)
                    total_block_count = count
                    print(total_block_count)           
                    if student_data1.total_block != total_block_count:
                        student_data1.total_block = total_block_count
                        s = student_data1.save()
                        print(s)
                                
                    if is_updated:    
                        student_data.save()
                        student_data2.save()
                        student_data1.save()
                        update_message = "Data updated successfully."
                        print('update')
                    else:
                    # No update message
                        update_message = ""
                
                
                context = {
                    'student_data': student_data,
                    'student_data1': student_data1,
                    'student_data2': student_data2,
                    'my_data3': my_data3,
                    'update_message': update_message
                }
                return render(request, 'student_edit.html', context)
            except Alumni.DoesNotExist:
                raise Http404("Student data not found.")    
 
 
def listjob(request):
    internships = Post_Vaccancy.objects.all()
    organizations = Organization.objects.all()
    student_id = request.session.get('student_id', None)
    context = {'internships': internships, 'organizations': organizations, 'student_id': student_id}
    return render(request, 'listjob.html', context)

def detailsjob(request,email_id,profile_name):
    organizations = Organization.objects.get(email_id=email_id)
    internships = Post_Vaccancy.objects.get(email_id=email_id,profile_name=profile_name)
    student_id = request.session.get('student_id', None)
    context = {'internships': internships, 'organizations': organizations,'student_id':student_id}
    return render(request,'detailsjob.html', context) 

def applied_student(request):
    role = request.session.get('role', None)
    print(role)
    student_id = request.session.get('student_id', None)
    print(student_id)
    name= JobApplication.objects.filter(student_eno=student_id)
    context = {'name': name,'student_id':student_id,'role':role}
    return render(request, 'applied_jobs.html',context)


def slogout(request):
    del request.session['student_id']
    return redirect('student')

def alumni_dashboard(request):
    if request.method == "POST":
        eno_id = request.POST.get('eno_id')
        placed_company=request.POST.get('doing')
        company=request.POST.get('company')
        btech=request.POST.get('pursing')
        myuser = Main_Info_Alumni(eno_id=eno_id,placed_company= placed_company,company=company,btech=btech)
        myuser.save()
        print('data stored in main_Registration table')
        my_data = request.session.get('student_id', None)
        print(my_data)
        my_data1 = get_object_or_404(Registration_stu, eno=my_data)
        my_data2 = get_object_or_404(Semester, eno=my_data)
        context = {
                        'my_data': my_data,
                        'my_data2': my_data2,
                        'my_data1': my_data1,
                    }
        profile_url = reverse('profile', args=[my_data])
        messages.success(request, 'Data updated successfully!')
        return redirect(profile_url)
    else:
        my_data = request.session.get('student_id', None)
        print(my_data)
        my_data1 = get_object_or_404(Registration_stu, eno=my_data)
        print(my_data1)
        my_data2 = get_object_or_404(Semester, eno=my_data)
        print(my_data2)
        context = {
                        'my_data': my_data,
                        'my_data2': my_data2,
                        'my_data1': my_data1,
                    }
        return render(request, 'alumni_dashboard.html', context)
    
@never_cache
def companylogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        users = CompnayRegistration.objects.filter(email_id=username)
        print(users)
        pswd = Company.objects.filter(password=password)
        print(pswd)
        if users.exists() and pswd.exists():
            my_data = get_object_or_404(Company,email_id=username)
            request.session['email_id'] = username
            request.session['role'] = 'company'
            context ={
                'my_data':my_data,
                'email_id': username
            }
            return render(request, 'companydash.html',context)
        else:
            messages.error(request, 'Invalid username or password')
            
    return render(request, 'companylogin.html', {'messages': messages.get_messages(request)})
        
def companyRegi(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        fname = request.POST.get('fname')
        lname =request.POST.get('lname')
        mobile = request.POST.get('mobile')
        myuser = Company(email_id=email, password=password,fname=fname,lname=lname,mobile=mobile)
        myuser.save()
        my_var = myuser.email_id
        print('user created')
        
        #registration goes to tpo  
        return render(request,'companyReg2.html',{'my_var':my_var})   
    else:
        return render(request,'companyRegi.html')
    
    
def companyReg2(request):
    if request.method == "POST":
        email = request.POST.get('email')
        company = Company.objects.get(email_id=email)
        organization = request.POST.get('organization')
        description = request.POST.get('description')
        logo = request.FILES['image']
        website =request.POST.get('website')
        instragram = request.POST.get('instragram')
        linkedin = request.POST.get('linkedin')
        facebook =request.POST.get('facebook')
        cin= request.POST.get('cin')
        document=request.FILES['document']
        myuser = Organization(email_id=company,organization=organization, description=description,logo=logo,website=website,instragram=instragram,linkedin=linkedin,facebook=facebook,cin=cin,document=document)
        myuser.save()
        my_var = myuser.email_id.email_id
        context ={
            'my_var':my_var 
        }
        print('user created')
        
        tpo_approval_request = CompnayRegistration.objects.create(
        email_id=my_var,
        organization=myuser.organization,
        description=myuser.description,
        logo=myuser.logo,
        cin=myuser.cin,
        document=myuser.document,
        approved=False
        )
        return render(request, 'registration_success.html')
    else :
        return render(request,'companyReg2.html',context)
def internshipjob(request,email_id,name):
    if request.method == "POST":
        email = request.POST.get('email')
        c = Company.objects.get(email_id=email)
        name =request.POST.get('name')
        o = Organization.objects.get(organization=name)
        a= request.POST.get('occupation')
        profile = request.POST.get('profile')
        skill = request.POST.get('skill')
        status =request.POST.get('status')
        location = request.POST.get('location')
        responsbility =request.POST.get('responsibility')
        parttime = request.POST.get('part_time')
        duration = request.POST.get('duration')
        duration_scale = request.POST.get('duration_scale')
        sduration_scale = request.POST.get('sduration_scale')
        salary = request.POST.get('salary')
        application_deadline = request.POST.get('ad')
        availbilty = request.POST.get('availbilty')
        myuser = Post_Vaccancy(email_id=c,organization=o,occupation=a, profile_name=profile,skill=skill,type=status,city= location,application_deadline=application_deadline,availbilty=availbilty,resposibility=responsbility,part_time=parttime,duration=duration,duration_scale=duration_scale,sduration_scale=sduration_scale,salary=salary)
        myuser.save()
        my_var = myuser.email_id
        print('user created')
        return render(request,'companylogin.html',{'my_var':my_var})
    else:
        return render(request,'internshipjob.html',{'email_id':email_id,'name':name}) 

def demo(request):
    email = request.session.get('email_id', None)
    company = Organization.objects.get(email_id=email)
    context ={
        'email':email,
        'company':company
    }
    if request.method == "POST":
        email_id = request.POST.get('email')
        c = Company.objects.get(email_id=email_id)
        name = request.POST.get('name')
        n= Organization.objects.get(organization=name)
        title = request.POST.get('title')
        description = request.POST.get('description')
        presenter = request.POST.get('presenter')
        topic= request.POST.get('topic')
        location= request.POST.get('location')
        number= request.POST.get('number')
        date= request.POST.get('date')
        duration= request.POST.get('duration')
        myuser = Demo(email=c, name=n, title=title, description=description,presenter=presenter,topic=topic,location=location,contact=number,duration=duration,date=date)
        myuser.save()
        messages.success(request, 'Demo Lecture Posted successfully!')
        return render(request, 'demo.html',context) 
    else:
        return render(request, 'demo.html',context)    

def postjob(request,email_id,name):
    if request.method == "POST":
        email = request.POST.get('email')
        c = Company.objects.get(email_id=email)
        name =request.POST.get('name')
        o = Organization.objects.get(organization=name)
        a= request.POST.get('occupation')
        profile = request.POST.get('profile')
        skill = request.POST.get('skill')
        status =request.POST.get('status')
        location = request.POST.get('location')
        responsbility =request.POST.get('responsibility')
        parttime = request.POST.get('part_time')
        duration = request.POST.get('duration')
        duration_scale = request.POST.get('duration_scale')
        sduration_scale = request.POST.get('sduration_scale')
        salary = request.POST.get('salary')
        application_deadline = request.POST.get('ad')
        availbilty = request.POST.get('availbilty')
        myuser = Post_Vaccancy(email_id=c,organization=o,occupation=a, profile_name=profile,skill=skill,type=status,city= location,application_deadline=application_deadline,availbilty=availbilty,resposibility=responsbility,part_time=parttime,duration=duration,duration_scale=duration_scale,sduration_scale=sduration_scale,salary=salary)
        myuser.save()
        my_var = myuser.email_id
        print('user created')
        return redirect('companypost')
    else:
        return render(request,'postjob.html',{'email_id':email_id,'name':name})




def edit_company(request):
    email=request.session.get('email_id')
    print(email)
    my_data = get_object_or_404(Company,email_id=email)
    print(my_data)
    fname=my_data.fname
    print(fname)
    update_message = ""   
    if request.method == "POST":
        is_updated = False
        if my_data.fname != request.POST.get('fname'):
            my_data.fname = request.POST.get('fname')
            is_updated = True
            
        if my_data.lname != request.POST.get('lname'):
            my_data.lname = request.POST.get('lname')
            is_updated = True
        if my_data.mobile != request.POST.get('mobile'):
            my_data.mobile = request.POST.get('mobile')
            is_updated = True 
            
        if is_updated:    
            my_data.save()  
            update_message = "Data updated successfully." 
               
        context = {
                    'my_data': my_data,
                    'update_message': update_message 
                }      
        return render(request,'companydash.html',context)
    else:
        context = {
                    'my_data': my_data,
                } 
        return render(request,'edit_company.html',context)
    


@never_cache
def companydash(request):
    email_id = request.session.get('email_id', None)
    my_data = get_object_or_404(Company,email_id= email_id)
    context ={
                'my_data':my_data
            }
    return render(request,'companydash.html',context)
    

def companypost(request):
    email_id = request.session.get('email_id')
    print(email_id)
    # Call the delete_expired_posts function here
    job_post = Post_Vaccancy.objects.filter(email_id_id=email_id)
    demo_lecture = Demo.objects.filter(email=email_id)
    print(job_post)
    if job_post:
        # The user has already posted an internship, so display the details
        company = Company.objects.get(email_id=email_id)
        organizations = Organization.objects.get(email_id=email_id)
        context = {'job_post': job_post, 'organizations': organizations,'company':company,'demo_lecture':demo_lecture}
        delete_expired_posts(request)
        return render(request, 'companypost.html', context)
    else :
        company = Company.objects.get(email_id=email_id)
        organizations = Organization.objects.get(email_id=email_id)
        context = {'job_post': job_post, 'organizations': organizations,'company':company,'demo_lecture':demo_lecture}
        return render(request, 'companypost.html', context)    


def applied(request):
    email_id = request.session.get('email_id', None)
    print(email_id)
    stu_applied = JobApplication.objects.filter(email_id_id=email_id).select_related('student_eno')
    print(stu_applied)
    success_message = request.GET.get('success')
    context={'stu_applied':stu_applied,'email_id':email_id,'success_message': success_message }
    return render(request,'applied.html',context)


def student_details(request,student_eno,email_id):
    print(student_eno)
    student_data2 = get_object_or_404(Registration_stu,eno=student_eno)
    email =email_id
    student_data = get_object_or_404(MainRegistration_stu, eno_id=student_eno)
    student_data1 = get_object_or_404(Semester,eno=student_eno)
    context = {
        'student_data': student_data,
        'student_data1':  student_data1,
        'student_data2':student_data2,
        'email':email
    }
    return render(request,'student_details.html', context)


def send_interview_email(request):
    if request.method == 'POST':
        to_email = request.POST.get('email')
        subject = request.POST.get('subject')
        from_student =request.POST.get('fromEmail')
        email_body = request.POST.get('emailBody')
        print(to_email)
        print(from_student)
        print(email_body)
        try:
            mail=send_mail(subject , email_body,from_student, [to_email])
            print(mail)
            
            # Reset the EMAIL_HOST_USER to the original value
            
            # Email sent successfully
            success_message = "Email sent successfully!"
            
            student_eno = request.POST.get('student_eno')
            student_data2 = get_object_or_404(Registration_stu, eno=student_eno)
            student_data = get_object_or_404(MainRegistration_stu, eno_id=student_eno)
            student_data1 = get_object_or_404(Semester, eno=student_eno)

            context = {
                'success_message': success_message,
                'student_data': student_data,
                'student_data1': student_data1,
                'student_data2': student_data2,
            }
            return render(request, 'student_details.html',context)

        except Exception as e:
            # Error sending email
            error_message = "An error occurred while sending the email. Please try again later."
            return render(request, 'student_details.html', {'error_message': error_message})

    # Handle GET requests or render the form again for validation errors
    return render(request, 'student_details.html')


def selected_student(request):
    if request.method == "POST":
        eno_id = request.POST.get('eno_id')
        profile = request.POST.get('profile')
        salary = request.POST.get('salary')
        to_email = request.POST.get('toEmail')
        subject = request.POST.get('subject')
        email_body = request.POST.get('emailBody')

        main_registration = Registration_stu.objects.get(eno=eno_id)
        from_email = 'shrutimaurya169@gmail.com'

        mail = send_mail(subject, email_body, from_email, [to_email])

        email = request.session.get('email_id', None)
        company = Organization.objects.get(email_id=email)

        myuser = SelectedStudent(eno=main_registration, email_id=company, profile_name=profile, salary=salary)
        myuser.save()
        
        JobApplication.objects.filter(student_eno=main_registration, profile_name=profile).delete()

        print('email is send ')
        # Set a success flag in the URL redirect
        success_url = reverse('applied') + '?success=true'
        return redirect(success_url)
    else:
        # Fetch the necessary data for displaying in the template
        email = request.session.get('email_id', None)
        stu_applied = JobApplication.objects.filter(email_id_id=email).select_related('student_eno')

        context = {
            'stu_applied': stu_applied,
            'success_message': request.GET.get('success')
        }
        return render(request, 'applied.html', context)
    

def get_candidate(request):
    selected_students = SelectedStudent.objects.all().select_related('eno','email_id')
    role = request.session.get('role', None)
    print(role)
    context = {'selected_students': selected_students}
    return render(request, 'selected_candidate.html',context) 


def tpodasboard(request):
    return render(request,'tpodasboard.html')

def retrieve_computer_students(request):
    selected_students = SelectedStudent.objects.all()
    print(selected_students)
    eno_list = selected_students.values_list('eno', flat=True)
    print(eno_list)
    computer_students = Registration_stu.objects.filter(branch='CE', eno=eno_list[:1])
    print(computer_students)
    selected = SelectedStudent.objects.all().select_related('email_id')
    print('werfgh',selected)
    context ={'computer_students':computer_students,'selected_students':selected_students,'selected':selected}
    return render(request,'retrieve_computer_students.html',context)    

def retrieve_IT_students(request):
    selected_students = SelectedStudent.objects.all()
    print(selected_students)
    eno_list = selected_students.values_list('eno', flat=True)
    print(eno_list)
    computer_students = Registration_stu.objects.filter(branch='IT', eno=eno_list[:1])
    print(computer_students)
    selected = SelectedStudent.objects.all().select_related('email_id')
    print('werfgh',selected)
    context ={'computer_students':computer_students,'selected_students':selected_students,'selected':selected}
    return render(request,'retrieve_computer_students.html',context)    

def retrieve_EC_students(request):
    selected_students = SelectedStudent.objects.all()
    print(selected_students)
    eno_list = selected_students.values_list('eno', flat=True)
    print(eno_list)
    computer_students = Registration_stu.objects.filter(branch='EC', eno=eno_list[:1])
    print(computer_students)
    selected = SelectedStudent.objects.all().select_related('email_id')
    print('werfgh',selected)
    context ={'computer_students':computer_students,'selected_students':selected_students,'selected':selected}
    return render(request,'retrieve_computer_students.html',context)    

def retrieve_Cvil_students(request):
    selected_students = SelectedStudent.objects.all()
    print(selected_students)
    eno_list = selected_students.values_list('eno', flat=True)
    print(eno_list)
    computer_students = Registration_stu.objects.filter(branch='cvil', eno=eno_list[:1])
    print(computer_students)
    selected = SelectedStudent.objects.all().select_related('email_id')
    print('werfgh',selected)
    context ={'computer_students':computer_students,'selected_students':selected_students,'selected':selected}
    return render(request,'retrieve_computer_students.html',context)    

def retrieve_CDDM_students(request):
    selected_students = SelectedStudent.objects.all()
    print(selected_students)
    eno_list = selected_students.values_list('eno', flat=True)
    print(eno_list)
    computer_students = Registration_stu.objects.filter(branch='CDDM', eno=eno_list[:1])
    print(computer_students)
    selected = SelectedStudent.objects.all().select_related('email_id')
    print('werfgh',selected)
    context ={'computer_students':computer_students,'selected_students':selected_students,'selected':selected}
    return render(request,'retrieve_computer_students.html',context)    

def retrieve_Architecture_students(request):
    selected_students = SelectedStudent.objects.all()
    print(selected_students)
    eno_list = selected_students.values_list('eno', flat=True)
    print(eno_list)
    computer_students = Registration_stu.objects.filter(branch='AE', eno=eno_list[:1])
    print(computer_students)
    selected = SelectedStudent.objects.all().select_related('email_id')
    print('werfgh',selected)
    context ={'computer_students':computer_students,'selected_students':selected_students,'selected':selected}
    return render(request,'retrieve_computer_students.html',context)   

def retrieve_Biomedical_students(request):
    selected_students = SelectedStudent.objects.all()
    print(selected_students)
    eno_list = selected_students.values_list('eno', flat=True)
    print(eno_list)
    computer_students = Registration_stu.objects.filter(branch='CE', eno=eno_list[:1])
    print(computer_students)
    selected = SelectedStudent.objects.all().select_related('email_id')
    print('werfgh',selected)
    context ={'computer_students':computer_students,'selected_students':selected_students,'selected':selected}
    return render(request,'retrieve_computer_students.html',context)    

def selected_total_student(request):
    selected_students = SelectedStudent.objects.filter(email_id__organization='Wipro')
    total_students = selected_students.count()
    context = {
        'selected_students': selected_students,
        'total_students': total_students
    }
    return render(request,'home.html',context)



def tprofile(request,eno):
    my_data = get_object_or_404(TpoRegistration,eno=eno)
    
    context = {
        'my_data': my_data,
    }
    return render(request,'tprofile.html',context)

def tstudent(request):
    my_data = request.session.get('tpo_id', None)
    context ={
         'my_data': my_data,
    }
    return render(request,'tstudent.html',context)

def sem_display(request,eno_id):
    my_data = get_object_or_404(Registration_stu, eno=eno_id)
    results = Semester.objects.filter(student_id=my_data.id)
    sem = Semester.objects.get(eno=eno_id)
    context = {'sem': sem}
    return render(request,'sem_display.html', context)


 

def clogout(request):
    del request.session['email_id']
    return redirect('companylogin')




def tpologin(request): 
    print("call")
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(username) 
        users = TpoRegistration.objects.filter(eno=username,password=password)
        print(username) 
        if users.exists():
            my_data = get_object_or_404(TpoRegistration,eno=username)
            request.session['role'] = 'tpo'
            request.session['tpo_id'] = username
            context ={
                'my_data':my_data,
            }
            return render(request, 'tpodasboard.html',context)
        else:
            messages.error(request, 'Invalid username or password')
            
    return render(request, 'tpologin.html', {'messages': messages.get_messages(request)})

def tlogout(request):
    del request.session['tpo_id']
    return redirect('tpologin')
      
def tpoRegistration(request):
    if request.method == "POST":
            eno = request.POST.get('eno')
            email = request.POST.get('email')
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            password = request.POST.get('password')
            repassword = request.POST.get('repassword')
            branch =request.POST.get('branch')
            print(fname)
            myuser = TpoRegistration(eno=eno, email=email,fname=fname,lname=lname,password=password,repassword=repassword,branch=branch)
            try:
                    myuser.full_clean()
            except ValidationError as e:
                 # Handle validation error here
                pass        
            myuser.save()
            my_var = myuser.eno
            my_name = myuser.fname
            print(my_name)
            context ={
                'my_var':my_var,
                'my_name':my_name
            }
            print(my_var)
            print('user created')
            return render(request, 'tpologin.html',context) 
    else :
           return render(request,'tpoRegistration.html')   



def  tappliedStudent(request):
    my_data=request.session.get('tpo_id',None)
    eno= JobApplication.objects.all()
    print(eno)
    context = {'eno': eno,'my_data':my_data}
     # display job applications for a specific job
    return render(request,'tappliedStudent.html',context)

def appliedAlumni(request):
    my_data=request.session.get('tpo_id',None)
    # Retrieve all alumni IDs from the Alumni table
    alumni_eno = list(Alumni.objects.values_list('eno', flat=True))
    # Convert the alumni_eno list from strings to integers
    alumni_eno = [int(eno) for eno in alumni_eno]
    
    # Filter the JobApplications table to get the applications of the alumni
    eno = JobApplication.objects.filter(student_eno_id__in=alumni_eno)
    
    if eno.exists():
        print(eno)
        context = {'eno': eno,'my_data':my_data}
        return render(request, 'appliedAlumni.html', context)
    else:
        error_msg = "No job applications found for alumni."
        context = {'error_msg': error_msg,'my_data':my_data}
        return render(request, 'appliedAlumni.html', context)




def registerStudent(request):
    eno= MainRegistration_stu.objects.all()
    role = request.session.get('role', None)
    my_data = request.session.get('tpo_id', None)
    print(eno)
    print(my_data)
    context = {'eno': eno,
               'my_data': my_data,
               'role':role}   
    return render(request,'registerStudent.html',context)    

def talumni(request):
    my_data = request.session.get('tpo_id', None)
    context ={
         'my_data': my_data,
    }
    return render(request,'talumni.html',context)

def RegisterAlumni(request):
    alumni_data = Alumni.objects.all()
    my_data = request.session.get('tpo_id', None)
    context = {'alumni_data': alumni_data,'my_data':my_data}
    return render(request, 'RegisterAlumni.html', context)


def tcompany(request): 
    my_data = request.session.get('tpo_id', None)
    context = {'my_data': my_data}   
    return render(request,'tcompany.html',context)    

def registerCompany(request):
    email= Company.objects.all()
    organizations = Organization.objects.all()
    internships = Post_Vaccancy.objects.all()
    print(internships.count())
    print('-------------------')
    my_data = request.session.get('tpo_id', None)
    print(email)
    context = {'email': email,'organizations':organizations,'internships': internships,'my_data': my_data}   
    return render(request,'registerCompany.html',context)    

def cregistration_profile(request,email_id):
    my_data = request.session.get('tpo_id',None)
    email= Company.objects.get(email_id=email_id)
    print(email)
    organizations =Organization.objects.get(email_id=email_id)
    context={'email':email,'organizations':organizations,'my_data':my_data}
    return render(request,'cregistration_profile.html',context)

def sregistration_profile(request,eno):
    student=Registration_stu.objects.get(eno=eno)
    print(student)
    context={'student':student,}
    return render(request,'sregistration_profile.html',context)

def delete_expired_posts(request):
    today = date.today()
    expired_posts = Post_Vaccancy.objects.filter(application_deadline__lt=today)
    deleted_posts_count = expired_posts.count()
    expired_posts.delete()
    print(f"{deleted_posts_count} posts deleted.")
    message = f"{deleted_posts_count} posts deleted."
    email_id = request.session.get('email_id')
    print(email_id)
    # Call the delete_expired_posts function here
    job_post = Post_Vaccancy.objects.filter(email_id_id=email_id)
    print(job_post)
    if job_post:
        # The user has already posted an internship, so display the details
        company = Company.objects.get(email_id=email_id)
        organizations = Organization.objects.get(email_id=email_id)
        context = {'job_post': job_post, 'organizations': organizations,'company':company,'message': message,'email_id':email_id}
    return render(request, 'companypost.html',context)


  
    
def display_data(request):
  if request.method=="GET":  
    param1 = request.GET.get('my_var')
    print(param1)
    # Retrieve the data from the session variable
    return render(request, 'mainregistration.html', {'my_var':  param1})
  else :
      param1 = request.GET.get('my_var')
      return render(request, 'mainregistration.html', {' my_var ':  param1})



def company_email_approval(request):
    return render(request,'company_email_approval.html')




def requestCompany (request):
    my_data=request.session.get('tpo_id',None)
    registration_requests = CompnayRegistration.objects.all()
    context ={
        'registration_requests': registration_requests,
        'my_data':my_data
    }
    return render(request, 'requestCompany.html',context)


def approve_Company(request, request_id):
    registration_request = CompnayRegistration.objects.get(id=request_id)
    name = Organization.objects.get(email_id=registration_request.email_id)
    registration_request.approved = True
    registration_request.save()
    print(name.organization)
     # Send the approval email
    subject = 'Registration Request Approved'
    message = 'Your registration request has been approved. Welcome!'
    from_email = 'shrutimaurya169@gmail.com'  # Replace with your email address
    to_email = registration_request.email_id
    
        # Render the email template
    email_template = 'company_email_approval.html'  # Path to your email template
    email_context = {
        'email_id' : registration_request.email_id,
        'name' : name.organization,
        'registration_request': registration_request,
        'semester_link': 'http://127.0.0.1:8000/internshipjob'  # Replace with the actual URL of your semester.html page
    }
    email_html = render_to_string(email_template, email_context)
    email_text = strip_tags(email_html)
    
    # Send the email
    send_mail(subject, email_text, from_email, [to_email], html_message=email_html) 
    messages.success(request, 'Approval email sent successfully.')
    return redirect('requestCompany')



def disapprove_Company(request, request_id):
    registration_request = get_object_or_404(CompnayRegistration, id=request_id)
    registration_request.delete()
    
    student_info = get_object_or_404(Company, email_id=registration_request.email_id)
    student_info.delete()
    
    # Send the disapproval email
    subject = 'Registration Request Disapproved'
    message = 'Your registration request has been disapproved. Please contact the TPO.'
    from_email = 'shrutimaurya169@gmail.com'  # Replace with your email address
    to_email = registration_request.email_id

    send_mail(subject, message, from_email, [to_email])

    # Redirect to the appropriate page or display a success message
    return redirect('requestCompany')  # Redirect to the TPO dashboard or any other desired page




def my_dashboard(request):
    registration_requests = StudentRegistration.objects.all()
    print(registration_requests)
    my_data = request.session.get('tpo_id', None)
    context ={
        'registration_requests': registration_requests,
        'my_data':my_data
    }
    return render(request, 'my_dashboard.html',context)
  
def prefrences(request):
    return render(request,'prefrences.html')










def details(request,email_id,profile_name):
    my_data = request.session.get('tpo_id', None)
    organizations = Organization.objects.get(email_id=email_id)
    internships = Post_Vaccancy.objects.get(email_id=email_id,profile_name=profile_name)
    student_id = request.session.get('student_id', None)
    context = {'internships': internships, 'organizations': organizations,'student_id':student_id,'my_data':my_data}
    return render(request,'details.html', context)

def details_demo(request,email_id,title):
    my_data = request.session.get('tpo_id', None)
    organizations = Organization.objects.get(email_id=email_id)
    internships = Demo.objects.get(email_id=email_id,title=title)
    student_id = request.session.get('student_id', None)
    context = {'internships': internships, 'organizations': organizations,'student_id':student_id,'my_data':my_data}
    return render(request,'details_demo.html', context)


       
    
def jobApplication(request):
    student_id = request.session.get('student_id', None)
    if request.method == "POST":
        eno =request.POST.get('eno')
        print(eno) 
        student = Registration_stu.objects.get(eno=eno) 
        print(student)
        email = request.POST.get('email')
        company = Company.objects.get(email_id=email)
        print('---------------------------------------------')
        print(company)
        org_name =request.POST.get('org_name')
        profile =request.POST.get('profile')
        salary =request.POST.get('salary')
        has_applied = JobApplication.objects.filter(student_eno=student, email_id =company,profile_name=profile).exists()
        print(has_applied)
        if has_applied:
        # User has already applied for this job, show an error message
            organizations = Organization.objects.get(email_id=email)
            internships = Post_Vaccancy.objects.get(email_id=email,profile_name=profile)
           
            messages.error(request, 'You have already applied for this job')
            context ={'internships': internships, 'organizations': organizations,'student_id':student_id}
            return render(request, 'detailsjob.html',context)
        else: 
            myuser =JobApplication(student_eno=student ,email_id=company,org_name=org_name,profile_name=profile,salary=salary)
            myuser.save()
            print(eno)
            my_var = myuser.email_id
            context={
                'my_var':my_var,
                'student_id':student_id
            }
            messages.success(request, 'You have successfully applied for this job')
            return redirect('listjob')
    else :
        return render(request,'detailsjob.html',student_id)





   
# database 

def get_demo(request):
    demo = Demo.objects.all().select_related('name').order_by('id')
    my_data = request.session.get('tpo_id', None)
    print(demo)

    context={
        'demo':demo,'my_data':my_data }
    return render(request, 'get_demo.html',context)


def rusume(request):
    return render(request, 'rusume.html')    

def approve_demo(request, email_id, title):
    # Retrieve the approved demo lecture
    demo_lecture = Demo.objects.get(email_id=email_id, title=title)
    name =Organization.objects.get(email_id=email_id)
    demo_lecture.approved = True
    demo_lecture.save()  # Save the changes to the database

    # Get the list of student emails who registered for this demo lecture
    registered_students = StudentRegistration.objects.all()

    # Get the list of student emails
    student_emails = [student.email for student in registered_students]

    # Add the approving company's email to the recipient list
    recipient_list = student_emails + [demo_lecture.email_id]

    # Render the email message for the company
    company_context = {'demo_lecture': demo_lecture}
    company_message = 'Your Demo Lecture Application get Approved By TPO Member For any further details please contact to TPO Member'

    # Render the email message for the students
    student_context = {'demo_lecture': demo_lecture,'name':name}
    student_message = render_to_string('demo_approved_email.html', student_context)

    # Send email to the approving company
    company_subject = 'Demo Lecture Approved'
    from_email = 'shrutimaurya169@gmail.com'
    company_recipient_list = [demo_lecture.email_id]
    send_mail(company_subject, company_message, from_email, company_recipient_list, fail_silently=False)

    # Send email to all registered students
    student_subject = 'Demo Lecture Details'
    from_email = 'shrutimaurya169@gmail.com'
    send_mail(student_subject, message='', html_message=student_message, from_email=from_email,  recipient_list=student_emails, fail_silently=False)

    print(demo_lecture.approved)
    messages.success(request, 'Emails sent successfully.')
    return redirect('get_demo')


def disapprove_demo(request, email_id, title):
    # Retrieve the demo lecture to disapprove
    demo_lecture = Demo.objects.get(email_id=email_id, title=title)
    demo_lecture.approved = False
    demo_lecture.disapproved = 'Disapprove'
    demo_lecture.save()  # Save the changes to the database

    # Render the email message for the company
    company_context = {'demo_lecture': demo_lecture}
    company_message = 'Your Demo Lecture Application get Disapproved By TPO Member For any further details please contact to TPO Member'

    # Send email to the approving company
    company_subject = 'Demo Lecture Disapproved'
    from_email = 'shrutimaurya169@gmail.com'  # Replace with your email address or use a dedicated email account

    send_mail(company_subject, company_message, from_email,  recipient_list=[demo_lecture.email_id], fail_silently=False)
    messages.success(request, 'Emails sent successfully.')
    return redirect('get_demo')

  
  #pdf
def generate_pdf(request):
    # Render the HTML content to be converted into a PDF
    html_content = render_to_string('rusume.html', context={})
    
    # Specify the output path for the PDF
    pdf_path = "C:\\Users\\Shruti Maurya\\Downloads\\output.pdf"
    
   
    
    # Convert HTML to PDF using pdfkit
    pdfkit.from_string(html_content, pdf_path,configuration=pdfkit.configuration(wkhtmltopdf=r'F:\PDF\wkhtmltopdf\bin\wkhtmltopdf.exe'))

    # Read the generated PDF file
    with open(pdf_path, 'rb') as pdf_file:
        pdf_data = pdf_file.read()

    # Return the PDF as a download response
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=output.pdf'
    return response
def loginasstudent(request):
    return render(request,'loginasstudent.html')