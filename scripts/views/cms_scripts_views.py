from authentication.models import User, Country
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from authentication.models import Permission, Company, Role
from cms.models import CMSMenu, CMSMenuContent, MetaData, CMSMenuContentImage, BlogCategory, Blog, EmailAddress, SendEmail, Review, Itinerary, Tag, MetaData

@api_view(['POST'])
def load_CMSMenu(request, company_id):
    if company_id == 1:
        file_path = 'all_json/cms/it/cms_CMSMenu_it.json'
    elif company_id == 2:
        file_path = 'all_json/cms/uk/cms_CMSMenu_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_cms_data = json.load(file)
        for cms_data in all_cms_data:
            fields = cms_data.get('fields')
            print("raw cms menu:", fields)
            print('\n')

            fields['old_id'] = cms_data.get('pk')
            company_instance = Company.objects.get(id=company_id)
            fields['company_id'] = company_instance

            # handle created_by and updated_by fields
            created_by_old_id = fields.get('created_by')
            updated_by_old_id = fields.get('updated_by')
            if created_by_old_id:
                try:
                    created_by_user = User.objects.get(old_id=created_by_old_id, company_id=company_instance)
                    fields['created_by'] = created_by_user
                except User.DoesNotExist:
                    fields['created_by'] = None
            else:
                fields['created_by'] = None
            if updated_by_old_id:
                try:
                    updated_by_user = User.objects.get(old_id=updated_by_old_id, company_id=company_instance)
                    fields['updated_by'] = updated_by_user
                except User.DoesNotExist:
                    fields['updated_by'] = None
            else:
                fields['updated_by'] = None

            # handle created_at and updated_at fields
            created_at_old_id = fields.get('created_at')
            updated_at_old_id = fields.get('updated_at')
            if created_at_old_id:
                fields['created_at'] = created_at_old_id
            else:
                fields['created_at'] = None
            if updated_at_old_id:
                fields['updated_at'] = updated_at_old_id
            else:
                fields['updated_at'] = None

            #we will assign the parent later
            fields.pop('parent', None)

            print("reformed cms menu:", fields)
            print("-----")
            print("\n")
            
            if not CMSMenu.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                cms_menu_obj = CMSMenu.objects.create(**fields)

                print(f"Saved CMSMenu, id = {cms_menu_obj.id}, old_id = {cms_menu_obj.old_id}")
            else:
                print(f"cms menu with old_id = {fields['old_id']} already exists. Skipping.")
    
    return Response({'message': 'Loading all cms menu successful.'}, status=200)

@api_view(['POST'])
def handle_CMSMenu_parent(request, company_id):
    if company_id == 1:
        file_path = 'all_json/cms/it/cms_CMSMenu_it.json'
    elif company_id == 2:
        file_path = 'all_json/cms/uk/cms_CMSMenu_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_file_data = json.load(file)
        for data in all_file_data:
            fields = data.get('fields')
            fields['old_id'] = data.get('pk')
            company_instance = Company.objects.get(id=company_id)
            fields['company_id'] = company_instance
            print("data:", fields)

            # retrieving parent data from file data and assigning them to the db data
            parent_id = fields.get('parent')
            print("parent_id:", parent_id)
            if parent_id is not None:
                parent = CMSMenu.objects.filter(old_id=parent_id, company_id=company_instance).first()
                if parent:
                    cms_menu_instance = CMSMenu.objects.filter(old_id=fields['old_id'], company_id=company_instance).first()
                    if cms_menu_instance:
                        cms_menu_instance.parent = parent
                        cms_menu_instance.save()
                        print(f"Updated CMSMenu id={cms_menu_instance.id} with parent id={parent.id}")

    
    return Response({'message': 'Handling all cms menu metadata successful.'}, status=200)

