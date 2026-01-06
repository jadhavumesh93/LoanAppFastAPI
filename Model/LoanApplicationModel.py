from pydantic import BaseModel

'''
class LoanApplicationModel(BaseModel):
    #CustomerType : int
    Username : str | None = None
    LoanAmount : int
    Term : str
    EmpLength : int
    AnnualIncome : float
    ApplicationType : str
    #HasSecondaryApplicant : str
    SecAppFicoRangeLow : int | None=None
    SecAppRevolUtil : int | None=None
    SecAppPAN : str | None=None
    HomeOwnership : str
    LoanPurpose : str
    VerificationStatus : str
'''
 
class LoanApplicationModel(BaseModel):
    #CustomerType : int
    CustomerID : str
    LoanAmount : int
    Term : str
    ApplicationType : str
    SecAppAvailable : bool
    SecAppAnnualInc : float | None=None
    SecAppFICO : int | None=None
    SecAppDTI : float | None=None
    SecAppPAN : str | None=None
    HomeOwnership : str
    LoanPurpose : str
    VerificationStatus : str
    
class LoanUpdateModel(BaseModel):
    loan_id : int
    value : str