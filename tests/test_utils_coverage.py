import os
import time
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch, PropertyMock, call

import pytest


# =============================================================================
# utils/password_policy.py  (34 stmts, 0% → 100%)
# =============================================================================

class TestPasswordPolicy:
    @patch("utils.password_policy.SystemSettings")
    def test_policy_enabled_true(self, MockS):
        MockS.get_setting.return_value = "true"
        from utils.password_policy import password_policy_enabled
        assert password_policy_enabled() is True

    @patch("utils.password_policy.SystemSettings")
    def test_policy_enabled_false(self, MockS):
        MockS.get_setting.return_value = "false"
        from utils.password_policy import password_policy_enabled
        assert password_policy_enabled() is False

    @patch("utils.password_policy.SystemSettings")
    def test_policy_enabled_1(self, MockS):
        MockS.get_setting.return_value = "1"
        from utils.password_policy import password_policy_enabled
        assert password_policy_enabled() is True

    @patch("utils.password_policy.SystemSettings")
    def test_policy_enabled_empty(self, MockS):
        MockS.get_setting.return_value = ""
        from utils.password_policy import password_policy_enabled
        assert password_policy_enabled() is False

    @patch("utils.password_policy.password_policy_enabled")
    def test_validate_disabled_short(self, mock_enabled):
        mock_enabled.return_value = False
        from utils.password_policy import validate_password
        ok, msg = validate_password("ab")
        assert ok is False
        assert "قصيرة" in msg

    @patch("utils.password_policy.password_policy_enabled")
    def test_validate_disabled_ok(self, mock_enabled):
        mock_enabled.return_value = False
        from utils.password_policy import validate_password
        ok, msg = validate_password("abcdef")
        assert ok is True
        assert msg == ""

    @patch("utils.password_policy.SystemSettings")
    def test_validate_enabled_too_short(self, MockS):
        def fake_get(k, d=None):
            if k == "password_policy_enabled":
                return "true"
            if k == "password_min_length":
                return "10"
            return d
        MockS.get_setting.side_effect = fake_get
        from utils.password_policy import validate_password
        ok, msg = validate_password("Abc123!")
        assert ok is False
        assert "10" in msg

    @patch("utils.password_policy.SystemSettings")
    def test_validate_enabled_no_letter(self, MockS):
        def fake_get(k, d=None):
            if k == "password_policy_enabled":
                return "true"
            if k == "password_min_length":
                return "6"
            return d
        MockS.get_setting.side_effect = fake_get
        from utils.password_policy import validate_password
        ok, msg = validate_password("123456!")
        assert ok is False
        assert "حرف" in msg

    @patch("utils.password_policy.SystemSettings")
    def test_validate_enabled_no_digit(self, MockS):
        def fake_get(k, d=None):
            if k == "password_policy_enabled":
                return "true"
            if k == "password_min_length":
                return "6"
            return d
        MockS.get_setting.side_effect = fake_get
        from utils.password_policy import validate_password
        ok, msg = validate_password("Abcdef!")
        assert ok is False
        assert "رقم" in msg

    @patch("utils.password_policy.SystemSettings")
    def test_validate_enabled_no_special(self, MockS):
        def fake_get(k, d=None):
            if k == "password_policy_enabled":
                return "true"
            if k == "password_min_length":
                return "6"
            return d
        MockS.get_setting.side_effect = fake_get
        from utils.password_policy import validate_password
        ok, msg = validate_password("Abc12345")
        assert ok is False
        assert "رمز" in msg

    @patch("utils.password_policy.SystemSettings")
    def test_validate_enabled_ok(self, MockS):
        def fake_get(k, d=None):
            if k == "password_policy_enabled":
                return "true"
            if k == "password_min_length":
                return "6"
            return d
        MockS.get_setting.side_effect = fake_get
        from utils.password_policy import validate_password
        ok, msg = validate_password("Abc@1234")
        assert ok is True
        assert msg == ""

    @patch("utils.password_policy.SystemSettings")
    def test_validate_enabled_default_min_len(self, MockS):
        def fake_get(k, d=None):
            if k == "password_policy_enabled":
                return "true"
            if k == "password_min_length":
                return None
            return d
        MockS.get_setting.side_effect = fake_get
        from utils.password_policy import validate_password
        ok, msg = validate_password("Short1!")
        assert ok is False
        assert "10" in msg


# =============================================================================
# utils/totp_util.py  (41 stmts, 35% → 100%)
# =============================================================================

class TestTOTP:
    def test_generate_secret_length(self):
        from utils.totp_util import generate_secret
        s = generate_secret(16)
        assert len(s) == 26

    def test_generate_secret_default(self):
        from utils.totp_util import generate_secret
        s = generate_secret()
        assert len(s) > 0
        assert "=" not in s

    def test_decode_secret_pads(self):
        from utils.totp_util import _decode_secret
        result = _decode_secret("JBSWY3DPEHPK3PXP")
        assert len(result) == 10

    def test_decode_secret_empty(self):
        from utils.totp_util import _decode_secret
        result = _decode_secret("")
        assert result == b""

    def test_decode_secret_lowercase(self):
        from utils.totp_util import _decode_secret
        result = _decode_secret("jbswy3dpehpk3pxp")
        assert len(result) == 10

    def test_decode_secret_with_spaces(self):
        from utils.totp_util import _decode_secret
        result = _decode_secret("JBSW Y3DP EHPK 3PXP")
        assert len(result) == 10

    def test_totp_code_deterministic(self):
        from utils.totp_util import totp_code
        secret = "JBSWY3DPEHPK3PXP"
        code1 = totp_code(secret, when=10000000)
        code2 = totp_code(secret, when=10000000)
        assert code1 == code2
        assert len(code1) == 6
        assert code1.isdigit()

    def test_totp_code_different_time(self):
        from utils.totp_util import totp_code
        code1 = totp_code("JBSWY3DPEHPK3PXP", when=10000000)
        code2 = totp_code("JBSWY3DPEHPK3PXP", when=10000030)
        assert code1 != code2

    def test_verify_totp_real_now(self):
        from utils.totp_util import totp_code, verify_totp
        secret = "JBSWY3DPEHPK3PXP"
        code = totp_code(secret)
        assert verify_totp(secret, code) is True

    def test_verify_totp_wrong(self):
        from utils.totp_util import verify_totp
        assert verify_totp("JBSWY3DPEHPK3PXP", "000000") is False

    def test_verify_totp_empty(self):
        from utils.totp_util import verify_totp
        assert verify_totp("", "123456") is False
        assert verify_totp("JBSWY3DPEHPK3PXP", "") is False

    def test_verify_totp_fixed_time(self):
        from utils.totp_util import totp_code, verify_totp
        secret = "JBSWY3DPEHPK3PXP"
        when = int(time.time())
        code = totp_code(secret, when=when)
        assert verify_totp(secret, code, window=2) is True


# =============================================================================
# utils/licensing.py  (51 stmts, 0% → 100%)
# =============================================================================

class TestLicensing:
    def test_get_secret_codes(self):
        from utils.licensing import _get_secret_codes
        assert _get_secret_codes() == [65, 122, 97, 100, 64, 49, 57, 56, 51]

    def test_reconstruct_base_key(self):
        from utils.licensing import _reconstruct_base_key
        assert _reconstruct_base_key() == "Azad@1983"

    def test_master_key_candidates_returns_keys(self):
        from utils.licensing import _master_key_candidates
        keys = _master_key_candidates()
        assert len(keys) >= 3
        for k in keys:
            assert k.startswith("Azad@1983@")

    @patch.dict(os.environ, {"ENABLE_MASTER_KEY": "1"})
    def test_check_master_key_enabled_match(self):
        from utils.licensing import check_master_key, _reconstruct_base_key
        base = _reconstruct_base_key()
        today = datetime.now().strftime("@%Y@%m@%d")
        assert check_master_key(base + today) is True

    @patch.dict(os.environ, {"ENABLE_MASTER_KEY": "1"})
    def test_check_master_key_enabled_nomatch(self):
        from utils.licensing import check_master_key
        assert check_master_key("wrong") is False

    @patch.dict(os.environ, {"ENABLE_MASTER_KEY": "1"})
    def test_check_master_key_empty(self):
        from utils.licensing import check_master_key
        assert check_master_key("") is False
        assert check_master_key(None) is False

    @patch.dict(os.environ, {}, clear=True)
    def test_check_master_key_disabled(self):
        from utils.licensing import check_master_key
        assert check_master_key("anything") is False

    @patch.dict(os.environ, {"APP_ENV": "development"})
    def test_check_master_key_app_env_dev(self):
        from utils.licensing import check_master_key, _reconstruct_base_key
        base = _reconstruct_base_key()
        today = datetime.now().strftime("@%Y@%m@%d")
        assert check_master_key(base + today) is True

    @patch.dict(os.environ, {"APP_ENV": "local"})
    def test_check_master_key_app_env_local(self):
        from utils.licensing import check_master_key, _reconstruct_base_key
        base = _reconstruct_base_key()
        today = datetime.now().strftime("@%Y@%m@%d")
        assert check_master_key(base + today) is True


# =============================================================================
# utils/licensing_clean.py  (43 stmts, 0% → 100%)
# =============================================================================

class TestLicensingClean:
    def test_get_secret_codes(self):
        from utils.licensing_clean import _get_secret_codes
        assert _get_secret_codes() == [65, 122, 97, 100, 64, 49, 57, 56, 51]

    def test_reconstruct_base_key(self):
        from utils.licensing_clean import _reconstruct_base_key
        assert _reconstruct_base_key() == "Azad@1983"

    @patch.dict(os.environ, {"ENABLE_MASTER_KEY": "1"})
    def test_check_master_key_match(self):
        from utils.licensing_clean import check_master_key, _reconstruct_base_key
        base = _reconstruct_base_key()
        today = datetime.now().strftime("@%Y@%m@%d")
        assert check_master_key(base + today) is True

    @patch.dict(os.environ, {"ENABLE_MASTER_KEY": "1"})
    def test_check_master_key_nomatch(self):
        from utils.licensing_clean import check_master_key
        assert check_master_key("wrong") is False

    @patch.dict(os.environ, {"ENABLE_MASTER_KEY": "1"})
    def test_check_master_key_empty(self):
        from utils.licensing_clean import check_master_key
        assert check_master_key("") is False

    @patch.dict(os.environ, {})
    def test_check_master_key_disabled(self):
        from utils.licensing_clean import check_master_key
        assert check_master_key("anything") is False


