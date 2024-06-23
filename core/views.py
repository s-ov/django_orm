from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Prefetch
from django.utils import timezone

from .models import Restaurant, Rating, Sale, Staff, StaffRestaurant
from .forms import RatingForm, RestaurantForm


# def index(request):
#     if request.method == "POST":
#         form = RestaurantForm(request.POST)
#         if form.is_valid():
#             # if class RatingForm(forms.Form) ===>>> form.cleaned_data()   instead of   form.save() 
#             form.save()     
#         else:
#             return render(request, "core/index.html", {"form": form})
#     context = {"form": RestaurantForm()}
#     return render(request, "core/index.html", context)


# def index(request):
#     jobs = StaffRestaurant.objects.prefetch_related("restaurant", "staff")
#     for job in jobs:
#         print(job.restaurant.name)
#         print(job.staff.name)
#     return render(request, "core/index.html", {"jobs": jobs})

def index(request):
    restaurants = Restaurant.objects.all()[:5]
    return render(request, "core/index.html", {"restaurants": restaurants})


def index_3(request):
    # ===========   prefetch_related()  =============
    # restaurants = Restaurant.objects.prefetch_related("ratings", "sales")
    # restaurants = Restaurant.objects.filter(name__startswith="c").prefetch_related("ratings", "sales")
    # context = {"restaurants": restaurants}

    # ===========   select_related()  =============
    # ratings = Rating.objects.select_related("restaurant")

    # ===========   only(c_n1, c_n2) - must be indicated column name  =============
    # ratings = Rating.objects.only("rating", "restaurant__name").select_related("restaurant")
    # context = {"ratings": ratings}

    #              ============= Prefetch() objects ==================
    # Get all 5-star ratings and fetch all sales for the 5-star restaurants

    month_ago = timezone.now() - timezone.timedelta(days=30)
    monthly_sales = Prefetch("sales", queryset=Sale.objects.filter(date_time__gte=month_ago))
    restaurants = Restaurant.objects.prefetch_related("ratings", monthly_sales).filter(ratings__rating=5)
    restaurants = restaurants.annotate(total_sales=Sum("sales__income")).order_by("total_sales")
    context = {"ratings": restaurants}
    return render(request, "core/index.html", context)


def add_restaurant(request):
    if request.method == "POST":
        form = RestaurantForm(request.POST or None)
        if form.is_valid():
            form.save()
        else:
            return render(request, "core/add_restaurant.html", {"form": form})
    return render(request, "core/add_restaurant.html", {"form": RestaurantForm()})
    

def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    return render(request, 'core/restaurant.html', {'restaurant': restaurant})
