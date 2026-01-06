import pandas as pd
import numpy as np
import random
from Model.LoanApplicationModel import LoanApplicationModel
from Model.UserProfile import UserProfile
from DB import DbHandle

class ProfileProcessing:
    def __init__(self):
        random.seed(298)
    
    def update(self, user_profile : UserProfile):
        # Generate Credit bureau data for NEW CUSTOMER ONLY
        if(not user_profile.is_update):
            db_handle = DbHandle.DbHandle()
            profile_save = db_handle.save_app_data(user_profile)
            if(profile_save == -1):
                return pd.DataFrame(), profile_save
            data = self.generate_customer_financials(user_profile.selected_emp_length, user_profile.annual_income)
            data["PAN"] = user_profile.pan
            #data["FICO"] = 829
            data["cust_id"] = user_profile.cust_id
            data["annual_income"] = user_profile.annual_income
            data["emp_length"] = user_profile.selected_emp_length
            print(f"Update data = {data}")
        
            db_handle = DbHandle.DbHandle()
            result = db_handle.save_cust_fin_data(data)
        
            return data, result
        '''
        else:
            #df_cust_data = self.get_cust_fin_data(user_profile.cust_id)
            data = self.generate_customer_financials(user_profile.selected_emp_length, user_profile.annual_income)
            data["PAN"] = user_profile.pan
            #data["FICO"] = 829
            data["cust_id"] = user_profile.cust_id
            data["annual_income"] = user_profile.annual_income
            data["emp_length"] = user_profile.selected_emp_length
            print(f"Update data = {data}")
        
            db_handle = DbHandle.DbHandle()
            result = db_handle.save_cust_fin_data(data)
        
            return data, result
        '''

    def generate_customer_financials(self, emp_length, annual_inc):
        """
        Generate realistic dummy customer financial data based on:
        - emp_length   : int (years)
        - annual_inc   : float or int
        """

        # Safety
        emp_length = max(0, min(emp_length, 40)) if emp_length > 0 else 1
        #annual_inc = max(10000, annual_inc)

        # Income influence factor
        income_factor = annual_inc / 100000

        # Employment stability influence
        emp_factor = emp_length / 10

        data = {}

        # Debt-To-Income Ratio (lower for higher income/stability)
        data["dti"] = round(max(1, np.random.normal(15 / (income_factor+0.5), 5)), 2)

        # Delinquencies (less with higher emp_length)
        data["delinq_2yrs"] = max(0, int(np.random.poisson(1 - 0.1*emp_factor)))

        # Number of open accounts
        data["open_acc"] = int(np.random.normal(10 + emp_factor*2, 3))

        data["pub_rec"] = random.choice([0, 0, 0, 1])  # Rare

        # Revolving balance based on income
        data["revol_bal"] = max(0, int(np.random.normal(annual_inc * 0.1, 2000)))

        # Revolving utilization
        data["revol_util"] = round(random.uniform(5, 60 - emp_factor*3), 1)

        #data["application_type"] = random.choice(["Individual", "Joint"])

        data["acc_now_delinq"] = 0

        data["tot_coll_amt"] = max(0, int(np.random.exponential(500)))
        data["tot_cur_bal"] = int(data["open_acc"] * np.random.uniform(1000, 8000))

        # Installment loan activity
        data["open_acc_6m"] = max(0, int(np.random.poisson(1)))
        data["open_act_il"] = max(0, int(np.random.poisson(2)))
        data["open_il_12m"] = max(0, int(np.random.poisson(1)))
        data["open_il_24m"] = max(0, int(np.random.poisson(2)))
        data["mths_since_rcnt_il"] = random.randint(0, 36)
        data["il_util"] = round(random.uniform(10, 80), 1)

        data["open_rv_12m"] = int(np.random.poisson(1))
        data["open_rv_24m"] = int(np.random.poisson(1.5))

        data["max_bal_bc"] = int(np.random.uniform(1000, 8000))

        data["all_util"] = round(random.uniform(10, 70), 1)

        #data["inq_fi"] = int(np.random.poisson(1 + (1-income_factor)))
        data["inq_fi"] = int(np.random.poisson(max(0.01, 2 - income_factor)))

        data["acc_open_past_24mths"] = random.randint(1, 10)

        data["avg_cur_bal"] = int(data["tot_cur_bal"] / max(1, data["open_acc"]))

        data["bc_open_to_buy"] = int(np.random.uniform(1000, 15000))
        data["bc_util"] = round(random.uniform(10, 80), 1)

        # Age of accounts (distributions based on stability)
        data["mo_sin_old_il_acct"] = random.randint(12, 180)
        data["mo_sin_old_rev_tl_op"] = random.randint(6, 200)
        data["mo_sin_rcnt_rev_tl_op"] = random.randint(1, 24)
        data["mo_sin_rcnt_tl"] = random.randint(1, 24)

        data["mort_acc"] = max(0, int(np.random.poisson(0.5 + emp_factor)))

        data["mths_since_recent_bc"] = random.randint(0, 36)
        data["mths_since_recent_bc_dlq"] = random.randint(0, 48)
        data["mths_since_recent_inq"] = random.randint(0, 12)
        data["mths_since_recent_revol_delinq"] = random.randint(0, 60)

        data["num_accts_ever_120_pd"] = random.choice([0, 0, 0, 1])
        data["num_actv_bc_tl"] = random.randint(1, 6)
        data["num_actv_rev_tl"] = random.randint(1, 6)
        data["num_bc_sats"] = random.randint(1, 6)
        data["num_bc_tl"] = random.randint(1, 10)
        data["num_il_tl"] = random.randint(1, 10)
        data["num_op_rev_tl"] = random.randint(1, 10)
        data["num_rev_accts"] = random.randint(1, 12)
        data["num_rev_tl_bal_gt_0"] = random.randint(1, 10)

        data["num_tl_120dpd_2m"] = 0
        data["num_tl_30dpd"] = random.choice([0, 0, 1])
        data["num_tl_90g_dpd_24m"] = random.choice([0, 0, 1])

        data["num_tl_op_past_12m"] = random.randint(1, 6)

        data["pct_tl_nvr_dlq"] = round(random.uniform(70, 100), 1)
        data["percent_bc_gt_75"] = random.randint(0, 100)

        data["tax_liens"] = random.choice([0, 0, 1])

        data["tot_hi_cred_lim"] = int(np.random.uniform(annual_inc * 0.5, annual_inc * 3))
        data["FICO"] = 300 + ((0.6 * min(annual_inc / 1000, 100)) + (0.4 * min(emp_length * 10, 100))) * 5.5

        return data   
#
    def check_fin_data_exist(self, customer_id : str):
        db_handle = DbHandle.DbHandle()
        return db_handle.check_cust_fin_exist(customer_id)
#
    def get_customer_profile(self, customer_id : str):
        db_handle = DbHandle.DbHandle()
        profile_data = db_handle.get_customer_profile(customer_id)
        return profile_data.to_dict()
    
    def get_cust_fin_data(self, loan_data : LoanApplicationModel):
        db_handle = DbHandle.DbHandle()
        cust_fin_data = db_handle.get_cust_fin_data(loan_data)
        #return cust_fin_data.to_dict()
        return cust_fin_data
        