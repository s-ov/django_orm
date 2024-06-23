from django.contrib.auth.models import User
from core.models import Restaurant, Rating, Sale, Staff, StaffRestaurant, Comment

from django.utils import timezone
from django.db import connection
from django.db.models.functions import Lower, Upper, Length, Concat, Coalesce
from django.db.models import (Count, Avg, Max, Min, Sum, StdDev, Variance, CharField, 
                              Value, F, Q, Case, When, Subquery, OuterRef, Exists)

from django.contrib.contenttypes.models import ContentType

import itertools
import random
from pprint import pprint


# pip install django-extensions
# ./manage.py runscript orm_scripts
# ./manage.py shell_plus --print-sql
# earliest()/latest()   =>  for datetime fields


def run():
    """ 
            Django Model Methods 
        @property is very useful if you have a simple logic        
    """
    # restaurant = Restaurant.objects.first()
    # restaurant.nickname = 'Bastard'             # we don't need < restaurant.save() >
    # print(f'Nickname: {restaurant.nickname}')
    # print(f'Name: {restaurant.name}')
    # print(f'Property: {restaurant.restaurant_name}')

    # restaurant = Restaurant.objects.first()
    # restaurant.date_opened = timezone.now().date()  # gives current date
    # print(f'Opened in {restaurant.date_opened}')
    # print(f'This year, {restaurant.was_opened_this_year}')

    restaurant = Restaurant.objects.first()
    now = timezone.now().date()  # gives current date
    restaurant.date_opened = now
    referenced_date = now - timezone.timedelta(days=5)
    print(restaurant.is_opened_after(referenced_date))
    

# ====================================================================================
    """
        ER Diagrams(Entity Relation)
        Django Extensions ->>> Graph Models  

        python3 manage.py graph_models core > models.dot
        !!! then we have to open up special website and paste in there content of  'models.dot' file  !!!

        python3 manage.py graph_models core auth > models.dot
        !!! 'auth' shows even built-in django models such as 'User' !!!

        GraphViz generator: https://dreampuf.github.io/GraphvizOnline
    """

    """     DB Constraint    """
    # restaurant = Restaurant.objects.last()
    # user = User.objects.first()
    # rating = Rating.objects.create(user=user, restaurant=restaurant, rating=4)
    # print(rating)
    """After creation constrains =... in model Rating in class Meta we must -> ./manage.py makemigrations+migrate"""
    """
        The benefit of using UniqueConstraint we can apply an expressions. We can also -> unique=True

        It gives only one comment can make certain user for certain restaurant :

            models.UniqueConstraint(
                fields=['user', 'restaurant'],
                name='user_restaurant_uniq'
            )
    """

    """         GENERIC RELATIONS    """
    # restaurant = Restaurant.objects.get(pk=8)
    # comments = restaurant.comments.all()
    # print(comments)

    # restaurant = Restaurant.objects.get(pk=8)
    # restaurant.comments.add(
    #     Comment.objects.create(text="Stinky hole", content_object=restaurant)
    # )
    # print(restaurant.comments.count())

    # restaurant = Restaurant.objects.get(pk=8)
    # last_comment = restaurant.comments.last()
    # restaurant.comments.remove(last_comment)
    # print(restaurant.comments.count())

    """   comments = GenericRelation('Comment', related_query_name='restaurant')   """
    # comments = Comment.objects.filter(restaurant__restaurant_type=Restaurant.TypeChoices.CHINESE)
    # print(comments)
    # print(comments.count())

    """         GENERIC FOREIGN KEY    """
    # comments = Comment.objects.all()
    # for comment in comments:
    #     print(comment.content_object, type(comment.content_object))

    # comment = Comment.objects.first()
    # print(comment.content_object)

    """ programmaticly adding commments"""
    # restaurant = Restaurant.objects.first()
    # comment = Comment.objects.create(text="Aweful restaurant", content_object=restaurant)
    # print(comment.content_object)
    # print(comment.__dict__)

    """         Content-Type    """
    # content_types = ContentType.objects.all()
    # print(content_types)

    # content_types = ContentType.objects.filter(app_label="core")
    # print([c.model for c in content_types])

    """     model_class()    """
    # content_type = ContentType.objects.get(app_label="core", model="restaurant")
    # restaurant_model = content_type.model_class()
    # print(restaurant_model)
    # print(restaurant_model.objects.all())

    """     get_object_for_this_type()    """
    # content_type = ContentType.objects.get(app_label="core", model="restaurant")
    # restaurant_model = content_type.get_object_for_this_type(name="Taco Bell")
    # print(restaurant_model)
    # print(restaurant_model.latitude)

    """ !!!    get_for_model()  - TO WORK WITH PARTICULAR MODEL !!!  """
    # rating_content_type = ContentType.objects.get_for_model(Rating)
    # print(rating_content_type.app_label)
    # model_class = rating_content_type.model_class()
    # print(model_class.objects.all())

    
