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
        mock_app.config.get.return_value = True
        from utils.payment_allocation_policy import payment_auto_allocate_enabled
        result = payment_auto_allocate_enabled()
        assert result is True

    @patch("models.SystemSettings")
    def test_auto_allocate_enabled_via_settings(self, MockS):
        MockS.get_setting.return_value = True
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
