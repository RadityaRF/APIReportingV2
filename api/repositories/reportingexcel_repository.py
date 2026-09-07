from api.mssql import get_db_mssql_connection

class MSSQLRepository:

    @classmethod
    def get_branch_report(cls, year: int, month: int, branch_type: int = 0):
        query = """
            SET NOCOUNT ON;

            DECLARE @Year INT = ?;
            DECLARE @Month INT = ?;
            DECLARE @BranchType INT = ?;

            -- Parameter Validations inside T-SQL
            IF @Month NOT BETWEEN 1 AND 12
            BEGIN
                THROW 50001, '@Month harus antara 1 sampai 12.', 1;
            END;

            IF @BranchType NOT BETWEEN 0 AND 2
            BEGIN
                THROW 50002, '@BranchType harus 0 (Semua), 1 (Konvensional), atau 2 (Sharia).', 1;
            END;

            IF OBJECT_ID('tempdb..#A') IS NOT NULL DROP TABLE #A;

            SELECT GL.Branch, GL.Account, A.Description, T.Description AS Type, S.Classification, 
                CASE 
                    WHEN GL.Account IN ('61000000', '63000000','64200000','64300000','64400000','64500000','64600000','64700000','64800000','64900000','65000000','66000000','69000000')
                        THEN SUM(GL.Ending) * -1
                    ELSE SUM(GL.Ending)
                    END AS Ending,
                CASE 
                    WHEN B.ShariaF = 0 THEN 'Konven'
                    WHEN B.ShariaF = 1 THEN 'Sharia'
                END AS MappingBranch
            INTO #A
            FROM GL
            INNER JOIN Account A ON GL.Account = A.Account
            INNER JOIN Type T ON T.Type = A.Type
            INNER JOIN Temporary_Data.dbo.sysMappingPL S ON S.Account = GL.Account
            INNER JOIN Branch B ON B.Branch = GL.Branch
            WHERE GL.Year = @Year
                AND GL.Month BETWEEN 1 AND @Month
                AND B.Op_Flag = 1
                AND (
                    @BranchType = 0
                    OR (@BranchType = 1 AND B.ShariaF = 0)
                    OR (@BranchType = 2 AND B.ShariaF = 1)
                )
            GROUP BY GL.Branch, GL.Account, T.Description, A.Description, S.Classification, B.ShariaF;

            SELECT Branch, Account, Description, Type, Classification, SUM(Ending) AS Ending, MappingBranch
            FROM #A
            GROUP BY Branch, Account, Description, Type, MappingBranch, Classification
            HAVING SUM(Ending) <> 0
            ORDER BY Branch, Account ASC;

            DROP TABLE #A;
        """

        # Parameters are cast to built-in int type, ensuring type safety
        params = [int(year), int(month), int(branch_type)]

        with get_db_mssql_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                
                while cursor.description is None:
                    if not cursor.nextset():
                        return

                columns = [column[0] for column in cursor.description]
                for row in cursor:
                    yield dict(zip(columns, row))