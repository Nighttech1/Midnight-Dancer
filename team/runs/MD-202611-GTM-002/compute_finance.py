"""Reproduce GTM-002 scenarios. Standard library only; values are assumptions."""
from decimal import Decimal, ROUND_HALF_UP
from math import ceil
import json
from pathlib import Path

D = Decimal
def money(x): return x.quantize(D('0.01'), rounding=ROUND_HALF_UP)
def num(x): return float(x) if isinstance(x, D) else x

assumptions = {
    'status': 'scenario_not_forecast_or_approved_spend',
    'period': 'illustrative_4_weeks',
    'currency': 'RUB',
    'price': 1490,
    'effective_acquiring_rate_assumed_not_contract': 0.055,
    'conditional_B2C_NPD_rate_no_initial_credit': 0.04,
    'risk_reserve_rate_not_actual_refund': 0.05,
    'variable_cash_cost_per_original_sale': 20,
    'cash_overhead_assumed': 1500,
    'founder_total_hours_including_code_sales_support_admin': 26,
    'founder_hour_value_assumed': 1000,
    'past_development_cost': None,
    'actual_sales': None,
    'actual_payment_provider_fee': None,
    'actual_owner_hour_value': None,
    'provider_approval': False,
}
price=D('1490'); fee_rate=D('.055'); tax_rate=D('.04'); risk=D('.05')
variable=D('20'); overhead=D('1500'); time=D('26000')
rows=[]
for n in [1,5,10,30,50]:
    gross=price*n
    fee=money(gross*fee_rate)
    tax=money(gross*tax_rate)
    reserve=money(gross*risk)
    cash=gross-fee-tax-variable*n-overhead
    rows.append(dict(sales=n,gross=gross,fee=fee,conditional_tax=tax,variable_cost=variable*n,
                     cash_result_after_tax_reserve_and_overhead=cash,
                     risk_reserve_not_cash_outflow=reserve,
                     prudent_result=cash-reserve,economic_result=cash-reserve-time))
unit=price*(1-fee_rate-tax_rate)-variable
prudent_unit=unit-price*risk
stress_n=10; refunds_n=1
gross=price*stress_n; refunds=price*refunds_n
stress_cash=gross-refunds-money(gross*fee_rate)-money((gross-refunds)*tax_rate)-variable*stress_n-overhead
result={
    'assumptions':assumptions,
    'formulas':{
        'cash_no_actual_refunds':'gross - effective_fee - conditional_tax_on_gross - variable_cost - cash_overhead',
        'prudent_result':'cash_no_actual_refunds - planning_risk_reserve',
        'economic_result':'prudent_result - all_founder_hours * assumed_hour_value',
        'refund_stress':'gross - actual_refund - fee_on_original_gross - tax_on_corrected_income - variable_cost_all_original_sales - overhead',
    },
    'unit_cash_before_fixed':unit,
    'unit_prudent_before_fixed':prudent_unit,
    'cash_break_even_with_risk_reserve_sales':ceil(overhead/prudent_unit),
    'economic_break_even_sales':ceil((overhead+time)/prudent_unit),
    'sales_for_10000_economic_result':ceil((overhead+time+D('10000'))/prudent_unit),
    'scenarios':rows,
    'refund_stress':{'original_sales':stress_n,'actual_refunds':refunds_n,'cash_after_tax_and_overhead':stress_cash,
                     'economic_after_owner_time':stress_cash-time,'additional_risk_reserve':False,
                     'note':'Assumes full refund correctly reflected for NPD; fee retained on original charge; contract may differ.'},
    'sensitivity':[
        {'effective_fee':float(f),'hour_value':h,'economic_break_even_sales':ceil((overhead+D(26*h))/(price*(1-f-tax_rate-risk)-variable))}
        for f in [D('.039'),D('.0427'),D('.055'),D('.08')] for h in [0,500,1000,1500]
    ],
    'daily_time_budget_minutes':[60,90],
    'fortnight_schedule_minutes':[60,60,60,60,60,60,30,60,60,60,60,60,60,30],
    'notes':[
        'Tax eligibility, contract fee, cash overhead and costs remain unverified for this seller.',
        'NPD commission is not deducted from tax income. The 5% risk reserve is not an actual refund or expense payment.',
        'Warm organic acquisition cash cost is not evidence of scalable CAC. Owner hours are valued separately.',
        'Contract fee is not asserted to equal the modeled 5.5%.',
        'Four-week schedule totals26h; no result assumes more owner time than the plan allows.',
    ],
}
assert unit==D('1328.45') and prudent_unit==D('1253.95')
assert sum(result['fortnight_schedule_minutes'])==780
assert result['economic_break_even_sales']==22 and result['sales_for_10000_economic_result']==30
encoded=json.dumps(result,ensure_ascii=False,indent=2,default=num)+'\n'
Path(__file__).with_name('finance-scenarios.json').write_text(encoded)
print(json.dumps({'rows':rows,'break_even':result['economic_break_even_sales'],'total_fortnight_hours':13},default=num,ensure_ascii=False))