@api_view(['POST'])
def load_CMSMenuContent(request, company_id):
    if company_id == 1:
        file_path = 'all_json/cms/it/cms_CMSMenuContent_it.json'
    elif company_id == 2:
        file_path = 'all_json/cms/uk/cms_CMSMenuContent_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_cms_menu_content_data = json.load(file)
        for cms_menu_content_data in all_cms_menu_content_data:
            fields = cms_menu_content_data.get('fields')
            print("raw cms menu content :", fields)
            print('\n')

            fields['old_id'] = cms_menu_content_data.get('pk')
            company_instance = Company.objects.get(id=company_id)
            fields['company_id'] = company_instance

            # handle created_by and updated_by fields
            created_by_old_id = fields.get('created_by')
            updated_by_old_id = fields.get('updated_by')
            if created_by_old_id:
                try:
                    created_by_user = User.objects.get(old_id=created_by_old_id, company_id=company_instance)
                    fields['created_by'] = created_by_user
                except User.DoesNotExist:
                    fields['created_by'] = None
            else:
                fields['created_by'] = None
            if updated_by_old_id:
                try:
                    updated_by_user = User.objects.get(old_id=updated_by_old_id, company_id=company_instance)
                    fields['updated_by'] = updated_by_user
                except User.DoesNotExist:
                    fields['updated_by'] = None
            else:
                fields['updated_by'] = None

            #handle cms_menu foreign key
            cms_menu_old_id = fields.get('cms_menu')
            if cms_menu_old_id:
                cms_menu_instance = CMSMenu.objects.filter(old_id=cms_menu_old_id, company_id=company_instance).first()
                if cms_menu_instance:
                    fields['cms_menu'] = cms_menu_instance
                else:
                    fields['cms_menu'] = None
            else:
                fields['cms_menu'] = None

            print("reformed cms menu:", fields)
            print("-----")
            print("\n")
            
            if not CMSMenuContent.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                cms_menu_content_obj = CMSMenuContent.objects.create(**fields)

                print(f"Saved CMSMenuContent, id = {cms_menu_content_obj.id}, old_id = {cms_menu_content_obj.old_id}")
            else:
                print(f"cms menu content with old_id = {fields['old_id']} already exists. Skipping.")
    
    return Response({'message': 'Loading all cms menu successful.'}, status=200)

@api_view(['POST'])
def load_CMSMenuContentImage(request, company_id):
    if company_id == 1:
        file_path = 'all_json/cms/it/cms_CMSMenuContentImage_it.json'
    elif company_id == 2:
        file_path = 'all_json/cms/uk/cms_CMSMenuContentImage_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_cms_menu_content_image_data = json.load(file)
        for cms_menu_content_image_data in all_cms_menu_content_image_data:
            fields = cms_menu_content_image_data.get('fields')
            print("raw cms menu content image :", fields)
            print('\n')

            fields['old_id'] = cms_menu_content_image_data.get('pk')
            company_instance = Company.objects.get(id=company_id)
            fields['company_id'] = company_instance

            # handle created_by and updated_by fields
            created_by_old_id = fields.get('created_by')
            updated_by_old_id = fields.get('updated_by')
            if created_by_old_id:
                try:
                    created_by_user = User.objects.get(old_id=created_by_old_id, company_id=company_instance)
                    fields['created_by'] = created_by_user
                except User.DoesNotExist:
                    fields['created_by'] = None
            else:
                fields['created_by'] = None
            if updated_by_old_id:
                try:
                    updated_by_user = User.objects.get(old_id=updated_by_old_id, company_id=company_instance)
                    fields['updated_by'] = updated_by_user
                except User.DoesNotExist:
                    fields['updated_by'] = None
            else:
                fields['updated_by'] = None

            #handle cms_menu foreign key
            cms_menu_old_id = fields.get('cms_menu')
            if cms_menu_old_id:
                cms_menu_instance = CMSMenu.objects.filter(old_id=cms_menu_old_id, company_id=company_instance).first()
                if cms_menu_instance:
                    fields['cms_menu'] = cms_menu_instance
                else:
                    fields['cms_menu'] = None
            else:
                fields['cms_menu'] = None

            print("reformed cms menu content image:", fields)
            print("-----")
            print("\n")
            
            if not CMSMenuContentImage.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                cms_menu_content_image_obj = CMSMenuContentImage.objects.create(**fields)

                print(f"Saved CMSMenuContentImage, id = {cms_menu_content_image_obj.id}, old_id = {cms_menu_content_image_obj.old_id}")
            else:
                print(f"cms menu content image with old_id = {fields['old_id']} already exists. Skipping.")
    
    return Response({'message': 'Loading all cms menu content images successful.'}, status=200)