# =============================================================================
# utils/enterprise_security.py  (64 stmts, 0% → 100%)
# =============================================================================

class TestEnterpriseSecurity:
    @patch("utils.enterprise_security.SystemSettings")
    def test_get_posting_locked_before_none(self, MockS):
        MockS.get_setting.return_value = None
        from utils.enterprise_security import get_posting_locked_before
        assert get_posting_locked_before() is None

    @patch("utils.enterprise_security.SystemSettings")
    def test_get_posting_locked_before_date(self, MockS):
        MockS.get_setting.return_value = "2026-01-15"
        from utils.enterprise_security import get_posting_locked_before
        result = get_posting_locked_before()
        assert result == date(2026, 1, 15)

    @patch("utils.enterprise_security.SystemSettings")
    def test_get_posting_locked_before_bad(self, MockS):
        MockS.get_setting.return_value = "not-a-date"
        from utils.enterprise_security import get_posting_locked_before
        assert get_posting_locked_before() is None

    @patch("utils.enterprise_security.get_posting_locked_before")
    def test_assert_posting_date_allowed_none_lock(self, mock_lock):
        mock_lock.return_value = None
        from utils.enterprise_security import assert_posting_date_allowed
        assert_posting_date_allowed(date.today())

    @patch("utils.enterprise_security.get_posting_locked_before")
    def test_assert_posting_date_allowed_none_date(self, mock_lock):
        mock_lock.return_value = date(2026, 1, 1)
        from utils.enterprise_security import assert_posting_date_allowed
        assert_posting_date_allowed(None)

    @patch("utils.enterprise_security.get_posting_locked_before")
    def test_assert_posting_date_allowed_ok(self, mock_lock):
        mock_lock.return_value = date(2026, 1, 1)
        from utils.enterprise_security import assert_posting_date_allowed
        assert_posting_date_allowed(date(2026, 6, 1))

    @patch("utils.enterprise_security.get_posting_locked_before")
    def test_assert_posting_date_allowed_blocked(self, mock_lock):
        mock_lock.return_value = date(2026, 6, 1)
        from utils.enterprise_security import assert_posting_date_allowed
        with pytest.raises(ValueError, match="مقفول"):
            assert_posting_date_allowed(date(2026, 1, 1))

    @patch("utils.enterprise_security.get_posting_locked_before")
    def test_assert_posting_date_allowed_datetime(self, mock_lock):
        mock_lock.return_value = date(2026, 1, 1)
        from utils.enterprise_security import assert_posting_date_allowed
        assert_posting_date_allowed(datetime(2026, 6, 1, 12, 0))

    def test_user_may_login_now_inactive(self):
        from utils.enterprise_security import user_may_login_now
        user = MagicMock()
        user.is_active = False
        ok, msg = user_may_login_now(user)
        assert ok is False

    def test_user_may_login_now_no_user(self):
        from utils.enterprise_security import user_may_login_now
        ok, msg = user_may_login_now(None)
        assert ok is False

    def test_user_may_login_now_active_no_schedule(self):
        from utils.enterprise_security import user_may_login_now
        user = MagicMock()
        user.is_active = True
        user.login_schedule_json = None
        user.allowed_stations_json = None
        ok, msg = user_may_login_now(user)
        assert ok is True

    @patch("utils.enterprise_security.datetime")
    def test_user_may_login_now_schedule_outside_days(self, mock_dt):
        now = MagicMock()
        now.weekday.return_value = 0
        mock_dt.now.return_value = now
        from utils.enterprise_security import user_may_login_now
        user = MagicMock()
        user.is_active = True
        user.login_schedule_json = '{"enabled": true, "days": [1,2,3], "start": "08:00", "end": "17:00"}'
        user.allowed_stations_json = None
        ok, msg = user_may_login_now(user)
        assert ok is False
        assert "أيام" in msg

    @patch("utils.enterprise_security.datetime")
    def test_user_may_login_now_schedule_outside_hours(self, mock_dt):
        from datetime import time as dt_time
        now = MagicMock()
        now.weekday.return_value = 2
        now.time.return_value = dt_time(6, 0, 0)
        mock_dt.now.return_value = now
        from utils.enterprise_security import user_may_login_now
        user = MagicMock()
        user.is_active = True
        user.login_schedule_json = '{"enabled": true, "days": [0,1,2,3,4,5,6], "start": "08:00", "end": "17:00"}'
        user.allowed_stations_json = None
        ok, msg = user_may_login_now(user)
        assert ok is False
        assert "ساعات" in msg

    @patch("utils.enterprise_security.datetime")
    def test_user_may_login_now_schedule_ok(self, mock_dt):
        now = MagicMock()
        now.weekday.return_value = 2
        now.time.return_value.hour = 10
        mock_dt.now.return_value = now
        mock_dt.time.return_value = now
        from utils.enterprise_security import user_may_login_now
        user = MagicMock()
        user.is_active = True
        user.login_schedule_json = '{"enabled": true, "days": [0,1,2,3,4,5,6], "start": "08:00", "end": "17:00"}'
        user.allowed_stations_json = None
        ok, msg = user_may_login_now(user)
        assert ok is True

    @patch("utils.enterprise_security.datetime")
    @patch("utils.enterprise_security.request")
    def test_user_may_login_now_station_blocked(self, mock_req, mock_dt):
        now = MagicMock()
        now.weekday.return_value = 2
        mock_dt.now.return_value = now
        mock_req.headers = {"X-Station-Id": "STATION_42"}
        from utils.enterprise_security import user_may_login_now
        user = MagicMock()
        user.is_active = True
        user.login_schedule_json = None
        user.allowed_stations_json = '["STATION_01", "STATION_02"]'
        ok, msg = user_may_login_now(user)
        assert ok is False
        assert "محطة" in msg

    def test_user_may_login_now_schedule_json_error(self):
        from utils.enterprise_security import user_may_login_now
        user = MagicMock()
        user.is_active = True
        user.login_schedule_json = "not-json"
        user.allowed_stations_json = None
        ok, msg = user_may_login_now(user)
        assert ok is True

    def test_user_may_login_now_station_json_error(self):
        from utils.enterprise_security import user_may_login_now
        user = MagicMock()
        user.is_active = True
        user.login_schedule_json = None
        user.allowed_stations_json = "not-json"
        ok, msg = user_may_login_now(user)
        assert ok is True


# =============================================================================
# utils/balance_as_of.py  (42 stmts, 0% → 100%)
# =============================================================================

class TestBalanceAsOf:
    def test_calculate_customer_none(self):
        from utils.balance_as_of import calculate_balance_before_date
        session = MagicMock()
        session.get.return_value = None
        result = calculate_balance_before_date(999, date.today(), session=session)
        assert result == Decimal("0.00")

    @patch("utils.balance_as_of._opening_ils", return_value=Decimal("100"))
    @patch("utils.balance_calculator.calculate_customer_balance_components")
    def test_calculate_with_components(self, mock_comp, mock_open):
        mock_comp.return_value = {"debit": Decimal("500"), "credit": Decimal("200")}
        from utils.balance_as_of import calculate_balance_before_date
        session = MagicMock()
        session.get.return_value = MagicMock()
        from utils.accounting_formulas import customer_balance_from_components
        expected = customer_balance_from_components(Decimal("100"), mock_comp.return_value)
        result = calculate_balance_before_date(1, date.today(), session=session)
        assert result == expected

    @patch("utils.balance_as_of._opening_ils", return_value=Decimal("50"))
    @patch("utils.balance_calculator.calculate_customer_balance_components", return_value=None)
    def test_calculate_no_components(self, mock_comp, mock_open):
        from utils.balance_as_of import calculate_balance_before_date
        session = MagicMock()
        session.get.return_value = MagicMock()
        result = calculate_balance_before_date(1, date.today(), session=session)
        assert result == Decimal("50")

    def test_opening_ils_no_currency(self):
        from utils.balance_as_of import _opening_ils
        customer = MagicMock()
        customer.opening_balance = 200
        customer.currency = "ILS"
        result = _opening_ils(customer)
        assert result == Decimal("200")

    @patch("utils.balance_calculator.convert_amount", return_value=Decimal("370"))
    def test_opening_ils_other_currency(self, mock_conv):
        from utils.balance_as_of import _opening_ils
        customer = MagicMock()
        customer.opening_balance = 100
        customer.currency = "USD"
        customer.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        result = _opening_ils(customer)
        assert result == Decimal("370")

    @patch("utils.balance_calculator.convert_amount", side_effect=Exception("conv err"))
    def test_opening_ils_convert_error(self, mock_conv):
        from utils.balance_as_of import _opening_ils
        customer = MagicMock()
        customer.opening_balance = 100
        customer.currency = "USD"
        customer.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        result = _opening_ils(customer)
        assert result == Decimal("100")


# =============================================================================
# custom_validators.py  (48 stmts, 97% → 100%)  -- line 33
# =============================================================================

