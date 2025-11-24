from requests import Response
from rest_framework import serializers
from tour.models import CancellationPolicy, PenaltyRules, TourItinerary, Tour, DayTourPrice, AvailableDate, AvailableTime, TourContentImage
from datetime import datetime
from django_currentuser.middleware import get_current_authenticated_user

from tour.serializers.tour_itinerary_serializers import TourItineraryListSerializer, TourItinerarySerializer

class AvailableDateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    date = serializers.DateField(
            input_formats=["%Y-%m-%d", "%m/%d/%Y"],  # Accept both formats
            format="%m/%d/%Y"
        )
    class Meta:
        model = AvailableDate 
        fields = ['id', 'date']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['date'] = instance.date.strftime("%m/%d/%Y")
        return rep

class AvailableTimeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    time = serializers.TimeField(
        input_formats=["%H:%M:%S", "%I:%M %p"],  # Accept both formats
        format="%I:%M %p"
    )
    class Meta:
        model = AvailableTime
        fields = ['id', 'time']
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['time'] = instance.time.strftime("%I:%M %p")
        return rep

class DayTourPriceListSerializer(serializers.ModelSerializer):
    # available_dates = serializers.SerializerMethodField()
    # available_times = serializers.SerializerMethodField()
    available_dates = AvailableDateSerializer(many=True)
    available_times = AvailableTimeSerializer(many=True)

    class Meta:
        model = DayTourPrice
        fields = ['id', 'price_per_person', 'group_price', 'guide', 'available_dates', 'available_times']

    # def get_available_dates(self, obj):
    #     return [str(date.date.strftime("%m/%d/%Y")) for date in obj.available_dates.all()]

    # def get_available_times(self, obj):
    #     return [str(time.time.strftime("%I:%M %p")) for time in obj.available_times.all()]
    

class DayTourPriceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    # available_dates = serializers.ListField(child=serializers.CharField(), write_only=True)
    # available_times = serializers.ListField(child=serializers.CharField(), write_only=True)
    available_dates = AvailableDateSerializer(many=True, write_only=True)
    available_times = AvailableTimeSerializer(many=True, write_only=True)
    tour = serializers.PrimaryKeyRelatedField(read_only=True)
    company = serializers.PrimaryKeyRelatedField(read_only=True)

    # available_dates_list = serializers.SerializerMethodField()
    # available_times_list = serializers.SerializerMethodField()

    class Meta:
        model = DayTourPrice
        fields = '__all__'
        # fields = ['id','tour', 'price_per_person', 'group_price', 'guide','available_dates', 'available_times']

    # def get_available_dates_list(self, obj):
    #     return [str(date.date.strftime("%m/%d/%Y")) for date in obj.available_dates.all()]

    # def get_available_times_list(self, obj):
    #     return [str(time.time.strftime("%I:%M %p")) for time in obj.available_times.all()]

    def create(self, validated_data):
        print("validated_data from create method of DayTourPriceSerializer: ", validated_data)
        available_dates = validated_data.pop('available_dates', [])
        available_times = validated_data.pop('available_times', [])
        tour = self.context.get('tour')
        company = self.context.get('company')
        day_tour_price = DayTourPrice.objects.create(tour=tour, company=company, **validated_data)

        # Parse & create AvailableDate objects
        for item in available_dates:
            AvailableDate.objects.create(day_tour_price=day_tour_price, company=company, date=item['date'])

        # Parse & create AvailableTime objects
        for item in available_times:
            AvailableTime.objects.create(day_tour_price=day_tour_price, company=company, time=item['time'])

        return day_tour_price

    def update(self, instance, validated_data):
        # Extract and remove custom fields from validated data
        available_dates = validated_data.pop('available_dates', [])
        existing_date_ids = [item['id'] for item in available_dates if 'id' in item]
        instance.available_dates.exclude(id__in=existing_date_ids).delete()

        available_times = validated_data.pop('available_times', [])
        existing_time_ids = [item['id'] for item in available_times if 'id' in item]
        instance.available_times.exclude(id__in=existing_time_ids).delete()

        # Update basic fields
        instance.price_per_person = validated_data.get('price_per_person', instance.price_per_person)
        instance.group_price = validated_data.get('group_price', instance.group_price)
        instance.guide = validated_data.get('guide', instance.guide)
        instance.save()

        # -------------------------
        # 🗓️ Handle Available Dates
        # -------------------------

        for item in available_dates:
            if 'id' in item:
                date_obj = AvailableDate.objects.get(id=item['id'])
                date_obj.date = item['date']  # already a datetime.date object
                date_obj.save()
            else:
                AvailableDate.objects.create(day_tour_price=instance, date=item['date'])
                
        # -------------------------
        # ⏰ Handle Available Times
        # -------------------------

        for item in available_times:
            if 'id' in item:
                time_obj = AvailableTime.objects.get(id=item['id'])
                time_obj.time = item['time']  # already a datetime.time object
                time_obj.save()
            else:
                AvailableTime.objects.create(day_tour_price=instance, time=item['time'])
        
        return instance

class TourContentImageListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = TourContentImage
        fields = '__all__'
        extra_kwargs = {
            'created_at':{
                'read_only': True,
            },
            'updated_at':{
                'read_only': True,
            },
            'created_by':{
                'read_only': True,
            },
            'updated_by':{
                'read_only': True,
            },
        }

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else obj.created_by
        
    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else obj.updated_by
    

class PenaltyRulesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # add this
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = PenaltyRules
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'cancellation_policy_list')  #jodi model e 'cancellation_policy_list' fild ta k nullable, blankable na kori tahole ei line ta lagbe
        # read_only_fields = ('created_at', 'updated_at')  


class PenaltyRulesListSerializer(serializers.ModelSerializer):    
    # id = serializers.IntegerField(required=False)  # writable id

    class Meta:
        model = PenaltyRules
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
class CancellationPolicySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # writable id
    penalty_rules = PenaltyRulesSerializer(many=True)
    company = serializers.PrimaryKeyRelatedField(read_only=True)


    class Meta:
        model = CancellationPolicy
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'tour')  #jodi model e 'tour' fild ta k nullable, blankable na kori tahole ei line ta lagbe
    
    def create(self, validated_data):
        tour = self.context.get('tour')
        company = self.context.get('company')
        validated_data['tour'] = tour
        validated_data['company'] = company
        print("company from create method of CancellationPolicySerializer : ", company)
        print('\n')
        print("validated_data from create method of CancellationPolicySerializer: ", validated_data)
        penalty_rules = validated_data.pop('penalty_rules', [])
        print("penalty_rules_data from create method of CancellationPolicySerializer: ", penalty_rules)
        print('\n')
        print("after popping penalty_rules from validated_data: ", validated_data)
        print('\n')
        print("validated_data from create method of CancellationPolicySerializer: ", validated_data)
        print('\n')
        cancellation_policy = CancellationPolicy.objects.create(**validated_data)
        print("cancellation_policy object after creation from create method of CancellationPolicySerializer: ", cancellation_policy)
        if len(penalty_rules) > 0:
            for rule_data in penalty_rules:
                print("rule data :", rule_data)
                rule_data['cancellation_policy_list'] = cancellation_policy
                days_before = rule_data.get('days_before', 0)
                hours_before = rule_data.get('hours_before', 0)
                cutoff_hours = (days_before * 24) + hours_before
                rule_data['cutoff_hours'] = cutoff_hours
                rule_data['company'] = company
                print("rule data after calculating cutoff_hours:", rule_data)
                penalty_rule = PenaltyRules.objects.create(**rule_data)
                print("Penalty Rule created:", penalty_rule)
        print("From CancellationPolicySerializer Cancellation Policy created for ->:", cancellation_policy)
        return cancellation_policy
    
    def update(self, instance, validated_data):
        # pop penalty_rules data
        penalty_rules = validated_data.pop('penalty_rules', [])
        print('\n')
        print("penalty rules data from update method of CancellationPolicySerializer: ", penalty_rules)
        # step 1: update basic fields of CancellationPolicy
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        print('\n')
        print(f"Cancellation Policy of id {instance.id} is updated.")

        # step 2: Handle PenaltyRules update
        existing_rules = {rule.id : rule for rule in instance.penalty_rules.all()}
        print("existing rules :", existing_rules)

        sent_rule_ids = []
        for rule_data in penalty_rules:
            print("rule data :", rule_data)
            rule_id = rule_data.get('id', None)

            if rule_id and rule_id in existing_rules:
                # Update existing rule
                penalty_rule = existing_rules[rule_id]
                days_before = rule_data.get('days_before', 0)
                hours_before = rule_data.get('hours_before', 0)
                rule_data['cutoff_hours'] = (days_before * 24) + hours_before
                for attr, value in rule_data.items():
                    setattr(penalty_rule, attr, value)
                penalty_rule.save()
                sent_rule_ids.append(rule_id)
                print(f"Updated penalty rule id is : {rule_id}")
            else:
                # create new rule
                days_before = rule_data.get('days_before', 0)
                hours_before = rule_data.get('hours_before', 0)
                rule_data['cutoff_hours'] = (days_before * 24) + hours_before
                rule_data['cancellation_policy_list'] = instance
                penalty_rule = PenaltyRules.objects.create(**rule_data)
                print(f"Created new penalty rule id is : {penalty_rule.id}")

        # Delete rules not in the update request
        for rule_id, rule in existing_rules.items():
            if rule_id not in sent_rule_ids:
                rule.delete()
                print(f"Deleted penalty rule id is : {rule_id}")

        return instance

