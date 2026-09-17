import unittest
from phone_utils import clean_phone_number, categorize_phone_number, process_phone_numbers
from excel_processor import load_excel_numbers
from sms_client import send_sms_blast, build_payload

class TestSMSBlasterV2(unittest.TestCase):

    def test_phone_normalization(self):
        # Float conversion fix
        self.assertEqual(clean_phone_number("9676775035.0"), "09676775035")
        self.assertEqual(clean_phone_number(9676775035.0), "09676775035")

        # Missing leading zero fix
        self.assertEqual(clean_phone_number("9178346464"), "09178346464")

        # International prefix fixes
        self.assertEqual(clean_phone_number("+639178346464"), "09178346464")
        self.assertEqual(clean_phone_number("639178346464"), "09178346464")

        # Formatting artifacts (spaces, dashes)
        self.assertEqual(clean_phone_number("0917-834-6464"), "09178346464")
        self.assertEqual(clean_phone_number("0917 834 6464"), "09178346464")

        # Landline
        self.assertEqual(clean_phone_number("0289515892"), "0289515892")

    def test_categorization(self):
        self.assertEqual(categorize_phone_number("09178346464"), "mobile")
        self.assertEqual(categorize_phone_number("0289515892"), "landline")
        self.assertEqual(categorize_phone_number("", "#N/A"), "na")
        self.assertEqual(categorize_phone_number(""), "empty")
        self.assertEqual(categorize_phone_number("12345"), "unknown")

    def test_batch_processing(self):
        sample_data = [
            "9676775035.0",
            "+639178346464",
            "0289515892",
            "#N/A",
            "",
            "invalid_num"
        ]
        result = process_phone_numbers(sample_data)
        self.assertEqual(len(result.mobile_numbers), 2)
        self.assertEqual(result.mobile_numbers, ["09676775035", "09178346464"])
        self.assertEqual(result.joined_mobile_numbers, "09676775035,09178346464")
        self.assertFalse(result.joined_mobile_numbers.startswith(","))
        self.assertEqual(len(result.tel_numbers), 1)
        self.assertEqual(result.na_count, 1)
        self.assertEqual(result.empty_count, 1)
        self.assertEqual(len(result.unknown_numbers), 1)

    def test_excel_loading(self):
        # Load from 1.xlsx
        result = load_excel_numbers("1.xlsx", col_identifier=6)
        self.assertTrue(result.total_mobile_count > 0)
        self.assertFalse(result.joined_mobile_numbers.startswith(","))

    def test_sms_client_dry_run(self):
        payload = build_payload("Test message", "09178346464,09181234567")
        self.assertEqual(payload["message"], "Test message")
        self.assertEqual(payload["receivers"], "09178346464,09181234567")

        res = send_sms_blast("Test message", "09178346464", dry_run=True)
        self.assertTrue(res["dry_run"])
        self.assertTrue(res["success"])

if __name__ == "__main__":
    unittest.main()
