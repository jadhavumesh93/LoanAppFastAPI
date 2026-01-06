from pydantic import BaseModel

class UserProfile(BaseModel):
    #CustomerType : int
    Username : str | None = None
    Password : str | None = None
    FirstName : str | None = None
    MiddleName : str | None = None
    LastName : str | None = None
    Phone : str | None = None
    Email : str | None = None
    DOB : str | None = None
    PAN : str | None = None
    AnnualIncome : float | None = None
    EmpLength : int | None = None