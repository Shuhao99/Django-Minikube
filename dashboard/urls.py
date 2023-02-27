from django.urls import path
from . import views

urlpatterns = [
    path('', views.started_ride, name='started_ride'),
    path('shared/', views.shared_rides, name='shared rides'),

    path('register/', views.register, name='register'),
    path('require_ride/', views.require_ride, name='require ride'),

    path('ride_detail/<int:pk>', views.ride_detail, name='ride detail'),
    path('ride_detail/edit/<int:pk>', views.edit_ride, name='edit ride'),
    path('ride_detail/edit/success', views.edit_success, name='ride edit success'),
    path('ride_detail/<int:pk>/cancel/', views.ride_cancel, name='cancel ride'),
    path('quit_ride/<int:pk>', views.quit_ride, name='quit ride'),

    path('search_rides/', views.search_ride, name='search rides'),
    path('join_ride/<int:pk>', views.join_ride, name='join ride'),
    path('join_ride/success', views.join_success, name='join success'),
    path('join_ride/failed', views.join_fail, name='join fail'),


    path('profile/', views.profile_page, name='profile'),
    path('profile/edit_personal_info', views.edit_profile, name='profile_edit_personal'),
    path('profile/change_credential', views.change_password, name='profile_edit_password'),


    #vehicle registrate
    path('vehicle_reg/', views.vehicle_registrate, name='vehicle registrate'),
    #switch to driver portal redirect to vehicle regist or tasks
    path('driver/', views.switch_to_driver, name='switch to driver'),
    path('tasks/', views.driver_tasks, name='tasks'),
    path('complete/<int:pk>', views.complete_task, name='complete task'),
    path('my_vehicle/', views.check_my_vehicle, name='my vehicle'),
    path('edit_vehicle/', views.EditVehicle.as_view(), name='edit vehicle'),
    path('search_tasks/', views.search_tasks, name='search tasks'),
    path('confirm/<int:pk>', views.confirm_task, name='task confirm'),

    #delete driver account
    path('delete_account/', views.delete_vehicle, name='delete account'),
    path('delete_confirm/', views.delete_confirm, name='delete confirm'),

    path('404/', views.handle_404, name='404'),
]
