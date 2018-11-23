import csv
import sys
import datetime

#
# LOCAL FUNCTIONS
#
def unumlaut(str):
    v_str = str
    v_str = v_str.replace("ä", "ae")
    v_str = v_str.replace("ö", "oe")
    v_str = v_str.replace("ü", "ue")
    v_str = v_str.replace("Ä", "AE")
    v_str = v_str.replace("Ö", "OE")
    v_str = v_str.replace("Ü", "UE")
    return v_str

# Get input file name
v_input_file = sys.argv[1]
v_output_file = sys.argv[2]
print "Filename: ", v_input_file
print "Output: ", v_output_file


# Open output file for write
v_out = open(v_output_file, "w")

# Write file header
v_out.write("!Type:Bank" + "\n")

# Loop through rows
with open(v_input_file) as csvfile:
    file_reader = csv.reader(csvfile, delimiter=';')
    v_row_num = 0
    v_footer = 0
    v_header = 0
    v_new_trx = 0
    v_balance_line = 0
    v_balance_row_num = 0
    v_opening_balance = 0
    v_closing_balance = 0
    v_amount = 0
    v_balance = 0
    v_out_lines = 0
    v_previous_transaction_no = ""
    v_text = ""
    v_trx = ""
    v_currency = ""
    v_date = datetime.date

    # declare output variables
    o_date = o_amount = o_payee = o_memo = o_trx = ""
    o_address_1 = o_address_2 = o_address_3 = o_address_4 = o_address_5 = o_address_6 = ""

    for row in file_reader:
        v_row_num = v_row_num + 1
        r_valuation_date = row[0]
        r_banking_relationship = row[1]
        r_portfolio = row[2]
        r_product = row[3]
        r_iban = row[4]
        r_currency = row[5]
        r_date_from = row[6]
        r_date_to = row[7]
        r_account_description = row[8]
        r_trade_date = row[9]
        r_booking_date = row[10]
        r_value_date = row[11]
        r_description_1 = row[12]
        r_description_2 = row[13]
        r_description_3 = row[14]
        r_transaction_no = row[15]
        r_exchange_rate = row[16]
        r_individual_amount = row[17]
        r_debit = row[18]
        r_credit = row[19]
        r_balance = row[20]

        # is this the header
        if v_row_num == 1:
            v_header = 1
        else:
            v_header = 0

        # is this the footer
        if row[0] == "":
            v_footer = 1

        # is this the balance header (part of the footer)
        if v_footer == 1\
                and row[0] == "Closing balance":
            v_balance_row_num = v_row_num + 1

        # Get balance values from balance line
        if v_row_num == v_balance_row_num:
            v_balance_line = 1
            # 1st column is the closing balance
            v_str = row[0].replace("\'", "")
            v_closing_balance = float(v_str)

            # 2nd column is the opening balance
            v_str = row[1].replace("\'", "")
            v_opening_balance = float(v_str)

            # re initialize str
            v_str = ""

        # Skip header and footer
        if v_header != 1\
                and v_footer != 1:

            # is this a new transaction or only an addendum
            if r_transaction_no == v_previous_transaction_no:
                v_new_trx = 0
            else:
                v_new_trx = 1
                # init row variables
                v_amount = v_balance = 0.0
                v_trx = v_payee = v_text = ""
                v_currency = "CHF"

                # init output variables
                o_date = o_amount = o_payee = o_memo = o_trx = ""
                o_address_1 = o_address_2 = o_address_3 = o_address_4 = o_address_5 = o_address_6 = ""

            # build text
            # Take description 3,2,1 for new transactions and add 1 and amount for additional information
            if v_new_trx == 1:
                # Description 3
                if r_description_3 != "":
                    if v_text != "":
                        v_text = v_text + " // "
                    v_text = v_text + r_description_3

                # Description 2
                if r_description_2 != "":
                    if v_text != "":
                        v_text = v_text + " // "
                    v_text = v_text + r_description_2

                # Description 1
                if r_description_1 != "":
                    if v_text != "":
                        v_text = v_text + " // "
                    v_text = v_text + r_description_1

            # Add additional information for additional text
            if v_new_trx == 0:

                # Description 1
                if r_description_1 != "":
                    if v_text != "":
                        v_text = v_text + " // "
                    v_text = v_text + r_description_1

                # Amount and exchange rate
                if r_individual_amount != "":
                    v_text = v_text + " - Amount: " + r_individual_amount
                if r_exchange_rate != "":
                    v_text = v_text + " - Exchange Rate: " + r_exchange_rate

            # get transaction information, if it is a new transaction
            if v_new_trx == 1:
                v_trx = r_transaction_no
                if r_debit != "":
                    v_str = r_debit.replace("\'", "")
                    v_amount = v_amount - float(v_str)
                if r_credit != "":
                    v_str = r_credit.replace("\'", "")
                    v_amount = v_amount + float(v_str)
                if r_balance != "":
                    v_str = r_balance.replace("\'", "")
                    v_balance = v_balance + float(v_str)
                if r_value_date != "":
                    v_date = datetime.datetime.strptime(r_value_date, "%d.%m.%Y")
                if r_currency != "":
                    v_currency = r_currency.upper()
                # Payee is a bit complicated
                if r_description_1.upper().startswith("PAYNET ORDER"):
                    v_payee = r_description_3.upper()
                if r_description_1.upper().startswith("MAESTRO PA"):
                    v_payee = r_description_3.upper().split(", VOM")[0]
                if r_description_1.upper().startswith("ATM W"):
                    v_payee = "ATM " + r_description_3.upper().split(", VOM")[0]
                if r_description_3.upper().find("E-BANKING CHF DOMESTIC") > 0:
                    v_payee = r_description_3.upper().split(", E-BA")[0]
                if r_description_1.upper().startswith("SALARY P"):
                    v_payee = r_description_2.upper()
                if r_description_1.upper().startswith("E-BANKING ORDER"):
                    v_payee = r_description_2.upper()
                if r_description_1.upper().startswith("PAYMENT"):
                    v_payee = r_description_2.upper()
                if r_description_1.upper().startswith("STANDING ORDER"):
                    v_payee = r_description_3.upper()

            # set current trxNo as previous trxNo
            v_previous_transaction_no = r_transaction_no

            #
            # Prepare output
            #
            if v_new_trx == 1\
                    and v_header == 0\
                    and (v_footer == 0 or (v_footer == 1 and row[0] == "")):
                v_out_lines = v_out_lines + 1
                # Date. Format MM.DD.YYYY
                o_date = "D{}".format(v_date.strftime("%m.%d.%Y"))

                # Amount Format: [-]{CUR}9.99
                if v_amount < 0:
                    o_amount = "T-{}{:.2f}".format(v_currency, v_amount * -1)
                else:
                    o_amount = "T{}{:.2f}".format(v_currency, v_amount)

                # Payeer
                if v_payee != "":
                    o_payee = "P{}".format(v_payee)
                else:
                    o_payee = "P{}".format(v_text.upper())

                # Memo: No format
                o_memo = "M{} // Balance: {:.2f}".format(v_text, v_balance)

                # Booking Number
                o_trx = "N{}".format(v_trx)

                o_date = unumlaut(o_date).upper()
                o_amount = unumlaut(o_amount).upper()
                o_payee = unumlaut(o_payee).upper()
                o_memo = unumlaut(o_memo).upper()
                o_trx = unumlaut(o_trx).upper()

                # Print it out
                print v_out_lines, o_date, o_amount, o_payee, o_trx

                # Write to file
                v_out.write(o_date + "\n")
                v_out.write(o_amount + "\n")
                v_out.write(o_payee + "\n")
                v_out.write(o_memo + "\n")
                v_out.write(o_trx + "\n")
                v_out.write("^" + "\n")
v_out.close()
