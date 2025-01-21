from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from userlog.models import UserLog
import inspect

# For restricting other app data
def is_relevant_app(sender):
    app_label = sender._meta.app_label
    return app_label in ["order", "product"]



def get_request():
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            return frame_record[0].f_locals['request']
    return None


@receiver(pre_save)
def log_object_changes(sender, instance, **kwargs):
    if sender.__name__ not in ["UserLog", "Session", "Token"] and is_relevant_app(sender):
        request = get_request()

        # Object is new,cant compare the changes
        if not instance.pk:
            return

        try:
            original_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            original_instance = None

        changes = []
        action_data = {}
        for field in instance._meta.fields:
            field_name = field.name
            original_value = getattr(original_instance, field_name) if original_instance else None
            new_value = getattr(instance, field_name)
            if original_value != new_value:
                changes.append(f"{field_name}: {original_value} -> {new_value}")
                action_data[field_name] = f"{new_value}"

        if changes:
            action_type = "update"
            action = f'Updated {sender.__name__} {instance} ({", ".join(changes)})'
            content_type = ContentType.objects.get_for_model(sender)
            if request and request.user.is_authenticated:
                UserLog.objects.create(
                    user=request.user,
                    action=action,
                    content_type=content_type,
                    action_type=action_type,
                    action_data=action_data,
                    object_id=instance.pk,
                )


@receiver(post_save)
def log_object_creation_update(sender, instance, created, **kwargs):
    if sender.__name__ not in ["UserLog", "Session", "Token"] and is_relevant_app(sender):
        request = get_request()

        if created:
            action = f'Created {sender.__name__} {instance}'
            action_type = "create"
            action_data = {}
            for field in instance._meta.fields:
                field_name = field.name
                new_value = getattr(instance, field_name)
                if new_value is not None:
                    action_data[field_name] = f"{new_value}"

            content_type = ContentType.objects.get_for_model(sender)

            if request and request.user.is_authenticated:
                UserLog.objects.create(
                    user=request.user,
                    action=action,
                    content_type=content_type,
                    action_type=action_type,
                    action_data=action_data,
                    object_id=instance.pk,
                )


@receiver(post_delete)
def log_object_deletion(sender, instance, **kwargs):
    if sender.__name__ not in ["UserLog", "Session", "Token"] and is_relevant_app(sender):
        request = get_request()
        content_type = ContentType.objects.get_for_model(sender)
        action_type = "delete"
        if request is not None and sender.__name__ != "Session":
            UserLog.objects.create(
                user=request.user,
                action=f'Deleted {sender.__name__} {instance}',
                action_type=action_type,
                content_type=content_type,
                object_id=instance.pk,
            )



# @receiver(pre_save)
# def log_object_changes(sender, instance, **kwargs):
    
#     if sender.__name__ != "UserLog" and sender.__name__ != "Session" and sender.__name__ != "Token":
#         import inspect
#         request = ""
#         for frame_record in inspect.stack():
#             if frame_record[3] == 'get_response':
#                 request = frame_record[0].f_locals['request']
#                 break
#         else:
#             request = None

#         ### Object is new, so we can't compare the changes###
#         if not instance.pk:
#             return

#         # original_instance = sender.objects.get(pk=instance.pk)
#         ### updated for manufacure
#         try:
#             original_instance = sender.objects.get(pk=instance.pk)
#         except sender.DoesNotExist:
#             original_instance = None
#         changes = []
#         action_data = {}
#         for field in instance._meta.fields:
#             field_name = field.name
#             original_value = getattr(original_instance, field_name)  if original_instance else None ### updated for manufacure
#             new_value = getattr(instance, field_name)
#             if original_value != new_value:
#                 changes.append(f"{field_name}: {original_value} -> {new_value}")
#                 action_data[field_name] = f"{new_value}"
        
#         if changes:
#             action_type="update"
#             action = f'Updated {sender.__name__} {instance} ({", ".join(changes)})'
#             content_type = ContentType.objects.get_for_model(sender)
#             if request and request.user.is_authenticated:
#                 UserLog.objects.create(
#                     user=request.user,
#                     action=action,
#                     content_type=content_type,
#                     action_type=action_type,
#                     action_data=action_data,
#                     object_id=instance.pk,
#             )
            

# @receiver(post_save)
# def log_object_creation_update(sender, instance, created, **kwargs):
#     if sender.__name__ != "UserLog" and sender.__name__ != "Session" and sender.__name__ != "Token":
#         import inspect
#         request=""
#         for frame_record in inspect.stack():
#             if frame_record[3]=='get_response':
#                 request = frame_record[0].f_locals['request']
#                 break
#         else:
#             request = None

#         if created:
#             action = f'Created {sender.__name__} {instance}'
#             # original_instance = sender.objects.get(pk=instance.pk)
#             action_type="create"
#             action_data = {}
#             for field in instance._meta.fields:
#                 field_name = field.name
#                 new_value = getattr(instance, field_name)
#                 if new_value is not None:
#                     action_data[field_name] = f"{new_value}"
#             # print(original_instance)
            
#         # else:
#         #     original_instance = sender.objects.get(pk=instance.pk)
#         #     changes = []
#         #     for field in instance._meta.fields:
#         #         field_name = field.name
#         #         original_value = getattr(original_instance, field_name)
#         #         new_value = getattr(instance, field_name)
#         #         if original_value != new_value:
#         #             changes.append(f"{field_name}: {original_value} -> {new_value}")
#         #     action = f'Updated {sender.__name__} {instance} ({", ".join(changes)})'
    
#             content_type = ContentType.objects.get_for_model(sender)

#             if request and request.user.is_authenticated:
#                 UserLog.objects.create(
#                     user=request.user,
#                     action=action,
#                     content_type=content_type,
#                     action_type=action_type,
#                     action_data=action_data,
#                     object_id=instance.pk,
#                 )



# @receiver(post_delete)
# def log_object_deletion(sender, instance, **kwargs):
#     if sender.__name__ != "UserLog" or sender.__name__ != "Session" and sender.__name__ != "Token":
#         # print("---------------------------------------------------------------------")
#         import inspect 
#         request=""
#         for frame_record in inspect.stack():
#             if frame_record[3]=='get_response':
#                 request = frame_record[0].f_locals['request']
#                 break
#         else:
#             request = None
#         content_type = ContentType.objects.get_for_model(sender)
#         action_type="delete"
#         # print(instance)
#         # print(content_type)
#         # print(sender.__name__)
#         if request is not None and sender.__name__ != "Session":
#             UserLog.objects.create(
#                 user=request.user,
#                 action=f'Deleted {sender.__name__} {instance}',
#                 action_type=action_type,
#                 content_type=content_type,
#                 object_id=instance.pk,
#                 )