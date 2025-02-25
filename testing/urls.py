from django.urls import path

from . import views

urlpatterns = [
path("",views.home,name="Home"),
path("fishlist/",views.fish_list_view,name="FishList"),
path("fishlist/space/<int:space_id>/", views.fish_list_view, name="FishListBySpace"),
path("balance/",views.balance,name="Money"),
path("about/",views.about,name="AboutUs"),
path('clear_fish_log/', views.clear_fish_log, name='clear_fish_log'),
path('clear_money_log/', views.clear_money_log, name='clear_money_log'),
]