class CancellationPolicyListSerializer(serializers.ModelSerializer):
    penalty_rules = PenaltyRulesListSerializer(many=True, read_only=True)
    tour = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CancellationPolicy
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Sort penalty rules by cutoff_hours ascending
        rep['penalty_rules'] = sorted(rep['penalty_rules'], key=lambda x: x['cutoff_hours'])
        return rep

class TourListSerializer(serializers.ModelSerializer):
    day_tour_price_list = DayTourPriceListSerializer(many=True, read_only=True)
    thumbnail_image = serializers.ImageField(write_only=True)
    tour_images = serializers.SerializerMethodField() # jehetu shudhu image gulor list chai
    itineraries_list = TourItineraryListSerializer(many=True, read_only=True)
    cancellation_policies_list = CancellationPolicyListSerializer(many=True, read_only=True)
    class Meta:
        model = Tour
        # fields = ['id', 'name', 'description', 'day_tour_price_list', 'created_at', 'updated_at']
        fields = '__all__'

    def get_tour_images(self, obj):
        tour_images = []
        # as related_name = "tour_images" is in the TourContentImage for asscociated tour.
        all_images = obj.tour_images.all()
        for img in all_images:
            if img.cloudflare_image_url:
                tour_images.append(img.cloudflare_image_url)
        return tour_images


