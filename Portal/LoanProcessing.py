from sre_constants import MAX_REPEAT
import hashlib
import math
from datetime import datetime
import numpy as np
import pandas as pd
import json
import joblib
import os
from collections import OrderedDict
from DB.DbHandle import DbHandle
from Model.LoanApplicationModel import LoanApplicationModel
import shap

class LoanProcessing:
    def __init__(self):
        self.root_dir = os.getcwd()
        self.ML_dir = "./ML/"
        self.model_name = "random_forest_classifier.sav"
        self.loan_columns = self.ML_dir + "loan_columns.csv"
        self.descriptive_features = pd.read_csv(self.loan_columns)
        self.loan_db_cols = ['CUST_ID', 'sec_app_pan', 'loan_amnt', 'term', 'home_ownership', 'purpose', 'verification_status', 'sec_dti', 'sec_annual_inc', 'sec_fico_score', 'SEC_APP_AVAIL', 'EMP_LENGTH', 'ANNUAL_INC']
    
    def incoming_data_process(self, loan_application_model : LoanApplicationModel):
        #data_str = data.replace("'", '"')
        #data_dict = json.loads(data_str)
        #print(f"Loaded Json data = {data_dict}")
        dict_customer = {}

        #customer_type = loan_application_model
        loan_amt = loan_application_model.LoanAmount
        term = loan_application_model.Term
        emp_length = loan_application_model.EmpLength
        annual_inc = loan_application_model.AnnualIncome
        application_type = loan_application_model.ApplicationType
        sec_annual_inc = loan_application_model.SecAppRevolUtil
        sec_dti = loan_application_model.SecAppFicoRangeLow
        #has_secondary_applicant = loan_application_model['has_secondary_applicant']
        home_ownership = loan_application_model.HomeOwnership
        loan_purpose = loan_application_model.LoanPurpose
        verification_status = loan_application_model.VerificationStatus

        if(term == '36 months'):
            term_36_months = 1
            term_60_months = 0
        else:
            term_36_months = 0
            term_60_months = 1

        if(application_type == 'Individual'):
            application_type = 0
            sec_annual_inc = 9999999
            sec_dti = 0
        else:
            application_type = 1
            #annual_inc += 50000 # Dummy value

        # Home Ownership
        home_ownership_MORTGAGE = 0
        home_ownership_OWN = 0
        home_ownership_RENT = 0
        home_ownership_OTHER = 0
        match(home_ownership):
            case 'MORTGAGE':
                home_ownership_MORTGAGE = 1
            case 'OWN':
                home_ownership_OWN = 1
            case 'RENT':
                home_ownership_RENT = 1
            case 'OTHER':
                home_ownership_OTHER = 1
            case _:
                home_ownership_OTHER = 1

        # Loan Purpose
        purpose_debt_consolidation = 0
        purpose_vehicle = 0
        purpose_credit_card = 0
        purpose_house = 0
        purpose_medical = 0
        purpose_other = 0
        purpose_business = 0
        purpose_educational = 0
        match(loan_purpose):
            case 'debt_consolidation':
                purpose_debt_consolidation = 1
            case 'vehicle':
                purpose_vehicle = 1
            case 'credit_card':
                purpose_credit_card = 1
            case 'house':
                purpose_house = 1
            case 'medical':
                purpose_medical = 1
            case 'other':
                purpose_other = 1
            case 'business':
                purpose_business = 1
            case 'educational':
                purpose_educational = 1
            case _:
                purpose_other = 1

        # Verification Status
        verification_status_Verified = 0
        verification_status_Not_Verified = 0
        verification_status_Source_Verified = 0
        print(f"Verification Status = {verification_status}")
        match(verification_status):
            case 'Verified':
                verification_status_Verified = 1
            case 'Not Verified':
                verification_status_Not_Verified = 1
            case 'Source Verified':
                verification_status_Source_Verified = 1

        dict_customer = {
            'loan_amnt': loan_amt,
            'term_36 months': term_36_months,
            'term_60 months': term_60_months,
            'emp_length': emp_length,
            'annual_inc': annual_inc,
            'application_type': application_type,
            'sec_annual_inc' : sec_annual_inc,
            'sec_dti' : sec_dti,
            #'has_secondary_applicant': has_secondary_applicant,
            'home_ownership_MORTGAGE': home_ownership_MORTGAGE,
            'home_ownership_OWN': home_ownership_OWN,
            'home_ownership_RENT': home_ownership_RENT,
            'home_ownership_OTHER': home_ownership_OTHER,
            'purpose_debt_consolidation': purpose_debt_consolidation,
            'purpose_vehicle': purpose_vehicle,
            'purpose_credit_card': purpose_credit_card,
            'purpose_house': purpose_house,
            'purpose_medical': purpose_medical,
            'purpose_other': purpose_other,
            'purpose_business': purpose_business,
            'purpose_educational': purpose_educational,
            'verification_status_Verified': verification_status_Verified,
            'verification_status_Not Verified': verification_status_Not_Verified,
            'verification_status_Source Verified': verification_status_Source_Verified
            #'sec_app_worth': sec_app_worth
            #'sec_app_fico_low_range' : sec_app_fico_range_low,
            #'sec_app_revol_util' : sec_app_revol_util
            #

        }

        #df_customer = pd.DataFrame(dict_customer, index=[0])
        print(f"dict_customer = {dict_customer}")
        # Home ownership
        # Customer Type = 0 -> New Customer
        #if(customer_type == 0):
        #    pass
        # Customer Type = 1 -> Existing Customer
        #else:
        #    pass


        return dict_customer

    def generate_credit_bureau_features(self, basic_app_features):
        """
        Generate credit bureau features deterministically from ALL basic application features
        using mathematical transformations only
        """

        # Create comprehensive seed from ALL basic features
        seed_parts = []
        for key, value in basic_app_features.items():
            seed_parts.append(f"{key}{value}")
        seed_data = "".join(seed_parts)
        seed_hash = hashlib.md5(seed_data.encode()).hexdigest()
        seed_int = int(seed_hash[:8], 16)

        # Extract ALL basic features with defaults
        loan_amnt = basic_app_features.get('loan_amnt', 10000)
        annual_inc = basic_app_features.get('annual_inc', 50000)
        emp_length = basic_app_features.get('emp_length', 3)
        application_type = basic_app_features.get('application_type', 'Individual')
        sec_annual_inc = basic_app_features.get('sec_annual_inc', 0)
        sec_dti = basic_app_features.get('sec_dti', 0)
        #has_secondary_applicant = basic_app_features.get('has_secondary_applicant', 0)
        #sec_app_fico_low = basic_app_features.get('sec_app_fico_range_low')
        #sec_app_revol_util = basic_app_features.get('sec_app_revol_util')

        # Home ownership features
        print(f"{basic_app_features}")
        home_ownership = 'RENT'  # Default
        for home_type in ['MORTGAGE', 'OWN', 'RENT', 'OTHER']:
            if basic_app_features.get(f'home_ownership_{home_type}', 0) == 1:
                home_ownership = home_type
                break

        # Loan purpose
        loan_purpose = 'debt_consolidation'  # Default
        for purpose in ['vehicle', 'credit_card', 'debt_consolidation', 'home_improvement',
                    'house', 'business', 'medical', 'other', 'educational']:
            if basic_app_features.get(f'purpose_{purpose}', 0) == 1:
                loan_purpose = purpose
                break

        # Verification status
        verification_status = 'Not Verified'  # Default
        for status in ['Not Verified', 'Source Verified', 'Verified']:
            if basic_app_features.get(f'verification_status_{status.replace(" ", "_")}', 0) == 1:
                verification_status = status
                break

        # Loan term
        term_36_months = basic_app_features.get('term_36 months', 0)
        term_60_months = basic_app_features.get('term_60 months', 0)
        loan_term = 36 if term_36_months else 60

        # Calculate comprehensive factors from ALL basic features
        income_ratio = min(2.0, loan_amnt / max(1, annual_inc))
        employment_factor = min(1.0, emp_length / 10.0)

        # Home ownership factor (better credit for homeowners)
        home_owner_factor = 1.2 if home_ownership in ['MORTGAGE', 'OWN'] else 1.0

        # Loan purpose factor (riskier purposes get worse credit)
        purpose_risk_factors = {
            'vehicle' : 1.0, 'credit_card' : 0.9, 'debt_consolidation' : 0.6,
                    'house' : 1.2, 'business' : 1.5, 'medical' : 1.0, 'other' : 0.4, 'educational' : 1.0
        }
        #purpose_risk_factors = {
        #    'debt_consolidation': 1.0, 'home_improvement': 1.1, 'house': 1.2,
        #    'car': 1.0, 'major_purchase': 1.0, 'medical': 0.9, 'credit_card': 0.9,
        #    'small_business': 0.8, 'educational': 1.1, 'wedding': 1.0,
        #    'moving': 0.9, 'vacation': 0.8, 'renewable_energy': 1.0, 'other': 0.9
        #}
        purpose_factor = purpose_risk_factors.get(loan_purpose, 1.0)

        # Verification status factor
        verification_factors = {
            'Verified': 1.2,
            'Source Verified': 1.1,
            'Not Verified': 1.0
        }
        verification_factor = verification_factors.get(verification_status, 1.0)

        # Loan term factor (longer term = higher risk)
        term_factor = 0.9 if loan_term == 60 else 1.0

        # Application type factor
        app_type_factor = 1.1 if application_type == 'Joint' else 1.0

        # Combined risk modifier
        combined_modifier = (home_owner_factor * purpose_factor * verification_factor *
                            term_factor * app_type_factor)

        credit_features = {}

        # FICO & Credit Scores (300-850) - influenced by ALL basic factors
        base_score = 300 + self.deterministic_value(seed_int, 1, 550, modifier=combined_modifier)
        employment_bonus = min(50, emp_length * 5)
        income_bonus = min(30, int(annual_inc / 10000))
        # Additional bonuses based on home ownership and verification
        home_bonus = 20 if home_ownership in ['MORTGAGE', 'OWN'] else 0
        verification_bonus = 15 if verification_status == 'Verified' else 0
        credit_features['fico_score'] = min(850, base_score + employment_bonus +
                                        income_bonus + home_bonus + verification_bonus)

        # Delinquency History - influenced by employment and income
        emp_delinq_modifier = max(0.5, 1.0 - (emp_length * 0.05))
        income_delinq_modifier = max(0.5, 1.0 - (annual_inc / 200000))

        credit_features['delinq_2yrs'] = self.deterministic_value(seed_int, 2, 5, modifier=emp_delinq_modifier * income_delinq_modifier)
        credit_features['acc_now_delinq'] = self.deterministic_value(seed_int, 3, 3, modifier=emp_delinq_modifier)
        credit_features['pub_rec'] = self.deterministic_value(seed_int, 4, 4, modifier=emp_delinq_modifier)
        credit_features['tax_liens'] = self.deterministic_value(seed_int, 5, 2, modifier=income_delinq_modifier)

        # Payment delinquency metrics - influenced by loan purpose
        purpose_delinq_modifier = 1.2 if loan_purpose in ['small_business', 'medical'] else 1.0
        credit_features['num_tl_30dpd'] = self.deterministic_value(seed_int, 6, 8, modifier=purpose_delinq_modifier)
        credit_features['num_tl_120dpd_2m'] = self.deterministic_value(seed_int, 7, 3, modifier=purpose_delinq_modifier)
        credit_features['num_tl_90g_dpd_24m'] = self.deterministic_value(seed_int, 8, 5, modifier=purpose_delinq_modifier)
        credit_features['num_accts_ever_120_pd'] = self.deterministic_value(seed_int, 9, 6, modifier=purpose_delinq_modifier)

        # Credit Accounts - influenced by income and employment
        income_account_modifier = min(2.0, annual_inc / 50000)
        base_accounts = max(3, int(emp_length * 2))
        total_accounts = base_accounts + self.deterministic_value(seed_int, 10, 40, modifier=income_account_modifier)
        credit_features['open_acc'] = total_accounts

        # Account type distribution influenced by home ownership and loan purpose
        home_installment_modifier = 1.5 if home_ownership in ['MORTGAGE', 'OWN'] else 1.0
        installment_accounts = self.deterministic_value(seed_int, 11, min(20, total_accounts), modifier=home_installment_modifier)
        credit_features['open_act_il'] = installment_accounts
        credit_features['num_il_tl'] = installment_accounts

        # Revolving accounts influenced by loan purpose
        purpose_rev_modifier = 1.3 if loan_purpose == 'credit_card' else 1.0
        rev_accounts = self.deterministic_value(seed_int, 12, min(25, total_accounts - installment_accounts), modifier=purpose_rev_modifier)
        credit_features['num_rev_accts'] = rev_accounts
        credit_features['num_op_rev_tl'] = rev_accounts

        # Bankcard accounts
        bankcard_accounts = self.deterministic_value(seed_int, 13, min(15, rev_accounts))
        credit_features['num_bc_tl'] = bankcard_accounts
        credit_features['num_rev_tl_bal_gt_0'] = self.deterministic_value(seed_int, 14, rev_accounts)

        # Credit Utilization & Balances - heavily influenced by income
        income_limit_modifier = min(3.0, annual_inc / 50000)
        total_credit_limit = max(5000, annual_inc * 0.6 * income_limit_modifier)
        credit_features['tot_hi_cred_lim'] = total_credit_limit + self.deterministic_value(seed_int, 15, 50000, modifier=income_limit_modifier)

        # Revolving calculations influenced by loan amount
        loan_util_modifier = min(1.5, loan_amnt / 10000)
        rev_util_rate = self.deterministic_value(seed_int, 16, 100, modifier=loan_util_modifier) / 100.0
        credit_features['revol_util'] = rev_util_rate * 100
        credit_features['revol_bal'] = int(total_credit_limit * rev_util_rate * 0.7)

        credit_features['tot_cur_bal'] = credit_features['revol_bal'] + self.deterministic_value(seed_int, 17, 50000, modifier=income_limit_modifier)
        credit_features['max_bal_bc'] = self.deterministic_value(seed_int, 18, 20000, modifier=income_limit_modifier)

        # Utilization metrics influenced by verification status
        verification_util_modifier = 0.8 if verification_status == 'Verified' else 1.0
        credit_features['all_util'] = self.deterministic_value(seed_int, 19, 85, modifier=verification_util_modifier)
        credit_features['bc_util'] = self.deterministic_value(seed_int, 20, 90, modifier=verification_util_modifier)
        credit_features['bc_open_to_buy'] = max(0, total_credit_limit - credit_features['revol_bal'])

        # Recent Activity - influenced by loan term and application type
        term_activity_modifier = 1.2 if loan_term == 60 else 1.0
        joint_app_modifier = 1.3 if application_type == 'Joint' else 1.0

        credit_features['open_acc_6m'] = self.deterministic_value(seed_int, 21, 8, modifier=term_activity_modifier)
        credit_features['open_il_12m'] = self.deterministic_value(seed_int, 22, 5, modifier=joint_app_modifier)
        credit_features['open_il_24m'] = credit_features['open_il_12m'] + self.deterministic_value(seed_int, 23, 3, modifier=joint_app_modifier)
        credit_features['open_rv_12m'] = self.deterministic_value(seed_int, 24, 6, modifier=term_activity_modifier)
        credit_features['open_rv_24m'] = credit_features['open_rv_12m'] + self.deterministic_value(seed_int, 25, 4, modifier=term_activity_modifier)
        credit_features['num_tl_op_past_12m'] = credit_features['open_il_12m'] + credit_features['open_rv_12m']
        credit_features['inq_fi'] = self.deterministic_value(seed_int, 26, 12, modifier=term_activity_modifier)
        credit_features['acc_open_past_24mths'] = credit_features['open_il_24m'] + credit_features['open_rv_24m']

        # Time-Based Metrics - influenced by employment length
        emp_time_modifier = 1 if emp_length < 1 else min(2.0, emp_length / 3.0)
        credit_features['mths_since_rcnt_il'] = self.deterministic_value(seed_int, 27, 36, modifier=1/emp_time_modifier)
        credit_features['mo_sin_old_il_acct'] = max(12, self.deterministic_value(seed_int, 28, 240, modifier=emp_time_modifier))
        credit_features['mo_sin_old_rev_tl_op'] = max(6, self.deterministic_value(seed_int, 29, 180, modifier=emp_time_modifier))
        credit_features['mo_sin_rcnt_rev_tl_op'] = self.deterministic_value(seed_int, 30, 24, modifier=1/emp_time_modifier)
        credit_features['mo_sin_rcnt_tl'] = self.deterministic_value(seed_int, 31, 18, modifier=1/emp_time_modifier)
        credit_features['mths_since_recent_bc'] = self.deterministic_value(seed_int, 32, 24, modifier=1/emp_time_modifier)
        credit_features['mths_since_recent_inq'] = self.deterministic_value(seed_int, 33, 12, modifier=1/emp_time_modifier)

        # Delinquency time metrics - influenced by home ownership
        home_delinq_modifier = 0.7 if home_ownership in ['MORTGAGE', 'OWN'] else 1.0
        credit_features['mths_since_recent_bc_dlq'] = self.deterministic_value(seed_int, 34, 60, modifier=home_delinq_modifier)
        if credit_features['mths_since_recent_bc_dlq'] == 0:
            credit_features['mths_since_recent_bc_dlq'] = 999

        credit_features['mths_since_recent_revol_delinq'] = self.deterministic_value(seed_int, 35, 48, modifier=home_delinq_modifier)
        if credit_features['mths_since_recent_revol_delinq'] == 0:
            credit_features['mths_since_recent_revol_delinq'] = 999

        # Additional Credit Metrics
        credit_features['il_util'] = self.deterministic_value(seed_int, 36, 80)

        # Mortgage accounts directly influenced by home ownership
        if home_ownership == 'MORTGAGE':
            credit_features['mort_acc'] = 1 + self.deterministic_value(seed_int, 37, 3)
        else:
            credit_features['mort_acc'] = self.deterministic_value(seed_int, 37, 2)

        credit_features['num_actv_bc_tl'] = max(0, bankcard_accounts - self.deterministic_value(seed_int, 38, bankcard_accounts))
        credit_features['num_actv_rev_tl'] = max(0, rev_accounts - self.deterministic_value(seed_int, 39, rev_accounts))

        credit_features['num_bc_sats'] = self.deterministic_value(seed_int, 40, 8)
        credit_features['percent_bc_gt_75'] = self.deterministic_value(seed_int, 41, 100)

        # Percentage never delinquent - influenced by verification status
        verification_delinq_modifier = 1.2 if verification_status == 'Verified' else 1.0
        never_delinq_pct = max(50, 100 - (credit_features['delinq_2yrs'] * 10 +
                                        credit_features['num_tl_30dpd'] * 5))
        credit_features['pct_tl_nvr_dlq'] = min(100, never_delinq_pct * verification_delinq_modifier)

        # Balance metrics
        if total_accounts > 0:
            credit_features['avg_cur_bal'] = credit_features['tot_cur_bal'] / total_accounts
        else:
            credit_features['avg_cur_bal'] = 0

        # Collection amount influenced by loan purpose
        purpose_coll_modifier = 1.5 if loan_purpose in ['medical', 'educational', 'house', 'business'] else 1.0
        credit_features['tot_coll_amt'] = self.deterministic_value(seed_int, 42, 10000, modifier=purpose_coll_modifier)

        # Debt settlement influenced by income and employment
        # debt_settlement_chance = max(1, min(10, 10 - emp_length + int(income_ratio * 5)))
        # credit_features['debt_settlement_flag'] = 1 if deterministic_value(43, 100) < debt_settlement_chance else 0

        # Secondary applicant worth (if applicable)
        # if has_secondary_applicant:
        #     sec_app_modifier = deterministic_value(44, 100) / 100.0
        #     # Higher worth for verified joint applications
        #     if verification_status == 'Verified':
        #         sec_app_modifier *= 1.5
        #     credit_features['sec_app_worth'] = annual_inc * sec_app_modifier
        # else:
        #     credit_features['sec_app_worth'] = 0


        # DTI - influenced by income and loan purpose
        base_dti = np.where(
            loan_purpose == 'debt_consolidation', 25,
            np.where(loan_purpose == 'credit_card', 22,
                    np.where(loan_amnt / annual_inc > 0.3, 28, 18))
        )
        credit_features['dti'] = np.clip(base_dti + self.deterministic_value(seed_int, 43, 10, min_val=-5), 5, 45)
        credit_features['sec_annual_inc'] = sec_annual_inc
        credit_features['sec_dti'] = sec_dti
        w1 = 1.8
        w2 = 10
        credit_features['sec_fico_score'] = (850 - sec_dti * w1 + np.log(sec_annual_inc) * w2)

        return credit_features
        
    def deterministic_value(self, seed_int, index, max_val, min_val=0, modifier=1.0):
        """Generate deterministic values using trigonometric functions"""
        
        angle = (seed_int + index * 137) % 360
        trig_val = abs(math.sin(math.radians(angle)) + math.cos(math.radians(angle * 3)))
        value = min_val + int((trig_val * (max_val - min_val) * modifier) % (max_val - min_val + 1))
        return max(min_val, min(max_val, value))
        
        #return credit_features
    
    def customer_data_preprocessing(self, data : LoanApplicationModel):
        print("Incoming Data")
        customer_data = self.incoming_data_process(data)
        #print(f"Loaded Json data = {data_dict}")
        print("Step 1 done")

        # Generate credit bureau features
        credit_bureau_data = self.generate_credit_bureau_features(customer_data)
        print("Step 2 done")

        # Define the comprehensive list of expected columns
        X_columns = ['loan_amnt', 'emp_length', 'annual_inc', 'dti',
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
        'home_ownership_OWN', 'home_ownership_OTHER', 'home_ownership_RENT',
        'purpose_business', 'purpose_credit_card', 'purpose_debt_consolidation',
        'purpose_house', 'purpose_medical', 'purpose_other', 'purpose_vehicle',
        'verification_status_Not Verified',
        'verification_status_Source Verified', 'verification_status_Verified',
        'sec_dti', 'sec_annual_inc', 'sec_fico_score', 'fico_score',
        'purpose_educational']

        df_basic = pd.DataFrame(customer_data, index=[0])
        df_credit_bureau = pd.DataFrame(credit_bureau_data, index=[0])
        print("Step 3 done")

        # Remove overlapping columns from df_credit_bureau before concatenation
        # These columns are already present in df_basic from the input customer_data
        overlap_cols = ['sec_annual_inc', 'sec_dti']
        df_credit_bureau = df_credit_bureau.drop(columns=[col for col in overlap_cols if col in df_credit_bureau.columns], errors='ignore')

        df_simulated_data = pd.concat([df_basic, df_credit_bureau], axis=1)

        # The line below was used for debugging, keeping for reference but not needed for execution
        # print(f"{{[x for x in set(X_columns) if X_columns.count(x) > 1]}}")

        df_simulated_data = df_simulated_data.reindex(columns=X_columns)
        df_simulated_data.rename({'home_ownership_OTHER' : 'home_ownership_Other'}, axis=1, inplace=True)
        print("Step 4 done")
        return df_simulated_data
    
    def prediction(self, customer_data : pd.DataFrame):
        model_path = self.root_dir + self.ML_dir + self.model_name        
        model = joblib.load(model_path)
        pred = model.predict(customer_data)
        default_prob = model.predict_proba(customer_data)[0][0]
        repay_prob = model.predict_proba(customer_data)[0][1]
        
        return ["Approved" if pred == 1 else "Rejected", default_prob * 100]
    #
    def get_top_features_df(self, shap_values, feature_names, relevant_features, prediction, top_n=5):
        """
        Return top features as a DataFrame
        """
        if isinstance(shap_values, list):
            shap_array = shap_values[0][0]  # For binary classification
        else:
            shap_array = shap_values[0]     # For regression or newer API

        
        shap_dict = dict()
        for (feature, shap_val) in zip(feature_names, shap_array):
            #desc_feat = self.descriptive_features[feature]
            shap_dict[feature] = shap_val

        new_shap_dict = dict()
        for k, v in shap_dict.items():
            if(k in relevant_features):
                new_shap_dict[k] = shap_dict[k]
        #print(f"New shap dict = {new_shap_dict}")
        shap_dict_sorted = dict(sorted(new_shap_dict.items(), key=lambda item : item[1]))
        '''print(f"Sorted dict = {shap_dict_sorted}")
        
        top_df_dict = dict()
        if(prediction == "Rejected"):
            for i in range(top_n):
                #print(shap_dict_sorted[i])
                top_df_dict[shap_dict_sorted[i][0]] = shap_dict_sorted[i][1]
        else:
            print("APPROVED")
            for i in range(len(shap_dict_sorted)-1, len(shap_dict_sorted) - top_n - 1, -1):
                #print(shap_dict_sorted[i])
                top_df_dict[shap_dict_sorted[i][0]] = shap_dict_sorted[i][1]
        
        return top_df_dict'''
        return shap_dict_sorted
        
    #
    def shap_explainer(self, customer_data : pd.DataFrame, prediction, top_n = -1):
        model_path = self.root_dir + self.ML_dir + self.model_name        
        model = joblib.load(model_path)
        explainer = shap.TreeExplainer(model)
        shap_values_cust = explainer.shap_values(customer_data)
        shap_values_cust_0 = shap_values_cust[:, :, 0]
        #print(f"Shap values = {shap_values_cust_0}")
        #print(explainer.expected_value)
        #print(shap_values_cust_0[0])

        # Uncomment to see Waterfall model of Features importance and their contribution to the Random Forest Prediction
        '''
        shap.plots._waterfall.waterfall_legacy(
            explainer.expected_value[0],    # expected value for class 0
            shap_values_cust_0[0],         # SHAP values for that row
            feature_names=df_simulated_data.columns
        )
        '''
        #print(f"Incoming Customer data = {customer_data}")
        relevant_data = self.get_relevant_features(customer_data)
        #print(f"Relevant data = {relevant_data}")
        top_features = self.get_top_features_df(shap_values=shap_values_cust_0, feature_names=customer_data.columns, relevant_features=relevant_data, prediction=prediction, top_n=top_n)
        #print(f"Top features = {top_features}")
        return top_features
    #
    def get_relevant_features(self, customer_data : pd.DataFrame):
        row = customer_data.iloc[0]
        relevant_data = row[row != 0]
        #print(f"Relevant features = {relevant_data.index.to_list()}")
        #print(f"Relevant features = {customer_data[customer_data != 0]}")
        
        return relevant_data.index.to_list()
    #
    def get_features_description(self):
        print(self.descriptive_features.head())
    #
    def loan_apps(self, loan_model : LoanApplicationModel, prediction : str, df_shap, default_rate : float):
        db_handle = DbHandle()
        result = db_handle.save_loan_app(loan_model, prediction, df_shap, default_rate)
        return result
    
    #
    def loan_details(self, customer_id : int, start = 0, end = 20, sorting = "LoanID"):
        db_handle = DbHandle()
        df, total_count = db_handle.get_loan_details(customer_id, start, end, sorting)
        
        return df.to_dict(orient='records'), total_count
    
    def cust_fin_details(self, customer_id : int):
        db_handle = DbHandle()
        df : pd.DataFrame = db_handle.get_cust_fin_details(customer_id)
        
        return df.to_dict(orient='records')
    
    def update_loan_apps(self, loan_id : int, value : str):
        db_handle = DbHandle()
        result = db_handle.update_loan_app(loan_id, value)
        return result