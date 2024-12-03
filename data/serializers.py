from rest_framework import serializers
from accounts.models import User  # accounts app dan User modelini import qiling

from django.core.files.base import ContentFile
import base64
import six
import uuid

from .models import (
    MainData, InformativeData, FinancialData, ObjectPhoto, AllData,
    InvestorInfo, Category, Area, SmartNote, Currency, Faq, CadastralPhoto, ProductPhoto, Status, Image, Video
)


class AllDataProSerializer(serializers.ModelSerializer):
    cat_name = serializers.SerializerMethodField()
    cat_id = serializers.SerializerMethodField()

    class Meta:
        model = AllData
        fields = ('id', 'main_data', 'informative_data', 'financial_data', 'date_created', 'cat_name', 'cat_id')

    def get_cat_name(self, obj):
        main_data = obj.main_data
        if main_data and main_data.category:
            return main_data.category.category
        return None

    def get_cat_id(self, obj):
        main_data = obj.main_data
        if main_data and main_data.category:
            return main_data.category.id
        return None


class CategoryApiSerializer(serializers.ModelSerializer):
    main_data = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'category', 'main_data')
        read_only_fields = ('id',)

    def get_main_data(self, obj):
        main_data_objects = obj.main_data.all()

        serializer = MainDataSerializer(main_data_objects, many=True)

        return serializer.data


class AreaAPISerializer(serializers.ModelSerializer):
    main_data = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = ('id', 'location', 'main_data')
        read_only_fields = ('id',)

    def get_main_data(self, obj):
        main_data_objects = obj.main_data.all()

        serializer = MainDataSerializer(main_data_objects, many=True)

        return serializer.data


class MainDataAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = MainData
        fields = ['enterprise_name', 'legal_form', 'location', 'lat', 'long', 'field_of_activity',
                  'infrastructure', 'project_staff', 'category', 'user']


class MainDataAPISerializer(serializers.ModelSerializer):
    location = serializers.PrimaryKeyRelatedField(queryset=Area.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = MainData
        fields = ['enterprise_name', 'legal_form', 'location', 'lat', 'long', 'field_of_activity', 'infrastructure',
                  'project_staff', 'category', 'is_validated', 'user']


class MainDataSerializer(serializers.Serializer):
    enterprise_name = serializers.CharField(max_length=30)
    legal_form = serializers.CharField(max_length=30)
    location = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Area.objects.all())
    lat = serializers.DecimalField(max_digits=22, decimal_places=18)
    long = serializers.DecimalField(max_digits=22, decimal_places=18)
    field_of_activity = serializers.CharField(max_length=30)
    infrastructure = serializers.CharField(max_length=30)
    project_staff = serializers.DecimalField(max_digits=4, decimal_places=0)
    category = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Category.objects.all())


class AlldateCategorySerializer(serializers.ModelSerializer):
    main_name = serializers.SerializerMethodField()
    formation = serializers.SerializerMethodField()
    main_cat = serializers.SerializerMethodField()
    main_obj_photo = serializers.SerializerMethodField()
    main_area = serializers.SerializerMethodField()

    class Meta:
        model = AllData
        fields = ('id', 'main_name', 'formation', 'main_cat', 'main_obj_photo', 'main_area')  # `main_cat` ni qo'shdim

    def get_main_name(self, obj):
        return obj.main_data.enterprise_name

    def get_formation(self, obj):
        return obj.informative_data.formation_date

    def get_main_cat(self, obj):
        if obj.main_data.category:  # agar main_data da category mavjud bo'lsa
            return obj.main_data.category.category
        else:
            return None

    def get_main_area(self, obj):
        if obj.main_data.location:  # agar main_data da category mavjud bo'lsa
            return obj.main_data.location.location
        else:
            return None

    def get_main_obj_photo(self, obj):
        informative_model_photos = obj.informative_data.object_foto.all()
        request = self.context.get('request')
        if request is None:
            return None
        image_urls = [request.build_absolute_uri(photo.image.url) for photo in informative_model_photos]
        return image_urls


class AreaAPISerializer(serializers.ModelSerializer):
    main_data = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = ('id', 'location', 'main_data')
        read_only_fields = ('id',)

    def get_main_data(self, obj):
        main_data_objects = obj.main_data.all()

        serializer = MainDataSerializer(main_data_objects, many=True)

        return serializer.data


