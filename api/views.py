from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, time
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import StreamingHttpResponse, JsonResponse

from .serializers import RefNoRequestSerializer, TransactionSummaryRequestSerializer
from .repositories.covering_repository import CoveringRepository
from .repositories.reportingexcel_repository import MSSQLRepository
from .services.mapping_product import enrich_product_data
from .services.product_service import enrich_and_group_by_product_name
from .services.export_service import ExportService
from drf_spectacular.utils import extend_schema

class HealthCheckView(APIView):

    def get(self, request):
        return Response(
            {
                "success": True,
                "message": "API Running"
            }
        )


class CoveringDetailView(APIView):

    def post(self, request):

        serializer = RefNoRequestSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = CoveringRepository.get_by_refno(
            serializer.validated_data["refno"]
        )

        return Response(
            {
                "data": data
            }
        )


class CoveringListView(APIView):

    def get(self, request):

        data = CoveringRepository.get_all()

        return Response(
            {
                "success": True,
                "count": len(data),
                "data": data
            }
        )


## For Summary All Range Date
class TransactionSummaryView(APIView):

    @extend_schema(
        request=TransactionSummaryRequestSerializer,
        responses={200: dict}
    )
    def post(self, request):

        serializer = TransactionSummaryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data["start_date"]
        end_date = serializer.validated_data["end_date"]

        start_dt_str = start_date.strftime("%Y-%m-%d") + " 00:00:00"
        end_dt_str = end_date.strftime("%Y-%m-%d") + " 23:59:59"

        data = CoveringRepository.group_by_product_and_date(
            start_dt_str,
            end_dt_str
        )

        return Response(enrich_product_data(data))
            
## For HasSync Is Null or 0 Value
class TransactionSummaryUnsyncedView(APIView):

    @extend_schema(
        request=TransactionSummaryRequestSerializer,
        responses={200: dict},
        description="Get UNSYNCED grouped by product_name"
    )
    def post(self, request):

        serializer = TransactionSummaryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data["start_date"]
        end_date = serializer.validated_data["end_date"]

        start_dt_str = start_date.strftime("%Y-%m-%d") + " 00:00:00"
        end_dt_str = end_date.strftime("%Y-%m-%d") + " 23:59:59"

        raw_data = CoveringRepository.group_by_product_and_date_unsynced(
            start_dt_str,
            end_dt_str
        )

        enriched = enrich_product_data(raw_data)

        grouped = enrich_and_group_by_product_name(enriched)

        # Return the flat list directly
        return Response(grouped)
    
    
## Detail Unsynced
class TransactionDetailUnsyncedView(APIView):

    @extend_schema(
        request=TransactionSummaryRequestSerializer,
        responses={200: list},
        description="Get detailed records for UNSYNCED transactions with validation info"
    )
    def post(self, request):

        serializer = TransactionSummaryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data["start_date"]
        end_date = serializer.validated_data["end_date"]

        start_dt_str = start_date.strftime("%Y-%m-%d") + " 00:00:00"
        end_dt_str = end_date.strftime("%Y-%m-%d") + " 23:59:59"

        # Fetch detailed unsynced records joined with CoveringValidation
        raw_details = CoveringRepository.get_unsynced_details_with_validation(
            start_dt_str,
            end_dt_str
        )

        # Optional: Pass through product enrichment helper if you map product_id to product_name
        # enriched_details = enrich_product_data(raw_details)
        # return Response(enriched_details, status=status.HTTP_200_OK)

        return Response(raw_details, status=status.HTTP_200_OK)
    
    
class ReportingPnL(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Extract input parameters from JSON payload body
        data = request.data or {}

        # 1. Sanitize & Validate Inputs
        raw_year = data.get('year', datetime.now().year)
        raw_month = data.get('month', datetime.now().month)
        raw_branch_type = data.get('branch_type', 0)

        try:
            year = int(str(raw_year).strip())
            month = int(str(raw_month).strip())
            branch_type = int(str(raw_branch_type).strip())
        except (ValueError, TypeError):
            return JsonResponse(
                {"error": "Invalid payload format. 'year', 'month', and 'branch_type' must be integers."},
                status=400
            )

        # 2. Enforce Boundary Checks (Input Sanitization)
        if not (1900 <= year <= 2100):
            return JsonResponse({"error": "year must be between 1900 and 2100."}, status=400)

        if not (1 <= month <= 12):
            return JsonResponse({"error": "month must be between 1 and 12."}, status=400)

        if branch_type not in (0, 1, 2):
            return JsonResponse({"error": "branch_type must be 0 (All), 1 (Konven), or 2 (Sharia)."}, status=400)

        # 3. Stream CSV Response
        response = StreamingHttpResponse(
            ExportService.generate_mssql_csv(year=year, month=month, branch_type=branch_type),
            content_type='text/csv'
        )
        filename = f"gl_report_{year}_{month}_type{branch_type}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
