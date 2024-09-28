from settings import Settings
from models import coverflex
import requests
import os
import json
from decimal import Decimal
from datetime import datetime
from actual import Actual
from actual.queries import create_transaction, create_account, get_account

settings = Settings()


def get_transactions(token):
	headers = {"Authorization": f"Bearer {token}"}
	current_year = datetime.today().strftime("%Y")
	response = requests.get(
		f"{settings.COVERFLEX_MOVEMENTS_URL}?filters[movement_from]={current_year}-01-01&filters[movement_to]={current_year}-12-31&pagination=no",
		headers=headers,
	)
	if response.status_code != 200:
		print(f"Error: {response.status_code} - {response.text}")
		print("Refreshing the token")
		token = auth(refresh=True)
		get_transactions(token)
	else:
		transactions = coverflex.MovementsModel.model_validate(response.json())
		return transactions


def auth(refresh: bool = False):
	auth_file = "auth.json"
	if refresh:
		os.remove(auth_file)
	if os.path.exists(auth_file):
		print("Retrieving existing auth token")
		with open(auth_file) as file:
			data = json.load(file)
		return data["token"]
	else:
		print("Auth token is missing. Performing authentication")
		payload = coverflex.AuthPayload(email=settings.COVERFLEX_EMAIL, password=settings.COVERFLEX_PASSWORD)
		response = requests.post(settings.COVERFLEX_AUTH_URL, json=payload.model_dump(exclude_unset=True))
		if response.status_code == 202:
			print("Waiting for OTP authentication...")
			otp = input("Enter OTP: ")
			payload.otp = otp
			response = requests.post(settings.COVERFLEX_AUTH_URL, json=payload.model_dump())

		if response.status_code == 201:
			print("Authentication successful!")
			try:
				auth = coverflex.AuthSuccess.model_validate(response.json())
				with open("auth.json", "w") as outfile:
					json.dump(auth.model_dump(), outfile, ensure_ascii=False, indent=4)
				return auth.token
			except Exception as e:
				print(e)
		else:
			print(f"Error: {response.status_code} - {response.text}")
			print("Authentication failed")


def convert_amount_to_decimal(amount, is_debit: bool = True):
	if is_debit:
		return Decimal(f"-{abs(amount) // 100}.{abs(amount) % 100:02d}")
	else:
		return Decimal(f"{abs(amount) // 100}.{abs(amount) % 100:02d}")


def main():
	token = auth()

	transactions = get_transactions(token)
	with Actual(
		base_url=settings.ACTUAL_URL, password=settings.ACTUAL_PASSWORD, file=settings.ACTUAL_FILE, cert=True
	) as actual:
		coverflex_account = get_account(actual.session, name=settings.COVERFLEX_ACTUAL_ACCOUNT)
		if coverflex_account is None:
			print(f"Creating a coverflex account in ActualBudget")
			coverflex_account = create_account(actual.session, settings.COVERFLEX_ACTUAL_ACCOUNT)
		else:
			print(f"Retrieved your coverflex account {coverflex_account}")
		for transaction in transactions.movements.list:
			print(transaction)
			amount = convert_amount_to_decimal(transaction.amount.amount, transaction.is_debit)
			t = create_transaction(
				s=actual.session,
				date=datetime.strptime(transaction.executed_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
				account=coverflex_account,
				imported_payee=transaction.merchant_name,
				notes=transaction.description,
				amount=amount,
				cleared=True,
			)
		actual.commit()
	# for transaction in transactions.movements.list:
	# 	print(transaction)


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("KeyboardInterrupt")