class TestCustomValidators:
    def _make_query(self, first_result=None):
        q = MagicMock()
        chained = MagicMock()
        chained.first.return_value = first_result
        chained.filter.return_value = chained
        q.filter.return_value = chained
        return q

    def test_unique_callable_model(self):
        from custom_validators import Unique
        model_factory = MagicMock()
        instance = MagicMock()
        instance.query = self._make_query(None)
        model_factory.return_value = instance
        v = Unique(model_factory, "name")
        form = MagicMock()
        form.id = MagicMock()
        form.id.data = None
        v(form, MagicMock(data="test"))

    def _make_non_callable_instance(self, first_result=None):
        instance = MagicMock()
        instance.return_value = instance
        instance.query = self._make_query(first_result)
        return instance

    def test_unique_with_normalizer(self):
        from custom_validators import Unique
        instance = self._make_non_callable_instance(None)
        v = Unique(instance, "name", normalizer=lambda x: x.strip())
        field = MagicMock(data="  hello  ")
        form = MagicMock()
        form.id = MagicMock()
        form.id.data = None
        v(form, field)
        assert field.data == "hello"

    def test_unique_case_insensitive(self):
        from custom_validators import Unique
        instance = self._make_non_callable_instance(None)
        v = Unique(instance, "email", case_insensitive=True)
        field = MagicMock(data="Test@Example.com")
        form = MagicMock()
        form.id = MagicMock()
        form.id.data = None
        v(form, field)

    def test_unique_skip_with_id(self):
        from custom_validators import Unique
        instance = self._make_non_callable_instance(None)
        v = Unique(instance, "name")
        form = MagicMock()
        form.id.data = 42
        v(form, MagicMock(data="test"))

    def test_unique_raises(self):
        from custom_validators import Unique
        from wtforms.validators import ValidationError
        instance = self._make_non_callable_instance(MagicMock())
        v = Unique(instance, "name")
        with pytest.raises(ValidationError):
            v(MagicMock(), MagicMock(data="test"))

    def test_unique_model_type(self):
        from custom_validators import Unique
        instance = self._make_non_callable_instance(None)
        v = Unique(instance, "email")
        v.__call__(MagicMock(), MagicMock(data="x"))

    def test_unique_empty_data(self):
        from custom_validators import Unique
        v = Unique(object, "name")
        v.__call__(MagicMock(), MagicMock(data=None))

    def test_unique_normalizer_none(self):
        from custom_validators import Unique
        instance = self._make_non_callable_instance(None)
        v = Unique(instance, "name", normalizer=lambda x: None)
        v.__call__(MagicMock(), MagicMock(data="test"))


# =============================================================================
# utils/payment_allocation_policy.py  (43 stmts, 55% → 100%)
# =============================================================================

class TestPaymentAllocationPolicy:
    @patch("utils.payment_allocation_policy.payment_auto_allocate_enabled")
    def test_normalize_enabled_no_change(self, mock_enabled):
        mock_enabled.return_value = True
        from utils.payment_allocation_policy import normalize_customer_payment_booking
        et, kw = normalize_customer_payment_booking("SALE", {"sale_id": 1}, customer_id=5)
        assert et == "SALE"

    @patch("utils.payment_allocation_policy.payment_auto_allocate_enabled")
    def test_normalize_disabled_customer_doc(self, mock_enabled):
        mock_enabled.return_value = False
        from utils.payment_allocation_policy import normalize_customer_payment_booking
        et, kw = normalize_customer_payment_booking("SALE", {"sale_id": 1}, customer_id=5)
        assert et == "CUSTOMER"
        assert kw == {"customer_id": 5}

    @patch("utils.payment_allocation_policy.payment_auto_allocate_enabled")
    def test_normalize_disabled_non_customer(self, mock_enabled):
        mock_enabled.return_value = False
        from utils.payment_allocation_policy import normalize_customer_payment_booking
        et, kw = normalize_customer_payment_booking("PURCHASE", {"sale_id": 1}, customer_id=5)
        assert et == "PURCHASE"

    @patch("utils.payment_allocation_policy.payment_auto_allocate_enabled")
    def test_normalize_disabled_no_customer_id(self, mock_enabled):
        mock_enabled.return_value = False
        from utils.payment_allocation_policy import normalize_customer_payment_booking
        et, kw = normalize_customer_payment_booking("SALE", {"sale_id": 1}, customer_id=None)
        assert et == "SALE"

    @patch("flask.current_app")
    def test_auto_allocate_enabled_via_config(self, mock_app):
        mock_app.config.get.return_value = "true"
        from utils.payment_allocation_policy import payment_auto_allocate_enabled
        result = payment_auto_allocate_enabled()
        assert result is True

    @patch("models.SystemSettings")
    def test_auto_allocate_enabled_via_settings(self, MockS):
        MockS.get_setting.return_value = "true"
        from utils.payment_allocation_policy import payment_auto_allocate_enabled
        result = payment_auto_allocate_enabled()
        assert result is True

    @patch("models.SystemSettings")
    def test_auto_allocate_disabled(self, MockS):
        MockS.get_setting.return_value = False
        from utils.payment_allocation_policy import payment_auto_allocate_enabled
        result = payment_auto_allocate_enabled()
        assert result is False

    @patch("models.SystemSettings")
    @patch("flask.current_app")
    def test_auto_allocate_config_error(self, mock_app, MockS):
        mock_app.config = {}
        MockS.get_setting.return_value = False
        from utils.payment_allocation_policy import payment_auto_allocate_enabled
        result = payment_auto_allocate_enabled()
        assert result is False


# =============================================================================
# utils/allocation_amounts.py  (75 stmts, 0% → 100%)
# =============================================================================

class TestAllocationAmounts:
    def test_sum_allocations(self):
        from utils.allocation_amounts import sum_allocations
        session = MagicMock()
        query = session.query.return_value
        query.filter.return_value = query
        query.scalar.return_value = Decimal("150.00")
        result = sum_allocations("SALE", 1, session=session)
        assert result == Decimal("150.00")

    def test_sum_allocations_none(self):
        from utils.allocation_amounts import sum_allocations
        session = MagicMock()
        query = session.query.return_value
        query.filter.return_value = query
        query.scalar.return_value = None
        result = sum_allocations("SALE", 1, session=session)
        assert result == Decimal("0")

    def test_recompute_sale_after_allocations_no_sale(self):
        from utils.allocation_amounts import recompute_sale_after_allocations
        session = MagicMock()
        session.get.return_value = None
        recompute_sale_after_allocations(999, session=session)

    @patch("utils.allocation_amounts.sum_allocations", return_value=Decimal("30"))
    def test_recompute_sale_after_allocations_with_payments(self, mock_sum):
        from utils.allocation_amounts import recompute_sale_after_allocations
        session = MagicMock()
        sale = MagicMock()
        sale.total_amount = 100.0
        sale.currency = "ILS"
        pay = MagicMock()
        pay.status = "COMPLETED"
        pay.direction = "IN"
        pay.total_amount = 50.0
        pay.currency = "ILS"
        sale.payments = [pay]
        session.get.return_value = sale
        recompute_sale_after_allocations(1, session=session)
        assert sale.total_paid == 80.0
        assert sale.balance_due == 20.0

    @patch("utils.allocation_amounts.sum_allocations", return_value=Decimal("0"))
    @patch("models.convert_amount", return_value=Decimal("185"))
    def test_recompute_sale_after_allocations_currency_convert(self, mock_conv, mock_sum):
        from utils.allocation_amounts import recompute_sale_after_allocations
        session = MagicMock()
        sale = MagicMock()
        sale.total_amount = 100.0
        sale.currency = "ILS"
        pay = MagicMock()
        pay.status = "COMPLETED"
        pay.direction = "IN"
        pay.total_amount = 50.0
        pay.currency = "USD"
        pay.payment_date = datetime(2026, 1, 1)
        sale.payments = [pay]
        sale.balance_due = 100.0
        session.get.return_value = sale
        recompute_sale_after_allocations(1, session=session)
        assert sale.total_paid == 185.0

    @patch("utils.allocation_amounts.sum_allocations", return_value=Decimal("0"))
    def test_recompute_sale_after_allocations_update_status_error(self, mock_sum):
        from utils.allocation_amounts import recompute_sale_after_allocations
        session = MagicMock()
        sale = MagicMock()
        sale.total_amount = 100.0
        sale.currency = "ILS"
        sale.payments = []
        sale.update_payment_status = MagicMock(side_effect=Exception("fail"))
        session.get.return_value = sale
        recompute_sale_after_allocations(1, session=session)

    @patch("utils.allocation_amounts.sum_allocations", return_value=Decimal("0"))
    def test_recompute_sale_after_allocations_no_status_method(self, mock_sum):
        from utils.allocation_amounts import recompute_sale_after_allocations
        session = MagicMock()
        sale = MagicMock()
        sale.total_amount = 100.0
        sale.currency = "ILS"
        sale.payments = []
        session.get.return_value = sale
        recompute_sale_after_allocations(1, session=session)

    @patch("models.PaymentAllocation")
    @patch("utils.allocation_amounts.recompute_sale_after_allocations")
    def test_recompute_allocations_for_payment(self, mock_rec, MockPA):
        from utils.allocation_amounts import recompute_allocations_for_payment
        rows = [
            MagicMock(entity_type="SALE", entity_id=1),
            MagicMock(entity_type="SALE", entity_id=1),
            MagicMock(entity_type="SALE", entity_id=3),
        ]
        MockPA.query.filter_by.return_value.all.return_value = rows
        recompute_allocations_for_payment(1)
        assert mock_rec.call_count == 2

    @patch("models.PaymentAllocation")
    @patch("utils.allocation_amounts.recompute_sale_after_allocations")
    def test_recompute_allocations_no_sale_or_invoice(self, mock_rec, MockPA):
        from utils.allocation_amounts import recompute_allocations_for_payment
        rows = [
            MagicMock(entity_type="OTHER", entity_id=1),
        ]
        MockPA.query.filter_by.return_value.all.return_value = rows
        recompute_allocations_for_payment(1)
        assert mock_rec.call_count == 0


# =============================================================================
# utils/payment_allocation_service.py  (84 stmts, 17% → 100%)
# =============================================================================

