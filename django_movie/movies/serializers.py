from rest_framework import serializers

from .models import Movie, Review, Rating, Actor


class FilterReviewListSerializer(serializers.ListSerializer):
    """Фильтер комментариев, только parents"""

    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)


class RecursiveSerializer(serializers.Serializer):
    """Вывод рекурсивно children"""

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class ActorsListSerializer(serializers.ModelSerializer):
    """Вывод списка актёров и режиссёров"""

    class Meta:
        model = Actor
        fields = ('id', 'name', 'image')


class ActorDetailSerializer(serializers.ModelSerializer):
    """Вывод полного описания актёра или режиссёра"""

    class Meta:
        model = Actor
        fields = '__all__'


class MovieListSerializer(serializers.ModelSerializer):
    """Список фильмов"""
    user_rating = serializers.BooleanField()
    average_rating = serializers.FloatField()

    class Meta:
        model = Movie
        fields = ('id', 'title', 'tagline', 'category', 'user_rating', 'average_rating')


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Добавление отзыва"""

    class Meta:
        model = Review
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Вывод отзывов"""
    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterReviewListSerializer
        model = Review
        fields = ('name', 'text', 'children')


class MovieDetailSerializer(serializers.ModelSerializer):
    """Детали фильма"""
    category = serializers.SlugRelatedField(slug_field='name', read_only='True')
    actors = ActorsListSerializer(read_only='True', many=True)
    directors = ActorsListSerializer(read_only='True', many=True)
    genres = serializers.SlugRelatedField(slug_field='name', read_only='True', many=True)
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        exclude = ('draft',)


class CreateRatingSerializer(serializers.ModelSerializer):
    """Создание рейтинга пользователя"""

    def create(self, validated_data):
        rating, _ = Rating.objects.update_or_create(
            ip=validated_data.get('ip', None),
            movie=validated_data.get('movie', None),
            defaults={'star': validated_data.get('star')}
        )
        # сериализатор был переделан под generics, поэтому здесь теперь кортеж
        # rating = Rating.objects.update_or_create(
        #     ip=validated_data.get('ip', None),
        #     movie=validated_data.get('movie', None),
        #     defaults={'star': validated_data.get('star')}
        # )
        return rating

    class Meta:
        model = Rating
        fields = ('star', 'movie')
