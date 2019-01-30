from unittest import TestCase

from modules.database import broker as b


class TestBroker(TestCase):

    customer_element = {
        "element_name": "customer",
        "type": "primary",
        "table_name": "customers",
        "show_columns": ["customerName"],
        "attributes": [
            {
                "keyword": "_",
                "type": "word",
                "table_name": "customers",
                "columns": ["customerName"]
            },
            {
                "keyword": "with contact",
                "type": "word",
                "table_name": "customers",
                "columns": ["contactLastName", "contactFirstName"]
            },
            {
                "keyword": "located in",
                "type": "word",
                "table_name": "customers",
                "columns": ["city", "state", "country"]
            },
            {
                "keyword": "paid",
                "type": "num",
                "table_name": "payments",
                "columns": ["amount"],
                "by": [
                    {
                        "from_table_name": "customers",
                        "from_columns": ["customerNumber"],
                        "to_table_name": "payments",
                        "to_columns": ["customerNumber"]
                    }
                ]
            },
            {
                "keyword": "ordered",
                "type": "word",
                "table_name": "products",
                "columns": ["productName"],
                "by": [
                    {
                        "from_table_name": "customers",
                        "from_columns": ["customerNumber"],
                        "to_table_name": "orders",
                        "to_columns": ["customerNumber"]
                    },
                    {
                        "from_table_name": "orders",
                        "from_columns": ["orderNumber"],
                        "to_table_name": "orderdetails",
                        "to_columns": ["orderNumber"]
                    },
                    {
                        "from_table_name": "orderdetails",
                        "from_columns": ["productCode"],
                        "to_table_name": "products",
                        "to_columns": ["productCode"]
                    }
                ]
            },
            {
                "keyword": "reported to",
                "type": "word",
                "table_name": "employees",
                "columns": ["lastName", "firstName"],
                "by": [
                    {
                        "from_table_name": "customers",
                        "from_columns": ["salesRepEmployeeNumber"],
                        "to_table_name": "employees",
                        "to_columns": ["employeeNumber"]
                    }
                ]
            },
        ],
        "relations": [
            {
                "keyword": "payments made",
                "element_name": "payment",
                "by": [
                    {
                        "from_table_name": "customers",
                        "from_columns": ["customerNumber"],
                        "to_table_name": "payments",
                        "to_columns": ["customerNumber"]
                    }
                ]
            },
            {
                "keyword": "related sales representative",
                "element_name": "employee",
                "by": [
                    {
                        "from_table_name": "customers",
                        "from_columns": ["salesRepEmployeeNumber"],
                        "to_table_name": "employees",
                        "to_columns": ["employeeNumber"]
                    }
                ]
            },
            {
                "keyword": "orders made",
                "element_name": "order",
                "by": [
                    {
                        "from_table_name": "customers",
                        "from_columns": ["customerNumber"],
                        "to_table_name": "orders",
                        "to_columns": ["customerNumber"]
                    }
                ]
            }
        ]
    }

    customer_self_attribute = {
        "keyword": "test to customer",
        "type": "word",
        "table_name": "customers",
        "columns": ["customerName"],
        "by": [
            {
                "from_table_name": "customers",
                "from_columns": ["selfRelationCustNumber"],
                "to_table_name": "customers",
                "to_columns": ["customerNumber"]
            }
        ]
    }

    for a in customer_element['attributes']:
        a['operator'] = '='

    for a in customer_element['attributes']:
        a['value'] = '123'

    def test_label_attribute_columns(self):

        b.label_attributes(self.customer_element['attributes'])

        for a in self.customer_element['attributes']:
            print(a['letter'])
            for r in a.get('by', []):
                print('{} {}'.format(r['from_letter'], r['to_letter']))
            print('- - -')
        # self.fail()

    def test_get_FROM_query_string(self):

        self.customer_element['attributes'].append(self.customer_self_attribute)
        b.label_attributes(self.customer_element['attributes'])
        print(b.get_FROM_query_string('customers', self.customer_element['attributes']))

    def test_get_WHERE_JOIN_query_string(self):

        self.customer_element['attributes'].append(self.customer_self_attribute)
        b.label_attributes(self.customer_element['attributes'])
        print(b.get_WHERE_JOIN_query_string(self.customer_element['attributes']))

    def test_get_WHERE_ATTRIBUTES_query_string(self):

        self.customer_element['attributes'].append(self.customer_self_attribute)
        b.label_attributes(self.customer_element['attributes'])
        print(b.get_WHERE_ATTRIBUTES_query_string(self.customer_element['attributes']))

    def test_execute_query_select(self):

        b.load_db_schema()
        b.connect()
        print(b.query_find('customers', self.customer_element['attributes']))