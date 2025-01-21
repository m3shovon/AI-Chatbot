from rest_framework import serializers
from userlog import models

class LogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserLog
        fields = '__all__'
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["model"] = instance.content_type.name
        response["created_by"] = instance.user.name
        
        sql = ""
        if instance.action_type == "create":
            sql = "INSERT INTO " + str(instance.content_type.app_label) + "_"+ str(instance.content_type.model) + " "
            if instance.action_data:
                data = eval(instance.action_data)
                field = "("
                values = "("
                for key, value in data.items():
                    field = field + str(key) +", "
                    values = values +"'"+ str(value)+"', "
                sql = sql + field[:-2] + ") VALUES " + values[:-2] + ");"
            
           
        elif instance.action_type == "update":
            sql = "UPDATE " + str(instance.content_type.app_label) + "_"+ str(instance.content_type.model) + " SET "
            if instance.action_data:
                data = eval(instance.action_data)
                for key, value in data.items():
                    sql = sql + str(key) + "='" + str(value)+"', "
            if instance.object_id:
                sql = sql[:-2] + " WHERE id="+ str(instance.object_id) + ";"
            
        else:
            sql = "DELETE FROM " + str(instance.content_type.app_label) + "_"+ str(instance.content_type.model)
            if instance.object_id:
                sql = sql + " WHERE id="+ str(instance.object_id) + ";"
        response["sql"] = sql
        return response