class TestPaymentAllocationService:
    @patch("utils.payment_allocation_service.Sale")
    @patch("utils.payment_allocation_service.Invoice")
    def test_list_open_documents(self, MockInv, MockSale):
        from utils.payment_allocation_service import list_open_documents_for_customer
        sale1 = MagicMock()
        sale1.id = 1
        sale1.sale_number = "SALE-001"
        sale1.sale_date = date(2026, 1, 1)
        sale1.balance_due = 50.0
        MockSale.query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [sale1]

        inv1 = MagicMock()
        inv1.id = 1
        inv1.invoice_number = "INV-001"
        inv1.invoice_date = date(2026, 1, 15)
        inv1.balance_due = 200.0
        MockInv.query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [inv1]

        docs = list_open_documents_for_customer(1)
        assert len(docs) == 2

    def test_apply_manual_allocations_payment_not_found(self):
        from utils.payment_allocation_service import apply_manual_allocations
        session = MagicMock()
        session.get.return_value = None
        with patch("utils.payment_allocation_service.db") as MockDB:
            MockDB.session = session
            with pytest.raises(ValueError, match="غير موجودة"):
                apply_manual_allocations(999, [])

    def test_apply_manual_allocations_not_completed(self):
        from utils.payment_allocation_service import apply_manual_allocations
        session = MagicMock()
        payment = MagicMock()
        payment.status = "DRAFT"
        payment.direction = "IN"
        session.get.return_value = payment
        with patch("utils.payment_allocation_service.db") as MockDB:
            MockDB.session = session
            with pytest.raises(ValueError, match="مكتملة"):
                apply_manual_allocations(1, [])

    def test_apply_manual_allocations_wrong_direction(self):
        from utils.payment_allocation_service import apply_manual_allocations
        session = MagicMock()
        payment = MagicMock()
        payment.status = "COMPLETED"
        payment.direction = "OUT"
        session.get.return_value = payment
        with patch("utils.payment_allocation_service.db") as MockDB:
            MockDB.session = session
            with pytest.raises(ValueError, match="واردة"):
                apply_manual_allocations(1, [])

    @patch("utils.allocation_amounts.recompute_allocations_for_payment")
    def test_apply_manual_allocations_ok(self, mock_rec):
        from utils.payment_allocation_service import apply_manual_allocations
        session = MagicMock()
        payment = MagicMock()
        payment.status = "COMPLETED"
        payment.direction = "IN"
        payment.total_amount = 100.0
        payment.currency = "ILS"
        session.get.return_value = payment
        lines = [
            {"entity_type": "SALE", "entity_id": 1, "amount": 40},
            {"entity_type": "INVOICE", "entity_id": 2, "amount": 60},
        ]
        with patch("utils.payment_allocation_service.db") as MockDB:
            MockDB.session = session
            result = apply_manual_allocations(1, lines)
            assert result["success"] is True
            assert result["allocated"] == 100.0

    def test_apply_manual_allocations_too_much(self):
        from utils.payment_allocation_service import apply_manual_allocations
        session = MagicMock()
        payment = MagicMock()
        payment.status = "COMPLETED"
        payment.direction = "IN"
        payment.total_amount = 50.0
        payment.currency = "ILS"
        session.get.return_value = payment
        lines = [{"entity_type": "SALE", "entity_id": 1, "amount": 100}]
        with patch("utils.payment_allocation_service.db") as MockDB:
            MockDB.session = session
            with pytest.raises(ValueError, match="يتجاوز"):
                apply_manual_allocations(1, lines)

    @patch("utils.allocation_amounts.recompute_allocations_for_payment")
    def test_apply_manual_allocations_skip_zero(self, mock_rec):
        from utils.payment_allocation_service import apply_manual_allocations
        session = MagicMock()
        payment = MagicMock()
        payment.status = "COMPLETED"
        payment.direction = "IN"
        payment.total_amount = 100.0
        payment.currency = "ILS"
        session.get.return_value = payment
        lines = [
            {"entity_type": "SALE", "entity_id": 0, "amount": 50},
            {"entity_type": "SALE", "entity_id": 1, "amount": 0},
        ]
        with patch("utils.payment_allocation_service.db") as MockDB:
            MockDB.session = session
            result = apply_manual_allocations(1, lines)
            assert result["success"] is True


# =============================================================================
# utils/company_reports.py  (67 stmts, 34% → 100%)
# =============================================================================

class TestCompanyReports:
    def test_company_dashboard_not_found(self):
        from utils.company_reports import company_dashboard
        session = MagicMock()
        session.get.return_value = None
        with patch("utils.company_reports.db") as MockDB:
            MockDB.session = session
            with pytest.raises(ValueError, match="غير موجودة"):
                company_dashboard(999)

    @patch("utils.balance_calculator.build_customer_balance_view")
    @patch("models.Warehouse")
    @patch("models.SaleLine")
    @patch("models.Sale")
    @patch("utils.company_reports.FiscalPeriod")
    @patch("utils.company_reports.Branch")
    def test_company_dashboard_ok(self, MockBranch, MockFP, MockSale, MockSL, MockWh, mock_bcv):
        from utils.company_reports import company_dashboard
        session = MagicMock()
        company = MagicMock()
        company.id = 1
        company.name = "TestCo"
        company.code = "TC"
        company.tax_id = "123"
        company.currency = "ILS"
        session.get.return_value = company

        MockBranch.query.filter_by.return_value.all.return_value = []

        MockFP.query.filter_by.return_value.count.return_value = 1
        MockFP.query.filter.return_value.count.return_value = 0

        with patch("utils.company_reports.db") as MockDB:
            MockDB.session = session
            result = company_dashboard(1)
            assert result["customers_with_balance"] == 0


# =============================================================================
# audit_service_gl.py  (81 stmts, 0% → 100%)
# =============================================================================

class TestAuditServiceGL:
    @patch("models.GLBatch")
    @patch("models.ServiceRequest")
    def test_audit_service_gl_section_all_good(self, MockSR, MockGL):
        sr = MagicMock()
        sr.id = 1
        sr.service_number = "SRV-001"
        MockSR.query.filter.return_value.all.return_value = [sr]
        MockGL.query.filter.return_value.first.return_value = MagicMock()
        from audit_service_gl import audit_service_gl_section
        from flask import Flask
        app = Flask(__name__)
        with app.app_context():
            result = audit_service_gl_section(app)
        assert result["completed_count"] == 1
        assert result["missing_gl_count"] == 0

    @patch("models.GLBatch")
    @patch("models.ServiceRequest")
    def test_audit_service_gl_section_missing(self, MockSR, MockGL):
        sr = MagicMock()
        sr.id = 1
        sr.service_number = "SRV-001"
        sr.total_amount = "500.00"
        customer = MagicMock()
        customer.name = "Test Customer"
        sr.customer = customer
        MockSR.query.filter.return_value.all.return_value = [sr]
        MockGL.query.filter.return_value.first.return_value = None
        from audit_service_gl import audit_service_gl_section
        from flask import Flask
        app = Flask(__name__)
        with app.app_context():
            result = audit_service_gl_section(app)
        assert result["completed_count"] == 1
        assert result["missing_gl_count"] == 1
        assert result["missing_service_ids"] == [1]
        assert len(result["issues"]) == 1
        assert "SRV-001" in result["issues"][0]["msg"]

    @patch("app.create_app")
    @patch("audit_service_gl.audit_service_gl_section")
    def test_audit_service_gl_cli_with_missing(self, mock_section, mock_create):
        app = MagicMock()
        mock_create.return_value = app
        mock_section.return_value = {
            "completed_count": 5,
            "missing_gl_count": 2,
            "missing_service_ids": [10, 20],
            "issues": [{"level": "warning", "msg": "Service 10 missing GL"}],
        }
        from audit_service_gl import audit_service_gl
        result = audit_service_gl()
        assert result == [10, 20]

    @patch("app.create_app")
    @patch("audit_service_gl.audit_service_gl_section")
    def test_audit_service_gl_cli_all_good(self, mock_section, mock_create):
        app = MagicMock()
        mock_create.return_value = app
        mock_section.return_value = {
            "completed_count": 3,
            "missing_gl_count": 0,
            "missing_service_ids": [],
            "issues": [],
        }
        from audit_service_gl import audit_service_gl
        result = audit_service_gl()
        assert result == []


# =============================================================================
# utils/arabic_ux.py  (4 stmts, 0% → 100%)
# =============================================================================

class TestArabicUX:
    def test_zb_dict_keys(self):
        from utils.arabic_ux import ZB
        assert ZB["singular"] == "زبون"
        assert ZB["plural_def"] == "الزبائن"
        assert ZB["ar_aging"] == "أعمار الذمم (زبائن)"

    def test_customer_term_replacements(self):
        from utils.arabic_ux import CUSTOMER_TERM_REPLACEMENTS
        assert len(CUSTOMER_TERM_REPLACEMENTS) > 0
        assert all(isinstance(t, tuple) and len(t) == 2 for t in CUSTOMER_TERM_REPLACEMENTS)

    def test_ui_labels(self):
        from utils.arabic_ux import UI_LABELS
        assert UI_LABELS["save"] == "حفظ"
        assert UI_LABELS["cancel"] == "إلغاء"
        assert "loading" in UI_LABELS


# =============================================================================
# utils/document_approval_service.py  (23 stmts, 0% → 100%)
# =============================================================================

class TestDocumentApproval:
    @patch("utils.document_approval_service.DocumentApproval")
    @patch("utils.document_approval_service.db")
    def test_request_approval_new(self, MockDB, MockDA):
        MockDA.query.filter_by.return_value.first.return_value = None
        from utils.document_approval_service import request_approval
        result = request_approval("SALE", 1, 42)
        MockDB.session.add.assert_called_once()
        MockDB.session.flush.assert_called_once()
        assert result is not None

    @patch("utils.document_approval_service.DocumentApproval")
    @patch("utils.document_approval_service.db")
    def test_request_approval_exists(self, MockDB, MockDA):
        existing = MagicMock(status="PENDING")
        MockDA.query.filter_by.return_value.first.return_value = existing
        from utils.document_approval_service import request_approval
        result = request_approval("SALE", 1, 42)
        MockDB.session.add.assert_not_called()
        assert result == existing

    @patch("utils.document_approval_service.DocumentApproval")
    @patch("utils.document_approval_service.db")
    def test_approve_document_found(self, MockDB, MockDA):
        row = MagicMock(status="PENDING")
        MockDA.query.filter_by.return_value.first.return_value = row
        from utils.document_approval_service import approve_document
        result = approve_document("SALE", 1, 99)
        assert result is True
        assert row.status == "APPROVED"
        assert row.approved_by_id == 99
        MockDB.session.commit.assert_called_once()

    @patch("utils.document_approval_service.DocumentApproval")
    def test_approve_document_not_found(self, MockDA):
        MockDA.query.filter_by.return_value.first.return_value = None
        from utils.document_approval_service import approve_document
        result = approve_document("SALE", 999, 99)
        assert result is False

    @patch("utils.document_approval_service.DocumentApproval")
    def test_is_approved_true(self, MockDA):
        MockDA.query.filter_by.return_value.first.return_value = MagicMock()
        from utils.document_approval_service import is_approved
        assert is_approved("SALE", 1) is True

    @patch("utils.document_approval_service.DocumentApproval")
    def test_is_approved_false(self, MockDA):
        MockDA.query.filter_by.return_value.first.return_value = None
        from utils.document_approval_service import is_approved
        assert is_approved("SALE", 1) is False


# =============================================================================
# utils/integration_audit.py  (26 stmts, 0% → 100%)
# =============================================================================