# ======================== Subquery() ========================================================
    """
        SELECT * FROM core_sale WHERE restaurant_id IN 
        (SELECT id FROM core_restaurant WHERE restaurant_type IN ('IT', 'CH'))
    """

    # sales = Sale.objects.filter(restaurant__restaurant_type__in=['IT', 'CH'])

    # restaurant = Restaurant.objects.filter(restaurant_type__in=['IT', 'CH'])
    # sales = Sale.objects.filter(restaurant__in=Subquery(restaurant.values('pk')))
    # print(len(sales))

    """
        SELECT id, name, restaurant_type, 
        (SELECT income FROM core_sale WHERE restaurant_id=core_restaurant.id
        ORDER BY date_time DESC LIMIT 1) AS last_sale
        FROM core_restaurant
    """
    # annotate() each restaurant with its MOST RECENT sale
    # sales = Sale.objects.filter(restaurant=OuterRef('pk')).order_by('-date_time')

    # outer query
    # restaurants = Restaurant.objects.annotate(last_sale_income=Subquery(sales.values('income')[:1]))
    # for restaurant in restaurants:
    #     print(f'{restaurant.name} =>>> {restaurant.last_sale_income}')

    # restaurants = Restaurant.objects.annotate(
    #     last_sale_income=Subquery(sales.values('income')[:1]),
    #     last_sale_expenditure=Subquery(sales.values('expenditure')[:1]),
    #     profit = F('last_sale_income') - F('last_sale_expenditure')
    #     )

    # print(restaurants.first().profit)


    # ========= filter to restaurants that have any sales with income > 85 ========================
    # =======================    Exists(), OuterRef()   ==========================================

    # restaurants = Restaurant.objects.filter(
    #     Exists(Sale.objects.filter(restaurant=OuterRef('pk'), income__gt=85))
    # )
    # restaurants= Restaurant.objects.filter(
    #     ~Exists(Rating.objects.filter(restaurant=OuterRef('pk'), rating=2))
    # )


    # five_days_ago = timezone.now() - timezone.timedelta(days=15)
    # sales = Sale.objects.filter(restaurant=OuterRef('pk'), date_time__gte=five_days_ago)
    # restaurants = Restaurant.objects.filter(Exists(sales)).order_by('name')
    # print(restaurants.count())



# aggragate total sales over each 10 days period, starting from the first sale up until the last one

    # first_sale = Sale.objects.aggregate(first_sale_date=Min('date_time'))['first_sale_date']
    # last_sale = Sale.objects.aggregate(last_sale_date=Max('date_time'))['last_sale_date']

    # generate a list of dates each 10 days apart
    # dates = []
    # counter = itertools.count()

    # while (dt := first_sale + timezone.timedelta(days=10 * next(counter))) <= last_sale:
    #     dates.append(dt)

    # whens = [
    #     When(date_time__range=(dt, dt + timezone.timedelta(days=10)), then=Value(dt.date())) for dt in dates
    # ]
    # case = Case(*whens, output_field=CharField())

    # print(Sale.objects.annotate(date_range=case).values('date_range').annotate(total_sales=Sum('income')))
    

