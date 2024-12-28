from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Employee, Broker, Meeting
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import date
from django.views.decorators.csrf import csrf_exempt


# Register view to create a new user and employee
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create Employee record for the new user
            Employee.objects.create(
                user=user,
                name=user.username,
                mobile=request.POST.get('mobile', "1234567890"),  # Placeholder
                designation="Employee",  # Default designation
                latitude=0.0,  # Placeholder
                longitude=0.0  # Placeholder
            )
            return redirect('login')  # Redirect to login after registration
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


# Login view to authenticate user and start a session
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to the dashboard after login
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')


# Logout view to log the user out
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout


# Dashboard view for the logged-in user to see brokers near their location
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Employee, Broker, Meeting
from geopy.distance import geodesic
from math import radians
from datetime import date
from math import radians
from math import sin, cos, sqrt, atan2, radians

# Haversine formula to calculate the distance between two geographic coordinates
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Employee, Broker, Meeting
from math import sin, cos, sqrt, atan2, radians
from datetime import date

# Haversine formula to calculate the distance between two geographic coordinates
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = (pow(sin(delta_phi / 2), 2) + cos(phi1) * cos(phi2) * pow(sin(delta_lambda / 2), 2))
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c * 1000  # distance in meters
    return distance


from haversine import haversine, Unit
from django.shortcuts import render, get_object_or_404, redirect


from django.contrib import messages

def dashboard(request):
    employee = get_object_or_404(Employee, user=request.user)

    # Check if the location is set
    if employee.latitude == 0.0 and employee.longitude == 0.0:
        return redirect('update_location')  # Redirect to the update location page

    user_latitude = employee.latitude
    user_longitude = employee.longitude

    # Find nearby brokers (within 100 meters)
    brokers = Broker.objects.all()
    nearby_brokers = []
    for broker in brokers:
        distance = broker.distance_to(user_latitude, user_longitude)
        if distance <= 100:  # 100 meters range
            nearby_brokers.append({
                'id': broker.id,  # Include ID to pass to the form
                'name': broker.name,
                'location': broker.location,
                'latitude': broker.latitude,
                'longitude': broker.longitude,
                'distance': distance
            })

    if request.method == 'POST':
        broker_id = request.POST.get('broker_id')
        meeting_date = request.POST.get('meeting_date')
        feedback = request.POST.get('feedback')

        # Validate broker_id
        if not broker_id:
            messages.error(request, "Broker ID is missing.")
            return redirect('dashboard')

        try:
            broker = get_object_or_404(Broker, id=broker_id)
            meeting = Meeting.objects.create(
                broker=broker,
                employee=employee,
                date=meeting_date,
                feedback=feedback
            )
            messages.success(request, "Meeting scheduled successfully.")
            return redirect('meeting_confirmation')  # Redirect to a confirmation page
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    return render(request, 'dashboard.html', {
        'employee': employee,
        'user_latitude': user_latitude,
        'user_longitude': user_longitude,
        'brokers': nearby_brokers
    })




@login_required
@login_required
@csrf_exempt
def update_location(request):
    employee = Employee.objects.get(user=request.user)

    if request.method == 'POST':
        # Update profile details
        employee.name = request.POST.get('name', employee.name)
        employee.mobile = request.POST.get('mobile', employee.mobile)
        employee.designation = request.POST.get('designation', employee.designation)
        employee.latitude = float(request.POST.get('latitude', employee.latitude))
        employee.longitude = float(request.POST.get('longitude', employee.longitude))

        # Save the updated information
        employee.save()

        return redirect('dashboard')  # Redirect to dashboard after update

    return render(request, 'update_location.html', {'employee': employee})



@csrf_exempt
def get_location_data(request):
    location = request.GET.get('location', '')
    if location:
        geolocator = Nominatim(user_agent="realestate_app")
        geocode_result = geolocator.geocode(location)
        if geocode_result:
            lat_lng = geocode_result.latitude, geocode_result.longitude
            return JsonResponse({'latitude': lat_lng[0], 'longitude': lat_lng[1]})
    return JsonResponse({'error': 'Location not found'}, status=404)


# View to return the user's location (for API call)
@csrf_exempt
def get_user_location(request):
    geolocator = Nominatim(user_agent="realestate_app")
    location = geolocator.geocode("current location")  # Dummy location, adjust as per your use case
    if location:
        return JsonResponse({'latitude': location.latitude, 'longitude': location.longitude})
    return JsonResponse({'error': 'Location not found'}, status=400)


def meeting_confirmation(request):
    # Get the latest meeting of the logged-in employee
    employee = request.user.employee  # Assuming a OneToOneField between User and Employee
    meeting = Meeting.objects.filter(employee=employee).order_by('-id').first()

    # Pass meeting details to the template
    context = {
        'meeting_broker': meeting.broker.name if meeting else "N/A",
        'meeting_date': meeting.date if meeting else "N/A",
        'meeting_feedback': meeting.feedback if meeting else "N/A"
    }
    return render(request, 'meeting_confirmation.html', context)