@api_view(['POST'])
def load_BlogCategory(request, company_id):
    if company_id == 1:
        file_path = 'all_json/cms/it/cms_BlogCategory_it.json'
    elif company_id == 2:
        file_path = 'all_json/cms/uk/cms_BlogCategory_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_blog_category_data = json.load(file)
        for blog_category_data in all_blog_category_data:
            fields = blog_category_data.get('fields')
            print("raw blog category:", fields)
            print('\n')

            fields['old_id'] = blog_category_data.get('pk')
            company_instance = Company.objects.get(id=company_id)
            fields['company_id'] = company_instance

            # handle created_by and updated_by fields
            created_by_old_id = fields.get('created_by')
            updated_by_old_id = fields.get('updated_by')
            if created_by_old_id:
                try:
                    created_by_user = User.objects.get(old_id=created_by_old_id, company_id=company_instance)
                    fields['created_by'] = created_by_user
                except User.DoesNotExist:
                    fields['created_by'] = None
            else:
                fields['created_by'] = None

            if updated_by_old_id:
                try:
                    updated_by_user = User.objects.get(old_id=updated_by_old_id, company_id=company_instance)
                    fields['updated_by'] = updated_by_user
                except User.DoesNotExist:
                    fields['updated_by'] = None
            else:
                fields['updated_by'] = None

            print("reformed blog category:", fields)
            print("-----")
            print("\n")
            
            if not BlogCategory.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                blog_category_obj = BlogCategory.objects.create(**fields)

                print(f"Saved BlogCategory, id = {blog_category_obj.id}, old_id = {blog_category_obj.old_id}")
            else:
                print(f"blog category with old_id = {fields['old_id']} already exists. Skipping.")

    return Response({'message': 'Loading all blog category successful.'}, status=200)

@api_view(['POST'])
def handle_BlogCategory_created_at(request, company_id):
    if company_id == 1:
        file_path = 'all_json/cms/it/cms_BlogCategory_it.json'
    elif company_id == 2:
        file_path = 'all_json/cms/uk/cms_BlogCategory_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_blog_category_data = json.load(file)
        for blog_category_data in all_blog_category_data:
            fields = blog_category_data.get('fields')
            print("raw blog category:", fields)
            print('\n')

            blogCategory_old_id = blog_category_data.get('pk')
            created_at_old_id = fields.get('created_at')

            company_instance = Company.objects.get(id=company_id)

            blogCategory_instance = BlogCategory.objects.filter(old_id = blogCategory_old_id, company_id = company_instance).first()
            blogCategory_instance.created_at = created_at_old_id
            blogCategory_instance.save()
    
    return Response({'message': 'updateing all blog category created at successful.'}, status=200)