# ====================    assign a continent to each restaurant    =============================
    # types = Restaurant.TypeChoices
    # europian = Q(restaurant_type=types.ITALIAN) | Q(restaurant_type=types.GREEK)
    # asian = Q(restaurant_type=types.INDIAN) | Q(restaurant_type=types.CHINESE)
    # north_american = Q(restaurant_type=types.MEXICAN)

    # restaurants = Restaurant.objects.annotate(continent=Case(
    #     When(europian, then=Value('Europe')),
    #     When(asian, then=Value('Asia')),
    #     When(north_american, then=Value('North America')),
    #     default=Value('Not available'),
    # ))
    # print(restaurants.filter(continent='Europe'))


# ====================    annotate(), Case(), When()    =============================
    # italian = Restaurant.TypeChoices.ITALIAN
    # restaurants = Restaurant.objects.annotate(is_italian=Case(When(restaurant_type=italian, then=True), default=False))
    # print(restaurants.filter(is_italian=True))
    # print(restaurants.values('name', 'is_italian'))

    # print(Restaurant.objects.annotate(sales_num=Count('sales')).values('name','sales_num'))

    # restaurants = Restaurant.objects.annotate(sales_num=Count('sales'))
    # restaurants = restaurants.annotate(is_popular=Case(
    #                                                   When(sales_num__gte=8, then=True), 
    #                                                   default=False))
    # print(restaurants.filter(is_popular=True))

    # =====================================================================================
    # Restaurant has avrage rating > 3.5 and more then one rating
    # restaurants = Restaurant.objects.annotate(
    #                                         avg_rating=Avg('ratings__rating'), 
    #                                         ratings_num=Count('ratings__pk')
    # )
    # print(restaurants.values('avg_rating', 'ratings_num').filter(avg_rating__gt=3.5, ratings_num__gt=1))
    # restaurants = restaurants.annotate(highly_rated=Case(
    #                                                     When(avg_rating__gt=3.5, then=True),    
    #                                                     default=False)
                                                        # )

    # ======================= range lookup =============================                                                    
    # restaurants = restaurants.annotate(rating_bucket=Case(
    #                                                     When(highly_rating__gt=3.5, then=Value('Highly rated')),    
    #                                                     When(avg_rating__range=(2.5, 3.5), then=Value('Avarage rated')),
    #                                                     When(low_rating__lt=2.5, then=Value('Low rated')),
    #                                                     default=False))
    # print(restaurants.filter(highly_rated=True))

# ====================  using F() object to sort NULL values  =============================
    # print(Restaurant.objects.order_by(F('capacity').asc(nulls_last=True)).values('capacity'))

    # print(Restaurant.objects.filter(capacity__isnull=False).order_by('-capacity').values('name', 'capacity'))

# ====================     Coalesce()      =============================
    # rest = Restaurant.objects.first()
    # rest.name = 'china'
    # rest.save()
    # print(Restaurant.objects.annotate(name_value=Coalesce(F'name', F'nickname')).values('name_value'))

    # print(Restaurant.objects.aggregate(total_capacity=Sum('capacity')))
    # print(Restaurant.objects.aggregate(total_capacity=Coalesce(Sum('capacity'), 0)))

    # print(Rating.objects.filter(rating__gt=0).aggregate(average=Avg('rating', default=0.0)))

# ====================           =============================
    # restaurant = Restaurant.objects.first()
    # restaurant_2 = Restaurant.objects.last()
    # restaurant.capacity = 100
    # restaurant.save()
    # restaurant_2.capacity = 200
    # restaurant_2.save()
    
    # print(Restaurant.objects.filter(capacity__isnull=False).count())

    # print(Restaurant.objects.order_by('capacity').values('name', 'capacity')[3:5])
