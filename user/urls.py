from .views.user.urls import urlpatterns as user_urls
from .views.another.urls import urlpatterns as another_urls

urlpatterns = []

urlpatterns += user_urls
urlpatterns += another_urls

