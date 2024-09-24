from pydantic import BaseModel
from typing import Any, List, Optional


class AuthPayload(BaseModel):
	email: str
	password: str
	otp: str = ""


class AuthSuccess(BaseModel):
	token: str
	refresh_token: str


class Amount(BaseModel):
	currency: str
	amount: int


class Pocket(BaseModel):
	id: str
	type: str
	owner_id: str
	provider_id: str
	owner_type: str
	has_movements: bool


class BalanceAfter(BaseModel):
	currency: str
	amount: int


class BalanceBefore(BaseModel):
	currency: str
	amount: int


class ListItem(BaseModel):
	id: str
	status: str
	type: str
	description: str
	category: Optional[str]
	amount: Amount
	is_debit: bool
	pocket_id: str
	executed_at: str
	pocket: Pocket
	subcategory: Any
	balance_after: BalanceAfter
	balance_before: BalanceBefore
	merchant_name: Optional[str]
	is_transfer_adjustment: bool


class Movements(BaseModel):
	list: List[ListItem]
	total_pages: int
	total_results: int
	current_page: int
	results_per_page: int


class MovementsModel(BaseModel):
	movements: Movements
