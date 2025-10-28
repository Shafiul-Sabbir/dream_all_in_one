from authentication.models import User, Country
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from authentication.models import Permission, Company, Role
from cms.models import CMSMenu, CMSMenuContent, MetaData, CMSMenuContentImage, BlogCategory, Blog

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
                cms_blog_country_instance = Country.objects.filter(old_id=cms_blog_country_old_id, company_id=company_instance).first()
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