# ===================================  Q Object ==================================================
    # it = Restaurant.TypeChoices.ITALIAN
    # rating = Rating.objects.filter(restaurant__restaurant_type=it)
    # print(rating)
    # mx = Restaurant.TypeChoices.MEXICAN

    # print(Restaurant.objects.filter(Q(restaurant_type=it) | Q(restaurant_type=mx)))
    # restaurants = Restaurant.objects.filter(Q(name__icontains='italian') | Q(name__icontains='mexican'))
    # for restaurant in restaurants:
    #     print(restaurant.name)

    # it_or_mx = Q(restaurant_type=it) | Q(restaurant_type=mx)
    # print(Restaurant.objects.filter(it_or_mx))
    # recently_opened = Q(date_opened__gte=timezone.now() - timezone.timedelta(days=30))
    # not_recently_opened = ~Q(date_opened__gte=timezone.now() - timezone.timedelta(days=30))
    # print(Restaurant.objects.filter(it_or_mx | recently_opened))


    # ====================       Q(restaurant__name__regex='[0-9]+')    =============================
    # name_has_num = Q(restaurant__name__regex='[0-9]+')
    # profited = Q(income__gt=F('expenditure'))
    # print(Sale.objects.filter(name_has_num & profited).values_list('restaurant__name', flat=True).distinct())

    # print(Sale.objects.filter(name_has_num & profited).distinct().count())


    # =====================      select_related('restaurant')   ==============================
    # sales = Sale.objects.select_related('restaurant').filter(name_has_num & profited).distinct()
    # print(sales)

    # print(Restaurant.objects.filter(restaurant_type__in=[it, mx]))
    # print(Restaurant.objects.filter(name__icontains='1'))
    

# ===================================  F Expression ==============================================
    # rating = Rating.objects.filter(rating=1).first()
    # rating.rating = F('rating') + 1      # instead of < rating.rating += 1 >
    # rating.save()

    # Rating.objects.update(rating=F('rating') * 2)

    # sales = Sale.objects.all()
    # for sale in sales:
    #     sale.expenditure = random.uniform(5, 100)
    # Sale.objects.bulk_update(sales, ['expenditure'])    # bulk_update() to fill up new field <expenditure>

    # sales = Sale.objects.filter(expenditure__gt=F('income'))
    # print(sales)

# ===========================  F Expression in annotate() ============================================

    # sales = Sale.objects.annotate(profit=F('income') - F('expenditure')).order_by('-profit')
    # print(sales.first().profit)

# ===========================  F Expression in aggregate() ============================================

    # sales = Sale.objects.aggregate(profit=Sum(F('income') - F('expenditure')))

    # sales = Sale.objects.aggregate(profit=Count('id', filter=Q(income__gt=F('expenditure'))),
    #                                loss=Count('id', filter=Q(income__lt=F('expenditure'))))
    # print(sales)

# ===========================  F Expression in values() ===============================================

    # sales = Sale.objects.values('restaurant').annotate(profit=F('income') - F('expenditure'))
    # print(sales.first().get('profit'))

# ===================================  F Expression - refresh_from_db()==================================
    # rating = Rating.objects.first()
    # print(rating.rating)                # e.g. 7
    # rating.rating = F('rating') + 1      # instead of < rating.rating += 1 >
    # rating.save()
    # print(rating.rating)                # ===>>>  F(rating) + Value(1)

    # rating.refresh_from_db()
# ================================================================================================
    # restaurants = Restaurant.objects.annotate(total_income=Sum('sales__income'))
    # print([restaurant.total_income for restaurant in restaurants])

    # values('name', 'total_income') =>>> helps to improve performance
    # restaurants = Restaurant.objects.annotate(total_income=Sum('sales__income')).values('name', 'total_income')
    # print([restaurant['total_income'] for restaurant in restaurants])

    # restaurant_ratings = Restaurant.objects.annotate(
    #     ratings_num=Count('ratings'),
    #     avg_rating=Avg('ratings__rating'))
    # print(restaurant_ratings.values('name', 'ratings_num', 'avg_rating'))

    # restaurants = Restaurant.objects.values('restaurant_type').annotate(ratings_num=Count('ratings'))
    # print(restaurants)

    # restaurants_sales = Restaurant.objects.annotate(total_sales=Sum('sales__income')).order_by('total_sales')
    # restaurants_sales = Restaurant.objects.annotate(total_sales=Sum('sales__income')).  \
    #                                        filter(total_sales__gte=500). \
    #                                        order_by('total_sales')
    # for sales in restaurants_sales:
    #     print(sales.name, sales.total_sales)
    # print(restaurants_sales.values('name', 'total_sales'))

    # restaurants_sales = Restaurant.objects.annotate(total_sales=Sum('sales__income')).filter(total_sales__gte=500)
    # print(restaurants_sales.aggregate(avg_sales=Avg('total_sales')))