@api_view(['POST'])
def load_Blog(request, company_id):
    if company_id == 1:
        file_path = 'all_json/cms/it/cms_Blog_it.json'
    elif company_id == 2:
        file_path = 'all_json/cms/uk/cms_Blog_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_blog_data = json.load(file)
        for blog_data in all_blog_data:
            fields = blog_data.get('fields')
            print("raw blog :", fields)
            print('\n')

            fields['old_id'] = blog_data.get('pk')
            company_instance = Company.objects.get(id=company_id)
            fields['company_id'] = company_instance

            # handle created_by and updated_by fields
            created_by_old_id = fields.get('created_by')
            updated_by_old_id = fields.get('updated_by')
            if created_by_old_id:
                try:
                    created_by_user = User.objects.get(old_id=created_by_old_id, company_id=company_instance)
                    fields['created_by'] = created_by_user
                except User.DoesNotExist:
                    fields['created_by'] = None
            else:
                fields['created_by'] = None

            if updated_by_old_id:
                try:
                    updated_by_user = User.objects.get(old_id=updated_by_old_id, company_id=company_instance)
                    fields['updated_by'] = updated_by_user
                except User.DoesNotExist:
                    fields['updated_by'] = None
            else:
                fields['updated_by'] = None

           #handle cms menu content foreign key
            cms_menu_content_old_id = fields.get('cms_content')
            if cms_menu_content_old_id:
                cms_menu_content_instance = CMSMenuContent.objects.filter(old_id=cms_menu_content_old_id, company_id=company_instance).first()
                if cms_menu_content_instance:
                    fields['cms_content'] = cms_menu_content_instance
                else:
                    fields['cms_content'] = None
            else:
                fields['cms_content'] = None

            #handle blog category foreign key
            cms_blog_category_old_id = fields.get('blog_category')
            if cms_blog_category_old_id:
                cms_blog_category_instance = BlogCategory.objects.filter(old_id=cms_blog_category_old_id, company_id=company_instance).first()
                if cms_blog_category_instance:
                    fields['blog_category'] = cms_blog_category_instance
                else:
                    fields['blog_category'] = None
            else:
                fields['blog_category'] = None

            #handle blog country foreign key
            cms_blog_country_old_id = fields.get('blog_country')
            if cms_blog_country_old_id:
                cms_blog_country_instance = Country.objects.filter(old_id=cms_blog_country_old_id, company_id=company_instance).exists()
                if cms_blog_country_instance:
                    fields['blog_country'] = cms_blog_country_instance
                else:
                    fields['blog_country'] = None
            else:
                fields['blog_country'] = None



            print("reformed blog :", fields)
            print("-----")
            print("\n")
            
            if not Blog.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                blog_obj = Blog.objects.create(**fields)

                print(f"Saved Blog, id = {blog_obj.id}, old_id = {blog_obj.old_id}")
            else:
                print(f"blog with old_id = {fields['old_id']} already exists. Skipping.")

    return Response({'message': 'Loading all blog successful.'}, status=200)

@api_view(['POST'])
def load_EmailAddress(request, company_id):
    if company_id == 1:
        file_path = 'all_json/cms/it/cms_EmailAddress_it.json'
    elif company_id == 2:
        file_path = 'all_json/cms/uk/cms_EmailAddress_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_email_address_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)

        for email_address_data in all_email_address_data:
            fields = email_address_data.get('fields')
            print("raw email address:", fields)
            print('\n')

            fields['old_id'] = email_address_data.get('pk')
            fields['company_id'] = company_instance

            print("reformed email address:", fields)
            print("-----")
            print("\n")
            
            if not EmailAddress.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                email_address_obj = EmailAddress.objects.create(**fields)

                print(f"Saved EmailAddress, id = {email_address_obj.id}, old_id = {email_address_obj.old_id}")
            else:
                print(f"email address with old_id = {fields['old_id']} already exists. Skipping.")
    
    return Response({'message': 'Loading all email address successful.'}, status=200)

@api_view(['POST'])
def load_SendEmail(request, company_id):
    if company_id == 1:
        file_path = 'all_json/cms/it/cms_SendEmail_it.json'
    elif company_id == 2:
        file_path = 'all_json/cms/uk/cms_SendEmail_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_send_email_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)

        for send_email_data in all_send_email_data:
            fields = send_email_data.get('fields')
            print("raw send email:", fields)
            print('\n')

            fields['old_id'] = send_email_data.get('pk')
            fields['company_id'] = company_instance

            print("reformed send email:", fields)
            print("-----")
            print("\n")
            
            if not SendEmail.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                send_email_obj = SendEmail.objects.create(**fields)

                print(f"Saved SendEmail, id = {send_email_obj.id}, old_id = {send_email_obj.old_id}")
            else:
                print(f"send email with old_id = {fields['old_id']} already exists. Skipping.")
    
    return Response({'message': 'Loading all send email successful.'}, status=200)

