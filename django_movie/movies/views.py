from django.db import models

from django_filters.rest_framework import DjangoFilterBackend

# from rest_framework.response import Response
# from rest_framework.views import APIView
from rest_framework import generics,permissions

from .models import Movie, Actor
from .serializers import MovieListSerializer, MovieDetailSerializer, ReviewCreateSerializer, CreateRatingSerializer, \
    ActorsListSerializer, ActorDetailSerializer
from .service import get_client_ip
from .filters import MovieFilter


class MovieListView(generics.ListAPIView):
    """Вывод списка фильмов"""
    serializer_class = MovieListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MovieFilter
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        movies = Movie.objects.filter(draft=False).annotate(
            user_rating=models.Count('ratings', filter=models.Q(ratings__ip=get_client_ip(self.request)))
        ).annotate(
            average_rating=models.Avg('ratings__star')
        )
        return movies


# см. выше. переделан под generics
# class MovieListView(APIView):
#     """Вывод списка фильмов"""
#
#     def get(self, request):
#         movies = Movie.objects.filter(draft=False).annotate(
#             user_rating=models.Count('ratings', filter=models.Q(ratings__ip=get_client_ip(request)))
#         ).annotate(
#             average_rating=models.Avg('ratings__star')
#         )
#         serializer = MovieListSerializer(movies, many=True)
#         return Response(serializer.data)


class MovieDetailView(generics.RetrieveAPIView):
    """Вывод информации о фильме"""
    queryset = Movie.objects.filter(draft=False)
    serializer_class = MovieDetailSerializer


# см. выше. переделан под generics
# class MovieDetailView(APIView):
#     """Вывод информации о фильме"""
#
#     def get(self, request, pk):
#         movie = Movie.objects.get(id=pk, draft=False)
#         serializer = MovieDetailSerializer(movie)
#         return Response(serializer.data)

class ReviewCreateView(generics.CreateAPIView):
    """Добавление отзыва к фильму"""
    serializer_class = ReviewCreateSerializer


# см. выше. переделан под generics
# class ReviewCreateView(APIView):
#     """Добавление отзыва к фильму"""
#
#     def post(self, request):
#         review = ReviewCreateSerializer(data=request.data)
#         if review.is_valid():
#             review.save()
#             return Response(status=201)

class AddRatingStarView(generics.CreateAPIView):
    serializer_class = CreateRatingSerializer

    def perform_create(self, serializer):
        serializer.save(ip=get_client_ip(self.request))


# см. выше. переделан под generics
# class AddRatingStarView(APIView):
#     def post(self, request):
#         serializer = CreateRatingSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(ip=get_client_ip(request))
#             return Response(status=201)
#         else:
#             return Response(status=400)


class ActorsListView(generics.ListAPIView):
    """Вывод списка актёров и режиссёров"""
    queryset = Actor.objects.all()
    serializer_class = ActorsListSerializer


class ActorDetailView(generics.RetrieveAPIView):
    """Вывод полного описания актёра или режиссёра"""
    queryset = Actor.objects.all()
    serializer_class = ActorDetailSerializer