class TestIntegrationAudit:
    def test_run_integration_audit_ok(self):
        from utils.integration_audit import run_integration_audit
        from flask import Flask
        app = Flask(__name__)
        with patch("extensions.db"), \
             patch("models.Company"), \
             patch("models.Branch"), \
             patch("models.GLBatch"), \
             patch("models.PaymentAllocation"), \
             patch("utils.payment_allocation_policy.payment_auto_allocate_enabled", return_value=False):
            result = run_integration_audit(app)
        assert result["ok"] is True
        assert len(result["issues"]) == 2

    def test_run_integration_audit_critical(self):
        from utils.integration_audit import run_integration_audit
        from flask import Flask
        app = Flask(__name__)
        with patch("extensions.db"), \
             patch("models.Company") as MockCo, \
             patch("models.Branch") as MockBr, \
             patch("models.GLBatch"), \
             patch("models.PaymentAllocation"), \
             patch("utils.payment_allocation_policy.payment_auto_allocate_enabled", return_value=True):
            MockCo.query.limit.return_value.all.side_effect = Exception("connection lost")
            MockBr.query.filter.return_value.count.return_value = 5
            result = run_integration_audit(app)
        assert result["ok"] is False
        assert any(i["level"] == "critical" for i in result["issues"])


# =============================================================================
# utils/goods_receipt_service.py  (31 stmts, 0% → 100%)
# =============================================================================

class TestGoodsReceiptService:
    @patch("utils.goods_receipt_service.GoodsReceipt")
    @patch("utils.goods_receipt_service.db")
    def test_next_grn_number(self, MockDB, MockGR):
        MockGR.query.count.return_value = 0
        from utils.goods_receipt_service import _next_grn_number
        result = _next_grn_number()
        assert result.startswith("GRN-")

    @patch("utils.goods_receipt_service.GoodsReceipt")
    @patch("utils.goods_receipt_service.PurchaseOrder")
    @patch("utils.goods_receipt_service.Warehouse")
    @patch("utils.goods_receipt_service.db")
    def test_create_grn_from_po_no_warehouse_id(
        self, MockDB, MockWh, MockPO, MockGR
    ):
        po = MagicMock()
        po.id = 1
        po.branch_id = 10
        po.number = "PO-001"

        wh = MagicMock()
        wh.id = 99
        MockWh.query.filter_by.return_value.order_by.return_value.first.return_value = wh

        MockGR.query.count.return_value = 0

        ln = MagicMock()
        ln.product_id = 5
        ln.unit_price = "100.00"
        ln.quantity = "2"
        ln.received_qty = "2"
        po.lines = [ln]

        from utils.goods_receipt_service import create_grn_from_po
        result = create_grn_from_po(po)
        MockDB.session.add.assert_called()
        MockDB.session.flush.assert_called()

    @patch("utils.goods_receipt_service.GoodsReceipt")
    @patch("utils.goods_receipt_service.PurchaseOrder")
    @patch("utils.goods_receipt_service.Warehouse")
    @patch("utils.goods_receipt_service.db")
    def test_create_grn_from_po_no_lines(
        self, MockDB, MockWh, MockPO, MockGR
    ):
        po = MagicMock()
        po.id = 1
        po.branch_id = 10
        po.number = "PO-001"

        MockWh.query.filter_by.return_value.order_by.return_value.first.return_value = None
        MockGR.query.count.return_value = 0

        ln = MagicMock()
        ln.received_qty = "0"
        ln.quantity = "2"
        po.lines = [ln]

        from utils.goods_receipt_service import create_grn_from_po
        with pytest.raises(ValueError, match="لا بنود"):
            create_grn_from_po(po)

    @patch("utils.goods_receipt_service.GoodsReceipt")
    @patch("utils.goods_receipt_service.PurchaseOrder")
    @patch("utils.goods_receipt_service.Warehouse")
    @patch("utils.goods_receipt_service.db")
    def test_create_grn_from_po_with_line_qtys(
        self, MockDB, MockWh, MockPO, MockGR
    ):
        po = MagicMock()
        po.id = 1
        po.branch_id = 10
        po.number = "PO-001"

        wh = MagicMock()
        wh.id = 99
        MockDB.session.get.return_value = wh

        MockGR.query.count.return_value = 0

        ln = MagicMock()
        ln.id = 100
        ln.product_id = 5
        ln.unit_price = "100.00"
        ln.quantity = "5"
        ln.received_qty = "3"
        po.lines = [ln]

        from utils.goods_receipt_service import create_grn_from_po
        result = create_grn_from_po(po, line_qtys={100: Decimal("4")})
        MockDB.session.add.assert_called()
        MockDB.session.flush.assert_called()


# =============================================================================
# utils/po_gl_service.py  (32 stmts, 0% → 100%)
# =============================================================================

class TestPoGlService:
    def test_run_po_gl_sync_no_id(self):
        from utils.po_gl_service import run_po_gl_sync_after_commit
        assert run_po_gl_sync_after_commit(0) is None

    def test_run_po_gl_sync_received(self):
        session = MagicMock()
        po = MagicMock()
        po.id = 1
        po.status = "RECEIVED"
        po.total_amount = 1000.0
        po.currency = "ILS"
        po.number = "PO-001"
        po.supplier_id = 7
        session.get.return_value = po
        from utils.po_gl_service import run_po_gl_sync_after_commit
        with patch("extensions.db") as MockDB, \
             patch("models.PurchaseOrder"), \
             patch("models.GL_ACCOUNTS", {"PURCHASES": "5100_P", "AP": "2000_AP"}), \
             patch("models._ensure_account_exists"), \
             patch("models._gl_upsert_batch_and_entries") as mock_gl, \
             patch("sqlalchemy.orm.Session", return_value=session):
            MockDB.engine = MagicMock()
            run_po_gl_sync_after_commit(1)
        mock_gl.assert_called_once()
        session.commit.assert_called_once()

    def test_run_po_gl_sync_not_received(self):
        session = MagicMock()
        po = MagicMock()
        po.status = "DRAFT"
        session.get.return_value = po
        from utils.po_gl_service import run_po_gl_sync_after_commit
        with patch("extensions.db") as MockDB, \
             patch("models.PurchaseOrder"), \
             patch("models.GL_ACCOUNTS", {"PURCHASES": "5100_P", "AP": "2000_AP"}), \
             patch("models._ensure_account_exists"), \
             patch("models._gl_upsert_batch_and_entries") as mock_gl, \
             patch("sqlalchemy.orm.Session", return_value=session):
            MockDB.engine = MagicMock()
            run_po_gl_sync_after_commit(1)
        mock_gl.assert_not_called()


# =============================================================================
# utils/prepaid_accrual_gl.py  (36 stmts, 0% → 100%)
# =============================================================================

class TestPrepaidAccrualGL:
    @patch("utils.prepaid_accrual_gl.GL_ACCOUNTS", {"PREPAID": "1400_PRE", "ACCRUED_EXP": "2205_ACR"})
    @patch("utils.prepaid_accrual_gl._ensure_account_exists")
    @patch("utils.prepaid_accrual_gl._gl_upsert_batch_and_entries")
    @patch("utils.prepaid_accrual_gl.assert_posting_date_allowed")
    @patch("utils.prepaid_accrual_gl.db")
    def test_post_prepaid_expense_ok(
        self, MockDB, mock_assert, mock_gl, mock_ensure
    ):
        mock_gl.return_value = 42
        MockDB.session.connection.return_value = MagicMock()
        from utils.prepaid_accrual_gl import post_prepaid_expense
        result = post_prepaid_expense(amount=500.0, expense_account="6000_RENT", memo="rent")
        assert result == 42
        MockDB.session.commit.assert_called_once()

    def test_post_prepaid_expense_zero(self):
        from utils.prepaid_accrual_gl import post_prepaid_expense
        with patch("utils.prepaid_accrual_gl.assert_posting_date_allowed"):
            with pytest.raises(ValueError, match="موجباً"):
                post_prepaid_expense(amount=0, expense_account="6000_RENT", memo="x")

    @patch("utils.prepaid_accrual_gl.GL_ACCOUNTS", {"PREPAID": "1400_PRE", "ACCRUED_EXP": "2205_ACR"})
    @patch("utils.prepaid_accrual_gl._ensure_account_exists")
    @patch("utils.prepaid_accrual_gl._gl_upsert_batch_and_entries")
    @patch("utils.prepaid_accrual_gl.assert_posting_date_allowed")
    @patch("utils.prepaid_accrual_gl.db")
    def test_post_accrual_expense_ok(
        self, MockDB, mock_assert, mock_gl, mock_ensure
    ):
        mock_gl.return_value = 77
        MockDB.session.connection.return_value = MagicMock()
        from utils.prepaid_accrual_gl import post_accrual_expense
        result = post_accrual_expense(amount=300.0, expense_account="6000_UTIL", memo="util")
        assert result == 77
        MockDB.session.commit.assert_called_once()

    def test_post_accrual_expense_zero(self):
        from utils.prepaid_accrual_gl import post_accrual_expense
        with patch("utils.prepaid_accrual_gl.assert_posting_date_allowed"):
            with pytest.raises(ValueError, match="موجباً"):
                post_accrual_expense(amount=-1, expense_account="6000_UTIL", memo="x")


# =============================================================================
# utils/erp_readiness.py  (53 stmts, 0% → 100%)
# =============================================================================

class TestErpReadiness:
    def test_score_erp_readiness(self):
        from flask import Flask
        app = Flask(__name__)
        app.url_map.iter_rules = MagicMock(return_value=[])
        from utils.erp_readiness import score_erp_readiness
        with patch("extensions.db") as MockDB, \
             patch("models.Account"), \
             patch("models.GLBatch"), \
             patch("models.GLEntry"), \
             patch("models.PayrollRun"), \
             patch("models.SupplierInvoice"), \
             patch("models.GoodsReceipt"), \
             patch("models.Sale"), \
             patch("models.TaxEntry"), \
             patch("models.User"), \
             patch("models.DocumentApproval") as MockDA, \
             patch("models.StockLevel"), \
             patch("models.SystemSettings"), \
             patch("utils.erp_readiness.importlib.import_module", side_effect=ImportError):
            MockDA.query.filter_by.return_value.count.return_value = 0
            MockDB.session.query.return_value.limit.return_value.count.return_value = 0
            result = score_erp_readiness(app)
        assert "overall" in result
        assert "modules" in result
        assert result["pass_all_90"] is False

    def test_has_route_true(self):
        from utils.erp_readiness import _has_route
        app = MagicMock()
        rule1 = MagicMock()
        rule1.rule = "/sales"
        rule2 = MagicMock()
        rule2.rule = "/reports/financial"
        app.url_map.iter_rules.return_value = [rule1, rule2]
        assert _has_route(app, "/sales") is True
        assert _has_route(app, "/nonexistent") is False

    def test_module_exists(self):
        from utils.erp_readiness import _module_exists
        assert _module_exists("os") is True
        assert _module_exists("nonexistent_module_xyz123") is False