class TourSerializer(serializers.ModelSerializer):
    day_tour_price_list = DayTourPriceSerializer(many=True)
    day_tour_price_list_read = DayTourPriceListSerializer(many=True, read_only=True, source='day_tour_price_list')
    itineraries_list = TourItinerarySerializer(many=True)
    cancellation_policies_list = CancellationPolicySerializer(many=True) 



    class Meta:
        model = Tour
        # fields = ['id', 'name', 'description', 'day_tour_price_list', 'day_tour_price_list_read', 'created_at', 'updated_at']
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # replace write-only field with read-only field in output
        rep['day_tour_price_list'] = rep.pop('day_tour_price_list_read')
        return rep
    
    def create(self, validated_data):
        request = self.context.get("request")
        files = request.FILES
        print("files : ", files)

        print("validated data from create method of TourSerializer : ", validated_data)
        print('\n')

        # finding company id from validated data
        company = validated_data.get('company', None)
        print("company from create method of TourSerializer : ", company)
        print('\n')

        # handle day tour price list
        day_tour_price_list = validated_data.pop('day_tour_price_list', [])
        print("day_tour_price_list from create method of Tourserializer : ", day_tour_price_list)
        print('\n')

        # handle itinerary list
        itineraries_list = validated_data.pop('itineraries_list', [])
        print("itinerary_list data from create method of TourSerializer:", itineraries_list)
        print('\n')

        # handle cancellation policies list
        cancellation_policies_list = validated_data.pop('cancellation_policies_list', [])
        print("cancellation_policies_list data from create method of TourSerializer:", cancellation_policies_list)
        print('\n')

        # handle images
        print("start working with images from create method, clearing images from tour creation data.")
        images = {}
        image_keys = [key for key in files.keys() if key.startswith("images[0]")]
        print('image_keys: ', image_keys)
        for key in image_keys:
            image = files.get(key)
            images[key] = image
            print(f"Processing {key} => {image}")
        print("images dictionary from create mehod of TourSerializer is : ", images)
        print('\n')

        print("validated data from create method of TourSerializer:", validated_data)
        tour = Tour.objects.create(
            **validated_data)
        print("Tour created:", tour)

        # creating Day tour Price List
        print("creating DayTourPrices.")
        for day_price_data in day_tour_price_list:
            serializer = DayTourPriceSerializer(data=day_price_data, context={'tour': tour, 'company': company})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print("DayTourPrice created:", serializer.instance)
        print('\n')

        # creating  itinerary list 
        print("creating Itineraries")
        for itinerary_data in itineraries_list:
            itinerary_data['tour'] = tour.id
            serializer = TourItinerarySerializer(data=itinerary_data, context={'company': company})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print("Itinerary created:", serializer.instance)
        print('\n')

        # creating cancellation policies list
        print("creating Cancellation Policies")
        for policy_data in cancellation_policies_list:
            print("policy data is :",policy_data)
            serializer = CancellationPolicySerializer(data=policy_data, context={'tour': tour, 'company': company})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print("Cancellation Policy created:", serializer.instance)
        print('\n')

        # creating tour content images
        print("creating images")
        image_data = {}
        for key, value in images.items():
            image_data["tour"] = tour.id
            image_data["head"] = str(value)
            image_data["image"] = value
            image_data["company"] = company
            print("image data is :",image_data)
            serializer = TourContentImageSerializer(data=image_data, context={'company': company})
            # print("TourContentImageSerializer is : ", serializer)

            if serializer.is_valid():
                serializer.save()
                print(f"image {value} is saved successfully")
            else:
                print("errors : ", serializer.errors)
        print('\n')

        # handle created_by field
        user = get_current_authenticated_user()
        print("current authenticated user in TourSerializer created method:", user)
        if user is not None:
            tour.created_by = user
            tour.save(update_fields=["created_by"])  # <--- only save this field
        print("Tour creation completed.")
        print("created by : ", tour.created_by)
        print('\n')
        return tour

    def update(self, instance, validated_data):
        print(f"tour of id {instance.id} is updating.")
        request = self.context.get("request")
        files = request.FILES
        print("files : ", files)

        # finding company id from validated data
        company = validated_data.get('company', None)
        print("company from update method of TourSerializer : ", company)
        print('\n')

        print("validated data from update method of TourSerializer : ", validated_data)

        # instance এর ফিল্ড update করতে ছোট্ট trick:
        for attr, value in validated_data.items():
            if attr != 'day_tour_price_list' and attr != "itineraries_list" and attr != 'cancellation_policies_list':  # nested field বাদ
                setattr(instance, attr, value)
        instance.save()

        # day_tour_price_list update part:
        new_day_prices = validated_data.pop('day_tour_price_list', [])
        existing_ids = [item['id'] for item in new_day_prices if 'id' in item]
        instance.day_tour_price_list.exclude(id__in=existing_ids).delete()

        for day_price_data in new_day_prices:
            # updating the existing DayTourPrice from create part of Tour as existing id is given
            if 'id' in day_price_data:
                print("updating the existing DayTourPrice from update part of TourSerializer as existing id is given")
                obj = DayTourPrice.objects.get(id=day_price_data['id'], tour=instance)
                serializer = DayTourPriceSerializer(obj, data=day_price_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

            # creating new DayTourPrice from update part of Tour as id is absent
            else:
                print("creating new DayTourPrice from update part of TourSerializer as id is absent")
                serializer = DayTourPriceSerializer(data=day_price_data, context={'tour': instance})
                serializer.is_valid(raise_exception=True)
                serializer.save()
        print("day_tour_price updated successfully")

        # cancellation policies update part
        cancellation_policies_data = validated_data.pop('cancellation_policies_list', [])
        existing_policies = {cp.id: cp for cp in instance.cancellation_policies_list.all()}
        print('\n')
        print("existing policies data : ", cancellation_policies_data)
        print('\n')
        print("existing policies in db : ", existing_policies)
        print('\n')

        sent_policy_ids = []
        for policy_data in cancellation_policies_data:
            print('\n')
            policy_id = policy_data.get('id', None)
            if policy_id is not None:
                print(f"for policy id {policy_data['id']} -> policy data : {policy_data}")
            else:
                print(f"for policy id None -> policy data : {policy_data}")

            print('\n')

            if policy_id and policy_id in existing_policies:
                policy_instance = existing_policies[policy_id]
                print(f"Updating cancellation Policy ID : {policy_id} with its data : ", policy_data)
                serializer = CancellationPolicySerializer(policy_instance, data=policy_data, partial=True, context={'tour': instance})
                if serializer.is_valid():
                    serializer.save()
                    sent_policy_ids.append(policy_id)
                    print(f"Updated cancellation Policy ID : {policy_id}")
                else:
                    print("validation errors:", serializer.errors)
            else:
                policy_data['tour'] = instance.id
                serializer = CancellationPolicySerializer(data=policy_data, context={'tour': instance})
                if serializer.is_valid():
                    serializer.save()
                    print(f"Created new cancellation Policy ID : {serializer.instance.id}")
                else:
                    print("validation errors:", serializer.errors)
        # Delete policies not in the update request
        for policy_id, policy in existing_policies.items():
            if policy_id not in sent_policy_ids:
                policy.delete()
        print("cancellation policies updated successfully.")


        # Itineraries Update Part
        itineraries_list = validated_data.pop('itineraries_list', [])
        print("itinerary_list data from create method of TourSerializer:", itineraries_list)
        print('\n')
        for itinerary_data in itineraries_list:
            itinerary_data['tour'] = instance.id
            serializer = TourItinerarySerializer(data=itinerary_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print("Itinerary created:", serializer.instance)

        

        # handle images
        print("start working with images from update method.")
        images = {}
        image_keys = [key for key in files.keys() if key.startswith("images[0]")]
        print('image_keys: ', image_keys)
        for key in image_keys:
            image = files.get(key)
            images[key] = image
            print(f"Processing {key} => {image}")
        print("images dictionary from update mehod of TourSerializer is : ", images)
        print('\n')

        # creating tour content images
        print("creating images")
        image_data = {}
        for key, value in images.items():
            image_data["tour"] = instance.id
            image_data["head"] = str(value)
            image_data["image"] = value
            print("image data is :",image_data)
            serializer = TourContentImageSerializer(data=image_data, context={'company': instance.company})
            print("TourContentImageSerializer is : ", serializer)

            if serializer.is_valid():
                serializer.save()
                print(f"image {value} is saved successfully")
            else:
                print("errors : ", serializer.errors)

        # handle updated_by field
        user = get_current_authenticated_user()
        print("current authenticated user in TourSerializer update method:", user)
        if user is not None:
            instance.updated_by = user
            instance.save(update_fields=["updated_by"])  # <--- only save this field
        return instance
        


class TourContentImageSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = TourContentImage
        fields = '__all__'

    def create(self, validated_data):
        image = validated_data.get('image', None)
        company = self.context.get('company')
        validated_data['company'] = company
        print('\n')
        print('requested data for create from TourContentImageSerializer: ', validated_data)
        print('\n')
        if image is not None:
            print("image from TourContentImageSerializer create method:", image)
            print('\n')

        modelObject = super().create(validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.created_by = user
            modelObject.save(update_fields=["created_by"])  # <--- only save this field
        # modelObject.save()
        return modelObject
    
    def update(self, instance, validated_data):
        print('\n')
        print('requested data for update: ', validated_data)
        print('\n')
        image = validated_data.get('image', None)
        print("image from TourContentImageSerializer update method:", image)
        print('\n')
        if image is not None:
            print("image from TourContentImageSerializer update method:", image)
            print('\n')

        modelObject = super().update(instance=instance, validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.updated_by = user
            modelObject.save(update_fields=["updated_by"])
        # modelObject.save()
        return modelObject
    


    