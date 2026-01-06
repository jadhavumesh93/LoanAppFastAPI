from typing import Optional
from pydantic import BaseModel

class UserProfile(BaseModel):
    update_type: Optional[str] = None
    is_update : bool = False
    cust_id : int
    email: Optional[str] = ""
    password: Optional[str] = ""
    first_name: Optional[str] = ""
    middle_name: Optional[str] = ""
    last_name: Optional[str] = ""
    date_of_birth: Optional[str] = ""
    pan: Optional[str] = ""
    pan_path: Optional[str] = ""
    phone: Optional[str] = ""
    flat_no: Optional[str] = ""
    society: Optional[str] = ""
    locality: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    pincode: Optional[str] = ""
    profile_picture_path: Optional[str] = ""
    annual_income: Optional[int] = 0
    selected_emp_length: Optional[int] = 0