@api_view(['POST'])
def load_Review(request, company_id):
    if company_id == 1:
        file_path = 'all_json/cms/it/cms_Review_it.json'
    elif company_id == 2:
        file_path = 'all_json/cms/uk/cms_Review_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_review_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)

        for review_data in all_review_data:
            fields = review_data.get('fields')
            print("raw review:", fields)
            print('\n')

            fields['old_id'] = review_data.get('pk')
            fields['company_id'] = company_instance

            # handle created_by and updated_by fields
            created_by_old_id = fields.get('created_by')
            updated_by_old_id = fields.get('updated_by')
            if created_by_old_id:
                try:
                    created_by_user = User.objects.get(old_id=created_by_old_id, company_id=company_instance)
                    fields['created_by'] = created_by_user
                except User.DoesNotExist:
                    fields['created_by'] = None
            else:
                fields['created_by'] = None

            if updated_by_old_id:
                try:
                    updated_by_user = User.objects.get(old_id=updated_by_old_id, company_id=company_instance)
                    fields['updated_by'] = updated_by_user
                except User.DoesNotExist:
                    fields['updated_by'] = None
            else:
                fields['updated_by'] = None

            print("reformed review:", fields)
            print("-----")
            print("\n")
            
            if not Review.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                review_obj = Review.objects.create(**fields)

                print(f"Saved Review, id = {review_obj.id}, old_id = {review_obj.old_id}")
            else:
                print(f"review with old_id = {fields['old_id']} already exists. Skipping.")
    
    return Response({'message': 'Loading all review successful.'}, status=200)

@api_view(['POST'])
def load_Itinerary(request, company_id):
    if company_id == 1:
        file_path = 'all_json/cms/it/cms_Itinerary_it.json'
    elif company_id == 2:
        file_path = 'all_json/cms/uk/cms_Itinerary_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_itinerary_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)

        for itinerary_data in all_itinerary_data:
            fields = itinerary_data.get('fields')
            print("raw itinerary:", fields)
            print('\n')

            fields['old_id'] = itinerary_data.get('pk')
            fields['company_id'] = company_instance

            # handle created_by and updated_by fields
            created_by_old_id = fields.get('created_by')
            updated_by_old_id = fields.get('updated_by')
            if created_by_old_id:
                try:
                    created_by_user = User.objects.get(old_id=created_by_old_id, company_id=company_instance)
                    fields['created_by'] = created_by_user
                except User.DoesNotExist:
                    fields['created_by'] = None
            else:
                fields['created_by'] = None

            if updated_by_old_id:
                try:
                    updated_by_user = User.objects.get(old_id=updated_by_old_id, company_id=company_instance)
                    fields['updated_by'] = updated_by_user
                except User.DoesNotExist:
                    fields['updated_by'] = None
            else:
                fields['updated_by'] = None

            #handle cms menu content foreign key
            cms_menu_content_old_id = fields.get('cms_content')
            if cms_menu_content_old_id:
                cms_menu_content_instance = CMSMenuContent.objects.filter(old_id=cms_menu_content_old_id, company_id=company_instance).first()
                if cms_menu_content_instance:
                    fields['cms_content'] = cms_menu_content_instance
                else:
                    fields['cms_content'] = None
            else:
                fields['cms_content'] = None

            print("reformed itinerary:", fields)
            print("-----")
            print("\n")
            
            if not Itinerary.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                itinerary_obj = Itinerary.objects.create(**fields)

                print(f"Saved Itinerary, id = {itinerary_obj.id}, old_id = {itinerary_obj.old_id}")
            else:
                print(f"itinerary with old_id = {fields['old_id']} already exists. Skipping.")
    
    return Response({'message': 'Loading all itinerary successful.'}, status=200)

