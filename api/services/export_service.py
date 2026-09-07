import csv
import io
from api.repositories.reportingexcel_repository import MSSQLRepository

class ExportService:

    @classmethod
    def generate_mssql_csv(cls, year, month, branch_type=0):
        output = io.StringIO()
        writer = csv.writer(output)

        headers = ['Branch', 'Account', 'Description', 'Type', 'Classification', 'Ending', 'MappingBranch']
        writer.writerow(headers)
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        data_stream = MSSQLRepository.get_branch_report(
            year=year, 
            month=month, 
            branch_type=branch_type
        )

        for row in data_stream:
            ending_val = row.get('Ending')
            formatted_ending = f"{ending_val:.6f}" if ending_val is not None else "0.0"

            writer.writerow([
                row.get('Branch', ''),
                row.get('Account', ''),
                row.get('Description', ''),
                row.get('Type', ''),
                row.get('Classification', ''),
                formatted_ending,
                row.get('MappingBranch', '')
            ])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)