# =============================================================================
# utils/comparative_financial.py  (56 stmts, 0% → 100%)
# =============================================================================

class TestComparativeFinancial:
    def test_period_bounds_default(self):
        from utils.comparative_financial import _period_bounds
        start, end = _period_bounds(2024)
        assert start.year == 2024 and start.month == 1 and start.day == 1
        assert end.year == 2024 and end.month == 12 and end.day == 31

    def test_period_bounds_partial(self):
        from utils.comparative_financial import _period_bounds
        start, end = _period_bounds(2024, month_start=4, month_end=6)
        assert start.month == 4
        assert end.month == 6

    def test_account_balances_for_period_no_prefix(self):
        session = MagicMock()
        q = MagicMock()
        session.query.return_value = q
        q.join.return_value = q
        q.filter.return_value = q
        q.group_by.return_value = q
        q.all.return_value = [("4000_SALES", 1000.0, 0.0)]
        q2 = MagicMock()
        q2.all.return_value = []
        from utils.comparative_financial import account_balances_for_period
        with patch("utils.comparative_financial.resolve_branch_filter", return_value=None):
            with patch("utils.comparative_financial.db") as MockDB:
                MockDB.session = session
                result = account_balances_for_period(
                    datetime(2024, 1, 1), datetime(2024, 12, 31)
                )
        assert "4000_SALES" in result

    def test_account_balances_for_period_with_branches(self):
        session = MagicMock()
        q = MagicMock()
        session.query.return_value = q
        q.join.return_value = q
        q.filter.return_value = q
        q.group_by.return_value = q
        q.all.return_value = []
        from utils.comparative_financial import account_balances_for_period
        with patch("utils.comparative_financial.resolve_branch_filter", return_value=[1, 2]):
            with patch("utils.comparative_financial.db") as MockDB:
                MockDB.session = session
                result = account_balances_for_period(
                    datetime(2024, 1, 1), datetime(2024, 12, 31)
                )
        assert result == {}

    def test_account_balances_for_period_empty_branches(self):
        session = MagicMock()
        q = MagicMock()
        session.query.return_value = q
        q.join.return_value = q
        q.filter.return_value = q
        q.group_by.return_value = q
        q.all.return_value = []
        from utils.comparative_financial import account_balances_for_period
        with patch("utils.comparative_financial.resolve_branch_filter", return_value=[]):
            with patch("utils.comparative_financial.db") as MockDB:
                MockDB.session = session
                result = account_balances_for_period(
                    datetime(2024, 1, 1), datetime(2024, 12, 31)
                )
        assert result == {}


# =============================================================================
# utils/ux_messages.py  (69 stmts, 0% → 100%)
# =============================================================================

class TestUxMessages:
    def test_normalize_flash_category(self):
        from utils.ux_messages import normalize_flash_category
        assert normalize_flash_category("error") == "danger"
        assert normalize_flash_category("success") == "success"
        assert normalize_flash_category("warn") == "warning"
        assert normalize_flash_category("info") == "info"
        assert normalize_flash_category(None) == "info"

    def test_msg(self):
        from utils.ux_messages import msg
        assert "تعذّر" in msg("internal_error")
        assert msg("nonexistent_key_xyz", default="fallback") == "fallback"
        assert msg("unknown_key") == "unknown_key"

    def test_flash_title(self):
        from utils.ux_messages import flash_title
        assert flash_title("success") == "تم بنجاح"
        assert flash_title("danger") == "تعذّر الإكمال"

    def test_flash_icon(self):
        from utils.ux_messages import flash_icon
        assert flash_icon("success") == "fa-check-circle"
        assert flash_icon("unknown") == "fa-info-circle"

    def test_clean_flash_text_none(self):
        from utils.ux_messages import clean_flash_text
        assert clean_flash_text(None) == ""

    def test_clean_flash_text_empty(self):
        from utils.ux_messages import clean_flash_text
        assert clean_flash_text("  ") == ""

    def test_clean_flash_text_alias(self):
        from utils.ux_messages import clean_flash_text
        result = clean_flash_text("حدث خطأ داخلي")
        assert "تعذّر" in result

    def test_clean_flash_text_alias_lower(self):
        from utils.ux_messages import clean_flash_text
        result = clean_flash_text("ليس لديك صلاحية")
        assert "صلاحية" in result

    def test_clean_flash_text_alias_prefix(self):
        from utils.ux_messages import clean_flash_text
        result = clean_flash_text("ليس لديك صلاحية. اتصل بالمسؤول")
        assert "صلاحية" in result

    def test_clean_flash_text_strip_emoji(self):
        from utils.ux_messages import clean_flash_text
        result = clean_flash_text("✅ تم بنجاح")
        assert "تم بنجاح" in result

    def test_resolve_user_message_key(self):
        from utils.ux_messages import resolve_user_message
        assert "تعذّر" in resolve_user_message(key="internal_error")

    def test_resolve_user_message_clean(self):
        from utils.ux_messages import resolve_user_message
        result = resolve_user_message(message="حذف بنجاح")
        assert "حذف" in result

    def test_resolve_user_message_default(self):
        from utils.ux_messages import resolve_user_message
        result = resolve_user_message(message="")
        assert "تعذّر" in result

    def test_prepare_flash(self):
        from utils.ux_messages import prepare_flash
        result = prepare_flash("success", "تم الحفظ")
        assert result["category"] == "success"
        assert result["title"] == "تم بنجاح"
        assert "الحفظ" in result["message"]

    def test_prepare_flash_none(self):
        from utils.ux_messages import prepare_flash
        result = prepare_flash(None, None)
        assert result["category"] == "info"

    def test_api_payload_success(self):
        from utils.ux_messages import api_payload
        result = api_payload(success=True)
        assert result["success"] is True
        assert "تم" in result["message"]

    def test_api_payload_error(self):
        from utils.ux_messages import api_payload
        result = api_payload(success=False, key="permission_denied")
        assert result["success"] is False

    def test_api_payload_with_errors(self):
        from utils.ux_messages import api_payload
        result = api_payload(success=False, key="validation_error", errors={"field": ["error"]})
        assert "errors" in result
        assert result["errors"] == {"field": ["error"]}


# =============================================================================
# utils/supplier_invoice_service.py  (87 stmts, 0% → 100%)
# =============================================================================