class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    def to_internal_value(self, data):

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension,)

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class ObjectPhotoSerializer(serializers.ModelSerializer):
    # image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = ObjectPhoto
        fields = ('image',)


class InformativeDataSerializer(serializers.Serializer):
    product_info = serializers.CharField(max_length=30)
    project_capacity = serializers.CharField(max_length=30)
    formation_date = serializers.DateTimeField()
    total_area = serializers.DecimalField(max_digits=6, decimal_places=0)
    building_area = serializers.DecimalField(max_digits=6, decimal_places=0)
    tech_equipment = serializers.CharField(max_length=30)
    product_photo = Base64ImageField(max_length=None, use_url=True)
    cadastral_info = Base64ImageField(max_length=None, use_url=True)


# Temur

class CadastraInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CadastralPhoto
        fields = ('id', 'informative_data', 'image',)


class ProductPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhoto
        fields = ('id', 'informative_data', 'image',)


class InformativeProDataSerializer(serializers.ModelSerializer):
    cadastral_info_list = CadastraInfoSerializer(many=True, read_only=True)
    product_photo_list = ProductPhotoSerializer(many=True, read_only=True)
    object_foto = ObjectPhotoSerializer(many=True, read_only=True)

    cadastral_info = serializers.ListField(
        child=serializers.ImageField(max_length=1000, allow_empty_file=False, use_url=False),
        write_only=True
    )
    product_photo = serializers.ListField(
        child=serializers.ImageField(max_length=1000, allow_empty_file=False, use_url=False),
        write_only=True
    )

    object_photo = serializers.ListField(
        child=serializers.ImageField(max_length=1000, allow_empty_file=False, use_url=False),
        write_only=True
    )

    class Meta:
        model = InformativeData
        fields = ('product_info', 'project_capacity', 'total_area', 'formation_date',
                  'building_area', 'tech_equipment',
                  'cadastral_info', 'product_photo', 'object_photo',
                  'object_foto', 'cadastral_info_list', 'product_photo_list')

    def update(self, instance, validated_data):
        cadastral_info_data = validated_data.pop('cadastral_info', [])
        product_photo_data = validated_data.pop('product_photo', [])
        object_photos_data = validated_data.pop('object_photo', [])

        # Obyektni yangilash
        instance.product_info = validated_data.get('product_info', instance.product_info)
        instance.project_capacity = validated_data.get('project_capacity', instance.project_capacity)
        instance.total_area = validated_data.get('total_area', instance.total_area)
        instance.formation_date = validated_data.get('formation_date', instance.formation_date)
        instance.building_area = validated_data.get('building_area', instance.building_area)
        instance.tech_equipment = validated_data.get('tech_equipment', instance.tech_equipment)
        instance.save()

        instance.cadastral_info_list.all().delete()
        # CadastralPhoto obyektlarini yaratish va informative_data ni bog'lash
        [CadastralPhoto.objects.create(image=image_data, informative_data=instance) for
         image_data in cadastral_info_data]
        instance.product_photo_list.all().delete()

        [ProductPhoto.objects.create(image=photo_data, informative_data=instance) for
         photo_data in product_photo_data]
        instance.object_foto.all().delete()

        [ObjectPhoto.objects.create(image=obhect_data, informative_data=instance) for
         obhect_data in object_photos_data]

        return instance


class FinancialDataSerializer(serializers.Serializer):
    export_share = serializers.DecimalField(max_digits=18, decimal_places=4)
    authorized_capital = serializers.DecimalField(max_digits=18, decimal_places=4)
    estimated_value = serializers.DecimalField(max_digits=18, decimal_places=4)
    investment_or_loan_amount = serializers.DecimalField(max_digits=18, decimal_places=4)
    investment_direction = serializers.CharField(max_length=30)
    major_shareholders = serializers.CharField(max_length=30)
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())

    def update(self, instance, validated_data):
        # Validated data bilan o'zgaruvchilarni yangilash
        instance.export_share = validated_data.get('export_share', instance.export_share)
        instance.authorized_capital = validated_data.get('authorized_capital', instance.authorized_capital)
        instance.estimated_value = validated_data.get('estimated_value', instance.estimated_value)
        instance.investment_or_loan_amount = validated_data.get('investment_or_loan_amount',
                                                                instance.investment_or_loan_amount)
        instance.investment_direction = validated_data.get('investment_direction', instance.investment_direction)
        instance.major_shareholders = validated_data.get('major_shareholders', instance.major_shareholders)
        instance.currency = validated_data.get('currency', instance.currency)

        # O'zgarishlarni saqlash
        instance.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class MainDataRetrieveSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    class Meta:
        model = MainData
        fields = '__all__'

    def get_category(self, object):
        return object.category.category if object.category else None

    def get_location(self, object):
        return object.location.location if object.location else None


