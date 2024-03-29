from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recommendation_list.models.recommendations import RecommendationList, Favorites, Recommendation, CategoryEnum, \
    Likes
from recommendation_list.models.tags import Tag
from recommendation_list.serializers.tags_serializers import TagSerializer
from user.serializers import CustomUserSerializer
from django_enum_choices.serializers import EnumChoiceField


class RecommendationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recommendation
        fields = ['id', 'text', 'photo']


class RelatedCustomUserField(CustomUserSerializer):
    def to_internal_value(self, data):
        return data


class RecommendationListSerializer(serializers.ModelSerializer):
    recommendations = RecommendationSerializer(many=True, required=True)
    user = RelatedCustomUserField()
    category = EnumChoiceField(CategoryEnum)
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = RecommendationList
        fields = ['id', 'recommendations', 'tags', 'user', 'is_draft', 'photo', 'category', 'header']
        extra_kwargs = {
            'tags': {'required': False}
        }

    def create(self, validated_data):
        recommendations = validated_data.pop('recommendations')
        tags = validated_data.pop('tags', [])
        recommendation_list = super().create(validated_data)
        recs = []
        for recommendation in recommendations:
            recommendation['recommendation_list'] = recommendation_list
            recs.append(Recommendation(**recommendation))
        Recommendation.objects.bulk_create(recs)
        for tag in tags:
            new_tag, created = Tag.objects.get_or_create(name=tag['name'])
            recommendation_list.tags.add(new_tag)
        return recommendation_list

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.clear()
            for tag in tags:
                new_tag, created = Tag.objects.get_or_create(name=tag['name'])
                instance.tags.add(new_tag)
        if 'recommendations' in validated_data:
            recommendations = validated_data.pop('recommendations')
            recs = []
            for recommendation in recommendations:
                recommendation['recommendation_list'] = instance
                recs.append(Recommendation(**recommendation))
            Recommendation.objects.bulk_create(recs)
        return super().update(instance, validated_data)


class FavoritesCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorites
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorites.objects.all(),
                fields=['recommendation_list', 'user']
            )
        ]


class LikesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Likes
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Likes.objects.all(),
                fields=['recommendation_list', 'user']
            )
        ]