# ================================================================================================


# Restaurant 1 [Rating 4.5]
    # concatination = Concat(
    #     'name', Value(' [Rating: '), Avg('ratings__rating'), Value(']'), 
    #     output_field=CharField()
    #     )
    # restaurants = Restaurant.objects.annotate(message=concatination)
    # print(restaurants.first().message)
    # print(restaurants[6].message)

    # for restaurant in restaurants:
    #     print(restaurant.message)

# ========================================= annotate() ============================================================================
# fetch all restaurants and let's assume we want to get the number of characters in their names
    # restaurants = Restaurant.objects.annotate(name_length=Length('name'))
    # print(restaurants.first().name_length)
    # print(restaurants.values('name_length').first()['name_length'])
    # print(restaurants.values('name', 'name_length'))

    # restaurants = Restaurant.objects.annotate(name_length=Length('name')).filter(name_length__gte=10)
    # print(restaurants)

# =====================================aggregate(), count(), Count(), Avg(), Max(), Min(), Sum()================================================
    # month_ago = timezone.now() - timezone.timedelta(days=30)
    # sales = Sale.objects.filter(date_time__gte=month_ago)

    # print(sales)
    # print(sales.aggregate(total_income=Sum('income')))
    # print(Sale.objects.aggregate(total_income=Sum('income'), 
    #                              average_income=Avg('income'),
    #                              min_income=Min('income'),
    #                              max_income=Max('income'))
                                #  )
    
    # print(Restaurant.objects.count())
    # print(Rating.objects.filter(restaurant__name__startswith='c').aggregate(average=Avg('rating')))
    # print(Rating.objects.aggregate(average_rating=Avg('rating')))
    # print(Restaurant.objects.aggregate(Count('name')))
    # print(Restaurant.objects.aggregate(total=Count('name')))
    # print(Restaurant.objects.filter(name__startswith='c').count())

# =============================   values_list() returns tuple =========================================================
    # restaurants = Restaurant.objects.values_list('name', flat=True)
    # restaurants = Restaurant.objects.values_list('name', 'date_opened')
    # print(restaurants)

# =============================   values() returns dict ================================================================

    # italian = Restaurant.objects.filter(restaurant_type=Restaurant.TypeChoices.ITALIAN)
    # italian = Restaurant.TypeChoices.ITALIAN
    # rating = Rating.objects.filter(restaurant__restaurant_type=italian).values('rating', 'restaurant__name')
    # print(rating)

    # restaurant = Restaurant.objects.values(name_upper=Upper('name'))[:3]
    # restaurant = Restaurant.objects.values(upper_name=Upper('name'))[:3]

    # restaurant = Restaurant.objects.values('name', 'date_opened').first()
    # print(restaurant, restaurant['name'])
# ===========================   prefetch_related ===========================
    # staff, created = Staff.objects.get_or_create(name='John Doe', defaults={'name': 'John Doe'})
    # staff.restaurants.set(
    #     Restaurant.objects.all()[:10],
    #     through_defaults={'salary': (10_000 * random.randint(2, 8))}
    #     )
    
