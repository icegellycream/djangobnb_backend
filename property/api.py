from django.http import JsonResponse

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from .forms import PropertyForm
from .models import Property, Reservation
from .serializers import PropertiesListSerializer, PropertiesDetailSerializer, ReservationListSerializer


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def properties_list(request):
    properties = Property.objects.all()

    #
    #Filter

    landlord_id = request.GET.get('landlord_id', '')

    if landlord_id:
        properties = properties.filter(landlord_id=landlord_id)
    
    #
    #

    serializer = PropertiesListSerializer(properties, many=True)

    return JsonResponse({
        'data': serializer.data 
    })

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def property_reservations(request, pk):
    try:
        property = Property.objects.get(pk=pk)
        reservations = property.reservations.all()

        serializer = ReservationListSerializer(reservations, many=True)

        return JsonResponse(serializer.data, safe=False)
    except Property.DoesNotExist:
        return JsonResponse({'error': 'Property not found'}, status=404)

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def properties_detail(request, pk):
    try:
        property = Property.objects.get(pk=pk)
        serializer = PropertiesDetailSerializer(property, many=False)
        
        return JsonResponse({
            'data': serializer.data
        })
    except Property.DoesNotExist:
        return JsonResponse({'error': 'Property not found'}, status=404)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_property(request):
    form = PropertyForm(request.POST, request.FILES)

    if form.is_valid():
        property = form.save(commit=False)
        property.landlord = request.user
        property.save()

        return JsonResponse({'success': True})
    else:
        print('error', form.errors, form.non_field_errors)
        return JsonResponse({'errors': form.errors.as_json()}, status=400)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def book_property(request, pk):
    try:
        property = Property.objects.get(pk=pk)
        
        # Extract booking data from form
        guests = request.POST.get('guests')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        number_of_nights = request.POST.get('number_of_nights')
        total_price = request.POST.get('total_price')
        
        # Create reservation
        reservation = Reservation.objects.create(
            property=property,
            start_date=start_date,
            end_date=end_date,
            number_of_nights=number_of_nights,
            guests=guests,
            total_price=total_price,
            created_by=request.user
        )
        
        return JsonResponse({'success': True, 'message': 'Property booked successfully'})
        
    except Property.DoesNotExist:
        return JsonResponse({'error': 'Property not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)