import pandas as pd
import pyodbc

from Model.LoanApplicationModel import LoanApplicationModel
from Model.UserProfile import UserProfile

class DbHandle:
    def __init__(self):
        self.conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=host.docker.internal,1433;"
            "DATABASE=LoanApplication;"
            "UID=fastapi_user;"
            "PWD=Strong@Password123;"
            "Encrypt=no;"   
        )
        #self.conn = pyodbc.connect(
        #                "DRIVER={ODBC Driver 17 for SQL Server};"
        #                "SERVER=UMESH;"
        #                "DATABASE=LoanApplication;"
        #                "Trusted_Connection=yes;"
        #                "TrustServerCertificate=yes;"
        #            )
	    
        self.cursor = self.conn.cursor()
        self.cursor.fast_executemany = True
        print("Connection Success")
        self.X_columns = ['loan_amnt', 'emp_length', 'annual_inc', 'dti',
        'delinq_2yrs', 'open_acc', 'pub_rec', 'revol_bal', 'revol_util',
        'application_type', 'acc_now_delinq', 'tot_coll_amt', 'tot_cur_bal',
        'open_acc_6m', 'open_act_il', 'open_il_12m', 'open_il_24m',
        'mths_since_rcnt_il', 'il_util', 'open_rv_12m', 'open_rv_24m',
        'max_bal_bc', 'all_util', 'inq_fi', 'acc_open_past_24mths',
        'avg_cur_bal', 'bc_open_to_buy', 'bc_util', 'mo_sin_old_il_acct',
        'mo_sin_old_rev_tl_op', 'mo_sin_rcnt_rev_tl_op', 'mo_sin_rcnt_tl',
        'mort_acc', 'mths_since_recent_bc', 'mths_since_recent_bc_dlq',
        'mths_since_recent_inq', 'mths_since_recent_revol_delinq',
        'num_accts_ever_120_pd', 'num_actv_bc_tl', 'num_actv_rev_tl',
        'num_bc_sats', 'num_bc_tl', 'num_il_tl', 'num_op_rev_tl',
        'num_rev_accts', 'num_rev_tl_bal_gt_0', 'num_tl_120dpd_2m',
        'num_tl_30dpd', 'num_tl_90g_dpd_24m', 'num_tl_op_past_12m',
        'pct_tl_nvr_dlq', 'percent_bc_gt_75', 'tax_liens', 'tot_hi_cred_lim',
        'term_36 months', 'term_60 months', 'home_ownership_MORTGAGE',
        'home_ownership_OWN', 'home_ownership_Other', 'home_ownership_RENT',
        'purpose_business', 'purpose_credit_card', 'purpose_debt_consolidation',
        'purpose_house', 'purpose_medical', 'purpose_other', 'purpose_vehicle',
        'verification_status_Not Verified',
        'verification_status_Source Verified', 'verification_status_Verified',
        'sec_dti', 'sec_annual_inc', 'sec_fico_score', 'fico_score',
        'purpose_educational']
    
    def save_loan_app(self, loan: LoanApplicationModel, prediction : str, df_shap : pd.DataFrame, default_rate : float):
        cmd = """
            DECLARE @RESULT INT;

            EXEC dbo.PROC_SaveLoanApps
                @CUSTID=?,
                @application_type=?,
                @sec_app_pan=?,
                @loan_amnt=?,
                @term=?,
                @home_ownership=?,
                @purpose=?,
                @verification_status=?,
                @sec_dti=?,
                @sec_annual_inc=?,
                @sec_fico_score=?,
                @sec_app_avail=?,
                @pred_result=?,
                @default_rate=?,
                @shap=?,
                @RESULT=@RESULT OUTPUT;

            SELECT @RESULT AS RESULT;
        """

        params = [
            int(loan.CustomerID),                           # @CUSTID
            loan.ApplicationType,
            loan.SecAppPAN,                                 # @sec_app_pan
            float(loan.LoanAmount),                         # @loan_amnt
            loan.Term,                                      # @term
            loan.HomeOwnership,                             # @home_ownership
            loan.LoanPurpose,                               # @purpose
            loan.VerificationStatus,                        # @verification_status
            float(loan.SecAppDTI) if loan.SecAppDTI else None,              # @sec_dti
            float(loan.SecAppAnnualInc) if loan.SecAppAnnualInc else None,  # @sec_annual_inc
            int(loan.SecAppFICO) if loan.SecAppFICO else None,              # @sec_fico_score
            1 if loan.SecAppAvailable else 0,                # @sec_app_avail
            prediction,
            default_rate,
            str(df_shap),
        ]

        self.cursor.execute(cmd, params)
        result = self.cursor.fetchone()[0]

        self.conn.commit()
        self.cursor.close()
        self.conn.close()

        return result
    
    def save_cust_fin_data(self, row : dict):
        sql = """
            DECLARE @RESULT INT;

            EXEC dbo.PROC_SaveCustFinData
                @CUST_ID=?,
                @dti=?,
                @delinq_2yrs=?,
                @open_acc=?,
                @pub_rec=?,
                @revol_bal=?,
                @revol_util=?,
                @acc_now_delinq=?,
                @tot_coll_amt=?,
                @tot_cur_bal=?,
                @open_acc_6m=?,
                @open_act_il=?,
                @open_il_12m=?,
                @open_il_24m=?,
                @mths_since_rcnt_il=?,
                @il_util=?,
                @open_rv_12m=?,
                @open_rv_24m=?,
                @max_bal_bc=?,
                @all_util=?,
                @inq_fi=?,
                @acc_open_past_24mths=?,
                @avg_cur_bal=?,
                @bc_open_to_buy=?,
                @bc_util=?,
                @mo_sin_old_il_acct=?,
                @mo_sin_old_rev_tl_op=?,
                @mo_sin_rcnt_rev_tl_op=?,
                @mo_sin_rcnt_tl=?,
                @mort_acc=?,
                @mths_since_recent_bc=?,
                @mths_since_recent_bc_dlq=?,
                @mths_since_recent_inq=?,
                @mths_since_recent_revol_delinq=?,
                @num_accts_ever_120_pd=?,
                @num_actv_bc_tl=?,
                @num_actv_rev_tl=?,
                @num_bc_sats=?,
                @num_bc_tl=?,
                @num_il_tl=?,
                @num_op_rev_tl=?,
                @num_rev_accts=?,
                @num_rev_tl_bal_gt_0=?,
                @num_tl_120dpd_2m=?,
                @num_tl_30dpd=?,
                @num_tl_90g_dpd_24m=?,
                @num_tl_op_past_12m=?,
                @pct_tl_nvr_dlq=?,
                @percent_bc_gt_75=?,
                @tax_liens=?,
                @tot_hi_cred_lim=?,
                @FICO=?,
                @PAN=?,
                @AnnualIncome=?,
                @EmpLength=?,
                @RESULT=@RESULT OUTPUT;

            SELECT @RESULT AS RESULT;
        """

        # Build the parameter list IN THE EXACT ORDER REQUIRED
        #row = cust_fin_data.iloc[0]
        params = [
            row["cust_id"],
            row["dti"],
            row["delinq_2yrs"],
            row["open_acc"],
            row["pub_rec"],
            row["revol_bal"],
            row["revol_util"],
            row["acc_now_delinq"],
            row["tot_coll_amt"],
            row["tot_cur_bal"],
            row["open_acc_6m"],
            row["open_act_il"],
            row["open_il_12m"],
            row["open_il_24m"],
            row["mths_since_rcnt_il"],
            row["il_util"],
            row["open_rv_12m"],
            row["open_rv_24m"],
            row["max_bal_bc"],
            row["all_util"],
            row["inq_fi"],
            row["acc_open_past_24mths"],
            row["avg_cur_bal"],
            row["bc_open_to_buy"],
            row["bc_util"],
            row["mo_sin_old_il_acct"],
            row["mo_sin_old_rev_tl_op"],
            row["mo_sin_rcnt_rev_tl_op"],
            row["mo_sin_rcnt_tl"],
            row["mort_acc"],
            row["mths_since_recent_bc"],
            row["mths_since_recent_bc_dlq"],
            row["mths_since_recent_inq"],
            row["mths_since_recent_revol_delinq"],
            row["num_accts_ever_120_pd"],
            row["num_actv_bc_tl"],
            row["num_actv_rev_tl"],
            row["num_bc_sats"],
            row["num_bc_tl"],
            row["num_il_tl"],
            row["num_op_rev_tl"],
            row["num_rev_accts"],
            row["num_rev_tl_bal_gt_0"],
            row["num_tl_120dpd_2m"],
            row["num_tl_30dpd"],
            row["num_tl_90g_dpd_24m"],
            row["num_tl_op_past_12m"],
            row["pct_tl_nvr_dlq"],
            row["percent_bc_gt_75"],
            row["tax_liens"],
            row["tot_hi_cred_lim"],
            int(row["FICO"]),
            row["PAN"],
            row["annual_income"],
            row["emp_length"]
        ]

        self.cursor.execute(sql, params)

        # Fetch stored procedure OUTPUT value
        result = self.cursor.fetchone()[0]
        
        if(result and result == 1):
            print("Customer Financial Data Save Successful")
        else:
            print("Customer Financial Data Save Failed")

        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        
        return result

    def get_pan(self, pan : str):
        sql = """
            SELECT CASE 
                    WHEN EXISTS (SELECT 1 FROM CUST_FIN_DATA WHERE PAN = ?) 
                    THEN 1 ELSE 0 
                END AS PANExists;
        """

        self.cursor.execute(sql, (pan,))
        exists = self.cursor.fetchone()[0]

        self.cursor.close()
        self.conn.close()

        if exists == 1:
            print(f"PAN {pan} exists in CUST_FIN_DATA.")
        else:
            print(f"PAN {pan} does NOT exist in CUST_FIN_DATA.")
            
        return exists
    
    def save_app_data(self, user_profile : UserProfile):
        try:
            cmd = """
                DECLARE @RESULT INT;

                EXEC dbo.PROC_CustomerProfileUpdate
                    @UpdateValue=?,
                    @CUST_ID=?,
                    @ProfilePicture=?,
                    @PANImage=?,
                    @FirstName=?,
                    @MiddleName=?,
                    @LastName=?,
                    @Email=?,
                    @Phone=?,
                    @Password=?,
                    @DOB=?,
                    @PAN=?,
                    @FLAT=?,
                    @SOCIETY=?,
                    @LOCALITY=?,
                    @CITY=?,
                    @STATE=?,
                    @PINCODE=?,
                    @EmpLength=?,
                    @AnnualInc=?,
                    @RESULT=@RESULT OUTPUT;

                SELECT @RESULT AS RESULT;
            """

            params = [
                user_profile.update_type, 
                user_profile.cust_id,                           # @CUSTID
                user_profile.profile_picture_path,
                user_profile.pan_path,                                 # @sec_app_pan
                user_profile.first_name,                         # @loan_amnt
                user_profile.middle_name,                                      # @term
                user_profile.last_name,                             # @home_ownership
                user_profile.email,                               # @purpose
                user_profile.phone,                        # @verification_status
                user_profile.password,              # @sec_dti
                user_profile.date_of_birth,  # @sec_annual_inc
                user_profile.pan,              # @sec_fico_score
                user_profile.flat_no,                # @sec_app_avail
                user_profile.society,
                user_profile.locality,
                user_profile.city,
                user_profile.state,
                user_profile.pincode,
                user_profile.selected_emp_length,
                user_profile.annual_income,
            ]

            self.cursor.execute(cmd, params)
            result = self.cursor.fetchone()[0]

            self.conn.commit()
            self.cursor.close()
            self.conn.close()

            return result
        except:
            return -1
    #
    def check_sec_app_available(self, sec_app_pan : str):
        sql = """
            SELECT CASE 
                    WHEN EXISTS (SELECT 1 FROM CUSTOMER WHERE PAN = ?) 
                    THEN 1 ELSE 0 
                END AS CustFinExists;
        """

        self.cursor.execute(sql, (sec_app_pan,))
        exists = self.cursor.fetchone()[0]

        self.cursor.close()
        self.conn.close()

        return exists == 1
    #
    def get_customer_profile(self, customer_id : str):
        sql = """
            SELECT * FROM CUSTOMER A
            LEFT OUTER JOIN CUST_ADDRESS B ON A.CUST_ID = B.CUST_ID
            LEFT OUTER JOIN CUST_IMG C ON A.CUST_ID = C.CUST_ID
            WHERE A.CUST_ID = ?;
        """

        self.cursor.execute(sql, (customer_id,))
        rows = self.cursor.fetchall()
        
        columns = [column[0] for column in self.cursor.description]

        # Convert to DataFrame
        df = pd.DataFrame.from_records(rows, columns=columns)
        
        print(f"Data = {df}")

        self.cursor.close()
        self.conn.close()
        
        return df.iloc[0]
    
    def get_loan_details(self, customer_id : int, start = 0, end = 20, sorting = 'LoanID'):
        sql = """
            EXEC dbo.PROC_GetLoanDetails
                @CustomerID=?,
                @StartIndex = ?,
                @PageSize = ?,
                @Sorting = ?
        """

        self.cursor.execute(sql, (customer_id, start, end, sorting))
        rows = self.cursor.fetchall()
        
        columns = [column[0] for column in self.cursor.description]

        # Convert to DataFrame
        df = pd.DataFrame.from_records(rows, columns=columns)
        
        print(f"Data = {df}")
        
        # Get Total Records count
        self.cursor.nextset()
        total_count = self.cursor.fetchone()[0]

        self.cursor.close()
        self.conn.close()
        
        print(f"\nLoan Details DF = {df}\n")
        return df, total_count
    
    def get_cust_fin_details(self, customer_id : int):
        sql = """
            EXEC dbo.[PROC_GetCustFinDetails]
                @CustomerID=?
        """

        self.cursor.execute(sql, (customer_id,))
        rows = self.cursor.fetchall()
        
        columns = [column[0] for column in self.cursor.description]

        # Convert to DataFrame
        df = pd.DataFrame.from_records(rows, columns=columns)
        
        print(f"Data = {df}")

        self.cursor.close()
        self.conn.close()
        
        return df
    
    def get_cust_fin_data(self, loan_data : LoanApplicationModel):
        sql = """
        SELECT A.*, B.emp_length FROM CUST_FIN_DATA A
        RIGHT JOIN CUSTOMER B
        ON A.CUST_ID=B.CUST_ID
        WHERE A.CUST_ID = ?;
        """

        self.cursor.execute(sql, (loan_data.CustomerID,))
        rows = self.cursor.fetchall()
        
        columns = [column[0].lower() for column in self.cursor.description]

        # Convert to DataFrame
        df = pd.DataFrame.from_records(rows, columns=columns)
        df = self.map_fin_data_model(df.copy(), loan_data)
        print(f"Data = {df}")

        self.cursor.close()
        self.conn.close()
        
        if(df.shape[0] > 0):
            #return df.iloc[0]
            return df
        else:
            return df
        
    def map_fin_data_model(self, df_fin_data : pd.DataFrame, loan_data : LoanApplicationModel):
        df_cust_data = df_fin_data#pd.DataFrame(columns=df_fin_data.columns)
        df_cust_data["loan_amnt"] = loan_data.LoanAmount
        df_cust_data["application_type"] = 0 if loan_data.ApplicationType == "Individual" else 1
        
        df_cust_data["term_36 months"] = 1 if loan_data.Term == "36 months" else 0
        df_cust_data["term_60 months"] = 1 if loan_data.Term == "60 months" else 0
        df_cust_data["home_ownership_MORTGAGE"] = 0
        df_cust_data["home_ownership_OWN"] = 0
        df_cust_data["home_ownership_RENT"] = 0
        df_cust_data["home_ownership_Other"] = 0
        match(loan_data.HomeOwnership):
            case 'MORTGAGE':
                df_cust_data["home_ownership_MORTGAGE"] = 1
            case 'OWN':
                df_cust_data["home_ownership_OWN"] = 1
            case 'RENT':
                df_cust_data["home_ownership_RENT"] = 1
            case 'OTHER':
                df_cust_data["home_ownership_Other"] = 1
            case _:
                df_cust_data["home_ownership_Other"] = 1

        df_cust_data["purpose_debt_consolidation"] = 0                
        df_cust_data["purpose_vehicle"] = 0
        df_cust_data["purpose_credit_card"] = 0
        df_cust_data["purpose_house"] = 0
        df_cust_data["purpose_medical"] = 0
        df_cust_data["purpose_business"] = 0
        df_cust_data["purpose_educational"] = 0
        df_cust_data["purpose_other"] = 0
        match(loan_data.LoanPurpose):
            case 'debt_consolidation':
                df_cust_data["purpose_debt_consolidation"] = 1
            case 'vehicle':
                df_cust_data["purpose_vehicle"] = 1
            case 'credit_card':
                df_cust_data["purpose_credit_card"] = 1
            case 'house':
                df_cust_data["purpose_house"] = 1
            case 'medical':
                df_cust_data["purpose_medical"] = 1
            case 'other':
                df_cust_data["purpose_other"] = 1
            case 'business':
                df_cust_data["purpose_business"] = 1
            case 'educational':
                df_cust_data["purpose_educational"] = 1
            case _:
                df_cust_data["purpose_other"] = 1
                
        df_cust_data["verification_status_Verified"] = 0
        df_cust_data["verification_status_Not Verified"] = 0
        df_cust_data["verification_status_Source Verified"] = 0
        match(loan_data.VerificationStatus):
            case 'Verified':
                df_cust_data["verification_status_Verified"] = 1
            case 'Not Verified':
                df_cust_data["verification_status_Not Verified"] = 1
            case 'Source Verified':
                df_cust_data["verification_status_Source Verified"] = 1
                
        # Still have to add Secondary app fields
        df_cust_data["sec_annual_inc"] = loan_data.SecAppAnnualInc
        df_cust_data["sec_fico_score"] = loan_data.SecAppFICO
        df_cust_data["sec_dti"] = loan_data.SecAppDTI
        
        # Drop Irrelevant columns now
        df_cust_data.drop(['cust_id', 'pan'], axis=1, inplace=True)
        print(f"DF_CUST_COLUMNS = {df_cust_data.columns}")
        df_cust_data = df_cust_data.reindex(columns=self.X_columns)
        print(f"DF CUST DATA = {df_cust_data}\nCust data columns len = {df_cust_data.shape[1]}")
        return df_cust_data
    #
    def update_loan_app(self, loan_id : int, value : str):
        cmd = """
            DECLARE @RESULT INT;

            EXEC dbo.PROC_UpdateLoanApps
                @LoanID=?,
                @Value=?,
                @RESULT=@RESULT OUTPUT;

            SELECT @RESULT AS RESULT;
        """

        params = [
            loan_id,
            value
        ]

        self.cursor.execute(cmd, params)
        result = self.cursor.fetchone()[0]

        self.conn.commit()
        self.cursor.close()
        self.conn.close()

        return result