--
-- PostgreSQL database dump
--

\restrict h6FqF4nHdwSqoCRRxR0wKhsDb6mcbovXo1umyDbbcR0KhwpAFDLiuBERA4fqVfs

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accounts (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(100) NOT NULL,
    type character varying(9) NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.accounts OWNER TO postgres;

--
-- Name: accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.accounts_id_seq OWNER TO postgres;

--
-- Name: accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.accounts_id_seq OWNED BY public.accounts.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: archives; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.archives (
    id integer NOT NULL,
    record_type character varying(50) NOT NULL,
    record_id integer NOT NULL,
    table_name character varying(100) NOT NULL,
    archived_data text NOT NULL,
    archive_reason character varying(200),
    archived_by integer NOT NULL,
    archived_at timestamp without time zone NOT NULL,
    original_created_at timestamp without time zone,
    original_updated_at timestamp without time zone
);


ALTER TABLE public.archives OWNER TO postgres;

--
-- Name: archives_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.archives_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.archives_id_seq OWNER TO postgres;

--
-- Name: archives_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.archives_id_seq OWNED BY public.archives.id;


--
-- Name: asset_depreciations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.asset_depreciations (
    id integer NOT NULL,
    asset_id integer NOT NULL,
    fiscal_year integer NOT NULL,
    fiscal_month integer,
    depreciation_date date NOT NULL,
    depreciation_amount numeric(12,2) NOT NULL,
    accumulated_depreciation numeric(12,2) NOT NULL,
    book_value numeric(12,2) NOT NULL,
    gl_batch_id integer,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_depreciation_amount_ge_0 CHECK ((depreciation_amount >= (0)::numeric)),
    CONSTRAINT ck_fiscal_month_range CHECK (((fiscal_month >= 1) AND (fiscal_month <= 12)))
);


ALTER TABLE public.asset_depreciations OWNER TO postgres;

--
-- Name: asset_depreciations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.asset_depreciations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.asset_depreciations_id_seq OWNER TO postgres;

--
-- Name: asset_depreciations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.asset_depreciations_id_seq OWNED BY public.asset_depreciations.id;


--
-- Name: asset_maintenance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.asset_maintenance (
    id integer NOT NULL,
    asset_id integer NOT NULL,
    maintenance_date date NOT NULL,
    maintenance_type character varying(100),
    cost numeric(12,2) NOT NULL,
    expense_id integer,
    description text,
    next_maintenance_date date,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_maintenance_cost_ge_0 CHECK ((cost >= (0)::numeric))
);


ALTER TABLE public.asset_maintenance OWNER TO postgres;

--
-- Name: asset_maintenance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.asset_maintenance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.asset_maintenance_id_seq OWNER TO postgres;

--
-- Name: asset_maintenance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.asset_maintenance_id_seq OWNED BY public.asset_maintenance.id;


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    model_name character varying(100) NOT NULL,
    record_id integer,
    customer_id integer,
    user_id integer,
    action character varying(20) NOT NULL,
    old_data text,
    new_data text,
    ip_address character varying(45),
    user_agent character varying(255),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: auth_audit; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_audit (
    id integer NOT NULL,
    user_id integer,
    event character varying(40) NOT NULL,
    success boolean DEFAULT true NOT NULL,
    ip character varying(64),
    user_agent character varying(255),
    note character varying(255),
    metadata json,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.auth_audit OWNER TO postgres;

--
-- Name: auth_audit_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_audit_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.auth_audit_id_seq OWNER TO postgres;

--
-- Name: auth_audit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_audit_id_seq OWNED BY public.auth_audit.id;


--
-- Name: bank_accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bank_accounts (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(200) NOT NULL,
    bank_name character varying(200) NOT NULL,
    account_number character varying(100) NOT NULL,
    iban character varying(34),
    swift_code character varying(11),
    currency character varying(10) NOT NULL,
    branch_id integer,
    gl_account_code character varying(20) NOT NULL,
    opening_balance numeric(15,2) NOT NULL,
    current_balance numeric(15,2) NOT NULL,
    last_reconciled_date date,
    notes text,
    is_active boolean DEFAULT true NOT NULL,
    created_by integer,
    updated_by integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_bank_current_balance_not_null CHECK ((current_balance IS NOT NULL))
);


ALTER TABLE public.bank_accounts OWNER TO postgres;

--
-- Name: bank_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bank_accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bank_accounts_id_seq OWNER TO postgres;

--
-- Name: bank_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bank_accounts_id_seq OWNED BY public.bank_accounts.id;


--
-- Name: bank_reconciliations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bank_reconciliations (
    id integer NOT NULL,
    bank_account_id integer NOT NULL,
    reconciliation_number character varying(50),
    period_start date NOT NULL,
    period_end date NOT NULL,
    book_balance numeric(15,2) NOT NULL,
    bank_balance numeric(15,2) NOT NULL,
    unmatched_book_count integer,
    unmatched_bank_count integer,
    unmatched_book_amount numeric(15,2),
    unmatched_bank_amount numeric(15,2),
    reconciled_by integer NOT NULL,
    reconciled_at timestamp without time zone NOT NULL,
    approved_by integer,
    approved_at timestamp without time zone,
    status character varying(9) NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_reconciliation_period CHECK ((period_end >= period_start))
);


ALTER TABLE public.bank_reconciliations OWNER TO postgres;

--
-- Name: bank_reconciliations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bank_reconciliations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bank_reconciliations_id_seq OWNER TO postgres;

--
-- Name: bank_reconciliations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bank_reconciliations_id_seq OWNED BY public.bank_reconciliations.id;


--
-- Name: bank_statements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bank_statements (
    id integer NOT NULL,
    bank_account_id integer NOT NULL,
    statement_number character varying(50),
    statement_date date NOT NULL,
    period_start date NOT NULL,
    period_end date NOT NULL,
    opening_balance numeric(15,2) NOT NULL,
    closing_balance numeric(15,2) NOT NULL,
    total_deposits numeric(15,2),
    total_withdrawals numeric(15,2),
    file_path character varying(500),
    imported_at timestamp without time zone,
    imported_by integer,
    status character varying(10) NOT NULL,
    notes text,
    created_by integer,
    updated_by integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_statement_balance CHECK ((closing_balance = ((opening_balance + total_deposits) - total_withdrawals)))
);


ALTER TABLE public.bank_statements OWNER TO postgres;

--
-- Name: bank_statements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bank_statements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bank_statements_id_seq OWNER TO postgres;

--
-- Name: bank_statements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bank_statements_id_seq OWNED BY public.bank_statements.id;


--
-- Name: bank_transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bank_transactions (
    id integer NOT NULL,
    bank_account_id integer NOT NULL,
    statement_id integer,
    transaction_date date NOT NULL,
    value_date date,
    reference character varying(100),
    description text,
    debit numeric(15,2),
    credit numeric(15,2),
    balance numeric(15,2),
    matched boolean NOT NULL,
    payment_id integer,
    gl_batch_id integer,
    reconciliation_id integer,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_bank_tx_debit_credit CHECK ((((debit = (0)::numeric) AND (credit > (0)::numeric)) OR ((credit = (0)::numeric) AND (debit > (0)::numeric)) OR ((debit = (0)::numeric) AND (credit = (0)::numeric))))
);


ALTER TABLE public.bank_transactions OWNER TO postgres;

--
-- Name: bank_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bank_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bank_transactions_id_seq OWNER TO postgres;

--
-- Name: bank_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bank_transactions_id_seq OWNED BY public.bank_transactions.id;


--
-- Name: branches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.branches (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    code character varying(32) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    address character varying(200),
    city character varying(100),
    geo_lat numeric(10,6),
    geo_lng numeric(10,6),
    phone character varying(32),
    email character varying(120),
    manager_user_id integer,
    manager_employee_id integer,
    timezone character varying(64),
    currency character varying(10) DEFAULT 'ILS'::character varying NOT NULL,
    tax_id character varying(64),
    notes text,
    is_archived boolean DEFAULT false NOT NULL,
    archived_at timestamp without time zone,
    archived_by integer,
    archive_reason character varying(200),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.branches OWNER TO postgres;

--
-- Name: branches_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.branches_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.branches_id_seq OWNER TO postgres;

--
-- Name: branches_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.branches_id_seq OWNED BY public.branches.id;


--
-- Name: budget_commitments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.budget_commitments (
    id integer NOT NULL,
    budget_id integer NOT NULL,
    source_type character varying(8) NOT NULL,
    source_id integer NOT NULL,
    committed_amount numeric(12,2) NOT NULL,
    commitment_date date NOT NULL,
    status character varying(9) NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_commitment_amount_ge_0 CHECK ((committed_amount >= (0)::numeric))
);


ALTER TABLE public.budget_commitments OWNER TO postgres;

--
-- Name: budget_commitments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.budget_commitments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.budget_commitments_id_seq OWNER TO postgres;

--
-- Name: budget_commitments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.budget_commitments_id_seq OWNED BY public.budget_commitments.id;


--
-- Name: budgets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.budgets (
    id integer NOT NULL,
    fiscal_year integer NOT NULL,
    account_code character varying(20) NOT NULL,
    branch_id integer,
    site_id integer,
    allocated_amount numeric(12,2) NOT NULL,
    notes text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_budget_allocated_ge_0 CHECK ((allocated_amount >= (0)::numeric))
);


ALTER TABLE public.budgets OWNER TO postgres;

--
-- Name: budgets_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.budgets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.budgets_id_seq OWNER TO postgres;

--
-- Name: budgets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.budgets_id_seq OWNED BY public.budgets.id;


--
-- Name: checks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.checks (
    id integer NOT NULL,
    check_number character varying(100) NOT NULL,
    check_bank character varying(200) NOT NULL,
    check_date timestamp without time zone NOT NULL,
    check_due_date timestamp without time zone NOT NULL,
    amount numeric(12,2) NOT NULL,
    currency character varying(10) NOT NULL,
    fx_rate_issue numeric(10,6),
    fx_rate_issue_source character varying(20),
    fx_rate_issue_timestamp timestamp without time zone,
    fx_rate_issue_base character varying(10),
    fx_rate_issue_quote character varying(10),
    fx_rate_cash numeric(10,6),
    fx_rate_cash_source character varying(20),
    fx_rate_cash_timestamp timestamp without time zone,
    fx_rate_cash_base character varying(10),
    fx_rate_cash_quote character varying(10),
    direction character varying(3) NOT NULL,
    status character varying(11) NOT NULL,
    drawer_name character varying(200),
    drawer_phone character varying(20),
    drawer_id_number character varying(50),
    drawer_address text,
    payee_name character varying(200),
    payee_phone character varying(20),
    payee_account character varying(50),
    notes text,
    internal_notes text,
    reference_number character varying(100),
    status_history text,
    customer_id integer,
    supplier_id integer,
    partner_id integer,
    payment_id integer,
    created_by_id integer NOT NULL,
    is_archived boolean NOT NULL,
    archived_at timestamp without time zone,
    archived_by integer,
    archive_reason character varying(200),
    resubmit_allowed_count integer NOT NULL,
    legal_return_allowed_count integer NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_check_amount_positive CHECK ((amount > (0)::numeric))
);


ALTER TABLE public.checks OWNER TO postgres;

--
-- Name: checks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.checks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.checks_id_seq OWNER TO postgres;

--
-- Name: checks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.checks_id_seq OWNED BY public.checks.id;


--
-- Name: cost_allocation_execution_lines; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cost_allocation_execution_lines (
    id integer NOT NULL,
    execution_id integer NOT NULL,
    source_cost_center_id integer,
    target_cost_center_id integer,
    amount numeric(15,2) NOT NULL,
    percentage numeric(5,2),
    gl_batch_id integer
);


ALTER TABLE public.cost_allocation_execution_lines OWNER TO postgres;

--
-- Name: cost_allocation_execution_lines_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cost_allocation_execution_lines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cost_allocation_execution_lines_id_seq OWNER TO postgres;

--
-- Name: cost_allocation_execution_lines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cost_allocation_execution_lines_id_seq OWNED BY public.cost_allocation_execution_lines.id;


--
-- Name: cost_allocation_executions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cost_allocation_executions (
    id integer NOT NULL,
    rule_id integer,
    execution_date date NOT NULL,
    total_amount numeric(15,2) NOT NULL,
    status character varying(8) DEFAULT 'DRAFT'::character varying NOT NULL,
    gl_batch_id integer,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.cost_allocation_executions OWNER TO postgres;

--
-- Name: cost_allocation_executions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cost_allocation_executions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cost_allocation_executions_id_seq OWNER TO postgres;

--
-- Name: cost_allocation_executions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cost_allocation_executions_id_seq OWNED BY public.cost_allocation_executions.id;


--
-- Name: cost_allocation_lines; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cost_allocation_lines (
    id integer NOT NULL,
    rule_id integer NOT NULL,
    target_cost_center_id integer NOT NULL,
    percentage numeric(5,2),
    fixed_amount numeric(15,2),
    allocation_driver character varying(100),
    driver_value numeric(15,2),
    notes text,
    CONSTRAINT ck_allocation_line_percentage CHECK (((percentage >= (0)::numeric) AND (percentage <= (100)::numeric)))
);


ALTER TABLE public.cost_allocation_lines OWNER TO postgres;

--
-- Name: cost_allocation_lines_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cost_allocation_lines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cost_allocation_lines_id_seq OWNER TO postgres;

--
-- Name: cost_allocation_lines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cost_allocation_lines_id_seq OWNED BY public.cost_allocation_lines.id;


--
-- Name: cost_allocation_rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cost_allocation_rules (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    source_cost_center_id integer,
    allocation_method character varying(14) NOT NULL,
    frequency character varying(9),
    is_active boolean DEFAULT true NOT NULL,
    auto_execute boolean DEFAULT false NOT NULL,
    last_executed_at timestamp without time zone,
    next_execution_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.cost_allocation_rules OWNER TO postgres;

--
-- Name: cost_allocation_rules_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cost_allocation_rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cost_allocation_rules_id_seq OWNER TO postgres;

--
-- Name: cost_allocation_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cost_allocation_rules_id_seq OWNED BY public.cost_allocation_rules.id;


--
-- Name: cost_center_alert_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cost_center_alert_logs (
    id integer NOT NULL,
    alert_id integer,
    cost_center_id integer,
    triggered_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    trigger_value numeric(15,2),
    threshold_value numeric(15,2),
    message text,
    severity character varying(8),
    notified_users json,
    notification_sent boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.cost_center_alert_logs OWNER TO postgres;

--
-- Name: cost_center_alert_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cost_center_alert_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cost_center_alert_logs_id_seq OWNER TO postgres;

--
-- Name: cost_center_alert_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cost_center_alert_logs_id_seq OWNED BY public.cost_center_alert_logs.id;


--
-- Name: cost_center_alerts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cost_center_alerts (
    id integer NOT NULL,
    cost_center_id integer NOT NULL,
    alert_type character varying(15) NOT NULL,
    threshold_type character varying(10) DEFAULT 'PERCENTAGE'::character varying NOT NULL,
    threshold_value numeric(15,2) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    notify_manager boolean DEFAULT true NOT NULL,
    notify_emails json,
    notify_users json,
    last_triggered_at timestamp without time zone,
    trigger_count integer DEFAULT 0 NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.cost_center_alerts OWNER TO postgres;

--
-- Name: cost_center_alerts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cost_center_alerts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cost_center_alerts_id_seq OWNER TO postgres;

--
-- Name: cost_center_alerts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cost_center_alerts_id_seq OWNED BY public.cost_center_alerts.id;


--
-- Name: cost_center_allocations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cost_center_allocations (
    id integer NOT NULL,
    cost_center_id integer NOT NULL,
    source_type character varying(8) NOT NULL,
    source_id integer NOT NULL,
    amount numeric(15,2) NOT NULL,
    percentage numeric(5,2),
    allocation_date date NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_cc_alloc_amount_ge_0 CHECK ((amount >= (0)::numeric)),
    CONSTRAINT ck_cc_alloc_percentage_range CHECK (((percentage >= (0)::numeric) AND (percentage <= (100)::numeric)))
);


ALTER TABLE public.cost_center_allocations OWNER TO postgres;

--
-- Name: cost_center_allocations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cost_center_allocations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cost_center_allocations_id_seq OWNER TO postgres;

--
-- Name: cost_center_allocations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cost_center_allocations_id_seq OWNED BY public.cost_center_allocations.id;


--
-- Name: cost_centers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cost_centers (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(200) NOT NULL,
    parent_id integer,
    description text,
    manager_id integer,
    gl_account_code character varying(50),
    budget_amount numeric(15,2),
    actual_amount numeric(15,2),
    is_active boolean DEFAULT true NOT NULL,
    created_by integer,
    updated_by integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_cost_center_budget_ge_0 CHECK ((budget_amount >= (0)::numeric))
);


ALTER TABLE public.cost_centers OWNER TO postgres;

--
-- Name: cost_centers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cost_centers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cost_centers_id_seq OWNER TO postgres;

--
-- Name: cost_centers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cost_centers_id_seq OWNED BY public.cost_centers.id;


--
-- Name: currencies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.currencies (
    code character varying(10) NOT NULL,
    name character varying(100) NOT NULL,
    symbol character varying(10),
    decimals integer DEFAULT 2 NOT NULL,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.currencies OWNER TO postgres;

--
-- Name: customer_loyalty; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer_loyalty (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    total_points integer NOT NULL,
    available_points integer NOT NULL,
    used_points integer NOT NULL,
    loyalty_tier character varying(50) NOT NULL,
    total_spent numeric(12,2) NOT NULL,
    last_activity timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.customer_loyalty OWNER TO postgres;

--
-- Name: customer_loyalty_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customer_loyalty_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customer_loyalty_id_seq OWNER TO postgres;

--
-- Name: customer_loyalty_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customer_loyalty_id_seq OWNED BY public.customer_loyalty.id;


--
-- Name: customer_loyalty_points; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer_loyalty_points (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    points integer NOT NULL,
    reason character varying(255) NOT NULL,
    type character varying(50) NOT NULL,
    reference_id integer,
    reference_type character varying(50),
    expires_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.customer_loyalty_points OWNER TO postgres;

--
-- Name: customer_loyalty_points_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customer_loyalty_points_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customer_loyalty_points_id_seq OWNER TO postgres;

--
-- Name: customer_loyalty_points_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customer_loyalty_points_id_seq OWNED BY public.customer_loyalty_points.id;


--
-- Name: customers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customers (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    phone character varying(20) NOT NULL,
    whatsapp character varying(20),
    email character varying(120),
    address character varying(200),
    password_hash character varying(128),
    category character varying(20),
    notes text,
    is_active boolean DEFAULT true NOT NULL,
    is_online boolean DEFAULT false NOT NULL,
    is_archived boolean DEFAULT false NOT NULL,
    archived_at timestamp without time zone,
    archived_by integer,
    archive_reason character varying(200),
    credit_limit numeric(12,2) DEFAULT 0 NOT NULL,
    discount_rate numeric(5,2) DEFAULT 0 NOT NULL,
    currency character varying(10) DEFAULT 'ILS'::character varying NOT NULL,
    opening_balance numeric(12,2) DEFAULT 0 NOT NULL,
    current_balance numeric(12,2) DEFAULT 0 NOT NULL,
    sales_balance numeric(12,2) DEFAULT 0 NOT NULL,
    returns_balance numeric(12,2) DEFAULT 0 NOT NULL,
    invoices_balance numeric(12,2) DEFAULT 0 NOT NULL,
    services_balance numeric(12,2) DEFAULT 0 NOT NULL,
    preorders_balance numeric(12,2) DEFAULT 0 NOT NULL,
    online_orders_balance numeric(12,2) DEFAULT 0 NOT NULL,
    payments_in_balance numeric(12,2) DEFAULT 0 NOT NULL,
    payments_out_balance numeric(12,2) DEFAULT 0 NOT NULL,
    checks_in_balance numeric(12,2) DEFAULT 0 NOT NULL,
    checks_out_balance numeric(12,2) DEFAULT 0 NOT NULL,
    returned_checks_in_balance numeric(12,2) DEFAULT 0 NOT NULL,
    returned_checks_out_balance numeric(12,2) DEFAULT 0 NOT NULL,
    expenses_balance numeric(12,2) DEFAULT 0 NOT NULL,
    service_expenses_balance numeric(12,2) DEFAULT 0 NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_customer_credit_limit_non_negative CHECK ((credit_limit >= (0)::numeric)),
    CONSTRAINT ck_customer_discount_0_100 CHECK (((discount_rate >= (0)::numeric) AND (discount_rate <= (100)::numeric)))
);


ALTER TABLE public.customers OWNER TO postgres;

--
-- Name: COLUMN customers.opening_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.opening_balance IS 'الرصيد الافتتاحي (موجب=له رصيد عندنا، سالب=لنا رصيد عنده)';


--
-- Name: COLUMN customers.current_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.current_balance IS 'الرصيد الحالي المحدث';


--
-- Name: COLUMN customers.sales_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.sales_balance IS 'رصيد المبيعات';


--
-- Name: COLUMN customers.returns_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.returns_balance IS 'رصيد المرتجعات';


--
-- Name: COLUMN customers.invoices_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.invoices_balance IS 'رصيد الفواتير';


--
-- Name: COLUMN customers.services_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.services_balance IS 'رصيد الخدمات';


--
-- Name: COLUMN customers.preorders_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.preorders_balance IS 'رصيد الحجوزات المسبقة';


--
-- Name: COLUMN customers.online_orders_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.online_orders_balance IS 'رصيد الطلبات الأونلاين';


--
-- Name: COLUMN customers.payments_in_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.payments_in_balance IS 'رصيد الدفعات الواردة';


--
-- Name: COLUMN customers.payments_out_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.payments_out_balance IS 'رصيد الدفعات الصادرة';


--
-- Name: COLUMN customers.checks_in_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.checks_in_balance IS 'رصيد الشيكات الواردة';


--
-- Name: COLUMN customers.checks_out_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.checks_out_balance IS 'رصيد الشيكات الصادرة';


--
-- Name: COLUMN customers.returned_checks_in_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.returned_checks_in_balance IS 'رصيد الشيكات المرتدة الواردة';


--
-- Name: COLUMN customers.returned_checks_out_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.returned_checks_out_balance IS 'رصيد الشيكات المرتدة الصادرة';


--
-- Name: COLUMN customers.expenses_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.expenses_balance IS 'رصيد المصروفات العادية (تُطرح)';


--
-- Name: COLUMN customers.service_expenses_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.service_expenses_balance IS 'رصيد مصروفات توريد الخدمات (تُضاف)';


--
-- Name: customers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customers_id_seq OWNER TO postgres;

--
-- Name: customers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customers_id_seq OWNED BY public.customers.id;


--
-- Name: deletion_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deletion_logs (
    id integer NOT NULL,
    deletion_type character varying(20) NOT NULL,
    entity_id integer NOT NULL,
    entity_name character varying(200) NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    deleted_by integer NOT NULL,
    deletion_reason text,
    confirmation_code character varying(50),
    deleted_data json,
    related_entities json,
    stock_reversals json,
    accounting_reversals json,
    balance_reversals json,
    restored_at timestamp without time zone,
    restored_by integer,
    restoration_notes text,
    CONSTRAINT chk_deletion_status CHECK (((status)::text = ANY ((ARRAY['PENDING'::character varying, 'COMPLETED'::character varying, 'FAILED'::character varying, 'RESTORED'::character varying])::text[])))
);


ALTER TABLE public.deletion_logs OWNER TO postgres;

--
-- Name: deletion_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.deletion_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.deletion_logs_id_seq OWNER TO postgres;

--
-- Name: deletion_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.deletion_logs_id_seq OWNED BY public.deletion_logs.id;


--
-- Name: employee_advance_installments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employee_advance_installments (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    advance_expense_id integer NOT NULL,
    installment_number integer NOT NULL,
    total_installments integer NOT NULL,
    amount numeric(12,2) NOT NULL,
    currency character varying(10) NOT NULL,
    due_date date NOT NULL,
    paid boolean NOT NULL,
    paid_date date,
    paid_in_salary_expense_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.employee_advance_installments OWNER TO postgres;

--
-- Name: employee_advance_installments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employee_advance_installments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employee_advance_installments_id_seq OWNER TO postgres;

--
-- Name: employee_advance_installments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employee_advance_installments_id_seq OWNED BY public.employee_advance_installments.id;


--
-- Name: employee_advances; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employee_advances (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    amount numeric(12,2) NOT NULL,
    currency character varying(10) NOT NULL,
    advance_date date NOT NULL,
    reason text,
    total_installments integer NOT NULL,
    installments_paid integer NOT NULL,
    fully_paid boolean NOT NULL,
    notes text,
    expense_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.employee_advances OWNER TO postgres;

--
-- Name: employee_advances_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employee_advances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employee_advances_id_seq OWNER TO postgres;

--
-- Name: employee_advances_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employee_advances_id_seq OWNED BY public.employee_advances.id;


--
-- Name: employee_deductions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employee_deductions (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    deduction_type character varying(50) NOT NULL,
    amount numeric(12,2) NOT NULL,
    currency character varying(10) NOT NULL,
    start_date date NOT NULL,
    end_date date,
    is_active boolean NOT NULL,
    notes text,
    expense_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.employee_deductions OWNER TO postgres;

--
-- Name: employee_deductions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employee_deductions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employee_deductions_id_seq OWNER TO postgres;

--
-- Name: employee_deductions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employee_deductions_id_seq OWNED BY public.employee_deductions.id;


--
-- Name: employee_skills; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employee_skills (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    skill_id integer NOT NULL,
    proficiency_level character varying(12) NOT NULL,
    years_experience integer DEFAULT 0 NOT NULL,
    certification_number character varying(100),
    certification_authority character varying(200),
    certification_date date,
    expiry_date date,
    verified_by integer,
    verification_date date,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.employee_skills OWNER TO postgres;

--
-- Name: employee_skills_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employee_skills_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employee_skills_id_seq OWNER TO postgres;

--
-- Name: employee_skills_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employee_skills_id_seq OWNED BY public.employee_skills.id;


--
-- Name: employees; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employees (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    "position" character varying(100),
    salary numeric(15,2),
    phone character varying(20),
    email character varying(120),
    hire_date date,
    bank_name character varying(100),
    account_number character varying(100),
    notes text,
    currency character varying(10) DEFAULT 'ILS'::character varying NOT NULL,
    branch_id integer NOT NULL,
    site_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.employees OWNER TO postgres;

--
-- Name: employees_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employees_id_seq OWNER TO postgres;

--
-- Name: employees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employees_id_seq OWNED BY public.employees.id;


--
-- Name: engineering_skills; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.engineering_skills (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(200) NOT NULL,
    name_ar character varying(200),
    category character varying(100),
    description text,
    is_certification_required boolean DEFAULT false NOT NULL,
    certification_validity_months integer,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.engineering_skills OWNER TO postgres;

--
-- Name: engineering_skills_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.engineering_skills_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.engineering_skills_id_seq OWNER TO postgres;

--
-- Name: engineering_skills_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.engineering_skills_id_seq OWNED BY public.engineering_skills.id;


--
-- Name: engineering_tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.engineering_tasks (
    id integer NOT NULL,
    task_number character varying(50) NOT NULL,
    title character varying(300) NOT NULL,
    description text,
    task_type character varying(12) NOT NULL,
    priority character varying(8) DEFAULT 'MEDIUM'::character varying NOT NULL,
    status character varying(11) DEFAULT 'PENDING'::character varying NOT NULL,
    assigned_team_id integer,
    assigned_to_id integer,
    required_skills json,
    estimated_hours numeric(8,2),
    actual_hours numeric(8,2) DEFAULT 0 NOT NULL,
    estimated_cost numeric(15,2),
    actual_cost numeric(15,2) DEFAULT 0 NOT NULL,
    scheduled_start timestamp without time zone,
    scheduled_end timestamp without time zone,
    actual_start timestamp without time zone,
    actual_end timestamp without time zone,
    customer_id integer,
    location character varying(300),
    equipment_needed text,
    tools_needed text,
    materials_needed json,
    safety_requirements text,
    quality_standards text,
    completion_notes text,
    completion_photos json,
    customer_satisfaction_rating integer,
    customer_feedback text,
    cost_center_id integer,
    project_id integer,
    service_request_id integer,
    parent_task_id integer,
    gl_batch_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_task_rating_range CHECK (((customer_satisfaction_rating >= 1) AND (customer_satisfaction_rating <= 5)))
);


ALTER TABLE public.engineering_tasks OWNER TO postgres;

--
-- Name: engineering_tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.engineering_tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.engineering_tasks_id_seq OWNER TO postgres;

--
-- Name: engineering_tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.engineering_tasks_id_seq OWNED BY public.engineering_tasks.id;


--
-- Name: engineering_team_members; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.engineering_team_members (
    id integer NOT NULL,
    team_id integer NOT NULL,
    employee_id integer NOT NULL,
    role character varying(10) NOT NULL,
    join_date date DEFAULT CURRENT_DATE NOT NULL,
    leave_date date,
    hourly_rate numeric(10,2),
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.engineering_team_members OWNER TO postgres;

--
-- Name: engineering_team_members_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.engineering_team_members_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.engineering_team_members_id_seq OWNER TO postgres;

--
-- Name: engineering_team_members_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.engineering_team_members_id_seq OWNED BY public.engineering_team_members.id;


--
-- Name: engineering_teams; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.engineering_teams (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(200) NOT NULL,
    team_leader_id integer,
    specialty character varying(11) NOT NULL,
    cost_center_id integer,
    branch_id integer,
    max_concurrent_tasks integer DEFAULT 5 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    description text,
    equipment_inventory json,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.engineering_teams OWNER TO postgres;

--
-- Name: engineering_teams_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.engineering_teams_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.engineering_teams_id_seq OWNER TO postgres;

--
-- Name: engineering_teams_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.engineering_teams_id_seq OWNED BY public.engineering_teams.id;


--
-- Name: engineering_timesheets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.engineering_timesheets (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    task_id integer,
    work_date date NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    break_duration_minutes integer DEFAULT 0 NOT NULL,
    actual_work_hours numeric(5,2) NOT NULL,
    billable_hours numeric(5,2),
    hourly_rate numeric(10,2),
    total_cost numeric(15,2),
    productivity_rating character varying(9),
    work_description text,
    issues_encountered text,
    materials_used json,
    location character varying(300),
    status character varying(9) DEFAULT 'DRAFT'::character varying NOT NULL,
    approved_by integer,
    approval_date timestamp without time zone,
    approval_notes text,
    cost_center_id integer,
    gl_batch_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_timesheet_break_positive CHECK ((break_duration_minutes >= 0)),
    CONSTRAINT ck_timesheet_hours_positive CHECK ((actual_work_hours > (0)::numeric))
);


ALTER TABLE public.engineering_timesheets OWNER TO postgres;

--
-- Name: engineering_timesheets_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.engineering_timesheets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.engineering_timesheets_id_seq OWNER TO postgres;

--
-- Name: engineering_timesheets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.engineering_timesheets_id_seq OWNED BY public.engineering_timesheets.id;


--
-- Name: equipment_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment_types (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    model_number character varying(100),
    chassis_number character varying(100),
    notes text,
    category character varying(50),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.equipment_types OWNER TO postgres;

--
-- Name: equipment_types_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.equipment_types_id_seq OWNER TO postgres;

--
-- Name: equipment_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_types_id_seq OWNED BY public.equipment_types.id;


--
-- Name: exchange_rates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exchange_rates (
    id integer NOT NULL,
    base_code character varying(10) NOT NULL,
    quote_code character varying(10) NOT NULL,
    rate numeric(18,8) NOT NULL,
    valid_from timestamp without time zone DEFAULT now() NOT NULL,
    source character varying(50),
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.exchange_rates OWNER TO postgres;

--
-- Name: exchange_rates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.exchange_rates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.exchange_rates_id_seq OWNER TO postgres;

--
-- Name: exchange_rates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.exchange_rates_id_seq OWNED BY public.exchange_rates.id;


--
-- Name: exchange_transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exchange_transactions (
    id integer NOT NULL,
    product_id integer NOT NULL,
    warehouse_id integer NOT NULL,
    supplier_id integer,
    partner_id integer,
    quantity integer NOT NULL,
    direction character varying(10) DEFAULT 'IN'::character varying NOT NULL,
    unit_cost numeric(12,2),
    is_priced boolean DEFAULT false NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_exchange_qty_positive CHECK ((quantity > 0)),
    CONSTRAINT ck_exchange_unit_cost_non_negative CHECK (((unit_cost IS NULL) OR (unit_cost >= (0)::numeric)))
);


ALTER TABLE public.exchange_transactions OWNER TO postgres;

--
-- Name: exchange_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.exchange_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.exchange_transactions_id_seq OWNER TO postgres;

--
-- Name: exchange_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.exchange_transactions_id_seq OWNED BY public.exchange_transactions.id;


--
-- Name: expense_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expense_types (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    is_active boolean NOT NULL,
    code character varying(50),
    fields_meta json,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.expense_types OWNER TO postgres;

--
-- Name: expense_types_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expense_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.expense_types_id_seq OWNER TO postgres;

--
-- Name: expense_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expense_types_id_seq OWNED BY public.expense_types.id;


--
-- Name: expenses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expenses (
    id integer NOT NULL,
    date timestamp without time zone NOT NULL,
    amount numeric(12,2) NOT NULL,
    currency character varying(10) NOT NULL,
    fx_rate_used numeric(10,6),
    fx_rate_source character varying(20),
    fx_rate_timestamp timestamp without time zone,
    fx_base_currency character varying(10),
    fx_quote_currency character varying(10),
    type_id integer NOT NULL,
    branch_id integer NOT NULL,
    site_id integer,
    employee_id integer,
    customer_id integer,
    warehouse_id integer,
    partner_id integer,
    supplier_id integer,
    shipment_id integer,
    utility_account_id integer,
    stock_adjustment_id integer,
    payee_type character varying(20) NOT NULL,
    payee_entity_id integer,
    payee_name character varying(200),
    beneficiary_name character varying(200),
    paid_to character varying(200),
    disbursed_by character varying(200),
    period_start date,
    period_end date,
    payment_method character varying(20) NOT NULL,
    payment_details text,
    description character varying(200),
    notes text,
    tax_invoice_number character varying(100),
    check_number character varying(100),
    check_bank character varying(100),
    check_due_date date,
    check_payee character varying(200),
    bank_transfer_ref character varying(100),
    bank_name character varying(100),
    account_number character varying(100),
    account_holder character varying(200),
    card_number character varying(8),
    card_holder character varying(120),
    card_expiry character varying(10),
    online_gateway character varying(50),
    online_ref character varying(100),
    telecom_phone_number character varying(30),
    telecom_service_type character varying(20),
    insurance_company_name character varying(200),
    insurance_company_address character varying(200),
    insurance_company_phone character varying(30),
    marketing_company_name character varying(200),
    marketing_company_address character varying(200),
    marketing_coverage_details character varying(200),
    bank_fee_bank_name character varying(200),
    bank_fee_notes text,
    gov_fee_entity_name character varying(200),
    gov_fee_entity_address character varying(200),
    gov_fee_notes text,
    port_fee_port_name character varying(200),
    port_fee_notes text,
    travel_destination character varying(200),
    travel_reason character varying(200),
    travel_notes text,
    shipping_company_name character varying(200),
    shipping_notes text,
    maintenance_provider_name character varying(200),
    maintenance_provider_address character varying(200),
    maintenance_notes text,
    rent_property_address character varying(200),
    rent_property_notes text,
    tech_provider_name character varying(200),
    tech_provider_phone character varying(30),
    tech_provider_address character varying(200),
    tech_subscription_id character varying(100),
    storage_property_address character varying(200),
    storage_expected_days integer,
    storage_start_date date,
    storage_notes text,
    customs_arrival_date date,
    customs_departure_date date,
    customs_origin character varying(200),
    customs_port_name character varying(200),
    customs_notes text,
    training_company_name character varying(200),
    training_location character varying(200),
    training_duration_days integer,
    training_participants_count integer,
    training_notes text,
    training_participants_names text,
    training_topics text,
    entertainment_duration_days integer,
    entertainment_notes text,
    bank_fee_reference character varying(100),
    bank_fee_contact_name character varying(200),
    bank_fee_contact_phone character varying(30),
    gov_fee_reference character varying(100),
    port_fee_reference character varying(100),
    port_fee_agent_name character varying(200),
    port_fee_agent_phone character varying(30),
    salary_notes text,
    salary_reference character varying(100),
    travel_duration_days integer,
    travel_start_date date,
    travel_companions text,
    travel_cost_center character varying(100),
    employee_advance_period character varying(100),
    employee_advance_reason character varying(200),
    employee_advance_notes text,
    shipping_date date,
    shipping_reference character varying(100),
    shipping_mode character varying(50),
    shipping_tracking_number character varying(100),
    maintenance_details text,
    maintenance_completion_date date,
    maintenance_technician_name character varying(200),
    import_tax_reference character varying(100),
    import_tax_notes text,
    hospitality_type character varying(20),
    hospitality_notes text,
    hospitality_attendees text,
    hospitality_location character varying(200),
    telecom_notes text,
    office_supplier_name character varying(200),
    office_notes text,
    office_items_list text,
    office_purchase_reference character varying(100),
    home_relation_to_company character varying(100),
    home_address character varying(200),
    home_owner_name character varying(200),
    home_notes text,
    home_cost_share numeric(12,2),
    partner_expense_reason character varying(200),
    partner_expense_notes text,
    partner_expense_reference character varying(100),
    supplier_expense_reason character varying(200),
    supplier_expense_notes text,
    supplier_expense_reference character varying(100),
    handling_notes text,
    handling_quantity numeric(12,2),
    handling_unit character varying(50),
    handling_reference character varying(100),
    fuel_vehicle_number character varying(50),
    fuel_driver_name character varying(100),
    fuel_usage_type character varying(20),
    fuel_volume numeric(12,3),
    fuel_notes text,
    fuel_station_name character varying(200),
    fuel_odometer_start integer,
    fuel_odometer_end integer,
    transport_beneficiary_name character varying(200),
    transport_reason character varying(200),
    transport_usage_type character varying(20),
    transport_notes text,
    transport_route_details text,
    insurance_policy_number character varying(100),
    insurance_notes text,
    legal_company_name character varying(200),
    legal_company_address character varying(200),
    legal_case_notes text,
    legal_case_number character varying(100),
    legal_case_type character varying(100),
    is_archived boolean NOT NULL,
    archived_at timestamp without time zone,
    archived_by integer,
    archive_reason character varying(200),
    cost_center_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_expense_amount_non_negative CHECK ((amount >= (0)::numeric)),
    CONSTRAINT chk_expense_payment_method_allowed CHECK (((payment_method)::text = ANY ((ARRAY['cash'::character varying, 'cheque'::character varying, 'bank'::character varying, 'card'::character varying, 'online'::character varying, 'other'::character varying])::text[]))),
    CONSTRAINT ck_expense_payee_type_allowed CHECK (((payee_type)::text = ANY ((ARRAY['EMPLOYEE'::character varying, 'SUPPLIER'::character varying, 'PARTNER'::character varying, 'UTILITY'::character varying, 'OTHER'::character varying])::text[])))
);


ALTER TABLE public.expenses OWNER TO postgres;

--
-- Name: expenses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expenses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.expenses_id_seq OWNER TO postgres;

--
-- Name: expenses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expenses_id_seq OWNED BY public.expenses.id;


--
-- Name: fixed_asset_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fixed_asset_categories (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(100) NOT NULL,
    account_code character varying(20) NOT NULL,
    depreciation_account_code character varying(20) NOT NULL,
    useful_life_years integer NOT NULL,
    depreciation_method character varying(17) NOT NULL,
    depreciation_rate numeric(5,2),
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_depreciation_rate_range CHECK (((depreciation_rate >= (0)::numeric) AND (depreciation_rate <= (100)::numeric))),
    CONSTRAINT ck_useful_life_gt_0 CHECK ((useful_life_years > 0))
);


ALTER TABLE public.fixed_asset_categories OWNER TO postgres;

--
-- Name: fixed_asset_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fixed_asset_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fixed_asset_categories_id_seq OWNER TO postgres;

--
-- Name: fixed_asset_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fixed_asset_categories_id_seq OWNED BY public.fixed_asset_categories.id;


--
-- Name: fixed_assets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fixed_assets (
    id integer NOT NULL,
    asset_number character varying(50) NOT NULL,
    name character varying(200) NOT NULL,
    category_id integer NOT NULL,
    branch_id integer,
    site_id integer,
    purchase_date date NOT NULL,
    purchase_price numeric(12,2) NOT NULL,
    supplier_id integer,
    serial_number character varying(100),
    barcode character varying(100),
    location character varying(200),
    status character varying(8) NOT NULL,
    disposal_date date,
    disposal_amount numeric(12,2),
    disposal_notes text,
    notes text,
    is_archived boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_asset_price_ge_0 CHECK ((purchase_price >= (0)::numeric))
);


ALTER TABLE public.fixed_assets OWNER TO postgres;

--
-- Name: fixed_assets_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fixed_assets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fixed_assets_id_seq OWNER TO postgres;

--
-- Name: fixed_assets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fixed_assets_id_seq OWNED BY public.fixed_assets.id;


--
-- Name: gl_batches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gl_batches (
    id integer NOT NULL,
    code character varying(50),
    source_type character varying(30),
    source_id integer,
    purpose character varying(30),
    memo character varying(255),
    posted_at timestamp without time zone,
    currency character varying(10) NOT NULL,
    entity_type character varying(30),
    entity_id integer,
    status character varying(6) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.gl_batches OWNER TO postgres;

--
-- Name: gl_batches_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gl_batches_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.gl_batches_id_seq OWNER TO postgres;

--
-- Name: gl_batches_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gl_batches_id_seq OWNED BY public.gl_batches.id;


--
-- Name: gl_entries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gl_entries (
    id integer NOT NULL,
    batch_id integer NOT NULL,
    account character varying(20) NOT NULL,
    debit numeric(12,2) NOT NULL,
    credit numeric(12,2) NOT NULL,
    currency character varying(10) NOT NULL,
    ref character varying(100),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_gl_credit_ge_0 CHECK ((credit >= (0)::numeric)),
    CONSTRAINT ck_gl_debit_ge_0 CHECK ((debit >= (0)::numeric)),
    CONSTRAINT ck_gl_entry_nonzero CHECK (((debit > (0)::numeric) OR (credit > (0)::numeric))),
    CONSTRAINT ck_gl_entry_one_side CHECK (((debit = (0)::numeric) OR (credit = (0)::numeric)))
);


ALTER TABLE public.gl_entries OWNER TO postgres;

--
-- Name: gl_entries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gl_entries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.gl_entries_id_seq OWNER TO postgres;

--
-- Name: gl_entries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gl_entries_id_seq OWNED BY public.gl_entries.id;


--
-- Name: import_runs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.import_runs (
    id integer NOT NULL,
    warehouse_id integer,
    user_id integer,
    filename character varying(255),
    file_sha256 character varying(64),
    dry_run boolean DEFAULT false NOT NULL,
    inserted integer DEFAULT 0 NOT NULL,
    updated integer DEFAULT 0 NOT NULL,
    skipped integer DEFAULT 0 NOT NULL,
    errors integer DEFAULT 0 NOT NULL,
    duration_ms integer DEFAULT 0 NOT NULL,
    report_path character varying(255),
    notes character varying(255),
    meta json,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.import_runs OWNER TO postgres;

--
-- Name: import_runs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.import_runs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.import_runs_id_seq OWNER TO postgres;

--
-- Name: import_runs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.import_runs_id_seq OWNED BY public.import_runs.id;


--
-- Name: invoice_lines; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.invoice_lines (
    id integer NOT NULL,
    invoice_id integer NOT NULL,
    description character varying(200) NOT NULL,
    quantity double precision NOT NULL,
    unit_price numeric(12,2) NOT NULL,
    tax_rate numeric(5,2) NOT NULL,
    discount numeric(5,2) NOT NULL,
    product_id integer,
    CONSTRAINT ck_invoice_line_discount_range CHECK (((discount >= (0)::numeric) AND (discount <= (100)::numeric))),
    CONSTRAINT ck_invoice_line_quantity_non_negative CHECK ((quantity >= (0)::double precision)),
    CONSTRAINT ck_invoice_line_tax_rate_range CHECK (((tax_rate >= (0)::numeric) AND (tax_rate <= (100)::numeric))),
    CONSTRAINT ck_invoice_line_unit_price_non_negative CHECK ((unit_price >= (0)::numeric))
);


ALTER TABLE public.invoice_lines OWNER TO postgres;

--
-- Name: invoice_lines_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.invoice_lines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.invoice_lines_id_seq OWNER TO postgres;

--
-- Name: invoice_lines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.invoice_lines_id_seq OWNED BY public.invoice_lines.id;


--
-- Name: invoices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.invoices (
    id integer NOT NULL,
    invoice_number character varying(50) NOT NULL,
    invoice_date timestamp without time zone NOT NULL,
    due_date timestamp without time zone,
    customer_id integer NOT NULL,
    supplier_id integer,
    partner_id integer,
    sale_id integer,
    service_id integer,
    preorder_id integer,
    source character varying(8) NOT NULL,
    kind character varying(11) NOT NULL,
    credit_for_id integer,
    refund_of_id integer,
    currency character varying(10) NOT NULL,
    fx_rate_used numeric(10,6),
    fx_rate_source character varying(20),
    fx_rate_timestamp timestamp without time zone,
    fx_base_currency character varying(10),
    fx_quote_currency character varying(10),
    total_amount numeric(12,2) NOT NULL,
    tax_amount numeric(12,2) NOT NULL,
    discount_amount numeric(12,2) NOT NULL,
    notes text,
    terms text,
    refunded_total numeric(12,2) NOT NULL,
    idempotency_key character varying(64),
    cancelled_at timestamp without time zone,
    cancelled_by integer,
    cancel_reason character varying(200),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.invoices OWNER TO postgres;

--
-- Name: invoices_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.invoices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.invoices_id_seq OWNER TO postgres;

--
-- Name: invoices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.invoices_id_seq OWNED BY public.invoices.id;


--
-- Name: notes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notes (
    id integer NOT NULL,
    content text NOT NULL,
    author_id integer,
    entity_type character varying(50),
    entity_id character varying(50),
    is_pinned boolean DEFAULT false NOT NULL,
    priority character varying(6) NOT NULL,
    target_type character varying(50),
    target_ids text,
    notification_type character varying(50),
    notification_date timestamp without time zone,
    is_sent boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.notes OWNER TO postgres;

--
-- Name: notes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notes_id_seq OWNER TO postgres;

--
-- Name: notes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notes_id_seq OWNED BY public.notes.id;


--
-- Name: notification_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification_logs (
    id integer NOT NULL,
    type character varying(20) NOT NULL,
    recipient character varying(255) NOT NULL,
    subject character varying(500),
    content text,
    status character varying(20) NOT NULL,
    provider_id character varying(100),
    error_message text,
    extra_data text,
    sent_at timestamp without time zone,
    delivered_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    customer_id integer,
    user_id integer
);


ALTER TABLE public.notification_logs OWNER TO postgres;

--
-- Name: notification_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notification_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notification_logs_id_seq OWNER TO postgres;

--
-- Name: notification_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notification_logs_id_seq OWNED BY public.notification_logs.id;


--
-- Name: online_cart_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.online_cart_items (
    id integer NOT NULL,
    cart_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity integer NOT NULL,
    price numeric(12,2) NOT NULL,
    added_at timestamp without time zone,
    CONSTRAINT chk_cart_item_price_non_negative CHECK ((price >= (0)::numeric)),
    CONSTRAINT chk_cart_item_qty_positive CHECK ((quantity > 0))
);


ALTER TABLE public.online_cart_items OWNER TO postgres;

--
-- Name: online_cart_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.online_cart_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.online_cart_items_id_seq OWNER TO postgres;

--
-- Name: online_cart_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.online_cart_items_id_seq OWNED BY public.online_cart_items.id;


--
-- Name: online_carts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.online_carts (
    id integer NOT NULL,
    cart_id character varying(50),
    customer_id integer,
    session_id character varying(100),
    status character varying(9) NOT NULL,
    expires_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.online_carts OWNER TO postgres;

--
-- Name: online_carts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.online_carts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.online_carts_id_seq OWNER TO postgres;

--
-- Name: online_carts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.online_carts_id_seq OWNED BY public.online_carts.id;


--
-- Name: online_payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.online_payments (
    id integer NOT NULL,
    payment_ref character varying(100),
    order_id integer NOT NULL,
    amount numeric(12,2) NOT NULL,
    currency character varying(10) NOT NULL,
    fx_rate_used numeric(10,6),
    fx_rate_source character varying(20),
    fx_rate_timestamp timestamp without time zone,
    fx_base_currency character varying(10),
    fx_quote_currency character varying(10),
    method character varying(50),
    gateway character varying(50),
    status character varying(8) NOT NULL,
    transaction_data json,
    processed_at timestamp without time zone,
    card_last4 character varying(4),
    card_encrypted bytea,
    card_expiry character varying(5),
    cardholder_name character varying(128),
    card_brand character varying(20),
    card_fingerprint character varying(64),
    payment_id integer,
    idempotency_key character varying(64),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_online_payment_amount_positive CHECK ((amount > (0)::numeric))
);


ALTER TABLE public.online_payments OWNER TO postgres;

--
-- Name: online_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.online_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.online_payments_id_seq OWNER TO postgres;

--
-- Name: online_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.online_payments_id_seq OWNED BY public.online_payments.id;


--
-- Name: online_preorder_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.online_preorder_items (
    id integer NOT NULL,
    order_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity integer NOT NULL,
    price numeric(12,2) NOT NULL,
    CONSTRAINT chk_online_item_price_non_negative CHECK ((price >= (0)::numeric)),
    CONSTRAINT chk_online_item_qty_positive CHECK ((quantity > 0))
);


ALTER TABLE public.online_preorder_items OWNER TO postgres;

--
-- Name: online_preorder_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.online_preorder_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.online_preorder_items_id_seq OWNER TO postgres;

--
-- Name: online_preorder_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.online_preorder_items_id_seq OWNED BY public.online_preorder_items.id;


--
-- Name: online_preorders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.online_preorders (
    id integer NOT NULL,
    order_number character varying(50),
    customer_id integer NOT NULL,
    cart_id integer,
    warehouse_id integer,
    prepaid_amount numeric(12,2),
    total_amount numeric(12,2),
    base_amount numeric(12,2),
    tax_rate numeric(5,2),
    tax_amount numeric(12,2),
    currency character varying(10) NOT NULL,
    fx_rate_used numeric(10,6),
    fx_rate_source character varying(20),
    fx_rate_timestamp timestamp without time zone,
    fx_base_currency character varying(10),
    fx_quote_currency character varying(10),
    expected_fulfillment timestamp without time zone,
    actual_fulfillment timestamp without time zone,
    status character varying(9) NOT NULL,
    payment_status character varying(7) NOT NULL,
    payment_method character varying(50),
    notes text,
    shipping_address text,
    billing_address text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_online_base_non_negative CHECK ((base_amount >= (0)::numeric)),
    CONSTRAINT chk_online_prepaid_non_negative CHECK ((prepaid_amount >= (0)::numeric)),
    CONSTRAINT chk_online_tax_non_negative CHECK ((tax_amount >= (0)::numeric)),
    CONSTRAINT chk_online_tax_rate_0_100 CHECK (((tax_rate >= (0)::numeric) AND (tax_rate <= (100)::numeric))),
    CONSTRAINT chk_online_total_non_negative CHECK ((total_amount >= (0)::numeric))
);


ALTER TABLE public.online_preorders OWNER TO postgres;

--
-- Name: online_preorders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.online_preorders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.online_preorders_id_seq OWNER TO postgres;

--
-- Name: online_preorders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.online_preorders_id_seq OWNED BY public.online_preorders.id;


--
-- Name: partner_settlement_lines; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.partner_settlement_lines (
    id integer NOT NULL,
    settlement_id integer NOT NULL,
    source_type character varying(30) NOT NULL,
    source_id integer,
    description character varying(255),
    product_id integer,
    warehouse_id integer,
    quantity numeric(12,3),
    unit_price numeric(12,2),
    gross_amount numeric(12,2),
    share_percent numeric(6,3),
    share_amount numeric(12,2),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.partner_settlement_lines OWNER TO postgres;

--
-- Name: partner_settlement_lines_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.partner_settlement_lines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.partner_settlement_lines_id_seq OWNER TO postgres;

--
-- Name: partner_settlement_lines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.partner_settlement_lines_id_seq OWNED BY public.partner_settlement_lines.id;


--
-- Name: partner_settlements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.partner_settlements (
    id integer NOT NULL,
    code character varying(40),
    partner_id integer NOT NULL,
    from_date timestamp without time zone NOT NULL,
    to_date timestamp without time zone NOT NULL,
    currency character varying(10) NOT NULL,
    fx_rate_used numeric(10,6),
    fx_rate_source character varying(20),
    fx_rate_timestamp timestamp without time zone,
    fx_base_currency character varying(10),
    fx_quote_currency character varying(10),
    status character varying(9) NOT NULL,
    notes text,
    total_gross numeric(12,2) NOT NULL,
    total_share numeric(12,2) NOT NULL,
    total_costs numeric(12,2) NOT NULL,
    total_due numeric(12,2) NOT NULL,
    previous_settlement_id integer,
    opening_balance numeric(12,2) DEFAULT 0 NOT NULL,
    rights_inventory numeric(12,2) DEFAULT 0 NOT NULL,
    rights_sales_share numeric(12,2) DEFAULT 0 NOT NULL,
    rights_preorders numeric(12,2) DEFAULT 0 NOT NULL,
    rights_total numeric(12,2) DEFAULT 0 NOT NULL,
    obligations_sales_to_partner numeric(12,2) DEFAULT 0 NOT NULL,
    obligations_services numeric(12,2) DEFAULT 0 NOT NULL,
    obligations_damaged numeric(12,2) DEFAULT 0 NOT NULL,
    obligations_expenses numeric(12,2) DEFAULT 0 NOT NULL,
    obligations_returns numeric(12,2) DEFAULT 0 NOT NULL,
    obligations_total numeric(12,2) DEFAULT 0 NOT NULL,
    payments_out numeric(12,2) DEFAULT 0 NOT NULL,
    payments_in numeric(12,2) DEFAULT 0 NOT NULL,
    payments_net numeric(12,2) DEFAULT 0 NOT NULL,
    closing_balance numeric(12,2) DEFAULT 0 NOT NULL,
    is_approved boolean DEFAULT false NOT NULL,
    approved_by integer,
    approved_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.partner_settlements OWNER TO postgres;

--
-- Name: partner_settlements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.partner_settlements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.partner_settlements_id_seq OWNER TO postgres;

--
-- Name: partner_settlements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.partner_settlements_id_seq OWNED BY public.partner_settlements.id;


--
-- Name: partners; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.partners (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    contact_info character varying(200),
    identity_number character varying(100),
    phone_number character varying(20),
    email character varying(120),
    address character varying(200),
    share_percentage numeric(5,2) DEFAULT 0 NOT NULL,
    currency character varying(10) DEFAULT 'ILS'::character varying NOT NULL,
    opening_balance numeric(12,2) DEFAULT 0 NOT NULL,
    current_balance numeric(12,2) DEFAULT 0 NOT NULL,
    inventory_balance numeric(12,2) DEFAULT 0 NOT NULL,
    sales_share_balance numeric(12,2) DEFAULT 0 NOT NULL,
    sales_to_partner_balance numeric(12,2) DEFAULT 0 NOT NULL,
    service_fees_balance numeric(12,2) DEFAULT 0 NOT NULL,
    preorders_to_partner_balance numeric(12,2) DEFAULT 0 NOT NULL,
    preorders_prepaid_balance numeric(12,2) DEFAULT 0 NOT NULL,
    damaged_items_balance numeric(12,2) DEFAULT 0 NOT NULL,
    payments_in_balance numeric(12,2) DEFAULT 0 NOT NULL,
    payments_out_balance numeric(12,2) DEFAULT 0 NOT NULL,
    returned_checks_in_balance numeric(12,2) DEFAULT 0 NOT NULL,
    returned_checks_out_balance numeric(12,2) DEFAULT 0 NOT NULL,
    expenses_balance numeric(12,2) DEFAULT 0 NOT NULL,
    service_expenses_balance numeric(12,2) DEFAULT 0 NOT NULL,
    notes text,
    customer_id integer,
    is_archived boolean NOT NULL,
    archived_at timestamp without time zone,
    archived_by integer,
    archive_reason character varying(200),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.partners OWNER TO postgres;

--
-- Name: COLUMN partners.opening_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.partners.opening_balance IS 'الرصيد الافتتاحي (موجب=له رصيد عندنا، سالب=لنا رصيد عنده)';


--
-- Name: COLUMN partners.current_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.partners.current_balance IS 'الرصيد الحالي المحدث';


--
-- Name: COLUMN partners.inventory_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.partners.inventory_balance IS 'رصيد المخزون';


--
-- Name: COLUMN partners.sales_share_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.partners.sales_share_balance IS 'رصيد نصيب المبيعات';


--
-- Name: COLUMN partners.sales_to_partner_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.partners.sales_to_partner_balance IS 'رصيد المبيعات له';


--
-- Name: COLUMN partners.service_fees_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.partners.service_fees_balance IS 'رصيد رسوم الصيانة';


--
-- Name: COLUMN partners.preorders_to_partner_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.partners.preorders_to_partner_balance IS 'رصيد الحجوزات له';


--
-- Name: COLUMN partners.preorders_prepaid_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.partners.preorders_prepaid_balance IS 'رصيد العربونات المدفوعة';


--
-- Name: COLUMN partners.damaged_items_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.partners.damaged_items_balance IS 'رصيد القطع التالفة';


--
-- Name: COLUMN partners.payments_in_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.partners.payments_in_balance IS 'رصيد الدفعات الواردة';


--
-- Name: COLUMN partners.payments_out_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.partners.payments_out_balance IS 'رصيد الدفعات الصادرة';


--
-- Name: COLUMN partners.returned_checks_in_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.partners.returned_checks_in_balance IS 'رصيد الشيكات المرتدة الواردة';


--
-- Name: COLUMN partners.returned_checks_out_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.partners.returned_checks_out_balance IS 'رصيد الشيكات المرتدة الصادرة';


--
-- Name: COLUMN partners.expenses_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.partners.expenses_balance IS 'رصيد المصروفات العادية (تُطرح)';


--
-- Name: COLUMN partners.service_expenses_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.partners.service_expenses_balance IS 'رصيد توريد الخدمة (تُضاف)';


--
-- Name: partners_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.partners_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.partners_id_seq OWNER TO postgres;

--
-- Name: partners_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.partners_id_seq OWNED BY public.partners.id;


--
-- Name: payment_splits; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payment_splits (
    id integer NOT NULL,
    payment_id integer NOT NULL,
    method character varying(6) NOT NULL,
    amount numeric(12,2) NOT NULL,
    details json NOT NULL,
    currency character varying(10) NOT NULL,
    converted_amount numeric(12,2) NOT NULL,
    converted_currency character varying(10) NOT NULL,
    fx_rate_used numeric(10,6),
    fx_rate_source character varying(20),
    fx_rate_timestamp timestamp without time zone,
    fx_base_currency character varying(10),
    fx_quote_currency character varying(10),
    CONSTRAINT chk_split_amount_positive CHECK ((amount > (0)::numeric))
);


ALTER TABLE public.payment_splits OWNER TO postgres;

--
-- Name: payment_splits_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payment_splits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payment_splits_id_seq OWNER TO postgres;

--
-- Name: payment_splits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payment_splits_id_seq OWNED BY public.payment_splits.id;


--
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    id integer NOT NULL,
    payment_number character varying(50) NOT NULL,
    payment_date timestamp without time zone NOT NULL,
    subtotal numeric(12,2),
    tax_rate numeric(5,2),
    tax_amount numeric(12,2),
    total_amount numeric(12,2) NOT NULL,
    currency character varying(10) NOT NULL,
    fx_rate_used numeric(10,6),
    fx_rate_source character varying(20),
    fx_rate_timestamp timestamp without time zone,
    fx_base_currency character varying(10),
    fx_quote_currency character varying(10),
    method character varying(6) NOT NULL,
    status character varying(9) NOT NULL,
    direction character varying(3) NOT NULL,
    entity_type character varying(13) NOT NULL,
    reference character varying(100),
    receipt_number character varying(50),
    notes text,
    receiver_name character varying(200),
    deliverer_name character varying(200),
    check_number character varying(100),
    check_bank character varying(100),
    check_due_date timestamp without time zone,
    card_holder character varying(100),
    card_expiry character varying(10),
    card_last4 character varying(4),
    bank_transfer_ref character varying(100),
    created_by integer,
    customer_id integer,
    supplier_id integer,
    partner_id integer,
    shipment_id integer,
    expense_id integer,
    loan_settlement_id integer,
    sale_id integer,
    invoice_id integer,
    preorder_id integer,
    service_id integer,
    refund_of_id integer,
    idempotency_key character varying(64),
    is_archived boolean NOT NULL,
    archived_at timestamp without time zone,
    archived_by integer,
    archive_reason character varying(200),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_payment_one_target CHECK (((((((((((
CASE
    WHEN (customer_id IS NOT NULL) THEN 1
    ELSE 0
END +
CASE
    WHEN (supplier_id IS NOT NULL) THEN 1
    ELSE 0
END) +
CASE
    WHEN (partner_id IS NOT NULL) THEN 1
    ELSE 0
END) +
CASE
    WHEN (shipment_id IS NOT NULL) THEN 1
    ELSE 0
END) +
CASE
    WHEN (expense_id IS NOT NULL) THEN 1
    ELSE 0
END) +
CASE
    WHEN (loan_settlement_id IS NOT NULL) THEN 1
    ELSE 0
END) +
CASE
    WHEN (sale_id IS NOT NULL) THEN 1
    ELSE 0
END) +
CASE
    WHEN (invoice_id IS NOT NULL) THEN 1
    ELSE 0
END) +
CASE
    WHEN (preorder_id IS NOT NULL) THEN 1
    ELSE 0
END) +
CASE
    WHEN (service_id IS NOT NULL) THEN 1
    ELSE 0
END) <= 1)),
    CONSTRAINT ck_payment_total_positive CHECK ((total_amount > (0)::numeric))
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- Name: payments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payments_id_seq OWNER TO postgres;

--
-- Name: payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payments_id_seq OWNED BY public.payments.id;


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permissions (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(100),
    description character varying(255),
    name_ar character varying(120),
    module character varying(50),
    is_protected boolean DEFAULT false NOT NULL,
    aliases json
);


ALTER TABLE public.permissions OWNER TO postgres;

--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.permissions_id_seq OWNER TO postgres;

--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.permissions_id_seq OWNED BY public.permissions.id;


--
-- Name: preorders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.preorders (
    id integer NOT NULL,
    reference character varying(50),
    preorder_date timestamp without time zone,
    expected_date timestamp without time zone,
    customer_id integer,
    supplier_id integer,
    partner_id integer,
    product_id integer NOT NULL,
    warehouse_id integer NOT NULL,
    quantity integer NOT NULL,
    prepaid_amount numeric(12,2) DEFAULT 0,
    tax_rate numeric(5,2) DEFAULT 0,
    status character varying(9) DEFAULT 'PENDING'::character varying NOT NULL,
    notes text,
    payment_method character varying(6) DEFAULT 'cash'::character varying NOT NULL,
    currency character varying(10) DEFAULT 'ILS'::character varying NOT NULL,
    fx_rate_used numeric(10,6),
    fx_rate_source character varying(20),
    fx_rate_timestamp timestamp without time zone,
    fx_base_currency character varying(10),
    fx_quote_currency character varying(10),
    refunded_total numeric(12,2) DEFAULT 0 NOT NULL,
    refund_of_id integer,
    idempotency_key character varying(64),
    cancelled_at timestamp without time zone,
    cancelled_by integer,
    cancel_reason character varying(200),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_preorder_prepaid_non_negative CHECK ((prepaid_amount >= (0)::numeric)),
    CONSTRAINT chk_preorder_quantity_positive CHECK ((quantity > 0)),
    CONSTRAINT chk_preorder_refunded_total_non_negative CHECK ((refunded_total >= (0)::numeric)),
    CONSTRAINT chk_preorder_tax_rate CHECK (((tax_rate >= (0)::numeric) AND (tax_rate <= (100)::numeric)))
);


ALTER TABLE public.preorders OWNER TO postgres;

--
-- Name: preorders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.preorders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.preorders_id_seq OWNER TO postgres;

--
-- Name: preorders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.preorders_id_seq OWNED BY public.preorders.id;


--
-- Name: product_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    parent_id integer,
    description text,
    image_url character varying(255),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.product_categories OWNER TO postgres;

--
-- Name: product_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.product_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_categories_id_seq OWNER TO postgres;

--
-- Name: product_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.product_categories_id_seq OWNED BY public.product_categories.id;


--
-- Name: product_partners; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_partners (
    id integer NOT NULL,
    product_id integer NOT NULL,
    partner_id integer NOT NULL,
    share_percent double precision NOT NULL,
    share_amount numeric(12,2),
    notes text,
    CONSTRAINT chk_partner_share CHECK (((share_percent >= (0)::double precision) AND (share_percent <= (100)::double precision))),
    CONSTRAINT ck_product_partner_share_amount_non_negative CHECK ((share_amount >= (0)::numeric))
);


ALTER TABLE public.product_partners OWNER TO postgres;

--
-- Name: product_partners_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.product_partners_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_partners_id_seq OWNER TO postgres;

--
-- Name: product_partners_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.product_partners_id_seq OWNED BY public.product_partners.id;


--
-- Name: product_rating_helpful; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_rating_helpful (
    id integer NOT NULL,
    rating_id integer NOT NULL,
    customer_id integer,
    ip_address character varying(45),
    is_helpful boolean NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.product_rating_helpful OWNER TO postgres;

--
-- Name: product_rating_helpful_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.product_rating_helpful_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_rating_helpful_id_seq OWNER TO postgres;

--
-- Name: product_rating_helpful_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.product_rating_helpful_id_seq OWNED BY public.product_rating_helpful.id;


--
-- Name: product_ratings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_ratings (
    id integer NOT NULL,
    product_id integer NOT NULL,
    customer_id integer,
    rating integer NOT NULL,
    title character varying(255),
    comment text,
    is_verified_purchase boolean NOT NULL,
    is_approved boolean NOT NULL,
    helpful_count integer NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_rating_range CHECK (((rating >= 1) AND (rating <= 5)))
);


ALTER TABLE public.product_ratings OWNER TO postgres;

--
-- Name: product_ratings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.product_ratings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_ratings_id_seq OWNER TO postgres;

--
-- Name: product_ratings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.product_ratings_id_seq OWNED BY public.product_ratings.id;


--
-- Name: product_supplier_loans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_supplier_loans (
    id integer NOT NULL,
    product_id integer NOT NULL,
    supplier_id integer NOT NULL,
    loan_value numeric(12,2) NOT NULL,
    deferred_price numeric(12,2),
    is_settled boolean,
    partner_share_quantity integer NOT NULL,
    partner_share_value numeric(12,2) NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_psl_deferred_price_ge_0 CHECK (((deferred_price IS NULL) OR (deferred_price >= (0)::numeric))),
    CONSTRAINT ck_psl_loan_value_ge_0 CHECK ((loan_value >= (0)::numeric)),
    CONSTRAINT ck_psl_share_qty_ge_0 CHECK ((partner_share_quantity >= 0)),
    CONSTRAINT ck_psl_share_val_ge_0 CHECK ((partner_share_value >= (0)::numeric))
);


ALTER TABLE public.product_supplier_loans OWNER TO postgres;

--
-- Name: product_supplier_loans_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.product_supplier_loans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_supplier_loans_id_seq OWNER TO postgres;

--
-- Name: product_supplier_loans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.product_supplier_loans_id_seq OWNED BY public.product_supplier_loans.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    id integer NOT NULL,
    sku character varying(50),
    name character varying(255) NOT NULL,
    description text,
    part_number character varying(100),
    brand character varying(100),
    commercial_name character varying(100),
    chassis_number character varying(100),
    serial_no character varying(100),
    barcode character varying(100),
    unit character varying(50),
    category_name character varying(100),
    purchase_price numeric(12,2) DEFAULT 0 NOT NULL,
    selling_price numeric(12,2) DEFAULT 0 NOT NULL,
    cost_before_shipping numeric(12,2) DEFAULT 0 NOT NULL,
    cost_after_shipping numeric(12,2) DEFAULT 0 NOT NULL,
    unit_price_before_tax numeric(12,2) DEFAULT 0 NOT NULL,
    price numeric(12,2) DEFAULT 0 NOT NULL,
    min_price numeric(12,2),
    max_price numeric(12,2),
    tax_rate numeric(5,2) DEFAULT 0 NOT NULL,
    min_qty integer DEFAULT 0 NOT NULL,
    reorder_point integer,
    image character varying(255),
    notes text,
    condition character varying(11) DEFAULT 'NEW'::character varying NOT NULL,
    origin_country character varying(50),
    warranty_period integer,
    weight numeric(10,2),
    dimensions character varying(50),
    is_active boolean DEFAULT true NOT NULL,
    is_digital boolean DEFAULT false NOT NULL,
    is_exchange boolean DEFAULT false NOT NULL,
    is_published boolean DEFAULT true NOT NULL,
    vehicle_type_id integer,
    category_id integer,
    supplier_id integer,
    supplier_international_id integer,
    supplier_local_id integer,
    online_name character varying(255),
    online_price numeric(12,2) DEFAULT 0,
    online_image character varying(255),
    currency character varying(10) DEFAULT 'ILS'::character varying NOT NULL,
    fx_rate_used numeric(10,6),
    fx_rate_source character varying(20),
    fx_rate_timestamp timestamp without time zone,
    fx_base_currency character varying(10),
    fx_quote_currency character varying(10),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_product_cost_after_ge_0 CHECK ((cost_after_shipping >= (0)::numeric)),
    CONSTRAINT ck_product_cost_before_ge_0 CHECK ((cost_before_shipping >= (0)::numeric)),
    CONSTRAINT ck_product_max_price_ge_0 CHECK (((max_price IS NULL) OR (max_price >= (0)::numeric))),
    CONSTRAINT ck_product_min_price_ge_0 CHECK (((min_price IS NULL) OR (min_price >= (0)::numeric))),
    CONSTRAINT ck_product_min_qty_ge_0 CHECK ((min_qty >= 0)),
    CONSTRAINT ck_product_online_price_ge_0 CHECK (((online_price IS NULL) OR (online_price >= (0)::numeric))),
    CONSTRAINT ck_product_price_ge_0 CHECK ((price >= (0)::numeric)),
    CONSTRAINT ck_product_purchase_ge_0 CHECK ((purchase_price >= (0)::numeric)),
    CONSTRAINT ck_product_reorder_ge_0 CHECK (((reorder_point IS NULL) OR (reorder_point >= 0))),
    CONSTRAINT ck_product_selling_ge_0 CHECK ((selling_price >= (0)::numeric)),
    CONSTRAINT ck_product_tax_rate_0_100 CHECK (((tax_rate >= (0)::numeric) AND (tax_rate <= (100)::numeric))),
    CONSTRAINT ck_product_unit_before_tax_ge_0 CHECK ((unit_price_before_tax >= (0)::numeric)),
    CONSTRAINT ck_product_weight_ge_0 CHECK (((weight IS NULL) OR (weight >= (0)::numeric)))
);


ALTER TABLE public.products OWNER TO postgres;

--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_id_seq OWNER TO postgres;

--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: project_change_orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_change_orders (
    id integer NOT NULL,
    project_id integer NOT NULL,
    change_number character varying(50) NOT NULL,
    title character varying(300) NOT NULL,
    description text NOT NULL,
    requested_by integer,
    requested_date date NOT NULL,
    reason text,
    scope_change text,
    cost_impact numeric(15,2),
    schedule_impact_days integer,
    status character varying(12) NOT NULL,
    approved_by integer,
    approved_date date,
    implemented_date date,
    rejection_reason text,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_change_cost_not_null CHECK ((cost_impact IS NOT NULL)),
    CONSTRAINT ck_change_schedule_ge_0 CHECK ((schedule_impact_days >= 0))
);


ALTER TABLE public.project_change_orders OWNER TO postgres;

--
-- Name: project_change_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_change_orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.project_change_orders_id_seq OWNER TO postgres;

--
-- Name: project_change_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_change_orders_id_seq OWNED BY public.project_change_orders.id;


--
-- Name: project_costs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_costs (
    id integer NOT NULL,
    project_id integer NOT NULL,
    phase_id integer,
    cost_type character varying(8) NOT NULL,
    source_id integer,
    amount numeric(15,2) NOT NULL,
    cost_date date NOT NULL,
    description text,
    gl_batch_id integer,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_project_cost_amount_ge_0 CHECK ((amount >= (0)::numeric))
);


ALTER TABLE public.project_costs OWNER TO postgres;

--
-- Name: project_costs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_costs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.project_costs_id_seq OWNER TO postgres;

--
-- Name: project_costs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_costs_id_seq OWNED BY public.project_costs.id;


--
-- Name: project_issues; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_issues (
    id integer NOT NULL,
    project_id integer NOT NULL,
    task_id integer,
    issue_number character varying(50) NOT NULL,
    title character varying(300) NOT NULL,
    description text NOT NULL,
    category character varying(8) NOT NULL,
    severity character varying(8) NOT NULL,
    priority character varying(6) NOT NULL,
    status character varying(11) NOT NULL,
    reported_by integer,
    assigned_to integer,
    reported_date date NOT NULL,
    resolved_date date,
    resolution text,
    cost_impact numeric(15,2),
    schedule_impact_days integer,
    root_cause text,
    preventive_action text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.project_issues OWNER TO postgres;

--
-- Name: project_issues_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_issues_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.project_issues_id_seq OWNER TO postgres;

--
-- Name: project_issues_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_issues_id_seq OWNED BY public.project_issues.id;


--
-- Name: project_milestones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_milestones (
    id integer NOT NULL,
    project_id integer NOT NULL,
    phase_id integer,
    milestone_number character varying(50) NOT NULL,
    name character varying(300) NOT NULL,
    description text,
    due_date date NOT NULL,
    completed_date date,
    billing_amount numeric(15,2),
    tax_rate numeric(5,2),
    tax_amount numeric(12,2),
    billing_percentage numeric(5,2),
    invoice_id integer,
    payment_terms_days integer,
    status character varying(11) NOT NULL,
    completion_criteria text,
    deliverables json,
    approval_required boolean,
    approved_by integer,
    approved_at timestamp without time zone,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_milestone_billing_ge_0 CHECK ((billing_amount >= (0)::numeric)),
    CONSTRAINT ck_milestone_billing_pct CHECK (((billing_percentage >= (0)::numeric) AND (billing_percentage <= (100)::numeric))),
    CONSTRAINT ck_milestone_tax_non_negative CHECK ((tax_amount >= (0)::numeric)),
    CONSTRAINT ck_milestone_tax_rate_0_100 CHECK (((tax_rate >= (0)::numeric) AND (tax_rate <= (100)::numeric)))
);


ALTER TABLE public.project_milestones OWNER TO postgres;

--
-- Name: project_milestones_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_milestones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.project_milestones_id_seq OWNER TO postgres;

--
-- Name: project_milestones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_milestones_id_seq OWNED BY public.project_milestones.id;


--
-- Name: project_phases; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_phases (
    id integer NOT NULL,
    project_id integer NOT NULL,
    name character varying(200) NOT NULL,
    "order" integer NOT NULL,
    start_date date,
    end_date date,
    planned_budget numeric(15,2),
    actual_cost numeric(15,2),
    status character varying(11) NOT NULL,
    completion_percentage numeric(5,2),
    description text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_phase_budget_ge_0 CHECK ((planned_budget >= (0)::numeric)),
    CONSTRAINT ck_phase_completion_range CHECK (((completion_percentage >= (0)::numeric) AND (completion_percentage <= (100)::numeric)))
);


ALTER TABLE public.project_phases OWNER TO postgres;

--
-- Name: project_phases_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_phases_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.project_phases_id_seq OWNER TO postgres;

--
-- Name: project_phases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_phases_id_seq OWNED BY public.project_phases.id;


--
-- Name: project_resources; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_resources (
    id integer NOT NULL,
    project_id integer NOT NULL,
    task_id integer,
    resource_type character varying(13) NOT NULL,
    employee_id integer,
    product_id integer,
    resource_name character varying(200),
    quantity numeric(10,2) NOT NULL,
    unit_cost numeric(12,2) NOT NULL,
    total_cost numeric(15,2) NOT NULL,
    allocation_date date NOT NULL,
    start_date date,
    end_date date,
    hours_allocated numeric(8,2),
    hours_used numeric(8,2),
    status character varying(9) NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_resource_hours_alloc_ge_0 CHECK ((hours_allocated >= (0)::numeric)),
    CONSTRAINT ck_resource_hours_used_ge_0 CHECK ((hours_used >= (0)::numeric)),
    CONSTRAINT ck_resource_quantity_gt_0 CHECK ((quantity > (0)::numeric)),
    CONSTRAINT ck_resource_unit_cost_ge_0 CHECK ((unit_cost >= (0)::numeric))
);


ALTER TABLE public.project_resources OWNER TO postgres;

--
-- Name: project_resources_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_resources_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.project_resources_id_seq OWNER TO postgres;

--
-- Name: project_resources_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_resources_id_seq OWNED BY public.project_resources.id;


--
-- Name: project_revenues; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_revenues (
    id integer NOT NULL,
    project_id integer NOT NULL,
    phase_id integer,
    revenue_type character varying(9) NOT NULL,
    source_id integer,
    amount numeric(15,2) NOT NULL,
    revenue_date date NOT NULL,
    description text,
    gl_batch_id integer,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_project_revenue_amount_ge_0 CHECK ((amount >= (0)::numeric))
);


ALTER TABLE public.project_revenues OWNER TO postgres;

--
-- Name: project_revenues_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_revenues_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.project_revenues_id_seq OWNER TO postgres;

--
-- Name: project_revenues_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_revenues_id_seq OWNED BY public.project_revenues.id;


--
-- Name: project_risks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_risks (
    id integer NOT NULL,
    project_id integer NOT NULL,
    risk_number character varying(50) NOT NULL,
    title character varying(300) NOT NULL,
    description text NOT NULL,
    category character varying(9) NOT NULL,
    probability character varying(9) NOT NULL,
    impact character varying(10) NOT NULL,
    risk_score numeric(5,2) NOT NULL,
    status character varying(10) NOT NULL,
    mitigation_plan text,
    contingency_plan text,
    owner_id integer,
    identified_date date NOT NULL,
    review_date date,
    closed_date date,
    actual_impact_cost numeric(15,2),
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_risk_score_range CHECK (((risk_score >= (0)::numeric) AND (risk_score <= (25)::numeric)))
);


ALTER TABLE public.project_risks OWNER TO postgres;

--
-- Name: project_risks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_risks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.project_risks_id_seq OWNER TO postgres;

--
-- Name: project_risks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_risks_id_seq OWNED BY public.project_risks.id;


--
-- Name: project_tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_tasks (
    id integer NOT NULL,
    project_id integer NOT NULL,
    phase_id integer,
    task_number character varying(50) NOT NULL,
    name character varying(300) NOT NULL,
    description text,
    assigned_to integer,
    priority character varying(8) NOT NULL,
    status character varying(11) NOT NULL,
    start_date date NOT NULL,
    due_date date NOT NULL,
    completed_date date,
    estimated_hours numeric(8,2),
    actual_hours numeric(8,2),
    completion_percentage numeric(5,2),
    depends_on json,
    blocked_reason text,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_task_actual_hours_ge_0 CHECK ((actual_hours >= (0)::numeric)),
    CONSTRAINT ck_task_completion_range CHECK (((completion_percentage >= (0)::numeric) AND (completion_percentage <= (100)::numeric))),
    CONSTRAINT ck_task_est_hours_ge_0 CHECK ((estimated_hours >= (0)::numeric))
);


ALTER TABLE public.project_tasks OWNER TO postgres;

--
-- Name: project_tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.project_tasks_id_seq OWNER TO postgres;

--
-- Name: project_tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_tasks_id_seq OWNED BY public.project_tasks.id;


--
-- Name: projects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.projects (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(200) NOT NULL,
    client_id integer,
    start_date date NOT NULL,
    end_date date,
    planned_end_date date,
    budget_amount numeric(15,2),
    estimated_cost numeric(15,2),
    estimated_revenue numeric(15,2),
    actual_cost numeric(15,2),
    actual_revenue numeric(15,2),
    cost_center_id integer,
    manager_id integer NOT NULL,
    branch_id integer,
    status character varying(9) NOT NULL,
    completion_percentage numeric(5,2),
    description text,
    notes text,
    is_active boolean DEFAULT true NOT NULL,
    created_by integer,
    updated_by integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_project_budget_ge_0 CHECK ((budget_amount >= (0)::numeric)),
    CONSTRAINT ck_project_completion_range CHECK (((completion_percentage >= (0)::numeric) AND (completion_percentage <= (100)::numeric)))
);


ALTER TABLE public.projects OWNER TO postgres;

--
-- Name: projects_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.projects_id_seq OWNER TO postgres;

--
-- Name: projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.projects_id_seq OWNED BY public.projects.id;


--
-- Name: recurring_invoice_schedules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recurring_invoice_schedules (
    id integer NOT NULL,
    template_id integer NOT NULL,
    invoice_id integer,
    scheduled_date date NOT NULL,
    generated_at timestamp without time zone,
    status character varying(20) NOT NULL,
    error_message text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_schedule_status CHECK (((status)::text = ANY ((ARRAY['PENDING'::character varying, 'GENERATED'::character varying, 'FAILED'::character varying, 'SKIPPED'::character varying])::text[])))
);


ALTER TABLE public.recurring_invoice_schedules OWNER TO postgres;

--
-- Name: recurring_invoice_schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.recurring_invoice_schedules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recurring_invoice_schedules_id_seq OWNER TO postgres;

--
-- Name: recurring_invoice_schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.recurring_invoice_schedules_id_seq OWNED BY public.recurring_invoice_schedules.id;


--
-- Name: recurring_invoice_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recurring_invoice_templates (
    id integer NOT NULL,
    template_name character varying(200) NOT NULL,
    customer_id integer NOT NULL,
    description text,
    amount numeric(15,2) NOT NULL,
    currency character varying(10) NOT NULL,
    tax_rate numeric(5,2),
    frequency character varying(20) NOT NULL,
    start_date date NOT NULL,
    end_date date,
    next_invoice_date date,
    is_active boolean DEFAULT true NOT NULL,
    branch_id integer NOT NULL,
    site_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_recurring_amount_ge_0 CHECK ((amount >= (0)::numeric)),
    CONSTRAINT ck_recurring_frequency CHECK (((frequency)::text = ANY ((ARRAY['DAILY'::character varying, 'WEEKLY'::character varying, 'MONTHLY'::character varying, 'QUARTERLY'::character varying, 'YEARLY'::character varying])::text[])))
);


ALTER TABLE public.recurring_invoice_templates OWNER TO postgres;

--
-- Name: recurring_invoice_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.recurring_invoice_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recurring_invoice_templates_id_seq OWNER TO postgres;

--
-- Name: recurring_invoice_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.recurring_invoice_templates_id_seq OWNED BY public.recurring_invoice_templates.id;


--
-- Name: resource_time_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.resource_time_logs (
    id integer NOT NULL,
    project_id integer NOT NULL,
    task_id integer,
    resource_id integer,
    employee_id integer NOT NULL,
    log_date date NOT NULL,
    hours_worked numeric(8,2) NOT NULL,
    hourly_rate numeric(10,2) NOT NULL,
    total_cost numeric(12,2) NOT NULL,
    description text,
    approved boolean,
    approved_by integer,
    approved_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_hourly_rate_ge_0 CHECK ((hourly_rate >= (0)::numeric)),
    CONSTRAINT ck_hours_worked_range CHECK (((hours_worked > (0)::numeric) AND (hours_worked <= (24)::numeric)))
);


ALTER TABLE public.resource_time_logs OWNER TO postgres;

--
-- Name: resource_time_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.resource_time_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.resource_time_logs_id_seq OWNER TO postgres;

--
-- Name: resource_time_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.resource_time_logs_id_seq OWNED BY public.resource_time_logs.id;


--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_permissions (
    role_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.role_permissions OWNER TO postgres;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(200),
    is_default boolean NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: saas_invoices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.saas_invoices (
    id integer NOT NULL,
    invoice_number character varying(50) NOT NULL,
    subscription_id integer NOT NULL,
    amount numeric(10,2) NOT NULL,
    currency character varying(10) NOT NULL,
    status character varying(20) NOT NULL,
    due_date timestamp without time zone,
    paid_at timestamp without time zone,
    payment_method character varying(50),
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.saas_invoices OWNER TO postgres;

--
-- Name: saas_invoices_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.saas_invoices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.saas_invoices_id_seq OWNER TO postgres;

--
-- Name: saas_invoices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.saas_invoices_id_seq OWNED BY public.saas_invoices.id;


--
-- Name: saas_plans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.saas_plans (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    price_monthly numeric(10,2) NOT NULL,
    price_yearly numeric(10,2),
    currency character varying(10) NOT NULL,
    max_users integer,
    max_invoices integer,
    storage_gb integer,
    features text,
    is_active boolean DEFAULT true NOT NULL,
    is_popular boolean DEFAULT false NOT NULL,
    sort_order integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.saas_plans OWNER TO postgres;

--
-- Name: saas_plans_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.saas_plans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.saas_plans_id_seq OWNER TO postgres;

--
-- Name: saas_plans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.saas_plans_id_seq OWNED BY public.saas_plans.id;


--
-- Name: saas_subscriptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.saas_subscriptions (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    plan_id integer NOT NULL,
    status character varying(20) NOT NULL,
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone,
    trial_end_date timestamp without time zone,
    auto_renew boolean DEFAULT true NOT NULL,
    cancelled_at timestamp without time zone,
    cancelled_by integer,
    cancellation_reason text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.saas_subscriptions OWNER TO postgres;

--
-- Name: saas_subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.saas_subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.saas_subscriptions_id_seq OWNER TO postgres;

--
-- Name: saas_subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.saas_subscriptions_id_seq OWNED BY public.saas_subscriptions.id;


--
-- Name: sale_lines; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sale_lines (
    id integer NOT NULL,
    sale_id integer NOT NULL,
    product_id integer NOT NULL,
    warehouse_id integer NOT NULL,
    quantity integer NOT NULL,
    unit_price numeric(12,2) NOT NULL,
    discount_rate numeric(5,2) NOT NULL,
    tax_rate numeric(5,2) NOT NULL,
    line_receiver character varying(200),
    note character varying(200),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_sale_line_discount_rate_range CHECK (((discount_rate >= (0)::numeric) AND (discount_rate <= (100)::numeric))),
    CONSTRAINT chk_sale_line_qty_positive CHECK ((quantity > 0)),
    CONSTRAINT chk_sale_line_tax_rate_range CHECK (((tax_rate >= (0)::numeric) AND (tax_rate <= (100)::numeric))),
    CONSTRAINT chk_sale_line_unit_price_non_negative CHECK ((unit_price >= (0)::numeric))
);


ALTER TABLE public.sale_lines OWNER TO postgres;

--
-- Name: sale_lines_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sale_lines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sale_lines_id_seq OWNER TO postgres;

--
-- Name: sale_lines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sale_lines_id_seq OWNED BY public.sale_lines.id;


--
-- Name: sale_return_lines; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sale_return_lines (
    id integer NOT NULL,
    sale_return_id integer NOT NULL,
    product_id integer NOT NULL,
    warehouse_id integer,
    quantity integer NOT NULL,
    unit_price numeric(12,2) NOT NULL,
    notes character varying(200),
    condition character varying(10) NOT NULL,
    liability_party character varying(8),
    CONSTRAINT ck_sale_return_price_ge0 CHECK ((unit_price >= (0)::numeric)),
    CONSTRAINT ck_sale_return_qty_pos CHECK ((quantity > 0))
);


ALTER TABLE public.sale_return_lines OWNER TO postgres;

--
-- Name: sale_return_lines_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sale_return_lines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sale_return_lines_id_seq OWNER TO postgres;

--
-- Name: sale_return_lines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sale_return_lines_id_seq OWNED BY public.sale_return_lines.id;


--
-- Name: sale_returns; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sale_returns (
    id integer NOT NULL,
    sale_id integer,
    customer_id integer,
    warehouse_id integer,
    reason character varying(200),
    status character varying(9) NOT NULL,
    notes text,
    total_amount numeric(12,2) NOT NULL,
    tax_rate numeric(5,2),
    tax_amount numeric(12,2),
    currency character varying(10) NOT NULL,
    fx_rate_used numeric(10,6),
    fx_rate_source character varying(20),
    fx_rate_timestamp timestamp without time zone,
    fx_base_currency character varying(10),
    fx_quote_currency character varying(10),
    credit_note_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_sale_return_tax_non_negative CHECK ((tax_amount >= (0)::numeric)),
    CONSTRAINT ck_sale_return_tax_rate_0_100 CHECK (((tax_rate >= (0)::numeric) AND (tax_rate <= (100)::numeric)))
);


ALTER TABLE public.sale_returns OWNER TO postgres;

--
-- Name: sale_returns_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sale_returns_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sale_returns_id_seq OWNER TO postgres;

--
-- Name: sale_returns_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sale_returns_id_seq OWNED BY public.sale_returns.id;


--
-- Name: sales; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sales (
    id integer NOT NULL,
    sale_number character varying(50),
    sale_date timestamp without time zone NOT NULL,
    customer_id integer NOT NULL,
    seller_id integer NOT NULL,
    seller_employee_id integer,
    preorder_id integer,
    tax_rate numeric(5,2) NOT NULL,
    discount_total numeric(12,2) NOT NULL,
    notes text,
    receiver_name character varying(200),
    status character varying(9) NOT NULL,
    payment_status character varying(8) NOT NULL,
    currency character varying(10) NOT NULL,
    fx_rate_used numeric(10,6),
    fx_rate_source character varying(20),
    fx_rate_timestamp timestamp without time zone,
    fx_base_currency character varying(10),
    fx_quote_currency character varying(10),
    shipping_address text,
    billing_address text,
    shipping_cost numeric(10,2) NOT NULL,
    total_amount numeric(12,2) NOT NULL,
    total_paid numeric(12,2) NOT NULL,
    balance_due numeric(12,2) NOT NULL,
    refunded_total numeric(12,2) NOT NULL,
    refund_of_id integer,
    idempotency_key character varying(64),
    cancelled_at timestamp without time zone,
    cancelled_by integer,
    cancel_reason character varying(200),
    is_archived boolean NOT NULL,
    archived_at timestamp without time zone,
    archived_by integer,
    archive_reason character varying(200),
    cost_center_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_sale_discount_non_negative CHECK ((discount_total >= (0)::numeric)),
    CONSTRAINT ck_sale_refunded_total_non_negative CHECK ((refunded_total >= (0)::numeric)),
    CONSTRAINT ck_sale_shipping_cost_non_negative CHECK ((shipping_cost >= (0)::numeric)),
    CONSTRAINT ck_sale_total_amount_non_negative CHECK ((total_amount >= (0)::numeric)),
    CONSTRAINT ck_sale_total_paid_non_negative CHECK ((total_paid >= (0)::numeric))
);


ALTER TABLE public.sales OWNER TO postgres;

--
-- Name: sales_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sales_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sales_id_seq OWNER TO postgres;

--
-- Name: sales_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sales_id_seq OWNED BY public.sales.id;


--
-- Name: service_parts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service_parts (
    id integer NOT NULL,
    service_id integer NOT NULL,
    part_id integer NOT NULL,
    warehouse_id integer NOT NULL,
    quantity integer NOT NULL,
    unit_price numeric(10,2) NOT NULL,
    discount numeric(12,2),
    tax_rate numeric(5,2),
    note character varying(200),
    notes text,
    partner_id integer,
    share_percentage numeric(5,2),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_service_part_discount_max CHECK ((discount <= ((quantity)::numeric * unit_price))),
    CONSTRAINT chk_service_part_discount_positive CHECK ((discount >= (0)::numeric)),
    CONSTRAINT chk_service_part_price_non_negative CHECK ((unit_price >= (0)::numeric)),
    CONSTRAINT chk_service_part_qty_positive CHECK ((quantity > 0)),
    CONSTRAINT chk_service_part_share_range CHECK (((share_percentage >= (0)::numeric) AND (share_percentage <= (100)::numeric))),
    CONSTRAINT chk_service_part_tax_range CHECK (((tax_rate >= (0)::numeric) AND (tax_rate <= (100)::numeric)))
);


ALTER TABLE public.service_parts OWNER TO postgres;

--
-- Name: service_parts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.service_parts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_parts_id_seq OWNER TO postgres;

--
-- Name: service_parts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.service_parts_id_seq OWNED BY public.service_parts.id;


--
-- Name: service_requests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service_requests (
    id integer NOT NULL,
    service_number character varying(50),
    customer_id integer NOT NULL,
    mechanic_id integer,
    vehicle_type_id integer,
    status character varying(11) NOT NULL,
    priority character varying(6) NOT NULL,
    vehicle_vrn character varying(50),
    vehicle_model character varying(100),
    chassis_number character varying(100),
    engineer_notes text,
    description text,
    estimated_duration integer,
    actual_duration integer,
    estimated_cost numeric(12,2),
    total_cost numeric(12,2),
    start_time date,
    end_time date,
    problem_description text,
    diagnosis text,
    resolution text,
    notes text,
    received_at timestamp without time zone,
    started_at timestamp without time zone,
    expected_delivery timestamp without time zone,
    completed_at timestamp without time zone,
    currency character varying(10) NOT NULL,
    fx_rate_used numeric(10,6),
    fx_rate_source character varying(20),
    fx_rate_timestamp timestamp without time zone,
    fx_base_currency character varying(10),
    fx_quote_currency character varying(10),
    tax_rate numeric(5,2),
    discount_total numeric(12,2),
    parts_total numeric(12,2),
    labor_total numeric(12,2),
    total_amount numeric(12,2),
    consume_stock boolean NOT NULL,
    warranty_days integer,
    refunded_total numeric(12,2) NOT NULL,
    refund_of_id integer,
    idempotency_key character varying(64),
    cancelled_at timestamp without time zone,
    cancelled_by integer,
    cancel_reason character varying(200),
    is_archived boolean NOT NULL,
    archived_at timestamp without time zone,
    archived_by integer,
    archive_reason character varying(200),
    cost_center_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.service_requests OWNER TO postgres;

--
-- Name: service_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.service_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_requests_id_seq OWNER TO postgres;

--
-- Name: service_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.service_requests_id_seq OWNED BY public.service_requests.id;


--
-- Name: service_tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service_tasks (
    id integer NOT NULL,
    service_id integer NOT NULL,
    partner_id integer,
    share_percentage numeric(5,2),
    description character varying(200) NOT NULL,
    quantity integer,
    unit_price numeric(10,2) NOT NULL,
    discount numeric(12,2),
    tax_rate numeric(5,2),
    note character varying(200),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_service_task_discount_max CHECK ((discount <= ((quantity)::numeric * unit_price))),
    CONSTRAINT chk_service_task_discount_positive CHECK ((discount >= (0)::numeric)),
    CONSTRAINT chk_service_task_price_non_negative CHECK ((unit_price >= (0)::numeric)),
    CONSTRAINT chk_service_task_qty_positive CHECK ((quantity > 0)),
    CONSTRAINT chk_service_task_share_range CHECK (((share_percentage >= (0)::numeric) AND (share_percentage <= (100)::numeric))),
    CONSTRAINT chk_service_task_tax_range CHECK (((tax_rate >= (0)::numeric) AND (tax_rate <= (100)::numeric)))
);


ALTER TABLE public.service_tasks OWNER TO postgres;

--
-- Name: service_tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.service_tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_tasks_id_seq OWNER TO postgres;

--
-- Name: service_tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.service_tasks_id_seq OWNED BY public.service_tasks.id;


--
-- Name: shipment_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.shipment_items (
    id integer NOT NULL,
    shipment_id integer NOT NULL,
    product_id integer NOT NULL,
    warehouse_id integer,
    quantity integer NOT NULL,
    unit_cost numeric(12,2) NOT NULL,
    declared_value numeric(12,2),
    landed_extra_share numeric(12,2),
    landed_unit_cost numeric(12,2),
    notes character varying(200),
    CONSTRAINT chk_shipment_item_qty_positive CHECK ((quantity > 0)),
    CONSTRAINT ck_shipment_item_declared_value_non_negative CHECK ((declared_value >= (0)::numeric)),
    CONSTRAINT ck_shipment_item_landed_extra_share_non_negative CHECK ((landed_extra_share >= (0)::numeric)),
    CONSTRAINT ck_shipment_item_landed_unit_cost_non_negative CHECK ((landed_unit_cost >= (0)::numeric)),
    CONSTRAINT ck_shipment_item_unit_cost_non_negative CHECK ((unit_cost >= (0)::numeric))
);


ALTER TABLE public.shipment_items OWNER TO postgres;

--
-- Name: shipment_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.shipment_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.shipment_items_id_seq OWNER TO postgres;

--
-- Name: shipment_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.shipment_items_id_seq OWNED BY public.shipment_items.id;


--
-- Name: shipment_partners; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.shipment_partners (
    id integer NOT NULL,
    shipment_id integer NOT NULL,
    partner_id integer NOT NULL,
    identity_number character varying(100),
    phone_number character varying(20),
    address character varying(200),
    unit_price_before_tax numeric(12,2),
    expiry_date date,
    share_percentage numeric(5,2),
    share_amount numeric(12,2),
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_shipment_partner_share CHECK (((share_percentage >= (0)::numeric) AND (share_percentage <= (100)::numeric))),
    CONSTRAINT ck_shipment_partner_share_amount_non_negative CHECK ((share_amount >= (0)::numeric)),
    CONSTRAINT ck_shipment_partner_unit_price_non_negative CHECK ((unit_price_before_tax >= (0)::numeric))
);


ALTER TABLE public.shipment_partners OWNER TO postgres;

--
-- Name: shipment_partners_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.shipment_partners_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.shipment_partners_id_seq OWNER TO postgres;

--
-- Name: shipment_partners_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.shipment_partners_id_seq OWNED BY public.shipment_partners.id;


--
-- Name: shipments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.shipments (
    id integer NOT NULL,
    number character varying(50),
    shipment_number character varying(50),
    date timestamp without time zone,
    shipment_date timestamp without time zone,
    expected_arrival timestamp without time zone,
    actual_arrival timestamp without time zone,
    delivered_date timestamp without time zone,
    origin character varying(100),
    destination character varying(100),
    destination_id integer,
    status character varying(20) DEFAULT 'DRAFT'::character varying NOT NULL,
    value_before numeric(12,2),
    shipping_cost numeric(12,2),
    customs numeric(12,2),
    vat numeric(12,2),
    insurance numeric(12,2),
    total_cost numeric(12,2),
    carrier character varying(100),
    tracking_number character varying(100),
    notes text,
    currency character varying(10) NOT NULL,
    fx_rate_used numeric(10,6),
    fx_rate_source character varying(20),
    fx_rate_timestamp timestamp without time zone,
    fx_base_currency character varying(10),
    fx_quote_currency character varying(10),
    sale_id integer,
    weight numeric(10,3),
    dimensions character varying(100),
    package_count integer,
    priority character varying(20),
    delivery_method character varying(50),
    delivery_instructions text,
    customs_declaration character varying(100),
    customs_cleared_date timestamp without time zone,
    delivery_attempts integer,
    last_delivery_attempt timestamp without time zone,
    return_reason text,
    is_archived boolean NOT NULL,
    archived_at timestamp without time zone,
    archived_by integer,
    archive_reason character varying(200),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_shipment_status_allowed CHECK (((status)::text = ANY ((ARRAY['DRAFT'::character varying, 'PENDING'::character varying, 'IN_TRANSIT'::character varying, 'IN_CUSTOMS'::character varying, 'ARRIVED'::character varying, 'DELIVERED'::character varying, 'CANCELLED'::character varying, 'RETURNED'::character varying, 'CREATED'::character varying])::text[]))),
    CONSTRAINT ck_shipment_customs_non_negative CHECK ((customs >= (0)::numeric)),
    CONSTRAINT ck_shipment_insurance_non_negative CHECK ((insurance >= (0)::numeric)),
    CONSTRAINT ck_shipment_shipping_cost_non_negative CHECK ((shipping_cost >= (0)::numeric)),
    CONSTRAINT ck_shipment_value_before_non_negative CHECK ((value_before >= (0)::numeric)),
    CONSTRAINT ck_shipment_vat_non_negative CHECK ((vat >= (0)::numeric))
);


ALTER TABLE public.shipments OWNER TO postgres;

--
-- Name: shipments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.shipments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.shipments_id_seq OWNER TO postgres;

--
-- Name: shipments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.shipments_id_seq OWNED BY public.shipments.id;


--
-- Name: sites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sites (
    id integer NOT NULL,
    branch_id integer NOT NULL,
    name character varying(120) NOT NULL,
    code character varying(32) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    address character varying(200),
    city character varying(100),
    geo_lat numeric(10,6),
    geo_lng numeric(10,6),
    manager_user_id integer,
    manager_employee_id integer,
    notes text,
    is_archived boolean DEFAULT false NOT NULL,
    archived_at timestamp without time zone,
    archived_by integer,
    archive_reason character varying(200),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.sites OWNER TO postgres;

--
-- Name: sites_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sites_id_seq OWNER TO postgres;

--
-- Name: sites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sites_id_seq OWNED BY public.sites.id;


--
-- Name: stock_adjustment_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stock_adjustment_items (
    id integer NOT NULL,
    adjustment_id integer NOT NULL,
    product_id integer NOT NULL,
    warehouse_id integer,
    quantity integer NOT NULL,
    unit_cost numeric(12,2) NOT NULL,
    notes character varying(200),
    CONSTRAINT ck_stock_adjustment_item_cost_non_negative CHECK ((unit_cost >= (0)::numeric)),
    CONSTRAINT ck_stock_adjustment_item_qty_positive CHECK ((quantity > 0))
);


ALTER TABLE public.stock_adjustment_items OWNER TO postgres;

--
-- Name: stock_adjustment_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.stock_adjustment_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stock_adjustment_items_id_seq OWNER TO postgres;

--
-- Name: stock_adjustment_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.stock_adjustment_items_id_seq OWNED BY public.stock_adjustment_items.id;


--
-- Name: stock_adjustments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stock_adjustments (
    id integer NOT NULL,
    date timestamp without time zone NOT NULL,
    warehouse_id integer,
    reason character varying(20) NOT NULL,
    notes text,
    total_cost numeric(12,2) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_stock_adjustment_reason_allowed CHECK (((reason)::text = ANY ((ARRAY['DAMAGED'::character varying, 'STORE_USE'::character varying])::text[]))),
    CONSTRAINT ck_stock_adjustment_total_cost_non_negative CHECK ((total_cost >= (0)::numeric))
);


ALTER TABLE public.stock_adjustments OWNER TO postgres;

--
-- Name: stock_adjustments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.stock_adjustments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stock_adjustments_id_seq OWNER TO postgres;

--
-- Name: stock_adjustments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.stock_adjustments_id_seq OWNED BY public.stock_adjustments.id;


--
-- Name: stock_levels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stock_levels (
    id integer NOT NULL,
    product_id integer NOT NULL,
    warehouse_id integer NOT NULL,
    quantity integer DEFAULT 0 NOT NULL,
    reserved_quantity integer DEFAULT 0 NOT NULL,
    min_stock integer,
    max_stock integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_max_ge_min CHECK (((min_stock IS NULL) OR (max_stock IS NULL) OR (max_stock >= min_stock))),
    CONSTRAINT ck_max_non_negative CHECK (((max_stock IS NULL) OR (max_stock >= 0))),
    CONSTRAINT ck_min_non_negative CHECK (((min_stock IS NULL) OR (min_stock >= 0))),
    CONSTRAINT ck_reserved_non_negative CHECK ((reserved_quantity >= 0)),
    CONSTRAINT ck_stock_non_negative CHECK ((quantity >= 0))
);


ALTER TABLE public.stock_levels OWNER TO postgres;

--
-- Name: stock_levels_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.stock_levels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stock_levels_id_seq OWNER TO postgres;

--
-- Name: stock_levels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.stock_levels_id_seq OWNED BY public.stock_levels.id;


--
-- Name: supplier_loan_settlements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.supplier_loan_settlements (
    id integer NOT NULL,
    loan_id integer,
    supplier_id integer,
    settled_price numeric(12,2) NOT NULL,
    settlement_date timestamp without time zone,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_settlement_price_non_negative CHECK ((settled_price >= (0)::numeric))
);


ALTER TABLE public.supplier_loan_settlements OWNER TO postgres;

--
-- Name: supplier_loan_settlements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.supplier_loan_settlements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.supplier_loan_settlements_id_seq OWNER TO postgres;

--
-- Name: supplier_loan_settlements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.supplier_loan_settlements_id_seq OWNED BY public.supplier_loan_settlements.id;


--
-- Name: supplier_settlement_lines; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.supplier_settlement_lines (
    id integer NOT NULL,
    settlement_id integer NOT NULL,
    source_type character varying(30) NOT NULL,
    source_id integer,
    description character varying(255),
    product_id integer,
    quantity numeric(12,3),
    unit_price numeric(12,2),
    gross_amount numeric(12,2),
    needs_pricing boolean NOT NULL,
    cost_source character varying(20),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.supplier_settlement_lines OWNER TO postgres;

--
-- Name: supplier_settlement_lines_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.supplier_settlement_lines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.supplier_settlement_lines_id_seq OWNER TO postgres;

--
-- Name: supplier_settlement_lines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.supplier_settlement_lines_id_seq OWNED BY public.supplier_settlement_lines.id;


--
-- Name: supplier_settlements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.supplier_settlements (
    id integer NOT NULL,
    code character varying(40),
    supplier_id integer NOT NULL,
    from_date timestamp without time zone NOT NULL,
    to_date timestamp without time zone NOT NULL,
    currency character varying(10) NOT NULL,
    fx_rate_used numeric(10,6),
    fx_rate_source character varying(20),
    fx_rate_timestamp timestamp without time zone,
    fx_base_currency character varying(10),
    fx_quote_currency character varying(10),
    status character varying(9) NOT NULL,
    mode character varying(10) NOT NULL,
    notes text,
    total_gross numeric(12,2),
    total_due numeric(12,2),
    previous_settlement_id integer,
    opening_balance numeric(12,2) DEFAULT 0 NOT NULL,
    rights_exchange numeric(12,2) DEFAULT 0 NOT NULL,
    rights_total numeric(12,2) DEFAULT 0 NOT NULL,
    obligations_sales numeric(12,2) DEFAULT 0 NOT NULL,
    obligations_services numeric(12,2) DEFAULT 0 NOT NULL,
    obligations_preorders numeric(12,2) DEFAULT 0 NOT NULL,
    obligations_expenses numeric(12,2) DEFAULT 0 NOT NULL,
    obligations_total numeric(12,2) DEFAULT 0 NOT NULL,
    payments_out numeric(12,2) DEFAULT 0 NOT NULL,
    payments_in numeric(12,2) DEFAULT 0 NOT NULL,
    payments_returns numeric(12,2) DEFAULT 0 NOT NULL,
    payments_net numeric(12,2) DEFAULT 0 NOT NULL,
    closing_balance numeric(12,2) DEFAULT 0 NOT NULL,
    is_approved boolean DEFAULT false NOT NULL,
    approved_by integer,
    approved_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.supplier_settlements OWNER TO postgres;

--
-- Name: supplier_settlements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.supplier_settlements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.supplier_settlements_id_seq OWNER TO postgres;

--
-- Name: supplier_settlements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.supplier_settlements_id_seq OWNED BY public.supplier_settlements.id;


--
-- Name: suppliers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.suppliers (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    is_local boolean DEFAULT true NOT NULL,
    identity_number character varying(100),
    contact character varying(200),
    phone character varying(20),
    email character varying(120),
    address character varying(200),
    notes text,
    payment_terms character varying(50),
    currency character varying(10) DEFAULT 'ILS'::character varying NOT NULL,
    opening_balance numeric(12,2) DEFAULT 0 NOT NULL,
    current_balance numeric(12,2) DEFAULT 0 NOT NULL,
    exchange_items_balance numeric(12,2) DEFAULT 0 NOT NULL,
    sale_returns_balance numeric(12,2) DEFAULT 0 NOT NULL,
    sales_balance numeric(12,2) DEFAULT 0 NOT NULL,
    services_balance numeric(12,2) DEFAULT 0 NOT NULL,
    preorders_balance numeric(12,2) DEFAULT 0 NOT NULL,
    payments_in_balance numeric(12,2) DEFAULT 0 NOT NULL,
    payments_out_balance numeric(12,2) DEFAULT 0 NOT NULL,
    preorders_prepaid_balance numeric(12,2) DEFAULT 0 NOT NULL,
    returns_balance numeric(12,2) DEFAULT 0 NOT NULL,
    expenses_balance numeric(12,2) DEFAULT 0 NOT NULL,
    service_expenses_balance numeric(12,2) DEFAULT 0 NOT NULL,
    returned_checks_in_balance numeric(12,2) DEFAULT 0 NOT NULL,
    returned_checks_out_balance numeric(12,2) DEFAULT 0 NOT NULL,
    customer_id integer,
    is_archived boolean NOT NULL,
    archived_at timestamp without time zone,
    archived_by integer,
    archive_reason character varying(200),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.suppliers OWNER TO postgres;

--
-- Name: COLUMN suppliers.opening_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.suppliers.opening_balance IS 'الرصيد الافتتاحي (موجب=له رصيد عندنا، سالب=لنا رصيد عنده)';


--
-- Name: COLUMN suppliers.current_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.suppliers.current_balance IS 'الرصيد الحالي المحدث';


--
-- Name: COLUMN suppliers.exchange_items_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.suppliers.exchange_items_balance IS 'رصيد قطع التبادل';


--
-- Name: COLUMN suppliers.sale_returns_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.suppliers.sale_returns_balance IS 'رصيد مرتجعات المبيعات';


--
-- Name: COLUMN suppliers.sales_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.suppliers.sales_balance IS 'رصيد المبيعات';


--
-- Name: COLUMN suppliers.services_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.suppliers.services_balance IS 'رصيد الخدمات';


--
-- Name: COLUMN suppliers.preorders_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.suppliers.preorders_balance IS 'رصيد الحجوزات المسبقة';


--
-- Name: COLUMN suppliers.payments_in_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.suppliers.payments_in_balance IS 'رصيد الدفعات الواردة';


--
-- Name: COLUMN suppliers.payments_out_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.suppliers.payments_out_balance IS 'رصيد الدفعات الصادرة';


--
-- Name: COLUMN suppliers.preorders_prepaid_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.suppliers.preorders_prepaid_balance IS 'رصيد أرصدة الحجوزات';


--
-- Name: COLUMN suppliers.returns_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.suppliers.returns_balance IS 'رصيد المرتجعات Exchange';


--
-- Name: COLUMN suppliers.expenses_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.suppliers.expenses_balance IS 'رصيد المصروفات العادية (تُطرح)';


--
-- Name: COLUMN suppliers.service_expenses_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.suppliers.service_expenses_balance IS 'رصيد مصروفات توريد الخدمة (تُضاف)';


--
-- Name: COLUMN suppliers.returned_checks_in_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.suppliers.returned_checks_in_balance IS 'رصيد الشيكات المرتدة الواردة';


--
-- Name: COLUMN suppliers.returned_checks_out_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.suppliers.returned_checks_out_balance IS 'رصيد الشيكات المرتدة الصادرة';


--
-- Name: suppliers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.suppliers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.suppliers_id_seq OWNER TO postgres;

--
-- Name: suppliers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.suppliers_id_seq OWNED BY public.suppliers.id;


--
-- Name: system_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_settings (
    id integer NOT NULL,
    key character varying(100) NOT NULL,
    value text,
    description text,
    data_type character varying(20),
    is_public boolean,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.system_settings OWNER TO postgres;

--
-- Name: system_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.system_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.system_settings_id_seq OWNER TO postgres;

--
-- Name: system_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.system_settings_id_seq OWNED BY public.system_settings.id;


--
-- Name: tax_entries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tax_entries (
    id integer NOT NULL,
    entry_type character varying(20) NOT NULL,
    transaction_type character varying(50) NOT NULL,
    transaction_id integer,
    transaction_reference character varying(50),
    tax_rate numeric(5,2) NOT NULL,
    base_amount numeric(12,2) NOT NULL,
    tax_amount numeric(12,2) NOT NULL,
    total_amount numeric(12,2) NOT NULL,
    currency character varying(3),
    debit_account character varying(20),
    credit_account character varying(20),
    gl_entry_id integer,
    fiscal_year integer,
    fiscal_month integer,
    tax_period character varying(7),
    is_reconciled boolean,
    is_filed boolean,
    filing_reference character varying(100),
    customer_id integer,
    supplier_id integer,
    notes text,
    created_at timestamp without time zone NOT NULL,
    created_by integer
);


ALTER TABLE public.tax_entries OWNER TO postgres;

--
-- Name: tax_entries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tax_entries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tax_entries_id_seq OWNER TO postgres;

--
-- Name: tax_entries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tax_entries_id_seq OWNED BY public.tax_entries.id;


--
-- Name: transfers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transfers (
    id integer NOT NULL,
    reference character varying(50),
    product_id integer NOT NULL,
    source_id integer NOT NULL,
    destination_id integer NOT NULL,
    quantity integer NOT NULL,
    direction character varying(10) NOT NULL,
    transfer_date timestamp without time zone,
    notes text,
    user_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_transfer_diff_wh CHECK ((source_id <> destination_id)),
    CONSTRAINT chk_transfer_qty_positive CHECK ((quantity > 0))
);


ALTER TABLE public.transfers OWNER TO postgres;

--
-- Name: transfers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transfers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.transfers_id_seq OWNER TO postgres;

--
-- Name: transfers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transfers_id_seq OWNED BY public.transfers.id;


--
-- Name: user_branches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_branches (
    id integer NOT NULL,
    user_id integer NOT NULL,
    branch_id integer NOT NULL,
    is_primary boolean NOT NULL,
    can_manage boolean NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.user_branches OWNER TO postgres;

--
-- Name: user_branches_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_branches_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_branches_id_seq OWNER TO postgres;

--
-- Name: user_branches_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_branches_id_seq OWNED BY public.user_branches.id;


--
-- Name: user_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_permissions (
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.user_permissions OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role_id integer,
    is_active boolean DEFAULT true NOT NULL,
    is_system_account boolean DEFAULT false NOT NULL,
    last_login timestamp without time zone,
    last_seen timestamp without time zone,
    last_login_ip character varying(64),
    login_count integer DEFAULT 0 NOT NULL,
    avatar_url character varying(500),
    notes_text text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: utility_accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.utility_accounts (
    id integer NOT NULL,
    utility_type character varying(20) NOT NULL,
    provider character varying(120) NOT NULL,
    account_no character varying(100),
    meter_no character varying(100),
    alias character varying(120),
    is_active boolean NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_utility_type_allowed CHECK (((utility_type)::text = ANY ((ARRAY['ELECTRICITY'::character varying, 'WATER'::character varying])::text[])))
);


ALTER TABLE public.utility_accounts OWNER TO postgres;

--
-- Name: utility_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.utility_accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.utility_accounts_id_seq OWNER TO postgres;

--
-- Name: utility_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.utility_accounts_id_seq OWNED BY public.utility_accounts.id;


--
-- Name: warehouse_partner_shares; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.warehouse_partner_shares (
    id integer NOT NULL,
    partner_id integer NOT NULL,
    warehouse_id integer,
    product_id integer,
    share_percentage double precision NOT NULL,
    share_amount numeric(12,2),
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_wps_share_amount_non_negative CHECK ((share_amount >= (0)::numeric)),
    CONSTRAINT ck_wps_share_percentage_range CHECK (((share_percentage >= (0)::double precision) AND (share_percentage <= (100)::double precision)))
);


ALTER TABLE public.warehouse_partner_shares OWNER TO postgres;

--
-- Name: warehouse_partner_shares_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.warehouse_partner_shares_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.warehouse_partner_shares_id_seq OWNER TO postgres;

--
-- Name: warehouse_partner_shares_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.warehouse_partner_shares_id_seq OWNED BY public.warehouse_partner_shares.id;


--
-- Name: warehouses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.warehouses (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    warehouse_type character varying(9) DEFAULT 'MAIN'::character varying NOT NULL,
    location character varying(200),
    branch_id integer,
    is_active boolean DEFAULT true NOT NULL,
    parent_id integer,
    supplier_id integer,
    partner_id integer,
    share_percent numeric(5,2) DEFAULT 0,
    capacity integer,
    current_occupancy integer DEFAULT 0,
    notes text,
    online_slug character varying(150),
    online_is_default boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.warehouses OWNER TO postgres;

--
-- Name: warehouses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.warehouses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.warehouses_id_seq OWNER TO postgres;

--
-- Name: warehouses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.warehouses_id_seq OWNED BY public.warehouses.id;


--
-- Name: workflow_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_actions (
    id integer NOT NULL,
    workflow_instance_id integer NOT NULL,
    step_number integer NOT NULL,
    step_name character varying(200) NOT NULL,
    action_type character varying(12) NOT NULL,
    actor_id integer NOT NULL,
    action_date timestamp without time zone NOT NULL,
    decision character varying(50),
    comments text,
    attachments json,
    delegated_to integer,
    delegated_at timestamp without time zone,
    duration_hours numeric(8,2),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.workflow_actions OWNER TO postgres;

--
-- Name: workflow_actions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workflow_actions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workflow_actions_id_seq OWNER TO postgres;

--
-- Name: workflow_actions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workflow_actions_id_seq OWNED BY public.workflow_actions.id;


--
-- Name: workflow_definitions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_definitions (
    id integer NOT NULL,
    workflow_code character varying(50) NOT NULL,
    workflow_name character varying(200) NOT NULL,
    workflow_name_ar character varying(200),
    description text,
    workflow_type character varying(12) NOT NULL,
    entity_type character varying(12) NOT NULL,
    steps_definition json NOT NULL,
    auto_start boolean NOT NULL,
    auto_start_condition json,
    is_active boolean NOT NULL,
    version integer NOT NULL,
    timeout_hours integer,
    escalation_rules json,
    created_by integer,
    updated_by integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.workflow_definitions OWNER TO postgres;

--
-- Name: workflow_definitions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workflow_definitions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workflow_definitions_id_seq OWNER TO postgres;

--
-- Name: workflow_definitions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workflow_definitions_id_seq OWNED BY public.workflow_definitions.id;


--
-- Name: workflow_instances; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_instances (
    id integer NOT NULL,
    workflow_definition_id integer NOT NULL,
    instance_code character varying(50) NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id integer NOT NULL,
    status character varying(16) NOT NULL,
    current_step integer NOT NULL,
    total_steps integer NOT NULL,
    started_by integer NOT NULL,
    started_at timestamp without time zone NOT NULL,
    completed_at timestamp without time zone,
    completed_by integer,
    cancelled_at timestamp without time zone,
    cancelled_by integer,
    cancellation_reason text,
    due_date timestamp without time zone,
    context_data json,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.workflow_instances OWNER TO postgres;

--
-- Name: workflow_instances_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workflow_instances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workflow_instances_id_seq OWNER TO postgres;

--
-- Name: workflow_instances_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workflow_instances_id_seq OWNED BY public.workflow_instances.id;


--
-- Name: accounts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts ALTER COLUMN id SET DEFAULT nextval('public.accounts_id_seq'::regclass);


--
-- Name: archives id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.archives ALTER COLUMN id SET DEFAULT nextval('public.archives_id_seq'::regclass);


--
-- Name: asset_depreciations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_depreciations ALTER COLUMN id SET DEFAULT nextval('public.asset_depreciations_id_seq'::regclass);


--
-- Name: asset_maintenance id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_maintenance ALTER COLUMN id SET DEFAULT nextval('public.asset_maintenance_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: auth_audit id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_audit ALTER COLUMN id SET DEFAULT nextval('public.auth_audit_id_seq'::regclass);


--
-- Name: bank_accounts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_accounts ALTER COLUMN id SET DEFAULT nextval('public.bank_accounts_id_seq'::regclass);


--
-- Name: bank_reconciliations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_reconciliations ALTER COLUMN id SET DEFAULT nextval('public.bank_reconciliations_id_seq'::regclass);


--
-- Name: bank_statements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_statements ALTER COLUMN id SET DEFAULT nextval('public.bank_statements_id_seq'::regclass);


--
-- Name: bank_transactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_transactions ALTER COLUMN id SET DEFAULT nextval('public.bank_transactions_id_seq'::regclass);


--
-- Name: branches id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branches ALTER COLUMN id SET DEFAULT nextval('public.branches_id_seq'::regclass);


--
-- Name: budget_commitments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.budget_commitments ALTER COLUMN id SET DEFAULT nextval('public.budget_commitments_id_seq'::regclass);


--
-- Name: budgets id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.budgets ALTER COLUMN id SET DEFAULT nextval('public.budgets_id_seq'::regclass);


--
-- Name: checks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.checks ALTER COLUMN id SET DEFAULT nextval('public.checks_id_seq'::regclass);


--
-- Name: cost_allocation_execution_lines id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_execution_lines ALTER COLUMN id SET DEFAULT nextval('public.cost_allocation_execution_lines_id_seq'::regclass);


--
-- Name: cost_allocation_executions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_executions ALTER COLUMN id SET DEFAULT nextval('public.cost_allocation_executions_id_seq'::regclass);


--
-- Name: cost_allocation_lines id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_lines ALTER COLUMN id SET DEFAULT nextval('public.cost_allocation_lines_id_seq'::regclass);


--
-- Name: cost_allocation_rules id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_rules ALTER COLUMN id SET DEFAULT nextval('public.cost_allocation_rules_id_seq'::regclass);


--
-- Name: cost_center_alert_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_center_alert_logs ALTER COLUMN id SET DEFAULT nextval('public.cost_center_alert_logs_id_seq'::regclass);


--
-- Name: cost_center_alerts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_center_alerts ALTER COLUMN id SET DEFAULT nextval('public.cost_center_alerts_id_seq'::regclass);


--
-- Name: cost_center_allocations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_center_allocations ALTER COLUMN id SET DEFAULT nextval('public.cost_center_allocations_id_seq'::regclass);


--
-- Name: cost_centers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_centers ALTER COLUMN id SET DEFAULT nextval('public.cost_centers_id_seq'::regclass);


--
-- Name: customer_loyalty id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_loyalty ALTER COLUMN id SET DEFAULT nextval('public.customer_loyalty_id_seq'::regclass);


--
-- Name: customer_loyalty_points id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_loyalty_points ALTER COLUMN id SET DEFAULT nextval('public.customer_loyalty_points_id_seq'::regclass);


--
-- Name: customers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers ALTER COLUMN id SET DEFAULT nextval('public.customers_id_seq'::regclass);


--
-- Name: deletion_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deletion_logs ALTER COLUMN id SET DEFAULT nextval('public.deletion_logs_id_seq'::regclass);


--
-- Name: employee_advance_installments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_advance_installments ALTER COLUMN id SET DEFAULT nextval('public.employee_advance_installments_id_seq'::regclass);


--
-- Name: employee_advances id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_advances ALTER COLUMN id SET DEFAULT nextval('public.employee_advances_id_seq'::regclass);


--
-- Name: employee_deductions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_deductions ALTER COLUMN id SET DEFAULT nextval('public.employee_deductions_id_seq'::regclass);


--
-- Name: employee_skills id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_skills ALTER COLUMN id SET DEFAULT nextval('public.employee_skills_id_seq'::regclass);


--
-- Name: employees id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees ALTER COLUMN id SET DEFAULT nextval('public.employees_id_seq'::regclass);


--
-- Name: engineering_skills id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_skills ALTER COLUMN id SET DEFAULT nextval('public.engineering_skills_id_seq'::regclass);


--
-- Name: engineering_tasks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_tasks ALTER COLUMN id SET DEFAULT nextval('public.engineering_tasks_id_seq'::regclass);


--
-- Name: engineering_team_members id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_team_members ALTER COLUMN id SET DEFAULT nextval('public.engineering_team_members_id_seq'::regclass);


--
-- Name: engineering_teams id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_teams ALTER COLUMN id SET DEFAULT nextval('public.engineering_teams_id_seq'::regclass);


--
-- Name: engineering_timesheets id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_timesheets ALTER COLUMN id SET DEFAULT nextval('public.engineering_timesheets_id_seq'::regclass);


--
-- Name: equipment_types id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_types ALTER COLUMN id SET DEFAULT nextval('public.equipment_types_id_seq'::regclass);


--
-- Name: exchange_rates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exchange_rates ALTER COLUMN id SET DEFAULT nextval('public.exchange_rates_id_seq'::regclass);


--
-- Name: exchange_transactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exchange_transactions ALTER COLUMN id SET DEFAULT nextval('public.exchange_transactions_id_seq'::regclass);


--
-- Name: expense_types id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_types ALTER COLUMN id SET DEFAULT nextval('public.expense_types_id_seq'::regclass);


--
-- Name: expenses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses ALTER COLUMN id SET DEFAULT nextval('public.expenses_id_seq'::regclass);


--
-- Name: fixed_asset_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fixed_asset_categories ALTER COLUMN id SET DEFAULT nextval('public.fixed_asset_categories_id_seq'::regclass);


--
-- Name: fixed_assets id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fixed_assets ALTER COLUMN id SET DEFAULT nextval('public.fixed_assets_id_seq'::regclass);


--
-- Name: gl_batches id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gl_batches ALTER COLUMN id SET DEFAULT nextval('public.gl_batches_id_seq'::regclass);


--
-- Name: gl_entries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gl_entries ALTER COLUMN id SET DEFAULT nextval('public.gl_entries_id_seq'::regclass);


--
-- Name: import_runs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.import_runs ALTER COLUMN id SET DEFAULT nextval('public.import_runs_id_seq'::regclass);


--
-- Name: invoice_lines id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoice_lines ALTER COLUMN id SET DEFAULT nextval('public.invoice_lines_id_seq'::regclass);


--
-- Name: invoices id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices ALTER COLUMN id SET DEFAULT nextval('public.invoices_id_seq'::regclass);


--
-- Name: notes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notes ALTER COLUMN id SET DEFAULT nextval('public.notes_id_seq'::regclass);


--
-- Name: notification_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_logs ALTER COLUMN id SET DEFAULT nextval('public.notification_logs_id_seq'::regclass);


--
-- Name: online_cart_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_cart_items ALTER COLUMN id SET DEFAULT nextval('public.online_cart_items_id_seq'::regclass);


--
-- Name: online_carts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_carts ALTER COLUMN id SET DEFAULT nextval('public.online_carts_id_seq'::regclass);


--
-- Name: online_payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_payments ALTER COLUMN id SET DEFAULT nextval('public.online_payments_id_seq'::regclass);


--
-- Name: online_preorder_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_preorder_items ALTER COLUMN id SET DEFAULT nextval('public.online_preorder_items_id_seq'::regclass);


--
-- Name: online_preorders id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_preorders ALTER COLUMN id SET DEFAULT nextval('public.online_preorders_id_seq'::regclass);


--
-- Name: partner_settlement_lines id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_settlement_lines ALTER COLUMN id SET DEFAULT nextval('public.partner_settlement_lines_id_seq'::regclass);


--
-- Name: partner_settlements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_settlements ALTER COLUMN id SET DEFAULT nextval('public.partner_settlements_id_seq'::regclass);


--
-- Name: partners id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partners ALTER COLUMN id SET DEFAULT nextval('public.partners_id_seq'::regclass);


--
-- Name: payment_splits id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_splits ALTER COLUMN id SET DEFAULT nextval('public.payment_splits_id_seq'::regclass);


--
-- Name: payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments ALTER COLUMN id SET DEFAULT nextval('public.payments_id_seq'::regclass);


--
-- Name: permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions ALTER COLUMN id SET DEFAULT nextval('public.permissions_id_seq'::regclass);


--
-- Name: preorders id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.preorders ALTER COLUMN id SET DEFAULT nextval('public.preorders_id_seq'::regclass);


--
-- Name: product_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_categories ALTER COLUMN id SET DEFAULT nextval('public.product_categories_id_seq'::regclass);


--
-- Name: product_partners id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_partners ALTER COLUMN id SET DEFAULT nextval('public.product_partners_id_seq'::regclass);


--
-- Name: product_rating_helpful id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_rating_helpful ALTER COLUMN id SET DEFAULT nextval('public.product_rating_helpful_id_seq'::regclass);


--
-- Name: product_ratings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_ratings ALTER COLUMN id SET DEFAULT nextval('public.product_ratings_id_seq'::regclass);


--
-- Name: product_supplier_loans id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_supplier_loans ALTER COLUMN id SET DEFAULT nextval('public.product_supplier_loans_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: project_change_orders id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_change_orders ALTER COLUMN id SET DEFAULT nextval('public.project_change_orders_id_seq'::regclass);


--
-- Name: project_costs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_costs ALTER COLUMN id SET DEFAULT nextval('public.project_costs_id_seq'::regclass);


--
-- Name: project_issues id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_issues ALTER COLUMN id SET DEFAULT nextval('public.project_issues_id_seq'::regclass);


--
-- Name: project_milestones id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_milestones ALTER COLUMN id SET DEFAULT nextval('public.project_milestones_id_seq'::regclass);


--
-- Name: project_phases id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_phases ALTER COLUMN id SET DEFAULT nextval('public.project_phases_id_seq'::regclass);


--
-- Name: project_resources id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_resources ALTER COLUMN id SET DEFAULT nextval('public.project_resources_id_seq'::regclass);


--
-- Name: project_revenues id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_revenues ALTER COLUMN id SET DEFAULT nextval('public.project_revenues_id_seq'::regclass);


--
-- Name: project_risks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_risks ALTER COLUMN id SET DEFAULT nextval('public.project_risks_id_seq'::regclass);


--
-- Name: project_tasks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_tasks ALTER COLUMN id SET DEFAULT nextval('public.project_tasks_id_seq'::regclass);


--
-- Name: projects id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects ALTER COLUMN id SET DEFAULT nextval('public.projects_id_seq'::regclass);


--
-- Name: recurring_invoice_schedules id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recurring_invoice_schedules ALTER COLUMN id SET DEFAULT nextval('public.recurring_invoice_schedules_id_seq'::regclass);


--
-- Name: recurring_invoice_templates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recurring_invoice_templates ALTER COLUMN id SET DEFAULT nextval('public.recurring_invoice_templates_id_seq'::regclass);


--
-- Name: resource_time_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resource_time_logs ALTER COLUMN id SET DEFAULT nextval('public.resource_time_logs_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: saas_invoices id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_invoices ALTER COLUMN id SET DEFAULT nextval('public.saas_invoices_id_seq'::regclass);


--
-- Name: saas_plans id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_plans ALTER COLUMN id SET DEFAULT nextval('public.saas_plans_id_seq'::regclass);


--
-- Name: saas_subscriptions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_subscriptions ALTER COLUMN id SET DEFAULT nextval('public.saas_subscriptions_id_seq'::regclass);


--
-- Name: sale_lines id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_lines ALTER COLUMN id SET DEFAULT nextval('public.sale_lines_id_seq'::regclass);


--
-- Name: sale_return_lines id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_return_lines ALTER COLUMN id SET DEFAULT nextval('public.sale_return_lines_id_seq'::regclass);


--
-- Name: sale_returns id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_returns ALTER COLUMN id SET DEFAULT nextval('public.sale_returns_id_seq'::regclass);


--
-- Name: sales id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales ALTER COLUMN id SET DEFAULT nextval('public.sales_id_seq'::regclass);


--
-- Name: service_parts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_parts ALTER COLUMN id SET DEFAULT nextval('public.service_parts_id_seq'::regclass);


--
-- Name: service_requests id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests ALTER COLUMN id SET DEFAULT nextval('public.service_requests_id_seq'::regclass);


--
-- Name: service_tasks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_tasks ALTER COLUMN id SET DEFAULT nextval('public.service_tasks_id_seq'::regclass);


--
-- Name: shipment_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipment_items ALTER COLUMN id SET DEFAULT nextval('public.shipment_items_id_seq'::regclass);


--
-- Name: shipment_partners id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipment_partners ALTER COLUMN id SET DEFAULT nextval('public.shipment_partners_id_seq'::regclass);


--
-- Name: shipments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipments ALTER COLUMN id SET DEFAULT nextval('public.shipments_id_seq'::regclass);


--
-- Name: sites id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sites ALTER COLUMN id SET DEFAULT nextval('public.sites_id_seq'::regclass);


--
-- Name: stock_adjustment_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_adjustment_items ALTER COLUMN id SET DEFAULT nextval('public.stock_adjustment_items_id_seq'::regclass);


--
-- Name: stock_adjustments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_adjustments ALTER COLUMN id SET DEFAULT nextval('public.stock_adjustments_id_seq'::regclass);


--
-- Name: stock_levels id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_levels ALTER COLUMN id SET DEFAULT nextval('public.stock_levels_id_seq'::regclass);


--
-- Name: supplier_loan_settlements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.supplier_loan_settlements ALTER COLUMN id SET DEFAULT nextval('public.supplier_loan_settlements_id_seq'::regclass);


--
-- Name: supplier_settlement_lines id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.supplier_settlement_lines ALTER COLUMN id SET DEFAULT nextval('public.supplier_settlement_lines_id_seq'::regclass);


--
-- Name: supplier_settlements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.supplier_settlements ALTER COLUMN id SET DEFAULT nextval('public.supplier_settlements_id_seq'::regclass);


--
-- Name: suppliers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers ALTER COLUMN id SET DEFAULT nextval('public.suppliers_id_seq'::regclass);


--
-- Name: system_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_settings ALTER COLUMN id SET DEFAULT nextval('public.system_settings_id_seq'::regclass);


--
-- Name: tax_entries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tax_entries ALTER COLUMN id SET DEFAULT nextval('public.tax_entries_id_seq'::regclass);


--
-- Name: transfers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transfers ALTER COLUMN id SET DEFAULT nextval('public.transfers_id_seq'::regclass);


--
-- Name: user_branches id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_branches ALTER COLUMN id SET DEFAULT nextval('public.user_branches_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: utility_accounts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.utility_accounts ALTER COLUMN id SET DEFAULT nextval('public.utility_accounts_id_seq'::regclass);


--
-- Name: warehouse_partner_shares id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_partner_shares ALTER COLUMN id SET DEFAULT nextval('public.warehouse_partner_shares_id_seq'::regclass);


--
-- Name: warehouses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouses ALTER COLUMN id SET DEFAULT nextval('public.warehouses_id_seq'::regclass);


--
-- Name: workflow_actions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_actions ALTER COLUMN id SET DEFAULT nextval('public.workflow_actions_id_seq'::regclass);


--
-- Name: workflow_definitions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_definitions ALTER COLUMN id SET DEFAULT nextval('public.workflow_definitions_id_seq'::regclass);


--
-- Name: workflow_instances id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_instances ALTER COLUMN id SET DEFAULT nextval('public.workflow_instances_id_seq'::regclass);


--
-- Data for Name: accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accounts (id, code, name, type, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
84a17762f7c4
\.


--
-- Data for Name: archives; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.archives (id, record_type, record_id, table_name, archived_data, archive_reason, archived_by, archived_at, original_created_at, original_updated_at) FROM stdin;
1	service_requests	2	service_requests	{"id": 2, "service_number": "SRV-20251109205347", "customer_id": 18, "mechanic_id": null, "vehicle_type_id": 2, "status": "COMPLETED", "priority": "URGENT", "vehicle_vrn": "123", "vehicle_model": null, "chassis_number": null, "engineer_notes": null, "description": null, "estimated_duration": 0, "actual_duration": null, "estimated_cost": null, "total_cost": 0.0, "start_time": null, "end_time": null, "problem_description": "تصليح جدلة", "diagnosis": null, "resolution": null, "notes": null, "received_at": "2025-11-09T20:53:47.448410", "started_at": null, "expected_delivery": null, "completed_at": "2025-11-09T20:53:47.448554", "currency": "ILS", "fx_rate_used": null, "fx_rate_source": null, "fx_rate_timestamp": null, "fx_base_currency": null, "fx_quote_currency": null, "tax_rate": 0.0, "discount_total": 0.0, "parts_total": 0.0, "labor_total": 0.0, "total_amount": 0.0, "consume_stock": false, "warranty_days": 0, "refunded_total": 0.0, "refund_of_id": null, "idempotency_key": null, "cancelled_at": null, "cancelled_by": null, "cancel_reason": null, "is_archived": false, "archived_at": null, "archived_by": null, "archive_reason": null, "cost_center_id": null, "created_at": "2025-11-09T20:53:47", "updated_at": "2025-11-09T20:53:47"}	خاطىء	1	2025-11-09 20:55:59.772882	2025-11-09 20:53:47	2025-11-09 20:53:47
\.


--
-- Data for Name: asset_depreciations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.asset_depreciations (id, asset_id, fiscal_year, fiscal_month, depreciation_date, depreciation_amount, accumulated_depreciation, book_value, gl_batch_id, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: asset_maintenance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.asset_maintenance (id, asset_id, maintenance_date, maintenance_type, cost, expense_id, description, next_maintenance_date, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_logs (id, model_name, record_id, customer_id, user_id, action, old_data, new_data, ip_address, user_agent, created_at, updated_at) FROM stdin;
1	Customer	1	1	1	CREATE	\N	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-23T20:45:21"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-23 20:45:21	2025-10-23 20:45:21
2	Sale	1	\N	1	CREATE	\N	{"id": 1, "sale_number": "SAL20251023-0001", "customer_id": 1, "seller_id": 1, "sale_date": "2025-10-23", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": "", "lines": [{"product_id": 9, "warehouse_id": 1, "quantity": 1, "unit_price": 6000.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 4, "warehouse_id": 1, "quantity": 4, "unit_price": 7000.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 3, "warehouse_id": 1, "quantity": 7, "unit_price": 8000.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 7, "warehouse_id": 1, "quantity": 1, "unit_price": 13000.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 8, "warehouse_id": 1, "quantity": 1, "unit_price": 13000.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 10, "warehouse_id": 1, "quantity": 1, "unit_price": 14000.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 2, "warehouse_id": 1, "quantity": 2, "unit_price": 16000.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 1, "warehouse_id": 1, "quantity": 4, "unit_price": 23000.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 6, "warehouse_id": 1, "quantity": 1, "unit_price": 14000.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 5, "warehouse_id": 1, "quantity": 10, "unit_price": 1500.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-10-23 20:50:04.583778	2025-10-23 20:50:04
3	Customer	2	2	1	CREATE	\N	{"id": 2, "name": "اياد الغزاوي", "phone": "0562151515", "whatsapp": "0562151515", "email": "awll@gmail.com", "address": "", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-24T16:29:32"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-24 16:29:32	2025-10-24 16:29:32
4	Customer	2	2	1	UPDATE	{"id": 2, "name": "اياد الغزاوي", "phone": "0562151515", "whatsapp": "0562151515", "email": "awll@gmail.com", "address": "", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-24T16:29:32"}	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0562151515", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-24T16:30:33"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-24 16:30:33	2025-10-24 16:30:33
5	Customer	2	2	1	UPDATE	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0562151515", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-24T16:30:33"}	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0562151515", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-24T16:30:33"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-24 16:34:50	2025-10-24 16:34:50
6	Customer	2	2	1	UPDATE	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0562151515", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-24T16:30:33"}	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0599070235", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-24T17:15:55"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-24 17:15:55	2025-10-24 17:15:55
7	Sale	2	\N	1	CREATE	\N	{"id": 2, "sale_number": "SAL20251024-0001", "customer_id": 2, "seller_id": 1, "sale_date": "2025-10-24", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": "", "lines": [{"product_id": 19, "warehouse_id": 2, "quantity": 1, "unit_price": 8000.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 17, "warehouse_id": 2, "quantity": 1, "unit_price": 5500.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 14, "warehouse_id": 2, "quantity": 1, "unit_price": 3500.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 12, "warehouse_id": 2, "quantity": 1, "unit_price": 8000.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 18, "warehouse_id": 2, "quantity": 1, "unit_price": 1500.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 15, "warehouse_id": 2, "quantity": 1, "unit_price": 2000.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 16, "warehouse_id": 2, "quantity": 3, "unit_price": 1500.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 11, "warehouse_id": 2, "quantity": 3, "unit_price": 4500.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 13, "warehouse_id": 2, "quantity": 6, "unit_price": 1500.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-10-24 18:36:54.467931	2025-10-24 18:36:54
39	Sale	5	\N	1	CREATE	\N	{"id": 5, "sale_number": "SAL20251029-0001", "customer_id": 5, "seller_id": 1, "sale_date": "2025-10-29", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": "", "lines": [{"product_id": 23, "warehouse_id": 2, "quantity": 1, "unit_price": 2800.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-10-29 16:56:58.142229	2025-10-29 16:56:58
8	Customer	2	2	1	UPDATE	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0599070235", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-24T17:15:55"}	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0599070235", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-24T17:15:55"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-24 20:00:40	2025-10-24 20:00:40
9	Customer	2	2	1	UPDATE	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0599070235", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-24T17:15:55"}	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0599070235", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-24T20:01:22"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-24 20:01:22	2025-10-24 20:01:22
10	Customer	3	\N	1	CREATE	\N	{"id": 3, "name": "بلال نادر", "phone": "0595138813", "whatsapp": "0595138813", "email": "", "address": "", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T20:03:22", "updated_at": "2025-10-24T20:03:22"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-24 20:03:22	2025-10-24 20:03:22
11	Customer	2	2	1	UPDATE	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0599070235", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-24T20:01:22"}	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0599070235", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-25T20:07:36"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-25 20:07:36	2025-10-25 20:07:36
12	Customer	2	2	1	UPDATE	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0599070235", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-25T20:07:36"}	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0599070235", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-25T20:07:36"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-25 20:08:35	2025-10-25 20:08:35
13	Customer	2	2	1	UPDATE	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0599070235", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-25T20:07:36"}	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0599070235", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-25T20:07:36"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-25 20:12:02	2025-10-25 20:12:02
14	Customer	2	2	1	UPDATE	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0599070235", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-25T20:07:36"}	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0599070235", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-25T20:07:36"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-25 20:19:35	2025-10-25 20:19:35
40	Customer	6	6	1	CREATE	\N	{"id": 6, "name": "وليد قصراوي مضخات", "phone": "0522462411", "whatsapp": "0522462411", "email": "", "address": "قصرا- نابلس", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-29T17:35:24", "updated_at": "2025-10-29T17:35:24"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-29 17:35:24	2025-10-29 17:35:24
15	Customer	2	2	1	UPDATE	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0599070235", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-25T20:07:36"}	{"id": 2, "name": "اياد الغزاوي", "phone": "0599070235", "whatsapp": "0599070235", "email": "awll@gmail.com", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-24T16:29:32", "updated_at": "2025-10-25T20:27:15"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-25 20:27:15	2025-10-25 20:27:15
16	Customer	1	1	1	UPDATE	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 283000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-23T20:45:21"}	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 283000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-23T20:45:21"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-25 21:38:49	2025-10-25 21:38:49
17	Customer	1	1	1	UPDATE	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 283000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-23T20:45:21"}	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 283000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-23T20:45:21"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-25 21:39:11	2025-10-25 21:39:11
18	Customer	1	1	1	UPDATE	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 283000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-23T20:45:21"}	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 283000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-23T20:45:21"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-25 21:46:24	2025-10-25 21:46:24
19	Sale	3	\N	1	CREATE	\N	{"id": 3, "sale_number": "SAL20251025-0001", "customer_id": 2, "seller_id": 1, "sale_date": "2025-10-26", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": "استلمت", "lines": [{"product_id": 21, "warehouse_id": 2, "quantity": 1, "unit_price": 2500.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-10-25 22:18:44.578674	2025-10-25 22:18:44
20	Customer	3	3	1	CREATE	\N	{"id": 3, "name": "أحمد الصالحي", "phone": "0599477482", "whatsapp": "0599477482", "email": "", "address": "", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-25T22:37:45", "updated_at": "2025-10-25T22:37:45"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-25 22:37:46	2025-10-25 22:37:46
21	Customer	3	3	1	UPDATE	{"id": 3, "name": "أحمد الصالحي", "phone": "0599477482", "whatsapp": "0599477482", "email": "", "address": "", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-25T22:37:45", "updated_at": "2025-10-25T22:37:45"}	{"id": 3, "name": "أحمد الصالحي", "phone": "0599477482", "whatsapp": "0599477482", "email": "", "address": "", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-25T22:37:45", "updated_at": "2025-10-25T22:37:45"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-25 22:38:01	2025-10-25 22:38:01
22	Customer	3	3	1	UPDATE	{"id": 3, "name": "أحمد الصالحي", "phone": "0599477482", "whatsapp": "0599477482", "email": "", "address": "", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-25T22:37:45", "updated_at": "2025-10-25T22:37:45"}	{"id": 3, "name": "أحمد الصالحي", "phone": "0599477482", "whatsapp": "0599477482", "email": "", "address": "", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -20400.0, "created_at": "2025-10-25T22:37:45", "updated_at": "2025-10-25T22:39:13"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-25 22:39:13	2025-10-25 22:39:13
52	Sale	9	\N	1	CREATE	\N	{"id": 9, "sale_number": "SAL20251103-0001", "customer_id": 6, "seller_id": 1, "sale_date": "2025-11-03", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 1800.0, "notes": null, "lines": [{"product_id": 24, "warehouse_id": 3, "quantity": 3, "unit_price": 1500.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-03 14:04:33.119619	2025-11-03 14:04:33
23	Customer	3	3	1	UPDATE	{"id": 3, "name": "أحمد الصالحي", "phone": "0599477482", "whatsapp": "0599477482", "email": "", "address": "", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -20400.0, "created_at": "2025-10-25T22:37:45", "updated_at": "2025-10-25T22:39:13"}	{"id": 3, "name": "أحمد الصالحي", "phone": "0599477482", "whatsapp": "0599477482", "email": "", "address": "", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -20400.0, "created_at": "2025-10-25T22:37:45", "updated_at": "2025-10-25T22:39:50"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-25 22:39:50	2025-10-25 22:39:50
24	Customer	3	3	1	UPDATE	{"id": 3, "name": "أحمد الصالحي", "phone": "0599477482", "whatsapp": "0599477482", "email": "", "address": "", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -20400.0, "created_at": "2025-10-25T22:37:45", "updated_at": "2025-10-25T22:39:50"}	{"id": 3, "name": "أحمد الصالحي", "phone": "0599477482", "whatsapp": "0599477482", "email": "", "address": "", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -20400.0, "created_at": "2025-10-25T22:37:45", "updated_at": "2025-10-25T22:41:41"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-25 22:41:41	2025-10-25 22:41:41
25	Customer	1	1	1	UPDATE	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 283000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-25T21:47:22"}	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 283000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-25T23:00:12"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-25 23:00:12	2025-10-25 23:00:12
26	Customer	1	1	1	UPDATE	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 283000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-25T23:00:12"}	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 283000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-25T23:00:12"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-25 23:00:39	2025-10-25 23:00:39
27	Customer	1	1	1	UPDATE	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 283000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-25T23:00:12"}	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 283000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-25T23:01:11"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-25 23:01:11	2025-10-25 23:01:11
28	Customer	1	1	1	UPDATE	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 283000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-25T23:01:11"}	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 283000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-25T23:01:43"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-25 23:01:43	2025-10-25 23:01:43
29	Customer	1	1	1	UPDATE	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 283000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-25T23:01:43"}	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 283000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-25T23:01:43"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-25 23:03:57	2025-10-25 23:03:57
30	Customer	1	1	1	UPDATE	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -203000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-25T23:01:43"}	{"id": 1, "name": "عامر ابو شخيدم", "phone": "0599279012", "whatsapp": "0599279012", "email": "nasersameer15@gmail.com", "address": "الخليل - فرش الهوى", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -203000.0, "created_at": "2025-10-23T20:45:21", "updated_at": "2025-10-26T11:42:30"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-26 11:42:30	2025-10-26 11:42:30
31	Customer	3	3	1	UPDATE	{"id": 3, "name": "أحمد الصالحي", "phone": "0599477482", "whatsapp": "0599477482", "email": "", "address": "", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -20400.0, "created_at": "2025-10-25T22:37:45", "updated_at": "2025-10-25T22:41:41"}	{"id": 3, "name": "أحمد الصالحي", "phone": "0599477482", "whatsapp": "0599477482", "email": "", "address": "", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -20400.0, "created_at": "2025-10-25T22:37:45", "updated_at": "2025-10-26T11:42:45"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-26 11:42:45	2025-10-26 11:42:45
32	Customer	4	\N	1	CREATE	\N	{"id": 4, "name": "فحص تجريبي 1", "phone": "0562150193", "whatsapp": "0562150193", "email": "", "address": "", "category": "عادي", "currency": "JOD", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -500.0, "created_at": "2025-10-26T13:01:44", "updated_at": "2025-10-26T13:01:44"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-26 13:01:44	2025-10-26 13:01:44
33	Customer	4	4	1	CREATE	\N	{"id": 4, "name": "منصور خليلي جماعين", "phone": "0568257928", "whatsapp": "0568257928", "email": "", "address": "نابلس-جماعين", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-26T17:30:06", "updated_at": "2025-10-26T17:30:06"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-26 17:30:06	2025-10-26 17:30:06
34	Customer	4	4	1	UPDATE	{"id": 4, "name": "منصور خليلي جماعين", "phone": "0568257928", "whatsapp": "0568257928", "email": "", "address": "نابلس-جماعين", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-26T17:30:06", "updated_at": "2025-10-26T17:30:06"}	{"id": 4, "name": "منصور خليلي جماعين", "phone": "0568257928", "whatsapp": "0568257928", "email": "", "address": "نابلس-جماعين", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-26T17:30:06", "updated_at": "2025-10-26T17:30:27"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-26 17:30:27	2025-10-26 17:30:27
35	Sale	4	\N	1	CREATE	\N	{"id": 4, "sale_number": "SAL20251026-0001", "customer_id": 4, "seller_id": 1, "sale_date": "2025-10-26", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": "", "lines": [{"product_id": 22, "warehouse_id": 2, "quantity": 1, "unit_price": 5000.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-10-26 17:32:38.2482	2025-10-26 17:32:38
36	Customer	3	3	1	UPDATE	{"id": 3, "name": "أحمد الصالحي", "phone": "0599477482", "whatsapp": "0599477482", "email": "", "address": "", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -20400.0, "created_at": "2025-10-25T22:37:45", "updated_at": "2025-10-26T11:42:45"}	{"id": 3, "name": "أحمد الصالحي", "phone": "0599477482", "whatsapp": "0599477482", "email": "", "address": "نابلس - شارع روجيب", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -20400.0, "created_at": "2025-10-25T22:37:45", "updated_at": "2025-10-26T17:44:40"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-26 17:44:40	2025-10-26 17:44:40
37	Customer	5	5	1	CREATE	\N	{"id": 5, "name": "يوسف ابو علي دورا", "phone": "0598212231", "whatsapp": "0598212231", "email": "", "address": "البيرة - المنطقة الصناعية", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-29T16:54:22", "updated_at": "2025-10-29T16:54:22"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-29 16:54:22	2025-10-29 16:54:22
38	Customer	5	5	1	UPDATE	{"id": 5, "name": "يوسف ابو علي دورا", "phone": "0598212231", "whatsapp": "0598212231", "email": "", "address": "البيرة - المنطقة الصناعية", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-29T16:54:22", "updated_at": "2025-10-29T16:54:22"}	{"id": 5, "name": "يوسف ابو علي دورا", "phone": "0598212231", "whatsapp": "0598212231", "email": "", "address": "البيرة - المنطقة الصناعية", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-29T16:54:22", "updated_at": "2025-10-29T16:54:44"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-29 16:54:44	2025-10-29 16:54:44
41	Customer	6	6	1	UPDATE	{"id": 6, "name": "وليد قصراوي مضخات", "phone": "0522462411", "whatsapp": "0522462411", "email": "", "address": "قصرا- نابلس", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-29T17:35:24", "updated_at": "2025-10-29T17:35:24"}	{"id": 6, "name": "وليد قصراوي مضخات", "phone": "0522462411", "whatsapp": "0522462411", "email": "", "address": "قصرا- نابلس", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-29T17:35:24", "updated_at": "2025-10-29T17:35:48"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-29 17:35:48	2025-10-29 17:35:48
42	Sale	5	\N	1	CREATE	\N	{"id": 5, "sale_number": "SAL20251029-0001", "customer_id": 6, "seller_id": 1, "sale_date": "2025-10-29", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": "", "lines": [{"product_id": 24, "warehouse_id": 3, "quantity": 3, "unit_price": 900.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-10-29 17:38:09.010046	2025-10-29 17:38:09
43	Sale	5	\N	1	CREATE	\N	{"id": 5, "sale_number": "SAL20251029-0001", "customer_id": 5, "seller_id": 1, "sale_date": "2025-10-29", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 500.0, "notes": "", "lines": [{"product_id": 23, "warehouse_id": 2, "quantity": 1, "unit_price": 3000.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-10-29 18:17:58.699781	2025-10-29 18:17:58
44	Sale	6	\N	1	CREATE	\N	{"id": 6, "sale_number": "SAL20251029-0002", "customer_id": 5, "seller_id": 1, "sale_date": "2025-10-29", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 100.0, "notes": "", "lines": [{"product_id": 25, "warehouse_id": 3, "quantity": 2, "unit_price": 200.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-10-29 18:22:54.266515	2025-10-29 18:22:54
45	Sale	7	\N	1	CREATE	\N	{"id": 7, "sale_number": "SAL20251029-0003", "customer_id": 6, "seller_id": 1, "sale_date": "2025-10-29", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 1800.0, "notes": "", "lines": [{"product_id": 24, "warehouse_id": 3, "quantity": 3, "unit_price": 1500.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-10-29 18:24:17.821663	2025-10-29 18:24:17
46	Customer	7	7	1	CREATE	\N	{"id": 7, "name": "محمد نعيم", "phone": "0592041000", "whatsapp": "0592041000", "email": "", "address": "رام الله-الريحان", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-29T18:35:15", "updated_at": "2025-10-29T18:35:15"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-29 18:35:15	2025-10-29 18:35:15
47	Customer	7	7	1	UPDATE	{"id": 7, "name": "محمد نعيم", "phone": "0592041000", "whatsapp": "0592041000", "email": "", "address": "رام الله-الريحان", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-29T18:35:15", "updated_at": "2025-10-29T18:35:15"}	{"id": 7, "name": "محمد نعيم", "phone": "0592041000", "whatsapp": "0592041000", "email": "", "address": "رام الله-الريحان", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-29T18:35:15", "updated_at": "2025-10-29T18:35:27"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-29 18:35:27	2025-10-29 18:35:27
48	Customer	8	8	1	CREATE	\N	{"id": 8, "name": "محمد سمير سبسطية", "phone": "0569307241", "whatsapp": "0569307241", "email": "", "address": "رام الله", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-29T20:31:40", "updated_at": "2025-10-29T20:31:40"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-29 20:31:40	2025-10-29 20:31:40
49	Customer	8	8	1	UPDATE	{"id": 8, "name": "محمد سمير سبسطية", "phone": "0569307241", "whatsapp": "0569307241", "email": "", "address": "رام الله", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-29T20:31:40", "updated_at": "2025-10-29T20:31:40"}	{"id": 8, "name": "محمد سمير سبسطية", "phone": "0569307241", "whatsapp": "0569307241", "email": "", "address": "رام الله", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-29T20:31:40", "updated_at": "2025-10-29T20:31:55"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0	2025-10-29 20:31:55	2025-10-29 20:31:55
50	Sale	8	\N	1	CREATE	\N	{"id": 8, "sale_number": "SAL20251029-0004", "customer_id": 8, "seller_id": 1, "sale_date": "2025-10-29", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 2000.0, "notes": "", "lines": [{"product_id": 27, "warehouse_id": 2, "quantity": 2, "unit_price": 4500.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-10-29 20:34:53.21393	2025-10-29 20:34:53
51	Customer	4	4	1	UPDATE	{"id": 4, "name": "منصور خليلي جماعين", "phone": "0568257928", "whatsapp": "0568257928", "email": "", "address": "نابلس-جماعين", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -500.0, "created_at": "2025-10-26T17:30:06", "updated_at": "2025-10-31T14:41:10"}	{"id": 4, "name": "منصور خليلي جماعين", "phone": "0568257928", "whatsapp": "0568257928", "email": "", "address": "نابلس-جماعين", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-10-26T17:30:06", "updated_at": "2025-11-02T19:47:50"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-02 19:47:50	2025-11-02 19:47:50
53	Customer	9	9	1	CREATE	\N	{"id": 9, "name": "احمد ياسين طولكرم", "phone": "0599675858", "whatsapp": "0599675858", "email": "", "address": "طولكرم", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-04T12:12:16", "updated_at": "2025-11-04T12:12:16"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-04 12:12:16	2025-11-04 12:12:16
54	Customer	9	9	1	UPDATE	{"id": 9, "name": "احمد ياسين طولكرم", "phone": "0599675858", "whatsapp": "0599675858", "email": "", "address": "طولكرم", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-04T12:12:16", "updated_at": "2025-11-04T12:12:16"}	{"id": 9, "name": "احمد ياسين طولكرم", "phone": "0599675858", "whatsapp": "0599675858", "email": "", "address": "طولكرم", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-04T12:12:16", "updated_at": "2025-11-04T12:12:41"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-04 12:12:41	2025-11-04 12:12:41
55	Sale	10	\N	1	CREATE	\N	{"id": 10, "sale_number": "SAL20251104-0001", "customer_id": 9, "seller_id": 1, "sale_date": "2025-11-04", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 4000.0, "notes": null, "lines": [{"product_id": 14, "warehouse_id": 2, "quantity": 1, "unit_price": 7000.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-04 12:14:19.70998	2025-11-04 12:14:19
56	Customer	10	10	1	CREATE	\N	{"id": 10, "name": "عارف القرناوي رهط", "phone": "0537615791", "whatsapp": "0537615791", "email": "", "address": "رهط-بير السبع", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-04T12:26:35", "updated_at": "2025-11-04T12:26:35"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-04 12:26:35	2025-11-04 12:26:35
57	Sale	11	\N	1	CREATE	\N	{"id": 11, "sale_number": "SAL20251104-0002", "customer_id": 10, "seller_id": 1, "sale_date": "2025-11-04", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": "تم البيع مع التركيب", "lines": [{"product_id": 28, "warehouse_id": 5, "quantity": 1, "unit_price": 40000.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-04 12:34:30.467978	2025-11-04 12:34:30
58	Customer	11	11	1	CREATE	\N	{"id": 11, "name": "سميح عموري طولكرم", "phone": "00972599356532", "whatsapp": "00972599356532", "email": "", "address": "طولكرم", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-04T14:50:07", "updated_at": "2025-11-04T14:50:07"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-04 14:50:07	2025-11-04 14:50:07
59	Sale	12	\N	1	CREATE	\N	{"id": 12, "sale_number": "SAL20251104-0003", "customer_id": 11, "seller_id": 1, "sale_date": "2025-11-04", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 2500.0, "notes": null, "lines": [{"product_id": 29, "warehouse_id": 3, "quantity": 10, "unit_price": 800.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-04 14:55:36.135109	2025-11-04 14:55:36
60	Customer	10	10	1	UPDATE	{"id": 10, "name": "عارف القرناوي رهط", "phone": "0537615791", "whatsapp": "0537615791", "email": "", "address": "رهط-بير السبع", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-04T12:26:35", "updated_at": "2025-11-04T12:26:35"}	{"id": 10, "name": "عارف القرناوي رهط", "phone": "0537615791", "whatsapp": "0537615791", "email": "", "address": "رهط-بير السبع", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-04T12:26:35", "updated_at": "2025-11-04T15:01:12"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-04 15:01:12	2025-11-04 15:01:12
61	Customer	11	11	1	UPDATE	{"id": 11, "name": "سميح عموري طولكرم", "phone": "00972599356532", "whatsapp": "00972599356532", "email": "", "address": "طولكرم", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-04T14:50:07", "updated_at": "2025-11-04T14:50:07"}	{"id": 11, "name": "سميح عموري طولكرم", "phone": "00972599356532", "whatsapp": "00972599356532", "email": "", "address": "طولكرم", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-04T14:50:07", "updated_at": "2025-11-04T15:01:31"}	10.0.4.218	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-04 15:01:31	2025-11-04 15:01:31
62	Sale	13	\N	1	CREATE	\N	{"id": 13, "sale_number": "SAL20251105-0001", "customer_id": 12, "seller_id": 1, "sale_date": "2025-11-05", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 16.0, "shipping_cost": 750.0, "discount_total": 1500.0, "notes": null, "lines": [{"product_id": 30, "warehouse_id": 6, "quantity": 33, "unit_price": 2000.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-05 15:34:45.394721	2025-11-05 15:34:45
63	Customer	12	12	1	CREATE	\N	{"id": 12, "name": "فريد ابو اياد الطوري", "phone": "0542356007", "whatsapp": "0542356007", "email": "", "address": "طمرة", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-06T12:39:09", "updated_at": "2025-11-06T12:39:09"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-06 12:39:09	2025-11-06 12:39:09
74	Sale	17	\N	1	CREATE	\N	{"id": 17, "sale_number": "SAL20251107-0004", "customer_id": 14, "seller_id": 1, "sale_date": "2025-11-07", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 10000.0, "notes": null, "lines": [{"product_id": 37, "warehouse_id": 7, "quantity": 1, "unit_price": 60000.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-07 15:37:09.013654	2025-11-07 15:37:09
64	Customer	12	12	1	UPDATE	{"id": 12, "name": "فريد ابو اياد الطوري", "phone": "0542356007", "whatsapp": "0542356007", "email": "", "address": "طمرة", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-06T12:39:09", "updated_at": "2025-11-06T12:39:09"}	{"id": 12, "name": "فريد ابو اياد الطوري", "phone": "0542356007", "whatsapp": "0542356007", "email": "", "address": "طمرة", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 15000.0, "created_at": "2025-11-06T12:39:09", "updated_at": "2025-11-06T12:39:33"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-06 12:39:33	2025-11-06 12:39:33
65	Sale	13	\N	1	CREATE	\N	{"id": 13, "sale_number": "SAL20251106-0001", "customer_id": 1, "seller_id": 1, "sale_date": "2025-11-06", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 1600.0, "notes": null, "lines": [{"product_id": 31, "warehouse_id": 3, "quantity": 2, "unit_price": 1500.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-06 12:47:12.398811	2025-11-06 12:47:12
66	Customer	13	13	1	CREATE	\N	{"id": 13, "name": "يوس ابو اسماعيل", "phone": "0595950354", "whatsapp": "0595950354", "email": "", "address": "بيت سوريك", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-07T14:23:38", "updated_at": "2025-11-07T14:23:38"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-07 14:23:38	2025-11-07 14:23:38
67	Customer	13	13	1	UPDATE	{"id": 13, "name": "يوس ابو اسماعيل", "phone": "0595950354", "whatsapp": "0595950354", "email": "", "address": "بيت سوريك", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-07T14:23:38", "updated_at": "2025-11-07T14:23:38"}	{"id": 13, "name": "يوس ابو اسماعيل", "phone": "0595950354", "whatsapp": "0595950354", "email": "", "address": "بيت سوريك", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-07T14:23:38", "updated_at": "2025-11-07T14:23:52"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-07 14:23:52	2025-11-07 14:23:52
68	Customer	13	13	1	UPDATE	{"id": 13, "name": "يوس ابو اسماعيل", "phone": "0595950354", "whatsapp": "0595950354", "email": "", "address": "بيت سوريك", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-07T14:23:38", "updated_at": "2025-11-07T14:23:52"}	{"id": 13, "name": "يوسف ابو اسماعيل", "phone": "0595950354", "whatsapp": "0595950354", "email": "", "address": "بيت سوريك", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-07T14:23:38", "updated_at": "2025-11-07T14:34:25"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-07 14:34:25	2025-11-07 14:34:25
69	Sale	14	\N	1	CREATE	\N	{"id": 14, "sale_number": "SAL20251107-0001", "customer_id": 13, "seller_id": 1, "sale_date": "2025-11-07", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 36, "warehouse_id": 3, "quantity": 1, "unit_price": 200.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 32, "warehouse_id": 3, "quantity": 1, "unit_price": 600.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 33, "warehouse_id": 3, "quantity": 1, "unit_price": 500.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 34, "warehouse_id": 3, "quantity": 1, "unit_price": 200.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 35, "warehouse_id": 6, "quantity": 1, "unit_price": 400.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-07 14:40:07.243463	2025-11-07 14:40:07
70	Customer	14	14	1	CREATE	\N	{"id": 14, "name": "محمد فارس", "phone": "0599842300", "whatsapp": "0599842300", "email": "", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-07T15:00:46", "updated_at": "2025-11-07T15:00:46"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-07 15:00:46	2025-11-07 15:00:46
71	Customer	14	14	1	UPDATE	{"id": 14, "name": "محمد فارس", "phone": "0599842300", "whatsapp": "0599842300", "email": "", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-07T15:00:46", "updated_at": "2025-11-07T15:00:46"}	{"id": 14, "name": "محمد فارس", "phone": "0599842300", "whatsapp": "0599842300", "email": "", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-07T15:00:46", "updated_at": "2025-11-07T15:00:59"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-07 15:00:59	2025-11-07 15:00:59
72	Sale	15	\N	1	CREATE	\N	{"id": 15, "sale_number": "SAL20251107-0002", "customer_id": 14, "seller_id": 1, "sale_date": "2025-11-07", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": "لعطية طولكرم", "lines": [{"product_id": 39, "warehouse_id": 2, "quantity": 1, "unit_price": 7000.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-07 15:34:26.998322	2025-11-07 15:34:27
73	Sale	16	\N	1	CREATE	\N	{"id": 16, "sale_number": "SAL20251107-0003", "customer_id": 14, "seller_id": 1, "sale_date": "2025-11-07", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 500.0, "notes": null, "lines": [{"product_id": 42, "warehouse_id": 3, "quantity": 1, "unit_price": 4000.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-07 15:35:51.712387	2025-11-07 15:35:51
75	Sale	18	\N	1	CREATE	\N	{"id": 18, "sale_number": "SAL20251107-0005", "customer_id": 14, "seller_id": 1, "sale_date": "2025-11-07", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 5000.0, "notes": "لعز الزايد", "lines": [{"product_id": 38, "warehouse_id": 5, "quantity": 1, "unit_price": 35000.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-07 15:38:49.428145	2025-11-07 15:38:49
76	Sale	19	\N	1	CREATE	\N	{"id": 19, "sale_number": "SAL20251107-0006", "customer_id": 14, "seller_id": 1, "sale_date": "2025-11-07", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 500.0, "notes": null, "lines": [{"product_id": 40, "warehouse_id": 6, "quantity": 1, "unit_price": 1500.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 41, "warehouse_id": 6, "quantity": 1, "unit_price": 300.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-07 15:40:41.514853	2025-11-07 15:40:41
77	Sale	20	\N	1	CREATE	\N	{"id": 20, "sale_number": "SAL20251107-0007", "customer_id": 14, "seller_id": 1, "sale_date": "2025-11-07", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 43, "warehouse_id": 3, "quantity": 2, "unit_price": 100.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-07 15:41:37.774531	2025-11-07 15:41:37
78	Sale	21	\N	1	CREATE	\N	{"id": 21, "sale_number": "SAL20251107-0008", "customer_id": 14, "seller_id": 1, "sale_date": "2025-11-07", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 44, "warehouse_id": 6, "quantity": 1, "unit_price": 200.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-07 15:44:16.955218	2025-11-07 15:44:16
79	Customer	14	14	1	UPDATE	{"id": 14, "name": "محمد فارس", "phone": "0599842300", "whatsapp": "0599842300", "email": "", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -92200.0, "created_at": "2025-11-07T15:00:46", "updated_at": "2025-11-07T15:00:59"}	{"id": 14, "name": "محمد فارس", "phone": "0599842300", "whatsapp": "0599842300", "email": "", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -247760.0, "created_at": "2025-11-07T15:00:46", "updated_at": "2025-11-07T15:52:56"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-07 15:52:56	2025-11-07 15:52:56
80	Customer	15	15	1	CREATE	\N	{"id": 15, "name": "حمودة ابو عامر الجواريش", "phone": "0543399985", "whatsapp": "0543399985", "email": "", "address": "الرملة", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-07T16:53:43", "updated_at": "2025-11-07T16:53:43"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-07 16:53:43	2025-11-07 16:53:43
81	Customer	16	16	1	CREATE	\N	{"id": 16, "name": "نصرالله سمير جهاد بني عودة", "phone": "0592800646", "whatsapp": "0592800646", "email": "", "address": "رافات-رام الله", "category": "بلاتيني", "currency": "USD", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-09T09:58:50", "updated_at": "2025-11-09T09:58:50"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-09 09:58:50	2025-11-09 09:58:50
82	Customer	15	15	1	UPDATE	{"id": 15, "name": "حمودة ابو عامر الجواريش", "phone": "0543399985", "whatsapp": "0543399985", "email": "", "address": "الرملة", "category": "عادي", "currency": "ILS", "is_active": false, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-07T16:53:43", "updated_at": "2025-11-07T16:53:43"}	{"id": 15, "name": "حمودة ابو عامر الجواريش", "phone": "0543399985", "whatsapp": "0543399985", "email": "", "address": "الرملة", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-07T16:53:43", "updated_at": "2025-11-09T20:33:56"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-09 20:33:56	2025-11-09 20:33:56
83	Customer	17	17	1	CREATE	\N	{"id": 17, "name": "عدنان السلامين", "phone": "0599432107", "whatsapp": "0599432107", "email": "", "address": "دورا-الخليل", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-09T20:44:42", "updated_at": "2025-11-09T20:44:42"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-09 20:44:42	2025-11-09 20:44:42
84	Sale	22	\N	1	CREATE	\N	{"id": 22, "sale_number": "SAL20251109-0001", "customer_id": 17, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-09", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 300.0, "notes": null, "lines": [{"product_id": 45, "warehouse_id": 6, "quantity": 1, "unit_price": 800.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-09 20:47:15.224985	2025-11-09 20:47:15
85	Customer	18	18	1	CREATE	\N	{"id": 18, "name": "قنديل للاسفلت والتعهدات العامة", "phone": "0568335555", "whatsapp": "0568335555", "email": "", "address": "رافات-رام الله", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-09T20:51:26", "updated_at": "2025-11-09T20:51:26"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-09 20:51:26	2025-11-09 20:51:26
86	Sale	23	\N	1	CREATE	\N	{"id": 23, "sale_number": "SAL20251109-0002", "customer_id": 18, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-09", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 46, "warehouse_id": 3, "quantity": 1, "unit_price": 450.0, "discount_rate": 22.22, "tax_rate": 0.0}, {"product_id": 47, "warehouse_id": 3, "quantity": 1, "unit_price": 200.0, "discount_rate": 25.0, "tax_rate": 0.0}, {"product_id": 48, "warehouse_id": 8, "quantity": 1, "unit_price": 800.0, "discount_rate": 37.5, "tax_rate": 0.0}]}	\N	\N	2025-11-09 21:26:18.946515	2025-11-09 21:26:18
87	Customer	19	19	1	CREATE	\N	{"id": 19, "name": "ابو ناصر ونش", "phone": "0599756559", "whatsapp": "0599756559", "email": "", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-09T21:35:54", "updated_at": "2025-11-09T21:35:54"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-09 21:35:54	2025-11-09 21:35:54
88	Customer	20	20	1	CREATE	\N	{"id": 20, "name": "زهران ابو ربحي", "phone": "0537318120", "whatsapp": "0537318120", "email": "", "address": "طيرة المثلث", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-09T21:37:37", "updated_at": "2025-11-09T21:37:37"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-09 21:37:37	2025-11-09 21:37:37
89	Sale	24	\N	1	CREATE	\N	{"id": 24, "sale_number": "SAL20251109-0003", "customer_id": 19, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-09", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": "استلم طرمبة وباقي 3", "lines": [{"product_id": 58, "warehouse_id": 2, "quantity": 4, "unit_price": 5000.0, "discount_rate": 35.0, "tax_rate": 0.0}]}	\N	\N	2025-11-09 21:55:58.282054	2025-11-09 21:55:58
90	Sale	25	\N	1	CREATE	\N	{"id": 25, "sale_number": "SAL20251109-0004", "customer_id": 19, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-09", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 59, "warehouse_id": 8, "quantity": 1, "unit_price": 800.0, "discount_rate": 37.5, "tax_rate": 0.0}, {"product_id": 60, "warehouse_id": 8, "quantity": 1, "unit_price": 400.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 52, "warehouse_id": 1, "quantity": 2, "unit_price": 1500.0, "discount_rate": 20.0, "tax_rate": 0.0}, {"product_id": 51, "warehouse_id": 1, "quantity": 5, "unit_price": 1000.0, "discount_rate": 20.0, "tax_rate": 0.0}, {"product_id": 49, "warehouse_id": 1, "quantity": 4, "unit_price": 800.0, "discount_rate": 25.0, "tax_rate": 0.0}, {"product_id": 50, "warehouse_id": 1, "quantity": 2, "unit_price": 1500.0, "discount_rate": 20.0, "tax_rate": 0.0}]}	\N	\N	2025-11-09 22:10:51.809818	2025-11-09 22:10:51
91	Sale	26	\N	1	CREATE	\N	{"id": 26, "sale_number": "SAL20251109-0005", "customer_id": 20, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-10", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 55, "warehouse_id": 4, "quantity": 1, "unit_price": 1200.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 54, "warehouse_id": 4, "quantity": 1, "unit_price": 800.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 53, "warehouse_id": 4, "quantity": 1, "unit_price": 800.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 56, "warehouse_id": 4, "quantity": 1, "unit_price": 2000.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 57, "warehouse_id": 3, "quantity": 1, "unit_price": 2000.0, "discount_rate": 60.0, "tax_rate": 0.0}]}	\N	\N	2025-11-09 22:17:09.970706	2025-11-09 22:17:09
92	Customer	20	20	1	UPDATE	{"id": 20, "name": "زهران ابو ربحي", "phone": "0537318120", "whatsapp": "0537318120", "email": "", "address": "طيرة المثلث", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -5600.0, "created_at": "2025-11-09T21:37:37", "updated_at": "2025-11-09T21:37:37"}	{"id": 20, "name": "زهران ابو ربحي", "phone": "0537318120", "whatsapp": "0537318120", "email": "", "address": "طيرة المثلث", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -5600.0, "created_at": "2025-11-09T21:37:37", "updated_at": "2025-11-09T21:37:37"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-09 22:20:08	2025-11-09 22:20:08
93	Sale	26	\N	1	UPDATE	{"id": 26, "sale_number": "SAL20251109-0005", "customer_id": 20, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-10", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 55, "warehouse_id": 4, "quantity": 1, "unit_price": 1200.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 54, "warehouse_id": 4, "quantity": 1, "unit_price": 800.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 53, "warehouse_id": 4, "quantity": 1, "unit_price": 800.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 56, "warehouse_id": 4, "quantity": 1, "unit_price": 2000.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 57, "warehouse_id": 3, "quantity": 1, "unit_price": 2000.0, "discount_rate": 60.0, "tax_rate": 0.0}]}	{"id": 26, "sale_number": "SAL20251109-0005", "customer_id": 20, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-10", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 55, "warehouse_id": 4, "quantity": 1, "unit_price": 1200.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 54, "warehouse_id": 4, "quantity": 1, "unit_price": 800.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 53, "warehouse_id": 4, "quantity": 1, "unit_price": 800.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 56, "warehouse_id": 4, "quantity": 1, "unit_price": 2000.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 57, "warehouse_id": 3, "quantity": 1, "unit_price": 2000.0, "discount_rate": 60.0, "tax_rate": 0.0}]}	\N	\N	2025-11-09 22:21:38.250737	2025-11-09 22:21:38
94	Customer	21	21	1	CREATE	\N	{"id": 21, "name": "فيصل الجمل", "phone": "0592922224", "whatsapp": "0592922224", "email": "", "address": "بيت سوريك", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-10T12:30:46", "updated_at": "2025-11-10T12:30:46"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-10 12:30:46	2025-11-10 12:30:46
95	Sale	27	\N	1	CREATE	\N	{"id": 27, "sale_number": "SAL20251110-0001", "customer_id": 21, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-10", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 15, "warehouse_id": 2, "quantity": 1, "unit_price": 2000.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-10 12:33:35.574251	2025-11-10 12:33:35
96	Sale	23	\N	1	UPDATE	{"id": 23, "sale_number": "SAL20251109-0002", "customer_id": 18, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-09", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 46, "warehouse_id": 3, "quantity": 1, "unit_price": 450.0, "discount_rate": 22.22, "tax_rate": 0.0}, {"product_id": 47, "warehouse_id": 3, "quantity": 1, "unit_price": 200.0, "discount_rate": 25.0, "tax_rate": 0.0}, {"product_id": 48, "warehouse_id": 8, "quantity": 1, "unit_price": 800.0, "discount_rate": 37.5, "tax_rate": 0.0}]}	{"id": 23, "sale_number": "SAL20251109-0002", "customer_id": 18, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-09", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 46, "warehouse_id": 3, "quantity": 1, "unit_price": 450.0, "discount_rate": 22.22, "tax_rate": 0.0}, {"product_id": 47, "warehouse_id": 3, "quantity": 1, "unit_price": 200.0, "discount_rate": 25.0, "tax_rate": 0.0}, {"product_id": 48, "warehouse_id": 8, "quantity": 1, "unit_price": 800.0, "discount_rate": 37.5, "tax_rate": 0.0}]}	\N	\N	2025-11-10 22:19:03.813239	2025-11-10 22:19:03
97	Customer	22	22	1	CREATE	\N	{"id": 22, "name": "سامي كمال الطميزي", "phone": "0598167539", "whatsapp": "0598167539", "email": "", "address": "اذنا - الخليل", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": -1000.0, "created_at": "2025-11-10T22:32:42", "updated_at": "2025-11-10T22:32:42"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-10 22:32:42	2025-11-10 22:32:42
98	Customer	23	23	1	CREATE	\N	{"id": 23, "name": "علي حنيحن", "phone": "0595285333", "whatsapp": "0595285333", "email": "", "address": "حلول-الخليل", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-12T12:33:55", "updated_at": "2025-11-12T12:33:55"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-12 12:33:56	2025-11-12 12:33:56
99	Sale	28	\N	1	CREATE	\N	{"id": 28, "sale_number": "SAL20251112-0001", "customer_id": 23, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-12", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 63, "warehouse_id": 3, "quantity": 1, "unit_price": 2000.0, "discount_rate": 35.0, "tax_rate": 0.0}]}	\N	\N	2025-11-12 12:42:25.760759	2025-11-12 12:42:25
100	Customer	24	24	1	CREATE	\N	{"id": 24, "name": "طرمبة جرافة فولفو", "phone": "0599711354", "whatsapp": "0599711354", "email": "", "address": "بيت لقيا-رام الله", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-12T14:32:59", "updated_at": "2025-11-12T14:32:59"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0	2025-11-12 14:32:59	2025-11-12 14:32:59
101	Sale	29	\N	1	CREATE	\N	{"id": 29, "sale_number": "SAL20251112-0002", "customer_id": 24, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-12", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 64, "warehouse_id": 2, "quantity": 1, "unit_price": 10000.0, "discount_rate": 10.0, "tax_rate": 0.0}]}	\N	\N	2025-11-12 14:34:59.182828	2025-11-12 14:34:59
102	Customer	25	25	1	CREATE	\N	{"id": 25, "name": "فادي غيث", "phone": "0598888657", "whatsapp": "0598888657", "email": "", "address": "الخليل- المنقطة الجنوبية", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-12T17:32:11", "updated_at": "2025-11-12T17:32:11"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-12 17:32:11	2025-11-12 17:32:11
103	Sale	30	\N	1	CREATE	\N	{"id": 30, "sale_number": "SAL20251112-0003", "customer_id": 25, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-12", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 65, "warehouse_id": 5, "quantity": 2, "unit_price": 8000.0, "discount_rate": 25.0, "tax_rate": 0.0}]}	\N	\N	2025-11-12 17:37:52.816276	2025-11-12 17:37:52
104	Customer	26	26	1	CREATE	\N	{"id": 26, "name": "شركة اتكو الهندسية", "phone": "0598890792", "whatsapp": "0598890792", "email": "", "address": "رام الله - بيتونيا", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-12T19:48:13", "updated_at": "2025-11-12T19:48:13"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-12 19:48:13	2025-11-12 19:48:13
105	Customer	27	27	1	CREATE	\N	{"id": 27, "name": "احمد ابو رزق جماعين", "phone": "0592571618", "whatsapp": "0592571618", "email": "", "address": "جماعين - نابلس", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-13T10:32:14", "updated_at": "2025-11-13T10:32:14"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-13 10:32:14	2025-11-13 10:32:14
106	Sale	31	\N	1	CREATE	\N	{"id": 31, "sale_number": "SAL20251113-0001", "customer_id": 27, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-13", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 66, "warehouse_id": 2, "quantity": 1, "unit_price": 7000.0, "discount_rate": 50.0, "tax_rate": 0.0}]}	\N	\N	2025-11-13 10:36:37.994186	2025-11-13 10:36:37
107	Customer	28	28	1	CREATE	\N	{"id": 28, "name": "ادهم قطام", "phone": "0568828204", "whatsapp": "0568828204", "email": "", "address": "اريحا", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-13T22:45:35", "updated_at": "2025-11-13T22:45:35"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-13 22:45:35	2025-11-13 22:45:35
108	Sale	32	\N	1	CREATE	\N	{"id": 32, "sale_number": "SAL20251113-0002", "customer_id": 28, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-14", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 2300.0, "notes": null, "lines": [{"product_id": 67, "warehouse_id": 2, "quantity": 1, "unit_price": 5000.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-13 22:53:04.666345	2025-11-13 22:53:04
109	Customer	30	30	1	CREATE	\N	{"id": 30, "name": "طوب شاهين", "phone": "00000000000", "whatsapp": "00000000000", "email": "", "address": "بيتونيا", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-16T20:12:21", "updated_at": "2025-11-16T20:12:21"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-16 20:12:21	2025-11-16 20:12:21
110	Customer	31	31	1	CREATE	\N	{"id": 31, "name": "ونشات رام الله", "phone": "000000000000", "whatsapp": "000000000000", "email": "", "address": "", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-16T20:13:00", "updated_at": "2025-11-16T20:13:00"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-16 20:13:00	2025-11-16 20:13:00
111	Sale	33	\N	1	CREATE	\N	{"id": 33, "sale_number": "SAL20251116-0001", "customer_id": 30, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-16", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 71, "warehouse_id": 3, "quantity": 25, "unit_price": 20.0, "discount_rate": 50.0, "tax_rate": 0.0}]}	\N	\N	2025-11-16 20:15:17.480107	2025-11-16 20:15:17
112	Sale	34	\N	1	CREATE	\N	{"id": 34, "sale_number": "SAL20251116-0002", "customer_id": 31, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-16", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 10.0, "notes": null, "lines": [{"product_id": 71, "warehouse_id": 3, "quantity": 15, "unit_price": 16.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-16 20:16:55.756675	2025-11-16 20:16:55
113	Customer	32	32	1	CREATE	\N	{"id": 32, "name": "مجهول", "phone": "0000000000", "whatsapp": "0000000000", "email": "", "address": "", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-16T20:18:30", "updated_at": "2025-11-16T20:18:30"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-16 20:18:30	2025-11-16 20:18:30
114	Sale	35	\N	1	CREATE	\N	{"id": 35, "sale_number": "SAL20251116-0003", "customer_id": 32, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-16", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 100.0, "notes": null, "lines": [{"product_id": 70, "warehouse_id": 3, "quantity": 1, "unit_price": 850.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-16 20:19:31.429531	2025-11-16 20:19:31
115	Sale	36	\N	1	CREATE	\N	{"id": 36, "sale_number": "SAL20251117-0001", "customer_id": 32, "seller_id": 1, "seller_employee_id": 1, "sale_date": "2025-11-17", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 72, "warehouse_id": 3, "quantity": 1, "unit_price": 250.0, "discount_rate": 20.0, "tax_rate": 0.0}, {"product_id": 73, "warehouse_id": 3, "quantity": 2, "unit_price": 50.0, "discount_rate": 30.0, "tax_rate": 0.0}]}	\N	\N	2025-11-17 15:03:27.79012	2025-11-17 15:03:27
116	Sale	37	\N	1	CREATE	\N	{"id": 37, "sale_number": "SAL20251117-0002", "customer_id": 32, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-17", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 74, "warehouse_id": 3, "quantity": 1, "unit_price": 200.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-17 15:07:31.537667	2025-11-17 15:07:31
117	Payment	121	\N	1	CREATE	\N	\N	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-18 16:28:10.369797	2025-11-18 16:28:10
118	Sale	38	\N	1	CREATE	\N	{"id": 38, "sale_number": "SAL20251125-0001", "customer_id": 1, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-25", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 75, "warehouse_id": 1, "quantity": 1, "unit_price": 7500.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-25 10:43:07.183361	2025-11-25 10:43:07
119	Customer	37	37	1	CREATE	\N	{"id": 37, "name": "سامح الباشا", "phone": "0503004498", "whatsapp": "0503004498", "email": "", "address": "", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-25T10:45:11", "updated_at": "2025-11-25T10:45:11"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-25 10:45:11	2025-11-25 10:45:11
120	Sale	39	\N	1	CREATE	\N	{"id": 39, "sale_number": "SAL20251125-0002", "customer_id": 37, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-25", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 3000.0, "notes": null, "lines": [{"product_id": 20, "warehouse_id": 2, "quantity": 1, "unit_price": 13000.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-25 10:48:00.851788	2025-11-25 10:48:00
121	Sale	40	\N	1	CREATE	\N	{"id": 40, "sale_number": "SAL20251125-0003", "customer_id": 2, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-25", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 1000.0, "notes": null, "lines": [{"product_id": 77, "warehouse_id": 2, "quantity": 1, "unit_price": 3500.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-25 11:00:04.642328	2025-11-25 11:00:04
122	Customer	38	38	1	CREATE	\N	{"id": 38, "name": "موسى الخيري", "phone": "0505351728", "whatsapp": "0505351728", "email": "", "address": "رام الله-كفرعقب", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-25T13:07:50", "updated_at": "2025-11-25T13:07:50"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-25 13:07:50	2025-11-25 13:07:50
123	Sale	41	\N	1	CREATE	\N	{"id": 41, "sale_number": "SAL20251125-0004", "customer_id": 38, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-25", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 2950.0, "notes": null, "lines": [{"product_id": 78, "warehouse_id": 3, "quantity": 4, "unit_price": 600.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 80, "warehouse_id": 3, "quantity": 4, "unit_price": 250.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 79, "warehouse_id": 3, "quantity": 1, "unit_price": 2000.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 82, "warehouse_id": 3, "quantity": 5, "unit_price": 350.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 81, "warehouse_id": 3, "quantity": 4, "unit_price": 250.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-25 13:19:20.035537	2025-11-25 13:19:20
124	Customer	39	39	1	CREATE	\N	{"id": 39, "name": "محمد شعيب", "phone": "0597418414", "whatsapp": "0597418414", "email": "", "address": "رام الله-ام الشرايط", "category": "عادي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 0.0, "balance": 0.0, "created_at": "2025-11-25T13:26:57", "updated_at": "2025-11-25T13:26:57"}	10.0.5.32	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-25 13:26:57	2025-11-25 13:26:57
125	Sale	42	\N	1	CREATE	\N	{"id": 42, "sale_number": "SAL20251125-0005", "customer_id": 13, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-25", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 85, "warehouse_id": 3, "quantity": 1, "unit_price": 1200.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-25 13:31:38.651686	2025-11-25 13:31:38
126	Sale	43	\N	1	CREATE	\N	{"id": 43, "sale_number": "SAL20251125-0006", "customer_id": 13, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-25", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 84, "warehouse_id": 3, "quantity": 2, "unit_price": 200.0, "discount_rate": 50.0, "tax_rate": 0.0}]}	\N	\N	2025-11-25 13:33:29.885425	2025-11-25 13:33:29
127	Sale	44	\N	1	CREATE	\N	{"id": 44, "sale_number": "SAL20251125-0007", "customer_id": 39, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-25", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 86, "warehouse_id": 3, "quantity": 3, "unit_price": 300.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-25 13:36:04.832723	2025-11-25 13:36:04
128	Sale	44	\N	1	UPDATE	{"id": 44, "sale_number": "SAL20251125-0007", "customer_id": 39, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-25", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 86, "warehouse_id": 3, "quantity": 3, "unit_price": 300.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	{"id": 44, "sale_number": "SAL20251125-0007", "customer_id": 39, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-25", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 86, "warehouse_id": 3, "quantity": 3, "unit_price": 300.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-25 13:37:35.798764	2025-11-25 13:37:35
129	Sale	45	\N	1	CREATE	\N	{"id": 45, "sale_number": "SAL20251125-0008", "customer_id": 27, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-25", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 88, "warehouse_id": 2, "quantity": 1, "unit_price": 2000.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-25 13:40:30.831723	2025-11-25 13:40:30
130	Sale	46	\N	1	CREATE	\N	{"id": 46, "sale_number": "SAL20251125-0009", "customer_id": 32, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-26", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 300.0, "notes": null, "lines": [{"product_id": 89, "warehouse_id": 3, "quantity": 1, "unit_price": 1300.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-25 22:14:03.843386	2025-11-25 22:14:03
131	Sale	47	\N	1	CREATE	\N	{"id": 47, "sale_number": "SAL20251128-0001", "customer_id": 32, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-28", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 1050.0, "notes": null, "lines": [{"product_id": 91, "warehouse_id": 8, "quantity": 1, "unit_price": 1500.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-28 14:45:34.734598	2025-11-28 14:45:34
132	Sale	48	\N	1	CREATE	\N	{"id": 48, "sale_number": "SAL20251128-0002", "customer_id": 32, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-28", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 700.0, "notes": null, "lines": [{"product_id": 92, "warehouse_id": 4, "quantity": 1, "unit_price": 1500.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-28 14:59:39.797584	2025-11-28 14:59:39
133	Sale	49	\N	1	CREATE	\N	{"id": 49, "sale_number": "SAL20251128-0003", "customer_id": 32, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-28", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 94, "warehouse_id": 1, "quantity": 1, "unit_price": 29000.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-28 15:39:29.423475	2025-11-28 15:39:29
134	Sale	50	\N	1	CREATE	\N	{"id": 50, "sale_number": "SAL20251130-0001", "customer_id": 32, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-30", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 1800.0, "notes": null, "lines": [{"product_id": 95, "warehouse_id": 6, "quantity": 2, "unit_price": 1500.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-30 07:38:57.009198	2025-11-30 07:38:57
135	Sale	51	\N	1	CREATE	\N	{"id": 51, "sale_number": "SAL20251130-0002", "customer_id": 36, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-11-30", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 2900.0, "notes": null, "lines": [{"product_id": 96, "warehouse_id": 3, "quantity": 4, "unit_price": 1200.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 97, "warehouse_id": 3, "quantity": 1, "unit_price": 1200.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 98, "warehouse_id": 3, "quantity": 1, "unit_price": 1000.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-11-30 19:46:46.964307	2025-11-30 19:46:46
136	Sale	52	\N	1	CREATE	\N	{"id": 52, "sale_number": "SAL20251201-0001", "customer_id": 32, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-12-01", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 30, "warehouse_id": 3, "quantity": 1, "unit_price": 200.0, "discount_rate": 25.0, "tax_rate": 0.0}]}	\N	\N	2025-12-01 14:15:01.502036	2025-12-01 14:15:01
137	Sale	53	\N	1	CREATE	\N	{"id": 53, "sale_number": "SAL20251202-0001", "customer_id": 13, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-12-02", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 100, "warehouse_id": 4, "quantity": 2, "unit_price": 200.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 99, "warehouse_id": 4, "quantity": 2, "unit_price": 500.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-12-02 20:40:58.585551	2025-12-02 20:40:58
138	Sale	54	\N	1	CREATE	\N	{"id": 54, "sale_number": "SAL20251202-0002", "customer_id": 17, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-12-02", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 300.0, "notes": null, "lines": [{"product_id": 24, "warehouse_id": 3, "quantity": 1, "unit_price": 1500.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-12-02 20:42:21.580655	2025-12-02 20:42:21
139	Sale	55	\N	1	CREATE	\N	{"id": 55, "sale_number": "SAL20251204-0001", "customer_id": 13, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-12-05", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 100, "warehouse_id": 4, "quantity": 1, "unit_price": 200.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 101, "warehouse_id": 4, "quantity": 1, "unit_price": 650.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-12-04 22:42:10.708659	2025-12-04 22:42:10
140	Sale	56	\N	1	CREATE	\N	{"id": 56, "sale_number": "SAL20251204-0002", "customer_id": 34, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-12-05", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 102, "warehouse_id": 3, "quantity": 3, "unit_price": 800.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 103, "warehouse_id": 3, "quantity": 3, "unit_price": 300.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 104, "warehouse_id": 3, "quantity": 1, "unit_price": 800.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-12-04 23:05:37.601994	2025-12-04 23:05:37
141	Sale	57	\N	1	CREATE	\N	{"id": 57, "sale_number": "SAL20251205-0001", "customer_id": 14, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-12-05", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 106, "warehouse_id": 3, "quantity": 5, "unit_price": 80.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 105, "warehouse_id": 3, "quantity": 217, "unit_price": 20.0, "discount_rate": 50.0, "tax_rate": 0.0}, {"product_id": 107, "warehouse_id": 3, "quantity": 14, "unit_price": 20.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-12-05 19:52:44.494591	2025-12-05 19:52:44
142	Customer	14	14	1	UPDATE	{"id": 14, "name": "محمد فارس", "phone": "0599842300", "whatsapp": "0599842300", "email": "", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": false, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 96000.0, "balance": -154610.0, "created_at": "2025-11-07T15:00:46", "updated_at": "2025-12-06T18:56:59"}	{"id": 14, "name": "محمد فارس", "phone": "0599842300", "whatsapp": "0599842300", "email": "", "address": "رام الله", "category": "ذهبي", "currency": "ILS", "is_active": true, "is_online": true, "is_archived": false, "discount_rate": 0.0, "credit_limit": 0.0, "total_invoiced": 0.0, "total_paid": 96000.0, "balance": -154610.0, "created_at": "2025-11-07T15:00:46", "updated_at": "2025-12-06T19:37:12"}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	2025-12-06 19:37:12	2025-12-06 19:37:12
143	Sale	58	\N	1	CREATE	\N	{"id": 58, "sale_number": "SAL20251208-0001", "customer_id": 13, "seller_id": 1, "seller_employee_id": 1, "sale_date": "2025-12-09", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 109, "warehouse_id": 3, "quantity": 1, "unit_price": 350.0, "discount_rate": 0.0, "tax_rate": 0.0}, {"product_id": 108, "warehouse_id": 3, "quantity": 1, "unit_price": 1200.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-12-08 23:15:19.819061	2025-12-08 23:15:19
144	Sale	59	\N	1	CREATE	\N	{"id": 59, "sale_number": "SAL20251208-0002", "customer_id": 34, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-12-09", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 81, "warehouse_id": 3, "quantity": 4, "unit_price": 250.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-12-08 23:18:26.312531	2025-12-08 23:18:26
145	SaleReturn	1	\N	1	CREATE	\N	\N	\N	\N	2025-12-08 23:24:46	2025-12-08 23:24:46
146	SaleReturn	1	\N	1	CANCEL	\N	\N	\N	\N	2025-12-08 23:24:59	2025-12-08 23:24:59
147	SaleReturn	2	\N	1	CREATE	\N	\N	\N	\N	2025-12-08 23:26:03	2025-12-08 23:26:03
148	Sale	60	\N	1	CREATE	\N	{"id": 60, "sale_number": "SAL20251209-0001", "customer_id": 1, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-12-10", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 100.0, "notes": "شحن محرك بكار عدد 2", "lines": [{"product_id": 110, "warehouse_id": 10, "quantity": 2600, "unit_price": 10.0, "discount_rate": 15.0, "tax_rate": 0.0}]}	\N	\N	2025-12-09 23:16:01.102843	2025-12-09 23:16:01
149	Sale	61	\N	1	CREATE	\N	{"id": 61, "sale_number": "SAL20251214-0001", "customer_id": 2, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-12-14", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 15, "warehouse_id": 2, "quantity": 1, "unit_price": 2000.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-12-14 14:04:29.99073	2025-12-14 14:04:29
150	Sale	62	\N	1	CREATE	\N	{"id": 62, "sale_number": "SAL20251214-0002", "customer_id": 2, "seller_id": 1, "seller_employee_id": 3, "sale_date": "2025-12-14", "status": "CONFIRMED", "currency": "ILS", "tax_rate": 0.0, "shipping_cost": 0.0, "discount_total": 0.0, "notes": null, "lines": [{"product_id": 112, "warehouse_id": 2, "quantity": 2, "unit_price": 500.0, "discount_rate": 0.0, "tax_rate": 0.0}]}	\N	\N	2025-12-14 14:07:06.081603	2025-12-14 14:07:06
\.


--
-- Data for Name: auth_audit; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_audit (id, user_id, event, success, ip, user_agent, note, metadata, created_at) FROM stdin;
\.


--
-- Data for Name: bank_accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bank_accounts (id, code, name, bank_name, account_number, iban, swift_code, currency, branch_id, gl_account_code, opening_balance, current_balance, last_reconciled_date, notes, is_active, created_by, updated_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: bank_reconciliations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bank_reconciliations (id, bank_account_id, reconciliation_number, period_start, period_end, book_balance, bank_balance, unmatched_book_count, unmatched_bank_count, unmatched_book_amount, unmatched_bank_amount, reconciled_by, reconciled_at, approved_by, approved_at, status, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: bank_statements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bank_statements (id, bank_account_id, statement_number, statement_date, period_start, period_end, opening_balance, closing_balance, total_deposits, total_withdrawals, file_path, imported_at, imported_by, status, notes, created_by, updated_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: bank_transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bank_transactions (id, bank_account_id, statement_id, transaction_date, value_date, reference, description, debit, credit, balance, matched, payment_id, gl_batch_id, reconciliation_id, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: branches; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.branches (id, name, code, is_active, address, city, geo_lat, geo_lng, phone, email, manager_user_id, manager_employee_id, timezone, currency, tax_id, notes, is_archived, archived_at, archived_by, archive_reason, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: budget_commitments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.budget_commitments (id, budget_id, source_type, source_id, committed_amount, commitment_date, status, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: budgets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.budgets (id, fiscal_year, account_code, branch_id, site_id, allocated_amount, notes, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: checks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.checks (id, check_number, check_bank, check_date, check_due_date, amount, currency, fx_rate_issue, fx_rate_issue_source, fx_rate_issue_timestamp, fx_rate_issue_base, fx_rate_issue_quote, fx_rate_cash, fx_rate_cash_source, fx_rate_cash_timestamp, fx_rate_cash_base, fx_rate_cash_quote, direction, status, drawer_name, drawer_phone, drawer_id_number, drawer_address, payee_name, payee_phone, payee_account, notes, internal_notes, reference_number, status_history, customer_id, supplier_id, partner_id, payment_id, created_by_id, is_archived, archived_at, archived_by, archive_reason, resubmit_allowed_count, legal_return_allowed_count, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: cost_allocation_execution_lines; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cost_allocation_execution_lines (id, execution_id, source_cost_center_id, target_cost_center_id, amount, percentage, gl_batch_id) FROM stdin;
\.


--
-- Data for Name: cost_allocation_executions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cost_allocation_executions (id, rule_id, execution_date, total_amount, status, gl_batch_id, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: cost_allocation_lines; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cost_allocation_lines (id, rule_id, target_cost_center_id, percentage, fixed_amount, allocation_driver, driver_value, notes) FROM stdin;
\.


--
-- Data for Name: cost_allocation_rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cost_allocation_rules (id, code, name, description, source_cost_center_id, allocation_method, frequency, is_active, auto_execute, last_executed_at, next_execution_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: cost_center_alert_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cost_center_alert_logs (id, alert_id, cost_center_id, triggered_at, trigger_value, threshold_value, message, severity, notified_users, notification_sent, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: cost_center_alerts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cost_center_alerts (id, cost_center_id, alert_type, threshold_type, threshold_value, is_active, notify_manager, notify_emails, notify_users, last_triggered_at, trigger_count, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: cost_center_allocations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cost_center_allocations (id, cost_center_id, source_type, source_id, amount, percentage, allocation_date, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: cost_centers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cost_centers (id, code, name, parent_id, description, manager_id, gl_account_code, budget_amount, actual_amount, is_active, created_by, updated_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: currencies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.currencies (code, name, symbol, decimals, is_active) FROM stdin;
ILS	شيكل إسرائيلي	ILS	2	t
USD	دولار أمريكي	USD	2	t
EUR	يورو	EUR	2	t
JOD	دينار أردني	JOD	2	t
AED	درهم إماراتي	AED	2	t
SAR	ريال سعودي	SAR	2	t
EGP	جنيه مصري	EGP	2	t
GBP	جنيه إسترليني	GBP	2	t
\.


--
-- Data for Name: customer_loyalty; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customer_loyalty (id, customer_id, total_points, available_points, used_points, loyalty_tier, total_spent, last_activity, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: customer_loyalty_points; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customer_loyalty_points (id, customer_id, points, reason, type, reference_id, reference_type, expires_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customers (id, name, phone, whatsapp, email, address, password_hash, category, notes, is_active, is_online, is_archived, archived_at, archived_by, archive_reason, credit_limit, discount_rate, currency, opening_balance, current_balance, sales_balance, returns_balance, invoices_balance, services_balance, preorders_balance, online_orders_balance, payments_in_balance, payments_out_balance, checks_in_balance, checks_out_balance, returned_checks_in_balance, returned_checks_out_balance, expenses_balance, service_expenses_balance, created_at, updated_at) FROM stdin;
1	عامر ابو شخيدم	0599279012	0599279012	nasersameer15@gmail.com	الخليل - فرش الهوى	scrypt:32768:8:1$DQQ3FZfkNfUvBNwa$7cc2496685e9e734334f353d89a38c8692ae694fa110720f5f66c0db0a11bf65898ddd4a0144845656e98065283e5f	ذهبي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	-22500.00	291900.00	0.00	0.00	0.00	0.00	0.00	281400.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-10-23 20:45:21	2025-12-10 17:21:58
2	اياد الغزاوي	0599070235	0599070235	awll@gmail.com	رام الله	scrypt:32768:8:1$CHNlfzqojmeVzWxc$077534cbf525f9ca1f837d4e1118558d78b24cd0cb429925cffcec7b7fb3c1c1c4b2c4e103ebac12c6462757595f94	ذهبي	حساب قديم منهي عليه بتاريخ 18-4-2025 11200 لنا عند اياد	t	t	f	\N	\N	\N	0.00	0.00	ILS	-11200.00	-21200.00	60500.00	0.00	0.00	0.00	0.00	0.00	50500.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-10-24 16:29:32	2025-12-08 09:20:48
3	أحمد الصالحي	0599477482	0599477482	azad@0599477482	نابلس - شارع روجيب	scrypt:32768:8:1$dROIONPn87yUWH98$67764f205a5c0057094fec77a528f5a87a733e041aeba674a673d43329e1e348d2f126d8f5e19f40f790cf1ac33d0d	ذهبي	لنا عند احمد باقي ثمن مزليك من دبي وشحن بضاعة 20400	t	t	f	\N	\N	\N	0.00	0.00	ILS	-20400.00	20400.00	0.00	0.00	0.00	0.00	0.00	0.00	20400.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-10-25 22:37:45	2025-12-06 19:58:04
4	منصور خليلي جماعين	0568257928	0568257928	azad@0568257928	نابلس-جماعين	scrypt:32768:8:1$Gvf392gUQQRSEM7P$479db2a852773e5b8a3260aaef10e59903ddd4971a54092b40ef707995a4a7f5eb323956e70bfbda4b462695febf5c	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	5000.00	0.00	0.00	0.00	0.00	0.00	5000.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-10-26 17:30:06	2025-12-06 19:58:04
5	يوسف ابو علي دورا	0598212231	0598212231	azad@0598212231	البيرة - المنطقة الصناعية	scrypt:32768:8:1$jUoggDrM1azcBACe$ff0342a77fb7d5d7c5b8c31674f1e68bdbe69c12cc5798094dc42c39fec379804b59c1f1673ab554c6b8b17411cdd4	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	-300.00	2800.00	0.00	0.00	0.00	0.00	0.00	2500.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-10-29 16:54:22	2025-12-06 19:58:04
6	وليد قصراوي مضخات	0522462411	0522462411	azad@0522462411	قصرا- نابلس	scrypt:32768:8:1$JrBC2sxRuuFuDcRH$697bbf5aba6bf3bee1bdbe0e27f9dbf97427256c7177cf4a9033b28153b678d2acd159128968244ea77a417770b6ff	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	5400.00	0.00	0.00	0.00	0.00	0.00	5400.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-10-29 17:35:24	2025-12-06 19:58:04
7	محمد نعيم	0592041000	0592041000	azad@0592041000	رام الله-الريحان	scrypt:32768:8:1$q2FIq2VTFQXeV3kq$9b7b93ee583892118b1185fdea0d5c064c435cfa1bfde480ca190dec96be633a78f527d6c675f75e5ac138ac0256ea	ذهبي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	-1000.00	0.00	0.00	0.00	6000.00	0.00	0.00	5000.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-10-29 18:35:15	2025-12-06 19:58:04
8	محمد سمير سبسطية	0569307241	0569307241	azad@0569307241	رام الله	scrypt:32768:8:1$B4tkUOxVFRiCTJrp$4a199da4e381fc8c8b09f5ebdf2d98e2845728b128024e8d5bd0c0e77a4a0834adea31da0ce0a3f279eb3c300a7cbc	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	-4000.00	7000.00	0.00	0.00	0.00	0.00	0.00	3000.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-10-29 20:31:40	2025-12-06 19:58:04
9	احمد ياسين طولكرم	0599675858	0599675858	azad@0599675858	طولكرم	scrypt:32768:8:1$jVKYIm8c2nOhxtxl$64ab96c7517a576e5449358cd9502565c709188798fb6d0938db21235e58d5e1dc5d17c809e159c2f09289cb0e25b7	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	3000.00	0.00	0.00	0.00	0.00	0.00	3000.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-04 12:12:16	2025-12-06 19:58:04
10	عارف القرناوي رهط	0537615791	0537615791	azad@0537615791	رهط-بير السبع	scrypt:32768:8:1$pwXbUbbLjBzu8uG4$f387233a0f2d5c9203277d493ad6896388d38949c36048fcfc8687d3d0250e94f480d34dc2fad43f2e2cca2a2f938f	ذهبي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	40000.00	0.00	0.00	0.00	0.00	0.00	40000.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-04 12:26:35	2025-12-06 19:58:04
11	سميح عموري طولكرم	00972599356532	00972599356532	azad@00972599356532	طولكرم	scrypt:32768:8:1$6NP0LRhhGT8QWwpi$488b3d3e63d1f9d5ff25bd94278fc36585d3db774c0ce6ae5e3fb6176b366e4cfb48d7b83967341346108ae035b1a9	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	5500.00	0.00	0.00	0.00	0.00	0.00	5500.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-04 14:50:07	2025-12-06 19:58:04
12	فريد ابو اياد الطوري	0542356007	0542356007	azad@0542356007	طمرة	scrypt:32768:8:1$ORjT3f5Jc5EUT6Gy$750afad749c7f8a7580f8a184996cfad8c21b243e588dc82987fbd3b0116d96a8a76f180617471496da1c239330885	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	15000.00	16300.00	0.00	0.00	0.00	0.00	0.00	0.00	1300.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-06 12:39:09	2025-12-06 19:58:04
13	يوسف ابو اسماعيل	0595950354	0595950354	azad@0595950354	بيت سوريك	scrypt:32768:8:1$e7cJ87aqxNqo25Ai$f992213b83ad282b1baca50a2a0649e848e38291f26f970b2c3fb52c760b80320b9a64c2f21f6846bb42ba433cb10e	ذهبي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	-5550.00	5550.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-07 14:23:38	2025-12-06 19:58:04
14	محمد فارس	0599842300	0599842300	azad@0599842300	رام الله	scrypt:32768:8:1$5Bb8MfV8cqEaf646$116ef60c425908629cd4e2503774d0f6111ea73d1bfdbe34362d86e5699fdf5e1be58f91e9264ea632e83a06f982ef	ذهبي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	-155560.00	-154610.00	95050.00	0.00	0.00	0.00	0.00	0.00	96000.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-07 15:00:46	2025-12-06 19:58:04
15	حمودة ابو عامر الجواريش	0543399985	0543399985	azad@0543399985	الرملة	scrypt:32768:8:1$eV2hJqeEvFRJvaFy$174504052d62216fd4e3a4b3c2755de24c0e3633ee3529beb3d4b0327e509660606f9e1fb61c59157fbb61fd7c99a5	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-07 16:53:43	2025-12-06 19:58:04
16	نصرالله سمير جهاد بني عودة	0592800646	0592800646	azad@0592800646	رافات-رام الله	scrypt:32768:8:1$6E48pax9NVIJP2Sj$d7ca5e6a81c37f7d5ad8cc8a03f3a781ff1764052acab1b23f75e54cf2e8ede9fd8c5541a38a1d2e38e146d8e402d0	بلاتيني	\N	t	t	f	\N	\N	\N	0.00	0.00	USD	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-09 09:58:50	2025-12-06 19:58:04
17	عدنان السلامين	0599432107	0599432107	azad@0599432107	دورا-الخليل	scrypt:32768:8:1$Fw6ngdGiuqvlmbws$b07cb69da45008c017ca433a11591a3a8b0885fd410223b9b70101246fd3c4a41755b911289c37225912ce5c423d46	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	1700.00	0.00	0.00	0.00	0.00	0.00	1700.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-09 20:44:42	2025-12-06 19:58:04
18	قنديل للاسفلت والتعهدات العامة	0568335555	0568335555	azad@0568335555	رافات-رام الله	scrypt:32768:8:1$ik5Cu9hQ14Ikpnuq$1ecd62299ceab2d1dd21bc873df85d51a405b700534909774d5a64e9e22e3f25efb44535098cc464ddd7ca1ce55f4c	ذهبي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	-750.00	650.00	0.00	0.00	7900.00	0.00	0.00	7800.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-09 20:51:26	2025-12-06 19:58:04
19	ابو ناصر ونش	0599756559	0599756559	azad@0599756559	رام الله	scrypt:32768:8:1$cMb9WyFd8O7R2Ga4$ea9116a22ca86fd7cc55e13a689e408bdeb37d4ead2292a83c4e2df69d35f2321affa0a6830ed6e986f19d0132e810	ذهبي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	-10100.00	25100.00	0.00	0.00	0.00	0.00	0.00	12500.00	0.00	0.00	0.00	0.00	0.00	12500.00	0.00	2025-11-09 21:35:54	2025-12-16 09:17:36
20	زهران ابو ربحي	0537318120	0537318120	azad@0537318120	طيرة المثلث	scrypt:32768:8:1$JI5kHSRgWFs9r3x5$2945f602c8a32be41ecc868a8635bd49bf6f573f02707413ae865a0dd7076030751b924d115011fe6288b32276ffa6	ذهبي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	-6500.00	5900.00	0.00	0.00	10000.00	0.00	0.00	9400.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-09 21:37:37	2025-12-06 19:58:04
21	فيصل الجمل	0592922224	0592922224	azad@0592922224	بيت سوريك	scrypt:32768:8:1$pMQ33BhEVRS9OIme$3232d722044e296aa4046bfa060900e416c52bb645f6398e20235a675e4b3b5e1400acb725004dfdfeb10e425dbc17	ذهبي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	2000.00	0.00	0.00	0.00	0.00	0.00	2000.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-10 12:30:46	2025-12-06 19:58:04
22	سامي كمال الطميزي	0598167539	0598167539	azad@0598167539	اذنا - الخليل	scrypt:32768:8:1$lL2J9RTVYhZAkEHP$2d5e3cec77b821b2e1c161d3182aaa16d35c58143a37d8eca3d19234597d0024bccab3fa7d63a688e16e740e9037d4	ذهبي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	-1000.00	-2000.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2000.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-10 22:32:42	2025-12-06 19:58:04
23	علي حنيحن	0595285333	0595285333	azad@0595285333	حلول-الخليل	scrypt:32768:8:1$iZmX6lfsirAxIv7J$9c0d57e5710851884138f4f20495b1e9c3747383b6d76b842045661b8edcac22d284b95647e1e34893562e278f2770	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	1300.00	0.00	0.00	0.00	0.00	0.00	1300.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-12 12:33:55	2025-12-06 19:58:04
24	طرمبة جرافة فولفو	0599711354	0599711354	azad@0599711354	بيت لقيا-رام الله	scrypt:32768:8:1$29i3AxF9Hgx7OdJ8$d449d5522b223c08d4b293d488223450417740b62cfe26c8e91d39282ad64e76a178edeb5512e9a5a05367fd5996a1	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	9000.00	0.00	0.00	0.00	0.00	0.00	9000.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-12 14:32:59	2025-12-06 19:58:04
25	فادي غيث	0598888657	0598888657	azad@0598888657	الخليل- المنقطة الجنوبية	scrypt:32768:8:1$SdsOtI0ZdsycdXpG$fc4bccf200aada06ecaba6823ed96a068a903af4458c08f627272b63b1555bdfbbf5111386a6582f2e2988d45045a1	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	-2000.00	12000.00	0.00	0.00	0.00	0.00	0.00	10000.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-12 17:32:11	2025-12-06 19:58:04
26	شركة اتكو الهندسية	0598890792	0598890792	azad@0598890792	رام الله - بيتونيا	scrypt:32768:8:1$olqOaLCluPi457ae$d2b23741b75111b1a21428542bc10ff7a3af52929849695b298e561ac21cce4925eb599b8126905480ebfcbe294462	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	20000.00	0.00	0.00	0.00	0.00	0.00	0.00	20000.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-12 19:48:13	2025-12-06 19:58:04
27	احمد ابو رزق جماعين	0592571618	0592571618	azad@0592571618	جماعين - نابلس	scrypt:32768:8:1$2QjHINeZksKuPPPA$ca20e505a63297184e80cf151543054a055296ca2ee3112c5d902e198eaee48be891fe03fb2d1639ac10fd82a01230	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	5500.00	0.00	0.00	0.00	0.00	0.00	7300.00	1800.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-13 10:32:14	2025-12-06 19:58:04
28	ادهم قطام	0568828204	0568828204	azad@0568828204	اريحا	scrypt:32768:8:1$czxtUfH9xPNnw6Jq$6f2e4c92b1ce8fd38820b8d2c3f63dd3a72e73b5c0008eff7102bb15ec7658a74a73f86711ce0c8321a0307d66b931	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	2700.00	0.00	0.00	0.00	0.00	0.00	2700.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-13 22:45:35	2025-12-06 19:58:04
29	اشرف يطاوي بيتونيا	202511161928441	202511161928441	azad@202511161928441	بيتونيا-دوار الفواكه	scrypt:32768:8:1$v8bLXcO4xbE5AxLp$d5f135c30d516ee21766ecb3e61bbeab05f42abb5b002c04386c8361f68ebf8019588d6e9a2e73cc5745163e51c99e	عادي	AUTO-SUPPLIER-4	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-16 19:28:44	2025-12-06 19:58:04
30	طوب شاهين	00000000000	00000000000	azad@00000000000	بيتونيا	scrypt:32768:8:1$4nwSE6fYzwB9nJQc$a1f346b87811f196f62e61d6c1e909aa6f66595491a8cc0148cb76f0144b233c6261a6dadfa7182a134a22d6d9e432	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	250.00	0.00	0.00	0.00	0.00	0.00	250.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-16 20:12:21	2025-12-06 19:58:04
31	ونشات رام الله	000000000000	000000000000	azad@000000000000	\N	scrypt:32768:8:1$SI6Qag9tjZ89jIpT$08a01a4a0d869c83039ffc4a0c52f5364b8a00dc563f986f55a7b3b429340d33729fc0e8da09d430e6fb1abf3ebaf6	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	230.00	0.00	0.00	0.00	0.00	0.00	230.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-16 20:13:00	2025-12-06 19:58:04
32	مجهول	0000000000	0000000000	azad@0000000000	\N	scrypt:32768:8:1$7ykrLDMaljWrCtDN$4f0923420bda935a3e3415158602e202857d4cec8ea4b74bfae929111c554d1b5459af61ca1b91ba61eb5faa9e4233	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	33820.00	0.00	0.00	0.00	0.00	0.00	33820.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-16 20:18:30	2025-12-06 19:58:04
33	اسماعيل ابو خلف	0549097681	0549097681	azad@0549097681	كفر عقب	scrypt:32768:8:1$qx7n6q3kOtZuTz4l$666aeacddd2dbc46351d5b688847f581a11c4cdc16ed84fee6c8d1662b6c0692594c6136f8d8532787822802d9c604	عادي	AUTO-SUPPLIER-5	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-16 20:47:40	2025-12-06 19:58:04
34	عمار النجار	0569099091	0569099091	azad@0569099091	رام الله بيتونيا	scrypt:32768:8:1$eEEugcyTQFdvkAoN$0517285768f5d0209089f124ee4cbc53fd0ae9887fb11c8f086e41b7dd20c537a0e339068585d4915fb663fac2c488	عادي	AUTO-PARTNER-1	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	-4100.00	4100.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-24 01:17:37	2025-12-06 19:58:04
35	ابراهيم قدح	0502269197	0502269197	azad@0502269197	كفر مندا	scrypt:32768:8:1$Lf9qRkLGqPDtA55A$1082e96d143f40d3681e74dabcaea42c67f9d7fb8fea7fc1b82d4a337572afe29d7e613dd1d7c0addc5a1d1700ed91	عادي	AUTO-SUPPLIER-1	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-24 01:17:37	2025-12-06 19:58:04
36	مراد المحسيري	0522454302	0522454302	azad@0522454302	الخضر-بيت لحم	scrypt:32768:8:1$4EDszpq2qU0dpnjx$bb15e184029a1092d3052d0183b85b91829b803cce1ecf6af78472ab97630f45d4a30247457557c23d38419a426782	عادي	AUTO-SUPPLIER-2	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	-4100.00	4100.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-24 01:17:37	2025-12-06 19:58:04
37	سامح الباشا	0503004498	0503004498	azad@0503004498	\N	scrypt:32768:8:1$GKBElKGXswOOPDb4$5a87f624544ae4f85e133cd86ebb1072e4bc2970c4e1676fc17e1500a62c031171fd205005dc6b21a21d3af8c6f87f	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	-10000.00	10000.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-25 10:45:11	2025-12-06 19:58:04
38	موسى الخيري	0505351728	0505351728	azad@0505351728	رام الله-كفرعقب	scrypt:32768:8:1$4gBxSgei2B0pFDtz$e846b4be100a8aecefb4fadc9b758e5d096078119c17628dce19cb5ff7b6b025e1aecb1154b6f419c406898164cdc0	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	5200.00	0.00	0.00	0.00	0.00	0.00	5200.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-25 13:07:50	2025-12-06 19:58:04
39	محمد شعيب	0597418414	0597418414	azad@0597418414	رام الله-ام الشرايط	scrypt:32768:8:1$LZZqKVKHeThC1Xli$44244f02e6a78cd8a9c423e0871b83e291632909a9d5f05d55100a6315909823ebdc3cb71c5a799d1a4f562603133b	عادي	\N	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	-3075.00	3075.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-25 13:26:57	2025-12-06 19:58:04
40	سيف بلشة	202511281438475	202511281438475	azad@202511281438475	\N	scrypt:32768:8:1$hyLnnPTqZlRkOhDY$2503f95bf462d873be6b441028c7d0113560230ed359cd45caddcac0876021c180299f3e00c5e7c76d35dcfb55db4a	عادي	AUTO-SUPPLIER-6	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-28 14:38:47	2025-12-06 19:58:04
41	بهاء حسونة	0597133330	0597133330	azad@0597133330	رام الله-بيتونيا	scrypt:32768:8:1$uGlwWODnpWtprf3T$38c08c33ba0a06d21e3e656583bd0bc399042885b44c505f81d2f8f70142f7f670fc134536687e5060666dcad8a15a	عادي	AUTO-SUPPLIER-7	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-28 15:02:46	2025-12-06 19:58:04
42	ايلي مراد قطع	0522726056	0522726056	azad@0522726056	\N	scrypt:32768:8:1$wqqrgp7UBBJE8o4Q$57b01d73c61a9cda2801034f6c400ec20cd931624eb313256957b77bb9a249a5bb34182818318506a90c5c18fb61d4	عادي	AUTO-SUPPLIER-8	t	t	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-11-28 15:05:15	2025-12-06 19:58:04
43	حسن شهوان	0599220101	0599220101	\N	مزايا مول	\N	عادي	AUTO-SUPPLIER-9	t	f	f	\N	\N	\N	0.00	0.00	ILS	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	2025-12-14 14:10:32	2025-12-14 14:10:32
\.


--
-- Data for Name: deletion_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.deletion_logs (id, deletion_type, entity_id, entity_name, status, created_at, updated_at, deleted_by, deletion_reason, confirmation_code, deleted_data, related_entities, stock_reversals, accounting_reversals, balance_reversals, restored_at, restored_by, restoration_notes) FROM stdin;
1	PAYMENT	1	الدفعة #PMT20251023-0001	COMPLETED	2025-10-24 17:23:28.241366	2025-10-24 17:23:28.252929	1	O	DEL_72CAA9FA	"{\\"id\\": 1, \\"payment_number\\": \\"PMT20251023-0001\\", \\"entity_type\\": \\"SALE\\", \\"customer_id\\": null, \\"supplier_id\\": null, \\"partner_id\\": null, \\"expense_id\\": null, \\"sale_id\\": 1, \\"total_amount\\": 80000.0, \\"payment_date\\": \\"2025-10-23T20:50:00\\", \\"method\\": \\"cash\\", \\"status\\": \\"COMPLETED\\", \\"direction\\": \\"IN\\"}"	"{}"	"[]"	"[]"	"[]"	\N	\N	\N
2	CUSTOMER	3	بلال نادر	COMPLETED	2025-10-25 20:03:13.74511	2025-10-25 20:03:13.871155	1	ydv	DEL_90746C88	"{\\"id\\": 3, \\"name\\": \\"\\\\u0628\\\\u0644\\\\u0627\\\\u0644 \\\\u0646\\\\u0627\\\\u062f\\\\u0631\\", \\"phone\\": \\"0595138813\\", \\"email\\": \\"\\", \\"address\\": null, \\"created_at\\": \\"2025-10-24T20:03:22\\", \\"updated_at\\": \\"2025-10-24T20:03:22\\"}"	"{\\"sales\\": [], \\"payments\\": []}"	"[]"	"[]"	"[]"	\N	\N	\N
3	CUSTOMER	4	فحص تجريبي 1	COMPLETED	2025-10-26 16:55:14.095414	2025-10-26 16:55:14.118944	1	اها	DEL_B8781B74	"{\\"id\\": 4, \\"name\\": \\"\\\\u0641\\\\u062d\\\\u0635 \\\\u062a\\\\u062c\\\\u0631\\\\u064a\\\\u0628\\\\u064a 1\\", \\"phone\\": \\"0562150193\\", \\"email\\": null, \\"address\\": null, \\"created_at\\": \\"2025-10-26T13:01:44\\", \\"updated_at\\": \\"2025-10-26T13:01:44\\"}"	"{\\"sales\\": [], \\"payments\\": []}"	"[]"	"[]"	"[]"	\N	\N	\N
4	SALE	5	بيع #SAL20251029-0001	COMPLETED	2025-10-29 16:59:44.625672	2025-10-29 16:59:44.656133	1	حر	DEL_4C036A83	"{\\"id\\": 5, \\"sale_number\\": \\"SAL20251029-0001\\", \\"customer_id\\": 5, \\"total_amount\\": 2800.0, \\"sale_date\\": \\"2025-10-29T18:54:00\\", \\"status\\": \\"CONFIRMED\\", \\"currency\\": \\"ILS\\"}"	"[]"	"[{\\"product_id\\": 23, \\"warehouse_id\\": 2, \\"quantity_restored\\": 1.0, \\"old_quantity\\": 2.0, \\"new_quantity\\": 3.0}]"	"[{\\"batch_id\\": 45, \\"source_type\\": \\"SALE\\", \\"source_id\\": 5, \\"description\\": \\"GLBatch \\\\u0644\\\\u0644\\\\u0628\\\\u064a\\\\u0639\\"}, {\\"batch_id\\": 44, \\"source_type\\": \\"PAYMENT\\", \\"source_id\\": 15, \\"description\\": \\"GLBatch \\\\u0644\\\\u0644\\\\u062f\\\\u0641\\\\u0639\\\\u0629 #PMT20251029-0002\\"}]"	"[]"	\N	\N	\N
5	SALE	5	بيع #SAL20251029-0001	COMPLETED	2025-10-29 17:40:53.730091	2025-10-29 17:40:53.779994	1	ا	DEL_2DFFCE8F	"{\\"id\\": 5, \\"sale_number\\": \\"SAL20251029-0001\\", \\"customer_id\\": 6, \\"total_amount\\": 2700.0, \\"sale_date\\": \\"2025-10-29T19:36:00\\", \\"status\\": \\"CONFIRMED\\", \\"currency\\": \\"ILS\\"}"	"[]"	"[{\\"product_id\\": 24, \\"warehouse_id\\": 3, \\"quantity_restored\\": 3.0, \\"old_quantity\\": 37.0, \\"new_quantity\\": 40.0}]"	"[{\\"batch_id\\": 43, \\"source_type\\": \\"SALE\\", \\"source_id\\": 5, \\"description\\": \\"GLBatch \\\\u0644\\\\u0644\\\\u0628\\\\u064a\\\\u0639\\"}]"	"[]"	\N	\N	\N
6	SUPPLIER	1	مورد افتراضي	COMPLETED	2025-11-04 21:11:40.372572	2025-11-04 21:11:40.467707	1	ن	DEL_CADE268D	"{}"	"{}"	"[]"	"[]"	"[]"	\N	\N	\N
7	SUPPLIER	2	مورد تجريبي	COMPLETED	2025-11-04 21:12:13.931233	2025-11-04 21:12:13.952961	1	خن	DEL_92E68C0A	"{}"	"{}"	"[]"	"[]"	"[]"	\N	\N	\N
8	PARTNER	2	شريك تجريبي	COMPLETED	2025-11-04 21:14:35.850937	2025-11-04 21:14:36.104734	1	hih	DEL_17B25E05	"{}"	"{}"	"[{\\"product_id\\": 19, \\"warehouse_id\\": 2, \\"quantity_restored\\": 1.0, \\"old_quantity\\": 9.0, \\"new_quantity\\": 10.0}, {\\"product_id\\": 17, \\"warehouse_id\\": 2, \\"quantity_restored\\": 1.0, \\"old_quantity\\": 2.0, \\"new_quantity\\": 3.0}, {\\"product_id\\": 14, \\"warehouse_id\\": 2, \\"quantity_restored\\": 1.0, \\"old_quantity\\": 7.0, \\"new_quantity\\": 8.0}, {\\"product_id\\": 12, \\"warehouse_id\\": 2, \\"quantity_restored\\": 1.0, \\"old_quantity\\": 19.0, \\"new_quantity\\": 20.0}, {\\"product_id\\": 18, \\"warehouse_id\\": 2, \\"quantity_restored\\": 1.0, \\"old_quantity\\": 0.0, \\"new_quantity\\": 1.0}, {\\"product_id\\": 15, \\"warehouse_id\\": 2, \\"quantity_restored\\": 1.0, \\"old_quantity\\": 9.0, \\"new_quantity\\": 10.0}, {\\"product_id\\": 16, \\"warehouse_id\\": 2, \\"quantity_restored\\": 3.0, \\"old_quantity\\": 7.0, \\"new_quantity\\": 10.0}, {\\"product_id\\": 11, \\"warehouse_id\\": 2, \\"quantity_restored\\": 3.0, \\"old_quantity\\": 22.0, \\"new_quantity\\": 25.0}, {\\"product_id\\": 13, \\"warehouse_id\\": 2, \\"quantity_restored\\": 6.0, \\"old_quantity\\": 4.0, \\"new_quantity\\": 10.0}, {\\"product_id\\": 21, \\"warehouse_id\\": 2, \\"quantity_restored\\": 1.0, \\"old_quantity\\": 9.0, \\"new_quantity\\": 10.0}]"	"[]"	"[]"	\N	\N	\N
9	PARTNER	1	شريك افتراضي	COMPLETED	2025-11-04 21:15:18.851929	2025-11-04 21:15:18.992465	1	ok	DEL_64DE8FA2	"{}"	"{}"	"[{\\"product_id\\": 9, \\"warehouse_id\\": 1, \\"quantity_restored\\": 1.0, \\"old_quantity\\": 0.0, \\"new_quantity\\": 1.0}, {\\"product_id\\": 4, \\"warehouse_id\\": 1, \\"quantity_restored\\": 4.0, \\"old_quantity\\": 0.0, \\"new_quantity\\": 4.0}, {\\"product_id\\": 3, \\"warehouse_id\\": 1, \\"quantity_restored\\": 7.0, \\"old_quantity\\": 0.0, \\"new_quantity\\": 7.0}, {\\"product_id\\": 7, \\"warehouse_id\\": 1, \\"quantity_restored\\": 1.0, \\"old_quantity\\": 0.0, \\"new_quantity\\": 1.0}, {\\"product_id\\": 8, \\"warehouse_id\\": 1, \\"quantity_restored\\": 1.0, \\"old_quantity\\": 0.0, \\"new_quantity\\": 1.0}, {\\"product_id\\": 10, \\"warehouse_id\\": 1, \\"quantity_restored\\": 1.0, \\"old_quantity\\": 0.0, \\"new_quantity\\": 1.0}, {\\"product_id\\": 2, \\"warehouse_id\\": 1, \\"quantity_restored\\": 2.0, \\"old_quantity\\": 0.0, \\"new_quantity\\": 2.0}, {\\"product_id\\": 1, \\"warehouse_id\\": 1, \\"quantity_restored\\": 4.0, \\"old_quantity\\": 0.0, \\"new_quantity\\": 4.0}, {\\"product_id\\": 6, \\"warehouse_id\\": 1, \\"quantity_restored\\": 1.0, \\"old_quantity\\": 0.0, \\"new_quantity\\": 1.0}, {\\"product_id\\": 5, \\"warehouse_id\\": 1, \\"quantity_restored\\": 10.0, \\"old_quantity\\": 0.0, \\"new_quantity\\": 10.0}]"	"[]"	"[]"	\N	\N	\N
10	SUPPLIER	3	عصفور عصفور	COMPLETED	2025-11-05 07:20:35.43367	2025-11-05 07:20:35.52322	1	كرر	DEL_E955FCBC	"{}"	"{}"	"[]"	"[]"	"[]"	\N	\N	\N
11	SUPPLIER	2	مورد تجريبي	COMPLETED	2025-11-05 07:20:49.625338	2025-11-05 07:20:49.648239	1	ككك	DEL_2EEAAFA7	"{}"	"{}"	"[]"	"[]"	"[]"	\N	\N	\N
12	SUPPLIER	1	مورد اختبار نهائي	COMPLETED	2025-11-05 07:50:11.891178	2025-11-05 07:50:11.953315	1	اختبار الحل الكامل	DEL_31097140	"{}"	"{}"	"[]"	"[]"	"[]"	\N	\N	\N
13	SUPPLIER	1	مورد اختبار نهائي	COMPLETED	2025-11-05 07:52:43.651654	2025-11-05 07:52:43.706352	1	اختبار الحل الكامل	DEL_913D5E8B	"{}"	"{}"	"[]"	"[]"	"[]"	\N	\N	\N
14	SUPPLIER	1	مورد نهائي	COMPLETED	2025-11-05 07:54:07.649457	2025-11-05 07:54:07.712005	1	اختبار	DEL_AA88C104	"{}"	"{}"	"[]"	"[]"	"[]"	\N	\N	\N
15	PARTNER	1	شريك نهائي	COMPLETED	2025-11-05 07:54:07.743157	2025-11-05 07:54:07.788696	1	اختبار	DEL_77DDB1E5	"{}"	"{}"	"[]"	"[]"	"[]"	\N	\N	\N
16	PAYMENT	37	الدفعة #PMT20251109-0002	COMPLETED	2025-11-09 20:33:06.357563	2025-11-09 20:33:06.418464	1	hhh	DEL_E33D3209	"{\\"id\\": 37, \\"payment_number\\": \\"PMT20251109-0002\\", \\"entity_type\\": \\"CUSTOMER\\", \\"customer_id\\": 16, \\"supplier_id\\": null, \\"partner_id\\": null, \\"expense_id\\": null, \\"sale_id\\": null, \\"total_amount\\": 20000.0, \\"payment_date\\": \\"2025-11-09T09:57:00\\", \\"method\\": \\"cash\\", \\"status\\": \\"COMPLETED\\", \\"direction\\": \\"OUT\\"}"	"{}"	"[]"	"[{\\"batch_id\\": 106, \\"source_type\\": \\"PAYMENT\\", \\"source_id\\": 37}]"	"[]"	\N	\N	\N
17	PAYMENT	36	الدفعة #PMT20251109-0001	COMPLETED	2025-11-09 20:33:29.303831	2025-11-09 20:33:29.318727	1	hgh	DEL_41F67B8A	"{\\"id\\": 36, \\"payment_number\\": \\"PMT20251109-0001\\", \\"entity_type\\": \\"CUSTOMER\\", \\"customer_id\\": 9, \\"supplier_id\\": null, \\"partner_id\\": null, \\"expense_id\\": null, \\"sale_id\\": null, \\"total_amount\\": 555.0, \\"payment_date\\": \\"2025-11-09T00:22:00\\", \\"method\\": \\"cash\\", \\"status\\": \\"COMPLETED\\", \\"direction\\": \\"OUT\\"}"	"{}"	"[]"	"[{\\"batch_id\\": 105, \\"source_type\\": \\"PAYMENT\\", \\"source_id\\": 36}]"	"[]"	\N	\N	\N
18	EXPENSE	24	النفقة #24	COMPLETED	2025-11-12 17:17:32.240968	2025-11-12 17:17:32.395366	1	لا ى	DEL_AFD3DF7F	"{\\"id\\": 24, \\"description\\": null, \\"amount\\": 2000.0, \\"date\\": \\"2025-11-10T00:00:00\\", \\"currency\\": \\"ILS\\", \\"type_id\\": 15, \\"payee_type\\": \\"EMPLOYEE\\", \\"payee_entity_id\\": 5, \\"payee_name\\": \\"\\\\u0627\\\\u064a\\\\u0627\\\\u062f \\\\u0646\\\\u0648\\\\u0641\\\\u0644\\", \\"beneficiary_name\\": null, \\"payment_method\\": \\"cash\\", \\"notes\\": \\"\\\\u0631\\\\u0627\\\\u062a\\\\u0628 \\\\u0634\\\\u0647\\\\u0631 \\\\u0646\\\\u0648\\\\u0641\\\\u0645\\\\u0628\\\\u0631 2025\\"}"	"{\\"payments\\": [{\\"id\\": 64, \\"total_amount\\": 2000.0, \\"payment_date\\": \\"2025-11-12T00:45:33\\", \\"method\\": \\"cash\\", \\"status\\": \\"COMPLETED\\"}]}"	"[]"	"[]"	"[]"	\N	\N	\N
19	PAYMENT	68	الدفعة #PMT20251112-0004	COMPLETED	2025-11-12 20:43:54.891705	2025-11-12 20:43:55.1935	1	تا	DEL_70969EBA	"{\\"id\\": 68, \\"payment_number\\": \\"PMT20251112-0004\\", \\"entity_type\\": \\"SUPPLIER\\", \\"customer_id\\": null, \\"supplier_id\\": 1, \\"partner_id\\": null, \\"expense_id\\": null, \\"sale_id\\": null, \\"total_amount\\": 1000.0, \\"payment_date\\": \\"2025-11-12T20:41:00\\", \\"method\\": \\"cash\\", \\"status\\": \\"COMPLETED\\", \\"direction\\": \\"IN\\"}"	"{}"	"[]"	"[{\\"batch_id\\": 138, \\"source_type\\": \\"PAYMENT\\", \\"source_id\\": 68}]"	"[]"	\N	\N	\N
20	PAYMENT	71	الدفعة #PMT20251113-0002	COMPLETED	2025-11-13 12:09:36.544701	2025-11-13 12:09:36.594633	1	لا	DEL_2958091D	"{\\"id\\": 71, \\"payment_number\\": \\"PMT20251113-0002\\", \\"entity_type\\": \\"CUSTOMER\\", \\"customer_id\\": 27, \\"supplier_id\\": null, \\"partner_id\\": null, \\"expense_id\\": null, \\"sale_id\\": null, \\"total_amount\\": 1000.0, \\"payment_date\\": \\"2025-11-13T10:43:00\\", \\"method\\": \\"cash\\", \\"status\\": \\"REFUNDED\\", \\"direction\\": \\"IN\\"}"	"{}"	"[]"	"[{\\"batch_id\\": 162, \\"source_type\\": \\"PAYMENT\\", \\"source_id\\": 71}]"	"[]"	\N	\N	\N
21	PAYMENT	19	الدفعة #PMT20251031-0001	COMPLETED	2025-11-13 16:37:14.266282	2025-11-13 16:37:14.365208	1	احذف	DEL_F13D6934	"{\\"id\\": 19, \\"payment_number\\": \\"PMT20251031-0001\\", \\"entity_type\\": \\"CUSTOMER\\", \\"customer_id\\": 7, \\"supplier_id\\": null, \\"partner_id\\": null, \\"expense_id\\": null, \\"sale_id\\": null, \\"total_amount\\": 5000.0, \\"payment_date\\": \\"2025-10-31T23:03:00\\", \\"method\\": \\"cash\\", \\"status\\": \\"COMPLETED\\", \\"direction\\": \\"IN\\"}"	"{}"	"[]"	"[{\\"batch_id\\": 54, \\"source_type\\": \\"PAYMENT\\", \\"source_id\\": 19}]"	"[]"	\N	\N	\N
22	PAYMENT	75	الدفعة #PMT20251113-0006	COMPLETED	2025-11-13 16:37:42.510678	2025-11-13 16:37:42.531734	1	حذف	DEL_4F33745E	"{\\"id\\": 75, \\"payment_number\\": \\"PMT20251113-0006\\", \\"entity_type\\": \\"CUSTOMER\\", \\"customer_id\\": 7, \\"supplier_id\\": null, \\"partner_id\\": null, \\"expense_id\\": null, \\"sale_id\\": null, \\"total_amount\\": 6000.0, \\"payment_date\\": \\"2025-11-13T15:56:00\\", \\"method\\": \\"cash\\", \\"status\\": \\"COMPLETED\\", \\"direction\\": \\"IN\\"}"	"{}"	"[]"	"[{\\"batch_id\\": 167, \\"source_type\\": \\"PAYMENT\\", \\"source_id\\": 75}]"	"[]"	\N	\N	\N
23	PAYMENT	80	الدفعة #PMT20251115-0002	COMPLETED	2025-11-16 20:35:00.464307	2025-11-16 20:35:00.525272	1	ىىة	DEL_2962CDAC	"{\\"id\\": 80, \\"payment_number\\": \\"PMT20251115-0002\\", \\"entity_type\\": \\"SUPPLIER\\", \\"customer_id\\": null, \\"supplier_id\\": 3, \\"partner_id\\": null, \\"expense_id\\": null, \\"sale_id\\": null, \\"total_amount\\": 12000.0, \\"payment_date\\": \\"2025-11-15T12:14:00\\", \\"method\\": \\"cash\\", \\"status\\": \\"COMPLETED\\", \\"direction\\": \\"OUT\\"}"	"{}"	"[]"	"[{\\"batch_id\\": 177, \\"source_type\\": \\"PAYMENT\\", \\"source_id\\": 80}]"	"[]"	\N	\N	\N
24	PAYMENT	79	الدفعة #PMT20251115-0001	COMPLETED	2025-11-16 20:39:25.334479	2025-11-16 20:39:25.357674	1	نمممك	DEL_D752D1A6	"{\\"id\\": 79, \\"payment_number\\": \\"PMT20251115-0001\\", \\"entity_type\\": \\"SUPPLIER\\", \\"customer_id\\": null, \\"supplier_id\\": 3, \\"partner_id\\": null, \\"expense_id\\": null, \\"sale_id\\": null, \\"total_amount\\": 20000.0, \\"payment_date\\": \\"2025-11-15T12:12:00\\", \\"method\\": \\"cash\\", \\"status\\": \\"COMPLETED\\", \\"direction\\": \\"OUT\\"}"	"{}"	"[]"	"[{\\"batch_id\\": 176, \\"source_type\\": \\"PAYMENT\\", \\"source_id\\": 79}]"	"[]"	\N	\N	\N
25	SUPPLIER	3	اسماعيل ابو خلف	COMPLETED	2025-11-16 20:45:07.054344	2025-11-16 20:45:07.113769	1	لارلا	DEL_62D8959E	"{}"	"{}"	"[]"	"[]"	"[]"	\N	\N	\N
26	PAYMENT	118	الدفعة #PMT20251116-0036	COMPLETED	2025-11-16 21:13:46.192227	2025-11-16 21:13:46.214154	1	ؤلالؤلالا	DEL_8B44AA67	"{\\"id\\": 118, \\"payment_number\\": \\"PMT20251116-0036\\", \\"entity_type\\": \\"SUPPLIER\\", \\"customer_id\\": null, \\"supplier_id\\": 5, \\"partner_id\\": null, \\"expense_id\\": null, \\"sale_id\\": null, \\"total_amount\\": 32000.0, \\"payment_date\\": \\"2025-11-16T21:12:00\\", \\"method\\": \\"cash\\", \\"status\\": \\"COMPLETED\\", \\"direction\\": \\"OUT\\"}"	"{}"	"[]"	"[{\\"batch_id\\": 225, \\"source_type\\": \\"PAYMENT\\", \\"source_id\\": 118}]"	"[]"	\N	\N	\N
\.


--
-- Data for Name: employee_advance_installments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employee_advance_installments (id, employee_id, advance_expense_id, installment_number, total_installments, amount, currency, due_date, paid, paid_date, paid_in_salary_expense_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: employee_advances; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employee_advances (id, employee_id, amount, currency, advance_date, reason, total_installments, installments_paid, fully_paid, notes, expense_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: employee_deductions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employee_deductions (id, employee_id, deduction_type, amount, currency, start_date, end_date, is_active, notes, expense_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: employee_skills; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employee_skills (id, employee_id, skill_id, proficiency_level, years_experience, certification_number, certification_authority, certification_date, expiry_date, verified_by, verification_date, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: employees; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employees (id, name, "position", salary, phone, email, hire_date, bank_name, account_number, notes, currency, branch_id, site_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: engineering_skills; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.engineering_skills (id, code, name, name_ar, category, description, is_certification_required, certification_validity_months, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: engineering_tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.engineering_tasks (id, task_number, title, description, task_type, priority, status, assigned_team_id, assigned_to_id, required_skills, estimated_hours, actual_hours, estimated_cost, actual_cost, scheduled_start, scheduled_end, actual_start, actual_end, customer_id, location, equipment_needed, tools_needed, materials_needed, safety_requirements, quality_standards, completion_notes, completion_photos, customer_satisfaction_rating, customer_feedback, cost_center_id, project_id, service_request_id, parent_task_id, gl_batch_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: engineering_team_members; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.engineering_team_members (id, team_id, employee_id, role, join_date, leave_date, hourly_rate, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: engineering_teams; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.engineering_teams (id, code, name, team_leader_id, specialty, cost_center_id, branch_id, max_concurrent_tasks, is_active, description, equipment_inventory, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: engineering_timesheets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.engineering_timesheets (id, employee_id, task_id, work_date, start_time, end_time, break_duration_minutes, actual_work_hours, billable_hours, hourly_rate, total_cost, productivity_rating, work_description, issues_encountered, materials_used, location, status, approved_by, approval_date, approval_notes, cost_center_id, gl_batch_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: equipment_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipment_types (id, name, model_number, chassis_number, notes, category, created_at, updated_at) FROM stdin;
1	case sr210	2018	\N	\N	\N	2025-10-29 20:45:55	2025-10-29 20:45:55
2	BOMAG BF700	2020	\N	\N	FINISHER	2025-11-09 20:53:13	2025-11-09 20:53:13
3	هام120	\N	\N	\N	\N	2025-11-09 21:07:38	2025-11-09 21:07:38
4	volvo finisher	\N	\N	\N	\N	2025-11-25 10:51:27	2025-11-25 10:51:27
\.


--
-- Data for Name: exchange_rates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exchange_rates (id, base_code, quote_code, rate, valid_from, source, is_active) FROM stdin;
1	JOD	ILS	4.59000000	2025-10-31 20:26:15.416981	External API	t
2	USD	ILS	3.25000000	2025-10-31 22:19:39.637832	External API	t
3	USD	ILS	3.26000000	2025-11-04 20:24:37.745486	External API	t
4	USD	ILS	3.27000000	2025-11-05 15:11:41.091706	External API	t
5	USD	ILS	3.26000000	2025-11-09 09:59:30.403172	External API	t
6	USD	ILS	3.24000000	2025-01-01 00:00:00	External API	t
\.


--
-- Data for Name: exchange_transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exchange_transactions (id, product_id, warehouse_id, supplier_id, partner_id, quantity, direction, unit_cost, is_priced, notes, created_at, updated_at) FROM stdin;
1	68	9	2	\N	1	IN	60000.00	t	SupplierID:2(مراد المحسيري) | paid:60000.00 | price:60000.00	2025-11-15 13:06:16	2025-11-15 13:06:16
2	69	9	4	\N	1	IN	4500.00	t	SupplierID:4(اشرف يطاوي بيتونيا) | paid:4500.00 | price:4500.00	2025-11-16 19:32:03	2025-11-16 19:32:03
3	90	9	6	\N	1	IN	6500.00	t	SupplierID:6(سيف بلشة) | paid:6500.00 | price:6500.00	2025-11-28 14:42:11	2025-11-28 14:42:11
\.


--
-- Data for Name: expense_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expense_types (id, name, description, is_active, code, fields_meta, created_at, updated_at) FROM stdin;
1	رواتب (معطل)	رواتب الموظفين	f	SALARY_OLD_DISABLED	"{\\"ledger\\": {\\"expense_account\\": \\"6100_SALARIES\\", \\"counterparty_account\\": \\"2150_PAYROLL_CLEARING\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-29 16:10:44	2025-11-16 01:02:03
2	إيجار	مصروف إيجار	t	RENT	"{\\"required\\": [\\"warehouse_id\\"], \\"optional\\": [\\"period\\", \\"beneficiary_name\\", \\"description\\"], \\"gl_account_code\\": \\"6200_RENT\\", \\"ledger\\": {\\"expense_account\\": \\"6200_RENT\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-29 16:10:44	2025-11-16 01:09:37
3	مرافق	مصروف مرافق	t	UTILITIES	"{\\"required\\": [\\"utility_account_id\\"], \\"optional\\": [\\"period\\", \\"description\\"], \\"gl_account_code\\": \\"6300_UTILITIES\\", \\"ledger\\": {\\"expense_account\\": \\"6300_UTILITIES\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-29 16:10:44	2025-11-16 01:09:37
4	صيانة	مصروف صيانة	t	MAINTENANCE	"{\\"required\\": [], \\"optional\\": [\\"warehouse_id\\", \\"beneficiary_name\\", \\"description\\"], \\"gl_account_code\\": \\"6400_MAINTENANCE\\", \\"ledger\\": {\\"expense_account\\": \\"6400_MAINTENANCE\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-29 16:10:44	2025-11-16 01:09:37
5	مواصلات	مصاريف النقل والتوصيل	f	TRANSPORT	"{\\"gl_account_code\\": \\"6320_TRANSPORT\\", \\"ledger\\": {\\"expense_account\\": \\"6975_TRANSPORT\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-29 16:10:44	2025-11-16 01:09:37
6	اتصالات	هاتف وإنترنت	t	TELECOM	"{\\"gl_account_code\\": \\"6310_TELECOM\\", \\"ledger\\": {\\"expense_account\\": \\"6310_TELECOM\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-29 16:10:44	2025-11-16 01:09:37
7	تسويق وإعلان	الإعلانات والدعاية	f	MARKETING_OLD	"{\\"gl_account_code\\": \\"6920_MARKETING\\", \\"required\\": [\\"period\\", \\"telecom_phone_number\\", \\"telecom_service_type\\"], \\"optional\\": [\\"utility_account_id\\", \\"beneficiary_name\\"], \\"ledger\\": {\\"expense_account\\": \\"6920_MARKETING\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-29 16:10:44	2025-11-16 01:09:37
8	مستلزمات مكتبية	قرطاسية ومستلزمات	f	OFFICE_OLD	"{\\"gl_account_code\\": \\"6600_OFFICE\\", \\"ledger\\": {\\"expense_account\\": \\"6600_OFFICE\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-29 16:10:44	2025-11-16 01:09:37
9	ضرائب ورسوم	ضرائب ورسوم حكومية	f	TAX_FEES	"{\\"gl_account_code\\": \\"6810_TAX_FEES\\", \\"ledger\\": {\\"expense_account\\": \\"6805_TAXES\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-29 16:10:44	2025-11-16 01:09:37
10	تأمينات	تأمينات طبية وتجارية	f	INS_OLD	"{\\"gl_account_code\\": \\"6700_INSURANCE\\", \\"ledger\\": {\\"expense_account\\": \\"6700_INSURANCE\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-29 16:10:44	2025-11-16 01:09:37
11	استشارات	استشارات قانونية ومحاسبية	f	CONSULTING	"{\\"gl_account_code\\": \\"6750_CONSULTING\\", \\"ledger\\": {\\"expense_account\\": \\"6405_CONSULTING_FEES\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-29 16:10:44	2025-11-16 01:09:37
12	ضيافة	مصروف ضيافة	t	HOSPITALITY	"{\\"required\\": [], \\"optional\\": [\\"beneficiary_name\\", \\"description\\"], \\"gl_account_code\\": \\"6950_HOSPITALITY\\", \\"ledger\\": {\\"expense_account\\": \\"6950_HOSPITALITY\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-29 16:10:44	2025-11-16 01:09:37
13	أخرى	مصروفات أخرى	t	OTHER	"{\\"required\\": [], \\"optional\\": [\\"beneficiary_name\\", \\"description\\"], \\"gl_account_code\\": \\"5000_EXPENSES\\", \\"ledger\\": {\\"expense_account\\": \\"5000_EXPENSES\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-29 16:10:44	2025-11-16 01:09:37
14	مصاريف بيت	\N	f	HOME_OLD	"{\\"gl_account_code\\": \\"6960_HOME_EXPENSE\\", \\"ledger\\": {\\"expense_account\\": \\"6960_HOME_EXPENSE\\", \\"counterparty_account\\": \\"3100_OWNER_CURRENT\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-29 18:38:19	2025-11-16 01:02:03
15	رواتب	مصروف رواتب وأجور	t	SALARY	"{\\"required\\": [\\"employee_id\\", \\"period\\"], \\"optional\\": [\\"description\\"], \\"gl_account_code\\": \\"6100_SALARIES\\", \\"ledger\\": {\\"expense_account\\": \\"6100_SALARIES\\", \\"counterparty_account\\": \\"2150_PAYROLL_CLEARING\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 17:56:24	2025-11-16 01:02:03
16	سلفة موظف	سلف الموظفين	t	EMPLOYEE_ADVANCE	"{\\"required\\": [\\"employee_id\\"], \\"optional\\": [\\"period\\", \\"description\\"], \\"gl_account_code\\": \\"6110_EMPLOYEE_ADVANCES\\", \\"ledger\\": {\\"expense_account\\": \\"6110_EMPLOYEE_ADVANCES\\", \\"counterparty_account\\": \\"2150_EMPLOYEE_ADVANCES\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 17:56:24	2025-11-16 01:02:03
17	وقود	مصروف وقود	t	FUEL	"{\\"required\\": [], \\"optional\\": [\\"beneficiary_name\\", \\"description\\"], \\"gl_account_code\\": \\"6500_FUEL\\", \\"ledger\\": {\\"expense_account\\": \\"6500_FUEL\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
18	لوازم مكتبية	مصروف لوازم مكتبية	t	OFFICE	"{\\"required\\": [], \\"optional\\": [\\"beneficiary_name\\", \\"description\\"], \\"gl_account_code\\": \\"6600_OFFICE\\", \\"ledger\\": {\\"expense_account\\": \\"6600_OFFICE\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
19	تأمين	مصروف تأمين	t	INSURANCE	"{\\"required\\": [], \\"optional\\": [\\"beneficiary_name\\", \\"description\\"], \\"gl_account_code\\": \\"6700_INSURANCE\\", \\"ledger\\": {\\"expense_account\\": \\"6700_INSURANCE\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
20	رسوم حكومية	مصروف رسوم وضرائب	t	GOV_FEES	"{\\"required\\": [], \\"optional\\": [\\"beneficiary_name\\", \\"description\\"], \\"gl_account_code\\": \\"6800_GOV_FEES\\", \\"ledger\\": {\\"expense_account\\": \\"6800_GOV_FEES\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
21	سفر ومهمات	مصروف سفر	t	TRAVEL	"{\\"required\\": [], \\"optional\\": [\\"beneficiary_name\\", \\"description\\"], \\"gl_account_code\\": \\"6900_TRAVEL\\", \\"ledger\\": {\\"expense_account\\": \\"6900_TRAVEL\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
42	كهرباء	فواتير كهرباء	t	\N	\N	2025-12-18 16:35:41.770519	2025-12-18 16:35:41.770519
43	مياه	فواتير مياه	t	\N	\N	2025-12-18 16:35:41.770519	2025-12-18 16:35:41.770519
22	تدريب	مصروف تدريب	t	TRAINING	"{\\"required\\": [], \\"optional\\": [\\"beneficiary_name\\", \\"description\\"], \\"gl_account_code\\": \\"6910_TRAINING\\", \\"ledger\\": {\\"expense_account\\": \\"6910_TRAINING\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
23	تسويق وإعلانات	مصروف تسويق	t	MARKETING	"{\\"required\\": [\\"period\\", \\"telecom_phone_number\\", \\"telecom_service_type\\"], \\"optional\\": [\\"utility_account_id\\", \\"beneficiary_name\\"], \\"gl_account_code\\": \\"6920_MARKETING\\", \\"ledger\\": {\\"expense_account\\": \\"6920_MARKETING\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
24	اشتراكات تقنية	مصروف برمجيات	t	SOFTWARE	"{\\"required\\": [\\"period\\"], \\"optional\\": [\\"beneficiary_name\\", \\"description\\"], \\"gl_account_code\\": \\"6930_SOFTWARE\\", \\"ledger\\": {\\"expense_account\\": \\"6930_SOFTWARE\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
25	رسوم بنكية	مصروف رسوم بنكية	t	BANK_FEES	"{\\"required\\": [\\"beneficiary_name\\"], \\"optional\\": [\\"description\\"], \\"gl_account_code\\": \\"6940_BANK_FEES\\", \\"ledger\\": {\\"expense_account\\": \\"6940_BANK_FEES\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
26	مصاريف بيتية	مصروفات بيتية	t	HOME_EXPENSE	"{\\"required\\": [], \\"optional\\": [\\"beneficiary_name\\", \\"description\\"], \\"gl_account_code\\": \\"6960_HOME_EXPENSE\\", \\"ledger\\": {\\"expense_account\\": \\"6960_HOME_EXPENSE\\", \\"counterparty_account\\": \\"3100_OWNER_CURRENT\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:02:03
27	مصاريف المالكين	مصروفات المالكين	t	OWNERS_EXPENSE	"{\\"required\\": [], \\"optional\\": [\\"beneficiary_name\\", \\"description\\"], \\"gl_account_code\\": \\"6970_OWNERS_EXPENSE\\", \\"ledger\\": {\\"expense_account\\": \\"6970_OWNER_CURRENT\\", \\"counterparty_account\\": \\"3100_OWNER_CURRENT\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:02:03
28	ترفيه	مصروف ترفيهي	t	ENTERTAINMENT	"{\\"required\\": [], \\"optional\\": [\\"beneficiary_name\\", \\"description\\"], \\"gl_account_code\\": \\"6980_ENTERTAINMENT\\", \\"ledger\\": {\\"expense_account\\": \\"6980_ENTERTAINMENT\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
29	تأمين شحنة	مصروف تأمين شحن	t	SHIP_INSURANCE	"{\\"required\\": [\\"shipment_id\\"], \\"optional\\": [\\"description\\"], \\"gl_account_code\\": \\"5510_SHIP_INSURANCE\\", \\"ledger\\": {\\"expense_account\\": \\"5510_SHIP_INSURANCE\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
31	ضريبة استيراد	مصروف ضرائب استيراد	t	SHIP_IMPORT_TAX	"{\\"required\\": [\\"shipment_id\\"], \\"optional\\": [\\"description\\"], \\"gl_account_code\\": \\"5530_SHIP_IMPORT_TAX\\", \\"ledger\\": {\\"expense_account\\": \\"5530_SHIP_IMPORT_TAX\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
32	شحن	مصروف شحن	t	SHIP_FREIGHT	"{\\"required\\": [\\"shipment_id\\"], \\"optional\\": [\\"description\\"], \\"gl_account_code\\": \\"5540_SHIP_FREIGHT\\", \\"ledger\\": {\\"expense_account\\": \\"5540_SHIP_FREIGHT\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
33	تخليص جمركي	مصروف تخليص جمركي	t	SHIP_CLEARANCE	"{\\"required\\": [\\"shipment_id\\"], \\"optional\\": [\\"description\\"], \\"gl_account_code\\": \\"5550_SHIP_CLEARANCE\\", \\"ledger\\": {\\"expense_account\\": \\"5550_SHIP_CLEARANCE\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
34	مناولة وأرضيات	مصروف مناولة/أرضيات	t	SHIP_HANDLING	"{\\"required\\": [\\"shipment_id\\"], \\"optional\\": [\\"description\\"], \\"gl_account_code\\": \\"5560_SHIP_HANDLING\\", \\"ledger\\": {\\"expense_account\\": \\"5560_SHIP_HANDLING\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
35	رسوم موانئ	مصروف رسوم ميناء/مطار	t	SHIP_PORT_FEES	"{\\"required\\": [\\"shipment_id\\"], \\"optional\\": [\\"description\\"], \\"gl_account_code\\": \\"5570_SHIP_PORT_FEES\\", \\"ledger\\": {\\"expense_account\\": \\"5570_SHIP_PORT_FEES\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
36	تخزين مؤقت	مصروف تخزين مؤقت	t	SHIP_STORAGE	"{\\"required\\": [\\"shipment_id\\"], \\"optional\\": [\\"description\\"], \\"gl_account_code\\": \\"5580_SHIP_STORAGE\\", \\"ledger\\": {\\"expense_account\\": \\"5580_SHIP_STORAGE\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-11-16 01:09:37
37	مصروف مورد	مصاريف متعلقة بالموردين (مصاريف شحن، جمارك، خدمات)	t	SUPPLIER_EXPENSE	"{\\"gl_account_code\\": \\"5100_SUPPLIER_EXPENSES\\", \\"required\\": [\\"supplier_id\\"], \\"optional\\": [\\"beneficiary_name\\", \\"period\\"], \\"ledger\\": {\\"expense_account\\": \\"5100_SUPPLIER_EXPENSES\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-11-04 19:36:09	2025-11-16 01:09:37
38	مصروف شريك	مصاريف متعلقة بالشركاء (تسويات، مصاريف مشتركة)	t	PARTNER_EXPENSE	"{\\"gl_account_code\\": \\"5200_PARTNER_EXPENSES\\", \\"required\\": [\\"partner_id\\"], \\"optional\\": [\\"beneficiary_name\\", \\"period\\"], \\"ledger\\": {\\"expense_account\\": \\"5200_PARTNER_EXPENSES\\", \\"counterparty_account\\": \\"2200_PARTNER_CLEARING\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-11-04 19:36:09	2025-11-16 01:02:03
39	فاتورة جوال	\N	t	\N	"{\\"kind\\": \\"MISC\\", \\"required\\": [], \\"ledger\\": {\\"expense_account\\": \\"5000_EXPENSES\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-11-07 14:15:01	2025-11-16 01:09:37
40	فواتير مياه وكهرباء	\N	t	\N	"{\\"gl_account_code\\": \\"5000_EXPENSES\\", \\"ledger\\": {\\"expense_account\\": \\"5000_EXPENSES\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-11-13 21:31:49	2025-11-16 01:09:37
41	نقل	\N	t	\N	"{\\"gl_account_code\\": \\"6320_TRANSPORT\\"}"	2025-11-16 20:20:56	2025-11-16 20:20:56
30	جمارك	رسوم جمركية	t	SHIP_CUSTOMS	"{\\"required\\": [\\"shipment_id\\"], \\"optional\\": [\\"description\\"], \\"gl_account_code\\": \\"5520_SHIP_CUSTOMS\\", \\"ledger\\": {\\"expense_account\\": \\"5520_SHIP_CUSTOMS\\", \\"counterparty_account\\": \\"2000_AP\\", \\"cash_account\\": \\"1000_CASH\\"}, \\"payment_behavior\\": \\"ON_ACCOUNT\\"}"	2025-10-31 20:41:37	2025-12-18 16:35:41.770519
44	تالف	توالف/هدر مخزون	t	\N	\N	2025-12-18 16:35:41.770519	2025-12-18 16:35:41.770519
45	استخدام داخلي	استهلاك داخلي للمخزون	t	\N	\N	2025-12-18 16:35:41.770519	2025-12-18 16:35:41.770519
46	متفرقات	مصروفات أخرى	t	\N	\N	2025-12-18 16:35:41.770519	2025-12-18 16:35:41.770519
\.


--
-- Data for Name: expenses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expenses (id, date, amount, currency, fx_rate_used, fx_rate_source, fx_rate_timestamp, fx_base_currency, fx_quote_currency, type_id, branch_id, site_id, employee_id, customer_id, warehouse_id, partner_id, supplier_id, shipment_id, utility_account_id, stock_adjustment_id, payee_type, payee_entity_id, payee_name, beneficiary_name, paid_to, disbursed_by, period_start, period_end, payment_method, payment_details, description, notes, tax_invoice_number, check_number, check_bank, check_due_date, check_payee, bank_transfer_ref, bank_name, account_number, account_holder, card_number, card_holder, card_expiry, online_gateway, online_ref, telecom_phone_number, telecom_service_type, insurance_company_name, insurance_company_address, insurance_company_phone, marketing_company_name, marketing_company_address, marketing_coverage_details, bank_fee_bank_name, bank_fee_notes, gov_fee_entity_name, gov_fee_entity_address, gov_fee_notes, port_fee_port_name, port_fee_notes, travel_destination, travel_reason, travel_notes, shipping_company_name, shipping_notes, maintenance_provider_name, maintenance_provider_address, maintenance_notes, rent_property_address, rent_property_notes, tech_provider_name, tech_provider_phone, tech_provider_address, tech_subscription_id, storage_property_address, storage_expected_days, storage_start_date, storage_notes, customs_arrival_date, customs_departure_date, customs_origin, customs_port_name, customs_notes, training_company_name, training_location, training_duration_days, training_participants_count, training_notes, training_participants_names, training_topics, entertainment_duration_days, entertainment_notes, bank_fee_reference, bank_fee_contact_name, bank_fee_contact_phone, gov_fee_reference, port_fee_reference, port_fee_agent_name, port_fee_agent_phone, salary_notes, salary_reference, travel_duration_days, travel_start_date, travel_companions, travel_cost_center, employee_advance_period, employee_advance_reason, employee_advance_notes, shipping_date, shipping_reference, shipping_mode, shipping_tracking_number, maintenance_details, maintenance_completion_date, maintenance_technician_name, import_tax_reference, import_tax_notes, hospitality_type, hospitality_notes, hospitality_attendees, hospitality_location, telecom_notes, office_supplier_name, office_notes, office_items_list, office_purchase_reference, home_relation_to_company, home_address, home_owner_name, home_notes, home_cost_share, partner_expense_reason, partner_expense_notes, partner_expense_reference, supplier_expense_reason, supplier_expense_notes, supplier_expense_reference, handling_notes, handling_quantity, handling_unit, handling_reference, fuel_vehicle_number, fuel_driver_name, fuel_usage_type, fuel_volume, fuel_notes, fuel_station_name, fuel_odometer_start, fuel_odometer_end, transport_beneficiary_name, transport_reason, transport_usage_type, transport_notes, transport_route_details, insurance_policy_number, insurance_notes, legal_company_name, legal_company_address, legal_case_notes, legal_case_number, legal_case_type, is_archived, archived_at, archived_by, archive_reason, cost_center_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: fixed_asset_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fixed_asset_categories (id, code, name, account_code, depreciation_account_code, useful_life_years, depreciation_method, depreciation_rate, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: fixed_assets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fixed_assets (id, asset_number, name, category_id, branch_id, site_id, purchase_date, purchase_price, supplier_id, serial_number, barcode, location, status, disposal_date, disposal_amount, disposal_notes, notes, is_archived, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: gl_batches; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gl_batches (id, code, source_type, source_id, purpose, memo, posted_at, currency, entity_type, entity_id, status, created_at, updated_at) FROM stdin;
10	SALE-2-REVENUE-20251025204434	SALE	2	REVENUE	فاتورة مبيعات #SAL20251024-0001 - اياد الغزاوي	2025-10-31 12:39:01.804446	ILS	CUSTOMER	2	POSTED	2025-10-25 20:44:34	2025-10-31 12:39:01
11	PAYMENT-7-PAYMENT-20251025205637	PAYMENT	7	PAYMENT	قبض من عميل - PMT20251003-0001	2025-10-31 12:39:01.800965	ILS	CUSTOMER	1	POSTED	2025-10-25 20:56:37	2025-10-31 14:23:40
13	PAYMENT-8-PAYMENT-20251025205929	PAYMENT	8	PAYMENT	قبض من عميل - PMT20250921-0001	2025-10-31 12:39:01.801247	ILS	CUSTOMER	1	POSTED	2025-10-25 20:59:29	2025-10-31 14:23:40
15	PAYMENT-9-PAYMENT-20251025210223	PAYMENT	9	PAYMENT	قبض من عميل - PMT20251023-0001	2025-10-31 12:39:01.80154	ILS	CUSTOMER	1	POSTED	2025-10-25 21:02:23	2025-10-31 14:23:40
17	PAYMENT-10-PAYMENT-20251025210408	PAYMENT	10	PAYMENT	قبض من عميل - PMT20250910-0001	2025-10-31 12:39:01.801927	ILS	CUSTOMER	1	POSTED	2025-10-25 21:04:08	2025-10-31 14:23:40
19	CUSTOMER-2-OPENING_BALANCE-20251025214722	CUSTOMER	2	OPENING_BALANCE	رصيد افتتاحي - اياد الغزاوي	2025-10-31 12:39:01.797777	ILS	CUSTOMER	2	POSTED	2025-10-25 21:47:22	2025-10-31 12:39:01
20	CUSTOMER-3-OPENING_BALANCE-20251025224141	CUSTOMER	3	OPENING_BALANCE	رصيد افتتاحي - أحمد الصالحي	2025-10-31 12:39:01.798149	ILS	CUSTOMER	3	POSTED	2025-10-25 22:41:41	2025-10-31 12:39:01
21	CUSTOMER-4-OPENING_BALANCE-20251026130144	CUSTOMER	4	OPENING_BALANCE	رصيد افتتاحي - فحص تجريبي 1	2025-10-31 12:39:01.798459	ILS	CUSTOMER	4	POSTED	2025-10-26 13:01:44	2025-10-31 12:39:01
23	SALE-4-REVENUE-20251026173349	SALE	4	REVENUE	فاتورة مبيعات #SAL20251026-0001 - منصور خليلي جماعين	2025-10-31 12:39:01.804737	ILS	CUSTOMER	4	POSTED	2025-10-26 17:33:49	2025-10-31 12:39:01
24	CHK-CHECK-5-CA13344E	check_check	5	\N	قيد شيك:  - تم السحب	2025-10-28 15:20:55.490954	ILS	\N	\N	POSTED	2025-10-28 15:20:55	2025-10-28 15:20:55
25	CHK-CHECK-1-4F9B486D	check_check	1	\N	قيد شيك:  - تم السحب	2025-10-28 15:21:01.751746	ILS	\N	\N	POSTED	2025-10-28 15:21:01	2025-10-28 15:21:01
26	PAYMENT-12-PAYMENT-20251028234012	PAYMENT	12	PAYMENT	قبض من عميل - PMT20251028-0001	2025-10-31 12:39:01.802467	ILS	CUSTOMER	1	POSTED	2025-10-28 23:40:12	2025-10-31 14:23:40
27	SALE-1-REVENUE-20251028234012	SALE	1	REVENUE	فاتورة مبيعات #SAL20251023-0001 - عامر ابو شخيدم	2025-10-31 12:39:01.804132	ILS	CUSTOMER	1	POSTED	2025-10-28 23:40:12	2025-10-31 12:39:01
28	CHK-CHECK-6-E576A0CD	check_check	6	\N	قيد شيك:  - تم السحب	2025-10-29 12:36:24.10811	ILS	\N	\N	POSTED	2025-10-29 12:36:24	2025-10-29 12:36:24
29	CHK-CHECK-4-FB7921F6	check_check	4	\N	قيد شيك:  - تم السحب	2025-10-29 12:36:42.59372	ILS	\N	\N	POSTED	2025-10-29 12:36:42	2025-10-29 12:36:42
35	PAYMENT-1-PAYMENT-20251029160140	PAYMENT	1	PAYMENT	قبض من عميل - PMT20251024-0001	2025-10-31 12:39:01.799533	ILS	CUSTOMER	2	POSTED	2025-10-29 16:01:40	2025-10-31 14:23:40
36	PAYMENT-4-PAYMENT-20251029160140	PAYMENT	4	PAYMENT	قبض من عميل - PMT20251011-0001	2025-10-31 12:39:01.800117	ILS	CUSTOMER	2	POSTED	2025-10-29 16:01:40	2025-10-31 14:23:40
37	PAYMENT-5-PAYMENT-20251029160140	PAYMENT	5	PAYMENT	قبض من عميل - PMT20251020-0001	2025-10-31 12:39:01.800427	ILS	CUSTOMER	2	POSTED	2025-10-29 16:01:40	2025-10-31 14:23:40
38	PAYMENT-6-PAYMENT-20251029160140	PAYMENT	6	PAYMENT	قبض من عميل - PMT20251025-0002	2025-10-31 12:39:01.800694	ILS	CUSTOMER	2	POSTED	2025-10-29 16:01:40	2025-10-31 14:23:40
40	PAYMENT-13-PAYMENT-20251029163702	PAYMENT	13	PAYMENT	قبض من عميل - PMT20251028-0002	2025-10-31 12:39:01.80271	ILS	CUSTOMER	3	POSTED	2025-10-29 16:37:02	2025-10-31 12:39:01
42	PAYMENT-14-PAYMENT-20251029164853	PAYMENT	14	PAYMENT	قبض من عميل - PMT20251029-0001	2025-10-31 12:39:01.802957	ILS	CUSTOMER	2	POSTED	2025-10-29 16:48:53	2025-10-31 12:39:01
43	PAYMENT-16-PAYMENT-20251029181836	PAYMENT	16	PAYMENT	قبض من عميل - PMT20251029-0002	2025-10-31 12:39:01.80324	ILS	CUSTOMER	5	POSTED	2025-10-29 18:18:36	2025-10-31 14:23:40
44	PAYMENT-17-PAYMENT-20251029182443	PAYMENT	17	PAYMENT	قبض من عميل - PMT20251029-0003	2025-10-31 12:39:01.803569	ILS	CUSTOMER	6	POSTED	2025-10-29 18:24:43	2025-10-31 14:23:40
46	PAYMENT-18-PAYMENT-20251029203517	PAYMENT	18	PAYMENT	قبض من عميل - PMT20251029-0004	2025-10-31 12:39:01.803815	ILS	CUSTOMER	8	POSTED	2025-10-29 20:35:17	2025-10-31 14:23:40
47	SALE-3-REVENUE-20251031124222	SALE	3	REVENUE	فاتورة مبيعات #SAL20251025-0001 - اياد الغزاوي	2025-10-31 12:42:22.693608	ILS	CUSTOMER	2	POSTED	2025-10-31 12:42:22	2025-10-31 12:42:22
48	PAYMENT-2-PAYMENT-20251031124222	PAYMENT	2	PAYMENT	قبض من عميل - PMT20251025-0001	2025-10-31 12:42:22.742798	ILS	CUSTOMER	2	POSTED	2025-10-31 12:42:22	2025-10-31 14:23:40
49	SALE-5-REVENUE-20251031125024	SALE	5	REVENUE	فاتورة مبيعات #SAL20251029-0001 - يوسف ابو علي دورا	2025-10-31 12:50:24.738343	ILS	CUSTOMER	5	POSTED	2025-10-31 12:50:24	2025-10-31 12:50:24
50	SALE-6-REVENUE-20251031125024	SALE	6	REVENUE	فاتورة مبيعات #SAL20251029-0002 - يوسف ابو علي دورا	2025-10-31 12:50:24.748269	ILS	CUSTOMER	5	POSTED	2025-10-31 12:50:24	2025-10-31 12:50:24
51	SALE-7-REVENUE-20251031125024	SALE	7	REVENUE	فاتورة مبيعات #SAL20251029-0003 - وليد قصراوي مضخات	2025-10-31 12:50:24.753307	ILS	CUSTOMER	6	POSTED	2025-10-31 12:50:24	2025-10-31 12:50:24
52	SALE-8-REVENUE-20251031125024	SALE	8	REVENUE	فاتورة مبيعات #SAL20251029-0004 - محمد سمير سبسطية	2025-10-31 12:50:24.757593	ILS	CUSTOMER	8	POSTED	2025-10-31 12:50:24	2025-10-31 12:50:24
56	SERVICE-1-SERVICE-20251101171646	SERVICE	1	SERVICE	صيانة - SRV-20251031211614	2025-11-01 17:16:46.220594	ILS	CUSTOMER	7	POSTED	2025-11-01 17:16:46	2025-11-01 17:16:46
60	PAYMENT-20-PAYMENT-20251103140503	PAYMENT	20	PAYMENT	قبض من عميل - PMT20251103-0001	2025-11-03 14:05:03.011954	ILS	SALE	9	POSTED	2025-11-03 14:05:03	2025-11-03 14:05:03
61	PAYMENT-21-PAYMENT-20251104121451	PAYMENT	21	PAYMENT	قبض من عميل - PMT20251104-0001	2025-11-04 12:14:51.565062	ILS	SALE	10	POSTED	2025-11-04 12:14:51	2025-11-04 12:14:51
62	SALE-11-REVENUE-20251104123430	SALE	11	REVENUE	فاتورة مبيعات #SAL20251104-0002 - عميل	2025-11-04 12:34:30.463175	ILS	CUSTOMER	10	POSTED	2025-11-04 12:34:30	2025-11-04 12:34:30
63	PAYMENT-22-PAYMENT-20251104123457	PAYMENT	22	PAYMENT	قبض من عميل - PMT20251104-0002	2025-11-04 12:34:57.798459	ILS	SALE	11	POSTED	2025-11-04 12:34:57	2025-11-04 12:34:57
64	PAYMENT-23-PAYMENT-20251104150039	PAYMENT	23	PAYMENT	قبض من عميل - PMT20251104-0003	2025-11-04 15:00:39.236886	ILS	SALE	12	POSTED	2025-11-04 15:00:39	2025-11-04 15:00:39
65	EXPENSE-1-EXPENSE-20251104193759	EXPENSE	1	EXPENSE	أخرى - بهاء الشاكوش	2025-11-04 19:37:59.757003	ILS	OTHER	\N	POSTED	2025-11-04 19:37:59	2025-11-04 19:37:59
66	EXPENSE-3-EXPENSE-20251104194320	EXPENSE	3	EXPENSE	أخرى - kwv	2025-11-04 19:43:20.289492	ILS	OTHER	\N	POSTED	2025-11-04 19:43:20	2025-11-04 19:43:20
67	EXPENSE-4-EXPENSE-20251104194320	EXPENSE	4	EXPENSE	رواتب - بلال نادر	2025-11-04 19:43:20.293202	ILS	EMPLOYEE	1	POSTED	2025-11-04 19:43:20	2025-11-04 19:43:20
68	SUPPLIER-2-OPENING_BALANCE-20251104195112	SUPPLIER	2	OPENING_BALANCE	رصيد افتتاحي - مورد تجريبي	2025-11-04 19:51:12.32773	ILS	SUPPLIER	2	POSTED	2025-11-04 19:51:12	2025-11-04 19:51:12
69	PARTNER-2-OPENING_BALANCE-20251104195112	PARTNER	2	OPENING_BALANCE	رصيد افتتاحي - شريك تجريبي	2025-11-04 19:51:12.352782	ILS	PARTNER	2	POSTED	2025-11-04 19:51:12	2025-11-04 19:51:12
70	EXPENSE-5-EXPENSE-20251104202439	EXPENSE	5	EXPENSE	مصروف مورد - حماد	2025-11-04 20:24:39.689489	ILS	OTHER	\N	POSTED	2025-11-04 20:24:39	2025-11-04 20:24:39
71	EXPENSE-2-EXPENSE-20251104203021	EXPENSE	2	EXPENSE	مصاريف بيت - 	2025-11-04 22:30:21.353884	ILS	OTHER	\N	POSTED	2025-11-04 20:30:21	2025-11-04 20:30:21
72	EXPENSE_REVERSAL-5-REVERSAL-20251104210925	EXPENSE_REVERSAL	5	REVERSAL	عكس قيد - حذف مصروف #5 - حماد	2025-11-04 21:09:25.721334	ILS	OTHER	\N	POSTED	2025-11-04 21:09:25	2025-11-04 21:09:25
73	SUPPLIER-3-OPENING_BALANCE-20251105072009	SUPPLIER	3	OPENING_BALANCE	رصيد افتتاحي - عصفور عصفور	2025-11-05 07:20:09.108456	ILS	SUPPLIER	3	POSTED	2025-11-05 07:20:09	2025-11-05 07:20:09
74	PARTNER-1-OPENING_BALANCE-20251105081128	PARTNER	1	OPENING_BALANCE	رصيد افتتاحي - سلامه محمد	2025-11-05 08:11:28.482997	ILS	PARTNER	1	POSTED	2025-11-05 08:11:28	2025-11-05 08:11:28
75	SUPPLIER-1-OPENING_BALANCE-20251105082540	SUPPLIER	1	OPENING_BALANCE	رصيد افتتاحي - سلامه مورد	2025-11-05 08:25:40.87447	ILS	SUPPLIER	1	POSTED	2025-11-05 08:25:40	2025-11-05 08:25:40
76	PAYMENT-24-PAYMENT-20251105084029	PAYMENT	24	PAYMENT	سداد لـ مورد - PMT20251105-0001	2025-11-05 08:40:29.429475	ILS	SUPPLIER	1	POSTED	2025-11-05 08:40:29	2025-11-05 08:40:29
77	PAYMENT-25-PAYMENT-20251105150729	PAYMENT	25	PAYMENT	سداد لـ مورد - PMT20251105-0001	2025-11-05 15:07:29.964043	ILS	SUPPLIER	1	POSTED	2025-11-05 15:07:29	2025-11-05 15:07:29
78	EXPENSE-6-EXPENSE-20251105151142	EXPENSE	6	EXPENSE	مصروف مورد - نفسه	2025-11-05 15:11:42.635307	ILS	OTHER	\N	POSTED	2025-11-05 15:11:42	2025-11-05 15:11:42
80	PAYMENT-26-PAYMENT-20251106122511	PAYMENT	26	PAYMENT	قبض من عميل - PMT20251106-0001	2025-11-06 12:25:11.00392	ILS	CUSTOMER	1	POSTED	2025-11-06 12:25:11	2025-11-06 12:25:11
81	CUSTOMER-12-OPENING_BALANCE-20251106123933	CUSTOMER	12	OPENING_BALANCE	رصيد افتتاحي - فريد ابو اياد الطوري	2025-11-06 12:39:33.179235	ILS	CUSTOMER	12	POSTED	2025-11-06 12:39:33	2025-11-06 12:39:33
82	PAYMENT-27-PAYMENT-20251106124818	PAYMENT	27	PAYMENT	قبض من عميل - PMT20251106-0002	2025-11-06 12:48:18.395313	ILS	CUSTOMER	1	POSTED	2025-11-06 12:48:18	2025-11-06 12:48:18
83	EXPENSE-7-EXPENSE-20251106125024	EXPENSE	7	EXPENSE	وقود - المحل	2025-11-06 12:50:24.969517	ILS	OTHER	\N	POSTED	2025-11-06 12:50:24	2025-11-06 12:50:24
84	EXPENSE-8-EXPENSE-20251106125059	EXPENSE	8	EXPENSE	أخرى - براء	2025-11-06 12:50:59.777443	ILS	OTHER	\N	POSTED	2025-11-06 12:50:59	2025-11-06 12:50:59
85	EXPENSE-9-EXPENSE-20251106155419	EXPENSE	9	EXPENSE	وقود - المحل	2025-11-06 15:54:19.833526	ILS	OTHER	\N	POSTED	2025-11-06 15:54:19	2025-11-06 15:54:19
86	EXPENSE-10-EXPENSE-20251106155447	EXPENSE	10	EXPENSE	أخرى - براء	2025-11-06 15:54:47.182338	ILS	OTHER	\N	POSTED	2025-11-06 15:54:47	2025-11-06 15:54:47
87	EXPENSE-11-EXPENSE-20251106155516	EXPENSE	11	EXPENSE	وقود - pajero	2025-11-06 15:55:16.909702	ILS	OTHER	\N	POSTED	2025-11-06 15:55:16	2025-11-06 15:55:16
88	PAYMENT-28-PAYMENT-20251106155731	PAYMENT	28	PAYMENT	سداد لـ مورد - PMT20251106-0003	2025-11-06 15:57:31.542552	ILS	SUPPLIER	1	POSTED	2025-11-06 15:57:31	2025-11-06 15:57:31
89	EXPENSE-12-EXPENSE-20251107141021	EXPENSE	12	EXPENSE	أخرى - بهاء	2025-11-07 14:10:21.455585	ILS	OTHER	\N	POSTED	2025-11-07 14:10:21	2025-11-07 14:10:21
90	EXPENSE-13-EXPENSE-20251107141052	EXPENSE	13	EXPENSE	أخرى - ضياء	2025-11-07 14:10:52.653119	ILS	OTHER	\N	POSTED	2025-11-07 14:10:52	2025-11-07 14:10:52
91	EXPENSE-14-EXPENSE-20251107141141	EXPENSE	14	EXPENSE	لوازم مكتبية - المكتب	2025-11-07 14:11:41.56759	ILS	OTHER	\N	POSTED	2025-11-07 14:11:41	2025-11-07 14:11:41
92	EXPENSE-15-EXPENSE-20251107141331	EXPENSE	15	EXPENSE	أخرى - نصر	2025-11-07 14:13:31.808536	ILS	OTHER	\N	POSTED	2025-11-07 14:13:31	2025-11-07 14:13:31
93	SALE-14-REVENUE-20251107144007	SALE	14	REVENUE	فاتورة مبيعات #SAL20251107-0001 - عميل	2025-11-07 14:40:07.195198	ILS	CUSTOMER	13	POSTED	2025-11-07 14:40:07	2025-11-07 14:40:07
94	SALE-15-REVENUE-20251107153426	SALE	15	REVENUE	فاتورة مبيعات #SAL20251107-0002 - عميل	2025-11-07 15:34:26.991896	ILS	CUSTOMER	14	POSTED	2025-11-07 15:34:26	2025-11-07 15:34:26
95	SALE-20-REVENUE-20251107154137	SALE	20	REVENUE	فاتورة مبيعات #SAL20251107-0007 - عميل	2025-11-07 15:41:37.767569	ILS	CUSTOMER	14	POSTED	2025-11-07 15:41:37	2025-11-07 15:41:37
96	SALE-21-REVENUE-20251107154416	SALE	21	REVENUE	فاتورة مبيعات #SAL20251107-0008 - عميل	2025-11-07 15:44:16.946706	ILS	CUSTOMER	14	POSTED	2025-11-07 15:44:16	2025-11-07 15:44:16
97	CUSTOMER-14-OPENING_BALANCE-20251107155256	CUSTOMER	14	OPENING_BALANCE	رصيد افتتاحي - محمد فارس	2025-11-07 15:52:56.800596	ILS	CUSTOMER	14	POSTED	2025-11-07 15:52:56	2025-11-07 15:52:56
98	PAYMENT-29-PAYMENT-20251107155644	PAYMENT	29	PAYMENT	قبض من عميل - PMT20230430-0001	2025-11-07 15:56:44.714492	ILS	CUSTOMER	14	POSTED	2025-11-07 15:56:44	2025-11-07 15:56:44
99	PAYMENT-30-PAYMENT-20251107155935	PAYMENT	30	PAYMENT	قبض من عميل - PMT20230507-0001	2025-11-07 15:59:35.517999	ILS	CUSTOMER	14	POSTED	2025-11-07 15:59:35	2025-11-07 15:59:35
100	PAYMENT-31-PAYMENT-20251107160237	PAYMENT	31	PAYMENT	قبض من عميل - PMT20251107-0001	2025-11-07 16:02:37.830479	ILS	CUSTOMER	14	POSTED	2025-11-07 16:02:37	2025-11-07 16:02:37
101	PAYMENT-32-PAYMENT-20251107160513	PAYMENT	32	PAYMENT	قبض من عميل - PMT20240107-0001	2025-11-07 16:05:13.860169	ILS	CUSTOMER	14	POSTED	2025-11-07 16:05:13	2025-11-07 16:05:13
102	PAYMENT-33-PAYMENT-20251107160713	PAYMENT	33	PAYMENT	قبض من عميل - PMT20240207-0001	2025-11-07 16:07:13.148464	ILS	CUSTOMER	14	POSTED	2025-11-07 16:07:13	2025-11-07 16:07:13
103	PAYMENT-34-PAYMENT-20251107160911	PAYMENT	34	PAYMENT	قبض من عميل - PMT20240605-0001	2025-11-07 16:09:11.755201	ILS	CUSTOMER	14	POSTED	2025-11-07 16:09:11	2025-11-07 16:09:11
104	PAYMENT-35-PAYMENT-20251107161044	PAYMENT	35	PAYMENT	قبض من عميل - PMT20251107-0002	2025-11-07 16:10:44.635823	ILS	CUSTOMER	14	POSTED	2025-11-07 16:10:44	2025-11-07 16:10:44
105	EXPENSE-16-EXPENSE-20251109203540	EXPENSE	16	EXPENSE	أخرى - حساب سمير بنك الشارقة الاسلامي	2025-11-09 20:35:40.251789	ILS	OTHER	\N	POSTED	2025-11-09 20:35:40	2025-11-09 20:35:40
106	EXPENSE-17-EXPENSE-20251109203710	EXPENSE	17	EXPENSE	وقود - مزليك تويوتا	2025-11-09 20:37:10.975427	ILS	OTHER	\N	POSTED	2025-11-09 20:37:10	2025-11-09 20:37:10
107	EXPENSE-18-EXPENSE-20251109203842	EXPENSE	18	EXPENSE	أخرى - مصطفى طولكرم	2025-11-09 20:38:42.61151	ILS	OTHER	\N	POSTED	2025-11-09 20:38:42	2025-11-09 20:38:42
108	PAYMENT-38-PAYMENT-20251109204731	PAYMENT	38	PAYMENT	قبض من عميل - PMT20251109-0001	2025-11-09 20:47:31.908112	ILS	CUSTOMER	17	POSTED	2025-11-09 20:47:31	2025-11-09 20:47:31
109	SERVICE-2-SERVICE-20251109205802	SERVICE	2	SERVICE	صيانة - SRV-20251109205633	2025-11-09 20:58:02.58122	ILS	CUSTOMER	18	POSTED	2025-11-09 20:58:02	2025-11-09 20:58:02
110	PAYMENT-39-PAYMENT-20251109205956	PAYMENT	39	PAYMENT	قبض من عميل - PMT20251109-0002	2025-11-09 20:59:56.145502	ILS	CUSTOMER	18	POSTED	2025-11-09 20:59:56	2025-11-09 20:59:56
111	EXPENSE-19-EXPENSE-20251109210507	EXPENSE	19	EXPENSE	فاتورة جوال - 	2025-11-09 21:05:07.791234	ILS	OTHER	\N	POSTED	2025-11-09 21:05:07	2025-11-09 21:05:07
112	SALE-23-REVENUE-20251109212618	SALE	23	REVENUE	فاتورة مبيعات #SAL20251109-0002 - عميل	2025-11-09 21:26:18.927193	ILS	CUSTOMER	18	POSTED	2025-11-09 21:26:18	2025-11-09 21:26:18
113	SALE-24-REVENUE-20251109215558	SALE	24	REVENUE	فاتورة مبيعات #SAL20251109-0003 - عميل	2025-11-09 21:55:58.275261	ILS	CUSTOMER	19	POSTED	2025-11-09 21:55:58	2025-11-09 21:55:58
114	PAYMENT-40-PAYMENT-20251109215651	PAYMENT	40	PAYMENT	قبض من عميل - PMT20251109-0003	2025-11-09 21:56:51.968139	ILS	CUSTOMER	19	POSTED	2025-11-09 21:56:51	2025-11-09 21:56:51
115	SALE-25-REVENUE-20251109221051	SALE	25	REVENUE	فاتورة مبيعات #SAL20251109-0004 - عميل	2025-11-09 22:10:51.758239	ILS	CUSTOMER	19	POSTED	2025-11-09 22:10:51	2025-11-09 22:10:51
116	SALE-26-REVENUE-20251109221709	SALE	26	REVENUE	فاتورة مبيعات #SAL20251109-0005 - عميل	2025-11-09 22:17:09.929441	ILS	CUSTOMER	20	POSTED	2025-11-09 22:17:09	2025-11-09 22:17:09
117	EXPENSE-20-EXPENSE-20251109222759	EXPENSE	20	EXPENSE	لوازم مكتبية - المكتب	2025-11-09 22:27:59.893136	ILS	OTHER	\N	POSTED	2025-11-09 22:27:59	2025-11-09 22:27:59
118	EXPENSE-21-EXPENSE-20251109222908	EXPENSE	21	EXPENSE	أخرى - احمد غنام	2025-11-09 22:29:08.758033	ILS	OTHER	\N	POSTED	2025-11-09 22:29:08	2025-11-09 22:29:08
119	EXPENSE-22-EXPENSE-20251109223019	EXPENSE	22	EXPENSE	فاتورة جوال - 	2025-11-09 22:30:19.119959	ILS	OTHER	\N	POSTED	2025-11-09 22:30:19	2025-11-09 22:30:19
120	EXPENSE-23-EXPENSE-20251109223305	EXPENSE	23	EXPENSE	أخرى - ابو ناصر ونش	2025-11-09 22:33:05.001679	ILS	OTHER	\N	POSTED	2025-11-09 22:33:05	2025-11-09 22:33:05
121	SALE-27-REVENUE-20251110123335	SALE	27	REVENUE	فاتورة مبيعات #SAL20251110-0001 - عميل	2025-11-10 12:33:35.548714	ILS	CUSTOMER	21	POSTED	2025-11-10 12:33:35	2025-11-10 12:33:35
122	PAYMENT-41-PAYMENT-20251110123351	PAYMENT	41	PAYMENT	قبض من عميل - PMT20251110-0001	2025-11-10 12:33:51.68056	ILS	CUSTOMER	21	POSTED	2025-11-10 12:33:51	2025-11-10 12:33:51
123	EXPENSE-24-EXPENSE-20251110124946	EXPENSE	24	EXPENSE	رواتب - اياد نوفل	2025-11-10 12:49:46.050864	ILS	EMPLOYEE	2	POSTED	2025-11-10 12:49:46	2025-11-10 12:49:46
125	CUSTOMER-22-OPENING_BALANCE-20251110223242	CUSTOMER	22	OPENING_BALANCE	رصيد افتتاحي - سامي كمال الطميزي	2025-11-10 22:32:42.298511	ILS	CUSTOMER	22	POSTED	2025-11-10 22:32:42	2025-11-10 22:32:42
126	PAYMENT-42-PAYMENT-20251110224347	PAYMENT	42	PAYMENT	سداد لـ عميل - PMT20251110-0002	2025-11-10 22:43:47.741734	ILS	CUSTOMER	22	POSTED	2025-11-10 22:43:47	2025-11-10 22:43:47
127	SALE-28-REVENUE-20251112124225	SALE	28	REVENUE	فاتورة مبيعات #SAL20251112-0001 - عميل	2025-11-12 12:42:25.734336	ILS	CUSTOMER	23	POSTED	2025-11-12 12:42:25	2025-11-12 12:42:25
128	EXPENSE-25-EXPENSE-20251112124347	EXPENSE	25	EXPENSE	لوازم مكتبية - 	2025-11-12 12:43:47.999886	ILS	OTHER	\N	POSTED	2025-11-12 12:43:48	2025-11-12 12:43:48
129	SALE-29-REVENUE-20251112143459	SALE	29	REVENUE	فاتورة مبيعات #SAL20251112-0002 - عميل	2025-11-12 14:34:59.162634	ILS	CUSTOMER	24	POSTED	2025-11-12 14:34:59	2025-11-12 14:34:59
130	PAYMENT-65-PAYMENT-20251112143605	PAYMENT	65	PAYMENT	قبض من عميل - PMT20251112-0001	2025-11-12 14:36:05.386241	ILS	CUSTOMER	24	POSTED	2025-11-12 14:36:05	2025-11-12 14:36:05
131	EXPENSE_REVERSAL-24-REVERSAL-20251112171732	EXPENSE_REVERSAL	24	REVERSAL	عكس قيد - حذف مصروف #24 - اياد نوفل	2025-11-12 17:17:32.426211	ILS	EMPLOYEE	5	POSTED	2025-11-12 17:17:32	2025-11-12 17:17:32
132	EXPENSE-26-EXPENSE-20251112171837	EXPENSE	26	EXPENSE	أخرى - اياد نوفل	2025-11-12 17:18:37.917065	ILS	OTHER	\N	POSTED	2025-11-12 17:18:37	2025-11-12 17:18:37
133	SALE-30-REVENUE-20251112173752	SALE	30	REVENUE	فاتورة مبيعات #SAL20251112-0003 - عميل	2025-11-12 17:37:52.759365	ILS	CUSTOMER	25	POSTED	2025-11-12 17:37:52	2025-11-12 17:37:52
134	PAYMENT-66-PAYMENT-20251112173957	PAYMENT	66	PAYMENT	قبض من عميل - PMT20251112-0002	2025-11-12 17:39:57.840235	ILS	CUSTOMER	25	POSTED	2025-11-12 17:39:57	2025-11-12 17:39:57
135	PAYMENT-67-PAYMENT-20251112194954	PAYMENT	67	PAYMENT	قبض من عميل - PMT20251112-0003	2025-11-12 19:49:54.306381	ILS	CUSTOMER	26	POSTED	2025-11-12 19:49:54	2025-11-12 19:49:54
136	EXPENSE-27-EXPENSE-20251112201504	EXPENSE	27	EXPENSE	وقود - 	2025-11-12 20:15:04.090033	ILS	OTHER	\N	POSTED	2025-11-12 20:15:04	2025-11-12 20:15:04
137	EXPENSE_REVERSAL-4-REVERSAL-20251112203617	EXPENSE_REVERSAL	4	REVERSAL	عكس قيد - حذف مصروف #4 - بلال نادر	2025-11-12 20:36:17.684051	ILS	EMPLOYEE	4	POSTED	2025-11-12 20:36:17	2025-11-12 20:36:17
138	PAYMENT-69-PAYMENT-20251112204452	PAYMENT	69	PAYMENT	سداد لـ مورد - PMT20251112-0004	2025-11-12 20:44:52.639785	ILS	SUPPLIER	1	POSTED	2025-11-12 20:44:52	2025-11-12 20:44:52
139	PAYMENT-43-PAYMENT-20251112221903	PAYMENT	43	PAYMENT	سداد لـ مصروف - EXP-PAY-1	2025-11-12 22:19:03.36627	ILS	EXPENSE	1	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
140	PAYMENT-44-PAYMENT-20251112221903	PAYMENT	44	PAYMENT	سداد لـ مصروف - EXP-PAY-2	2025-11-12 22:19:03.375268	ILS	EXPENSE	2	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
141	PAYMENT-45-PAYMENT-20251112221903	PAYMENT	45	PAYMENT	سداد لـ مصروف - EXP-PAY-3	2025-11-12 22:19:03.376825	ILS	EXPENSE	3	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
142	PAYMENT-47-PAYMENT-20251112221903	PAYMENT	47	PAYMENT	سداد لـ مصروف - EXP-PAY-7	2025-11-12 22:19:03.37842	ILS	EXPENSE	7	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
143	PAYMENT-48-PAYMENT-20251112221903	PAYMENT	48	PAYMENT	سداد لـ مصروف - EXP-PAY-8	2025-11-12 22:19:03.379944	ILS	EXPENSE	8	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
144	PAYMENT-49-PAYMENT-20251112221903	PAYMENT	49	PAYMENT	سداد لـ مصروف - EXP-PAY-9	2025-11-12 22:19:03.381559	ILS	EXPENSE	9	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
145	PAYMENT-50-PAYMENT-20251112221903	PAYMENT	50	PAYMENT	سداد لـ مصروف - EXP-PAY-10	2025-11-12 22:19:03.3831	ILS	EXPENSE	10	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
146	PAYMENT-51-PAYMENT-20251112221903	PAYMENT	51	PAYMENT	سداد لـ مصروف - EXP-PAY-11	2025-11-12 22:19:03.384722	ILS	EXPENSE	11	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
147	PAYMENT-52-PAYMENT-20251112221903	PAYMENT	52	PAYMENT	سداد لـ مصروف - EXP-PAY-12	2025-11-12 22:19:03.386136	ILS	EXPENSE	12	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
148	PAYMENT-53-PAYMENT-20251112221903	PAYMENT	53	PAYMENT	سداد لـ مصروف - EXP-PAY-13	2025-11-12 22:19:03.387437	ILS	EXPENSE	13	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
149	PAYMENT-54-PAYMENT-20251112221903	PAYMENT	54	PAYMENT	سداد لـ مصروف - EXP-PAY-14	2025-11-12 22:19:03.388942	ILS	EXPENSE	14	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
150	PAYMENT-55-PAYMENT-20251112221903	PAYMENT	55	PAYMENT	سداد لـ مصروف - EXP-PAY-15	2025-11-12 22:19:03.390401	ILS	EXPENSE	15	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
151	PAYMENT-56-PAYMENT-20251112221903	PAYMENT	56	PAYMENT	سداد لـ مصروف - EXP-PAY-16	2025-11-12 22:19:03.391704	ILS	EXPENSE	16	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
152	PAYMENT-57-PAYMENT-20251112221903	PAYMENT	57	PAYMENT	سداد لـ مصروف - EXP-PAY-17	2025-11-12 22:19:03.392845	ILS	EXPENSE	17	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
153	PAYMENT-58-PAYMENT-20251112221903	PAYMENT	58	PAYMENT	سداد لـ مصروف - EXP-PAY-18	2025-11-12 22:19:03.394059	ILS	EXPENSE	18	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
154	PAYMENT-59-PAYMENT-20251112221903	PAYMENT	59	PAYMENT	سداد لـ مصروف - EXP-PAY-19	2025-11-12 22:19:03.395263	ILS	EXPENSE	19	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
155	PAYMENT-60-PAYMENT-20251112221903	PAYMENT	60	PAYMENT	سداد لـ مصروف - EXP-PAY-20	2025-11-12 22:19:03.396475	ILS	EXPENSE	20	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
156	PAYMENT-61-PAYMENT-20251112221903	PAYMENT	61	PAYMENT	سداد لـ مصروف - EXP-PAY-21	2025-11-12 22:19:03.397928	ILS	EXPENSE	21	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
157	PAYMENT-62-PAYMENT-20251112221903	PAYMENT	62	PAYMENT	سداد لـ مصروف - EXP-PAY-22	2025-11-12 22:19:03.399234	ILS	EXPENSE	22	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
158	PAYMENT-63-PAYMENT-20251112221903	PAYMENT	63	PAYMENT	سداد لـ مصروف - EXP-PAY-23	2025-11-12 22:19:03.400793	ILS	EXPENSE	23	POSTED	2025-11-12 22:19:03	2025-11-12 22:19:03
159	PAYMENT-70-PAYMENT-20251113092835	PAYMENT	70	PAYMENT	قبض من عميل - PMT20251113-0001	2025-11-13 09:28:35.159277	ILS	CUSTOMER	18	POSTED	2025-11-13 09:28:35	2025-11-13 09:28:35
161	SALE-31-REVENUE-20251113103637	SALE	31	REVENUE	فاتورة مبيعات #SAL20251113-0001 - عميل	2025-11-13 10:36:37.986047	ILS	CUSTOMER	27	POSTED	2025-11-13 10:36:37	2025-11-13 10:36:37
163	PAYMENT-72-PAYMENT-20251113120914	PAYMENT	72	PAYMENT	قبض من عميل - PMT20251113-0003	2025-11-13 12:09:14.897255	ILS	CUSTOMER	27	POSTED	2025-11-13 12:09:14	2025-11-13 12:09:14
164	PAYMENT-73-PAYMENT-20251113121104	PAYMENT	73	PAYMENT	سداد لـ عميل - PMT20251113-0004	2025-11-13 12:11:04.773728	ILS	CUSTOMER	27	POSTED	2025-11-13 12:11:04	2025-11-13 12:11:04
165	PAYMENT-74-PAYMENT-20251113121324	PAYMENT	74	PAYMENT	قبض من عميل - PMT20251113-0005	2025-11-13 12:13:24.204937	ILS	CUSTOMER	23	POSTED	2025-11-13 12:13:24	2025-11-13 12:13:24
167	PAYMENT-76-PAYMENT-20251113192517	PAYMENT	76	PAYMENT	قبض من عميل - PMT20251113-0006	2025-11-13 19:25:17.289517	ILS	CUSTOMER	7	POSTED	2025-11-13 19:25:17	2025-11-13 19:25:17
168	EXPENSE-28-EXPENSE-20251113213855	EXPENSE	28	EXPENSE	فواتير مياه وكهرباء - 	2025-11-13 21:38:55.64776	ILS	OTHER	\N	POSTED	2025-11-13 21:38:55	2025-11-13 21:38:55
169	EXPENSE-29-EXPENSE-20251113225355	EXPENSE	29	EXPENSE	أخرى - بهاء	2025-11-13 22:53:55.447991	ILS	OTHER	\N	POSTED	2025-11-13 22:53:55	2025-11-13 22:53:55
170	EXPENSE-30-EXPENSE-20251113225417	EXPENSE	30	EXPENSE	أخرى - ضياء	2025-11-13 22:54:17.40097	ILS	OTHER	\N	POSTED	2025-11-13 22:54:17	2025-11-13 22:54:17
171	EXPENSE-31-EXPENSE-20251113225507	EXPENSE	31	EXPENSE	أخرى - براء	2025-11-13 22:55:07.153748	ILS	OTHER	\N	POSTED	2025-11-13 22:55:07	2025-11-13 22:55:07
172	EXPENSE-32-EXPENSE-20251113225540	EXPENSE	32	EXPENSE	وقود - المحل	2025-11-13 22:55:40.713184	ILS	OTHER	\N	POSTED	2025-11-13 22:55:40	2025-11-13 22:55:40
173	PAYMENT-77-PAYMENT-20251114204551	PAYMENT	77	PAYMENT	قبض من عميل - PMT20251114-0001	2025-11-14 20:45:51.570638	ILS	CUSTOMER	1	POSTED	2025-11-14 20:45:51	2025-11-14 20:45:51
174	PAYMENT-78-PAYMENT-20251114205024	PAYMENT	78	PAYMENT	سداد لـ مورد - PMT20251114-0002	2025-11-14 20:50:24.921311	ILS	SUPPLIER	2	POSTED	2025-11-14 20:50:24	2025-11-14 20:50:24
175	EXPENSE-33-EXPENSE-20251114205313	EXPENSE	33	EXPENSE	أخرى - kwv	2025-11-14 20:53:13.923583	ILS	OTHER	\N	POSTED	2025-11-14 20:53:13	2025-11-14 20:53:13
178	PAYMENT-81-PAYMENT-20251115130616	PAYMENT	81	PAYMENT	سداد لـ مورد - PMT20251115-0003	2025-11-15 13:06:16.650469	ILS	SUPPLIER	2	POSTED	2025-11-15 13:06:16	2025-11-15 13:06:16
179	PAYMENT-82-PAYMENT-20251116020732	PAYMENT	82	PAYMENT	سداد لـ مصروف - PMT20251116-0001	2025-11-16 02:07:32.423099	ILS	EXPENSE	1	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
180	PAYMENT-83-PAYMENT-20251116020732	PAYMENT	83	PAYMENT	سداد لـ مصروف - PMT20251116-0002	2025-11-16 02:07:32.429839	ILS	EXPENSE	2	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
181	PAYMENT-84-PAYMENT-20251116020732	PAYMENT	84	PAYMENT	سداد لـ مصروف - PMT20251116-0003	2025-11-16 02:07:32.439907	ILS	EXPENSE	3	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
182	PAYMENT-85-PAYMENT-20251116020732	PAYMENT	85	PAYMENT	سداد لـ مصروف - PMT20251116-0004	2025-11-16 02:07:32.447364	ILS	EXPENSE	7	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
183	PAYMENT-86-PAYMENT-20251116020732	PAYMENT	86	PAYMENT	سداد لـ مصروف - PMT20251116-0005	2025-11-16 02:07:32.455329	ILS	EXPENSE	8	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
184	PAYMENT-87-PAYMENT-20251116020732	PAYMENT	87	PAYMENT	سداد لـ مصروف - PMT20251116-0006	2025-11-16 02:07:32.463476	ILS	EXPENSE	9	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
185	PAYMENT-88-PAYMENT-20251116020732	PAYMENT	88	PAYMENT	سداد لـ مصروف - PMT20251116-0007	2025-11-16 02:07:32.471643	ILS	EXPENSE	10	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
186	PAYMENT-89-PAYMENT-20251116020732	PAYMENT	89	PAYMENT	سداد لـ مصروف - PMT20251116-0008	2025-11-16 02:07:32.479567	ILS	EXPENSE	11	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
187	PAYMENT-90-PAYMENT-20251116020732	PAYMENT	90	PAYMENT	سداد لـ مصروف - PMT20251116-0009	2025-11-16 02:07:32.488538	ILS	EXPENSE	12	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
188	PAYMENT-91-PAYMENT-20251116020732	PAYMENT	91	PAYMENT	سداد لـ مصروف - PMT20251116-0010	2025-11-16 02:07:32.49854	ILS	EXPENSE	13	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
189	PAYMENT-92-PAYMENT-20251116020732	PAYMENT	92	PAYMENT	سداد لـ مصروف - PMT20251116-0011	2025-11-16 02:07:32.507256	ILS	EXPENSE	14	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
190	PAYMENT-93-PAYMENT-20251116020732	PAYMENT	93	PAYMENT	سداد لـ مصروف - PMT20251116-0012	2025-11-16 02:07:32.514226	ILS	EXPENSE	15	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
191	PAYMENT-94-PAYMENT-20251116020732	PAYMENT	94	PAYMENT	سداد لـ مصروف - PMT20251116-0013	2025-11-16 02:07:32.521049	ILS	EXPENSE	16	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
192	PAYMENT-95-PAYMENT-20251116020732	PAYMENT	95	PAYMENT	سداد لـ مصروف - PMT20251116-0014	2025-11-16 02:07:32.530012	ILS	EXPENSE	17	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
193	PAYMENT-96-PAYMENT-20251116020732	PAYMENT	96	PAYMENT	سداد لـ مصروف - PMT20251116-0015	2025-11-16 02:07:32.537549	ILS	EXPENSE	18	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
194	PAYMENT-97-PAYMENT-20251116020732	PAYMENT	97	PAYMENT	سداد لـ مصروف - PMT20251116-0016	2025-11-16 02:07:32.546438	ILS	EXPENSE	19	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
195	PAYMENT-98-PAYMENT-20251116020732	PAYMENT	98	PAYMENT	سداد لـ مصروف - PMT20251116-0017	2025-11-16 02:07:32.555516	ILS	EXPENSE	20	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
196	PAYMENT-99-PAYMENT-20251116020732	PAYMENT	99	PAYMENT	سداد لـ مصروف - PMT20251116-0018	2025-11-16 02:07:32.564304	ILS	EXPENSE	21	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
197	PAYMENT-100-PAYMENT-20251116020732	PAYMENT	100	PAYMENT	سداد لـ مصروف - PMT20251116-0019	2025-11-16 02:07:32.573759	ILS	EXPENSE	22	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
198	PAYMENT-101-PAYMENT-20251116020732	PAYMENT	101	PAYMENT	سداد لـ مصروف - PMT20251116-0020	2025-11-16 02:07:32.581197	ILS	EXPENSE	23	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
199	PAYMENT-102-PAYMENT-20251116020732	PAYMENT	102	PAYMENT	سداد لـ مصروف - PMT20251116-0021	2025-11-16 02:07:32.589905	ILS	EXPENSE	25	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
200	PAYMENT-103-PAYMENT-20251116020732	PAYMENT	103	PAYMENT	سداد لـ مصروف - PMT20251116-0022	2025-11-16 02:07:32.59726	ILS	EXPENSE	26	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
201	PAYMENT-104-PAYMENT-20251116020732	PAYMENT	104	PAYMENT	سداد لـ مصروف - PMT20251116-0023	2025-11-16 02:07:32.605547	ILS	EXPENSE	27	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
202	PAYMENT-105-PAYMENT-20251116020732	PAYMENT	105	PAYMENT	سداد لـ مصروف - PMT20251116-0024	2025-11-16 02:07:32.615434	ILS	EXPENSE	28	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
203	PAYMENT-106-PAYMENT-20251116020732	PAYMENT	106	PAYMENT	سداد لـ مصروف - PMT20251116-0025	2025-11-16 02:07:32.626553	ILS	EXPENSE	29	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
204	PAYMENT-107-PAYMENT-20251116020732	PAYMENT	107	PAYMENT	سداد لـ مصروف - PMT20251116-0026	2025-11-16 02:07:32.632764	ILS	EXPENSE	30	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
205	PAYMENT-108-PAYMENT-20251116020732	PAYMENT	108	PAYMENT	سداد لـ مصروف - PMT20251116-0027	2025-11-16 02:07:32.640141	ILS	EXPENSE	31	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
206	PAYMENT-109-PAYMENT-20251116020732	PAYMENT	109	PAYMENT	سداد لـ مصروف - PMT20251116-0028	2025-11-16 02:07:32.647412	ILS	EXPENSE	32	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
207	PAYMENT-110-PAYMENT-20251116020732	PAYMENT	110	PAYMENT	سداد لـ مصروف - PMT20251116-0029	2025-11-16 02:07:32.654226	ILS	EXPENSE	33	POSTED	2025-11-16 02:07:32	2025-11-16 02:07:32
208	PAYMENT-111-PAYMENT-20251116193203	PAYMENT	111	PAYMENT	سداد لـ مورد - PMT20251116-0030	2025-11-16 19:32:03.705632	ILS	SUPPLIER	4	POSTED	2025-11-16 19:32:03	2025-11-16 19:32:03
209	EXPENSE-34-ACCRUAL-20251116193649	EXPENSE	34	ACCRUAL	قيد مصروف #34	2025-11-16 19:36:49.049212	ILS	SUPPLIER	3	POSTED	2025-11-16 19:36:49	2025-11-16 19:36:49
210	PAYMENT-112-PAYMENT-20251116200117	PAYMENT	112	PAYMENT	قبض من عميل - PMT20251116-0031	2025-11-16 20:01:17.004505	ILS	CUSTOMER	28	POSTED	2025-11-16 20:01:17	2025-11-16 20:01:17
211	SALE-33-REVENUE-20251116201517	SALE	33	REVENUE	فاتورة مبيعات #SAL20251116-0001 - عميل	2025-11-16 20:15:17.472925	ILS	CUSTOMER	30	POSTED	2025-11-16 20:15:17	2025-11-16 20:15:17
212	PAYMENT-113-PAYMENT-20251116201544	PAYMENT	113	PAYMENT	قبض من عميل - PMT20251116-0032	2025-11-16 20:15:44.667112	ILS	CUSTOMER	30	POSTED	2025-11-16 20:15:44	2025-11-16 20:15:44
213	PAYMENT-114-PAYMENT-20251116201712	PAYMENT	114	PAYMENT	قبض من عميل - PMT20251116-0033	2025-11-16 20:17:12.705942	ILS	CUSTOMER	31	POSTED	2025-11-16 20:17:12	2025-11-16 20:17:12
214	PAYMENT-115-PAYMENT-20251116201952	PAYMENT	115	PAYMENT	قبض من عميل - PMT20251116-0034	2025-11-16 20:19:52.035408	ILS	CUSTOMER	32	POSTED	2025-11-16 20:19:52	2025-11-16 20:19:52
215	EXPENSE-35-ACCRUAL-20251116202144	EXPENSE	35	ACCRUAL	قيد مصروف #35	2025-11-16 20:21:44.565325	ILS	\N	\N	POSTED	2025-11-16 20:21:44	2025-11-16 20:21:44
216	EXPENSE-36-ACCRUAL-20251116202207	EXPENSE	36	ACCRUAL	قيد مصروف #36	2025-11-16 20:22:07.859476	ILS	\N	\N	POSTED	2025-11-16 20:22:07	2025-11-16 20:22:07
217	EXPENSE-37-ACCRUAL-20251116202230	EXPENSE	37	ACCRUAL	قيد مصروف #37	2025-11-16 20:22:30.305313	ILS	\N	\N	POSTED	2025-11-16 20:22:30	2025-11-16 20:22:30
218	EXPENSE-38-ACCRUAL-20251116202305	EXPENSE	38	ACCRUAL	قيد مصروف #38	2025-11-16 20:23:05.442194	ILS	\N	\N	POSTED	2025-11-16 20:23:05	2025-11-16 20:23:05
219	EXPENSE-39-ACCRUAL-20251116202345	EXPENSE	39	ACCRUAL	قيد مصروف #39	2025-11-16 20:23:45.093668	ILS	\N	\N	POSTED	2025-11-16 20:23:45	2025-11-16 20:23:45
220	EXPENSE-40-ACCRUAL-20251116202454	EXPENSE	40	ACCRUAL	قيد مصروف #40	2025-11-16 20:24:54.83076	ILS	\N	\N	POSTED	2025-11-16 20:24:54	2025-11-16 20:24:54
221	EXPENSE-41-ACCRUAL-20251116202553	EXPENSE	41	ACCRUAL	قيد مصروف #41	2025-11-16 20:25:53.630288	ILS	\N	\N	POSTED	2025-11-16 20:25:53	2025-11-16 20:25:53
222	PAYMENT-116-PAYMENT-20251116204101	PAYMENT	116	PAYMENT	سداد لـ مورد - PMT20251116-0035	2025-11-16 20:41:01.82721	ILS	SUPPLIER	3	POSTED	2025-11-16 20:41:01	2025-11-16 20:41:01
223	EXPENSE-42-ACCRUAL-20251116204814	EXPENSE	42	ACCRUAL	قيد مصروف #42	2025-11-16 20:48:14.507638	ILS	SUPPLIER	5	POSTED	2025-11-16 20:48:14	2025-11-16 20:48:14
224	PAYMENT-117-PAYMENT-20251116204831	PAYMENT	117	PAYMENT	سداد لـ مصروف - PMT20251116-0035	2025-11-16 20:48:31.984132	ILS	EXPENSE	42	POSTED	2025-11-16 20:48:31	2025-11-16 20:48:31
225	SALE-36-REVENUE-20251117150327	SALE	36	REVENUE	فاتورة مبيعات #SAL20251117-0001 - عميل	2025-11-17 15:03:27.68909	ILS	CUSTOMER	32	POSTED	2025-11-17 15:03:27	2025-11-17 15:03:27
226	SALE-37-REVENUE-20251117150731	SALE	37	REVENUE	فاتورة مبيعات #SAL20251117-0002 - عميل	2025-11-17 15:07:31.528598	ILS	CUSTOMER	32	POSTED	2025-11-17 15:07:31	2025-11-17 15:07:31
227	PAYMENT-119-PAYMENT-20251117150801	PAYMENT	119	PAYMENT	قبض من عميل - PMT20251117-0001	2025-11-17 15:08:01.322243	ILS	CUSTOMER	32	POSTED	2025-11-17 15:08:01	2025-11-17 15:08:01
228	PAYMENT-120-PAYMENT-20251117150825	PAYMENT	120	PAYMENT	قبض من عميل - PMT20251117-0002	2025-11-17 15:08:25.605243	ILS	CUSTOMER	32	POSTED	2025-11-17 15:08:25	2025-11-17 15:08:25
229	EXPENSE-43-ACCRUAL-20251117150950	EXPENSE	43	ACCRUAL	قيد مصروف #43	2025-11-17 15:09:50.010014	ILS	\N	\N	POSTED	2025-11-17 15:09:50	2025-11-17 15:09:50
230	EXPENSE-44-ACCRUAL-20251117151013	EXPENSE	44	ACCRUAL	قيد مصروف #44	2025-11-17 15:10:13.166812	ILS	\N	\N	POSTED	2025-11-17 15:10:13	2025-11-17 15:10:13
231	PAYMENT-121-PAYMENT-20251118162810	PAYMENT	121	PAYMENT	قبض من عميل - PMT20251118-0001	2025-11-18 16:28:10.267696	ILS	CUSTOMER	18	POSTED	2025-11-18 16:28:10	2025-11-18 16:28:10
232	PAYMENT-122-PAYMENT-20251125103949	PAYMENT	122	PAYMENT	قبض من عميل - PMT20251125-0001	2025-11-25 10:39:49.539705	ILS	CUSTOMER	1	POSTED	2025-11-25 10:39:49	2025-11-25 10:39:49
233	PAYMENT_SPLIT-61-PAYMENT-20251125103949	PAYMENT_SPLIT	61	PAYMENT	قبض نقد من عميل - Split #61 - PMT20251125-0001	2025-11-25 10:39:49.551054	ILS	CUSTOMER	1	POSTED	2025-11-25 10:39:49	2025-11-25 10:39:49
234	SALE-38-REVENUE-20251125104307	SALE	38	REVENUE	فاتورة مبيعات #SAL20251125-0001 - عميل	2025-11-25 10:43:07.175517	ILS	CUSTOMER	1	POSTED	2025-11-25 10:43:07	2025-11-25 10:43:07
235	SALE-39-REVENUE-20251125104800	SALE	39	REVENUE	فاتورة مبيعات #SAL20251125-0002	2025-11-25 10:48:00.846097	ILS	CUSTOMER	37	POSTED	2025-11-25 10:48:00	2025-11-25 10:48:00
236	SERVICE-4-SERVICE-20251125105256	SERVICE	4	SERVICE	صيانة - SRV-20251125105207	2025-11-25 10:52:56.313042	ILS	CUSTOMER	18	POSTED	2025-11-25 10:52:56	2025-11-25 10:52:56
237	PAYMENT-123-PAYMENT-20251125105333	PAYMENT	123	PAYMENT	قبض من عميل - PMT20251125-0002	2025-11-25 10:53:33.028768	ILS	CUSTOMER	18	POSTED	2025-11-25 10:53:33	2025-11-25 10:53:33
238	PAYMENT_SPLIT-62-PAYMENT-20251125105333	PAYMENT_SPLIT	62	PAYMENT	قبض نقد من عميل - Split #62 - PMT20251125-0002	2025-11-25 10:53:33.036433	ILS	CUSTOMER	18	POSTED	2025-11-25 10:53:33	2025-11-25 10:53:33
239	SALE-40-REVENUE-20251125110004	SALE	40	REVENUE	فاتورة مبيعات #SAL20251125-0003	2025-11-25 11:00:04.629556	ILS	CUSTOMER	2	POSTED	2025-11-25 11:00:04	2025-11-25 11:00:04
240	SALE-41-REVENUE-20251125131919	SALE	41	REVENUE	فاتورة مبيعات #SAL20251125-0004	2025-11-25 13:19:19.575248	ILS	CUSTOMER	38	POSTED	2025-11-25 13:19:19	2025-11-25 13:19:19
241	PAYMENT-124-PAYMENT-20251125132006	PAYMENT	124	PAYMENT	قبض من عميل - PMT20251125-0003	2025-11-25 13:20:06.712389	ILS	CUSTOMER	38	POSTED	2025-11-25 13:20:06	2025-11-25 13:20:06
242	PAYMENT_SPLIT-63-PAYMENT-20251125132006	PAYMENT_SPLIT	63	PAYMENT	قبض نقد من عميل - Split #63 - PMT20251125-0003	2025-11-25 13:20:06.730389	ILS	CUSTOMER	38	POSTED	2025-11-25 13:20:06	2025-11-25 13:20:06
243	SALE-42-REVENUE-20251125133138	SALE	42	REVENUE	فاتورة مبيعات #SAL20251125-0005 - عميل	2025-11-25 13:31:38.634309	ILS	CUSTOMER	13	POSTED	2025-11-25 13:31:38	2025-11-25 13:31:38
244	SALE-43-REVENUE-20251125133329	SALE	43	REVENUE	فاتورة مبيعات #SAL20251125-0006 - عميل	2025-11-25 13:33:29.878901	ILS	CUSTOMER	13	POSTED	2025-11-25 13:33:29	2025-11-25 13:33:29
245	SALE-44-REVENUE-20251125133604	SALE	44	REVENUE	فاتورة مبيعات #SAL20251125-0007 - عميل	2025-11-25 13:36:04.826198	ILS	CUSTOMER	39	POSTED	2025-11-25 13:36:04	2025-11-25 13:36:04
246	SALE-45-REVENUE-20251125134030	SALE	45	REVENUE	فاتورة مبيعات #SAL20251125-0008 - عميل	2025-11-25 13:40:30.826204	ILS	CUSTOMER	27	POSTED	2025-11-25 13:40:30	2025-11-25 13:40:30
247	PAYMENT-125-PAYMENT-20251125134054	PAYMENT	125	PAYMENT	قبض من عميل - PMT20251125-0004	2025-11-25 13:40:54.230943	ILS	CUSTOMER	27	POSTED	2025-11-25 13:40:54	2025-11-25 13:40:54
248	PAYMENT_SPLIT-64-PAYMENT-20251125134054	PAYMENT_SPLIT	64	PAYMENT	قبض نقد من عميل - Split #64 - PMT20251125-0004	2025-11-25 13:40:54.237491	ILS	CUSTOMER	27	POSTED	2025-11-25 13:40:54	2025-11-25 13:40:54
249	SALE-46-REVENUE-20251125221403	SALE	46	REVENUE	فاتورة مبيعات #SAL20251125-0009	2025-11-25 22:14:03.828315	ILS	CUSTOMER	32	POSTED	2025-11-25 22:14:03	2025-11-25 22:14:03
250	PAYMENT-126-PAYMENT-20251125221428	PAYMENT	126	PAYMENT	قبض من عميل - PMT20251125-0005	2025-11-25 22:14:28.984518	ILS	CUSTOMER	32	POSTED	2025-11-25 22:14:28	2025-11-25 22:14:28
251	PAYMENT_SPLIT-65-PAYMENT-20251125221429	PAYMENT_SPLIT	65	PAYMENT	قبض نقد من عميل - Split #65 - PMT20251125-0005	2025-11-25 22:14:29.021684	ILS	CUSTOMER	32	POSTED	2025-11-25 22:14:29	2025-11-25 22:14:29
252	EXPENSE-45-ACCRUAL-20251125221806	EXPENSE	45	ACCRUAL	قيد مصروف #45	2025-11-25 22:18:06.019106	ILS	\N	\N	POSTED	2025-11-25 22:18:06	2025-11-25 22:18:06
253	EXPENSE-46-ACCRUAL-20251125221838	EXPENSE	46	ACCRUAL	قيد مصروف #46	2025-11-25 22:18:38.905018	ILS	\N	\N	POSTED	2025-11-25 22:18:38	2025-11-25 22:18:38
254	EXPENSE-47-ACCRUAL-20251125221935	EXPENSE	47	ACCRUAL	قيد مصروف #47	2025-11-25 22:19:35.68428	ILS	\N	\N	POSTED	2025-11-25 22:19:35	2025-11-25 22:19:35
255	SERVICE-5-SERVICE-20251128143634	SERVICE	5	SERVICE	صيانة - SRV-20251128143547	2025-11-28 14:36:34.746138	ILS	CUSTOMER	20	POSTED	2025-11-28 14:36:34	2025-11-28 14:36:34
256	PAYMENT-127-PAYMENT-20251128143733	PAYMENT	127	PAYMENT	قبض من عميل - PMT20251128-0001	2025-11-28 14:37:33.305752	ILS	CUSTOMER	20	POSTED	2025-11-28 14:37:33	2025-11-28 14:37:33
257	PAYMENT_SPLIT-66-PAYMENT-20251128143733	PAYMENT_SPLIT	66	PAYMENT	قبض نقد من عميل - Split #66 - PMT20251128-0001	2025-11-28 14:37:33.317947	ILS	CUSTOMER	20	POSTED	2025-11-28 14:37:33	2025-11-28 14:37:33
258	PAYMENT-128-PAYMENT-20251128144211	PAYMENT	128	PAYMENT	سداد لـ مورد - PMT20251128-0002	2025-11-28 14:42:11.281494	ILS	SUPPLIER	6	POSTED	2025-11-28 14:42:11	2025-11-28 14:42:11
259	SALE-47-REVENUE-20251128144534	SALE	47	REVENUE	فاتورة مبيعات #SAL20251128-0001	2025-11-28 14:45:34.722224	ILS	CUSTOMER	32	POSTED	2025-11-28 14:45:34	2025-11-28 14:45:34
260	PAYMENT-129-PAYMENT-20251128144553	PAYMENT	129	PAYMENT	قبض من عميل - PMT20251128-0003	2025-11-28 14:45:53.94757	ILS	CUSTOMER	32	POSTED	2025-11-28 14:45:53	2025-11-28 14:45:53
261	PAYMENT_SPLIT-67-PAYMENT-20251128144553	PAYMENT_SPLIT	67	PAYMENT	قبض نقد من عميل - Split #67 - PMT20251128-0003	2025-11-28 14:45:53.96128	ILS	CUSTOMER	32	POSTED	2025-11-28 14:45:53	2025-11-28 14:45:53
262	PAYMENT-130-PAYMENT-20251128144709	PAYMENT	130	PAYMENT	قبض من عميل - PMT20251128-0004	2025-11-28 14:47:09.233476	ILS	CUSTOMER	18	POSTED	2025-11-28 14:47:09	2025-11-28 14:47:09
263	PAYMENT_SPLIT-68-PAYMENT-20251128144709	PAYMENT_SPLIT	68	PAYMENT	قبض بنك من عميل - Split #68 - PMT20251128-0004	2025-11-28 14:47:09.238889	ILS	CUSTOMER	18	POSTED	2025-11-28 14:47:09	2025-11-28 14:47:09
264	EXPENSE-48-ACCRUAL-20251128145608	EXPENSE	48	ACCRUAL	قيد مصروف #48	2025-11-28 14:56:08.945076	ILS	\N	\N	POSTED	2025-11-28 14:56:08	2025-11-28 14:56:08
265	EXPENSE-49-ACCRUAL-20251128145704	EXPENSE	49	ACCRUAL	قيد مصروف #49	2025-11-28 14:57:04.097173	ILS	\N	\N	POSTED	2025-11-28 14:57:04	2025-11-28 14:57:04
266	SALE-48-REVENUE-20251128145939	SALE	48	REVENUE	فاتورة مبيعات #SAL20251128-0002	2025-11-28 14:59:39.715055	ILS	CUSTOMER	32	POSTED	2025-11-28 14:59:39	2025-11-28 14:59:39
267	PAYMENT-131-PAYMENT-20251128145954	PAYMENT	131	PAYMENT	قبض من عميل - PMT20251128-0005	2025-11-28 14:59:54.258298	ILS	CUSTOMER	32	POSTED	2025-11-28 14:59:54	2025-11-28 14:59:54
268	PAYMENT_SPLIT-69-PAYMENT-20251128145954	PAYMENT_SPLIT	69	PAYMENT	قبض نقد من عميل - Split #69 - PMT20251128-0005	2025-11-28 14:59:54.268223	ILS	CUSTOMER	32	POSTED	2025-11-28 14:59:54	2025-11-28 14:59:54
269	PAYMENT-132-PAYMENT-20251128150310	PAYMENT	132	PAYMENT	سداد لـ مورد - PMT20251128-0006	2025-11-28 15:03:10.85026	ILS	SUPPLIER	7	POSTED	2025-11-28 15:03:10	2025-11-28 15:03:10
270	PAYMENT_SPLIT-70-PAYMENT-20251128150310	PAYMENT_SPLIT	70	PAYMENT	سداد نقد لـ مورد - Split #70 - PMT20251128-0006	2025-11-28 15:03:10.870455	ILS	SUPPLIER	7	POSTED	2025-11-28 15:03:10	2025-11-28 15:03:10
271	EXPENSE-50-ACCRUAL-20251128152302	EXPENSE	50	ACCRUAL	قيد توريد خدمة #50	2025-11-28 15:23:02.144091	ILS	SUPPLIER	8	POSTED	2025-11-28 15:23:02	2025-11-28 15:23:02
272	PAYMENT-133-PAYMENT-20251128152310	PAYMENT	133	PAYMENT	سداد لـ مصروف - PMT20251128-0007	2025-11-28 15:23:10.066732	ILS	EXPENSE	50	POSTED	2025-11-28 15:23:10	2025-11-28 15:23:10
273	EXPENSE-51-ACCRUAL-20251128152427	EXPENSE	51	ACCRUAL	قيد مصروف #51	2025-11-28 15:24:27.58687	ILS	\N	\N	POSTED	2025-11-28 15:24:27	2025-11-28 15:24:27
274	EXPENSE-52-ACCRUAL-20251128153830	EXPENSE	52	ACCRUAL	قيد مصروف #52	2025-11-28 15:38:30.610815	ILS	\N	\N	POSTED	2025-11-28 15:38:30	2025-11-28 15:38:30
275	SALE-49-REVENUE-20251128153929	SALE	49	REVENUE	فاتورة مبيعات #SAL20251128-0003 - عميل	2025-11-28 15:39:29.419332	ILS	CUSTOMER	32	POSTED	2025-11-28 15:39:29	2025-11-28 15:39:29
276	PAYMENT-134-PAYMENT-20251128153950	PAYMENT	134	PAYMENT	قبض من عميل - PMT20251128-0008	2025-11-28 15:39:50.966052	ILS	CUSTOMER	32	POSTED	2025-11-28 15:39:50	2025-11-28 15:39:50
277	PAYMENT_SPLIT-71-PAYMENT-20251128153950	PAYMENT_SPLIT	71	PAYMENT	قبض نقد من عميل - Split #71 - PMT20251128-0008	2025-11-28 15:39:50.97211	ILS	CUSTOMER	32	POSTED	2025-11-28 15:39:50	2025-11-28 15:39:50
278	PAYMENT_SPLIT-6-PAYMENT-20251128215350	PAYMENT_SPLIT	6	PAYMENT	قبض بنك من عميل - Split #6 - PMT20251020-0001	2025-11-28 21:53:50.921155	ILS	CUSTOMER	2	POSTED	2025-11-28 21:53:50	2025-11-28 21:53:50
279	PAYMENT_SPLIT-1-PAYMENT-20251128215446	PAYMENT_SPLIT	1	PAYMENT	قبض بنك من عميل - Split #1 - PMT20251024-0001	2025-11-28 21:54:46.391957	ILS	CUSTOMER	2	POSTED	2025-11-28 21:54:46	2025-11-28 21:54:46
280	PAYMENT_SPLIT-7-PAYMENT-20251128215457	PAYMENT_SPLIT	7	PAYMENT	قبض بنك من عميل - Split #7 - PMT20251025-0002	2025-11-28 21:54:57.232706	ILS	CUSTOMER	2	POSTED	2025-11-28 21:54:57	2025-11-28 21:54:57
281	SALE-50-REVENUE-20251130073856	SALE	50	REVENUE	فاتورة مبيعات #SAL20251130-0001	2025-11-30 07:38:56.981878	ILS	CUSTOMER	32	POSTED	2025-11-30 07:38:56	2025-11-30 07:38:56
282	PAYMENT-136-PAYMENT-20251130073942	PAYMENT	136	PAYMENT	قبض من عميل - PMT20251130-0001	2025-11-30 07:39:42.787467	ILS	CUSTOMER	32	POSTED	2025-11-30 07:39:42	2025-11-30 07:39:42
283	PAYMENT_SPLIT-72-PAYMENT-20251130073942	PAYMENT_SPLIT	72	PAYMENT	قبض نقد من عميل - Split #72 - PMT20251130-0001	2025-11-30 07:39:42.805888	ILS	CUSTOMER	32	POSTED	2025-11-30 07:39:42	2025-11-30 07:39:42
284	SALE-51-REVENUE-20251130194646	SALE	51	REVENUE	فاتورة مبيعات #SAL20251130-0002	2025-11-30 19:46:46.713548	ILS	CUSTOMER	36	POSTED	2025-11-30 19:46:46	2025-11-30 19:46:46
285	PAYMENT-137-PAYMENT-20251130195252	PAYMENT	137	PAYMENT	قبض من عميل - PMT20251130-0002	2025-11-30 19:52:52.14217	ILS	CUSTOMER	12	POSTED	2025-11-30 19:52:52	2025-11-30 19:52:52
286	PAYMENT_SPLIT-73-PAYMENT-20251130195252	PAYMENT_SPLIT	73	PAYMENT	قبض نقد من عميل - Split #73 - PMT20251130-0002	2025-11-30 19:52:52.167109	ILS	CUSTOMER	12	POSTED	2025-11-30 19:52:52	2025-11-30 19:52:52
287	PAYMENT-138-PAYMENT-20251201140944	PAYMENT	138	PAYMENT	سداد لـ مورد - PMT20251201-0001	2025-12-01 14:09:44.064479	ILS	SUPPLIER	1	POSTED	2025-12-01 14:09:44	2025-12-01 14:09:44
288	PAYMENT_SPLIT-74-PAYMENT-20251201140944	PAYMENT_SPLIT	74	PAYMENT	سداد نقد لـ مورد - Split #74 - PMT20251201-0001	2025-12-01 14:09:44.082175	ILS	SUPPLIER	1	POSTED	2025-12-01 14:09:44	2025-12-01 14:09:44
289	EXPENSE-53-ACCRUAL-20251201141303	EXPENSE	53	ACCRUAL	قيد مصروف #53	2025-12-01 14:13:03.06337	ILS	\N	\N	POSTED	2025-12-01 14:13:03	2025-12-01 14:13:03
290	SALE-52-REVENUE-20251201141501	SALE	52	REVENUE	فاتورة مبيعات #SAL20251201-0001 - عميل	2025-12-01 14:15:01.482776	ILS	CUSTOMER	32	POSTED	2025-12-01 14:15:01	2025-12-01 14:15:01
291	PAYMENT-139-PAYMENT-20251201141620	PAYMENT	139	PAYMENT	قبض من عميل - PMT20251201-0002	2025-12-01 14:16:20.489171	ILS	CUSTOMER	32	POSTED	2025-12-01 14:16:20	2025-12-01 14:16:20
292	PAYMENT_SPLIT-75-PAYMENT-20251201141620	PAYMENT_SPLIT	75	PAYMENT	قبض نقد من عميل - Split #75 - PMT20251201-0002	2025-12-01 14:16:20.526937	ILS	CUSTOMER	32	POSTED	2025-12-01 14:16:20	2025-12-01 14:16:20
293	SALE-53-REVENUE-20251202204058	SALE	53	REVENUE	فاتورة مبيعات #SAL20251202-0001 - عميل	2025-12-02 20:40:58.563111	ILS	CUSTOMER	13	POSTED	2025-12-02 20:40:58	2025-12-02 20:40:58
294	SALE-54-REVENUE-20251202204221	SALE	54	REVENUE	فاتورة مبيعات #SAL20251202-0002	2025-12-02 20:42:21.564653	ILS	CUSTOMER	17	POSTED	2025-12-02 20:42:21	2025-12-02 20:42:21
295	PAYMENT-140-PAYMENT-20251202204238	PAYMENT	140	PAYMENT	قبض من عميل - PMT20251202-0001	2025-12-02 20:42:38.93018	ILS	CUSTOMER	17	POSTED	2025-12-02 20:42:38	2025-12-02 20:42:38
296	PAYMENT_SPLIT-76-PAYMENT-20251202204238	PAYMENT_SPLIT	76	PAYMENT	قبض نقد من عميل - Split #76 - PMT20251202-0001	2025-12-02 20:42:38.962781	ILS	CUSTOMER	17	POSTED	2025-12-02 20:42:38	2025-12-02 20:42:38
298	SALE-55-REVENUE-20251204224210	SALE	55	REVENUE	فاتورة مبيعات #SAL20251204-0001 - عميل	2025-12-04 22:42:10.681211	ILS	CUSTOMER	13	POSTED	2025-12-04 22:42:10	2025-12-04 22:42:10
299	SALE-56-REVENUE-20251204230537	SALE	56	REVENUE	فاتورة مبيعات #SAL20251204-0002 - عميل	2025-12-04 23:05:37.570941	ILS	CUSTOMER	34	POSTED	2025-12-04 23:05:37	2025-12-04 23:05:37
300	SERVICE-3-SERVICE-20251204233314	SERVICE	3	SERVICE	صيانة - SRV-20251110222022	2025-12-04 23:33:14.029805	ILS	CUSTOMER	18	POSTED	2025-12-04 23:33:14	2025-12-04 23:33:14
301	PAYMENT-141-PAYMENT-20251204233357	PAYMENT	141	PAYMENT	قبض من عميل - PMT20251204-0001	2025-12-04 23:33:57.108659	ILS	CUSTOMER	18	POSTED	2025-12-04 23:33:57	2025-12-04 23:33:57
302	PAYMENT_SPLIT-77-PAYMENT-20251204233357	PAYMENT_SPLIT	77	PAYMENT	قبض بنك من عميل - Split #77 - PMT20251204-0001	2025-12-04 23:33:57.115958	ILS	CUSTOMER	18	POSTED	2025-12-04 23:33:57	2025-12-04 23:33:57
303	SALE-57-REVENUE-20251205195244	SALE	57	REVENUE	فاتورة مبيعات #SAL20251205-0001 - عميل	2025-12-05 19:52:44.390879	ILS	CUSTOMER	14	POSTED	2025-12-05 19:52:44	2025-12-05 19:52:44
304	PAYMENT-142-PAYMENT-20251205200152	PAYMENT	142	PAYMENT	قبض من عميل - PMT20251205-0001	2025-12-05 20:01:52.973977	ILS	CUSTOMER	25	POSTED	2025-12-05 20:01:52	2025-12-05 20:01:52
305	PAYMENT_SPLIT-78-PAYMENT-20251205200152	PAYMENT_SPLIT	78	PAYMENT	قبض نقد من عميل - Split #78 - PMT20251205-0001	2025-12-05 20:01:52.986184	ILS	CUSTOMER	25	POSTED	2025-12-05 20:01:52	2025-12-05 20:01:52
306	PAYMENT-143-PAYMENT-20251207093517	PAYMENT	143	PAYMENT	قبض من عميل - PMT20251207-0001	2025-12-07 09:35:17.696584	ILS	CUSTOMER	2	POSTED	2025-12-07 09:35:17	2025-12-07 09:35:17
307	PAYMENT_SPLIT-79-PAYMENT-20251207093517	PAYMENT_SPLIT	79	PAYMENT	قبض نقد من عميل - Split #79 - PMT20251207-0001	2025-12-07 09:35:17.708735	ILS	CUSTOMER	2	POSTED	2025-12-07 09:35:17	2025-12-07 09:35:17
308	PAYMENT-144-PAYMENT-20251208231051	PAYMENT	144	PAYMENT	سداد لـ مورد - PMT20251208-0001	2025-12-08 23:10:51.246622	ILS	SUPPLIER	1	POSTED	2025-12-08 23:10:51	2025-12-08 23:10:51
309	PAYMENT_SPLIT-80-PAYMENT-20251208231051	PAYMENT_SPLIT	80	PAYMENT	سداد نقد لـ مورد - Split #80 - PMT20251208-0001	2025-12-08 23:10:51.258488	ILS	SUPPLIER	1	POSTED	2025-12-08 23:10:51	2025-12-08 23:10:51
310	SALE-58-REVENUE-20251208231519	SALE	58	REVENUE	فاتورة مبيعات #SAL20251208-0001 - عميل	2025-12-08 23:15:19.804167	ILS	CUSTOMER	13	POSTED	2025-12-08 23:15:19	2025-12-08 23:15:19
311	SALE-59-REVENUE-20251208231826	SALE	59	REVENUE	فاتورة مبيعات #SAL20251208-0002 - عميل	2025-12-08 23:18:26.301498	ILS	CUSTOMER	34	POSTED	2025-12-08 23:18:26	2025-12-08 23:18:26
312	SALE_RETURN-1-RETURN-20251208232446	SALE_RETURN	1	RETURN	مرتجع مبيعات - 1	2025-12-08 23:24:46.79487	ILS	CUSTOMER	18	POSTED	2025-12-08 23:24:46	2025-12-08 23:24:46
313	SALE_RETURN-2-RETURN-20251208232603	SALE_RETURN	2	RETURN	مرتجع مبيعات - 2	2025-12-08 23:26:03.136079	ILS	CUSTOMER	18	POSTED	2025-12-08 23:26:03	2025-12-08 23:26:03
314	EXPENSE_REVERSAL-23-REVERSAL-20251208233057	EXPENSE_REVERSAL	23	REVERSAL	عكس قيد - حذف مصروف #23 - ابو ناصر ونش	2025-12-08 23:30:57.965927	ILS	CUSTOMER	19	POSTED	2025-12-08 23:30:57	2025-12-08 23:30:57
315	SALE-60-REVENUE-20251209231601	SALE	60	REVENUE	فاتورة مبيعات #SAL20251209-0001	2025-12-09 23:16:01.094669	ILS	CUSTOMER	1	POSTED	2025-12-09 23:16:01	2025-12-09 23:16:01
316	PAYMENT-145-PAYMENT-20251209231625	PAYMENT	145	PAYMENT	قبض من عميل - PMT20251209-0001	2025-12-09 23:16:25.139143	ILS	CUSTOMER	1	POSTED	2025-12-09 23:16:25	2025-12-09 23:16:25
317	PAYMENT_SPLIT-81-PAYMENT-20251209231625	PAYMENT_SPLIT	81	PAYMENT	قبض نقد من عميل - Split #81 - PMT20251209-0001	2025-12-09 23:16:25.145851	ILS	CUSTOMER	1	POSTED	2025-12-09 23:16:25	2025-12-09 23:16:25
318	EXPENSE_REVERSAL-53-REVERSAL-20251214134350	EXPENSE_REVERSAL	53	REVERSAL	عكس قيد - حذف مصروف #53 - lwhvdt	2025-12-14 13:43:50.085014	ILS	OTHER	\N	POSTED	2025-12-14 13:43:50	2025-12-14 13:43:50
319	SALE-61-REVENUE-20251214140429	SALE	61	REVENUE	فاتورة مبيعات #SAL20251214-0001 - عميل	2025-12-14 14:04:29.983553	ILS	CUSTOMER	2	POSTED	2025-12-14 14:04:29	2025-12-14 14:04:29
320	SALE-62-REVENUE-20251214140706	SALE	62	REVENUE	فاتورة مبيعات #SAL20251214-0002 - عميل	2025-12-14 14:07:06.072726	ILS	CUSTOMER	2	POSTED	2025-12-14 14:07:06	2025-12-14 14:07:06
321	SUPPLIER-9-OPENING_BALANCE-20251214141032	SUPPLIER	9	OPENING_BALANCE	رصيد افتتاحي - حسن شهوان	2025-12-14 14:10:32.317567	ILS	SUPPLIER	9	POSTED	2025-12-14 14:10:32	2025-12-14 14:10:32
322	PAYMENT-146-PAYMENT-20251214141129	PAYMENT	146	PAYMENT	سداد لـ مورد - PMT20251214-0001	2025-12-14 14:11:29.321589	ILS	SUPPLIER	9	POSTED	2025-12-14 14:11:29	2025-12-14 14:11:29
323	PAYMENT_SPLIT-82-PAYMENT-20251214141129	PAYMENT_SPLIT	82	PAYMENT	سداد نقد لـ مورد - Split #82 - PMT20251214-0001	2025-12-14 14:11:29.328195	ILS	SUPPLIER	9	POSTED	2025-12-14 14:11:29	2025-12-14 14:11:29
324	PAYMENT-147-PAYMENT-20251216091102	PAYMENT	147	PAYMENT	قبض من عميل - PMT20251216-0001	2025-12-16 09:11:02.754198	ILS	CUSTOMER	1	POSTED	2025-12-16 09:11:02	2025-12-16 09:11:02
325	PAYMENT_SPLIT-83-PAYMENT-20251216091102	PAYMENT_SPLIT	83	PAYMENT	قبض نقد من عميل - Split #83 - PMT20251216-0001	2025-12-16 09:11:02.775608	ILS	CUSTOMER	1	POSTED	2025-12-16 09:11:02	2025-12-16 09:11:02
326	PAYMENT-148-PAYMENT-20251216091704	PAYMENT	148	PAYMENT	قبض من عميل - PMT20251216-0002	2025-12-16 09:17:04.656859	ILS	CUSTOMER	19	POSTED	2025-12-16 09:17:04	2025-12-16 09:17:04
327	PAYMENT_SPLIT-84-PAYMENT-20251216091704	PAYMENT_SPLIT	84	PAYMENT	قبض نقد من عميل - Split #84 - PMT20251216-0002	2025-12-16 09:17:04.670044	ILS	CUSTOMER	19	POSTED	2025-12-16 09:17:04	2025-12-16 09:17:04
\.


--
-- Data for Name: gl_entries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gl_entries (id, batch_id, account, debit, credit, currency, ref, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: import_runs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.import_runs (id, warehouse_id, user_id, filename, file_sha256, dry_run, inserted, updated, skipped, errors, duration_ms, report_path, notes, meta, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: invoice_lines; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.invoice_lines (id, invoice_id, description, quantity, unit_price, tax_rate, discount, product_id) FROM stdin;
\.


--
-- Data for Name: invoices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.invoices (id, invoice_number, invoice_date, due_date, customer_id, supplier_id, partner_id, sale_id, service_id, preorder_id, source, kind, credit_for_id, refund_of_id, currency, fx_rate_used, fx_rate_source, fx_rate_timestamp, fx_base_currency, fx_quote_currency, total_amount, tax_amount, discount_amount, notes, terms, refunded_total, idempotency_key, cancelled_at, cancelled_by, cancel_reason, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: notes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notes (id, content, author_id, entity_type, entity_id, is_pinned, priority, target_type, target_ids, notification_type, notification_date, is_sent, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: notification_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notification_logs (id, type, recipient, subject, content, status, provider_id, error_message, extra_data, sent_at, delivered_at, created_at, customer_id, user_id) FROM stdin;
\.


--
-- Data for Name: online_cart_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.online_cart_items (id, cart_id, product_id, quantity, price, added_at) FROM stdin;
\.


--
-- Data for Name: online_carts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.online_carts (id, cart_id, customer_id, session_id, status, expires_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: online_payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.online_payments (id, payment_ref, order_id, amount, currency, fx_rate_used, fx_rate_source, fx_rate_timestamp, fx_base_currency, fx_quote_currency, method, gateway, status, transaction_data, processed_at, card_last4, card_encrypted, card_expiry, cardholder_name, card_brand, card_fingerprint, payment_id, idempotency_key, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: online_preorder_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.online_preorder_items (id, order_id, product_id, quantity, price) FROM stdin;
\.


--
-- Data for Name: online_preorders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.online_preorders (id, order_number, customer_id, cart_id, warehouse_id, prepaid_amount, total_amount, base_amount, tax_rate, tax_amount, currency, fx_rate_used, fx_rate_source, fx_rate_timestamp, fx_base_currency, fx_quote_currency, expected_fulfillment, actual_fulfillment, status, payment_status, payment_method, notes, shipping_address, billing_address, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: partner_settlement_lines; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.partner_settlement_lines (id, settlement_id, source_type, source_id, description, product_id, warehouse_id, quantity, unit_price, gross_amount, share_percent, share_amount, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: partner_settlements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.partner_settlements (id, code, partner_id, from_date, to_date, currency, fx_rate_used, fx_rate_source, fx_rate_timestamp, fx_base_currency, fx_quote_currency, status, notes, total_gross, total_share, total_costs, total_due, previous_settlement_id, opening_balance, rights_inventory, rights_sales_share, rights_preorders, rights_total, obligations_sales_to_partner, obligations_services, obligations_damaged, obligations_expenses, obligations_returns, obligations_total, payments_out, payments_in, payments_net, closing_balance, is_approved, approved_by, approved_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: partners; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.partners (id, name, contact_info, identity_number, phone_number, email, address, share_percentage, currency, opening_balance, current_balance, inventory_balance, sales_share_balance, sales_to_partner_balance, service_fees_balance, preorders_to_partner_balance, preorders_prepaid_balance, damaged_items_balance, payments_in_balance, payments_out_balance, returned_checks_in_balance, returned_checks_out_balance, expenses_balance, service_expenses_balance, notes, customer_id, is_archived, archived_at, archived_by, archive_reason, created_at, updated_at) FROM stdin;
1	عمار النجار	\N	\N	0569099091	\N	رام الله بيتونيا	50.00	ILS	0.00	19900.00	0.00	25000.00	5100.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	\N	34	f	\N	\N	\N	2025-11-07 15:13:42	2025-12-10 16:51:23
\.


--
-- Data for Name: payment_splits; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payment_splits (id, payment_id, method, amount, details, currency, converted_amount, converted_currency, fx_rate_used, fx_rate_source, fx_rate_timestamp, fx_base_currency, fx_quote_currency) FROM stdin;
1	1	cheque	15000.00	"{\\"check_number\\": \\"0008\\", \\"check_bank\\": \\"\\\\u063a\\\\u064a\\\\u0631 \\", \\"check_due_date\\": \\"2025-07-25\\", \\"check_history\\": [{\\"timestamp\\": \\"2025-11-28T21:54:46.383108\\", \\"status\\": \\"CANCELLED\\", \\"user\\": \\"owner\\"}], \\"check_status\\": \\"CANCELLED\\", \\"check_note\\": \\"\\\\u062a\\\\u0645 \\\\u0625\\\\u0644\\\\u063a\\\\u0627\\\\u0621 \\\\u0627\\\\u0644\\\\u0634\\\\u064a\\\\u0643\\"}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
2	2	cash	2000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
4	4	cheque	4000.00	"{\\"check_number\\": \\"30000107\\", \\"check_bank\\": \\"\\\\u0628\\\\u0646\\\\u0643 \\\\u0641\\\\u0644\\\\u0633\\\\u0637\\\\u064a\\\\u0646\\", \\"check_due_date\\": \\"2026-02-12\\"}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
5	4	cheque	6000.00	"{\\"check_number\\": \\"30000007\\", \\"check_bank\\": \\"\\\\u0627\\\\u0644\\\\u0627\\\\u0633\\\\u0644\\\\u0627\\\\u0645\\\\u064a \\\\u0627\\\\u0644\\\\u0641\\\\u0644\\\\u0633\\\\u0637\\\\u064a\\\\u0646\\\\u064a\\", \\"check_due_date\\": \\"2026-01-25\\"}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
6	5	cheque	7500.00	"{\\"check_number\\": \\"30001609\\", \\"check_bank\\": \\"\\\\u0627\\\\u0644\\\\u0639\\\\u0642\\\\u0627\\\\u0631\\\\u064a \\\\u0627\\\\u0644\\\\u0645\\\\u0635\\\\u0631\\\\u064a \\\\u0627\\\\u0644\\\\u0639\\\\u0631\\\\u0628\\\\u064a\\", \\"check_due_date\\": \\"2025-10-31\\", \\"check_history\\": [{\\"timestamp\\": \\"2025-11-28T21:53:50.909234\\", \\"status\\": \\"CANCELLED\\", \\"user\\": \\"owner\\"}], \\"check_status\\": \\"CANCELLED\\", \\"check_note\\": \\"\\\\u062a\\\\u0645 \\\\u0625\\\\u0644\\\\u063a\\\\u0627\\\\u0621 \\\\u0627\\\\u0644\\\\u0634\\\\u064a\\\\u0643\\"}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
7	6	cheque	9000.00	"{\\"check_number\\": \\"123\\", \\"check_bank\\": \\"\\\\u062b\\\\u0644\\\\u0627\\\\u062b \\\\u0634\\\\u064a\\\\u0643\\\\u0627\\\\u062a \\\\u063a\\\\u064a\\\\u0631 \\\\u0645\\\\u0639\\\\u0631\\\\u0648\\\\u0641\\", \\"check_due_date\\": \\"2025-06-30\\", \\"check_history\\": [{\\"timestamp\\": \\"2025-11-28T21:54:57.222941\\", \\"status\\": \\"CANCELLED\\", \\"user\\": \\"owner\\"}], \\"check_status\\": \\"CANCELLED\\", \\"check_note\\": \\"\\\\u062a\\\\u0645 \\\\u0625\\\\u0644\\\\u063a\\\\u0627\\\\u0621 \\\\u0627\\\\u0644\\\\u0634\\\\u064a\\\\u0643\\"}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
8	7	cash	20000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
9	8	cash	20000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
10	9	cash	20000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
11	10	cash	20000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
13	12	cash	10000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
14	13	cash	20400.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
15	14	cash	5000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
16	16	cash	2500.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
17	17	cash	2700.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
18	18	cash	3000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
20	20	cash	2700.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
21	21	cash	3000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
22	22	cash	40000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
23	23	cash	5500.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
24	26	cash	50000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
25	27	cash	1400.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
26	28	cash	18500.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
27	29	cash	10000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
28	30	cash	13000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
29	31	cash	15000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
30	32	cash	25000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
31	33	cash	13000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
32	34	cash	10000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
33	35	card	10000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
34	38	cash	500.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
35	39	cash	2000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
36	40	cash	12500.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
37	41	cash	2000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
38	42	cash	2000.00	"{}"	ILS	0.00	ILS	\N	\N	\N	\N	\N
39	65	cash	9000.00	"{}"	ILS	9000.00	ILS	1.000000	same	2025-11-12 14:36:05.276825	ILS	ILS
40	66	cash	6000.00	"{}"	ILS	6000.00	ILS	1.000000	same	2025-11-12 17:39:57.778281	ILS	ILS
41	67	cash	20000.00	"{}"	ILS	20000.00	ILS	1.000000	same	2025-11-12 19:49:54.256296	ILS	ILS
42	69	cash	1000.00	"{}"	ILS	1000.00	ILS	1.000000	same	2025-11-12 20:44:52.601369	ILS	ILS
43	70	cash	1000.00	"{}"	ILS	1000.00	ILS	1.000000	same	2025-11-13 09:28:35.103404	ILS	ILS
46	72	bank	5500.00	"{\\"bank_transfer_ref\\": \\"ARAB BANK\\"}"	ILS	5500.00	ILS	1.000000	same	2025-11-13 12:09:14.850672	ILS	ILS
47	73	cash	1800.00	"{}"	ILS	1800.00	ILS	1.000000	same	2025-11-13 12:11:04.723561	ILS	ILS
48	74	cash	1300.00	"{}"	ILS	1300.00	ILS	1.000000	same	2025-11-13 12:13:24.169033	ILS	ILS
49	76	cash	5000.00	"{}"	ILS	5000.00	ILS	1.000000	same	2025-11-13 19:25:17.224368	ILS	ILS
50	77	cash	60000.00	"{}"	ILS	60000.00	ILS	1.000000	same	2025-11-14 20:45:51.508236	ILS	ILS
51	78	cash	60000.00	"{}"	ILS	60000.00	ILS	1.000000	same	2025-11-14 20:50:24.861063	ILS	ILS
54	112	cash	2700.00	"{}"	ILS	2700.00	ILS	1.000000	same	2025-11-16 20:01:16.96535	ILS	ILS
55	113	cash	250.00	"{}"	ILS	250.00	ILS	1.000000	same	2025-11-16 20:15:44.616211	ILS	ILS
56	114	cash	230.00	"{}"	ILS	230.00	ILS	1.000000	same	2025-11-16 20:17:12.664058	ILS	ILS
57	115	cash	750.00	"{}"	ILS	750.00	ILS	1.000000	same	2025-11-16 20:19:51.997286	ILS	ILS
58	119	cash	200.00	"{}"	ILS	200.00	ILS	1.000000	same	2025-11-17 15:08:01.264163	ILS	ILS
59	120	cash	270.00	"{}"	ILS	270.00	ILS	1.000000	same	2025-11-17 15:08:25.529601	ILS	ILS
60	121	cash	500.00	"{}"	ILS	500.00	ILS	1.000000	same	2025-11-18 16:28:10.138559	ILS	ILS
61	122	cash	80000.00	"{}"	ILS	80000.00	ILS	1.000000	same	2025-11-25 10:39:49.491118	ILS	ILS
62	123	cash	1800.00	"{}"	ILS	1800.00	ILS	1.000000	same	2025-11-25 10:53:32.945202	ILS	ILS
63	124	cash	5200.00	"{}"	ILS	5200.00	ILS	1.000000	same	2025-11-25 13:20:06.666531	ILS	ILS
64	125	cash	1800.00	"{}"	ILS	1800.00	ILS	1.000000	same	2025-11-25 13:40:54.199277	ILS	ILS
65	126	cash	1000.00	"{}"	ILS	1000.00	ILS	1.000000	same	2025-11-25 22:14:28.885034	ILS	ILS
66	127	cash	9400.00	"{}"	ILS	9400.00	ILS	1.000000	same	2025-11-28 14:37:33.261402	ILS	ILS
67	129	cash	450.00	"{}"	ILS	450.00	ILS	1.000000	same	2025-11-28 14:45:53.901282	ILS	ILS
68	130	bank	1500.00	"{\\"bank_transfer_ref\\": \\"\\\\u0646\\\\u0635\\\\u0631 \\\\u0628\\\\u0646\\\\u0643 \\\\u0641\\\\u0644\\\\u0633\\\\u0637\\\\u064a\\\\u0646\\"}"	ILS	1500.00	ILS	1.000000	same	2025-11-28 14:47:09.183608	ILS	ILS
69	131	cash	800.00	"{}"	ILS	800.00	ILS	1.000000	same	2025-11-28 14:59:54.225214	ILS	ILS
70	132	cash	800.00	"{}"	ILS	800.00	ILS	1.000000	same	2025-11-28 15:03:10.693131	ILS	ILS
71	134	cash	29000.00	"{}"	ILS	29000.00	ILS	1.000000	same	2025-11-28 15:39:50.934283	ILS	ILS
72	136	cash	1200.00	"{}"	ILS	1200.00	ILS	1.000000	same	2025-11-30 07:39:42.736183	ILS	ILS
73	137	cash	1300.00	"{}"	ILS	1300.00	ILS	1.000000	same	2025-11-30 19:52:52.082513	ILS	ILS
74	138	cash	9000.00	"{}"	ILS	9000.00	ILS	1.000000	same	2025-12-01 14:09:43.966165	ILS	ILS
75	139	cash	150.00	"{}"	ILS	150.00	ILS	1.000000	same	2025-12-01 14:16:20.364602	ILS	ILS
76	140	cash	1200.00	"{}"	ILS	1200.00	ILS	1.000000	same	2025-12-02 20:42:38.860803	ILS	ILS
77	141	bank	1000.00	"{\\"bank_transfer_ref\\": \\"4112025\\"}"	ILS	1000.00	ILS	1.000000	same	2025-12-04 23:33:57.076562	ILS	ILS
78	142	cash	4000.00	"{}"	ILS	4000.00	ILS	1.000000	same	2025-12-05 20:01:52.932241	ILS	ILS
79	143	cash	2000.00	"{}"	ILS	2000.00	ILS	1.000000	same	2025-12-07 09:35:17.660078	ILS	ILS
80	144	cash	5000.00	"{}"	ILS	5000.00	ILS	1.000000	same	2025-12-08 23:10:51.168594	ILS	ILS
81	145	cash	10000.00	"{}"	ILS	10000.00	ILS	1.000000	same	2025-12-09 23:16:25.100829	ILS	ILS
82	146	cash	61000.00	"{}"	ILS	61000.00	ILS	1.000000	same	2025-12-14 14:11:29.245243	ILS	ILS
83	147	cash	20000.00	"{}"	ILS	20000.00	ILS	1.000000	same	2025-12-16 09:11:02.686947	ILS	ILS
84	148	cash	2500.00	"{}"	ILS	2500.00	ILS	1.000000	same	2025-12-16 09:17:04.579429	ILS	ILS
\.


--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payments (id, payment_number, payment_date, subtotal, tax_rate, tax_amount, total_amount, currency, fx_rate_used, fx_rate_source, fx_rate_timestamp, fx_base_currency, fx_quote_currency, method, status, direction, entity_type, reference, receipt_number, notes, receiver_name, deliverer_name, check_number, check_bank, check_due_date, card_holder, card_expiry, card_last4, bank_transfer_ref, created_by, customer_id, supplier_id, partner_id, shipment_id, expense_id, loan_settlement_id, sale_id, invoice_id, preorder_id, service_id, refund_of_id, idempotency_key, is_archived, archived_at, archived_by, archive_reason, created_at, updated_at) FROM stdin;
1	PMT20251024-0001	2025-10-24 19:07:00	\N	\N	\N	15000.00	ILS	\N	\N	\N	\N	\N	cheque	COMPLETED	IN	CUSTOMER	دفعة واردة من اياد الغزاوي	\N	\n[2025-11-28 21:54:46] ⛔ Split #1 حالة الشيك: ملغي\n   💬 تم إلغاء الشيك\n   👤 owner\n   [STATE=CANCELLED]	owner	اياد الغزاوي	\N	غير محدد	2025-11-23 19:07:00	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	2	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-10-29 15:51:54	2025-11-28 21:54:46
2	PMT20251025-0001	2025-10-25 20:04:00	\N	\N	\N	2000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من اياد الغزاوي - SAL20251024-0001	\N	دفع مبيعة: SAL20251024-0001 - العميل: اياد الغزاوي	owner	اياد الغزاوي	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	2	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-10-29 15:51:54	2025-11-12 22:19:03
4	PMT20251011-0001	2025-10-11 20:30:00	\N	\N	\N	10000.00	ILS	\N	\N	\N	\N	\N	cheque	COMPLETED	IN	CUSTOMER	دفع مبيعة من اياد الغزاوي - SAL20251024-0001	\N	دفع مبيعة: SAL20251024-0001 - العميل: اياد الغزاوي	owner	اياد الغزاوي	\N	غير محدد	2025-11-10 20:30:00	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	2	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-10-29 15:51:54	2025-11-12 22:19:03
5	PMT20251020-0001	2025-10-20 20:34:00	\N	\N	\N	7500.00	ILS	\N	\N	\N	\N	\N	cheque	COMPLETED	IN	CUSTOMER	دفع مبيعة من اياد الغزاوي - SAL20251024-0001	\N	دفع مبيعة: SAL20251024-0001 - العميل: اياد الغزاوي\n[2025-11-28 21:53:50] ⛔ Split #6 حالة الشيك: ملغي\n   💬 تم إلغاء الشيك\n   👤 owner\n   [STATE=CANCELLED]	owner	اياد الغزاوي	\N	غير محدد	2025-11-19 20:34:00	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	2	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-10-29 15:51:54	2025-11-28 21:53:51
6	PMT20251025-0002	2025-10-25 20:43:00	\N	\N	\N	9000.00	ILS	\N	\N	\N	\N	\N	cheque	COMPLETED	IN	CUSTOMER	دفع مبيعة من اياد الغزاوي - SAL20251024-0001	\N	دفع مبيعة: SAL20251024-0001 - العميل: اياد الغزاوي\n[2025-11-28 21:54:57] ⛔ Split #7 حالة الشيك: ملغي\n   💬 تم إلغاء الشيك\n   👤 owner\n   [STATE=CANCELLED]	owner	اياد الغزاوي	\N	غير محدد	2025-11-24 20:43:00	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	2	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-10-29 15:51:54	2025-11-28 21:54:57
7	PMT20251003-0001	2025-10-03 20:55:00	\N	\N	\N	20000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من عامر ابو شخيدم - SAL20251023-0001	\N	دفع مبيعة: SAL20251023-0001 - العميل: عامر ابو شخيدم	owner	عامر ابو شخيدم	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-10-29 15:51:54	2025-11-12 22:19:03
8	PMT20250921-0001	2025-09-21 20:57:00	\N	\N	\N	20000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من عامر ابو شخيدم - SAL20251023-0001	\N	دفع مبيعة: SAL20251023-0001 - العميل: عامر ابو شخيدم	owner	عامر ابو شخيدم	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-10-29 15:51:54	2025-11-12 22:19:03
9	PMT20251023-0001	2025-10-23 20:59:00	\N	\N	\N	20000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من عامر ابو شخيدم - SAL20251023-0001	\N	دفع مبيعة: SAL20251023-0001 - العميل: عامر ابو شخيدم	owner	عامر ابو شخيدم	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-10-29 15:51:54	2025-11-12 22:19:03
10	PMT20250910-0001	2025-09-10 21:03:00	\N	\N	\N	20000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من عامر ابو شخيدم - SAL20251023-0001	\N	دفع مبيعة: SAL20251023-0001 - العميل: عامر ابو شخيدم	owner	عامر ابو شخيدم	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-10-29 15:51:54	2025-11-12 22:19:03
12	PMT20251028-0001	2025-10-28 23:39:00	\N	\N	\N	10000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من عامر ابو شخيدم - SAL20251023-0001	\N	دفع مبيعة: SAL20251023-0001 - العميل: عامر ابو شخيدم	owner	عامر ابو شخيدم	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-10-29 15:51:54	2025-11-12 22:19:03
13	PMT20251028-0002	2025-10-28 16:35:00	\N	\N	\N	20400.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من أحمد الصالحي	\N		owner	أحمد الصالحي	\N	\N	\N	\N	\N	\N	\N	1	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-10-29 16:37:02	2025-11-12 22:19:03
14	PMT20251029-0001	2025-10-29 16:47:00	\N	\N	\N	5000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من اياد الغزاوي	\N		owner	اياد الغزاوي	\N	\N	\N	\N	\N	\N	\N	1	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-10-29 16:48:52	2025-11-12 22:19:03
16	PMT20251029-0002	2025-10-29 18:18:00	\N	\N	\N	2500.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من يوسف ابو علي دورا - SAL20251029-0001	\N	دفع مبيعة: SAL20251029-0001 - العميل: يوسف ابو علي دورا	owner	يوسف ابو علي دورا	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	5	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-10-29 18:18:36	2025-11-12 22:19:03
17	PMT20251029-0003	2025-10-29 18:24:00	\N	\N	\N	2700.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من وليد قصراوي مضخات - SAL20251029-0003	\N	دفع مبيعة: SAL20251029-0003 - العميل: وليد قصراوي مضخات	owner	وليد قصراوي مضخات	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	7	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-10-29 18:24:43	2025-11-12 22:19:03
18	PMT20251029-0004	2025-10-29 20:34:00	\N	\N	\N	3000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من محمد سمير سبسطية - SAL20251029-0004	\N	دفع مبيعة: SAL20251029-0004 - العميل: محمد سمير سبسطية	owner	محمد سمير سبسطية	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	8	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-10-29 20:35:17	2025-11-12 22:19:03
20	PMT20251103-0001	2025-11-03 14:04:00	\N	\N	\N	2700.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من وليد قصراوي مضخات - SAL20251103-0001	\N	دفع مبيعة: SAL20251103-0001 - العميل: وليد قصراوي مضخات	owner	وليد قصراوي مضخات	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	9	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-03 14:05:02	2025-11-12 22:19:03
21	PMT20251104-0001	2025-11-04 12:14:00	\N	\N	\N	3000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من احمد ياسين طولكرم - SAL20251104-0001	\N	دفع مبيعة: SAL20251104-0001 - العميل: احمد ياسين طولكرم	owner	احمد ياسين طولكرم	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	10	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-04 12:14:51	2025-11-12 22:19:03
22	PMT20251104-0002	2025-11-04 12:34:00	\N	\N	\N	40000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من عارف القرناوي رهط - SAL20251104-0002	\N	دفع مبيعة: SAL20251104-0002 - العميل: عارف القرناوي رهط	owner	عارف القرناوي رهط	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	11	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-04 12:34:57	2025-11-12 22:19:03
23	PMT20251104-0003	2025-11-04 14:56:00	\N	\N	\N	5500.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من سميح عموري طولكرم - SAL20251104-0003	\N	دفع مبيعة: SAL20251104-0003 - العميل: سميح عموري طولكرم	owner	سميح عموري طولكرم	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	12	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-04 15:00:39	2025-11-12 22:19:03
26	PMT20251106-0001	2025-11-06 12:24:00	\N	\N	\N	50000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من عامر ابو شخيدم	\N		owner	عامر ابو شخيدم	\N	\N	\N	\N	\N	\N	\N	1	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-06 12:25:11	2025-11-12 22:19:03
27	PMT20251106-0002	2025-11-06 12:47:00	\N	\N	\N	1400.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من عامر ابو شخيدم - SAL20251106-0001	\N	دفع مبيعة: SAL20251106-0001 - العميل: عامر ابو شخيدم	owner	عامر ابو شخيدم	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	13	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-06 12:48:18	2025-11-12 22:19:03
28	PMT20251106-0003	2025-11-06 15:56:00	\N	\N	\N	18500.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	SUPPLIER	دفعة صادرة إلى ابراهيم قدح	\N	تحت الحساب	ابراهيم قدح	Owner	\N	\N	\N	\N	\N	\N	\N	1	\N	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-06 15:57:31	2025-11-12 22:19:03
29	PMT20230430-0001	2025-01-02 00:00:00	\N	\N	\N	10000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من محمد فارس	\N	بيد فراس	owner	محمد فارس	\N	\N	\N	\N	\N	\N	\N	1	14	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-07 15:56:44	2025-12-06 17:16:57
30	PMT20230507-0001	2025-01-03 00:00:00	\N	\N	\N	13000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من محمد فارس	\N	شكات عدد 3 تم صرفها	owner	محمد فارس	\N	\N	\N	\N	\N	\N	\N	1	14	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-07 15:59:35	2025-12-06 17:16:57
31	PMT20251107-0001	2025-11-07 16:01:00	\N	\N	\N	15000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من محمد فارس	\N	من شكات الرنج	owner	محمد فارس	\N	\N	\N	\N	\N	\N	\N	1	14	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-07 16:02:37	2025-11-12 22:19:03
32	PMT20240107-0001	2025-01-04 00:00:00	\N	\N	\N	25000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من محمد فارس	\N	شيكات عدد 3 بيد سمير	owner	محمد فارس	\N	\N	\N	\N	\N	\N	\N	1	14	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-07 16:05:13	2025-12-06 17:16:57
33	PMT20240207-0001	2025-01-05 00:00:00	\N	\N	\N	13000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من محمد فارس	\N	بيد فراس في المحل	owner	محمد فارس	\N	\N	\N	\N	\N	\N	\N	1	14	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-07 16:07:13	2025-12-06 17:16:57
34	PMT20240605-0001	2025-01-06 00:00:00	\N	\N	\N	10000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من محمد فارس	\N	من فراس بيد فرسان في المحل	owner	محمد فارس	\N	\N	\N	\N	\N	\N	\N	1	14	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-07 16:09:11	2025-12-06 17:16:57
35	PMT20251107-0002	2025-11-07 16:09:00	\N	\N	\N	10000.00	ILS	\N	\N	\N	\N	\N	card	COMPLETED	IN	CUSTOMER	دفعة واردة من محمد فارس	\N	بيد ابو فارس	owner	محمد فارس	\N	\N	\N	\N	\N	\N	\N	1	14	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-07 16:10:44	2025-11-12 22:19:03
38	PMT20251109-0001	2025-11-09 20:47:00	\N	\N	\N	500.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من عدنان السلامين - SAL20251109-0001	\N	دفع مبيعة: SAL20251109-0001 - العميل: عدنان السلامين	owner	عدنان السلامين	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	22	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-09 20:47:31	2025-11-12 22:19:03
39	PMT20251109-0002	2025-11-09 20:59:00	\N	\N	\N	2000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع صيانة من قنديل للاسفلت والتعهدات العامة - SRV-20251109205633	\N	دفع طلب صيانة: SRV-20251109205633 - العميل: قنديل للاسفلت والتعهدات العامة - المركبة: غير محدد دفعة من محمد فادي	owner	قنديل للاسفلت والتعهدات العامة	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2	\N	\N	f	\N	\N	\N	2025-11-09 20:59:56	2025-11-12 22:19:03
40	PMT20251109-0003	2025-11-09 21:56:00	\N	\N	\N	12500.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من ابو ناصر ونش - SAL20251109-0003	\N	دفع مبيعة: SAL20251109-0003 - العميل: ابو ناصر ونش	owner	ابو ناصر ونش	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	24	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-09 21:56:51	2025-11-12 22:19:03
41	PMT20251110-0001	2025-11-10 12:33:00	\N	\N	\N	2000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من فيصل الجمل - SAL20251110-0001	\N	دفع مبيعة: SAL20251110-0001 - العميل: فيصل الجمل	owner	فيصل الجمل	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	27	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-10 12:33:51	2025-11-12 22:19:03
42	PMT20251110-0002	2025-11-10 22:42:00	\N	\N	\N	2000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	CUSTOMER	\N	\N	دين لسامي بيد الشوفير	سامي كمال الطميزي	Owner	\N	\N	\N	\N	\N	\N	\N	1	22	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-10 22:43:47	2025-11-12 22:19:03
65	PMT20251112-0001	2025-11-12 14:35:00	\N	\N	\N	9000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من طرمبة جرافة فولفو	\N		owner	طرمبة جرافة فولفو	\N	\N	\N	\N	\N	\N	\N	1	24	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-12 14:36:05	2025-11-12 22:19:03
66	PMT20251112-0002	2025-11-12 17:39:00	\N	\N	\N	6000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من فادي غيث	\N	باقي له ماتور	owner	فادي غيث	\N	\N	\N	\N	\N	\N	\N	1	25	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-12 17:39:57	2025-11-12 22:19:03
67	PMT20251112-0003	2025-11-12 19:48:00	\N	\N	\N	20000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من شركة اتكو الهندسية	\N	دفعة تحت الحساب من رامي	owner	شركة اتكو الهندسية	\N	\N	\N	\N	\N	\N	\N	1	26	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-12 19:49:54	2025-11-12 22:19:03
69	PMT20251112-0004	2025-11-12 20:44:00	\N	\N	\N	1000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	SUPPLIER	دفعة صادرة إلى ابراهيم قدح	\N		ابراهيم قدح	Owner	\N	\N	\N	\N	\N	\N	\N	1	\N	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-12 20:44:52	2025-11-12 22:19:03
70	PMT20251113-0001	2025-11-13 09:26:00	\N	\N	\N	1000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع صيانة من قنديل للاسفلت والتعهدات العامة - SRV-20251109205633	\N	دفع طلب صيانة: SRV-20251109205633 - العميل: قنديل للاسفلت والتعهدات العامة - المركبة: غير محدد\n[2025-11-18 16:27:24] ⟲ Split #44 حالة الشيك: مرتجع\n   💬 تم إرجاع الشيك من البنك\n   👤 owner\n   [STATE=RETURNED]\n[SETTLED=true] تم تسوية الشيك مرتجع عن طريق دفع بديل	naser sameer	محمد فادي	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2	\N	\N	f	\N	\N	\N	2025-11-13 09:28:35	2025-12-06 17:21:20
72	PMT20251113-0003	2025-11-13 12:07:00	\N	\N	\N	5500.00	ILS	\N	\N	\N	\N	\N	bank	COMPLETED	IN	CUSTOMER	دفعة واردة من احمد ابو رزق جماعين	\N	تحويل لحساب نصر 	owner	احمد ابو رزق جماعين	\N	\N	\N	\N	\N	\N	\N	1	27	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-13 12:09:14	2025-11-13 12:09:14
73	PMT20251113-0004	2025-11-13 12:09:00	\N	\N	\N	1800.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	CUSTOMER	دفعة صادرة إلى احمد ابو رزق جماعين	\N	باقي له 200 لان ثمن المحرك 3500 شيقل	احمد	نصر	\N	\N	\N	\N	\N	\N	\N	1	27	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-13 12:11:04	2025-11-13 12:11:04
74	PMT20251113-0005	2025-11-13 12:13:00	\N	\N	\N	1300.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من علي حنيحن	\N		naser sameer	علي حنيحن	\N	\N	\N	\N	\N	\N	\N	1	23	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-13 12:13:24	2025-11-13 12:13:24
76	PMT20251113-0006	2025-11-13 19:24:00	\N	\N	\N	5000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع صيانة من محمد نعيم - SRV-20251031211614	\N	دفع طلب صيانة: SRV-20251031211614 - العميل: محمد نعيم - المركبة: 2020	نصر	نفسه	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	f	\N	\N	\N	2025-11-13 19:25:17	2025-11-13 19:25:17
77	PMT20251114-0001	2025-11-14 20:45:00	\N	\N	\N	60000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من عامر ابو شخيدم	\N		مراد المحسيري	عامر	\N	\N	\N	\N	\N	\N	\N	1	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-14 20:45:51	2025-11-14 20:45:51
78	PMT20251114-0002	2025-11-14 20:48:00	\N	\N	\N	60000.00	ILS	\N	\N	\N	\N	\N	cash	REFUNDED	OUT	SUPPLIER	دفعة صادرة إلى مراد المحسيري	\N	ثمن باجر 2013 jcb	مراد المحسيري	عامر ابو شخيدم	\N	\N	\N	\N	\N	\N	\N	1	\N	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-14 20:50:24	2025-11-15 13:09:50
81	PMT20251115-0003	2025-11-15 13:06:16.630451	\N	\N	\N	60000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	SUPPLIER	\N	\N	دفعة مقدمة عند استلام 1 قطعة - باجر 3cx jcb 2013	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-15 13:06:16	2025-11-15 13:06:16
82	PMT20251116-0001	2025-11-16 02:07:32.408125	\N	\N	\N	12500.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
83	PMT20251116-0002	2025-11-16 02:07:32.42582	\N	\N	\N	1000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-2	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
84	PMT20251116-0003	2025-11-16 02:07:32.432251	\N	\N	\N	4000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-3	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	3	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
85	PMT20251116-0004	2025-11-16 02:07:32.44251	\N	\N	\N	400.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-7	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	7	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
86	PMT20251116-0005	2025-11-16 02:07:32.449731	\N	\N	\N	300.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-8	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	8	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
87	PMT20251116-0006	2025-11-16 02:07:32.457349	\N	\N	\N	400.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-9	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	9	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
88	PMT20251116-0007	2025-11-16 02:07:32.466174	\N	\N	\N	400.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-10	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	10	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
89	PMT20251116-0008	2025-11-16 02:07:32.473662	\N	\N	\N	400.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-11	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	11	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
90	PMT20251116-0009	2025-11-16 02:07:32.481981	\N	\N	\N	500.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-12	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	12	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
91	PMT20251116-0010	2025-11-16 02:07:32.490607	\N	\N	\N	900.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-13	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	13	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
92	PMT20251116-0011	2025-11-16 02:07:32.501367	\N	\N	\N	200.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-14	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	14	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
93	PMT20251116-0012	2025-11-16 02:07:32.509961	\N	\N	\N	500.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-15	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	15	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
94	PMT20251116-0013	2025-11-16 02:07:32.516434	\N	\N	\N	66000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-16	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	16	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
95	PMT20251116-0014	2025-11-16 02:07:32.523576	\N	\N	\N	250.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-17	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	17	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
96	PMT20251116-0015	2025-11-16 02:07:32.532278	\N	\N	\N	1000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-18	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	18	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
97	PMT20251116-0016	2025-11-16 02:07:32.539941	\N	\N	\N	150.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-19	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	19	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
98	PMT20251116-0017	2025-11-16 02:07:32.548805	\N	\N	\N	600.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-20	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	20	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
99	PMT20251116-0018	2025-11-16 02:07:32.557993	\N	\N	\N	6000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-21	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	21	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
100	PMT20251116-0019	2025-11-16 02:07:32.56672	\N	\N	\N	230.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-22	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	22	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
102	PMT20251116-0021	2025-11-16 02:07:32.583854	\N	\N	\N	320.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-25	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	25	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
103	PMT20251116-0022	2025-11-16 02:07:32.592176	\N	\N	\N	2500.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-26	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	26	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
104	PMT20251116-0023	2025-11-16 02:07:32.599453	\N	\N	\N	100.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-27	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	27	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
105	PMT20251116-0024	2025-11-16 02:07:32.608284	\N	\N	\N	2194.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-28	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	28	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
106	PMT20251116-0025	2025-11-16 02:07:32.618756	\N	\N	\N	400.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-29	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	29	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
107	PMT20251116-0026	2025-11-16 02:07:32.629015	\N	\N	\N	400.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-30	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	30	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
108	PMT20251116-0027	2025-11-16 02:07:32.634719	\N	\N	\N	200.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-31	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	31	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
109	PMT20251116-0028	2025-11-16 02:07:32.642808	\N	\N	\N	400.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-32	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	32	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
110	PMT20251116-0029	2025-11-16 02:07:32.64968	\N	\N	\N	500.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	AUTO-EXP-33	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	33	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 02:07:32	2025-11-16 02:07:32
111	PMT20251116-0030	2025-11-16 19:32:03.667014	\N	\N	\N	4500.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	SUPPLIER	\N	\N	دفعة مقدمة عند استلام 1 قطعة - مزليك نيسان 2.5 طن قديم	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 19:32:03	2025-11-16 19:32:03
112	PMT20251116-0031	2025-11-16 19:56:00	\N	\N	\N	2700.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من ادهم قطام - SAL20251113-0002	\N	دفع مبيعة: SAL20251113-0002 - العميل: ادهم قطام	جهاد	تكسي	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	32	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 20:01:17	2025-11-16 20:01:17
113	PMT20251116-0032	2025-11-16 20:15:00	\N	\N	\N	250.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من طوب شاهين - SAL20251116-0001	\N	دفع مبيعة: SAL20251116-0001 - العميل: طوب شاهين	جهاد	الشيخ	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	33	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 20:15:44	2025-11-16 20:15:44
114	PMT20251116-0033	2025-11-16 20:16:00	\N	\N	\N	230.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من ونشات رام الله - SAL20251116-0002	\N	دفع مبيعة: SAL20251116-0002 - العميل: ونشات رام الله	owner	ونشات رام الله	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	34	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 20:17:12	2025-11-16 20:17:12
115	PMT20251116-0034	2025-11-16 20:19:00	\N	\N	\N	750.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من مجهول - SAL20251116-0003	\N	دفع مبيعة: SAL20251116-0003 - العميل: مجهول	براء	مجهول	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	35	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 20:19:52	2025-11-16 20:19:52
117	PMT20251116-0035	2025-11-16 20:48:31.962524	\N	\N	\N	32000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE		\N		اسماعيل ابو خلف	\N	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	42	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-16 20:48:31	2025-11-16 20:48:31
119	PMT20251117-0001	2025-11-17 15:07:00	\N	\N	\N	200.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من مجهول - SAL20251117-0002	\N	دفع مبيعة: SAL20251117-0002 - العميل: مجهول	naser sameer	مجهول	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	37	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-17 15:08:01	2025-11-17 15:08:01
120	PMT20251117-0002	2025-11-17 15:08:00	\N	\N	\N	270.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من مجهول - SAL20251117-0001	\N	دفع مبيعة: SAL20251117-0001 - العميل: مجهول	naser sameer	مجهول	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	36	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-17 15:08:25	2025-11-17 15:08:25
121	PMT20251118-0001	2025-11-18 16:27:00	\N	\N	\N	500.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	CHK-SETTLE-30000047	\N	تسوية شيك مرتجع رقم 30000047	naser sameer	محمد فادي	\N	\N	\N	\N	\N	\N	\N	1	18	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-18 16:28:10	2025-11-18 16:28:10
122	PMT20251125-0001	2025-11-25 10:39:00	\N	\N	\N	80000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من عامر ابو شخيدم	\N		جهاد	عامر	\N	\N	\N	\N	\N	\N	\N	1	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-25 10:39:49	2025-11-25 10:39:49
123	PMT20251125-0002	2025-11-25 10:53:00	\N	\N	\N	1800.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع صيانة من قنديل للاسفلت والتعهدات العامة - SRV-20251125105207	\N	دفع طلب صيانة: SRV-20251125105207 - العميل: قنديل للاسفلت والتعهدات العامة - المركبة: غير محدد	نصر	محمد فادي	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	4	\N	\N	f	\N	\N	\N	2025-11-25 10:53:33	2025-11-25 10:53:33
124	PMT20251125-0003	2025-11-25 13:19:00	\N	\N	\N	5200.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من موسى الخيري - SAL20251125-0004	\N	دفع مبيعة: SAL20251125-0004 - العميل: موسى الخيري	نصر	موسى	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	41	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-25 13:20:06	2025-11-25 13:20:06
125	PMT20251125-0004	2025-11-25 13:40:00	\N	\N	\N	1800.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من احمد ابو رزق جماعين - SAL20251125-0008	\N	دفع مبيعة: SAL20251125-0008 - العميل: احمد ابو رزق جماعين	naser sameer	احمد	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	45	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-25 13:40:54	2025-11-25 13:40:54
126	PMT20251125-0005	2025-11-25 22:14:00	\N	\N	\N	1000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من مجهول - SAL20251125-0009	\N	دفع مبيعة: SAL20251125-0009 - العميل: مجهول	owner	مجهول	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	46	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-25 22:14:28	2025-11-25 22:14:28
127	PMT20251128-0001	2025-11-28 14:36:00	\N	\N	\N	9400.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع صيانة من زهران ابو ربحي - SRV-20251128143547	\N	دفع طلب صيانة: SRV-20251128143547 - العميل: زهران ابو ربحي - المركبة: غير محدد	جهاد	زهران	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	5	\N	\N	f	\N	\N	\N	2025-11-28 14:37:33	2025-11-28 14:37:33
128	PMT20251128-0002	2025-11-28 14:42:11.004372	\N	\N	\N	6500.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	SUPPLIER	\N	\N	دفعة مقدمة عند استلام 1 قطعة - كيتور ديزل كبير	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	6	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-28 14:42:11	2025-11-28 14:42:11
129	PMT20251128-0003	2025-11-28 14:45:00	\N	\N	\N	450.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من مجهول - SAL20251128-0001	\N	دفع مبيعة: SAL20251128-0001 - العميل: مجهول	naser sameer	مجهول	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	47	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-28 14:45:53	2025-11-28 14:45:53
130	PMT20251128-0004	2025-11-28 14:46:00	\N	\N	\N	1500.00	ILS	\N	\N	\N	\N	\N	bank	COMPLETED	IN	CUSTOMER	دفعة واردة من قنديل للاسفلت والتعهدات العامة	\N		نصر	محمد فادي	\N	\N	\N	\N	\N	\N	\N	1	18	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-28 14:47:09	2025-11-28 14:47:09
131	PMT20251128-0005	2025-11-28 14:59:00	\N	\N	\N	800.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من مجهول - SAL20251128-0002	\N	دفع مبيعة: SAL20251128-0002 - العميل: مجهول	owner	مجهول	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	48	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-28 14:59:54	2025-11-28 14:59:54
132	PMT20251128-0006	2025-11-28 15:02:00	\N	\N	\N	800.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	SUPPLIER	دفعة صادرة إلى بهاء حسونة	\N		بهاء حسونة	owner	\N	\N	\N	\N	\N	\N	\N	1	\N	7	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-28 15:03:10	2025-11-28 15:03:10
133	PMT20251128-0007	2025-11-28 15:23:09.989769	\N	\N	\N	3500.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	EXPENSE	مصروف #50 - كسكيت 2012 عدد10	\N	كسكيت 2012 عدد10	ايلي مراد قطع	\N	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	50	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-28 15:23:10	2025-11-28 15:23:10
134	PMT20251128-0008	2025-11-28 15:39:00	\N	\N	\N	29000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من مجهول - SAL20251128-0003	\N	دفع مبيعة: SAL20251128-0003 - العميل: مجهول	owner	مجهول	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	49	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-28 15:39:50	2025-11-28 15:39:50
135	PMT-MIG-135	2025-10-26 00:00:00	\N	\N	\N	5000.00	ILS	\N	\N	\N	\N	\N	cheque	COMPLETED	IN	CUSTOMER	\N	\N	\N	\N	\N	30000449	الاستثمار الفلسطيني	\N	\N	\N	\N	\N	\N	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-10-26 00:00:00	2025-10-26 00:00:00
136	PMT20251130-0001	2025-11-30 07:39:00	\N	\N	\N	1200.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من مجهول - SAL20251130-0001	\N	دفع مبيعة: SAL20251130-0001 - العميل: مجهول	naser sameer	مجهول	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	50	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-30 07:39:42	2025-11-30 07:39:42
137	PMT20251130-0002	2025-11-30 19:51:00	\N	\N	\N	1300.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من فريد ابو اياد الطوري	\N	دفعة بدل شحن كمبيوتر من دبي	naser sameer	فريد	\N	\N	\N	\N	\N	\N	\N	1	12	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-11-30 19:52:52	2025-11-30 19:52:52
138	PMT20251201-0001	2025-12-01 14:09:00	\N	\N	\N	9000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	SUPPLIER	دفعة صادرة إلى ابراهيم قدح	\N		ابراهيم قدح	owner	\N	\N	\N	\N	\N	\N	\N	1	\N	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-12-01 14:09:44	2025-12-01 14:09:44
139	PMT20251201-0002	2025-12-01 14:16:00	\N	\N	\N	150.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من مجهول - SAL20251201-0001	\N	دفع مبيعة: SAL20251201-0001 - العميل: مجهول	owner	مجهول	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	52	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-12-01 14:16:20	2025-12-01 14:16:20
140	PMT20251202-0001	2025-12-02 20:42:00	\N	\N	\N	1200.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من عدنان السلامين - SAL20251202-0002	\N	دفع مبيعة: SAL20251202-0002 - العميل: عدنان السلامين	naser sameer	عدنان السلامين	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	54	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-12-02 20:42:38	2025-12-02 20:42:38
141	PMT20251204-0001	2025-12-04 23:33:00	\N	\N	\N	1000.00	ILS	\N	\N	\N	\N	\N	bank	COMPLETED	IN	CUSTOMER	دفع صيانة من قنديل للاسفلت والتعهدات العامة - SRV-20251110222022	\N	دفع طلب صيانة: SRV-20251110222022 - العميل: قنديل للاسفلت والتعهدات العامة - المركبة: غير محدد	owner	قنديل للاسفلت والتعهدات العامة	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	3	\N	\N	f	\N	\N	\N	2025-12-04 23:33:57	2025-12-04 23:33:57
142	PMT20251205-0001	2025-12-05 20:01:00	\N	\N	\N	4000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من فادي غيث - SAL20251112-0003	\N	دفع مبيعة: SAL20251112-0003 - العميل: فادي غيث	owner	فادي غيث	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	30	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-12-05 20:01:52	2025-12-05 20:01:52
143	PMT20251207-0001	2025-12-07 09:34:00	\N	\N	\N	2000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من اياد الغزاوي	\N		جهاد	اياد	\N	\N	\N	\N	\N	\N	\N	1	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-12-07 09:35:17	2025-12-07 09:35:17
144	PMT20251208-0001	2025-12-08 23:10:00	\N	\N	\N	5000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	SUPPLIER	دفعة صادرة إلى ابراهيم قدح	\N		ابراهيم قدح	owner	\N	\N	\N	\N	\N	\N	\N	1	\N	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-12-08 23:10:51	2025-12-08 23:10:51
145	PMT20251209-0001	2025-12-09 23:16:00	\N	\N	\N	10000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفع مبيعة من عامر ابو شخيدم - SAL20251209-0001	\N	دفع مبيعة: SAL20251209-0001 - العميل: عامر ابو شخيدم	naser sameer	شوفير	\N	\N	\N	\N	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	60	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-12-09 23:16:25	2025-12-09 23:16:25
146	PMT20251214-0001	2025-12-14 14:10:00	\N	\N	\N	61000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	OUT	SUPPLIER	دفعة صادرة إلى حسن شهوان	\N		حسن	owner	\N	\N	\N	\N	\N	\N	\N	1	\N	9	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-12-14 14:11:29	2025-12-14 14:11:29
147	PMT20251216-0001	2025-12-16 09:09:00	\N	\N	\N	20000.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من عامر ابو شخيدم	\N	سلمت ل صائب ابو سنينة من ثمن مزليكات	صائب طه	عامر	\N	\N	\N	\N	\N	\N	\N	1	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-12-16 09:11:02	2025-12-16 09:11:02
148	PMT20251216-0002	2025-12-16 09:16:00	\N	\N	\N	2500.00	ILS	\N	\N	\N	\N	\N	cash	COMPLETED	IN	CUSTOMER	دفعة واردة من ابو ناصر ونش	\N	رفع حاوية 	رفع حاوية	ابو ناصر ونش	\N	\N	\N	\N	\N	\N	\N	1	19	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	2025-12-16 09:17:04	2025-12-16 09:17:04
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permissions (id, name, code, description, name_ar, module, is_protected, aliases) FROM stdin;
1	access_ai_assistant	access_ai_assistant	استخدام المساعد الذكي	الوصول للمساعد الذكي	ai	t	[]
2	access_owner_dashboard	access_owner_dashboard	الوصول للوحة التحكم الخاصة بالمالك	الوصول للوحة المالك	owner_only	t	[]
3	backup_database	backup_database	إنشاء نسخة احتياطية من قاعدة البيانات	نسخ احتياطي للنظام	system	t	[]
4	hard_delete	hard_delete	حذف نهائي من قاعدة البيانات	حذف قوي	system	t	[]
5	manage_advanced_accounting	manage_advanced_accounting	الوصول لوحدات المحاسبة المتقدمة	إدارة المحاسبة المتقدمة	owner_only	t	[]
6	manage_any_user_permissions	manage_any_user_permissions	إضافة وتعديل وحذف صلاحيات أي مستخدم	إدارة صلاحيات أي مستخدم	owner_only	t	[]
7	manage_ledger	manage_ledger	التحكم الكامل بالدفتر العام	إدارة الدفتر	owner_only	t	[]
8	manage_permissions	manage_permissions	إضافة وتعديل وحذف الصلاحيات	إدارة الصلاحيات	users	t	[]
9	manage_roles	manage_roles	إضافة وتعديل وحذف أدوار المستخدمين	إدارة الأدوار	users	t	[]
10	manage_users	manage_users	إضافة وتعديل وحذف المستخدمين	إدارة المستخدمين	users	t	[]
11	restore_database	restore_database	استعادة قاعدة البيانات من نسخة احتياطية	استعادة نسخة احتياطية	system	t	[]
12	train_ai	train_ai	تدريب وإدارة المساعد الذكي	تدريب المساعد الذكي	ai	t	[]
13	view_audit_logs	view_audit_logs	عرض كل سجلات النظام	عرض سجلات التدقيق	system	t	[]
14	access_api	access_api	الوصول لواجهة API	الوصول إلى API	other	f	[]
15	add_customer	add_customer	إضافة عميل جديد	إضافة عميل	customers	f	[]
16	add_partner	add_partner	إضافة شريك جديد	إضافة شريك	vendors	f	[]
17	add_preorder	add_preorder	إضافة طلب مسبق	إضافة طلب مسبق	shop	f	[]
18	add_supplier	add_supplier	إضافة مورد جديد	إضافة مورد	vendors	f	[]
19	browse_products	browse_products	تصفح منتجات المتجر	تصفح المنتجات	shop	f	[]
20	delete_preorder	delete_preorder	حذف طلب مسبق	حذف طلب مسبق	shop	f	[]
21	edit_preorder	edit_preorder	تعديل طلب مسبق	تعديل طلب مسبق	shop	f	[]
22	manage_api	manage_api	إدارة واجهة API	إدارة API	other	f	[]
23	manage_barcode	manage_barcode	إدارة الباركود	إدارة الباركود	other	f	[]
24	manage_currencies	manage_currencies	إدارة العملات وأسعار الصرف	إدارة العملات	accounting	f	[]
25	manage_customers	manage_customers	إدارة كاملة للعملاء	إدارة العملاء	customers	f	[]
26	manage_exchange	manage_exchange	إدارة تحويلات العملات	إدارة التحويلات	accounting	f	[]
27	manage_expenses	manage_expenses	إدارة المصاريف والرواتب	إدارة المصاريف	accounting	f	[]
28	manage_inventory	manage_inventory	إدارة جرد المخزون	إدارة الجرد	warehouses	f	[]
29	manage_notes	manage_notes	إضافة وتعديل الملاحظات	إدارة الملاحظات	other	f	[]
30	manage_payments	manage_payments	إدارة المدفوعات والسندات	إدارة المدفوعات	accounting	f	[]
31	manage_reports	manage_reports	إنشاء وتعديل التقارير	إدارة التقارير	accounting	f	[]
32	manage_sales	manage_sales	إدارة كاملة للمبيعات	إدارة المبيعات	sales	f	[]
33	manage_service	manage_service	إدارة كاملة لطلبات الصيانة	إدارة الصيانة	service	f	[]
34	manage_shipments	manage_shipments	إدارة الشحنات والتوصيل	إدارة الشحن	shipments	f	[]
35	manage_shop	manage_shop	إدارة المتجر الإلكتروني	إدارة المتجر	shop	f	[]
36	manage_vendors	manage_vendors	إدارة الموردين والشركاء	إدارة الموردين	vendors	f	[]
37	manage_warehouses	manage_warehouses	إدارة كاملة للمستودعات	إدارة المستودعات	warehouses	f	[]
38	place_online_order	place_online_order	إنشاء طلب من المتجر	طلب أونلاين	shop	f	[]
39	view_barcode	view_barcode	عرض الباركود	عرض الباركود	other	f	[]
40	view_customers	view_customers	عرض قائمة العملاء	عرض العملاء	customers	f	[]
41	view_inventory	view_inventory	عرض جرد المخزون	عرض الجرد	warehouses	f	[]
42	view_notes	view_notes	عرض الملاحظات	عرض الملاحظات	other	f	[]
43	view_own_account	view_own_account	عرض الحساب الشخصي	عرض حسابي	other	f	[]
44	view_own_orders	view_own_orders	عرض طلبات المستخدم الشخصية	عرض طلباتي	other	f	[]
45	view_parts	view_parts	عرض قطع الغيار	عرض القطع	warehouses	f	[]
46	view_preorders	view_preorders	عرض الطلبات المسبقة	عرض الطلبات المسبقة	shop	f	[]
47	view_reports	view_reports	عرض التقارير المالية	عرض التقارير	accounting	f	[]
48	view_sales	view_sales	عرض قائمة المبيعات	عرض المبيعات	sales	f	[]
49	view_service	view_service	عرض طلبات الصيانة	عرض الصيانة	service	f	[]
50	view_shop	view_shop	الدخول للمتجر الإلكتروني	عرض المتجر	shop	f	[]
51	view_warehouses	view_warehouses	عرض قائمة المستودعات	عرض المستودعات	warehouses	f	[]
52	warehouse_transfer	warehouse_transfer	نقل البضائع بين المستودعات	تحويل مخزني	warehouses	f	[]
\.


--
-- Data for Name: preorders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.preorders (id, reference, preorder_date, expected_date, customer_id, supplier_id, partner_id, product_id, warehouse_id, quantity, prepaid_amount, tax_rate, status, notes, payment_method, currency, fx_rate_used, fx_rate_source, fx_rate_timestamp, fx_base_currency, fx_quote_currency, refunded_total, refund_of_id, idempotency_key, cancelled_at, cancelled_by, cancel_reason, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: product_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product_categories (id, name, parent_id, description, image_url, created_at, updated_at) FROM stdin;
1	محركات	\N	\N	\N	2025-10-23 20:02:09	2025-10-23 20:02:09
2	lkj[hj 2	\N	\N	\N	2025-10-23 20:21:21	2025-10-23 20:21:21
3	GEARBOX	\N	\N	\N	2025-10-23 20:32:19	2025-10-23 20:32:19
4	HYD PUMP	\N	\N	\N	2025-10-24 16:34:22	2025-10-24 16:34:22
5	HYD PARTS	\N	\N	\N	2025-10-24 16:44:39	2025-10-24 16:44:39
6	كوبلنات	\N	\N	\N	2025-10-29 17:32:47	2025-10-29 17:32:47
7	فلاتر	\N	\N	\N	2025-10-29 18:21:32	2025-10-29 18:21:32
8	بخاخات	\N	\N	\N	2025-10-29 18:28:35	2025-10-29 18:28:35
9	محركات ديزل	\N	\N	\N	2025-11-04 12:28:46	2025-11-04 12:28:46
10	جلود اهتزاز	\N	\N	\N	2025-11-04 14:51:02	2025-11-04 14:51:02
11	زيوت وشحمة	\N	\N	\N	2025-11-05 22:44:46	2025-11-05 22:44:46
12	الكترونيات	\N	\N	\N	2025-11-06 12:44:12	2025-11-06 12:44:12
13	كسكيتات	\N	\N	\N	2025-11-07 14:26:11	2025-11-07 14:26:11
14	مراوح تبريد	\N	\N	\N	2025-11-07 14:31:33	2025-11-07 14:31:33
15	برابيش هواء وماء ماتور	\N	\N	\N	2025-11-07 14:32:53	2025-11-07 14:32:53
16	رديترات	\N	\N	\N	2025-11-07 15:22:36	2025-11-07 15:22:36
17	قطع محركات جديدة	\N	\N	\N	2025-11-07 15:26:32	2025-11-07 15:26:32
18	متفرقات	\N	\N	\N	2025-11-07 15:30:21	2025-11-07 15:30:21
19	قطع محركات مستعملة	\N	\N	\N	2025-11-09 21:39:43	2025-11-09 21:39:43
20	معدات	\N	\N	\N	2025-11-15 13:04:37	2025-11-15 13:04:37
21	خدمات	\N	\N	\N	2025-11-15 13:14:23	2025-11-15 13:14:23
22	مولدات وماكنات	\N	\N	\N	2025-11-28 14:41:12	2025-11-28 14:41:12
23	شحن وجمرك	\N	\N	\N	2025-12-09 23:13:47	2025-12-09 23:13:47
\.


--
-- Data for Name: product_partners; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product_partners (id, product_id, partner_id, share_percent, share_amount, notes) FROM stdin;
\.


--
-- Data for Name: product_rating_helpful; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product_rating_helpful (id, rating_id, customer_id, ip_address, is_helpful, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: product_ratings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product_ratings (id, product_id, customer_id, rating, title, comment, is_verified_purchase, is_approved, helpful_count, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: product_supplier_loans; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product_supplier_loans (id, product_id, supplier_id, loan_value, deferred_price, is_settled, partner_share_quantity, partner_share_value, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (id, sku, name, description, part_number, brand, commercial_name, chassis_number, serial_no, barcode, unit, category_name, purchase_price, selling_price, cost_before_shipping, cost_after_shipping, unit_price_before_tax, price, min_price, max_price, tax_rate, min_qty, reorder_point, image, notes, condition, origin_country, warranty_period, weight, dimensions, is_active, is_digital, is_exchange, is_published, vehicle_type_id, category_id, supplier_id, supplier_international_id, supplier_local_id, online_name, online_price, online_image, currency, fx_rate_used, fx_rate_source, fx_rate_timestamp, fx_base_currency, fx_quote_currency, created_at, updated_at) FROM stdin;
1	\N	PACCAR MX13 ENGINE	يطبق سعر شحن 8.5شيقل للكيلو	\N	\N	\N	\N	\N	\N	\N	\N	16100.00	23000.00	0.00	0.00	0.00	23000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	1	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-23 20:25:39	2025-10-31 22:19:43
2	\N	MERCEDES OM936 ENGINE	\N	\N	\N	\N	\N	\N	\N	\N	\N	11200.00	16000.00	0.00	0.00	0.00	16000.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	\N	1	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-23 20:27:38	2025-10-24 15:34:50
3	\N	CUMMINS ISF3.8 ENGINE EGR	\N	\N	\N	\N	\N	\N	\N	\N	\N	5600.00	8000.00	0.00	0.00	0.00	8000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	1	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-23 20:30:29	2025-10-24 15:34:50
4	\N	CUMMINS ISF3.8 ENGINE	\N	\N	\N	\N	\N	\N	\N	\N	\N	4900.00	7000.00	0.00	0.00	0.00	7000.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	\N	1	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-23 20:31:34	2025-10-24 15:34:50
5	\N	ZF GEARBOX	مشكل قياس 800و700و1000	\N	\N	\N	\N	\N	\N	\N	\N	1050.00	1500.00	0.00	0.00	0.00	1500.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	3	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-23 20:33:31	2025-10-24 15:34:50
6	\N	VOLVO D5 ENGINE	\N	\N	\N	\N	\N	\N	\N	\N	\N	9800.00	14000.00	0.00	0.00	0.00	14000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	1	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-23 20:35:21	2025-10-24 15:34:50
7	\N	EICHER 4CYL ENGINE	\N	\N	\N	\N	\N	\N	\N	\N	\N	9100.00	13000.00	0.00	0.00	0.00	13000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	1	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-23 20:38:23	2025-10-24 15:34:50
8	\N	EICHER 6CYL ENGINE	\N	\N	\N	\N	\N	\N	\N	\N	\N	9100.00	13000.00	0.00	0.00	0.00	13000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	1	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-23 20:39:11	2025-10-24 15:34:50
9	\N	CUMMINS 4.5 ENGINE	\N	\N	\N	\N	\N	\N	\N	\N	\N	4200.00	6000.00	0.00	0.00	0.00	6000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	1	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-23 20:40:24	2025-10-24 15:34:50
10	\N	MERCEDES 4CYL ENGINE	\N	\N	\N	\N	\N	\N	\N	\N	\N	9800.00	14000.00	0.00	0.00	0.00	14000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	1	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-23 20:41:13	2025-10-24 15:34:50
11	\N	طرمبة ريكس روث 90 خلاطة مفحوصة	\N	\N	\N	\N	\N	\N	\N	\N	\N	4900.00	7000.00	0.00	0.00	0.00	7000.00	4500.00	7000.00	0.00	5	\N	products/default.png	\N	USED	GERMANY	0	\N	\N	t	f	f	f	\N	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-24 16:37:25	2025-11-02 15:41:50
12	\N	طرمبة ريكس روث 190	\N	\N	\N	\N	\N	\N	\N	\N	\N	10500.00	15000.00	0.00	0.00	0.00	15000.00	8000.00	15000.00	0.00	5	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-24 16:41:06	2025-11-02 15:41:50
13	\N	طرمبة ريكس روث 90 خلاطة خربان	\N	\N	\N	\N	\N	\N	\N	\N	\N	3150.00	4500.00	0.00	0.00	0.00	4500.00	1500.00	4500.00	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-24 16:43:35	2025-11-02 15:41:50
14	\N	سلكتور مضخة باطون	\N	\N	\N	\N	\N	\N	\N	\N	\N	4900.00	7000.00	0.00	0.00	0.00	7000.00	3500.00	7500.00	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	5	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-24 16:45:23	2025-11-02 15:41:50
15	\N	طرمبة ريكس روث 28 مضخة باطون	\N	\N	\N	\N	\N	\N	\N	\N	\N	4200.00	6000.00	0.00	0.00	0.00	6000.00	2000.00	6000.00	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-24 16:50:11	2025-11-02 15:41:50
16	\N	محرك جير خلاطة	\N	\N	\N	\N	\N	\N	\N	\N	\N	4200.00	6000.00	0.00	0.00	0.00	6000.00	1500.00	6000.00	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-24 16:51:46	2025-11-02 15:41:50
17	\N	جير خلاطة مع محرك	\N	\N	\N	\N	\N	\N	\N	\N	\N	3850.00	10000.00	0.00	0.00	0.00	5500.00	5500.00	10000.00	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	3	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-24 16:52:53	2025-11-02 15:41:50
18	\N	طرمبة بوم 55	\N	\N	\N	\N	\N	\N	\N	\N	\N	4200.00	6000.00	0.00	0.00	0.00	6000.00	1500.00	6000.00	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-24 16:54:10	2025-11-02 15:41:50
19	\N	ترانسفير مضخة ناعم	\N	\N	\N	\N	\N	\N	\N	\N	\N	5600.00	15000.00	0.00	0.00	0.00	8000.00	8000.00	15000.00	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	3	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-24 16:55:14	2025-11-02 15:41:50
20	\N	محرك مشي جيل \\كاتربلر	\N	\N	\N	\N	\N	\N	\N	\N	\N	9100.00	13000.00	0.00	0.00	0.00	13000.00	10000.00	13000.00	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	\N	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-24 17:13:04	2025-12-06 20:28:52
21	\N	طرمبة المنيوم كومناتور	\N	\N	\N	\N	\N	\N	\N	\N	\N	2450.00	3500.00	0.00	0.00	0.00	3500.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-25 22:16:37	2025-11-02 15:41:50
22	\N	طرمبة ريكس روث 90 قديم	\N	\N	\N	\N	\N	\N	\N	\N	\N	4200.00	6000.00	0.00	0.00	0.00	6000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-26 11:46:10	2025-11-02 15:41:50
23	\N	طرمبة تحضير ريكس روث 90 كبير	\N	\N	\N	\N	\N	\N	\N	\N	\N	0.00	3000.00	0.00	1500.00	0.00	3000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	5	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-29 12:40:04	2025-10-29 12:40:04
24	\N	كوبلن اطلس186 جديد	\N	\N	\N	\N	\N	\N	\N	\N	\N	0.00	1500.00	0.00	700.00	0.00	1500.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	\N	6	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-29 17:33:16	2025-10-29 17:33:16
25	\N	فلتر هايدروليك اصفر	\N	\N	\N	\N	\N	\N	\N	\N	\N	0.00	200.00	0.00	100.00	0.00	200.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	\N	7	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-29 18:21:59	2025-10-29 18:21:59
26	\N	بخاخ FPT F34 مستعمل	\N	\N	\N	\N	\N	\N	\N	\N	\N	0.00	2000.00	0.00	1000.00	0.00	2000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	8	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-29 18:33:45	2025-10-29 18:33:45
27	\N	طرمبة تحضير ريكس روث125	\N	\N	\N	\N	\N	\N	\N	\N	\N	0.00	4500.00	0.00	2000.00	0.00	4500.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	5	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-10-29 20:33:20	2025-10-29 20:33:20
28	\N	محرك كامنز QSL 9	\N	\N	\N	\N	\N	\N	\N	\N	\N	20000.00	40000.00	0.00	0.00	0.00	40000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	1	9	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-04 12:32:07	2025-11-04 12:32:07
29	\N	جلدة اهتزاز مدحلة مربعة حجم كبير 7سم	\N	\N	\N	\N	\N	\N	\N	\N	\N	500.00	800.00	0.00	0.00	0.00	800.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	1	10	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-04 14:51:47	2025-11-04 14:51:47
30	\N	سطل شحمة	\N	\N	\N	\N	\N	\N	\N	\N	\N	100.00	200.00	0.00	0.00	0.00	200.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	1	11	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-05 22:45:34	2025-11-05 22:45:34
31	\N	شاحن الكتروني 12-24	\N	\N	\N	\N	\N	\N	\N	\N	\N	500.00	1500.00	0.00	0.00	0.00	1500.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	1	12	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-06 12:45:18	2025-11-06 12:45:18
32	\N	كسكيت راس YANMAR 3TNV82	\N	\N	\N	\N	\N	\N	\N	\N	\N	250.00	800.00	0.00	0.00	0.00	800.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	1	13	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-07 14:27:21	2025-11-07 14:27:21
33	\N	كسكيت راس متسوبيشي 4LE	\N	\N	\N	\N	\N	\N	\N	\N	\N	150.00	600.00	0.00	0.00	0.00	600.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	1	7	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-07 14:28:33	2025-11-07 14:28:33
34	\N	كسكيت منفولت 2011	\N	\N	\N	\N	\N	\N	\N	\N	\N	50.00	300.00	0.00	0.00	0.00	300.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	1	13	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-07 14:29:35	2025-11-07 14:29:35
35	\N	مروحة كوبوتا شفط	\N	\N	\N	\N	\N	\N	\N	\N	\N	200.00	600.00	0.00	0.00	0.00	600.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	1	14	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-07 14:31:52	2025-11-07 14:31:52
36	\N	بربيش هوا تيربو	\N	\N	\N	\N	\N	\N	\N	\N	\N	50.00	300.00	0.00	0.00	0.00	300.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	1	15	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-07 14:33:10	2025-11-07 14:33:10
37	\N	سكانيا 6 سلندر احمر	\N	\N	\N	\N	\N	\N	\N	\N	\N	30000.00	60000.00	0.00	0.00	0.00	60000.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	1	9	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-07 15:18:02	2025-11-07 15:18:02
38	\N	كاتربلر3306	\N	\N	\N	\N	\N	\N	\N	\N	\N	18000.00	35000.00	0.00	0.00	0.00	35000.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	1	9	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-07 15:19:03	2025-11-07 15:19:03
39	\N	طرمبة رفع بوبكات S650	\N	\N	\N	\N	\N	\N	\N	\N	\N	3000.00	7000.00	0.00	0.00	0.00	7000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	1	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-07 15:21:12	2025-11-07 15:21:12
40	\N	رديتر مكيف بوبكات CASE	\N	\N	\N	\N	\N	\N	\N	\N	\N	750.00	1500.00	0.00	0.00	0.00	1500.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	1	16	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-07 15:23:06	2025-11-07 15:23:06
41	\N	مروحة مكيف بوبكاتCASE	\N	\N	\N	\N	\N	\N	\N	\N	\N	150.00	300.00	0.00	0.00	0.00	300.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	1	14	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-07 15:24:32	2025-11-07 15:24:32
42	\N	غطا صباب دوتس 3.6	\N	\N	\N	\N	\N	\N	\N	\N	\N	1500.00	4000.00	0.00	0.00	0.00	4000.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	1	17	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-07 15:27:02	2025-11-07 15:27:02
43	\N	بربيش شادر 15متر	\N	\N	\N	\N	\N	\N	\N	\N	\N	30.00	100.00	0.00	0.00	0.00	100.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	1	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-07 15:30:41	2025-11-07 15:30:41
44	\N	كويل 12 فولت	\N	\N	\N	\N	\N	\N	\N	\N	\N	150.00	300.00	0.00	0.00	0.00	300.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	1	5	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-07 15:43:08	2025-11-07 15:43:08
45	\N	كوبلن جرافة زتلماير	\N	\N	\N	\N	\N	\N	\N	\N	\N	200.00	800.00	0.00	0.00	0.00	800.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	6	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-09 20:45:38	2025-11-09 20:45:38
46	\N	طرمبة ضراب 12فولت عادية	\N	\N	\N	\N	\N	\N	\N	\N	\N	100.00	450.00	0.00	0.00	0.00	450.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	3	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-09 21:08:02	2025-11-09 21:08:02
47	\N	ضراب سولار اسود بوش	\N	\N	\N	\N	\N	\N	\N	\N	\N	50.00	200.00	0.00	0.00	0.00	200.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-09 21:08:44	2025-11-09 21:08:44
48	\N	طرمبة ماء 2 انش كهرباء	\N	\N	\N	\N	\N	\N	\N	\N	\N	200.00	800.00	0.00	0.00	0.00	800.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-09 21:11:09	2025-11-09 21:11:09
49	\N	دبابة نقل مواكن صغيرة	\N	\N	\N	\N	\N	\N	\N	\N	\N	350.00	800.00	0.00	0.00	0.00	800.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-09 21:29:29	2025-11-09 21:29:29
50	\N	دبابة نقل مواكن كبيرة	\N	\N	\N	\N	\N	\N	\N	\N	\N	700.00	1500.00	0.00	0.00	0.00	1500.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-09 21:30:20	2025-11-09 21:30:20
51	\N	جك اصفر 5 طون ارضي	\N	\N	\N	\N	\N	\N	\N	\N	\N	300.00	1000.00	0.00	0.00	0.00	1000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-09 21:32:01	2025-11-09 21:32:01
52	\N	جك ازرق 10 طون ارضي	\N	\N	\N	\N	\N	\N	\N	\N	\N	300.00	1500.00	0.00	0.00	0.00	1500.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-09 21:33:13	2025-11-09 21:33:13
53	\N	حساس كرنك كوبوتا 3307	\N	\N	\N	\N	\N	\N	\N	\N	\N	500.00	1500.00	0.00	0.00	0.00	1500.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	19	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-09 21:40:04	2025-11-09 21:40:04
54	\N	حساس ضغط ماسورة 3307	\N	\N	\N	\N	\N	\N	\N	\N	\N	500.00	1500.00	0.00	0.00	0.00	1500.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	19	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-09 21:41:14	2025-11-09 21:41:14
55	\N	بلف طرمبة سولار كوبوتا 3307	\N	\N	\N	\N	\N	\N	\N	\N	\N	500.00	1800.00	0.00	0.00	0.00	1800.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	19	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-09 21:41:51	2025-11-09 21:41:51
56	\N	مبرد EGR C2.2	\N	\N	\N	\N	\N	\N	\N	\N	\N	500.00	3500.00	0.00	0.00	0.00	3500.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	19	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-09 21:44:27	2025-11-09 21:44:27
57	\N	غطا صباب RG 4	\N	\N	\N	\N	\N	\N	\N	\N	\N	500.00	2000.00	0.00	0.00	0.00	2000.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	\N	17	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-09 21:46:05	2025-11-09 21:46:05
58	\N	طرمبة ونش مع تحكم	\N	\N	\N	\N	\N	\N	\N	\N	\N	1000.00	5000.00	0.00	0.00	0.00	5000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-09 21:51:23	2025-11-09 21:51:23
59	\N	بلانكو يدوي 3 طن	\N	\N	\N	\N	\N	\N	\N	\N	\N	300.00	800.00	0.00	0.00	0.00	800.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-09 21:51:55	2025-11-09 21:51:55
60	\N	مجبد CMجنزير	\N	\N	\N	\N	\N	\N	\N	\N	\N	200.00	600.00	0.00	0.00	0.00	600.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-09 21:52:37	2025-11-09 21:52:37
61	\N	ماسورة بخاخ كوبوتا1703	\N	\N	\N	\N	\N	\N	\N	\N	\N	100.00	400.00	0.00	0.00	0.00	400.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	19	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-10 22:10:33	2025-11-10 22:10:33
62	\N	حساس ضغط زيت سلك واحد	\N	\N	\N	\N	\N	\N	\N	\N	\N	150.00	350.00	0.00	0.00	0.00	350.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	17	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-10 22:11:36	2025-11-10 22:11:36
63	\N	كوبلن ثلاثي حجم 30	\N	\N	\N	\N	\N	\N	\N	\N	\N	1200.00	2000.00	0.00	0.00	0.00	2000.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	\N	6	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-12 12:36:03	2025-11-12 12:36:03
64	\N	طرمبة ريكس روث 71	\N	\N	\N	\N	\N	\N	\N	\N	\N	3000.00	10000.00	0.00	0.00	0.00	10000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-12 14:20:54	2025-11-12 14:20:54
65	\N	كامنز 11	\N	\N	\N	\N	\N	\N	\N	\N	\N	3000.00	8000.00	0.00	0.00	0.00	8000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	1	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-12 17:36:15	2025-11-12 17:36:15
66	\N	محرك مروحة شفرات 45 لتر	\N	\N	\N	\N	\N	\N	\N	\N	\N	1500.00	7000.00	0.00	0.00	0.00	7000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-13 10:34:07	2025-11-13 10:34:07
67	\N	ستليت محرك مني صغير	\N	\N	\N	\N	\N	\N	\N	\N	\N	1000.00	5000.00	0.00	0.00	0.00	5000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	5	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-13 22:50:58	2025-11-13 22:50:58
68	\N	باجر 3cx jcb 2013	\N	\N	\N	\N	\N	\N	\N	\N	\N	60000.00	90000.00	0.00	0.00	0.00	90000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	t	f	\N	20	2	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-15 13:06:16	2025-11-15 13:06:16
69	\N	مزليك نيسان 2.5 طن قديم	\N	\N	\N	\N	\N	\N	\N	\N	\N	4500.00	8000.00	0.00	0.00	0.00	8000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	t	f	\N	20	4	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-16 19:32:03	2025-11-16 19:32:03
70	\N	كابل مدحلة 75	\N	\N	\N	\N	\N	\N	\N	\N	\N	200.00	850.00	0.00	0.00	0.00	850.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-16 20:02:45	2025-11-16 20:02:45
71	\N	كابل بولاد 14 ملي	\N	\N	\N	\N	\N	\N	\N	متر	\N	9.00	20.00	0.00	0.00	0.00	20.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-16 20:04:26	2025-11-16 20:04:26
72	\N	ازميل جك كمبريصة قصير جديد	\N	\N	\N	\N	\N	\N	\N	\N	\N	100.00	250.00	0.00	0.00	0.00	250.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-17 14:59:06	2025-11-17 14:59:06
73	\N	نبل بربيش كمريصة حفر	\N	\N	\N	\N	\N	\N	\N	\N	\N	10.00	50.00	0.00	0.00	0.00	50.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-17 14:59:54	2025-11-17 14:59:54
74	\N	جلدة جرة مضخة سمسم	\N	\N	\N	\N	\N	\N	\N	\N	\N	50.00	350.00	0.00	0.00	0.00	350.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-17 15:05:02	2025-11-17 15:05:02
75	\N	كامنز 4.5	\N	\N	\N	\N	\N	\N	\N	\N	\N	6500.00	7500.00	0.00	0.00	0.00	7500.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	1	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-25 10:42:22	2025-11-25 10:42:22
76	\N	محرك مشي جيل	\N	\N	\N	\N	\N	\N	\N	\N	\N	3000.00	12000.00	0.00	0.00	0.00	12000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-25 10:46:47	2025-11-25 10:46:47
77	\N	طرمبة موزة 32 مضخة	\N	\N	\N	\N	\N	\N	\N	\N	\N	1500.00	3500.00	0.00	0.00	0.00	3500.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-25 10:58:29	2025-11-25 10:58:29
78	\N	بستون بيركنز 404 STD	\N	\N	\N	\N	\N	\N	\N	\N	\N	100.00	600.00	0.00	0.00	0.00	600.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	\N	17	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-25 13:09:05	2025-11-25 13:09:05
79	\N	طقم بيركنز 404	\N	\N	\N	\N	\N	\N	\N	\N	\N	400.00	2000.00	0.00	0.00	0.00	2000.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	\N	17	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-25 13:10:36	2025-11-25 13:10:36
80	\N	رنج بستون بيركنز 404 STD	\N	\N	\N	\N	\N	\N	\N	\N	\N	50.00	250.00	0.00	0.00	0.00	250.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	\N	17	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-25 13:11:32	2025-11-25 13:11:32
81	\N	كشنيت متحرك بيركنز404 STD	\N	\N	\N	\N	\N	\N	\N	\N	\N	50.00	250.00	0.00	0.00	0.00	250.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	\N	17	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-25 13:12:53	2025-11-25 13:12:53
82	\N	كشنيت ثابت بيركنز 404 STD	\N	\N	\N	\N	\N	\N	\N	\N	\N	50.00	350.00	0.00	0.00	0.00	350.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	\N	17	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-25 13:14:10	2025-11-25 13:14:10
83	\N	كابل بولاد 5ملي	\N	\N	\N	\N	\N	\N	\N	متر	\N	1.00	5.00	0.00	0.00	0.00	5.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-25 13:28:23	2025-11-25 13:28:23
84	\N	ملقط كابل اشتراك جوز	\N	\N	\N	\N	\N	\N	\N	\N	\N	50.00	200.00	0.00	0.00	0.00	200.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-25 13:29:29	2025-11-25 13:29:29
85	\N	كشاط تايمنج 1011 دوتس مع مشد	\N	\N	\N	\N	\N	\N	\N	\N	\N	300.00	1200.00	0.00	0.00	0.00	1200.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	17	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-25 13:30:26	2025-11-25 13:30:26
86	\N	فلتر زيت دوتس قصير	\N	\N	\N	\N	\N	\N	\N	\N	\N	100.00	300.00	0.00	0.00	0.00	300.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	7	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-25 13:34:47	2025-11-25 13:34:47
87	\N	فلتر سولار دوتس مع تصريف	\N	\N	\N	\N	\N	\N	\N	\N	\N	50.00	200.00	0.00	0.00	0.00	200.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	7	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-25 13:35:08	2025-11-25 13:35:08
88	\N	قطع طرمبة مني	\N	\N	\N	\N	\N	\N	\N	\N	\N	200.00	5000.00	0.00	0.00	0.00	5000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	5	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-25 13:39:20	2025-11-25 13:39:20
89	\N	كوبلن مني 1.5 طون	\N	\N	\N	\N	\N	\N	\N	\N	\N	500.00	1300.00	0.00	0.00	0.00	1300.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-25 22:12:24	2025-11-25 22:12:24
90	\N	كيتور ديزل كبير	\N	\N	\N	\N	\N	\N	\N	\N	\N	6500.00	10000.00	0.00	0.00	0.00	10000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	t	f	\N	18	6	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-28 14:42:10	2025-11-28 14:42:10
91	\N	شاحن الكتروني فاز 24/48	\N	\N	\N	\N	\N	\N	\N	\N	\N	150.00	1500.00	0.00	0.00	0.00	1500.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	12	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-28 14:43:55	2025-11-28 14:43:55
92	\N	حساس حرارة هواء اسوزو 6HK1	\N	\N	\N	\N	\N	\N	\N	\N	\N	400.00	1500.00	0.00	0.00	0.00	1500.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	12	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-28 14:58:29	2025-11-28 14:58:29
93	\N	كسكيت راس دوتس 2012 VR	3خزوق	\N	\N	\N	\N	\N	\N	\N	\N	350.00	1500.00	0.00	0.00	0.00	1500.00	\N	\N	0.00	0	\N	products/default.png	\N	NEW	\N	0	\N	\N	t	f	f	f	\N	17	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-28 15:20:46	2025-11-28 15:20:46
94	\N	ماتور هينو	\N	\N	\N	\N	\N	\N	\N	\N	\N	26000.00	29000.00	0.00	0.00	0.00	29000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	9	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-28 15:33:16	2025-11-28 15:33:16
95	\N	عيار لحام ميلر 401	\N	\N	\N	\N	\N	\N	\N	\N	\N	200.00	1500.00	0.00	0.00	0.00	1500.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	12	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-30 07:37:51	2025-11-30 07:37:51
96	\N	بخاخ كوبوتا 2203 حديث	\N	\N	\N	\N	\N	\N	\N	\N	\N	50.00	1200.00	0.00	0.00	0.00	1200.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	17	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-30 19:38:45	2025-11-30 19:38:45
97	\N	كشاط مشي S130 اصلي	\N	\N	\N	\N	\N	\N	\N	\N	\N	400.00	1200.00	0.00	0.00	0.00	1200.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	17	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-30 19:40:25	2025-11-30 19:40:25
98	\N	مشد قشاط S130	\N	\N	\N	\N	\N	\N	\N	\N	\N	300.00	1000.00	0.00	0.00	0.00	1000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-11-30 19:42:48	2025-11-30 19:42:48
99	\N	حرذون دوتس 1011	\N	\N	\N	\N	\N	\N	\N	\N	\N	200.00	500.00	0.00	0.00	0.00	500.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	19	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-12-02 20:38:43	2025-12-02 20:38:43
100	\N	سيخ صباب دوتس 1011	\N	\N	\N	\N	\N	\N	\N	\N	\N	50.00	200.00	0.00	0.00	0.00	200.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	19	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-12-02 20:39:45	2025-12-02 20:39:45
101	\N	كسكيت راس دوتس 1011 4 سلندر	\N	\N	\N	\N	\N	\N	\N	\N	\N	150.00	650.00	0.00	0.00	0.00	650.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	17	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-12-04 22:34:37	2025-12-04 22:34:37
102	\N	بستون كوبوتا 2203 سن 87	\N	\N	\N	\N	\N	\N	\N	\N	\N	180.00	800.00	0.00	0.00	0.00	800.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	17	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-12-04 22:50:54	2025-12-04 22:50:54
103	\N	رنج كوبوتا 2203 سن87	\N	\N	\N	\N	\N	\N	\N	\N	\N	50.00	300.00	0.00	0.00	0.00	300.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	17	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-12-04 22:54:56	2025-12-04 22:54:56
104	\N	كسكيت راس كوبوتا 1703	\N	\N	\N	\N	\N	\N	\N	\N	\N	200.00	800.00	0.00	0.00	0.00	800.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	17	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-12-04 22:58:34	2025-12-04 22:58:34
105	\N	سن قحاطة	\N	\N	\N	\N	\N	\N	\N	\N	\N	5.00	20.00	0.00	0.00	0.00	20.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-12-05 19:46:54	2025-12-05 19:46:54
106	\N	حمالة سن قحاطة	\N	\N	\N	\N	\N	\N	\N	\N	\N	50.00	100.00	0.00	0.00	0.00	100.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-12-05 19:50:06	2025-12-05 19:50:06
107	\N	زطمة قحاطة	\N	\N	\N	\N	\N	\N	\N	\N	\N	5.00	20.00	0.00	0.00	0.00	20.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	18	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-12-05 19:51:20	2025-12-05 19:51:20
108	\N	فلتر سيبراتور اطلس 186	\N	\N	\N	\N	\N	\N	\N	\N	\N	300.00	1200.00	0.00	0.00	0.00	1200.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	7	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-12-08 23:11:54	2025-12-08 23:11:54
109	\N	فلتر زيت توربينة اطلس 186	\N	\N	\N	\N	\N	\N	\N	\N	\N	50.00	350.00	0.00	0.00	0.00	350.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	7	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-12-08 23:12:28	2025-12-08 23:12:28
110	\N	شحن محركات من الامارات الى رام الله	\N	\N	\N	\N	\N	\N	\N	\N	\N	8.00	10.00	0.00	0.00	0.00	10.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	23	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-12-09 23:14:10	2025-12-09 23:14:10
111	\N	طرمبة المنيوم صغير	\N	\N	\N	\N	\N	\N	\N	\N	\N	300.00	2000.00	0.00	0.00	0.00	2000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-12-14 13:57:13	2025-12-14 13:57:13
112	\N	طرمبة المنيوم صغير	\N	\N	\N	\N	\N	\N	\N	\N	\N	300.00	2000.00	0.00	0.00	0.00	2000.00	\N	\N	0.00	0	\N	products/default.png	\N	USED	\N	0	\N	\N	t	f	f	f	\N	4	\N	\N	\N	\N	0.00	\N	ILS	\N	\N	\N	\N	\N	2025-12-14 14:06:17	2025-12-14 14:06:17
\.


--
-- Data for Name: project_change_orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.project_change_orders (id, project_id, change_number, title, description, requested_by, requested_date, reason, scope_change, cost_impact, schedule_impact_days, status, approved_by, approved_date, implemented_date, rejection_reason, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: project_costs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.project_costs (id, project_id, phase_id, cost_type, source_id, amount, cost_date, description, gl_batch_id, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: project_issues; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.project_issues (id, project_id, task_id, issue_number, title, description, category, severity, priority, status, reported_by, assigned_to, reported_date, resolved_date, resolution, cost_impact, schedule_impact_days, root_cause, preventive_action, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: project_milestones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.project_milestones (id, project_id, phase_id, milestone_number, name, description, due_date, completed_date, billing_amount, tax_rate, tax_amount, billing_percentage, invoice_id, payment_terms_days, status, completion_criteria, deliverables, approval_required, approved_by, approved_at, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: project_phases; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.project_phases (id, project_id, name, "order", start_date, end_date, planned_budget, actual_cost, status, completion_percentage, description, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: project_resources; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.project_resources (id, project_id, task_id, resource_type, employee_id, product_id, resource_name, quantity, unit_cost, total_cost, allocation_date, start_date, end_date, hours_allocated, hours_used, status, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: project_revenues; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.project_revenues (id, project_id, phase_id, revenue_type, source_id, amount, revenue_date, description, gl_batch_id, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: project_risks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.project_risks (id, project_id, risk_number, title, description, category, probability, impact, risk_score, status, mitigation_plan, contingency_plan, owner_id, identified_date, review_date, closed_date, actual_impact_cost, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: project_tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.project_tasks (id, project_id, phase_id, task_number, name, description, assigned_to, priority, status, start_date, due_date, completed_date, estimated_hours, actual_hours, completion_percentage, depends_on, blocked_reason, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.projects (id, code, name, client_id, start_date, end_date, planned_end_date, budget_amount, estimated_cost, estimated_revenue, actual_cost, actual_revenue, cost_center_id, manager_id, branch_id, status, completion_percentage, description, notes, is_active, created_by, updated_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: recurring_invoice_schedules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.recurring_invoice_schedules (id, template_id, invoice_id, scheduled_date, generated_at, status, error_message, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: recurring_invoice_templates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.recurring_invoice_templates (id, template_name, customer_id, description, amount, currency, tax_rate, frequency, start_date, end_date, next_invoice_date, is_active, branch_id, site_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: resource_time_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.resource_time_logs (id, project_id, task_id, resource_id, employee_id, log_date, hours_worked, hourly_rate, total_cost, description, approved, approved_by, approved_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.role_permissions (role_id, permission_id) FROM stdin;
1	6
1	1
1	12
1	7
1	2
1	13
1	8
1	3
1	9
1	4
1	10
1	5
1	11
8	6
8	1
8	12
8	7
8	2
8	13
8	8
8	3
8	9
8	4
8	10
8	5
8	11
2	6
2	1
2	12
2	7
2	2
2	13
2	8
2	3
2	9
2	4
2	10
2	5
2	11
9	6
9	1
9	12
9	7
9	2
9	13
9	8
9	3
9	9
9	4
9	10
9	5
9	11
3	33
3	19
3	18
3	48
3	13
3	47
3	34
3	50
3	35
3	36
3	52
3	37
3	51
3	38
3	20
3	39
3	21
3	40
3	22
3	41
3	23
3	42
3	24
3	43
3	3
3	25
3	44
3	26
3	45
3	31
3	27
3	49
3	32
3	28
3	14
3	15
3	8
3	16
3	9
3	29
3	17
3	10
3	30
3	46
10	33
10	18
10	48
10	47
10	36
10	52
10	37
10	51
10	39
10	40
10	41
10	23
10	42
10	25
10	31
10	45
10	27
10	32
10	49
10	28
10	15
10	16
10	29
10	30
4	41
4	33
4	42
4	48
4	40
4	15
4	51
4	47
4	25
4	45
4	30
4	27
4	49
4	32
5	41
5	33
5	51
5	47
5	45
5	49
6	19
6	43
6	38
6	44
6	50
6	46
11	50
11	19
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name, description, is_default) FROM stdin;
1	Owner	System Owner with full control	f
2	super_admin	\N	f
3	admin	\N	f
4	staff	\N	f
5	mechanic	\N	f
6	registered_customer	\N	f
7	owner	👑 مالك النظام - صلاحيات كاملة ومطلقة على كل شيء بلا استثناء	f
8	developer	💻 مطور النظام - صلاحيات تقنية كاملة	f
9	super	⚡ سوبر - نفس صلاحيات المدير الأعلى	f
10	manager	👨‍💼 مشرف - إشراف على العمليات اليومية	f
11	guest	👤 زائر غير مسجل - تصفح المتجر فقط	f
\.


--
-- Data for Name: saas_invoices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.saas_invoices (id, invoice_number, subscription_id, amount, currency, status, due_date, paid_at, payment_method, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: saas_plans; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.saas_plans (id, name, description, price_monthly, price_yearly, currency, max_users, max_invoices, storage_gb, features, is_active, is_popular, sort_order, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: saas_subscriptions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.saas_subscriptions (id, customer_id, plan_id, status, start_date, end_date, trial_end_date, auto_renew, cancelled_at, cancelled_by, cancellation_reason, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sale_lines; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sale_lines (id, sale_id, product_id, warehouse_id, quantity, unit_price, discount_rate, tax_rate, line_receiver, note, created_at, updated_at) FROM stdin;
1	1	9	1	1	6000.00	0.00	0.00	\N	\N	2025-10-23 20:50:04	2025-10-23 20:50:04
2	1	4	1	4	7000.00	0.00	0.00	\N	\N	2025-10-23 20:50:04	2025-10-23 20:50:04
3	1	3	1	7	8000.00	0.00	0.00	\N	\N	2025-10-23 20:50:04	2025-10-23 20:50:04
4	1	7	1	1	13000.00	0.00	0.00	\N	\N	2025-10-23 20:50:04	2025-10-23 20:50:04
5	1	8	1	1	13000.00	0.00	0.00	\N	\N	2025-10-23 20:50:04	2025-10-23 20:50:04
6	1	10	1	1	14000.00	0.00	0.00	\N	\N	2025-10-23 20:50:04	2025-10-23 20:50:04
7	1	2	1	2	16000.00	0.00	0.00	\N	\N	2025-10-23 20:50:04	2025-10-23 20:50:04
8	1	1	1	4	23000.00	0.00	0.00	\N	\N	2025-10-23 20:50:04	2025-10-23 20:50:04
9	1	6	1	1	14000.00	0.00	0.00	\N	\N	2025-10-23 20:50:04	2025-10-23 20:50:04
10	1	5	1	10	1500.00	0.00	0.00	\N	\N	2025-10-23 20:50:04	2025-10-23 20:50:04
11	2	19	2	1	8000.00	0.00	0.00	\N	\N	2025-10-24 18:36:54	2025-10-24 18:36:54
12	2	17	2	1	5500.00	0.00	0.00	\N	\N	2025-10-24 18:36:54	2025-10-24 18:36:54
13	2	14	2	1	3500.00	0.00	0.00	\N	\N	2025-10-24 18:36:54	2025-10-24 18:36:54
14	2	12	2	1	8000.00	0.00	0.00	\N	\N	2025-10-24 18:36:54	2025-10-24 18:36:54
15	2	18	2	1	1500.00	0.00	0.00	\N	\N	2025-10-24 18:36:54	2025-10-24 18:36:54
16	2	15	2	1	2000.00	0.00	0.00	\N	\N	2025-10-24 18:36:54	2025-10-24 18:36:54
17	2	16	2	3	1500.00	0.00	0.00	\N	\N	2025-10-24 18:36:54	2025-10-24 18:36:54
18	2	11	2	3	4500.00	0.00	0.00	\N	\N	2025-10-24 18:36:54	2025-10-24 18:36:54
19	2	13	2	6	1500.00	0.00	0.00	\N	\N	2025-10-24 18:36:54	2025-10-24 18:36:54
20	3	21	2	1	2500.00	0.00	0.00	سعيد	\N	2025-10-25 22:18:44	2025-10-25 22:18:44
21	4	22	2	1	5000.00	0.00	0.00	منصور	استلم	2025-10-26 17:32:38	2025-10-26 17:32:38
22	5	23	2	1	3000.00	0.00	0.00	\N	\N	2025-10-29 18:17:58	2025-10-29 18:17:58
23	6	25	3	2	200.00	0.00	0.00	يوسف	\N	2025-10-29 18:22:54	2025-10-29 18:22:54
24	7	24	3	3	1500.00	0.00	0.00	اخو وليد	\N	2025-10-29 18:24:17	2025-10-29 18:24:17
25	8	27	2	2	4500.00	0.00	0.00	\N	\N	2025-10-29 20:34:53	2025-10-29 20:34:53
26	9	24	3	3	1500.00	0.00	0.00	اخو وليد	\N	2025-11-03 14:04:32	2025-11-03 14:04:32
27	10	14	2	1	7000.00	0.00	0.00	احمد	\N	2025-11-04 12:14:19	2025-11-04 12:14:19
28	11	28	5	1	40000.00	0.00	0.00	عارف	شامل التركيب	2025-11-04 12:34:30	2025-11-04 12:34:30
29	12	29	3	10	800.00	0.00	0.00	سميح	\N	2025-11-04 14:55:36	2025-11-04 14:55:36
30	13	31	3	2	1500.00	0.00	0.00	عامر	\N	2025-11-06 12:47:12	2025-11-06 12:47:12
31	14	36	3	1	200.00	0.00	0.00	يوسف	\N	2025-11-07 14:40:07	2025-11-07 14:40:07
32	14	32	3	1	600.00	0.00	0.00	يوسف	\N	2025-11-07 14:40:07	2025-11-07 14:40:07
33	14	33	3	1	500.00	0.00	0.00	يوسف	\N	2025-11-07 14:40:07	2025-11-07 14:40:07
34	14	34	3	1	200.00	0.00	0.00	يوسف	\N	2025-11-07 14:40:07	2025-11-07 14:40:07
35	14	35	6	1	400.00	0.00	0.00	يوسف	\N	2025-11-07 14:40:07	2025-11-07 14:40:07
36	15	39	2	1	7000.00	0.00	0.00	تكسي	عطية طولكرم	2025-11-07 15:34:26	2025-11-07 15:34:26
37	16	42	3	1	4000.00	0.00	0.00	فرسان	\N	2025-11-07 15:35:51	2025-11-07 15:35:51
38	17	37	7	1	60000.00	0.00	0.00	سيارة نقل	\N	2025-11-07 15:37:09	2025-11-07 15:37:09
39	18	38	5	1	35000.00	0.00	0.00	سيارة نقل	\N	2025-11-07 15:38:49	2025-11-07 15:38:49
40	19	40	6	1	1500.00	0.00	0.00	فرسان	\N	2025-11-07 15:40:41	2025-11-07 15:40:41
41	19	41	6	1	300.00	0.00	0.00	فرسان	\N	2025-11-07 15:40:41	2025-11-07 15:40:41
42	20	43	3	2	100.00	0.00	0.00	ابو فارس	\N	2025-11-07 15:41:37	2025-11-07 15:41:37
43	21	44	6	1	200.00	0.00	0.00	ابو فارس	\N	2025-11-07 15:44:16	2025-11-07 15:44:16
44	22	45	6	1	800.00	0.00	0.00	تكسي	\N	2025-11-09 20:47:15	2025-11-09 20:47:15
48	24	58	2	4	5000.00	35.00	0.00	ابو ناصر	\N	2025-11-09 21:55:58	2025-11-09 21:55:58
49	25	59	8	1	800.00	37.50	0.00	ابو ناصر	\N	2025-11-09 22:10:51	2025-11-09 22:10:51
50	25	60	8	1	400.00	0.00	0.00	ابو ناصر	\N	2025-11-09 22:10:51	2025-11-09 22:10:51
51	25	52	1	2	1500.00	20.00	0.00	في الطريق	\N	2025-11-09 22:10:51	2025-11-09 22:10:51
52	25	51	1	5	1000.00	20.00	0.00	في الطريق	\N	2025-11-09 22:10:51	2025-11-09 22:10:51
53	25	49	1	4	800.00	25.00	0.00	في الطريق	\N	2025-11-09 22:10:51	2025-11-09 22:10:51
54	25	50	1	2	1500.00	20.00	0.00	في الطريق	\N	2025-11-09 22:10:51	2025-11-09 22:10:51
55	26	55	4	1	1300.00	0.00	0.00	زهران	\N	2025-11-09 22:21:38	2025-11-09 22:21:38
56	26	54	4	1	1000.00	0.00	0.00	زهران	\N	2025-11-09 22:21:38	2025-11-09 22:21:38
57	26	53	4	1	800.00	0.00	0.00	زهران	\N	2025-11-09 22:21:38	2025-11-09 22:21:38
58	26	56	4	1	2000.00	0.00	0.00	زهران	\N	2025-11-09 22:21:38	2025-11-09 22:21:38
59	26	57	3	1	2000.00	60.00	0.00	زهران	\N	2025-11-09 22:21:38	2025-11-09 22:21:38
60	27	15	2	1	2000.00	0.00	0.00	فيصل	\N	2025-11-10 12:33:35	2025-11-10 12:33:35
61	23	47	3	1	200.00	25.00	0.00	محمد فادي	\N	2025-11-10 22:19:03	2025-11-10 22:19:03
62	23	48	8	1	800.00	37.50	0.00	جهاد فادي	\N	2025-11-10 22:19:03	2025-11-10 22:19:03
63	28	63	3	1	2000.00	35.00	0.00	علي	\N	2025-11-12 12:42:25	2025-11-12 12:42:25
64	29	64	2	1	10000.00	10.00	0.00	\N	\N	2025-11-12 14:34:59	2025-11-12 14:34:59
65	30	65	5	2	8000.00	25.00	0.00	\N	\N	2025-11-12 17:37:52	2025-11-12 17:37:52
66	31	66	2	1	7000.00	50.00	0.00	\N	\N	2025-11-13 10:36:37	2025-11-13 10:36:37
67	32	67	2	1	5000.00	0.00	0.00	تكسي	\N	2025-11-13 22:53:04	2025-11-13 22:53:04
68	33	71	3	25	20.00	50.00	0.00	\N	\N	2025-11-16 20:15:17	2025-11-16 20:15:17
69	34	71	3	15	16.00	0.00	0.00	\N	\N	2025-11-16 20:16:55	2025-11-16 20:16:55
70	35	70	3	1	850.00	0.00	0.00	\N	\N	2025-11-16 20:19:31	2025-11-16 20:19:31
71	36	72	3	1	250.00	20.00	0.00	\N	\N	2025-11-17 15:03:27	2025-11-17 15:03:27
72	36	73	3	2	50.00	30.00	0.00	\N	\N	2025-11-17 15:03:27	2025-11-17 15:03:27
73	37	74	3	1	200.00	0.00	0.00	\N	\N	2025-11-17 15:07:31	2025-11-17 15:07:31
74	38	75	1	1	7500.00	0.00	0.00	\N	\N	2025-11-25 10:43:07	2025-11-25 10:43:07
75	39	20	2	1	13000.00	0.00	0.00	\N	\N	2025-11-25 10:48:00	2025-11-25 10:48:00
76	40	77	2	1	3500.00	0.00	0.00	\N	\N	2025-11-25 11:00:04	2025-11-25 11:00:04
77	41	78	3	4	600.00	0.00	0.00	\N	\N	2025-11-25 13:19:19	2025-11-25 13:19:19
78	41	80	3	4	250.00	0.00	0.00	\N	\N	2025-11-25 13:19:19	2025-11-25 13:19:19
79	41	79	3	1	2000.00	0.00	0.00	\N	\N	2025-11-25 13:19:19	2025-11-25 13:19:19
80	41	82	3	5	350.00	0.00	0.00	\N	\N	2025-11-25 13:19:19	2025-11-25 13:19:19
81	41	81	3	4	250.00	0.00	0.00	\N	\N	2025-11-25 13:19:19	2025-11-25 13:19:19
82	42	85	3	1	1200.00	0.00	0.00	\N	\N	2025-11-25 13:31:38	2025-11-25 13:31:38
83	43	84	3	2	200.00	50.00	0.00	\N	\N	2025-11-25 13:33:29	2025-11-25 13:33:29
84	44	86	3	3	300.00	0.00	0.00	\N	\N	2025-11-25 13:37:35	2025-11-25 13:37:35
85	44	87	3	3	200.00	0.00	0.00	\N	\N	2025-11-25 13:37:35	2025-11-25 13:37:35
86	44	24	3	1	1500.00	0.00	0.00	\N	\N	2025-11-25 13:37:35	2025-11-25 13:37:35
87	44	83	3	15	5.00	0.00	0.00	\N	\N	2025-11-25 13:37:35	2025-11-25 13:37:35
88	45	88	2	1	2000.00	0.00	0.00	\N	\N	2025-11-25 13:40:30	2025-11-25 13:40:30
89	46	89	3	1	1300.00	0.00	0.00	\N	\N	2025-11-25 22:14:03	2025-11-25 22:14:03
90	47	91	8	1	1500.00	0.00	0.00	\N	\N	2025-11-28 14:45:34	2025-11-28 14:45:34
91	48	92	4	1	1500.00	0.00	0.00	\N	\N	2025-11-28 14:59:39	2025-11-28 14:59:39
92	49	94	1	1	29000.00	0.00	0.00	\N	\N	2025-11-28 15:39:29	2025-11-28 15:39:29
93	50	95	6	2	1500.00	0.00	0.00	\N	\N	2025-11-30 07:38:56	2025-11-30 07:38:56
94	51	96	3	4	1200.00	0.00	0.00	\N	\N	2025-11-30 19:46:46	2025-11-30 19:46:46
95	51	97	3	1	1200.00	0.00	0.00	\N	\N	2025-11-30 19:46:46	2025-11-30 19:46:46
96	51	98	3	1	1000.00	0.00	0.00	\N	\N	2025-11-30 19:46:46	2025-11-30 19:46:46
97	52	30	3	1	200.00	25.00	0.00	\N	\N	2025-12-01 14:15:01	2025-12-01 14:15:01
98	53	100	4	2	200.00	0.00	0.00	\N	\N	2025-12-02 20:40:58	2025-12-02 20:40:58
99	53	99	4	2	500.00	0.00	0.00	\N	\N	2025-12-02 20:40:58	2025-12-02 20:40:58
100	54	24	3	1	1500.00	0.00	0.00	\N	\N	2025-12-02 20:42:21	2025-12-02 20:42:21
101	55	100	4	1	200.00	0.00	0.00	\N	\N	2025-12-04 22:42:10	2025-12-04 22:42:10
102	55	101	4	1	650.00	0.00	0.00	\N	\N	2025-12-04 22:42:10	2025-12-04 22:42:10
103	56	102	3	3	800.00	0.00	0.00	\N	\N	2025-12-04 23:05:37	2025-12-04 23:05:37
104	56	103	3	3	300.00	0.00	0.00	\N	\N	2025-12-04 23:05:37	2025-12-04 23:05:37
105	56	104	3	1	800.00	0.00	0.00	\N	\N	2025-12-04 23:05:37	2025-12-04 23:05:37
106	57	106	3	5	80.00	0.00	0.00	\N	\N	2025-12-05 19:52:44	2025-12-05 19:52:44
107	57	105	3	217	20.00	50.00	0.00	\N	\N	2025-12-05 19:52:44	2025-12-05 19:52:44
108	57	107	3	14	20.00	0.00	0.00	\N	\N	2025-12-05 19:52:44	2025-12-05 19:52:44
109	58	109	3	1	350.00	0.00	0.00	\N	\N	2025-12-08 23:15:19	2025-12-08 23:15:19
110	58	108	3	1	1200.00	0.00	0.00	\N	\N	2025-12-08 23:15:19	2025-12-08 23:15:19
111	59	81	3	4	250.00	0.00	0.00	\N	\N	2025-12-08 23:18:26	2025-12-08 23:18:26
112	60	110	10	2600	10.00	15.00	0.00	\N	\N	2025-12-09 23:16:00	2025-12-09 23:16:00
113	61	15	2	1	2000.00	0.00	0.00	\N	\N	2025-12-14 14:04:29	2025-12-14 14:04:29
114	62	112	2	2	500.00	0.00	0.00	\N	\N	2025-12-14 14:07:06	2025-12-14 14:07:06
\.


--
-- Data for Name: sale_return_lines; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sale_return_lines (id, sale_return_id, product_id, warehouse_id, quantity, unit_price, notes, condition, liability_party) FROM stdin;
1	2	47	3	1	150.00	\N	GOOD	\N
2	2	48	8	1	500.00	\N	GOOD	\N
\.


--
-- Data for Name: sale_returns; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sale_returns (id, sale_id, customer_id, warehouse_id, reason, status, notes, total_amount, tax_rate, tax_amount, currency, fx_rate_used, fx_rate_source, fx_rate_timestamp, fx_base_currency, fx_quote_currency, credit_note_id, created_at, updated_at) FROM stdin;
1	23	18	3	خربان	CANCELLED	\N	0.00	0.00	0.00	ILS	\N	\N	\N	\N	\N	\N	2025-12-08 23:24:46	2025-12-08 23:24:59
2	23	18	3	خربان	CONFIRMED	\N	650.00	0.00	0.00	ILS	\N	\N	\N	\N	\N	\N	2025-12-08 23:26:03	2025-12-08 23:26:03
\.


--
-- Data for Name: sales; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sales (id, sale_number, sale_date, customer_id, seller_id, seller_employee_id, preorder_id, tax_rate, discount_total, notes, receiver_name, status, payment_status, currency, fx_rate_used, fx_rate_source, fx_rate_timestamp, fx_base_currency, fx_quote_currency, shipping_address, billing_address, shipping_cost, total_amount, total_paid, balance_due, refunded_total, refund_of_id, idempotency_key, cancelled_at, cancelled_by, cancel_reason, is_archived, archived_at, archived_by, archive_reason, cost_center_id, created_at, updated_at) FROM stdin;
1	SAL20251023-0001	2025-10-23 23:45:00	1	1	\N	\N	0.00	0.00		\N	CONFIRMED	PARTIAL	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	283000.00	90000.00	193000.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-10-23 20:50:04	2025-11-12 22:19:03
2	SAL20251024-0001	2025-10-24 21:28:00	2	1	\N	\N	0.00	0.00			CONFIRMED	PARTIAL	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	55500.00	43500.00	12000.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-10-24 18:36:54	2025-11-28 21:54:57
3	SAL20251025-0001	2025-10-26 01:17:00	2	1	\N	\N	0.00	0.00	استلمت	سعيد	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	2500.00	0.00	2500.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-10-25 22:18:44	2025-10-25 22:18:44
4	SAL20251026-0001	2025-10-26 19:31:00	4	1	\N	\N	0.00	0.00		منصور	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	5000.00	5000.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-10-26 17:32:38	2025-11-12 22:19:03
5	SAL20251029-0001	2025-10-29 20:17:00	5	1	\N	\N	0.00	500.00		يوسف	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	2500.00	2500.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-10-29 18:17:58	2025-11-12 22:19:03
6	SAL20251029-0002	2025-10-29 20:22:00	5	1	\N	\N	0.00	100.00		يوسف	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	300.00	0.00	300.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-10-29 18:22:54	2025-10-29 18:22:54
7	SAL20251029-0003	2025-10-29 20:23:00	6	1	\N	\N	0.00	1800.00		اخو وليد	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	2700.00	2700.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-10-29 18:24:17	2025-11-12 22:19:03
8	SAL20251029-0004	2025-10-29 22:33:00	8	1	\N	\N	0.00	2000.00		محمد	CONFIRMED	PARTIAL	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	7000.00	3000.00	4000.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-10-29 20:34:53	2025-11-12 22:19:03
9	SAL20251103-0001	2025-11-03 16:03:00	6	1	\N	\N	0.00	1800.00	\N	اخو وليد	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	2700.00	2700.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-03 14:04:32	2025-11-12 22:19:03
10	SAL20251104-0001	2025-11-04 14:13:00	9	1	\N	\N	0.00	4000.00	\N	احمد ياسين	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	3000.00	3000.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-04 12:14:19	2025-11-12 22:19:03
11	SAL20251104-0002	2025-11-04 14:33:00	10	1	\N	\N	0.00	0.00	تم البيع مع التركيب	عارف	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	40000.00	40000.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-04 12:34:30	2025-11-12 22:19:03
12	SAL20251104-0003	2025-11-04 16:53:00	11	1	\N	\N	0.00	2500.00	\N	سميح	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	5500.00	5500.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-04 14:55:36	2025-11-12 22:19:03
13	SAL20251106-0001	2025-11-06 14:45:00	1	1	\N	\N	0.00	1600.00	\N	عامر	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	1400.00	1400.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-06 12:47:12	2025-11-12 22:19:03
14	SAL20251107-0001	2025-11-07 16:38:00	13	1	\N	\N	0.00	0.00	\N	يوسف	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	1900.00	0.00	1900.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-07 14:40:07	2025-11-07 14:40:07
15	SAL20251107-0002	2025-11-07 17:32:00	14	1	\N	\N	0.00	0.00	لعطية طولكرم	ابو فارس	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	7000.00	0.00	7000.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-07 15:34:26	2025-11-07 15:34:26
16	SAL20251107-0003	2025-11-07 17:34:00	14	1	\N	\N	0.00	500.00	\N	ابو فارس	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	3500.00	0.00	3500.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-07 15:35:51	2025-11-07 15:35:51
17	SAL20251107-0004	2025-11-07 17:36:00	14	1	\N	\N	0.00	10000.00	\N	ابو فارس	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	50000.00	0.00	50000.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-07 15:37:08	2025-11-07 15:37:09
18	SAL20251107-0005	2025-11-07 17:37:00	14	1	\N	\N	0.00	5000.00	لعز الزايد	ابو فارس	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	30000.00	0.00	30000.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-07 15:38:49	2025-11-07 15:38:49
19	SAL20251107-0006	2025-11-07 17:39:00	14	1	\N	\N	0.00	500.00	\N	ابو فارس	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	1300.00	0.00	1300.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-07 15:40:41	2025-11-07 15:40:41
20	SAL20251107-0007	2025-11-07 17:40:00	14	1	\N	\N	0.00	0.00	\N	ابو فارس	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	200.00	0.00	200.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-07 15:41:37	2025-11-07 15:41:37
21	SAL20251107-0008	2025-11-07 17:43:00	14	1	\N	\N	0.00	0.00	\N	ابو فارس	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	200.00	0.00	200.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-07 15:44:16	2025-11-07 15:44:16
22	SAL20251109-0001	2025-11-09 22:45:00	17	1	3	\N	0.00	300.00	\N	تكسي	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	500.00	500.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-09 20:47:15	2025-11-12 22:19:03
23	SAL20251109-0002	2025-11-09 23:22:00	18	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	650.00	0.00	650.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-09 21:26:18	2025-11-10 22:19:03
24	SAL20251109-0003	2025-11-09 23:53:00	19	1	3	\N	0.00	0.00	استلم طرمبة وباقي 3	\N	CONFIRMED	PARTIAL	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	13000.00	12500.00	500.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-09 21:55:58	2025-12-06 17:21:34
25	SAL20251109-0004	2025-11-09 23:57:00	19	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	12100.00	0.00	12100.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-09 22:10:51	2025-11-09 22:10:51
26	SAL20251109-0005	2025-11-10 00:11:00	20	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	5900.00	0.00	5900.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-09 22:17:09	2025-11-09 22:21:38
27	SAL20251110-0001	2025-11-10 14:31:00	21	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	2000.00	2000.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-10 12:33:35	2025-11-12 22:19:03
28	SAL20251112-0001	2025-11-12 14:41:00	23	1	3	\N	0.00	0.00	\N	علي	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	1300.00	0.00	1300.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-12 12:42:25	2025-11-12 12:42:25
29	SAL20251112-0002	2025-11-12 16:34:00	24	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	9000.00	0.00	9000.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-12 14:34:59	2025-11-12 14:34:59
30	SAL20251112-0003	2025-11-12 19:36:00	25	1	3	\N	0.00	0.00	\N	فادي	CONFIRMED	PARTIAL	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	12000.00	4000.00	8000.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-12 17:37:52	2025-12-05 20:01:53
31	SAL20251113-0001	2025-11-13 12:34:00	27	1	3	\N	0.00	0.00	\N	احمد	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	3500.00	0.00	3500.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-13 10:36:37	2025-11-13 10:36:37
32	SAL20251113-0002	2025-11-14 00:52:00	28	1	3	\N	0.00	2300.00	\N	\N	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	2700.00	2700.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-13 22:53:04	2025-11-16 20:01:17
33	SAL20251116-0001	2025-11-16 22:14:00	30	1	3	\N	0.00	0.00	\N	الشيخ	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	250.00	250.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-16 20:15:17	2025-11-16 20:15:45
34	SAL20251116-0002	2025-11-16 22:16:00	31	1	3	\N	0.00	10.00	\N	\N	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	230.00	230.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-16 20:16:55	2025-11-16 20:17:12
35	SAL20251116-0003	2025-11-16 22:18:00	32	1	3	\N	0.00	100.00	\N	\N	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	750.00	750.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-16 20:19:31	2025-11-16 20:19:52
36	SAL20251117-0001	2025-11-17 17:02:00	32	1	1	\N	0.00	0.00	\N	\N	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	270.00	270.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-17 15:03:27	2025-11-17 15:08:25
37	SAL20251117-0002	2025-11-17 17:07:00	32	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	200.00	200.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-17 15:07:31	2025-11-17 15:08:01
38	SAL20251125-0001	2025-11-25 12:42:00	1	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	7500.00	0.00	7500.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-25 10:43:07	2025-11-25 10:43:07
39	SAL20251125-0002	2025-11-25 12:47:00	37	1	3	\N	0.00	3000.00	\N	سامح	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	10000.00	0.00	10000.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-25 10:48:00	2025-11-25 10:48:00
40	SAL20251125-0003	2025-11-25 12:58:00	2	1	3	\N	0.00	1000.00	\N	اياد	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	2500.00	0.00	2500.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-25 11:00:04	2025-11-25 11:00:04
41	SAL20251125-0004	2025-11-25 15:15:00	38	1	3	\N	0.00	2950.00	\N	موسى	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	5200.00	5200.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-25 13:19:19	2025-11-25 13:20:07
42	SAL20251125-0005	2025-11-25 15:31:00	13	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	1200.00	0.00	1200.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-25 13:31:38	2025-11-25 13:31:38
43	SAL20251125-0006	2025-11-25 15:32:00	13	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	200.00	0.00	200.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-25 13:33:29	2025-11-25 13:33:29
44	SAL20251125-0007	2025-11-25 15:35:00	39	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	3075.00	0.00	3075.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-25 13:36:04	2025-11-25 13:37:35
45	SAL20251125-0008	2025-11-25 15:39:00	27	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PARTIAL	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	2000.00	1800.00	200.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-25 13:40:30	2025-11-25 13:40:54
46	SAL20251125-0009	2025-11-26 00:13:00	32	1	3	\N	0.00	300.00	\N	\N	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	1000.00	1000.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-25 22:14:03	2025-11-25 22:14:29
47	SAL20251128-0001	2025-11-28 16:45:00	32	1	3	\N	0.00	1050.00	\N	\N	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	450.00	450.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-28 14:45:34	2025-11-28 14:45:54
48	SAL20251128-0002	2025-11-28 16:58:00	32	1	3	\N	0.00	700.00	\N	\N	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	800.00	800.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-28 14:59:39	2025-11-28 14:59:54
49	SAL20251128-0003	2025-11-28 17:39:00	32	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	29000.00	29000.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-28 15:39:29	2025-11-28 15:39:51
50	SAL20251130-0001	2025-11-30 09:38:00	32	1	3	\N	0.00	1800.00	\N	\N	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	1200.00	1200.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-30 07:38:56	2025-11-30 07:39:43
51	SAL20251130-0002	2025-11-30 21:43:00	36	1	3	\N	0.00	2900.00	\N	\N	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	4100.00	0.00	4100.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-30 19:46:46	2025-11-30 19:46:46
52	SAL20251201-0001	2025-12-01 16:14:00	32	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	150.00	150.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-12-01 14:15:01	2025-12-01 14:16:21
53	SAL20251202-0001	2025-12-02 22:40:00	13	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	1400.00	0.00	1400.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-12-02 20:40:58	2025-12-02 20:40:58
54	SAL20251202-0002	2025-12-02 22:41:00	17	1	3	\N	0.00	300.00	\N	\N	CONFIRMED	PAID	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	1200.00	1200.00	0.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-12-02 20:42:21	2025-12-02 20:42:39
55	SAL20251204-0001	2025-12-05 00:37:00	13	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	850.00	0.00	850.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-12-04 22:42:10	2025-12-04 22:42:10
56	SAL20251204-0002	2025-12-05 01:03:00	34	1	3	\N	0.00	0.00	\N	عمار	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	4100.00	0.00	4100.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-12-04 23:05:37	2025-12-04 23:05:37
57	SAL20251205-0001	2025-12-05 21:51:00	14	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	2850.00	0.00	2850.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-12-05 19:52:44	2025-12-05 19:52:44
58	SAL20251208-0001	2025-12-09 01:14:00	13	1	1	\N	0.00	0.00	\N	\N	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	1550.00	0.00	1550.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-12-08 23:15:19	2025-12-08 23:15:19
59	SAL20251208-0002	2025-12-09 01:17:00	34	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	1000.00	0.00	1000.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-12-08 23:18:26	2025-12-08 23:18:26
60	SAL20251209-0001	2025-12-10 01:14:00	1	1	3	\N	0.00	100.00	شحن محرك بكار عدد 2	\N	CONFIRMED	PARTIAL	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	22000.00	10000.00	12000.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-12-09 23:16:00	2025-12-09 23:16:25
61	SAL20251214-0001	2025-12-14 16:01:00	2	1	3	\N	0.00	0.00	\N	سعيد	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	2000.00	0.00	2000.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-12-14 14:04:29	2025-12-14 14:04:29
62	SAL20251214-0002	2025-12-14 16:06:00	2	1	3	\N	0.00	0.00	\N	\N	CONFIRMED	PENDING	ILS	\N	\N	\N	\N	\N	\N	\N	0.00	1000.00	0.00	1000.00	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-12-14 14:07:06	2025-12-14 14:07:06
\.


--
-- Data for Name: service_parts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.service_parts (id, service_id, part_id, warehouse_id, quantity, unit_price, discount, tax_rate, note, notes, partner_id, share_percentage, created_at, updated_at) FROM stdin;
1	1	26	4	4	2000.00	3000.00	0.00	\N	\N	\N	0.00	2025-10-31 22:46:27	2025-10-31 22:46:27
2	3	46	3	1	450.00	150.00	0.00	\N	\N	\N	0.00	2025-11-10 22:21:13	2025-11-10 22:21:13
3	3	62	3	1	350.00	100.00	0.00	\N	\N	\N	0.00	2025-11-10 22:22:02	2025-11-10 22:22:02
4	3	61	4	3	250.00	0.00	0.00	\N	\N	\N	0.00	2025-11-13 12:18:34	2025-11-13 12:18:34
\.


--
-- Data for Name: service_requests; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.service_requests (id, service_number, customer_id, mechanic_id, vehicle_type_id, status, priority, vehicle_vrn, vehicle_model, chassis_number, engineer_notes, description, estimated_duration, actual_duration, estimated_cost, total_cost, start_time, end_time, problem_description, diagnosis, resolution, notes, received_at, started_at, expected_delivery, completed_at, currency, fx_rate_used, fx_rate_source, fx_rate_timestamp, fx_base_currency, fx_quote_currency, tax_rate, discount_total, parts_total, labor_total, total_amount, consume_stock, warranty_days, refunded_total, refund_of_id, idempotency_key, cancelled_at, cancelled_by, cancel_reason, is_archived, archived_at, archived_by, archive_reason, cost_center_id, created_at, updated_at) FROM stdin;
1	SRV-20251031211614	7	\N	1	COMPLETED	MEDIUM	123	2020	\N	\N	\N	120	99	\N	6000.00	\N	\N		\N	\N	\N	2025-10-31 21:16:14.662452	2025-10-31 21:16:25.262323	\N	2025-10-31 22:55:46.869681	ILS	\N	\N	\N	\N	\N	0.00	0.00	5000.00	1000.00	6000.00	f	0	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-10-31 21:16:14	2025-10-31 22:55:46
2	SRV-20251109205633	18	\N	2	COMPLETED	URGENT	1234	\N	\N	\N	\N	2000	1	\N	3500.00	\N	\N		\N	\N	\N	2025-11-09 20:56:33.250172	2025-11-09 20:56:40.193753	\N	2025-11-09 20:58:02.555406	ILS	\N	\N	\N	\N	\N	0.00	0.00	0.00	3500.00	3500.00	f	0	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-09 20:56:33	2025-11-09 20:58:02
3	SRV-20251110222022	18	\N	3	COMPLETED	HIGH	222	\N	\N	\N	\N	240	3899	\N	3000.00	\N	\N		\N	\N	\N	2025-11-10 22:20:22.200005	2025-11-10 22:20:35.020823	\N	2025-11-13 15:19:38.781918	ILS	\N	\N	\N	\N	\N	0.00	0.00	1300.00	1300.00	2600.00	f	0	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-10 22:20:22	2025-11-13 15:19:38
4	SRV-20251125105207	18	\N	4	COMPLETED	URGENT	000000	\N	\N	\N	\N	10	0	\N	1800.00	\N	\N	تصليح طرمبة تحضير	\N	\N	\N	2025-11-25 10:52:07.559233	2025-11-25 10:52:15.970952	\N	2025-11-25 10:52:55.969844	ILS	\N	\N	\N	\N	\N	0.00	0.00	0.00	1800.00	1800.00	f	0	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-25 10:52:07	2025-11-25 10:52:55
5	SRV-20251128143547	20	\N	\N	COMPLETED	URGENT	52524	\N	\N	\N	\N	200	0	\N	10000.00	\N	\N		\N	\N	\N	2025-11-28 14:35:47.781691	2025-11-28 14:35:52.18203	\N	2025-11-28 14:36:32.864836	ILS	\N	\N	\N	\N	\N	0.00	0.00	0.00	10000.00	10000.00	f	0	0.00	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	2025-11-28 14:35:47	2025-11-28 14:36:32
\.


--
-- Data for Name: service_tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.service_tasks (id, service_id, partner_id, share_percentage, description, quantity, unit_price, discount, tax_rate, note, created_at, updated_at) FROM stdin;
1	1	\N	0.00	تغيير بخاخات+فحص	1	1000.00	0.00	0.00	تغيير بخاخات+فحص	2025-10-31 22:47:06	2025-10-31 22:47:06
2	2	\N	0.00	تصليح جدلة كهرباء	1	2000.00	0.00	0.00	\N	2025-11-09 20:57:14	2025-11-09 20:57:14
3	2	\N	0.00	فحص كمبيوتر	1	1500.00	0.00	0.00	\N	2025-11-09 20:57:47	2025-11-09 20:57:47
4	3	\N	0.00	تصليح جدلة كهرباة وفحص واجرة عمل	1	1300.00	0.00	0.00	\N	2025-11-10 22:25:56	2025-11-10 22:25:56
5	4	\N	0.00	تصليح طرمبة تحضير	1	1800.00	0.00	0.00	\N	2025-11-25 10:52:46	2025-11-25 10:52:46
6	5	\N	0.00	تصليح طرمبة مني باجر بوبكات	1	10000.00	0.00	0.00	\N	2025-11-28 14:36:28	2025-11-28 14:36:28
\.


--
-- Data for Name: shipment_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.shipment_items (id, shipment_id, product_id, warehouse_id, quantity, unit_cost, declared_value, landed_extra_share, landed_unit_cost, notes) FROM stdin;
\.


--
-- Data for Name: shipment_partners; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.shipment_partners (id, shipment_id, partner_id, identity_number, phone_number, address, unit_price_before_tax, expiry_date, share_percentage, share_amount, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: shipments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.shipments (id, number, shipment_number, date, shipment_date, expected_arrival, actual_arrival, delivered_date, origin, destination, destination_id, status, value_before, shipping_cost, customs, vat, insurance, total_cost, carrier, tracking_number, notes, currency, fx_rate_used, fx_rate_source, fx_rate_timestamp, fx_base_currency, fx_quote_currency, sale_id, weight, dimensions, package_count, priority, delivery_method, delivery_instructions, customs_declaration, customs_cleared_date, delivery_attempts, last_delivery_attempt, return_reason, is_archived, archived_at, archived_by, archive_reason, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sites; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sites (id, branch_id, name, code, is_active, address, city, geo_lat, geo_lng, manager_user_id, manager_employee_id, notes, is_archived, archived_at, archived_by, archive_reason, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: stock_adjustment_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.stock_adjustment_items (id, adjustment_id, product_id, warehouse_id, quantity, unit_cost, notes) FROM stdin;
\.


--
-- Data for Name: stock_adjustments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.stock_adjustments (id, date, warehouse_id, reason, notes, total_cost, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: stock_levels; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.stock_levels (id, product_id, warehouse_id, quantity, reserved_quantity, min_stock, max_stock, created_at, updated_at) FROM stdin;
1	1	1	4	0	\N	\N	2025-10-23 20:25:39	2025-11-04 21:15:18
2	2	1	2	0	\N	\N	2025-10-23 20:27:38	2025-11-04 21:15:18
3	3	1	7	0	\N	\N	2025-10-23 20:30:29	2025-11-04 21:15:18
4	4	1	4	0	\N	\N	2025-10-23 20:31:34	2025-11-04 21:15:18
5	5	1	10	0	\N	\N	2025-10-23 20:33:31	2025-11-04 21:15:18
6	6	1	1	0	\N	\N	2025-10-23 20:35:21	2025-11-04 21:15:18
7	7	1	1	0	\N	\N	2025-10-23 20:38:23	2025-11-04 21:15:18
8	8	1	1	0	\N	\N	2025-10-23 20:39:11	2025-11-04 21:15:18
9	9	1	1	0	\N	\N	2025-10-23 20:40:24	2025-11-04 21:15:18
10	10	1	1	0	\N	\N	2025-10-23 20:41:13	2025-11-04 21:15:18
11	11	2	25	0	\N	\N	2025-10-24 16:37:25	2025-11-04 21:14:35
12	12	2	20	0	\N	\N	2025-10-24 16:41:06	2025-11-04 21:14:35
13	13	2	10	0	\N	\N	2025-10-24 16:43:36	2025-11-04 21:14:35
14	14	2	8	0	\N	\N	2025-10-24 16:45:23	2025-11-04 21:14:35
15	15	2	7	0	\N	\N	2025-10-24 16:50:11	2025-12-14 14:04:29
16	16	2	10	0	\N	\N	2025-10-24 16:51:46	2025-11-04 21:14:35
17	17	2	3	0	\N	\N	2025-10-24 16:52:54	2025-11-04 21:14:35
18	18	2	1	0	\N	\N	2025-10-24 16:54:10	2025-11-04 21:14:35
19	19	2	10	0	\N	\N	2025-10-24 16:55:14	2025-11-04 21:14:35
20	20	2	24	0	\N	\N	2025-10-24 17:13:04	2025-11-25 10:48:00
21	21	2	10	0	\N	\N	2025-10-25 22:16:37	2025-11-04 21:14:35
22	22	2	0	0	\N	\N	2025-10-26 11:46:10	2025-10-26 17:32:38
23	23	2	1	0	\N	\N	2025-10-29 12:40:04	2025-10-29 18:18:36
24	24	3	26	0	\N	\N	2025-10-29 17:33:16	2025-12-02 20:42:39
25	25	3	18	0	\N	\N	2025-10-29 18:21:59	2025-10-29 18:22:54
26	26	4	20	0	\N	\N	2025-10-29 18:33:45	2025-10-29 18:33:45
27	27	2	1	0	\N	\N	2025-10-29 20:33:20	2025-10-29 20:34:53
28	28	5	0	0	\N	\N	2025-11-04 12:32:07	2025-11-04 12:34:30
29	29	3	10	0	\N	\N	2025-11-04 14:51:47	2025-11-04 15:00:39
30	30	3	48	0	\N	\N	2025-11-05 22:45:34	2025-12-01 14:16:21
31	31	3	6	0	\N	\N	2025-11-06 12:45:18	2025-11-06 12:48:18
32	32	3	4	0	\N	\N	2025-11-07 14:27:21	2025-11-07 14:40:07
33	33	3	29	0	\N	\N	2025-11-07 14:28:33	2025-11-07 14:40:07
34	34	3	4	0	\N	\N	2025-11-07 14:29:35	2025-11-07 14:40:07
35	35	6	4	0	\N	\N	2025-11-07 14:31:52	2025-11-07 14:40:07
36	36	3	499	0	\N	\N	2025-11-07 14:33:10	2025-11-07 14:40:07
37	37	7	0	0	\N	\N	2025-11-07 15:18:02	2025-11-07 15:37:09
38	38	5	0	0	\N	\N	2025-11-07 15:19:03	2025-11-07 15:38:49
39	39	2	0	0	\N	\N	2025-11-07 15:21:12	2025-11-07 15:34:26
40	40	6	0	0	\N	\N	2025-11-07 15:23:06	2025-11-07 15:40:41
41	41	6	0	0	\N	\N	2025-11-07 15:24:32	2025-11-07 15:40:41
42	42	3	2	0	\N	\N	2025-11-07 15:27:02	2025-11-07 15:35:51
43	43	3	48	0	\N	\N	2025-11-07 15:30:41	2025-11-07 15:41:37
44	44	6	9	0	\N	\N	2025-11-07 15:43:08	2025-11-07 15:44:16
45	45	6	0	0	\N	\N	2025-11-09 20:45:38	2025-11-09 20:47:31
46	46	3	29	1	\N	\N	2025-11-09 21:08:02	2025-11-10 22:19:03
47	47	3	5	1	\N	\N	2025-11-09 21:08:44	2025-11-10 22:19:03
48	48	8	5	1	\N	\N	2025-11-09 21:11:09	2025-11-10 22:19:03
49	49	1	0	0	\N	\N	2025-11-09 21:29:29	2025-11-09 22:10:51
50	50	1	0	0	\N	\N	2025-11-09 21:30:20	2025-11-09 22:10:51
51	51	1	1	0	\N	\N	2025-11-09 21:32:01	2025-11-09 22:10:51
52	52	1	8	0	\N	\N	2025-11-09 21:33:13	2025-11-09 22:10:51
53	53	4	4	1	\N	\N	2025-11-09 21:40:04	2025-11-09 22:21:38
54	54	4	4	1	\N	\N	2025-11-09 21:41:14	2025-11-09 22:21:38
55	55	4	4	1	\N	\N	2025-11-09 21:41:51	2025-11-09 22:21:38
56	56	4	2	1	\N	\N	2025-11-09 21:44:27	2025-11-09 22:21:38
57	57	3	4	1	\N	\N	2025-11-09 21:46:05	2025-11-09 22:21:38
58	58	2	1	0	\N	\N	2025-11-09 21:51:23	2025-11-09 21:55:58
59	59	8	0	0	\N	\N	2025-11-09 21:51:55	2025-11-09 22:10:51
60	60	8	9	0	\N	\N	2025-11-09 21:52:37	2025-11-09 22:10:51
61	61	4	12	0	\N	\N	2025-11-10 22:10:34	2025-11-10 22:10:34
62	62	3	5	0	\N	\N	2025-11-10 22:11:36	2025-11-10 22:11:36
63	63	3	4	0	\N	\N	2025-11-12 12:36:03	2025-11-12 12:42:25
64	64	2	2	0	\N	\N	2025-11-12 14:20:54	2025-11-12 14:34:59
65	65	5	0	0	\N	\N	2025-11-12 17:36:15	2025-11-12 17:37:52
66	66	2	0	0	\N	\N	2025-11-13 10:34:07	2025-11-13 10:36:37
67	67	2	3	0	\N	\N	2025-11-13 22:50:58	2025-11-16 20:01:17
68	68	9	1	0	\N	\N	2025-11-15 13:06:16	2025-11-15 13:06:29
69	69	9	1	0	\N	\N	2025-11-16 19:32:03	2025-11-16 19:32:17
70	70	3	18	0	\N	\N	2025-11-16 20:02:45	2025-11-16 20:19:52
71	71	3	420	0	\N	\N	2025-11-16 20:04:26	2025-11-16 20:17:12
72	72	3	8	0	\N	\N	2025-11-17 14:59:06	2025-11-17 15:08:25
73	73	3	46	0	\N	\N	2025-11-17 14:59:54	2025-11-17 15:08:25
74	74	3	28	0	\N	\N	2025-11-17 15:05:02	2025-11-17 15:08:01
75	75	1	0	0	\N	\N	2025-11-25 10:42:22	2025-11-25 10:43:07
76	76	2	20	0	\N	\N	2025-11-25 10:46:47	2025-11-25 10:46:47
77	77	2	4	0	\N	\N	2025-11-25 10:58:29	2025-11-25 11:00:04
78	78	3	32	0	\N	\N	2025-11-25 13:09:05	2025-11-25 13:20:07
79	79	3	3	0	\N	\N	2025-11-25 13:10:36	2025-11-25 13:20:07
80	80	3	32	0	\N	\N	2025-11-25 13:11:32	2025-11-25 13:20:07
81	81	3	12	0	\N	\N	2025-11-25 13:12:53	2025-12-08 23:18:26
82	82	3	20	0	\N	\N	2025-11-25 13:14:10	2025-11-25 13:20:07
83	83	3	200	0	\N	\N	2025-11-25 13:28:23	2025-11-25 13:28:23
84	84	3	8	0	\N	\N	2025-11-25 13:29:29	2025-11-25 13:33:29
85	85	3	4	0	\N	\N	2025-11-25 13:30:26	2025-11-25 13:31:38
86	86	3	17	3	\N	\N	2025-11-25 13:34:47	2025-11-25 13:37:35
87	87	3	20	0	\N	\N	2025-11-25 13:35:08	2025-11-25 13:35:08
88	88	2	99	0	\N	\N	2025-11-25 13:39:20	2025-11-25 13:40:30
89	89	3	8	0	\N	\N	2025-11-25 22:12:24	2025-11-25 22:14:29
90	90	9	2	0	\N	\N	2025-11-28 14:42:10	2025-11-28 14:42:10
91	91	8	18	0	\N	\N	2025-11-28 14:43:55	2025-11-28 14:45:54
92	92	4	0	0	\N	\N	2025-11-28 14:58:29	2025-11-28 14:59:54
93	93	3	10	0	\N	\N	2025-11-28 15:20:46	2025-11-28 15:20:46
94	94	1	0	0	\N	\N	2025-11-28 15:33:16	2025-11-28 15:39:29
95	95	6	1	0	\N	\N	2025-11-30 07:37:51	2025-11-30 07:39:43
96	96	3	46	0	\N	\N	2025-11-30 19:38:45	2025-11-30 19:46:46
97	97	3	1	0	\N	\N	2025-11-30 19:40:25	2025-11-30 19:46:46
98	98	3	4	0	\N	\N	2025-11-30 19:42:48	2025-11-30 19:46:46
99	99	4	8	0	\N	\N	2025-12-02 20:38:43	2025-12-02 20:40:58
100	100	4	17	0	\N	\N	2025-12-02 20:39:45	2025-12-04 22:42:10
101	101	4	4	0	\N	\N	2025-12-04 22:34:37	2025-12-04 22:42:10
102	102	3	27	0	\N	\N	2025-12-04 22:50:54	2025-12-04 23:05:37
103	103	3	27	0	\N	\N	2025-12-04 22:54:56	2025-12-04 23:05:37
104	104	3	9	0	\N	\N	2025-12-04 22:58:34	2025-12-04 23:05:37
105	105	3	0	0	\N	\N	2025-12-05 19:46:54	2025-12-05 19:52:44
106	106	3	0	0	\N	\N	2025-12-05 19:50:06	2025-12-05 19:52:44
107	107	3	0	0	\N	\N	2025-12-05 19:51:20	2025-12-05 19:52:44
108	108	3	19	0	\N	\N	2025-12-08 23:11:54	2025-12-08 23:15:19
109	109	3	49	0	\N	\N	2025-12-08 23:12:28	2025-12-08 23:15:19
110	110	10	997400	0	\N	\N	2025-12-09 23:14:10	2025-12-09 23:16:01
111	111	1	60	0	\N	\N	2025-12-14 13:57:13	2025-12-14 13:57:13
112	112	2	58	0	\N	\N	2025-12-14 14:06:17	2025-12-14 14:07:06
\.


--
-- Data for Name: supplier_loan_settlements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.supplier_loan_settlements (id, loan_id, supplier_id, settled_price, settlement_date, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: supplier_settlement_lines; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.supplier_settlement_lines (id, settlement_id, source_type, source_id, description, product_id, quantity, unit_price, gross_amount, needs_pricing, cost_source, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: supplier_settlements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.supplier_settlements (id, code, supplier_id, from_date, to_date, currency, fx_rate_used, fx_rate_source, fx_rate_timestamp, fx_base_currency, fx_quote_currency, status, mode, notes, total_gross, total_due, previous_settlement_id, opening_balance, rights_exchange, rights_total, obligations_sales, obligations_services, obligations_preorders, obligations_expenses, obligations_total, payments_out, payments_in, payments_returns, payments_net, closing_balance, is_approved, approved_by, approved_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: suppliers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.suppliers (id, name, is_local, identity_number, contact, phone, email, address, notes, payment_terms, currency, opening_balance, current_balance, exchange_items_balance, sale_returns_balance, sales_balance, services_balance, preorders_balance, payments_in_balance, payments_out_balance, preorders_prepaid_balance, returns_balance, expenses_balance, service_expenses_balance, returned_checks_in_balance, returned_checks_out_balance, customer_id, is_archived, archived_at, archived_by, archive_reason, created_at, updated_at) FROM stdin;
1	ابراهيم قدح	f	\N	\N	0502269197	\N	كفر مندا	\N	\N	ILS	0.00	-33500.00	0.00	0.00	0.00	0.00	0.00	0.00	33500.00	0.00	0.00	0.00	0.00	0.00	0.00	35	f	\N	\N	\N	2025-11-05 22:36:51	2025-12-08 23:10:51
2	مراد المحسيري	f	\N	\N	0522454302	\N	الخضر-بيت لحم	\N	\N	ILS	0.00	-4100.00	60000.00	0.00	4100.00	0.00	0.00	0.00	60000.00	0.00	0.00	0.00	0.00	0.00	0.00	36	f	\N	\N	\N	2025-11-14 20:48:15	2025-12-01 14:09:04
4	اشرف يطاوي بيتونيا	f	\N	\N	\N	\N	بيتونيا-دوار الفواكه	\N	\N	ILS	0.00	0.00	4500.00	0.00	0.00	0.00	0.00	0.00	4500.00	0.00	0.00	0.00	0.00	0.00	0.00	29	f	\N	\N	\N	2025-11-16 19:28:44	2025-11-24 01:40:10
5	اسماعيل ابو خلف	f	\N	\N	0549097681	\N	كفر عقب	\N	\N	ILS	0.00	14200.00	0.00	0.00	0.00	0.00	0.00	0.00	32000.00	0.00	0.00	0.00	46200.00	0.00	0.00	33	f	\N	\N	\N	2025-11-16 20:47:40	2025-11-24 01:40:10
6	سيف بلشة	f	\N	\N	\N	\N	\N	\N	\N	ILS	0.00	0.00	6500.00	0.00	0.00	0.00	0.00	0.00	6500.00	0.00	0.00	0.00	0.00	0.00	0.00	40	f	\N	\N	\N	2025-11-28 14:38:47	2025-11-28 14:42:11
7	بهاء حسونة	f	\N	\N	0597133330	\N	رام الله-بيتونيا	\N	\N	ILS	0.00	-800.00	0.00	0.00	0.00	0.00	0.00	0.00	800.00	0.00	0.00	0.00	0.00	0.00	0.00	41	f	\N	\N	\N	2025-11-28 15:02:46	2025-11-28 15:03:10
8	ايلي مراد قطع	f	\N	\N	0522726056	\N	\N	\N	\N	ILS	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	0.00	42	f	\N	\N	\N	2025-11-28 15:05:15	2025-11-28 15:05:15
9	حسن شهوان	f	\N	\N	0599220101	\N	مزايا مول	تصدير حاويات عدد 5	\N	ILS	84000.00	23000.00	0.00	0.00	0.00	0.00	0.00	0.00	61000.00	0.00	0.00	0.00	0.00	0.00	0.00	43	f	\N	\N	\N	2025-12-14 14:10:32	2025-12-14 14:12:01
\.


--
-- Data for Name: system_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_settings (id, key, value, description, data_type, is_public, created_at, updated_at) FROM stdin;
1	COMPANY_NAME	AZAD	\N	string	f	2025-10-31 12:02:23.696875	2025-10-31 12:02:23.696882
2	CURRENCY_SYMBOL	$	\N	string	f	2025-10-31 12:02:23.70188	2025-10-31 12:02:23.701885
3	TIMEZONE	UTC	\N	string	f	2025-10-31 12:02:23.705164	2025-10-31 12:02:23.70517
4	DATE_FORMAT	%Y-%m-%d	\N	string	f	2025-10-31 12:02:23.707991	2025-10-31 12:02:23.707995
5	TIME_FORMAT	%H:%M:%S	\N	string	f	2025-10-31 12:02:23.710129	2025-10-31 12:02:23.710134
6	default_vat_rate	18.0	نسبة VAT الافتراضية	number	f	2025-10-31 14:45:36.805542	2025-10-31 19:16:11.041588
7	vat_enabled	True	تفعيل VAT	boolean	f	2025-10-31 14:45:36.810462	2025-10-31 19:16:11.046882
8	income_tax_rate	15.0	ضريبة دخل الشركات	number	f	2025-10-31 14:45:36.812443	2025-10-31 19:16:11.052325
9	withholding_tax_rate	5.0	الخصم من المنبع	number	f	2025-10-31 14:45:36.814859	2025-10-31 19:16:11.055069
10	social_insurance_enabled	False	تفعيل التأمينات	boolean	f	2025-10-31 14:45:36.817346	2025-10-31 19:16:11.057356
11	social_insurance_company	7.5	نسبة التأمين - الشركة	number	f	2025-10-31 14:45:36.819927	2025-10-31 19:16:11.059872
12	social_insurance_employee	7.0	نسبة التأمين - الموظف	number	f	2025-10-31 14:45:36.821426	2025-10-31 19:16:11.063096
13	overtime_rate_normal	1.5	معدل العمل الإضافي	number	f	2025-10-31 14:45:36.8233	2025-10-31 19:16:11.067798
14	working_hours_per_day	8.0	ساعات العمل اليومية	number	f	2025-10-31 14:45:36.826127	2025-10-31 19:16:11.070778
15	asset_auto_depreciation	True	استهلاك تلقائي	boolean	f	2025-10-31 14:45:36.82837	2025-10-31 19:16:11.073801
16	asset_threshold_amount	500.0	حد مبلغ الأصول	number	f	2025-10-31 14:45:36.831098	2025-10-31 19:16:11.076149
17	cost_centers_enabled	False	تفعيل مراكز التكلفة	boolean	f	2025-10-31 14:45:36.832893	2025-10-31 19:16:11.077563
18	budgeting_enabled	False	تفعيل الموازنات	boolean	f	2025-10-31 14:45:36.834302	2025-10-31 19:16:11.07855
19	fiscal_year_start_month	1	بداية السنة المالية	number	f	2025-10-31 14:45:36.835568	2025-10-31 19:16:11.079491
20	notify_on_service_complete	True	إشعار اكتمال الصيانة	boolean	f	2025-10-31 14:45:36.83755	2025-10-31 19:16:11.082269
21	notify_on_payment_due	True	إشعار استحقاق الدفعات	boolean	f	2025-10-31 14:45:36.840485	2025-10-31 19:16:11.087491
22	notify_on_low_stock	True	تنبيه انخفاض المخزون	boolean	f	2025-10-31 14:45:36.844337	2025-10-31 19:16:11.089456
23	payment_reminder_days	3.0	التذكير قبل الاستحقاق	number	f	2025-10-31 14:45:36.84811	2025-10-31 19:16:11.091841
24	allow_negative_stock	False	السماح بالمخزون السالب	boolean	f	2025-10-31 14:45:36.850236	2025-10-31 19:16:11.093022
25	require_approval_for_sales_above	10000.0	طلب موافقة للمبيعات الكبيرة	number	f	2025-10-31 14:45:36.851623	2025-10-31 19:16:11.093951
26	discount_max_percent	50.0	الحد الأقصى للخصم	number	f	2025-10-31 14:45:36.852886	2025-10-31 19:16:11.094904
27	credit_limit_check	True	فحص حد الائتمان	boolean	f	2025-10-31 14:45:36.854352	2025-10-31 19:16:11.095821
28	multi_tenancy_enabled	False	تفعيل تعدد المستأجرين	boolean	f	2025-10-31 14:45:36.856388	2025-10-31 19:16:11.096796
29	trial_period_days	30.0	مدة التجريبي	number	f	2025-10-31 14:45:36.860741	2025-10-31 19:16:11.102418
30	twilio_account_sid		Twilio Account SID for SMS/WhatsApp	string	f	2025-10-31 15:31:45.653458	2025-10-31 15:31:45.651679
31	twilio_auth_token		Twilio Auth Token	string	f	2025-10-31 15:31:45.656828	2025-10-31 15:31:45.656539
32	twilio_phone_number		Twilio Phone Number (e.g., +970562150193)	string	f	2025-10-31 15:31:45.659629	2025-10-31 15:31:45.659368
33	twilio_whatsapp_number	whatsapp:+14155238886	Twilio WhatsApp Number	string	f	2025-10-31 15:31:45.662379	2025-10-31 15:31:45.662121
34	inventory_manager_phone		رقم هاتف مدير المخزون للإشعارات	string	f	2025-10-31 15:31:45.667319	2025-10-31 15:31:45.666547
35	inventory_manager_email		بريد مدير المخزون للإشعارات	string	f	2025-10-31 15:31:45.671284	2025-10-31 15:31:45.671032
36	COMPANY_PHONE	+970562150193	\N	string	f	2025-10-31 19:15:50.567923	2025-10-31 19:15:50.567928
37	COMPANY_ADDRESS	رام الله	\N	string	f	2025-10-31 19:16:00.257487	2025-10-31 19:16:00.257494
38	system_health_last_run	{"checks": [{"name": "\\u0642\\u0627\\u0639\\u062f\\u0629 \\u0627\\u0644\\u0628\\u064a\\u0627\\u0646\\u0627\\u062a", "status": "ok", "message": "\\u062a\\u0639\\u0645\\u0644 \\u0628\\u0634\\u0643\\u0644 \\u0635\\u062d\\u064a\\u062d"}, {"name": "\\u0627\\u0644\\u0645\\u0633\\u0627\\u062d\\u0629", "status": "ok", "message": "\\u0645\\u062a\\u0628\\u0642\\u064a 41.53 GB"}, {"name": "\\u0635\\u0644\\u0627\\u062d\\u064a\\u0627\\u062a \\u0627\\u0644\\u0643\\u062a\\u0627\\u0628\\u0629", "status": "ok", "message": "\\u0635\\u0644\\u0627\\u062d\\u064a\\u0627\\u062a \\u0635\\u062d\\u064a\\u062d\\u0629"}, {"name": "\\u0627\\u0644\\u062a\\u0643\\u0627\\u0645\\u0644\\u0627\\u062a", "status": "warning", "message": "\\u0644\\u0627 \\u062a\\u0648\\u062c\\u062f \\u062a\\u0643\\u0627\\u0645\\u0644\\u0627\\u062a"}, {"name": "\\u0627\\u0644\\u0623\\u062f\\u0627\\u0621", "status": "ok", "message": "0ms"}], "score": 93, "time": "2025-12-06T19:19:46.976745"}	\N	json	f	2025-12-06 19:19:46.979635	2025-12-06 19:19:46.977717
\.


--
-- Data for Name: tax_entries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tax_entries (id, entry_type, transaction_type, transaction_id, transaction_reference, tax_rate, base_amount, tax_amount, total_amount, currency, debit_account, credit_account, gl_entry_id, fiscal_year, fiscal_month, tax_period, is_reconciled, is_filed, filing_reference, customer_id, supplier_id, notes, created_at, created_by) FROM stdin;
1	OUTPUT_VAT	SALE	13	SAL20251105-0001	16.00	646.55	103.45	750.00	ILS	\N	\N	\N	2025	11	2025-11	f	f	\N	12	\N	\N	2025-11-05 15:34:45.406653	\N
\.


--
-- Data for Name: transfers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.transfers (id, reference, product_id, source_id, destination_id, quantity, direction, transfer_date, notes, user_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: user_branches; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_branches (id, user_id, branch_id, is_primary, can_manage, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: user_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_permissions (user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, password_hash, role_id, is_active, is_system_account, last_login, last_seen, last_login_ip, login_count, avatar_url, notes_text, created_at, updated_at) FROM stdin;
2	developer	developer@example.com	scrypt:32768:8:1$YhgZfLO2EZpZRohq$64727bcfdd49e4ec1a924159939463cf0265c270d687612a8619d8d84bcf9da58eea900056c68744d65476567cac9feff052f79ccba182e184a5546a1fdc7930	8	t	t	\N	\N	\N	0	\N	\N	2025-12-18 14:28:53.945936	2025-12-18 14:28:53.945936
4	admin	admin@example.com	scrypt:32768:8:1$l9o0c8IcSBaQ8OZH$5cafeb36bee22c89b9a19eadb0ec3e0c4cc6dc4d32ab2aac30f26640e6b061784ba8845734584d2033f3d67d5bdf4dbac4b29eceb312e6dc55d26e3329dc6347	3	t	f	\N	\N	\N	0	\N	\N	2025-12-18 14:28:53.945936	2025-12-18 14:28:53.945936
5	manager	manager@example.com	scrypt:32768:8:1$qFdy0pt1TobNo7Ue$6bffb3794639e0c77ad95a6171aee841fa2349cc23fb1f1ec055f451673d554280836dd5919bb26118cc94ee567147d9894d989bf05d5c0254c1f0f4e1db56ad	10	t	f	\N	\N	\N	0	\N	\N	2025-12-18 14:28:53.945936	2025-12-18 14:28:53.945936
6	staff	staff@example.com	scrypt:32768:8:1$ODM29VwoG7Ui528P$60196af618b270e8eff458ec4a9caa2f89f931a52a4efd866476931597e7f1408aa6dff7c7378322418c0d595f5ea4f85228ed21176332d14bf32de5755f2402	4	t	f	\N	\N	\N	0	\N	\N	2025-12-18 14:28:53.945936	2025-12-18 14:28:53.945936
7	mechanic	mechanic@example.com	scrypt:32768:8:1$87jvvRNs3CIMOpBT$6531e2217d19ea0b0b5dde738537365c4e0a0ef0f8c91b8ce8c577b8528a958b8708685cc1d8c70d3c9fa513e532ad1ed7a6b4dc3f3de26dfcf3ed013c3501b9	5	t	f	\N	\N	\N	0	\N	\N	2025-12-18 14:28:53.945936	2025-12-18 14:28:53.945936
8	customer	customer@example.com	scrypt:32768:8:1$FEPB01Rja8xamYjU$29d3d9fac9edcf0bda8a4e3038bd472736c63be8ca738e28b4e9455405b9037626f1eca1013864181d3493539c0e044d8bd2d6b540c08fde377966780f4548ac	6	t	f	\N	\N	\N	0	\N	\N	2025-12-18 14:28:53.945936	2025-12-18 14:28:53.945936
3	super_admin	rafideen.ahmadghannam@gmail.com	scrypt:32768:8:1$Cvo3wbQW5AOpRdxM$69f52133814793f71ed367aefc2b3e074e17457fb077f0da3512e87c6be7ef4d0c0fe8c8a73e5c7a38ff32db6bbaf233dd7d64e8b46d9bb1b7f996e4d9d543ff	2	t	f	\N	\N	\N	0	\N	\N	2025-12-18 14:28:53.945936	2025-12-19 00:42:58.891305
1	owner	owner@system.local	scrypt:32768:8:1$SEOGuMsCzrYuGGQl$1f0a8738117d448698777340004e26c7381f5c562ecb9a0673187b82c2ce408a4b6dfefb523093a4a8875772656520fe6bdc0e59d0cfdfe217d5fef96f85c146	1	t	t	2025-12-19 22:56:58.040023	2025-12-19 22:56:53.849006	127.0.0.1	218	\N	\N	2025-10-22 18:22:55	2025-12-19 22:56:57.806598
\.


--
-- Data for Name: utility_accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.utility_accounts (id, utility_type, provider, account_no, meter_no, alias, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: warehouse_partner_shares; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.warehouse_partner_shares (id, partner_id, warehouse_id, product_id, share_percentage, share_amount, notes, created_at, updated_at) FROM stdin;
1	1	\N	37	50	15000.00	\N	2025-11-07 15:18:02	2025-11-07 15:18:02
\.


--
-- Data for Name: warehouses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.warehouses (id, name, warehouse_type, location, branch_id, is_active, parent_id, supplier_id, partner_id, share_percent, capacity, current_occupancy, notes, online_slug, online_is_default, created_at, updated_at) FROM stdin;
1	مشتريات للزبائن من دبي	MAIN	دبي الى رام الله	1	t	\N	\N	\N	0.00	5000	0	بضاعة مشترى من دبي لزبائن الضفة	\N	f	2025-10-23 19:37:29	2025-10-23 19:37:29
2	طرمبات هايدروليك	MAIN	المخزن الأزرق	1	t	\N	\N	\N	0.00	10000	0	\N	\N	f	2025-10-24 16:32:15	2025-10-24 16:32:15
3	قطع جديدة	MAIN	المخزن الجديد	1	t	\N	\N	\N	0.00	20000	0	\N	\N	f	2025-10-29 17:32:17	2025-10-29 17:32:17
4	قطع محركات مستعملة	MAIN	\N	1	t	\N	\N	\N	0.00	1000000	0	\N	\N	f	2025-10-29 18:27:55	2025-10-29 18:27:55
5	محركات مستعملة	MAIN	الاحمر	1	t	\N	\N	\N	0.00	50000	0	\N	\N	f	2025-11-04 12:27:36	2025-11-04 12:27:36
6	قطع مستعملة	MAIN	متفرع	1	t	\N	\N	\N	0.00	\N	0	\N	\N	f	2025-11-07 14:30:36	2025-11-07 14:30:36
7	شراكة مع عمار (كاتربلر)	PARTNER	\N	1	t	\N	\N	\N	0.00	1000	0	\N	\N	f	2025-11-07 15:15:14	2025-11-07 15:15:14
8	عدد ومتفرقات	MAIN	متفرع	1	t	\N	\N	\N	0.00	20000	0	\N	\N	f	2025-11-09 21:10:22	2025-11-09 21:10:22
9	معدات واليات	EXCHANGE	\N	1	t	\N	\N	\N	0.00	\N	0	\N	\N	f	2025-11-15 13:03:58	2025-11-15 13:03:58
10	شحن	MAIN	\N	1	t	\N	\N	\N	0.00	\N	0	\N	\N	f	2025-12-09 23:12:44	2025-12-09 23:12:44
\.


--
-- Data for Name: workflow_actions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workflow_actions (id, workflow_instance_id, step_number, step_name, action_type, actor_id, action_date, decision, comments, attachments, delegated_to, delegated_at, duration_hours, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: workflow_definitions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workflow_definitions (id, workflow_code, workflow_name, workflow_name_ar, description, workflow_type, entity_type, steps_definition, auto_start, auto_start_condition, is_active, version, timeout_hours, escalation_rules, created_by, updated_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: workflow_instances; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workflow_instances (id, workflow_definition_id, instance_code, entity_type, entity_id, status, current_step, total_steps, started_by, started_at, completed_at, completed_by, cancelled_at, cancelled_by, cancellation_reason, due_date, context_data, created_at, updated_at) FROM stdin;
\.


--
-- Name: accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.accounts_id_seq', 1, false);


--
-- Name: archives_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.archives_id_seq', 2, false);


--
-- Name: asset_depreciations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.asset_depreciations_id_seq', 1, false);


--
-- Name: asset_maintenance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.asset_maintenance_id_seq', 1, false);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 153, true);


--
-- Name: auth_audit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_audit_id_seq', 1, false);


--
-- Name: bank_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bank_accounts_id_seq', 1, false);


--
-- Name: bank_reconciliations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bank_reconciliations_id_seq', 1, false);


--
-- Name: bank_statements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bank_statements_id_seq', 1, false);


--
-- Name: bank_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bank_transactions_id_seq', 1, false);


--
-- Name: branches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.branches_id_seq', 1, false);


--
-- Name: budget_commitments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.budget_commitments_id_seq', 1, false);


--
-- Name: budgets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.budgets_id_seq', 1, false);


--
-- Name: checks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.checks_id_seq', 1, false);


--
-- Name: cost_allocation_execution_lines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cost_allocation_execution_lines_id_seq', 1, false);


--
-- Name: cost_allocation_executions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cost_allocation_executions_id_seq', 1, false);


--
-- Name: cost_allocation_lines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cost_allocation_lines_id_seq', 1, false);


--
-- Name: cost_allocation_rules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cost_allocation_rules_id_seq', 1, false);


--
-- Name: cost_center_alert_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cost_center_alert_logs_id_seq', 1, false);


--
-- Name: cost_center_alerts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cost_center_alerts_id_seq', 1, false);


--
-- Name: cost_center_allocations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cost_center_allocations_id_seq', 1, false);


--
-- Name: cost_centers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cost_centers_id_seq', 1, false);


--
-- Name: customer_loyalty_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.customer_loyalty_id_seq', 1, false);


--
-- Name: customer_loyalty_points_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.customer_loyalty_points_id_seq', 1, false);


--
-- Name: customers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.customers_id_seq', 44, false);


--
-- Name: deletion_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.deletion_logs_id_seq', 27, false);


--
-- Name: employee_advance_installments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employee_advance_installments_id_seq', 1, false);


--
-- Name: employee_advances_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employee_advances_id_seq', 1, false);


--
-- Name: employee_deductions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employee_deductions_id_seq', 1, false);


--
-- Name: employee_skills_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employee_skills_id_seq', 1, false);


--
-- Name: employees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employees_id_seq', 1, false);


--
-- Name: engineering_skills_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.engineering_skills_id_seq', 1, false);


--
-- Name: engineering_tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.engineering_tasks_id_seq', 1, false);


--
-- Name: engineering_team_members_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.engineering_team_members_id_seq', 1, false);


--
-- Name: engineering_teams_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.engineering_teams_id_seq', 1, false);


--
-- Name: engineering_timesheets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.engineering_timesheets_id_seq', 1, false);


--
-- Name: equipment_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_types_id_seq', 5, false);


--
-- Name: exchange_rates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exchange_rates_id_seq', 7, false);


--
-- Name: exchange_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exchange_transactions_id_seq', 4, false);


--
-- Name: expense_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expense_types_id_seq', 46, true);


--
-- Name: expenses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expenses_id_seq', 1, false);


--
-- Name: fixed_asset_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fixed_asset_categories_id_seq', 1, false);


--
-- Name: fixed_assets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fixed_assets_id_seq', 1, false);


--
-- Name: gl_batches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gl_batches_id_seq', 328, false);


--
-- Name: gl_entries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gl_entries_id_seq', 1, false);


--
-- Name: import_runs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.import_runs_id_seq', 1, false);


--
-- Name: invoice_lines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.invoice_lines_id_seq', 1, false);


--
-- Name: invoices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.invoices_id_seq', 1, false);


--
-- Name: notes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notes_id_seq', 1, false);


--
-- Name: notification_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notification_logs_id_seq', 1, false);


--
-- Name: online_cart_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.online_cart_items_id_seq', 1, false);


--
-- Name: online_carts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.online_carts_id_seq', 1, false);


--
-- Name: online_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.online_payments_id_seq', 1, false);


--
-- Name: online_preorder_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.online_preorder_items_id_seq', 1, false);


--
-- Name: online_preorders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.online_preorders_id_seq', 1, false);


--
-- Name: partner_settlement_lines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.partner_settlement_lines_id_seq', 1, false);


--
-- Name: partner_settlements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.partner_settlements_id_seq', 1, false);


--
-- Name: partners_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.partners_id_seq', 2, false);


--
-- Name: payment_splits_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payment_splits_id_seq', 85, false);


--
-- Name: payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payments_id_seq', 149, false);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.permissions_id_seq', 52, true);


--
-- Name: preorders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.preorders_id_seq', 1, false);


--
-- Name: product_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.product_categories_id_seq', 24, false);


--
-- Name: product_partners_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.product_partners_id_seq', 1, false);


--
-- Name: product_rating_helpful_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.product_rating_helpful_id_seq', 1, false);


--
-- Name: product_ratings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.product_ratings_id_seq', 1, false);


--
-- Name: product_supplier_loans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.product_supplier_loans_id_seq', 1, false);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_id_seq', 113, false);


--
-- Name: project_change_orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.project_change_orders_id_seq', 1, false);


--
-- Name: project_costs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.project_costs_id_seq', 1, false);


--
-- Name: project_issues_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.project_issues_id_seq', 1, false);


--
-- Name: project_milestones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.project_milestones_id_seq', 1, false);


--
-- Name: project_phases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.project_phases_id_seq', 1, false);


--
-- Name: project_resources_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.project_resources_id_seq', 1, false);


--
-- Name: project_revenues_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.project_revenues_id_seq', 1, false);


--
-- Name: project_risks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.project_risks_id_seq', 1, false);


--
-- Name: project_tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.project_tasks_id_seq', 1, false);


--
-- Name: projects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.projects_id_seq', 1, false);


--
-- Name: recurring_invoice_schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.recurring_invoice_schedules_id_seq', 1, false);


--
-- Name: recurring_invoice_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.recurring_invoice_templates_id_seq', 1, false);


--
-- Name: resource_time_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.resource_time_logs_id_seq', 1, false);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 12, false);


--
-- Name: saas_invoices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.saas_invoices_id_seq', 1, false);


--
-- Name: saas_plans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.saas_plans_id_seq', 1, false);


--
-- Name: saas_subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.saas_subscriptions_id_seq', 1, false);


--
-- Name: sale_lines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sale_lines_id_seq', 115, false);


--
-- Name: sale_return_lines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sale_return_lines_id_seq', 3, false);


--
-- Name: sale_returns_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sale_returns_id_seq', 3, false);


--
-- Name: sales_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sales_id_seq', 63, false);


--
-- Name: service_parts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.service_parts_id_seq', 5, false);


--
-- Name: service_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.service_requests_id_seq', 6, false);


--
-- Name: service_tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.service_tasks_id_seq', 7, false);


--
-- Name: shipment_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.shipment_items_id_seq', 1, false);


--
-- Name: shipment_partners_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.shipment_partners_id_seq', 1, false);


--
-- Name: shipments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.shipments_id_seq', 1, false);


--
-- Name: sites_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sites_id_seq', 1, false);


--
-- Name: stock_adjustment_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.stock_adjustment_items_id_seq', 1, false);


--
-- Name: stock_adjustments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.stock_adjustments_id_seq', 1, false);


--
-- Name: stock_levels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.stock_levels_id_seq', 113, false);


--
-- Name: supplier_loan_settlements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.supplier_loan_settlements_id_seq', 1, false);


--
-- Name: supplier_settlement_lines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.supplier_settlement_lines_id_seq', 1, false);


--
-- Name: supplier_settlements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.supplier_settlements_id_seq', 1, false);


--
-- Name: suppliers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.suppliers_id_seq', 10, false);


--
-- Name: system_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.system_settings_id_seq', 39, false);


--
-- Name: tax_entries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tax_entries_id_seq', 2, false);


--
-- Name: transfers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.transfers_id_seq', 1, false);


--
-- Name: user_branches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_branches_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 8, true);


--
-- Name: utility_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.utility_accounts_id_seq', 1, false);


--
-- Name: warehouse_partner_shares_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.warehouse_partner_shares_id_seq', 2, false);


--
-- Name: warehouses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.warehouses_id_seq', 11, false);


--
-- Name: workflow_actions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.workflow_actions_id_seq', 1, false);


--
-- Name: workflow_definitions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.workflow_definitions_id_seq', 1, false);


--
-- Name: workflow_instances_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.workflow_instances_id_seq', 1, false);


--
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: archives archives_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.archives
    ADD CONSTRAINT archives_pkey PRIMARY KEY (id);


--
-- Name: asset_depreciations asset_depreciations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_depreciations
    ADD CONSTRAINT asset_depreciations_pkey PRIMARY KEY (id);


--
-- Name: asset_maintenance asset_maintenance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_maintenance
    ADD CONSTRAINT asset_maintenance_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: auth_audit auth_audit_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_audit
    ADD CONSTRAINT auth_audit_pkey PRIMARY KEY (id);


--
-- Name: bank_accounts bank_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_accounts
    ADD CONSTRAINT bank_accounts_pkey PRIMARY KEY (id);


--
-- Name: bank_reconciliations bank_reconciliations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_reconciliations
    ADD CONSTRAINT bank_reconciliations_pkey PRIMARY KEY (id);


--
-- Name: bank_statements bank_statements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_statements
    ADD CONSTRAINT bank_statements_pkey PRIMARY KEY (id);


--
-- Name: bank_transactions bank_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_transactions
    ADD CONSTRAINT bank_transactions_pkey PRIMARY KEY (id);


--
-- Name: branches branches_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT branches_code_key UNIQUE (code);


--
-- Name: branches branches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT branches_pkey PRIMARY KEY (id);


--
-- Name: budget_commitments budget_commitments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.budget_commitments
    ADD CONSTRAINT budget_commitments_pkey PRIMARY KEY (id);


--
-- Name: budgets budgets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.budgets
    ADD CONSTRAINT budgets_pkey PRIMARY KEY (id);


--
-- Name: checks checks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.checks
    ADD CONSTRAINT checks_pkey PRIMARY KEY (id);


--
-- Name: cost_allocation_execution_lines cost_allocation_execution_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_execution_lines
    ADD CONSTRAINT cost_allocation_execution_lines_pkey PRIMARY KEY (id);


--
-- Name: cost_allocation_executions cost_allocation_executions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_executions
    ADD CONSTRAINT cost_allocation_executions_pkey PRIMARY KEY (id);


--
-- Name: cost_allocation_lines cost_allocation_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_lines
    ADD CONSTRAINT cost_allocation_lines_pkey PRIMARY KEY (id);


--
-- Name: cost_allocation_rules cost_allocation_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_rules
    ADD CONSTRAINT cost_allocation_rules_pkey PRIMARY KEY (id);


--
-- Name: cost_center_alert_logs cost_center_alert_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_center_alert_logs
    ADD CONSTRAINT cost_center_alert_logs_pkey PRIMARY KEY (id);


--
-- Name: cost_center_alerts cost_center_alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_center_alerts
    ADD CONSTRAINT cost_center_alerts_pkey PRIMARY KEY (id);


--
-- Name: cost_center_allocations cost_center_allocations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_center_allocations
    ADD CONSTRAINT cost_center_allocations_pkey PRIMARY KEY (id);


--
-- Name: cost_centers cost_centers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_centers
    ADD CONSTRAINT cost_centers_pkey PRIMARY KEY (id);


--
-- Name: currencies currencies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.currencies
    ADD CONSTRAINT currencies_pkey PRIMARY KEY (code);


--
-- Name: customer_loyalty customer_loyalty_customer_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_loyalty
    ADD CONSTRAINT customer_loyalty_customer_id_key UNIQUE (customer_id);


--
-- Name: customer_loyalty customer_loyalty_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_loyalty
    ADD CONSTRAINT customer_loyalty_pkey PRIMARY KEY (id);


--
-- Name: customer_loyalty_points customer_loyalty_points_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_loyalty_points
    ADD CONSTRAINT customer_loyalty_points_pkey PRIMARY KEY (id);


--
-- Name: customers customers_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_email_key UNIQUE (email);


--
-- Name: customers customers_phone_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_phone_key UNIQUE (phone);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- Name: deletion_logs deletion_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deletion_logs
    ADD CONSTRAINT deletion_logs_pkey PRIMARY KEY (id);


--
-- Name: employee_advance_installments employee_advance_installments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_advance_installments
    ADD CONSTRAINT employee_advance_installments_pkey PRIMARY KEY (id);


--
-- Name: employee_advances employee_advances_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_advances
    ADD CONSTRAINT employee_advances_pkey PRIMARY KEY (id);


--
-- Name: employee_deductions employee_deductions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_deductions
    ADD CONSTRAINT employee_deductions_pkey PRIMARY KEY (id);


--
-- Name: employee_skills employee_skills_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_skills
    ADD CONSTRAINT employee_skills_pkey PRIMARY KEY (id);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (id);


--
-- Name: engineering_skills engineering_skills_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_skills
    ADD CONSTRAINT engineering_skills_pkey PRIMARY KEY (id);


--
-- Name: engineering_tasks engineering_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_tasks
    ADD CONSTRAINT engineering_tasks_pkey PRIMARY KEY (id);


--
-- Name: engineering_team_members engineering_team_members_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_team_members
    ADD CONSTRAINT engineering_team_members_pkey PRIMARY KEY (id);


--
-- Name: engineering_teams engineering_teams_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_teams
    ADD CONSTRAINT engineering_teams_pkey PRIMARY KEY (id);


--
-- Name: engineering_timesheets engineering_timesheets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_timesheets
    ADD CONSTRAINT engineering_timesheets_pkey PRIMARY KEY (id);


--
-- Name: equipment_types equipment_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_types
    ADD CONSTRAINT equipment_types_pkey PRIMARY KEY (id);


--
-- Name: exchange_rates exchange_rates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exchange_rates
    ADD CONSTRAINT exchange_rates_pkey PRIMARY KEY (id);


--
-- Name: exchange_transactions exchange_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exchange_transactions
    ADD CONSTRAINT exchange_transactions_pkey PRIMARY KEY (id);


--
-- Name: expense_types expense_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_types
    ADD CONSTRAINT expense_types_pkey PRIMARY KEY (id);


--
-- Name: expenses expenses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_pkey PRIMARY KEY (id);


--
-- Name: fixed_asset_categories fixed_asset_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fixed_asset_categories
    ADD CONSTRAINT fixed_asset_categories_pkey PRIMARY KEY (id);


--
-- Name: fixed_assets fixed_assets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fixed_assets
    ADD CONSTRAINT fixed_assets_pkey PRIMARY KEY (id);


--
-- Name: gl_batches gl_batches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gl_batches
    ADD CONSTRAINT gl_batches_pkey PRIMARY KEY (id);


--
-- Name: gl_entries gl_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gl_entries
    ADD CONSTRAINT gl_entries_pkey PRIMARY KEY (id);


--
-- Name: import_runs import_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.import_runs
    ADD CONSTRAINT import_runs_pkey PRIMARY KEY (id);


--
-- Name: invoice_lines invoice_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoice_lines
    ADD CONSTRAINT invoice_lines_pkey PRIMARY KEY (id);


--
-- Name: invoices invoices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_pkey PRIMARY KEY (id);


--
-- Name: notes notes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notes
    ADD CONSTRAINT notes_pkey PRIMARY KEY (id);


--
-- Name: notification_logs notification_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_logs
    ADD CONSTRAINT notification_logs_pkey PRIMARY KEY (id);


--
-- Name: online_cart_items online_cart_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_cart_items
    ADD CONSTRAINT online_cart_items_pkey PRIMARY KEY (id);


--
-- Name: online_carts online_carts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_carts
    ADD CONSTRAINT online_carts_pkey PRIMARY KEY (id);


--
-- Name: online_payments online_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_payments
    ADD CONSTRAINT online_payments_pkey PRIMARY KEY (id);


--
-- Name: online_preorder_items online_preorder_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_preorder_items
    ADD CONSTRAINT online_preorder_items_pkey PRIMARY KEY (id);


--
-- Name: online_preorders online_preorders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_preorders
    ADD CONSTRAINT online_preorders_pkey PRIMARY KEY (id);


--
-- Name: partner_settlement_lines partner_settlement_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_settlement_lines
    ADD CONSTRAINT partner_settlement_lines_pkey PRIMARY KEY (id);


--
-- Name: partner_settlements partner_settlements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_settlements
    ADD CONSTRAINT partner_settlements_pkey PRIMARY KEY (id);


--
-- Name: partners partners_identity_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partners
    ADD CONSTRAINT partners_identity_number_key UNIQUE (identity_number);


--
-- Name: partners partners_phone_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partners
    ADD CONSTRAINT partners_phone_number_key UNIQUE (phone_number);


--
-- Name: partners partners_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partners
    ADD CONSTRAINT partners_pkey PRIMARY KEY (id);


--
-- Name: payment_splits payment_splits_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_splits
    ADD CONSTRAINT payment_splits_pkey PRIMARY KEY (id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: preorders preorders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.preorders
    ADD CONSTRAINT preorders_pkey PRIMARY KEY (id);


--
-- Name: product_categories product_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_categories
    ADD CONSTRAINT product_categories_pkey PRIMARY KEY (id);


--
-- Name: product_partners product_partners_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_partners
    ADD CONSTRAINT product_partners_pkey PRIMARY KEY (id);


--
-- Name: product_rating_helpful product_rating_helpful_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_rating_helpful
    ADD CONSTRAINT product_rating_helpful_pkey PRIMARY KEY (id);


--
-- Name: product_ratings product_ratings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_ratings
    ADD CONSTRAINT product_ratings_pkey PRIMARY KEY (id);


--
-- Name: product_supplier_loans product_supplier_loans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_supplier_loans
    ADD CONSTRAINT product_supplier_loans_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: project_change_orders project_change_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_change_orders
    ADD CONSTRAINT project_change_orders_pkey PRIMARY KEY (id);


--
-- Name: project_costs project_costs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_costs
    ADD CONSTRAINT project_costs_pkey PRIMARY KEY (id);


--
-- Name: project_issues project_issues_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_issues
    ADD CONSTRAINT project_issues_pkey PRIMARY KEY (id);


--
-- Name: project_milestones project_milestones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_milestones
    ADD CONSTRAINT project_milestones_pkey PRIMARY KEY (id);


--
-- Name: project_phases project_phases_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_phases
    ADD CONSTRAINT project_phases_pkey PRIMARY KEY (id);


--
-- Name: project_resources project_resources_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_resources
    ADD CONSTRAINT project_resources_pkey PRIMARY KEY (id);


--
-- Name: project_revenues project_revenues_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_revenues
    ADD CONSTRAINT project_revenues_pkey PRIMARY KEY (id);


--
-- Name: project_risks project_risks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_risks
    ADD CONSTRAINT project_risks_pkey PRIMARY KEY (id);


--
-- Name: project_tasks project_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_tasks
    ADD CONSTRAINT project_tasks_pkey PRIMARY KEY (id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: recurring_invoice_schedules recurring_invoice_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recurring_invoice_schedules
    ADD CONSTRAINT recurring_invoice_schedules_pkey PRIMARY KEY (id);


--
-- Name: recurring_invoice_templates recurring_invoice_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recurring_invoice_templates
    ADD CONSTRAINT recurring_invoice_templates_pkey PRIMARY KEY (id);


--
-- Name: resource_time_logs resource_time_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resource_time_logs
    ADD CONSTRAINT resource_time_logs_pkey PRIMARY KEY (id);


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (role_id, permission_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: saas_invoices saas_invoices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_invoices
    ADD CONSTRAINT saas_invoices_pkey PRIMARY KEY (id);


--
-- Name: saas_plans saas_plans_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_plans
    ADD CONSTRAINT saas_plans_name_key UNIQUE (name);


--
-- Name: saas_plans saas_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_plans
    ADD CONSTRAINT saas_plans_pkey PRIMARY KEY (id);


--
-- Name: saas_subscriptions saas_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_subscriptions
    ADD CONSTRAINT saas_subscriptions_pkey PRIMARY KEY (id);


--
-- Name: sale_lines sale_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_lines
    ADD CONSTRAINT sale_lines_pkey PRIMARY KEY (id);


--
-- Name: sale_return_lines sale_return_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_return_lines
    ADD CONSTRAINT sale_return_lines_pkey PRIMARY KEY (id);


--
-- Name: sale_returns sale_returns_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_returns
    ADD CONSTRAINT sale_returns_pkey PRIMARY KEY (id);


--
-- Name: sales sales_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_pkey PRIMARY KEY (id);


--
-- Name: service_parts service_parts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_parts
    ADD CONSTRAINT service_parts_pkey PRIMARY KEY (id);


--
-- Name: service_requests service_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_pkey PRIMARY KEY (id);


--
-- Name: service_tasks service_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_tasks
    ADD CONSTRAINT service_tasks_pkey PRIMARY KEY (id);


--
-- Name: shipment_items shipment_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipment_items
    ADD CONSTRAINT shipment_items_pkey PRIMARY KEY (id);


--
-- Name: shipment_partners shipment_partners_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipment_partners
    ADD CONSTRAINT shipment_partners_pkey PRIMARY KEY (id);


--
-- Name: shipments shipments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipments
    ADD CONSTRAINT shipments_pkey PRIMARY KEY (id);


--
-- Name: sites sites_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sites
    ADD CONSTRAINT sites_pkey PRIMARY KEY (id);


--
-- Name: stock_adjustment_items stock_adjustment_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_adjustment_items
    ADD CONSTRAINT stock_adjustment_items_pkey PRIMARY KEY (id);


--
-- Name: stock_adjustments stock_adjustments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_adjustments
    ADD CONSTRAINT stock_adjustments_pkey PRIMARY KEY (id);


--
-- Name: stock_levels stock_levels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_levels
    ADD CONSTRAINT stock_levels_pkey PRIMARY KEY (id);


--
-- Name: supplier_loan_settlements supplier_loan_settlements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.supplier_loan_settlements
    ADD CONSTRAINT supplier_loan_settlements_pkey PRIMARY KEY (id);


--
-- Name: supplier_settlement_lines supplier_settlement_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.supplier_settlement_lines
    ADD CONSTRAINT supplier_settlement_lines_pkey PRIMARY KEY (id);


--
-- Name: supplier_settlements supplier_settlements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.supplier_settlements
    ADD CONSTRAINT supplier_settlements_pkey PRIMARY KEY (id);


--
-- Name: suppliers suppliers_identity_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_identity_number_key UNIQUE (identity_number);


--
-- Name: suppliers suppliers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_pkey PRIMARY KEY (id);


--
-- Name: system_settings system_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_pkey PRIMARY KEY (id);


--
-- Name: tax_entries tax_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tax_entries
    ADD CONSTRAINT tax_entries_pkey PRIMARY KEY (id);


--
-- Name: transfers transfers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transfers
    ADD CONSTRAINT transfers_pkey PRIMARY KEY (id);


--
-- Name: transfers transfers_reference_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transfers
    ADD CONSTRAINT transfers_reference_key UNIQUE (reference);


--
-- Name: budgets uq_budget_year_account_branch_site; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.budgets
    ADD CONSTRAINT uq_budget_year_account_branch_site UNIQUE (fiscal_year, account_code, branch_id, site_id);


--
-- Name: online_cart_items uq_cart_item_cart_product; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_cart_items
    ADD CONSTRAINT uq_cart_item_cart_product UNIQUE (cart_id, product_id);


--
-- Name: budget_commitments uq_commitment_source; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.budget_commitments
    ADD CONSTRAINT uq_commitment_source UNIQUE (source_type, source_id);


--
-- Name: cost_center_allocations uq_cost_center_allocation_source; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_center_allocations
    ADD CONSTRAINT uq_cost_center_allocation_source UNIQUE (source_type, source_id, cost_center_id);


--
-- Name: asset_depreciations uq_depreciation_asset_period; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_depreciations
    ADD CONSTRAINT uq_depreciation_asset_period UNIQUE (asset_id, fiscal_year, fiscal_month);


--
-- Name: employee_skills uq_employee_skill; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_skills
    ADD CONSTRAINT uq_employee_skill UNIQUE (employee_id, skill_id);


--
-- Name: expenses uq_expenses_stock_adjustment_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT uq_expenses_stock_adjustment_id UNIQUE (stock_adjustment_id);


--
-- Name: exchange_rates uq_fx_pair_from; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exchange_rates
    ADD CONSTRAINT uq_fx_pair_from UNIQUE (base_code, quote_code, valid_from);


--
-- Name: gl_batches uq_gl_source_purpose; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gl_batches
    ADD CONSTRAINT uq_gl_source_purpose UNIQUE (source_type, source_id, purpose);


--
-- Name: online_preorder_items uq_online_item_order_product; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_preorder_items
    ADD CONSTRAINT uq_online_item_order_product UNIQUE (order_id, product_id);


--
-- Name: service_parts uq_service_part_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_parts
    ADD CONSTRAINT uq_service_part_unique UNIQUE (service_id, part_id, warehouse_id);


--
-- Name: shipment_items uq_shipment_item_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipment_items
    ADD CONSTRAINT uq_shipment_item_unique UNIQUE (shipment_id, product_id, warehouse_id);


--
-- Name: shipment_partners uq_shipment_partner_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipment_partners
    ADD CONSTRAINT uq_shipment_partner_unique UNIQUE (shipment_id, partner_id);


--
-- Name: stock_levels uq_stock_product_wh; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_levels
    ADD CONSTRAINT uq_stock_product_wh UNIQUE (product_id, warehouse_id);


--
-- Name: engineering_team_members uq_team_member; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_team_members
    ADD CONSTRAINT uq_team_member UNIQUE (team_id, employee_id);


--
-- Name: user_branches uq_user_branch; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_branches
    ADD CONSTRAINT uq_user_branch UNIQUE (user_id, branch_id);


--
-- Name: utility_accounts uq_utility_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.utility_accounts
    ADD CONSTRAINT uq_utility_key UNIQUE (utility_type, provider, account_no);


--
-- Name: warehouse_partner_shares uq_wps_partner_wh_prod; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_partner_shares
    ADD CONSTRAINT uq_wps_partner_wh_prod UNIQUE (partner_id, warehouse_id, product_id);


--
-- Name: user_branches user_branches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_branches
    ADD CONSTRAINT user_branches_pkey PRIMARY KEY (id);


--
-- Name: user_permissions user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_permissions_pkey PRIMARY KEY (user_id, permission_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: utility_accounts utility_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.utility_accounts
    ADD CONSTRAINT utility_accounts_pkey PRIMARY KEY (id);


--
-- Name: warehouse_partner_shares warehouse_partner_shares_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_partner_shares
    ADD CONSTRAINT warehouse_partner_shares_pkey PRIMARY KEY (id);


--
-- Name: warehouses warehouses_online_slug_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_online_slug_key UNIQUE (online_slug);


--
-- Name: warehouses warehouses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_pkey PRIMARY KEY (id);


--
-- Name: workflow_actions workflow_actions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_actions
    ADD CONSTRAINT workflow_actions_pkey PRIMARY KEY (id);


--
-- Name: workflow_definitions workflow_definitions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_definitions
    ADD CONSTRAINT workflow_definitions_pkey PRIMARY KEY (id);


--
-- Name: workflow_instances workflow_instances_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_instances
    ADD CONSTRAINT workflow_instances_pkey PRIMARY KEY (id);


--
-- Name: gin_checks_check_number_trgm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX gin_checks_check_number_trgm ON public.checks USING gin (check_number public.gin_trgm_ops);


--
-- Name: gin_customers_name_trgm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX gin_customers_name_trgm ON public.customers USING gin (name public.gin_trgm_ops);


--
-- Name: gin_partners_name_trgm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX gin_partners_name_trgm ON public.partners USING gin (name public.gin_trgm_ops);


--
-- Name: gin_payments_notes_trgm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX gin_payments_notes_trgm ON public.payments USING gin (notes public.gin_trgm_ops);


--
-- Name: gin_payments_reference_trgm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX gin_payments_reference_trgm ON public.payments USING gin (reference public.gin_trgm_ops);


--
-- Name: gin_suppliers_name_trgm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX gin_suppliers_name_trgm ON public.suppliers USING gin (name public.gin_trgm_ops);


--
-- Name: idx_checks_customer_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_checks_customer_date ON public.checks USING btree (customer_id, check_date);


--
-- Name: idx_checks_payment; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_checks_payment ON public.checks USING btree (payment_id);


--
-- Name: idx_checks_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_checks_status ON public.checks USING btree (status);


--
-- Name: idx_expenses_customer_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_expenses_customer_date ON public.expenses USING btree (customer_id, date);


--
-- Name: idx_invoices_customer_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_invoices_customer_date ON public.invoices USING btree (customer_id, invoice_date);


--
-- Name: idx_payments_customer_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_payments_customer_date ON public.payments USING btree (customer_id, payment_date);


--
-- Name: idx_payments_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_payments_status ON public.payments USING btree (status);


--
-- Name: idx_sale_returns_customer; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sale_returns_customer ON public.sale_returns USING btree (customer_id);


--
-- Name: idx_sales_customer_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sales_customer_date ON public.sales USING btree (customer_id, sale_date);


--
-- Name: idx_services_customer_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_services_customer_date ON public.service_requests USING btree (customer_id, completed_at);


--
-- Name: idx_tax_period_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tax_period_type ON public.tax_entries USING btree (tax_period, entry_type);


--
-- Name: idx_tax_transaction; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tax_transaction ON public.tax_entries USING btree (transaction_type, transaction_id);


--
-- Name: ix_accounts_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_accounts_code ON public.accounts USING btree (code);


--
-- Name: ix_accounts_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_accounts_created_at ON public.accounts USING btree (created_at);


--
-- Name: ix_accounts_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_accounts_updated_at ON public.accounts USING btree (updated_at);


--
-- Name: ix_allocation_exec_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_allocation_exec_date ON public.cost_allocation_executions USING btree (execution_date);


--
-- Name: ix_allocation_line_rule; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_allocation_line_rule ON public.cost_allocation_lines USING btree (rule_id);


--
-- Name: ix_allocation_rule_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_allocation_rule_active ON public.cost_allocation_rules USING btree (is_active);


--
-- Name: ix_archives_record_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_archives_record_id ON public.archives USING btree (record_id);


--
-- Name: ix_archives_record_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_archives_record_type ON public.archives USING btree (record_type);


--
-- Name: ix_asset_category_branch; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_asset_category_branch ON public.fixed_assets USING btree (category_id, branch_id);


--
-- Name: ix_asset_depreciations_asset_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_asset_depreciations_asset_id ON public.asset_depreciations USING btree (asset_id);


--
-- Name: ix_asset_depreciations_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_asset_depreciations_created_at ON public.asset_depreciations USING btree (created_at);


--
-- Name: ix_asset_depreciations_depreciation_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_asset_depreciations_depreciation_date ON public.asset_depreciations USING btree (depreciation_date);


--
-- Name: ix_asset_depreciations_fiscal_month; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_asset_depreciations_fiscal_month ON public.asset_depreciations USING btree (fiscal_month);


--
-- Name: ix_asset_depreciations_fiscal_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_asset_depreciations_fiscal_year ON public.asset_depreciations USING btree (fiscal_year);


--
-- Name: ix_asset_depreciations_gl_batch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_asset_depreciations_gl_batch_id ON public.asset_depreciations USING btree (gl_batch_id);


--
-- Name: ix_asset_depreciations_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_asset_depreciations_updated_at ON public.asset_depreciations USING btree (updated_at);


--
-- Name: ix_asset_maintenance_asset_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_asset_maintenance_asset_id ON public.asset_maintenance USING btree (asset_id);


--
-- Name: ix_asset_maintenance_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_asset_maintenance_created_at ON public.asset_maintenance USING btree (created_at);


--
-- Name: ix_asset_maintenance_expense_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_asset_maintenance_expense_id ON public.asset_maintenance USING btree (expense_id);


--
-- Name: ix_asset_maintenance_maintenance_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_asset_maintenance_maintenance_date ON public.asset_maintenance USING btree (maintenance_date);


--
-- Name: ix_asset_maintenance_maintenance_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_asset_maintenance_maintenance_type ON public.asset_maintenance USING btree (maintenance_type);


--
-- Name: ix_asset_maintenance_next_maintenance_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_asset_maintenance_next_maintenance_date ON public.asset_maintenance USING btree (next_maintenance_date);


--
-- Name: ix_asset_maintenance_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_asset_maintenance_updated_at ON public.asset_maintenance USING btree (updated_at);


--
-- Name: ix_asset_status_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_asset_status_date ON public.fixed_assets USING btree (status, purchase_date);


--
-- Name: ix_audit_logs_action; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_action ON public.audit_logs USING btree (action);


--
-- Name: ix_audit_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_created_at ON public.audit_logs USING btree (created_at);


--
-- Name: ix_audit_logs_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_customer_id ON public.audit_logs USING btree (customer_id);


--
-- Name: ix_audit_logs_model_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_model_name ON public.audit_logs USING btree (model_name);


--
-- Name: ix_audit_logs_record_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_record_id ON public.audit_logs USING btree (record_id);


--
-- Name: ix_audit_logs_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_updated_at ON public.audit_logs USING btree (updated_at);


--
-- Name: ix_audit_logs_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_user_id ON public.audit_logs USING btree (user_id);


--
-- Name: ix_auth_audit_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_auth_audit_created_at ON public.auth_audit USING btree (created_at);


--
-- Name: ix_auth_audit_event; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_auth_audit_event ON public.auth_audit USING btree (event);


--
-- Name: ix_auth_audit_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_auth_audit_user_id ON public.auth_audit USING btree (user_id);


--
-- Name: ix_bank_account_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_account_code ON public.bank_accounts USING btree (code);


--
-- Name: ix_bank_accounts_bank_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_accounts_bank_name ON public.bank_accounts USING btree (bank_name);


--
-- Name: ix_bank_accounts_branch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_accounts_branch_id ON public.bank_accounts USING btree (branch_id);


--
-- Name: ix_bank_accounts_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_bank_accounts_code ON public.bank_accounts USING btree (code);


--
-- Name: ix_bank_accounts_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_accounts_created_at ON public.bank_accounts USING btree (created_at);


--
-- Name: ix_bank_accounts_created_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_accounts_created_by ON public.bank_accounts USING btree (created_by);


--
-- Name: ix_bank_accounts_currency; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_accounts_currency ON public.bank_accounts USING btree (currency);


--
-- Name: ix_bank_accounts_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_accounts_is_active ON public.bank_accounts USING btree (is_active);


--
-- Name: ix_bank_accounts_last_reconciled_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_accounts_last_reconciled_date ON public.bank_accounts USING btree (last_reconciled_date);


--
-- Name: ix_bank_accounts_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_accounts_name ON public.bank_accounts USING btree (name);


--
-- Name: ix_bank_accounts_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_accounts_updated_at ON public.bank_accounts USING btree (updated_at);


--
-- Name: ix_bank_accounts_updated_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_accounts_updated_by ON public.bank_accounts USING btree (updated_by);


--
-- Name: ix_bank_reconciliations_bank_account_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_reconciliations_bank_account_id ON public.bank_reconciliations USING btree (bank_account_id);


--
-- Name: ix_bank_reconciliations_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_reconciliations_created_at ON public.bank_reconciliations USING btree (created_at);


--
-- Name: ix_bank_reconciliations_period_end; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_reconciliations_period_end ON public.bank_reconciliations USING btree (period_end);


--
-- Name: ix_bank_reconciliations_period_start; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_reconciliations_period_start ON public.bank_reconciliations USING btree (period_start);


--
-- Name: ix_bank_reconciliations_reconciliation_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_bank_reconciliations_reconciliation_number ON public.bank_reconciliations USING btree (reconciliation_number);


--
-- Name: ix_bank_reconciliations_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_reconciliations_status ON public.bank_reconciliations USING btree (status);


--
-- Name: ix_bank_reconciliations_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_reconciliations_updated_at ON public.bank_reconciliations USING btree (updated_at);


--
-- Name: ix_bank_statements_bank_account_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_statements_bank_account_id ON public.bank_statements USING btree (bank_account_id);


--
-- Name: ix_bank_statements_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_statements_created_at ON public.bank_statements USING btree (created_at);


--
-- Name: ix_bank_statements_created_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_statements_created_by ON public.bank_statements USING btree (created_by);


--
-- Name: ix_bank_statements_imported_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_statements_imported_at ON public.bank_statements USING btree (imported_at);


--
-- Name: ix_bank_statements_period_end; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_statements_period_end ON public.bank_statements USING btree (period_end);


--
-- Name: ix_bank_statements_period_start; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_statements_period_start ON public.bank_statements USING btree (period_start);


--
-- Name: ix_bank_statements_statement_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_statements_statement_date ON public.bank_statements USING btree (statement_date);


--
-- Name: ix_bank_statements_statement_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_statements_statement_number ON public.bank_statements USING btree (statement_number);


--
-- Name: ix_bank_statements_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_statements_status ON public.bank_statements USING btree (status);


--
-- Name: ix_bank_statements_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_statements_updated_at ON public.bank_statements USING btree (updated_at);


--
-- Name: ix_bank_statements_updated_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_statements_updated_by ON public.bank_statements USING btree (updated_by);


--
-- Name: ix_bank_transactions_bank_account_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_transactions_bank_account_id ON public.bank_transactions USING btree (bank_account_id);


--
-- Name: ix_bank_transactions_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_transactions_created_at ON public.bank_transactions USING btree (created_at);


--
-- Name: ix_bank_transactions_gl_batch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_transactions_gl_batch_id ON public.bank_transactions USING btree (gl_batch_id);


--
-- Name: ix_bank_transactions_matched; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_transactions_matched ON public.bank_transactions USING btree (matched);


--
-- Name: ix_bank_transactions_payment_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_transactions_payment_id ON public.bank_transactions USING btree (payment_id);


--
-- Name: ix_bank_transactions_reconciliation_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_transactions_reconciliation_id ON public.bank_transactions USING btree (reconciliation_id);


--
-- Name: ix_bank_transactions_reference; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_transactions_reference ON public.bank_transactions USING btree (reference);


--
-- Name: ix_bank_transactions_statement_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_transactions_statement_id ON public.bank_transactions USING btree (statement_id);


--
-- Name: ix_bank_transactions_transaction_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_transactions_transaction_date ON public.bank_transactions USING btree (transaction_date);


--
-- Name: ix_bank_transactions_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_transactions_updated_at ON public.bank_transactions USING btree (updated_at);


--
-- Name: ix_bank_transactions_value_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_transactions_value_date ON public.bank_transactions USING btree (value_date);


--
-- Name: ix_bank_tx_account_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_tx_account_date ON public.bank_transactions USING btree (bank_account_id, transaction_date);


--
-- Name: ix_bank_tx_matched; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bank_tx_matched ON public.bank_transactions USING btree (matched, bank_account_id);


--
-- Name: ix_branches_archived_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_branches_archived_at ON public.branches USING btree (archived_at);


--
-- Name: ix_branches_archived_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_branches_archived_by ON public.branches USING btree (archived_by);


--
-- Name: ix_branches_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_branches_created_at ON public.branches USING btree (created_at);


--
-- Name: ix_branches_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_branches_is_active ON public.branches USING btree (is_active);


--
-- Name: ix_branches_is_archived; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_branches_is_archived ON public.branches USING btree (is_archived);


--
-- Name: ix_branches_manager_employee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_branches_manager_employee_id ON public.branches USING btree (manager_employee_id);


--
-- Name: ix_branches_manager_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_branches_manager_user_id ON public.branches USING btree (manager_user_id);


--
-- Name: ix_branches_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_branches_name ON public.branches USING btree (name);


--
-- Name: ix_branches_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_branches_updated_at ON public.branches USING btree (updated_at);


--
-- Name: ix_budget_commitments_budget_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_budget_commitments_budget_id ON public.budget_commitments USING btree (budget_id);


--
-- Name: ix_budget_commitments_commitment_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_budget_commitments_commitment_date ON public.budget_commitments USING btree (commitment_date);


--
-- Name: ix_budget_commitments_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_budget_commitments_created_at ON public.budget_commitments USING btree (created_at);


--
-- Name: ix_budget_commitments_source_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_budget_commitments_source_id ON public.budget_commitments USING btree (source_id);


--
-- Name: ix_budget_commitments_source_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_budget_commitments_source_type ON public.budget_commitments USING btree (source_type);


--
-- Name: ix_budget_commitments_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_budget_commitments_status ON public.budget_commitments USING btree (status);


--
-- Name: ix_budget_commitments_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_budget_commitments_updated_at ON public.budget_commitments USING btree (updated_at);


--
-- Name: ix_budget_year_account; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_budget_year_account ON public.budgets USING btree (fiscal_year, account_code);


--
-- Name: ix_budget_year_branch; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_budget_year_branch ON public.budgets USING btree (fiscal_year, branch_id);


--
-- Name: ix_budgets_account_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_budgets_account_code ON public.budgets USING btree (account_code);


--
-- Name: ix_budgets_branch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_budgets_branch_id ON public.budgets USING btree (branch_id);


--
-- Name: ix_budgets_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_budgets_created_at ON public.budgets USING btree (created_at);


--
-- Name: ix_budgets_fiscal_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_budgets_fiscal_year ON public.budgets USING btree (fiscal_year);


--
-- Name: ix_budgets_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_budgets_is_active ON public.budgets USING btree (is_active);


--
-- Name: ix_budgets_site_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_budgets_site_id ON public.budgets USING btree (site_id);


--
-- Name: ix_budgets_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_budgets_updated_at ON public.budgets USING btree (updated_at);


--
-- Name: ix_cart_item_cart_product; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cart_item_cart_product ON public.online_cart_items USING btree (cart_id, product_id);


--
-- Name: ix_cc_alert_center_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cc_alert_center_active ON public.cost_center_alerts USING btree (cost_center_id, is_active);


--
-- Name: ix_cc_alert_log_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cc_alert_log_date ON public.cost_center_alert_logs USING btree (triggered_at);


--
-- Name: ix_change_order_project_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_change_order_project_status ON public.project_change_orders USING btree (project_id, status);


--
-- Name: ix_checks_archived_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_archived_at ON public.checks USING btree (archived_at);


--
-- Name: ix_checks_archived_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_archived_by ON public.checks USING btree (archived_by);


--
-- Name: ix_checks_check_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_check_date ON public.checks USING btree (check_date);


--
-- Name: ix_checks_check_date_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_check_date_status ON public.checks USING btree (check_date, status);


--
-- Name: ix_checks_check_due_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_check_due_date ON public.checks USING btree (check_due_date);


--
-- Name: ix_checks_check_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_check_number ON public.checks USING btree (check_number);


--
-- Name: ix_checks_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_created_at ON public.checks USING btree (created_at);


--
-- Name: ix_checks_created_by_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_created_by_id ON public.checks USING btree (created_by_id);


--
-- Name: ix_checks_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_customer_id ON public.checks USING btree (customer_id);


--
-- Name: ix_checks_customer_id_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_customer_id_date ON public.checks USING btree (customer_id, check_date);


--
-- Name: ix_checks_date_pending; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_date_pending ON public.checks USING btree (check_date) WHERE ((status)::text = 'PENDING'::text);


--
-- Name: ix_checks_direction; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_direction ON public.checks USING btree (direction);


--
-- Name: ix_checks_direction_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_direction_status ON public.checks USING btree (direction, status);


--
-- Name: ix_checks_is_archived; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_is_archived ON public.checks USING btree (is_archived);


--
-- Name: ix_checks_is_archived_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_is_archived_status ON public.checks USING btree (is_archived, status);


--
-- Name: ix_checks_partner_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_partner_id ON public.checks USING btree (partner_id);


--
-- Name: ix_checks_partner_id_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_partner_id_date ON public.checks USING btree (partner_id, check_date);


--
-- Name: ix_checks_payment_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_payment_id ON public.checks USING btree (payment_id);


--
-- Name: ix_checks_payment_id_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_payment_id_status ON public.checks USING btree (payment_id, status);


--
-- Name: ix_checks_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_status ON public.checks USING btree (status);


--
-- Name: ix_checks_status_due_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_status_due_date ON public.checks USING btree (status, check_due_date);


--
-- Name: ix_checks_status_due_date_direction; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_status_due_date_direction ON public.checks USING btree (status, check_due_date, direction);


--
-- Name: ix_checks_supplier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_supplier_id ON public.checks USING btree (supplier_id);


--
-- Name: ix_checks_supplier_id_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_supplier_id_date ON public.checks USING btree (supplier_id, check_date);


--
-- Name: ix_checks_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_checks_updated_at ON public.checks USING btree (updated_at);


--
-- Name: ix_commitment_budget_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_commitment_budget_status ON public.budget_commitments USING btree (budget_id, status);


--
-- Name: ix_cost_allocation_execution_lines_execution_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_allocation_execution_lines_execution_id ON public.cost_allocation_execution_lines USING btree (execution_id);


--
-- Name: ix_cost_allocation_execution_lines_source_cost_center_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_allocation_execution_lines_source_cost_center_id ON public.cost_allocation_execution_lines USING btree (source_cost_center_id);


--
-- Name: ix_cost_allocation_execution_lines_target_cost_center_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_allocation_execution_lines_target_cost_center_id ON public.cost_allocation_execution_lines USING btree (target_cost_center_id);


--
-- Name: ix_cost_allocation_executions_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_allocation_executions_created_at ON public.cost_allocation_executions USING btree (created_at);


--
-- Name: ix_cost_allocation_executions_gl_batch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_allocation_executions_gl_batch_id ON public.cost_allocation_executions USING btree (gl_batch_id);


--
-- Name: ix_cost_allocation_executions_rule_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_allocation_executions_rule_id ON public.cost_allocation_executions USING btree (rule_id);


--
-- Name: ix_cost_allocation_executions_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_allocation_executions_updated_at ON public.cost_allocation_executions USING btree (updated_at);


--
-- Name: ix_cost_allocation_lines_target_cost_center_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_allocation_lines_target_cost_center_id ON public.cost_allocation_lines USING btree (target_cost_center_id);


--
-- Name: ix_cost_allocation_rules_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_cost_allocation_rules_code ON public.cost_allocation_rules USING btree (code);


--
-- Name: ix_cost_allocation_rules_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_allocation_rules_created_at ON public.cost_allocation_rules USING btree (created_at);


--
-- Name: ix_cost_allocation_rules_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_allocation_rules_name ON public.cost_allocation_rules USING btree (name);


--
-- Name: ix_cost_allocation_rules_source_cost_center_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_allocation_rules_source_cost_center_id ON public.cost_allocation_rules USING btree (source_cost_center_id);


--
-- Name: ix_cost_allocation_rules_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_allocation_rules_updated_at ON public.cost_allocation_rules USING btree (updated_at);


--
-- Name: ix_cost_center_alert_logs_alert_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_center_alert_logs_alert_id ON public.cost_center_alert_logs USING btree (alert_id);


--
-- Name: ix_cost_center_alert_logs_cost_center_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_center_alert_logs_cost_center_id ON public.cost_center_alert_logs USING btree (cost_center_id);


--
-- Name: ix_cost_center_alert_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_center_alert_logs_created_at ON public.cost_center_alert_logs USING btree (created_at);


--
-- Name: ix_cost_center_alert_logs_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_center_alert_logs_updated_at ON public.cost_center_alert_logs USING btree (updated_at);


--
-- Name: ix_cost_center_alerts_cost_center_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_center_alerts_cost_center_id ON public.cost_center_alerts USING btree (cost_center_id);


--
-- Name: ix_cost_center_alerts_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_center_alerts_created_at ON public.cost_center_alerts USING btree (created_at);


--
-- Name: ix_cost_center_alerts_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_center_alerts_updated_at ON public.cost_center_alerts USING btree (updated_at);


--
-- Name: ix_cost_center_alloc_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_center_alloc_date ON public.cost_center_allocations USING btree (cost_center_id, allocation_date);


--
-- Name: ix_cost_center_allocations_allocation_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_center_allocations_allocation_date ON public.cost_center_allocations USING btree (allocation_date);


--
-- Name: ix_cost_center_allocations_cost_center_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_center_allocations_cost_center_id ON public.cost_center_allocations USING btree (cost_center_id);


--
-- Name: ix_cost_center_allocations_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_center_allocations_created_at ON public.cost_center_allocations USING btree (created_at);


--
-- Name: ix_cost_center_allocations_source_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_center_allocations_source_id ON public.cost_center_allocations USING btree (source_id);


--
-- Name: ix_cost_center_allocations_source_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_center_allocations_source_type ON public.cost_center_allocations USING btree (source_type);


--
-- Name: ix_cost_center_allocations_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_center_allocations_updated_at ON public.cost_center_allocations USING btree (updated_at);


--
-- Name: ix_cost_center_parent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_center_parent ON public.cost_centers USING btree (parent_id, is_active);


--
-- Name: ix_cost_centers_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_cost_centers_code ON public.cost_centers USING btree (code);


--
-- Name: ix_cost_centers_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_centers_created_at ON public.cost_centers USING btree (created_at);


--
-- Name: ix_cost_centers_created_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_centers_created_by ON public.cost_centers USING btree (created_by);


--
-- Name: ix_cost_centers_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_centers_is_active ON public.cost_centers USING btree (is_active);


--
-- Name: ix_cost_centers_manager_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_centers_manager_id ON public.cost_centers USING btree (manager_id);


--
-- Name: ix_cost_centers_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_centers_name ON public.cost_centers USING btree (name);


--
-- Name: ix_cost_centers_parent_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_centers_parent_id ON public.cost_centers USING btree (parent_id);


--
-- Name: ix_cost_centers_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_centers_updated_at ON public.cost_centers USING btree (updated_at);


--
-- Name: ix_cost_centers_updated_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_centers_updated_by ON public.cost_centers USING btree (updated_by);


--
-- Name: ix_customer_loyalty_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customer_loyalty_created_at ON public.customer_loyalty USING btree (created_at);


--
-- Name: ix_customer_loyalty_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customer_loyalty_customer_id ON public.customer_loyalty USING btree (customer_id);


--
-- Name: ix_customer_loyalty_points_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customer_loyalty_points_created_at ON public.customer_loyalty_points USING btree (created_at);


--
-- Name: ix_customer_loyalty_points_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customer_loyalty_points_updated_at ON public.customer_loyalty_points USING btree (updated_at);


--
-- Name: ix_customer_loyalty_tier; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customer_loyalty_tier ON public.customer_loyalty USING btree (loyalty_tier);


--
-- Name: ix_customer_loyalty_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customer_loyalty_updated_at ON public.customer_loyalty USING btree (updated_at);


--
-- Name: ix_customers_archived_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customers_archived_at ON public.customers USING btree (archived_at);


--
-- Name: ix_customers_archived_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customers_archived_by ON public.customers USING btree (archived_by);


--
-- Name: ix_customers_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customers_category ON public.customers USING btree (category);


--
-- Name: ix_customers_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customers_created_at ON public.customers USING btree (created_at);


--
-- Name: ix_customers_current_balance; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customers_current_balance ON public.customers USING btree (current_balance);


--
-- Name: ix_customers_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customers_is_active ON public.customers USING btree (is_active);


--
-- Name: ix_customers_is_archived; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customers_is_archived ON public.customers USING btree (is_archived);


--
-- Name: ix_customers_is_online; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customers_is_online ON public.customers USING btree (is_online);


--
-- Name: ix_customers_lower_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customers_lower_email ON public.customers USING btree (lower((email)::text));


--
-- Name: ix_customers_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customers_name ON public.customers USING btree (name);


--
-- Name: ix_customers_phone; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customers_phone ON public.customers USING btree (phone);


--
-- Name: ix_customers_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customers_updated_at ON public.customers USING btree (updated_at);


--
-- Name: ix_deletion_entity; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deletion_entity ON public.deletion_logs USING btree (deletion_type, entity_id);


--
-- Name: ix_deletion_logs_confirmation_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_deletion_logs_confirmation_code ON public.deletion_logs USING btree (confirmation_code);


--
-- Name: ix_deletion_logs_deleted_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deletion_logs_deleted_by ON public.deletion_logs USING btree (deleted_by);


--
-- Name: ix_deletion_logs_deletion_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deletion_logs_deletion_type ON public.deletion_logs USING btree (deletion_type);


--
-- Name: ix_deletion_logs_entity_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deletion_logs_entity_id ON public.deletion_logs USING btree (entity_id);


--
-- Name: ix_deletion_logs_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deletion_logs_status ON public.deletion_logs USING btree (status);


--
-- Name: ix_deletion_type_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deletion_type_status ON public.deletion_logs USING btree (deletion_type, status);


--
-- Name: ix_depreciation_year_month; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_depreciation_year_month ON public.asset_depreciations USING btree (fiscal_year, fiscal_month);


--
-- Name: ix_employee_advance_installments_advance_expense_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_advance_installments_advance_expense_id ON public.employee_advance_installments USING btree (advance_expense_id);


--
-- Name: ix_employee_advance_installments_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_advance_installments_created_at ON public.employee_advance_installments USING btree (created_at);


--
-- Name: ix_employee_advance_installments_due_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_advance_installments_due_date ON public.employee_advance_installments USING btree (due_date);


--
-- Name: ix_employee_advance_installments_employee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_advance_installments_employee_id ON public.employee_advance_installments USING btree (employee_id);


--
-- Name: ix_employee_advance_installments_paid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_advance_installments_paid ON public.employee_advance_installments USING btree (paid);


--
-- Name: ix_employee_advance_installments_paid_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_advance_installments_paid_date ON public.employee_advance_installments USING btree (paid_date);


--
-- Name: ix_employee_advance_installments_paid_in_salary_expense_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_advance_installments_paid_in_salary_expense_id ON public.employee_advance_installments USING btree (paid_in_salary_expense_id);


--
-- Name: ix_employee_advance_installments_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_advance_installments_updated_at ON public.employee_advance_installments USING btree (updated_at);


--
-- Name: ix_employee_advances_advance_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_advances_advance_date ON public.employee_advances USING btree (advance_date);


--
-- Name: ix_employee_advances_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_advances_created_at ON public.employee_advances USING btree (created_at);


--
-- Name: ix_employee_advances_employee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_advances_employee_id ON public.employee_advances USING btree (employee_id);


--
-- Name: ix_employee_advances_expense_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_advances_expense_id ON public.employee_advances USING btree (expense_id);


--
-- Name: ix_employee_advances_fully_paid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_advances_fully_paid ON public.employee_advances USING btree (fully_paid);


--
-- Name: ix_employee_advances_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_advances_updated_at ON public.employee_advances USING btree (updated_at);


--
-- Name: ix_employee_deductions_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_deductions_created_at ON public.employee_deductions USING btree (created_at);


--
-- Name: ix_employee_deductions_deduction_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_deductions_deduction_type ON public.employee_deductions USING btree (deduction_type);


--
-- Name: ix_employee_deductions_employee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_deductions_employee_id ON public.employee_deductions USING btree (employee_id);


--
-- Name: ix_employee_deductions_end_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_deductions_end_date ON public.employee_deductions USING btree (end_date);


--
-- Name: ix_employee_deductions_expense_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_deductions_expense_id ON public.employee_deductions USING btree (expense_id);


--
-- Name: ix_employee_deductions_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_deductions_is_active ON public.employee_deductions USING btree (is_active);


--
-- Name: ix_employee_deductions_start_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_deductions_start_date ON public.employee_deductions USING btree (start_date);


--
-- Name: ix_employee_deductions_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_deductions_updated_at ON public.employee_deductions USING btree (updated_at);


--
-- Name: ix_employee_skill_expiry; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_skill_expiry ON public.employee_skills USING btree (expiry_date);


--
-- Name: ix_employee_skills_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_skills_created_at ON public.employee_skills USING btree (created_at);


--
-- Name: ix_employee_skills_employee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_skills_employee_id ON public.employee_skills USING btree (employee_id);


--
-- Name: ix_employee_skills_skill_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_skills_skill_id ON public.employee_skills USING btree (skill_id);


--
-- Name: ix_employee_skills_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_skills_updated_at ON public.employee_skills USING btree (updated_at);


--
-- Name: ix_employees_branch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employees_branch_id ON public.employees USING btree (branch_id);


--
-- Name: ix_employees_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employees_created_at ON public.employees USING btree (created_at);


--
-- Name: ix_employees_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_employees_email ON public.employees USING btree (email);


--
-- Name: ix_employees_hire_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employees_hire_date ON public.employees USING btree (hire_date);


--
-- Name: ix_employees_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employees_name ON public.employees USING btree (name);


--
-- Name: ix_employees_site_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employees_site_id ON public.employees USING btree (site_id);


--
-- Name: ix_employees_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employees_updated_at ON public.employees USING btree (updated_at);


--
-- Name: ix_eng_task_assigned; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_eng_task_assigned ON public.engineering_tasks USING btree (assigned_to_id, status);


--
-- Name: ix_eng_task_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_eng_task_priority ON public.engineering_tasks USING btree (priority);


--
-- Name: ix_eng_task_scheduled; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_eng_task_scheduled ON public.engineering_tasks USING btree (scheduled_start, scheduled_end);


--
-- Name: ix_eng_task_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_eng_task_status ON public.engineering_tasks USING btree (status);


--
-- Name: ix_eng_team_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_eng_team_active ON public.engineering_teams USING btree (is_active);


--
-- Name: ix_eng_team_specialty; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_eng_team_specialty ON public.engineering_teams USING btree (specialty);


--
-- Name: ix_engineering_skills_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_engineering_skills_code ON public.engineering_skills USING btree (code);


--
-- Name: ix_engineering_skills_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_skills_created_at ON public.engineering_skills USING btree (created_at);


--
-- Name: ix_engineering_skills_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_skills_is_active ON public.engineering_skills USING btree (is_active);


--
-- Name: ix_engineering_skills_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_skills_name ON public.engineering_skills USING btree (name);


--
-- Name: ix_engineering_skills_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_skills_updated_at ON public.engineering_skills USING btree (updated_at);


--
-- Name: ix_engineering_tasks_assigned_team_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_tasks_assigned_team_id ON public.engineering_tasks USING btree (assigned_team_id);


--
-- Name: ix_engineering_tasks_assigned_to_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_tasks_assigned_to_id ON public.engineering_tasks USING btree (assigned_to_id);


--
-- Name: ix_engineering_tasks_cost_center_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_tasks_cost_center_id ON public.engineering_tasks USING btree (cost_center_id);


--
-- Name: ix_engineering_tasks_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_tasks_created_at ON public.engineering_tasks USING btree (created_at);


--
-- Name: ix_engineering_tasks_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_tasks_customer_id ON public.engineering_tasks USING btree (customer_id);


--
-- Name: ix_engineering_tasks_parent_task_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_tasks_parent_task_id ON public.engineering_tasks USING btree (parent_task_id);


--
-- Name: ix_engineering_tasks_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_tasks_project_id ON public.engineering_tasks USING btree (project_id);


--
-- Name: ix_engineering_tasks_scheduled_end; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_tasks_scheduled_end ON public.engineering_tasks USING btree (scheduled_end);


--
-- Name: ix_engineering_tasks_scheduled_start; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_tasks_scheduled_start ON public.engineering_tasks USING btree (scheduled_start);


--
-- Name: ix_engineering_tasks_service_request_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_tasks_service_request_id ON public.engineering_tasks USING btree (service_request_id);


--
-- Name: ix_engineering_tasks_task_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_engineering_tasks_task_number ON public.engineering_tasks USING btree (task_number);


--
-- Name: ix_engineering_tasks_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_tasks_updated_at ON public.engineering_tasks USING btree (updated_at);


--
-- Name: ix_engineering_team_members_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_team_members_created_at ON public.engineering_team_members USING btree (created_at);


--
-- Name: ix_engineering_team_members_employee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_team_members_employee_id ON public.engineering_team_members USING btree (employee_id);


--
-- Name: ix_engineering_team_members_team_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_team_members_team_id ON public.engineering_team_members USING btree (team_id);


--
-- Name: ix_engineering_team_members_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_team_members_updated_at ON public.engineering_team_members USING btree (updated_at);


--
-- Name: ix_engineering_teams_branch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_teams_branch_id ON public.engineering_teams USING btree (branch_id);


--
-- Name: ix_engineering_teams_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_engineering_teams_code ON public.engineering_teams USING btree (code);


--
-- Name: ix_engineering_teams_cost_center_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_teams_cost_center_id ON public.engineering_teams USING btree (cost_center_id);


--
-- Name: ix_engineering_teams_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_teams_created_at ON public.engineering_teams USING btree (created_at);


--
-- Name: ix_engineering_teams_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_teams_name ON public.engineering_teams USING btree (name);


--
-- Name: ix_engineering_teams_team_leader_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_teams_team_leader_id ON public.engineering_teams USING btree (team_leader_id);


--
-- Name: ix_engineering_teams_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_teams_updated_at ON public.engineering_teams USING btree (updated_at);


--
-- Name: ix_engineering_timesheets_cost_center_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_timesheets_cost_center_id ON public.engineering_timesheets USING btree (cost_center_id);


--
-- Name: ix_engineering_timesheets_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_timesheets_created_at ON public.engineering_timesheets USING btree (created_at);


--
-- Name: ix_engineering_timesheets_employee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_timesheets_employee_id ON public.engineering_timesheets USING btree (employee_id);


--
-- Name: ix_engineering_timesheets_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_timesheets_updated_at ON public.engineering_timesheets USING btree (updated_at);


--
-- Name: ix_engineering_timesheets_work_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_engineering_timesheets_work_date ON public.engineering_timesheets USING btree (work_date);


--
-- Name: ix_equipment_types_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_equipment_types_created_at ON public.equipment_types USING btree (created_at);


--
-- Name: ix_equipment_types_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_equipment_types_name ON public.equipment_types USING btree (name);


--
-- Name: ix_equipment_types_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_equipment_types_updated_at ON public.equipment_types USING btree (updated_at);


--
-- Name: ix_exchange_prod_wh; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exchange_prod_wh ON public.exchange_transactions USING btree (product_id, warehouse_id);


--
-- Name: ix_exchange_rates_base_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exchange_rates_base_code ON public.exchange_rates USING btree (base_code);


--
-- Name: ix_exchange_rates_quote_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exchange_rates_quote_code ON public.exchange_rates USING btree (quote_code);


--
-- Name: ix_exchange_rates_valid_from; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exchange_rates_valid_from ON public.exchange_rates USING btree (valid_from);


--
-- Name: ix_exchange_supplier; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exchange_supplier ON public.exchange_transactions USING btree (supplier_id);


--
-- Name: ix_exchange_transactions_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exchange_transactions_created_at ON public.exchange_transactions USING btree (created_at);


--
-- Name: ix_exchange_transactions_direction; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exchange_transactions_direction ON public.exchange_transactions USING btree (direction);


--
-- Name: ix_exchange_transactions_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exchange_transactions_product_id ON public.exchange_transactions USING btree (product_id);


--
-- Name: ix_exchange_transactions_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exchange_transactions_updated_at ON public.exchange_transactions USING btree (updated_at);


--
-- Name: ix_exchange_transactions_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exchange_transactions_warehouse_id ON public.exchange_transactions USING btree (warehouse_id);


--
-- Name: ix_expense_customer_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expense_customer_date ON public.expenses USING btree (customer_id, date);


--
-- Name: ix_expense_partner_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expense_partner_date ON public.expenses USING btree (partner_id, date);


--
-- Name: ix_expense_shipment_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expense_shipment_date ON public.expenses USING btree (shipment_id, date);


--
-- Name: ix_expense_supplier_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expense_supplier_date ON public.expenses USING btree (supplier_id, date);


--
-- Name: ix_expense_type_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expense_type_date ON public.expenses USING btree (type_id, date);


--
-- Name: ix_expense_types_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_expense_types_code ON public.expense_types USING btree (code);


--
-- Name: ix_expense_types_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expense_types_created_at ON public.expense_types USING btree (created_at);


--
-- Name: ix_expense_types_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_expense_types_name ON public.expense_types USING btree (name);


--
-- Name: ix_expense_types_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expense_types_updated_at ON public.expense_types USING btree (updated_at);


--
-- Name: ix_expenses_archived_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_archived_at ON public.expenses USING btree (archived_at);


--
-- Name: ix_expenses_archived_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_archived_by ON public.expenses USING btree (archived_by);


--
-- Name: ix_expenses_branch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_branch_id ON public.expenses USING btree (branch_id);


--
-- Name: ix_expenses_cost_center_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_cost_center_id ON public.expenses USING btree (cost_center_id);


--
-- Name: ix_expenses_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_created_at ON public.expenses USING btree (created_at);


--
-- Name: ix_expenses_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_customer_id ON public.expenses USING btree (customer_id);


--
-- Name: ix_expenses_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_date ON public.expenses USING btree (date);


--
-- Name: ix_expenses_employee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_employee_id ON public.expenses USING btree (employee_id);


--
-- Name: ix_expenses_is_archived; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_is_archived ON public.expenses USING btree (is_archived);


--
-- Name: ix_expenses_paid_to; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_paid_to ON public.expenses USING btree (paid_to);


--
-- Name: ix_expenses_partner_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_partner_id ON public.expenses USING btree (partner_id);


--
-- Name: ix_expenses_payee_entity_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_payee_entity_id ON public.expenses USING btree (payee_entity_id);


--
-- Name: ix_expenses_payee_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_payee_name ON public.expenses USING btree (payee_name);


--
-- Name: ix_expenses_payee_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_payee_type ON public.expenses USING btree (payee_type);


--
-- Name: ix_expenses_period_end; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_period_end ON public.expenses USING btree (period_end);


--
-- Name: ix_expenses_period_start; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_period_start ON public.expenses USING btree (period_start);


--
-- Name: ix_expenses_shipment_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_shipment_id ON public.expenses USING btree (shipment_id);


--
-- Name: ix_expenses_site_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_site_id ON public.expenses USING btree (site_id);


--
-- Name: ix_expenses_stock_adjustment_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_stock_adjustment_id ON public.expenses USING btree (stock_adjustment_id);


--
-- Name: ix_expenses_supplier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_supplier_id ON public.expenses USING btree (supplier_id);


--
-- Name: ix_expenses_tax_invoice_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_tax_invoice_number ON public.expenses USING btree (tax_invoice_number);


--
-- Name: ix_expenses_type_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_type_id ON public.expenses USING btree (type_id);


--
-- Name: ix_expenses_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_updated_at ON public.expenses USING btree (updated_at);


--
-- Name: ix_expenses_utility_account_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_utility_account_id ON public.expenses USING btree (utility_account_id);


--
-- Name: ix_expenses_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expenses_warehouse_id ON public.expenses USING btree (warehouse_id);


--
-- Name: ix_fixed_asset_categories_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_fixed_asset_categories_code ON public.fixed_asset_categories USING btree (code);


--
-- Name: ix_fixed_asset_categories_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_asset_categories_created_at ON public.fixed_asset_categories USING btree (created_at);


--
-- Name: ix_fixed_asset_categories_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_asset_categories_is_active ON public.fixed_asset_categories USING btree (is_active);


--
-- Name: ix_fixed_asset_categories_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_asset_categories_name ON public.fixed_asset_categories USING btree (name);


--
-- Name: ix_fixed_asset_categories_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_asset_categories_updated_at ON public.fixed_asset_categories USING btree (updated_at);


--
-- Name: ix_fixed_assets_asset_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_fixed_assets_asset_number ON public.fixed_assets USING btree (asset_number);


--
-- Name: ix_fixed_assets_barcode; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_assets_barcode ON public.fixed_assets USING btree (barcode);


--
-- Name: ix_fixed_assets_branch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_assets_branch_id ON public.fixed_assets USING btree (branch_id);


--
-- Name: ix_fixed_assets_category_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_assets_category_id ON public.fixed_assets USING btree (category_id);


--
-- Name: ix_fixed_assets_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_assets_created_at ON public.fixed_assets USING btree (created_at);


--
-- Name: ix_fixed_assets_disposal_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_assets_disposal_date ON public.fixed_assets USING btree (disposal_date);


--
-- Name: ix_fixed_assets_is_archived; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_assets_is_archived ON public.fixed_assets USING btree (is_archived);


--
-- Name: ix_fixed_assets_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_assets_name ON public.fixed_assets USING btree (name);


--
-- Name: ix_fixed_assets_purchase_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_assets_purchase_date ON public.fixed_assets USING btree (purchase_date);


--
-- Name: ix_fixed_assets_serial_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_assets_serial_number ON public.fixed_assets USING btree (serial_number);


--
-- Name: ix_fixed_assets_site_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_assets_site_id ON public.fixed_assets USING btree (site_id);


--
-- Name: ix_fixed_assets_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_assets_status ON public.fixed_assets USING btree (status);


--
-- Name: ix_fixed_assets_supplier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_assets_supplier_id ON public.fixed_assets USING btree (supplier_id);


--
-- Name: ix_fixed_assets_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fixed_assets_updated_at ON public.fixed_assets USING btree (updated_at);


--
-- Name: ix_gl_batches_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_gl_batches_code ON public.gl_batches USING btree (code);


--
-- Name: ix_gl_batches_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_batches_created_at ON public.gl_batches USING btree (created_at);


--
-- Name: ix_gl_batches_entity_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_batches_entity_id ON public.gl_batches USING btree (entity_id);


--
-- Name: ix_gl_batches_entity_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_batches_entity_type ON public.gl_batches USING btree (entity_type);


--
-- Name: ix_gl_batches_posted_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_batches_posted_at ON public.gl_batches USING btree (posted_at);


--
-- Name: ix_gl_batches_purpose; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_batches_purpose ON public.gl_batches USING btree (purpose);


--
-- Name: ix_gl_batches_source_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_batches_source_id ON public.gl_batches USING btree (source_id);


--
-- Name: ix_gl_batches_source_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_batches_source_type ON public.gl_batches USING btree (source_type);


--
-- Name: ix_gl_batches_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_batches_status ON public.gl_batches USING btree (status);


--
-- Name: ix_gl_batches_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_batches_updated_at ON public.gl_batches USING btree (updated_at);


--
-- Name: ix_gl_entity; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_entity ON public.gl_batches USING btree (entity_type, entity_id);


--
-- Name: ix_gl_entries_account; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_entries_account ON public.gl_entries USING btree (account);


--
-- Name: ix_gl_entries_account_currency; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_entries_account_currency ON public.gl_entries USING btree (account, currency);


--
-- Name: ix_gl_entries_batch_account; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_entries_batch_account ON public.gl_entries USING btree (batch_id, account);


--
-- Name: ix_gl_entries_batch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_entries_batch_id ON public.gl_entries USING btree (batch_id);


--
-- Name: ix_gl_entries_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_entries_created_at ON public.gl_entries USING btree (created_at);


--
-- Name: ix_gl_entries_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_entries_updated_at ON public.gl_entries USING btree (updated_at);


--
-- Name: ix_gl_status_source; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_gl_status_source ON public.gl_batches USING btree (status, source_type, source_id);


--
-- Name: ix_import_runs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_import_runs_created_at ON public.import_runs USING btree (created_at);


--
-- Name: ix_import_runs_dry_run; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_import_runs_dry_run ON public.import_runs USING btree (dry_run);


--
-- Name: ix_import_runs_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_import_runs_updated_at ON public.import_runs USING btree (updated_at);


--
-- Name: ix_import_runs_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_import_runs_user_id ON public.import_runs USING btree (user_id);


--
-- Name: ix_import_runs_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_import_runs_warehouse_id ON public.import_runs USING btree (warehouse_id);


--
-- Name: ix_invoice_lines_invoice_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoice_lines_invoice_id ON public.invoice_lines USING btree (invoice_id);


--
-- Name: ix_invoice_lines_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoice_lines_product_id ON public.invoice_lines USING btree (product_id);


--
-- Name: ix_invoices_cancelled_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_cancelled_at ON public.invoices USING btree (cancelled_at);


--
-- Name: ix_invoices_cancelled_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_cancelled_by ON public.invoices USING btree (cancelled_by);


--
-- Name: ix_invoices_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_created_at ON public.invoices USING btree (created_at);


--
-- Name: ix_invoices_credit_for_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_credit_for_id ON public.invoices USING btree (credit_for_id);


--
-- Name: ix_invoices_customer_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_customer_date ON public.invoices USING btree (customer_id, invoice_date);


--
-- Name: ix_invoices_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_customer_id ON public.invoices USING btree (customer_id);


--
-- Name: ix_invoices_due_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_due_date ON public.invoices USING btree (due_date);


--
-- Name: ix_invoices_idempotency_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_invoices_idempotency_key ON public.invoices USING btree (idempotency_key);


--
-- Name: ix_invoices_invoice_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_invoice_date ON public.invoices USING btree (invoice_date);


--
-- Name: ix_invoices_invoice_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_invoices_invoice_number ON public.invoices USING btree (invoice_number);


--
-- Name: ix_invoices_kind; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_kind ON public.invoices USING btree (kind);


--
-- Name: ix_invoices_partner_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_partner_id ON public.invoices USING btree (partner_id);


--
-- Name: ix_invoices_preorder_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_preorder_id ON public.invoices USING btree (preorder_id);


--
-- Name: ix_invoices_refund_of_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_refund_of_id ON public.invoices USING btree (refund_of_id);


--
-- Name: ix_invoices_sale_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_sale_id ON public.invoices USING btree (sale_id);


--
-- Name: ix_invoices_service_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_service_id ON public.invoices USING btree (service_id);


--
-- Name: ix_invoices_source; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_source ON public.invoices USING btree (source);


--
-- Name: ix_invoices_supplier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_supplier_id ON public.invoices USING btree (supplier_id);


--
-- Name: ix_invoices_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_invoices_updated_at ON public.invoices USING btree (updated_at);


--
-- Name: ix_issue_project_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_issue_project_status ON public.project_issues USING btree (project_id, status);


--
-- Name: ix_issue_severity_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_issue_severity_priority ON public.project_issues USING btree (severity, priority);


--
-- Name: ix_loyalty_points_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_loyalty_points_customer_id ON public.customer_loyalty_points USING btree (customer_id);


--
-- Name: ix_loyalty_points_expires; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_loyalty_points_expires ON public.customer_loyalty_points USING btree (expires_at);


--
-- Name: ix_loyalty_points_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_loyalty_points_type ON public.customer_loyalty_points USING btree (type);


--
-- Name: ix_maintenance_asset_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_maintenance_asset_date ON public.asset_maintenance USING btree (asset_id, maintenance_date);


--
-- Name: ix_milestone_project_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_milestone_project_status ON public.project_milestones USING btree (project_id, status);


--
-- Name: ix_notes_author_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notes_author_id ON public.notes USING btree (author_id);


--
-- Name: ix_notes_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notes_created_at ON public.notes USING btree (created_at);


--
-- Name: ix_notes_entity_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notes_entity_id ON public.notes USING btree (entity_id);


--
-- Name: ix_notes_entity_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notes_entity_type ON public.notes USING btree (entity_type);


--
-- Name: ix_notes_is_pinned; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notes_is_pinned ON public.notes USING btree (is_pinned);


--
-- Name: ix_notes_is_sent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notes_is_sent ON public.notes USING btree (is_sent);


--
-- Name: ix_notes_notification_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notes_notification_date ON public.notes USING btree (notification_date);


--
-- Name: ix_notes_notification_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notes_notification_type ON public.notes USING btree (notification_type);


--
-- Name: ix_notes_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notes_priority ON public.notes USING btree (priority);


--
-- Name: ix_notes_target_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notes_target_type ON public.notes USING btree (target_type);


--
-- Name: ix_notes_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notes_updated_at ON public.notes USING btree (updated_at);


--
-- Name: ix_notification_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_logs_created_at ON public.notification_logs USING btree (created_at);


--
-- Name: ix_notification_logs_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_logs_customer_id ON public.notification_logs USING btree (customer_id);


--
-- Name: ix_notification_logs_recipient; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_logs_recipient ON public.notification_logs USING btree (recipient);


--
-- Name: ix_notification_logs_sent_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_logs_sent_at ON public.notification_logs USING btree (sent_at);


--
-- Name: ix_notification_logs_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_logs_status ON public.notification_logs USING btree (status);


--
-- Name: ix_notification_logs_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_logs_type ON public.notification_logs USING btree (type);


--
-- Name: ix_notification_logs_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_logs_user_id ON public.notification_logs USING btree (user_id);


--
-- Name: ix_online_cart_items_added_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_cart_items_added_at ON public.online_cart_items USING btree (added_at);


--
-- Name: ix_online_cart_items_cart_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_cart_items_cart_id ON public.online_cart_items USING btree (cart_id);


--
-- Name: ix_online_cart_items_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_cart_items_product_id ON public.online_cart_items USING btree (product_id);


--
-- Name: ix_online_carts_cart_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_online_carts_cart_id ON public.online_carts USING btree (cart_id);


--
-- Name: ix_online_carts_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_carts_created_at ON public.online_carts USING btree (created_at);


--
-- Name: ix_online_carts_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_carts_customer_id ON public.online_carts USING btree (customer_id);


--
-- Name: ix_online_carts_expires_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_carts_expires_at ON public.online_carts USING btree (expires_at);


--
-- Name: ix_online_carts_session_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_carts_session_id ON public.online_carts USING btree (session_id);


--
-- Name: ix_online_carts_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_carts_status ON public.online_carts USING btree (status);


--
-- Name: ix_online_carts_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_carts_updated_at ON public.online_carts USING btree (updated_at);


--
-- Name: ix_online_item_order_product; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_item_order_product ON public.online_preorder_items USING btree (order_id, product_id);


--
-- Name: ix_online_payments_card_fingerprint; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_payments_card_fingerprint ON public.online_payments USING btree (card_fingerprint);


--
-- Name: ix_online_payments_card_last4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_payments_card_last4 ON public.online_payments USING btree (card_last4);


--
-- Name: ix_online_payments_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_payments_created_at ON public.online_payments USING btree (created_at);


--
-- Name: ix_online_payments_gateway_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_payments_gateway_status ON public.online_payments USING btree (gateway, status);


--
-- Name: ix_online_payments_idempotency_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_online_payments_idempotency_key ON public.online_payments USING btree (idempotency_key);


--
-- Name: ix_online_payments_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_payments_order_id ON public.online_payments USING btree (order_id);


--
-- Name: ix_online_payments_order_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_payments_order_status ON public.online_payments USING btree (order_id, status);


--
-- Name: ix_online_payments_payment_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_payments_payment_id ON public.online_payments USING btree (payment_id);


--
-- Name: ix_online_payments_payment_ref; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_online_payments_payment_ref ON public.online_payments USING btree (payment_ref);


--
-- Name: ix_online_payments_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_payments_status ON public.online_payments USING btree (status);


--
-- Name: ix_online_payments_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_payments_updated_at ON public.online_payments USING btree (updated_at);


--
-- Name: ix_online_preorder_items_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_preorder_items_order_id ON public.online_preorder_items USING btree (order_id);


--
-- Name: ix_online_preorder_items_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_preorder_items_product_id ON public.online_preorder_items USING btree (product_id);


--
-- Name: ix_online_preorders_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_preorders_created_at ON public.online_preorders USING btree (created_at);


--
-- Name: ix_online_preorders_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_preorders_customer_id ON public.online_preorders USING btree (customer_id);


--
-- Name: ix_online_preorders_customer_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_preorders_customer_status ON public.online_preorders USING btree (customer_id, status);


--
-- Name: ix_online_preorders_order_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_online_preorders_order_number ON public.online_preorders USING btree (order_number);


--
-- Name: ix_online_preorders_payment_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_preorders_payment_status ON public.online_preorders USING btree (payment_status);


--
-- Name: ix_online_preorders_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_preorders_status ON public.online_preorders USING btree (status);


--
-- Name: ix_online_preorders_status_paystatus; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_preorders_status_paystatus ON public.online_preorders USING btree (status, payment_status);


--
-- Name: ix_online_preorders_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_preorders_updated_at ON public.online_preorders USING btree (updated_at);


--
-- Name: ix_online_preorders_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_online_preorders_warehouse_id ON public.online_preorders USING btree (warehouse_id);


--
-- Name: ix_partner_settlement_lines_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_settlement_lines_created_at ON public.partner_settlement_lines USING btree (created_at);


--
-- Name: ix_partner_settlement_lines_settlement_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_settlement_lines_settlement_id ON public.partner_settlement_lines USING btree (settlement_id);


--
-- Name: ix_partner_settlement_lines_source_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_settlement_lines_source_id ON public.partner_settlement_lines USING btree (source_id);


--
-- Name: ix_partner_settlement_lines_source_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_settlement_lines_source_type ON public.partner_settlement_lines USING btree (source_type);


--
-- Name: ix_partner_settlement_lines_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_settlement_lines_updated_at ON public.partner_settlement_lines USING btree (updated_at);


--
-- Name: ix_partner_settlements_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_partner_settlements_code ON public.partner_settlements USING btree (code);


--
-- Name: ix_partner_settlements_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_settlements_created_at ON public.partner_settlements USING btree (created_at);


--
-- Name: ix_partner_settlements_from_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_settlements_from_date ON public.partner_settlements USING btree (from_date);


--
-- Name: ix_partner_settlements_is_approved; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_settlements_is_approved ON public.partner_settlements USING btree (is_approved);


--
-- Name: ix_partner_settlements_partner_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_settlements_partner_id ON public.partner_settlements USING btree (partner_id);


--
-- Name: ix_partner_settlements_previous_settlement_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_settlements_previous_settlement_id ON public.partner_settlements USING btree (previous_settlement_id);


--
-- Name: ix_partner_settlements_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_settlements_status ON public.partner_settlements USING btree (status);


--
-- Name: ix_partner_settlements_to_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_settlements_to_date ON public.partner_settlements USING btree (to_date);


--
-- Name: ix_partner_settlements_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_settlements_updated_at ON public.partner_settlements USING btree (updated_at);


--
-- Name: ix_partners_archived_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_archived_at ON public.partners USING btree (archived_at);


--
-- Name: ix_partners_archived_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_archived_by ON public.partners USING btree (archived_by);


--
-- Name: ix_partners_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_created_at ON public.partners USING btree (created_at);


--
-- Name: ix_partners_currency_balance; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_currency_balance ON public.partners USING btree (currency, current_balance);


--
-- Name: ix_partners_current_balance; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_current_balance ON public.partners USING btree (current_balance);


--
-- Name: ix_partners_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_customer_id ON public.partners USING btree (customer_id);


--
-- Name: ix_partners_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_partners_email ON public.partners USING btree (email);


--
-- Name: ix_partners_is_archived; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_is_archived ON public.partners USING btree (is_archived);


--
-- Name: ix_partners_is_archived_balance; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_is_archived_balance ON public.partners USING btree (is_archived, current_balance);


--
-- Name: ix_partners_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_name ON public.partners USING btree (name);


--
-- Name: ix_partners_name_phone; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_name_phone ON public.partners USING btree (name, phone_number);


--
-- Name: ix_partners_share_percentage; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_share_percentage ON public.partners USING btree (share_percentage);


--
-- Name: ix_partners_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_updated_at ON public.partners USING btree (updated_at);


--
-- Name: ix_pay_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pay_created_at ON public.payments USING btree (payment_date);


--
-- Name: ix_pay_currency; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pay_currency ON public.payments USING btree (currency);


--
-- Name: ix_pay_dir_stat_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pay_dir_stat_type ON public.payments USING btree (direction, status, entity_type);


--
-- Name: ix_pay_direction; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pay_direction ON public.payments USING btree (direction);


--
-- Name: ix_pay_inv_status_dir; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pay_inv_status_dir ON public.payments USING btree (invoice_id, status, direction);


--
-- Name: ix_pay_partner_status_dir; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pay_partner_status_dir ON public.payments USING btree (partner_id, status, direction);


--
-- Name: ix_pay_preorder_status_dir; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pay_preorder_status_dir ON public.payments USING btree (preorder_id, status, direction);


--
-- Name: ix_pay_reversal; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pay_reversal ON public.payments USING btree (refund_of_id);


--
-- Name: ix_pay_sale_status_dir; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pay_sale_status_dir ON public.payments USING btree (sale_id, status, direction);


--
-- Name: ix_pay_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pay_status ON public.payments USING btree (status);


--
-- Name: ix_pay_supplier_status_dir; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pay_supplier_status_dir ON public.payments USING btree (supplier_id, status, direction);


--
-- Name: ix_payment_splits_method; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payment_splits_method ON public.payment_splits USING btree (method);


--
-- Name: ix_payment_splits_payment_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payment_splits_payment_id ON public.payment_splits USING btree (payment_id);


--
-- Name: ix_payments_archived_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_archived_at ON public.payments USING btree (archived_at);


--
-- Name: ix_payments_archived_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_archived_by ON public.payments USING btree (archived_by);


--
-- Name: ix_payments_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_created_at ON public.payments USING btree (created_at);


--
-- Name: ix_payments_created_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_created_by ON public.payments USING btree (created_by);


--
-- Name: ix_payments_currency; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_currency ON public.payments USING btree (currency);


--
-- Name: ix_payments_customer_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_customer_date ON public.payments USING btree (customer_id, payment_date);


--
-- Name: ix_payments_customer_date_completed; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_customer_date_completed ON public.payments USING btree (customer_id, payment_date) WHERE ((is_archived = false) AND ((status)::text = 'COMPLETED'::text));


--
-- Name: ix_payments_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_customer_id ON public.payments USING btree (customer_id);


--
-- Name: ix_payments_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_date ON public.payments USING btree (payment_date);


--
-- Name: ix_payments_date_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_date_active ON public.payments USING btree (payment_date) WHERE (is_archived = false);


--
-- Name: ix_payments_direction; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_direction ON public.payments USING btree (direction);


--
-- Name: ix_payments_entity_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_entity_type ON public.payments USING btree (entity_type);


--
-- Name: ix_payments_expense_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_expense_id ON public.payments USING btree (expense_id);


--
-- Name: ix_payments_idempotency_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_payments_idempotency_key ON public.payments USING btree (idempotency_key);


--
-- Name: ix_payments_invoice_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_invoice_id ON public.payments USING btree (invoice_id);


--
-- Name: ix_payments_is_archived; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_is_archived ON public.payments USING btree (is_archived);


--
-- Name: ix_payments_loan_settlement_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_loan_settlement_id ON public.payments USING btree (loan_settlement_id);


--
-- Name: ix_payments_method; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_method ON public.payments USING btree (method);


--
-- Name: ix_payments_partner_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_partner_date ON public.payments USING btree (partner_id, payment_date);


--
-- Name: ix_payments_partner_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_partner_id ON public.payments USING btree (partner_id);


--
-- Name: ix_payments_payment_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_payments_payment_number ON public.payments USING btree (payment_number);


--
-- Name: ix_payments_preorder_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_preorder_id ON public.payments USING btree (preorder_id);


--
-- Name: ix_payments_receipt_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_payments_receipt_number ON public.payments USING btree (receipt_number);


--
-- Name: ix_payments_sale_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_sale_id ON public.payments USING btree (sale_id);


--
-- Name: ix_payments_service_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_service_id ON public.payments USING btree (service_id);


--
-- Name: ix_payments_shipment_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_shipment_id ON public.payments USING btree (shipment_id);


--
-- Name: ix_payments_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_status ON public.payments USING btree (status);


--
-- Name: ix_payments_supplier_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_supplier_date ON public.payments USING btree (supplier_id, payment_date);


--
-- Name: ix_payments_supplier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_supplier_id ON public.payments USING btree (supplier_id);


--
-- Name: ix_payments_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_updated_at ON public.payments USING btree (updated_at);


--
-- Name: ix_permissions_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_permissions_code ON public.permissions USING btree (code);


--
-- Name: ix_permissions_module; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_permissions_module ON public.permissions USING btree (module);


--
-- Name: ix_permissions_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_permissions_name ON public.permissions USING btree (name);


--
-- Name: ix_preorders_cancelled_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_preorders_cancelled_at ON public.preorders USING btree (cancelled_at);


--
-- Name: ix_preorders_cancelled_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_preorders_cancelled_by ON public.preorders USING btree (cancelled_by);


--
-- Name: ix_preorders_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_preorders_created_at ON public.preorders USING btree (created_at);


--
-- Name: ix_preorders_cust_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_preorders_cust_status ON public.preorders USING btree (customer_id, status);


--
-- Name: ix_preorders_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_preorders_customer_id ON public.preorders USING btree (customer_id);


--
-- Name: ix_preorders_idempotency_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_preorders_idempotency_key ON public.preorders USING btree (idempotency_key);


--
-- Name: ix_preorders_partner_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_preorders_partner_status ON public.preorders USING btree (partner_id, status);


--
-- Name: ix_preorders_preorder_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_preorders_preorder_date ON public.preorders USING btree (preorder_date);


--
-- Name: ix_preorders_prod_wh; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_preorders_prod_wh ON public.preorders USING btree (product_id, warehouse_id);


--
-- Name: ix_preorders_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_preorders_product_id ON public.preorders USING btree (product_id);


--
-- Name: ix_preorders_reference; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_preorders_reference ON public.preorders USING btree (reference);


--
-- Name: ix_preorders_refund_of_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_preorders_refund_of_id ON public.preorders USING btree (refund_of_id);


--
-- Name: ix_preorders_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_preorders_status ON public.preorders USING btree (status);


--
-- Name: ix_preorders_supplier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_preorders_supplier_id ON public.preorders USING btree (supplier_id);


--
-- Name: ix_preorders_supplier_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_preorders_supplier_status ON public.preorders USING btree (supplier_id, status);


--
-- Name: ix_preorders_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_preorders_updated_at ON public.preorders USING btree (updated_at);


--
-- Name: ix_preorders_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_preorders_warehouse_id ON public.preorders USING btree (warehouse_id);


--
-- Name: ix_product_categories_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_categories_created_at ON public.product_categories USING btree (created_at);


--
-- Name: ix_product_categories_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_categories_name ON public.product_categories USING btree (name);


--
-- Name: ix_product_categories_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_categories_updated_at ON public.product_categories USING btree (updated_at);


--
-- Name: ix_product_partner_pair; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_partner_pair ON public.product_partners USING btree (product_id, partner_id);


--
-- Name: ix_product_rating_helpful_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_rating_helpful_created_at ON public.product_rating_helpful USING btree (created_at);


--
-- Name: ix_product_rating_helpful_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_rating_helpful_updated_at ON public.product_rating_helpful USING btree (updated_at);


--
-- Name: ix_product_ratings_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_ratings_created_at ON public.product_ratings USING btree (created_at);


--
-- Name: ix_product_ratings_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_ratings_customer_id ON public.product_ratings USING btree (customer_id);


--
-- Name: ix_product_ratings_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_ratings_product_id ON public.product_ratings USING btree (product_id);


--
-- Name: ix_product_ratings_rating; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_ratings_rating ON public.product_ratings USING btree (rating);


--
-- Name: ix_product_ratings_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_ratings_updated_at ON public.product_ratings USING btree (updated_at);


--
-- Name: ix_product_supplier_loans_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_supplier_loans_created_at ON public.product_supplier_loans USING btree (created_at);


--
-- Name: ix_product_supplier_loans_is_settled; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_supplier_loans_is_settled ON public.product_supplier_loans USING btree (is_settled);


--
-- Name: ix_product_supplier_loans_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_supplier_loans_product_id ON public.product_supplier_loans USING btree (product_id);


--
-- Name: ix_product_supplier_loans_supplier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_supplier_loans_supplier_id ON public.product_supplier_loans USING btree (supplier_id);


--
-- Name: ix_product_supplier_loans_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_supplier_loans_updated_at ON public.product_supplier_loans USING btree (updated_at);


--
-- Name: ix_products_brand; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_brand ON public.products USING btree (brand);


--
-- Name: ix_products_brand_part; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_brand_part ON public.products USING btree (brand, part_number);


--
-- Name: ix_products_category_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_category_active ON public.products USING btree (category_id, is_active);


--
-- Name: ix_products_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_created_at ON public.products USING btree (created_at);


--
-- Name: ix_products_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_name ON public.products USING btree (name);


--
-- Name: ix_products_part_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_part_number ON public.products USING btree (part_number);


--
-- Name: ix_products_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_updated_at ON public.products USING btree (updated_at);


--
-- Name: ix_project_change_orders_approved_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_change_orders_approved_by ON public.project_change_orders USING btree (approved_by);


--
-- Name: ix_project_change_orders_approved_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_change_orders_approved_date ON public.project_change_orders USING btree (approved_date);


--
-- Name: ix_project_change_orders_change_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_project_change_orders_change_number ON public.project_change_orders USING btree (change_number);


--
-- Name: ix_project_change_orders_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_change_orders_created_at ON public.project_change_orders USING btree (created_at);


--
-- Name: ix_project_change_orders_implemented_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_change_orders_implemented_date ON public.project_change_orders USING btree (implemented_date);


--
-- Name: ix_project_change_orders_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_change_orders_project_id ON public.project_change_orders USING btree (project_id);


--
-- Name: ix_project_change_orders_requested_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_change_orders_requested_by ON public.project_change_orders USING btree (requested_by);


--
-- Name: ix_project_change_orders_requested_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_change_orders_requested_date ON public.project_change_orders USING btree (requested_date);


--
-- Name: ix_project_change_orders_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_change_orders_status ON public.project_change_orders USING btree (status);


--
-- Name: ix_project_change_orders_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_change_orders_updated_at ON public.project_change_orders USING btree (updated_at);


--
-- Name: ix_project_cost_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_cost_date ON public.project_costs USING btree (project_id, cost_date);


--
-- Name: ix_project_costs_cost_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_costs_cost_date ON public.project_costs USING btree (cost_date);


--
-- Name: ix_project_costs_cost_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_costs_cost_type ON public.project_costs USING btree (cost_type);


--
-- Name: ix_project_costs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_costs_created_at ON public.project_costs USING btree (created_at);


--
-- Name: ix_project_costs_gl_batch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_costs_gl_batch_id ON public.project_costs USING btree (gl_batch_id);


--
-- Name: ix_project_costs_phase_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_costs_phase_id ON public.project_costs USING btree (phase_id);


--
-- Name: ix_project_costs_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_costs_project_id ON public.project_costs USING btree (project_id);


--
-- Name: ix_project_costs_source_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_costs_source_id ON public.project_costs USING btree (source_id);


--
-- Name: ix_project_costs_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_costs_updated_at ON public.project_costs USING btree (updated_at);


--
-- Name: ix_project_issues_assigned_to; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_issues_assigned_to ON public.project_issues USING btree (assigned_to);


--
-- Name: ix_project_issues_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_issues_category ON public.project_issues USING btree (category);


--
-- Name: ix_project_issues_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_issues_created_at ON public.project_issues USING btree (created_at);


--
-- Name: ix_project_issues_issue_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_issues_issue_number ON public.project_issues USING btree (issue_number);


--
-- Name: ix_project_issues_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_issues_priority ON public.project_issues USING btree (priority);


--
-- Name: ix_project_issues_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_issues_project_id ON public.project_issues USING btree (project_id);


--
-- Name: ix_project_issues_reported_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_issues_reported_by ON public.project_issues USING btree (reported_by);


--
-- Name: ix_project_issues_reported_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_issues_reported_date ON public.project_issues USING btree (reported_date);


--
-- Name: ix_project_issues_resolved_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_issues_resolved_date ON public.project_issues USING btree (resolved_date);


--
-- Name: ix_project_issues_severity; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_issues_severity ON public.project_issues USING btree (severity);


--
-- Name: ix_project_issues_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_issues_status ON public.project_issues USING btree (status);


--
-- Name: ix_project_issues_task_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_issues_task_id ON public.project_issues USING btree (task_id);


--
-- Name: ix_project_issues_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_issues_updated_at ON public.project_issues USING btree (updated_at);


--
-- Name: ix_project_milestones_approved_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_milestones_approved_at ON public.project_milestones USING btree (approved_at);


--
-- Name: ix_project_milestones_approved_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_milestones_approved_by ON public.project_milestones USING btree (approved_by);


--
-- Name: ix_project_milestones_completed_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_milestones_completed_date ON public.project_milestones USING btree (completed_date);


--
-- Name: ix_project_milestones_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_milestones_created_at ON public.project_milestones USING btree (created_at);


--
-- Name: ix_project_milestones_due_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_milestones_due_date ON public.project_milestones USING btree (due_date);


--
-- Name: ix_project_milestones_invoice_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_milestones_invoice_id ON public.project_milestones USING btree (invoice_id);


--
-- Name: ix_project_milestones_milestone_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_milestones_milestone_number ON public.project_milestones USING btree (milestone_number);


--
-- Name: ix_project_milestones_phase_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_milestones_phase_id ON public.project_milestones USING btree (phase_id);


--
-- Name: ix_project_milestones_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_milestones_project_id ON public.project_milestones USING btree (project_id);


--
-- Name: ix_project_milestones_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_milestones_status ON public.project_milestones USING btree (status);


--
-- Name: ix_project_milestones_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_milestones_updated_at ON public.project_milestones USING btree (updated_at);


--
-- Name: ix_project_phase_project_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_phase_project_order ON public.project_phases USING btree (project_id, "order");


--
-- Name: ix_project_phases_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_phases_created_at ON public.project_phases USING btree (created_at);


--
-- Name: ix_project_phases_end_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_phases_end_date ON public.project_phases USING btree (end_date);


--
-- Name: ix_project_phases_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_phases_project_id ON public.project_phases USING btree (project_id);


--
-- Name: ix_project_phases_start_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_phases_start_date ON public.project_phases USING btree (start_date);


--
-- Name: ix_project_phases_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_phases_status ON public.project_phases USING btree (status);


--
-- Name: ix_project_phases_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_phases_updated_at ON public.project_phases USING btree (updated_at);


--
-- Name: ix_project_resource_project_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_resource_project_type ON public.project_resources USING btree (project_id, resource_type);


--
-- Name: ix_project_resources_allocation_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_resources_allocation_date ON public.project_resources USING btree (allocation_date);


--
-- Name: ix_project_resources_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_resources_created_at ON public.project_resources USING btree (created_at);


--
-- Name: ix_project_resources_employee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_resources_employee_id ON public.project_resources USING btree (employee_id);


--
-- Name: ix_project_resources_end_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_resources_end_date ON public.project_resources USING btree (end_date);


--
-- Name: ix_project_resources_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_resources_product_id ON public.project_resources USING btree (product_id);


--
-- Name: ix_project_resources_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_resources_project_id ON public.project_resources USING btree (project_id);


--
-- Name: ix_project_resources_resource_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_resources_resource_type ON public.project_resources USING btree (resource_type);


--
-- Name: ix_project_resources_start_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_resources_start_date ON public.project_resources USING btree (start_date);


--
-- Name: ix_project_resources_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_resources_status ON public.project_resources USING btree (status);


--
-- Name: ix_project_resources_task_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_resources_task_id ON public.project_resources USING btree (task_id);


--
-- Name: ix_project_resources_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_resources_updated_at ON public.project_resources USING btree (updated_at);


--
-- Name: ix_project_revenue_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_revenue_date ON public.project_revenues USING btree (project_id, revenue_date);


--
-- Name: ix_project_revenues_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_revenues_created_at ON public.project_revenues USING btree (created_at);


--
-- Name: ix_project_revenues_gl_batch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_revenues_gl_batch_id ON public.project_revenues USING btree (gl_batch_id);


--
-- Name: ix_project_revenues_phase_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_revenues_phase_id ON public.project_revenues USING btree (phase_id);


--
-- Name: ix_project_revenues_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_revenues_project_id ON public.project_revenues USING btree (project_id);


--
-- Name: ix_project_revenues_revenue_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_revenues_revenue_date ON public.project_revenues USING btree (revenue_date);


--
-- Name: ix_project_revenues_revenue_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_revenues_revenue_type ON public.project_revenues USING btree (revenue_type);


--
-- Name: ix_project_revenues_source_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_revenues_source_id ON public.project_revenues USING btree (source_id);


--
-- Name: ix_project_revenues_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_revenues_updated_at ON public.project_revenues USING btree (updated_at);


--
-- Name: ix_project_risks_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_risks_category ON public.project_risks USING btree (category);


--
-- Name: ix_project_risks_closed_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_risks_closed_date ON public.project_risks USING btree (closed_date);


--
-- Name: ix_project_risks_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_risks_created_at ON public.project_risks USING btree (created_at);


--
-- Name: ix_project_risks_identified_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_risks_identified_date ON public.project_risks USING btree (identified_date);


--
-- Name: ix_project_risks_impact; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_risks_impact ON public.project_risks USING btree (impact);


--
-- Name: ix_project_risks_owner_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_risks_owner_id ON public.project_risks USING btree (owner_id);


--
-- Name: ix_project_risks_probability; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_risks_probability ON public.project_risks USING btree (probability);


--
-- Name: ix_project_risks_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_risks_project_id ON public.project_risks USING btree (project_id);


--
-- Name: ix_project_risks_review_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_risks_review_date ON public.project_risks USING btree (review_date);


--
-- Name: ix_project_risks_risk_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_risks_risk_number ON public.project_risks USING btree (risk_number);


--
-- Name: ix_project_risks_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_risks_status ON public.project_risks USING btree (status);


--
-- Name: ix_project_risks_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_risks_updated_at ON public.project_risks USING btree (updated_at);


--
-- Name: ix_project_status_dates; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_status_dates ON public.projects USING btree (status, start_date, end_date);


--
-- Name: ix_project_task_assigned_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_task_assigned_status ON public.project_tasks USING btree (assigned_to, status);


--
-- Name: ix_project_task_project_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_task_project_status ON public.project_tasks USING btree (project_id, status);


--
-- Name: ix_project_tasks_assigned_to; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_tasks_assigned_to ON public.project_tasks USING btree (assigned_to);


--
-- Name: ix_project_tasks_completed_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_tasks_completed_date ON public.project_tasks USING btree (completed_date);


--
-- Name: ix_project_tasks_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_tasks_created_at ON public.project_tasks USING btree (created_at);


--
-- Name: ix_project_tasks_due_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_tasks_due_date ON public.project_tasks USING btree (due_date);


--
-- Name: ix_project_tasks_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_tasks_name ON public.project_tasks USING btree (name);


--
-- Name: ix_project_tasks_phase_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_tasks_phase_id ON public.project_tasks USING btree (phase_id);


--
-- Name: ix_project_tasks_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_tasks_priority ON public.project_tasks USING btree (priority);


--
-- Name: ix_project_tasks_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_tasks_project_id ON public.project_tasks USING btree (project_id);


--
-- Name: ix_project_tasks_start_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_tasks_start_date ON public.project_tasks USING btree (start_date);


--
-- Name: ix_project_tasks_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_tasks_status ON public.project_tasks USING btree (status);


--
-- Name: ix_project_tasks_task_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_tasks_task_number ON public.project_tasks USING btree (task_number);


--
-- Name: ix_project_tasks_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_tasks_updated_at ON public.project_tasks USING btree (updated_at);


--
-- Name: ix_projects_branch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_projects_branch_id ON public.projects USING btree (branch_id);


--
-- Name: ix_projects_client_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_projects_client_id ON public.projects USING btree (client_id);


--
-- Name: ix_projects_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_projects_code ON public.projects USING btree (code);


--
-- Name: ix_projects_cost_center_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_projects_cost_center_id ON public.projects USING btree (cost_center_id);


--
-- Name: ix_projects_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_projects_created_at ON public.projects USING btree (created_at);


--
-- Name: ix_projects_created_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_projects_created_by ON public.projects USING btree (created_by);


--
-- Name: ix_projects_end_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_projects_end_date ON public.projects USING btree (end_date);


--
-- Name: ix_projects_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_projects_is_active ON public.projects USING btree (is_active);


--
-- Name: ix_projects_manager_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_projects_manager_id ON public.projects USING btree (manager_id);


--
-- Name: ix_projects_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_projects_name ON public.projects USING btree (name);


--
-- Name: ix_projects_start_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_projects_start_date ON public.projects USING btree (start_date);


--
-- Name: ix_projects_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_projects_status ON public.projects USING btree (status);


--
-- Name: ix_projects_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_projects_updated_at ON public.projects USING btree (updated_at);


--
-- Name: ix_projects_updated_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_projects_updated_by ON public.projects USING btree (updated_by);


--
-- Name: ix_psl_product_supplier; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_psl_product_supplier ON public.product_supplier_loans USING btree (product_id, supplier_id);


--
-- Name: ix_psl_supplier_settled; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_psl_supplier_settled ON public.product_supplier_loans USING btree (supplier_id, is_settled);


--
-- Name: ix_rating_helpful_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_rating_helpful_customer_id ON public.product_rating_helpful USING btree (customer_id);


--
-- Name: ix_rating_helpful_ip; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_rating_helpful_ip ON public.product_rating_helpful USING btree (ip_address);


--
-- Name: ix_rating_helpful_rating_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_rating_helpful_rating_id ON public.product_rating_helpful USING btree (rating_id);


--
-- Name: ix_reconciliation_account_period; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reconciliation_account_period ON public.bank_reconciliations USING btree (bank_account_id, period_start, period_end);


--
-- Name: ix_recurring_invoice_schedules_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recurring_invoice_schedules_created_at ON public.recurring_invoice_schedules USING btree (created_at);


--
-- Name: ix_recurring_invoice_schedules_invoice_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recurring_invoice_schedules_invoice_id ON public.recurring_invoice_schedules USING btree (invoice_id);


--
-- Name: ix_recurring_invoice_schedules_scheduled_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recurring_invoice_schedules_scheduled_date ON public.recurring_invoice_schedules USING btree (scheduled_date);


--
-- Name: ix_recurring_invoice_schedules_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recurring_invoice_schedules_status ON public.recurring_invoice_schedules USING btree (status);


--
-- Name: ix_recurring_invoice_schedules_template_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recurring_invoice_schedules_template_id ON public.recurring_invoice_schedules USING btree (template_id);


--
-- Name: ix_recurring_invoice_schedules_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recurring_invoice_schedules_updated_at ON public.recurring_invoice_schedules USING btree (updated_at);


--
-- Name: ix_recurring_invoice_templates_branch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recurring_invoice_templates_branch_id ON public.recurring_invoice_templates USING btree (branch_id);


--
-- Name: ix_recurring_invoice_templates_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recurring_invoice_templates_created_at ON public.recurring_invoice_templates USING btree (created_at);


--
-- Name: ix_recurring_invoice_templates_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recurring_invoice_templates_customer_id ON public.recurring_invoice_templates USING btree (customer_id);


--
-- Name: ix_recurring_invoice_templates_frequency; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recurring_invoice_templates_frequency ON public.recurring_invoice_templates USING btree (frequency);


--
-- Name: ix_recurring_invoice_templates_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recurring_invoice_templates_is_active ON public.recurring_invoice_templates USING btree (is_active);


--
-- Name: ix_recurring_invoice_templates_next_invoice_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recurring_invoice_templates_next_invoice_date ON public.recurring_invoice_templates USING btree (next_invoice_date);


--
-- Name: ix_recurring_invoice_templates_site_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recurring_invoice_templates_site_id ON public.recurring_invoice_templates USING btree (site_id);


--
-- Name: ix_recurring_invoice_templates_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recurring_invoice_templates_updated_at ON public.recurring_invoice_templates USING btree (updated_at);


--
-- Name: ix_resource_time_logs_approved; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resource_time_logs_approved ON public.resource_time_logs USING btree (approved);


--
-- Name: ix_resource_time_logs_approved_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resource_time_logs_approved_by ON public.resource_time_logs USING btree (approved_by);


--
-- Name: ix_resource_time_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resource_time_logs_created_at ON public.resource_time_logs USING btree (created_at);


--
-- Name: ix_resource_time_logs_employee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resource_time_logs_employee_id ON public.resource_time_logs USING btree (employee_id);


--
-- Name: ix_resource_time_logs_log_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resource_time_logs_log_date ON public.resource_time_logs USING btree (log_date);


--
-- Name: ix_resource_time_logs_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resource_time_logs_project_id ON public.resource_time_logs USING btree (project_id);


--
-- Name: ix_resource_time_logs_resource_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resource_time_logs_resource_id ON public.resource_time_logs USING btree (resource_id);


--
-- Name: ix_resource_time_logs_task_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resource_time_logs_task_id ON public.resource_time_logs USING btree (task_id);


--
-- Name: ix_resource_time_logs_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resource_time_logs_updated_at ON public.resource_time_logs USING btree (updated_at);


--
-- Name: ix_risk_project_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_risk_project_status ON public.project_risks USING btree (project_id, status);


--
-- Name: ix_risk_score; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_risk_score ON public.project_risks USING btree (risk_score DESC);


--
-- Name: ix_roles_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_roles_name ON public.roles USING btree (name);


--
-- Name: ix_saas_invoices_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_saas_invoices_created_at ON public.saas_invoices USING btree (created_at);


--
-- Name: ix_saas_invoices_invoice_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_saas_invoices_invoice_number ON public.saas_invoices USING btree (invoice_number);


--
-- Name: ix_saas_invoices_subscription_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_saas_invoices_subscription_id ON public.saas_invoices USING btree (subscription_id);


--
-- Name: ix_saas_invoices_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_saas_invoices_updated_at ON public.saas_invoices USING btree (updated_at);


--
-- Name: ix_saas_plans_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_saas_plans_created_at ON public.saas_plans USING btree (created_at);


--
-- Name: ix_saas_plans_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_saas_plans_updated_at ON public.saas_plans USING btree (updated_at);


--
-- Name: ix_saas_subscriptions_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_saas_subscriptions_created_at ON public.saas_subscriptions USING btree (created_at);


--
-- Name: ix_saas_subscriptions_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_saas_subscriptions_customer_id ON public.saas_subscriptions USING btree (customer_id);


--
-- Name: ix_saas_subscriptions_plan_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_saas_subscriptions_plan_id ON public.saas_subscriptions USING btree (plan_id);


--
-- Name: ix_saas_subscriptions_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_saas_subscriptions_updated_at ON public.saas_subscriptions USING btree (updated_at);


--
-- Name: ix_sai_prod_wh; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sai_prod_wh ON public.stock_adjustment_items USING btree (product_id, warehouse_id);


--
-- Name: ix_sale_line_sale; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_line_sale ON public.sale_lines USING btree (sale_id);


--
-- Name: ix_sale_lines_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_lines_created_at ON public.sale_lines USING btree (created_at);


--
-- Name: ix_sale_lines_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_lines_product_id ON public.sale_lines USING btree (product_id);


--
-- Name: ix_sale_lines_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_lines_updated_at ON public.sale_lines USING btree (updated_at);


--
-- Name: ix_sale_lines_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_lines_warehouse_id ON public.sale_lines USING btree (warehouse_id);


--
-- Name: ix_sale_return_line_prod_wh; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_return_line_prod_wh ON public.sale_return_lines USING btree (product_id, warehouse_id);


--
-- Name: ix_sale_return_lines_condition; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_return_lines_condition ON public.sale_return_lines USING btree (condition);


--
-- Name: ix_sale_return_lines_liability_party; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_return_lines_liability_party ON public.sale_return_lines USING btree (liability_party);


--
-- Name: ix_sale_return_lines_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_return_lines_product_id ON public.sale_return_lines USING btree (product_id);


--
-- Name: ix_sale_return_lines_sale_return_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_return_lines_sale_return_id ON public.sale_return_lines USING btree (sale_return_id);


--
-- Name: ix_sale_return_lines_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_return_lines_warehouse_id ON public.sale_return_lines USING btree (warehouse_id);


--
-- Name: ix_sale_returns_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_returns_created_at ON public.sale_returns USING btree (created_at);


--
-- Name: ix_sale_returns_credit_note_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_returns_credit_note_id ON public.sale_returns USING btree (credit_note_id);


--
-- Name: ix_sale_returns_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_returns_customer_id ON public.sale_returns USING btree (customer_id);


--
-- Name: ix_sale_returns_sale_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_returns_sale_id ON public.sale_returns USING btree (sale_id);


--
-- Name: ix_sale_returns_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_returns_status ON public.sale_returns USING btree (status);


--
-- Name: ix_sale_returns_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_returns_updated_at ON public.sale_returns USING btree (updated_at);


--
-- Name: ix_sale_returns_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sale_returns_warehouse_id ON public.sale_returns USING btree (warehouse_id);


--
-- Name: ix_sales_archived_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_archived_at ON public.sales USING btree (archived_at);


--
-- Name: ix_sales_archived_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_archived_by ON public.sales USING btree (archived_by);


--
-- Name: ix_sales_cancelled_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_cancelled_at ON public.sales USING btree (cancelled_at);


--
-- Name: ix_sales_cancelled_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_cancelled_by ON public.sales USING btree (cancelled_by);


--
-- Name: ix_sales_cost_center_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_cost_center_id ON public.sales USING btree (cost_center_id);


--
-- Name: ix_sales_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_created_at ON public.sales USING btree (created_at);


--
-- Name: ix_sales_customer_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_customer_date ON public.sales USING btree (customer_id, sale_date);


--
-- Name: ix_sales_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_customer_id ON public.sales USING btree (customer_id);


--
-- Name: ix_sales_customer_status_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_customer_status_date ON public.sales USING btree (customer_id, status, sale_date);


--
-- Name: ix_sales_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_date ON public.sales USING btree (sale_date);


--
-- Name: ix_sales_idempotency_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sales_idempotency_key ON public.sales USING btree (idempotency_key);


--
-- Name: ix_sales_is_archived; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_is_archived ON public.sales USING btree (is_archived);


--
-- Name: ix_sales_payment_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_payment_status ON public.sales USING btree (payment_status);


--
-- Name: ix_sales_payment_status_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_payment_status_date ON public.sales USING btree (payment_status, sale_date);


--
-- Name: ix_sales_preorder_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_preorder_id ON public.sales USING btree (preorder_id);


--
-- Name: ix_sales_refund_of_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_refund_of_id ON public.sales USING btree (refund_of_id);


--
-- Name: ix_sales_sale_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_sale_date ON public.sales USING btree (sale_date);


--
-- Name: ix_sales_sale_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sales_sale_number ON public.sales USING btree (sale_number);


--
-- Name: ix_sales_seller_employee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_seller_employee_id ON public.sales USING btree (seller_employee_id);


--
-- Name: ix_sales_seller_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_seller_id ON public.sales USING btree (seller_id);


--
-- Name: ix_sales_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_status ON public.sales USING btree (status);


--
-- Name: ix_sales_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_updated_at ON public.sales USING btree (updated_at);


--
-- Name: ix_service_part_pair; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_part_pair ON public.service_parts USING btree (service_id, part_id);


--
-- Name: ix_service_part_partner; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_part_partner ON public.service_parts USING btree (partner_id);


--
-- Name: ix_service_parts_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_parts_created_at ON public.service_parts USING btree (created_at);


--
-- Name: ix_service_parts_part_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_parts_part_id ON public.service_parts USING btree (part_id);


--
-- Name: ix_service_parts_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_parts_updated_at ON public.service_parts USING btree (updated_at);


--
-- Name: ix_service_parts_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_parts_warehouse_id ON public.service_parts USING btree (warehouse_id);


--
-- Name: ix_service_received_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_received_active ON public.service_requests USING btree (received_at) WHERE ((status)::text = ANY ((ARRAY['PENDING'::character varying, 'IN_PROGRESS'::character varying, 'DIAGNOSIS'::character varying])::text[]));


--
-- Name: ix_service_requests_archived_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_archived_at ON public.service_requests USING btree (archived_at);


--
-- Name: ix_service_requests_archived_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_archived_by ON public.service_requests USING btree (archived_by);


--
-- Name: ix_service_requests_cancelled_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_cancelled_at ON public.service_requests USING btree (cancelled_at);


--
-- Name: ix_service_requests_cancelled_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_cancelled_by ON public.service_requests USING btree (cancelled_by);


--
-- Name: ix_service_requests_cost_center_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_cost_center_id ON public.service_requests USING btree (cost_center_id);


--
-- Name: ix_service_requests_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_created_at ON public.service_requests USING btree (created_at);


--
-- Name: ix_service_requests_customer_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_customer_date ON public.service_requests USING btree (customer_id, received_at);


--
-- Name: ix_service_requests_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_customer_id ON public.service_requests USING btree (customer_id);


--
-- Name: ix_service_requests_customer_status_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_customer_status_date ON public.service_requests USING btree (customer_id, status, received_at);


--
-- Name: ix_service_requests_idempotency_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_service_requests_idempotency_key ON public.service_requests USING btree (idempotency_key);


--
-- Name: ix_service_requests_is_archived; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_is_archived ON public.service_requests USING btree (is_archived);


--
-- Name: ix_service_requests_mechanic_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_mechanic_id ON public.service_requests USING btree (mechanic_id);


--
-- Name: ix_service_requests_mechanic_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_mechanic_status ON public.service_requests USING btree (mechanic_id, status);


--
-- Name: ix_service_requests_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_priority ON public.service_requests USING btree (priority);


--
-- Name: ix_service_requests_received_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_received_at ON public.service_requests USING btree (received_at);


--
-- Name: ix_service_requests_received_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_received_status ON public.service_requests USING btree (received_at, status);


--
-- Name: ix_service_requests_refund_of_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_refund_of_id ON public.service_requests USING btree (refund_of_id);


--
-- Name: ix_service_requests_service_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_service_requests_service_number ON public.service_requests USING btree (service_number);


--
-- Name: ix_service_requests_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_status ON public.service_requests USING btree (status);


--
-- Name: ix_service_requests_status_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_status_created_at ON public.service_requests USING btree (status, created_at);


--
-- Name: ix_service_requests_status_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_status_priority ON public.service_requests USING btree (status, priority);


--
-- Name: ix_service_requests_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_updated_at ON public.service_requests USING btree (updated_at);


--
-- Name: ix_service_requests_vehicle_type_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_requests_vehicle_type_id ON public.service_requests USING btree (vehicle_type_id);


--
-- Name: ix_service_task_partner; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_task_partner ON public.service_tasks USING btree (partner_id);


--
-- Name: ix_service_task_service; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_task_service ON public.service_tasks USING btree (service_id);


--
-- Name: ix_service_tasks_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_tasks_created_at ON public.service_tasks USING btree (created_at);


--
-- Name: ix_service_tasks_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_tasks_updated_at ON public.service_tasks USING btree (updated_at);


--
-- Name: ix_shipment_items_prod_wh; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipment_items_prod_wh ON public.shipment_items USING btree (product_id, warehouse_id);


--
-- Name: ix_shipment_items_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipment_items_product_id ON public.shipment_items USING btree (product_id);


--
-- Name: ix_shipment_items_shipment_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipment_items_shipment_id ON public.shipment_items USING btree (shipment_id);


--
-- Name: ix_shipment_items_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipment_items_warehouse_id ON public.shipment_items USING btree (warehouse_id);


--
-- Name: ix_shipment_partner_pair; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipment_partner_pair ON public.shipment_partners USING btree (shipment_id, partner_id);


--
-- Name: ix_shipment_partners_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipment_partners_created_at ON public.shipment_partners USING btree (created_at);


--
-- Name: ix_shipment_partners_partner_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipment_partners_partner_id ON public.shipment_partners USING btree (partner_id);


--
-- Name: ix_shipment_partners_shipment_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipment_partners_shipment_id ON public.shipment_partners USING btree (shipment_id);


--
-- Name: ix_shipment_partners_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipment_partners_updated_at ON public.shipment_partners USING btree (updated_at);


--
-- Name: ix_shipments_archived_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipments_archived_at ON public.shipments USING btree (archived_at);


--
-- Name: ix_shipments_archived_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipments_archived_by ON public.shipments USING btree (archived_by);


--
-- Name: ix_shipments_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipments_created_at ON public.shipments USING btree (created_at);


--
-- Name: ix_shipments_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipments_date ON public.shipments USING btree (date);


--
-- Name: ix_shipments_dest_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipments_dest_status ON public.shipments USING btree (destination_id, status);


--
-- Name: ix_shipments_destination_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipments_destination_id ON public.shipments USING btree (destination_id);


--
-- Name: ix_shipments_is_archived; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipments_is_archived ON public.shipments USING btree (is_archived);


--
-- Name: ix_shipments_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_shipments_number ON public.shipments USING btree (number);


--
-- Name: ix_shipments_sale_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipments_sale_id ON public.shipments USING btree (sale_id);


--
-- Name: ix_shipments_shipment_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipments_shipment_date ON public.shipments USING btree (shipment_date);


--
-- Name: ix_shipments_shipment_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_shipments_shipment_number ON public.shipments USING btree (shipment_number);


--
-- Name: ix_shipments_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipments_status ON public.shipments USING btree (status);


--
-- Name: ix_shipments_tracking_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipments_tracking_number ON public.shipments USING btree (tracking_number);


--
-- Name: ix_shipments_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipments_updated_at ON public.shipments USING btree (updated_at);


--
-- Name: ix_sites_archived_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sites_archived_at ON public.sites USING btree (archived_at);


--
-- Name: ix_sites_archived_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sites_archived_by ON public.sites USING btree (archived_by);


--
-- Name: ix_sites_branch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sites_branch_id ON public.sites USING btree (branch_id);


--
-- Name: ix_sites_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sites_code ON public.sites USING btree (code);


--
-- Name: ix_sites_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sites_created_at ON public.sites USING btree (created_at);


--
-- Name: ix_sites_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sites_is_active ON public.sites USING btree (is_active);


--
-- Name: ix_sites_is_archived; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sites_is_archived ON public.sites USING btree (is_archived);


--
-- Name: ix_sites_manager_employee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sites_manager_employee_id ON public.sites USING btree (manager_employee_id);


--
-- Name: ix_sites_manager_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sites_manager_user_id ON public.sites USING btree (manager_user_id);


--
-- Name: ix_sites_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sites_name ON public.sites USING btree (name);


--
-- Name: ix_sites_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sites_updated_at ON public.sites USING btree (updated_at);


--
-- Name: ix_skill_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_skill_category ON public.engineering_skills USING btree (category);


--
-- Name: ix_statement_account_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_statement_account_date ON public.bank_statements USING btree (bank_account_id, statement_date);


--
-- Name: ix_stock_adjust_wh_reason_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_adjust_wh_reason_date ON public.stock_adjustments USING btree (warehouse_id, reason, date);


--
-- Name: ix_stock_adjustment_items_adjustment_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_adjustment_items_adjustment_id ON public.stock_adjustment_items USING btree (adjustment_id);


--
-- Name: ix_stock_adjustment_items_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_adjustment_items_product_id ON public.stock_adjustment_items USING btree (product_id);


--
-- Name: ix_stock_adjustment_items_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_adjustment_items_warehouse_id ON public.stock_adjustment_items USING btree (warehouse_id);


--
-- Name: ix_stock_adjustments_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_adjustments_created_at ON public.stock_adjustments USING btree (created_at);


--
-- Name: ix_stock_adjustments_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_adjustments_date ON public.stock_adjustments USING btree (date);


--
-- Name: ix_stock_adjustments_reason; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_adjustments_reason ON public.stock_adjustments USING btree (reason);


--
-- Name: ix_stock_adjustments_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_adjustments_updated_at ON public.stock_adjustments USING btree (updated_at);


--
-- Name: ix_stock_adjustments_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_adjustments_warehouse_id ON public.stock_adjustments USING btree (warehouse_id);


--
-- Name: ix_stock_levels_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_levels_created_at ON public.stock_levels USING btree (created_at);


--
-- Name: ix_stock_levels_prod; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_levels_prod ON public.stock_levels USING btree (product_id);


--
-- Name: ix_stock_levels_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_levels_product_id ON public.stock_levels USING btree (product_id);


--
-- Name: ix_stock_levels_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_levels_updated_at ON public.stock_levels USING btree (updated_at);


--
-- Name: ix_stock_levels_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_levels_warehouse_id ON public.stock_levels USING btree (warehouse_id);


--
-- Name: ix_stock_levels_wh; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_levels_wh ON public.stock_levels USING btree (warehouse_id);


--
-- Name: ix_stock_levels_wh_prod; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_levels_wh_prod ON public.stock_levels USING btree (warehouse_id, product_id);


--
-- Name: ix_stock_product_wh; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_product_wh ON public.stock_levels USING btree (product_id, warehouse_id);


--
-- Name: ix_supplier_loan_settlements_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_loan_settlements_created_at ON public.supplier_loan_settlements USING btree (created_at);


--
-- Name: ix_supplier_loan_settlements_loan_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_loan_settlements_loan_id ON public.supplier_loan_settlements USING btree (loan_id);


--
-- Name: ix_supplier_loan_settlements_supplier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_loan_settlements_supplier_id ON public.supplier_loan_settlements USING btree (supplier_id);


--
-- Name: ix_supplier_loan_settlements_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_loan_settlements_updated_at ON public.supplier_loan_settlements USING btree (updated_at);


--
-- Name: ix_supplier_settlement_lines_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_settlement_lines_created_at ON public.supplier_settlement_lines USING btree (created_at);


--
-- Name: ix_supplier_settlement_lines_needs_pricing; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_settlement_lines_needs_pricing ON public.supplier_settlement_lines USING btree (needs_pricing);


--
-- Name: ix_supplier_settlement_lines_settlement_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_settlement_lines_settlement_id ON public.supplier_settlement_lines USING btree (settlement_id);


--
-- Name: ix_supplier_settlement_lines_source_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_settlement_lines_source_id ON public.supplier_settlement_lines USING btree (source_id);


--
-- Name: ix_supplier_settlement_lines_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_settlement_lines_updated_at ON public.supplier_settlement_lines USING btree (updated_at);


--
-- Name: ix_supplier_settlements_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_supplier_settlements_code ON public.supplier_settlements USING btree (code);


--
-- Name: ix_supplier_settlements_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_settlements_created_at ON public.supplier_settlements USING btree (created_at);


--
-- Name: ix_supplier_settlements_from_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_settlements_from_date ON public.supplier_settlements USING btree (from_date);


--
-- Name: ix_supplier_settlements_is_approved; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_settlements_is_approved ON public.supplier_settlements USING btree (is_approved);


--
-- Name: ix_supplier_settlements_mode; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_settlements_mode ON public.supplier_settlements USING btree (mode);


--
-- Name: ix_supplier_settlements_previous_settlement_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_settlements_previous_settlement_id ON public.supplier_settlements USING btree (previous_settlement_id);


--
-- Name: ix_supplier_settlements_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_settlements_status ON public.supplier_settlements USING btree (status);


--
-- Name: ix_supplier_settlements_supplier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_settlements_supplier_id ON public.supplier_settlements USING btree (supplier_id);


--
-- Name: ix_supplier_settlements_to_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_settlements_to_date ON public.supplier_settlements USING btree (to_date);


--
-- Name: ix_supplier_settlements_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_supplier_settlements_updated_at ON public.supplier_settlements USING btree (updated_at);


--
-- Name: ix_suppliers_archived_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suppliers_archived_at ON public.suppliers USING btree (archived_at);


--
-- Name: ix_suppliers_archived_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suppliers_archived_by ON public.suppliers USING btree (archived_by);


--
-- Name: ix_suppliers_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suppliers_created_at ON public.suppliers USING btree (created_at);


--
-- Name: ix_suppliers_currency; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suppliers_currency ON public.suppliers USING btree (currency);


--
-- Name: ix_suppliers_current_balance; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suppliers_current_balance ON public.suppliers USING btree (current_balance);


--
-- Name: ix_suppliers_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suppliers_customer_id ON public.suppliers USING btree (customer_id);


--
-- Name: ix_suppliers_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_suppliers_email ON public.suppliers USING btree (email);


--
-- Name: ix_suppliers_is_archived; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suppliers_is_archived ON public.suppliers USING btree (is_archived);


--
-- Name: ix_suppliers_lower_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suppliers_lower_email ON public.suppliers USING btree (lower((email)::text));


--
-- Name: ix_suppliers_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suppliers_name ON public.suppliers USING btree (name);


--
-- Name: ix_suppliers_phone; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suppliers_phone ON public.suppliers USING btree (phone);


--
-- Name: ix_suppliers_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suppliers_updated_at ON public.suppliers USING btree (updated_at);


--
-- Name: ix_system_settings_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_system_settings_key ON public.system_settings USING btree (key);


--
-- Name: ix_tax_entries_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tax_entries_created_at ON public.tax_entries USING btree (created_at);


--
-- Name: ix_tax_entries_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tax_entries_customer_id ON public.tax_entries USING btree (customer_id);


--
-- Name: ix_tax_entries_entry_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tax_entries_entry_type ON public.tax_entries USING btree (entry_type);


--
-- Name: ix_tax_entries_fiscal_month; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tax_entries_fiscal_month ON public.tax_entries USING btree (fiscal_month);


--
-- Name: ix_tax_entries_fiscal_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tax_entries_fiscal_year ON public.tax_entries USING btree (fiscal_year);


--
-- Name: ix_tax_entries_is_filed; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tax_entries_is_filed ON public.tax_entries USING btree (is_filed);


--
-- Name: ix_tax_entries_is_reconciled; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tax_entries_is_reconciled ON public.tax_entries USING btree (is_reconciled);


--
-- Name: ix_tax_entries_supplier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tax_entries_supplier_id ON public.tax_entries USING btree (supplier_id);


--
-- Name: ix_tax_entries_tax_period; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tax_entries_tax_period ON public.tax_entries USING btree (tax_period);


--
-- Name: ix_tax_entries_transaction_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tax_entries_transaction_id ON public.tax_entries USING btree (transaction_id);


--
-- Name: ix_tax_entries_transaction_reference; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tax_entries_transaction_reference ON public.tax_entries USING btree (transaction_reference);


--
-- Name: ix_tax_entries_transaction_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tax_entries_transaction_type ON public.tax_entries USING btree (transaction_type);


--
-- Name: ix_team_member_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_team_member_active ON public.engineering_team_members USING btree (is_active);


--
-- Name: ix_time_log_employee_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_time_log_employee_date ON public.resource_time_logs USING btree (employee_id, log_date);


--
-- Name: ix_time_log_project_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_time_log_project_date ON public.resource_time_logs USING btree (project_id, log_date);


--
-- Name: ix_timesheet_employee_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_timesheet_employee_date ON public.engineering_timesheets USING btree (employee_id, work_date);


--
-- Name: ix_timesheet_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_timesheet_status ON public.engineering_timesheets USING btree (status);


--
-- Name: ix_timesheet_task; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_timesheet_task ON public.engineering_timesheets USING btree (task_id);


--
-- Name: ix_transfers_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_transfers_created_at ON public.transfers USING btree (created_at);


--
-- Name: ix_transfers_transfer_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_transfers_transfer_date ON public.transfers USING btree (transfer_date);


--
-- Name: ix_transfers_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_transfers_updated_at ON public.transfers USING btree (updated_at);


--
-- Name: ix_user_branches_branch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_branches_branch_id ON public.user_branches USING btree (branch_id);


--
-- Name: ix_user_branches_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_branches_created_at ON public.user_branches USING btree (created_at);


--
-- Name: ix_user_branches_is_primary; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_branches_is_primary ON public.user_branches USING btree (is_primary);


--
-- Name: ix_user_branches_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_branches_updated_at ON public.user_branches USING btree (updated_at);


--
-- Name: ix_user_branches_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_branches_user_id ON public.user_branches USING btree (user_id);


--
-- Name: ix_users_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_created_at ON public.users USING btree (created_at);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_is_active ON public.users USING btree (is_active);


--
-- Name: ix_users_is_system_account; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_is_system_account ON public.users USING btree (is_system_account);


--
-- Name: ix_users_last_login; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_last_login ON public.users USING btree (last_login);


--
-- Name: ix_users_last_seen; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_last_seen ON public.users USING btree (last_seen);


--
-- Name: ix_users_lower_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_lower_email ON public.users USING btree (lower((email)::text));


--
-- Name: ix_users_lower_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_lower_username ON public.users USING btree (lower((username)::text));


--
-- Name: ix_users_role_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_role_id ON public.users USING btree (role_id);


--
-- Name: ix_users_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_updated_at ON public.users USING btree (updated_at);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: ix_utility_accounts_account_no; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_utility_accounts_account_no ON public.utility_accounts USING btree (account_no);


--
-- Name: ix_utility_accounts_alias; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_utility_accounts_alias ON public.utility_accounts USING btree (alias);


--
-- Name: ix_utility_accounts_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_utility_accounts_created_at ON public.utility_accounts USING btree (created_at);


--
-- Name: ix_utility_accounts_meter_no; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_utility_accounts_meter_no ON public.utility_accounts USING btree (meter_no);


--
-- Name: ix_utility_accounts_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_utility_accounts_updated_at ON public.utility_accounts USING btree (updated_at);


--
-- Name: ix_utility_accounts_utility_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_utility_accounts_utility_type ON public.utility_accounts USING btree (utility_type);


--
-- Name: ix_utility_active_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_utility_active_type ON public.utility_accounts USING btree (is_active, utility_type);


--
-- Name: ix_warehouse_partner_shares_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_partner_shares_created_at ON public.warehouse_partner_shares USING btree (created_at);


--
-- Name: ix_warehouse_partner_shares_partner_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_partner_shares_partner_id ON public.warehouse_partner_shares USING btree (partner_id);


--
-- Name: ix_warehouse_partner_shares_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_partner_shares_product_id ON public.warehouse_partner_shares USING btree (product_id);


--
-- Name: ix_warehouse_partner_shares_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_partner_shares_updated_at ON public.warehouse_partner_shares USING btree (updated_at);


--
-- Name: ix_warehouse_partner_shares_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_partner_shares_warehouse_id ON public.warehouse_partner_shares USING btree (warehouse_id);


--
-- Name: ix_warehouses_branch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouses_branch_id ON public.warehouses USING btree (branch_id);


--
-- Name: ix_warehouses_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouses_created_at ON public.warehouses USING btree (created_at);


--
-- Name: ix_warehouses_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouses_name ON public.warehouses USING btree (name);


--
-- Name: ix_warehouses_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouses_updated_at ON public.warehouses USING btree (updated_at);


--
-- Name: ix_warehouses_warehouse_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouses_warehouse_type ON public.warehouses USING btree (warehouse_type);


--
-- Name: ix_workflow_action_actor_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_action_actor_date ON public.workflow_actions USING btree (actor_id, action_date);


--
-- Name: ix_workflow_action_instance_step; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_action_instance_step ON public.workflow_actions USING btree (workflow_instance_id, step_number);


--
-- Name: ix_workflow_actions_action_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_actions_action_date ON public.workflow_actions USING btree (action_date);


--
-- Name: ix_workflow_actions_action_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_actions_action_type ON public.workflow_actions USING btree (action_type);


--
-- Name: ix_workflow_actions_actor_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_actions_actor_id ON public.workflow_actions USING btree (actor_id);


--
-- Name: ix_workflow_actions_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_actions_created_at ON public.workflow_actions USING btree (created_at);


--
-- Name: ix_workflow_actions_delegated_to; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_actions_delegated_to ON public.workflow_actions USING btree (delegated_to);


--
-- Name: ix_workflow_actions_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_actions_updated_at ON public.workflow_actions USING btree (updated_at);


--
-- Name: ix_workflow_actions_workflow_instance_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_actions_workflow_instance_id ON public.workflow_actions USING btree (workflow_instance_id);


--
-- Name: ix_workflow_def_entity_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_def_entity_active ON public.workflow_definitions USING btree (entity_type, is_active);


--
-- Name: ix_workflow_definitions_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_definitions_created_at ON public.workflow_definitions USING btree (created_at);


--
-- Name: ix_workflow_definitions_created_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_definitions_created_by ON public.workflow_definitions USING btree (created_by);


--
-- Name: ix_workflow_definitions_entity_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_definitions_entity_type ON public.workflow_definitions USING btree (entity_type);


--
-- Name: ix_workflow_definitions_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_definitions_is_active ON public.workflow_definitions USING btree (is_active);


--
-- Name: ix_workflow_definitions_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_definitions_updated_at ON public.workflow_definitions USING btree (updated_at);


--
-- Name: ix_workflow_definitions_updated_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_definitions_updated_by ON public.workflow_definitions USING btree (updated_by);


--
-- Name: ix_workflow_definitions_workflow_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_workflow_definitions_workflow_code ON public.workflow_definitions USING btree (workflow_code);


--
-- Name: ix_workflow_definitions_workflow_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_definitions_workflow_type ON public.workflow_definitions USING btree (workflow_type);


--
-- Name: ix_workflow_inst_entity; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_inst_entity ON public.workflow_instances USING btree (entity_type, entity_id);


--
-- Name: ix_workflow_inst_status_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_inst_status_date ON public.workflow_instances USING btree (status, started_at);


--
-- Name: ix_workflow_instances_cancelled_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_cancelled_at ON public.workflow_instances USING btree (cancelled_at);


--
-- Name: ix_workflow_instances_cancelled_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_cancelled_by ON public.workflow_instances USING btree (cancelled_by);


--
-- Name: ix_workflow_instances_completed_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_completed_at ON public.workflow_instances USING btree (completed_at);


--
-- Name: ix_workflow_instances_completed_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_completed_by ON public.workflow_instances USING btree (completed_by);


--
-- Name: ix_workflow_instances_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_created_at ON public.workflow_instances USING btree (created_at);


--
-- Name: ix_workflow_instances_due_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_due_date ON public.workflow_instances USING btree (due_date);


--
-- Name: ix_workflow_instances_entity_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_entity_id ON public.workflow_instances USING btree (entity_id);


--
-- Name: ix_workflow_instances_entity_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_entity_type ON public.workflow_instances USING btree (entity_type);


--
-- Name: ix_workflow_instances_instance_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_workflow_instances_instance_code ON public.workflow_instances USING btree (instance_code);


--
-- Name: ix_workflow_instances_started_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_started_at ON public.workflow_instances USING btree (started_at);


--
-- Name: ix_workflow_instances_started_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_started_by ON public.workflow_instances USING btree (started_by);


--
-- Name: ix_workflow_instances_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_status ON public.workflow_instances USING btree (status);


--
-- Name: ix_workflow_instances_updated_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_updated_at ON public.workflow_instances USING btree (updated_at);


--
-- Name: ix_workflow_instances_workflow_definition_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_workflow_definition_id ON public.workflow_instances USING btree (workflow_definition_id);


--
-- Name: ix_wps_partner_wh_prod; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_wps_partner_wh_prod ON public.warehouse_partner_shares USING btree (partner_id, warehouse_id, product_id);


--
-- Name: uq_products_barcode; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_products_barcode ON public.products USING btree (barcode) WHERE (barcode IS NOT NULL);


--
-- Name: uq_products_serial_ci; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_products_serial_ci ON public.products USING btree (lower((serial_no)::text)) WHERE (serial_no IS NOT NULL);


--
-- Name: uq_products_sku_ci; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_products_sku_ci ON public.products USING btree (lower((sku)::text)) WHERE (sku IS NOT NULL);


--
-- Name: archives archives_archived_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.archives
    ADD CONSTRAINT archives_archived_by_fkey FOREIGN KEY (archived_by) REFERENCES public.users(id);


--
-- Name: asset_depreciations asset_depreciations_asset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_depreciations
    ADD CONSTRAINT asset_depreciations_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.fixed_assets(id) ON DELETE CASCADE;


--
-- Name: asset_depreciations asset_depreciations_gl_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_depreciations
    ADD CONSTRAINT asset_depreciations_gl_batch_id_fkey FOREIGN KEY (gl_batch_id) REFERENCES public.gl_batches(id);


--
-- Name: asset_maintenance asset_maintenance_asset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_maintenance
    ADD CONSTRAINT asset_maintenance_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.fixed_assets(id) ON DELETE CASCADE;


--
-- Name: asset_maintenance asset_maintenance_expense_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_maintenance
    ADD CONSTRAINT asset_maintenance_expense_id_fkey FOREIGN KEY (expense_id) REFERENCES public.expenses(id);


--
-- Name: audit_logs audit_logs_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id) ON DELETE SET NULL;


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: auth_audit auth_audit_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_audit
    ADD CONSTRAINT auth_audit_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: bank_accounts bank_accounts_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_accounts
    ADD CONSTRAINT bank_accounts_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: bank_accounts bank_accounts_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_accounts
    ADD CONSTRAINT bank_accounts_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: bank_accounts bank_accounts_gl_account_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_accounts
    ADD CONSTRAINT bank_accounts_gl_account_code_fkey FOREIGN KEY (gl_account_code) REFERENCES public.accounts(code) ON DELETE RESTRICT;


--
-- Name: bank_accounts bank_accounts_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_accounts
    ADD CONSTRAINT bank_accounts_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: bank_reconciliations bank_reconciliations_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_reconciliations
    ADD CONSTRAINT bank_reconciliations_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: bank_reconciliations bank_reconciliations_bank_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_reconciliations
    ADD CONSTRAINT bank_reconciliations_bank_account_id_fkey FOREIGN KEY (bank_account_id) REFERENCES public.bank_accounts(id) ON DELETE CASCADE;


--
-- Name: bank_reconciliations bank_reconciliations_reconciled_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_reconciliations
    ADD CONSTRAINT bank_reconciliations_reconciled_by_fkey FOREIGN KEY (reconciled_by) REFERENCES public.users(id);


--
-- Name: bank_statements bank_statements_bank_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_statements
    ADD CONSTRAINT bank_statements_bank_account_id_fkey FOREIGN KEY (bank_account_id) REFERENCES public.bank_accounts(id) ON DELETE CASCADE;


--
-- Name: bank_statements bank_statements_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_statements
    ADD CONSTRAINT bank_statements_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: bank_statements bank_statements_imported_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_statements
    ADD CONSTRAINT bank_statements_imported_by_fkey FOREIGN KEY (imported_by) REFERENCES public.users(id);


--
-- Name: bank_statements bank_statements_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_statements
    ADD CONSTRAINT bank_statements_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: bank_transactions bank_transactions_bank_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_transactions
    ADD CONSTRAINT bank_transactions_bank_account_id_fkey FOREIGN KEY (bank_account_id) REFERENCES public.bank_accounts(id) ON DELETE CASCADE;


--
-- Name: bank_transactions bank_transactions_gl_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_transactions
    ADD CONSTRAINT bank_transactions_gl_batch_id_fkey FOREIGN KEY (gl_batch_id) REFERENCES public.gl_batches(id);


--
-- Name: bank_transactions bank_transactions_payment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_transactions
    ADD CONSTRAINT bank_transactions_payment_id_fkey FOREIGN KEY (payment_id) REFERENCES public.payments(id);


--
-- Name: bank_transactions bank_transactions_reconciliation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_transactions
    ADD CONSTRAINT bank_transactions_reconciliation_id_fkey FOREIGN KEY (reconciliation_id) REFERENCES public.bank_reconciliations(id);


--
-- Name: bank_transactions bank_transactions_statement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_transactions
    ADD CONSTRAINT bank_transactions_statement_id_fkey FOREIGN KEY (statement_id) REFERENCES public.bank_statements(id) ON DELETE CASCADE;


--
-- Name: branches branches_archived_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT branches_archived_by_fkey FOREIGN KEY (archived_by) REFERENCES public.users(id);


--
-- Name: branches branches_manager_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT branches_manager_employee_id_fkey FOREIGN KEY (manager_employee_id) REFERENCES public.employees(id);


--
-- Name: branches branches_manager_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT branches_manager_user_id_fkey FOREIGN KEY (manager_user_id) REFERENCES public.users(id);


--
-- Name: budget_commitments budget_commitments_budget_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.budget_commitments
    ADD CONSTRAINT budget_commitments_budget_id_fkey FOREIGN KEY (budget_id) REFERENCES public.budgets(id) ON DELETE CASCADE;


--
-- Name: budgets budgets_account_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.budgets
    ADD CONSTRAINT budgets_account_code_fkey FOREIGN KEY (account_code) REFERENCES public.accounts(code) ON DELETE RESTRICT;


--
-- Name: budgets budgets_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.budgets
    ADD CONSTRAINT budgets_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE CASCADE;


--
-- Name: budgets budgets_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.budgets
    ADD CONSTRAINT budgets_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id) ON DELETE CASCADE;


--
-- Name: checks checks_archived_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.checks
    ADD CONSTRAINT checks_archived_by_fkey FOREIGN KEY (archived_by) REFERENCES public.users(id);


--
-- Name: checks checks_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.checks
    ADD CONSTRAINT checks_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id);


--
-- Name: checks checks_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.checks
    ADD CONSTRAINT checks_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id) ON DELETE SET NULL;


--
-- Name: checks checks_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.checks
    ADD CONSTRAINT checks_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id) ON DELETE SET NULL;


--
-- Name: checks checks_payment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.checks
    ADD CONSTRAINT checks_payment_id_fkey FOREIGN KEY (payment_id) REFERENCES public.payments(id) ON DELETE SET NULL;


--
-- Name: checks checks_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.checks
    ADD CONSTRAINT checks_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id) ON DELETE SET NULL;


--
-- Name: cost_allocation_execution_lines cost_allocation_execution_lines_execution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_execution_lines
    ADD CONSTRAINT cost_allocation_execution_lines_execution_id_fkey FOREIGN KEY (execution_id) REFERENCES public.cost_allocation_executions(id) ON DELETE CASCADE;


--
-- Name: cost_allocation_execution_lines cost_allocation_execution_lines_gl_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_execution_lines
    ADD CONSTRAINT cost_allocation_execution_lines_gl_batch_id_fkey FOREIGN KEY (gl_batch_id) REFERENCES public.gl_batches(id);


--
-- Name: cost_allocation_execution_lines cost_allocation_execution_lines_source_cost_center_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_execution_lines
    ADD CONSTRAINT cost_allocation_execution_lines_source_cost_center_id_fkey FOREIGN KEY (source_cost_center_id) REFERENCES public.cost_centers(id);


--
-- Name: cost_allocation_execution_lines cost_allocation_execution_lines_target_cost_center_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_execution_lines
    ADD CONSTRAINT cost_allocation_execution_lines_target_cost_center_id_fkey FOREIGN KEY (target_cost_center_id) REFERENCES public.cost_centers(id);


--
-- Name: cost_allocation_executions cost_allocation_executions_gl_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_executions
    ADD CONSTRAINT cost_allocation_executions_gl_batch_id_fkey FOREIGN KEY (gl_batch_id) REFERENCES public.gl_batches(id);


--
-- Name: cost_allocation_executions cost_allocation_executions_rule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_executions
    ADD CONSTRAINT cost_allocation_executions_rule_id_fkey FOREIGN KEY (rule_id) REFERENCES public.cost_allocation_rules(id);


--
-- Name: cost_allocation_lines cost_allocation_lines_rule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_lines
    ADD CONSTRAINT cost_allocation_lines_rule_id_fkey FOREIGN KEY (rule_id) REFERENCES public.cost_allocation_rules(id) ON DELETE CASCADE;


--
-- Name: cost_allocation_lines cost_allocation_lines_target_cost_center_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_lines
    ADD CONSTRAINT cost_allocation_lines_target_cost_center_id_fkey FOREIGN KEY (target_cost_center_id) REFERENCES public.cost_centers(id);


--
-- Name: cost_allocation_rules cost_allocation_rules_source_cost_center_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_allocation_rules
    ADD CONSTRAINT cost_allocation_rules_source_cost_center_id_fkey FOREIGN KEY (source_cost_center_id) REFERENCES public.cost_centers(id);


--
-- Name: cost_center_alert_logs cost_center_alert_logs_alert_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_center_alert_logs
    ADD CONSTRAINT cost_center_alert_logs_alert_id_fkey FOREIGN KEY (alert_id) REFERENCES public.cost_center_alerts(id) ON DELETE CASCADE;


--
-- Name: cost_center_alert_logs cost_center_alert_logs_cost_center_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_center_alert_logs
    ADD CONSTRAINT cost_center_alert_logs_cost_center_id_fkey FOREIGN KEY (cost_center_id) REFERENCES public.cost_centers(id);


--
-- Name: cost_center_alerts cost_center_alerts_cost_center_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_center_alerts
    ADD CONSTRAINT cost_center_alerts_cost_center_id_fkey FOREIGN KEY (cost_center_id) REFERENCES public.cost_centers(id) ON DELETE CASCADE;


--
-- Name: cost_center_allocations cost_center_allocations_cost_center_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_center_allocations
    ADD CONSTRAINT cost_center_allocations_cost_center_id_fkey FOREIGN KEY (cost_center_id) REFERENCES public.cost_centers(id) ON DELETE CASCADE;


--
-- Name: cost_centers cost_centers_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_centers
    ADD CONSTRAINT cost_centers_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: cost_centers cost_centers_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_centers
    ADD CONSTRAINT cost_centers_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.users(id);


--
-- Name: cost_centers cost_centers_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_centers
    ADD CONSTRAINT cost_centers_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.cost_centers(id);


--
-- Name: cost_centers cost_centers_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_centers
    ADD CONSTRAINT cost_centers_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: customer_loyalty customer_loyalty_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_loyalty
    ADD CONSTRAINT customer_loyalty_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: customer_loyalty_points customer_loyalty_points_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_loyalty_points
    ADD CONSTRAINT customer_loyalty_points_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: customers customers_archived_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_archived_by_fkey FOREIGN KEY (archived_by) REFERENCES public.users(id);


--
-- Name: deletion_logs deletion_logs_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deletion_logs
    ADD CONSTRAINT deletion_logs_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: deletion_logs deletion_logs_restored_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deletion_logs
    ADD CONSTRAINT deletion_logs_restored_by_fkey FOREIGN KEY (restored_by) REFERENCES public.users(id);


--
-- Name: employee_advance_installments employee_advance_installments_advance_expense_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_advance_installments
    ADD CONSTRAINT employee_advance_installments_advance_expense_id_fkey FOREIGN KEY (advance_expense_id) REFERENCES public.expenses(id);


--
-- Name: employee_advance_installments employee_advance_installments_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_advance_installments
    ADD CONSTRAINT employee_advance_installments_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: employee_advance_installments employee_advance_installments_paid_in_salary_expense_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_advance_installments
    ADD CONSTRAINT employee_advance_installments_paid_in_salary_expense_id_fkey FOREIGN KEY (paid_in_salary_expense_id) REFERENCES public.expenses(id);


--
-- Name: employee_advances employee_advances_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_advances
    ADD CONSTRAINT employee_advances_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: employee_advances employee_advances_expense_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_advances
    ADD CONSTRAINT employee_advances_expense_id_fkey FOREIGN KEY (expense_id) REFERENCES public.expenses(id);


--
-- Name: employee_deductions employee_deductions_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_deductions
    ADD CONSTRAINT employee_deductions_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: employee_deductions employee_deductions_expense_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_deductions
    ADD CONSTRAINT employee_deductions_expense_id_fkey FOREIGN KEY (expense_id) REFERENCES public.expenses(id);


--
-- Name: employee_skills employee_skills_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_skills
    ADD CONSTRAINT employee_skills_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: employee_skills employee_skills_skill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_skills
    ADD CONSTRAINT employee_skills_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.engineering_skills(id);


--
-- Name: employee_skills employee_skills_verified_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_skills
    ADD CONSTRAINT employee_skills_verified_by_fkey FOREIGN KEY (verified_by) REFERENCES public.users(id);


--
-- Name: employees employees_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: employees employees_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id);


--
-- Name: engineering_tasks engineering_tasks_assigned_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_tasks
    ADD CONSTRAINT engineering_tasks_assigned_team_id_fkey FOREIGN KEY (assigned_team_id) REFERENCES public.engineering_teams(id);


--
-- Name: engineering_tasks engineering_tasks_assigned_to_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_tasks
    ADD CONSTRAINT engineering_tasks_assigned_to_id_fkey FOREIGN KEY (assigned_to_id) REFERENCES public.employees(id);


--
-- Name: engineering_tasks engineering_tasks_cost_center_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_tasks
    ADD CONSTRAINT engineering_tasks_cost_center_id_fkey FOREIGN KEY (cost_center_id) REFERENCES public.cost_centers(id);


--
-- Name: engineering_tasks engineering_tasks_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_tasks
    ADD CONSTRAINT engineering_tasks_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: engineering_tasks engineering_tasks_gl_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_tasks
    ADD CONSTRAINT engineering_tasks_gl_batch_id_fkey FOREIGN KEY (gl_batch_id) REFERENCES public.gl_batches(id);


--
-- Name: engineering_tasks engineering_tasks_parent_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_tasks
    ADD CONSTRAINT engineering_tasks_parent_task_id_fkey FOREIGN KEY (parent_task_id) REFERENCES public.engineering_tasks(id);


--
-- Name: engineering_tasks engineering_tasks_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_tasks
    ADD CONSTRAINT engineering_tasks_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: engineering_tasks engineering_tasks_service_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_tasks
    ADD CONSTRAINT engineering_tasks_service_request_id_fkey FOREIGN KEY (service_request_id) REFERENCES public.service_requests(id);


--
-- Name: engineering_team_members engineering_team_members_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_team_members
    ADD CONSTRAINT engineering_team_members_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: engineering_team_members engineering_team_members_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_team_members
    ADD CONSTRAINT engineering_team_members_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.engineering_teams(id) ON DELETE CASCADE;


--
-- Name: engineering_teams engineering_teams_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_teams
    ADD CONSTRAINT engineering_teams_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: engineering_teams engineering_teams_cost_center_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_teams
    ADD CONSTRAINT engineering_teams_cost_center_id_fkey FOREIGN KEY (cost_center_id) REFERENCES public.cost_centers(id);


--
-- Name: engineering_teams engineering_teams_team_leader_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_teams
    ADD CONSTRAINT engineering_teams_team_leader_id_fkey FOREIGN KEY (team_leader_id) REFERENCES public.employees(id);


--
-- Name: engineering_timesheets engineering_timesheets_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_timesheets
    ADD CONSTRAINT engineering_timesheets_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: engineering_timesheets engineering_timesheets_cost_center_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_timesheets
    ADD CONSTRAINT engineering_timesheets_cost_center_id_fkey FOREIGN KEY (cost_center_id) REFERENCES public.cost_centers(id);


--
-- Name: engineering_timesheets engineering_timesheets_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_timesheets
    ADD CONSTRAINT engineering_timesheets_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: engineering_timesheets engineering_timesheets_gl_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_timesheets
    ADD CONSTRAINT engineering_timesheets_gl_batch_id_fkey FOREIGN KEY (gl_batch_id) REFERENCES public.gl_batches(id);


--
-- Name: engineering_timesheets engineering_timesheets_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.engineering_timesheets
    ADD CONSTRAINT engineering_timesheets_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.engineering_tasks(id);


--
-- Name: exchange_rates exchange_rates_base_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exchange_rates
    ADD CONSTRAINT exchange_rates_base_code_fkey FOREIGN KEY (base_code) REFERENCES public.currencies(code);


--
-- Name: exchange_rates exchange_rates_quote_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exchange_rates
    ADD CONSTRAINT exchange_rates_quote_code_fkey FOREIGN KEY (quote_code) REFERENCES public.currencies(code);


--
-- Name: exchange_transactions exchange_transactions_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exchange_transactions
    ADD CONSTRAINT exchange_transactions_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id);


--
-- Name: exchange_transactions exchange_transactions_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exchange_transactions
    ADD CONSTRAINT exchange_transactions_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: exchange_transactions exchange_transactions_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exchange_transactions
    ADD CONSTRAINT exchange_transactions_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id);


--
-- Name: exchange_transactions exchange_transactions_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exchange_transactions
    ADD CONSTRAINT exchange_transactions_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: expenses expenses_archived_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_archived_by_fkey FOREIGN KEY (archived_by) REFERENCES public.users(id);


--
-- Name: expenses expenses_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: expenses expenses_cost_center_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_cost_center_id_fkey FOREIGN KEY (cost_center_id) REFERENCES public.cost_centers(id);


--
-- Name: expenses expenses_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id) ON DELETE SET NULL;


--
-- Name: expenses expenses_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE SET NULL;


--
-- Name: expenses expenses_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id) ON DELETE SET NULL;


--
-- Name: expenses expenses_shipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_shipment_id_fkey FOREIGN KEY (shipment_id) REFERENCES public.shipments(id) ON DELETE SET NULL;


--
-- Name: expenses expenses_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id);


--
-- Name: expenses expenses_stock_adjustment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_stock_adjustment_id_fkey FOREIGN KEY (stock_adjustment_id) REFERENCES public.stock_adjustments(id) ON DELETE SET NULL;


--
-- Name: expenses expenses_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id) ON DELETE SET NULL;


--
-- Name: expenses expenses_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.expense_types(id) ON DELETE RESTRICT;


--
-- Name: expenses expenses_utility_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_utility_account_id_fkey FOREIGN KEY (utility_account_id) REFERENCES public.utility_accounts(id) ON DELETE SET NULL;


--
-- Name: expenses expenses_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE SET NULL;


--
-- Name: fixed_asset_categories fixed_asset_categories_account_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fixed_asset_categories
    ADD CONSTRAINT fixed_asset_categories_account_code_fkey FOREIGN KEY (account_code) REFERENCES public.accounts(code) ON DELETE RESTRICT;


--
-- Name: fixed_asset_categories fixed_asset_categories_depreciation_account_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fixed_asset_categories
    ADD CONSTRAINT fixed_asset_categories_depreciation_account_code_fkey FOREIGN KEY (depreciation_account_code) REFERENCES public.accounts(code) ON DELETE RESTRICT;


--
-- Name: fixed_assets fixed_assets_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fixed_assets
    ADD CONSTRAINT fixed_assets_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE CASCADE;


--
-- Name: fixed_assets fixed_assets_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fixed_assets
    ADD CONSTRAINT fixed_assets_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.fixed_asset_categories(id) ON DELETE RESTRICT;


--
-- Name: fixed_assets fixed_assets_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fixed_assets
    ADD CONSTRAINT fixed_assets_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id) ON DELETE CASCADE;


--
-- Name: fixed_assets fixed_assets_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fixed_assets
    ADD CONSTRAINT fixed_assets_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.partners(id);


--
-- Name: gl_entries gl_entries_account_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gl_entries
    ADD CONSTRAINT gl_entries_account_fkey FOREIGN KEY (account) REFERENCES public.accounts(code) ON DELETE RESTRICT;


--
-- Name: gl_entries gl_entries_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gl_entries
    ADD CONSTRAINT gl_entries_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES public.gl_batches(id) ON DELETE CASCADE;


--
-- Name: import_runs import_runs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.import_runs
    ADD CONSTRAINT import_runs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: import_runs import_runs_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.import_runs
    ADD CONSTRAINT import_runs_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE SET NULL;


--
-- Name: invoice_lines invoice_lines_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoice_lines
    ADD CONSTRAINT invoice_lines_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id);


--
-- Name: invoice_lines invoice_lines_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoice_lines
    ADD CONSTRAINT invoice_lines_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: invoices invoices_cancelled_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_cancelled_by_fkey FOREIGN KEY (cancelled_by) REFERENCES public.users(id);


--
-- Name: invoices invoices_credit_for_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_credit_for_id_fkey FOREIGN KEY (credit_for_id) REFERENCES public.invoices(id) ON DELETE SET NULL;


--
-- Name: invoices invoices_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: invoices invoices_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id);


--
-- Name: invoices invoices_preorder_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_preorder_id_fkey FOREIGN KEY (preorder_id) REFERENCES public.preorders(id);


--
-- Name: invoices invoices_refund_of_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_refund_of_id_fkey FOREIGN KEY (refund_of_id) REFERENCES public.invoices(id) ON DELETE SET NULL;


--
-- Name: invoices invoices_sale_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_sale_id_fkey FOREIGN KEY (sale_id) REFERENCES public.sales(id);


--
-- Name: invoices invoices_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.service_requests(id);


--
-- Name: invoices invoices_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id);


--
-- Name: notes notes_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notes
    ADD CONSTRAINT notes_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: notification_logs notification_logs_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_logs
    ADD CONSTRAINT notification_logs_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id) ON DELETE SET NULL;


--
-- Name: notification_logs notification_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_logs
    ADD CONSTRAINT notification_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: online_cart_items online_cart_items_cart_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_cart_items
    ADD CONSTRAINT online_cart_items_cart_id_fkey FOREIGN KEY (cart_id) REFERENCES public.online_carts(id) ON DELETE CASCADE;


--
-- Name: online_cart_items online_cart_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_cart_items
    ADD CONSTRAINT online_cart_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE RESTRICT;


--
-- Name: online_carts online_carts_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_carts
    ADD CONSTRAINT online_carts_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id) ON DELETE SET NULL;


--
-- Name: online_payments online_payments_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_payments
    ADD CONSTRAINT online_payments_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.online_preorders(id) ON DELETE CASCADE;


--
-- Name: online_payments online_payments_payment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_payments
    ADD CONSTRAINT online_payments_payment_id_fkey FOREIGN KEY (payment_id) REFERENCES public.payments(id) ON DELETE SET NULL;


--
-- Name: online_preorder_items online_preorder_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_preorder_items
    ADD CONSTRAINT online_preorder_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.online_preorders(id) ON DELETE CASCADE;


--
-- Name: online_preorder_items online_preorder_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_preorder_items
    ADD CONSTRAINT online_preorder_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE RESTRICT;


--
-- Name: online_preorders online_preorders_cart_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_preorders
    ADD CONSTRAINT online_preorders_cart_id_fkey FOREIGN KEY (cart_id) REFERENCES public.online_carts(id) ON DELETE SET NULL;


--
-- Name: online_preorders online_preorders_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_preorders
    ADD CONSTRAINT online_preorders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id) ON DELETE CASCADE;


--
-- Name: online_preorders online_preorders_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.online_preorders
    ADD CONSTRAINT online_preorders_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE SET NULL;


--
-- Name: partner_settlement_lines partner_settlement_lines_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_settlement_lines
    ADD CONSTRAINT partner_settlement_lines_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: partner_settlement_lines partner_settlement_lines_settlement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_settlement_lines
    ADD CONSTRAINT partner_settlement_lines_settlement_id_fkey FOREIGN KEY (settlement_id) REFERENCES public.partner_settlements(id) ON DELETE CASCADE;


--
-- Name: partner_settlement_lines partner_settlement_lines_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_settlement_lines
    ADD CONSTRAINT partner_settlement_lines_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: partner_settlements partner_settlements_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_settlements
    ADD CONSTRAINT partner_settlements_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: partner_settlements partner_settlements_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_settlements
    ADD CONSTRAINT partner_settlements_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id);


--
-- Name: partner_settlements partner_settlements_previous_settlement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_settlements
    ADD CONSTRAINT partner_settlements_previous_settlement_id_fkey FOREIGN KEY (previous_settlement_id) REFERENCES public.partner_settlements(id);


--
-- Name: partners partners_archived_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partners
    ADD CONSTRAINT partners_archived_by_fkey FOREIGN KEY (archived_by) REFERENCES public.users(id);


--
-- Name: partners partners_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partners
    ADD CONSTRAINT partners_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: payment_splits payment_splits_payment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_splits
    ADD CONSTRAINT payment_splits_payment_id_fkey FOREIGN KEY (payment_id) REFERENCES public.payments(id) ON DELETE CASCADE;


--
-- Name: payments payments_archived_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_archived_by_fkey FOREIGN KEY (archived_by) REFERENCES public.users(id);


--
-- Name: payments payments_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: payments payments_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id) ON DELETE CASCADE;


--
-- Name: payments payments_expense_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_expense_id_fkey FOREIGN KEY (expense_id) REFERENCES public.expenses(id) ON DELETE CASCADE;


--
-- Name: payments payments_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id) ON DELETE CASCADE;


--
-- Name: payments payments_loan_settlement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_loan_settlement_id_fkey FOREIGN KEY (loan_settlement_id) REFERENCES public.supplier_loan_settlements(id) ON DELETE CASCADE;


--
-- Name: payments payments_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id) ON DELETE CASCADE;


--
-- Name: payments payments_preorder_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_preorder_id_fkey FOREIGN KEY (preorder_id) REFERENCES public.preorders(id) ON DELETE CASCADE;


--
-- Name: payments payments_refund_of_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_refund_of_id_fkey FOREIGN KEY (refund_of_id) REFERENCES public.payments(id) ON DELETE SET NULL;


--
-- Name: payments payments_sale_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_sale_id_fkey FOREIGN KEY (sale_id) REFERENCES public.sales(id) ON DELETE CASCADE;


--
-- Name: payments payments_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.service_requests(id) ON DELETE CASCADE;


--
-- Name: payments payments_shipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_shipment_id_fkey FOREIGN KEY (shipment_id) REFERENCES public.shipments(id) ON DELETE CASCADE;


--
-- Name: payments payments_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id) ON DELETE CASCADE;


--
-- Name: preorders preorders_cancelled_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.preorders
    ADD CONSTRAINT preorders_cancelled_by_fkey FOREIGN KEY (cancelled_by) REFERENCES public.users(id);


--
-- Name: preorders preorders_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.preorders
    ADD CONSTRAINT preorders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: preorders preorders_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.preorders
    ADD CONSTRAINT preorders_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id);


--
-- Name: preorders preorders_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.preorders
    ADD CONSTRAINT preorders_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: preorders preorders_refund_of_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.preorders
    ADD CONSTRAINT preorders_refund_of_id_fkey FOREIGN KEY (refund_of_id) REFERENCES public.preorders(id) ON DELETE SET NULL;


--
-- Name: preorders preorders_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.preorders
    ADD CONSTRAINT preorders_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id);


--
-- Name: preorders preorders_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.preorders
    ADD CONSTRAINT preorders_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: product_categories product_categories_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_categories
    ADD CONSTRAINT product_categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.product_categories(id);


--
-- Name: product_partners product_partners_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_partners
    ADD CONSTRAINT product_partners_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id);


--
-- Name: product_partners product_partners_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_partners
    ADD CONSTRAINT product_partners_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: product_rating_helpful product_rating_helpful_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_rating_helpful
    ADD CONSTRAINT product_rating_helpful_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: product_rating_helpful product_rating_helpful_rating_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_rating_helpful
    ADD CONSTRAINT product_rating_helpful_rating_id_fkey FOREIGN KEY (rating_id) REFERENCES public.product_ratings(id);


--
-- Name: product_ratings product_ratings_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_ratings
    ADD CONSTRAINT product_ratings_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: product_ratings product_ratings_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_ratings
    ADD CONSTRAINT product_ratings_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: product_supplier_loans product_supplier_loans_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_supplier_loans
    ADD CONSTRAINT product_supplier_loans_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: product_supplier_loans product_supplier_loans_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_supplier_loans
    ADD CONSTRAINT product_supplier_loans_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id);


--
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.product_categories(id);


--
-- Name: products products_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id);


--
-- Name: products products_supplier_international_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_supplier_international_id_fkey FOREIGN KEY (supplier_international_id) REFERENCES public.suppliers(id);


--
-- Name: products products_supplier_local_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_supplier_local_id_fkey FOREIGN KEY (supplier_local_id) REFERENCES public.suppliers(id);


--
-- Name: products products_vehicle_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_vehicle_type_id_fkey FOREIGN KEY (vehicle_type_id) REFERENCES public.equipment_types(id);


--
-- Name: project_change_orders project_change_orders_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_change_orders
    ADD CONSTRAINT project_change_orders_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: project_change_orders project_change_orders_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_change_orders
    ADD CONSTRAINT project_change_orders_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: project_change_orders project_change_orders_requested_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_change_orders
    ADD CONSTRAINT project_change_orders_requested_by_fkey FOREIGN KEY (requested_by) REFERENCES public.users(id);


--
-- Name: project_costs project_costs_gl_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_costs
    ADD CONSTRAINT project_costs_gl_batch_id_fkey FOREIGN KEY (gl_batch_id) REFERENCES public.gl_batches(id);


--
-- Name: project_costs project_costs_phase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_costs
    ADD CONSTRAINT project_costs_phase_id_fkey FOREIGN KEY (phase_id) REFERENCES public.project_phases(id) ON DELETE SET NULL;


--
-- Name: project_costs project_costs_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_costs
    ADD CONSTRAINT project_costs_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: project_issues project_issues_assigned_to_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_issues
    ADD CONSTRAINT project_issues_assigned_to_fkey FOREIGN KEY (assigned_to) REFERENCES public.users(id);


--
-- Name: project_issues project_issues_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_issues
    ADD CONSTRAINT project_issues_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: project_issues project_issues_reported_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_issues
    ADD CONSTRAINT project_issues_reported_by_fkey FOREIGN KEY (reported_by) REFERENCES public.users(id);


--
-- Name: project_issues project_issues_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_issues
    ADD CONSTRAINT project_issues_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.project_tasks(id) ON DELETE SET NULL;


--
-- Name: project_milestones project_milestones_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_milestones
    ADD CONSTRAINT project_milestones_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: project_milestones project_milestones_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_milestones
    ADD CONSTRAINT project_milestones_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id);


--
-- Name: project_milestones project_milestones_phase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_milestones
    ADD CONSTRAINT project_milestones_phase_id_fkey FOREIGN KEY (phase_id) REFERENCES public.project_phases(id) ON DELETE SET NULL;


--
-- Name: project_milestones project_milestones_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_milestones
    ADD CONSTRAINT project_milestones_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: project_phases project_phases_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_phases
    ADD CONSTRAINT project_phases_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: project_resources project_resources_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_resources
    ADD CONSTRAINT project_resources_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: project_resources project_resources_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_resources
    ADD CONSTRAINT project_resources_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: project_resources project_resources_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_resources
    ADD CONSTRAINT project_resources_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: project_resources project_resources_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_resources
    ADD CONSTRAINT project_resources_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.project_tasks(id) ON DELETE CASCADE;


--
-- Name: project_revenues project_revenues_gl_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_revenues
    ADD CONSTRAINT project_revenues_gl_batch_id_fkey FOREIGN KEY (gl_batch_id) REFERENCES public.gl_batches(id);


--
-- Name: project_revenues project_revenues_phase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_revenues
    ADD CONSTRAINT project_revenues_phase_id_fkey FOREIGN KEY (phase_id) REFERENCES public.project_phases(id) ON DELETE SET NULL;


--
-- Name: project_revenues project_revenues_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_revenues
    ADD CONSTRAINT project_revenues_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: project_risks project_risks_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_risks
    ADD CONSTRAINT project_risks_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- Name: project_risks project_risks_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_risks
    ADD CONSTRAINT project_risks_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: project_tasks project_tasks_assigned_to_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_tasks
    ADD CONSTRAINT project_tasks_assigned_to_fkey FOREIGN KEY (assigned_to) REFERENCES public.users(id);


--
-- Name: project_tasks project_tasks_phase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_tasks
    ADD CONSTRAINT project_tasks_phase_id_fkey FOREIGN KEY (phase_id) REFERENCES public.project_phases(id) ON DELETE SET NULL;


--
-- Name: project_tasks project_tasks_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_tasks
    ADD CONSTRAINT project_tasks_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: projects projects_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: projects projects_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.customers(id);


--
-- Name: projects projects_cost_center_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_cost_center_id_fkey FOREIGN KEY (cost_center_id) REFERENCES public.cost_centers(id);


--
-- Name: projects projects_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: projects projects_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.users(id);


--
-- Name: projects projects_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: recurring_invoice_schedules recurring_invoice_schedules_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recurring_invoice_schedules
    ADD CONSTRAINT recurring_invoice_schedules_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id);


--
-- Name: recurring_invoice_schedules recurring_invoice_schedules_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recurring_invoice_schedules
    ADD CONSTRAINT recurring_invoice_schedules_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.recurring_invoice_templates(id) ON DELETE CASCADE;


--
-- Name: recurring_invoice_templates recurring_invoice_templates_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recurring_invoice_templates
    ADD CONSTRAINT recurring_invoice_templates_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: recurring_invoice_templates recurring_invoice_templates_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recurring_invoice_templates
    ADD CONSTRAINT recurring_invoice_templates_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: recurring_invoice_templates recurring_invoice_templates_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recurring_invoice_templates
    ADD CONSTRAINT recurring_invoice_templates_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id);


--
-- Name: resource_time_logs resource_time_logs_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resource_time_logs
    ADD CONSTRAINT resource_time_logs_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: resource_time_logs resource_time_logs_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resource_time_logs
    ADD CONSTRAINT resource_time_logs_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: resource_time_logs resource_time_logs_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resource_time_logs
    ADD CONSTRAINT resource_time_logs_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: resource_time_logs resource_time_logs_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resource_time_logs
    ADD CONSTRAINT resource_time_logs_resource_id_fkey FOREIGN KEY (resource_id) REFERENCES public.project_resources(id) ON DELETE CASCADE;


--
-- Name: resource_time_logs resource_time_logs_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resource_time_logs
    ADD CONSTRAINT resource_time_logs_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.project_tasks(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id);


--
-- Name: role_permissions role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: saas_invoices saas_invoices_subscription_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_invoices
    ADD CONSTRAINT saas_invoices_subscription_id_fkey FOREIGN KEY (subscription_id) REFERENCES public.saas_subscriptions(id);


--
-- Name: saas_subscriptions saas_subscriptions_cancelled_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_subscriptions
    ADD CONSTRAINT saas_subscriptions_cancelled_by_fkey FOREIGN KEY (cancelled_by) REFERENCES public.users(id);


--
-- Name: saas_subscriptions saas_subscriptions_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_subscriptions
    ADD CONSTRAINT saas_subscriptions_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: saas_subscriptions saas_subscriptions_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_subscriptions
    ADD CONSTRAINT saas_subscriptions_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.saas_plans(id);


--
-- Name: sale_lines sale_lines_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_lines
    ADD CONSTRAINT sale_lines_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: sale_lines sale_lines_sale_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_lines
    ADD CONSTRAINT sale_lines_sale_id_fkey FOREIGN KEY (sale_id) REFERENCES public.sales(id);


--
-- Name: sale_lines sale_lines_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_lines
    ADD CONSTRAINT sale_lines_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: sale_return_lines sale_return_lines_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_return_lines
    ADD CONSTRAINT sale_return_lines_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: sale_return_lines sale_return_lines_sale_return_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_return_lines
    ADD CONSTRAINT sale_return_lines_sale_return_id_fkey FOREIGN KEY (sale_return_id) REFERENCES public.sale_returns(id) ON DELETE CASCADE;


--
-- Name: sale_return_lines sale_return_lines_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_return_lines
    ADD CONSTRAINT sale_return_lines_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE SET NULL;


--
-- Name: sale_returns sale_returns_credit_note_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_returns
    ADD CONSTRAINT sale_returns_credit_note_id_fkey FOREIGN KEY (credit_note_id) REFERENCES public.invoices(id) ON DELETE SET NULL;


--
-- Name: sale_returns sale_returns_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_returns
    ADD CONSTRAINT sale_returns_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id) ON DELETE SET NULL;


--
-- Name: sale_returns sale_returns_sale_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_returns
    ADD CONSTRAINT sale_returns_sale_id_fkey FOREIGN KEY (sale_id) REFERENCES public.sales(id) ON DELETE SET NULL;


--
-- Name: sale_returns sale_returns_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_returns
    ADD CONSTRAINT sale_returns_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE SET NULL;


--
-- Name: sales sales_archived_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_archived_by_fkey FOREIGN KEY (archived_by) REFERENCES public.users(id);


--
-- Name: sales sales_cancelled_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_cancelled_by_fkey FOREIGN KEY (cancelled_by) REFERENCES public.users(id);


--
-- Name: sales sales_cost_center_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_cost_center_id_fkey FOREIGN KEY (cost_center_id) REFERENCES public.cost_centers(id);


--
-- Name: sales sales_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: sales sales_preorder_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_preorder_id_fkey FOREIGN KEY (preorder_id) REFERENCES public.preorders(id);


--
-- Name: sales sales_refund_of_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_refund_of_id_fkey FOREIGN KEY (refund_of_id) REFERENCES public.sales(id) ON DELETE SET NULL;


--
-- Name: sales sales_seller_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_seller_employee_id_fkey FOREIGN KEY (seller_employee_id) REFERENCES public.employees(id) ON DELETE SET NULL;


--
-- Name: sales sales_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.users(id);


--
-- Name: service_parts service_parts_part_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_parts
    ADD CONSTRAINT service_parts_part_id_fkey FOREIGN KEY (part_id) REFERENCES public.products(id);


--
-- Name: service_parts service_parts_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_parts
    ADD CONSTRAINT service_parts_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id);


--
-- Name: service_parts service_parts_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_parts
    ADD CONSTRAINT service_parts_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.service_requests(id) ON DELETE CASCADE;


--
-- Name: service_parts service_parts_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_parts
    ADD CONSTRAINT service_parts_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: service_requests service_requests_archived_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_archived_by_fkey FOREIGN KEY (archived_by) REFERENCES public.users(id);


--
-- Name: service_requests service_requests_cancelled_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_cancelled_by_fkey FOREIGN KEY (cancelled_by) REFERENCES public.users(id);


--
-- Name: service_requests service_requests_cost_center_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_cost_center_id_fkey FOREIGN KEY (cost_center_id) REFERENCES public.cost_centers(id);


--
-- Name: service_requests service_requests_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: service_requests service_requests_mechanic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_mechanic_id_fkey FOREIGN KEY (mechanic_id) REFERENCES public.users(id);


--
-- Name: service_requests service_requests_refund_of_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_refund_of_id_fkey FOREIGN KEY (refund_of_id) REFERENCES public.service_requests(id) ON DELETE SET NULL;


--
-- Name: service_requests service_requests_vehicle_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_vehicle_type_id_fkey FOREIGN KEY (vehicle_type_id) REFERENCES public.equipment_types(id);


--
-- Name: service_tasks service_tasks_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_tasks
    ADD CONSTRAINT service_tasks_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id);


--
-- Name: service_tasks service_tasks_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_tasks
    ADD CONSTRAINT service_tasks_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.service_requests(id) ON DELETE CASCADE;


--
-- Name: shipment_items shipment_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipment_items
    ADD CONSTRAINT shipment_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: shipment_items shipment_items_shipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipment_items
    ADD CONSTRAINT shipment_items_shipment_id_fkey FOREIGN KEY (shipment_id) REFERENCES public.shipments(id) ON DELETE CASCADE;


--
-- Name: shipment_items shipment_items_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipment_items
    ADD CONSTRAINT shipment_items_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE SET NULL;


--
-- Name: shipment_partners shipment_partners_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipment_partners
    ADD CONSTRAINT shipment_partners_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id) ON DELETE CASCADE;


--
-- Name: shipment_partners shipment_partners_shipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipment_partners
    ADD CONSTRAINT shipment_partners_shipment_id_fkey FOREIGN KEY (shipment_id) REFERENCES public.shipments(id) ON DELETE CASCADE;


--
-- Name: shipments shipments_archived_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipments
    ADD CONSTRAINT shipments_archived_by_fkey FOREIGN KEY (archived_by) REFERENCES public.users(id);


--
-- Name: shipments shipments_destination_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipments
    ADD CONSTRAINT shipments_destination_id_fkey FOREIGN KEY (destination_id) REFERENCES public.warehouses(id) ON DELETE SET NULL;


--
-- Name: shipments shipments_sale_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipments
    ADD CONSTRAINT shipments_sale_id_fkey FOREIGN KEY (sale_id) REFERENCES public.sales(id);


--
-- Name: sites sites_archived_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sites
    ADD CONSTRAINT sites_archived_by_fkey FOREIGN KEY (archived_by) REFERENCES public.users(id);


--
-- Name: sites sites_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sites
    ADD CONSTRAINT sites_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: sites sites_manager_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sites
    ADD CONSTRAINT sites_manager_employee_id_fkey FOREIGN KEY (manager_employee_id) REFERENCES public.employees(id);


--
-- Name: sites sites_manager_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sites
    ADD CONSTRAINT sites_manager_user_id_fkey FOREIGN KEY (manager_user_id) REFERENCES public.users(id);


--
-- Name: stock_adjustment_items stock_adjustment_items_adjustment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_adjustment_items
    ADD CONSTRAINT stock_adjustment_items_adjustment_id_fkey FOREIGN KEY (adjustment_id) REFERENCES public.stock_adjustments(id) ON DELETE CASCADE;


--
-- Name: stock_adjustment_items stock_adjustment_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_adjustment_items
    ADD CONSTRAINT stock_adjustment_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: stock_adjustment_items stock_adjustment_items_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_adjustment_items
    ADD CONSTRAINT stock_adjustment_items_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE SET NULL;


--
-- Name: stock_adjustments stock_adjustments_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_adjustments
    ADD CONSTRAINT stock_adjustments_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE SET NULL;


--
-- Name: stock_levels stock_levels_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_levels
    ADD CONSTRAINT stock_levels_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: stock_levels stock_levels_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_levels
    ADD CONSTRAINT stock_levels_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: supplier_loan_settlements supplier_loan_settlements_loan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.supplier_loan_settlements
    ADD CONSTRAINT supplier_loan_settlements_loan_id_fkey FOREIGN KEY (loan_id) REFERENCES public.product_supplier_loans(id) ON DELETE CASCADE;


--
-- Name: supplier_loan_settlements supplier_loan_settlements_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.supplier_loan_settlements
    ADD CONSTRAINT supplier_loan_settlements_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id) ON DELETE SET NULL;


--
-- Name: supplier_settlement_lines supplier_settlement_lines_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.supplier_settlement_lines
    ADD CONSTRAINT supplier_settlement_lines_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: supplier_settlement_lines supplier_settlement_lines_settlement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.supplier_settlement_lines
    ADD CONSTRAINT supplier_settlement_lines_settlement_id_fkey FOREIGN KEY (settlement_id) REFERENCES public.supplier_settlements(id) ON DELETE CASCADE;


--
-- Name: supplier_settlements supplier_settlements_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.supplier_settlements
    ADD CONSTRAINT supplier_settlements_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: supplier_settlements supplier_settlements_previous_settlement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.supplier_settlements
    ADD CONSTRAINT supplier_settlements_previous_settlement_id_fkey FOREIGN KEY (previous_settlement_id) REFERENCES public.supplier_settlements(id);


--
-- Name: supplier_settlements supplier_settlements_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.supplier_settlements
    ADD CONSTRAINT supplier_settlements_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id);


--
-- Name: suppliers suppliers_archived_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_archived_by_fkey FOREIGN KEY (archived_by) REFERENCES public.users(id);


--
-- Name: suppliers suppliers_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: tax_entries tax_entries_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tax_entries
    ADD CONSTRAINT tax_entries_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: tax_entries tax_entries_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tax_entries
    ADD CONSTRAINT tax_entries_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id) ON DELETE SET NULL;


--
-- Name: tax_entries tax_entries_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tax_entries
    ADD CONSTRAINT tax_entries_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id) ON DELETE SET NULL;


--
-- Name: transfers transfers_destination_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transfers
    ADD CONSTRAINT transfers_destination_id_fkey FOREIGN KEY (destination_id) REFERENCES public.warehouses(id);


--
-- Name: transfers transfers_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transfers
    ADD CONSTRAINT transfers_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: transfers transfers_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transfers
    ADD CONSTRAINT transfers_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.warehouses(id);


--
-- Name: transfers transfers_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transfers
    ADD CONSTRAINT transfers_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_branches user_branches_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_branches
    ADD CONSTRAINT user_branches_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: user_branches user_branches_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_branches
    ADD CONSTRAINT user_branches_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_permissions user_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id);


--
-- Name: user_permissions user_permissions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_permissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: warehouse_partner_shares warehouse_partner_shares_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_partner_shares
    ADD CONSTRAINT warehouse_partner_shares_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id);


--
-- Name: warehouse_partner_shares warehouse_partner_shares_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_partner_shares
    ADD CONSTRAINT warehouse_partner_shares_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: warehouse_partner_shares warehouse_partner_shares_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_partner_shares
    ADD CONSTRAINT warehouse_partner_shares_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: warehouses warehouses_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: warehouses warehouses_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.warehouses(id);


--
-- Name: warehouses warehouses_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id);


--
-- Name: warehouses warehouses_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id);


--
-- Name: workflow_actions workflow_actions_actor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_actions
    ADD CONSTRAINT workflow_actions_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES public.users(id);


--
-- Name: workflow_actions workflow_actions_delegated_to_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_actions
    ADD CONSTRAINT workflow_actions_delegated_to_fkey FOREIGN KEY (delegated_to) REFERENCES public.users(id);


--
-- Name: workflow_actions workflow_actions_workflow_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_actions
    ADD CONSTRAINT workflow_actions_workflow_instance_id_fkey FOREIGN KEY (workflow_instance_id) REFERENCES public.workflow_instances(id) ON DELETE CASCADE;


--
-- Name: workflow_definitions workflow_definitions_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_definitions
    ADD CONSTRAINT workflow_definitions_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: workflow_definitions workflow_definitions_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_definitions
    ADD CONSTRAINT workflow_definitions_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: workflow_instances workflow_instances_cancelled_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_instances
    ADD CONSTRAINT workflow_instances_cancelled_by_fkey FOREIGN KEY (cancelled_by) REFERENCES public.users(id);


--
-- Name: workflow_instances workflow_instances_completed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_instances
    ADD CONSTRAINT workflow_instances_completed_by_fkey FOREIGN KEY (completed_by) REFERENCES public.users(id);


--
-- Name: workflow_instances workflow_instances_started_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_instances
    ADD CONSTRAINT workflow_instances_started_by_fkey FOREIGN KEY (started_by) REFERENCES public.users(id);


--
-- Name: workflow_instances workflow_instances_workflow_definition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_instances
    ADD CONSTRAINT workflow_instances_workflow_definition_id_fkey FOREIGN KEY (workflow_definition_id) REFERENCES public.workflow_definitions(id) ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

\unrestrict h6FqF4nHdwSqoCRRxR0wKhsDb6mcbovXo1umyDbbcR0KhwpAFDLiuBERA4fqVfs