class TestSupplierInvoiceService:
    @patch("utils.supplier_invoice_service.SupplierInvoice")
    @patch("utils.supplier_invoice_service.db")
    def test_next_si_number(self, MockDB, MockSI):
        MockSI.query.count.return_value = 5
        from utils.supplier_invoice_service import _next_si_number
        assert _next_si_number().startswith("SINV-")

    @patch("utils.supplier_invoice_service.SupplierInvoice")
    @patch("utils.supplier_invoice_service.db")
    def test_create_from_purchase_order_bad_status(self, MockDB, MockSI):
        po = MagicMock()
        po.status = "DRAFT"
        from utils.supplier_invoice_service import create_from_purchase_order
        with pytest.raises(ValueError, match="مستلماً"):
            create_from_purchase_order(po)

    @patch("utils.supplier_invoice_service.SupplierInvoiceLine")
    @patch("utils.supplier_invoice_service.SupplierInvoice")
    @patch("utils.supplier_invoice_service.db")
    def test_create_from_purchase_order_already_posted(self, MockDB, MockSI, MockSIL):
        po = MagicMock()
        po.status = "RECEIVED"
        existing = MagicMock()
        MockSI.query.filter_by.return_value.first.return_value = existing
        from utils.supplier_invoice_service import create_from_purchase_order
        result = create_from_purchase_order(po)
        assert result == existing

    @patch("utils.supplier_invoice_service.SupplierInvoiceLine")
    @patch("utils.supplier_invoice_service.SupplierInvoice")
    @patch("utils.supplier_invoice_service.db")
    def test_create_from_purchase_order_no_lines(self, MockDB, MockSI, MockSIL):
        po = MagicMock()
        po.status = "RECEIVED"
        MockSI.query.filter_by.return_value.first.return_value = None
        MockSI.query.count.return_value = 1
        ln = MagicMock()
        ln.received_qty = "0"
        po.lines = [ln]
        from utils.supplier_invoice_service import create_from_purchase_order
        with pytest.raises(ValueError, match="كميات"):
            create_from_purchase_order(po)

    @patch("utils.supplier_invoice_service.SupplierInvoiceLine")
    @patch("utils.supplier_invoice_service.SupplierInvoice")
    @patch("utils.supplier_invoice_service.db")
    def test_create_from_purchase_order_ok(self, MockDB, MockSI, MockSIL):
        po = MagicMock()
        po.status = "RECEIVED"
        po.id = 1
        po.supplier_id = 5
        po.branch_id = 10
        po.currency = "ILS"
        po.number = "PO-001"

        MockSI.query.filter_by.return_value.first.return_value = None
        MockSI.query.count.return_value = 1

        ln = MagicMock()
        ln.received_qty = "2"
        ln.unit_price = "100.00"
        ln.product_id = 7
        ln.product.name = "Widget"
        po.lines = [ln]

        from utils.supplier_invoice_service import create_from_purchase_order
        result = create_from_purchase_order(po)
        MockDB.session.add.assert_called()

    @patch("utils.supplier_invoice_service._gl_upsert_batch_and_entries")
    @patch("utils.supplier_invoice_service._ensure_account_exists")
    @patch("utils.supplier_invoice_service.GL_ACCOUNTS",
           {"AP": "2000_AP", "PURCHASES": "5000_PUR", "VAT_INPUT": "1500_VAT"})
    @patch("utils.supplier_invoice_service.SupplierInvoice")
    @patch("utils.supplier_invoice_service.db")
    def test_post_supplier_invoice_gl(
        self, MockDB, MockSI, mock_ensure, mock_gl
    ):
        inv = MagicMock()
        inv.id = 1
        inv.status = "DRAFT"
        inv.total_amount = Decimal("232.00")
        inv.subtotal = Decimal("200.00")
        inv.vat_amount = Decimal("32.00")
        inv.currency = "ILS"
        inv.number = "SINV-001"
        inv.supplier_id = 5
        inv.branch_id = 10
        MockDB.session.get.return_value = inv
        mock_gl.return_value = 42

        from utils.supplier_invoice_service import post_supplier_invoice_gl
        result = post_supplier_invoice_gl(1)
        assert result == 42
        assert inv.status == "POSTED"

    @patch("utils.supplier_invoice_service._gl_upsert_batch_and_entries")
    @patch("utils.supplier_invoice_service._ensure_account_exists")
    @patch("utils.supplier_invoice_service.GL_ACCOUNTS",
           {"AP": "2000_AP", "PURCHASES": "5000_PUR"})
    @patch("utils.supplier_invoice_service.SupplierInvoice")
    @patch("utils.supplier_invoice_service.db")
    def test_post_supplier_invoice_no_vat(
        self, MockDB, MockSI, mock_ensure, mock_gl
    ):
        inv = MagicMock()
        inv.id = 2
        inv.status = "DRAFT"
        inv.total_amount = Decimal("100.00")
        inv.subtotal = Decimal("100.00")
        inv.vat_amount = Decimal("0")
        inv.currency = "ILS"
        inv.number = "SINV-002"
        inv.supplier_id = 5
        inv.branch_id = 10
        MockDB.session.get.return_value = inv
        mock_gl.return_value = 43

        from utils.supplier_invoice_service import post_supplier_invoice_gl
        result = post_supplier_invoice_gl(2)
        assert result == 43

    @patch("utils.supplier_invoice_service.SupplierInvoice")
    @patch("utils.supplier_invoice_service.db")
    def test_post_supplier_invoice_not_found(self, MockDB, MockSI):
        MockDB.session.get.return_value = None
        from utils.supplier_invoice_service import post_supplier_invoice_gl
        with pytest.raises(ValueError, match="غير موجودة"):
            post_supplier_invoice_gl(999)

    @patch("utils.supplier_invoice_service.SupplierInvoice")
    @patch("utils.supplier_invoice_service.db")
    def test_post_supplier_invoice_zero(self, MockDB, MockSI):
        inv = MagicMock()
        inv.status = "DRAFT"
        inv.total_amount = Decimal("0")
        MockDB.session.get.return_value = inv
        from utils.supplier_invoice_service import post_supplier_invoice_gl
        with pytest.raises(ValueError, match="صفر"):
            post_supplier_invoice_gl(1)

    @patch("models.Payment")
    @patch("utils.supplier_invoice_service._gl_upsert_batch_and_entries")
    @patch("utils.supplier_invoice_service._ensure_account_exists")
    @patch("utils.supplier_invoice_service.GL_ACCOUNTS",
           {"AP": "2000_AP", "BANK": "1010_BANK"})
    @patch("utils.supplier_invoice_service.SupplierInvoice")
    @patch("utils.supplier_invoice_service.db")
    def test_pay_supplier_invoice_ok(
        self, MockDB, MockSI, mock_ensure, mock_gl, MockPay
    ):
        inv = MagicMock()
        inv.status = "POSTED"
        inv.total_amount = Decimal("500.00")
        inv.amount_paid = Decimal("0")
        inv.currency = "ILS"
        inv.number = "SINV-001"
        inv.supplier_id = 5
        inv.branch_id = 10
        inv.id = 1
        MockPay.query.count.return_value = 1
        mock_gl.return_value = 55

        from utils.supplier_invoice_service import pay_supplier_invoice
        result = pay_supplier_invoice(inv, 500.0)
        assert result == 55
        MockDB.session.add.assert_called()
        MockDB.session.flush.assert_called()

    def test_pay_supplier_invoice_not_posted(self):
        inv = MagicMock()
        inv.status = "DRAFT"
        from utils.supplier_invoice_service import pay_supplier_invoice
        with pytest.raises(ValueError, match="ترحيل"):
            pay_supplier_invoice(inv, 100.0)

    def test_pay_supplier_invoice_bad_amount(self):
        inv = MagicMock()
        inv.status = "POSTED"
        inv.total_amount = Decimal("100.00")
        inv.amount_paid = Decimal("0")
        from utils.supplier_invoice_service import pay_supplier_invoice
        with pytest.raises(ValueError, match="غير صالح"):
            pay_supplier_invoice(inv, 200.0)


# =============================================================================
# utils/branding.py  (94 stmts, 0% → 100%)
# =============================================================================

class TestBranding:
    @patch("utils.branding.url_for")
    @patch("utils.branding.current_user")
    @patch("utils.branding.PLATFORM", {"logo": "img/logo.png", "favicon": "img/favicon.ico",
                                        "emblem": "img/emblem.png", "white": "img/white.png",
                                        "login_bg": "img/login_bg.png"})
    def test_resolve_branding_bundle_basic(self, mock_cu, mock_url):
        mock_url.return_value = "/static/img/logo.png"
        mock_cu.is_authenticated = False
        get_setting = MagicMock(side_effect=lambda k, *a: {
            "company_name": "TestCo",
        }.get(k, a[0] if a else ""))
        with_ver = lambda x: x + "?v=1"
        safe_static_path = lambda p, **kw: p
        safe_path_root = lambda p, **kw: p

        from utils.branding import resolve_branding_bundle
        result = resolve_branding_bundle(
            raw_settings={},
            get_setting=get_setting,
            with_ver=with_ver,
            safe_static_path=safe_static_path,
            safe_static_path_allow_root=safe_path_root,
            static_file_exists=MagicMock(return_value=True),
        )
        assert result["platform_company_name"] == "TestCo"
        assert result["platform_logo_url"] == "/static/img/logo.png?v=1"

    @patch("utils.branding.url_for")
    @patch("utils.branding.current_user")
    @patch("utils.branding.PLATFORM", {"logo": "img/logo.png", "favicon": "img/favicon.ico",
                                        "emblem": "img/emblem.png", "white": "img/white.png",
                                        "login_bg": "img/login_bg.png"})
    def test_resolve_branding_bundle_no_file(self, mock_cu, mock_url):
        mock_url.return_value = "/static/img/default.png"
        mock_cu.is_authenticated = False
        get_setting = MagicMock(return_value=None)
        with_ver = lambda x: x
        safe_static_path = lambda p, **kw: "fallback.png"
        safe_path_root = lambda p, **kw: "fallback.png"

        from utils.branding import resolve_branding_bundle
        result = resolve_branding_bundle(
            raw_settings={},
            get_setting=get_setting,
            with_ver=with_ver,
            safe_static_path=safe_static_path,
            safe_static_path_allow_root=safe_path_root,
            static_file_exists=MagicMock(return_value=False),
        )
        assert result["platform_company_name"] == "شركة أزاد للأنظمة الذكية"


# =============================================================================
# utils/company_reports.py  (extra coverage for remaining lines)
# =============================================================================

class TestCompanyReportsExtra:
    @patch("utils.company_reports.build_customer_balance_view")
    @patch("utils.company_reports.Branch")
    @patch("utils.company_reports.FiscalPeriod")
    @patch("utils.company_reports.db")
    def test_company_dashboard_with_balance(
        self, MockDB, MockFP, MockBr, mock_bcv
    ):
        from utils.company_reports import company_dashboard
        session = MagicMock()
        company = MagicMock()
        company.id = 1
        company.name = "TestCo"
        company.code = "TC"
        company.tax_id = "123"
        company.currency = "ILS"
        session.get.return_value = company

        MockBr.query.filter_by.return_value.all.return_value = [
            MagicMock(id=10),
        ]

        MockFP.query.filter_by.return_value.count.return_value = 2
        MockFP.query.filter.return_value.count.return_value = 1

        MockDB.session = session

        with patch("models.Sale") as MockSale:
            MockSale.customer_id = MagicMock()
            MockSale.customer_id.isnot.return_value = True
            MockSale.id = MagicMock()
            session.query.return_value.join.return_value.join.return_value.filter.return_value.distinct.return_value.limit.return_value = [(5,)]
            mock_bcv.return_value = {
                "success": True,
                "balance": {"amount": "1500.00"},
            }
            result = company_dashboard(1)

        assert result["customers_with_balance"] == 1
        assert result["customers_balance_net"] == 1500.0


# =============================================================================
# barcodes.py  (83 stmts, 40% → 100%)
# =============================================================================

