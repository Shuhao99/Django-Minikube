from django.shortcuts import get_object_or_404, redirect, render, render
from .forms import RegisterForm, ProfileForm, RideRequestForm, SearchRide, PersonalInfoForm, VehicleForm, ChangePasswordForm, SearchTask
from .models import User, Profile, Ride, Group, Vehicle
from django.core.mail import send_mail
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from django.views import generic
from django.contrib.auth.models import User
from django.http import Http404
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
#TODO: Success 页面, edit删除ride所有共享成员, 邮件提醒
#TODO: 检查非法输入
# take second element for sort

def require_ride(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
    if request.method == "POST":
        form = RideRequestForm(request.POST)
        curr_user = get_object_or_404(User, id=request.session['user_id'])
        if form.is_valid():
            ride = form.save(commit=False)
            ride.owner = curr_user
            try:
                group = Group.objects.get(user=curr_user, groupNum=ride.passengerNum)
            except Group.DoesNotExist:
                group = Group(user=curr_user, groupNum=ride.passengerNum)
                group.save()
            ride.save()
            ride.shared_by_user.add(group)
            messages.success(request, 'Request successfully.')
            return redirect("/")
        else:
            print("form not valid:"+str(form.errors))
    else:
        form = RideRequestForm()

    context = {'form': form}
    return render(request, 'dashboard/require_ride.html', context)

def started_ride(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
    else:
        curr_user = get_object_or_404(User, id = request.session['user_id'])
        open_ride = Ride.objects.filter(
            confirmed=False,
            completed=False,
            owner = curr_user
        ).order_by("arrive_time")
        confirmed_ride = Ride.objects.filter(
            confirmed=True,
            completed=False,
            owner = curr_user
        ).order_by("arrive_time")
        completed_ride = Ride.objects.filter(
            confirmed=True,
            completed=True,
            owner = curr_user
        ).order_by("arrive_time")
        context = {"open_rides": open_ride,
                   "confirmed_rides": confirmed_ride,
                   "completed_rides": completed_ride,
                   "user":curr_user
                   }
        return render(request, 'dashboard/started_ride.html', context)

def register(request):
    if request.method == 'POST':
        user_form = RegisterForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('/login')
    else:
        user_form = RegisterForm()
        profile_form = ProfileForm()
    return render(request, 'registration/register.html', context={'form': user_form,
                                                                  'profile_form': profile_form})

def ride_cancel(request, pk):
    if not request.session.get('is_login', None):
        return redirect('/login')
    ride = get_object_or_404(Ride, pk = pk)
    if not ride.owner == request.user:
        raise Http404
    ride.delete()

    return redirect('/')

def ride_detail(request, pk):
    if not request.session.get('is_login', None):
        return redirect('/login')
    gender = ['female', 'male', 'NG']

    try:
        ride = get_object_or_404(Ride, pk=pk)
    except:
        raise Http404("This is not your ride! ")

    curr_user = get_object_or_404(User, id=request.session['user_id'])
    if curr_user != ride.owner:
        find = False
        is_driver = False
        groups = Group.objects.filter(user=request.user)
        for group in groups:
            if group in ride.shared_by_user.all():
                find = True
        if ride.vehicle and request.user == ride.vehicle.owner:
                is_driver = True
        if (not find) and (not is_driver):
            raise Http404("This is not your ride! ")
    # status
    if ride.completed:
        status = "Completed"
    elif ride.confirmed:
        status = "Confirmed"
    else:
        status = "Open"

    v_type = ride.get_v_type()

    # driver
    if ride.vehicle:
        driver_name = ride.vehicle.owner.first_name + ' ' + ride.vehicle.owner.last_name
        plate = ride.vehicle.plateNumber
        driver_phone = ride.vehicle.owner.profile.mobile
        driver_email = ride.vehicle.owner.email
        driver = ride.vehicle.owner
    else:
        driver_name = "Not assigned yet"
        plate = "Unknown"
        driver_phone = "Unknown"
        driver_email = "Unknown"
        driver = None

    shared_by = ride.shared_by_user.all()
    context = {
        "dest" : ride.dest,
        "arrive_time" : ride.arrive_time,
        "v_type": v_type,
        "shared_by": shared_by,
        "owner" : ride.owner,
        "status" : status,
        "driver_name" : driver_name,
        "plate" : plate,
        "driver_phone": driver_phone,
        "driver_Email": driver_email,
        "gender": gender,
        "curr_user": curr_user,
        "ride": ride,
        "driver" : driver,
    }
    return render(request, 'dashboard/ride_detail.html',context)

#TODO: remove all relations and send email
def edit_success(request):
    return render(request, 'dashboard/ride_edit_success.html')

def edit_ride(request, pk):
    if not request.session.get('is_login', None):
        return redirect('/login')
    ride = get_object_or_404(Ride, pk=pk)
    if not ride.owner == request.user:
        raise Http404
    if request.method == 'POST':
        form = RideRequestForm(request.POST, instance=ride)
        form.save()
        mail_list = []
        for group in ride.shared_by_user.all():
            if group.user != request.user:
                mail_list.append(group.user.email)
                ride.shared_by_user.remove(group)
            elif group.groupNum != ride.passengerNum:
                try:
                    old_group = Group.objects.get(user=request.user, groupNum=ride.passengerNum)
                    ride.shared_by_user.remove(group)
                    ride.shared_by_user.add(old_group)
                except Group.DoesNotExist:
                    group.groupNum=ride.passengerNum
                    group.save()
        ride.save()
        mail_content = "<h3> Your Uber order has been canceled!</h3>" \
                       "<p>This ride has been edited by owner, your shared ride has been canceled.</p>" \
                       "<h4> Order information: </h4>" \
                       "Order number: {order_id} <br>" \
                       "Original destination: {dest} <br>" \
                       "Original expected arrive time: {time} <br>" \
                       "".format(order_id=ride.pk, dest=ride.dest,
                                time=ride.arrive_time)
        send_mail(
            subject="Your order has been canceled!",
            message='Email content',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=mail_list,
            fail_silently=False,
            html_message=mail_content
        )
        return redirect("/ride_detail/edit/success")
    else:
        form = RideRequestForm(instance=ride)
    return render(request,'dashboard/edit_ride.html', context={'form':form})

def search_ride(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
    if request.method == 'POST':
        form = SearchRide(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            addr = cleaned_data.get('address')
            start = cleaned_data.get('start')
            end = cleaned_data.get('end')
            number = cleaned_data.get('passengerNum')

            # number = int(number)
            #format time
            start = start.astimezone(timezone.utc)
            end = end.astimezone(timezone.utc)

            rides = Ride.objects.filter(
                completed=False,
                confirmed=False,
                if_share=True,
                arrive_time__gte=start,
                arrive_time__lte=end
            ).exclude(owner=request.user).order_by("arrive_time")
            addr = str(addr).lower().split()
            groups = Group.objects.filter(user=request.user)
            for group in groups:
                rides = [ride for ride in rides if group not in ride.shared_by_user.all()]
            for word in addr:
                rides = [ride for ride in rides if word in str(ride.dest).lower()]
            rides = [ride for ride in rides if \
                     number + ride.get_passenger_num() + 1 <= \
                     ride.get_capacity()]
            rides.sort(key=lambda x: x.arrive_time)
            message = "{number} orders found: ".format(number = str(len(rides)))
        else:
            rides = []
            message = "Input invalid" + str(list(form.errors.values())[0])
    else:
        form = SearchRide()
        rides = []
        message = "Results will be displayed below. "

    context = {
        "rides" : rides,
        "msg" : message,
        "form" : form
    }
    return render(request, 'dashboard/search_rides.html', context=context)

def join_ride(request, pk):
    if request.method == 'POST':
        ride = get_object_or_404(Ride, pk=pk)
        num_passengers = int(request.POST.get('number'))
        if num_passengers + ride.get_passenger_num() + 1 <= ride.get_capacity():
            try:
                group = Group.objects.get(user=request.user, groupNum=num_passengers)
            except Group.DoesNotExist:
                group = Group(user=request.user, groupNum=num_passengers)
                group.save()
            ride.shared_by_user.add(group)
            messages.success(request, 'Request successfully.')
            return redirect("/join_ride/success")
        else:
            return redirect("/join_ride/failed")

    return render(request, 'dashboard/join_ride.html')

def join_success(request):
    return render(request, 'dashboard/join_success.html')

def join_fail(request):
    return render(request, 'dashboard/join_failed.html')

def shared_rides(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
    else:
        curr_user = get_object_or_404(User, id = request.session['user_id'])
        groups = Group.objects.filter(user=request.user)

        open_ride_ = Ride.objects.filter(
            confirmed=False,
            completed=False,
        ).exclude(owner=request.user).order_by("arrive_time")

        open_ride = []
        for group in groups:
            open_ride += [ride for ride in open_ride_ if group in ride.shared_by_user.all()]
        open_ride.sort(key=lambda x: x.arrive_time)

        confirmed_ride_ = Ride.objects.filter(
            confirmed=True,
            completed=False,
        ).exclude(owner=request.user).order_by("arrive_time")

        confirmed_ride = []
        for group in groups:
            confirmed_ride += [ride for ride in confirmed_ride_ if group in ride.shared_by_user.all()]
        confirmed_ride.sort(key=lambda x: x.arrive_time)

        completed_ride_ = Ride.objects.filter(
            confirmed=True,
            completed=True,
        ).exclude(owner=request.user).order_by("arrive_time")

        completed_ride = []
        for group in groups:
            completed_ride += [ride for ride in completed_ride_ if group in ride.shared_by_user.all()]
        completed_ride.sort(key=lambda x: x.arrive_time)

        context = {"open_rides": open_ride,
                   "confirmed_rides": confirmed_ride,
                   "completed_rides": completed_ride,
                   "user":curr_user
                   }
    return render(request, 'dashboard/shared_rides.html', context)

def quit_ride(request, pk):
    if not request.session.get('is_login', None):
        return redirect('/login')
    ride = get_object_or_404(Ride, pk = pk)
    if request.user == ride.owner:
        raise Http404
    else:
        find = False
        groups = Group.objects.filter(user=request.user)
        for group in groups:
            if group in ride.shared_by_user.all():
                find = True
        if not find:
            raise Http404
    for group in ride.shared_by_user.all():
        if group.user == request.user:
            ride.shared_by_user.remove(group)
    ride.save()
    return redirect('/shared')

def profile_page(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
    user = get_object_or_404(User, id=request.user.id)
    info = get_object_or_404(Profile, user = user)
    gender = info.get_gender()
    context = {
        'user':user,
        'info':info,
        'gender':gender
    }
    return render(request, 'dashboard/profile.html', context)

def edit_profile(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
    if request.method == 'POST':
        user_form = PersonalInfoForm(request.POST)
        profile = get_object_or_404(Profile, user=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            curr_user = request.user
            curr_user.last_name = user_form.cleaned_data['last_name']
            curr_user.first_name = user_form.cleaned_data['first_name']
            curr_user.email = user_form.cleaned_data['email']
            curr_user.save()
            profile_form.save()
            return redirect('/profile')
    else:
        user_form = PersonalInfoForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'dashboard/edit_profile.html', context={'user_form': user_form,
                                                                  'profile_form': profile_form})

#TODO: change password
def change_password(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        user = form.save(commit=False)
        if form.is_valid():
            request.user.username = user.username
            request.user.password = user.password
            request.user.save()
            return redirect('/logout')
    else:
        form = ChangePasswordForm()
    return render(request, 'dashboard/change_password.html', context={'form': form})

def vehicle_registrate(request):
    if request.method == 'POST':
        vehicle_form = VehicleForm(request.POST)
        if vehicle_form.is_valid():
            vehicle = vehicle_form.save(commit=False)
            vehicle.owner = request.user
            vehicle.save()
            return redirect('/driver')
    else:
        vehicle_form = VehicleForm()
    return render(request, 'dashboard/vehicle_regist.html', context={'form': vehicle_form})

def switch_to_driver(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
    if hasattr(request.user, 'vehicle'):
        return redirect('/tasks')
    else:
        return redirect('/vehicle_reg')

def driver_tasks(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
    if not hasattr(request.user, 'vehicle'):
        return  redirect('/')
    else:
        curr_user = get_object_or_404(User, id = request.session['user_id'])
        ongoing = Ride.objects.filter(
            confirmed=True,
            completed=False,
            vehicle=request.user.vehicle
        ).order_by("arrive_time")

        completed = Ride.objects.filter(
            confirmed=True,
            completed=True,
            vehicle=request.user.vehicle
        ).order_by("arrive_time")
        context = {"ongoing": ongoing,
                   "completed": completed,
                   "user":curr_user
                   }
        return render(request, 'driver_side/driver_tasks.html', context)

def complete_task(request, pk):
    ride = get_object_or_404(Ride, pk=pk)
    if ride.vehicle and ride.vehicle.owner == request.user:
        ride.completed = True
        ride.save()
        return redirect("/tasks")
    else:
        raise Http404

def check_my_vehicle(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
    if not hasattr(request.user, 'vehicle'):
        return  redirect('/vehicle_reg')
    vehicle = request.user.vehicle
    return render(request, 'driver_side/my_vehicle.html', context={'vehicle': vehicle})

class EditVehicle(SuccessMessageMixin, generic.UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'driver_side/edit_vehicle.html'
    # redirect to this url after success
    success_url = "/my_vehicle"
    success_message = "Changes successfully saved."

    # Check if the user is qualified for edit
    def get_object(self, *args, **kwargs):
        if not self.request.session.get('is_login', None):
            return redirect('/login')
        if not hasattr(self.request.user, 'vehicle'):
            return redirect('/vehicle_reg')
        vehicle = get_object_or_404(Vehicle, owner=self.request.user)
        return vehicle

def search_tasks(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
    if not hasattr(request.user, 'vehicle'):
        return  redirect('/vehicle_reg')
    if request.method == 'POST':
        form = SearchTask(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            addr = cleaned_data.get('address')
            start = cleaned_data.get('start')
            end = cleaned_data.get('end')

            start = start.astimezone(timezone.utc)
            end = end.astimezone(timezone.utc)

            rides = Ride.objects.filter(
                completed=False,
                confirmed=False,
                arrive_time__gte=start,
                arrive_time__lte=end
            ).exclude(owner=request.user).order_by("arrive_time")

            if addr != '':
                addr = str(addr).lower().split()
                for word in addr:
                    rides = [ride for ride in rides if word in str(ride.dest).lower()]

            rides = [ride for ride in rides if \
                     (not ride.vehicleType) or \
                     ride.vehicleType == request.user.vehicle.vehicleType]

            rides = [ride for ride in rides if \
                     ride.get_passenger_num() + 1 <= \
                     request.user.vehicle.get_capacity()]

            rides = [ride for ride in rides if \
                     (not ride.special_req) or ride.special_req == ''\
                     or ride.special_req == request.user.vehicle.special_info]

            rides.sort(key=lambda x: x.arrive_time)
            message = "{number} orders found: ".format(number=str(len(rides)))
        else:
            rides = []
            message = "Input invalid" + str(list(form.errors.values())[0])
    else:
        form = SearchRide()
        rides = []
        message = "Results will be displayed below. "

    context = {
        "rides": rides,
        "msg": message,
        "form": form
    }
    return render(request, 'driver_side/search_tasks.html', context=context)

def confirm_task(request, pk):
    if not request.session.get('is_login', None):
        return redirect('/login')
    if not hasattr(request.user, 'vehicle'):
        return  redirect('/vehicle_reg')
    ride = get_object_or_404(Ride, pk=pk)
    curr_user = request.user
    if (not ride.vehicleType) or ride.vehicleType == curr_user.vehicle.vehicleType:
        if ride.get_passenger_num() + 1 <= \
           request.user.vehicle.get_capacity():
            if (not ride.special_req) or ride.special_req == ''\
                     or ride.special_req == request.user.vehicle.special_info:
                ride.confirmed = True
                ride.vehicle = curr_user.vehicle
                ride.save()
                mail_list = [ride.owner.email]
                for group in ride.shared_by_user.all():
                    mail_list.append(group.user.email)
                mail_content = "<h3> Your Uber order has been confirmed!</h3>" \
                               "<br>" \
                               "<h4> Order information: </h4>" \
                               "Order number: {order_id} <br>" \
                               "Destination: {dest} <br>" \
                               "Expected arrive time: {time} <br>" \
                               "Driver's mobile: {phone}<br>" \
                               "Car plate: {plate}<br><br>" \
                               "Travel Safe! ".format(order_id = ride.pk, dest = ride.dest,
                                         time = ride.arrive_time,
                                         phone = ride.vehicle.owner.profile.mobile,
                                         plate = ride.vehicle.plateNumber
                                         )
                send_mail(
                    subject="Your order has been confirmed!",
                    message='Email content',
                    from_email= settings.EMAIL_HOST_USER,
                    recipient_list=mail_list,
                    fail_silently=False,
                    html_message=mail_content
                )
                return redirect('/tasks')
    raise Http404

def delete_vehicle(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
    if not hasattr(request.user, 'vehicle'):
        return  redirect('/vehicle_reg')
    return render(request, 'driver_side/delete_confirm.html')

def delete_confirm(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
    if not hasattr(request.user, 'vehicle'):
        return redirect('/vehicle_reg')

    vehicle = request.user.vehicle
    rides = Ride.objects.filter(
        confirmed=True,
        completed=False,
        vehicle=vehicle
    )

    for ride in rides:
        mail_list = []
        for group in ride.shared_by_user.all():
            mail_list.append(group.user.email)

        mail_content = "<h3> Your Uber order has been canceled!</h3>" \
                       "<p>Your driver quited our platform, all his confirmed order were released and became open again.</p>" \
                       "<h4> Order information: </h4>" \
                       "Order number: {order_id} <br>" \
                       "Destination: {dest} <br>" \
                       "Expected arrive time: {time} <br>" \
                       "".format(order_id=ride.pk, dest=ride.dest,
                                 time=ride.arrive_time)
        send_mail(
            subject="Confirmed order be canceled!",
            message='Email content',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=mail_list,
            fail_silently=False,
            html_message=mail_content
        )
        ride.confirmed = False
        ride.vehicle = None
        ride.save()
    vehicle.delete()
    return redirect('/profile')

def handle_404(request):
    return render(request, '404/404.html')

def response_error_handler(request, exception=None):
    return render(request, '404/404.html')