from fastapi import FastAPI
from Model.LoanApplicationModel import LoanApplicationModel, LoanUpdateModel
from Model.UserProfile import UserProfile
from Portal.LoanProcessing import LoanProcessing
from Portal.ProfileProcessing import ProfileProcessing
from DB.DbHandle import DbHandle
import json
import pandas as pd

app = FastAPI()

@app.get("/")
def index():
    return {"message" : "Bhai Its working na full kadak!!!!"}

@app.post("/loanprediction")
async def loanprediction(loan_prediction_model : LoanApplicationModel):
    print(f"Loan Application = {loan_prediction_model}")
    
    loan_processing = LoanProcessing()
    '''
    customer_data = loan_processing.customer_data_preprocessing(loan_prediction_model)
    
    pred, pred_prob = loan_processing.prediction(customer_data) # Prediction
    shap_explanation = loan_processing.shap_explainer(customer_data, prediction=pred, top_n=10)
    #return {"Received Model" : customer_data.to_json()}
    return {"Prediction" : pred, "Default Probability" : f"{pred_prob}%", "SHAP Features" : shap_explanation}
    '''
    profile_process = ProfileProcessing()
    fin_data = profile_process.get_cust_fin_data(loan_prediction_model)
    print("GENERATED FIN DF")
    pred, pred_proba = loan_processing.prediction(fin_data)
    print("PERFORMED PREDICTION")
    shap_explanation = loan_processing.shap_explainer(fin_data, prediction=pred, top_n=-1)
    print(f"PERFORMED SHAP EXPLAIN = {str(shap_explanation)}")
    db_result = loan_processing.loan_apps(loan_prediction_model, pred, shap_explanation, pred_proba)
    #shap_result = loan_processing.save_shap_explain(df_shap=shap_explanation)
    print(f"DB RESULT = {db_result}")
    return {"LoanDetails" : fin_data.iloc[0].to_dict(), "Prediction" : pred, "Probability" : pred_proba, "SHAP" : shap_explanation, "LoanSaved" : db_result}
    #return {"LoanDetails" : fin_data.iloc[0].to_dict(), "Prediction" : pred, "Probability" : pred_proba, "SHAP" : shap_explanation, "LoanSaved" : 1}

@app.put("/profileupdate")
def profileupdate(user_profile : UserProfile):
    print(f"User Profile data = {user_profile}")
    profile_process = ProfileProcessing()
    profile, result = profile_process.update(user_profile)
    #return {"Update" : result, "UserProfile" : profile}
    return {"result" : result, "profile" : profile}

@app.get("/custfindata")
def custfindata(customer_id : str):
    profile_process = ProfileProcessing()
    exists = profile_process.check_fin_data_exist(customer_id=customer_id)
    cust_fin_data = profile_process.get_cust_fin_data(customer_id)
    return {"CustomerExists" : exists, "FinData" : cust_fin_data}

'''
@app.get("/checkcustfinexist")
def checkcustfinexist(customer_id : str):
    profile_process = ProfileProcessing()
    profile : pd.DataFrame = profile_process.get_customer_profile(customer_id)
    return {"ProfileData" : profile}
'''

@app.get('/customerprofile')
def customerprofile(customer_id : str):
    profile_process = ProfileProcessing()
    profile = profile_process.get_customer_profile(customer_id)
    return {"ProfileData" : profile}

@app.get('/custloandetails')
def custloandetails(customer_id : int, start = 0, end = 20, sorting = "LoanID"):
    loan_process = LoanProcessing()
    df_loan, total_count = loan_process.loan_details(customer_id, start, end, sorting)
    print(f"DF_LOAN = {df_loan}")
    return {"LoanDetails" : df_loan, "TotalCount" : total_count}

@app.get('/custfindetails')
def custfindetails(customer_id : int):
    loan_process = LoanProcessing()
    df_loan = loan_process.cust_fin_details(customer_id)
    print(f"DF_LOAN = {df_loan}")
    return {"CustFinDetails" : df_loan}

@app.put('/loanappupdate')
def loanappupdate(loan_update : LoanUpdateModel):
    print(f"loan_id = {loan_update.loan_id}")
    loan_process = LoanProcessing()
    result = loan_process.update_loan_apps(loan_update.loan_id, loan_update.value)
    return {"Result" : result}