class InformativeDataRetrieveSerializer(serializers.ModelSerializer):
    object_photos = ObjectPhotoSerializer(many=True)

    class Meta:
        model = InformativeData
        fields = (
            'id',
            'product_info',
            'project_capacity',
            'formation_date',
            'total_area',
            'building_area',
            'tech_equipment',
            'product_photo',
            'cadastral_info',
            'user',
            'object_photos'
        )


class FinancialDataRetrieveCustomSerializer(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()

    class Meta:
        model = FinancialData
        fields = '__all__'

    def get_currency(self, object):
        return object.currency.code


class FinancialDataRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialData
        fields = '__all__'


# ASADBEK
class InformativeProDataSerializerGet(serializers.ModelSerializer):
    cadastral_info_list = CadastraInfoSerializer(many=True, read_only=True)
    product_photo_list = ProductPhotoSerializer(many=True, read_only=True)
    object_foto = ObjectPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = InformativeData
        fields = ('product_info', 'project_capacity', 'total_area', 'formation_date',
                  'building_area', 'tech_equipment', 'object_foto',
                  'cadastral_info_list', 'product_photo_list')


class AllDataSerializer(serializers.ModelSerializer):
    main_data = MainDataRetrieveSerializer()
    informative_data = InformativeProDataSerializerGet()  # InformativeDataRetrieveSerializer() old version
    financial_data = FinancialDataRetrieveCustomSerializer()

    class Meta:
        model = AllData
        fields = (
            'id',
            'user',
            'main_data',
            'informative_data',
            'financial_data',
            'status',
            'date_created',
        )


class AllDataFilterSerializer(serializers.ModelSerializer):
    lat = serializers.SerializerMethodField()
    long = serializers.SerializerMethodField()

    class Meta:
        model = AllData
        fields = ('id', 'lat', 'long')

    def get_lat(self, object):
        return object.main_data.lat

    def get_long(self, object):
        return object.main_data.long


class MainDataDraftSerializer(serializers.Serializer):
    enterprise_name = serializers.CharField(max_length=256, allow_null=True, allow_blank=True, default='')
    legal_form = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    location = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Area.objects.all())
    lat = serializers.DecimalField(max_digits=22, decimal_places=18, default=0)
    long = serializers.DecimalField(max_digits=22, decimal_places=18, default=0)
    field_of_activity = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    infrastructure = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    project_staff = serializers.DecimalField(max_digits=4, decimal_places=0, default=0)
    category = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Category.objects.all())


class InformativeDataDraftSerializer(serializers.Serializer):
    product_info = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    project_capacity = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    formation_date = serializers.DateTimeField(allow_null=True, default=None)
    total_area = serializers.DecimalField(max_digits=6, decimal_places=0, default=0)
    building_area = serializers.DecimalField(max_digits=6, decimal_places=0, default=0)
    tech_equipment = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    # product_photo = serializers.ImageField(allow_null=True, default=None)
    # cadastral_info = serializers.FileField(allow_null=True, default=None)
    product_photo = Base64ImageField(max_length=None, use_url=True, allow_null=True, default=None)
    cadastral_info = Base64ImageField(max_length=None, use_url=True, allow_null=True, default=None)


class FinancialDataDraftSerializer(serializers.Serializer):
    export_share = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    authorized_capital = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    estimated_value = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    investment_or_loan_amount = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    investment_direction = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    major_shareholders = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())


# class InvestmentDraftSerializer(serializers.Serializer):
#     export_share_product = serializers.DecimalField(max_digits=6, decimal_places=0, default=0)
#     authorized_capital = serializers.DecimalField(max_digits=6, decimal_places=0, default=0)
#     company_value = serializers.DecimalField(max_digits=6, decimal_places=0, default=0)
#     investment_amount = serializers.DecimalField(max_digits=6, decimal_places=0, default=0)
#     investment_direction = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
#     principal_founders = serializers.CharField(max_length=1024, allow_null=True, allow_blank=True, default='')
#     all_data = serializers.IntegerField()


class InvestorInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorInfo
        fields = ('user_name', 'email', 'user_phone', 'message', 'file', 'all_data')


class InvestorInfoOwnSerializer(serializers.ModelSerializer):
    enterprise_name = serializers.SerializerMethodField()
    id_object = serializers.SerializerMethodField()

    class Meta:
        model = InvestorInfo
        fields = ('enterprise_name', 'id_object', 'message', 'date_created', 'status')

    def get_enterprise_name(self, object):
        return object.all_data.main_data.enterprise_name

    def get_id_object(self, object):
        return object.all_data.id


class ApproveRejectInvestorSerializer(serializers.Serializer):
    investor_id = serializers.IntegerField()
    all_data_id = serializers.IntegerField()
    is_approve = serializers.BooleanField()


class InvestorInfoGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorInfo
        fields = '__all__'


class InvestorInfoGetMinimumSerializer(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()

    class Meta:
        model = InvestorInfo
        fields = ('user_name', 'id', 'date_created', 'message')

    def get_message(self, object):
        return object.message[:87] + '...'


class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainData
        fields = ('lat', 'long',)


class ObjectIdAndCoordinatesSerializer(serializers.ModelSerializer):
    main_data = CoordinatesSerializer()

    class Meta:
        model = AllData
        fields = (
            'id',
            'main_data',
        )


class AllDataListSerializer(serializers.ModelSerializer):
    enterprise_name = serializers.SerializerMethodField()

    class Meta:
        model = AllData
        fields = (
            'id',
            'enterprise_name',
            'status',
            'date_created',
        )

    def get_enterprise_name(self, object):
        return object.main_data.enterprise_name


class AllDataAllUsersListSerializer(serializers.ModelSerializer):
    enterprise_name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    product_info = serializers.SerializerMethodField()

    class Meta:
        model = AllData
        fields = (
            'id',
            'enterprise_name',
            'image',
            'product_info',
        )

    def get_enterprise_name(self, object):
        return object.main_data.enterprise_name

    def get_image(self, object):
        image = object.informative_data.object_photos.all().first()
        return_image = ''
        if image is not None:
            return_image = image.image.url

        return return_image

    def get_product_info(self, object):
        return object.informative_data.product_info


class LocationSerializer(serializers.Serializer):
    lat = serializers.DecimalField(max_digits=22, decimal_places=18)
    long = serializers.DecimalField(max_digits=22, decimal_places=18)

class ImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['id', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url  # request yo'q bo'lsa faqat nisbiy URL qaytariladi


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'video']

    def get_video(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.video.url)
        return obj.video.url


class SmartNoteCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(max_length=1000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
        allow_null=True
    )
    videos = serializers.ListField(
        child=serializers.FileField(max_length=1000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
        allow_null=True
    )
    images_list = ImageSerializer(many=True, read_only=True)
    videos_list = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = SmartNote
        fields = ['id', 'main_data', 'text', 'name', 'custom_id', 'user', 'create_date_note', 'images', 'videos',
                  'images_list', 'videos_list']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        videos_data = validated_data.pop('videos', [])

        # SmartNote obyektini yaratish
        smart_note = SmartNote.objects.create(**validated_data)

        # Rasmlar va videolarni qo'shish
        if images_data:
            for image_file in images_data:
                Image.objects.create(smart_note=smart_note, image=image_file)

        if videos_data:
            for video_file in videos_data:
                Video.objects.create(smart_note=smart_note, video=video_file)

        return smart_note

    # def update(self, instance, validated_data):
    #     images_data = validated_data.pop('images', None)
    #     videos_data = validated_data.pop('videos', None)
    #
    #     instance.main_data = validated_data.get('main_data', instance.main_data)
    #     instance.text = validated_data.get('text', instance.text)
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.custom_id = validated_data.get('custom_id', instance.custom_id)
    #     instance.user = validated_data.get('user', instance.user)
    #     instance.create_date_note = validated_data.get('create_date_note', instance.create_date_note)
    #     instance.save()
    #
    #     if images_data is not None:
    #         instance.images.all().delete()  # eski rasm fayllarini o'chirish
    #         images_to_create = [Image(smart_note=instance, **image_data) for image_data in images_data]
    #         Image.objects.bulk_create(images_to_create)
    #
    #     if videos_data is not None:
    #         instance.videos.all().delete()  # eski video fayllarini o'chirish
    #         videos_to_create = [Video(smart_note=instance, **video_data) for video_data in videos_data]
    #         Video.objects.bulk_create(videos_to_create)
    #
    #     return instance

class SmartNoteMainDataSerializer(serializers.ModelSerializer):
    enterprise_name = serializers.CharField(source='main_data.enterprise_name', read_only=True)

    class Meta:
        model = MainData
        fields = ('id', 'enterprise_name')


class SmartNoteListRetrieveSerializer(serializers.ModelSerializer):
    main_data = SmartNoteMainDataSerializer()
    enterprise_name = serializers.SerializerMethodField()
    images = ImageSerializer(many=True, read_only=True)  # 'images' related_name dan foydalaniladi
    videos = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = SmartNote
        fields = ('id', 'enterprise_name', 'main_data', 'text', 'name', 'create_date_note', 'custom_id', 'images', 'videos')

    def get_enterprise_name(self, object):
        main_data = object.main_data
        if main_data and main_data.enterprise_name:
            return main_data.enterprise_name
        else:
            return None


class SmartNoteUpdateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(max_length=1000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
        allow_null=True
    )
    videos = serializers.ListField(
        child=serializers.FileField(max_length=1000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
        allow_null=True
    )
    images_list = ImageSerializer(many=True, read_only=True)
    videos_list = VideoSerializer(many=True, read_only=True)
    class Meta:
        model = SmartNote
        fields = ('text', 'name', 'create_date_note', 'custom_id', 'images', 'videos',
                  'images_list', 'videos_list')

    def update(self, instance, validated_data):
        # Yangilash uchun maydonlarni ajratish
        images_data = validated_data.pop('images', None)
        videos_data = validated_data.pop('videos', None)

        # Yangilash
        instance.main_data = validated_data.get('main_data', instance.main_data)
        instance.text = validated_data.get('text', instance.text)
        instance.name = validated_data.get('name', instance.name)
        instance.custom_id = validated_data.get('custom_id', instance.custom_id)
        instance.user = validated_data.get('user', instance.user)
        instance.create_date_note = validated_data.get('create_date_note', instance.create_date_note)
        instance.save()

        # Rasmlar va videolarni yangilash yoki qo'shish
        if images_data is not None:  # Faqat yangi rasmlar yuborilganida
            instance.images.all().delete()  # Oldingi rasmlarni o'chirish
            for image_file in images_data:
                if image_file:
                    Image.objects.create(smart_note=instance, image=image_file)

        if videos_data is not None:  # Faqat yangi videolar yuborilganida
            instance.videos.all().delete()  # Oldingi videolarni o'chirish
            for video_file in videos_data:
                if video_file:
                    Video.objects.create(smart_note=instance, video=video_file)

        return instance


class CustomIdSerializer(serializers.Serializer):
    custom_id = serializers.CharField(max_length=30, allow_null=True, allow_blank=True)


class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = '__all__'


# ASADbek


class InformativeDataGetSerializer(serializers.ModelSerializer):
    cadastral_info_list = CadastraInfoSerializer(many=True, read_only=True)
    product_photo_list = ProductPhotoSerializer(many=True, read_only=True)
    object_foto = ObjectPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = InformativeData
        fields = ('id', 'product_info', 'project_capacity', 'formation_date',
                  'total_area', 'building_area', 'tech_equipment',
                  'user', 'is_validated', 'object_foto', 'cadastral_info_list', 'product_photo_list')


class CategoryApiProSerializer(serializers.ModelSerializer):
    alldata = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'category_uz', 'category_ru', 'category_en', 'alldata',)
        read_only_fields = ('id',)

    def get_alldata(self, obj):
        all_data_objects = AllData.objects.filter(main_data__category=obj, status=Status.APPROVED)
        serializer = AlldateCategorySerializer(all_data_objects, many=True, context=self.context)
        return serializer.data


class AreaAPIDetailSerializer(serializers.ModelSerializer):
    main_data = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = ('id', 'location', 'lat', 'long', 'main_data',)

    def get_main_data(self, obj):
        return list(obj.main_data.all().values('id', 'lat', 'long', 'location'))