class TestBarcodes:
    @patch("barcodes.QR_AVAILABLE", False)
    def test_generate_qr_not_available(self):
        from barcodes import generate_qr_code
        assert generate_qr_code("test") is None

    @patch("barcodes.QR_AVAILABLE", False)
    def test_generate_barcode_image_not_available(self):
        from barcodes import generate_barcode_image
        assert generate_barcode_image("test") is None

    def test_compute_ean13_check_digit(self):
        from barcodes import compute_ean13_check_digit
        assert compute_ean13_check_digit("590123456789") == 3

    def test_compute_ean13_check_digit_bad_input(self):
        from barcodes import compute_ean13_check_digit
        with pytest.raises(ValueError, match="12 digits"):
            compute_ean13_check_digit("123")

    def test_normalize_barcode_none(self):
        from barcodes import normalize_barcode
        assert normalize_barcode(None) is None

    def test_normalize_barcode_empty(self):
        from barcodes import normalize_barcode
        assert normalize_barcode("") is None

    def test_normalize_barcode_no_digits(self):
        from barcodes import normalize_barcode
        assert normalize_barcode("ABC") is None

    def test_normalize_barcode_12(self):
        from barcodes import normalize_barcode
        result = normalize_barcode("590123456789")
        assert result == "5901234567893"

    def test_normalize_barcode_13(self):
        from barcodes import normalize_barcode
        result = normalize_barcode("5901234567893")
        assert result == "5901234567893"

    def test_is_valid_ean13_true(self):
        from barcodes import is_valid_ean13
        assert is_valid_ean13("5901234567893") is True

    def test_is_valid_ean13_false(self):
        from barcodes import is_valid_ean13
        assert is_valid_ean13("5901234567891") is False

    def test_is_valid_ean13_bad_format(self):
        from barcodes import is_valid_ean13
        assert is_valid_ean13("abc") is False

    def test_validate_barcode_empty(self):
        from barcodes import validate_barcode
        result = validate_barcode("")
        assert result["valid"] is False

    def test_validate_barcode_12(self):
        from barcodes import validate_barcode
        result = validate_barcode("590123456789")
        assert result["valid"] is True
        assert len(result["normalized"]) == 13

    def test_validate_barcode_13_good(self):
        from barcodes import validate_barcode
        result = validate_barcode("5901234567893")
        assert result["valid"] is True
        assert result["suggested"] is None

    def test_validate_barcode_13_bad(self):
        from barcodes import validate_barcode
        result = validate_barcode("5901234567891")
        assert result["valid"] is False
        assert result["suggested"] is not None

    def test_validate_barcode_other_len(self):
        from barcodes import validate_barcode
        result = validate_barcode("12345")
        assert result["valid"] is False

    @patch("barcodes.QR_AVAILABLE", True)
    @patch("barcodes.qrcode")
    def test_generate_qr_code_ok(self, mock_qr):
        mock_qr_instance = MagicMock()
        mock_qr.QRCode.return_value = mock_qr_instance
        mock_img = MagicMock()
        mock_qr_instance.make_image.return_value = mock_img
        from barcodes import generate_qr_code
        result = generate_qr_code("test data")
        assert result is not None
        assert result.startswith("data:image/png;base64,")

    @patch("barcodes.QR_AVAILABLE", True)
    @patch("barcodes.qrcode")
    def test_generate_barcode_image_ok(self, mock_qr):
        mock_qr_instance = MagicMock()
        mock_qr.QRCode.return_value = mock_qr_instance
        mock_img = MagicMock()
        mock_qr_instance.make_image.return_value = mock_img
        from barcodes import generate_barcode_image
        result = generate_barcode_image("1234567890123")
        assert result is not None
        assert result.startswith("data:image/png;base64,")

    @patch("barcodes.generate_qr_code")
    @patch("barcodes.generate_barcode_image")
    def test_create_printable_label(self, mock_bc, mock_qr):
        mock_qr.return_value = "data:qr"
        mock_bc.return_value = "data:bc"
        from barcodes import create_printable_label
        html = create_printable_label("Product X", "1234567890123", price=99.90)
        assert "Product X" in html
        assert "99.9" in html

    @patch("barcodes.generate_qr_code")
    @patch("barcodes.generate_barcode_image")
    def test_create_printable_label_no_price(self, mock_bc, mock_qr):
        mock_qr.return_value = "data:qr"
        mock_bc.return_value = "data:bc"
        from barcodes import create_printable_label
        html = create_printable_label("Product X", "1234567890123")
        assert "السعر" not in html

    @patch("barcodes.generate_qr_code")
    @patch("barcodes.generate_barcode_image")
    def test_print_label(self, mock_bc, mock_qr):
        mock_qr.return_value = "data:qr"
        mock_bc.return_value = "data:bc"
        from barcodes import print_label
        result = print_label("Product X", "1234567890123", price=50.0)
        assert "window.print" in result
        assert "Product X" in result


# =============================================================================
# acl.py  (55 stmts, 33% → 100%)
# =============================================================================

class TestAcl:
    @patch("acl.utils")
    def test_has_perm_not_callable(self, mock_utils):
        from acl import _has_perm
        user = MagicMock()
        user.has_permission = None
        assert _has_perm(user, "some_perm") is False

    def test_has_perm_callable(self):
        from acl import _has_perm
        user = MagicMock()
        user.has_permission.return_value = True
        assert _has_perm(user, "some_perm") is True

    def test_has_perm_callable_returns_false(self):
        from acl import _has_perm
        user = MagicMock()
        user.has_permission.return_value = False
        assert _has_perm(user, "some_perm") is False

    def test_has_perm_callable_raises(self):
        from acl import _has_perm
        user = MagicMock()
        user.has_permission.side_effect = Exception("fail")
        assert _has_perm(user, "some_perm") is False

    def _call_guard(self, bp, **kwargs):
        """Helper: call attach_acl and return the registered guard function."""
        from acl import attach_acl
        attach_acl(bp, **kwargs)
        guard = bp.before_request.call_args[0][0]
        return guard

    def test_attach_acl_options(self):
        bp = MagicMock()
        bp._acl_attached = False
        guard = self._call_guard(bp, read_perm="r", write_perm="w")
        with patch("acl.request") as mock_req:
            mock_req.method = "OPTIONS"
            assert guard() is None

    def test_attach_acl_public_read(self):
        bp = MagicMock()
        bp._acl_attached = False
        guard = self._call_guard(bp, read_perm="r", write_perm="w", public_read=True)
        with patch("acl.request") as mock_req:
            mock_req.method = "GET"
            mock_req.path = "/api/public"
            assert guard() is None

    def test_attach_acl_exempt_prefix(self):
        bp = MagicMock()
        bp._acl_attached = False
        guard = self._call_guard(bp, read_perm="r", write_perm="w")
        with patch("acl.request") as mock_req:
            mock_req.method = "POST"
            mock_req.path = "/static/css/style.css"
            assert guard() is None

    def test_attach_acl_already_attached(self):
        bp = MagicMock()
        bp._acl_attached = True
        from acl import attach_acl
        attach_acl(bp, read_perm="r", write_perm="w")
        bp.before_request.assert_not_called()

    def test_attach_acl_read_like_prefix(self):
        bp = MagicMock()
        bp._acl_attached = False
        mock_cu = MagicMock()
        mock_cu.is_authenticated = True
        guard = self._call_guard(bp, read_perm="r", write_perm="w",
                                 read_like_prefixes=["/api/export"])
        with patch("acl.request") as mock_req, \
             patch("acl.current_user", mock_cu), \
             patch("acl.utils.is_super", return_value=False), \
             patch("acl._has_perm", return_value=True):
            mock_req.method = "POST"
            mock_req.path = "/api/export/data"
            assert guard() is None

    def test_attach_acl_not_auth_api(self):
        bp = MagicMock()
        bp._acl_attached = False
        mock_cu = MagicMock()
        mock_cu.is_authenticated = False
        guard = self._call_guard(bp, read_perm="r", write_perm="w")
        with patch("acl.request") as mock_req, \
             patch("acl.current_user", mock_cu), \
             patch("acl.abort") as mock_abort:
            mock_req.method = "GET"
            mock_req.path = "/api/data"
            mock_req.accept_mimetypes.best = "application/json"
            guard()
            mock_abort.assert_called_once_with(401)

    def test_attach_acl_not_auth_non_api(self):
        bp = MagicMock()
        bp._acl_attached = False
        mock_cu = MagicMock()
        mock_cu.is_authenticated = False
        mock_lm = MagicMock()
        guard = self._call_guard(bp, read_perm="r", write_perm="w")
        with patch("acl.request") as mock_req, \
             patch("acl.current_user", mock_cu), \
             patch("acl.login_manager", mock_lm):
            mock_req.method = "GET"
            mock_req.path = "/html/page"
            mock_req.accept_mimetypes.best = "text/html"
            guard()
            mock_lm.unauthorized.assert_called_once()

    def test_attach_acl_is_super(self):
        bp = MagicMock()
        bp._acl_attached = False
        mock_cu = MagicMock()
        mock_cu.is_authenticated = True
        guard = self._call_guard(bp, read_perm="r", write_perm="w")
        with patch("acl.request") as mock_req, \
             patch("acl.current_user", mock_cu), \
             patch("acl.utils.is_super", return_value=True):
            mock_req.method = "DELETE"
            mock_req.path = "/admin/delete"
            assert guard() is None

    def test_attach_acl_is_read_forbidden(self):
        bp = MagicMock()
        bp._acl_attached = False
        mock_cu = MagicMock()
        mock_cu.is_authenticated = True
        guard = self._call_guard(bp, read_perm="r", write_perm="w")
        with patch("acl.request") as mock_req, \
             patch("acl.current_user", mock_cu), \
             patch("acl.utils.is_super", return_value=False), \
             patch("acl._has_perm", return_value=False), \
             patch("acl.abort") as mock_abort:
            mock_req.method = "GET"
            mock_req.path = "/api/secret"
            guard()
            mock_abort.assert_called_once_with(403)

    def test_attach_acl_write_forbidden(self):
        bp = MagicMock()
        bp._acl_attached = False
        mock_cu = MagicMock()
        mock_cu.is_authenticated = True
        guard = self._call_guard(bp, read_perm=None, write_perm="w")
        with patch("acl.request") as mock_req, \
             patch("acl.current_user", mock_cu), \
             patch("acl.utils.is_super", return_value=False), \
             patch("acl._has_perm", return_value=False), \
             patch("acl.abort") as mock_abort:
            mock_req.method = "POST"
            mock_req.path = "/api/data"
            guard()
            mock_abort.assert_called_once_with(403)

    def test_require_perm_super(self):
        with patch("acl.login_required", lambda f: f):
            from acl import require_perm

            def view():
                return "ok"

            wrapped = require_perm("admin_access")(view)
            with patch("acl.utils.is_super", return_value=True):
                assert wrapped() == "ok"

    def test_require_perm_has_perm(self):
        with patch("acl.login_required", lambda f: f):
            from acl import require_perm

            def view():
                return "ok"

            wrapped = require_perm("admin_access")(view)
            mock_cu = MagicMock()
            mock_cu.is_authenticated = True
            with patch("acl.utils.is_super", return_value=False), \
                 patch("acl.current_user", mock_cu), \
                 patch("acl._has_perm", return_value=True):
                assert wrapped() == "ok"

    def test_require_perm_forbidden(self):
        with patch("acl.login_required", lambda f: f):
            from acl import require_perm

            def view():
                return "ok"

            wrapped = require_perm("admin_access")(view)
            mock_cu = MagicMock()
            mock_cu.is_authenticated = True
            with patch("acl.utils.is_super", return_value=False), \
                 patch("acl.current_user", mock_cu), \
                 patch("acl._has_perm", return_value=False), \
                 patch("acl.abort") as mock_abort:
                wrapped()
                mock_abort.assert_called_once_with(403)