# ===========================   ManyToManyField  extra data (through='...') ===========================
    # staff, created = Staff.objects.get_or_create(name='John Doe', defaults={'name': 'John Doe'})
    # restaurant = Restaurant.objects.first()
    # restaurant2 = Restaurant.objects.last()

    # StaffRestaurant.objects.create(staff=staff, restaurant=restaurant, salary=10_000)
    # StaffRestaurant.objects.create(staff=staff, restaurant=restaurant2, salary=20_000)

    # staff_restaurant =StaffRestaurant.objects.filter(staff=staff)
    # for sr in staff_restaurant:
    #     print(sr.salary)

    # staff.restaurants.clear()

    # staff.restaurants.add(Restaurant.objects.first())
    # staff.restaurants.add(Restaurant.objects.last())

    # sr = StaffRestaurant.objects.get(staff=staff, restaurant=restaurant)
    # sr.salary = 10_000
    # sr.save()

    # restaurant_9 = Restaurant.objects.get(pk=9)
    # staff.restaurants.add(restaurant_9, through_defaults={'salary': 18_000})
    
# ==================================   ManyToManyField  ========================================
    # restaurant = Restaurant.objects.get(pk=26)
    # print(restaurant.staff_set.all())
    # print(restaurant.staff_set.add(Staff.objects.first(), Staff.objects.last()))
    # print(restaurant.staff_set.remove(Staff.objects.first()).all())
    # print(restaurant.staff_set.clear())

# ===============================================================================================
    # staff, created = Staff.objects.get_or_create(name='John Doe', defaults={'name': 'John Doe'})
    
    # staff.restaurants.add(Restaurant.objects.first())
    # staff.restaurants.set(Restaurant.objects.all()[:5])     # set() 'John Doe' to 5 restaurants

    # staff.restaurants.remove(Restaurant.objects.first())
    # staff.restaurants.clear()                                # clear() 'John Doe' from all restaurants

    # italian = staff.restaurants.filter(restaurant_type=Restaurant.TypeChoices.ITALIAN)

# ===============================================================================================
    # sales = Sale.objects.filter(restaurant__restaurant_type='IN')
    # print(sales)

# ===============================================================================================
    # ratings = Rating.objects.filter(restaurant__name__contains='Pizzeria')
    # print(ratings)

# ===============================================================================================
    # restaurant = Restaurant.objects.earliest('date_opened')
    # restaurant = Restaurant.objects.latest('date_opened')
    # print(restaurant)

    # restaurant = Restaurant.objects.get_or_create(
    #                         name='Sushi', 
    #                         defaults={'name': 'Sushi', 'date_opened': timezone.now()},
    #                         restaurant_type=Restaurant.TypeChoices.ITALIAN)

# ===============================================================================================
    # r = Restaurant.objects.all().first()
    # r.name = r.name.lower()
    # r.save()

# ===============================================================================================
    # restaurants = Restaurant.objects.order_by(Lower('name'))
    # restaurants = Restaurant.objects.order_by('date_opened')[0:5]
    # print(restaurants)

# ===============================================================================================
    # sales = Sale.objects.order_by('-date_time')
    # print(sales)

# ===============================================================================================
    # restaurants = Restaurant.objects.order_by('name').reverse()
    # print(restaurants)
    # restaurant = Restaurant.objects.order_by('name').first()
    # print(restaurant)

# ===============================================================================================
    # #sales = Sale.objects.filter(income__range=(50, 60)).values_list('restaurant__name', flat=100)
    # sales = Sale.objects.filter(income__range=(50, 60))
    # print([sale.income for sale in sales])

# ===============================================================================================
    # restaurants = Restaurant.objects.filter(name__lt='E')
    # print(restaurants)

# ===============================================================================================
    # chinese = Restaurant.TypeChoices.CHINESE
    # mexican = Restaurant.TypeChoices.MEXICAN
    # indian = Restaurant.TypeChoices.INDIAN
    # restaurant_types = [chinese, mexican, indian]
    # restaurants = Restaurant.objects.exclude(restaurant_type__in=restaurant_types)
    # restaurants = Restaurant.objects.exclude(restaurant_type__in=[chinese, mexican, indian])
    # print(restaurants)

# ===============================================================================================
    # chinese = Restaurant.TypeChoices.CHINESE
    # mexican = Restaurant.TypeChoices.MEXICAN
    # indian = Restaurant.TypeChoices.INDIAN
    # restaurant_types = [chinese, mexican, indian]
    # restaurants = Restaurant.objects.filter(restaurant_type__in=restaurant_types)
    # print(restaurants.count())