@api_view(['POST'])
def load_Tag(request, company_id):
    if company_id == 1:
        file_path = 'all_json/cms/it/cms_Tag_it.json'
    elif company_id == 2:
        file_path = 'all_json/cms/uk/cms_Tag_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_tag_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)

        for tag_data in all_tag_data:
            fields = tag_data.get('fields')
            print("raw tag:", fields)
            print('\n')

            fields['old_id'] = tag_data.get('pk')
            fields['company_id'] = company_instance

            # handle created_by and updated_by fields
            created_by_old_id = fields.get('created_by')
            updated_by_old_id = fields.get('updated_by')
            if created_by_old_id:
                try:
                    created_by_user = User.objects.get(old_id=created_by_old_id, company_id=company_instance)
                    fields['created_by'] = created_by_user
                except User.DoesNotExist:
                    fields['created_by'] = None
            else:
                fields['created_by'] = None

            if updated_by_old_id:
                try:
                    updated_by_user = User.objects.get(old_id=updated_by_old_id, company_id=company_instance)
                    fields['updated_by'] = updated_by_user
                except User.DoesNotExist:
                    fields['updated_by'] = None
            else:
                fields['updated_by'] = None

            #handle cms menu content foreign key
            cms_menu_content_old_id = fields.get('cms_content')
            if cms_menu_content_old_id:
                cms_menu_content_instance = CMSMenuContent.objects.filter(old_id=cms_menu_content_old_id, company_id=company_instance).first()
                if cms_menu_content_instance:
                    fields['cms_content'] = cms_menu_content_instance
                else:
                    fields['cms_content'] = None
            else:
                fields['cms_content'] = None


            print("reformed tag:", fields)
            print("-----")
            print("\n")
            
            if not Tag.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                tag_obj = Tag.objects.create(**fields)

                print(f"Saved Tag, id = {tag_obj.id}, old_id = {tag_obj.old_id}")
            else:
                print(f"tag with old_id = {fields['old_id']} already exists. Skipping.")
    
    return Response({'message': 'Loading all tag successful.'}, status=200)

@api_view(['POST'])
def handle_Tag_created_at(request, company_id):
    if company_id == 1:
        file_path = 'all_json/cms/it/cms_Tag_it.json'
    elif company_id == 2:
        file_path = 'all_json/cms/uk/cms_Tag_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_tag_data = json.load(file)
        for tag_data in all_tag_data:
            fields = tag_data.get('fields')
            print("raw tag:", fields)
            print('\n')

            tag_old_id = tag_data.get('pk')
            created_at_old_id = fields.get('created_at')

            company_instance = Company.objects.get(id=company_id)

            tag_instance = Tag.objects.filter(old_id = tag_old_id, company_id = company_instance).first()
            tag_instance.created_at = created_at_old_id
            tag_instance.save()
    
    return Response({'message': 'updateing all tag created at successful.'}, status=200)

@api_view(['POST'])
def load_MetaData(request, company_id):
    if company_id == 1:
        file_path = 'all_json/cms/it/cms_MetaData_it.json'
    elif company_id == 2:
        file_path = 'all_json/cms/uk/cms_MetaData_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_meta_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)

        for meta_data in all_meta_data:
            fields = meta_data.get('fields')
            print("raw meta data:", fields)
            print('\n')

            fields['old_id'] = meta_data.get('pk')
            fields['company_id'] = company_instance

            # handle created_by and updated_by fields
            created_by_old_id = fields.get('created_by')
            updated_by_old_id = fields.get('updated_by')
            if created_by_old_id:
                try:
                    created_by_user = User.objects.get(old_id=created_by_old_id, company_id=company_instance)
                    fields['created_by'] = created_by_user
                except User.DoesNotExist:
                    fields['created_by'] = None
            else:
                fields['created_by'] = None

            if updated_by_old_id:
                try:
                    updated_by_user = User.objects.get(old_id=updated_by_old_id, company_id=company_instance)
                    fields['updated_by'] = updated_by_user
                except User.DoesNotExist:
                    fields['updated_by'] = None
            else:
                fields['updated_by'] = None

            #handle cms menu content foreign key
            cms_menu_content_old_id = fields.get('cms_content')
            if cms_menu_content_old_id:
                cms_menu_content_instance = CMSMenuContent.objects.filter(old_id=cms_menu_content_old_id, company_id=company_instance).first()
                if cms_menu_content_instance:
                    fields['cms_content'] = cms_menu_content_instance
                else:
                    fields['cms_content'] = None
            else:
                fields['cms_content'] = None

            print("reformed meta data:", fields)
            print("-----")
            print("\n")
            
            if not MetaData.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                meta_data_obj = MetaData.objects.create(**fields)

                print(f"Saved MetaData, id = {meta_data_obj.id}, old_id = {meta_data_obj.old_id}")
            else:
                print(f"meta data with old_id = {fields['old_id']} already exists. Skipping.")
    
    return Response({'message': 'Loading all meta data successful.'}, status=200)