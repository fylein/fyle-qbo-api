data = {
    "bill_payload": {
        "VendorRef": {"value": "43"},
        "APAccountRef": {"value": "33"},
        "DepartmentRef": {"value": "None"},
        "TxnDate": "2022-01-21",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Reimbursable expense by ashwin.t@fyle.in on 2022-01-21 ",
        "Line": [
            {
                "Description": "ashwin.t@fyle.in - Travel - 2022-01-21 - C/2022/01/R/8 -  - https://staging.fyle.tech/app/admin/#/company_expenses?txnId=txlPjmNxssq1&org_id=orGcBCVPijjO",
                "DetailType": "AccountBasedExpenseLineDetail",
                "Amount": 60.0,
                "AccountBasedExpenseLineDetail": {"AccountRef": {"value": "57"},"CustomerRef": {"value": "None"},"ClassRef": {"value": "None"},"TaxCodeRef": {"value": "None"},"TaxAmount": 0.0,"BillableStatus": "NotBillable"},
            }
        ],
        "DocNumber": "C/2022/01/R/8",
        'GlobalTaxCalculation': 'TaxInclusive'
    },
    "bill_payload_with_tax_override": {
        "DocNumber": "C/2022/01/R/8",
        'VendorRef': {'value': '84'},
        'APAccountRef': {'value': '33'},
        'DepartmentRef': {'value': None},
        'TxnDate': '2024-06-24',
        'CurrencyRef': {'value': 'USD'},
        'PrivateNote': 'Credit card expense by sravan.kumar@fyle.in on 2022-05-23 ',
        'Line': [
            {
                'Description': 'sravan.kumar@fyle.in - WIP - 2022-05-23 - C/2022/05/R/8 -  - None/app/admin/#/company_expenses?txnId=tx3i1mrGprDs&org_id=orPJvXuoLqvJ',
                'DetailType': 'AccountBasedExpenseLineDetail',
                'Amount': 0.89,
                'AccountBasedExpenseLineDetail': {
                    'CustomerRef': {'value': None},
                    'ClassRef': {'value': '5000000000000142238'},
                    'TaxCodeRef': {'value': '17'},
                    'BillableStatus': 'NotBillable',
                    'AccountRef': {'value': '69'},
                    'TaxAmount': 0.11
                }
            }
        ],
        'ExchangeRate': 1.2309,
        'GlobalTaxCalculation': 'TaxExcluded',
        'TxnTaxDetail': {
            'TaxLine': [
                {
                    'Amount': 0.06,
                    'DetailType': 'TaxLineDetail',
                    'TaxLineDetail': {'TaxRateRef': {'value': '28'},'PercentBased': False,'NetAmountTaxable': 0.89}
                },
                {
                    'Amount': 0.05,
                    'DetailType': 'TaxLineDetail',
                    'TaxLineDetail': {'TaxRateRef': {'value': '37'},'PercentBased': False,'NetAmountTaxable': 0.89}
                }
            ]
        }
    },
    "bill_payload_item_based_payload": {
        "DocNumber": "C/2022/01/R/8",
        "VendorRef": {"value": "43"},
        "APAccountRef": {"value": "33"},
        "DepartmentRef": {"value": "None"},
        "TxnDate": "2022-01-21",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Reimbursable expense by ashwin.t@fyle.in on 2022-01-21 ",
        'GlobalTaxCalculation': 'TaxInclusive',
        "Line": [
            {
                "Description": "ashwin.t@fyle.in - Travel - 2022-01-21 - C/2022/01/R/8 -  - https://staging.fyle.tech/app/admin/#/company_expenses?txnId=txlPjmNxssq1&org_id=orGcBCVPijjO",
                "DetailType": "ItemBasedExpenseLineDetail",
                "Amount": 60.0,
                "ItemBasedExpenseLineDetail": {"ItemRef": {"value": "125"},"Qty": 1,"CustomerRef": {"value": "None"},"ClassRef": {"value": "None"},"TaxCodeRef": {"value": "None"},"BillableStatus": "NotBillable"},
            }
        ]
    },
    "bill_payload_item_based_payload_with_tax_override": {
        "DocNumber": "C/2022/01/R/8",
        "VendorRef": {"value": "84"},
        "APAccountRef": {"value": "33"},
        "DepartmentRef": {"value": None},
        "TxnDate": "2024-06-24",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Credit card expense by sravan.kumar@fyle.in on 2024-06-24 ",
        "Line": [
            {
                "Description": "sravan.kumar@fyle.in - Concrete - 2024-06-24 - C/2023/04/R/1 -  - None/app/admin/#/company_expenses?txnId=txT4kpMbHdKn&org_id=orPJvXuoLqvJ",
                "DetailType": "ItemBasedExpenseLineDetail",
                "Amount": 0.89,
                "ItemBasedExpenseLineDetail": {
                    "CustomerRef": {"value": None},
                    "ClassRef": {"value": "5000000000000142238"},
                    "TaxCodeRef": {"value": "17"},
                    "BillableStatus": "NotBillable",
                    "ItemRef": {"value": "3"},
                    "Qty": 1,
                },
            }
        ],
        "GlobalTaxCalculation": "TaxExcluded",
        "TxnTaxDetail": {
            "TaxLine": [
                {
                    "Amount": 0.06,
                    "DetailType": "TaxLineDetail",
                    "TaxLineDetail": {
                        "TaxRateRef": {"value": "28"},
                        "PercentBased": False,
                        "NetAmountTaxable": 0.89,
                    },
                },
                {
                    "Amount": 0.05,
                    "DetailType": "TaxLineDetail",
                    "TaxLineDetail": {
                        "TaxRateRef": {"value": "37"},
                        "PercentBased": False,
                        "NetAmountTaxable": 0.89,
                    },
                },
            ]
        }
    },
    "bill_payload_item_and_account_based_payload": {
        "DocNumber": "C/2022/01/R/8",
        'VendorRef': {'value': '84'},
        'APAccountRef': {'value': '33'},
        'DepartmentRef': {'value': None},
        'TxnDate': '2023-07-06',
        'CurrencyRef': {'value': 'USD'},
        'PrivateNote': 'Credit card expense by sravan.kumar@fyle.in',
        'GlobalTaxCalculation': 'TaxInclusive',
        'Line': [
            {
                'Description': 'sravan.kumar@fyle.in - Concrete - 2023-07-06 - C/2023/04/R/2 -  - None/app/admin/#/company_expenses?txnId=txybL0Dw709h&org_id=orPJvXuoLqvJ',
                'DetailType': 'ItemBasedExpenseLineDetail',
                'Amount': 1.0,
                'ItemBasedExpenseLineDetail': {'CustomerRef': {'value': None},'ClassRef': {'value': '5000000000000142238'},'TaxCodeRef': {'value': None},'BillableStatus': 'NotBillable','ItemRef': {'value': '3'},'Qty': 1},
            },
            {
                'Description': 'sravan.kumar@fyle.in - WIP - 2023-07-06 - C/2023/04/R/2 -  - None/app/admin/#/company_expenses?txnId=txoF0nqv6cG3&org_id=orPJvXuoLqvJ',
                'DetailType': 'AccountBasedExpenseLineDetail',
                'Amount': 10.0,
                'AccountBasedExpenseLineDetail': {'CustomerRef': {'value': None},'ClassRef': {'value': '5000000000000142238'},'TaxCodeRef': {'value': None},'BillableStatus': 'NotBillable','AccountRef': {'value': '69'},'TaxAmount': 0.0},
            },
        ],
    },
    "bill_payload_item_and_account_based_payload_with_tax_override": {
        "DocNumber": "C/2022/01/R/8",
        "VendorRef": {"value": "84"},
        "APAccountRef": {"value": "33"},
        "DepartmentRef": {"value": None},
        "TxnDate": "2024-06-24",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Credit card expense by sravan.kumar@fyle.in",
        "Line": [
            {
                "Description": "sravan.kumar@fyle.in - Concrete - 2024-06-24 - C/2023/04/R/2 -  - None/app/admin/#/company_expenses?txnId=txybL0Dw709h&org_id=orPJvXuoLqvJ",
                "DetailType": "ItemBasedExpenseLineDetail",
                "Amount": 0.89,
                "ItemBasedExpenseLineDetail": {
                    "CustomerRef": {"value": None},
                    "ClassRef": {"value": "5000000000000142238"},
                    "TaxCodeRef": {"value": "17"},
                    "BillableStatus": "NotBillable",
                    "ItemRef": {"value": "3"},
                    "Qty": 1,
                },
            },
            {
                "Description": "sravan.kumar@fyle.in - WIP - 2024-06-24 - C/2023/04/R/2 -  - None/app/admin/#/company_expenses?txnId=txoF0nqv6cG3&org_id=orPJvXuoLqvJ",
                "DetailType": "AccountBasedExpenseLineDetail",
                "Amount": 8.93,
                "AccountBasedExpenseLineDetail": {
                    "CustomerRef": {"value": None},
                    "ClassRef": {"value": "5000000000000142238"},
                    "TaxCodeRef": {"value": "17"},
                    "BillableStatus": "NotBillable",
                    "AccountRef": {"value": "69"},
                    "TaxAmount": 1.07,
                },
            },
        ],
        "GlobalTaxCalculation": "TaxExcluded",
        "TxnTaxDetail": {
            "TaxLine": [
                {
                    "Amount": 0.68,
                    "DetailType": "TaxLineDetail",
                    "TaxLineDetail": {
                        "TaxRateRef": {"value": "28"},
                        "PercentBased": False,
                        "NetAmountTaxable": 9.82,
                    },
                },
                {
                    "Amount": 0.5,
                    "DetailType": "TaxLineDetail",
                    "TaxLineDetail": {
                        "TaxRateRef": {"value": "37"},
                        "PercentBased": False,
                        "NetAmountTaxable": 9.82,
                    },
                },
            ]
        },
    },
    "credit_card_purchase_payload": {
        "DocNumber": "E/2022/01/T/9",
        "PaymentType": "CreditCard",
        "AccountRef": {"value": "42"},
        "EntityRef": {"value": "58"},
        "DepartmentRef": {"value": "None"},
        "TxnDate": "2022-01-21",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Credit card expense by ashwin.t@fyle.in on 2022-01-21 ",
        "Credit": False,
        "Line": [
            {
                "Description": "ashwin.t@fyle.in - Travel - 2022-01-21 - C/2022/01/R/8 -  - https://staging.fyle.tech/app/admin/#/company_expenses?txnId=txvh8qm7RTRI&org_id=orGcBCVPijjO",
                "DetailType": "AccountBasedExpenseLineDetail",
                "Amount": 30.0,
                "AccountBasedExpenseLineDetail": {"AccountRef": {"value": "57"},"CustomerRef": {"value": "None"},"ClassRef": {"value": "None"},"TaxCodeRef": {"value": "None"},"TaxAmount": 0.0,"BillableStatus": "NotBillable"},
            }
        ],
        'GlobalTaxCalculation': 'TaxInclusive'
    },
    "credit_card_purchase_payload_with_tax_override": {
        'DocNumber': 'E/2022/05/T/17',
        'PaymentType': 'CreditCard',
        'AccountRef': {'value': '41'},
        'EntityRef': {'value': '58'},
        'DepartmentRef': {'value': None},
        'TxnDate': '2022-05-17',
        'CurrencyRef': {'value': 'USD'},
        'PrivateNote': 'Credit card expense by ashwin.t@fyle.in spent on merchant Ashwin on 2022-05-17 ',
        'Credit': False,
        'Line': [
            {
                'Description': 'ashwin.t@fyle.in - Food - 2022-05-17 - C/2022/05/R/5 -  - None/app/admin/#/company_expenses?txnId=txj8kWkDTyog&org_id=or79Cob97KSh',
                'DetailType': 'AccountBasedExpenseLineDetail',
                'Amount': 0.89,
                'AccountBasedExpenseLineDetail': {'CustomerRef': {'value': None},'ClassRef': {'value': None},'TaxCodeRef': {'value': '17'},'BillableStatus': 'NotBillable','AccountRef': {'value': '13'},'TaxAmount': 0.11}
            }
        ],
        'GlobalTaxCalculation': 'TaxExcluded',
        'TxnTaxDetail': {
            'TaxLine': [
                {
                    'Amount': 0.06,
                    'DetailType': 'TaxLineDetail',
                    'TaxLineDetail': {'TaxRateRef': {'value': '28'},'PercentBased': False,'NetAmountTaxable': 0.89}
                },
                {
                    'Amount': 0.05,
                    'DetailType': 'TaxLineDetail',
                    'TaxLineDetail': {'TaxRateRef': {'value': '37'},'PercentBased': False,'NetAmountTaxable': 0.89}
                }
            ]
        }
    },
    "credit_card_purchase_item_based_payload": {
        "DocNumber": "E/2023/04/T/4",
        "PaymentType": "CreditCard",
        "AccountRef": {"value": "41"},
        "EntityRef": {"value": "58"},
        "DepartmentRef": {"value": "None"},
        "TxnDate": "2023-04-19",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Credit card expense by sravan.kumar@fyle.in on 2023-04-19 ",
        "Credit": False,
        "Line": [
            {
                "Description": "sravan.kumar@fyle.in - Concrete - 2023-04-19 - C/2023/04/R/3 -  - None/app/admin/#/company_expenses?txnId=txT4kpMbHdLm&org_id=or79Cob97KSh",
                "DetailType": "ItemBasedExpenseLineDetail",
                "Amount": 1.0,
                "ItemBasedExpenseLineDetail": {"ItemRef": {"value": "3"},"Qty": 1,"CustomerRef": {"value": "None"},"ClassRef": {"value": "None"},"TaxCodeRef": {"value": "None"},"BillableStatus": "NotBillable"},
            }
        ],
        'GlobalTaxCalculation': 'TaxInclusive'
    },
    "credit_card_purchase_item_based_payload_with_tax_override": {
        "DocNumber": "E/2023/04/T/4",
        "PaymentType": "CreditCard",
        "AccountRef": {"value": "41"},
        "EntityRef": {"value": "58"},
        "DepartmentRef": {"value": "None"},
        "TxnDate": "2023-04-19",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Credit card expense by sravan.kumar@fyle.in on 2023-04-19 ",
        "Credit": False,
        "Line": [
            {
                "Description": "sravan.kumar@fyle.in - Concrete - 2023-04-19 - C/2023/04/R/3 -  - None/app/admin/#/company_expenses?txnId=txT4kpMbHdLm&org_id=or79Cob97KSh",
                "DetailType": "ItemBasedExpenseLineDetail",
                "Amount": 1.0,
                "ItemBasedExpenseLineDetail": {"ItemRef": {"value": "3"},"Qty": 1,"CustomerRef": {"value": "None"},"ClassRef": {"value": "None"},'TaxCodeRef': {'value': '17'},"BillableStatus": "NotBillable"},
            }
        ],
        'GlobalTaxCalculation': 'TaxExcluded',
        'TxnTaxDetail': {
            'TaxLine': [
                {
                    'Amount': 0.06,
                    'DetailType': 'TaxLineDetail',
                    'TaxLineDetail': {'TaxRateRef': {'value': '28'},'PercentBased': False,'NetAmountTaxable': 0.89}
                },
                {
                    'Amount': 0.05,
                    'DetailType': 'TaxLineDetail',
                    'TaxLineDetail': {'TaxRateRef': {'value': '37'},'PercentBased': False,'NetAmountTaxable': 0.89}
                }
            ]
        }
    },
    "credit_card_purchase_item_and_account_based_payload": {
        'DocNumber': 'E/2023/04/T/6',
        'PaymentType': 'CreditCard',
        'AccountRef': {'value': '41'},
        'EntityRef': {'value': '58'},
        'DepartmentRef': {'value': None},
        'TxnDate': '2023-07-06',
        'CurrencyRef': {'value': 'USD'},
        'PrivateNote': 'Credit card expense by sravan.kumar@fyle.in',
        'Credit': False,
        'Line': [
            {
                'Description': 'sravan.kumar@fyle.in - Concrete - 2023-07-06 - C/2023/04/R/3 -  - None/app/admin/#/company_expenses?txnId=txT4kpMbHdLg8&org_id=or79Cob97KSh',
                'DetailType': 'ItemBasedExpenseLineDetail',
                'Amount': 1.0,
                'ItemBasedExpenseLineDetail': {'CustomerRef': {'value': None},'ClassRef': {'value': None},'TaxCodeRef': {'value': None},'BillableStatus': 'NotBillable','ItemRef': {'value': '3'},'Qty': 1},
            },
            {
                'Description': 'sravan.kumar@fyle.in - Food - 2023-07-06 - C/2023/04/R/2 -  - None/app/admin/#/company_expenses?txnId=txoF0nqv6cG89&org_id=or79Cob97KSh',
                'DetailType': 'AccountBasedExpenseLineDetail',
                'Amount': 10.0,
                'AccountBasedExpenseLineDetail': {'CustomerRef': {'value': None},'ClassRef': {'value': None},'TaxCodeRef': {'value': None},'BillableStatus': 'NotBillable','AccountRef': {'value': '13'},'TaxAmount': 0.0},
            },
        ],
        'GlobalTaxCalculation': 'TaxInclusive'
    },
    "credit_card_purchase_item_and_account_based_payload_with_tax_override": {
        "DocNumber": "E/2023/04/T/6",
        "PaymentType": "CreditCard",
        "AccountRef": {"value": "41"},
        "EntityRef": {"value": "58"},
        "DepartmentRef": {"value": None},
        "TxnDate": "2024-06-24",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Credit card expense by sravan.kumar@fyle.in",
        "Credit": False,
        "Line": [
            {
                "Description": "sravan.kumar@fyle.in - Concrete - 2024-06-24 - C/2023/04/R/3 -  - None/app/admin/#/company_expenses?txnId=txT4kpMbHdLg8&org_id=or79Cob97KSh",
                "DetailType": "ItemBasedExpenseLineDetail",
                "Amount": 0.89,
                "ItemBasedExpenseLineDetail": {
                    "CustomerRef": {"value": None},
                    "ClassRef": {"value": None},
                    "TaxCodeRef": {"value": "17"},
                    "BillableStatus": "NotBillable",
                    "ItemRef": {"value": "3"},
                    "Qty": 1,
                },
            },
            {
                "Description": "sravan.kumar@fyle.in - Food - 2024-06-24 - C/2023/04/R/2 -  - None/app/admin/#/company_expenses?txnId=txoF0nqv6cG89&org_id=or79Cob97KSh",
                "DetailType": "AccountBasedExpenseLineDetail",
                "Amount": 8.93,
                "AccountBasedExpenseLineDetail": {
                    "CustomerRef": {"value": None},
                    "ClassRef": {"value": None},
                    "TaxCodeRef": {"value": "17"},
                    "BillableStatus": "NotBillable",
                    "AccountRef": {"value": "13"},
                    "TaxAmount": 1.07,
                },
            },
        ],
        "GlobalTaxCalculation": "TaxExcluded",
        "TxnTaxDetail": {
            "TaxLine": [
                {
                    "Amount": 0.68,
                    "DetailType": "TaxLineDetail",
                    "TaxLineDetail": {
                        "TaxRateRef": {"value": "28"},
                        "PercentBased": False,
                        "NetAmountTaxable": 9.82,
                    },
                },
                {
                    "Amount": 0.5,
                    "DetailType": "TaxLineDetail",
                    "TaxLineDetail": {
                        "TaxRateRef": {"value": "37"},
                        "PercentBased": False,
                        "NetAmountTaxable": 9.82,
                    },
                },
            ]
        },
    },
    "qbo_expense_item_based_payload": {
        'DocNumber': None,
        'PaymentType': 'Cash',
        'AccountRef': {'value': '94'},
        'EntityRef': {'value': '60'},
        'DepartmentRef': {'value': None},
        'TxnDate': '2023-04-19',
        'CurrencyRef': {'value': 'USD'},
        'PrivateNote': 'Credit card expense by sravan.kumar@fyle.in on 2023-04-19 ',
        'Credit': None,
        'Line': [
            {
                'Description': 'sravan.kumar@fyle.in - Concrete - 2023-04-19 - C/2023/04/R/6 -  - None/app/admin/#/company_expenses?txnId=txT4kpMbHdIp&org_id=or79Cob97KSh',
                'DetailType': 'ItemBasedExpenseLineDetail',
                'Amount': 1.0,
                'ItemBasedExpenseLineDetail': {'ItemRef': {'value': '3'},'Qty': 1,'CustomerRef': {'value': None},'ClassRef': {'value': None},'TaxCodeRef': {'value': None},'BillableStatus': 'NotBillable'},
            }
        ],
        'GlobalTaxCalculation': 'TaxInclusive'
    },
    "qbo_expense_item_based_payload_with_tax_override": {
        "DocNumber": None,
        "PaymentType": "Cash",
        "AccountRef": {"value": "94"},
        "EntityRef": {"value": "60"},
        "DepartmentRef": {"value": None},
        "TxnDate": "2024-06-24",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Credit card expense by sravan.kumar@fyle.in on 2024-06-24 ",
        "Credit": None,
        "Line": [
            {
                "Description": "sravan.kumar@fyle.in - Concrete - 2024-06-24 - C/2023/04/R/6 -  - None/app/admin/#/company_expenses?txnId=txT4kpMbHdIp&org_id=or79Cob97KSh",
                "DetailType": "ItemBasedExpenseLineDetail",
                "Amount": 0.89,
                "ItemBasedExpenseLineDetail": {
                    "CustomerRef": {"value": None},
                    "ClassRef": {"value": None},
                    "TaxCodeRef": {"value": "17"},
                    "BillableStatus": "NotBillable",
                    "ItemRef": {"value": "3"},
                    "Qty": 1,
                },
            }
        ],
        "GlobalTaxCalculation": "TaxExcluded",
        "TxnTaxDetail": {
            "TaxLine": [
                {
                    "Amount": 0.06,
                    "DetailType": "TaxLineDetail",
                    "TaxLineDetail": {
                        "TaxRateRef": {"value": "28"},
                        "PercentBased": False,
                        "NetAmountTaxable": 0.89,
                    },
                },
                {
                    "Amount": 0.05,
                    "DetailType": "TaxLineDetail",
                    "TaxLineDetail": {
                        "TaxRateRef": {"value": "37"},
                        "PercentBased": False,
                        "NetAmountTaxable": 0.89,
                    },
                },
            ]
        },
    },
    "qbo_expense_item_and_account_based_payload": {
        'DocNumber': None,
        'PaymentType': 'Cash',
        'AccountRef': {'value': '94'},
        'EntityRef': {'value': '60'},
        'DepartmentRef': {'value': None},
        'TxnDate': '2023-07-06',
        'CurrencyRef': {'value': 'USD'},
        'PrivateNote': 'Credit card expense by sravan.kumar@fyle.in',
        'Credit': None,
        'Line': [
            {
                'Description': 'sravan.kumar@fyle.in - Food - 2023-07-06 - C/2023/04/R/6 -  - None/app/admin/#/company_expenses?txnId=txoF0nqv6cG78&org_id=or79Cob97KSh',
                'DetailType': 'AccountBasedExpenseLineDetail',
                'Amount': 10.0,
                'AccountBasedExpenseLineDetail': {'CustomerRef': {'value': None},'ClassRef': {'value': None},'TaxCodeRef': {'value': None},'BillableStatus': 'NotBillable','AccountRef': {'value': '13'},'TaxAmount': 0.0},
            },
            {
                'Description': 'sravan.kumar@fyle.in - Concrete - 2023-07-06 - C/2023/04/R/6 -  - None/app/admin/#/company_expenses?txnId=txT4kpMbHdLg87L&org_id=or79Cob97KSh',
                'DetailType': 'ItemBasedExpenseLineDetail',
                'Amount': 1.0,
                'ItemBasedExpenseLineDetail': {'CustomerRef': {'value': None},'ClassRef': {'value': None},'TaxCodeRef': {'value': None},'BillableStatus': 'NotBillable','ItemRef': {'value': '3'},'Qty': 1},
            },
        ],
        'GlobalTaxCalculation': 'TaxInclusive'
    },
    "qbo_expense_item_and_account_based_payload_with_tax_override": {
        "DocNumber": None,
        "PaymentType": "Cash",
        "AccountRef": {"value": "94"},
        "EntityRef": {"value": "60"},
        "DepartmentRef": {"value": None},
        "TxnDate": "2024-06-24",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Credit card expense by sravan.kumar@fyle.in",
        "Credit": None,
        "Line": [
            {
                "Description": "sravan.kumar@fyle.in - Concrete - 2024-06-24 - C/2023/04/R/6 -  - None/app/admin/#/company_expenses?txnId=txT4kpMbHdLg87L&org_id=or79Cob97KSh",
                "DetailType": "ItemBasedExpenseLineDetail",
                "Amount": 0.89,
                "ItemBasedExpenseLineDetail": {
                    "CustomerRef": {"value": None},
                    "ClassRef": {"value": None},
                    "TaxCodeRef": {"value": "17"},
                    "BillableStatus": "NotBillable",
                    "ItemRef": {"value": "3"},
                    "Qty": 1,
                },
            },
            {
                "Description": "sravan.kumar@fyle.in - Food - 2024-06-24 - C/2023/04/R/6 -  - None/app/admin/#/company_expenses?txnId=txoF0nqv6cG78&org_id=or79Cob97KSh",
                "DetailType": "AccountBasedExpenseLineDetail",
                "Amount": 8.93,
                "AccountBasedExpenseLineDetail": {
                    "CustomerRef": {"value": None},
                    "ClassRef": {"value": None},
                    "TaxCodeRef": {"value": "17"},
                    "BillableStatus": "NotBillable",
                    "AccountRef": {"value": "13"},
                    "TaxAmount": 1.07,
                },
            },
        ],
        "GlobalTaxCalculation": "TaxExcluded",
        "TxnTaxDetail": {
            "TaxLine": [
                {
                    "Amount": 0.68,
                    "DetailType": "TaxLineDetail",
                    "TaxLineDetail": {
                        "TaxRateRef": {"value": "28"},
                        "PercentBased": False,
                        "NetAmountTaxable": 9.82,
                    },
                },
                {
                    "Amount": 0.5,
                    "DetailType": "TaxLineDetail",
                    "TaxLineDetail": {
                        "TaxRateRef": {"value": "37"},
                        "PercentBased": False,
                        "NetAmountTaxable": 9.82,
                    },
                },
            ]
        },
    },
    "qbo_expense_payload": {
        "DocNumber": "None",
        "PaymentType": "Cash",
        "AccountRef": {"value": "41"},
        "EntityRef": {"value": "55"},
        "DepartmentRef": {"value": "None"},
        "TxnDate": "2022-01-23",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Reimbursable expense by ashwin.t@fyle.in on 2022-01-23 ",
        "Credit": "None",
        "Line": [
            {
                "Description": "ashwin.t@fyle.in - Food - 2022-01-23 - C/2022/01/R/16 -  - https://staging.fyle.tech/app/admin/#/company_expenses?txnId=txRJYVMgMaH6&org_id=or79Cob97KSh",
                "DetailType": "AccountBasedExpenseLineDetail",
                "Amount": 60.0,
                "AccountBasedExpenseLineDetail": {"AccountRef": {"value": "56"},"CustomerRef": {"value": "None"},"ClassRef": {"value": "None"},"TaxCodeRef": {"value": "None"},"TaxAmount": 0.0,"BillableStatus": "NotBillable"},
            }
        ],
        'GlobalTaxCalculation': 'TaxInclusive'
    },
    "qbo_expense_payload_with_tax_override": {
        'DocNumber': None,
        'PaymentType': 'Cash',
        'AccountRef': {'value': '35'},
        'EntityRef': {'value': '55'},
        'DepartmentRef': {'value': None},
        'TxnDate': '2024-06-24',
        'CurrencyRef': {'value': 'USD'},
        'PrivateNote': 'Reimbursable expense by user9@fyleforgotham.in on 2020-05-13 ',
        'Credit': None,
        'Line': [
            {
                'Description': 'user9@fyleforgotham.in - Office Party - 2020-05-13 - C/2021/04/R/42 -  - None/app/admin/#/company_expenses?txnId=txU2qpKmrUR9&org_id=or79Cob97KSh',
                'DetailType': 'AccountBasedExpenseLineDetail',
                'Amount': 1060.71,
                'AccountBasedExpenseLineDetail': {
                    'CustomerRef': {'value': None},
                    'ClassRef': {'value': None},
                    'TaxCodeRef': {'value': '17'},
                    'BillableStatus': 'NotBillable',
                    'AccountRef': {'value': '13'},'TaxAmount': 127.29
                }
            }
        ],
        'GlobalTaxCalculation': 'TaxExcluded',
        'TxnTaxDetail': {
            'TaxLine': [
                {
                    'Amount': 74.25,
                    'DetailType': 'TaxLineDetail',
                    'TaxLineDetail': {'TaxRateRef': {'value': '28'},'PercentBased': False,'NetAmountTaxable': 1060.71}
                },
                {
                    'Amount': 53.04,
                    'DetailType': 'TaxLineDetail',
                    'TaxLineDetail': {'TaxRateRef': {'value': '37'},'PercentBased': False,'NetAmountTaxable': 1060.71}
                }
            ]
        }
    },
    "journal_entry_payload": {
        "GlobalTaxCalculation": "TaxInclusive",
        "TxnDate": "2022-01-23",
        "PrivateNote": "Credit card expense by ashwin.t@fyle.in on 2022-01-23 ",
        "DocNumber": "1",
        "Line": [
            {
                "DetailType": "JournalEntryLineDetail",
                "Description": "ashwin.t@fyle.in - Food - 2022-01-23 - C/2022/01/R/14 -  - https://staging.fyle.tech/app/admin/#/company_expenses?txnId=txMFjDHNxEPt&org_id=or79Cob97KSh",
                "Amount": 90.0,
                "JournalEntryLineDetail": {
                    "PostingType": "Credit",
                    "AccountRef": {"value": "42"},
                    "DepartmentRef": {"value": "None"},
                    "ClassRef": {"value": "None"},
                    "Entity": {"EntityRef": {"value": "55"},"Type": "Employee"},
                    "TaxInclusiveAmt": 90.0,
                    "TaxCodeRef": {"value": "None"},
                    "TaxAmount": 0.0,
                    "TaxApplicableOn": "Purchase",
                },
            },
            {
                "DetailType": "JournalEntryLineDetail",
                "Description": "ashwin.t@fyle.in - Food - 2022-01-23 - C/2022/01/R/14 -  - https://staging.fyle.tech/app/admin/#/company_expenses?txnId=txMFjDHNxEPt&org_id=or79Cob97KSh",
                "Amount": 90.0,
                "JournalEntryLineDetail": {
                    "PostingType": "Debit",
                    "AccountRef": {"value": "56"},
                    "DepartmentRef": {"value": "None"},
                    "ClassRef": {"value": "None"},
                    "Entity": {"EntityRef": {"value": "55"},"Type": "Employee"},
                    "TaxInclusiveAmt": 90.0,
                    "TaxCodeRef": {"value": "None"},
                    "TaxAmount": 0.0,
                    "TaxApplicableOn": "Purchase",
                },
            },
        ],
        "CurrencyRef": {"value": "USD"},
        "TxnTaxDetail": {"TaxLine": [{"Amount": 103.55,"DetailType": "TaxLineDetail","TaxLineDetail": {"NetAmountTaxable": 0,"PercentBased": True,"TaxRateRef": {"name": "ON TAX PURCHASE","value": "6"}}}]},
    },
    "cheque_payload": {
        "DocNumber": "None",
        "PaymentType": "Check",
        "AccountRef": {"value": "35"},
        "EntityRef": {"value": "55"},
        "DepartmentRef": {"value": "None"},
        "TxnDate": "2022-01-31",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Credit card expense by ashwin.t@fyle.in on 2022-01-23 ",
        "Credit": "None",
        "Line": [
            {
                "Description": "ashwin.t@fyle.in - Food - 2022-01-23 - C/2022/01/R/14 -  - https://staging.fyle.tech/app/admin/#/company_expenses?txnId=txMFjDHNxEPt&org_id=or79Cob97KSh",
                "DetailType": "AccountBasedExpenseLineDetail",
                "Amount": 90.0,
                "AccountBasedExpenseLineDetail": {"AccountRef": {"value": "56"},"ClassRef": {"value": "None"},"CustomerRef": {"value": "None"},"TaxCodeRef": {"value": "None"},"TaxAmount": 0.0,"BillableStatus": "NotBillable"},
            }
        ],
        'GlobalTaxCalculation': 'TaxInclusive'
    },
    "cheque_payload_with_tax_override": {
        "DocNumber": None,
        "PaymentType": "Check",
        "AccountRef": {"value": "95"},
        "EntityRef": {"value": "55"},
        "DepartmentRef": {"value": None},
        "TxnDate": "2024-06-24",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Reimbursable expense by user9@fyleforgotham.in",
        "Credit": None,
        "Line": [
            {
                "Description": "user9@fyleforgotham.in - Food - 2020-05-10 - C/2021/04/R/42 -  - None/app/admin/#/company_expenses?txnId=txHmoggWDQZs&org_id=or79Cob97KSh",
                "DetailType": "AccountBasedExpenseLineDetail",
                "Amount": 715.18,
                "AccountBasedExpenseLineDetail": {
                    "CustomerRef": {"value": None},
                    "ClassRef": {"value": None},
                    "TaxCodeRef": {"value": "17"},
                    "BillableStatus": "NotBillable",
                    "AccountRef": {"value": "13"},
                    "TaxAmount": 85.82,
                },
            },
            {
                "Description": "user9@fyleforgotham.in - Office Party - 2020-05-01 - C/2021/04/R/42 -  - None/app/admin/#/company_expenses?txnId=txqy5WraeWt6&org_id=or79Cob97KSh",
                "DetailType": "AccountBasedExpenseLineDetail",
                "Amount": 1609.82,
                "AccountBasedExpenseLineDetail": {
                    "CustomerRef": {"value": None},
                    "ClassRef": {"value": None},
                    "TaxCodeRef": {"value": "17"},
                    "BillableStatus": "NotBillable",
                    "AccountRef": {"value": "13"},
                    "TaxAmount": 193.18,
                },
            },
            {
                "Description": "user9@fyleforgotham.in - Others - 2020-05-01 - C/2021/04/R/42 -  - None/app/admin/#/company_expenses?txnId=tx5PXU8lacAv&org_id=or79Cob97KSh",
                "DetailType": "AccountBasedExpenseLineDetail",
                "Amount": 528.57,
                "AccountBasedExpenseLineDetail": {
                    "CustomerRef": {"value": None},
                    "ClassRef": {"value": None},
                    "TaxCodeRef": {"value": "17"},
                    "BillableStatus": "NotBillable",
                    "AccountRef": {"value": "9"},
                    "TaxAmount": 63.43,
                },
            },
        ],
        "GlobalTaxCalculation": "TaxExcluded",
        "TxnTaxDetail": {
            "TaxLine": [
                {
                    "Amount": 199.75,
                    "DetailType": "TaxLineDetail",
                    "TaxLineDetail": {
                        "TaxRateRef": {"value": "28"},
                        "PercentBased": False,
                        "NetAmountTaxable": 2853.57,
                    },
                },
                {
                    "Amount": 142.68,
                    "DetailType": "TaxLineDetail",
                    "TaxLineDetail": {
                        "TaxRateRef": {"value": "37"},
                        "PercentBased": False,
                        "NetAmountTaxable": 2853.57,
                    },
                },
            ]
        },
    },
    "cheque_item_based_payload": {
        "DocNumber": "None",
        "PaymentType": "Check",
        "AccountRef": {"value": "95"},
        "EntityRef": {"value": "55"},
        "DepartmentRef": {"value": "None"},
        "TxnDate": "2023-04-19",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Reimbursable expense by user9@fyleforgotham.in on 2023-04-19 ",
        "Credit": "None",
        "Line": [
            {
                "Description": "user9@fyleforgotham.in - Concrete - 2023-04-19 - C/2023/04/R/13 -  - None/app/admin/#/company_expenses?txnId=txT4kpMbiPlHdLm&org_id=or79Cob97KSh",
                "DetailType": "ItemBasedExpenseLineDetail",
                "Amount": 1.0,
                "ItemBasedExpenseLineDetail": {"ItemRef": {"value": "3"},"Qty": 1,"CustomerRef": {"value": "None"},"ClassRef": {"value": "None"},"TaxCodeRef": {"value": "None"},"BillableStatus": "NotBillable"},
            }
        ],
        'GlobalTaxCalculation': 'TaxInclusive'
    },
    "cheque_item_based_payload_with_tax_override": {
        "DocNumber": None,
        "PaymentType": "Check",
        "AccountRef": {"value": "95"},
        "EntityRef": {"value": "55"},
        "DepartmentRef": {"value": None},
        "TxnDate": "2024-06-24",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Reimbursable expense by user9@fyleforgotham.in on 2024-06-24 ",
        "Credit": None,
        "Line": [
            {
                "Description": "user9@fyleforgotham.in - Concrete - 2024-06-24 - C/2023/04/R/7 -  - None/app/admin/#/company_expenses?txnId=txT4kpMbiPlHdLm&org_id=or79Cob97KSh",
                "DetailType": "ItemBasedExpenseLineDetail",
                "Amount": 0.89,
                "ItemBasedExpenseLineDetail": {
                    "CustomerRef": {"value": None},
                    "ClassRef": {"value": None},
                    "TaxCodeRef": {"value": "17"},
                    "BillableStatus": "NotBillable",
                    "ItemRef": {"value": "3"},
                    "Qty": 1,
                },
            }
        ],
        "GlobalTaxCalculation": "TaxExcluded",
        "TxnTaxDetail": {
            "TaxLine": [
                {
                    "Amount": 0.06,
                    "DetailType": "TaxLineDetail",
                    "TaxLineDetail": {
                        "TaxRateRef": {"value": "28"},
                        "PercentBased": False,
                        "NetAmountTaxable": 0.89,
                    },
                },
                {
                    "Amount": 0.05,
                    "DetailType": "TaxLineDetail",
                    "TaxLineDetail": {
                        "TaxRateRef": {"value": "37"},
                        "PercentBased": False,
                        "NetAmountTaxable": 0.89,
                    },
                },
            ]
        },
    },
    "cheque_item_and_account_based_payload": {
        "DocNumber": "None",
        "PaymentType": "Check",
        "AccountRef": {"value": "95"},
        "EntityRef": {"value": "55"},
        "DepartmentRef": {"value": "None"},
        "TxnDate": "2023-04-19",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Reimbursable expense by user9@fyleforgotham.in",
        "Credit": "None",
        "Line": [
            {
                "Description": "user9@fyleforgotham.in - Concrete - 2023-04-19 - C/2023/04/R/13 -  - None/app/admin/#/company_expenses?txnId=txT4kpKidaAdLm&org_id=or79Cob97KSh",
                "DetailType": "ItemBasedExpenseLineDetail",
                "Amount": 1.0,
                "ItemBasedExpenseLineDetail": {"ItemRef": {"value": "3"},"Qty": 1,"CustomerRef": {"value": "None"},"ClassRef": {"value": "None"},"TaxCodeRef": {"value": "None"},"BillableStatus": "NotBillable"},
            },
            {
                "Description": "user9@fyleforgotham.in - Food - 2023-04-19 - C/2023/04/R/13 -  - None/app/admin/#/company_expenses?txnId=txT4kpMbiadw&org_id=or79Cob97KSh",
                "DetailType": "AccountBasedExpenseLineDetail",
                "Amount": 1.0,
                "AccountBasedExpenseLineDetail": {"AccountRef": {"value": "13"},"ClassRef": {"value": "None"},"CustomerRef": {"value": "None"},"TaxCodeRef": {"value": "None"},"TaxAmount": 0.0,"BillableStatus": "NotBillable"},
            },
        ],
        'GlobalTaxCalculation': 'TaxInclusive'
    },
    "cheque_item_and_account_based_payload_with_tax_override": {
        "DocNumber": None,
        "PaymentType": "Check",
        "AccountRef": {"value": "95"},
        "EntityRef": {"value": "55"},
        "DepartmentRef": {"value": None},
        "TxnDate": "2024-06-24",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Reimbursable expense by user9@fyleforgotham.in",
        "Credit": None,
        "Line": [
            {
                "Description": "user9@fyleforgotham.in - Concrete - 2024-06-24 - C/2023/04/R/13 -  - None/app/admin/#/company_expenses?txnId=txT4kpKidaAdLm&org_id=or79Cob97KSh",
                "DetailType": "ItemBasedExpenseLineDetail",
                "Amount": 0.89,
                "ItemBasedExpenseLineDetail": {
                    "CustomerRef": {"value": None},
                    "ClassRef": {"value": None},
                    "TaxCodeRef": {"value": "17"},
                    "BillableStatus": "NotBillable",
                    "ItemRef": {"value": "3"},
                    "Qty": 1,
                },
            },
            {
                "Description": "user9@fyleforgotham.in - Food - 2024-06-24 - C/2023/04/R/13 -  - None/app/admin/#/company_expenses?txnId=txT4kpMbiadw&org_id=or79Cob97KSh",
                "DetailType": "AccountBasedExpenseLineDetail",
                "Amount": 0.89,
                "AccountBasedExpenseLineDetail": {
                    "CustomerRef": {"value": None},
                    "ClassRef": {"value": None},
                    "TaxCodeRef": {"value": "17"},
                    "BillableStatus": "NotBillable",
                    "AccountRef": {"value": "13"},
                    "TaxAmount": 0.11,
                },
            },
        ],
        "GlobalTaxCalculation": "TaxExcluded",
        "TxnTaxDetail": {
            "TaxLine": [
                {
                    "Amount": 0.12,
                    "DetailType": "TaxLineDetail",
                    "TaxLineDetail": {
                        "TaxRateRef": {"value": "28"},
                        "PercentBased": False,
                        "NetAmountTaxable": 1.78,
                    },
                },
                {
                    "Amount": 0.1,
                    "DetailType": "TaxLineDetail",
                    "TaxLineDetail": {
                        "TaxRateRef": {"value": "37"},
                        "PercentBased": False,
                        "NetAmountTaxable": 1.78,
                    },
                },
            ]
        },
    },
    "bill_response": {
        "SyncToken": "2",
        "domain": "QBO",
        "APAccountRef": {"name": "Accounts Payable (A/P)","value": "33"},
        "VendorRef": {"name": "Norton Lumber and Building Materials","value": "46"},
        "TxnDate": "2014-11-06",
        "TotalAmt": 103.55,
        "CurrencyRef": {"name": "United States Dollar","value": "USD"},
        "LinkedTxn": [{"TxnId": "118","TxnType": "BillPaymentCheck"}],
        "SalesTermRef": {"value": "3"},
        "DueDate": "2014-12-06",
        "sparse": False,
        "Line": [
            {"DetailType": "TaxLineDetail","Amount": 103.55,"Id": "1","DetailType": "TaxLineDetail","TaxLineDetail": {"NetAmountTaxable": 0,"PercentBased": True,"TaxRateRef": {"name": "ON TAX PURCHASE","value": "6"}},"Description": "Lumber"}
        ],
        "Balance": 0,
        "Id": "25",
        "MetaData": {"CreateTime": "2014-11-06T15:37:25-08:00","LastUpdatedTime": "2015-02-09T10:11:11-08:00"},
    },
    "post_bill": {"Bill": {"Id": "sdfghjk"}},
    "post_purchase": {"Purchase": {"Id": "sdfghjk"}},
    "post_journal_entry": {"JournalEntry": {"Id": "sdfghjk"}},
    "tax_code_response": [
        {
            "SyncToken": "0",
            "domain": "QBO",
            "TaxGroup": True,
            "Name": "California",
            "Taxable": True,
            "PurchaseTaxRateList": {"TaxRateDetail": [{"TaxRateRef": {"value": "6","name": "ON TAX PURCHASE"},"TaxTypeApplicable": "TaxOnAmount","TaxOrder": 0}]},
            "sparse": False,
            "Active": True,
            "Description": "California",
            "MetaData": {"CreateTime": "2014-09-18T12:17:04-07:00","LastUpdatedTime": "2014-09-18T12:17:04-07:00"},
            "Id": "2",
            "SalesTaxRateList": {"TaxRateDetail": [{"TaxTypeApplicable": "TaxOnAmount","TaxRateRef": {"name": "California","value": "3"},"TaxOrder": 0}]},
        }
    ],
    "vendor_response": [
        {
            "PrimaryEmailAddr": {"Address": "Books@Intuit.com"},
            "Vendor1099": False,
            "domain": "QBO",
            "GivenName": "Bessie",
            "DisplayName": "Books by Bessie",
            'CurrencyRef': {'value': 'USD','name': 'United States Dollar'},
            "BillAddr": {"City": "Palo Alto","Line1": "15 Main St.","PostalCode": "94303","Lat": "37.445013","Long": "-122.1391443","CountrySubDivisionCode": "CA","Id": "31"},
            "SyncToken": "0",
            "PrintOnCheckName": "Books by Bessie",
            "FamilyName": "Williams",
            "PrimaryPhone": {"FreeFormNumber": "(650) 555-7745"},
            "AcctNum": "1345",
            "CompanyName": "Books by Bessie",
            "WebAddr": {"URI": "http://www.booksbybessie.co"},
            "sparse": False,
            "Active": True,
            "Balance": 0,
            "Id": "30",
            "MetaData": {"CreateTime": "2014-09-12T10:07:56-07:00","LastUpdatedTime": "2014-09-17T11:13:46-07:00"},
        }
    ],
    "post_vendor_resp": {
        "Vendor": {
            "PrimaryEmailAddr": {"Address": "Books@Intuit.com"},
            "Vendor1099": False,
            "domain": "QBO",
            "GivenName": "samp_merchant",
            "DisplayName": "samp_merchant",
            "BillAddr": {"City": "Palo Alto","Line1": "15 Main St.","PostalCode": "94303","Lat": "37.445013","Long": "-122.1391443","CountrySubDivisionCode": "CA","Id": "31"},
            "SyncToken": "0",
            "PrintOnCheckName": "samp_merchant",
            "FamilyName": "Williams",
            "PrimaryPhone": {"FreeFormNumber": "(650) 555-7745"},
            "AcctNum": "1345",
            "CompanyName": "samp_merchant",
            "WebAddr": {"URI": "http://www.booksbybessie.co"},
            "sparse": False,
            "Active": True,
            "Balance": 0,
            "Id": "58",
            "MetaData": {"CreateTime": "2014-09-12T10:07:56-07:00","LastUpdatedTime": "2014-09-17T11:13:46-07:00"},
        }
    },
    "employee_response": [
        {
            "SyncToken": "0",
            "domain": "QBO",
            "DisplayName": "Bill Miller",
            "PrimaryPhone": {"FreeFormNumber": "234-525-1234"},
            "PrintOnCheckName": "Bill Miller",
            "FamilyName": "Miller",
            "Active": True,
            "SSN": "XXX-XX-XXXX",
            "PrimaryAddr": {"CountrySubDivisionCode": "CA","City": "Middlefield","PostalCode": "93242","Id": "116","Line1": "45 N. Elm Street"},
            "sparse": False,
            "BillableTime": False,
            "GivenName": "Bill",
            "Id": "71",
            "MetaData": {"CreateTime": "2015-07-24T09:34:35-07:00","LastUpdatedTime": "2015-07-24T09:34:35-07:00"},
        }
    ],
    "employee_response_after_sync": [
        {
            "SyncToken": "0",
            "domain": "QBO",
            "DisplayName": "Bill sync after",
            "PrimaryPhone": {"FreeFormNumber": "234-525-1234"},
            "PrintOnCheckName": "Bill sync after",
            "FamilyName": "sync after",
            "Active": True,
            "SSN": "XXX-XX-XXXX",
            "PrimaryAddr": {"CountrySubDivisionCode": "CA","City": "Middlefield","PostalCode": "93242","Id": "116","Line1": "45 N. Elm Street"},
            "sparse": False,
            "BillableTime": False,
            "GivenName": "Bill sync after",
            "Id": "72syncafter",
            "MetaData": {"CreateTime": "2015-07-24T09:34:35-07:00","LastUpdatedTime": "2015-07-24T09:34:35-07:00"},
        }
    ],
    "employee_response_with_inactive_values": [
        {
            "SyncToken": "0",
            "domain": "QBO",
            "DisplayName": "Bill Miller inactive",
            "PrimaryPhone": {"FreeFormNumber": "234-525-1234"},
            "PrintOnCheckName": "Bill Miller inactive",
            "FamilyName": "Miller inactive",
            "Active": True,
            "SSN": "XXX-XX-XXXX",
            "PrimaryAddr": {"CountrySubDivisionCode": "CA","City": "Middlefield","PostalCode": "93242","Id": "116","Line1": "45 N. Elm Street"},
            "sparse": False,
            "BillableTime": False,
            "GivenName": "Bill inactive",
            "Id": "73423",
            "MetaData": {"CreateTime": "2015-07-24T09:34:35-07:00","LastUpdatedTime": "2015-07-24T09:34:35-07:00"},
        }
    ],
    "class_response": [
        {
            "FullyQualifiedName": "France",
            "domain": "QBO",
            "Name": "France",
            "SyncToken": "0",
            "SubClass": False,
            "sparse": False,
            "Active": True,
            "Id": "5000000000000007280",
            "MetaData": {"CreateTime": "2015-07-22T13:57:27-07:00","LastUpdatedTime": "2015-07-22T13:57:27-07:00"},
        },
        {
            "FullyQualifiedName": "France",
            "domain": "QBO",
            "Name": "France",
            "SyncToken": "0",
            "SubClass": False,
            "sparse": False,
            "Active": True,
            "Id": "9",
            "MetaData": {"CreateTime": "2015-07-22T13:57:27-07:00","LastUpdatedTime": "2015-07-22T13:57:27-07:00"},
        },
    ],
    "department_response": [
        {
            "FullyQualifiedName": "Marketing Department",
            "domain": "QBO",
            "Name": "Marketing Department",
            "SyncToken": "0",
            "SubDepartment": False,
            "sparse": False,
            "Active": True,
            "Id": "2",
            "MetaData": {"CreateTime": "2013-08-13T11:52:48-07:00","LastUpdatedTime": "2013-08-13T11:52:48-07:00"},
        }
    ],
    "tax_rate_get_by_id": {
        "RateValue": 2,
        "AgencyRef": {"value": "1"},
        "domain": "QBO",
        "Name": "Tucson City",
        "SyncToken": "0",
        "SpecialTaxType": "NONE",
        "DisplayType": "ReadOnly",
        "sparse": False,
        "Active": True,
        "MetaData": {"CreateTime": "2014-09-18T12:17:04-07:00","LastUpdatedTime": "2014-09-18T12:17:04-07:00"},
        "Id": "2",
        "Description": "Sales Tax",
    },
    "account_response": [
        {
            "FullyQualifiedName": "Expense",
            "domain": "QBO",
            "Name": "Expense",
            "Classification": "Liability",
            "AccountSubType": "AccountsPayable",
            "CurrentBalanceWithSubAccounts": -1091.23,
            "sparse": False,
            "MetaData": {"CreateTime": "2014-09-12T10:12:02-07:00","LastUpdatedTime": "2015-06-30T15:09:07-07:00"},
            "AccountType": "Expense",
            "CurrentBalance": -1091.23,
            "Active": True,
            "SyncToken": "0",
            "Id": "7",
            "SubAccount": False,
        },
        {
            "FullyQualifiedName": "Bank",
            "domain": "QBO",
            "Name": "Bank",
            "Classification": "Liability",
            "AccountSubType": "AccountsPayable",
            "CurrentBalanceWithSubAccounts": -1091.23,
            "sparse": False,
            "MetaData": {"CreateTime": "2014-09-12T10:12:02-07:00","LastUpdatedTime": "2015-06-30T15:09:07-07:00"},
            "AccountType": "Bank",
            "CurrentBalance": -1091.23,
            "Active": True,
            "SyncToken": "0",
            "Id": "33",
            "SubAccount": False,
        },
        {
            "FullyQualifiedName": "Credit Card",
            "domain": "QBO",
            "Name": "Credit Card",
            "Classification": "Liability",
            "AccountSubType": "AccountsPayable",
            "CurrentBalanceWithSubAccounts": -1091.23,
            "sparse": False,
            "MetaData": {"CreateTime": "2014-09-12T10:12:02-07:00","LastUpdatedTime": "2015-06-30T15:09:07-07:00"},
            "AccountType": "Credit Card",
            "CurrentBalance": -1091.23,
            "Active": True,
            "SyncToken": "0",
            "Id": "33",
            "SubAccount": False,
        },
        {
            "FullyQualifiedName": "Credit Card",
            "domain": "QBO",
            "Name": "Credit Card",
            "Classification": "Liability",
            "AccountSubType": "AccountsPayable",
            "CurrentBalanceWithSubAccounts": -1091.23,
            "sparse": False,
            "MetaData": {"CreateTime": "2014-09-12T10:12:02-07:00","LastUpdatedTime": "2015-06-30T15:09:07-07:00"},
            "AccountType": "Credit Cards",
            "CurrentBalance": -1091.23,
            "Active": True,
            "SyncToken": "0",
            "Id": "34",
            "SubAccount": False,
        },
    ],
    "preference_response": {
        "AccountingInfoPrefs": {
            "FirstMonthOfFiscalYear": "January",
            "UseAccountNumbers": True,
            "TaxYearMonth": "January",
            "ClassTrackingPerTxn": False,
            "TrackDepartments": True,
            "TaxForm": "6",
            "CustomerTerminology": "Customers",
            "BookCloseDate": "2018-12-31",
            "DepartmentTerminology": "Location",
            "ClassTrackingPerTxnLine": True,
        }
    },
    "construct_bill": {
        "VendorRef": {"value": "84"},
        "APAccountRef": {"value": "33"},
        "DepartmentRef": {"value": "None"},
        "TxnDate": "2022-08-30",
        "CurrencyRef": {"value": "USD"},
        "PrivateNote": "Credit card expense by sravan.kumar@fyle.in on 2022-05-23 ",
        "Line": [
            {
                "Description": "sravan.kumar@fyle.in - WIP - 2022-05-23 - C/2022/05/R/8 -  - https://staging.fyle.tech/app/admin/#/company_expenses?txnId=tx3i1mrGprDs&org_id=orPJvXuoLqvJ",
                "DetailType": "AccountBasedExpenseLineDetail",
                "Amount": 1.0,
                "AccountBasedExpenseLineDetail": {"AccountRef": {"value": "69"},"CustomerRef": {"value": "None"},"ClassRef": {"value": "5000000000000142238"},"TaxCodeRef": {"value": "None"},"TaxAmount": 0.0,"BillableStatus": "NotBillable"},
            }
        ],
    },
    "bill_payment_response": {
        "SyncToken": "0",
        "domain": "QBO",
        "VendorRef": {"name": "Bob's Burger Joint","value": "56"},
        "TxnDate": "2015-07-14",
        "TotalAmt": 200.0,
        "PayType": "Check",
        "PrivateNote": "Acct. 1JK90",
        "sparse": False,
        "Line": [{"Amount": 200.0,"LinkedTxn": [{"TxnId": "234","TxnType": "Bill"}]}],
        "Id": "236",
        "CheckPayment": {"PrintStatus": "NeedToPrint","BankAccountRef": {"name": "Checking","value": "35"}},
        "MetaData": {"CreateTime": "2015-07-14T12:34:04-07:00","LastUpdatedTime": "2015-07-14T12:34:04-07:00"},
    },
    "company_info": {
        "SyncToken": "4",
        "domain": "QBO",
        "LegalAddr": {"City": "Mountain View","Country": "US","Line1": "2500 Garcia Ave","PostalCode": "94043","CountrySubDivisionCode": "CA","Id": "1"},
        "SupportedLanguages": "en",
        "CompanyName": "Sandbox Company_US_4",
        "Country": "US",
        "CompanyAddr": {"City": "Mountain View","Country": "US","Line1": "2500 Garcia Ave","PostalCode": "94043","CountrySubDivisionCode": "CA","Id": "1"},
        "sparse": False,
        "Id": "1",
        "WebAddr": {},
        "FiscalYearStartMonth": "January",
        "CustomerCommunicationAddr": {"City": "Mountain View","Country": "US","Line1": "2500 Garcia Ave","PostalCode": "94043","CountrySubDivisionCode": "CA","Id": "1"},
        "PrimaryPhone": {"FreeFormNumber": "(650)944-4444"},
        "LegalName": "Larry's Bakery",
        "CompanyStartDate": "2015-06-05",
        "Email": {"Address": "donotreply@intuit.com"},
        "NameValue": [{"Name": "NeoEnabled","Value": "True"}],
        "MetaData": {"CreateTime": "2015-06-05T13:55:54-07:00","LastUpdatedTime": "2015-07-06T08:51:50-07:00"},
    },
    "reimbursements": [
        {
            "amount": 76,
            "code": None,
            "created_at": "2022-01-20T16:30:44.584100",
            "creator_user_id": "usqywo0f3nBY",
            "currency": "USD",
            "id": "sett283OqFZ42",
            "is_exported": False,
            "is_paid": True,
            "mode": "OFFLINE",
            "org_id": "orsO0VW86WLQ",
            "paid_at": "2022-01-20T16:30:44.584100",
            "purpose": "C/2022/01/R/2;Ashwin",
            "reimbursement_number": "P/2022/01/R/2",
            "settlement_id": "sett283OqFZ42",
            "updated_at": "2022-01-20T16:30:44.584100",
            "user_id": "usqywo0f3nBY",
        }
    ],
    'empty_general_maapings': {
        'default_ccc_vendor_id': '',
        'default_ccc_vendor_name': '',
        'accounts_payable_name': '',
        'accounts_payable_id': '',
        'bank_account_name': '',
        'bank_account_id': '',
        'qbo_expense_account_name': '',
        'qbo_expense_account_id': '',
        'default_debit_card_account_name': '',
        'default_debit_card_account_id': '',
        'default_tax_code_id': '',
        'default_tax_code_name': '',
        'default_ccc_account_id': '',
        'default_ccc_account_name': '',
    },
    'items_response_with_inactive_values': [
        {
            "Name": "Concrete",
            "Description": "Concrete for fountain installation",
            "Active": True,
            "FullyQualifiedName": "Concrete",
            "Taxable": True,
            "UnitPrice": 0,
            "Type": "Service",
            "IncomeAccountRef": {"value": "48","name": "Fountains and Garden Lighting"},
            "PurchaseCost": 0,
            "TrackQtyOnHand": False,
            "domain": "QBO",
            "sparse": False,
            "Id": "3",
            "SyncToken": "1",
            "MetaData": {"CreateTime": "2019-12-16T10:36:03-08:00","LastUpdatedTime": "2019-12-19T12:47:47-08:00"},
        },
        {
            "Name": "Maintenance & Repair",
            "Description": "Maintenance & Repair",
            "Active": True,
            "FullyQualifiedName": "Maintenance & Repair",
            "Taxable": False,
            "UnitPrice": 0,
            "Type": "Service",
            "IncomeAccountRef": {"value": "53","name": "Maintenance and Repair"},
            "PurchaseCost": 0,
            "TrackQtyOnHand": False,
            "domain": "QBO",
            "sparse": False,
            "Id": "9",
            "SyncToken": "0",
            "MetaData": {"CreateTime": "2019-12-16T10:45:18-08:00","LastUpdatedTime": "2019-12-16T10:45:18-08:00"},
        },
    ],
    'items_response_with_category': [
        {
            "Name": "Concrete Category",
            "Description": "Concrete for fountain installation",
            "Active": True,
            "FullyQualifiedName": "Concrete Category Sync",
            "Taxable": True,
            "UnitPrice": 0,
            "Type": "Category",
            "IncomeAccountRef": {"value": "48","name": "Fountains and Garden Lighting"},
            "PurchaseCost": 0,
            "TrackQtyOnHand": False,
            "domain": "QBO",
            "sparse": False,
            "Id": "3category",
            "SyncToken": "1",
            "MetaData": {"CreateTime": "2019-12-16T10:36:03-08:00","LastUpdatedTime": "2019-12-19T12:47:47-08:00"},
        },
    ],
    'items_response': [
        {
            "Name": "Concrete",
            "Description": "Concrete for fountain installation",
            "Active": True,
            "FullyQualifiedName": "Concrete",
            "Taxable": True,
            "UnitPrice": 0,
            "Type": "Service",
            "IncomeAccountRef": {"value": "48","name": "Fountains and Garden Lighting"},
            "PurchaseCost": 0,
            "TrackQtyOnHand": False,
            "domain": "QBO",
            "sparse": False,
            "Id": "3",
            "SyncToken": "1",
            "MetaData": {"CreateTime": "2019-12-16T10:36:03-08:00","LastUpdatedTime": "2019-12-19T12:47:47-08:00"},
        },
        {
            "Name": "Lighting",
            "Description": "Garden Lighting",
            "Active": True,
            "FullyQualifiedName": "Lighting",
            "Taxable": True,
            "UnitPrice": 0,
            "Type": "Service",
            "IncomeAccountRef": {"value": "48","name": "Fountains and Garden Lighting"},
            "PurchaseCost": 0,
            "TrackQtyOnHand": False,
            "domain": "QBO",
            "sparse": False,
            "Id": "8",
            "SyncToken": "1",
            "MetaData": {"CreateTime": "2019-12-16T10:44:40-08:00","LastUpdatedTime": "2019-12-19T12:47:38-08:00"},
        },
        {
            "Name": "Maintenance & Repair",
            "Description": "Maintenance & Repair",
            "Active": True,
            "FullyQualifiedName": "Maintenance & Repair",
            "Taxable": False,
            "UnitPrice": 0,
            "Type": "Service",
            "IncomeAccountRef": {"value": "53","name": "Maintenance and Repair"},
            "PurchaseCost": 0,
            "TrackQtyOnHand": False,
            "domain": "QBO",
            "sparse": False,
            "Id": "9",
            "SyncToken": "0",
            "MetaData": {"CreateTime": "2019-12-16T10:45:18-08:00","LastUpdatedTime": "2019-12-16T10:45:18-08:00"},
        },
        {
            "Name": "Pest Control",
            "Description": "Pest Control Services",
            "Active": True,
            "FullyQualifiedName": "Pest Control",
            "Taxable": False,
            "UnitPrice": 35,
            "Type": "Service",
            "IncomeAccountRef": {"value": "54","name": "Pest Control Services"},
            "PurchaseCost": 0,
            "TrackQtyOnHand": False,
            "domain": "QBO",
            "sparse": False,
            "Id": "10",
            "SyncToken": "0",
            "MetaData": {"CreateTime": "2019-12-16T10:45:49-08:00","LastUpdatedTime": "2019-12-16T10:45:49-08:00"},
        },
    ],
    "webhook_payload_multi_entity": {
        "eventNotifications": [
            {
                "realmId": "123456789",
                "dataChangeEvent": {
                    "entities": [
                        {
                            "name": "Account",
                            "id": "1",
                            "operation": "Create",
                            "lastUpdated": "2023-12-01T10:00:00-08:00"
                        },
                        {
                            "name": "Item",
                            "id": "2",
                            "operation": "Update",
                            "lastUpdated": "2023-12-01T10:05:00-08:00"
                        }
                    ]
                }
            }
        ]
    },
    "webhook_payload_single_entity": {
        "eventNotifications": [
            {
                "realmId": "987654321",
                "dataChangeEvent": {
                    "entities": [
                        {
                            "name": "Vendor",
                            "id": "3",
                            "operation": "Delete",
                            "lastUpdated": "2023-12-01T11:00:00-08:00"
                        }
                    ]
                }
            }
        ]
    },
    "webhook_payload_nonexistent_realm": {
        "eventNotifications": [
            {
                "realmId": "nonexistent_realm",
                "dataChangeEvent": {
                    "entities": [
                        {
                            "name": "Account",
                            "id": "999",
                            "operation": "Create",
                            "lastUpdated": "2023-12-01T12:00:00-08:00"
                        }
                    ]
                }
            }
        ]
    },
    "vendor_response_after_sync": [
        {
            "PrimaryEmailAddr": {"Address": "NewBooks@Intuit.com"},
            "Vendor1099": False,
            "domain": "QBO",
            "GivenName": "Anna 1",
            "DisplayName": "Sync After testing",
            'CurrencyRef': {'value': 'USD','name': 'United States Dollar'},
            "BillAddr": {"City": "San Francisco","Line1": "25 Market St.","PostalCode": "94102","Lat": "37.445013","Long": "-122.1391443","CountrySubDivisionCode": "CA","Id": "32"},
            "SyncToken": "0",
            "PrintOnCheckName": "Books by Anna 1",
            "FamilyName": "Johnson 1",
            "PrimaryPhone": {"FreeFormNumber": "(650) 555-8856"},
            "AcctNum": "1346",
            "CompanyName": "Books by Anna 1",
            "WebAddr": {"URI": "http://www.booksbyanna.co"},
            "sparse": False,
            "Active": True,
            "Balance": 0,
            "Id": "32sync",
            "MetaData": {"CreateTime": "2014-09-12T10:07:56-07:00","LastUpdatedTime": "2014-09-17T11:13:46-07:00"},
        }
    ],
    "department_response_after_sync": [
        {
            "FullyQualifiedName": "Sales Department 1",
            "domain": "QBO",
            "Name": "Sales Department 1",
            "SyncToken": "0",
            "SubDepartment": False,
            "sparse": False,
            "Active": True,
            "Id": "33",
            "MetaData": {"CreateTime": "2013-08-13T11:52:48-07:00","LastUpdatedTime": "2013-08-13T11:52:48-07:00"},
        }
    ],
    "department_response_with_inactive_values": [
        {
            "FullyQualifiedName": "Sales Department taxi",
            "domain": "QBO",
            "Name": "Sales Department taxi",
            "SyncToken": "0",
            "SubDepartment": False,
            "sparse": False,
            "Active": False,
            "Id": "33",
            "MetaData": {"CreateTime": "2013-08-13T11:52:48-07:00","LastUpdatedTime": "2013-08-13T11:52:48-07:00"},
        }
    ],
    "items_response_after_sync": [
        {
            "Name": "Garden Tools 1",
            "Description": "Garden Tools and Equipment",
            "Active": True,
            "FullyQualifiedName": "Garden Sync After",
            "Taxable": True,
            "UnitPrice": 0,
            "Type": "Service",
            "IncomeAccountRef": {"value": "49","name": "Garden Tools and Equipment"},
            "PurchaseCost": 0,
            "TrackQtyOnHand": False,
            "domain": "QBO",
            "sparse": False,
            "Id": "12sync",
            "SyncToken": "1",
            "MetaData": {"CreateTime": "2019-12-16T10:36:03-08:00","LastUpdatedTime": "2019-12-19T12:47:47-08:00"},
        }
    ],
    "tax_code_response_after_sync": [
        {
            "SyncToken": "0",
            "domain": "QBO",
            "TaxGroup": True,
            "Name": "New Sync After",
            "Taxable": True,
            "PurchaseTaxRateList": {"TaxRateDetail": [{"TaxRateRef": {"value": "7","name": "NY TAX PURCHASE"},"TaxTypeApplicable": "TaxOnAmount","TaxOrder": 0}]},
            "sparse": False,
            "Active": True,
            "Description": "New York 1",
            "MetaData": {"CreateTime": "2014-09-18T12:17:04-07:00","LastUpdatedTime": "2014-09-18T12:17:04-07:00"},
            "Id": "4sync",
            "SalesTaxRateList": {"TaxRateDetail": [{"TaxTypeApplicable": "TaxOnAmount","TaxRateRef": {"name": "New York","value": "4"},"TaxOrder": 0}]},
        }
    ],
    "tax_code_response_with_inactive_values": [
        {
            "SyncToken": "0",
            "domain": "QBO",
            "TaxGroup": True,
            "Name": "New Sync After inactive",
            "Taxable": True,
            "PurchaseTaxRateList": {"TaxRateDetail": [{"TaxRateRef": {"value": "7","name": "NY TAX PURCHASE"},"TaxTypeApplicable": "TaxOnAmount","TaxOrder": 0}]},
            "sparse": False,
            "Active": True,
            "Description": "New York 1 inactive",
            "MetaData": {"CreateTime": "2014-09-18T12:17:04-07:00","LastUpdatedTime": "2014-09-18T12:17:04-07:00"},
            "Id": "4syncinactive",
            "SalesTaxRateList": {"TaxRateDetail": [{"TaxTypeApplicable": "TaxOnAmount","TaxRateRef": {"name": "New York","value": "4"},"TaxOrder": 0}]},
        }
    ],
    "account_response_after_sync": [
        {
            "FullyQualifiedName": "Office Supplies 23",
            "domain": "QBO",
            "Name": "Office Supplies 2",
            "Classification": "Expense",
            "AccountSubType": "OfficeExpenses",
            "CurrentBalanceWithSubAccounts": -500.00,
            "sparse": False,
            "MetaData": {"CreateTime": "2014-09-12T10:12:02-07:00","LastUpdatedTime": "2015-06-30T15:09:07-07:00"},
            "AccountType": "Expense",
            "CurrentBalance": -500.00,
            "Active": True,
            "SyncToken": "0",
            "Id": "4110",
            "SubAccount": False,
        }
    ],
    "class_response_after_sync": [
        {
            "FullyQualifiedName": "Germany 1",
            "domain": "QBO",
            "Name": "Germany 1",
            "SyncToken": "0",
            "SubClass": False,
            "sparse": False,
            "Active": True,
            "Id": "5000000000000007282",
            "MetaData": {"CreateTime": "2015-07-22T13:57:27-07:00","LastUpdatedTime": "2015-07-22T13:57:27-07:00"},
        }
    ],
    "class_response_with_inactive_values": [
        {
            "FullyQualifiedName": "Germany 1 tax",
            "domain": "QBO",
            "Name": "Germany 1 tax",
            "SyncToken": "0",
            "SubClass": False,
            "sparse": False,
            "Active": False,
            "Id": "5000000000000007282",
            "MetaData": {"CreateTime": "2015-07-22T13:57:27-07:00","LastUpdatedTime": "2015-07-22T13:57:27-07:00"},
        }
    ],
    "customer_response_after_sync": [
        {
            "FullyQualifiedName": "Spain Sync After",
            "domain": "QBO",
            "Name": "Spain 1",
            "SyncToken": "0",
            "sparse": False,
            "Active": True,
            "Id": "12sync",
            "MetaData": {"CreateTime": "2015-07-22T13:57:27-07:00","LastUpdatedTime": "2015-07-22T13:57:27-07:00"},
        }
    ],
}
