from rest_framework import serializers


class RefNoRequestSerializer(serializers.Serializer):
    refno = serializers.CharField(
        required=True,
        max_length=100
    )
    
class TransactionSummaryRequestSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()