# ===============================================================================================
    # chinese = Restaurant.TypeChoices.CHINESE
    # restaurants = Restaurant.objects.filter(restaurant_type=chinese, name__startswith='C')
    # print(restaurants)
# ===============================================================================================
    # print(Restaurant.objects.filter(restaurant_type=Restaurant.TypeChoices.CHINESE).count())

    # restaurants = Restaurant.objects.filter(restaurant_type=Restaurant.TypeChoices.CHINESE)
    # print(restaurants.exists())

    # Restaurant.objects.filter(name__startswith='A').delete()

# ===============================================================================================
    # print(Restaurant.objects.count())
    # print(Rating.objects.count())
    # print(Sale.objects.count())

# ===============================================================================================
    # restaurants = Restaurant.objects.filter(name__startswith='A')
    # restaurants.update(
    #     date_opened=timezone.now() - timezone.timedelta(days=355),
    #     website='https://www.google.com'
    # )
# ===============================================================================================
    # restaurant = Restaurant.objects.first()
    # print(restaurant.pk)
    # print(restaurant.ratings.all())

    # restaurant.delete()
    # Restaurant.objects.all().delete()

# ===============================================================================================
    # user = User.objects.create_user(
    #     username="admin",
    #     password="admin",
    # )
# ==============================================================================================
    # user=User.objects.get(id=2)
    # restaurant=Restaurant.objects.first()
    # rating = Rating(user=user, restaurant=restaurant, rating=2)
    # rating.full_clean() #it runs validation
    # rating.save()

# ===============================================================================================
    # user=User.objects.first(),
    # restaurant=Restaurant.objects.first()
    # rating, created = Rating.objects.get_or_create(
    #     user=user,
    #     restaurant=restaurant,
    #     rating=4
    # )
    # if created:
    #     """write some code here"""
# ==============================================================================================
    # restaurant = Restaurant.objects.first()
    # user = User.objects.first()
    # print(Rating.objects.get_or_create(restaurant=restaurant, user=user, rating=4))

    # restaurant = Restaurant.objects.first()
    # print(restaurant.sales.all())
# ===============================================================================================
    # sales = Sale.objects.create(
    #     restaurant=Restaurant.objects.first(),
    #     income=1000,
    #     date_time=timezone.now()
    # )
    # sales = Sale.objects.create(
    #     restaurant=Restaurant.objects.first(),
    #     income=1460,
    #     date_time=timezone.now()
    # )
# ===============================================================================================
    # restaurant = Restaurant.objects.first()
    # print(restaurant.rating_set.all())
    # !!! after <related_name='ratings'> in Restaurant model  !!!
    # print(restaurant.ratings.all())
# ===============================================================================================
    # rating = Rating.objects.first()
    # print(rating.rating)
    # print(rating.restaurant)
    # print(rating.user.username)

    # restaurant = Restaurant.objects.first()
    # print(restaurant.name)
    # restaurant.name = 'Florence' /// restaurant.save(update_fields=['name'])
    # restaurant.save()
# =================================================================================================
    # print(Rating.objects.filter(rating__gt=3))
    # print(Rating.objects.exclude(rating__gt=3))
    # print(Rating.objects.filter(rating=3))
    # print(Rating.objects.filter(rating=5).count())

    # user = User.objects.first()
    # restaurant = Restaurant.objects.first()
    # rating = Rating.objects.create(user=user, restaurant=restaurant, rating=5)

    # restaurant = Restaurant.objects.create(
    #     name='Athena',
    #     latitude = 45.438,
    #     longitude = 12.33,
    #     date_opened = timezone.now(),
    #     restaurant_type = Restaurant.TypeChoices.GREEK
    # )
    
    # restaurant.name = 'Verona'
    # restaurant.latitude = 45.438
    # restaurant.longitude = 12.33
    # restaurant.date_opened = timezone.now()
    # restaurant.restaurant_type = Restaurant.TypeChoices.ITALIAN
    # restaurant.save()

    # print(connection.queries)
