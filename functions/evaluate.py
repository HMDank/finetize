from vnstock import financial_report
import pandas as pd


def symbol_eval(symbol, frequency):
    income_statement = financial_report(symbol, report_type='IncomeStatement', frequency=frequency.capitalize())
    income_statement = income_statement.set_index(income_statement.columns[0])
    balance_sheet = financial_report(symbol, report_type='BalanceSheet', frequency=frequency.capitalize())
    balance_sheet = balance_sheet.set_index(balance_sheet.columns[0])
    cash_flow = financial_report(symbol, report_type='CashFlow', frequency=frequency.capitalize())
    cash_flow = cash_flow.set_index(cash_flow.columns[0])

    financial = {
        'Sales': income_statement.loc['Doanh số thuần'],
        'Gross Profit': income_statement.loc['Lãi gộp'],
        'Selling Expenses': income_statement.loc['Chi phí bán hàng'],
        'G&A Expenses': income_statement.loc['Chi phí quản lý doanh  nghiệp'],
        'Operating Income': income_statement.loc['Lãi/(lỗ) từ hoạt động kinh doanh'],
        'Interest Income': income_statement.loc['Thu nhập tài chính'],
        'Associates Income': income_statement.loc['Lãi/(lỗ) từ công ty liên doanh'],
        'EBIT': income_statement.loc['EBIT'] + income_statement.loc['Lãi/(lỗ) từ công ty liên doanh'],
        'Deprication': cash_flow.loc['Khấu hao TSCĐ'],
        'Affiliates Dividends': cash_flow.loc['Cổ tức và tiền lãi nhận được'],
        'EBITDA': cash_flow.loc['Cổ tức và tiền lãi nhận được'] + income_statement.loc['EBITDA'],
        '(ADJ) Interest Expenses': income_statement.loc['Trong đó: Chi phí lãi vay'],
        'Tax Expenses': income_statement.loc['Chi phí thuế thu nhập doanh nghiệp'],
        'FFO': cash_flow.loc['Cổ tức và tiền lãi nhận được'] + income_statement.loc['EBITDA'] + income_statement.loc['Chi phí thuế thu nhập doanh nghiệp'] + income_statement.loc['Thu nhập tài chính'] - income_statement.loc['Trong đó: Chi phí lãi vay'],
        'Free Operation Cash Flow': cash_flow.loc['Lưu chuyển tiền thuần từ các hoạt động sản xuất kinh doanh'],
        'PBT': income_statement.loc['Lãi/(lỗ) ròng trước thuế'],
        'PAT': income_statement.loc['Lãi/(lỗ) thuần sau thuế'],
    }

    balance = {
        'Total Current Asset': balance_sheet.loc['TÀI SẢN NGẮN HẠN'],
        'Cash & Cash Equivalent': balance_sheet.loc['Tiền và tương đương tiền'],
        'Short-Term Investments': balance_sheet.loc['Đầu tư ngắn hạn'],
        'Inventory': balance_sheet.loc['Hàng tồn kho, ròng'],
        'Total Asset': balance_sheet.loc['TỔNG TÀI SẢN'],
        'Total Current Liabilities': balance_sheet.loc['Nợ ngắn hạn'],
        '(Total) Short-Term Debt': balance_sheet.loc['Vay ngắn hạn'],
        '(Total) Long-Term Debt': balance_sheet.loc['Vay dài hạn'],
        'Total Debt': balance_sheet.loc['Vay dài hạn'] + balance_sheet.loc['Vay ngắn hạn'],
        'Long-Term Liabilities': balance_sheet.loc['Nợ dài hạn'],
        'Total Liabilities': balance_sheet.loc['NỢ PHẢI TRẢ'],
        'Equity': balance_sheet.loc['VỐN CHỦ SỞ HỮU'],
        'Total Capital': balance_sheet.loc['Vay dài hạn'] + balance_sheet.loc['Vay ngắn hạn'] + balance_sheet.loc['VỐN CHỦ SỞ HỮU'],
    }
    total_capital = balance['Total Capital']
    if frequency.capitalize() == 'Yearly':
        avg = [None]
        for i in range(len(total_capital) - 1):
            average = (total_capital.iloc[i] + total_capital.iloc[i + 1]) / 2
            avg.append(average)
    else:
        avg = [None, None, None]
        for i in range(len(total_capital) - 4):
            average = (total_capital.iloc[i] + total_capital.iloc[i + 1] + total_capital.iloc[i + 3] + total_capital.iloc[i + 4]) / 4
            avg.append(average)

    balance['Average Total Capital (2_yrs)'] = avg

# Create the DataFrame
    financial_df = pd.DataFrame(financial).T
    balance_df = pd.DataFrame(balance).T

    return financial_df, balance_df
