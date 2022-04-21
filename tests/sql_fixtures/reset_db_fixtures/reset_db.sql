--
-- PostgreSQL database dump
--

-- Dumped from database version 14.1 (Debian 14.1-1.pgdg110+1)
-- Dumped by pg_dump version 14.2 (Debian 14.2-1.pgdg100+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: delete_workspace(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.delete_workspace(_workspace_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
  rcount integer;
BEGIN
  RAISE NOTICE 'Deleting data from workspace % ', _workspace_id;

  DELETE
  FROM task_logs tl
  WHERE tl.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % task_logs', rcount;

  DELETE
  FROM bill_lineitems bl
  WHERE bl.bill_id IN (
      SELECT b.id FROM bills b WHERE b.expense_group_id IN (
          SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
      ) 
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % bill_lineitems', rcount;

  DELETE
  FROM bills b
  WHERE b.expense_group_id IN (
      SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % bills', rcount;

  DELETE
  FROM qbo_expense_lineitems qel
  WHERE qel.qbo_expense_id IN (
      SELECT qe.id FROM qbo_expenses qe WHERE qe.expense_group_id IN (
          SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
      )
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % qbo_expense_lineitems', rcount;

  DELETE
  FROM qbo_expenses qe
  WHERE qe.expense_group_id IN (
      SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % qbo_expenses', rcount;

  DELETE
  FROM cheque_lineitems cl
  WHERE cl.cheque_id IN (
      SELECT c.id FROM cheques c WHERE c.expense_group_id IN (
          SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
      )
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % cheque_lineitems', rcount;

  DELETE
  FROM cheques c
  WHERE c.expense_group_id IN (
      SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % cheques', rcount;

  DELETE
  FROM credit_card_purchase_lineitems ccpl
  WHERE ccpl.credit_card_purchase_id IN (
      SELECT ccp.id FROM credit_card_purchases ccp WHERE ccp.expense_group_id IN (
          SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
      )
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % credit_card_purchase_lineitems', rcount;

  DELETE
  FROM credit_card_purchases ccp
  WHERE ccp.expense_group_id IN (
      SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % credit_card_purchases', rcount;

  DELETE
  FROM journal_entry_lineitems jel
  WHERE jel.journal_entry_id IN (
      SELECT c.id FROM journal_entries c WHERE c.expense_group_id IN (
          SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
      )
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % journal_entry_lineitems', rcount;

  DELETE
  FROM journal_entries je
  WHERE je.expense_group_id IN (
      SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % journal_entries', rcount;

  DELETE
  FROM bill_payment_lineitems bpl
  WHERE bpl.bill_payment_id IN (
      SELECT bp.id FROM bill_payments bp WHERE bp.expense_group_id IN (
          SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
      )
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % bill_payment_lineitems', rcount;

  DELETE
  FROM bill_payments bp
  WHERE bp.expense_group_id IN (
      SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % bill_payments', rcount;

  DELETE
  FROM reimbursements r
  WHERE r.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % reimbursements', rcount;

  DELETE
  FROM expenses e
  WHERE e.id IN (
      SELECT expense_id FROM expense_groups_expenses ege WHERE ege.expensegroup_id IN (
          SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
      )
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % expenses', rcount;

  DELETE
  FROM expense_groups_expenses ege
  WHERE ege.expensegroup_id IN (
      SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % expense_groups_expenses', rcount;

  DELETE
  FROM expense_groups eg
  WHERE eg.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % expense_groups', rcount;

  DELETE
  FROM employee_mappings em
  WHERE em.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % employee_mappings', rcount;

  DELETE
  FROM category_mappings cm
  WHERE cm.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % category_mappings', rcount;

  DELETE
  FROM mappings m
  WHERE m.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % mappings', rcount;

  DELETE
  FROM mapping_settings ms
  WHERE ms.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % mapping_settings', rcount;

  DELETE
  FROM general_mappings gm
  WHERE gm.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % general_mappings', rcount;

  DELETE
  FROM workspace_general_settings wgs
  WHERE wgs.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % workspace_general_settings', rcount;

  DELETE
  FROM expense_group_settings egs
  WHERE egs.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % expense_group_settings', rcount;

  DELETE
  FROM fyle_credentials fc
  WHERE fc.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % fyle_credentials', rcount;

  DELETE
  FROM qbo_credentials qc
  WHERE qc.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % qbo_credentials', rcount;

  DELETE
  FROM expense_attributes ea
  WHERE ea.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % expense_attributes', rcount;

  DELETE
  FROM destination_attributes da
  WHERE da.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % destination_attributes', rcount;

  DELETE
  FROM workspace_schedules wsch
  WHERE wsch.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % workspace_schedules', rcount;

  DELETE
  FROM django_q_schedule dqs
  WHERE dqs.args = _workspace_id::varchar(255);
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % django_q_schedule', rcount;

  DELETE
  FROM auth_tokens aut
  WHERE aut.user_id IN (
      SELECT u.id FROM users u WHERE u.id IN (
          SELECT wu.user_id FROM workspaces_user wu WHERE workspace_id = _workspace_id
      )
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % auth_tokens', rcount;

  DELETE
  FROM workspaces_user wu
  WHERE workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % workspaces_user', rcount;

  DELETE
  FROM users u
  WHERE u.id IN (
      SELECT wu.user_id FROM workspaces_user wu WHERE workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % users', rcount;

  DELETE
  FROM workspaces w
  WHERE w.id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % workspaces', rcount;

RETURN;
END
$$;


ALTER FUNCTION public.delete_workspace(_workspace_id integer) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_group_id_seq OWNED BY public.auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_group_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_group_permissions_id_seq OWNED BY public.auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_permission_id_seq OWNED BY public.auth_permission.id;


--
-- Name: auth_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_tokens (
    id integer NOT NULL,
    refresh_token text NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.auth_tokens OWNER TO postgres;

--
-- Name: bill_lineitems; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bill_lineitems (
    id integer NOT NULL,
    account_id character varying(255) NOT NULL,
    class_id character varying(255),
    customer_id character varying(255),
    amount double precision NOT NULL,
    description text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    bill_id integer NOT NULL,
    expense_id integer NOT NULL,
    billable boolean,
    tax_amount double precision,
    tax_code character varying(255)
);


ALTER TABLE public.bill_lineitems OWNER TO postgres;

--
-- Name: bill_payment_lineitems; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bill_payment_lineitems (
    id integer NOT NULL,
    amount double precision NOT NULL,
    linked_transaction_id character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    bill_payment_id integer NOT NULL
);


ALTER TABLE public.bill_payment_lineitems OWNER TO postgres;

--
-- Name: bill_payment_lineitems_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bill_payment_lineitems_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bill_payment_lineitems_id_seq OWNER TO postgres;

--
-- Name: bill_payment_lineitems_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bill_payment_lineitems_id_seq OWNED BY public.bill_payment_lineitems.id;


--
-- Name: bill_payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bill_payments (
    id integer NOT NULL,
    private_note text NOT NULL,
    vendor_id character varying(255) NOT NULL,
    amount double precision NOT NULL,
    currency character varying(255) NOT NULL,
    payment_account character varying(255) NOT NULL,
    accounts_payable_id character varying(255) NOT NULL,
    department_id character varying(255),
    transaction_date date NOT NULL,
    bill_payment_number character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    expense_group_id integer NOT NULL
);


ALTER TABLE public.bill_payments OWNER TO postgres;

--
-- Name: bill_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bill_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bill_payments_id_seq OWNER TO postgres;

--
-- Name: bill_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bill_payments_id_seq OWNED BY public.bill_payments.id;


--
-- Name: bills; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bills (
    id integer NOT NULL,
    accounts_payable_id character varying(255) NOT NULL,
    vendor_id character varying(255) NOT NULL,
    department_id character varying(255),
    transaction_date date NOT NULL,
    currency character varying(255) NOT NULL,
    private_note text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    expense_group_id integer NOT NULL,
    paid_on_qbo boolean NOT NULL,
    payment_synced boolean NOT NULL
);


ALTER TABLE public.bills OWNER TO postgres;

--
-- Name: category_mappings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.category_mappings (
    id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    destination_account_id integer,
    destination_expense_head_id integer,
    source_category_id integer NOT NULL,
    workspace_id integer NOT NULL
);


ALTER TABLE public.category_mappings OWNER TO postgres;

--
-- Name: category_mappings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.category_mappings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.category_mappings_id_seq OWNER TO postgres;

--
-- Name: category_mappings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.category_mappings_id_seq OWNED BY public.category_mappings.id;


--
-- Name: cheque_lineitems; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cheque_lineitems (
    id integer NOT NULL,
    account_id character varying(255) NOT NULL,
    class_id character varying(255),
    customer_id character varying(255),
    amount double precision NOT NULL,
    description text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    cheque_id integer NOT NULL,
    expense_id integer NOT NULL,
    billable boolean,
    tax_amount double precision,
    tax_code character varying(255)
);


ALTER TABLE public.cheque_lineitems OWNER TO postgres;

--
-- Name: cheques; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cheques (
    id integer NOT NULL,
    bank_account_id character varying(255) NOT NULL,
    entity_id character varying(255) NOT NULL,
    department_id character varying(255),
    transaction_date date NOT NULL,
    currency character varying(255) NOT NULL,
    private_note text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    expense_group_id integer NOT NULL
);


ALTER TABLE public.cheques OWNER TO postgres;

--
-- Name: credit_card_purchase_lineitems; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.credit_card_purchase_lineitems (
    id integer NOT NULL,
    account_id character varying(255) NOT NULL,
    class_id character varying(255),
    customer_id character varying(255),
    amount double precision NOT NULL,
    description text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    credit_card_purchase_id integer NOT NULL,
    expense_id integer NOT NULL,
    billable boolean,
    tax_amount double precision,
    tax_code character varying(255)
);


ALTER TABLE public.credit_card_purchase_lineitems OWNER TO postgres;

--
-- Name: credit_card_purchases; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.credit_card_purchases (
    id integer NOT NULL,
    ccc_account_id character varying(255) NOT NULL,
    entity_id character varying(255) NOT NULL,
    department_id character varying(255),
    transaction_date date NOT NULL,
    currency character varying(255) NOT NULL,
    private_note text NOT NULL,
    credit_card_purchase_number character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    expense_group_id integer NOT NULL
);


ALTER TABLE public.credit_card_purchases OWNER TO postgres;

--
-- Name: destination_attributes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.destination_attributes (
    id integer NOT NULL,
    attribute_type character varying(255) NOT NULL,
    display_name character varying(255) NOT NULL,
    value character varying(255) NOT NULL,
    destination_id character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    active boolean,
    detail jsonb,
    auto_created boolean NOT NULL
);


ALTER TABLE public.destination_attributes OWNER TO postgres;

--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_admin_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_content_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_migrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;


--
-- Name: django_q_ormq; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_q_ormq (
    id integer NOT NULL,
    key character varying(100) NOT NULL,
    payload text NOT NULL,
    lock timestamp with time zone
);


ALTER TABLE public.django_q_ormq OWNER TO postgres;

--
-- Name: django_q_ormq_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_q_ormq_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_q_ormq_id_seq OWNER TO postgres;

--
-- Name: django_q_ormq_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_q_ormq_id_seq OWNED BY public.django_q_ormq.id;


--
-- Name: django_q_schedule; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_q_schedule (
    id integer NOT NULL,
    func character varying(256) NOT NULL,
    hook character varying(256),
    args text,
    kwargs text,
    schedule_type character varying(1) NOT NULL,
    repeats integer NOT NULL,
    next_run timestamp with time zone,
    task character varying(100),
    name character varying(100),
    minutes smallint,
    cron character varying(100),
    CONSTRAINT django_q_schedule_minutes_check CHECK ((minutes >= 0))
);


ALTER TABLE public.django_q_schedule OWNER TO postgres;

--
-- Name: django_q_schedule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_q_schedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_q_schedule_id_seq OWNER TO postgres;

--
-- Name: django_q_schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_q_schedule_id_seq OWNED BY public.django_q_schedule.id;


--
-- Name: django_q_task; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_q_task (
    name character varying(100) NOT NULL,
    func character varying(256) NOT NULL,
    hook character varying(256),
    args text,
    kwargs text,
    result text,
    started timestamp with time zone NOT NULL,
    stopped timestamp with time zone NOT NULL,
    success boolean NOT NULL,
    id character varying(32) NOT NULL,
    "group" character varying(100),
    attempt_count integer NOT NULL
);


ALTER TABLE public.django_q_task OWNER TO postgres;

--
-- Name: django_session; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO postgres;

--
-- Name: employee_mappings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employee_mappings (
    id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    destination_card_account_id integer,
    destination_employee_id integer,
    destination_vendor_id integer,
    source_employee_id integer NOT NULL,
    workspace_id integer NOT NULL
);


ALTER TABLE public.employee_mappings OWNER TO postgres;

--
-- Name: employee_mappings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employee_mappings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.employee_mappings_id_seq OWNER TO postgres;

--
-- Name: employee_mappings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employee_mappings_id_seq OWNED BY public.employee_mappings.id;


--
-- Name: expense_attributes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expense_attributes (
    id integer NOT NULL,
    attribute_type character varying(255) NOT NULL,
    display_name character varying(255) NOT NULL,
    value character varying(255) NOT NULL,
    source_id character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    active boolean,
    detail jsonb,
    auto_mapped boolean NOT NULL,
    auto_created boolean NOT NULL
);


ALTER TABLE public.expense_attributes OWNER TO postgres;

--
-- Name: expense_group_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expense_group_settings (
    id integer NOT NULL,
    reimbursable_expense_group_fields character varying(100)[] NOT NULL,
    corporate_credit_card_expense_group_fields character varying(100)[] NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    reimbursable_export_date_type character varying(100) NOT NULL,
    expense_state character varying(100) NOT NULL,
    import_card_credits boolean NOT NULL,
    ccc_export_date_type character varying(100) NOT NULL
);


ALTER TABLE public.expense_group_settings OWNER TO postgres;

--
-- Name: expense_groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expense_groups (
    id integer NOT NULL,
    description jsonb,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    fund_source character varying(255) NOT NULL,
    exported_at timestamp with time zone,
    response_logs jsonb
);


ALTER TABLE public.expense_groups OWNER TO postgres;

--
-- Name: expense_groups_expenses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expense_groups_expenses (
    id integer NOT NULL,
    expensegroup_id integer NOT NULL,
    expense_id integer NOT NULL
);


ALTER TABLE public.expense_groups_expenses OWNER TO postgres;

--
-- Name: expenses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expenses (
    id integer NOT NULL,
    employee_email character varying(255) NOT NULL,
    category character varying(255),
    sub_category character varying(255),
    project character varying(255),
    expense_id character varying(255) NOT NULL,
    expense_number character varying(255) NOT NULL,
    claim_number character varying(255),
    amount double precision NOT NULL,
    currency character varying(5) NOT NULL,
    foreign_amount double precision,
    foreign_currency character varying(15),
    settlement_id character varying(255),
    reimbursable boolean NOT NULL,
    exported boolean NOT NULL,
    state character varying(255) NOT NULL,
    vendor character varying(255),
    cost_center character varying(255),
    purpose text,
    report_id character varying(255) NOT NULL,
    spent_at timestamp with time zone,
    approved_at timestamp with time zone,
    expense_created_at timestamp with time zone NOT NULL,
    expense_updated_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    fund_source character varying(255) NOT NULL,
    custom_properties jsonb,
    verified_at timestamp with time zone,
    billable boolean,
    paid_on_qbo boolean NOT NULL,
    org_id character varying(255),
    tax_amount double precision,
    tax_group_id character varying(255),
    file_ids character varying(255)[],
    corporate_card_id character varying(255)
);


ALTER TABLE public.expenses OWNER TO postgres;

--
-- Name: fyle_accounting_mappings_destinationattribute_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fyle_accounting_mappings_destinationattribute_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fyle_accounting_mappings_destinationattribute_id_seq OWNER TO postgres;

--
-- Name: fyle_accounting_mappings_destinationattribute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fyle_accounting_mappings_destinationattribute_id_seq OWNED BY public.destination_attributes.id;


--
-- Name: fyle_accounting_mappings_expenseattribute_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fyle_accounting_mappings_expenseattribute_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fyle_accounting_mappings_expenseattribute_id_seq OWNER TO postgres;

--
-- Name: fyle_accounting_mappings_expenseattribute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fyle_accounting_mappings_expenseattribute_id_seq OWNED BY public.expense_attributes.id;


--
-- Name: mappings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mappings (
    id integer NOT NULL,
    source_type character varying(255) NOT NULL,
    destination_type character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    destination_id integer NOT NULL,
    source_id integer NOT NULL,
    workspace_id integer NOT NULL
);


ALTER TABLE public.mappings OWNER TO postgres;

--
-- Name: fyle_accounting_mappings_mapping_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fyle_accounting_mappings_mapping_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fyle_accounting_mappings_mapping_id_seq OWNER TO postgres;

--
-- Name: fyle_accounting_mappings_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fyle_accounting_mappings_mapping_id_seq OWNED BY public.mappings.id;


--
-- Name: mapping_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mapping_settings (
    id integer NOT NULL,
    source_field character varying(255) NOT NULL,
    destination_field character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    import_to_fyle boolean NOT NULL,
    is_custom boolean NOT NULL
);


ALTER TABLE public.mapping_settings OWNER TO postgres;

--
-- Name: fyle_accounting_mappings_mappingsetting_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fyle_accounting_mappings_mappingsetting_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fyle_accounting_mappings_mappingsetting_id_seq OWNER TO postgres;

--
-- Name: fyle_accounting_mappings_mappingsetting_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fyle_accounting_mappings_mappingsetting_id_seq OWNED BY public.mapping_settings.id;


--
-- Name: fyle_credentials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fyle_credentials (
    id integer NOT NULL,
    refresh_token text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    cluster_domain character varying(255)
);


ALTER TABLE public.fyle_credentials OWNER TO postgres;

--
-- Name: fyle_expense_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fyle_expense_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fyle_expense_id_seq OWNER TO postgres;

--
-- Name: fyle_expense_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fyle_expense_id_seq OWNED BY public.expenses.id;


--
-- Name: fyle_expensegroup_expenses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fyle_expensegroup_expenses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fyle_expensegroup_expenses_id_seq OWNER TO postgres;

--
-- Name: fyle_expensegroup_expenses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fyle_expensegroup_expenses_id_seq OWNED BY public.expense_groups_expenses.id;


--
-- Name: fyle_expensegroup_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fyle_expensegroup_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fyle_expensegroup_id_seq OWNER TO postgres;

--
-- Name: fyle_expensegroup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fyle_expensegroup_id_seq OWNED BY public.expense_groups.id;


--
-- Name: fyle_expensegroupsettings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fyle_expensegroupsettings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fyle_expensegroupsettings_id_seq OWNER TO postgres;

--
-- Name: fyle_expensegroupsettings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fyle_expensegroupsettings_id_seq OWNED BY public.expense_group_settings.id;


--
-- Name: fyle_rest_auth_authtokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fyle_rest_auth_authtokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fyle_rest_auth_authtokens_id_seq OWNER TO postgres;

--
-- Name: fyle_rest_auth_authtokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fyle_rest_auth_authtokens_id_seq OWNED BY public.auth_tokens.id;


--
-- Name: general_mappings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.general_mappings (
    id integer NOT NULL,
    bank_account_name character varying(255),
    bank_account_id character varying(40),
    default_ccc_account_name character varying(255),
    default_ccc_account_id character varying(40),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    accounts_payable_id character varying(40),
    accounts_payable_name character varying(255),
    default_ccc_vendor_id character varying(255),
    default_ccc_vendor_name character varying(255),
    bill_payment_account_id character varying(255),
    bill_payment_account_name character varying(255),
    qbo_expense_account_id character varying(40),
    qbo_expense_account_name character varying(255),
    default_tax_code_id character varying(255),
    default_tax_code_name character varying(255),
    default_debit_card_account_id character varying(40),
    default_debit_card_account_name character varying(255)
);


ALTER TABLE public.general_mappings OWNER TO postgres;

--
-- Name: journal_entries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.journal_entries (
    id integer NOT NULL,
    transaction_date date NOT NULL,
    currency character varying(255) NOT NULL,
    private_note text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    expense_group_id integer NOT NULL
);


ALTER TABLE public.journal_entries OWNER TO postgres;

--
-- Name: journal_entry_lineitems; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.journal_entry_lineitems (
    id integer NOT NULL,
    debit_account_id character varying(255) NOT NULL,
    account_id character varying(255) NOT NULL,
    class_id character varying(255),
    entity_id character varying(255) NOT NULL,
    entity_type character varying(255) NOT NULL,
    customer_id character varying(255),
    department_id character varying(255),
    posting_type character varying(255),
    amount double precision NOT NULL,
    description text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    expense_id integer NOT NULL,
    journal_entry_id integer NOT NULL,
    tax_amount double precision,
    tax_code character varying(255)
);


ALTER TABLE public.journal_entry_lineitems OWNER TO postgres;

--
-- Name: mappings_generalmapping_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mappings_generalmapping_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mappings_generalmapping_id_seq OWNER TO postgres;

--
-- Name: mappings_generalmapping_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mappings_generalmapping_id_seq OWNED BY public.general_mappings.id;


--
-- Name: qbo_credentials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.qbo_credentials (
    id integer NOT NULL,
    refresh_token text NOT NULL,
    realm_id character varying(40) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    company_name character varying(255),
    country character varying(255)
);


ALTER TABLE public.qbo_credentials OWNER TO postgres;

--
-- Name: qbo_expense_lineitems; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.qbo_expense_lineitems (
    id integer NOT NULL,
    account_id character varying(255) NOT NULL,
    class_id character varying(255),
    customer_id character varying(255),
    amount double precision NOT NULL,
    billable boolean,
    description text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    expense_id integer NOT NULL,
    qbo_expense_id integer NOT NULL,
    tax_amount double precision,
    tax_code character varying(255)
);


ALTER TABLE public.qbo_expense_lineitems OWNER TO postgres;

--
-- Name: qbo_expense_lineitems_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.qbo_expense_lineitems_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.qbo_expense_lineitems_id_seq OWNER TO postgres;

--
-- Name: qbo_expense_lineitems_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.qbo_expense_lineitems_id_seq OWNED BY public.qbo_expense_lineitems.id;


--
-- Name: qbo_expenses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.qbo_expenses (
    id integer NOT NULL,
    expense_account_id character varying(255) NOT NULL,
    entity_id character varying(255) NOT NULL,
    department_id character varying(255),
    transaction_date date NOT NULL,
    currency character varying(255) NOT NULL,
    private_note text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    expense_group_id integer NOT NULL
);


ALTER TABLE public.qbo_expenses OWNER TO postgres;

--
-- Name: qbo_expenses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.qbo_expenses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.qbo_expenses_id_seq OWNER TO postgres;

--
-- Name: qbo_expenses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.qbo_expenses_id_seq OWNED BY public.qbo_expenses.id;


--
-- Name: quickbooks_online_bill_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quickbooks_online_bill_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quickbooks_online_bill_id_seq OWNER TO postgres;

--
-- Name: quickbooks_online_bill_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quickbooks_online_bill_id_seq OWNED BY public.bills.id;


--
-- Name: quickbooks_online_billlineitem_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quickbooks_online_billlineitem_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quickbooks_online_billlineitem_id_seq OWNER TO postgres;

--
-- Name: quickbooks_online_billlineitem_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quickbooks_online_billlineitem_id_seq OWNED BY public.bill_lineitems.id;


--
-- Name: quickbooks_online_cheque_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quickbooks_online_cheque_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quickbooks_online_cheque_id_seq OWNER TO postgres;

--
-- Name: quickbooks_online_cheque_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quickbooks_online_cheque_id_seq OWNED BY public.cheques.id;


--
-- Name: quickbooks_online_chequelineitem_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quickbooks_online_chequelineitem_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quickbooks_online_chequelineitem_id_seq OWNER TO postgres;

--
-- Name: quickbooks_online_chequelineitem_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quickbooks_online_chequelineitem_id_seq OWNED BY public.cheque_lineitems.id;


--
-- Name: quickbooks_online_creditcardpurchase_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quickbooks_online_creditcardpurchase_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quickbooks_online_creditcardpurchase_id_seq OWNER TO postgres;

--
-- Name: quickbooks_online_creditcardpurchase_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quickbooks_online_creditcardpurchase_id_seq OWNED BY public.credit_card_purchases.id;


--
-- Name: quickbooks_online_creditcardpurchaselineitem_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quickbooks_online_creditcardpurchaselineitem_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quickbooks_online_creditcardpurchaselineitem_id_seq OWNER TO postgres;

--
-- Name: quickbooks_online_creditcardpurchaselineitem_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quickbooks_online_creditcardpurchaselineitem_id_seq OWNED BY public.credit_card_purchase_lineitems.id;


--
-- Name: quickbooks_online_journalentry_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quickbooks_online_journalentry_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quickbooks_online_journalentry_id_seq OWNER TO postgres;

--
-- Name: quickbooks_online_journalentry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quickbooks_online_journalentry_id_seq OWNED BY public.journal_entries.id;


--
-- Name: quickbooks_online_journalentrylineitem_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quickbooks_online_journalentrylineitem_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quickbooks_online_journalentrylineitem_id_seq OWNER TO postgres;

--
-- Name: quickbooks_online_journalentrylineitem_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quickbooks_online_journalentrylineitem_id_seq OWNED BY public.journal_entry_lineitems.id;


--
-- Name: reimbursements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reimbursements (
    id integer NOT NULL,
    settlement_id character varying(255) NOT NULL,
    reimbursement_id character varying(255) NOT NULL,
    state character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL
);


ALTER TABLE public.reimbursements OWNER TO postgres;

--
-- Name: reimbursements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reimbursements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reimbursements_id_seq OWNER TO postgres;

--
-- Name: reimbursements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reimbursements_id_seq OWNED BY public.reimbursements.id;


--
-- Name: task_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task_logs (
    id integer NOT NULL,
    type character varying(50) NOT NULL,
    task_id character varying(255),
    status character varying(255) NOT NULL,
    detail jsonb,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    bill_id integer,
    expense_group_id integer,
    workspace_id integer NOT NULL,
    cheque_id integer,
    credit_card_purchase_id integer,
    journal_entry_id integer,
    bill_payment_id integer,
    qbo_expense_id integer,
    quickbooks_errors jsonb
);


ALTER TABLE public.task_logs OWNER TO postgres;

--
-- Name: tasks_tasklog_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tasks_tasklog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tasks_tasklog_id_seq OWNER TO postgres;

--
-- Name: tasks_tasklog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tasks_tasklog_id_seq OWNED BY public.task_logs.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    user_id character varying(255) NOT NULL,
    full_name character varying(255) NOT NULL,
    active boolean NOT NULL,
    staff boolean NOT NULL,
    admin boolean NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.id;


--
-- Name: workspace_general_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workspace_general_settings (
    id integer NOT NULL,
    reimbursable_expenses_object character varying(50) NOT NULL,
    corporate_credit_card_expenses_object character varying(50),
    employee_field_mapping character varying(50) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    import_projects boolean NOT NULL,
    import_categories boolean NOT NULL,
    sync_fyle_to_qbo_payments boolean NOT NULL,
    sync_qbo_to_fyle_payments boolean NOT NULL,
    auto_map_employees character varying(50),
    category_sync_version character varying(50) NOT NULL,
    auto_create_destination_entity boolean NOT NULL,
    map_merchant_to_vendor boolean NOT NULL,
    je_single_credit_line boolean NOT NULL,
    change_accounting_period boolean NOT NULL,
    import_tax_codes boolean,
    charts_of_accounts character varying(100)[] NOT NULL,
    memo_structure character varying(100)[] NOT NULL,
    map_fyle_cards_qbo_account boolean NOT NULL,
    skip_cards_mapping boolean NOT NULL
);


ALTER TABLE public.workspace_general_settings OWNER TO postgres;

--
-- Name: workspace_schedules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workspace_schedules (
    id integer NOT NULL,
    enabled boolean NOT NULL,
    start_datetime timestamp with time zone,
    interval_hours integer,
    schedule_id integer,
    workspace_id integer NOT NULL
);


ALTER TABLE public.workspace_schedules OWNER TO postgres;

--
-- Name: workspaces; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workspaces (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    fyle_org_id character varying(255) NOT NULL,
    qbo_realm_id character varying(255) NOT NULL,
    last_synced_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    destination_synced_at timestamp with time zone,
    source_synced_at timestamp with time zone,
    cluster_domain character varying(255)
);


ALTER TABLE public.workspaces OWNER TO postgres;

--
-- Name: workspaces_fylecredential_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workspaces_fylecredential_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workspaces_fylecredential_id_seq OWNER TO postgres;

--
-- Name: workspaces_fylecredential_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workspaces_fylecredential_id_seq OWNED BY public.fyle_credentials.id;


--
-- Name: workspaces_qbocredential_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workspaces_qbocredential_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workspaces_qbocredential_id_seq OWNER TO postgres;

--
-- Name: workspaces_qbocredential_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workspaces_qbocredential_id_seq OWNED BY public.qbo_credentials.id;


--
-- Name: workspaces_user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workspaces_user (
    id integer NOT NULL,
    workspace_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.workspaces_user OWNER TO postgres;

--
-- Name: workspaces_workspace_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workspaces_workspace_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workspaces_workspace_id_seq OWNER TO postgres;

--
-- Name: workspaces_workspace_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workspaces_workspace_id_seq OWNED BY public.workspaces.id;


--
-- Name: workspaces_workspace_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workspaces_workspace_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workspaces_workspace_user_id_seq OWNER TO postgres;

--
-- Name: workspaces_workspace_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workspaces_workspace_user_id_seq OWNED BY public.workspaces_user.id;


--
-- Name: workspaces_workspacegeneralsettings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workspaces_workspacegeneralsettings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workspaces_workspacegeneralsettings_id_seq OWNER TO postgres;

--
-- Name: workspaces_workspacegeneralsettings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workspaces_workspacegeneralsettings_id_seq OWNED BY public.workspace_general_settings.id;


--
-- Name: workspaces_workspaceschedule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workspaces_workspaceschedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workspaces_workspaceschedule_id_seq OWNER TO postgres;

--
-- Name: workspaces_workspaceschedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workspaces_workspaceschedule_id_seq OWNED BY public.workspace_schedules.id;


--
-- Name: auth_group id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group ALTER COLUMN id SET DEFAULT nextval('public.auth_group_id_seq'::regclass);


--
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_group_permissions_id_seq'::regclass);


--
-- Name: auth_permission id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission ALTER COLUMN id SET DEFAULT nextval('public.auth_permission_id_seq'::regclass);


--
-- Name: auth_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_tokens ALTER COLUMN id SET DEFAULT nextval('public.fyle_rest_auth_authtokens_id_seq'::regclass);


--
-- Name: bill_lineitems id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_lineitems ALTER COLUMN id SET DEFAULT nextval('public.quickbooks_online_billlineitem_id_seq'::regclass);


--
-- Name: bill_payment_lineitems id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_payment_lineitems ALTER COLUMN id SET DEFAULT nextval('public.bill_payment_lineitems_id_seq'::regclass);


--
-- Name: bill_payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_payments ALTER COLUMN id SET DEFAULT nextval('public.bill_payments_id_seq'::regclass);


--
-- Name: bills id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bills ALTER COLUMN id SET DEFAULT nextval('public.quickbooks_online_bill_id_seq'::regclass);


--
-- Name: category_mappings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.category_mappings ALTER COLUMN id SET DEFAULT nextval('public.category_mappings_id_seq'::regclass);


--
-- Name: cheque_lineitems id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cheque_lineitems ALTER COLUMN id SET DEFAULT nextval('public.quickbooks_online_chequelineitem_id_seq'::regclass);


--
-- Name: cheques id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cheques ALTER COLUMN id SET DEFAULT nextval('public.quickbooks_online_cheque_id_seq'::regclass);


--
-- Name: credit_card_purchase_lineitems id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credit_card_purchase_lineitems ALTER COLUMN id SET DEFAULT nextval('public.quickbooks_online_creditcardpurchaselineitem_id_seq'::regclass);


--
-- Name: credit_card_purchases id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credit_card_purchases ALTER COLUMN id SET DEFAULT nextval('public.quickbooks_online_creditcardpurchase_id_seq'::regclass);


--
-- Name: destination_attributes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.destination_attributes ALTER COLUMN id SET DEFAULT nextval('public.fyle_accounting_mappings_destinationattribute_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);


--
-- Name: django_q_ormq id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_q_ormq ALTER COLUMN id SET DEFAULT nextval('public.django_q_ormq_id_seq'::regclass);


--
-- Name: django_q_schedule id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_q_schedule ALTER COLUMN id SET DEFAULT nextval('public.django_q_schedule_id_seq'::regclass);


--
-- Name: employee_mappings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_mappings ALTER COLUMN id SET DEFAULT nextval('public.employee_mappings_id_seq'::regclass);


--
-- Name: expense_attributes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_attributes ALTER COLUMN id SET DEFAULT nextval('public.fyle_accounting_mappings_expenseattribute_id_seq'::regclass);


--
-- Name: expense_group_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_group_settings ALTER COLUMN id SET DEFAULT nextval('public.fyle_expensegroupsettings_id_seq'::regclass);


--
-- Name: expense_groups id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_groups ALTER COLUMN id SET DEFAULT nextval('public.fyle_expensegroup_id_seq'::regclass);


--
-- Name: expense_groups_expenses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_groups_expenses ALTER COLUMN id SET DEFAULT nextval('public.fyle_expensegroup_expenses_id_seq'::regclass);


--
-- Name: expenses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses ALTER COLUMN id SET DEFAULT nextval('public.fyle_expense_id_seq'::regclass);


--
-- Name: fyle_credentials id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fyle_credentials ALTER COLUMN id SET DEFAULT nextval('public.workspaces_fylecredential_id_seq'::regclass);


--
-- Name: general_mappings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.general_mappings ALTER COLUMN id SET DEFAULT nextval('public.mappings_generalmapping_id_seq'::regclass);


--
-- Name: journal_entries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.journal_entries ALTER COLUMN id SET DEFAULT nextval('public.quickbooks_online_journalentry_id_seq'::regclass);


--
-- Name: journal_entry_lineitems id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.journal_entry_lineitems ALTER COLUMN id SET DEFAULT nextval('public.quickbooks_online_journalentrylineitem_id_seq'::regclass);


--
-- Name: mapping_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapping_settings ALTER COLUMN id SET DEFAULT nextval('public.fyle_accounting_mappings_mappingsetting_id_seq'::regclass);


--
-- Name: mappings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mappings ALTER COLUMN id SET DEFAULT nextval('public.fyle_accounting_mappings_mapping_id_seq'::regclass);


--
-- Name: qbo_credentials id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qbo_credentials ALTER COLUMN id SET DEFAULT nextval('public.workspaces_qbocredential_id_seq'::regclass);


--
-- Name: qbo_expense_lineitems id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qbo_expense_lineitems ALTER COLUMN id SET DEFAULT nextval('public.qbo_expense_lineitems_id_seq'::regclass);


--
-- Name: qbo_expenses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qbo_expenses ALTER COLUMN id SET DEFAULT nextval('public.qbo_expenses_id_seq'::regclass);


--
-- Name: reimbursements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reimbursements ALTER COLUMN id SET DEFAULT nextval('public.reimbursements_id_seq'::regclass);


--
-- Name: task_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs ALTER COLUMN id SET DEFAULT nextval('public.tasks_tasklog_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Name: workspace_general_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_general_settings ALTER COLUMN id SET DEFAULT nextval('public.workspaces_workspacegeneralsettings_id_seq'::regclass);


--
-- Name: workspace_schedules id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_schedules ALTER COLUMN id SET DEFAULT nextval('public.workspaces_workspaceschedule_id_seq'::regclass);


--
-- Name: workspaces id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces ALTER COLUMN id SET DEFAULT nextval('public.workspaces_workspace_id_seq'::regclass);


--
-- Name: workspaces_user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces_user ALTER COLUMN id SET DEFAULT nextval('public.workspaces_workspace_user_id_seq'::regclass);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add auth token	6	add_authtoken
22	Can change auth token	6	change_authtoken
23	Can delete auth token	6	delete_authtoken
24	Can view auth token	6	view_authtoken
25	Can add destination attribute	7	add_destinationattribute
26	Can change destination attribute	7	change_destinationattribute
27	Can delete destination attribute	7	delete_destinationattribute
28	Can view destination attribute	7	view_destinationattribute
29	Can add expense attribute	8	add_expenseattribute
30	Can change expense attribute	8	change_expenseattribute
31	Can delete expense attribute	8	delete_expenseattribute
32	Can view expense attribute	8	view_expenseattribute
33	Can add mapping setting	9	add_mappingsetting
34	Can change mapping setting	9	change_mappingsetting
35	Can delete mapping setting	9	delete_mappingsetting
36	Can view mapping setting	9	view_mappingsetting
37	Can add mapping	10	add_mapping
38	Can change mapping	10	change_mapping
39	Can delete mapping	10	delete_mapping
40	Can view mapping	10	view_mapping
41	Can add employee mapping	11	add_employeemapping
42	Can change employee mapping	11	change_employeemapping
43	Can delete employee mapping	11	delete_employeemapping
44	Can view employee mapping	11	view_employeemapping
45	Can add category mapping	12	add_categorymapping
46	Can change category mapping	12	change_categorymapping
47	Can delete category mapping	12	delete_categorymapping
48	Can view category mapping	12	view_categorymapping
49	Can add Scheduled task	13	add_schedule
50	Can change Scheduled task	13	change_schedule
51	Can delete Scheduled task	13	delete_schedule
52	Can view Scheduled task	13	view_schedule
53	Can add task	14	add_task
54	Can change task	14	change_task
55	Can delete task	14	delete_task
56	Can view task	14	view_task
57	Can add Failed task	15	add_failure
58	Can change Failed task	15	change_failure
59	Can delete Failed task	15	delete_failure
60	Can view Failed task	15	view_failure
61	Can add Successful task	16	add_success
62	Can change Successful task	16	change_success
63	Can delete Successful task	16	delete_success
64	Can view Successful task	16	view_success
65	Can add Queued task	17	add_ormq
66	Can change Queued task	17	change_ormq
67	Can delete Queued task	17	delete_ormq
68	Can view Queued task	17	view_ormq
69	Can add user	18	add_user
70	Can change user	18	change_user
71	Can delete user	18	delete_user
72	Can view user	18	view_user
73	Can add workspace	19	add_workspace
74	Can change workspace	19	change_workspace
75	Can delete workspace	19	delete_workspace
76	Can view workspace	19	view_workspace
77	Can add workspace schedule	20	add_workspaceschedule
78	Can change workspace schedule	20	change_workspaceschedule
79	Can delete workspace schedule	20	delete_workspaceschedule
80	Can view workspace schedule	20	view_workspaceschedule
81	Can add qbo credential	21	add_qbocredential
82	Can change qbo credential	21	change_qbocredential
83	Can delete qbo credential	21	delete_qbocredential
84	Can view qbo credential	21	view_qbocredential
85	Can add fyle credential	22	add_fylecredential
86	Can change fyle credential	22	change_fylecredential
87	Can delete fyle credential	22	delete_fylecredential
88	Can view fyle credential	22	view_fylecredential
89	Can add workspace general settings	23	add_workspacegeneralsettings
90	Can change workspace general settings	23	change_workspacegeneralsettings
91	Can delete workspace general settings	23	delete_workspacegeneralsettings
92	Can view workspace general settings	23	view_workspacegeneralsettings
93	Can add general mapping	24	add_generalmapping
94	Can change general mapping	24	change_generalmapping
95	Can delete general mapping	24	delete_generalmapping
96	Can view general mapping	24	view_generalmapping
97	Can add expense	25	add_expense
98	Can change expense	25	change_expense
99	Can delete expense	25	delete_expense
100	Can view expense	25	view_expense
101	Can add expense group	26	add_expensegroup
102	Can change expense group	26	change_expensegroup
103	Can delete expense group	26	delete_expensegroup
104	Can view expense group	26	view_expensegroup
105	Can add expense group settings	27	add_expensegroupsettings
106	Can change expense group settings	27	change_expensegroupsettings
107	Can delete expense group settings	27	delete_expensegroupsettings
108	Can view expense group settings	27	view_expensegroupsettings
109	Can add reimbursement	28	add_reimbursement
110	Can change reimbursement	28	change_reimbursement
111	Can delete reimbursement	28	delete_reimbursement
112	Can view reimbursement	28	view_reimbursement
113	Can add bill	29	add_bill
114	Can change bill	29	change_bill
115	Can delete bill	29	delete_bill
116	Can view bill	29	view_bill
117	Can add bill lineitem	30	add_billlineitem
118	Can change bill lineitem	30	change_billlineitem
119	Can delete bill lineitem	30	delete_billlineitem
120	Can view bill lineitem	30	view_billlineitem
121	Can add cheque	31	add_cheque
122	Can change cheque	31	change_cheque
123	Can delete cheque	31	delete_cheque
124	Can view cheque	31	view_cheque
125	Can add credit card purchase	32	add_creditcardpurchase
126	Can change credit card purchase	32	change_creditcardpurchase
127	Can delete credit card purchase	32	delete_creditcardpurchase
128	Can view credit card purchase	32	view_creditcardpurchase
129	Can add journal entry	33	add_journalentry
130	Can change journal entry	33	change_journalentry
131	Can delete journal entry	33	delete_journalentry
132	Can view journal entry	33	view_journalentry
133	Can add journal entry lineitem	34	add_journalentrylineitem
134	Can change journal entry lineitem	34	change_journalentrylineitem
135	Can delete journal entry lineitem	34	delete_journalentrylineitem
136	Can view journal entry lineitem	34	view_journalentrylineitem
137	Can add credit card purchase lineitem	35	add_creditcardpurchaselineitem
138	Can change credit card purchase lineitem	35	change_creditcardpurchaselineitem
139	Can delete credit card purchase lineitem	35	delete_creditcardpurchaselineitem
140	Can view credit card purchase lineitem	35	view_creditcardpurchaselineitem
141	Can add cheque lineitem	36	add_chequelineitem
142	Can change cheque lineitem	36	change_chequelineitem
143	Can delete cheque lineitem	36	delete_chequelineitem
144	Can view cheque lineitem	36	view_chequelineitem
145	Can add bill payment	37	add_billpayment
146	Can change bill payment	37	change_billpayment
147	Can delete bill payment	37	delete_billpayment
148	Can view bill payment	37	view_billpayment
149	Can add bill payment lineitem	38	add_billpaymentlineitem
150	Can change bill payment lineitem	38	change_billpaymentlineitem
151	Can delete bill payment lineitem	38	delete_billpaymentlineitem
152	Can view bill payment lineitem	38	view_billpaymentlineitem
153	Can add qbo expense	39	add_qboexpense
154	Can change qbo expense	39	change_qboexpense
155	Can delete qbo expense	39	delete_qboexpense
156	Can view qbo expense	39	view_qboexpense
157	Can add qbo expense lineitem	40	add_qboexpenselineitem
158	Can change qbo expense lineitem	40	change_qboexpenselineitem
159	Can delete qbo expense lineitem	40	delete_qboexpenselineitem
160	Can view qbo expense lineitem	40	view_qboexpenselineitem
161	Can add task log	41	add_tasklog
162	Can change task log	41	change_tasklog
163	Can delete task log	41	delete_tasklog
164	Can view task log	41	view_tasklog
\.


--
-- Data for Name: auth_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_tokens (id, refresh_token, user_id) FROM stdin;
\.


--
-- Data for Name: bill_lineitems; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bill_lineitems (id, account_id, class_id, customer_id, amount, description, created_at, updated_at, bill_id, expense_id, billable, tax_amount, tax_code) FROM stdin;
3	57	\N	\N	120	ashwin.t@fyle.in - Travel - 2022-01-21 - C/2022/01/R/7 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txDmcqOv8LMD?org_id=orGcBCVPijjO	2022-01-21 10:45:32.576643+00	2022-01-21 10:45:32.576711+00	3	6	\N	\N	\N
\.


--
-- Data for Name: bill_payment_lineitems; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bill_payment_lineitems (id, amount, linked_transaction_id, created_at, updated_at, bill_payment_id) FROM stdin;
\.


--
-- Data for Name: bill_payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bill_payments (id, private_note, vendor_id, amount, currency, payment_account, accounts_payable_id, department_id, transaction_date, bill_payment_number, created_at, updated_at, expense_group_id) FROM stdin;
\.


--
-- Data for Name: bills; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bills (id, accounts_payable_id, vendor_id, department_id, transaction_date, currency, private_note, created_at, updated_at, expense_group_id, paid_on_qbo, payment_synced) FROM stdin;
3	33	43	\N	2022-01-21	USD	Reimbursable expense by ashwin.t@fyle.in on 2022-01-21 	2022-01-21 10:45:31.084958+00	2022-01-21 10:45:31.08515+00	6	f	f
\.


--
-- Data for Name: category_mappings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.category_mappings (id, created_at, updated_at, destination_account_id, destination_expense_head_id, source_category_id, workspace_id) FROM stdin;
\.


--
-- Data for Name: cheque_lineitems; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cheque_lineitems (id, account_id, class_id, customer_id, amount, description, created_at, updated_at, cheque_id, expense_id, billable, tax_amount, tax_code) FROM stdin;
\.


--
-- Data for Name: cheques; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cheques (id, bank_account_id, entity_id, department_id, transaction_date, currency, private_note, created_at, updated_at, expense_group_id) FROM stdin;
\.


--
-- Data for Name: credit_card_purchase_lineitems; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.credit_card_purchase_lineitems (id, account_id, class_id, customer_id, amount, description, created_at, updated_at, credit_card_purchase_id, expense_id, billable, tax_amount, tax_code) FROM stdin;
4	57	\N	\N	50	ashwin.t@fyle.in - Travel - 2022-01-21 - C/2022/01/R/7 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txJkZlJS4LrA?org_id=orGcBCVPijjO	2022-01-21 10:45:36.088907+00	2022-01-21 10:45:36.088967+00	4	7	\N	\N	\N
\.


--
-- Data for Name: credit_card_purchases; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.credit_card_purchases (id, ccc_account_id, entity_id, department_id, transaction_date, currency, private_note, credit_card_purchase_number, created_at, updated_at, expense_group_id) FROM stdin;
4	42	58	\N	2022-01-21	USD	Credit card expense by ashwin.t@fyle.in on 2022-01-21 	E/2022/01/T/8	2022-01-21 10:45:35.271272+00	2022-01-21 10:45:35.271352+00	7
\.


--
-- Data for Name: destination_attributes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.destination_attributes (id, attribute_type, display_name, value, destination_id, created_at, updated_at, workspace_id, active, detail, auto_created) FROM stdin;
1099	CREDIT_CARD_ACCOUNT	Credit Card Account	Mastercard	41	2022-01-21 10:37:02.930954+00	2022-01-21 10:37:02.931454+00	8	\N	{"account_type": "Credit Card", "fully_qualified_name": "Mastercard"}	f
1100	CREDIT_CARD_ACCOUNT	Credit Card Account	Visa	42	2022-01-21 10:37:02.931839+00	2022-01-21 10:37:02.931908+00	8	\N	{"account_type": "Credit Card", "fully_qualified_name": "Visa"}	f
1101	BANK_ACCOUNT	Bank Account	Checking	35	2022-01-21 10:37:03.103072+00	2022-01-21 10:37:03.10316+00	8	\N	{"account_type": "Bank", "fully_qualified_name": "Checking"}	f
1102	BANK_ACCOUNT	Bank Account	Gayathiri	128	2022-01-21 10:37:03.103349+00	2022-01-21 10:37:03.103417+00	8	\N	{"account_type": "Bank", "fully_qualified_name": "Gayathiri"}	f
1103	BANK_ACCOUNT	Bank Account	Savings	36	2022-01-21 10:37:03.103792+00	2022-01-21 10:37:03.10388+00	8	\N	{"account_type": "Bank", "fully_qualified_name": "Savings"}	f
1104	ACCOUNTS_PAYABLE	Accounts Payable	Accounts Payable (A/P)	33	2022-01-21 10:37:03.2173+00	2022-01-21 10:37:03.217363+00	8	\N	{"account_type": "Accounts Payable", "fully_qualified_name": "Accounts Payable (A/P)"}	f
1105	ACCOUNTS_PAYABLE	Accounts Payable	Accounts Payable (A/P) 2	91	2022-01-21 10:37:03.217479+00	2022-01-21 10:37:03.217521+00	8	\N	{"account_type": "Accounts Payable", "fully_qualified_name": "Accounts Payable (A/P) 2"}	f
1106	ACCOUNTS_PAYABLE	Accounts Payable	Accounts Receivable (A/R)	84	2022-01-21 10:37:03.217638+00	2022-01-21 10:37:03.217682+00	8	\N	{"account_type": "Accounts Receivable", "fully_qualified_name": "Accounts Receivable (A/R)"}	f
1107	ACCOUNTS_PAYABLE	Accounts Payable	Advertising	7	2022-01-21 10:37:03.21779+00	2022-01-21 10:37:03.217833+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Advertising"}	f
1108	ACCOUNTS_PAYABLE	Accounts Payable	Arizona Dept. of Revenue Payable	89	2022-01-21 10:37:03.217937+00	2022-01-21 10:37:03.217978+00	8	\N	{"account_type": "Other Current Liability", "fully_qualified_name": "Arizona Dept. of Revenue Payable"}	f
1109	ACCOUNTS_PAYABLE	Accounts Payable	Automobile	55	2022-01-21 10:37:03.218086+00	2022-01-21 10:37:03.218129+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Automobile"}	f
1110	ACCOUNTS_PAYABLE	Accounts Payable	Automobile:Fuel	56	2022-01-21 10:37:03.218234+00	2022-01-21 10:37:03.218276+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Automobile:Fuel"}	f
1111	ACCOUNTS_PAYABLE	Accounts Payable	Bank Charges	8	2022-01-21 10:37:03.218382+00	2022-01-21 10:37:03.218424+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Bank Charges"}	f
1112	ACCOUNTS_PAYABLE	Accounts Payable	Billable Expense Income	85	2022-01-21 10:37:03.218528+00	2022-01-21 10:37:03.218574+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Billable Expense Income"}	f
1113	ACCOUNTS_PAYABLE	Accounts Payable	Board of Equalization Payable	90	2022-01-21 10:37:03.218692+00	2022-01-21 10:37:03.218731+00	8	\N	{"account_type": "Other Current Liability", "fully_qualified_name": "Board of Equalization Payable"}	f
1114	ACCOUNTS_PAYABLE	Accounts Payable	Bus	108	2022-01-21 10:37:03.218856+00	2022-01-21 10:37:03.218903+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Bus"}	f
1115	ACCOUNTS_PAYABLE	Accounts Payable	Business Expense	127	2022-01-21 10:37:03.219226+00	2022-01-21 10:37:03.219281+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Business Expense"}	f
1116	ACCOUNTS_PAYABLE	Accounts Payable	California Department of Tax and Fee Administration Payable	125	2022-01-21 10:37:03.219714+00	2022-01-21 10:37:03.219756+00	8	\N	{"account_type": "Other Current Liability", "fully_qualified_name": "California Department of Tax and Fee Administration Payable"}	f
1117	ACCOUNTS_PAYABLE	Accounts Payable	Commissions & fees	9	2022-01-21 10:37:03.219938+00	2022-01-21 10:37:03.219986+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Commissions & fees"}	f
1118	ACCOUNTS_PAYABLE	Accounts Payable	Cost of Goods Sold	80	2022-01-21 10:37:03.220107+00	2022-01-21 10:37:03.220154+00	8	\N	{"account_type": "Cost of Goods Sold", "fully_qualified_name": "Cost of Goods Sold"}	f
1119	ACCOUNTS_PAYABLE	Accounts Payable	Courier	111	2022-01-21 10:37:03.220273+00	2022-01-21 10:37:03.220318+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Courier"}	f
1120	ACCOUNTS_PAYABLE	Accounts Payable	Depreciation	40	2022-01-21 10:37:03.220434+00	2022-01-21 10:37:03.220477+00	8	\N	{"account_type": "Other Expense", "fully_qualified_name": "Depreciation"}	f
1121	ACCOUNTS_PAYABLE	Accounts Payable	Design income	82	2022-01-21 10:37:03.220624+00	2022-01-21 10:37:03.220673+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Design income"}	f
1122	ACCOUNTS_PAYABLE	Accounts Payable	Discounts given	86	2022-01-21 10:37:03.220972+00	2022-01-21 10:37:03.221049+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Discounts given"}	f
1123	ACCOUNTS_PAYABLE	Accounts Payable	Disposal Fees	28	2022-01-21 10:37:03.221218+00	2022-01-21 10:37:03.22127+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Disposal Fees"}	f
1124	ACCOUNTS_PAYABLE	Accounts Payable	Dues & Subscriptions	10	2022-01-21 10:37:03.221404+00	2022-01-21 10:37:03.22145+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Dues & Subscriptions"}	f
1125	ACCOUNTS_PAYABLE	Accounts Payable	Employee Reimbursables	129	2022-01-21 10:37:03.221579+00	2022-01-21 10:37:03.221625+00	8	\N	{"account_type": "Accounts Payable", "fully_qualified_name": "Employee Reimbursables"}	f
1126	ACCOUNTS_PAYABLE	Accounts Payable	Entertainment	104	2022-01-21 10:37:03.221754+00	2022-01-21 10:37:03.221801+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Entertainment"}	f
1127	ACCOUNTS_PAYABLE	Accounts Payable	Equipment Rental	29	2022-01-21 10:37:03.221923+00	2022-01-21 10:37:03.22197+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Equipment Rental"}	f
1128	ACCOUNTS_PAYABLE	Accounts Payable	Fees Billed	5	2022-01-21 10:37:03.225484+00	2022-01-21 10:37:03.225579+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Fees Billed"}	f
1129	ACCOUNTS_PAYABLE	Accounts Payable	Flight	116	2022-01-21 10:37:03.225946+00	2022-01-21 10:37:03.226014+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Flight"}	f
1130	ACCOUNTS_PAYABLE	Accounts Payable	Food	106	2022-01-21 10:37:03.22624+00	2022-01-21 10:37:03.226417+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Food"}	f
1131	ACCOUNTS_PAYABLE	Accounts Payable	Fuel	101	2022-01-21 10:37:03.226843+00	2022-01-21 10:37:03.226886+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Fuel"}	f
1132	ACCOUNTS_PAYABLE	Accounts Payable	Hotel	112	2022-01-21 10:37:03.226976+00	2022-01-21 10:37:03.227007+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Hotel"}	f
1133	ACCOUNTS_PAYABLE	Accounts Payable	Incremental Account	92	2022-01-21 10:37:03.227076+00	2022-01-21 10:37:03.227106+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Incremental Account"}	f
1134	ACCOUNTS_PAYABLE	Accounts Payable	Insurance	11	2022-01-21 10:37:03.227174+00	2022-01-21 10:37:03.227203+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Insurance"}	f
1135	ACCOUNTS_PAYABLE	Accounts Payable	Insurance:Workers Compensation	57	2022-01-21 10:37:03.227272+00	2022-01-21 10:37:03.227301+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Insurance:Workers Compensation"}	f
1136	ACCOUNTS_PAYABLE	Accounts Payable	Interest Earned	25	2022-01-21 10:37:03.227368+00	2022-01-21 10:37:03.227397+00	8	\N	{"account_type": "Other Income", "fully_qualified_name": "Interest Earned"}	f
1137	ACCOUNTS_PAYABLE	Accounts Payable	Internet	109	2022-01-21 10:37:03.227464+00	2022-01-21 10:37:03.227494+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Internet"}	f
1138	ACCOUNTS_PAYABLE	Accounts Payable	Inventory Asset	81	2022-01-21 10:37:03.227561+00	2022-01-21 10:37:03.22759+00	8	\N	{"account_type": "Other Current Asset", "fully_qualified_name": "Inventory Asset"}	f
1272	VENDOR	vendor	Jonathan Elliott	91	2022-01-21 10:37:09.927211+00	2022-01-21 10:37:09.931803+00	8	\N	{"email": "user53@fyleforjatinorg.com"}	f
1139	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses	58	2022-01-21 10:37:03.227657+00	2022-01-21 10:37:03.227686+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses"}	f
1140	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Cost of Labor	59	2022-01-21 10:37:03.227754+00	2022-01-21 10:37:03.227783+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Cost of Labor"}	f
1141	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Cost of Labor:Installation	60	2022-01-21 10:37:03.241383+00	2022-01-21 10:37:03.241484+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Cost of Labor:Installation"}	f
1142	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Cost of Labor:Maintenance and Repairs	61	2022-01-21 10:37:03.242176+00	2022-01-21 10:37:03.242248+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Cost of Labor:Maintenance and Repairs"}	f
1143	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Equipment Rental	62	2022-01-21 10:37:03.242332+00	2022-01-21 10:37:03.242363+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Equipment Rental"}	f
1144	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Job Materials	63	2022-01-21 10:37:03.242434+00	2022-01-21 10:37:03.242465+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials"}	f
1145	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Job Materials:Decks and Patios	64	2022-01-21 10:37:03.242534+00	2022-01-21 10:37:03.242564+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials:Decks and Patios"}	f
1146	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Job Materials:Fountain and Garden Lighting	65	2022-01-21 10:37:03.242638+00	2022-01-21 10:37:03.242668+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials:Fountain and Garden Lighting"}	f
1147	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Job Materials:Plants and Soil	66	2022-01-21 10:37:03.242736+00	2022-01-21 10:37:03.242767+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials:Plants and Soil"}	f
1148	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Job Materials:Sprinklers and Drip Systems	67	2022-01-21 10:37:03.242835+00	2022-01-21 10:37:03.242865+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials:Sprinklers and Drip Systems"}	f
1149	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Permits	68	2022-01-21 10:37:03.242933+00	2022-01-21 10:37:03.242963+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Permits"}	f
1150	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services	45	2022-01-21 10:37:03.243031+00	2022-01-21 10:37:03.243061+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services"}	f
1151	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services:Job Materials	46	2022-01-21 10:37:03.243129+00	2022-01-21 10:37:03.243706+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services:Job Materials"}	f
1152	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services:Job Materials:Decks and Patios	47	2022-01-21 10:37:03.243875+00	2022-01-21 10:37:03.24391+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services:Job Materials:Decks and Patios"}	f
1153	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services:Job Materials:Fountains and Garden Lighting	48	2022-01-21 10:37:03.243992+00	2022-01-21 10:37:03.244023+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services:Job Materials:Fountains and Garden Lighting"}	f
1154	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services:Job Materials:Plants and Soil	49	2022-01-21 10:37:03.268901+00	2022-01-21 10:37:03.268945+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services:Job Materials:Plants and Soil"}	f
1155	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services:Job Materials:Sprinklers and Drip Systems	50	2022-01-21 10:37:03.269017+00	2022-01-21 10:37:03.269047+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services:Job Materials:Sprinklers and Drip Systems"}	f
1156	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services:Labor	51	2022-01-21 10:37:03.269116+00	2022-01-21 10:37:03.269146+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services:Labor"}	f
1157	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services:Labor:Installation	52	2022-01-21 10:37:03.269213+00	2022-01-21 10:37:03.269243+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services:Labor:Installation"}	f
1158	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services:Labor:Maintenance and Repair	53	2022-01-21 10:37:03.26931+00	2022-01-21 10:37:03.269716+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services:Labor:Maintenance and Repair"}	f
1159	ACCOUNTS_PAYABLE	Accounts Payable	Legal & Professional Fees	12	2022-01-21 10:37:03.270026+00	2022-01-21 10:37:03.270069+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Legal & Professional Fees"}	f
1160	ACCOUNTS_PAYABLE	Accounts Payable	Legal & Professional Fees:Accounting	69	2022-01-21 10:37:03.270161+00	2022-01-21 10:37:03.270194+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Legal & Professional Fees:Accounting"}	f
1161	ACCOUNTS_PAYABLE	Accounts Payable	Legal & Professional Fees:Bookkeeper	70	2022-01-21 10:37:03.270272+00	2022-01-21 10:37:03.270302+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Legal & Professional Fees:Bookkeeper"}	f
1162	ACCOUNTS_PAYABLE	Accounts Payable	Legal & Professional Fees:Lawyer	71	2022-01-21 10:37:03.270376+00	2022-01-21 10:37:03.270406+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Legal & Professional Fees:Lawyer"}	f
1163	ACCOUNTS_PAYABLE	Accounts Payable	Loan Payable	43	2022-01-21 10:37:03.27048+00	2022-01-21 10:37:03.27051+00	8	\N	{"account_type": "Other Current Liability", "fully_qualified_name": "Loan Payable"}	f
1164	ACCOUNTS_PAYABLE	Accounts Payable	Maintenance and Repair	72	2022-01-21 10:37:03.27058+00	2022-01-21 10:37:03.27354+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Maintenance and Repair"}	f
1165	ACCOUNTS_PAYABLE	Accounts Payable	Maintenance and Repair:Building Repairs	73	2022-01-21 10:37:03.278013+00	2022-01-21 10:37:03.278212+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Maintenance and Repair:Building Repairs"}	f
1166	ACCOUNTS_PAYABLE	Accounts Payable	Maintenance and Repair:Computer Repairs	74	2022-01-21 10:37:03.278401+00	2022-01-21 10:37:03.279046+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Maintenance and Repair:Computer Repairs"}	f
1167	ACCOUNTS_PAYABLE	Accounts Payable	Maintenance and Repair:Equipment Repairs	75	2022-01-21 10:37:03.279957+00	2022-01-21 10:37:03.280067+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Maintenance and Repair:Equipment Repairs"}	f
1168	ACCOUNTS_PAYABLE	Accounts Payable	Meals	13	2022-01-21 10:37:03.282577+00	2022-01-21 10:37:03.282655+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Meals"}	f
1169	ACCOUNTS_PAYABLE	Accounts Payable	Mileage	105	2022-01-21 10:37:03.282825+00	2022-01-21 10:37:03.282879+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Mileage"}	f
1170	ACCOUNTS_PAYABLE	Accounts Payable	Miscellaneous	14	2022-01-21 10:37:03.283221+00	2022-01-21 10:37:03.28326+00	8	\N	{"account_type": "Other Expense", "fully_qualified_name": "Miscellaneous"}	f
1171	ACCOUNTS_PAYABLE	Accounts Payable	Notes Payable	44	2022-01-21 10:37:03.283335+00	2022-01-21 10:37:03.283366+00	8	\N	{"account_type": "Long Term Liability", "fully_qualified_name": "Notes Payable"}	f
1172	ACCOUNTS_PAYABLE	Accounts Payable	Office Expenses	15	2022-01-21 10:37:03.283438+00	2022-01-21 10:37:03.283468+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Office Expenses"}	f
1173	ACCOUNTS_PAYABLE	Accounts Payable	Office Party	115	2022-01-21 10:37:03.283537+00	2022-01-21 10:37:03.283567+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Office Party"}	f
1174	ACCOUNTS_PAYABLE	Accounts Payable	OFFICE SUPPLIES	98	2022-01-21 10:37:03.283675+00	2022-01-21 10:37:03.283927+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "OFFICE SUPPLIES"}	f
1175	ACCOUNTS_PAYABLE	Accounts Payable	Office Supplies 2	124	2022-01-21 10:37:03.284136+00	2022-01-21 10:37:03.284172+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Office Supplies 2"}	f
1176	ACCOUNTS_PAYABLE	Accounts Payable	Office/General Administrative Expenses	97	2022-01-21 10:37:03.284258+00	2022-01-21 10:37:03.284283+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Office/General Administrative Expenses"}	f
1177	ACCOUNTS_PAYABLE	Accounts Payable	Opening Balance Equity	34	2022-01-21 10:37:03.284342+00	2022-01-21 10:37:03.284364+00	8	\N	{"account_type": "Equity", "fully_qualified_name": "Opening Balance Equity"}	f
1178	ACCOUNTS_PAYABLE	Accounts Payable	Other Income	83	2022-01-21 10:37:03.284438+00	2022-01-21 10:37:03.284469+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Other Income"}	f
1179	ACCOUNTS_PAYABLE	Accounts Payable	Other Portfolio Income	26	2022-01-21 10:37:03.284555+00	2022-01-21 10:37:03.284584+00	8	\N	{"account_type": "Other Income", "fully_qualified_name": "Other Portfolio Income"}	f
1180	ACCOUNTS_PAYABLE	Accounts Payable	Others	123	2022-01-21 10:37:03.284655+00	2022-01-21 10:37:03.284684+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Others"}	f
1181	ACCOUNTS_PAYABLE	Accounts Payable	Out Of Scope Agency Payable	126	2022-01-21 10:37:03.284753+00	2022-01-21 10:37:03.284783+00	8	\N	{"account_type": "Other Current Liability", "fully_qualified_name": "Out Of Scope Agency Payable"}	f
1182	ACCOUNTS_PAYABLE	Accounts Payable	Parking	118	2022-01-21 10:37:03.284851+00	2022-01-21 10:37:03.28488+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Parking"}	f
1183	ACCOUNTS_PAYABLE	Accounts Payable	Penalties & Settlements	27	2022-01-21 10:37:03.284948+00	2022-01-21 10:37:03.284977+00	8	\N	{"account_type": "Other Expense", "fully_qualified_name": "Penalties & Settlements"}	f
1184	ACCOUNTS_PAYABLE	Accounts Payable	Per Diem	107	2022-01-21 10:37:03.285045+00	2022-01-21 10:37:03.285074+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Per Diem"}	f
1185	ACCOUNTS_PAYABLE	Accounts Payable	Pest Control Services	54	2022-01-21 10:37:03.285142+00	2022-01-21 10:37:03.285171+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Pest Control Services"}	f
1186	ACCOUNTS_PAYABLE	Accounts Payable	Phone	114	2022-01-21 10:37:03.285238+00	2022-01-21 10:37:03.285267+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Phone"}	f
1187	ACCOUNTS_PAYABLE	Accounts Payable	Prepaid Expenses	3	2022-01-21 10:37:03.285335+00	2022-01-21 10:37:03.285365+00	8	\N	{"account_type": "Other Current Asset", "fully_qualified_name": "Prepaid Expenses"}	f
1188	ACCOUNTS_PAYABLE	Accounts Payable	Professional Services	113	2022-01-21 10:37:03.285432+00	2022-01-21 10:37:03.285461+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Professional Services"}	f
1189	ACCOUNTS_PAYABLE	Accounts Payable	Promotional	16	2022-01-21 10:37:03.285528+00	2022-01-21 10:37:03.285558+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Promotional"}	f
1190	ACCOUNTS_PAYABLE	Accounts Payable	Purchases	78	2022-01-21 10:37:03.285625+00	2022-01-21 10:37:03.285654+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Purchases"}	f
1191	ACCOUNTS_PAYABLE	Accounts Payable	Refunds-Allowances	6	2022-01-21 10:37:03.285722+00	2022-01-21 10:37:03.285751+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Refunds-Allowances"}	f
1192	ACCOUNTS_PAYABLE	Accounts Payable	Rent or Lease	17	2022-01-21 10:37:03.292209+00	2022-01-21 10:37:03.292291+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Rent or Lease"}	f
1193	ACCOUNTS_PAYABLE	Accounts Payable	Retained Earnings	2	2022-01-21 10:37:03.296415+00	2022-01-21 10:37:03.323922+00	8	\N	{"account_type": "Equity", "fully_qualified_name": "Retained Earnings"}	f
1194	ACCOUNTS_PAYABLE	Accounts Payable	Sales of Product Income	79	2022-01-21 10:37:03.334975+00	2022-01-21 10:37:03.335094+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Sales of Product Income"}	f
1195	ACCOUNTS_PAYABLE	Accounts Payable	Services	1	2022-01-21 10:37:03.33522+00	2022-01-21 10:37:03.335257+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Services"}	f
1196	ACCOUNTS_PAYABLE	Accounts Payable	Snacks	102	2022-01-21 10:37:03.335346+00	2022-01-21 10:37:03.335389+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Snacks"}	f
1197	ACCOUNTS_PAYABLE	Accounts Payable	Software	117	2022-01-21 10:37:03.335853+00	2022-01-21 10:37:03.335892+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Software"}	f
1198	ACCOUNTS_PAYABLE	Accounts Payable	Stationery & Printing	19	2022-01-21 10:37:03.335982+00	2022-01-21 10:37:03.336013+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Stationery & Printing"}	f
1199	ACCOUNTS_PAYABLE	Accounts Payable	Supplies Test 2	20	2022-01-21 10:37:03.336089+00	2022-01-21 10:37:03.336234+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Supplies Test 2"}	f
1200	ACCOUNTS_PAYABLE	Accounts Payable	Tax	120	2022-01-21 10:37:03.336402+00	2022-01-21 10:37:03.336453+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Tax"}	f
1201	ACCOUNTS_PAYABLE	Accounts Payable	Taxes & Licenses	21	2022-01-21 10:37:03.336592+00	2022-01-21 10:37:03.336974+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Taxes & Licenses"}	f
1202	ACCOUNTS_PAYABLE	Accounts Payable	Taxi	110	2022-01-21 10:37:03.352901+00	2022-01-21 10:37:03.353023+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Taxi"}	f
1203	ACCOUNTS_PAYABLE	Accounts Payable	Test 2	96	2022-01-21 10:37:03.353417+00	2022-01-21 10:37:03.35747+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Test 2"}	f
1204	ACCOUNTS_PAYABLE	Accounts Payable	Test Staging	95	2022-01-21 10:37:03.415841+00	2022-01-21 10:37:03.415907+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Test Staging"}	f
1205	ACCOUNTS_PAYABLE	Accounts Payable	Toll Charge	119	2022-01-21 10:37:03.416199+00	2022-01-21 10:37:03.416315+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Toll Charge"}	f
1206	ACCOUNTS_PAYABLE	Accounts Payable	Train	100	2022-01-21 10:37:03.416707+00	2022-01-21 10:37:03.41682+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Train"}	f
1207	ACCOUNTS_PAYABLE	Accounts Payable	Training	121	2022-01-21 10:37:03.41729+00	2022-01-21 10:37:03.41737+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Training"}	f
1208	ACCOUNTS_PAYABLE	Accounts Payable	Travel	22	2022-01-21 10:37:03.417551+00	2022-01-21 10:37:03.417717+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Travel"}	f
1209	ACCOUNTS_PAYABLE	Accounts Payable	Travel Meals	23	2022-01-21 10:37:03.418033+00	2022-01-21 10:37:03.418102+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Travel Meals"}	f
1210	ACCOUNTS_PAYABLE	Accounts Payable	Truck	37	2022-01-21 10:37:03.418322+00	2022-01-21 10:37:03.418358+00	8	\N	{"account_type": "Fixed Asset", "fully_qualified_name": "Truck"}	f
1211	ACCOUNTS_PAYABLE	Accounts Payable	Truck:Depreciation	39	2022-01-21 10:37:03.418545+00	2022-01-21 10:37:03.418568+00	8	\N	{"account_type": "Fixed Asset", "fully_qualified_name": "Truck:Depreciation"}	f
1212	ACCOUNTS_PAYABLE	Accounts Payable	Truck:Original Cost	38	2022-01-21 10:37:03.418619+00	2022-01-21 10:37:03.418638+00	8	\N	{"account_type": "Fixed Asset", "fully_qualified_name": "Truck:Original Cost"}	f
1213	ACCOUNTS_PAYABLE	Accounts Payable	Unapplied Cash Bill Payment Expense	88	2022-01-21 10:37:03.418691+00	2022-01-21 10:37:03.418712+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Unapplied Cash Bill Payment Expense"}	f
1214	ACCOUNTS_PAYABLE	Accounts Payable	Unapplied Cash Payment Income	87	2022-01-21 10:37:03.418776+00	2022-01-21 10:37:03.418795+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Unapplied Cash Payment Income"}	f
1339	CLASS	class	Adidas	5000000000000142509	2022-01-21 10:37:17.425674+00	2022-01-21 10:37:17.425722+00	8	\N	\N	f
1215	ACCOUNTS_PAYABLE	Accounts Payable	Uncategorized Asset	32	2022-01-21 10:37:03.418848+00	2022-01-21 10:37:03.418878+00	8	\N	{"account_type": "Other Current Asset", "fully_qualified_name": "Uncategorized Asset"}	f
1216	ACCOUNTS_PAYABLE	Accounts Payable	Uncategorized Expense	31	2022-01-21 10:37:03.418945+00	2022-01-21 10:37:03.418974+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Uncategorized Expense"}	f
1217	ACCOUNTS_PAYABLE	Accounts Payable	Uncategorized Income	30	2022-01-21 10:37:03.419041+00	2022-01-21 10:37:03.419276+00	8	\N	{"account_type": "Income", "fully_qualified_name": "Uncategorized Income"}	f
1218	ACCOUNTS_PAYABLE	Accounts Payable	Undeposited Funds	4	2022-01-21 10:37:03.426331+00	2022-01-21 10:37:03.427177+00	8	\N	{"account_type": "Other Current Asset", "fully_qualified_name": "Undeposited Funds"}	f
1219	ACCOUNTS_PAYABLE	Accounts Payable	Unspecified	122	2022-01-21 10:37:03.427439+00	2022-01-21 10:37:03.427763+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Unspecified"}	f
1220	ACCOUNTS_PAYABLE	Accounts Payable	Utilities	24	2022-01-21 10:37:03.428006+00	2022-01-21 10:37:03.428047+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Utilities"}	f
1221	ACCOUNTS_PAYABLE	Accounts Payable	Utilities:Gas and Electric	76	2022-01-21 10:37:03.428322+00	2022-01-21 10:37:03.428365+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Utilities:Gas and Electric"}	f
1222	ACCOUNTS_PAYABLE	Accounts Payable	Utilities:Telephone	77	2022-01-21 10:37:03.428818+00	2022-01-21 10:37:03.428867+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Utilities:Telephone"}	f
1223	ACCOUNTS_PAYABLE	Accounts Payable	Utility	103	2022-01-21 10:37:03.42903+00	2022-01-21 10:37:03.429131+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Utility"}	f
1224	EMPLOYEE	employee	Ashwin Ashwin Ashwin	104	2022-01-21 10:37:06.309564+00	2022-01-21 10:37:06.309802+00	8	\N	{"email": "ashwin.t@fyle.in"}	f
1225	EMPLOYEE	employee	Chethan M	105	2022-01-21 10:37:06.30996+00	2022-01-21 10:37:06.310007+00	8	\N	{"email": "chethan.m@fyle.in"}	f
1226	EMPLOYEE	employee	Emily Platt	55	2022-01-21 10:37:06.310134+00	2022-01-21 10:37:06.310179+00	8	\N	{"email": "shwetabh.kumar@fylehq.com"}	f
1227	EMPLOYEE	employee	Fyle For SageIntacct Test Backend Integration	86	2022-01-21 10:37:06.310296+00	2022-01-21 10:37:06.310337+00	8	\N	{"email": "ajain_1212@gmail.com"}	f
1228	EMPLOYEE	employee	James Lee	118	2022-01-21 10:37:06.315056+00	2022-01-21 10:37:06.315201+00	8	\N	{"email": null}	f
1229	EMPLOYEE	employee	John Cena	63	2022-01-21 10:37:06.315405+00	2022-01-21 10:37:06.315457+00	8	\N	{"email": "jc@fylehq.com"}	f
1230	EMPLOYEE	employee	John Johnson	54	2022-01-21 10:37:06.315598+00	2022-01-21 10:37:06.315792+00	8	\N	{"email": "gokul.kathiresan@fyle.in"}	f
1231	EMPLOYEE	employee	John Mueller 1	62	2022-01-21 10:37:06.315954+00	2022-01-21 10:37:06.315999+00	8	\N	{"email": "John@fylehq.com"}	f
1232	EMPLOYEE	employee	NS Tester	74	2022-01-21 10:37:06.316119+00	2022-01-21 10:37:06.316163+00	8	\N	{"email": "admin1@fyleforfylens.in"}	f
1233	EMPLOYEE	employee	User 243	108	2022-01-21 10:37:06.318126+00	2022-01-21 10:37:06.318186+00	8	\N	{"email": null}	f
1234	VENDOR	vendor	Alexandra Fitzgerald	88	2022-01-21 10:37:09.880359+00	2022-01-21 10:37:09.880404+00	8	\N	{"email": "user5@fylefordemo1.biz"}	f
1235	VENDOR	vendor	Allison Hill	87	2022-01-21 10:37:09.895928+00	2022-01-21 10:37:09.896018+00	8	\N	{"email": "user32@fylefordemo1.biz"}	f
1236	VENDOR	vendor	Amanda Monroe	92	2022-01-21 10:37:09.896697+00	2022-01-21 10:37:09.896763+00	8	\N	{"email": "user66@fyleforjatinorg.com"}	f
1237	VENDOR	vendor	Amazon	94	2022-01-21 10:37:09.897161+00	2022-01-21 10:37:09.897234+00	8	\N	{"email": null}	f
1238	VENDOR	vendor	Amazon Web Services	97	2022-01-21 10:37:09.897389+00	2022-01-21 10:37:09.897438+00	8	\N	{"email": null}	f
1239	VENDOR	vendor	Anna Williamson	113	2022-01-21 10:37:09.897551+00	2022-01-21 10:37:09.897601+00	8	\N	{"email": "user17@fyleforjatinorg.com"}	f
1240	VENDOR	vendor	Anne Glass	111	2022-01-21 10:37:09.899005+00	2022-01-21 10:37:09.899046+00	8	\N	{"email": "user58@fyleforjatinorg.com"}	f
1241	VENDOR	vendor	Anne Jackson	109	2022-01-21 10:37:09.899118+00	2022-01-21 10:37:09.899148+00	8	\N	{"email": "user49@fyleforjatinorg.com"}	f
1242	VENDOR	vendor	Ashwin	30	2022-01-21 10:37:09.899216+00	2022-01-21 10:37:09.899246+00	8	\N	{"email": "ashwin.t@fyle.in"}	f
1243	VENDOR	vendor	Ashwin from NetSuite	110	2022-01-21 10:37:09.899314+00	2022-01-21 10:37:09.899343+00	8	\N	{"email": "ashwin.t@fyle.in"}	f
1244	VENDOR	vendor	Basket Case	89	2022-01-21 10:37:09.899411+00	2022-01-21 10:37:09.899441+00	8	\N	{"email": "admin1@fyleforquickbooks.fyleappz.com"}	f
1245	VENDOR	vendor	Blob Johnson	117	2022-01-21 10:37:09.899507+00	2022-01-21 10:37:09.899536+00	8	\N	{"email": "shwetabh.kumar@fylehq.com"}	f
1246	VENDOR	vendor	Blooper Bloop	116	2022-01-21 10:37:09.899748+00	2022-01-21 10:37:09.899778+00	8	\N	{"email": "shwetabh.kumar@fylehq.com"}	f
1247	VENDOR	vendor	Brenda Hawkins	119	2022-01-21 10:37:09.899845+00	2022-01-21 10:37:09.899874+00	8	\N	{"email": "user34@fyleforjatinorg.com"}	f
1248	VENDOR	vendor	Brian Foster	79	2022-01-21 10:37:09.899941+00	2022-01-21 10:37:09.899971+00	8	\N	{"email": "user2@fyleforucantseeme.blind"}	f
1249	VENDOR	vendor	Brosnahan Insurance Agency	31	2022-01-21 10:37:09.902576+00	2022-01-21 10:37:09.902742+00	8	\N	{"email": null}	f
1250	VENDOR	vendor	Cal Telephone	32	2022-01-21 10:37:09.902977+00	2022-01-21 10:37:09.903034+00	8	\N	{"email": null}	f
1251	VENDOR	vendor	Central Coalfields	112	2022-01-21 10:37:09.903233+00	2022-01-21 10:37:09.904022+00	8	\N	{"email": "user3@fyleforsage.intacct"}	f
1252	VENDOR	vendor	Chin's Gas and Oil	33	2022-01-21 10:37:09.904316+00	2022-01-21 10:37:09.904355+00	8	\N	{"email": null}	f
1253	VENDOR	vendor	Chris Curtis	80	2022-01-21 10:37:09.904433+00	2022-01-21 10:37:09.904463+00	8	\N	{"email": "user5@fyleforucantseeme.blind"}	f
1254	VENDOR	vendor	Cigna Health Care	34	2022-01-21 10:37:09.90453+00	2022-01-21 10:37:09.90456+00	8	\N	{"email": null}	f
1255	VENDOR	vendor	Credit Card Misc	93	2022-01-21 10:37:09.90479+00	2022-01-21 10:37:09.904821+00	8	\N	{"email": null}	f
1256	VENDOR	vendor	DOMINO'S	82	2022-01-21 10:37:09.904889+00	2022-01-21 10:37:09.904919+00	8	\N	{"email": null}	f
1257	VENDOR	vendor	DOMINO'S P	100	2022-01-21 10:37:09.904986+00	2022-01-21 10:37:09.905015+00	8	\N	{"email": null}	f
1258	VENDOR	vendor	Diego's Road Warrior Bodyshop	36	2022-01-21 10:37:09.905081+00	2022-01-21 10:37:09.905111+00	8	\N	{"email": null}	f
1259	VENDOR	vendor	Dominos	95	2022-01-21 10:37:09.905178+00	2022-01-21 10:37:09.905208+00	8	\N	{"email": null}	f
1260	VENDOR	vendor	EDD	37	2022-01-21 10:37:09.905274+00	2022-01-21 10:37:09.905434+00	8	\N	{"email": null}	f
1261	VENDOR	vendor	Edward Blankenship	90	2022-01-21 10:37:09.906164+00	2022-01-21 10:37:09.906226+00	8	\N	{"email": "user43@fyleforjatinorg.com"}	f
1262	VENDOR	vendor	Ellis Equipment Rental	38	2022-01-21 10:37:09.906819+00	2022-01-21 10:37:09.90687+00	8	\N	{"email": "Rental@intuit.com"}	f
1263	VENDOR	vendor	Fidelity	39	2022-01-21 10:37:09.906972+00	2022-01-21 10:37:09.907003+00	8	\N	{"email": null}	f
1264	VENDOR	vendor	Fyle Vendor	107	2022-01-21 10:37:09.907112+00	2022-01-21 10:37:09.907161+00	8	\N	{"email": "123@fye.in"}	f
1265	VENDOR	vendor	Gokul	56	2022-01-21 10:37:09.907271+00	2022-01-21 10:37:09.907319+00	8	\N	{"email": null}	f
1266	VENDOR	vendor	Gokul Kathiresan	64	2022-01-21 10:37:09.90758+00	2022-01-21 10:37:09.907636+00	8	\N	{"email": "jc@fylehq.com"}	f
1267	VENDOR	vendor	Gokul Kathiresan King	65	2022-01-21 10:37:09.90776+00	2022-01-21 10:37:09.907804+00	8	\N	{"email": "jc@fylehq.com"}	f
1268	VENDOR	vendor	Hall Properties	40	2022-01-21 10:37:09.907926+00	2022-01-21 10:37:09.907967+00	8	\N	{"email": null}	f
1269	VENDOR	vendor	Hicks Hardware	41	2022-01-21 10:37:09.908094+00	2022-01-21 10:37:09.908227+00	8	\N	{"email": null}	f
1270	VENDOR	vendor	James Taylor	66	2022-01-21 10:37:09.924453+00	2022-01-21 10:37:09.924957+00	8	\N	{"email": "user7@fylefordashboard1.com"}	f
1271	VENDOR	vendor	Jessica Lane	98	2022-01-21 10:37:09.92685+00	2022-01-21 10:37:09.926966+00	8	\N	{"email": "user8@fyleforlol.sob"}	f
1273	VENDOR	vendor	Joshua Wood	84	2022-01-21 10:37:09.932263+00	2022-01-21 10:37:09.932333+00	8	\N	{"email": "user1@fylefordashboard3.com"}	f
1274	VENDOR	vendor	Justin Glass	68	2022-01-21 10:37:09.934352+00	2022-01-21 10:37:09.934452+00	8	\N	{"email": "user9@fylefordashboard1.com"}	f
1275	VENDOR	vendor	Lee Advertising	42	2022-01-21 10:37:09.935945+00	2022-01-21 10:37:09.936017+00	8	\N	{"email": null}	f
1276	VENDOR	vendor	Lord Voldemort	106	2022-01-21 10:37:09.936464+00	2022-01-21 10:37:09.936545+00	8	\N	{"email": null}	f
1277	VENDOR	vendor	Mahoney Mugs	43	2022-01-21 10:37:09.938572+00	2022-01-21 10:37:09.938676+00	8	\N	{"email": null}	f
1278	VENDOR	vendor	Matt Damon	72	2022-01-21 10:37:09.938838+00	2022-01-21 10:37:09.938882+00	8	\N	{"email": "shwetabh.kumar@fyle.in"}	f
1279	VENDOR	vendor	Matthew Estrada	67	2022-01-21 10:37:09.938995+00	2022-01-21 10:37:09.939038+00	8	\N	{"email": "user10@fylefordashboard1.com"}	f
1280	VENDOR	vendor	Met Life Dental	44	2022-01-21 10:37:09.939145+00	2022-01-21 10:37:09.939185+00	8	\N	{"email": null}	f
1281	VENDOR	vendor	Natalie Pope	71	2022-01-21 10:37:09.939291+00	2022-01-21 10:37:09.939333+00	8	\N	{"email": "user3@fylefordashboard1.com"}	f
1282	VENDOR	vendor	National Eye Care	45	2022-01-21 10:37:09.939436+00	2022-01-21 10:37:09.939478+00	8	\N	{"email": "Nateyecare@intuit.com, pauliejones15@intuit.com"}	f
1283	VENDOR	vendor	Nilesh Pant	102	2022-01-21 10:37:09.939692+00	2022-01-21 10:37:09.939766+00	8	\N	{"email": "nilesh.p@fyle.in"}	f
1284	VENDOR	vendor	Norton Lumber and Building Materials	46	2022-01-21 10:37:09.984667+00	2022-01-21 10:37:09.984802+00	8	\N	{"email": "Materials@intuit.com"}	f
1285	VENDOR	vendor	PG&E	48	2022-01-21 10:37:09.985938+00	2022-01-21 10:37:09.985985+00	8	\N	{"email": "utilities@noemail.com"}	f
1286	VENDOR	vendor	Pam Seitz	47	2022-01-21 10:37:09.986063+00	2022-01-21 10:37:09.986093+00	8	\N	{"email": "SeitzCPA@noemail.com"}	f
1287	VENDOR	vendor	Peter Derek	35	2022-01-21 10:37:09.986162+00	2022-01-21 10:37:09.986192+00	8	\N	{"email": "shwetabh.kumar@fylehq.com"}	f
1288	VENDOR	vendor	Ravindra Jadeja	115	2022-01-21 10:37:09.986259+00	2022-01-21 10:37:09.986289+00	8	\N	{"email": "user9@fylefordashboard1.com"}	f
1289	VENDOR	vendor	Robertson & Associates	49	2022-01-21 10:37:09.986356+00	2022-01-21 10:37:09.986386+00	8	\N	{"email": null}	f
1290	VENDOR	vendor	Ryan Gallagher	70	2022-01-21 10:37:09.986453+00	2022-01-21 10:37:09.986483+00	8	\N	{"email": "approver1@fylefordashboard1.com"}	f
1291	VENDOR	vendor	STEAK-N-SHAKE#0664	101	2022-01-21 10:37:09.986549+00	2022-01-21 10:37:09.986862+00	8	\N	{"email": null}	f
1292	VENDOR	vendor	Samantha Washington	69	2022-01-21 10:37:09.987046+00	2022-01-21 10:37:09.987119+00	8	\N	{"email": "user4@fylefordashboard1.com"}	f
1293	VENDOR	vendor	Shwetabh Ji	114	2022-01-21 10:37:09.987606+00	2022-01-21 10:37:09.987745+00	8	\N	{"email": "user7@fylefordashboard3.com"}	f
1294	VENDOR	vendor	Squeaky Kleen Car Wash	57	2022-01-21 10:37:09.988014+00	2022-01-21 10:37:09.988083+00	8	\N	{"email": null}	f
1295	VENDOR	vendor	Tania's Nursery	50	2022-01-21 10:37:09.991754+00	2022-01-21 10:37:09.992807+00	8	\N	{"email": "plantqueen@taniasnursery.com"}	f
1296	VENDOR	vendor	Theresa Brown	81	2022-01-21 10:37:09.993119+00	2022-01-21 10:37:09.994006+00	8	\N	{"email": "admin1@fyleforucantseeme.blind"}	f
1297	VENDOR	vendor	Tim Philip Masonry	51	2022-01-21 10:37:09.994407+00	2022-01-21 10:37:09.994603+00	8	\N	{"email": "tim.philip@timphilipmasonry.com"}	f
1298	VENDOR	vendor	Tony Rondonuwu	52	2022-01-21 10:37:09.994834+00	2022-01-21 10:37:10.024304+00	8	\N	{"email": "tonyrjr@intuit.com"}	f
1299	VENDOR	vendor	Uber	96	2022-01-21 10:37:10.02455+00	2022-01-21 10:37:10.024734+00	8	\N	{"email": null}	f
1300	VENDOR	vendor	United States Treasury	53	2022-01-21 10:37:10.02489+00	2022-01-21 10:37:10.02494+00	8	\N	{"email": "taxesaregreat@intuit.com"}	f
1301	VENDOR	vendor	Victor Martinez	73	2022-01-21 10:37:10.025074+00	2022-01-21 10:37:10.025121+00	8	\N	{"email": "user6@fylefordashboard2.com"}	f
1302	VENDOR	vendor	Victor Martinez II	99	2022-01-21 10:37:10.025251+00	2022-01-21 10:37:10.025297+00	8	\N	{"email": "user6@fyleforintegrations.com"}	f
1303	VENDOR	vendor	Wal-Mart	83	2022-01-21 10:37:10.02542+00	2022-01-21 10:37:10.025662+00	8	\N	{"email": null}	f
1304	VENDOR	vendor	test Sharma	120	2022-01-21 10:37:10.026021+00	2022-01-21 10:37:10.02609+00	8	\N	{"email": "test@fyle.in"}	f
1305	CUSTOMER	customer	Amy's Bird Sanctuary	1	2022-01-21 10:37:14.520742+00	2022-01-21 10:37:14.520844+00	8	\N	\N	f
1306	CUSTOMER	customer	Amy's Bird Sanctuary:Test Project	58	2022-01-21 10:37:14.520967+00	2022-01-21 10:37:14.521016+00	8	\N	\N	f
1307	CUSTOMER	customer	Ashwinn	103	2022-01-21 10:37:14.521134+00	2022-01-21 10:37:14.521178+00	8	\N	\N	f
1308	CUSTOMER	customer	Bill's Windsurf Shop	2	2022-01-21 10:37:14.521268+00	2022-01-21 10:37:14.52131+00	8	\N	\N	f
1309	CUSTOMER	customer	Cool Cars	3	2022-01-21 10:37:14.521399+00	2022-01-21 10:37:14.521442+00	8	\N	\N	f
1310	CUSTOMER	customer	Diego Rodriguez	4	2022-01-21 10:37:14.521837+00	2022-01-21 10:37:14.521893+00	8	\N	\N	f
1311	CUSTOMER	customer	Diego Rodriguez:Test Project	59	2022-01-21 10:37:14.521987+00	2022-01-21 10:37:14.522045+00	8	\N	\N	f
1312	CUSTOMER	customer	Dukes Basketball Camp	5	2022-01-21 10:37:14.522168+00	2022-01-21 10:37:14.522214+00	8	\N	\N	f
1313	CUSTOMER	customer	Dylan Sollfrank	6	2022-01-21 10:37:14.522306+00	2022-01-21 10:37:14.52235+00	8	\N	\N	f
1314	CUSTOMER	customer	Freeman Sporting Goods	7	2022-01-21 10:37:14.522446+00	2022-01-21 10:37:14.522493+00	8	\N	\N	f
1315	CUSTOMER	customer	Freeman Sporting Goods:0969 Ocean View Road	8	2022-01-21 10:37:14.522593+00	2022-01-21 10:37:14.522885+00	8	\N	\N	f
1316	CUSTOMER	customer	Freeman Sporting Goods:55 Twin Lane	9	2022-01-21 10:37:14.522998+00	2022-01-21 10:37:14.523038+00	8	\N	\N	f
1317	CUSTOMER	customer	Geeta Kalapatapu	10	2022-01-21 10:37:14.523124+00	2022-01-21 10:37:14.523163+00	8	\N	\N	f
1318	CUSTOMER	customer	Gevelber Photography	11	2022-01-21 10:37:14.523247+00	2022-01-21 10:37:14.523285+00	8	\N	\N	f
1319	CUSTOMER	customer	Jeff's Jalopies	12	2022-01-21 10:37:14.523368+00	2022-01-21 10:37:14.523406+00	8	\N	\N	f
1320	CUSTOMER	customer	John Melton	13	2022-01-21 10:37:14.523634+00	2022-01-21 10:37:14.52368+00	8	\N	\N	f
1321	CUSTOMER	customer	Kate Whelan	14	2022-01-21 10:37:14.523769+00	2022-01-21 10:37:14.523808+00	8	\N	\N	f
1322	CUSTOMER	customer	Kookies by Kathy	16	2022-01-21 10:37:14.523893+00	2022-01-21 10:37:14.523932+00	8	\N	\N	f
1323	CUSTOMER	customer	Mark Cho	17	2022-01-21 10:37:14.524014+00	2022-01-21 10:37:14.524069+00	8	\N	\N	f
1324	CUSTOMER	customer	Paulsen Medical Supplies	18	2022-01-21 10:37:14.524153+00	2022-01-21 10:37:14.524196+00	8	\N	\N	f
1325	CUSTOMER	customer	Pye's Cakes	15	2022-01-21 10:37:14.524279+00	2022-01-21 10:37:14.524317+00	8	\N	\N	f
1326	CUSTOMER	customer	Rago Travel Agency	19	2022-01-21 10:37:14.5244+00	2022-01-21 10:37:14.524439+00	8	\N	\N	f
1327	CUSTOMER	customer	Red Rock Diner	20	2022-01-21 10:37:14.524522+00	2022-01-21 10:37:14.524561+00	8	\N	\N	f
1328	CUSTOMER	customer	Rondonuwu Fruit and Vegi	21	2022-01-21 10:37:14.524776+00	2022-01-21 10:37:14.524815+00	8	\N	\N	f
1329	CUSTOMER	customer	Shara Barnett	22	2022-01-21 10:37:14.5249+00	2022-01-21 10:37:14.524939+00	8	\N	\N	f
1330	CUSTOMER	customer	Shara Barnett:Barnett Design	23	2022-01-21 10:37:14.525023+00	2022-01-21 10:37:14.525061+00	8	\N	\N	f
1331	CUSTOMER	customer	Sheldon Cooper	60	2022-01-21 10:37:14.525145+00	2022-01-21 10:37:14.525183+00	8	\N	\N	f
1332	CUSTOMER	customer	Sheldon Cooper:Incremental Project	61	2022-01-21 10:37:14.525265+00	2022-01-21 10:37:14.525303+00	8	\N	\N	f
1333	CUSTOMER	customer	Sonnenschein Family Store	24	2022-01-21 10:37:14.525386+00	2022-01-21 10:37:14.525426+00	8	\N	\N	f
1334	CUSTOMER	customer	Sushi by Katsuyuki	25	2022-01-21 10:37:14.525508+00	2022-01-21 10:37:14.525546+00	8	\N	\N	f
1335	CUSTOMER	customer	Travis Waldron	26	2022-01-21 10:37:14.525755+00	2022-01-21 10:37:14.525802+00	8	\N	\N	f
1336	CUSTOMER	customer	Video Games by Dan	27	2022-01-21 10:37:14.525891+00	2022-01-21 10:37:14.525933+00	8	\N	\N	f
1337	CUSTOMER	customer	Wedding Planning by Whitney	28	2022-01-21 10:37:14.526019+00	2022-01-21 10:37:14.526059+00	8	\N	\N	f
1338	CUSTOMER	customer	Weiskopf Consulting	29	2022-01-21 10:37:14.526125+00	2022-01-21 10:37:14.526159+00	8	\N	\N	f
1340	CLASS	class	Fabrication	5000000000000219489	2022-01-21 10:37:17.425784+00	2022-01-21 10:37:17.425815+00	8	\N	\N	f
1341	CLASS	class	FAE	5000000000000142510	2022-01-21 10:37:17.425872+00	2022-01-21 10:37:17.425902+00	8	\N	\N	f
1342	TAX_CODE	Tax Code	Out of scope @0%	4	2022-01-21 10:37:21.736768+00	2022-01-21 10:37:21.736845+00	8	\N	{"tax_rate": 0, "tax_refs": [{"name": "NO TAX PURCHASE", "value": "5"}]}	f
1343	DEPARTMENT	Department	Accountants Inc	4	2022-01-21 10:37:24.605823+00	2022-01-21 10:37:24.605881+00	8	\N	\N	f
1344	DEPARTMENT	Department	Bangalore	1	2022-01-21 10:37:24.60623+00	2022-01-21 10:37:24.606967+00	8	\N	\N	f
1345	DEPARTMENT	Department	Bebe Rexha	2	2022-01-21 10:37:24.607349+00	2022-01-21 10:37:24.607399+00	8	\N	\N	f
1346	DEPARTMENT	Department	suhas_p1	3	2022-01-21 10:37:24.608098+00	2022-01-21 10:37:24.608154+00	8	\N	\N	f
1347	ACCOUNT	Account	Advertising	7	2022-01-21 10:37:36.324784+00	2022-01-21 10:37:36.324831+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Advertising"}	f
1348	ACCOUNT	Account	Automobile	55	2022-01-21 10:37:36.324909+00	2022-01-21 10:37:36.324939+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Automobile"}	f
1349	ACCOUNT	Account	Automobile:Fuel	56	2022-01-21 10:37:36.325007+00	2022-01-21 10:37:36.325037+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Automobile:Fuel"}	f
1350	ACCOUNT	Account	Bank Charges	8	2022-01-21 10:37:36.325105+00	2022-01-21 10:37:36.325134+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Bank Charges"}	f
1351	ACCOUNT	Account	Bus	108	2022-01-21 10:37:36.325201+00	2022-01-21 10:37:36.32523+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Bus"}	f
1352	ACCOUNT	Account	Business Expense	127	2022-01-21 10:37:36.325297+00	2022-01-21 10:37:36.325326+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Business Expense"}	f
1353	ACCOUNT	Account	Commissions & fees	9	2022-01-21 10:37:36.325392+00	2022-01-21 10:37:36.325422+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Commissions & fees"}	f
1354	ACCOUNT	Account	Courier	111	2022-01-21 10:37:36.325488+00	2022-01-21 10:37:36.325517+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Courier"}	f
1355	ACCOUNT	Account	Disposal Fees	28	2022-01-21 10:37:36.325596+00	2022-01-21 10:37:36.325626+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Disposal Fees"}	f
1356	ACCOUNT	Account	Dues & Subscriptions	10	2022-01-21 10:37:36.325693+00	2022-01-21 10:37:36.325723+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Dues & Subscriptions"}	f
1357	ACCOUNT	Account	Entertainment	104	2022-01-21 10:37:36.325788+00	2022-01-21 10:37:36.325818+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Entertainment"}	f
1358	ACCOUNT	Account	Equipment Rental	29	2022-01-21 10:37:36.325885+00	2022-01-21 10:37:36.325914+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Equipment Rental"}	f
1359	ACCOUNT	Account	Flight	116	2022-01-21 10:37:36.32598+00	2022-01-21 10:37:36.32601+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Flight"}	f
1360	ACCOUNT	Account	Food	106	2022-01-21 10:37:36.326076+00	2022-01-21 10:37:36.326105+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Food"}	f
1361	ACCOUNT	Account	Fuel	101	2022-01-21 10:37:36.326171+00	2022-01-21 10:37:36.326201+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Fuel"}	f
1362	ACCOUNT	Account	Hotel	112	2022-01-21 10:37:36.326267+00	2022-01-21 10:37:36.326296+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Hotel"}	f
1363	ACCOUNT	Account	Incremental Account	92	2022-01-21 10:37:36.326363+00	2022-01-21 10:37:36.326392+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Incremental Account"}	f
1364	ACCOUNT	Account	Insurance	11	2022-01-21 10:37:36.326458+00	2022-01-21 10:37:36.326488+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Insurance"}	f
1365	ACCOUNT	Account	Insurance:Workers Compensation	57	2022-01-21 10:37:36.326554+00	2022-01-21 10:37:36.326584+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Insurance:Workers Compensation"}	f
1366	ACCOUNT	Account	Internet	109	2022-01-21 10:37:36.32665+00	2022-01-21 10:37:36.326679+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Internet"}	f
1367	ACCOUNT	Account	Job Expenses	58	2022-01-21 10:37:36.326919+00	2022-01-21 10:37:36.326965+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses"}	f
1368	ACCOUNT	Account	Job Expenses:Cost of Labor	59	2022-01-21 10:37:36.32706+00	2022-01-21 10:37:36.327102+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Cost of Labor"}	f
1369	ACCOUNT	Account	Job Expenses:Cost of Labor:Installation	60	2022-01-21 10:37:36.327207+00	2022-01-21 10:37:36.342665+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Cost of Labor:Installation"}	f
1370	ACCOUNT	Account	Job Expenses:Cost of Labor:Maintenance and Repairs	61	2022-01-21 10:37:36.345798+00	2022-01-21 10:37:36.345845+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Cost of Labor:Maintenance and Repairs"}	f
1371	ACCOUNT	Account	Job Expenses:Equipment Rental	62	2022-01-21 10:37:36.345948+00	2022-01-21 10:37:36.345986+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Equipment Rental"}	f
1372	ACCOUNT	Account	Job Expenses:Job Materials	63	2022-01-21 10:37:36.346083+00	2022-01-21 10:37:36.346122+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials"}	f
1373	ACCOUNT	Account	Job Expenses:Job Materials:Decks and Patios	64	2022-01-21 10:37:36.346218+00	2022-01-21 10:37:36.346257+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials:Decks and Patios"}	f
1374	ACCOUNT	Account	Job Expenses:Job Materials:Fountain and Garden Lighting	65	2022-01-21 10:37:36.346353+00	2022-01-21 10:37:36.34639+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials:Fountain and Garden Lighting"}	f
1375	ACCOUNT	Account	Job Expenses:Job Materials:Plants and Soil	66	2022-01-21 10:37:36.346485+00	2022-01-21 10:37:36.346543+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials:Plants and Soil"}	f
1376	ACCOUNT	Account	Job Expenses:Job Materials:Sprinklers and Drip Systems	67	2022-01-21 10:37:36.346641+00	2022-01-21 10:37:36.346679+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials:Sprinklers and Drip Systems"}	f
1377	ACCOUNT	Account	Job Expenses:Permits	68	2022-01-21 10:37:36.346798+00	2022-01-21 10:37:36.346839+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Permits"}	f
1378	ACCOUNT	Account	Legal & Professional Fees	12	2022-01-21 10:37:36.346943+00	2022-01-21 10:37:36.346982+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Legal & Professional Fees"}	f
1379	ACCOUNT	Account	Legal & Professional Fees:Accounting	69	2022-01-21 10:37:36.347151+00	2022-01-21 10:37:36.347213+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Legal & Professional Fees:Accounting"}	f
1380	ACCOUNT	Account	Legal & Professional Fees:Bookkeeper	70	2022-01-21 10:37:36.347329+00	2022-01-21 10:37:36.347367+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Legal & Professional Fees:Bookkeeper"}	f
1381	ACCOUNT	Account	Legal & Professional Fees:Lawyer	71	2022-01-21 10:37:36.347464+00	2022-01-21 10:37:36.347501+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Legal & Professional Fees:Lawyer"}	f
1382	ACCOUNT	Account	Maintenance and Repair	72	2022-01-21 10:37:36.347604+00	2022-01-21 10:37:36.347644+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Maintenance and Repair"}	f
1383	ACCOUNT	Account	Maintenance and Repair:Building Repairs	73	2022-01-21 10:37:36.347762+00	2022-01-21 10:37:36.347802+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Maintenance and Repair:Building Repairs"}	f
1564	CUSTOMER	customer	Sonnenschein Family Store	24	2022-01-21 10:42:34.252661+00	2022-01-21 10:42:34.252796+00	9	\N	\N	f
1384	ACCOUNT	Account	Maintenance and Repair:Computer Repairs	74	2022-01-21 10:37:36.347904+00	2022-01-21 10:37:36.347943+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Maintenance and Repair:Computer Repairs"}	f
1385	ACCOUNT	Account	Maintenance and Repair:Equipment Repairs	75	2022-01-21 10:37:36.348041+00	2022-01-21 10:37:36.348081+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Maintenance and Repair:Equipment Repairs"}	f
1386	ACCOUNT	Account	Meals	13	2022-01-21 10:37:36.348181+00	2022-01-21 10:37:36.34822+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Meals"}	f
1387	ACCOUNT	Account	Mileage	105	2022-01-21 10:37:36.348318+00	2022-01-21 10:37:36.348356+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Mileage"}	f
1388	ACCOUNT	Account	Office Expenses	15	2022-01-21 10:37:36.348456+00	2022-01-21 10:37:36.348496+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Office Expenses"}	f
1389	ACCOUNT	Account	Office Party	115	2022-01-21 10:37:36.348594+00	2022-01-21 10:37:36.348633+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Office Party"}	f
1390	ACCOUNT	Account	OFFICE SUPPLIES	98	2022-01-21 10:37:36.348749+00	2022-01-21 10:37:36.348788+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "OFFICE SUPPLIES"}	f
1391	ACCOUNT	Account	Office Supplies 2	124	2022-01-21 10:37:36.348886+00	2022-01-21 10:37:36.348925+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Office Supplies 2"}	f
1392	ACCOUNT	Account	Office/General Administrative Expenses	97	2022-01-21 10:37:36.349029+00	2022-01-21 10:37:36.349069+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Office/General Administrative Expenses"}	f
1393	ACCOUNT	Account	Others	123	2022-01-21 10:37:36.349168+00	2022-01-21 10:37:36.349206+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Others"}	f
1394	ACCOUNT	Account	Parking	118	2022-01-21 10:37:36.349304+00	2022-01-21 10:37:36.349342+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Parking"}	f
1395	ACCOUNT	Account	Per Diem	107	2022-01-21 10:37:36.349439+00	2022-01-21 10:37:36.349477+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Per Diem"}	f
1396	ACCOUNT	Account	Phone	114	2022-01-21 10:37:36.349573+00	2022-01-21 10:37:36.349611+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Phone"}	f
1397	ACCOUNT	Account	Professional Services	113	2022-01-21 10:37:36.38626+00	2022-01-21 10:37:36.386319+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Professional Services"}	f
1398	ACCOUNT	Account	Promotional	16	2022-01-21 10:37:36.386424+00	2022-01-21 10:37:36.386464+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Promotional"}	f
1399	ACCOUNT	Account	Purchases	78	2022-01-21 10:37:36.386561+00	2022-01-21 10:37:36.386599+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Purchases"}	f
1400	ACCOUNT	Account	Rent or Lease	17	2022-01-21 10:37:36.386698+00	2022-01-21 10:37:36.386736+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Rent or Lease"}	f
1401	ACCOUNT	Account	Snacks	102	2022-01-21 10:37:36.386834+00	2022-01-21 10:37:36.386873+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Snacks"}	f
1402	ACCOUNT	Account	Software	117	2022-01-21 10:37:36.386972+00	2022-01-21 10:37:36.38701+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Software"}	f
1403	ACCOUNT	Account	Stationery & Printing	19	2022-01-21 10:37:36.387107+00	2022-01-21 10:37:36.387146+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Stationery & Printing"}	f
1404	ACCOUNT	Account	Supplies Test 2	20	2022-01-21 10:37:36.387243+00	2022-01-21 10:37:36.387281+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Supplies Test 2"}	f
1405	ACCOUNT	Account	Tax	120	2022-01-21 10:37:36.387378+00	2022-01-21 10:37:36.387416+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Tax"}	f
1406	ACCOUNT	Account	Taxes & Licenses	21	2022-01-21 10:37:36.387514+00	2022-01-21 10:37:36.387553+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Taxes & Licenses"}	f
1407	ACCOUNT	Account	Taxi	110	2022-01-21 10:37:36.387651+00	2022-01-21 10:37:36.387691+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Taxi"}	f
1408	ACCOUNT	Account	Test 2	96	2022-01-21 10:37:36.387788+00	2022-01-21 10:37:36.387826+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Test 2"}	f
1409	ACCOUNT	Account	Test Staging	95	2022-01-21 10:37:36.38792+00	2022-01-21 10:37:36.387957+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Test Staging"}	f
1410	ACCOUNT	Account	Toll Charge	119	2022-01-21 10:37:36.388053+00	2022-01-21 10:37:36.38809+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Toll Charge"}	f
1411	ACCOUNT	Account	Train	100	2022-01-21 10:37:36.388183+00	2022-01-21 10:37:36.388222+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Train"}	f
1412	ACCOUNT	Account	Training	121	2022-01-21 10:37:36.388317+00	2022-01-21 10:37:36.388355+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Training"}	f
1413	ACCOUNT	Account	Travel	22	2022-01-21 10:37:36.388449+00	2022-01-21 10:37:36.388487+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Travel"}	f
1414	ACCOUNT	Account	Travel Meals	23	2022-01-21 10:37:36.414562+00	2022-01-21 10:37:36.414632+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Travel Meals"}	f
1415	ACCOUNT	Account	Unapplied Cash Bill Payment Expense	88	2022-01-21 10:37:36.414768+00	2022-01-21 10:37:36.414806+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Unapplied Cash Bill Payment Expense"}	f
1416	ACCOUNT	Account	Uncategorized Expense	31	2022-01-21 10:37:36.414905+00	2022-01-21 10:37:36.414944+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Uncategorized Expense"}	f
1417	ACCOUNT	Account	Unspecified	122	2022-01-21 10:37:36.415041+00	2022-01-21 10:37:36.417916+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Unspecified"}	f
1418	ACCOUNT	Account	Utilities	24	2022-01-21 10:37:36.418112+00	2022-01-21 10:37:36.418158+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Utilities"}	f
1419	ACCOUNT	Account	Utilities:Gas and Electric	76	2022-01-21 10:37:36.418266+00	2022-01-21 10:37:36.418305+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Utilities:Gas and Electric"}	f
1420	ACCOUNT	Account	Utilities:Telephone	77	2022-01-21 10:37:36.418407+00	2022-01-21 10:37:36.418447+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Utilities:Telephone"}	f
1421	ACCOUNT	Account	Utility	103	2022-01-21 10:37:36.418547+00	2022-01-21 10:37:36.418589+00	8	\N	{"account_type": "Expense", "fully_qualified_name": "Utility"}	f
1422	CREDIT_CARD_ACCOUNT	Credit Card Account	Mastercard	41	2022-01-21 10:42:23.561668+00	2022-01-21 10:42:23.561752+00	9	\N	{"account_type": "Credit Card", "fully_qualified_name": "Mastercard"}	f
1423	CREDIT_CARD_ACCOUNT	Credit Card Account	Visa	42	2022-01-21 10:42:23.561951+00	2022-01-21 10:42:23.562005+00	9	\N	{"account_type": "Credit Card", "fully_qualified_name": "Visa"}	f
1424	BANK_ACCOUNT	Bank Account	Checking	35	2022-01-21 10:42:23.698358+00	2022-01-21 10:42:23.698428+00	9	\N	{"account_type": "Bank", "fully_qualified_name": "Checking"}	f
1425	BANK_ACCOUNT	Bank Account	Savings	36	2022-01-21 10:42:23.698547+00	2022-01-21 10:42:23.698588+00	9	\N	{"account_type": "Bank", "fully_qualified_name": "Savings"}	f
1426	ACCOUNTS_PAYABLE	Accounts Payable	Accounts Payable (A/P)	33	2022-01-21 10:42:23.845445+00	2022-01-21 10:42:23.845502+00	9	\N	{"account_type": "Accounts Payable", "fully_qualified_name": "Accounts Payable (A/P)"}	f
1427	ACCOUNTS_PAYABLE	Accounts Payable	Accounts Receivable (A/R)	84	2022-01-21 10:42:23.845608+00	2022-01-21 10:42:23.845648+00	9	\N	{"account_type": "Accounts Receivable", "fully_qualified_name": "Accounts Receivable (A/R)"}	f
1428	ACCOUNTS_PAYABLE	Accounts Payable	Advertising	7	2022-01-21 10:42:23.845748+00	2022-01-21 10:42:23.845788+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Advertising"}	f
1565	CUSTOMER	customer	Sushi by Katsuyuki	25	2022-01-21 10:42:34.252872+00	2022-01-21 10:42:34.252977+00	9	\N	\N	f
1429	ACCOUNTS_PAYABLE	Accounts Payable	Arizona Dept. of Revenue Payable	89	2022-01-21 10:42:23.845888+00	2022-01-21 10:42:23.845927+00	9	\N	{"account_type": "Other Current Liability", "fully_qualified_name": "Arizona Dept. of Revenue Payable"}	f
1430	ACCOUNTS_PAYABLE	Accounts Payable	Automobile	55	2022-01-21 10:42:23.846026+00	2022-01-21 10:42:23.846066+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Automobile"}	f
1431	ACCOUNTS_PAYABLE	Accounts Payable	Automobile:Fuel	56	2022-01-21 10:42:23.846163+00	2022-01-21 10:42:23.846202+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Automobile:Fuel"}	f
1432	ACCOUNTS_PAYABLE	Accounts Payable	Bank Charges	8	2022-01-21 10:42:23.846301+00	2022-01-21 10:42:23.846339+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Bank Charges"}	f
1433	ACCOUNTS_PAYABLE	Accounts Payable	Billable Expense Income	85	2022-01-21 10:42:23.846437+00	2022-01-21 10:42:23.846628+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Billable Expense Income"}	f
1434	ACCOUNTS_PAYABLE	Accounts Payable	Board of Equalization Payable	90	2022-01-21 10:42:23.84678+00	2022-01-21 10:42:23.846829+00	9	\N	{"account_type": "Other Current Liability", "fully_qualified_name": "Board of Equalization Payable"}	f
1435	ACCOUNTS_PAYABLE	Accounts Payable	California Department of Tax and Fee Administration Payable	91	2022-01-21 10:42:23.84696+00	2022-01-21 10:42:23.846998+00	9	\N	{"account_type": "Other Current Liability", "fully_qualified_name": "California Department of Tax and Fee Administration Payable"}	f
1436	ACCOUNTS_PAYABLE	Accounts Payable	Commissions & fees	9	2022-01-21 10:42:23.847102+00	2022-01-21 10:42:23.847136+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Commissions & fees"}	f
1437	ACCOUNTS_PAYABLE	Accounts Payable	Cost of Goods Sold	80	2022-01-21 10:42:23.847211+00	2022-01-21 10:42:23.84724+00	9	\N	{"account_type": "Cost of Goods Sold", "fully_qualified_name": "Cost of Goods Sold"}	f
1438	ACCOUNTS_PAYABLE	Accounts Payable	Depreciation	40	2022-01-21 10:42:23.847443+00	2022-01-21 10:42:23.847485+00	9	\N	{"account_type": "Other Expense", "fully_qualified_name": "Depreciation"}	f
1439	ACCOUNTS_PAYABLE	Accounts Payable	Design income	82	2022-01-21 10:42:23.847585+00	2022-01-21 10:42:23.847623+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Design income"}	f
1440	ACCOUNTS_PAYABLE	Accounts Payable	Discounts given	86	2022-01-21 10:42:23.847719+00	2022-01-21 10:42:23.847755+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Discounts given"}	f
1441	ACCOUNTS_PAYABLE	Accounts Payable	Disposal Fees	28	2022-01-21 10:42:23.84893+00	2022-01-21 10:42:23.849061+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Disposal Fees"}	f
1442	ACCOUNTS_PAYABLE	Accounts Payable	Dues & Subscriptions	10	2022-01-21 10:42:23.849391+00	2022-01-21 10:42:23.849451+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Dues & Subscriptions"}	f
1443	ACCOUNTS_PAYABLE	Accounts Payable	Equipment Rental	29	2022-01-21 10:42:23.878825+00	2022-01-21 10:42:23.878884+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Equipment Rental"}	f
1444	ACCOUNTS_PAYABLE	Accounts Payable	Fees Billed	5	2022-01-21 10:42:23.879114+00	2022-01-21 10:42:23.879176+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Fees Billed"}	f
1445	ACCOUNTS_PAYABLE	Accounts Payable	Insurance	11	2022-01-21 10:42:23.880251+00	2022-01-21 10:42:23.881015+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Insurance"}	f
1446	ACCOUNTS_PAYABLE	Accounts Payable	Insurance:Workers Compensation	57	2022-01-21 10:42:23.881248+00	2022-01-21 10:42:23.881288+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Insurance:Workers Compensation"}	f
1447	ACCOUNTS_PAYABLE	Accounts Payable	Interest Earned	25	2022-01-21 10:42:23.882874+00	2022-01-21 10:42:23.882974+00	9	\N	{"account_type": "Other Income", "fully_qualified_name": "Interest Earned"}	f
1448	ACCOUNTS_PAYABLE	Accounts Payable	Inventory Asset	81	2022-01-21 10:42:23.884579+00	2022-01-21 10:42:23.961101+00	9	\N	{"account_type": "Other Current Asset", "fully_qualified_name": "Inventory Asset"}	f
1449	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses	58	2022-01-21 10:42:23.961553+00	2022-01-21 10:42:23.961838+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses"}	f
1450	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Cost of Labor	59	2022-01-21 10:42:23.962083+00	2022-01-21 10:42:23.962145+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Cost of Labor"}	f
1451	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Cost of Labor:Installation	60	2022-01-21 10:42:24.011875+00	2022-01-21 10:42:24.011927+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Cost of Labor:Installation"}	f
1452	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Cost of Labor:Maintenance and Repairs	61	2022-01-21 10:42:24.012025+00	2022-01-21 10:42:24.012059+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Cost of Labor:Maintenance and Repairs"}	f
1453	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Equipment Rental	62	2022-01-21 10:42:24.012235+00	2022-01-21 10:42:24.012269+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Equipment Rental"}	f
1454	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Job Materials	63	2022-01-21 10:42:24.012955+00	2022-01-21 10:42:24.01306+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials"}	f
1455	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Job Materials:Decks and Patios	64	2022-01-21 10:42:24.013173+00	2022-01-21 10:42:24.013205+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials:Decks and Patios"}	f
1456	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Job Materials:Fountain and Garden Lighting	65	2022-01-21 10:42:24.013492+00	2022-01-21 10:42:24.013559+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials:Fountain and Garden Lighting"}	f
1457	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Job Materials:Plants and Soil	66	2022-01-21 10:42:24.013809+00	2022-01-21 10:42:24.013875+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials:Plants and Soil"}	f
1458	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Job Materials:Sprinklers and Drip Systems	67	2022-01-21 10:42:24.015857+00	2022-01-21 10:42:24.015926+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials:Sprinklers and Drip Systems"}	f
1459	ACCOUNTS_PAYABLE	Accounts Payable	Job Expenses:Permits	68	2022-01-21 10:42:24.016141+00	2022-01-21 10:42:24.016252+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Permits"}	f
1460	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services	45	2022-01-21 10:42:24.016396+00	2022-01-21 10:42:24.01829+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services"}	f
1461	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services:Job Materials	46	2022-01-21 10:42:24.075201+00	2022-01-21 10:42:24.075275+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services:Job Materials"}	f
1462	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services:Job Materials:Decks and Patios	47	2022-01-21 10:42:24.075438+00	2022-01-21 10:42:24.075795+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services:Job Materials:Decks and Patios"}	f
1463	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services:Job Materials:Fountains and Garden Lighting	48	2022-01-21 10:42:24.075967+00	2022-01-21 10:42:24.076013+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services:Job Materials:Fountains and Garden Lighting"}	f
1464	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services:Job Materials:Plants and Soil	49	2022-01-21 10:42:24.076166+00	2022-01-21 10:42:24.076222+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services:Job Materials:Plants and Soil"}	f
1566	CUSTOMER	customer	Travis Waldron	26	2022-01-21 10:42:34.253055+00	2022-01-21 10:42:34.253086+00	9	\N	\N	f
1465	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services:Job Materials:Sprinklers and Drip Systems	50	2022-01-21 10:42:24.076501+00	2022-01-21 10:42:24.076547+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services:Job Materials:Sprinklers and Drip Systems"}	f
1466	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services:Labor	51	2022-01-21 10:42:24.076627+00	2022-01-21 10:42:24.076658+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services:Labor"}	f
1467	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services:Labor:Installation	52	2022-01-21 10:42:24.076729+00	2022-01-21 10:42:24.076759+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services:Labor:Installation"}	f
1468	ACCOUNTS_PAYABLE	Accounts Payable	Landscaping Services:Labor:Maintenance and Repair	53	2022-01-21 10:42:24.076829+00	2022-01-21 10:42:24.076859+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Landscaping Services:Labor:Maintenance and Repair"}	f
1469	ACCOUNTS_PAYABLE	Accounts Payable	Legal & Professional Fees	12	2022-01-21 10:42:24.076995+00	2022-01-21 10:42:24.077044+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Legal & Professional Fees"}	f
1470	ACCOUNTS_PAYABLE	Accounts Payable	Legal & Professional Fees:Accounting	69	2022-01-21 10:42:24.077185+00	2022-01-21 10:42:24.07722+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Legal & Professional Fees:Accounting"}	f
1471	ACCOUNTS_PAYABLE	Accounts Payable	Legal & Professional Fees:Bookkeeper	70	2022-01-21 10:42:24.080855+00	2022-01-21 10:42:24.080904+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Legal & Professional Fees:Bookkeeper"}	f
1472	ACCOUNTS_PAYABLE	Accounts Payable	Legal & Professional Fees:Lawyer	71	2022-01-21 10:42:24.081004+00	2022-01-21 10:42:24.081235+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Legal & Professional Fees:Lawyer"}	f
1473	ACCOUNTS_PAYABLE	Accounts Payable	Loan Payable	43	2022-01-21 10:42:24.081335+00	2022-01-21 10:42:24.145296+00	9	\N	{"account_type": "Other Current Liability", "fully_qualified_name": "Loan Payable"}	f
1474	ACCOUNTS_PAYABLE	Accounts Payable	Maintenance and Repair	72	2022-01-21 10:42:24.146552+00	2022-01-21 10:42:24.146604+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Maintenance and Repair"}	f
1475	ACCOUNTS_PAYABLE	Accounts Payable	Maintenance and Repair:Building Repairs	73	2022-01-21 10:42:24.146694+00	2022-01-21 10:42:24.146726+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Maintenance and Repair:Building Repairs"}	f
1476	ACCOUNTS_PAYABLE	Accounts Payable	Maintenance and Repair:Computer Repairs	74	2022-01-21 10:42:24.333648+00	2022-01-21 10:42:24.333727+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Maintenance and Repair:Computer Repairs"}	f
1477	ACCOUNTS_PAYABLE	Accounts Payable	Maintenance and Repair:Equipment Repairs	75	2022-01-21 10:42:24.333874+00	2022-01-21 10:42:24.333921+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Maintenance and Repair:Equipment Repairs"}	f
1478	ACCOUNTS_PAYABLE	Accounts Payable	Meals and Entertainment	13	2022-01-21 10:42:24.334051+00	2022-01-21 10:42:24.334097+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Meals and Entertainment"}	f
1479	ACCOUNTS_PAYABLE	Accounts Payable	Miscellaneous	14	2022-01-21 10:42:24.33601+00	2022-01-21 10:42:24.351759+00	9	\N	{"account_type": "Other Expense", "fully_qualified_name": "Miscellaneous"}	f
1480	ACCOUNTS_PAYABLE	Accounts Payable	Notes Payable	44	2022-01-21 10:42:24.351988+00	2022-01-21 10:42:24.352048+00	9	\N	{"account_type": "Long Term Liability", "fully_qualified_name": "Notes Payable"}	f
1481	ACCOUNTS_PAYABLE	Accounts Payable	Office Expenses	15	2022-01-21 10:42:24.352193+00	2022-01-21 10:42:24.352241+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Office Expenses"}	f
1482	ACCOUNTS_PAYABLE	Accounts Payable	Opening Balance Equity	34	2022-01-21 10:42:24.352364+00	2022-01-21 10:42:24.352406+00	9	\N	{"account_type": "Equity", "fully_qualified_name": "Opening Balance Equity"}	f
1483	ACCOUNTS_PAYABLE	Accounts Payable	Other Income	83	2022-01-21 10:42:24.35252+00	2022-01-21 10:42:24.352561+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Other Income"}	f
1484	ACCOUNTS_PAYABLE	Accounts Payable	Other Portfolio Income	26	2022-01-21 10:42:24.352669+00	2022-01-21 10:42:24.35271+00	9	\N	{"account_type": "Other Income", "fully_qualified_name": "Other Portfolio Income"}	f
1485	ACCOUNTS_PAYABLE	Accounts Payable	Out Of Scope Agency Payable	92	2022-01-21 10:42:24.352818+00	2022-01-21 10:42:24.352858+00	9	\N	{"account_type": "Other Current Liability", "fully_qualified_name": "Out Of Scope Agency Payable"}	f
1486	ACCOUNTS_PAYABLE	Accounts Payable	Penalties & Settlements	27	2022-01-21 10:42:24.352964+00	2022-01-21 10:42:24.353004+00	9	\N	{"account_type": "Other Expense", "fully_qualified_name": "Penalties & Settlements"}	f
1487	ACCOUNTS_PAYABLE	Accounts Payable	Pest Control Services	54	2022-01-21 10:42:24.360959+00	2022-01-21 10:42:24.36105+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Pest Control Services"}	f
1488	ACCOUNTS_PAYABLE	Accounts Payable	Prepaid Expenses	3	2022-01-21 10:42:24.362643+00	2022-01-21 10:42:24.380846+00	9	\N	{"account_type": "Other Current Asset", "fully_qualified_name": "Prepaid Expenses"}	f
1489	ACCOUNTS_PAYABLE	Accounts Payable	Promotional	16	2022-01-21 10:42:24.382121+00	2022-01-21 10:42:24.382315+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Promotional"}	f
1490	ACCOUNTS_PAYABLE	Accounts Payable	Purchases	78	2022-01-21 10:42:24.382876+00	2022-01-21 10:42:24.383719+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Purchases"}	f
1491	ACCOUNTS_PAYABLE	Accounts Payable	Refunds-Allowances	6	2022-01-21 10:42:24.383872+00	2022-01-21 10:42:24.38391+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Refunds-Allowances"}	f
1492	ACCOUNTS_PAYABLE	Accounts Payable	Rent or Lease	17	2022-01-21 10:42:24.384003+00	2022-01-21 10:42:24.384035+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Rent or Lease"}	f
1493	ACCOUNTS_PAYABLE	Accounts Payable	Retained Earnings	2	2022-01-21 10:42:24.384126+00	2022-01-21 10:42:24.384248+00	9	\N	{"account_type": "Equity", "fully_qualified_name": "Retained Earnings"}	f
1494	ACCOUNTS_PAYABLE	Accounts Payable	Sales of Product Income	79	2022-01-21 10:42:24.394713+00	2022-01-21 10:42:24.394784+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Sales of Product Income"}	f
1495	ACCOUNTS_PAYABLE	Accounts Payable	Services	1	2022-01-21 10:42:24.395131+00	2022-01-21 10:42:24.395275+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Services"}	f
1496	ACCOUNTS_PAYABLE	Accounts Payable	Stationery & Printing	19	2022-01-21 10:42:24.396164+00	2022-01-21 10:42:24.396214+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Stationery & Printing"}	f
1497	ACCOUNTS_PAYABLE	Accounts Payable	Supplies	20	2022-01-21 10:42:24.396324+00	2022-01-21 10:42:24.396357+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Supplies"}	f
1498	ACCOUNTS_PAYABLE	Accounts Payable	Taxes & Licenses	21	2022-01-21 10:42:24.396436+00	2022-01-21 10:42:24.396467+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Taxes & Licenses"}	f
1499	ACCOUNTS_PAYABLE	Accounts Payable	Travel	22	2022-01-21 10:42:24.396542+00	2022-01-21 10:42:24.396573+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Travel"}	f
1500	ACCOUNTS_PAYABLE	Accounts Payable	Travel Meals	23	2022-01-21 10:42:24.396647+00	2022-01-21 10:42:24.396677+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Travel Meals"}	f
1501	ACCOUNTS_PAYABLE	Accounts Payable	Truck	37	2022-01-21 10:42:24.396749+00	2022-01-21 10:42:24.396779+00	9	\N	{"account_type": "Fixed Asset", "fully_qualified_name": "Truck"}	f
1502	ACCOUNTS_PAYABLE	Accounts Payable	Truck:Depreciation	39	2022-01-21 10:42:24.396851+00	2022-01-21 10:42:24.396881+00	9	\N	{"account_type": "Fixed Asset", "fully_qualified_name": "Truck:Depreciation"}	f
1503	ACCOUNTS_PAYABLE	Accounts Payable	Truck:Original Cost	38	2022-01-21 10:42:24.396952+00	2022-01-21 10:42:24.397179+00	9	\N	{"account_type": "Fixed Asset", "fully_qualified_name": "Truck:Original Cost"}	f
1504	ACCOUNTS_PAYABLE	Accounts Payable	Unapplied Cash Bill Payment Expense	88	2022-01-21 10:42:24.397902+00	2022-01-21 10:42:24.403185+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Unapplied Cash Bill Payment Expense"}	f
1505	ACCOUNTS_PAYABLE	Accounts Payable	Unapplied Cash Payment Income	87	2022-01-21 10:42:24.427728+00	2022-01-21 10:42:24.427779+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Unapplied Cash Payment Income"}	f
1506	ACCOUNTS_PAYABLE	Accounts Payable	Uncategorized Asset	32	2022-01-21 10:42:24.428421+00	2022-01-21 10:42:24.428781+00	9	\N	{"account_type": "Other Current Asset", "fully_qualified_name": "Uncategorized Asset"}	f
1507	ACCOUNTS_PAYABLE	Accounts Payable	Uncategorized Expense	31	2022-01-21 10:42:24.428973+00	2022-01-21 10:42:24.429026+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Uncategorized Expense"}	f
1508	ACCOUNTS_PAYABLE	Accounts Payable	Uncategorized Income	30	2022-01-21 10:42:24.431037+00	2022-01-21 10:42:24.431081+00	9	\N	{"account_type": "Income", "fully_qualified_name": "Uncategorized Income"}	f
1509	ACCOUNTS_PAYABLE	Accounts Payable	Undeposited Funds	4	2022-01-21 10:42:24.431164+00	2022-01-21 10:42:24.431205+00	9	\N	{"account_type": "Other Current Asset", "fully_qualified_name": "Undeposited Funds"}	f
1510	ACCOUNTS_PAYABLE	Accounts Payable	Utilities	24	2022-01-21 10:42:24.431273+00	2022-01-21 10:42:24.431293+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Utilities"}	f
1511	ACCOUNTS_PAYABLE	Accounts Payable	Utilities:Gas and Electric	76	2022-01-21 10:42:24.431339+00	2022-01-21 10:42:24.431361+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Utilities:Gas and Electric"}	f
1512	ACCOUNTS_PAYABLE	Accounts Payable	Utilities:Telephone	77	2022-01-21 10:42:24.431431+00	2022-01-21 10:42:24.431462+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Utilities:Telephone"}	f
1513	EMPLOYEE	employee	Emily Platt	55	2022-01-21 10:42:27.186173+00	2022-01-21 10:42:27.18627+00	9	\N	{"email": null}	f
1514	EMPLOYEE	employee	John Johnson	54	2022-01-21 10:42:27.187154+00	2022-01-21 10:42:27.187343+00	9	\N	{"email": null}	f
1515	VENDOR	vendor	Bob's Burger Joint	56	2022-01-21 10:42:30.014331+00	2022-01-21 10:42:30.014378+00	9	\N	{"email": null}	f
1516	VENDOR	vendor	Books by Bessie	30	2022-01-21 10:42:30.014455+00	2022-01-21 10:42:30.014489+00	9	\N	{"email": "Books@Intuit.com"}	f
1517	VENDOR	vendor	Brosnahan Insurance Agency	31	2022-01-21 10:42:30.01456+00	2022-01-21 10:42:30.014589+00	9	\N	{"email": null}	f
1518	VENDOR	vendor	Cal Telephone	32	2022-01-21 10:42:30.014657+00	2022-01-21 10:42:30.014686+00	9	\N	{"email": null}	f
1519	VENDOR	vendor	Chin's Gas and Oil	33	2022-01-21 10:42:30.014753+00	2022-01-21 10:42:30.014783+00	9	\N	{"email": null}	f
1520	VENDOR	vendor	Cigna Health Care	34	2022-01-21 10:42:30.015162+00	2022-01-21 10:42:30.015213+00	9	\N	{"email": null}	f
1521	VENDOR	vendor	Computers by Jenni	35	2022-01-21 10:42:30.015306+00	2022-01-21 10:42:30.015338+00	9	\N	{"email": "Msfixit@Intuit.com"}	f
1522	VENDOR	vendor	Diego's Road Warrior Bodyshop	36	2022-01-21 10:42:30.015409+00	2022-01-21 10:42:30.01544+00	9	\N	{"email": null}	f
1523	VENDOR	vendor	EDD	37	2022-01-21 10:42:30.015512+00	2022-01-21 10:42:30.015542+00	9	\N	{"email": null}	f
1524	VENDOR	vendor	Ellis Equipment Rental	38	2022-01-21 10:42:30.01561+00	2022-01-21 10:42:30.015639+00	9	\N	{"email": "Rental@intuit.com"}	f
1525	VENDOR	vendor	Fidelity	39	2022-01-21 10:42:30.015707+00	2022-01-21 10:42:30.015737+00	9	\N	{"email": null}	f
1526	VENDOR	vendor	Hall Properties	40	2022-01-21 10:42:30.015803+00	2022-01-21 10:42:30.015832+00	9	\N	{"email": null}	f
1527	VENDOR	vendor	Hicks Hardware	41	2022-01-21 10:42:30.0159+00	2022-01-21 10:42:30.015929+00	9	\N	{"email": null}	f
1528	VENDOR	vendor	Lee Advertising	42	2022-01-21 10:42:30.016377+00	2022-01-21 10:42:30.016434+00	9	\N	{"email": null}	f
1529	VENDOR	vendor	Mahoney Mugs	43	2022-01-21 10:42:30.017294+00	2022-01-21 10:42:30.017446+00	9	\N	{"email": null}	f
1530	VENDOR	vendor	Met Life Dental	44	2022-01-21 10:42:30.018161+00	2022-01-21 10:42:30.018213+00	9	\N	{"email": null}	f
1531	VENDOR	vendor	National Eye Care	45	2022-01-21 10:42:30.018311+00	2022-01-21 10:42:30.018341+00	9	\N	{"email": "Nateyecare@intuit.com, pauliejones15@intuit.com"}	f
1532	VENDOR	vendor	Norton Lumber and Building Materials	46	2022-01-21 10:42:30.018412+00	2022-01-21 10:42:30.018441+00	9	\N	{"email": "Materials@intuit.com"}	f
1533	VENDOR	vendor	PG&E	48	2022-01-21 10:42:30.01851+00	2022-01-21 10:42:30.01854+00	9	\N	{"email": "utilities@noemail.com"}	f
1534	VENDOR	vendor	Pam Seitz	47	2022-01-21 10:42:30.018608+00	2022-01-21 10:42:30.018637+00	9	\N	{"email": "SeitzCPA@noemail.com"}	f
1535	VENDOR	vendor	Robertson & Associates	49	2022-01-21 10:42:30.018705+00	2022-01-21 10:42:30.018734+00	9	\N	{"email": null}	f
1536	VENDOR	vendor	Squeaky Kleen Car Wash	57	2022-01-21 10:42:30.018801+00	2022-01-21 10:42:30.01883+00	9	\N	{"email": null}	f
1537	VENDOR	vendor	Tania's Nursery	50	2022-01-21 10:42:30.018897+00	2022-01-21 10:42:30.018927+00	9	\N	{"email": "plantqueen@taniasnursery.com"}	f
1538	VENDOR	vendor	Tim Philip Masonry	51	2022-01-21 10:42:30.018994+00	2022-01-21 10:42:30.019023+00	9	\N	{"email": "tim.philip@timphilipmasonry.com"}	f
1539	VENDOR	vendor	Tony Rondonuwu	52	2022-01-21 10:42:30.019091+00	2022-01-21 10:42:30.01912+00	9	\N	{"email": "tonyrjr@intuit.com"}	f
1540	VENDOR	vendor	United States Treasury	53	2022-01-21 10:42:30.019188+00	2022-01-21 10:42:30.019217+00	9	\N	{"email": "taxesaregreat@intuit.com"}	f
1541	CUSTOMER	customer	Amy's Bird Sanctuary	1	2022-01-21 10:42:34.238684+00	2022-01-21 10:42:34.238769+00	9	\N	\N	f
1542	CUSTOMER	customer	Bill's Windsurf Shop	2	2022-01-21 10:42:34.243317+00	2022-01-21 10:42:34.243386+00	9	\N	\N	f
1543	CUSTOMER	customer	Cool Cars	3	2022-01-21 10:42:34.243671+00	2022-01-21 10:42:34.243711+00	9	\N	\N	f
1544	CUSTOMER	customer	Diego Rodriguez	4	2022-01-21 10:42:34.24394+00	2022-01-21 10:42:34.243978+00	9	\N	\N	f
1545	CUSTOMER	customer	Dukes Basketball Camp	5	2022-01-21 10:42:34.244177+00	2022-01-21 10:42:34.244219+00	9	\N	\N	f
1546	CUSTOMER	customer	Dylan Sollfrank	6	2022-01-21 10:42:34.2443+00	2022-01-21 10:42:34.244421+00	9	\N	\N	f
1547	CUSTOMER	customer	Freeman Sporting Goods	7	2022-01-21 10:42:34.245366+00	2022-01-21 10:42:34.24544+00	9	\N	\N	f
1548	CUSTOMER	customer	Freeman Sporting Goods:0969 Ocean View Road	8	2022-01-21 10:42:34.245704+00	2022-01-21 10:42:34.245754+00	9	\N	\N	f
1549	CUSTOMER	customer	Freeman Sporting Goods:55 Twin Lane	9	2022-01-21 10:42:34.245955+00	2022-01-21 10:42:34.245996+00	9	\N	\N	f
1550	CUSTOMER	customer	Geeta Kalapatapu	10	2022-01-21 10:42:34.246065+00	2022-01-21 10:42:34.246222+00	9	\N	\N	f
1551	CUSTOMER	customer	Gevelber Photography	11	2022-01-21 10:42:34.246294+00	2022-01-21 10:42:34.24634+00	9	\N	\N	f
1552	CUSTOMER	customer	Jeff's Jalopies	12	2022-01-21 10:42:34.249307+00	2022-01-21 10:42:34.249395+00	9	\N	\N	f
1553	CUSTOMER	customer	John Melton	13	2022-01-21 10:42:34.24988+00	2022-01-21 10:42:34.249967+00	9	\N	\N	f
1554	CUSTOMER	customer	Kate Whelan	14	2022-01-21 10:42:34.250195+00	2022-01-21 10:42:34.2503+00	9	\N	\N	f
1555	CUSTOMER	customer	Kookies by Kathy	16	2022-01-21 10:42:34.250442+00	2022-01-21 10:42:34.250478+00	9	\N	\N	f
1556	CUSTOMER	customer	Mark Cho	17	2022-01-21 10:42:34.250819+00	2022-01-21 10:42:34.250899+00	9	\N	\N	f
1557	CUSTOMER	customer	Paulsen Medical Supplies	18	2022-01-21 10:42:34.250972+00	2022-01-21 10:42:34.251002+00	9	\N	\N	f
1558	CUSTOMER	customer	Pye's Cakes	15	2022-01-21 10:42:34.251123+00	2022-01-21 10:42:34.251157+00	9	\N	\N	f
1559	CUSTOMER	customer	Rago Travel Agency	19	2022-01-21 10:42:34.251219+00	2022-01-21 10:42:34.251401+00	9	\N	\N	f
1560	CUSTOMER	customer	Red Rock Diner	20	2022-01-21 10:42:34.251478+00	2022-01-21 10:42:34.251964+00	9	\N	\N	f
1561	CUSTOMER	customer	Rondonuwu Fruit and Vegi	21	2022-01-21 10:42:34.252136+00	2022-01-21 10:42:34.252177+00	9	\N	\N	f
1562	CUSTOMER	customer	Shara Barnett	22	2022-01-21 10:42:34.252247+00	2022-01-21 10:42:34.252288+00	9	\N	\N	f
1563	CUSTOMER	customer	Shara Barnett:Barnett Design	23	2022-01-21 10:42:34.252348+00	2022-01-21 10:42:34.252377+00	9	\N	\N	f
1567	CUSTOMER	customer	Video Games by Dan	27	2022-01-21 10:42:34.253271+00	2022-01-21 10:42:34.253303+00	9	\N	\N	f
1568	CUSTOMER	customer	Wedding Planning by Whitney	28	2022-01-21 10:42:34.25371+00	2022-01-21 10:42:34.262243+00	9	\N	\N	f
1569	CUSTOMER	customer	Weiskopf Consulting	29	2022-01-21 10:42:34.282741+00	2022-01-21 10:42:34.283002+00	9	\N	\N	f
1570	ACCOUNT	Account	Advertising	7	2022-01-21 10:42:38.338801+00	2022-01-21 10:42:38.338848+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Advertising"}	f
1571	ACCOUNT	Account	Automobile	55	2022-01-21 10:42:38.338921+00	2022-01-21 10:42:38.338951+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Automobile"}	f
1572	ACCOUNT	Account	Automobile:Fuel	56	2022-01-21 10:42:38.339017+00	2022-01-21 10:42:38.339047+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Automobile:Fuel"}	f
1573	ACCOUNT	Account	Bank Charges	8	2022-01-21 10:42:38.339128+00	2022-01-21 10:42:38.339157+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Bank Charges"}	f
1574	ACCOUNT	Account	Commissions & fees	9	2022-01-21 10:42:38.339223+00	2022-01-21 10:42:38.339252+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Commissions & fees"}	f
1575	ACCOUNT	Account	Disposal Fees	28	2022-01-21 10:42:38.339317+00	2022-01-21 10:42:38.339346+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Disposal Fees"}	f
1576	ACCOUNT	Account	Dues & Subscriptions	10	2022-01-21 10:42:38.339411+00	2022-01-21 10:42:38.339441+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Dues & Subscriptions"}	f
1577	ACCOUNT	Account	Equipment Rental	29	2022-01-21 10:42:38.339506+00	2022-01-21 10:42:38.339535+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Equipment Rental"}	f
1578	ACCOUNT	Account	Insurance	11	2022-01-21 10:42:38.3396+00	2022-01-21 10:42:38.339628+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Insurance"}	f
1579	ACCOUNT	Account	Insurance:Workers Compensation	57	2022-01-21 10:42:38.339694+00	2022-01-21 10:42:38.339723+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Insurance:Workers Compensation"}	f
1580	ACCOUNT	Account	Job Expenses	58	2022-01-21 10:42:38.339788+00	2022-01-21 10:42:38.339817+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses"}	f
1581	ACCOUNT	Account	Job Expenses:Cost of Labor	59	2022-01-21 10:42:38.339883+00	2022-01-21 10:42:38.339912+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Cost of Labor"}	f
1582	ACCOUNT	Account	Job Expenses:Cost of Labor:Installation	60	2022-01-21 10:42:38.339977+00	2022-01-21 10:42:38.340006+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Cost of Labor:Installation"}	f
1583	ACCOUNT	Account	Job Expenses:Cost of Labor:Maintenance and Repairs	61	2022-01-21 10:42:38.340071+00	2022-01-21 10:42:38.3401+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Cost of Labor:Maintenance and Repairs"}	f
1584	ACCOUNT	Account	Job Expenses:Equipment Rental	62	2022-01-21 10:42:38.340165+00	2022-01-21 10:42:38.340195+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Equipment Rental"}	f
1585	ACCOUNT	Account	Job Expenses:Job Materials	63	2022-01-21 10:42:38.340261+00	2022-01-21 10:42:38.340479+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials"}	f
1586	ACCOUNT	Account	Job Expenses:Job Materials:Decks and Patios	64	2022-01-21 10:42:38.340556+00	2022-01-21 10:42:38.340585+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials:Decks and Patios"}	f
1587	ACCOUNT	Account	Job Expenses:Job Materials:Fountain and Garden Lighting	65	2022-01-21 10:42:38.340665+00	2022-01-21 10:42:38.340694+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials:Fountain and Garden Lighting"}	f
1588	ACCOUNT	Account	Job Expenses:Job Materials:Plants and Soil	66	2022-01-21 10:42:38.340761+00	2022-01-21 10:42:38.340791+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials:Plants and Soil"}	f
1589	ACCOUNT	Account	Job Expenses:Job Materials:Sprinklers and Drip Systems	67	2022-01-21 10:42:38.340857+00	2022-01-21 10:42:38.340887+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Job Materials:Sprinklers and Drip Systems"}	f
1590	ACCOUNT	Account	Job Expenses:Permits	68	2022-01-21 10:42:38.340953+00	2022-01-21 10:42:38.340983+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Job Expenses:Permits"}	f
1591	ACCOUNT	Account	Legal & Professional Fees	12	2022-01-21 10:42:38.34105+00	2022-01-21 10:42:38.34108+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Legal & Professional Fees"}	f
1592	ACCOUNT	Account	Legal & Professional Fees:Accounting	69	2022-01-21 10:42:38.341146+00	2022-01-21 10:42:38.341175+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Legal & Professional Fees:Accounting"}	f
1593	ACCOUNT	Account	Legal & Professional Fees:Bookkeeper	70	2022-01-21 10:42:38.34124+00	2022-01-21 10:42:38.34127+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Legal & Professional Fees:Bookkeeper"}	f
1594	ACCOUNT	Account	Legal & Professional Fees:Lawyer	71	2022-01-21 10:42:38.341336+00	2022-01-21 10:42:38.341365+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Legal & Professional Fees:Lawyer"}	f
1595	ACCOUNT	Account	Maintenance and Repair	72	2022-01-21 10:42:38.341442+00	2022-01-21 10:42:38.341472+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Maintenance and Repair"}	f
1596	ACCOUNT	Account	Maintenance and Repair:Building Repairs	73	2022-01-21 10:42:38.341545+00	2022-01-21 10:42:38.341575+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Maintenance and Repair:Building Repairs"}	f
1597	ACCOUNT	Account	Maintenance and Repair:Computer Repairs	74	2022-01-21 10:42:38.342252+00	2022-01-21 10:42:38.342338+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Maintenance and Repair:Computer Repairs"}	f
1598	ACCOUNT	Account	Maintenance and Repair:Equipment Repairs	75	2022-01-21 10:42:38.342824+00	2022-01-21 10:42:38.342864+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Maintenance and Repair:Equipment Repairs"}	f
1599	ACCOUNT	Account	Meals and Entertainment	13	2022-01-21 10:42:38.342986+00	2022-01-21 10:42:38.343027+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Meals and Entertainment"}	f
1600	ACCOUNT	Account	Office Expenses	15	2022-01-21 10:42:38.343242+00	2022-01-21 10:42:38.343292+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Office Expenses"}	f
1601	ACCOUNT	Account	Promotional	16	2022-01-21 10:42:38.343725+00	2022-01-21 10:42:38.34378+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Promotional"}	f
1602	ACCOUNT	Account	Purchases	78	2022-01-21 10:42:38.344126+00	2022-01-21 10:42:38.344183+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Purchases"}	f
1603	ACCOUNT	Account	Rent or Lease	17	2022-01-21 10:42:38.34435+00	2022-01-21 10:42:38.344405+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Rent or Lease"}	f
1604	ACCOUNT	Account	Stationery & Printing	19	2022-01-21 10:42:38.344729+00	2022-01-21 10:42:38.344784+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Stationery & Printing"}	f
1605	ACCOUNT	Account	Supplies	20	2022-01-21 10:42:38.344947+00	2022-01-21 10:42:38.344998+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Supplies"}	f
1606	ACCOUNT	Account	Taxes & Licenses	21	2022-01-21 10:42:38.345164+00	2022-01-21 10:42:38.345208+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Taxes & Licenses"}	f
1607	ACCOUNT	Account	Travel	22	2022-01-21 10:42:38.345344+00	2022-01-21 10:42:38.34539+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Travel"}	f
1608	ACCOUNT	Account	Travel Meals	23	2022-01-21 10:42:38.345524+00	2022-01-21 10:42:38.345572+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Travel Meals"}	f
1940	EMPLOYEE	employee	Eren  Yeager	121	2022-01-28 10:12:38.844934+00	2022-01-28 10:12:38.84499+00	8	\N	{"email": null}	f
1609	ACCOUNT	Account	Unapplied Cash Bill Payment Expense	88	2022-01-21 10:42:38.345921+00	2022-01-21 10:42:38.345994+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Unapplied Cash Bill Payment Expense"}	f
1610	ACCOUNT	Account	Uncategorized Expense	31	2022-01-21 10:42:38.346141+00	2022-01-21 10:42:38.346193+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Uncategorized Expense"}	f
1611	ACCOUNT	Account	Utilities	24	2022-01-21 10:42:38.346344+00	2022-01-21 10:42:38.346403+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Utilities"}	f
1612	ACCOUNT	Account	Utilities:Gas and Electric	76	2022-01-21 10:42:38.346546+00	2022-01-21 10:42:38.349198+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Utilities:Gas and Electric"}	f
1613	ACCOUNT	Account	Utilities:Telephone	77	2022-01-21 10:42:38.349402+00	2022-01-21 10:42:38.349457+00	9	\N	{"account_type": "Expense", "fully_qualified_name": "Utilities:Telephone"}	f
1614	TAX_CODE	Tax Code	Out of scope @0%	4	2022-01-21 10:42:39.726257+00	2022-01-21 10:42:39.726319+00	9	\N	{"tax_rate": 0, "tax_refs": [{"name": "NO TAX PURCHASE", "value": "5"}]}	f
1615	VENDOR	vendor	Credit Card Misc	58	2022-01-21 10:45:34.818483+00	2022-01-21 16:53:58.941658+00	9	\N	{"email": null}	f
1616	VENDOR	vendor	test Sharma	59	2022-01-23 08:32:41.72086+00	2022-01-23 08:32:41.720905+00	9	\N	{"email": "test@fyle.in"}	f
1941	CREDIT_CARD_ACCOUNT	Credit Card Account	QBO CCC Support Account	130	2022-02-01 07:56:49.993188+00	2022-02-01 07:56:49.993237+00	8	\N	{"account_type": "Credit Card", "fully_qualified_name": "QBO CCC Support Account"}	f
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	contenttypes	contenttype
5	sessions	session
6	fyle_rest_auth	authtoken
7	fyle_accounting_mappings	destinationattribute
8	fyle_accounting_mappings	expenseattribute
9	fyle_accounting_mappings	mappingsetting
10	fyle_accounting_mappings	mapping
11	fyle_accounting_mappings	employeemapping
12	fyle_accounting_mappings	categorymapping
13	django_q	schedule
14	django_q	task
15	django_q	failure
16	django_q	success
17	django_q	ormq
18	users	user
19	workspaces	workspace
20	workspaces	workspaceschedule
21	workspaces	qbocredential
22	workspaces	fylecredential
23	workspaces	workspacegeneralsettings
24	mappings	generalmapping
25	fyle	expense
26	fyle	expensegroup
27	fyle	expensegroupsettings
28	fyle	reimbursement
29	quickbooks_online	bill
30	quickbooks_online	billlineitem
31	quickbooks_online	cheque
32	quickbooks_online	creditcardpurchase
33	quickbooks_online	journalentry
34	quickbooks_online	journalentrylineitem
35	quickbooks_online	creditcardpurchaselineitem
36	quickbooks_online	chequelineitem
37	quickbooks_online	billpayment
38	quickbooks_online	billpaymentlineitem
39	quickbooks_online	qboexpense
40	quickbooks_online	qboexpenselineitem
41	tasks	tasklog
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	users	0001_initial	2021-12-19 02:49:15.85686+00
2	contenttypes	0001_initial	2021-12-19 02:49:15.89764+00
3	admin	0001_initial	2021-12-19 02:49:15.929644+00
4	admin	0002_logentry_remove_auto_add	2021-12-19 02:49:15.962543+00
5	admin	0003_logentry_add_action_flag_choices	2021-12-19 02:49:15.97291+00
6	contenttypes	0002_remove_content_type_name	2021-12-19 02:49:16.012201+00
7	auth	0001_initial	2021-12-19 02:49:16.087551+00
8	auth	0002_alter_permission_name_max_length	2021-12-19 02:49:16.153636+00
9	auth	0003_alter_user_email_max_length	2021-12-19 02:49:16.174064+00
10	auth	0004_alter_user_username_opts	2021-12-19 02:49:16.188449+00
11	auth	0005_alter_user_last_login_null	2021-12-19 02:49:16.199504+00
12	auth	0006_require_contenttypes_0002	2021-12-19 02:49:16.204132+00
13	auth	0007_alter_validators_add_error_messages	2021-12-19 02:49:16.216237+00
14	auth	0008_alter_user_username_max_length	2021-12-19 02:49:16.229577+00
15	auth	0009_alter_user_last_name_max_length	2021-12-19 02:49:16.273919+00
16	auth	0010_alter_group_name_max_length	2021-12-19 02:49:16.288621+00
17	auth	0011_update_proxy_permissions	2021-12-19 02:49:16.302486+00
18	auth	0012_alter_user_first_name_max_length	2021-12-19 02:49:16.315485+00
19	django_q	0001_initial	2021-12-19 02:49:16.357695+00
20	django_q	0002_auto_20150630_1624	2021-12-19 02:49:16.372693+00
21	django_q	0003_auto_20150708_1326	2021-12-19 02:49:16.398523+00
22	django_q	0004_auto_20150710_1043	2021-12-19 02:49:16.418385+00
23	django_q	0005_auto_20150718_1506	2021-12-19 02:49:16.434986+00
24	django_q	0006_auto_20150805_1817	2021-12-19 02:49:16.449393+00
25	django_q	0007_ormq	2021-12-19 02:49:16.47001+00
26	django_q	0008_auto_20160224_1026	2021-12-19 02:49:16.479667+00
27	django_q	0009_auto_20171009_0915	2021-12-19 02:49:16.498462+00
28	django_q	0010_auto_20200610_0856	2021-12-19 02:49:16.514503+00
29	django_q	0011_auto_20200628_1055	2021-12-19 02:49:16.526939+00
30	django_q	0012_auto_20200702_1608	2021-12-19 02:49:16.535599+00
31	django_q	0013_task_attempt_count	2021-12-19 02:49:16.547997+00
32	workspaces	0001_initial	2021-12-19 02:49:16.681132+00
33	workspaces	0002_workspacegeneralsettings	2021-12-19 02:49:16.749057+00
34	workspaces	0003_auto_20200506_0739	2021-12-19 02:49:16.825186+00
35	workspaces	0004_workspacegeneralsettings_import_projects	2021-12-19 02:49:16.847123+00
36	workspaces	0005_workspacegeneralsettings_import_categories	2021-12-19 02:49:16.864616+00
37	workspaces	0006_auto_20201228_0436	2021-12-19 02:49:16.935376+00
38	fyle	0001_initial	2021-12-19 02:49:17.01166+00
39	fyle	0002_auto_20200420_0434	2021-12-19 02:49:17.108379+00
40	fyle	0003_auto_20200626_1401	2021-12-19 02:49:17.146308+00
41	fyle	0004_expensegroupsettings	2021-12-19 02:49:17.199104+00
42	fyle	0005_auto_20200819_1419	2021-12-19 02:49:17.245946+00
43	fyle	0006_auto_20200825_0631	2021-12-19 02:49:17.302832+00
44	fyle	0007_auto_20200827_0609	2021-12-19 02:49:17.334721+00
45	fyle	0008_auto_20200901_1038	2021-12-19 02:49:17.386001+00
46	fyle	0009_auto_20200929_0717	2021-12-19 02:49:17.461509+00
47	fyle	0010_auto_20201007_0826	2021-12-19 02:49:17.513168+00
48	fyle	0011_expensegroup_exported_at	2021-12-19 02:49:17.544934+00
49	fyle	0012_expense_billable	2021-12-19 02:49:17.558874+00
50	fyle	0013_auto_20201221_0748	2021-12-19 02:49:17.613651+00
51	fyle	0014_auto_20210120_1831	2021-12-19 02:49:17.671565+00
52	fyle	0015_expense_org_id	2021-12-19 02:49:17.698493+00
53	fyle	0016_expensegroup_response_logs	2021-12-19 02:49:17.721903+00
54	fyle	0017_expensegroupsettings_import_card_credits	2021-12-19 02:49:17.743172+00
55	fyle	0018_auto_20210830_0925	2021-12-19 02:49:17.764173+00
56	fyle	0019_auto_20211108_0422	2021-12-19 02:49:17.792595+00
57	fyle	0020_auto_20211206_0851	2021-12-19 02:49:17.866519+00
58	fyle	0021_auto_20211210_0726	2021-12-19 02:49:17.91809+00
59	fyle_accounting_mappings	0001_initial	2021-12-19 02:49:18.069317+00
60	fyle_accounting_mappings	0002_auto_20201117_0655	2021-12-19 02:49:18.175963+00
61	fyle_accounting_mappings	0003_auto_20201221_1244	2021-12-19 02:49:18.31247+00
62	fyle_accounting_mappings	0004_auto_20210127_1241	2021-12-19 02:49:18.353412+00
63	fyle_accounting_mappings	0005_expenseattribute_auto_mapped	2021-12-19 02:49:18.37882+00
64	fyle_accounting_mappings	0006_auto_20210305_0827	2021-12-19 02:49:18.42457+00
65	fyle_accounting_mappings	0007_auto_20210409_1931	2021-12-19 02:49:18.47885+00
66	fyle_accounting_mappings	0008_auto_20210604_0713	2021-12-19 02:49:18.579431+00
67	fyle_accounting_mappings	0009_auto_20210618_1004	2021-12-19 02:49:18.611904+00
68	fyle_accounting_mappings	0010_remove_mappingsetting_expense_field_id	2021-12-19 02:49:18.637136+00
69	fyle_accounting_mappings	0011_categorymapping_employeemapping	2021-12-19 02:49:18.734359+00
70	fyle_accounting_mappings	0012_auto_20211206_0600	2021-12-19 02:49:18.835461+00
71	fyle_rest_auth	0001_initial	2021-12-19 02:49:18.878435+00
72	fyle_rest_auth	0002_auto_20200101_1205	2021-12-19 02:49:18.935525+00
73	fyle_rest_auth	0003_auto_20200107_0921	2021-12-19 02:49:18.979596+00
74	fyle_rest_auth	0004_auto_20200107_1345	2021-12-19 02:49:19.033879+00
75	fyle_rest_auth	0005_remove_authtoken_access_token	2021-12-19 02:49:19.04855+00
76	fyle_rest_auth	0006_auto_20201221_0849	2021-12-19 02:49:19.062108+00
77	mappings	0001_initial	2021-12-19 02:49:19.209781+00
78	mappings	0002_auto_20200420_0434	2021-12-19 02:49:19.474919+00
79	mappings	0003_auto_20200930_0738	2021-12-19 02:49:19.536931+00
80	mappings	0004_auto_20201221_0748	2021-12-19 02:49:19.61884+00
81	mappings	0005_auto_20210120_1851	2021-12-19 02:49:19.689113+00
82	mappings	0006_auto_20210504_1913	2021-12-19 02:49:19.749448+00
83	mappings	0007_auto_20210722_1446	2021-12-19 02:49:19.903641+00
84	mappings	0008_auto_20210908_0617	2021-12-19 02:49:19.954038+00
85	quickbooks_online	0001_initial	2021-12-19 02:49:20.058442+00
86	quickbooks_online	0002_cheque_chequelineitem_creditcardpurchase_creditcardpurchaselineitem_journalentry_journalentrylineite	2021-12-19 02:49:20.508551+00
87	quickbooks_online	0003_auto_20200421_1033	2021-12-19 02:49:20.714982+00
88	quickbooks_online	0004_auto_20200707_1534	2021-12-19 02:49:20.806066+00
89	quickbooks_online	0005_auto_20201119_0947	2021-12-19 02:49:20.85851+00
90	quickbooks_online	0006_auto_20201120_0718	2021-12-19 02:49:20.924463+00
91	quickbooks_online	0007_auto_20201221_0748	2021-12-19 02:49:21.05343+00
92	quickbooks_online	0008_auto_20210120_1831	2021-12-19 02:49:21.221531+00
93	quickbooks_online	0009_remove_billpaymentlineitem_expense	2021-12-19 02:49:21.284661+00
94	quickbooks_online	0010_qboexpense_qboexpenselineitem	2021-12-19 02:49:21.413584+00
95	quickbooks_online	0011_auto_20210722_1446	2021-12-19 02:49:21.563372+00
96	quickbooks_online	0012_auto_20210830_1239	2021-12-19 02:49:21.736094+00
97	sessions	0001_initial	2021-12-19 02:49:21.757328+00
98	tasks	0001_initial	2021-12-19 02:49:21.834586+00
99	tasks	0002_auto_20200420_0434	2021-12-19 02:49:22.047167+00
100	tasks	0003_auto_20201221_0748	2021-12-19 02:49:22.107283+00
101	tasks	0004_tasklog_bill_payment	2021-12-19 02:49:22.169903+00
102	tasks	0005_tasklog_qbo_expense	2021-12-19 02:49:22.236655+00
103	tasks	0006_tasklog_quickbooks_errors	2021-12-19 02:49:22.285444+00
104	tasks	0007_auto_20211206_0851	2021-12-19 02:49:22.45153+00
105	users	0002_auto_20201228_0715	2021-12-19 02:49:22.46423+00
106	workspaces	0007_auto_20210120_1851	2021-12-19 02:49:22.521685+00
107	workspaces	0008_auto_20210215_1055	2021-12-19 02:49:22.649207+00
108	workspaces	0009_workspacegeneralsettings_auto_map_employees	2021-12-19 02:49:22.684805+00
109	workspaces	0010_workspacegeneralsettings_category_sync_version	2021-12-19 02:49:22.719096+00
110	workspaces	0011_workspacegeneralsettings_auto_create_detination_entity	2021-12-19 02:49:22.7515+00
111	workspaces	0012_workspacegeneralsettings_map_merchant_to_vendor	2021-12-19 02:49:22.782434+00
112	workspaces	0013_auto_20210428_0855	2021-12-19 02:49:22.841992+00
113	workspaces	0014_workspacegeneralsettings_je_single_credit_line	2021-12-19 02:49:22.872877+00
114	workspaces	0015_workspacegeneralsettings_change_accounting_period	2021-12-19 02:49:22.906697+00
115	workspaces	0016_auto_20210917_1035	2021-12-19 02:49:22.99116+00
116	workspaces	0017_workspace_cluster_domain	2021-12-19 02:49:23.024348+00
117	workspaces	0018_workspacegeneralsettings_charts_of_accounts	2021-12-19 02:49:23.063038+00
118	workspaces	0019_workspacegeneralsettings_memo_structure	2022-01-04 06:41:18.004555+00
119	fyle	0022_expense_file_ids	2022-02-01 06:32:58.821939+00
120	fyle	0023_expense_corporate_card_id	2022-02-01 06:32:58.901086+00
121	workspaces	0020_fylecredential_cluster_domain	2022-02-01 06:32:58.982929+00
122	workspaces	0021_workspacegeneralsettings_map_fyle_cards_qbo_account	2022-02-01 06:32:59.202384+00
123	workspaces	0022_workspacegeneralsettings_skip_cards_mapping	2022-02-02 11:15:57.170023+00
124	mappings	0009_auto_20220215_0843	2022-02-21 08:34:21.255745+00
\.


--
-- Data for Name: django_q_ormq; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_q_ormq (id, key, payload, lock) FROM stdin;
\.


--
-- Data for Name: django_q_schedule; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_q_schedule (id, func, hook, args, kwargs, schedule_type, repeats, next_run, task, name, minutes, cron) FROM stdin;
\.


--
-- Data for Name: django_q_task; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_q_task (name, func, hook, args, kwargs, result, started, stopped, success, id, "group", attempt_count) FROM stdin;
batman-venus-glucose-uncle	apps.quickbooks_online.tasks.async_sync_accounts	\N	gASVBQAAAAAAAABLAoWULg==	gAR9lC4=	\N	2022-01-12 10:26:00.21019+00	2022-01-12 10:26:06.457816+00	t	a33231b267dd4b1aa7293de79dd02088	\N	1
social-violet-pizza-louisiana	apps.mappings.tasks.auto_create_expense_fields_mappings	\N	gASVIAAAAAAAAABLAowKREVQQVJUTUVOVJSMC0RFUEFSVE1FTlRTlIeULg==	gAR9lC4=	\N	2022-01-12 10:27:33.177158+00	2022-01-12 10:27:35.528178+00	t	aeff0e93a2c24dc284a59607e085425a	\N	1
east-fifteen-thirteen-carbon	apps.mappings.tasks.auto_create_expense_fields_mappings	\N	gASVFQAAAAAAAABLAowFQ0xBU1OUjAVDTEFTU5SHlC4=	gAR9lC4=	\N	2022-01-12 10:27:31.86691+00	2022-01-12 10:27:36.246807+00	t	f3f1241e8cf54973b591689209021b0f	\N	1
pasta-skylark-angel-south	apps.quickbooks_online.tasks.async_sync_accounts	\N	gASVBQAAAAAAAABLBIWULg==	gAR9lC4=	\N	2022-01-19 09:42:52.97412+00	2022-01-19 09:42:59.23222+00	t	8b30b7a1cffa4ab5ad3af163abbf8a51	\N	1
july-eight-butter-cola	apps.fyle.tasks.create_expense_groups	\N	gASVSwIAAAAAAABLBF2UKIwIUEVSU09OQUyUjANDQ0OUZYwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoA4wKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAJkYpSMB2RlZmF1bHSUjAZhZGRpbmeUiXVijAJpZJRLAYwMd29ya3NwYWNlX2lklEsEjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBEwwxAg6xgZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoK0MKB+YBEwwxBQnvX5RoMIaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YoeULg==	gAR9lC4=	gASVawIAAAAAAACMEnBpY2tsZWZpZWxkLmZpZWxkc5SMDl9PYmplY3RXcmFwcGVylJOUKYGUTn2UjARfb2JqlIwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoBowKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAJkYpSMB2RlZmF1bHSUjAZhZGRpbmeUiXVijAJpZJRLAYwMd29ya3NwYWNlX2lklEsEjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBEwwxAg6xgZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoLkMKB+YBEwwxBQnvX5RoM4aUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnOGlGIu	2022-01-19 12:49:03.004596+00	2022-01-19 12:49:05.658787+00	t	360ec6934e574c6e907a8b7cb38fdfcb	\N	1
hawaii-summer-steak-triple	apps.quickbooks_online.tasks.create_credit_card_purchase	\N	gASVuAgAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMEmNyZWRpdGNhcmRwdXJjaGFzZZRoAowRcXVpY2tib29rc19vbmxpbmWUjBJDcmVkaXRDYXJkUHVyY2hhc2WUhpSFlFKUfZQojAZfc3RhdGWUaAspgZR9lCiMAmRilIwHZGVmYXVsdJRoDn2UjA1leHBlbnNlX2dyb3VwlGgHc4wGYWRkaW5nlIl1YowCaWSUSwGMEGV4cGVuc2VfZ3JvdXBfaWSUSwGMDmNjY19hY2NvdW50X2lklIwCNDGUjAllbnRpdHlfaWSUjAI5M5SMDWRlcGFydG1lbnRfaWSUTowQdHJhbnNhY3Rpb25fZGF0ZZSMCjIwMjItMDEtMTmUjAhjdXJyZW5jeZSMA1VTRJSMDHByaXZhdGVfbm90ZZSMNkNyZWRpdCBjYXJkIGV4cGVuc2UgYnkgYXNod2luLnRAZnlsZS5pbiBvbiAyMDIyLTAxLTE5IJSMG2NyZWRpdF9jYXJkX3B1cmNoYXNlX251bWJlcpSMDUUvMjAyMi8wMS9ULzKUjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBEwwxEwKihJSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwKdXBkYXRlZF9hdJRoMUMKB+YBEwwxEwKiwJRoNoaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnNoHoloGowHZGVmYXVsdJR1YowCaWSUSwGMDHdvcmtzcGFjZV9pZJRLBIwLZnVuZF9zb3VyY2WUjANDQ0OUjAtkZXNjcmlwdGlvbpR9lCiMCXJlcG9ydF9pZJSMDHJwS0pBR1hENmw3UJSMCmV4cGVuc2VfaWSUjAx0eHVlQUVMUDZCTWaUjAtmdW5kX3NvdXJjZZSMA0NDQ5SMDGNsYWltX251bWJlcpSMDUMvMjAyMi8wMS9SLzKUjA5lbXBsb3llZV9lbWFpbJSMEGFzaHdpbi50QGZ5bGUuaW6UjAhzcGVudF9hdJRoJ3WMDXJlc3BvbnNlX2xvZ3OUfZQojAhQdXJjaGFzZZR9lCiMCkFjY291bnRSZWaUfZQojAV2YWx1ZZSMAjQxlIwEbmFtZZSMCk1hc3RlcmNhcmSUdYwLUGF5bWVudFR5cGWUjApDcmVkaXRDYXJklIwJRW50aXR5UmVmlH2UKGhXjAI5M5RoWYwQQ3JlZGl0IENhcmQgTWlzY5SMBHR5cGWUjAZWZW5kb3KUdYwGQ3JlZGl0lImMCFRvdGFsQW10lEdAOQAAAAAAAIwKUHVyY2hhc2VFeJR9lIwDYW55lF2UfZQoaFmMLntodHRwOi8vc2NoZW1hLmludHVpdC5jb20vZmluYW5jZS92M31OYW1lVmFsdWWUjAxkZWNsYXJlZFR5cGWUjCZjb20uaW50dWl0LnNjaGVtYS5maW5hbmNlLnYzLk5hbWVWYWx1ZZSMBXNjb3BllIwmamF2YXgueG1sLmJpbmQuSkFYQkVsZW1lbnQkR2xvYmFsU2NvcGWUaFd9lCiMBE5hbWWUjAdUeG5UeXBllIwFVmFsdWWUjAI1NJR1jANuaWyUiYwLZ2xvYmFsU2NvcGWUiIwPdHlwZVN1YnN0aXR1dGVklIl1YXOMBmRvbWFpbpSMA1FCT5SMBnNwYXJzZZSJjAJJZJSMBDE5NTiUjAlTeW5jVG9rZW6UjAEwlIwITWV0YURhdGGUfZQojApDcmVhdGVUaW1llIwZMjAyMi0wMS0xOVQwNDo0OToyMS0wODowMJSMD0xhc3RVcGRhdGVkVGltZZSMGTIwMjItMDEtMTlUMDQ6NDk6MjEtMDg6MDCUdYwLQ3VzdG9tRmllbGSUXZSMCURvY051bWJlcpSMDUUvMjAyMi8wMS9ULzKUjAdUeG5EYXRllIwKMjAyMi0wMS0xOZSMC0N1cnJlbmN5UmVmlH2UKGhXjANVU0SUaFmMFFVuaXRlZCBTdGF0ZXMgRG9sbGFylHWMC1ByaXZhdGVOb3RllIw1Q3JlZGl0IGNhcmQgZXhwZW5zZSBieSBhc2h3aW4udEBmeWxlLmluIG9uIDIwMjItMDEtMTmUjARMaW5llF2UfZQoaHqMATGUjAtEZXNjcmlwdGlvbpSMmWFzaHdpbi50QGZ5bGUuaW4gLSBUcmF2ZWwgLSAyMDIyLTAxLTE5IC0gQy8yMDIyLzAxL1IvMiAtICAtIGh0dHBzOi8vc3RhZ2luZy5meWxlLnRlY2gvYXBwL21haW4vIy9lbnRlcnByaXNlL3ZpZXdfZXhwZW5zZS90eHVlQUVMUDZCTWY/b3JnX2lkPW9yR2NCQ1ZQaWpqT5SMBkFtb3VudJRHQDkAAAAAAACMCkRldGFpbFR5cGWUjB1BY2NvdW50QmFzZWRFeHBlbnNlTGluZURldGFpbJSMHUFjY291bnRCYXNlZEV4cGVuc2VMaW5lRGV0YWlslH2UKGhVfZQoaFeMATiUaFmMDEJhbmsgQ2hhcmdlc5R1jA5CaWxsYWJsZVN0YXR1c5SMC05vdEJpbGxhYmxllIwKVGF4Q29kZVJlZpR9lGhXjANOT06Uc3V1YXWMBHRpbWWUjB0yMDIyLTAxLTE5VDA0OjQ5OjIxLjU2MS0wODowMJR1jApjcmVhdGVkX2F0lGgxQwoH5gETDDEFCYY+lGg2hpRSlIwLZXhwb3J0ZWRfYXSUaDFDCgfmARMMMRUPNkqUhZRSlIwKdXBkYXRlZF9hdJRoMUMKB+YBEwwxFQ88RpRoNoaUUpSMD19kamFuZ29fdmVyc2lvbpRoPnViSwKGlC4=	gAR9lC4=	\N	2022-01-19 12:49:13.201711+00	2022-01-19 12:49:22.554032+00	t	988dc18fb9b6459cace4039f42784d96	44f483ca9e534964967aadc0741b84d9	1
spaghetti-mountain-red-thirteen	apps.fyle.tasks.create_expense_groups	\N	gASVSwIAAAAAAABLBF2UKIwIUEVSU09OQUyUjANDQ0OUZYwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoA4wKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAZhZGRpbmeUiYwCZGKUjAdkZWZhdWx0lHVijAJpZJRLAYwMd29ya3NwYWNlX2lklEsEjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBEwwxAg6xgZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoK0MKB+YBEw0BJQIdPpRoMIaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YoeULg==	gAR9lC4=	gASVawIAAAAAAACMEnBpY2tsZWZpZWxkLmZpZWxkc5SMDl9PYmplY3RXcmFwcGVylJOUKYGUTn2UjARfb2JqlIwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoBowKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAZhZGRpbmeUiYwCZGKUjAdkZWZhdWx0lHVijAJpZJRLAYwMd29ya3NwYWNlX2lklEsEjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBEwwxAg6xgZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoLkMKB+YBEw0BJQIdPpRoM4aUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnOGlGIu	2022-01-19 13:01:34.581576+00	2022-01-19 13:01:37.143197+00	t	4a511cd7aa46423aa63c270544ea95e5	\N	1
wolfram-november-jersey-violet	apps.quickbooks_online.tasks.create_credit_card_purchase	\N	gASVuAgAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMEmNyZWRpdGNhcmRwdXJjaGFzZZRoAowRcXVpY2tib29rc19vbmxpbmWUjBJDcmVkaXRDYXJkUHVyY2hhc2WUhpSFlFKUfZQojAZfc3RhdGWUaAspgZR9lCiMAmRilIwHZGVmYXVsdJRoDn2UjA1leHBlbnNlX2dyb3VwlGgHc4wGYWRkaW5nlIl1YowCaWSUSwKMEGV4cGVuc2VfZ3JvdXBfaWSUSwKMDmNjY19hY2NvdW50X2lklIwCNDGUjAllbnRpdHlfaWSUjAI5M5SMDWRlcGFydG1lbnRfaWSUTowQdHJhbnNhY3Rpb25fZGF0ZZSMCjIwMjItMDEtMTmUjAhjdXJyZW5jeZSMA1VTRJSMDHByaXZhdGVfbm90ZZSMNkNyZWRpdCBjYXJkIGV4cGVuc2UgYnkgYXNod2luLnRAZnlsZS5pbiBvbiAyMDIyLTAxLTE5IJSMG2NyZWRpdF9jYXJkX3B1cmNoYXNlX251bWJlcpSMDUUvMjAyMi8wMS9ULzOUjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBEw0BLw7e5pSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwKdXBkYXRlZF9hdJRoMUMKB+YBEw0BLw7fKZRoNoaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnNoHoloGowHZGVmYXVsdJR1YowCaWSUSwKMDHdvcmtzcGFjZV9pZJRLBIwLZnVuZF9zb3VyY2WUjANDQ0OUjAtkZXNjcmlwdGlvbpR9lCiMCXJlcG9ydF9pZJSMDHJwT2MzT296UXc5NpSMCmV4cGVuc2VfaWSUjAx0eDBtbU5KMFZyMWGUjAtmdW5kX3NvdXJjZZSMA0NDQ5SMDGNsYWltX251bWJlcpSMDUMvMjAyMi8wMS9SLzOUjA5lbXBsb3llZV9lbWFpbJSMEGFzaHdpbi50QGZ5bGUuaW6UjAhzcGVudF9hdJRoJ3WMDXJlc3BvbnNlX2xvZ3OUfZQojAhQdXJjaGFzZZR9lCiMCkFjY291bnRSZWaUfZQojAV2YWx1ZZSMAjQxlIwEbmFtZZSMCk1hc3RlcmNhcmSUdYwLUGF5bWVudFR5cGWUjApDcmVkaXRDYXJklIwJRW50aXR5UmVmlH2UKGhXjAI5M5RoWYwQQ3JlZGl0IENhcmQgTWlzY5SMBHR5cGWUjAZWZW5kb3KUdYwGQ3JlZGl0lImMCFRvdGFsQW10lEdAVoAAAAAAAIwKUHVyY2hhc2VFeJR9lIwDYW55lF2UfZQoaFmMLntodHRwOi8vc2NoZW1hLmludHVpdC5jb20vZmluYW5jZS92M31OYW1lVmFsdWWUjAxkZWNsYXJlZFR5cGWUjCZjb20uaW50dWl0LnNjaGVtYS5maW5hbmNlLnYzLk5hbWVWYWx1ZZSMBXNjb3BllIwmamF2YXgueG1sLmJpbmQuSkFYQkVsZW1lbnQkR2xvYmFsU2NvcGWUaFd9lCiMBE5hbWWUjAdUeG5UeXBllIwFVmFsdWWUjAI1NJR1jANuaWyUiYwLZ2xvYmFsU2NvcGWUiIwPdHlwZVN1YnN0aXR1dGVklIl1YXOMBmRvbWFpbpSMA1FCT5SMBnNwYXJzZZSJjAJJZJSMBDE5NTmUjAlTeW5jVG9rZW6UjAEwlIwITWV0YURhdGGUfZQojApDcmVhdGVUaW1llIwZMjAyMi0wMS0xOVQwNTowMTo1MC0wODowMJSMD0xhc3RVcGRhdGVkVGltZZSMGTIwMjItMDEtMTlUMDU6MDE6NTAtMDg6MDCUdYwLQ3VzdG9tRmllbGSUXZSMCURvY051bWJlcpSMDUUvMjAyMi8wMS9ULzOUjAdUeG5EYXRllIwKMjAyMi0wMS0xOZSMC0N1cnJlbmN5UmVmlH2UKGhXjANVU0SUaFmMFFVuaXRlZCBTdGF0ZXMgRG9sbGFylHWMC1ByaXZhdGVOb3RllIw1Q3JlZGl0IGNhcmQgZXhwZW5zZSBieSBhc2h3aW4udEBmeWxlLmluIG9uIDIwMjItMDEtMTmUjARMaW5llF2UfZQoaHqMATGUjAtEZXNjcmlwdGlvbpSMmWFzaHdpbi50QGZ5bGUuaW4gLSBUcmF2ZWwgLSAyMDIyLTAxLTE5IC0gQy8yMDIyLzAxL1IvMyAtICAtIGh0dHBzOi8vc3RhZ2luZy5meWxlLnRlY2gvYXBwL21haW4vIy9lbnRlcnByaXNlL3ZpZXdfZXhwZW5zZS90eDBtbU5KMFZyMWE/b3JnX2lkPW9yR2NCQ1ZQaWpqT5SMBkFtb3VudJRHQFaAAAAAAACMCkRldGFpbFR5cGWUjB1BY2NvdW50QmFzZWRFeHBlbnNlTGluZURldGFpbJSMHUFjY291bnRCYXNlZEV4cGVuc2VMaW5lRGV0YWlslH2UKGhVfZQoaFeMATiUaFmMDEJhbmsgQ2hhcmdlc5R1jA5CaWxsYWJsZVN0YXR1c5SMC05vdEJpbGxhYmxllIwKVGF4Q29kZVJlZpR9lGhXjANOT06Uc3V1YXWMBHRpbWWUjB0yMDIyLTAxLTE5VDA1OjAxOjQ5Ljk3MC0wODowMJR1jApjcmVhdGVkX2F0lGgxQwoH5gETDQElAYnplGg2hpRSlIwLZXhwb3J0ZWRfYXSUaDFDCgfmARMNATIAdXiUhZRSlIwKdXBkYXRlZF9hdJRoMUMKB+YBEw0BMgB2ZJRoNoaUUpSMD19kamFuZ29fdmVyc2lvbpRoPnViSwOGlC4=	gAR9lC4=	\N	2022-01-19 13:01:42.687886+00	2022-01-19 13:01:50.534886+00	t	69ea9be1179f41569ec7c8f879815a4d	e3d6860a1c1446fc8ccdad935403c2c9	1
bravo-speaker-salami-nine	apps.fyle.tasks.create_expense_groups	\N	gASVSwIAAAAAAABLBF2UKIwIUEVSU09OQUyUjANDQ0OUZYwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoA4wKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAZhZGRpbmeUiYwCZGKUjAdkZWZhdWx0lHVijAJpZJRLAYwMd29ya3NwYWNlX2lklEsEjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBEwwxAg6xgZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoK0MKB+YBFAcDFwxEFpRoMIaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YoeULg==	gAR9lC4=	gASVawIAAAAAAACMEnBpY2tsZWZpZWxkLmZpZWxkc5SMDl9PYmplY3RXcmFwcGVylJOUKYGUTn2UjARfb2JqlIwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoBowKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAZhZGRpbmeUiYwCZGKUjAdkZWZhdWx0lHVijAJpZJRLAYwMd29ya3NwYWNlX2lklEsEjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBEwwxAg6xgZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoLkMKB+YBFAcDFwxEFpRoM4aUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnOGlGIu	2022-01-20 07:03:20.882503+00	2022-01-20 07:03:23.813245+00	t	74ad945784ba46a986d2d53e6e3a37f8	\N	1
ink-bulldog-nitrogen-undress	apps.quickbooks_online.tasks.create_bill	\N	gASVXwcAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMBGJpbGyUaAKMEXF1aWNrYm9va3Nfb25saW5llIwEQmlsbJSGlIWUUpR9lCiMBl9zdGF0ZZRoCymBlH2UKIwCZGKUjAdkZWZhdWx0lGgOfZSMDWV4cGVuc2VfZ3JvdXCUaAdzjAZhZGRpbmeUiXVijAJpZJRLAYwQZXhwZW5zZV9ncm91cF9pZJRLA4wTYWNjb3VudHNfcGF5YWJsZV9pZJSMAjMzlIwJdmVuZG9yX2lklIwCOTSUjA1kZXBhcnRtZW50X2lklE6MEHRyYW5zYWN0aW9uX2RhdGWUjAoyMDIyLTAxLTIwlIwIY3VycmVuY3mUjANVU0SUjAxwcml2YXRlX25vdGWUjDdSZWltYnVyc2FibGUgZXhwZW5zZSBieSBhc2h3aW4udEBmeWxlLmluIG9uIDIwMjItMDEtMjAglIwOcGF5bWVudF9zeW5jZWSUiYwLcGFpZF9vbl9xYm+UiYwKY3JlYXRlZF9hdJSMCGRhdGV0aW1llIwIZGF0ZXRpbWWUk5RDCgfmARQHAyUOqHKUjARweXR6lIwEX1VUQ5STlClSlIaUUpSMCnVwZGF0ZWRfYXSUaDFDCgfmARQHAyUOqMmUaDaGlFKUjA9fZGphbmdvX3ZlcnNpb26UjAYzLjEuMTOUdWJzaB6JaBqMB2RlZmF1bHSUdWKMAmlklEsDjAx3b3Jrc3BhY2VfaWSUSwSMC2Z1bmRfc291cmNllIwIUEVSU09OQUyUjAtkZXNjcmlwdGlvbpR9lCiMCXJlcG9ydF9pZJSMDHJwaHhTOThaYjJ5cpSMC2Z1bmRfc291cmNllIwIUEVSU09OQUyUjAxjbGFpbV9udW1iZXKUjA1DLzIwMjIvMDEvUi80lIwOZW1wbG95ZWVfZW1haWyUjBBhc2h3aW4udEBmeWxlLmlulHWMDXJlc3BvbnNlX2xvZ3OUfZQojARCaWxslH2UKIwHRHVlRGF0ZZSMCjIwMjItMDEtMjCUjAdCYWxhbmNllEdAWUAAAAAAAIwGZG9tYWlulIwDUUJPlIwGc3BhcnNllImMAklklIwEMTk2MJSMCVN5bmNUb2tlbpSMATCUjAhNZXRhRGF0YZR9lCiMCkNyZWF0ZVRpbWWUjBkyMDIyLTAxLTE5VDIzOjAzOjQwLTA4OjAwlIwPTGFzdFVwZGF0ZWRUaW1llIwZMjAyMi0wMS0xOVQyMzowMzo0MC0wODowMJR1jAdUeG5EYXRllIwKMjAyMi0wMS0yMJSMC0N1cnJlbmN5UmVmlH2UKIwFdmFsdWWUjANVU0SUjARuYW1llIwUVW5pdGVkIFN0YXRlcyBEb2xsYXKUdYwLUHJpdmF0ZU5vdGWUjDZSZWltYnVyc2FibGUgZXhwZW5zZSBieSBhc2h3aW4udEBmeWxlLmluIG9uIDIwMjItMDEtMjCUjARMaW5llF2UfZQoaFiMATGUjAdMaW5lTnVtlEsBjAtEZXNjcmlwdGlvbpSMmWFzaHdpbi50QGZ5bGUuaW4gLSBUcmF2ZWwgLSAyMDIyLTAxLTIwIC0gQy8yMDIyLzAxL1IvNCAtICAtIGh0dHBzOi8vc3RhZ2luZy5meWxlLnRlY2gvYXBwL21haW4vIy9lbnRlcnByaXNlL3ZpZXdfZXhwZW5zZS90eE1zc0NidEVhaEM/b3JnX2lkPW9yR2NCQ1ZQaWpqT5SMBkFtb3VudJRHQFlAAAAAAACMCUxpbmtlZFR4bpRdlIwKRGV0YWlsVHlwZZSMHUFjY291bnRCYXNlZEV4cGVuc2VMaW5lRGV0YWlslIwdQWNjb3VudEJhc2VkRXhwZW5zZUxpbmVEZXRhaWyUfZQojApBY2NvdW50UmVmlH2UKGhmjAE4lGhojAxCYW5rIENoYXJnZXOUdYwOQmlsbGFibGVTdGF0dXOUjAtOb3RCaWxsYWJsZZSMClRheENvZGVSZWaUfZRoZowDTk9OlHN1dWGMCVZlbmRvclJlZpR9lChoZowCOTSUaGiMBkFtYXpvbpR1jAxBUEFjY291bnRSZWaUfZQoaGaMAjMzlGhojBZBY2NvdW50cyBQYXlhYmxlIChBL1AplHWMCFRvdGFsQW10lEdAWUAAAAAAAHWMBHRpbWWUjB0yMDIyLTAxLTE5VDIzOjAzOjQwLjQ3My0wODowMJR1jApjcmVhdGVkX2F0lGgxQwoH5gEUBwMXCzUdlGg2hpRSlIwLZXhwb3J0ZWRfYXSUaDFDCgfmARQHAygJrQWUhZRSlIwKdXBkYXRlZF9hdJRoMUMKB+YBFAcDKAm4L5RoNoaUUpSMD19kamFuZ29fdmVyc2lvbpRoPnViSwSGlC4=	gAR9lC4=	\N	2022-01-20 07:03:34.792375+00	2022-01-20 07:03:41.283905+00	t	39d9a623b089496b92fe9968316672c3	f639496e923848f180ba82391158d122	1
high-seventeen-low-fifteen	apps.fyle.tasks.create_expense_groups	\N	gASVSwIAAAAAAABLBF2UKIwIUEVSU09OQUyUjANDQ0OUZYwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoA4wKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAZhZGRpbmeUiYwCZGKUjAdkZWZhdWx0lHVijAJpZJRLAYwMd29ya3NwYWNlX2lklEsEjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBEwwxAg6xgZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoK0MKB+YBFAcGIg7DapRoMIaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YoeULg==	gAR9lC4=	gASVawIAAAAAAACMEnBpY2tsZWZpZWxkLmZpZWxkc5SMDl9PYmplY3RXcmFwcGVylJOUKYGUTn2UjARfb2JqlIwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoBowKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAZhZGRpbmeUiYwCZGKUjAdkZWZhdWx0lHVijAJpZJRLAYwMd29ya3NwYWNlX2lklEsEjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBEwwxAg6xgZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoLkMKB+YBFAcGIg7DapRoM4aUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnOGlGIu	2022-01-20 07:06:32.325826+00	2022-01-20 07:06:34.981832+00	t	08263b482edf4a78aa8736650b45a5a8	\N	1
michigan-cold-romeo-glucose	apps.quickbooks_online.tasks.create_bill	\N	gASVsgMAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMBGJpbGyUaAKMEXF1aWNrYm9va3Nfb25saW5llIwEQmlsbJSGlIWUUpR9lCiMBl9zdGF0ZZRoCymBlH2UKIwCZGKUjAdkZWZhdWx0lGgOfZSMDWV4cGVuc2VfZ3JvdXCUaAdzjAZhZGRpbmeUiXVijAJpZJRLAowQZXhwZW5zZV9ncm91cF9pZJRLBIwTYWNjb3VudHNfcGF5YWJsZV9pZJSMAjMzlIwJdmVuZG9yX2lklIwCOTSUjA1kZXBhcnRtZW50X2lklE6MEHRyYW5zYWN0aW9uX2RhdGWUjAoyMDIyLTAxLTIwlIwIY3VycmVuY3mUjANVU0SUjAxwcml2YXRlX25vdGWUjDdSZWltYnVyc2FibGUgZXhwZW5zZSBieSBhc2h3aW4udEBmeWxlLmluIG9uIDIwMjItMDEtMjAglIwOcGF5bWVudF9zeW5jZWSUiYwLcGFpZF9vbl9xYm+UiYwKY3JlYXRlZF9hdJSMCGRhdGV0aW1llIwIZGF0ZXRpbWWUk5RDCgfmARQJBToOneyUjARweXR6lIwEX1VUQ5STlClSlIaUUpSMCnVwZGF0ZWRfYXSUaDFDCgfmARQJBToOnh6UaDaGlFKUjA9fZGphbmdvX3ZlcnNpb26UjAYzLjEuMTOUdWJzaB6JaBqMB2RlZmF1bHSUdWKMAmlklEsEjAx3b3Jrc3BhY2VfaWSUSwSMC2Z1bmRfc291cmNllIwIUEVSU09OQUyUjAtkZXNjcmlwdGlvbpR9lCiMCXJlcG9ydF9pZJSMDHJwSHFEWk1QOTlVT5SMC2Z1bmRfc291cmNllIwIUEVSU09OQUyUjAxjbGFpbV9udW1iZXKUjA1DLzIwMjIvMDEvUi82lIwOZW1wbG95ZWVfZW1haWyUjBBhc2h3aW4udEBmeWxlLmlulHWMDXJlc3BvbnNlX2xvZ3OUTowKY3JlYXRlZF9hdJRoMUMKB+YBFAcGIgtYn5RoNoaUUpSMC2V4cG9ydGVkX2F0lE6MCnVwZGF0ZWRfYXSUaDFDCgfmARQHBiILWP6UaDaGlFKUjA9fZGphbmdvX3ZlcnNpb26UaD51YksGhpQu	gAR9lC4=	\N	2022-01-20 09:05:55.871778+00	2022-01-20 09:05:59.856319+00	t	9fc05680b81b43c9bdfe3ec1c6742cca	9085fa6d1900446798b3be0fbf35e387	1
thirteen-cola-finch-massachusetts	apps.quickbooks_online.tasks.create_credit_card_purchase	\N	gASV9AMAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMEmNyZWRpdGNhcmRwdXJjaGFzZZRoAowRcXVpY2tib29rc19vbmxpbmWUjBJDcmVkaXRDYXJkUHVyY2hhc2WUhpSFlFKUfZQojAZfc3RhdGWUaAspgZR9lCiMAmRilIwHZGVmYXVsdJRoDn2UjA1leHBlbnNlX2dyb3VwlGgHc4wGYWRkaW5nlIl1YowCaWSUSwOMEGV4cGVuc2VfZ3JvdXBfaWSUSwWMDmNjY19hY2NvdW50X2lklIwCNDGUjAllbnRpdHlfaWSUjAI5M5SMDWRlcGFydG1lbnRfaWSUTowQdHJhbnNhY3Rpb25fZGF0ZZSMCjIwMjItMDEtMjCUjAhjdXJyZW5jeZSMA1VTRJSMDHByaXZhdGVfbm90ZZSMNkNyZWRpdCBjYXJkIGV4cGVuc2UgYnkgYXNod2luLnRAZnlsZS5pbiBvbiAyMDIyLTAxLTIwIJSMG2NyZWRpdF9jYXJkX3B1cmNoYXNlX251bWJlcpSMDUUvMjAyMi8wMS9ULzSUjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFAkGAQa2wZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwKdXBkYXRlZF9hdJRoMUMKB+YBFAkGAQa2/pRoNoaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnNoHoloGowHZGVmYXVsdJR1YowCaWSUSwWMDHdvcmtzcGFjZV9pZJRLBIwLZnVuZF9zb3VyY2WUjANDQ0OUjAtkZXNjcmlwdGlvbpR9lCiMCXJlcG9ydF9pZJSMDHJwaEJlZExWa3lVMZSMCmV4cGVuc2VfaWSUjAx0eFNwTDkwMGhFakWUjAtmdW5kX3NvdXJjZZSMA0NDQ5SMDGNsYWltX251bWJlcpSMDUMvMjAyMi8wMS9SLzWUjA5lbXBsb3llZV9lbWFpbJSMEGFzaHdpbi50QGZ5bGUuaW6UjAhzcGVudF9hdJRoJ3WMDXJlc3BvbnNlX2xvZ3OUTowKY3JlYXRlZF9hdJRoMUMKB+YBFAcGIgtwSZRoNoaUUpSMC2V4cG9ydGVkX2F0lE6MCnVwZGF0ZWRfYXSUaDFDCgfmARQJBgEGLpaUaDaGlFKUjA9fZGphbmdvX3ZlcnNpb26UaD51YksFhpQu	gAR9lC4=	\N	2022-01-20 09:05:55.835874+00	2022-01-20 09:06:02.390824+00	t	1623fe1592d1412a90f002278be6f71c	42a656f1872d4a8098adec17fedc75c3	1
coffee-music-nine-oranges	apps.quickbooks_online.tasks.async_sync_accounts	\N	gASVBQAAAAAAAABLBoWULg==	gAR9lC4=	\N	2022-01-21 05:40:39.367058+00	2022-01-21 05:40:46.256738+00	t	4a4ff6d412de461cb36a0b4944cd002f	\N	1
princess-massachusetts-finch-fourteen	apps.quickbooks_online.tasks.async_sync_accounts	\N	gASVBQAAAAAAAABLB4WULg==	gAR9lC4=	\N	2022-01-21 05:47:05.342986+00	2022-01-21 05:47:12.266464+00	t	8f03dce3cfb146be8030887d8933fd0a	\N	1
bulldog-pizza-oranges-happy	apps.fyle.tasks.create_expense_groups	\N	gASVSwIAAAAAAABLB12UKIwIUEVSU09OQUyUjANDQ0OUZYwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoA4wKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAJkYpSMB2RlZmF1bHSUjAZhZGRpbmeUiXVijAJpZJRLB4wMd29ya3NwYWNlX2lklEsHjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFQoDEAY9i5SMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoK0MKB+YBFQoDEwLo9JRoMIaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YoeULg==	gAR9lC4=	gASVawIAAAAAAACMEnBpY2tsZWZpZWxkLmZpZWxkc5SMDl9PYmplY3RXcmFwcGVylJOUKYGUTn2UjARfb2JqlIwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoBowKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAJkYpSMB2RlZmF1bHSUjAZhZGRpbmeUiXVijAJpZJRLB4wMd29ya3NwYWNlX2lklEsHjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFQoDEAY9i5SMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoLkMKB+YBFQoDEwLo9JRoM4aUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnOGlGIu	2022-01-21 10:03:16.469285+00	2022-01-21 10:03:19.197476+00	t	4edb60eeacd7418a9290c3671a593228	\N	1
ten-mango-don-arizona	apps.quickbooks_online.tasks.create_bill	\N	gASVsgMAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMBGJpbGyUaAKMEXF1aWNrYm9va3Nfb25saW5llIwEQmlsbJSGlIWUUpR9lCiMBl9zdGF0ZZRoCymBlH2UKIwCZGKUjAdkZWZhdWx0lGgOfZSMDWV4cGVuc2VfZ3JvdXCUaAdzjAZhZGRpbmeUiXVijAJpZJRLA4wQZXhwZW5zZV9ncm91cF9pZJRLBowTYWNjb3VudHNfcGF5YWJsZV9pZJSMAjMzlIwJdmVuZG9yX2lklIwCNzSUjA1kZXBhcnRtZW50X2lklE6MEHRyYW5zYWN0aW9uX2RhdGWUjAoyMDIyLTAxLTIxlIwIY3VycmVuY3mUjANVU0SUjAxwcml2YXRlX25vdGWUjDdSZWltYnVyc2FibGUgZXhwZW5zZSBieSBhc2h3aW4udEBmeWxlLmluIG9uIDIwMjItMDEtMjEglIwOcGF5bWVudF9zeW5jZWSUiYwLcGFpZF9vbl9xYm+UiYwKY3JlYXRlZF9hdJSMCGRhdGV0aW1llIwIZGF0ZXRpbWWUk5RDCgfmARUKAxwFRE+UjARweXR6lIwEX1VUQ5STlClSlIaUUpSMCnVwZGF0ZWRfYXSUaDFDCgfmARUKAxwFRIeUaDaGlFKUjA9fZGphbmdvX3ZlcnNpb26UjAYzLjEuMTOUdWJzaB6JaBqMB2RlZmF1bHSUdWKMAmlklEsGjAx3b3Jrc3BhY2VfaWSUSweMC2Z1bmRfc291cmNllIwIUEVSU09OQUyUjAtkZXNjcmlwdGlvbpR9lCiMCXJlcG9ydF9pZJSMDHJwcUJLdXZDd25UWZSMC2Z1bmRfc291cmNllIwIUEVSU09OQUyUjAxjbGFpbV9udW1iZXKUjA1DLzIwMjIvMDEvUi83lIwOZW1wbG95ZWVfZW1haWyUjBBhc2h3aW4udEBmeWxlLmlulHWMDXJlc3BvbnNlX2xvZ3OUTowKY3JlYXRlZF9hdJRoMUMKB+YBFQoDEwIHKZRoNoaUUpSMC2V4cG9ydGVkX2F0lE6MCnVwZGF0ZWRfYXSUaDFDCgfmARUKAxMCB1qUaDaGlFKUjA9fZGphbmdvX3ZlcnNpb26UaD51YksJhpQu	gAR9lC4=	\N	2022-01-21 10:03:25.253085+00	2022-01-21 10:03:31.182473+00	t	b2de1dab6fbc4e1fb239f748c7437df1	661be4d0821041b59451ab47e59ecb1d	1
oven-carpet-emma-emma	apps.quickbooks_online.tasks.create_credit_card_purchase	\N	gASVwggAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMEmNyZWRpdGNhcmRwdXJjaGFzZZRoAowRcXVpY2tib29rc19vbmxpbmWUjBJDcmVkaXRDYXJkUHVyY2hhc2WUhpSFlFKUfZQojAZfc3RhdGWUaAspgZR9lCiMAmRilIwHZGVmYXVsdJRoDn2UjA1leHBlbnNlX2dyb3VwlGgHc4wGYWRkaW5nlIl1YowCaWSUSwSMEGV4cGVuc2VfZ3JvdXBfaWSUSweMDmNjY19hY2NvdW50X2lklIwCNDKUjAllbnRpdHlfaWSUjAI3NJSMDWRlcGFydG1lbnRfaWSUTowQdHJhbnNhY3Rpb25fZGF0ZZSMCjIwMjItMDEtMjGUjAhjdXJyZW5jeZSMA1VTRJSMDHByaXZhdGVfbm90ZZSMNkNyZWRpdCBjYXJkIGV4cGVuc2UgYnkgYXNod2luLnRAZnlsZS5pbiBvbiAyMDIyLTAxLTIxIJSMG2NyZWRpdF9jYXJkX3B1cmNoYXNlX251bWJlcpSMDUUvMjAyMi8wMS9ULziUjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFQoDHwtdjZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwKdXBkYXRlZF9hdJRoMUMKB+YBFQoDHwtd9ZRoNoaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnNoHoloGowHZGVmYXVsdJR1YowCaWSUSweMDHdvcmtzcGFjZV9pZJRLB4wLZnVuZF9zb3VyY2WUjANDQ0OUjAtkZXNjcmlwdGlvbpR9lCiMCXJlcG9ydF9pZJSMDHJwcUJLdXZDd25UWZSMCmV4cGVuc2VfaWSUjAx0eEprWmxKUzRMckGUjAtmdW5kX3NvdXJjZZSMA0NDQ5SMDGNsYWltX251bWJlcpSMDUMvMjAyMi8wMS9SLzeUjA5lbXBsb3llZV9lbWFpbJSMEGFzaHdpbi50QGZ5bGUuaW6UjAhzcGVudF9hdJRoJ3WMDXJlc3BvbnNlX2xvZ3OUfZQojAhQdXJjaGFzZZR9lCiMCkFjY291bnRSZWaUfZQojAV2YWx1ZZSMAjQylIwEbmFtZZSMBFZpc2GUdYwLUGF5bWVudFR5cGWUjApDcmVkaXRDYXJklIwJRW50aXR5UmVmlH2UKGhXjAI3NJRoWYwQQ3JlZGl0IENhcmQgTWlzY5SMBHR5cGWUjAZWZW5kb3KUdYwGQ3JlZGl0lImMCFRvdGFsQW10lEdASQAAAAAAAIwKUHVyY2hhc2VFeJR9lIwDYW55lF2UfZQoaFmMLntodHRwOi8vc2NoZW1hLmludHVpdC5jb20vZmluYW5jZS92M31OYW1lVmFsdWWUjAxkZWNsYXJlZFR5cGWUjCZjb20uaW50dWl0LnNjaGVtYS5maW5hbmNlLnYzLk5hbWVWYWx1ZZSMBXNjb3BllIwmamF2YXgueG1sLmJpbmQuSkFYQkVsZW1lbnQkR2xvYmFsU2NvcGWUaFd9lCiMBE5hbWWUjAdUeG5UeXBllIwFVmFsdWWUjAI1NJR1jANuaWyUiYwLZ2xvYmFsU2NvcGWUiIwPdHlwZVN1YnN0aXR1dGVklIl1YXOMBmRvbWFpbpSMA1FCT5SMBnNwYXJzZZSJjAJJZJSMAzIzNZSMCVN5bmNUb2tlbpSMATCUjAhNZXRhRGF0YZR9lCiMCkNyZWF0ZVRpbWWUjBkyMDIyLTAxLTIxVDAyOjAzOjMzLTA4OjAwlIwPTGFzdFVwZGF0ZWRUaW1llIwZMjAyMi0wMS0yMVQwMjowMzozMy0wODowMJR1jAtDdXN0b21GaWVsZJRdlIwJRG9jTnVtYmVylIwNRS8yMDIyLzAxL1QvOJSMB1R4bkRhdGWUjAoyMDIyLTAxLTIxlIwLQ3VycmVuY3lSZWaUfZQoaFeMA0dCUJRoWYwWQnJpdGlzaCBQb3VuZCBTdGVybGluZ5R1jAxFeGNoYW5nZVJhdGWUSwGMC1ByaXZhdGVOb3RllIw1Q3JlZGl0IGNhcmQgZXhwZW5zZSBieSBhc2h3aW4udEBmeWxlLmluIG9uIDIwMjItMDEtMjGUjARMaW5llF2UfZQoaHqMATGUjAtEZXNjcmlwdGlvbpSMmWFzaHdpbi50QGZ5bGUuaW4gLSBUcmF2ZWwgLSAyMDIyLTAxLTIxIC0gQy8yMDIyLzAxL1IvNyAtICAtIGh0dHBzOi8vc3RhZ2luZy5meWxlLnRlY2gvYXBwL21haW4vIy9lbnRlcnByaXNlL3ZpZXdfZXhwZW5zZS90eEprWmxKUzRMckE/b3JnX2lkPW9yR2NCQ1ZQaWpqT5SMBkFtb3VudJRHQEkAAAAAAACMCkRldGFpbFR5cGWUjB1BY2NvdW50QmFzZWRFeHBlbnNlTGluZURldGFpbJSMHUFjY291bnRCYXNlZEV4cGVuc2VMaW5lRGV0YWlslH2UKGhVfZQoaFeMAjc4lGhZjAlQdXJjaGFzZXOUdYwOQmlsbGFibGVTdGF0dXOUjAtOb3RCaWxsYWJsZZSMClRheENvZGVSZWaUfZRoV4wDTk9OlHN1dWF1jAR0aW1llIwdMjAyMi0wMS0yMVQwMjowMzozMy44MzMtMDg6MDCUdYwKY3JlYXRlZF9hdJRoMUMKB+YBFQoDEwJWPJRoNoaUUpSMC2V4cG9ydGVkX2F0lGgxQwoH5gEVCgMhDjjOlIWUUpSMCnVwZGF0ZWRfYXSUaDFDCgfmARUKAyEOOcyUaDaGlFKUjA9fZGphbmdvX3ZlcnNpb26UaD51YksIhpQu	gAR9lC4=	\N	2022-01-21 10:03:25.130854+00	2022-01-21 10:03:34.645702+00	t	507a7ffce32141a1aa9b545b3682d55f	8a5d8bceb16e4f1eaf53bd56ab9762a6	1
lemon-jersey-kilo-muppet	apps.quickbooks_online.tasks.create_journal_entry	\N	gASVOgMAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMDGpvdXJuYWxlbnRyeZRoAowRcXVpY2tib29rc19vbmxpbmWUjAxKb3VybmFsRW50cnmUhpSFlFKUfZQoaAloCymBlH2UKIwCZGKUjAdkZWZhdWx0lGgOfZSMDWV4cGVuc2VfZ3JvdXCUaAdzjAZhZGRpbmeUiXVijAJpZJRLAowQZXhwZW5zZV9ncm91cF9pZJRLDIwQdHJhbnNhY3Rpb25fZGF0ZZSMCjIwMjItMDEtMjOUjAhjdXJyZW5jeZSMA1VTRJSMDHByaXZhdGVfbm90ZZSMNkNyZWRpdCBjYXJkIGV4cGVuc2UgYnkgYXNod2luLnRAZnlsZS5pbiBvbiAyMDIyLTAxLTIzIJSMCmNyZWF0ZWRfYXSUjAhkYXRldGltZZSMCGRhdGV0aW1llJOUQwoH5gEXDCEsCEE2lIwEcHl0epSMBF9VVEOUk5QpUpSGlFKUjAp1cGRhdGVkX2F0lGgpQwoH5gEXDCEsCEF+lGguhpRSlIwPX2RqYW5nb192ZXJzaW9ulIwGMy4xLjEzlHVic2gdiWgZjAdkZWZhdWx0lHViaB5LDIwMd29ya3NwYWNlX2lklEsIjAtmdW5kX3NvdXJjZZSMA0NDQ5SMC2Rlc2NyaXB0aW9ulH2UKIwJcmVwb3J0X2lklIwMcnAySEpVUllLc1hJlIwLZnVuZF9zb3VyY2WUjANDQ0OUjAxjbGFpbV9udW1iZXKUjA5DLzIwMjIvMDEvUi8xNJSMDmVtcGxveWVlX2VtYWlslIwQYXNod2luLnRAZnlsZS5pbpR1jA1yZXNwb25zZV9sb2dzlE5oJmgpQwoH5gEXDA86BtuzlGguhpRSlIwLZXhwb3J0ZWRfYXSUTmgxaClDCgfmARcMDzoG2/6UaC6GlFKUjA9fZGphbmdvX3ZlcnNpb26UaDZ1YksPhpQu	gAR9lC4=	\N	2022-01-23 12:33:42.240913+00	2022-01-23 12:33:45.771233+00	t	4dda54b4b64246db8899294979789c08	e3f40eba0304415dba67b42b2ee2866a	1
winner-thirteen-minnesota-diet	apps.quickbooks_online.tasks.async_sync_accounts	\N	gASVBQAAAAAAAABLCIWULg==	gAR9lC4=	\N	2022-01-21 10:37:30.376776+00	2022-01-21 10:37:36.502976+00	t	0cf62d218bed4bf390837be321721a7a	\N	1
tango-georgia-thirteen-uniform	apps.quickbooks_online.tasks.async_sync_accounts	\N	gASVBQAAAAAAAABLCYWULg==	gAR9lC4=	\N	2022-01-21 10:42:32.692046+00	2022-01-21 10:42:38.452527+00	t	b772ffe37eef46849b58120f773901a8	\N	1
helium-leopard-quiet-moon	apps.fyle.tasks.create_expense_groups	\N	gASVSwIAAAAAAABLCV2UKIwIUEVSU09OQUyUjANDQ0OUZYwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoA4wKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAJkYpSMB2RlZmF1bHSUjAZhZGRpbmeUiXVijAJpZJRLB4wMd29ya3NwYWNlX2lklEsJjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFQotDwgBMZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoK0MKB+YBFQotEgzNmJRoMIaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YoeULg==	gAR9lC4=	gASVawIAAAAAAACMEnBpY2tsZWZpZWxkLmZpZWxkc5SMDl9PYmplY3RXcmFwcGVylJOUKYGUTn2UjARfb2JqlIwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoBowKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAJkYpSMB2RlZmF1bHSUjAZhZGRpbmeUiXVijAJpZJRLB4wMd29ya3NwYWNlX2lklEsJjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFQotDwgBMZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoLkMKB+YBFQotEgzNmJRoM4aUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnOGlGIu	2022-01-21 10:45:15.60101+00	2022-01-21 10:45:18.939558+00	t	66ae32a6857543cbbc48e8ab0836379a	\N	1
comet-bravo-monkey-dakota	apps.quickbooks_online.tasks.create_bill	\N	gASVdwcAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMBGJpbGyUaAKMEXF1aWNrYm9va3Nfb25saW5llIwEQmlsbJSGlIWUUpR9lCiMBl9zdGF0ZZRoCymBlH2UKIwCZGKUjAdkZWZhdWx0lGgOfZSMDWV4cGVuc2VfZ3JvdXCUaAdzjAZhZGRpbmeUiXVijAJpZJRLA4wQZXhwZW5zZV9ncm91cF9pZJRLBowTYWNjb3VudHNfcGF5YWJsZV9pZJSMAjMzlIwJdmVuZG9yX2lklIwCNDOUjA1kZXBhcnRtZW50X2lklE6MEHRyYW5zYWN0aW9uX2RhdGWUjAoyMDIyLTAxLTIxlIwIY3VycmVuY3mUjANVU0SUjAxwcml2YXRlX25vdGWUjDdSZWltYnVyc2FibGUgZXhwZW5zZSBieSBhc2h3aW4udEBmeWxlLmluIG9uIDIwMjItMDEtMjEglIwOcGF5bWVudF9zeW5jZWSUiYwLcGFpZF9vbl9xYm+UiYwKY3JlYXRlZF9hdJSMCGRhdGV0aW1llIwIZGF0ZXRpbWWUk5RDCgfmARUKLR8BS96UjARweXR6lIwEX1VUQ5STlClSlIaUUpSMCnVwZGF0ZWRfYXSUaDFDCgfmARUKLR8BTJ6UaDaGlFKUjA9fZGphbmdvX3ZlcnNpb26UjAYzLjEuMTOUdWJzaB6JaBqMB2RlZmF1bHSUdWKMAmlklEsGjAx3b3Jrc3BhY2VfaWSUSwmMC2Z1bmRfc291cmNllIwIUEVSU09OQUyUjAtkZXNjcmlwdGlvbpR9lCiMCXJlcG9ydF9pZJSMDHJwcUJLdXZDd25UWZSMC2Z1bmRfc291cmNllIwIUEVSU09OQUyUjAxjbGFpbV9udW1iZXKUjA1DLzIwMjIvMDEvUi83lIwOZW1wbG95ZWVfZW1haWyUjBBhc2h3aW4udEBmeWxlLmlulHWMDXJlc3BvbnNlX2xvZ3OUfZQojARCaWxslH2UKIwHRHVlRGF0ZZSMCjIwMjItMDEtMjGUjAdCYWxhbmNllEdAXgAAAAAAAIwGZG9tYWlulIwDUUJPlIwGc3BhcnNllImMAklklIwDMTQ2lIwJU3luY1Rva2VulIwBMJSMCE1ldGFEYXRhlH2UKIwKQ3JlYXRlVGltZZSMGTIwMjItMDEtMjFUMDI6NDU6MzQtMDg6MDCUjA9MYXN0VXBkYXRlZFRpbWWUjBkyMDIyLTAxLTIxVDAyOjQ1OjM0LTA4OjAwlHWMB1R4bkRhdGWUjAoyMDIyLTAxLTIxlIwLQ3VycmVuY3lSZWaUfZQojAV2YWx1ZZSMA1VTRJSMBG5hbWWUjBRVbml0ZWQgU3RhdGVzIERvbGxhcpR1jAtQcml2YXRlTm90ZZSMNlJlaW1idXJzYWJsZSBleHBlbnNlIGJ5IGFzaHdpbi50QGZ5bGUuaW4gb24gMjAyMi0wMS0yMZSMBExpbmWUXZR9lChoWIwBMZSMB0xpbmVOdW2USwGMC0Rlc2NyaXB0aW9ulIyZYXNod2luLnRAZnlsZS5pbiAtIFRyYXZlbCAtIDIwMjItMDEtMjEgLSBDLzIwMjIvMDEvUi83IC0gIC0gaHR0cHM6Ly9zdGFnaW5nLmZ5bGUudGVjaC9hcHAvbWFpbi8jL2VudGVycHJpc2Uvdmlld19leHBlbnNlL3R4RG1jcU92OExNRD9vcmdfaWQ9b3JHY0JDVlBpampPlIwGQW1vdW50lEdAXgAAAAAAAIwJTGlua2VkVHhulF2UjApEZXRhaWxUeXBllIwdQWNjb3VudEJhc2VkRXhwZW5zZUxpbmVEZXRhaWyUjB1BY2NvdW50QmFzZWRFeHBlbnNlTGluZURldGFpbJR9lCiMCkFjY291bnRSZWaUfZQoaGaMAjU3lGhojB5JbnN1cmFuY2U6V29ya2VycyBDb21wZW5zYXRpb26UdYwOQmlsbGFibGVTdGF0dXOUjAtOb3RCaWxsYWJsZZSMClRheENvZGVSZWaUfZRoZowDTk9OlHN1dWGMCVZlbmRvclJlZpR9lChoZowCNDOUaGiMDE1haG9uZXkgTXVnc5R1jAxBUEFjY291bnRSZWaUfZQoaGaMAjMzlGhojBZBY2NvdW50cyBQYXlhYmxlIChBL1AplHWMCFRvdGFsQW10lEdAXgAAAAAAAHWMBHRpbWWUjB0yMDIyLTAxLTIxVDAyOjQ1OjM0LjA5OC0wODowMJR1jApjcmVhdGVkX2F0lGgxQwoH5gEVCi0SCGwOlGg2hpRSlIwLZXhwb3J0ZWRfYXSUaDFDCgfmARUKLSIC6QOUhZRSlIwKdXBkYXRlZF9hdJRoMUMKB+YBFQotIgLrqZRoNoaUUpSMD19kamFuZ29fdmVyc2lvbpRoPnViSwmGlC4=	gAR9lC4=	\N	2022-01-21 10:45:28.335422+00	2022-01-21 10:45:35.001614+00	t	6d350073ae3640c2b1a97ef7218ae266	0599eb56173148dc9c004e3e5c53a6ac	1
kentucky-india-aspen-happy	apps.quickbooks_online.tasks.create_credit_card_purchase	\N	gASVxAgAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMEmNyZWRpdGNhcmRwdXJjaGFzZZRoAowRcXVpY2tib29rc19vbmxpbmWUjBJDcmVkaXRDYXJkUHVyY2hhc2WUhpSFlFKUfZQojAZfc3RhdGWUaAspgZR9lCiMAmRilIwHZGVmYXVsdJRoDn2UjA1leHBlbnNlX2dyb3VwlGgHc4wGYWRkaW5nlIl1YowCaWSUSwSMEGV4cGVuc2VfZ3JvdXBfaWSUSweMDmNjY19hY2NvdW50X2lklIwCNDKUjAllbnRpdHlfaWSUjAI1OJSMDWRlcGFydG1lbnRfaWSUTowQdHJhbnNhY3Rpb25fZGF0ZZSMCjIwMjItMDEtMjGUjAhjdXJyZW5jeZSMA1VTRJSMDHByaXZhdGVfbm90ZZSMNkNyZWRpdCBjYXJkIGV4cGVuc2UgYnkgYXNod2luLnRAZnlsZS5pbiBvbiAyMDIyLTAxLTIxIJSMG2NyZWRpdF9jYXJkX3B1cmNoYXNlX251bWJlcpSMDUUvMjAyMi8wMS9ULziUjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFQotIwQjqJSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwKdXBkYXRlZF9hdJRoMUMKB+YBFQotIwQj+JRoNoaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnNoHoloGowHZGVmYXVsdJR1YowCaWSUSweMDHdvcmtzcGFjZV9pZJRLCYwLZnVuZF9zb3VyY2WUjANDQ0OUjAtkZXNjcmlwdGlvbpR9lCiMCXJlcG9ydF9pZJSMDHJwcUJLdXZDd25UWZSMCmV4cGVuc2VfaWSUjAx0eEprWmxKUzRMckGUjAtmdW5kX3NvdXJjZZSMA0NDQ5SMDGNsYWltX251bWJlcpSMDUMvMjAyMi8wMS9SLzeUjA5lbXBsb3llZV9lbWFpbJSMEGFzaHdpbi50QGZ5bGUuaW6UjAhzcGVudF9hdJRoJ3WMDXJlc3BvbnNlX2xvZ3OUfZQojAhQdXJjaGFzZZR9lCiMCkFjY291bnRSZWaUfZQojAV2YWx1ZZSMAjQylIwEbmFtZZSMBFZpc2GUdYwLUGF5bWVudFR5cGWUjApDcmVkaXRDYXJklIwJRW50aXR5UmVmlH2UKGhXjAI1OJRoWYwQQ3JlZGl0IENhcmQgTWlzY5SMBHR5cGWUjAZWZW5kb3KUdYwGQ3JlZGl0lImMCFRvdGFsQW10lEdASQAAAAAAAIwKUHVyY2hhc2VFeJR9lIwDYW55lF2UfZQoaFmMLntodHRwOi8vc2NoZW1hLmludHVpdC5jb20vZmluYW5jZS92M31OYW1lVmFsdWWUjAxkZWNsYXJlZFR5cGWUjCZjb20uaW50dWl0LnNjaGVtYS5maW5hbmNlLnYzLk5hbWVWYWx1ZZSMBXNjb3BllIwmamF2YXgueG1sLmJpbmQuSkFYQkVsZW1lbnQkR2xvYmFsU2NvcGWUaFd9lCiMBE5hbWWUjAdUeG5UeXBllIwFVmFsdWWUjAI1NJR1jANuaWyUiYwLZ2xvYmFsU2NvcGWUiIwPdHlwZVN1YnN0aXR1dGVklIl1YXOMBmRvbWFpbpSMA1FCT5SMBnNwYXJzZZSJjAJJZJSMAzE0N5SMCVN5bmNUb2tlbpSMATCUjAhNZXRhRGF0YZR9lCiMCkNyZWF0ZVRpbWWUjBkyMDIyLTAxLTIxVDAyOjQ1OjM3LTA4OjAwlIwPTGFzdFVwZGF0ZWRUaW1llIwZMjAyMi0wMS0yMVQwMjo0NTozNy0wODowMJR1jAtDdXN0b21GaWVsZJRdlIwJRG9jTnVtYmVylIwNRS8yMDIyLzAxL1QvOJSMB1R4bkRhdGWUjAoyMDIyLTAxLTIxlIwLQ3VycmVuY3lSZWaUfZQoaFeMA1VTRJRoWYwUVW5pdGVkIFN0YXRlcyBEb2xsYXKUdYwLUHJpdmF0ZU5vdGWUjDVDcmVkaXQgY2FyZCBleHBlbnNlIGJ5IGFzaHdpbi50QGZ5bGUuaW4gb24gMjAyMi0wMS0yMZSMBExpbmWUXZR9lChoeowBMZSMC0Rlc2NyaXB0aW9ulIyZYXNod2luLnRAZnlsZS5pbiAtIFRyYXZlbCAtIDIwMjItMDEtMjEgLSBDLzIwMjIvMDEvUi83IC0gIC0gaHR0cHM6Ly9zdGFnaW5nLmZ5bGUudGVjaC9hcHAvbWFpbi8jL2VudGVycHJpc2Uvdmlld19leHBlbnNlL3R4SmtabEpTNExyQT9vcmdfaWQ9b3JHY0JDVlBpampPlIwGQW1vdW50lEdASQAAAAAAAIwKRGV0YWlsVHlwZZSMHUFjY291bnRCYXNlZEV4cGVuc2VMaW5lRGV0YWlslIwdQWNjb3VudEJhc2VkRXhwZW5zZUxpbmVEZXRhaWyUfZQoaFV9lChoV4wCNTeUaFmMHkluc3VyYW5jZTpXb3JrZXJzIENvbXBlbnNhdGlvbpR1jA5CaWxsYWJsZVN0YXR1c5SMC05vdEJpbGxhYmxllIwKVGF4Q29kZVJlZpR9lGhXjANOT06Uc3V1YXWMBHRpbWWUjB0yMDIyLTAxLTIxVDAyOjQ1OjM3LjU4Ni0wODowMJR1jApjcmVhdGVkX2F0lGgxQwoH5gEVCi0SCImDlGg2hpRSlIwLZXhwb3J0ZWRfYXSUaDFDCgfmARUKLSYAAQ6UhZRSlIwKdXBkYXRlZF9hdJRoMUMKB+YBFQotJgABxZRoNoaUUpSMD19kamFuZ29fdmVyc2lvbpRoPnViSwiGlC4=	gAR9lC4=	\N	2022-01-21 10:45:28.326847+00	2022-01-21 10:45:38.765024+00	t	8a5a08a8b2dd404cb5d6f49badae366c	84c2e93c928547afa6a6e1aae4cdb872	1
may-two-august-alanine	apps.fyle.tasks.create_expense_groups	\N	gASVSwIAAAAAAABLCV2UKIwIUEVSU09OQUyUjANDQ0OUZYwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoA4wKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAZhZGRpbmeUiYwCZGKUjAdkZWZhdWx0lHVijAJpZJRLB4wMd29ya3NwYWNlX2lklEsJjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFQotDwgBMZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoK0MKB+YBFQozBgiiJpRoMIaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YoeULg==	gAR9lC4=	gASVawIAAAAAAACMEnBpY2tsZWZpZWxkLmZpZWxkc5SMDl9PYmplY3RXcmFwcGVylJOUKYGUTn2UjARfb2JqlIwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoBowKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAZhZGRpbmeUiYwCZGKUjAdkZWZhdWx0lHVijAJpZJRLB4wMd29ya3NwYWNlX2lklEsJjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFQotDwgBMZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoLkMKB+YBFQozBgiiJpRoM4aUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnOGlGIu	2022-01-21 10:51:04.895781+00	2022-01-21 10:51:06.569968+00	t	f9c5a11a5b1b4aeeb1c1275af875db54	\N	1
item-foxtrot-single-six	apps.quickbooks_online.tasks.create_bill	\N	gASVsgMAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMBGJpbGyUaAKMEXF1aWNrYm9va3Nfb25saW5llIwEQmlsbJSGlIWUUpR9lCiMBl9zdGF0ZZRoCymBlH2UKIwCZGKUjAdkZWZhdWx0lGgOfZSMDWV4cGVuc2VfZ3JvdXCUaAdzjAZhZGRpbmeUiXVijAJpZJRLBIwQZXhwZW5zZV9ncm91cF9pZJRLCIwTYWNjb3VudHNfcGF5YWJsZV9pZJSMAjMzlIwJdmVuZG9yX2lklIwCNDOUjA1kZXBhcnRtZW50X2lklE6MEHRyYW5zYWN0aW9uX2RhdGWUjAoyMDIyLTAxLTIxlIwIY3VycmVuY3mUjANVU0SUjAxwcml2YXRlX25vdGWUjDdSZWltYnVyc2FibGUgZXhwZW5zZSBieSBhc2h3aW4udEBmeWxlLmluIG9uIDIwMjItMDEtMjEglIwOcGF5bWVudF9zeW5jZWSUiYwLcGFpZF9vbl9xYm+UiYwKY3JlYXRlZF9hdJSMCGRhdGV0aW1llIwIZGF0ZXRpbWWUk5RDCgfmARUQNTcMceuUjARweXR6lIwEX1VUQ5STlClSlIaUUpSMCnVwZGF0ZWRfYXSUaDFDCgfmARUQNTcMchSUaDaGlFKUjA9fZGphbmdvX3ZlcnNpb26UjAYzLjEuMTOUdWJzaB6JaBqMB2RlZmF1bHSUdWKMAmlklEsIjAx3b3Jrc3BhY2VfaWSUSwmMC2Z1bmRfc291cmNllIwIUEVSU09OQUyUjAtkZXNjcmlwdGlvbpR9lCiMCXJlcG9ydF9pZJSMDHJwZU02OEhLQ05OQZSMC2Z1bmRfc291cmNllIwIUEVSU09OQUyUjAxjbGFpbV9udW1iZXKUjA1DLzIwMjIvMDEvUi84lIwOZW1wbG95ZWVfZW1haWyUjBBhc2h3aW4udEBmeWxlLmlulHWMDXJlc3BvbnNlX2xvZ3OUTowKY3JlYXRlZF9hdJRoMUMKB+YBFQozBgf4aZRoNoaUUpSMC2V4cG9ydGVkX2F0lE6MCnVwZGF0ZWRfYXSUaDFDCgfmARUKMwYH+LKUaDaGlFKUjA9fZGphbmdvX3ZlcnNpb26UaD51YksLhpQu	gAR9lC4=	\N	2022-01-21 16:53:52.818061+00	2022-01-21 16:53:56.674993+00	t	59e2c310d4b7436ea0bafd210131f20a	0522461bccbd42fdabfe98781bcc760b	1
purple-west-table-one	apps.quickbooks_online.tasks.create_credit_card_purchase	\N	gASV9AMAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMEmNyZWRpdGNhcmRwdXJjaGFzZZRoAowRcXVpY2tib29rc19vbmxpbmWUjBJDcmVkaXRDYXJkUHVyY2hhc2WUhpSFlFKUfZQojAZfc3RhdGWUaAspgZR9lCiMAmRilIwHZGVmYXVsdJRoDn2UjA1leHBlbnNlX2dyb3VwlGgHc4wGYWRkaW5nlIl1YowCaWSUSwWMEGV4cGVuc2VfZ3JvdXBfaWSUSwmMDmNjY19hY2NvdW50X2lklIwCNDKUjAllbnRpdHlfaWSUjAI1OJSMDWRlcGFydG1lbnRfaWSUTowQdHJhbnNhY3Rpb25fZGF0ZZSMCjIwMjItMDEtMjGUjAhjdXJyZW5jeZSMA1VTRJSMDHByaXZhdGVfbm90ZZSMNkNyZWRpdCBjYXJkIGV4cGVuc2UgYnkgYXNod2luLnRAZnlsZS5pbiBvbiAyMDIyLTAxLTIxIJSMG2NyZWRpdF9jYXJkX3B1cmNoYXNlX251bWJlcpSMDUUvMjAyMi8wMS9ULzmUjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFRA1OwJ9iZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwKdXBkYXRlZF9hdJRoMUMKB+YBFRA1OwJ9tZRoNoaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnNoHoloGowHZGVmYXVsdJR1YowCaWSUSwmMDHdvcmtzcGFjZV9pZJRLCYwLZnVuZF9zb3VyY2WUjANDQ0OUjAtkZXNjcmlwdGlvbpR9lCiMCXJlcG9ydF9pZJSMDHJwZU02OEhLQ05OQZSMCmV4cGVuc2VfaWSUjAx0eHZoOHFtN1JUUkmUjAtmdW5kX3NvdXJjZZSMA0NDQ5SMDGNsYWltX251bWJlcpSMDUMvMjAyMi8wMS9SLziUjA5lbXBsb3llZV9lbWFpbJSMEGFzaHdpbi50QGZ5bGUuaW6UjAhzcGVudF9hdJRoJ3WMDXJlc3BvbnNlX2xvZ3OUTowKY3JlYXRlZF9hdJRoMUMKB+YBFQozBggZgJRoNoaUUpSMC2V4cG9ydGVkX2F0lE6MCnVwZGF0ZWRfYXSUaDFDCgfmARUQNTsBddqUaDaGlFKUjA9fZGphbmdvX3ZlcnNpb26UaD51YksKhpQu	gAR9lC4=	\N	2022-01-21 16:53:52.778274+00	2022-01-21 16:53:59.966865+00	t	cddf01a758844a64a81001616546ba3d	b340dee0055d416f89328b9a3f70c68a	1
double-connecticut-uranus-salami	apps.fyle.tasks.create_expense_groups	\N	gASVSwIAAAAAAABLCF2UKIwIUEVSU09OQUyUjANDQ0OUZYwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoA4wKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAJkYpSMB2RlZmF1bHSUjAZhZGRpbmeUiXVijAJpZJRLDIwMd29ya3NwYWNlX2lklEsIjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFwwDBwPAipSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoK0MKB+YBFwwDCwFBvZRoMIaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YoeULg==	gAR9lC4=	gASVawIAAAAAAACMEnBpY2tsZWZpZWxkLmZpZWxkc5SMDl9PYmplY3RXcmFwcGVylJOUKYGUTn2UjARfb2JqlIwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoBowKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAJkYpSMB2RlZmF1bHSUjAZhZGRpbmeUiXVijAJpZJRLDIwMd29ya3NwYWNlX2lklEsIjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFwwDBwPAipSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoLkMKB+YBFwwDCwFBvZRoM4aUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnOGlGIu	2022-01-23 12:03:07.317972+00	2022-01-23 12:03:11.0927+00	t	84779355cf6741c5a4372a519041543a	\N	1
kilo-hawaii-carolina-louisiana	apps.quickbooks_online.tasks.create_qbo_expense	\N	gASVRggAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMCnFib2V4cGVuc2WUaAKMEXF1aWNrYm9va3Nfb25saW5llIwKUUJPRXhwZW5zZZSGlIWUUpR9lCiMBl9zdGF0ZZRoCymBlH2UKIwCZGKUjAdkZWZhdWx0lGgOfZSMDWV4cGVuc2VfZ3JvdXCUaAdzjAZhZGRpbmeUiXVijAJpZJRLAYwQZXhwZW5zZV9ncm91cF9pZJRLCowSZXhwZW5zZV9hY2NvdW50X2lklIwCNDGUjAllbnRpdHlfaWSUjAI1NZSMDWRlcGFydG1lbnRfaWSUTowQdHJhbnNhY3Rpb25fZGF0ZZSMCjIwMjItMDEtMjOUjAhjdXJyZW5jeZSMA1VTRJSMDHByaXZhdGVfbm90ZZSMN1JlaW1idXJzYWJsZSBleHBlbnNlIGJ5IGFzaHdpbi50QGZ5bGUuaW4gb24gMjAyMi0wMS0yMyCUjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFwwDFQG78pSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwKdXBkYXRlZF9hdJRoL0MKB+YBFwwDFQG8IpRoNIaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnNoHoloGowHZGVmYXVsdJR1YowCaWSUSwqMDHdvcmtzcGFjZV9pZJRLCIwLZnVuZF9zb3VyY2WUjAhQRVJTT05BTJSMC2Rlc2NyaXB0aW9ulH2UKIwJcmVwb3J0X2lklIwMcnAwams3UmcxZXBrlIwLZnVuZF9zb3VyY2WUjAhQRVJTT05BTJSMDGNsYWltX251bWJlcpSMDkMvMjAyMi8wMS9SLzEzlIwOZW1wbG95ZWVfZW1haWyUjBBhc2h3aW4udEBmeWxlLmlulHWMDXJlc3BvbnNlX2xvZ3OUfZQojAhQdXJjaGFzZZR9lCiMCkFjY291bnRSZWaUfZQojAV2YWx1ZZSMAjQxlIwEbmFtZZSMCk1hc3RlcmNhcmSUdYwLUGF5bWVudFR5cGWUjApDcmVkaXRDYXJklIwJRW50aXR5UmVmlH2UKGhSjAI1NZRoVIwLRW1pbHkgUGxhdHSUjAR0eXBllIwIRW1wbG95ZWWUdYwGQ3JlZGl0lImMCFRvdGFsQW10lEdATgAAAAAAAIwKUHVyY2hhc2VFeJR9lIwDYW55lF2UfZQoaFSMLntodHRwOi8vc2NoZW1hLmludHVpdC5jb20vZmluYW5jZS92M31OYW1lVmFsdWWUjAxkZWNsYXJlZFR5cGWUjCZjb20uaW50dWl0LnNjaGVtYS5maW5hbmNlLnYzLk5hbWVWYWx1ZZSMBXNjb3BllIwmamF2YXgueG1sLmJpbmQuSkFYQkVsZW1lbnQkR2xvYmFsU2NvcGWUaFJ9lCiMBE5hbWWUjAdUeG5UeXBllIwFVmFsdWWUjAI1NJR1jANuaWyUiYwLZ2xvYmFsU2NvcGWUiIwPdHlwZVN1YnN0aXR1dGVklIl1YXOMBmRvbWFpbpSMA1FCT5SMBnNwYXJzZZSJjAJJZJSMBDE5NjmUjAlTeW5jVG9rZW6UjAEwlIwITWV0YURhdGGUfZQojApDcmVhdGVUaW1llIwZMjAyMi0wMS0yM1QwNDowMzoyNS0wODowMJSMD0xhc3RVcGRhdGVkVGltZZSMGTIwMjItMDEtMjNUMDQ6MDM6MjUtMDg6MDCUdYwLQ3VzdG9tRmllbGSUXZSMB1R4bkRhdGWUjAoyMDIyLTAxLTIzlIwLQ3VycmVuY3lSZWaUfZQoaFKMA1VTRJRoVIwUVW5pdGVkIFN0YXRlcyBEb2xsYXKUdYwLUHJpdmF0ZU5vdGWUjDZSZWltYnVyc2FibGUgZXhwZW5zZSBieSBhc2h3aW4udEBmeWxlLmluIG9uIDIwMjItMDEtMjOUjARMaW5llF2UfZQoaHWMATGUjAtEZXNjcmlwdGlvbpSMmGFzaHdpbi50QGZ5bGUuaW4gLSBGb29kIC0gMjAyMi0wMS0yMyAtIEMvMjAyMi8wMS9SLzEzIC0gIC0gaHR0cHM6Ly9zdGFnaW5nLmZ5bGUudGVjaC9hcHAvbWFpbi8jL2VudGVycHJpc2Uvdmlld19leHBlbnNlL3R4cmFTUEphRzlFcD9vcmdfaWQ9b3I3OUNvYjk3S1NolIwGQW1vdW50lEdATgAAAAAAAIwKRGV0YWlsVHlwZZSMHUFjY291bnRCYXNlZEV4cGVuc2VMaW5lRGV0YWlslIwdQWNjb3VudEJhc2VkRXhwZW5zZUxpbmVEZXRhaWyUfZQoaFB9lChoUowCNTaUaFSMD0F1dG9tb2JpbGU6RnVlbJR1jA5CaWxsYWJsZVN0YXR1c5SMC05vdEJpbGxhYmxllIwKVGF4Q29kZVJlZpR9lGhSjANOT06Uc3V1YXWMBHRpbWWUjB0yMDIyLTAxLTIzVDA0OjAzOjI1LjU2My0wODowMJR1jApjcmVhdGVkX2F0lGgvQwoH5gEXDAMLABMPlGg0hpRSlIwLZXhwb3J0ZWRfYXSUaC9DCgfmARcMAxkM9qWUhZRSlIwKdXBkYXRlZF9hdJRoL0MKB+YBFwwDGQz4M5RoNIaUUpSMD19kamFuZ29fdmVyc2lvbpRoPHViSw2GlC4=	gAR9lC4=	\N	2022-01-23 12:03:18.277771+00	2022-01-23 12:03:27.138635+00	t	f6cc450e079c4181be62718ced485981	68919b3ff6f1463c81fbc1499f001d48	1
solar-yankee-kitten-yankee	apps.fyle.tasks.create_expense_groups	\N	gASVSwIAAAAAAABLCF2UKIwIUEVSU09OQUyUjANDQ0OUZYwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoA4wKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAZhZGRpbmeUiYwCZGKUjAdkZWZhdWx0lHVijAJpZJRLDIwMd29ya3NwYWNlX2lklEsIjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFwwDBwPAipSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoK0MKB+YBFwwPOgiaT5RoMIaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YoeULg==	gAR9lC4=	gASVawIAAAAAAACMEnBpY2tsZWZpZWxkLmZpZWxkc5SMDl9PYmplY3RXcmFwcGVylJOUKYGUTn2UjARfb2JqlIwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoBowKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAZhZGRpbmeUiYwCZGKUjAdkZWZhdWx0lHVijAJpZJRLDIwMd29ya3NwYWNlX2lklEsIjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFwwDBwPAipSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoLkMKB+YBFwwPOgiaT5RoM4aUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnOGlGIu	2022-01-23 12:15:55.219883+00	2022-01-23 12:15:58.58071+00	t	75039d25b7314d378821c41e8ad99d32	\N	1
hawaii-coffee-football-fix	apps.quickbooks_online.tasks.create_journal_entry	\N	gASVWgMAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMDGpvdXJuYWxlbnRyeZRoAowRcXVpY2tib29rc19vbmxpbmWUjAxKb3VybmFsRW50cnmUhpSFlFKUfZQojAZfc3RhdGWUaAspgZR9lCiMAmRilIwHZGVmYXVsdJRoDn2UjA1leHBlbnNlX2dyb3VwlGgHc4wGYWRkaW5nlIl1YowCaWSUSwGMEGV4cGVuc2VfZ3JvdXBfaWSUSwyMEHRyYW5zYWN0aW9uX2RhdGWUjAoyMDIyLTAxLTIzlIwIY3VycmVuY3mUjANVU0SUjAxwcml2YXRlX25vdGWUjDZDcmVkaXQgY2FyZCBleHBlbnNlIGJ5IGFzaHdpbi50QGZ5bGUuaW4gb24gMjAyMi0wMS0yMyCUjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFwwQKA6BV5SMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwKdXBkYXRlZF9hdJRoKkMKB+YBFwwQKA6BiJRoL4aUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnNoHoloGowHZGVmYXVsdJR1YowCaWSUSwyMDHdvcmtzcGFjZV9pZJRLCIwLZnVuZF9zb3VyY2WUjANDQ0OUjAtkZXNjcmlwdGlvbpR9lCiMCXJlcG9ydF9pZJSMDHJwMkhKVVJZS3NYSZSMC2Z1bmRfc291cmNllIwDQ0NDlIwMY2xhaW1fbnVtYmVylIwOQy8yMDIyLzAxL1IvMTSUjA5lbXBsb3llZV9lbWFpbJSMEGFzaHdpbi50QGZ5bGUuaW6UdYwNcmVzcG9uc2VfbG9nc5ROjApjcmVhdGVkX2F0lGgqQwoH5gEXDA86BtuzlGgvhpRSlIwLZXhwb3J0ZWRfYXSUTowKdXBkYXRlZF9hdJRoKkMKB+YBFwwPOgbb/pRoL4aUUpSMD19kamFuZ29fdmVyc2lvbpRoN3ViSw+GlC4=	gAR9lC4=	\N	2022-01-23 12:16:37.860614+00	2022-01-23 12:16:41.798421+00	t	3266d3dc4e6646499124d42a103f482f	1d9b42656ef4496b9e884770a7da0e90	1
april-mississippi-washington-coffee	apps.quickbooks_online.tasks.create_qbo_expense	\N	gASVRggAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMCnFib2V4cGVuc2WUaAKMEXF1aWNrYm9va3Nfb25saW5llIwKUUJPRXhwZW5zZZSGlIWUUpR9lCiMBl9zdGF0ZZRoCymBlH2UKIwCZGKUjAdkZWZhdWx0lGgOfZSMDWV4cGVuc2VfZ3JvdXCUaAdzjAZhZGRpbmeUiXVijAJpZJRLAowQZXhwZW5zZV9ncm91cF9pZJRLC4wSZXhwZW5zZV9hY2NvdW50X2lklIwCNDGUjAllbnRpdHlfaWSUjAI1NZSMDWRlcGFydG1lbnRfaWSUTowQdHJhbnNhY3Rpb25fZGF0ZZSMCjIwMjItMDEtMjOUjAhjdXJyZW5jeZSMA1VTRJSMDHByaXZhdGVfbm90ZZSMN1JlaW1idXJzYWJsZSBleHBlbnNlIGJ5IGFzaHdpbi50QGZ5bGUuaW4gb24gMjAyMi0wMS0yMyCUjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFwwQKA7rGZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwKdXBkYXRlZF9hdJRoL0MKB+YBFwwQKA7rRZRoNIaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnNoHoloGowHZGVmYXVsdJR1YowCaWSUSwuMDHdvcmtzcGFjZV9pZJRLCIwLZnVuZF9zb3VyY2WUjAhQRVJTT05BTJSMC2Rlc2NyaXB0aW9ulH2UKIwJcmVwb3J0X2lklIwMcnAySEpVUllLc1hJlIwLZnVuZF9zb3VyY2WUjAhQRVJTT05BTJSMDGNsYWltX251bWJlcpSMDkMvMjAyMi8wMS9SLzE0lIwOZW1wbG95ZWVfZW1haWyUjBBhc2h3aW4udEBmeWxlLmlulHWMDXJlc3BvbnNlX2xvZ3OUfZQojAhQdXJjaGFzZZR9lCiMCkFjY291bnRSZWaUfZQojAV2YWx1ZZSMAjQxlIwEbmFtZZSMCk1hc3RlcmNhcmSUdYwLUGF5bWVudFR5cGWUjApDcmVkaXRDYXJklIwJRW50aXR5UmVmlH2UKGhSjAI1NZRoVIwLRW1pbHkgUGxhdHSUjAR0eXBllIwIRW1wbG95ZWWUdYwGQ3JlZGl0lImMCFRvdGFsQW10lEdATgAAAAAAAIwKUHVyY2hhc2VFeJR9lIwDYW55lF2UfZQoaFSMLntodHRwOi8vc2NoZW1hLmludHVpdC5jb20vZmluYW5jZS92M31OYW1lVmFsdWWUjAxkZWNsYXJlZFR5cGWUjCZjb20uaW50dWl0LnNjaGVtYS5maW5hbmNlLnYzLk5hbWVWYWx1ZZSMBXNjb3BllIwmamF2YXgueG1sLmJpbmQuSkFYQkVsZW1lbnQkR2xvYmFsU2NvcGWUaFJ9lCiMBE5hbWWUjAdUeG5UeXBllIwFVmFsdWWUjAI1NJR1jANuaWyUiYwLZ2xvYmFsU2NvcGWUiIwPdHlwZVN1YnN0aXR1dGVklIl1YXOMBmRvbWFpbpSMA1FCT5SMBnNwYXJzZZSJjAJJZJSMBDE5NzCUjAlTeW5jVG9rZW6UjAEwlIwITWV0YURhdGGUfZQojApDcmVhdGVUaW1llIwZMjAyMi0wMS0yM1QwNDoxNjo0My0wODowMJSMD0xhc3RVcGRhdGVkVGltZZSMGTIwMjItMDEtMjNUMDQ6MTY6NDMtMDg6MDCUdYwLQ3VzdG9tRmllbGSUXZSMB1R4bkRhdGWUjAoyMDIyLTAxLTIzlIwLQ3VycmVuY3lSZWaUfZQoaFKMA1VTRJRoVIwUVW5pdGVkIFN0YXRlcyBEb2xsYXKUdYwLUHJpdmF0ZU5vdGWUjDZSZWltYnVyc2FibGUgZXhwZW5zZSBieSBhc2h3aW4udEBmeWxlLmluIG9uIDIwMjItMDEtMjOUjARMaW5llF2UfZQoaHWMATGUjAtEZXNjcmlwdGlvbpSMmGFzaHdpbi50QGZ5bGUuaW4gLSBGb29kIC0gMjAyMi0wMS0yMyAtIEMvMjAyMi8wMS9SLzE0IC0gIC0gaHR0cHM6Ly9zdGFnaW5nLmZ5bGUudGVjaC9hcHAvbWFpbi8jL2VudGVycHJpc2Uvdmlld19leHBlbnNlL3R4aUt3bWlURGp3Sj9vcmdfaWQ9b3I3OUNvYjk3S1NolIwGQW1vdW50lEdATgAAAAAAAIwKRGV0YWlsVHlwZZSMHUFjY291bnRCYXNlZEV4cGVuc2VMaW5lRGV0YWlslIwdQWNjb3VudEJhc2VkRXhwZW5zZUxpbmVEZXRhaWyUfZQoaFB9lChoUowCNTaUaFSMD0F1dG9tb2JpbGU6RnVlbJR1jA5CaWxsYWJsZVN0YXR1c5SMC05vdEJpbGxhYmxllIwKVGF4Q29kZVJlZpR9lGhSjANOT06Uc3V1YXWMBHRpbWWUjB0yMDIyLTAxLTIzVDA0OjE2OjQzLjMyNC0wODowMJR1jApjcmVhdGVkX2F0lGgvQwoH5gEXDA86Bfu4lGg0hpRSlIwLZXhwb3J0ZWRfYXSUaC9DCgfmARcMECsHgaKUhZRSlIwKdXBkYXRlZF9hdJRoL0MKB+YBFwwQKweDApRoNIaUUpSMD19kamFuZ29fdmVyc2lvbpRoPHViSw6GlC4=	gAR9lC4=	\N	2022-01-23 12:16:37.760801+00	2022-01-23 12:16:44.088161+00	t	4e04a2efa5e3468d8da210ce098218b4	461032bd36b243d78957ffd0586a3083	1
apart-nevada-texas-diet	apps.fyle.tasks.create_expense_groups	\N	gASVSwIAAAAAAABLCF2UKIwIUEVSU09OQUyUjANDQ0OUZYwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoA4wKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAZhZGRpbmeUiYwCZGKUjAdkZWZhdWx0lHVijAJpZJRLDIwMd29ya3NwYWNlX2lklEsIjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFwwDBwPAipSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoK0MKB+YBFwwhJAGyYpRoMIaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YoeULg==	gAR9lC4=	gASVawIAAAAAAACMEnBpY2tsZWZpZWxkLmZpZWxkc5SMDl9PYmplY3RXcmFwcGVylJOUKYGUTn2UjARfb2JqlIwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoBowKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAZhZGRpbmeUiYwCZGKUjAdkZWZhdWx0lHVijAJpZJRLDIwMd29ya3NwYWNlX2lklEsIjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFwwDBwPAipSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoLkMKB+YBFwwhJAGyYpRoM4aUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnOGlGIu	2022-01-23 12:33:32.570169+00	2022-01-23 12:33:36.139142+00	t	66082f471c9e4c54bd804faf40d98923	\N	1
black-nebraska-illinois-single	apps.quickbooks_online.tasks.create_qbo_expense	\N	gASVRggAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMCnFib2V4cGVuc2WUaAKMEXF1aWNrYm9va3Nfb25saW5llIwKUUJPRXhwZW5zZZSGlIWUUpR9lCiMBl9zdGF0ZZRoCymBlH2UKIwCZGKUjAdkZWZhdWx0lGgOfZSMDWV4cGVuc2VfZ3JvdXCUaAdzjAZhZGRpbmeUiXVijAJpZJRLA4wQZXhwZW5zZV9ncm91cF9pZJRLDYwSZXhwZW5zZV9hY2NvdW50X2lklIwCNDGUjAllbnRpdHlfaWSUjAI1NZSMDWRlcGFydG1lbnRfaWSUTowQdHJhbnNhY3Rpb25fZGF0ZZSMCjIwMjItMDEtMjOUjAhjdXJyZW5jeZSMA1VTRJSMDHByaXZhdGVfbm90ZZSMN1JlaW1idXJzYWJsZSBleHBlbnNlIGJ5IGFzaHdpbi50QGZ5bGUuaW4gb24gMjAyMi0wMS0yMyCUjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFwwhLAiXTpSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwKdXBkYXRlZF9hdJRoL0MKB+YBFwwhLAiXjZRoNIaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnNoHoloGowHZGVmYXVsdJR1YowCaWSUSw2MDHdvcmtzcGFjZV9pZJRLCIwLZnVuZF9zb3VyY2WUjAhQRVJTT05BTJSMC2Rlc2NyaXB0aW9ulH2UKIwJcmVwb3J0X2lklIwMcnByVWVOd2l6REZilIwLZnVuZF9zb3VyY2WUjAhQRVJTT05BTJSMDGNsYWltX251bWJlcpSMDkMvMjAyMi8wMS9SLzE1lIwOZW1wbG95ZWVfZW1haWyUjBBhc2h3aW4udEBmeWxlLmlulHWMDXJlc3BvbnNlX2xvZ3OUfZQojAhQdXJjaGFzZZR9lCiMCkFjY291bnRSZWaUfZQojAV2YWx1ZZSMAjQxlIwEbmFtZZSMCk1hc3RlcmNhcmSUdYwLUGF5bWVudFR5cGWUjApDcmVkaXRDYXJklIwJRW50aXR5UmVmlH2UKGhSjAI1NZRoVIwLRW1pbHkgUGxhdHSUjAR0eXBllIwIRW1wbG95ZWWUdYwGQ3JlZGl0lImMCFRvdGFsQW10lEdATgAAAAAAAIwKUHVyY2hhc2VFeJR9lIwDYW55lF2UfZQoaFSMLntodHRwOi8vc2NoZW1hLmludHVpdC5jb20vZmluYW5jZS92M31OYW1lVmFsdWWUjAxkZWNsYXJlZFR5cGWUjCZjb20uaW50dWl0LnNjaGVtYS5maW5hbmNlLnYzLk5hbWVWYWx1ZZSMBXNjb3BllIwmamF2YXgueG1sLmJpbmQuSkFYQkVsZW1lbnQkR2xvYmFsU2NvcGWUaFJ9lCiMBE5hbWWUjAdUeG5UeXBllIwFVmFsdWWUjAI1NJR1jANuaWyUiYwLZ2xvYmFsU2NvcGWUiIwPdHlwZVN1YnN0aXR1dGVklIl1YXOMBmRvbWFpbpSMA1FCT5SMBnNwYXJzZZSJjAJJZJSMBDE5NzKUjAlTeW5jVG9rZW6UjAEwlIwITWV0YURhdGGUfZQojApDcmVhdGVUaW1llIwZMjAyMi0wMS0yM1QwNDozMzo0Ny0wODowMJSMD0xhc3RVcGRhdGVkVGltZZSMGTIwMjItMDEtMjNUMDQ6MzM6NDctMDg6MDCUdYwLQ3VzdG9tRmllbGSUXZSMB1R4bkRhdGWUjAoyMDIyLTAxLTIzlIwLQ3VycmVuY3lSZWaUfZQoaFKMA1VTRJRoVIwUVW5pdGVkIFN0YXRlcyBEb2xsYXKUdYwLUHJpdmF0ZU5vdGWUjDZSZWltYnVyc2FibGUgZXhwZW5zZSBieSBhc2h3aW4udEBmeWxlLmluIG9uIDIwMjItMDEtMjOUjARMaW5llF2UfZQoaHWMATGUjAtEZXNjcmlwdGlvbpSMmGFzaHdpbi50QGZ5bGUuaW4gLSBGb29kIC0gMjAyMi0wMS0yMyAtIEMvMjAyMi8wMS9SLzE1IC0gIC0gaHR0cHM6Ly9zdGFnaW5nLmZ5bGUudGVjaC9hcHAvbWFpbi8jL2VudGVycHJpc2Uvdmlld19leHBlbnNlL3R4UXlid093b1FBQT9vcmdfaWQ9b3I3OUNvYjk3S1NolIwGQW1vdW50lEdATgAAAAAAAIwKRGV0YWlsVHlwZZSMHUFjY291bnRCYXNlZEV4cGVuc2VMaW5lRGV0YWlslIwdQWNjb3VudEJhc2VkRXhwZW5zZUxpbmVEZXRhaWyUfZQoaFB9lChoUowCNTaUaFSMD0F1dG9tb2JpbGU6RnVlbJR1jA5CaWxsYWJsZVN0YXR1c5SMC05vdEJpbGxhYmxllIwKVGF4Q29kZVJlZpR9lGhSjANOT06Uc3V1YXWMBHRpbWWUjB0yMDIyLTAxLTIzVDA0OjMzOjQ3LjEyMS0wODowMJR1jApjcmVhdGVkX2F0lGgvQwoH5gEXDCEkAIg3lGg0hpRSlIwLZXhwb3J0ZWRfYXSUaC9DCgfmARcMIS8Es/CUhZRSlIwKdXBkYXRlZF9hdJRoL0MKB+YBFwwhLwS3a5RoNIaUUpSMD19kamFuZ29fdmVyc2lvbpRoPHViSxCGlC4=	gAR9lC4=	\N	2022-01-23 12:33:42.250739+00	2022-01-23 12:33:47.912496+00	t	50a857b977594ef789f2435a14e8417b	8d513a5f324245d59ac1f59f534a0fd9	1
kansas-xray-missouri-montana	apps.fyle.tasks.create_expense_groups	\N	gASVSwIAAAAAAABLCF2UKIwIUEVSU09OQUyUjANDQ0OUZYwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoA4wKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAZhZGRpbmeUiYwCZGKUjAdkZWZhdWx0lHVijAJpZJRLDIwMd29ya3NwYWNlX2lklEsIjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFwwDBwPAipSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoK0MKB+YBFwwlNgKGVZRoMIaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YoeULg==	gAR9lC4=	gASVawIAAAAAAACMEnBpY2tsZWZpZWxkLmZpZWxkc5SMDl9PYmplY3RXcmFwcGVylJOUKYGUTn2UjARfb2JqlIwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoBowKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAZhZGRpbmeUiYwCZGKUjAdkZWZhdWx0lHVijAJpZJRLDIwMd29ya3NwYWNlX2lklEsIjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFwwDBwPAipSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoLkMKB+YBFwwlNgKGVZRoM4aUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnOGlGIu	2022-01-23 12:37:51.498967+00	2022-01-23 12:37:54.170057+00	t	9f86b7c18a574e689754a0ed9201b2b3	\N	1
seventeen-double-texas-seven	apps.quickbooks_online.tasks.create_journal_entry	\N	gASVWgMAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMDGpvdXJuYWxlbnRyeZRoAowRcXVpY2tib29rc19vbmxpbmWUjAxKb3VybmFsRW50cnmUhpSFlFKUfZQojAZfc3RhdGWUaAspgZR9lCiMAmRilIwHZGVmYXVsdJRoDn2UjA1leHBlbnNlX2dyb3VwlGgHc4wGYWRkaW5nlIl1YowCaWSUSwOMEGV4cGVuc2VfZ3JvdXBfaWSUSwyMEHRyYW5zYWN0aW9uX2RhdGWUjAoyMDIyLTAxLTIzlIwIY3VycmVuY3mUjANVU0SUjAxwcml2YXRlX25vdGWUjDZDcmVkaXQgY2FyZCBleHBlbnNlIGJ5IGFzaHdpbi50QGZ5bGUuaW4gb24gMjAyMi0wMS0yMyCUjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFwwmAQ40JJSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwKdXBkYXRlZF9hdJRoKkMKB+YBFwwmAQ40d5RoL4aUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnNoHoloGowHZGVmYXVsdJR1YowCaWSUSwyMDHdvcmtzcGFjZV9pZJRLCIwLZnVuZF9zb3VyY2WUjANDQ0OUjAtkZXNjcmlwdGlvbpR9lCiMCXJlcG9ydF9pZJSMDHJwMkhKVVJZS3NYSZSMC2Z1bmRfc291cmNllIwDQ0NDlIwMY2xhaW1fbnVtYmVylIwOQy8yMDIyLzAxL1IvMTSUjA5lbXBsb3llZV9lbWFpbJSMEGFzaHdpbi50QGZ5bGUuaW6UdYwNcmVzcG9uc2VfbG9nc5ROjApjcmVhdGVkX2F0lGgqQwoH5gEXDA86BtuzlGgvhpRSlIwLZXhwb3J0ZWRfYXSUTowKdXBkYXRlZF9hdJRoKkMKB+YBFwwPOgbb/pRoL4aUUpSMD19kamFuZ29fdmVyc2lvbpRoN3ViSw+GlC4=	gAR9lC4=	\N	2022-01-23 12:37:59.608466+00	2022-01-23 12:38:03.123018+00	t	42dca3fe2f314d669042b8b76f83e1cf	7d8a82faffb3474f8846142e5dc5b4f6	1
missouri-oscar-iowa-nuts	apps.quickbooks_online.tasks.create_qbo_expense	\N	gASVnQMAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMCnFib2V4cGVuc2WUaAKMEXF1aWNrYm9va3Nfb25saW5llIwKUUJPRXhwZW5zZZSGlIWUUpR9lCiMBl9zdGF0ZZRoCymBlH2UKIwCZGKUjAdkZWZhdWx0lGgOfZSMDWV4cGVuc2VfZ3JvdXCUaAdzjAZhZGRpbmeUiXVijAJpZJRLBIwQZXhwZW5zZV9ncm91cF9pZJRLDowSZXhwZW5zZV9hY2NvdW50X2lklIwCNDGUjAllbnRpdHlfaWSUjAI1NZSMDWRlcGFydG1lbnRfaWSUTowQdHJhbnNhY3Rpb25fZGF0ZZSMCjIwMjItMDEtMjOUjAhjdXJyZW5jeZSMA1VTRJSMDHByaXZhdGVfbm90ZZSMN1JlaW1idXJzYWJsZSBleHBlbnNlIGJ5IGFzaHdpbi50QGZ5bGUuaW4gb24gMjAyMi0wMS0yMyCUjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBFwwmAQ7l1ZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwKdXBkYXRlZF9hdJRoL0MKB+YBFwwmAQ7mDJRoNIaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnNoHoloGowHZGVmYXVsdJR1YowCaWSUSw6MDHdvcmtzcGFjZV9pZJRLCIwLZnVuZF9zb3VyY2WUjAhQRVJTT05BTJSMC2Rlc2NyaXB0aW9ulH2UKIwJcmVwb3J0X2lklIwMcnBCUTl2eDdGSmMzlIwLZnVuZF9zb3VyY2WUjAhQRVJTT05BTJSMDGNsYWltX251bWJlcpSMDkMvMjAyMi8wMS9SLzE2lIwOZW1wbG95ZWVfZW1haWyUjBBhc2h3aW4udEBmeWxlLmlulHWMDXJlc3BvbnNlX2xvZ3OUTowKY3JlYXRlZF9hdJRoL0MKB+YBFwwlNgIWHJRoNIaUUpSMC2V4cG9ydGVkX2F0lE6MCnVwZGF0ZWRfYXSUaC9DCgfmARcMJTYCFluUaDSGlFKUjA9fZGphbmdvX3ZlcnNpb26UaDx1YksRhpQu	gAR9lC4=	\N	2022-01-23 12:37:59.61673+00	2022-01-23 12:38:04.747405+00	t	a6e008c01790456ab3b06500619f1749	d940fe9f905243b0a0b22f891c97154f	1
spaghetti-finch-double-california	apps.quickbooks_online.tasks.async_sync_accounts	\N	gASVBQAAAAAAAABLCoWULg==	gAR9lC4=	\N	2022-01-27 12:55:02.583895+00	2022-01-27 12:55:08.818904+00	t	a44aa7997c784001bdddcb9e63f08e03	\N	1
florida-uranus-lithium-delta	apps.fyle.tasks.create_expense_groups	\N	gASVRAIAAAAAAABLCl2UjAhQRVJTT05BTJRhjBVkamFuZ28uZGIubW9kZWxzLmJhc2WUjA5tb2RlbF91bnBpY2tsZZSTlIwFdGFza3OUjAdUYXNrTG9nlIaUhZRSlH2UKIwGX3N0YXRllGgCjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMAmRilIwHZGVmYXVsdJSMBmFkZGluZ5SJdWKMAmlklEsSjAx3b3Jrc3BhY2VfaWSUSwqMBHR5cGWUjBFGRVRDSElOR19FWFBFTlNFU5SMB3Rhc2tfaWSUTowQZXhwZW5zZV9ncm91cF9pZJROjAdiaWxsX2lklE6MCWNoZXF1ZV9pZJROjBBqb3VybmFsX2VudHJ5X2lklE6MF2NyZWRpdF9jYXJkX3B1cmNoYXNlX2lklE6MDnFib19leHBlbnNlX2lklE6MD2JpbGxfcGF5bWVudF9pZJROjAZzdGF0dXOUjAhDT01QTEVURZSMBmRldGFpbJR9lIwHbWVzc2FnZZSMF0NyZWF0aW5nIGV4cGVuc2UgZ3JvdXBzlHOMCmNyZWF0ZWRfYXSUjAhkYXRldGltZZSMCGRhdGV0aW1llJOUQwoH5gEbDDo4CIiolIwEcHl0epSMBF9VVEOUk5QpUpSGlFKUjBFxdWlja2Jvb2tzX2Vycm9yc5ROjAp1cGRhdGVkX2F0lGgqQwoH5gEbDDsAA/n/lGgvhpRSlIwPX2RqYW5nb192ZXJzaW9ulIwGMy4xLjEzlHVih5Qu	gAR9lC4=	gASVawIAAAAAAACMEnBpY2tsZWZpZWxkLmZpZWxkc5SMDl9PYmplY3RXcmFwcGVylJOUKYGUTn2UjARfb2JqlIwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoBowKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAJkYpSMB2RlZmF1bHSUjAZhZGRpbmeUiXVijAJpZJRLEowMd29ya3NwYWNlX2lklEsKjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowHYmlsbF9pZJROjAljaGVxdWVfaWSUTowQam91cm5hbF9lbnRyeV9pZJROjBdjcmVkaXRfY2FyZF9wdXJjaGFzZV9pZJROjA5xYm9fZXhwZW5zZV9pZJROjA9iaWxsX3BheW1lbnRfaWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YBGww6OAiIqJSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwRcXVpY2tib29rc19lcnJvcnOUTowKdXBkYXRlZF9hdJRoLkMKB+YBGww7AAP5/5RoM4aUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xM5R1YnOGlGIu	2022-01-27 12:58:56.60749+00	2022-01-27 12:59:00.275781+00	t	cc5a03dfaa374b3ea17f6ecba1bf5d71	\N	1
winner-paris-nuts-gee	apps.quickbooks_online.tasks.create_cheque	\N	gASVOQgAAAAAAACMFWRqYW5nby5kYi5tb2RlbHMuYmFzZZSMDm1vZGVsX3VucGlja2xllJOUjARmeWxllIwMRXhwZW5zZUdyb3VwlIaUhZRSlH2UKIwGX3N0YXRllGgAjApNb2RlbFN0YXRllJOUKYGUfZQojAxmaWVsZHNfY2FjaGWUfZSMBmNoZXF1ZZRoAowRcXVpY2tib29rc19vbmxpbmWUjAZDaGVxdWWUhpSFlFKUfZQojAZfc3RhdGWUaAspgZR9lCiMAmRilIwHZGVmYXVsdJRoDn2UjA1leHBlbnNlX2dyb3VwlGgHc4wGYWRkaW5nlIl1YowCaWSUSwGMEGV4cGVuc2VfZ3JvdXBfaWSUSw+MD2JhbmtfYWNjb3VudF9pZJSMAjM2lIwJZW50aXR5X2lklIwDMTA1lIwNZGVwYXJ0bWVudF9pZJROjBB0cmFuc2FjdGlvbl9kYXRllIwKMjAyMi0wMS0yN5SMCGN1cnJlbmN5lIwDVVNElIwMcHJpdmF0ZV9ub3RllIw3UmVpbWJ1cnNhYmxlIGV4cGVuc2UgYnkgYXNod2luLnRAZnlsZS5pbiBvbiAyMDIyLTAxLTI3IJSMCmNyZWF0ZWRfYXSUjAhkYXRldGltZZSMCGRhdGV0aW1llJOUQwoH5gEbDDsPDqEUlIwEcHl0epSMBF9VVEOUk5QpUpSGlFKUjAp1cGRhdGVkX2F0lGgvQwoH5gEbDDsPDqJVlGg0hpRSlIwPX2RqYW5nb192ZXJzaW9ulIwGMy4xLjEzlHVic2geiWgajAdkZWZhdWx0lHVijAJpZJRLD4wMd29ya3NwYWNlX2lklEsKjAtmdW5kX3NvdXJjZZSMCFBFUlNPTkFMlIwLZGVzY3JpcHRpb26UfZQojAlyZXBvcnRfaWSUjAxycHVsSHk1Z3hBTWyUjAtmdW5kX3NvdXJjZZSMCFBFUlNPTkFMlIwMY2xhaW1fbnVtYmVylIwOQy8yMDIyLzAxL1IvMTaUjA5lbXBsb3llZV9lbWFpbJSMEGFzaHdpbi50QGZ5bGUuaW6UdYwNcmVzcG9uc2VfbG9nc5R9lCiMCFB1cmNoYXNllH2UKIwKQWNjb3VudFJlZpR9lCiMBXZhbHVllIwCMzaUjARuYW1llIwHU2F2aW5nc5R1jAtQYXltZW50VHlwZZSMBUNoZWNrlIwJRW50aXR5UmVmlH2UKGhSjAMxMDWUaFSMCUNoZXRoYW4gTZSMBHR5cGWUjAhFbXBsb3llZZR1jAhUb3RhbEFtdJRHQFkAAAAAAACMC1ByaW50U3RhdHVzlIwGTm90U2V0lIwKUHVyY2hhc2VFeJR9lIwDYW55lF2UfZQoaFSMLntodHRwOi8vc2NoZW1hLmludHVpdC5jb20vZmluYW5jZS92M31OYW1lVmFsdWWUjAxkZWNsYXJlZFR5cGWUjCZjb20uaW50dWl0LnNjaGVtYS5maW5hbmNlLnYzLk5hbWVWYWx1ZZSMBXNjb3BllIwmamF2YXgueG1sLmJpbmQuSkFYQkVsZW1lbnQkR2xvYmFsU2NvcGWUaFJ9lCiMBE5hbWWUjAdUeG5UeXBllIwFVmFsdWWUjAEzlHWMA25pbJSJjAtnbG9iYWxTY29wZZSIjA90eXBlU3Vic3RpdHV0ZWSUiXVhc4wGZG9tYWlulIwDUUJPlIwGc3BhcnNllImMAklklIwEMjAwNZSMCVN5bmNUb2tlbpSMATCUjAhNZXRhRGF0YZR9lCiMCkNyZWF0ZVRpbWWUjBkyMDIyLTAxLTI3VDA0OjU5OjE4LTA4OjAwlIwPTGFzdFVwZGF0ZWRUaW1llIwZMjAyMi0wMS0yN1QwNDo1OToxOC0wODowMJR1jAtDdXN0b21GaWVsZJRdlIwHVHhuRGF0ZZSMCjIwMjItMDEtMjeUjAtDdXJyZW5jeVJlZpR9lChoUowDVVNElGhUjBRVbml0ZWQgU3RhdGVzIERvbGxhcpR1jAtQcml2YXRlTm90ZZSMNlJlaW1idXJzYWJsZSBleHBlbnNlIGJ5IGFzaHdpbi50QGZ5bGUuaW4gb24gMjAyMi0wMS0yN5SMBExpbmWUXZR9lChodowBMZSMC0Rlc2NyaXB0aW9ulIyYYXNod2luLnRAZnlsZS5pbiAtIEZvb2QgLSAyMDIyLTAxLTI3IC0gQy8yMDIyLzAxL1IvMTYgLSAgLSBodHRwczovL3N0YWdpbmcuZnlsZS50ZWNoL2FwcC9tYWluLyMvZW50ZXJwcmlzZS92aWV3X2V4cGVuc2UvdHh0Sks1T2FnMXVKP29yZ19pZD1vcmsyYzkwUEFIdGuUjAZBbW91bnSUR0BZAAAAAAAAjApEZXRhaWxUeXBllIwdQWNjb3VudEJhc2VkRXhwZW5zZUxpbmVEZXRhaWyUjB1BY2NvdW50QmFzZWRFeHBlbnNlTGluZURldGFpbJR9lChoUH2UKGhSjAIxMZRoVIwJSW5zdXJhbmNllHWMDkJpbGxhYmxlU3RhdHVzlIwLTm90QmlsbGFibGWUjApUYXhDb2RlUmVmlH2UaFKMA05PTpRzdXVhdYwEdGltZZSMHTIwMjItMDEtMjdUMDQ6NTk6MTguMjc2LTA4OjAwlHWMCmNyZWF0ZWRfYXSUaC9DCgfmARsMOwABaBSUaDSGlFKUjAtleHBvcnRlZF9hdJRoL0MKB+YBGww7EgV2+JSFlFKUjAp1cGRhdGVkX2F0lGgvQwoH5gEbDDsSBXhSlGg0hpRSlIwPX2RqYW5nb192ZXJzaW9ulGg8dWJLE4aULg==	gAR9lC4=	\N	2022-01-27 12:59:13.578689+00	2022-01-27 12:59:18.948269+00	t	d8044b61546c46d2988cc2765335b88c	521d817e3b9f4a9e8bddf84415cbcfaf	1
fourteen-king-july-india	apps.quickbooks_online.tasks.async_sync_accounts	\N	gASVBQAAAAAAAABLCIWULg==	gAR9lC4=	\N	2022-02-02 05:59:11.630144+00	2022-02-02 05:59:16.654162+00	t	45ecab4fbf4c4acbb4fb0a283994f23c	\N	1
low-undress-low-april	apps.quickbooks_online.tasks.async_sync_accounts	\N	gASVBQAAAAAAAABLCYWULg==	gAR9lC4=	\N	2022-02-02 11:46:34.087323+00	2022-02-02 11:46:39.491333+00	t	6f494810775a4388b98d22683a7f3c7e	\N	1
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
\.


--
-- Data for Name: employee_mappings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employee_mappings (id, created_at, updated_at, destination_card_account_id, destination_employee_id, destination_vendor_id, source_employee_id, workspace_id) FROM stdin;
5	2022-01-21 10:40:25.085006+00	2022-01-21 10:40:25.085158+00	1100	1226	\N	6968	8
6	2022-01-21 10:43:10.008094+00	2022-01-21 10:43:10.008172+00	1423	\N	1529	8689	9
\.


--
-- Data for Name: expense_attributes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expense_attributes (id, attribute_type, display_name, value, source_id, created_at, updated_at, workspace_id, active, detail, auto_mapped, auto_created) FROM stdin;
6955	EMPLOYEE	Employee	approver1@fyleforgotham.in	ouMvD0iJ0pXK	2022-01-21 10:37:00.779302+00	2022-01-21 10:37:00.779347+00	8	\N	{"location": null, "full_name": "Ryan Gallagher", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
6956	EMPLOYEE	Employee	owner@fyleforgotham.in	ouT4EarnaThA	2022-01-21 10:37:00.779425+00	2022-01-21 10:37:00.779455+00	8	\N	{"location": null, "full_name": "Fyle For Arkham Asylum", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
6957	EMPLOYEE	Employee	admin1@fyleforgotham.in	ouECRFhw3AjY	2022-01-21 10:37:00.779533+00	2022-01-21 10:37:00.779557+00	8	\N	{"location": null, "full_name": "Theresa Brown", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
6958	EMPLOYEE	Employee	user10@fyleforgotham.in	ou7yyjvEaliS	2022-01-21 10:37:00.784913+00	2022-01-21 10:37:00.784988+00	8	\N	{"location": null, "full_name": "Matthew Estrada", "department": "Department 4", "department_id": "depttugt5POp4K", "employee_code": null, "department_code": null}	f	f
6959	EMPLOYEE	Employee	user1@fyleforgotham.in	ouVT4YfloipJ	2022-01-21 10:37:00.785185+00	2022-01-21 10:37:00.785244+00	8	\N	{"location": null, "full_name": "Joshua Wood", "department": "Department 2", "department_id": "deptgZF9aUB0tH", "employee_code": null, "department_code": null}	f	f
6960	EMPLOYEE	Employee	user2@fyleforgotham.in	ou8TYuw4AxVG	2022-01-21 10:37:00.785408+00	2022-01-21 10:37:00.785462+00	8	\N	{"location": null, "full_name": "Brian Foster", "department": "Department 1", "department_id": "deptDhMjvs45aT", "employee_code": null, "department_code": null}	f	f
6961	EMPLOYEE	Employee	user3@fyleforgotham.in	ounUmTSUyiHX	2022-01-21 10:37:00.78562+00	2022-01-21 10:37:00.785669+00	8	\N	{"location": null, "full_name": "Natalie Pope", "department": "Department 1", "department_id": "deptDhMjvs45aT", "employee_code": null, "department_code": null}	f	f
6962	EMPLOYEE	Employee	user4@fyleforgotham.in	ouEetwpFkf3F	2022-01-21 10:37:00.78607+00	2022-01-21 10:37:00.797071+00	8	\N	{"location": null, "full_name": "Samantha Washington", "department": "Department 3", "department_id": "dept0DswoMIby7", "employee_code": null, "department_code": null}	f	f
6963	EMPLOYEE	Employee	user5@fyleforgotham.in	ouwVEj13iF6S	2022-01-21 10:37:00.79734+00	2022-01-21 10:37:00.7974+00	8	\N	{"location": null, "full_name": "Chris Curtis", "department": "Department 1", "department_id": "deptDhMjvs45aT", "employee_code": null, "department_code": null}	f	f
6964	EMPLOYEE	Employee	user6@fyleforgotham.in	ou5XWYQjmzym	2022-01-21 10:37:00.797566+00	2022-01-21 10:37:00.797615+00	8	\N	{"location": null, "full_name": "Victor Martinez", "department": "Department 3", "department_id": "dept0DswoMIby7", "employee_code": null, "department_code": null}	f	f
6965	EMPLOYEE	Employee	user7@fyleforgotham.in	ouT8HYOj1GYZ	2022-01-21 10:37:00.797769+00	2022-01-21 10:37:00.797816+00	8	\N	{"location": null, "full_name": "James Taylor", "department": "Department 4", "department_id": "depttugt5POp4K", "employee_code": null, "department_code": null}	f	f
6966	EMPLOYEE	Employee	user8@fyleforgotham.in	ouZF0bfmC1DV	2022-01-21 10:37:00.797948+00	2022-01-21 10:37:00.797991+00	8	\N	{"location": null, "full_name": "Jessica Lane", "department": "Department 2", "department_id": "deptgZF9aUB0tH", "employee_code": null, "department_code": null}	f	f
6967	EMPLOYEE	Employee	user9@fyleforgotham.in	ouh41Vnv7pl3	2022-01-21 10:37:00.798112+00	2022-01-21 10:37:00.798152+00	8	\N	{"location": null, "full_name": "Justin Glass", "department": "Department 3", "department_id": "dept0DswoMIby7", "employee_code": null, "department_code": null}	f	f
8689	EMPLOYEE	Employee	ashwin.t@fyle.in	ou02H42PvOg3	2022-01-21 10:42:20.695083+00	2022-01-21 10:43:09.649243+00	9	\N	{"location": null, "full_name": "Ashwin", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
6969	EMPLOYEE	Employee	nilesh.p@fyle.in	ouYbK261N8dp	2022-01-21 10:37:00.798496+00	2022-01-21 10:37:00.798535+00	8	\N	{"location": null, "full_name": "Nilesh Pant", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
6970	EMPLOYEE	Employee	nilesh.p+123@fyle.in	ouEPFtpfacUg	2022-01-21 10:37:00.798641+00	2022-01-21 10:37:00.798678+00	8	\N	{"location": null, "full_name": "Brad Pitt", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
6971	EMPLOYEE	Employee	nilesh.p+167@fyle.in	oufShLZ4Yvn3	2022-01-21 10:37:00.798779+00	2022-01-21 10:37:00.798815+00	8	\N	{"location": null, "full_name": "Vikrant Messi", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
6972	EMPLOYEE	Employee	hashirama@fyle.in	oumsHGfTBQiY	2022-01-21 10:37:00.798915+00	2022-01-21 10:37:00.798952+00	8	\N	{"location": null, "full_name": "hashirama", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
6973	EMPLOYEE	Employee	kite@fyle.in	oukW6LvoLNOC	2022-01-21 10:37:00.799052+00	2022-01-21 10:37:00.799088+00	8	\N	{"location": "", "full_name": "kite frecks", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
6974	EMPLOYEE	Employee	killua123@fyle.in	oudKdfEpPpUG	2022-01-21 10:37:00.799199+00	2022-01-21 10:37:00.799236+00	8	\N	{"location": "", "full_name": "Killua Zoldyc", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
6975	EMPLOYEE	Employee	hanibal@workato.com	ouForZnYcDzO	2022-01-21 10:37:00.799336+00	2022-01-21 10:37:00.799372+00	8	\N	{"location": "", "full_name": "Hanibal Lecter", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
6976	EMPLOYEE	Employee	shwetabh.kumar+1@fylehq.com	ouww9RIBEJSW	2022-01-21 10:37:00.799471+00	2022-01-21 10:37:00.799507+00	8	\N	{"location": "", "full_name": "Shwetabh", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
6977	EMPLOYEE	Employee	ilumi_1@fyle.in	ou2An2y637sy	2022-01-21 10:37:00.799606+00	2022-01-21 10:37:00.799643+00	8	\N	{"location": "", "full_name": "ilumi Zoldyc", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
6978	EMPLOYEE	Employee	labhvam+9@fyle.in	ouBmZxuJqGZI	2022-01-21 10:37:00.805717+00	2022-01-21 10:37:00.823289+00	8	\N	{"location": "", "full_name": "labhvamkr Sharma", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
6979	EMPLOYEE	Employee	labhvam+10@fyle.in	oux1yMQ91ETl	2022-01-21 10:37:00.824353+00	2022-01-21 10:37:00.824433+00	8	\N	{"location": "", "full_name": "labhvam10 Sharma", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
6980	EMPLOYEE	Employee	labhvam.s@fyle.com	ousR4RigHnI6	2022-01-21 10:37:00.824972+00	2022-01-21 10:37:00.825018+00	8	\N	{"location": "", "full_name": "Labhvamsharma", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
6981	EMPLOYEE	Employee	Killua.Z@fyle.in	oufhahwwM02b	2022-01-21 10:37:00.82513+00	2022-01-21 10:37:00.82517+00	8	\N	{"location": "", "full_name": "Killua Zoldyc", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
6982	EMPLOYEE	Employee	labhvam.s+1@fyle.in	ouIYlo36Npdm	2022-01-21 10:37:00.825277+00	2022-01-21 10:37:00.825316+00	8	\N	{"location": "", "full_name": "labhvamnew Sharma", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
6983	EMPLOYEE	Employee	killua@fyle.in	ouhZBgEWP90t	2022-01-21 10:37:00.825441+00	2022-01-21 10:37:00.825487+00	8	\N	{"location": "", "full_name": "labhvam", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
6984	EMPLOYEE	Employee	labhvam.s+2@fyle.in	ouSteuezQoZs	2022-01-21 10:37:00.825711+00	2022-01-21 10:37:00.825752+00	8	\N	{"location": "", "full_name": "labhvam2 Sharma", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
7050	CATEGORY	Category	COGS-Overhead on Projects	135563	2022-01-21 10:37:02.212406+00	2022-01-21 10:37:02.212464+00	8	\N	\N	f	f
6985	EMPLOYEE	Employee	labhvamkrsharma@gmail.com	outWTYTJiL2p	2022-01-21 10:37:00.82586+00	2022-01-21 10:37:00.825901+00	8	\N	{"location": "", "full_name": "Labham Sharma", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
6986	EMPLOYEE	Employee		oumBCPU68YiS	2022-01-21 10:37:00.826007+00	2022-01-21 10:37:00.826047+00	8	\N	{"location": "", "full_name": "Clarissa Jones", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
6987	EMPLOYEE	Employee	abhishek.j@fyle.in	ouPZdJlwhyrI	2022-01-21 10:37:00.826154+00	2022-01-21 10:37:00.826193+00	8	\N	{"location": null, "full_name": "abhishek jain", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
6988	EMPLOYEE	Employee	john.doe@fyle.in	ou0eP8IVezUa	2022-01-21 10:37:00.8263+00	2022-01-21 10:37:00.826342+00	8	\N	{"location": "", "full_name": "John Doe", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
6989	EMPLOYEE	Employee	neji.h@fyle.in	ou7A6PKctCRh	2022-01-21 10:37:00.826453+00	2022-01-21 10:37:00.826494+00	8	\N	{"location": "", "full_name": "neji smith", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
6990	EMPLOYEE	Employee	henry.s@fyle.in	ouOIRWYxnyk6	2022-01-21 10:37:00.826604+00	2022-01-21 10:37:00.826646+00	8	\N	{"location": "", "full_name": "Henry Doe", "department": null, "department_id": null, "employee_code": "", "department_code": null}	f	f
6991	CATEGORY	Category	ABN Withholding	157849	2022-01-21 10:37:02.127996+00	2022-01-21 10:37:02.128041+00	8	\N	\N	f	f
6992	CATEGORY	Category	Accm.Depr. Furniture & Fixtures	135613	2022-01-21 10:37:02.128106+00	2022-01-21 10:37:02.128136+00	8	\N	\N	f	f
6993	CATEGORY	Category	Accounting	135912	2022-01-21 10:37:02.128198+00	2022-01-21 10:37:02.128228+00	8	\N	\N	f	f
6994	CATEGORY	Category	Accounts Payable	135644	2022-01-21 10:37:02.128289+00	2022-01-21 10:37:02.128318+00	8	\N	\N	f	f
6995	CATEGORY	Category	Accounts Payable - Employees	135643	2022-01-21 10:37:02.128379+00	2022-01-21 10:37:02.128409+00	8	\N	\N	f	f
6996	CATEGORY	Category	Accounts Receivable	135641	2022-01-21 10:37:02.128471+00	2022-01-21 10:37:02.1285+00	8	\N	\N	f	f
6997	CATEGORY	Category	Accounts Receivable - Other	135642	2022-01-21 10:37:02.128575+00	2022-01-21 10:37:02.128604+00	8	\N	\N	f	f
6998	CATEGORY	Category	Accrued Payroll Tax Payable	135579	2022-01-21 10:37:02.128666+00	2022-01-21 10:37:02.128695+00	8	\N	\N	f	f
6999	CATEGORY	Category	Accrued Sales Tax Payable	135580	2022-01-21 10:37:02.128756+00	2022-01-21 10:37:02.128785+00	8	\N	\N	f	f
7000	CATEGORY	Category	Accumulated OCI	135547	2022-01-21 10:37:02.128847+00	2022-01-21 10:37:02.129062+00	8	\N	\N	f	f
7001	CATEGORY	Category	Activity	135444	2022-01-21 10:37:02.129189+00	2022-01-21 10:37:02.129222+00	8	\N	\N	f	f
7002	CATEGORY	Category	Actual Landed Costs	135578	2022-01-21 10:37:02.129284+00	2022-01-21 10:37:02.129314+00	8	\N	\N	f	f
7003	CATEGORY	Category	Advances Paid	135908	2022-01-21 10:37:02.129375+00	2022-01-21 10:37:02.129405+00	8	\N	\N	f	f
7004	CATEGORY	Category	Advertising	135716	2022-01-21 10:37:02.129466+00	2022-01-21 10:37:02.129499+00	8	\N	\N	f	f
7005	CATEGORY	Category	Advertising/Promotional	161875	2022-01-21 10:37:02.130166+00	2022-01-21 10:37:02.130235+00	8	\N	\N	f	f
7006	CATEGORY	Category	Airfare	135796	2022-01-21 10:37:02.130376+00	2022-01-21 10:37:02.130423+00	8	\N	\N	f	f
7007	CATEGORY	Category	Allocations	135549	2022-01-21 10:37:02.130527+00	2022-01-21 10:37:02.130572+00	8	\N	\N	f	f
7008	CATEGORY	Category	Allowance For Doubtful Accounts	135570	2022-01-21 10:37:02.130681+00	2022-01-21 10:37:02.130722+00	8	\N	\N	f	f
7009	CATEGORY	Category	Amortisation (and depreciation) expense	147479	2022-01-21 10:37:02.13082+00	2022-01-21 10:37:02.13086+00	8	\N	\N	f	f
7010	CATEGORY	Category	Amortization Expense	135623	2022-01-21 10:37:02.130955+00	2022-01-21 10:37:02.130994+00	8	\N	\N	f	f
7011	CATEGORY	Category	AR-Retainage	135640	2022-01-21 10:37:02.131088+00	2022-01-21 10:37:02.131128+00	8	\N	\N	f	f
7012	CATEGORY	Category	ash	135946	2022-01-21 10:37:02.13122+00	2022-01-21 10:37:02.131259+00	8	\N	\N	f	f
7013	CATEGORY	Category	ASHWIN MANUALLY ADDED THIS	135647	2022-01-21 10:37:02.131351+00	2022-01-21 10:37:02.131389+00	8	\N	\N	f	f
7014	CATEGORY	Category	ASHWIN MANUALLY ADDED THIS2	135550	2022-01-21 10:37:02.13148+00	2022-01-21 10:37:02.131518+00	8	\N	\N	f	f
7015	CATEGORY	Category	Aus Category	149228	2022-01-21 10:37:02.13161+00	2022-01-21 10:37:02.131648+00	8	\N	\N	f	f
7016	CATEGORY	Category	Automobile	135717	2022-01-21 10:37:02.13174+00	2022-01-21 10:37:02.131778+00	8	\N	\N	f	f
7017	CATEGORY	Category	Automobile Expense	135879	2022-01-21 10:37:02.131869+00	2022-01-21 10:37:02.131907+00	8	\N	\N	f	f
7018	CATEGORY	Category	Automobile:Fuel	135718	2022-01-21 10:37:02.131997+00	2022-01-21 10:37:02.132036+00	8	\N	\N	f	f
7019	CATEGORY	Category	Bad Debt Expense	135544	2022-01-21 10:37:02.132126+00	2022-01-21 10:37:02.132163+00	8	\N	\N	f	f
7020	CATEGORY	Category	Bad debts	147480	2022-01-21 10:37:02.132402+00	2022-01-21 10:37:02.132441+00	8	\N	\N	f	f
7021	CATEGORY	Category	Bank Charges	135543	2022-01-21 10:37:02.132533+00	2022-01-21 10:37:02.132572+00	8	\N	\N	f	f
7022	CATEGORY	Category	Bank Fees	135991	2022-01-21 10:37:02.132813+00	2022-01-21 10:37:02.132857+00	8	\N	\N	f	f
7023	CATEGORY	Category	Bank Revaluations	136007	2022-01-21 10:37:02.132954+00	2022-01-21 10:37:02.132993+00	8	\N	\N	f	f
7024	CATEGORY	Category	Bank Service Charges	135882	2022-01-21 10:37:02.133085+00	2022-01-21 10:37:02.13313+00	8	\N	\N	f	f
7025	CATEGORY	Category	BAS Expense	147482	2022-01-21 10:37:02.133521+00	2022-01-21 10:37:02.13357+00	8	\N	\N	f	f
7026	CATEGORY	Category	Bill Exchange Rate Variance	135923	2022-01-21 10:37:02.133809+00	2022-01-21 10:37:02.133855+00	8	\N	\N	f	f
7027	CATEGORY	Category	Bill Price Variance	135922	2022-01-21 10:37:02.133957+00	2022-01-21 10:37:02.133998+00	8	\N	\N	f	f
7028	CATEGORY	Category	Bill Quantity Variance	135921	2022-01-21 10:37:02.134092+00	2022-01-21 10:37:02.13413+00	8	\N	\N	f	f
7029	CATEGORY	Category	Buildings	135539	2022-01-21 10:37:02.134224+00	2022-01-21 10:37:02.134263+00	8	\N	\N	f	f
7030	CATEGORY	Category	Buildings Accm.Depr.	135609	2022-01-21 10:37:02.134353+00	2022-01-21 10:37:02.134391+00	8	\N	\N	f	f
7031	CATEGORY	Category	Build Price Variance	135934	2022-01-21 10:37:02.134482+00	2022-01-21 10:37:02.13452+00	8	\N	\N	f	f
7032	CATEGORY	Category	Build Quantity Variance	135935	2022-01-21 10:37:02.144872+00	2022-01-21 10:37:02.145013+00	8	\N	\N	f	f
7033	CATEGORY	Category	Bus	135455	2022-01-21 10:37:02.145579+00	2022-01-21 10:37:02.146028+00	8	\N	\N	f	f
7034	CATEGORY	Category	Business	135898	2022-01-21 10:37:02.146222+00	2022-01-21 10:37:02.146284+00	8	\N	\N	f	f
7035	CATEGORY	Category	Capitalized Software Costs	135608	2022-01-21 10:37:02.146391+00	2022-01-21 10:37:02.146431+00	8	\N	\N	f	f
7036	CATEGORY	Category	Cash	135601	2022-01-21 10:37:02.146677+00	2022-01-21 10:37:02.146728+00	8	\N	\N	f	f
7037	CATEGORY	Category	Cash Equivalents	135602	2022-01-21 10:37:02.146838+00	2022-01-21 10:37:02.146881+00	8	\N	\N	f	f
7038	CATEGORY	Category	Cell phone	137946	2022-01-21 10:37:02.146981+00	2022-01-21 10:37:02.147024+00	8	\N	\N	f	f
7039	CATEGORY	Category	Cellular	135904	2022-01-21 10:37:02.147133+00	2022-01-21 10:37:02.147173+00	8	\N	\N	f	f
7040	CATEGORY	Category	Cellular Phone	135792	2022-01-21 10:37:02.147273+00	2022-01-21 10:37:02.147313+00	8	\N	\N	f	f
7041	CATEGORY	Category	Checking	162001	2022-01-21 10:37:02.210022+00	2022-01-21 10:37:02.210103+00	8	\N	\N	f	f
7042	CATEGORY	Category	Cleaning	135992	2022-01-21 10:37:02.210196+00	2022-01-21 10:37:02.210273+00	8	\N	\N	f	f
7043	CATEGORY	Category	COGS-Billable Hours	135558	2022-01-21 10:37:02.210681+00	2022-01-21 10:37:02.210766+00	8	\N	\N	f	f
7044	CATEGORY	Category	COGS-Burden on Projects	135562	2022-01-21 10:37:02.210973+00	2022-01-21 10:37:02.211018+00	8	\N	\N	f	f
7045	CATEGORY	Category	COGS-Damage, Scrap, Spoilage	135635	2022-01-21 10:37:02.211118+00	2022-01-21 10:37:02.21121+00	8	\N	\N	f	f
7046	CATEGORY	Category	COGS-G&A on Projects	135564	2022-01-21 10:37:02.211324+00	2022-01-21 10:37:02.211363+00	8	\N	\N	f	f
7047	CATEGORY	Category	COGS-Indirect projects Costs Offset	135565	2022-01-21 10:37:02.211755+00	2022-01-21 10:37:02.21181+00	8	\N	\N	f	f
7048	CATEGORY	Category	COGS-Non-Billable Hours	135561	2022-01-21 10:37:02.21192+00	2022-01-21 10:37:02.211958+00	8	\N	\N	f	f
7049	CATEGORY	Category	COGS-Other	135569	2022-01-21 10:37:02.212176+00	2022-01-21 10:37:02.212227+00	8	\N	\N	f	f
7124	CATEGORY	Category	Insurance	135591	2022-01-21 10:37:02.634511+00	2022-01-21 10:37:02.634548+00	8	\N	\N	f	f
7051	CATEGORY	Category	COGS-Reimbursed Expenses	135566	2022-01-21 10:37:02.212748+00	2022-01-21 10:37:02.212798+00	8	\N	\N	f	f
7052	CATEGORY	Category	COGS Sales	135634	2022-01-21 10:37:02.213913+00	2022-01-21 10:37:02.214011+00	8	\N	\N	f	f
7053	CATEGORY	Category	COGS Services	135557	2022-01-21 10:37:02.226085+00	2022-01-21 10:37:02.226205+00	8	\N	\N	f	f
7054	CATEGORY	Category	Commission	135554	2022-01-21 10:37:02.227311+00	2022-01-21 10:37:02.227372+00	8	\N	\N	f	f
7055	CATEGORY	Category	Commissions and fees	147483	2022-01-21 10:37:02.227472+00	2022-01-21 10:37:02.227577+00	8	\N	\N	f	f
7056	CATEGORY	Category	Commissions & fees	135719	2022-01-21 10:37:02.227861+00	2022-01-21 10:37:02.227909+00	8	\N	\N	f	f
7057	CATEGORY	Category	Common Stock	135631	2022-01-21 10:37:02.227983+00	2022-01-21 10:37:02.228014+00	8	\N	\N	f	f
7058	CATEGORY	Category	Communication Expense - Fixed	147484	2022-01-21 10:37:02.22807+00	2022-01-21 10:37:02.228092+00	8	\N	\N	f	f
7059	CATEGORY	Category	Company Credit Card Offset	135581	2022-01-21 10:37:02.228154+00	2022-01-21 10:37:02.231071+00	8	\N	\N	f	f
7060	CATEGORY	Category	Consulting & Accounting	135993	2022-01-21 10:37:02.231199+00	2022-01-21 10:37:02.231231+00	8	\N	\N	f	f
7061	CATEGORY	Category	Contributions	135883	2022-01-21 10:37:02.231295+00	2022-01-21 10:37:02.231326+00	8	\N	\N	f	f
7062	CATEGORY	Category	Cost of Goods Sold	135910	2022-01-21 10:37:02.231388+00	2022-01-21 10:37:02.231418+00	8	\N	\N	f	f
7063	CATEGORY	Category	Courier	135458	2022-01-21 10:37:02.231479+00	2022-01-21 10:37:02.231508+00	8	\N	\N	f	f
7064	CATEGORY	Category	Customer Return Variance	135937	2022-01-21 10:37:02.23157+00	2022-01-21 10:37:02.231599+00	8	\N	\N	f	f
7065	CATEGORY	Category	Damaged Goods	135918	2022-01-21 10:37:02.23166+00	2022-01-21 10:37:02.23169+00	8	\N	\N	f	f
7066	CATEGORY	Category	Deferred Revenue	135615	2022-01-21 10:37:02.231751+00	2022-01-21 10:37:02.231781+00	8	\N	\N	f	f
7067	CATEGORY	Category	Deferred Revenue Contra	135614	2022-01-21 10:37:02.231842+00	2022-01-21 10:37:02.231872+00	8	\N	\N	f	f
7068	CATEGORY	Category	Depreciation	135994	2022-01-21 10:37:02.231933+00	2022-01-21 10:37:02.231963+00	8	\N	\N	f	f
7069	CATEGORY	Category	Depreciation Expense	135585	2022-01-21 10:37:02.232024+00	2022-01-21 10:37:02.232054+00	8	\N	\N	f	f
7070	CATEGORY	Category	Description about 00	137942	2022-01-21 10:37:02.232115+00	2022-01-21 10:37:02.232145+00	8	\N	\N	f	f
7071	CATEGORY	Category	Description about ASHWIN MANUALLY ADDED THIS	137943	2022-01-21 10:37:02.232207+00	2022-01-21 10:37:02.232236+00	8	\N	\N	f	f
7072	CATEGORY	Category	Description about ASHWIN MANUALLY ADDED THIS2	137944	2022-01-21 10:37:02.232298+00	2022-01-21 10:37:02.232327+00	8	\N	\N	f	f
7073	CATEGORY	Category	Disability	135888	2022-01-21 10:37:02.232389+00	2022-01-21 10:37:02.232418+00	8	\N	\N	f	f
7074	CATEGORY	Category	Disposal Fees	135720	2022-01-21 10:37:02.232479+00	2022-01-21 10:37:02.232509+00	8	\N	\N	f	f
7075	CATEGORY	Category	Dividends	135597	2022-01-21 10:37:02.23257+00	2022-01-21 10:37:02.232599+00	8	\N	\N	f	f
7076	CATEGORY	Category	Due from Entity 100	135606	2022-01-21 10:37:02.23266+00	2022-01-21 10:37:02.23269+00	8	\N	\N	f	f
7077	CATEGORY	Category	Due from Entity 200	135604	2022-01-21 10:37:02.232752+00	2022-01-21 10:37:02.232782+00	8	\N	\N	f	f
7078	CATEGORY	Category	Due from Entity 300	135605	2022-01-21 10:37:02.232843+00	2022-01-21 10:37:02.232872+00	8	\N	\N	f	f
7079	CATEGORY	Category	Dues and Expenses from Intacct	141657	2022-01-21 10:37:02.232934+00	2022-01-21 10:37:02.232963+00	8	\N	\N	f	f
7080	CATEGORY	Category	Dues and Subscriptions	136468	2022-01-21 10:37:02.233024+00	2022-01-21 10:37:02.233054+00	8	\N	\N	f	f
7081	CATEGORY	Category	Dues Expenses from Intacct	141965	2022-01-21 10:37:02.233116+00	2022-01-21 10:37:02.233725+00	8	\N	\N	f	f
7082	CATEGORY	Category	Dues & Subscriptions	135721	2022-01-21 10:37:02.233899+00	2022-01-21 10:37:02.233951+00	8	\N	\N	f	f
7083	CATEGORY	Category	Due to Entity 100	135617	2022-01-21 10:37:02.23407+00	2022-01-21 10:37:02.234117+00	8	\N	\N	f	f
7084	CATEGORY	Category	Due to Entity 200	135618	2022-01-21 10:37:02.234217+00	2022-01-21 10:37:02.234257+00	8	\N	\N	f	f
7085	CATEGORY	Category	Due to Entity 300	135616	2022-01-21 10:37:02.234366+00	2022-01-21 10:37:02.234408+00	8	\N	\N	f	f
7086	CATEGORY	Category	Duty Expense	135915	2022-01-21 10:37:02.234514+00	2022-01-21 10:37:02.234556+00	8	\N	\N	f	f
7087	CATEGORY	Category	Emma	146043	2022-01-21 10:37:02.234656+00	2022-01-21 10:37:02.234698+00	8	\N	\N	f	f
7088	CATEGORY	Category	Employee Advances	135574	2022-01-21 10:37:02.234815+00	2022-01-21 10:37:02.293796+00	8	\N	\N	f	f
7089	CATEGORY	Category	Employee Benefits	135553	2022-01-21 10:37:02.296182+00	2022-01-21 10:37:02.296228+00	8	\N	\N	f	f
7090	CATEGORY	Category	Employee Deductions	135583	2022-01-21 10:37:02.298786+00	2022-01-21 10:37:02.298832+00	8	\N	\N	f	f
7091	CATEGORY	Category	Entertainment	135450	2022-01-21 10:37:02.585609+00	2022-01-21 10:37:02.590524+00	8	\N	\N	f	f
7092	CATEGORY	Category	Equipment	137947	2022-01-21 10:37:02.594508+00	2022-01-21 10:37:02.594559+00	8	\N	\N	f	f
7093	CATEGORY	Category	Equipment Rental	135722	2022-01-21 10:37:02.601119+00	2022-01-21 10:37:02.601179+00	8	\N	\N	f	f
7094	CATEGORY	Category	Estimated Landed Costs	135577	2022-01-21 10:37:02.60128+00	2022-01-21 10:37:02.601319+00	8	\N	\N	f	f
7095	CATEGORY	Category	Exchange Rate Variance	135914	2022-01-21 10:37:02.60141+00	2022-01-21 10:37:02.601448+00	8	\N	\N	f	f
7096	CATEGORY	Category	Excise Tax	135636	2022-01-21 10:37:02.601538+00	2022-01-21 10:37:02.601576+00	8	\N	\N	f	f
7097	CATEGORY	Category	expense category	135797	2022-01-21 10:37:02.601665+00	2022-01-21 10:37:02.601703+00	8	\N	\N	f	f
7098	CATEGORY	Category	Flight	135463	2022-01-21 10:37:02.60179+00	2022-01-21 10:37:02.601829+00	8	\N	\N	f	f
7099	CATEGORY	Category	Food	135453	2022-01-21 10:37:02.606239+00	2022-01-21 10:37:02.606392+00	8	\N	\N	f	f
7100	CATEGORY	Category	Freight & Courier	135995	2022-01-21 10:37:02.610321+00	2022-01-21 10:37:02.610381+00	8	\N	\N	f	f
7101	CATEGORY	Category	Freight & Delivery	135884	2022-01-21 10:37:02.610496+00	2022-01-21 10:37:02.610541+00	8	\N	\N	f	f
7102	CATEGORY	Category	Freight Expense	135916	2022-01-21 10:37:02.612131+00	2022-01-21 10:37:02.61223+00	8	\N	\N	f	f
7103	CATEGORY	Category	Fuel	135446	2022-01-21 10:37:02.619053+00	2022-01-21 10:37:02.619208+00	8	\N	\N	f	f
7104	CATEGORY	Category	Furniture & Fixtures	135612	2022-01-21 10:37:02.627479+00	2022-01-21 10:37:02.627553+00	8	\N	\N	f	f
7105	CATEGORY	Category	Furniture & Fixtures Expense	135911	2022-01-21 10:37:02.627693+00	2022-01-21 10:37:02.627739+00	8	\N	\N	f	f
7106	CATEGORY	Category	Furniture for the department	137945	2022-01-21 10:37:02.629004+00	2022-01-21 10:37:02.629614+00	8	\N	\N	f	f
7107	CATEGORY	Category	Fyle	135551	2022-01-21 10:37:02.630152+00	2022-01-21 10:37:02.630213+00	8	\N	\N	f	f
7108	CATEGORY	Category	Fyleasdads	135648	2022-01-21 10:37:02.630344+00	2022-01-21 10:37:02.632398+00	8	\N	\N	f	f
7109	CATEGORY	Category	Fyle Expenses	135652	2022-01-21 10:37:02.632581+00	2022-01-21 10:37:02.63263+00	8	\N	\N	f	f
7110	CATEGORY	Category	Fyle Expenses!	135655	2022-01-21 10:37:02.632739+00	2022-01-21 10:37:02.63278+00	8	\N	\N	f	f
7111	CATEGORY	Category	Gain for Sale of an asset	135596	2022-01-21 10:37:02.632881+00	2022-01-21 10:37:02.632921+00	8	\N	\N	f	f
7112	CATEGORY	Category	Gain (loss) on Sale of Assets	135906	2022-01-21 10:37:02.633017+00	2022-01-21 10:37:02.633055+00	8	\N	\N	f	f
7113	CATEGORY	Category	Gas & Oil	135880	2022-01-21 10:37:02.633149+00	2022-01-21 10:37:02.633187+00	8	\N	\N	f	f
7114	CATEGORY	Category	General Expenses	135996	2022-01-21 10:37:02.633281+00	2022-01-21 10:37:02.633318+00	8	\N	\N	f	f
7115	CATEGORY	Category	Goods in Transit	135548	2022-01-21 10:37:02.633408+00	2022-01-21 10:37:02.633445+00	8	\N	\N	f	f
7116	CATEGORY	Category	Goods Received Not Invoiced (GRNI)	135576	2022-01-21 10:37:02.633534+00	2022-01-21 10:37:02.633571+00	8	\N	\N	f	f
7117	CATEGORY	Category	Goodwill	135584	2022-01-21 10:37:02.633659+00	2022-01-21 10:37:02.633695+00	8	\N	\N	f	f
7118	CATEGORY	Category	Ground Transportation-Parking	149332	2022-01-21 10:37:02.633781+00	2022-01-21 10:37:02.633818+00	8	\N	\N	f	f
7119	CATEGORY	Category	GST Paid	157846	2022-01-21 10:37:02.633903+00	2022-01-21 10:37:02.63394+00	8	\N	\N	f	f
7120	CATEGORY	Category	Hotel	135459	2022-01-21 10:37:02.634025+00	2022-01-21 10:37:02.634062+00	8	\N	\N	f	f
7121	CATEGORY	Category	Hotel-Lodging	149333	2022-01-21 10:37:02.634147+00	2022-01-21 10:37:02.634184+00	8	\N	\N	f	f
7122	CATEGORY	Category	Income Tax Expense	136010	2022-01-21 10:37:02.634269+00	2022-01-21 10:37:02.634305+00	8	\N	\N	f	f
7123	CATEGORY	Category	Incremental Account	135723	2022-01-21 10:37:02.634389+00	2022-01-21 10:37:02.634426+00	8	\N	\N	f	f
7125	CATEGORY	Category	Insurance - Disability	147488	2022-01-21 10:37:02.634633+00	2022-01-21 10:37:02.634669+00	8	\N	\N	f	f
7126	CATEGORY	Category	Insurance Expense	135885	2022-01-21 10:37:02.634755+00	2022-01-21 10:37:02.634791+00	8	\N	\N	f	f
7127	CATEGORY	Category	Insurance - General	147489	2022-01-21 10:37:02.634877+00	2022-01-21 10:37:02.634913+00	8	\N	\N	f	f
7128	CATEGORY	Category	Insurance - Liability	147490	2022-01-21 10:37:02.647579+00	2022-01-21 10:37:02.647628+00	8	\N	\N	f	f
7129	CATEGORY	Category	Insurance:Workers Compensation	135754	2022-01-21 10:37:02.647715+00	2022-01-21 10:37:02.647745+00	8	\N	\N	f	f
7130	CATEGORY	Category	Integration Test Account	135794	2022-01-21 10:37:02.647806+00	2022-01-21 10:37:02.647836+00	8	\N	\N	f	f
7131	CATEGORY	Category	Intercompany Payables	135619	2022-01-21 10:37:02.647897+00	2022-01-21 10:37:02.647926+00	8	\N	\N	f	f
7132	CATEGORY	Category	Intercompany Professional Fees	135622	2022-01-21 10:37:02.647987+00	2022-01-21 10:37:02.648016+00	8	\N	\N	f	f
7133	CATEGORY	Category	Intercompany Receivables	135607	2022-01-21 10:37:02.648077+00	2022-01-21 10:37:02.648106+00	8	\N	\N	f	f
7134	CATEGORY	Category	Interest Expense	135621	2022-01-21 10:37:02.648166+00	2022-01-21 10:37:02.648196+00	8	\N	\N	f	f
7135	CATEGORY	Category	Interest Income	135620	2022-01-21 10:37:02.648256+00	2022-01-21 10:37:02.648285+00	8	\N	\N	f	f
7136	CATEGORY	Category	Internet	135456	2022-01-21 10:37:02.648346+00	2022-01-21 10:37:02.648375+00	8	\N	\N	f	f
7137	CATEGORY	Category	Inventory	135626	2022-01-21 10:37:02.648435+00	2022-01-21 10:37:02.648464+00	8	\N	\N	f	f
7138	CATEGORY	Category	Inventory Asset	135909	2022-01-21 10:37:02.648525+00	2022-01-21 10:37:02.648555+00	8	\N	\N	f	f
7139	CATEGORY	Category	Inventory In Transit	135920	2022-01-21 10:37:02.648615+00	2022-01-21 10:37:02.648644+00	8	\N	\N	f	f
7140	CATEGORY	Category	Inventory-Kits	135628	2022-01-21 10:37:02.648705+00	2022-01-21 10:37:02.648734+00	8	\N	\N	f	f
7141	CATEGORY	Category	Inventory-Other	135627	2022-01-21 10:37:02.681544+00	2022-01-21 10:37:02.681731+00	8	\N	\N	f	f
7142	CATEGORY	Category	Inventory Returned Not Credited	135917	2022-01-21 10:37:02.681846+00	2022-01-21 10:37:02.681918+00	8	\N	\N	f	f
7143	CATEGORY	Category	Inventory Transfer Price Gain - Loss	135924	2022-01-21 10:37:02.682013+00	2022-01-21 10:37:02.682053+00	8	\N	\N	f	f
7144	CATEGORY	Category	Inventory Variance	135878	2022-01-21 10:37:02.682154+00	2022-01-21 10:37:02.682194+00	8	\N	\N	f	f
7145	CATEGORY	Category	Inventory Write Offs	135919	2022-01-21 10:37:02.682291+00	2022-01-21 10:37:02.682329+00	8	\N	\N	f	f
7146	CATEGORY	Category	Investments and Securities	135603	2022-01-21 10:37:02.682421+00	2022-01-21 10:37:02.682444+00	8	\N	\N	f	f
7147	CATEGORY	Category	Job Expenses	135755	2022-01-21 10:37:02.682527+00	2022-01-21 10:37:02.682566+00	8	\N	\N	f	f
7148	CATEGORY	Category	Job Expenses:Cost of Labor	135756	2022-01-21 10:37:02.682658+00	2022-01-21 10:37:02.682695+00	8	\N	\N	f	f
7149	CATEGORY	Category	Job Expenses:Cost of Labor:Installation	135724	2022-01-21 10:37:02.682787+00	2022-01-21 10:37:02.682825+00	8	\N	\N	f	f
7150	CATEGORY	Category	Job Expenses:Cost of Labor:Maintenance and Repairs	135725	2022-01-21 10:37:02.682917+00	2022-01-21 10:37:02.682955+00	8	\N	\N	f	f
7151	CATEGORY	Category	Job Expenses:Equipment Rental	135726	2022-01-21 10:37:02.683047+00	2022-01-21 10:37:02.683084+00	8	\N	\N	f	f
7152	CATEGORY	Category	Job Expenses:Job Materials	135727	2022-01-21 10:37:02.683175+00	2022-01-21 10:37:02.683212+00	8	\N	\N	f	f
7153	CATEGORY	Category	Job Expenses:Job Materials:Decks and Patios	135728	2022-01-21 10:37:02.718215+00	2022-01-21 10:37:02.718282+00	8	\N	\N	f	f
7154	CATEGORY	Category	Job Expenses:Job Materials:Fountain and Garden Lighting	135729	2022-01-21 10:37:02.76703+00	2022-01-21 10:37:02.76714+00	8	\N	\N	f	f
7155	CATEGORY	Category	Job Expenses:Job Materials:Plants and Soil	135730	2022-01-21 10:37:02.76802+00	2022-01-21 10:37:02.768098+00	8	\N	\N	f	f
7156	CATEGORY	Category	Job Expenses:Job Materials:Sprinklers and Drip Systems	135731	2022-01-21 10:37:02.76861+00	2022-01-21 10:37:02.768675+00	8	\N	\N	f	f
7157	CATEGORY	Category	Job Expenses:Permits	135732	2022-01-21 10:37:02.769323+00	2022-01-21 10:37:02.769419+00	8	\N	\N	f	f
7158	CATEGORY	Category	Labor	135941	2022-01-21 10:37:02.770005+00	2022-01-21 10:37:02.770108+00	8	\N	\N	f	f
7159	CATEGORY	Category	Labor Burden	135942	2022-01-21 10:37:02.770294+00	2022-01-21 10:37:02.770357+00	8	\N	\N	f	f
7160	CATEGORY	Category	Labor Cost Offset	135560	2022-01-21 10:37:02.770499+00	2022-01-21 10:37:02.770553+00	8	\N	\N	f	f
7161	CATEGORY	Category	Labor Cost Variance	135559	2022-01-21 10:37:02.77091+00	2022-01-21 10:37:02.772737+00	8	\N	\N	f	f
7162	CATEGORY	Category	LCT Paid	157847	2022-01-21 10:37:02.773431+00	2022-01-21 10:37:02.773488+00	8	\N	\N	f	f
7163	CATEGORY	Category	Legal	135913	2022-01-21 10:37:02.773936+00	2022-01-21 10:37:02.773992+00	8	\N	\N	f	f
7164	CATEGORY	Category	Legal and professional fees	147492	2022-01-21 10:37:02.775058+00	2022-01-21 10:37:02.775989+00	8	\N	\N	f	f
7165	CATEGORY	Category	Legal expenses	135997	2022-01-21 10:37:02.791255+00	2022-01-21 10:37:02.791422+00	8	\N	\N	f	f
7166	CATEGORY	Category	Legal & Professional Fees	135733	2022-01-21 10:37:02.792713+00	2022-01-21 10:37:02.792751+00	8	\N	\N	f	f
7167	CATEGORY	Category	Legal & Professional Fees:Accounting	135734	2022-01-21 10:37:02.792812+00	2022-01-21 10:37:02.792842+00	8	\N	\N	f	f
7168	CATEGORY	Category	Legal & Professional Fees:Bookkeeper	135735	2022-01-21 10:37:02.7929+00	2022-01-21 10:37:02.792922+00	8	\N	\N	f	f
7169	CATEGORY	Category	Legal & Professional Fees:Lawyer	135736	2022-01-21 10:37:02.793218+00	2022-01-21 10:37:02.793295+00	8	\N	\N	f	f
7170	CATEGORY	Category	Liability	135886	2022-01-21 10:37:02.794435+00	2022-01-21 10:37:02.794512+00	8	\N	\N	f	f
7171	CATEGORY	Category	Light, Power, Heating	135998	2022-01-21 10:37:02.795955+00	2022-01-21 10:37:02.797142+00	8	\N	\N	f	f
7172	CATEGORY	Category	Loss on discontinued operations, net of tax	147493	2022-01-21 10:37:02.797994+00	2022-01-21 10:37:02.798066+00	8	\N	\N	f	f
7173	CATEGORY	Category	Machine	135943	2022-01-21 10:37:02.798525+00	2022-01-21 10:37:02.799147+00	8	\N	\N	f	f
7174	CATEGORY	Category	Machine Burden	135944	2022-01-21 10:37:02.799336+00	2022-01-21 10:37:02.799383+00	8	\N	\N	f	f
7175	CATEGORY	Category	Machinery & Equipment	135610	2022-01-21 10:37:02.799513+00	2022-01-21 10:37:02.799561+00	8	\N	\N	f	f
7176	CATEGORY	Category	Machinery & Equipment Accm.Depr.	135611	2022-01-21 10:37:02.80067+00	2022-01-21 10:37:02.800943+00	8	\N	\N	f	f
7177	CATEGORY	Category	Maintenance and Repair	135737	2022-01-21 10:37:02.801394+00	2022-01-21 10:37:02.801585+00	8	\N	\N	f	f
7178	CATEGORY	Category	Maintenance and Repair:Building Repairs	135738	2022-01-21 10:37:02.811062+00	2022-01-21 10:37:02.849181+00	8	\N	\N	f	f
7179	CATEGORY	Category	Maintenance and Repair:Computer Repairs	135739	2022-01-21 10:37:02.849681+00	2022-01-21 10:37:02.849821+00	8	\N	\N	f	f
7180	CATEGORY	Category	Maintenance and Repair:Equipment Repairs	135740	2022-01-21 10:37:02.849935+00	2022-01-21 10:37:02.849996+00	8	\N	\N	f	f
7181	CATEGORY	Category	Management compensation	147494	2022-01-21 10:37:02.850198+00	2022-01-21 10:37:02.850244+00	8	\N	\N	f	f
7182	CATEGORY	Category	Manufacturing Expenses	135940	2022-01-21 10:37:02.850899+00	2022-01-21 10:37:02.850979+00	8	\N	\N	f	f
7183	CATEGORY	Category	Marketing and Advertising	135589	2022-01-21 10:37:02.851206+00	2022-01-21 10:37:02.851273+00	8	\N	\N	f	f
7184	CATEGORY	Category	Meals	135741	2022-01-21 10:37:02.852096+00	2022-01-21 10:37:02.852177+00	8	\N	\N	f	f
7185	CATEGORY	Category	Meals and Entertainment	135593	2022-01-21 10:37:02.857279+00	2022-01-21 10:37:02.857415+00	8	\N	\N	f	f
7186	CATEGORY	Category	Meals & Entertainment	135793	2022-01-21 10:37:02.857784+00	2022-01-21 10:37:02.857849+00	8	\N	\N	f	f
7187	CATEGORY	Category	Merchandise	135874	2022-01-21 10:37:02.858092+00	2022-01-21 10:37:02.85819+00	8	\N	\N	f	f
7188	CATEGORY	Category	Mfg Scrap	135939	2022-01-21 10:37:02.858381+00	2022-01-21 10:37:02.858451+00	8	\N	\N	f	f
7189	CATEGORY	Category	Mfg WIP	135932	2022-01-21 10:37:02.885403+00	2022-01-21 10:37:02.885488+00	8	\N	\N	f	f
7190	CATEGORY	Category	Mileage	135452	2022-01-21 10:37:02.885928+00	2022-01-21 10:37:02.886016+00	8	\N	\N	f	f
7191	CATEGORY	Category	Miscellaneous	163671	2022-01-21 10:37:02.997046+00	2022-01-21 10:37:02.997121+00	8	\N	\N	f	f
7192	CATEGORY	Category	Miscellaneous Expense	135889	2022-01-21 10:37:02.997291+00	2022-01-21 10:37:02.997347+00	8	\N	\N	f	f
7193	CATEGORY	Category	Motor Vehicle Expenses	135999	2022-01-21 10:37:02.997509+00	2022-01-21 10:37:02.99755+00	8	\N	\N	f	f
7194	CATEGORY	Category	Movies	145416	2022-01-21 10:37:02.997706+00	2022-01-21 10:37:02.997759+00	8	\N	\N	f	f
7195	CATEGORY	Category	Netflix	146042	2022-01-21 10:37:02.997905+00	2022-01-21 10:37:02.997944+00	8	\N	\N	f	f
7196	CATEGORY	Category	New Category	147927	2022-01-21 10:37:02.99809+00	2022-01-21 10:37:02.998129+00	8	\N	\N	f	f
7197	CATEGORY	Category	Note Receivable-Current	135873	2022-01-21 10:37:02.998277+00	2022-01-21 10:37:02.998328+00	8	\N	\N	f	f
7198	CATEGORY	Category	Notes Payable	135546	2022-01-21 10:37:02.998473+00	2022-01-21 10:37:02.998514+00	8	\N	\N	f	f
7199	CATEGORY	Category	Office Expense	135890	2022-01-21 10:37:02.998658+00	2022-01-21 10:37:02.998698+00	8	\N	\N	f	f
7200	CATEGORY	Category	Office Expenses	135742	2022-01-21 10:37:02.998843+00	2022-01-21 10:37:02.998883+00	8	\N	\N	f	f
7201	CATEGORY	Category	Office-General Administrative Expenses	135745	2022-01-21 10:37:02.999028+00	2022-01-21 10:37:02.999068+00	8	\N	\N	f	f
7202	CATEGORY	Category	Office Party	135462	2022-01-21 10:37:02.999203+00	2022-01-21 10:37:02.99951+00	8	\N	\N	f	f
7203	CATEGORY	Category	Office Supplies	135448	2022-01-21 10:37:02.999664+00	2022-01-21 10:37:02.999716+00	8	\N	\N	f	f
7204	CATEGORY	Category	Office Supplies 2	135744	2022-01-21 10:37:03.000065+00	2022-01-21 10:37:03.000106+00	8	\N	\N	f	f
7205	CATEGORY	Category	Office Suppliesdfsd	135555	2022-01-21 10:37:03.00023+00	2022-01-21 10:37:03.000606+00	8	\N	\N	f	f
7206	CATEGORY	Category	Online Fees	135905	2022-01-21 10:37:03.000791+00	2022-01-21 10:37:03.000842+00	8	\N	\N	f	f
7207	CATEGORY	Category	Other Assets	135630	2022-01-21 10:37:03.001001+00	2022-01-21 10:37:03.001051+00	8	\N	\N	f	f
7208	CATEGORY	Category	Other Direct Costs	135877	2022-01-21 10:37:03.001208+00	2022-01-21 10:37:03.00126+00	8	\N	\N	f	f
7209	CATEGORY	Category	Other Expense	135638	2022-01-21 10:37:03.001416+00	2022-01-21 10:37:03.001468+00	8	\N	\N	f	f
7210	CATEGORY	Category	Other G&A	135538	2022-01-21 10:37:03.001623+00	2022-01-21 10:37:03.001674+00	8	\N	\N	f	f
7211	CATEGORY	Category	Other general and administrative expenses	147497	2022-01-21 10:37:03.00183+00	2022-01-21 10:37:03.001881+00	8	\N	\N	f	f
7212	CATEGORY	Category	Other Income	135639	2022-01-21 10:37:03.002627+00	2022-01-21 10:37:03.041124+00	8	\N	\N	f	f
7213	CATEGORY	Category	Other Intangible Assets	135629	2022-01-21 10:37:03.041272+00	2022-01-21 10:37:03.041315+00	8	\N	\N	f	f
7214	CATEGORY	Category	Other Receivables	135870	2022-01-21 10:37:03.041406+00	2022-01-21 10:37:03.041447+00	8	\N	\N	f	f
7215	CATEGORY	Category	Others	135451	2022-01-21 10:37:03.041539+00	2022-01-21 10:37:03.041583+00	8	\N	\N	f	f
7216	CATEGORY	Category	Other selling expenses	147498	2022-01-21 10:37:03.041675+00	2022-01-21 10:37:03.041715+00	8	\N	\N	f	f
7217	CATEGORY	Category	Other Taxes	135637	2022-01-21 10:37:03.042304+00	2022-01-21 10:37:03.042404+00	8	\N	\N	f	f
7218	CATEGORY	Category	Other Types of Expenses-Advertising Expenses	147499	2022-01-21 10:37:03.042735+00	2022-01-21 10:37:03.042802+00	8	\N	\N	f	f
7219	CATEGORY	Category	Outside Services	135891	2022-01-21 10:37:03.042963+00	2022-01-21 10:37:03.043002+00	8	\N	\N	f	f
7220	CATEGORY	Category	Pager	135903	2022-01-21 10:37:03.043137+00	2022-01-21 10:37:03.043177+00	8	\N	\N	f	f
7221	CATEGORY	Category	Parking	135465	2022-01-21 10:37:03.04331+00	2022-01-21 10:37:03.043352+00	8	\N	\N	f	f
7222	CATEGORY	Category	Patents & Licenses	135552	2022-01-21 10:37:03.043484+00	2022-01-21 10:37:03.043523+00	8	\N	\N	f	f
7223	CATEGORY	Category	Pay As You Go Withholding	157850	2022-01-21 10:37:03.043855+00	2022-01-21 10:37:03.043895+00	8	\N	\N	f	f
7224	CATEGORY	Category	Payroll Expense	135540	2022-01-21 10:37:03.044098+00	2022-01-21 10:37:03.044133+00	8	\N	\N	f	f
7225	CATEGORY	Category	Payroll Expenses	135541	2022-01-21 10:37:03.044458+00	2022-01-21 10:37:03.044621+00	8	\N	\N	f	f
7226	CATEGORY	Category	Payroll Taxes	135625	2022-01-21 10:37:03.044868+00	2022-01-21 10:37:03.044914+00	8	\N	\N	f	f
7227	CATEGORY	Category	Penalties & Settlements	163672	2022-01-21 10:37:03.045069+00	2022-01-21 10:37:03.045188+00	8	\N	\N	f	f
7228	CATEGORY	Category	Per Diem	135454	2022-01-21 10:37:03.045331+00	2022-01-21 10:37:03.045383+00	8	\N	\N	f	f
7229	CATEGORY	Category	Phone	135461	2022-01-21 10:37:03.045497+00	2022-01-21 10:37:03.045545+00	8	\N	\N	f	f
7230	CATEGORY	Category	Postage & Delivery	135892	2022-01-21 10:37:03.04566+00	2022-01-21 10:37:03.045707+00	8	\N	\N	f	f
7231	CATEGORY	Category	Preferred Stock	135632	2022-01-21 10:37:03.045815+00	2022-01-21 10:37:03.045859+00	8	\N	\N	f	f
7232	CATEGORY	Category	Prepaid Expenses	135871	2022-01-21 10:37:03.045969+00	2022-01-21 10:37:03.04623+00	8	\N	\N	f	f
7233	CATEGORY	Category	Prepaid Income Taxes	135872	2022-01-21 10:37:03.04757+00	2022-01-21 10:37:03.047603+00	8	\N	\N	f	f
7234	CATEGORY	Category	Prepaid Insurance	135571	2022-01-21 10:37:03.047667+00	2022-01-21 10:37:03.047697+00	8	\N	\N	f	f
7235	CATEGORY	Category	Prepaid Other	135573	2022-01-21 10:37:03.047759+00	2022-01-21 10:37:03.047789+00	8	\N	\N	f	f
7236	CATEGORY	Category	Prepaid Rent	135572	2022-01-21 10:37:03.04785+00	2022-01-21 10:37:03.047879+00	8	\N	\N	f	f
7237	CATEGORY	Category	Printing & Stationery	136000	2022-01-21 10:37:03.047941+00	2022-01-21 10:37:03.04797+00	8	\N	\N	f	f
7238	CATEGORY	Category	Professional Fees	135893	2022-01-21 10:37:03.048033+00	2022-01-21 10:37:03.048062+00	8	\N	\N	f	f
7239	CATEGORY	Category	Professional Fees Expense	135592	2022-01-21 10:37:03.048124+00	2022-01-21 10:37:03.048153+00	8	\N	\N	f	f
7240	CATEGORY	Category	Professional Services	135460	2022-01-21 10:37:03.048214+00	2022-01-21 10:37:03.048244+00	8	\N	\N	f	f
7241	CATEGORY	Category	Promotional	135746	2022-01-21 10:37:03.111842+00	2022-01-21 10:37:03.111921+00	8	\N	\N	f	f
7242	CATEGORY	Category	Property	135899	2022-01-21 10:37:03.112056+00	2022-01-21 10:37:03.112104+00	8	\N	\N	f	f
7243	CATEGORY	Category	Purchase Price Variance	135933	2022-01-21 10:37:03.112213+00	2022-01-21 10:37:03.112256+00	8	\N	\N	f	f
7244	CATEGORY	Category	Purchases	135747	2022-01-21 10:37:03.11236+00	2022-01-21 10:37:03.1124+00	8	\N	\N	f	f
7245	CATEGORY	Category	Realised Currency Gains	136009	2022-01-21 10:37:03.112503+00	2022-01-21 10:37:03.112544+00	8	\N	\N	f	f
7246	CATEGORY	Category	Realized Gain-Loss	135927	2022-01-21 10:37:03.112644+00	2022-01-21 10:37:03.112842+00	8	\N	\N	f	f
7247	CATEGORY	Category	Reconciliation Discrepancies	163673	2022-01-21 10:37:03.112949+00	2022-01-21 10:37:03.11299+00	8	\N	\N	f	f
7248	CATEGORY	Category	Regular Service	135902	2022-01-21 10:37:03.113085+00	2022-01-21 10:37:03.113126+00	8	\N	\N	f	f
7249	CATEGORY	Category	Rent	135556	2022-01-21 10:37:03.113223+00	2022-01-21 10:37:03.113263+00	8	\N	\N	f	f
7250	CATEGORY	Category	Rent Expense	135894	2022-01-21 10:37:03.113363+00	2022-01-21 10:37:03.113405+00	8	\N	\N	f	f
7251	CATEGORY	Category	Rent or Lease	135748	2022-01-21 10:37:03.1135+00	2022-01-21 10:37:03.113539+00	8	\N	\N	f	f
7252	CATEGORY	Category	Rent or lease payments	147500	2022-01-21 10:37:03.113634+00	2022-01-21 10:37:03.113673+00	8	\N	\N	f	f
7253	CATEGORY	Category	Repairs	135881	2022-01-21 10:37:03.113766+00	2022-01-21 10:37:03.113805+00	8	\N	\N	f	f
7254	CATEGORY	Category	Repairs and Maintenance	135594	2022-01-21 10:37:03.113897+00	2022-01-21 10:37:03.113938+00	8	\N	\N	f	f
7255	CATEGORY	Category	Repairs & Maintenance	135895	2022-01-21 10:37:03.11403+00	2022-01-21 10:37:03.114072+00	8	\N	\N	f	f
7256	CATEGORY	Category	Retained Earnings	135633	2022-01-21 10:37:03.114163+00	2022-01-21 10:37:03.114202+00	8	\N	\N	f	f
7257	CATEGORY	Category	Revenue - Accessories	135586	2022-01-21 10:37:03.114293+00	2022-01-21 10:37:03.114332+00	8	\N	\N	f	f
7258	CATEGORY	Category	Revenue - Entry	135587	2022-01-21 10:37:03.114424+00	2022-01-21 10:37:03.114463+00	8	\N	\N	f	f
7259	CATEGORY	Category	Revenue - Other	135624	2022-01-21 10:37:03.114555+00	2022-01-21 10:37:03.114596+00	8	\N	\N	f	f
7260	CATEGORY	Category	Revenue - Surveillance	135588	2022-01-21 10:37:03.114688+00	2022-01-21 10:37:03.114727+00	8	\N	\N	f	f
7261	CATEGORY	Category	Rounding Gain-Loss	135926	2022-01-21 10:37:03.114817+00	2022-01-21 10:37:03.11486+00	8	\N	\N	f	f
7262	CATEGORY	Category	Salaries and Wages	135595	2022-01-21 10:37:03.114952+00	2022-01-21 10:37:03.11499+00	8	\N	\N	f	f
7263	CATEGORY	Category	Salaries Payable	135575	2022-01-21 10:37:03.115079+00	2022-01-21 10:37:03.115119+00	8	\N	\N	f	f
7264	CATEGORY	Category	Salaries & Wages	135876	2022-01-21 10:37:03.115209+00	2022-01-21 10:37:03.115247+00	8	\N	\N	f	f
7265	CATEGORY	Category	Salaries & Wages Expense	135907	2022-01-21 10:37:03.115336+00	2022-01-21 10:37:03.115374+00	8	\N	\N	f	f
7266	CATEGORY	Category	Savings	162002	2022-01-21 10:37:03.115464+00	2022-01-21 10:37:03.115503+00	8	\N	\N	f	f
7267	CATEGORY	Category	Service	135875	2022-01-21 10:37:03.115593+00	2022-01-21 10:37:03.115632+00	8	\N	\N	f	f
7268	CATEGORY	Category	Shipping and delivery expense	147501	2022-01-21 10:37:03.115721+00	2022-01-21 10:37:03.11576+00	8	\N	\N	f	f
7269	CATEGORY	Category	Snacks	135447	2022-01-21 10:37:03.115851+00	2022-01-21 10:37:03.11589+00	8	\N	\N	f	f
7270	CATEGORY	Category	Software	135464	2022-01-21 10:37:03.115979+00	2022-01-21 10:37:03.116017+00	8	\N	\N	f	f
7271	CATEGORY	Category	Software and Licenses	135645	2022-01-21 10:37:03.116107+00	2022-01-21 10:37:03.116145+00	8	\N	\N	f	f
7272	CATEGORY	Category	Spot Bonus	135537	2022-01-21 10:37:03.116235+00	2022-01-21 10:37:03.116274+00	8	\N	\N	f	f
7273	CATEGORY	Category	Stationery and printing	147502	2022-01-21 10:37:03.116364+00	2022-01-21 10:37:03.116403+00	8	\N	\N	f	f
7274	CATEGORY	Category	Stationery & Printing	135749	2022-01-21 10:37:03.116492+00	2022-01-21 10:37:03.11653+00	8	\N	\N	f	f
7275	CATEGORY	Category	sub ash	135947	2022-01-21 10:37:03.116621+00	2022-01-21 10:37:03.116659+00	8	\N	\N	f	f
7276	CATEGORY	Category	Subscriptions	136003	2022-01-21 10:37:03.116748+00	2022-01-21 10:37:03.116787+00	8	\N	\N	f	f
7277	CATEGORY	Category	Superannuation	136002	2022-01-21 10:37:03.116877+00	2022-01-21 10:37:03.116916+00	8	\N	\N	f	f
7278	CATEGORY	Category	Supplies	145002	2022-01-21 10:37:03.118599+00	2022-01-21 10:37:03.118655+00	8	\N	\N	f	f
7279	CATEGORY	Category	Supplies Expense	135896	2022-01-21 10:37:03.11875+00	2022-01-21 10:37:03.118783+00	8	\N	\N	f	f
7280	CATEGORY	Category	Supplies Test 2	135750	2022-01-21 10:37:03.118854+00	2022-01-21 10:37:03.118885+00	8	\N	\N	f	f
7281	CATEGORY	Category	SVB Checking	135598	2022-01-21 10:37:03.118953+00	2022-01-21 10:37:03.118983+00	8	\N	\N	f	f
7282	CATEGORY	Category	SVB Checking 2	135599	2022-01-21 10:37:03.119049+00	2022-01-21 10:37:03.119078+00	8	\N	\N	f	f
7283	CATEGORY	Category	SVB Checking 3	135600	2022-01-21 10:37:03.11914+00	2022-01-21 10:37:03.119621+00	8	\N	\N	f	f
7284	CATEGORY	Category	Sync Expense Account	145003	2022-01-21 10:37:03.144671+00	2022-01-21 10:37:03.145129+00	8	\N	\N	f	f
7285	CATEGORY	Category	Tax	135467	2022-01-21 10:37:03.14548+00	2022-01-21 10:37:03.146228+00	8	\N	\N	f	f
7286	CATEGORY	Category	Taxes & Licenses	135751	2022-01-21 10:37:03.1471+00	2022-01-21 10:37:03.147174+00	8	\N	\N	f	f
7287	CATEGORY	Category	Taxes & Licenses-Other	135897	2022-01-21 10:37:03.147304+00	2022-01-21 10:37:03.147353+00	8	\N	\N	f	f
7288	CATEGORY	Category	Taxi	135457	2022-01-21 10:37:03.147483+00	2022-01-21 10:37:03.147531+00	8	\N	\N	f	f
7289	CATEGORY	Category	Telecommunication Expense	135582	2022-01-21 10:37:03.147655+00	2022-01-21 10:37:03.148052+00	8	\N	\N	f	f
7290	CATEGORY	Category	Telephone Expense	135901	2022-01-21 10:37:03.148186+00	2022-01-21 10:37:03.148235+00	8	\N	\N	f	f
7291	CATEGORY	Category	Telephone & Internet	136004	2022-01-21 10:37:03.22953+00	2022-01-21 10:37:03.229573+00	8	\N	\N	f	f
7292	CATEGORY	Category	test	137949	2022-01-21 10:37:03.229637+00	2022-01-21 10:37:03.229667+00	8	\N	\N	f	f
7293	CATEGORY	Category	Test 2	135752	2022-01-21 10:37:03.229728+00	2022-01-21 10:37:03.229757+00	8	\N	\N	f	f
7294	CATEGORY	Category	Test Staging	135753	2022-01-21 10:37:03.229818+00	2022-01-21 10:37:03.229847+00	8	\N	\N	f	f
7295	CATEGORY	Category	Toll Charge	135466	2022-01-21 10:37:03.229908+00	2022-01-21 10:37:03.229938+00	8	\N	\N	f	f
7296	CATEGORY	Category	Trade Shows and Exhibits	135590	2022-01-21 10:37:03.229998+00	2022-01-21 10:37:03.230027+00	8	\N	\N	f	f
7297	CATEGORY	Category	Train	135445	2022-01-21 10:37:03.230089+00	2022-01-21 10:37:03.230118+00	8	\N	\N	f	f
7298	CATEGORY	Category	Training	135468	2022-01-21 10:37:03.230459+00	2022-01-21 10:37:03.230498+00	8	\N	\N	f	f
7299	CATEGORY	Category	Travel	135545	2022-01-21 10:37:03.230571+00	2022-01-21 10:37:03.2306+00	8	\N	\N	f	f
7300	CATEGORY	Category	Travel - Automobile	149798	2022-01-21 10:37:03.230662+00	2022-01-21 10:37:03.230692+00	8	\N	\N	f	f
7301	CATEGORY	Category	Travel Expenses	137948	2022-01-21 10:37:03.230753+00	2022-01-21 10:37:03.230783+00	8	\N	\N	f	f
7302	CATEGORY	Category	Travel expenses - general and admin expenses	147503	2022-01-21 10:37:03.230844+00	2022-01-21 10:37:03.230873+00	8	\N	\N	f	f
7303	CATEGORY	Category	Travel expenses - selling expenses	147504	2022-01-21 10:37:03.230934+00	2022-01-21 10:37:03.230964+00	8	\N	\N	f	f
7304	CATEGORY	Category	Travel Expenses which supports National - International	135542	2022-01-21 10:37:03.231025+00	2022-01-21 10:37:03.231055+00	8	\N	\N	f	f
7305	CATEGORY	Category	Travel - International	136006	2022-01-21 10:37:03.231116+00	2022-01-21 10:37:03.231146+00	8	\N	\N	f	f
7306	CATEGORY	Category	Travelling Charges	135795	2022-01-21 10:37:03.231207+00	2022-01-21 10:37:03.231236+00	8	\N	\N	f	f
7307	CATEGORY	Category	Travel Meals	135757	2022-01-21 10:37:03.231298+00	2022-01-21 10:37:03.231327+00	8	\N	\N	f	f
7308	CATEGORY	Category	Travel - National	136005	2022-01-21 10:37:03.231388+00	2022-01-21 10:37:03.231417+00	8	\N	\N	f	f
7309	CATEGORY	Category	UK EXP Account	157853	2022-01-21 10:37:03.231478+00	2022-01-21 10:37:03.231507+00	8	\N	\N	f	f
7310	CATEGORY	Category	UK Expense Acct	157852	2022-01-21 10:37:03.231568+00	2022-01-21 10:37:03.231598+00	8	\N	\N	f	f
7311	CATEGORY	Category	UK Expense Category	157669	2022-01-21 10:37:03.231659+00	2022-01-21 10:37:03.231688+00	8	\N	\N	f	f
7312	CATEGORY	Category	Unapplied Cash Bill Payment Expense	135758	2022-01-21 10:37:03.232123+00	2022-01-21 10:37:03.232167+00	8	\N	\N	f	f
7313	CATEGORY	Category	Unbuild Variance	135925	2022-01-21 10:37:03.232248+00	2022-01-21 10:37:03.232277+00	8	\N	\N	f	f
7314	CATEGORY	Category	Uncategorised Expense	147505	2022-01-21 10:37:03.232338+00	2022-01-21 10:37:03.232367+00	8	\N	\N	f	f
7315	CATEGORY	Category	Uncategorized Expense	135759	2022-01-21 10:37:03.232427+00	2022-01-21 10:37:03.232456+00	8	\N	\N	f	f
7316	CATEGORY	Category	Undeposited Funds	135868	2022-01-21 10:37:03.232521+00	2022-01-21 10:37:03.23255+00	8	\N	\N	f	f
7317	CATEGORY	Category	Unrealised Currency Gains	136008	2022-01-21 10:37:03.232612+00	2022-01-21 10:37:03.232641+00	8	\N	\N	f	f
7318	CATEGORY	Category	Unrealized Gain-Loss	135928	2022-01-21 10:37:03.232701+00	2022-01-21 10:37:03.232731+00	8	\N	\N	f	f
7319	CATEGORY	Category	Unspecified	135469	2022-01-21 10:37:03.232791+00	2022-01-21 10:37:03.232821+00	8	\N	\N	f	f
7320	CATEGORY	Category	Utilities	135646	2022-01-21 10:37:03.232881+00	2022-01-21 10:37:03.23291+00	8	\N	\N	f	f
7321	CATEGORY	Category	Utilities - Electric & Gas	147506	2022-01-21 10:37:03.232971+00	2022-01-21 10:37:03.233+00	8	\N	\N	f	f
7322	CATEGORY	Category	Utilities:Gas and Electric	135760	2022-01-21 10:37:03.233061+00	2022-01-21 10:37:03.233089+00	8	\N	\N	f	f
7323	CATEGORY	Category	Utilities:Telephone	135761	2022-01-21 10:37:03.23315+00	2022-01-21 10:37:03.233179+00	8	\N	\N	f	f
7324	CATEGORY	Category	Utilities - Water	147507	2022-01-21 10:37:03.233763+00	2022-01-21 10:37:03.233795+00	8	\N	\N	f	f
7325	CATEGORY	Category	Utility	135449	2022-01-21 10:37:03.23386+00	2022-01-21 10:37:03.233889+00	8	\N	\N	f	f
7326	CATEGORY	Category	VAT on Purchases	157851	2022-01-21 10:37:03.233952+00	2022-01-21 10:37:03.233981+00	8	\N	\N	f	f
7327	CATEGORY	Category	Vehicle Registration	135900	2022-01-21 10:37:03.234044+00	2022-01-21 10:37:03.234073+00	8	\N	\N	f	f
7328	CATEGORY	Category	Vendor Rebates	135936	2022-01-21 10:37:03.234134+00	2022-01-21 10:37:03.234164+00	8	\N	\N	f	f
7329	CATEGORY	Category	Vendor Return Variance	135938	2022-01-21 10:37:03.234225+00	2022-01-21 10:37:03.234255+00	8	\N	\N	f	f
7330	CATEGORY	Category	Wage expenses	147508	2022-01-21 10:37:03.234316+00	2022-01-21 10:37:03.234345+00	8	\N	\N	f	f
7331	CATEGORY	Category	Wages and Salaries	136001	2022-01-21 10:37:03.234406+00	2022-01-21 10:37:03.234435+00	8	\N	\N	f	f
7332	CATEGORY	Category	WET Paid	157848	2022-01-21 10:37:03.234497+00	2022-01-21 10:37:03.234526+00	8	\N	\N	f	f
7333	CATEGORY	Category	WIP	135929	2022-01-21 10:37:03.234587+00	2022-01-21 10:37:03.234617+00	8	\N	\N	f	f
7334	CATEGORY	Category	WIP COGS	135931	2022-01-21 10:37:03.234678+00	2022-01-21 10:37:03.234707+00	8	\N	\N	f	f
7335	CATEGORY	Category	WIP Revenue	135930	2022-01-21 10:37:03.234768+00	2022-01-21 10:37:03.234797+00	8	\N	\N	f	f
7336	CATEGORY	Category	WIP Variance	135945	2022-01-21 10:37:03.234858+00	2022-01-21 10:37:03.234887+00	8	\N	\N	f	f
7337	CATEGORY	Category	Workers' compensation	135887	2022-01-21 10:37:03.234948+00	2022-01-21 10:37:03.234977+00	8	\N	\N	f	f
7338	COST_CENTER	Cost Center	Administration	7227	2022-01-21 10:37:04.175054+00	2022-01-21 10:37:04.175634+00	8	\N	\N	f	f
7339	COST_CENTER	Cost Center	Audit	7223	2022-01-21 10:37:04.176224+00	2022-01-21 10:37:04.176304+00	8	\N	\N	f	f
7340	COST_CENTER	Cost Center	Internal	7221	2022-01-21 10:37:04.176845+00	2022-01-21 10:37:04.177055+00	8	\N	\N	f	f
7341	COST_CENTER	Cost Center	Legal and Secretarial	7229	2022-01-21 10:37:04.177239+00	2022-01-21 10:37:04.177288+00	8	\N	\N	f	f
7342	COST_CENTER	Cost Center	Marketing	7224	2022-01-21 10:37:04.177378+00	2022-01-21 10:37:04.177416+00	8	\N	\N	f	f
7343	COST_CENTER	Cost Center	Retail	7226	2022-01-21 10:37:04.177504+00	2022-01-21 10:37:04.177541+00	8	\N	\N	f	f
7344	COST_CENTER	Cost Center	Sales and Cross	7220	2022-01-21 10:37:04.177858+00	2022-01-21 10:37:04.177899+00	8	\N	\N	f	f
7345	COST_CENTER	Cost Center	SME	7225	2022-01-21 10:37:04.177987+00	2022-01-21 10:37:04.178026+00	8	\N	\N	f	f
7346	COST_CENTER	Cost Center	Strategy Planning	7228	2022-01-21 10:37:04.178115+00	2022-01-21 10:37:04.178154+00	8	\N	\N	f	f
7347	COST_CENTER	Cost Center	Treasury	7222	2022-01-21 10:37:04.178251+00	2022-01-21 10:37:04.178292+00	8	\N	\N	f	f
7348	PROJECT	Project	3M	246849	2022-01-21 10:37:07.369036+00	2022-01-21 10:37:07.369101+00	8	\N	\N	f	f
7349	PROJECT	Project	Aaron Abbott	246855	2022-01-21 10:37:07.369202+00	2022-01-21 10:37:07.369243+00	8	\N	\N	f	f
7350	PROJECT	Project	AB&I Holdings	246850	2022-01-21 10:37:07.369336+00	2022-01-21 10:37:07.369377+00	8	\N	\N	f	f
7351	PROJECT	Project	Absolute Location Support	246856	2022-01-21 10:37:07.369468+00	2022-01-21 10:37:07.369508+00	8	\N	\N	f	f
7352	PROJECT	Project	Academy Avenue Liquor Store	246857	2022-01-21 10:37:07.369599+00	2022-01-21 10:37:07.369638+00	8	\N	\N	f	f
7353	PROJECT	Project	Academy Sports & Outdoors	246858	2022-01-21 10:37:07.36973+00	2022-01-21 10:37:07.369769+00	8	\N	\N	f	f
7354	PROJECT	Project	Academy Vision Science Clinic	246859	2022-01-21 10:37:07.369859+00	2022-01-21 10:37:07.3699+00	8	\N	\N	f	f
7355	PROJECT	Project	Accountants Inc	246860	2022-01-21 10:37:07.369993+00	2022-01-21 10:37:07.370034+00	8	\N	\N	f	f
7356	PROJECT	Project	Acera	246861	2022-01-21 10:37:07.370127+00	2022-01-21 10:37:07.370167+00	8	\N	\N	f	f
7357	PROJECT	Project	Acme Systems Incorporated	246862	2022-01-21 10:37:07.370259+00	2022-01-21 10:37:07.370298+00	8	\N	\N	f	f
7358	PROJECT	Project	ACM Group	246851	2022-01-21 10:37:07.370389+00	2022-01-21 10:37:07.370428+00	8	\N	\N	f	f
7359	PROJECT	Project	AcuVision Eye Centre	246863	2022-01-21 10:37:07.370519+00	2022-01-21 10:37:07.370559+00	8	\N	\N	f	f
7360	PROJECT	Project	Advanced Design & Drafting Ltd	246864	2022-01-21 10:37:07.370651+00	2022-01-21 10:37:07.370692+00	8	\N	\N	f	f
7361	PROJECT	Project	Advanced Machining Techniques Inc.	246865	2022-01-21 10:37:07.370783+00	2022-01-21 10:37:07.370821+00	8	\N	\N	f	f
7362	PROJECT	Project	Adwin Ko	278532	2022-01-21 10:37:07.370912+00	2022-01-21 10:37:07.370955+00	8	\N	\N	f	f
7363	PROJECT	Project	Agrela Apartments Agency	246866	2022-01-21 10:37:07.371049+00	2022-01-21 10:37:07.37109+00	8	\N	\N	f	f
7364	PROJECT	Project	Ahonen Catering Group	246867	2022-01-21 10:37:07.371182+00	2022-01-21 10:37:07.371222+00	8	\N	\N	f	f
7365	PROJECT	Project	AIM Accounting	246852	2022-01-21 10:37:07.371313+00	2022-01-21 10:37:07.371353+00	8	\N	\N	f	f
7366	PROJECT	Project	AIQ Networks	246853	2022-01-21 10:37:07.371442+00	2022-01-21 10:37:07.371481+00	8	\N	\N	f	f
7367	PROJECT	Project	Alain Henderson	246868	2022-01-21 10:37:07.371571+00	2022-01-21 10:37:07.371611+00	8	\N	\N	f	f
7368	PROJECT	Project	Alamo Catering Group	246869	2022-01-21 10:37:07.371703+00	2022-01-21 10:37:07.371742+00	8	\N	\N	f	f
7369	PROJECT	Project	Alchemy PR	246870	2022-01-21 10:37:07.371833+00	2022-01-21 10:37:07.371873+00	8	\N	\N	f	f
7370	PROJECT	Project	Alesna Leasing Sales	246871	2022-01-21 10:37:07.371964+00	2022-01-21 10:37:07.372004+00	8	\N	\N	f	f
7371	PROJECT	Project	Alex Benedet	246872	2022-01-21 10:37:07.372094+00	2022-01-21 10:37:07.372133+00	8	\N	\N	f	f
7372	PROJECT	Project	Alex Blakey	278533	2022-01-21 10:37:07.372222+00	2022-01-21 10:37:07.37226+00	8	\N	\N	f	f
7373	PROJECT	Project	Alex Fabre	246873	2022-01-21 10:37:07.372351+00	2022-01-21 10:37:07.372389+00	8	\N	\N	f	f
7374	PROJECT	Project	Alex Wolfe	246874	2022-01-21 10:37:07.37248+00	2022-01-21 10:37:07.37252+00	8	\N	\N	f	f
7375	PROJECT	Project	All-Lift Inc	246878	2022-01-21 10:37:07.37261+00	2022-01-21 10:37:07.372649+00	8	\N	\N	f	f
7376	PROJECT	Project	All Occassions Event Coordination	246875	2022-01-21 10:37:07.372739+00	2022-01-21 10:37:07.372776+00	8	\N	\N	f	f
7377	PROJECT	Project	All Outdoors	246876	2022-01-21 10:37:07.372864+00	2022-01-21 10:37:07.372904+00	8	\N	\N	f	f
7378	PROJECT	Project	All World Produce	246877	2022-01-21 10:37:07.372993+00	2022-01-21 10:37:07.373034+00	8	\N	\N	f	f
7379	PROJECT	Project	Alpart	246879	2022-01-21 10:37:07.373124+00	2022-01-21 10:37:07.373164+00	8	\N	\N	f	f
7380	PROJECT	Project	Alpine Cafe and Wine Bar	246880	2022-01-21 10:37:07.373413+00	2022-01-21 10:37:07.373453+00	8	\N	\N	f	f
7381	PROJECT	Project	Altamirano Apartments Services	246881	2022-01-21 10:37:07.373538+00	2022-01-21 10:37:07.373575+00	8	\N	\N	f	f
7382	PROJECT	Project	Altonen Windows Rentals	246882	2022-01-21 10:37:07.373662+00	2022-01-21 10:37:07.3737+00	8	\N	\N	f	f
7383	PROJECT	Project	Amarillo Apartments Distributors	246883	2022-01-21 10:37:07.373786+00	2022-01-21 10:37:07.373824+00	8	\N	\N	f	f
7384	PROJECT	Project	Ambc	246884	2022-01-21 10:37:07.373912+00	2022-01-21 10:37:07.37395+00	8	\N	\N	f	f
7385	PROJECT	Project	AmerCaire	246885	2022-01-21 10:37:07.374036+00	2022-01-21 10:37:07.374074+00	8	\N	\N	f	f
7386	PROJECT	Project	AMG Inc	246854	2022-01-21 10:37:07.374162+00	2022-01-21 10:37:07.374199+00	8	\N	\N	f	f
7387	PROJECT	Project	Ammann Builders Fabricators	246886	2022-01-21 10:37:07.374286+00	2022-01-21 10:37:07.374325+00	8	\N	\N	f	f
7388	PROJECT	Project	Amsterdam Drug Store	246887	2022-01-21 10:37:07.374915+00	2022-01-21 10:37:07.375002+00	8	\N	\N	f	f
7389	PROJECT	Project	Amy Kall	246888	2022-01-21 10:37:07.375156+00	2022-01-21 10:37:07.375205+00	8	\N	\N	f	f
7390	PROJECT	Project	Amy's Bird Sanctuary	246788	2022-01-21 10:37:07.375319+00	2022-01-21 10:37:07.375363+00	8	\N	\N	f	f
7391	PROJECT	Project	Amy's Bird Sanctuary:Test Project	246789	2022-01-21 10:37:07.37547+00	2022-01-21 10:37:07.375511+00	8	\N	\N	f	f
7392	PROJECT	Project	Anderson Boughton Inc.	246889	2022-01-21 10:37:07.375615+00	2022-01-21 10:37:07.375656+00	8	\N	\N	f	f
7393	PROJECT	Project	Andersson Hospital Inc.	246890	2022-01-21 10:37:07.375754+00	2022-01-21 10:37:07.375795+00	8	\N	\N	f	f
7394	PROJECT	Project	Andrew Mager	246891	2022-01-21 10:37:07.375895+00	2022-01-21 10:37:07.37594+00	8	\N	\N	f	f
7395	PROJECT	Project	Andy Johnson	246892	2022-01-21 10:37:07.376039+00	2022-01-21 10:37:07.376081+00	8	\N	\N	f	f
7396	PROJECT	Project	Andy Thompson	246893	2022-01-21 10:37:07.376187+00	2022-01-21 10:37:07.376265+00	8	\N	\N	f	f
7397	PROJECT	Project	Angerman Markets Company	246894	2022-01-21 10:37:07.376366+00	2022-01-21 10:37:07.376406+00	8	\N	\N	f	f
7398	PROJECT	Project	Anonymous Customer HQ	246895	2022-01-21 10:37:07.395954+00	2022-01-21 10:37:07.396014+00	8	\N	\N	f	f
7399	PROJECT	Project	Another Killer Product	246896	2022-01-21 10:37:07.396128+00	2022-01-21 10:37:07.39617+00	8	\N	\N	f	f
7400	PROJECT	Project	Another Killer Product 1	246897	2022-01-21 10:37:07.396263+00	2022-01-21 10:37:07.396306+00	8	\N	\N	f	f
7401	PROJECT	Project	Anthony Jacobs	246898	2022-01-21 10:37:07.396653+00	2022-01-21 10:37:07.39683+00	8	\N	\N	f	f
7402	PROJECT	Project	Antioch Construction Company	246899	2022-01-21 10:37:07.396933+00	2022-01-21 10:37:07.397137+00	8	\N	\N	f	f
7403	PROJECT	Project	Apfel Electric Co.	246900	2022-01-21 10:37:07.39749+00	2022-01-21 10:37:07.397543+00	8	\N	\N	f	f
7404	PROJECT	Project	Applications to go Inc	246901	2022-01-21 10:37:07.399115+00	2022-01-21 10:37:07.399248+00	8	\N	\N	f	f
7405	PROJECT	Project	Aquino Apartments Dynamics	246902	2022-01-21 10:37:07.399381+00	2022-01-21 10:37:07.399421+00	8	\N	\N	f	f
7406	PROJECT	Project	Arcizo Automotive Sales	246903	2022-01-21 10:37:07.399514+00	2022-01-21 10:37:07.399556+00	8	\N	\N	f	f
7407	PROJECT	Project	Arlington Software Management	246904	2022-01-21 10:37:07.399645+00	2022-01-21 10:37:07.399683+00	8	\N	\N	f	f
7408	PROJECT	Project	Arnold Tanner	246905	2022-01-21 10:37:07.399769+00	2022-01-21 10:37:07.399808+00	8	\N	\N	f	f
7409	PROJECT	Project	Arredla and Hillseth Hardware -	246906	2022-01-21 10:37:07.399894+00	2022-01-21 10:37:07.399949+00	8	\N	\N	f	f
7410	PROJECT	Project	Art Institute of California	246907	2022-01-21 10:37:07.400036+00	2022-01-21 10:37:07.400075+00	8	\N	\N	f	f
7411	PROJECT	Project	Asch _ Agency	246908	2022-01-21 10:37:07.400162+00	2022-01-21 10:37:07.400201+00	8	\N	\N	f	f
7412	PROJECT	Project	Ashley Smoth	246909	2022-01-21 10:37:07.400289+00	2022-01-21 10:37:07.400328+00	8	\N	\N	f	f
7413	PROJECT	Project	Ashton Consulting Ltd	246910	2022-01-21 10:37:07.400415+00	2022-01-21 10:37:07.400452+00	8	\N	\N	f	f
7414	PROJECT	Project	Ashwinn	254145	2022-01-21 10:37:07.400541+00	2022-01-21 10:37:07.400579+00	8	\N	\N	f	f
7415	PROJECT	Project	Ashwinnnnnn	246821	2022-01-21 10:37:07.400665+00	2022-01-21 10:37:07.400703+00	8	\N	\N	f	f
7416	PROJECT	Project	Aslanian Publishing Agency	246911	2022-01-21 10:37:07.400789+00	2022-01-21 10:37:07.400827+00	8	\N	\N	f	f
7417	PROJECT	Project	Astry Software Holding Corp.	246912	2022-01-21 10:37:07.400913+00	2022-01-21 10:37:07.400951+00	8	\N	\N	f	f
7418	PROJECT	Project	Atherton Grocery	246913	2022-01-21 10:37:07.401038+00	2022-01-21 10:37:07.401075+00	8	\N	\N	f	f
7419	PROJECT	Project	August Li	246914	2022-01-21 10:37:07.40116+00	2022-01-21 10:37:07.401198+00	8	\N	\N	f	f
7420	PROJECT	Project	Ausbrooks Construction Incorporated	246915	2022-01-21 10:37:07.401285+00	2022-01-21 10:37:07.401324+00	8	\N	\N	f	f
7421	PROJECT	Project	Austin Builders Distributors	246916	2022-01-21 10:37:07.40141+00	2022-01-21 10:37:07.401447+00	8	\N	\N	f	f
7422	PROJECT	Project	Austin Publishing Inc.	246917	2022-01-21 10:37:07.401532+00	2022-01-21 10:37:07.40157+00	8	\N	\N	f	f
7423	PROJECT	Project	Avac Supplies Ltd.	246918	2022-01-21 10:37:07.401656+00	2022-01-21 10:37:07.401694+00	8	\N	\N	f	f
7424	PROJECT	Project	Avani Walters	246919	2022-01-21 10:37:07.40178+00	2022-01-21 10:37:07.401818+00	8	\N	\N	f	f
7425	PROJECT	Project	Axxess Group	246920	2022-01-21 10:37:07.401906+00	2022-01-21 10:37:07.401944+00	8	\N	\N	f	f
7426	PROJECT	Project	Baim Lumber -	246923	2022-01-21 10:37:07.402029+00	2022-01-21 10:37:07.402068+00	8	\N	\N	f	f
7427	PROJECT	Project	Bakkala Catering Distributors	246924	2022-01-21 10:37:07.402153+00	2022-01-21 10:37:07.402191+00	8	\N	\N	f	f
7428	PROJECT	Project	Bankey and Marris Hardware Corporation	246925	2022-01-21 10:37:07.402277+00	2022-01-21 10:37:07.402316+00	8	\N	\N	f	f
7429	PROJECT	Project	Barham Automotive Services	246926	2022-01-21 10:37:07.402402+00	2022-01-21 10:37:07.402438+00	8	\N	\N	f	f
7430	PROJECT	Project	Barich Metal Fabricators Inc.	246927	2022-01-21 10:37:07.402522+00	2022-01-21 10:37:07.402559+00	8	\N	\N	f	f
7431	PROJECT	Project	Barners and Rushlow Liquors Sales	246928	2022-01-21 10:37:07.402642+00	2022-01-21 10:37:07.402681+00	8	\N	\N	f	f
7432	PROJECT	Project	Barnhurst Title Inc.	246929	2022-01-21 10:37:07.402767+00	2022-01-21 10:37:07.402804+00	8	\N	\N	f	f
7433	PROJECT	Project	Baron Chess	246930	2022-01-21 10:37:07.402891+00	2022-01-21 10:37:07.402929+00	8	\N	\N	f	f
7434	PROJECT	Project	Bartkus Automotive Company	246931	2022-01-21 10:37:07.403018+00	2022-01-21 10:37:07.403055+00	8	\N	\N	f	f
7435	PROJECT	Project	Baumgarn Windows and Associates	246932	2022-01-21 10:37:07.403139+00	2022-01-21 10:37:07.403177+00	8	\N	\N	f	f
7436	PROJECT	Project	Bayas Hardware Dynamics	246935	2022-01-21 10:37:07.403262+00	2022-01-21 10:37:07.4033+00	8	\N	\N	f	f
7437	PROJECT	Project	Baylore	246936	2022-01-21 10:37:07.403387+00	2022-01-21 10:37:07.403425+00	8	\N	\N	f	f
7438	PROJECT	Project	Bay Media Research	246933	2022-01-21 10:37:07.40351+00	2022-01-21 10:37:07.403549+00	8	\N	\N	f	f
7439	PROJECT	Project	BaySide Office Space	246934	2022-01-21 10:37:07.403643+00	2022-01-21 10:37:07.403684+00	8	\N	\N	f	f
7440	PROJECT	Project	Beams Electric Agency	246937	2022-01-21 10:37:07.403776+00	2022-01-21 10:37:07.403815+00	8	\N	\N	f	f
7441	PROJECT	Project	Beatie Leasing Networking	246938	2022-01-21 10:37:07.404085+00	2022-01-21 10:37:07.40413+00	8	\N	\N	f	f
7442	PROJECT	Project	Beattie Batteries	246939	2022-01-21 10:37:07.404228+00	2022-01-21 10:37:07.404271+00	8	\N	\N	f	f
7443	PROJECT	Project	Beaubien Antiques Leasing	246940	2022-01-21 10:37:07.404363+00	2022-01-21 10:37:07.404402+00	8	\N	\N	f	f
7444	PROJECT	Project	Belgrade Telecom -	246941	2022-01-21 10:37:07.40449+00	2022-01-21 10:37:07.404529+00	8	\N	\N	f	f
7445	PROJECT	Project	Belisle Title Networking	246942	2022-01-21 10:37:07.404756+00	2022-01-21 10:37:07.404797+00	8	\N	\N	f	f
7446	PROJECT	Project	Below Liquors Corporation	246943	2022-01-21 10:37:07.404888+00	2022-01-21 10:37:07.404926+00	8	\N	\N	f	f
7447	PROJECT	Project	Bemo Publishing Corporation	246944	2022-01-21 10:37:07.405015+00	2022-01-21 10:37:07.405053+00	8	\N	\N	f	f
7448	PROJECT	Project	Benabides and Louris Builders Services	246947	2022-01-21 10:37:07.415383+00	2022-01-21 10:37:07.415432+00	8	\N	\N	f	f
7449	PROJECT	Project	Benbow Software	246948	2022-01-21 10:37:07.416141+00	2022-01-21 10:37:07.416225+00	8	\N	\N	f	f
7450	PROJECT	Project	Benge Liquors Incorporated	246949	2022-01-21 10:37:07.418362+00	2022-01-21 10:37:07.418454+00	8	\N	\N	f	f
7451	PROJECT	Project	Benjamin Yeung	278534	2022-01-21 10:37:07.418611+00	2022-01-21 10:37:07.418664+00	8	\N	\N	f	f
7452	PROJECT	Project	Ben Lomond Software Incorporated	246945	2022-01-21 10:37:07.41878+00	2022-01-21 10:37:07.418826+00	8	\N	\N	f	f
7453	PROJECT	Project	Bennett Consulting	246950	2022-01-21 10:37:07.418937+00	2022-01-21 10:37:07.419133+00	8	\N	\N	f	f
7454	PROJECT	Project	Ben Sandler	246946	2022-01-21 10:37:07.41925+00	2022-01-21 10:37:07.419295+00	8	\N	\N	f	f
7455	PROJECT	Project	Benton Construction Inc.	246951	2022-01-21 10:37:07.419398+00	2022-01-21 10:37:07.419439+00	8	\N	\N	f	f
7456	PROJECT	Project	Berliner Apartments Networking	246952	2022-01-21 10:37:07.419537+00	2022-01-21 10:37:07.419577+00	8	\N	\N	f	f
7457	PROJECT	Project	Berschauer Leasing Rentals	246953	2022-01-21 10:37:07.419674+00	2022-01-21 10:37:07.419715+00	8	\N	\N	f	f
7458	PROJECT	Project	Berthelette Antiques	246954	2022-01-21 10:37:07.419811+00	2022-01-21 10:37:07.41985+00	8	\N	\N	f	f
7459	PROJECT	Project	Bertot Attorneys Company	246955	2022-01-21 10:37:07.419944+00	2022-01-21 10:37:07.419985+00	8	\N	\N	f	f
7460	PROJECT	Project	Bertulli & Assoc	246956	2022-01-21 10:37:07.420244+00	2022-01-21 10:37:07.420285+00	8	\N	\N	f	f
7461	PROJECT	Project	Bethurum Telecom Sales	246957	2022-01-21 10:37:07.42038+00	2022-01-21 10:37:07.420421+00	8	\N	\N	f	f
7462	PROJECT	Project	Better Buy	246958	2022-01-21 10:37:07.420514+00	2022-01-21 10:37:07.420555+00	8	\N	\N	f	f
7463	PROJECT	Project	Bezak Construction Dynamics	246959	2022-01-21 10:37:07.420647+00	2022-01-21 10:37:07.420687+00	8	\N	\N	f	f
7464	PROJECT	Project	BFI Inc	246922	2022-01-21 10:37:07.42078+00	2022-01-21 10:37:07.42082+00	8	\N	\N	f	f
7465	PROJECT	Project	Bicycle Trailers	246960	2022-01-21 10:37:07.420913+00	2022-01-21 10:37:07.420953+00	8	\N	\N	f	f
7466	PROJECT	Project	Big 5 Sporting Goods	246961	2022-01-21 10:37:07.421046+00	2022-01-21 10:37:07.421087+00	8	\N	\N	f	f
7467	PROJECT	Project	Big Bear Lake Electric	246962	2022-01-21 10:37:07.421181+00	2022-01-21 10:37:07.42122+00	8	\N	\N	f	f
7468	PROJECT	Project	Big Bear Lake Plumbing Holding Corp.	246963	2022-01-21 10:37:07.421312+00	2022-01-21 10:37:07.421352+00	8	\N	\N	f	f
7469	PROJECT	Project	Billafuerte Software Company	246964	2022-01-21 10:37:07.421445+00	2022-01-21 10:37:07.421751+00	8	\N	\N	f	f
7470	PROJECT	Project	Bill's Windsurf Shop	246790	2022-01-21 10:37:07.421878+00	2022-01-21 10:37:07.42192+00	8	\N	\N	f	f
7471	PROJECT	Project	Bisonette Leasing	246965	2022-01-21 10:37:07.422021+00	2022-01-21 10:37:07.422061+00	8	\N	\N	f	f
7472	PROJECT	Project	Bleser Antiques Incorporated	246966	2022-01-21 10:37:07.42216+00	2022-01-21 10:37:07.422201+00	8	\N	\N	f	f
7473	PROJECT	Project	Blier Lumber Dynamics	246967	2022-01-21 10:37:07.422298+00	2022-01-21 10:37:07.42234+00	8	\N	\N	f	f
7474	PROJECT	Project	Blue Street Liquor Store	246968	2022-01-21 10:37:07.422442+00	2022-01-21 10:37:07.422483+00	8	\N	\N	f	f
7475	PROJECT	Project	Bobby Kelly	246972	2022-01-21 10:37:07.422578+00	2022-01-21 10:37:07.422618+00	8	\N	\N	f	f
7476	PROJECT	Project	Bobby Strands (Bobby@Strands.com)	246973	2022-01-21 10:37:07.422713+00	2022-01-21 10:37:07.422753+00	8	\N	\N	f	f
7477	PROJECT	Project	Bob Ledner	246969	2022-01-21 10:37:07.422845+00	2022-01-21 10:37:07.422885+00	8	\N	\N	f	f
7478	PROJECT	Project	Bob Smith (bsmith@bobsmith.com)	246970	2022-01-21 10:37:07.422977+00	2022-01-21 10:37:07.423017+00	8	\N	\N	f	f
7479	PROJECT	Project	Bob Walsh Funiture Store	246971	2022-01-21 10:37:07.423107+00	2022-01-21 10:37:07.423147+00	8	\N	\N	f	f
7480	PROJECT	Project	Bochenek and Skoog Liquors Company	246974	2022-01-21 10:37:07.423239+00	2022-01-21 10:37:07.423278+00	8	\N	\N	f	f
7481	PROJECT	Project	Bodfish Liquors Corporation	246975	2022-01-21 10:37:07.42337+00	2022-01-21 10:37:07.423408+00	8	\N	\N	f	f
7482	PROJECT	Project	Boise Antiques and Associates	246976	2022-01-21 10:37:07.423495+00	2022-01-21 10:37:07.42354+00	8	\N	\N	f	f
7483	PROJECT	Project	Boise Publishing Co.	246977	2022-01-21 10:37:07.423632+00	2022-01-21 10:37:07.423672+00	8	\N	\N	f	f
7484	PROJECT	Project	Boisselle Windows Distributors	246978	2022-01-21 10:37:07.423777+00	2022-01-21 10:37:07.423823+00	8	\N	\N	f	f
7485	PROJECT	Project	Bolder Construction Inc.	246979	2022-01-21 10:37:07.42392+00	2022-01-21 10:37:07.423962+00	8	\N	\N	f	f
7486	PROJECT	Project	Bollman Attorneys Company	246980	2022-01-21 10:37:07.424059+00	2022-01-21 10:37:07.424102+00	8	\N	\N	f	f
7487	PROJECT	Project	Bona Source	246981	2022-01-21 10:37:07.424204+00	2022-01-21 10:37:07.424244+00	8	\N	\N	f	f
7847	PROJECT	Project	Imran Kahn	247304	2022-01-21 10:37:07.647701+00	2022-01-21 10:37:07.647743+00	8	\N	\N	f	f
7488	PROJECT	Project	Boney Electric Dynamics	246982	2022-01-21 10:37:07.424488+00	2022-01-21 10:37:07.42453+00	8	\N	\N	f	f
7489	PROJECT	Project	Borowski Catering Management	246983	2022-01-21 10:37:07.424626+00	2022-01-21 10:37:07.424667+00	8	\N	\N	f	f
7490	PROJECT	Project	Botero Electric Co.	246984	2022-01-21 10:37:07.424951+00	2022-01-21 10:37:07.426964+00	8	\N	\N	f	f
7491	PROJECT	Project	Bowling Green Painting Incorporated	246985	2022-01-21 10:37:07.427175+00	2022-01-21 10:37:07.429083+00	8	\N	\N	f	f
7492	PROJECT	Project	Boynton Beach Title Networking	246986	2022-01-21 10:37:07.429947+00	2022-01-21 10:37:07.430024+00	8	\N	\N	f	f
7493	PROJECT	Project	Bracken Works Inc	246987	2022-01-21 10:37:07.4304+00	2022-01-21 10:37:07.430671+00	8	\N	\N	f	f
7494	PROJECT	Project	Braithwaite Tech	246988	2022-01-21 10:37:07.430766+00	2022-01-21 10:37:07.430799+00	8	\N	\N	f	f
7495	PROJECT	Project	Bramucci Construction	246989	2022-01-21 10:37:07.430862+00	2022-01-21 10:37:07.430892+00	8	\N	\N	f	f
7496	PROJECT	Project	Brandwein Builders Fabricators	246990	2022-01-21 10:37:07.430953+00	2022-01-21 10:37:07.430982+00	8	\N	\N	f	f
7497	PROJECT	Project	Brea Painting Company	246991	2022-01-21 10:37:07.431043+00	2022-01-21 10:37:07.431073+00	8	\N	\N	f	f
7498	PROJECT	Project	Brent Apartments Rentals	246992	2022-01-21 10:37:07.440404+00	2022-01-21 10:37:07.440448+00	8	\N	\N	f	f
7499	PROJECT	Project	Brewers Retail	246993	2022-01-21 10:37:07.440513+00	2022-01-21 10:37:07.440544+00	8	\N	\N	f	f
7500	PROJECT	Project	Brick Metal Fabricators Services	246994	2022-01-21 10:37:07.440606+00	2022-01-21 10:37:07.440636+00	8	\N	\N	f	f
7501	PROJECT	Project	Bridgham Electric Inc.	246995	2022-01-21 10:37:07.440697+00	2022-01-21 10:37:07.440727+00	8	\N	\N	f	f
7502	PROJECT	Project	Bright Brothers Design	246996	2022-01-21 10:37:07.440787+00	2022-01-21 10:37:07.440817+00	8	\N	\N	f	f
7503	PROJECT	Project	Broadnay and Posthuma Lumber and Associates	246997	2022-01-21 10:37:07.441451+00	2022-01-21 10:37:07.441491+00	8	\N	\N	f	f
7504	PROJECT	Project	Brochard Metal Fabricators Incorporated	246998	2022-01-21 10:37:07.441555+00	2022-01-21 10:37:07.441598+00	8	\N	\N	f	f
7505	PROJECT	Project	Brosey Antiques	278175	2022-01-21 10:37:07.44166+00	2022-01-21 10:37:07.441689+00	8	\N	\N	f	f
7506	PROJECT	Project	Brosey Antiques -	246999	2022-01-21 10:37:07.44175+00	2022-01-21 10:37:07.441779+00	8	\N	\N	f	f
7507	PROJECT	Project	Bruce Storm	247000	2022-01-21 10:37:07.44184+00	2022-01-21 10:37:07.441869+00	8	\N	\N	f	f
7508	PROJECT	Project	Brutsch Builders Incorporated	247001	2022-01-21 10:37:07.44193+00	2022-01-21 10:37:07.441959+00	8	\N	\N	f	f
7509	PROJECT	Project	Brytor Inetrnational	247002	2022-01-21 10:37:07.442022+00	2022-01-21 10:37:07.442052+00	8	\N	\N	f	f
7510	PROJECT	Project	B-Sharp Music	246921	2022-01-21 10:37:07.442114+00	2022-01-21 10:37:07.442143+00	8	\N	\N	f	f
7511	PROJECT	Project	Burney and Oesterreich Title Manufacturing	247003	2022-01-21 10:37:07.442204+00	2022-01-21 10:37:07.442233+00	8	\N	\N	f	f
7512	PROJECT	Project	Buroker Markets Incorporated	247004	2022-01-21 10:37:07.442294+00	2022-01-21 10:37:07.442323+00	8	\N	\N	f	f
7513	PROJECT	Project	Busacker Liquors Services	247005	2022-01-21 10:37:07.442384+00	2022-01-21 10:37:07.442413+00	8	\N	\N	f	f
7514	PROJECT	Project	Bushnell	247006	2022-01-21 10:37:07.442474+00	2022-01-21 10:37:07.442503+00	8	\N	\N	f	f
7515	PROJECT	Project	By The Beach Cafe	247007	2022-01-21 10:37:07.442564+00	2022-01-21 10:37:07.442593+00	8	\N	\N	f	f
7516	PROJECT	Project	Caleb Attorneys Distributors	247014	2022-01-21 10:37:07.442654+00	2022-01-21 10:37:07.442684+00	8	\N	\N	f	f
7517	PROJECT	Project	Calley Leasing and Associates	247015	2022-01-21 10:37:07.442744+00	2022-01-21 10:37:07.442773+00	8	\N	\N	f	f
7518	PROJECT	Project	Cambareri Painting Sales	247016	2022-01-21 10:37:07.442834+00	2022-01-21 10:37:07.442863+00	8	\N	\N	f	f
7519	PROJECT	Project	Canadian Customer	247017	2022-01-21 10:37:07.442924+00	2022-01-21 10:37:07.442953+00	8	\N	\N	f	f
7520	PROJECT	Project	Canuck Door Systems Co.	247018	2022-01-21 10:37:07.443015+00	2022-01-21 10:37:07.443044+00	8	\N	\N	f	f
7521	PROJECT	Project	Capano Labs	247019	2022-01-21 10:37:07.443104+00	2022-01-21 10:37:07.443133+00	8	\N	\N	f	f
7522	PROJECT	Project	Caquias and Jank Catering Distributors	247020	2022-01-21 10:37:07.443194+00	2022-01-21 10:37:07.443223+00	8	\N	\N	f	f
7523	PROJECT	Project	Careymon Dudley	247021	2022-01-21 10:37:07.443283+00	2022-01-21 10:37:07.443312+00	8	\N	\N	f	f
7524	PROJECT	Project	Carloni Builders Company	247022	2022-01-21 10:37:07.443373+00	2022-01-21 10:37:07.443402+00	8	\N	\N	f	f
7525	PROJECT	Project	Carlos Beato	247023	2022-01-21 10:37:07.443462+00	2022-01-21 10:37:07.443491+00	8	\N	\N	f	f
7526	PROJECT	Project	Carmel Valley Metal Fabricators Holding Corp.	247024	2022-01-21 10:37:07.443551+00	2022-01-21 10:37:07.44358+00	8	\N	\N	f	f
7527	PROJECT	Project	Carpentersville Publishing	247025	2022-01-21 10:37:07.443641+00	2022-01-21 10:37:07.44367+00	8	\N	\N	f	f
7528	PROJECT	Project	Carpinteria Leasing Services	247026	2022-01-21 10:37:07.44373+00	2022-01-21 10:37:07.443759+00	8	\N	\N	f	f
7529	PROJECT	Project	Carrie Davis	247027	2022-01-21 10:37:07.443819+00	2022-01-21 10:37:07.443848+00	8	\N	\N	f	f
7530	PROJECT	Project	Cash & Warren	247028	2022-01-21 10:37:07.443908+00	2022-01-21 10:37:07.443937+00	8	\N	\N	f	f
7531	PROJECT	Project	Castek Inc	247029	2022-01-21 10:37:07.443996+00	2022-01-21 10:37:07.444026+00	8	\N	\N	f	f
7532	PROJECT	Project	Casuse Liquors Inc.	247030	2022-01-21 10:37:07.444086+00	2022-01-21 10:37:07.444115+00	8	\N	\N	f	f
7533	PROJECT	Project	Cathy Quon	278535	2022-01-21 10:37:07.444175+00	2022-01-21 10:37:07.444204+00	8	\N	\N	f	f
7534	PROJECT	Project	Cathy Thoms	247031	2022-01-21 10:37:07.444265+00	2022-01-21 10:37:07.444294+00	8	\N	\N	f	f
7535	PROJECT	Project	Cawthron and Ullo Windows Corporation	247032	2022-01-21 10:37:07.444355+00	2022-01-21 10:37:07.444384+00	8	\N	\N	f	f
7536	PROJECT	Project	Celia Corp	247033	2022-01-21 10:37:07.444443+00	2022-01-21 10:37:07.444472+00	8	\N	\N	f	f
7537	PROJECT	Project	Central Islip Antiques Fabricators	247034	2022-01-21 10:37:07.444533+00	2022-01-21 10:37:07.444562+00	8	\N	\N	f	f
7538	PROJECT	Project	Cerritos Telecom and Associates	247035	2022-01-21 10:37:07.444622+00	2022-01-21 10:37:07.444651+00	8	\N	\N	f	f
7539	PROJECT	Project	CH2M Hill Ltd	247008	2022-01-21 10:37:07.444711+00	2022-01-21 10:37:07.44474+00	8	\N	\N	f	f
7540	PROJECT	Project	Chadha's Consultants	278536	2022-01-21 10:37:07.4448+00	2022-01-21 10:37:07.444829+00	8	\N	\N	f	f
7541	PROJECT	Project	Chamberlain Service Ltd	247036	2022-01-21 10:37:07.44489+00	2022-01-21 10:37:07.444919+00	8	\N	\N	f	f
7542	PROJECT	Project	Champaign Painting Rentals	247037	2022-01-21 10:37:07.44498+00	2022-01-21 10:37:07.445009+00	8	\N	\N	f	f
7543	PROJECT	Project	Chandrasekara Markets Sales	247038	2022-01-21 10:37:07.44533+00	2022-01-21 10:37:07.445399+00	8	\N	\N	f	f
7544	PROJECT	Project	Channer Antiques Dynamics	247039	2022-01-21 10:37:07.445519+00	2022-01-21 10:37:07.445561+00	8	\N	\N	f	f
7545	PROJECT	Project	Charlie Whitehead	278537	2022-01-21 10:37:07.445657+00	2022-01-21 10:37:07.445697+00	8	\N	\N	f	f
7546	PROJECT	Project	Charlotte Hospital Incorporated	247040	2022-01-21 10:37:07.445788+00	2022-01-21 10:37:07.445827+00	8	\N	\N	f	f
7547	PROJECT	Project	Cheese Factory	247041	2022-01-21 10:37:07.445918+00	2022-01-21 10:37:07.445957+00	8	\N	\N	f	f
7548	PROJECT	Project	Cheng-Cheng Lok	278538	2022-01-21 10:37:07.465312+00	2022-01-21 10:37:07.465857+00	8	\N	\N	f	f
7549	PROJECT	Project	Chess Art Gallery	247042	2022-01-21 10:37:07.466994+00	2022-01-21 10:37:07.467077+00	8	\N	\N	f	f
7550	PROJECT	Project	Chiaminto Attorneys Agency	247043	2022-01-21 10:37:07.467237+00	2022-01-21 10:37:07.46729+00	8	\N	\N	f	f
7551	PROJECT	Project	China Cuisine	247044	2022-01-21 10:37:07.467425+00	2022-01-21 10:37:07.467474+00	8	\N	\N	f	f
7552	PROJECT	Project	Chittenden _ Agency	247045	2022-01-21 10:37:07.468216+00	2022-01-21 10:37:07.468304+00	8	\N	\N	f	f
7553	PROJECT	Project	CICA	247009	2022-01-21 10:37:07.468456+00	2022-01-21 10:37:07.468516+00	8	\N	\N	f	f
7554	PROJECT	Project	Cino & Cino	247046	2022-01-21 10:37:07.46865+00	2022-01-21 10:37:07.468919+00	8	\N	\N	f	f
7555	PROJECT	Project	Circuit Cities	247047	2022-01-21 10:37:07.469081+00	2022-01-21 10:37:07.469141+00	8	\N	\N	f	f
7556	PROJECT	Project	CIS Environmental Services	247010	2022-01-21 10:37:07.469279+00	2022-01-21 10:37:07.469335+00	8	\N	\N	f	f
7557	PROJECT	Project	Clayton and Bubash Telecom Services	247048	2022-01-21 10:37:07.469467+00	2022-01-21 10:37:07.469518+00	8	\N	\N	f	f
7558	PROJECT	Project	Clement's Cleaners	278539	2022-01-21 10:37:07.469641+00	2022-01-21 10:37:07.46969+00	8	\N	\N	f	f
7559	PROJECT	Project	Clubb Electric Co.	247049	2022-01-21 10:37:07.469808+00	2022-01-21 10:37:07.469858+00	8	\N	\N	f	f
7560	PROJECT	Project	Cochell Markets Group	247050	2022-01-21 10:37:07.469974+00	2022-01-21 10:37:07.470021+00	8	\N	\N	f	f
7561	PROJECT	Project	Coen Publishing Co.	247051	2022-01-21 10:37:07.470134+00	2022-01-21 10:37:07.47019+00	8	\N	\N	f	f
7562	PROJECT	Project	Coklow Leasing Dynamics	247052	2022-01-21 10:37:07.47077+00	2022-01-21 10:37:07.470831+00	8	\N	\N	f	f
7563	PROJECT	Project	Coletta Hospital Inc.	247053	2022-01-21 10:37:07.471072+00	2022-01-21 10:37:07.471613+00	8	\N	\N	f	f
7564	PROJECT	Project	Colony Antiques	247054	2022-01-21 10:37:07.471713+00	2022-01-21 10:37:07.471743+00	8	\N	\N	f	f
7565	PROJECT	Project	Colorado Springs Leasing Fabricators	247055	2022-01-21 10:37:07.471806+00	2022-01-21 10:37:07.471836+00	8	\N	\N	f	f
7566	PROJECT	Project	Colosimo Catering and Associates	247056	2022-01-21 10:37:07.471897+00	2022-01-21 10:37:07.471926+00	8	\N	\N	f	f
7567	PROJECT	Project	Company 1618550408	249071	2022-01-21 10:37:07.471987+00	2022-01-21 10:37:07.472016+00	8	\N	\N	f	f
7568	PROJECT	Project	Company 1618566776	250488	2022-01-21 10:37:07.472077+00	2022-01-21 10:37:07.472106+00	8	\N	\N	f	f
7569	PROJECT	Project	Computer Literacy	247057	2022-01-21 10:37:07.472166+00	2022-01-21 10:37:07.472195+00	8	\N	\N	f	f
7570	PROJECT	Project	Computer Training Associates	247058	2022-01-21 10:37:07.472256+00	2022-01-21 10:37:07.472286+00	8	\N	\N	f	f
7571	PROJECT	Project	Connectus	247059	2022-01-21 10:37:07.472346+00	2022-01-21 10:37:07.472375+00	8	\N	\N	f	f
7572	PROJECT	Project	Constanza Liquors -	247060	2022-01-21 10:37:07.472435+00	2022-01-21 10:37:07.472464+00	8	\N	\N	f	f
7573	PROJECT	Project	Conteras Liquors Agency	247061	2022-01-21 10:37:07.472524+00	2022-01-21 10:37:07.472554+00	8	\N	\N	f	f
7574	PROJECT	Project	Conterras and Katen Attorneys Services	247062	2022-01-21 10:37:07.4731+00	2022-01-21 10:37:07.473149+00	8	\N	\N	f	f
7575	PROJECT	Project	Convery Attorneys and Associates	247063	2022-01-21 10:37:07.473217+00	2022-01-21 10:37:07.473247+00	8	\N	\N	f	f
7576	PROJECT	Project	Conway Products	247064	2022-01-21 10:37:07.473309+00	2022-01-21 10:37:07.473339+00	8	\N	\N	f	f
7577	PROJECT	Project	Cool Cars	246791	2022-01-21 10:37:07.4734+00	2022-01-21 10:37:07.473429+00	8	\N	\N	f	f
7578	PROJECT	Project	Cooler Title Company	247065	2022-01-21 10:37:07.47349+00	2022-01-21 10:37:07.473519+00	8	\N	\N	f	f
7579	PROJECT	Project	Cooper Equipment	247066	2022-01-21 10:37:07.473597+00	2022-01-21 10:37:07.473626+00	8	\N	\N	f	f
7580	PROJECT	Project	Cooper Industries	247067	2022-01-21 10:37:07.473686+00	2022-01-21 10:37:07.473716+00	8	\N	\N	f	f
7581	PROJECT	Project	Core Care Canada	247068	2022-01-21 10:37:07.473777+00	2022-01-21 10:37:07.473806+00	8	\N	\N	f	f
7582	PROJECT	Project	Core Care Technologies Inc.	247069	2022-01-21 10:37:07.473867+00	2022-01-21 10:37:07.473895+00	8	\N	\N	f	f
7583	PROJECT	Project	Coressel _ -	247070	2022-01-21 10:37:07.473956+00	2022-01-21 10:37:07.473985+00	8	\N	\N	f	f
7584	PROJECT	Project	Cosimini Software Agency	247071	2022-01-21 10:37:07.474046+00	2022-01-21 10:37:07.474076+00	8	\N	\N	f	f
7585	PROJECT	Project	Cotterman Software Company	247072	2022-01-21 10:37:07.474136+00	2022-01-21 10:37:07.474165+00	8	\N	\N	f	f
7586	PROJECT	Project	Cottew Publishing Inc.	247073	2022-01-21 10:37:07.474226+00	2022-01-21 10:37:07.474255+00	8	\N	\N	f	f
7587	PROJECT	Project	Cottman Publishing Manufacturing	247074	2022-01-21 10:37:07.474315+00	2022-01-21 10:37:07.474344+00	8	\N	\N	f	f
7588	PROJECT	Project	Coxum Software Dynamics	247075	2022-01-21 10:37:07.474405+00	2022-01-21 10:37:07.474434+00	8	\N	\N	f	f
7589	PROJECT	Project	CPSA	247012	2022-01-21 10:37:07.474495+00	2022-01-21 10:37:07.474826+00	8	\N	\N	f	f
7590	PROJECT	Project	CPS ltd	247011	2022-01-21 10:37:07.474952+00	2022-01-21 10:37:07.474987+00	8	\N	\N	f	f
7591	PROJECT	Project	Cray Systems	247076	2022-01-21 10:37:07.475094+00	2022-01-21 10:37:07.475145+00	8	\N	\N	f	f
7592	PROJECT	Project	Creasman Antiques Holding Corp.	247077	2022-01-21 10:37:07.475253+00	2022-01-21 10:37:07.475302+00	8	\N	\N	f	f
7593	PROJECT	Project	Creighton & Company	247078	2022-01-21 10:37:07.475416+00	2022-01-21 10:37:07.475464+00	8	\N	\N	f	f
7594	PROJECT	Project	Crighton Catering Company	247079	2022-01-21 10:37:07.475576+00	2022-01-21 10:37:07.475625+00	8	\N	\N	f	f
7595	PROJECT	Project	Crisafulli Hardware Holding Corp.	247080	2022-01-21 10:37:07.475736+00	2022-01-21 10:37:07.475781+00	8	\N	\N	f	f
7596	PROJECT	Project	Cruce Builders	247081	2022-01-21 10:37:07.47589+00	2022-01-21 10:37:07.47594+00	8	\N	\N	f	f
7597	PROJECT	Project	Culprit Inc.	247082	2022-01-21 10:37:07.476052+00	2022-01-21 10:37:07.476098+00	8	\N	\N	f	f
7598	PROJECT	Project	Customer Mapped Project	243609	2022-01-21 10:37:07.486576+00	2022-01-21 10:37:07.486639+00	8	\N	\N	f	f
7599	PROJECT	Project	Customer Sravan	274656	2022-01-21 10:37:07.486754+00	2022-01-21 10:37:07.486796+00	8	\N	\N	f	f
7600	PROJECT	Project	CVM Business Solutions	247013	2022-01-21 10:37:07.486895+00	2022-01-21 10:37:07.486937+00	8	\N	\N	f	f
7601	PROJECT	Project	Cwik and Klayman Metal Fabricators Holding Corp.	247083	2022-01-21 10:37:07.487032+00	2022-01-21 10:37:07.487074+00	8	\N	\N	f	f
7602	PROJECT	Project	Cytec Industries Inc	247084	2022-01-21 10:37:07.487169+00	2022-01-21 10:37:07.48721+00	8	\N	\N	f	f
7603	PROJECT	Project	Dale Jenson	247086	2022-01-21 10:37:07.487308+00	2022-01-21 10:37:07.487349+00	8	\N	\N	f	f
7604	PROJECT	Project	Dambrose and Ottum Leasing Holding Corp.	247087	2022-01-21 10:37:07.487646+00	2022-01-21 10:37:07.487676+00	8	\N	\N	f	f
7605	PROJECT	Project	Danniels Antiques Inc.	247088	2022-01-21 10:37:07.487738+00	2022-01-21 10:37:07.487767+00	8	\N	\N	f	f
7606	PROJECT	Project	Daquino Painting -	247089	2022-01-21 10:37:07.487828+00	2022-01-21 10:37:07.487858+00	8	\N	\N	f	f
7607	PROJECT	Project	Dary Construction Corporation	247090	2022-01-21 10:37:07.487918+00	2022-01-21 10:37:07.487948+00	8	\N	\N	f	f
7608	PROJECT	Project	David Langhor	247091	2022-01-21 10:37:07.488008+00	2022-01-21 10:37:07.488037+00	8	\N	\N	f	f
7609	PROJECT	Project	Days Creek Electric Services	247092	2022-01-21 10:37:07.488097+00	2022-01-21 10:37:07.488127+00	8	\N	\N	f	f
7610	PROJECT	Project	Deblasio Painting Holding Corp.	247093	2022-01-21 10:37:07.488187+00	2022-01-21 10:37:07.488216+00	8	\N	\N	f	f
7611	PROJECT	Project	Defaveri Construction	247094	2022-01-21 10:37:07.488276+00	2022-01-21 10:37:07.488305+00	8	\N	\N	f	f
7612	PROJECT	Project	Dehaney Liquors Co.	247095	2022-01-21 10:37:07.488366+00	2022-01-21 10:37:07.488395+00	8	\N	\N	f	f
7613	PROJECT	Project	DellPack (UK)	247097	2022-01-21 10:37:07.488455+00	2022-01-21 10:37:07.488485+00	8	\N	\N	f	f
7614	PROJECT	Project	DelRey Distributors	247096	2022-01-21 10:37:07.488546+00	2022-01-21 10:37:07.488575+00	8	\N	\N	f	f
7615	PROJECT	Project	Demaire Automotive Systems	247098	2022-01-21 10:37:07.488636+00	2022-01-21 10:37:07.488665+00	8	\N	\N	f	f
7616	PROJECT	Project	Denise Sweet	247099	2022-01-21 10:37:07.488726+00	2022-01-21 10:37:07.488755+00	8	\N	\N	f	f
7617	PROJECT	Project	Dennis Batemanger	247100	2022-01-21 10:37:07.488815+00	2022-01-21 10:37:07.491578+00	8	\N	\N	f	f
7618	PROJECT	Project	D&H Manufacturing	247085	2022-01-21 10:37:07.491808+00	2022-01-21 10:37:07.491854+00	8	\N	\N	f	f
7619	PROJECT	Project	Diamond Bar Plumbing	247101	2022-01-21 10:37:07.491947+00	2022-01-21 10:37:07.491987+00	8	\N	\N	f	f
7620	PROJECT	Project	Diego Rodriguez	246792	2022-01-21 10:37:07.492077+00	2022-01-21 10:37:07.492116+00	8	\N	\N	f	f
7621	PROJECT	Project	Diego Rodriguez:Test Project	246793	2022-01-21 10:37:07.492204+00	2022-01-21 10:37:07.492242+00	8	\N	\N	f	f
7622	PROJECT	Project	Diekema Attorneys Manufacturing	247102	2022-01-21 10:37:07.492332+00	2022-01-21 10:37:07.49237+00	8	\N	\N	f	f
7623	PROJECT	Project	Difebbo and Lewelling Markets Agency	247103	2022-01-21 10:37:07.492458+00	2022-01-21 10:37:07.492497+00	8	\N	\N	f	f
7624	PROJECT	Project	Dillain Collins	247104	2022-01-21 10:37:07.492584+00	2022-01-21 10:37:07.492622+00	8	\N	\N	f	f
7625	PROJECT	Project	Diluzio Automotive Group	247105	2022-01-21 10:37:07.492712+00	2022-01-21 10:37:07.492751+00	8	\N	\N	f	f
7626	PROJECT	Project	Dipiano Automotive Sales	247106	2022-01-21 10:37:07.492841+00	2022-01-21 10:37:07.492881+00	8	\N	\N	f	f
7627	PROJECT	Project	Doerrer Apartments Inc.	247107	2022-01-21 10:37:07.492971+00	2022-01-21 10:37:07.493013+00	8	\N	\N	f	f
7628	PROJECT	Project	Dogan Painting Leasing	247108	2022-01-21 10:37:07.493105+00	2022-01-21 10:37:07.493143+00	8	\N	\N	f	f
7629	PROJECT	Project	Doiel and Mcdivitt Construction Holding Corp.	247109	2022-01-21 10:37:07.493231+00	2022-01-21 10:37:07.493269+00	8	\N	\N	f	f
7630	PROJECT	Project	Dolfi Software Group	247110	2022-01-21 10:37:07.493359+00	2022-01-21 10:37:07.493397+00	8	\N	\N	f	f
7631	PROJECT	Project	Dominion Consulting	247111	2022-01-21 10:37:07.493485+00	2022-01-21 10:37:07.493523+00	8	\N	\N	f	f
7632	PROJECT	Project	Dorey Attorneys Distributors	247112	2022-01-21 10:37:07.493611+00	2022-01-21 10:37:07.49365+00	8	\N	\N	f	f
7633	PROJECT	Project	Dorminy Windows Rentals	247113	2022-01-21 10:37:07.493738+00	2022-01-21 10:37:07.493775+00	8	\N	\N	f	f
7634	PROJECT	Project	Douse Telecom Leasing	247114	2022-01-21 10:37:07.493864+00	2022-01-21 10:37:07.493902+00	8	\N	\N	f	f
7635	PROJECT	Project	Downey and Sweezer Electric Group	247116	2022-01-21 10:37:07.49399+00	2022-01-21 10:37:07.494028+00	8	\N	\N	f	f
7636	PROJECT	Project	Downey Catering Agency	247115	2022-01-21 10:37:07.494116+00	2022-01-21 10:37:07.494154+00	8	\N	\N	f	f
7637	PROJECT	Project	Dries Hospital Manufacturing	247117	2022-01-21 10:37:07.494243+00	2022-01-21 10:37:07.494281+00	8	\N	\N	f	f
7638	PROJECT	Project	Drown Markets Services	247118	2022-01-21 10:37:07.494369+00	2022-01-21 10:37:07.494408+00	8	\N	\N	f	f
7639	PROJECT	Project	Drumgoole Attorneys Corporation	247119	2022-01-21 10:37:07.494496+00	2022-01-21 10:37:07.494535+00	8	\N	\N	f	f
7640	PROJECT	Project	Duhamel Lumber Co.	247120	2022-01-21 10:37:07.494623+00	2022-01-21 10:37:07.494662+00	8	\N	\N	f	f
7641	PROJECT	Project	Dukes Basketball Camp	246794	2022-01-21 10:37:07.494751+00	2022-01-21 10:37:07.494788+00	8	\N	\N	f	f
7642	PROJECT	Project	Duman Windows Sales	247121	2022-01-21 10:37:07.494875+00	2022-01-21 10:37:07.494913+00	8	\N	\N	f	f
7643	PROJECT	Project	Dunlevy Software Corporation	247122	2022-01-21 10:37:07.494999+00	2022-01-21 10:37:07.495036+00	8	\N	\N	f	f
7644	PROJECT	Project	Duroseau Publishing	247123	2022-01-21 10:37:07.495122+00	2022-01-21 10:37:07.495159+00	8	\N	\N	f	f
7645	PROJECT	Project	Dylan Sollfrank	246795	2022-01-21 10:37:07.495247+00	2022-01-21 10:37:07.495747+00	8	\N	\N	f	f
7646	PROJECT	Project	Eachus Metal Fabricators Incorporated	247124	2022-01-21 10:37:07.495857+00	2022-01-21 10:37:07.495895+00	8	\N	\N	f	f
7647	PROJECT	Project	Eberlein and Preslipsky _ Holding Corp.	247125	2022-01-21 10:37:07.495982+00	2022-01-21 10:37:07.496019+00	8	\N	\N	f	f
7648	PROJECT	Project	Ecker Designs	278540	2022-01-21 10:37:07.506506+00	2022-01-21 10:37:07.506555+00	8	\N	\N	f	f
7649	PROJECT	Project	Eckerman Leasing Management	247126	2022-01-21 10:37:07.506639+00	2022-01-21 10:37:07.506674+00	8	\N	\N	f	f
7650	PROJECT	Project	Eckler Leasing	247127	2022-01-21 10:37:07.506746+00	2022-01-21 10:37:07.506778+00	8	\N	\N	f	f
7651	PROJECT	Project	Eckrote Construction Fabricators	247128	2022-01-21 10:37:07.506848+00	2022-01-21 10:37:07.506878+00	8	\N	\N	f	f
7652	PROJECT	Project	Ede Title Rentals	247130	2022-01-21 10:37:07.506945+00	2022-01-21 10:37:07.506975+00	8	\N	\N	f	f
7653	PROJECT	Project	Edin Lumber Distributors	247131	2022-01-21 10:37:07.50704+00	2022-01-21 10:37:07.50707+00	8	\N	\N	f	f
7654	PROJECT	Project	Ed Obuz	247129	2022-01-21 10:37:07.507133+00	2022-01-21 10:37:07.507163+00	8	\N	\N	f	f
7655	PROJECT	Project	Effectiovation Inc	247132	2022-01-21 10:37:07.507227+00	2022-01-21 10:37:07.507257+00	8	\N	\N	f	f
7656	PROJECT	Project	Efficiency Engineering	247133	2022-01-21 10:37:07.50732+00	2022-01-21 10:37:07.507349+00	8	\N	\N	f	f
7657	PROJECT	Project	Eichner Antiques -	247134	2022-01-21 10:37:07.507412+00	2022-01-21 10:37:07.507441+00	8	\N	\N	f	f
7658	PROJECT	Project	Electronics Direct to You	247136	2022-01-21 10:37:07.507504+00	2022-01-21 10:37:07.507533+00	8	\N	\N	f	f
7659	PROJECT	Project	Elegance Interior Design	247137	2022-01-21 10:37:07.507595+00	2022-01-21 10:37:07.507625+00	8	\N	\N	f	f
7660	PROJECT	Project	Eliszewski Windows Dynamics	247138	2022-01-21 10:37:07.507687+00	2022-01-21 10:37:07.507716+00	8	\N	\N	f	f
7661	PROJECT	Project	Ellenberger Windows Management	247139	2022-01-21 10:37:07.507778+00	2022-01-21 10:37:07.507807+00	8	\N	\N	f	f
7662	PROJECT	Project	El Paso Hardware Co.	247135	2022-01-21 10:37:07.507868+00	2022-01-21 10:37:07.507898+00	8	\N	\N	f	f
7663	PROJECT	Project	Emergys	247140	2022-01-21 10:37:07.50796+00	2022-01-21 10:37:07.507989+00	8	\N	\N	f	f
7664	PROJECT	Project	Empire Financial Group	247141	2022-01-21 10:37:07.508051+00	2022-01-21 10:37:07.508081+00	8	\N	\N	f	f
7665	PROJECT	Project	eNable Corp	247929	2022-01-21 10:37:07.508142+00	2022-01-21 10:37:07.508172+00	8	\N	\N	f	f
7666	PROJECT	Project	Engelkemier Catering Management	247142	2022-01-21 10:37:07.508233+00	2022-01-21 10:37:07.508262+00	8	\N	\N	f	f
7667	PROJECT	Project	Epling Builders Inc.	247143	2022-01-21 10:37:07.508324+00	2022-01-21 10:37:07.508353+00	8	\N	\N	f	f
7668	PROJECT	Project	Eric Korb	247144	2022-01-21 10:37:07.509121+00	2022-01-21 10:37:07.509184+00	8	\N	\N	f	f
7669	PROJECT	Project	Eric Schmidt	247145	2022-01-21 10:37:07.509285+00	2022-01-21 10:37:07.509326+00	8	\N	\N	f	f
7670	PROJECT	Project	Erin Kessman	247146	2022-01-21 10:37:07.509418+00	2022-01-21 10:37:07.509458+00	8	\N	\N	f	f
7671	PROJECT	Project	Ertle Painting Leasing	247147	2022-01-21 10:37:07.50955+00	2022-01-21 10:37:07.509593+00	8	\N	\N	f	f
7672	PROJECT	Project	Espar Heater Systems	247148	2022-01-21 10:37:07.509685+00	2022-01-21 10:37:07.509727+00	8	\N	\N	f	f
7673	PROJECT	Project	Estanislau and Brodka Electric Holding Corp.	247149	2022-01-21 10:37:07.509822+00	2022-01-21 10:37:07.51056+00	8	\N	\N	f	f
7674	PROJECT	Project	Estee Lauder	247150	2022-01-21 10:37:07.510746+00	2022-01-21 10:37:07.510803+00	8	\N	\N	f	f
7675	PROJECT	Project	Estevez Title and Associates	247151	2022-01-21 10:37:07.510967+00	2022-01-21 10:37:07.511018+00	8	\N	\N	f	f
7676	PROJECT	Project	Eugenio	247152	2022-01-21 10:37:07.511383+00	2022-01-21 10:37:07.513219+00	8	\N	\N	f	f
7677	PROJECT	Project	Evans Leasing Fabricators	247153	2022-01-21 10:37:07.513755+00	2022-01-21 10:37:07.513823+00	8	\N	\N	f	f
7678	PROJECT	Project	Everett Fine Wines	247154	2022-01-21 10:37:07.51395+00	2022-01-21 10:37:07.55836+00	8	\N	\N	f	f
7679	PROJECT	Project	Everett International	247155	2022-01-21 10:37:07.567794+00	2022-01-21 10:37:07.569934+00	8	\N	\N	f	f
7680	PROJECT	Project	Eyram Marketing	247156	2022-01-21 10:37:07.570039+00	2022-01-21 10:37:07.57007+00	8	\N	\N	f	f
7681	PROJECT	Project	Fabre Enterprises	247160	2022-01-21 10:37:07.570133+00	2022-01-21 10:37:07.570163+00	8	\N	\N	f	f
7682	PROJECT	Project	Fabrizio's Dry Cleaners	247161	2022-01-21 10:37:07.570224+00	2022-01-21 10:37:07.570254+00	8	\N	\N	f	f
7683	PROJECT	Project	Fagnani Builders	247162	2022-01-21 10:37:07.570314+00	2022-01-21 10:37:07.570344+00	8	\N	\N	f	f
7684	PROJECT	Project	FA-HB Inc.	247157	2022-01-21 10:37:07.570405+00	2022-01-21 10:37:07.570435+00	8	\N	\N	f	f
7685	PROJECT	Project	FA-HB Job	247158	2022-01-21 10:37:07.570495+00	2022-01-21 10:37:07.570524+00	8	\N	\N	f	f
7686	PROJECT	Project	Falls Church _ Agency	247163	2022-01-21 10:37:07.570585+00	2022-01-21 10:37:07.570614+00	8	\N	\N	f	f
7687	PROJECT	Project	Fantasy Gemmart	247164	2022-01-21 10:37:07.570674+00	2022-01-21 10:37:07.570704+00	8	\N	\N	f	f
7688	PROJECT	Project	Fasefax Systems	247165	2022-01-21 10:37:07.570764+00	2022-01-21 10:37:07.570794+00	8	\N	\N	f	f
7689	PROJECT	Project	Faske Software Group	247166	2022-01-21 10:37:07.570853+00	2022-01-21 10:37:07.570883+00	8	\N	\N	f	f
7690	PROJECT	Project	Fauerbach _ Agency	247167	2022-01-21 10:37:07.570943+00	2022-01-21 10:37:07.570973+00	8	\N	\N	f	f
7691	PROJECT	Project	Fenceroy and Herling Metal Fabricators Management	247168	2022-01-21 10:37:07.571034+00	2022-01-21 10:37:07.571063+00	8	\N	\N	f	f
7692	PROJECT	Project	Fernstrom Automotive Systems	247169	2022-01-21 10:37:07.571124+00	2022-01-21 10:37:07.571153+00	8	\N	\N	f	f
7693	PROJECT	Project	Ferrio and Donlon Builders Management	247170	2022-01-21 10:37:07.571214+00	2022-01-21 10:37:07.571243+00	8	\N	\N	f	f
7694	PROJECT	Project	Fetterolf and Loud Apartments Inc.	247171	2022-01-21 10:37:07.571304+00	2022-01-21 10:37:07.571333+00	8	\N	\N	f	f
7695	PROJECT	Project	Ficke Apartments Group	247172	2022-01-21 10:37:07.571394+00	2022-01-21 10:37:07.571423+00	8	\N	\N	f	f
7696	PROJECT	Project	FigmentSoft Inc	247173	2022-01-21 10:37:07.571483+00	2022-01-21 10:37:07.571513+00	8	\N	\N	f	f
7697	PROJECT	Project	Fiore Fashion Inc	247174	2022-01-21 10:37:07.571573+00	2022-01-21 10:37:07.571603+00	8	\N	\N	f	f
7698	PROJECT	Project	Fixed Fee Project with Five Tasks	284355	2022-01-21 10:37:07.581884+00	2022-01-21 10:37:07.581926+00	8	\N	\N	f	f
7699	PROJECT	Project	Florence Liquors and Associates	247175	2022-01-21 10:37:07.581989+00	2022-01-21 10:37:07.582019+00	8	\N	\N	f	f
7700	PROJECT	Project	Flores Inc	247176	2022-01-21 10:37:07.582081+00	2022-01-21 10:37:07.582111+00	8	\N	\N	f	f
7701	PROJECT	Project	Focal Point Opticians	247177	2022-01-21 10:37:07.582172+00	2022-01-21 10:37:07.582201+00	8	\N	\N	f	f
7702	PROJECT	Project	Ford Models Inc	247178	2022-01-21 10:37:07.582262+00	2022-01-21 10:37:07.582291+00	8	\N	\N	f	f
7703	PROJECT	Project	Forest Grove Liquors Company	247179	2022-01-21 10:37:07.582352+00	2022-01-21 10:37:07.582382+00	8	\N	\N	f	f
7704	PROJECT	Project	Formal Furnishings	247180	2022-01-21 10:37:07.582443+00	2022-01-21 10:37:07.582472+00	8	\N	\N	f	f
7705	PROJECT	Project	Formisano Hardware -	247181	2022-01-21 10:37:07.582533+00	2022-01-21 10:37:07.582563+00	8	\N	\N	f	f
7706	PROJECT	Project	Fort Walton Beach Electric Company	247182	2022-01-21 10:37:07.582623+00	2022-01-21 10:37:07.582653+00	8	\N	\N	f	f
7707	PROJECT	Project	Fossil Watch Limited	247183	2022-01-21 10:37:07.582713+00	2022-01-21 10:37:07.582743+00	8	\N	\N	f	f
7708	PROJECT	Project	Foulds Plumbing -	247184	2022-01-21 10:37:07.582804+00	2022-01-21 10:37:07.582834+00	8	\N	\N	f	f
7709	PROJECT	Project	Foxe Windows Management	247185	2022-01-21 10:37:07.582894+00	2022-01-21 10:37:07.582924+00	8	\N	\N	f	f
7710	PROJECT	Project	Foxmoor Formula	247186	2022-01-21 10:37:07.582985+00	2022-01-21 10:37:07.583014+00	8	\N	\N	f	f
7711	PROJECT	Project	Frank Edwards	247187	2022-01-21 10:37:07.583074+00	2022-01-21 10:37:07.583104+00	8	\N	\N	f	f
7712	PROJECT	Project	Frankland Attorneys Sales	247188	2022-01-21 10:37:07.583165+00	2022-01-21 10:37:07.583194+00	8	\N	\N	f	f
7713	PROJECT	Project	Franklin Photography	247189	2022-01-21 10:37:07.583255+00	2022-01-21 10:37:07.583285+00	8	\N	\N	f	f
7714	PROJECT	Project	Franklin Windows Inc.	247190	2022-01-21 10:37:07.583346+00	2022-01-21 10:37:07.583375+00	8	\N	\N	f	f
7715	PROJECT	Project	Fredericksburg Liquors Dynamics	247191	2022-01-21 10:37:07.583436+00	2022-01-21 10:37:07.583465+00	8	\N	\N	f	f
7716	PROJECT	Project	Freeman Sporting Goods	246796	2022-01-21 10:37:07.583526+00	2022-01-21 10:37:07.583556+00	8	\N	\N	f	f
7717	PROJECT	Project	Freeman Sporting Goods:0969 Ocean View Road	246797	2022-01-21 10:37:07.583616+00	2022-01-21 10:37:07.583645+00	8	\N	\N	f	f
7718	PROJECT	Project	Freeman Sporting Goods:55 Twin Lane	246798	2022-01-21 10:37:07.583706+00	2022-01-21 10:37:07.583735+00	8	\N	\N	f	f
7719	PROJECT	Project	Freier Markets Incorporated	247192	2022-01-21 10:37:07.583795+00	2022-01-21 10:37:07.583825+00	8	\N	\N	f	f
7720	PROJECT	Project	Freshour Apartments Agency	247193	2022-01-21 10:37:07.583885+00	2022-01-21 10:37:07.583914+00	8	\N	\N	f	f
7721	PROJECT	Project	Froilan Rosqueta	278541	2022-01-21 10:37:07.583976+00	2022-01-21 10:37:07.584005+00	8	\N	\N	f	f
7722	PROJECT	Project	FSI Industries (EUR)	247159	2022-01-21 10:37:07.584066+00	2022-01-21 10:37:07.584096+00	8	\N	\N	f	f
7723	PROJECT	Project	Fuhrmann Lumber Manufacturing	247195	2022-01-21 10:37:07.584156+00	2022-01-21 10:37:07.584186+00	8	\N	\N	f	f
7724	PROJECT	Project	Fujimura Catering Corporation	247196	2022-01-21 10:37:07.584247+00	2022-01-21 10:37:07.584276+00	8	\N	\N	f	f
7725	PROJECT	Project	Fullerton Software Inc.	247197	2022-01-21 10:37:07.584337+00	2022-01-21 10:37:07.584366+00	8	\N	\N	f	f
7726	PROJECT	Project	Furay and Bielawski Liquors Corporation	247198	2022-01-21 10:37:07.584427+00	2022-01-21 10:37:07.584456+00	8	\N	\N	f	f
7727	PROJECT	Project	Furniture Concepts	247199	2022-01-21 10:37:07.584517+00	2022-01-21 10:37:07.584546+00	8	\N	\N	f	f
7728	PROJECT	Project	Fuster Builders Co.	247200	2022-01-21 10:37:07.584607+00	2022-01-21 10:37:07.584636+00	8	\N	\N	f	f
7729	PROJECT	Project	FuTech	247194	2022-01-21 10:37:07.584697+00	2022-01-21 10:37:07.584727+00	8	\N	\N	f	f
7730	PROJECT	Project	Future Office Designs	247201	2022-01-21 10:37:07.584787+00	2022-01-21 10:37:07.584816+00	8	\N	\N	f	f
7731	PROJECT	Project	Fyle Engineering	243608	2022-01-21 10:37:07.584894+00	2022-01-21 10:37:07.584924+00	8	\N	\N	f	f
7732	PROJECT	Project	Fyle Integrations	274657	2022-01-21 10:37:07.584984+00	2022-01-21 10:37:07.585014+00	8	\N	\N	f	f
7733	PROJECT	Project	Fyle Main Project	243622	2022-01-21 10:37:07.585074+00	2022-01-21 10:37:07.585104+00	8	\N	\N	f	f
7734	PROJECT	Project	Fyle NetSuite Integration	284356	2022-01-21 10:37:07.585165+00	2022-01-21 10:37:07.585194+00	8	\N	\N	f	f
7735	PROJECT	Project	Fyle Nilesh	274658	2022-01-21 10:37:07.585255+00	2022-01-21 10:37:07.585285+00	8	\N	\N	f	f
7736	PROJECT	Project	Fyle Sage Intacct Integration	284357	2022-01-21 10:37:07.585345+00	2022-01-21 10:37:07.585374+00	8	\N	\N	f	f
7737	PROJECT	Project	Fyle Team Integrations	243607	2022-01-21 10:37:07.585435+00	2022-01-21 10:37:07.585465+00	8	\N	\N	f	f
7738	PROJECT	Project	Gacad Publishing Co.	247203	2022-01-21 10:37:07.585526+00	2022-01-21 10:37:07.585555+00	8	\N	\N	f	f
7739	PROJECT	Project	Gadison Electric Inc.	247204	2022-01-21 10:37:07.585615+00	2022-01-21 10:37:07.585645+00	8	\N	\N	f	f
7740	PROJECT	Project	Gainesville Plumbing Co.	247205	2022-01-21 10:37:07.585706+00	2022-01-21 10:37:07.585735+00	8	\N	\N	f	f
7741	PROJECT	Project	Galagher Plumbing Sales	247206	2022-01-21 10:37:07.585796+00	2022-01-21 10:37:07.585825+00	8	\N	\N	f	f
7742	PROJECT	Project	Galas Electric Rentals	247207	2022-01-21 10:37:07.585885+00	2022-01-21 10:37:07.585915+00	8	\N	\N	f	f
7743	PROJECT	Project	Gale Custom Sailboat	247208	2022-01-21 10:37:07.585975+00	2022-01-21 10:37:07.586005+00	8	\N	\N	f	f
7744	PROJECT	Project	Gallaugher Title Dynamics	247209	2022-01-21 10:37:07.586065+00	2022-01-21 10:37:07.586095+00	8	\N	\N	f	f
7745	PROJECT	Project	Galvan Attorneys Systems	247210	2022-01-21 10:37:07.586155+00	2022-01-21 10:37:07.586184+00	8	\N	\N	f	f
7746	PROJECT	Project	Garden Automotive Systems	247211	2022-01-21 10:37:07.586245+00	2022-01-21 10:37:07.586274+00	8	\N	\N	f	f
7747	PROJECT	Project	Gardnerville Automotive Sales	247212	2022-01-21 10:37:07.586335+00	2022-01-21 10:37:07.586389+00	8	\N	\N	f	f
7748	PROJECT	Project	Garitty Metal Fabricators Rentals	247213	2022-01-21 10:37:07.604975+00	2022-01-21 10:37:07.605021+00	8	\N	\N	f	f
7749	PROJECT	Project	Garret Leasing Rentals	247214	2022-01-21 10:37:07.605091+00	2022-01-21 10:37:07.605121+00	8	\N	\N	f	f
7750	PROJECT	Project	Gary Underwood	247215	2022-01-21 10:37:07.605182+00	2022-01-21 10:37:07.605211+00	8	\N	\N	f	f
7751	PROJECT	Project	Gauch Metal Fabricators Sales	247216	2022-01-21 10:37:07.605271+00	2022-01-21 10:37:07.605301+00	8	\N	\N	f	f
7752	PROJECT	Project	Gearan Title Networking	247217	2022-01-21 10:37:07.605378+00	2022-01-21 10:37:07.605546+00	8	\N	\N	f	f
7753	PROJECT	Project	Geeta Kalapatapu	246799	2022-01-21 10:37:07.605623+00	2022-01-21 10:37:07.607202+00	8	\N	\N	f	f
7754	PROJECT	Project	General Overhead	284358	2022-01-21 10:37:07.607317+00	2022-01-21 10:37:07.607351+00	8	\N	\N	f	f
7755	PROJECT	Project	General Overhead-Current	284359	2022-01-21 10:37:07.607422+00	2022-01-21 10:37:07.607454+00	8	\N	\N	f	f
7756	PROJECT	Project	Genis Builders Holding Corp.	247218	2022-01-21 10:37:07.607519+00	2022-01-21 10:37:07.60755+00	8	\N	\N	f	f
7757	PROJECT	Project	Gerba Construction Corporation	247219	2022-01-21 10:37:07.607832+00	2022-01-21 10:37:07.607869+00	8	\N	\N	f	f
7758	PROJECT	Project	Gerney Antiques Management	247220	2022-01-21 10:37:07.607932+00	2022-01-21 10:37:07.60796+00	8	\N	\N	f	f
7759	PROJECT	Project	Gesamondo Construction Leasing	247221	2022-01-21 10:37:07.608032+00	2022-01-21 10:37:07.608255+00	8	\N	\N	f	f
7760	PROJECT	Project	Gettenberg Title Manufacturing	247222	2022-01-21 10:37:07.608341+00	2022-01-21 10:37:07.608371+00	8	\N	\N	f	f
7761	PROJECT	Project	Gevelber Photography	246800	2022-01-21 10:37:07.60843+00	2022-01-21 10:37:07.608457+00	8	\N	\N	f	f
7762	PROJECT	Project	Gibsons Corporation	247223	2022-01-21 10:37:07.608526+00	2022-01-21 10:37:07.608565+00	8	\N	\N	f	f
7763	PROJECT	Project	Gilcrease Telecom Systems	247224	2022-01-21 10:37:07.608664+00	2022-01-21 10:37:07.608928+00	8	\N	\N	f	f
7764	PROJECT	Project	Gilroy Electric Services	247225	2022-01-21 10:37:07.609068+00	2022-01-21 10:37:07.609121+00	8	\N	\N	f	f
7765	PROJECT	Project	Gionest Metal Fabricators Co.	247226	2022-01-21 10:37:07.609239+00	2022-01-21 10:37:07.609286+00	8	\N	\N	f	f
7766	PROJECT	Project	GlassHouse Systems	247227	2022-01-21 10:37:07.609407+00	2022-01-21 10:37:07.609455+00	8	\N	\N	f	f
7767	PROJECT	Project	Glish Hospital Incorporated	247228	2022-01-21 10:37:07.612568+00	2022-01-21 10:37:07.613327+00	8	\N	\N	f	f
7768	PROJECT	Project	Global Supplies Inc.	247229	2022-01-21 10:37:07.613465+00	2022-01-21 10:37:07.613499+00	8	\N	\N	f	f
7769	PROJECT	Project	Glore Apartments Distributors	247230	2022-01-21 10:37:07.613675+00	2022-01-21 10:37:07.613708+00	8	\N	\N	f	f
7770	PROJECT	Project	Goepel Windows Management	247231	2022-01-21 10:37:07.613771+00	2022-01-21 10:37:07.613802+00	8	\N	\N	f	f
7771	PROJECT	Project	Gorman Ho	278542	2022-01-21 10:37:07.613867+00	2022-01-21 10:37:07.613967+00	8	\N	\N	f	f
7772	PROJECT	Project	GProxy Online	247202	2022-01-21 10:37:07.61405+00	2022-01-21 10:37:07.614082+00	8	\N	\N	f	f
7773	PROJECT	Project	Graber & Assoc	247232	2022-01-21 10:37:07.614156+00	2022-01-21 10:37:07.61421+00	8	\N	\N	f	f
7774	PROJECT	Project	Grana Automotive and Associates	247233	2022-01-21 10:37:07.614711+00	2022-01-21 10:37:07.614742+00	8	\N	\N	f	f
7775	PROJECT	Project	Grangeville Apartments Dynamics	247234	2022-01-21 10:37:07.614804+00	2022-01-21 10:37:07.614832+00	8	\N	\N	f	f
7776	PROJECT	Project	Grant Electronics	247235	2022-01-21 10:37:07.614933+00	2022-01-21 10:37:07.61568+00	8	\N	\N	f	f
7777	PROJECT	Project	Graphics R Us	247236	2022-01-21 10:37:07.616056+00	2022-01-21 10:37:07.616137+00	8	\N	\N	f	f
7778	PROJECT	Project	Grave Apartments Sales	247237	2022-01-21 10:37:07.616281+00	2022-01-21 10:37:07.616332+00	8	\N	\N	f	f
7779	PROJECT	Project	Graydon	247238	2022-01-21 10:37:07.61647+00	2022-01-21 10:37:07.616521+00	8	\N	\N	f	f
7780	PROJECT	Project	Green Grocery	247239	2022-01-21 10:37:07.616638+00	2022-01-21 10:37:07.616686+00	8	\N	\N	f	f
7781	PROJECT	Project	Green Street Spirits	247240	2022-01-21 10:37:07.616984+00	2022-01-21 10:37:07.617105+00	8	\N	\N	f	f
7782	PROJECT	Project	Greg Muller	247241	2022-01-21 10:37:07.617204+00	2022-01-21 10:37:07.617236+00	8	\N	\N	f	f
7783	PROJECT	Project	Gregory Daniels	247243	2022-01-21 10:37:07.6173+00	2022-01-21 10:37:07.617341+00	8	\N	\N	f	f
7784	PROJECT	Project	Greg Yamashige	247242	2022-01-21 10:37:07.617594+00	2022-01-21 10:37:07.617626+00	8	\N	\N	f	f
7785	PROJECT	Project	Gresham	247244	2022-01-21 10:37:07.617687+00	2022-01-21 10:37:07.617716+00	8	\N	\N	f	f
7786	PROJECT	Project	Grines Apartments Co.	247245	2022-01-21 10:37:07.617767+00	2022-01-21 10:37:07.617789+00	8	\N	\N	f	f
7787	PROJECT	Project	Guidaboni Publishing Leasing	247246	2022-01-21 10:37:07.617848+00	2022-01-21 10:37:07.617869+00	8	\N	\N	f	f
7788	PROJECT	Project	Gus Lee	247247	2022-01-21 10:37:07.618791+00	2022-01-21 10:37:07.618837+00	8	\N	\N	f	f
7789	PROJECT	Project	Gus Li	247248	2022-01-21 10:37:07.618905+00	2022-01-21 10:37:07.619042+00	8	\N	\N	f	f
7790	PROJECT	Project	Gus Photography	247249	2022-01-21 10:37:07.619169+00	2022-01-21 10:37:07.619335+00	8	\N	\N	f	f
7791	PROJECT	Project	Guzalak Leasing Leasing	247250	2022-01-21 10:37:07.619426+00	2022-01-21 10:37:07.619457+00	8	\N	\N	f	f
7792	PROJECT	Project	Hahn & Associates	247252	2022-01-21 10:37:07.619519+00	2022-01-21 10:37:07.619548+00	8	\N	\N	f	f
7793	PROJECT	Project	Haleiwa Windows Leasing	247253	2022-01-21 10:37:07.619675+00	2022-01-21 10:37:07.620153+00	8	\N	\N	f	f
7794	PROJECT	Project	Halick Title and Associates	247254	2022-01-21 10:37:07.620286+00	2022-01-21 10:37:07.620315+00	8	\N	\N	f	f
7795	PROJECT	Project	Hambly Spirits	247255	2022-01-21 10:37:07.620374+00	2022-01-21 10:37:07.620401+00	8	\N	\N	f	f
7796	PROJECT	Project	Hanninen Painting Distributors	247256	2022-01-21 10:37:07.620458+00	2022-01-21 10:37:07.620485+00	8	\N	\N	f	f
7797	PROJECT	Project	Hansen Car Dealership	247257	2022-01-21 10:37:07.620678+00	2022-01-21 10:37:07.620707+00	8	\N	\N	f	f
7798	PROJECT	Project	Harriage Plumbing Dynamics	247258	2022-01-21 10:37:07.636134+00	2022-01-21 10:37:07.636178+00	8	\N	\N	f	f
7799	PROJECT	Project	Harriott Construction Services	247259	2022-01-21 10:37:07.636351+00	2022-01-21 10:37:07.636385+00	8	\N	\N	f	f
7800	PROJECT	Project	Harrop Attorneys Inc.	247260	2022-01-21 10:37:07.636487+00	2022-01-21 10:37:07.636546+00	8	\N	\N	f	f
7801	PROJECT	Project	Harting Electric Fabricators	247261	2022-01-21 10:37:07.636997+00	2022-01-21 10:37:07.637052+00	8	\N	\N	f	f
7802	PROJECT	Project	Hawk Liquors Agency	247262	2022-01-21 10:37:07.637183+00	2022-01-21 10:37:07.637215+00	8	\N	\N	f	f
7803	PROJECT	Project	Hazel Robinson	278543	2022-01-21 10:37:07.637278+00	2022-01-21 10:37:07.637308+00	8	\N	\N	f	f
7804	PROJECT	Project	Healy Lumber -	247263	2022-01-21 10:37:07.637368+00	2022-01-21 10:37:07.637397+00	8	\N	\N	f	f
7805	PROJECT	Project	Hebden Automotive Dynamics	247264	2022-01-21 10:37:07.637824+00	2022-01-21 10:37:07.637952+00	8	\N	\N	f	f
7806	PROJECT	Project	Heeralall Metal Fabricators Incorporated	247265	2022-01-21 10:37:07.638026+00	2022-01-21 10:37:07.638056+00	8	\N	\N	f	f
7807	PROJECT	Project	Helfenbein Apartments Co.	247266	2022-01-21 10:37:07.638118+00	2022-01-21 10:37:07.638147+00	8	\N	\N	f	f
7808	PROJECT	Project	Helferty _ Services	247267	2022-01-21 10:37:07.638208+00	2022-01-21 10:37:07.638237+00	8	\N	\N	f	f
7809	PROJECT	Project	Helker and Heidkamp Software Systems	247268	2022-01-21 10:37:07.638387+00	2022-01-21 10:37:07.638421+00	8	\N	\N	f	f
7810	PROJECT	Project	Helping Hands Medical Supply	247269	2022-01-21 10:37:07.638485+00	2022-01-21 10:37:07.638515+00	8	\N	\N	f	f
7811	PROJECT	Project	Helvey Catering Distributors	247270	2022-01-21 10:37:07.638576+00	2022-01-21 10:37:07.638621+00	8	\N	\N	f	f
7812	PROJECT	Project	Hemauer Builders Inc.	247271	2022-01-21 10:37:07.638804+00	2022-01-21 10:37:07.638835+00	8	\N	\N	f	f
7813	PROJECT	Project	Hemet Builders Sales	247272	2022-01-21 10:37:07.638897+00	2022-01-21 10:37:07.638927+00	8	\N	\N	f	f
7814	PROJECT	Project	Henderson Cooper	247273	2022-01-21 10:37:07.638997+00	2022-01-21 10:37:07.639031+00	8	\N	\N	f	f
7815	PROJECT	Project	Henderson Liquors Manufacturing	247274	2022-01-21 10:37:07.639095+00	2022-01-21 10:37:07.639124+00	8	\N	\N	f	f
7816	PROJECT	Project	Hendrikson Builders Corporation	247275	2022-01-21 10:37:07.639185+00	2022-01-21 10:37:07.639215+00	8	\N	\N	f	f
7817	PROJECT	Project	Henneman Hardware	247276	2022-01-21 10:37:07.639275+00	2022-01-21 10:37:07.639307+00	8	\N	\N	f	f
7818	PROJECT	Project	Herline Hospital Holding Corp.	247277	2022-01-21 10:37:07.639394+00	2022-01-21 10:37:07.639423+00	8	\N	\N	f	f
7819	PROJECT	Project	Hershey's Canada	247278	2022-01-21 10:37:07.639484+00	2022-01-21 10:37:07.639513+00	8	\N	\N	f	f
7820	PROJECT	Project	Hess Sundries	247279	2022-01-21 10:37:07.639577+00	2022-01-21 10:37:07.639721+00	8	\N	\N	f	f
7821	PROJECT	Project	Hextall Consulting	247280	2022-01-21 10:37:07.639786+00	2022-01-21 10:37:07.639815+00	8	\N	\N	f	f
7822	PROJECT	Project	HGH Vision	247251	2022-01-21 10:37:07.639876+00	2022-01-21 10:37:07.639905+00	8	\N	\N	f	f
7823	PROJECT	Project	Hillian Construction Fabricators	247281	2022-01-21 10:37:07.639965+00	2022-01-21 10:37:07.639994+00	8	\N	\N	f	f
7824	PROJECT	Project	Hilltop Info Inc	247282	2022-01-21 10:37:07.640055+00	2022-01-21 10:37:07.640084+00	8	\N	\N	f	f
7825	PROJECT	Project	Himateja Madala	278544	2022-01-21 10:37:07.640144+00	2022-01-21 10:37:07.640173+00	8	\N	\N	f	f
7826	PROJECT	Project	Hirschy and Fahrenwald Liquors Incorporated	247283	2022-01-21 10:37:07.640234+00	2022-01-21 10:37:07.640272+00	8	\N	\N	f	f
7827	PROJECT	Project	Hixson Construction Agency	247284	2022-01-21 10:37:07.640337+00	2022-01-21 10:37:07.640366+00	8	\N	\N	f	f
7828	PROJECT	Project	Holgerson Automotive Services	247285	2022-01-21 10:37:07.640427+00	2022-01-21 10:37:07.640456+00	8	\N	\N	f	f
7829	PROJECT	Project	Hollyday Construction Networking	247287	2022-01-21 10:37:07.64052+00	2022-01-21 10:37:07.640549+00	8	\N	\N	f	f
7830	PROJECT	Project	Holly Romine	247286	2022-01-21 10:37:07.640609+00	2022-01-21 10:37:07.640638+00	8	\N	\N	f	f
7831	PROJECT	Project	Holtmeier Leasing -	247288	2022-01-21 10:37:07.640698+00	2022-01-21 10:37:07.640727+00	8	\N	\N	f	f
7832	PROJECT	Project	Honie Hospital Systems	247289	2022-01-21 10:37:07.640787+00	2022-01-21 10:37:07.640816+00	8	\N	\N	f	f
7833	PROJECT	Project	Honolulu Attorneys Sales	247290	2022-01-21 10:37:07.640876+00	2022-01-21 10:37:07.640904+00	8	\N	\N	f	f
7834	PROJECT	Project	Honolulu Markets Group	247291	2022-01-21 10:37:07.640965+00	2022-01-21 10:37:07.640994+00	8	\N	\N	f	f
7835	PROJECT	Project	Hood River Telecom	247292	2022-01-21 10:37:07.641054+00	2022-01-21 10:37:07.641083+00	8	\N	\N	f	f
7836	PROJECT	Project	Huck Apartments Inc.	247293	2022-01-21 10:37:07.641143+00	2022-01-21 10:37:07.641279+00	8	\N	\N	f	f
7837	PROJECT	Project	Hughson Runners	247294	2022-01-21 10:37:07.641341+00	2022-01-21 10:37:07.644954+00	8	\N	\N	f	f
7838	PROJECT	Project	Huit and Duer Publishing Dynamics	247295	2022-01-21 10:37:07.645059+00	2022-01-21 10:37:07.645091+00	8	\N	\N	f	f
7839	PROJECT	Project	Humphrey Yogurt	247296	2022-01-21 10:37:07.645167+00	2022-01-21 10:37:07.645197+00	8	\N	\N	f	f
7840	PROJECT	Project	Huntsville Apartments and Associates	247297	2022-01-21 10:37:07.64527+00	2022-01-21 10:37:07.645311+00	8	\N	\N	f	f
7841	PROJECT	Project	Hurlbutt Markets -	247298	2022-01-21 10:37:07.645423+00	2022-01-21 10:37:07.645852+00	8	\N	\N	f	f
7842	PROJECT	Project	Hurtgen Hospital Manufacturing	247299	2022-01-21 10:37:07.646331+00	2022-01-21 10:37:07.646442+00	8	\N	\N	f	f
7843	PROJECT	Project	Iain Bennett	247302	2022-01-21 10:37:07.64711+00	2022-01-21 10:37:07.647149+00	8	\N	\N	f	f
7844	PROJECT	Project	IBA Enterprises Inc	247300	2022-01-21 10:37:07.647215+00	2022-01-21 10:37:07.647246+00	8	\N	\N	f	f
7845	PROJECT	Project	ICC Inc	247301	2022-01-21 10:37:07.647336+00	2022-01-21 10:37:07.647371+00	8	\N	\N	f	f
7846	PROJECT	Project	Imperial Liquors Distributors	247303	2022-01-21 10:37:07.647434+00	2022-01-21 10:37:07.647463+00	8	\N	\N	f	f
7848	PROJECT	Project	Indianapolis Liquors Rentals	247305	2022-01-21 10:37:07.681517+00	2022-01-21 10:37:07.682039+00	8	\N	\N	f	f
7849	PROJECT	Project	Installation 2	247306	2022-01-21 10:37:07.682941+00	2022-01-21 10:37:07.683027+00	8	\N	\N	f	f
7850	PROJECT	Project	Installation FP	247307	2022-01-21 10:37:07.683284+00	2022-01-21 10:37:07.683337+00	8	\N	\N	f	f
7851	PROJECT	Project	Integrations	284360	2022-01-21 10:37:07.683452+00	2022-01-21 10:37:07.684061+00	8	\N	\N	f	f
7852	PROJECT	Project	Integrys Ltd	247308	2022-01-21 10:37:07.684998+00	2022-01-21 10:37:07.685078+00	8	\N	\N	f	f
7853	PROJECT	Project	Interior Solutions	247310	2022-01-21 10:37:07.685229+00	2022-01-21 10:37:07.685283+00	8	\N	\N	f	f
7854	PROJECT	Project	InterWorks Ltd	247309	2022-01-21 10:37:07.685392+00	2022-01-21 10:37:07.685439+00	8	\N	\N	f	f
7855	PROJECT	Project	Iorio Lumber Incorporated	247311	2022-01-21 10:37:07.686215+00	2022-01-21 10:37:07.686287+00	8	\N	\N	f	f
7856	PROJECT	Project	Jacint Tumacder	278545	2022-01-21 10:37:07.686483+00	2022-01-21 10:37:07.686779+00	8	\N	\N	f	f
7857	PROJECT	Project	Jackie Kugan	247313	2022-01-21 10:37:07.686963+00	2022-01-21 10:37:07.687019+00	8	\N	\N	f	f
7858	PROJECT	Project	Jackson Alexander	247314	2022-01-21 10:37:07.687219+00	2022-01-21 10:37:07.687284+00	8	\N	\N	f	f
7859	PROJECT	Project	Jaenicke Builders Management	247315	2022-01-21 10:37:07.687394+00	2022-01-21 10:37:07.68749+00	8	\N	\N	f	f
7860	PROJECT	Project	Jake Hamilton	247316	2022-01-21 10:37:07.687997+00	2022-01-21 10:37:07.688193+00	8	\N	\N	f	f
7861	PROJECT	Project	James McClure	247317	2022-01-21 10:37:07.688387+00	2022-01-21 10:37:07.688449+00	8	\N	\N	f	f
7862	PROJECT	Project	Jamie Taylor	247318	2022-01-21 10:37:07.688586+00	2022-01-21 10:37:07.688641+00	8	\N	\N	f	f
7863	PROJECT	Project	Janiak Attorneys Inc.	247319	2022-01-21 10:37:07.689168+00	2022-01-21 10:37:07.689221+00	8	\N	\N	f	f
7864	PROJECT	Project	Jasmer Antiques Management	247320	2022-01-21 10:37:07.689331+00	2022-01-21 10:37:07.689378+00	8	\N	\N	f	f
7865	PROJECT	Project	Jason Jacob	247321	2022-01-21 10:37:07.689797+00	2022-01-21 10:37:07.689857+00	8	\N	\N	f	f
7866	PROJECT	Project	Jason Paul Distribution	247322	2022-01-21 10:37:07.689989+00	2022-01-21 10:37:07.690111+00	8	\N	\N	f	f
7867	PROJECT	Project	Jeff Campbell	247323	2022-01-21 10:37:07.69024+00	2022-01-21 10:37:07.690286+00	8	\N	\N	f	f
7868	PROJECT	Project	Jeff's Jalopies	246801	2022-01-21 10:37:07.690411+00	2022-01-21 10:37:07.690455+00	8	\N	\N	f	f
7869	PROJECT	Project	Jelle Catering Group	247324	2022-01-21 10:37:07.690559+00	2022-01-21 10:37:07.690602+00	8	\N	\N	f	f
7870	PROJECT	Project	Jennings Financial	247325	2022-01-21 10:37:07.690998+00	2022-01-21 10:37:07.691049+00	8	\N	\N	f	f
7871	PROJECT	Project	Jennings Financial Inc.	247326	2022-01-21 10:37:07.691156+00	2022-01-21 10:37:07.691359+00	8	\N	\N	f	f
7872	PROJECT	Project	Jen Zaccarella	278546	2022-01-21 10:37:07.693629+00	2022-01-21 10:37:07.693684+00	8	\N	\N	f	f
7873	PROJECT	Project	Jeune Antiques Group	247327	2022-01-21 10:37:07.693793+00	2022-01-21 10:37:07.693824+00	8	\N	\N	f	f
7874	PROJECT	Project	Jeziorski _ Dynamics	247328	2022-01-21 10:37:07.693886+00	2022-01-21 10:37:07.693916+00	8	\N	\N	f	f
7875	PROJECT	Project	Jim's Custom Frames	247330	2022-01-21 10:37:07.694+00	2022-01-21 10:37:07.69403+00	8	\N	\N	f	f
7876	PROJECT	Project	Jim Strong	247329	2022-01-21 10:37:07.694159+00	2022-01-21 10:37:07.694193+00	8	\N	\N	f	f
7877	PROJECT	Project	JKL Co.	247312	2022-01-21 10:37:07.694259+00	2022-01-21 10:37:07.694288+00	8	\N	\N	f	f
7878	PROJECT	Project	Joanne Miller	247331	2022-01-21 10:37:07.694374+00	2022-01-21 10:37:07.694403+00	8	\N	\N	f	f
7879	PROJECT	Project	Joe Smith	247332	2022-01-21 10:37:07.694464+00	2022-01-21 10:37:07.694493+00	8	\N	\N	f	f
7880	PROJECT	Project	Johar Software Corporation	247333	2022-01-21 10:37:07.694808+00	2022-01-21 10:37:07.694867+00	8	\N	\N	f	f
7881	PROJECT	Project	John Boba	247334	2022-01-21 10:37:07.694971+00	2022-01-21 10:37:07.695015+00	8	\N	\N	f	f
7882	PROJECT	Project	John G. Roche Opticians	247335	2022-01-21 10:37:07.695291+00	2022-01-21 10:37:07.695371+00	8	\N	\N	f	f
7883	PROJECT	Project	John Melton	246802	2022-01-21 10:37:07.695511+00	2022-01-21 10:37:07.695557+00	8	\N	\N	f	f
7884	PROJECT	Project	John Nguyen	247336	2022-01-21 10:37:07.696025+00	2022-01-21 10:37:07.696093+00	8	\N	\N	f	f
7885	PROJECT	Project	John Paulsen	247337	2022-01-21 10:37:07.696226+00	2022-01-21 10:37:07.696274+00	8	\N	\N	f	f
7886	PROJECT	Project	John Smith Home Design	247338	2022-01-21 10:37:07.696387+00	2022-01-21 10:37:07.696431+00	8	\N	\N	f	f
7887	PROJECT	Project	Johnson & Johnson	247339	2022-01-21 10:37:07.696532+00	2022-01-21 10:37:07.69676+00	8	\N	\N	f	f
7888	PROJECT	Project	Jonas Island Applied Radiation	247340	2022-01-21 10:37:07.696913+00	2022-01-21 10:37:07.696954+00	8	\N	\N	f	f
7889	PROJECT	Project	Jonathan Ketner	247341	2022-01-21 10:37:07.697047+00	2022-01-21 10:37:07.697087+00	8	\N	\N	f	f
7890	PROJECT	Project	Jones & Bernstein Law Firm	247342	2022-01-21 10:37:07.697179+00	2022-01-21 10:37:07.697218+00	8	\N	\N	f	f
7891	PROJECT	Project	Jordan Burgess	278547	2022-01-21 10:37:07.697452+00	2022-01-21 10:37:07.697501+00	8	\N	\N	f	f
7892	PROJECT	Project	Julia Daniels	247343	2022-01-21 10:37:07.697836+00	2022-01-21 10:37:07.697903+00	8	\N	\N	f	f
7893	PROJECT	Project	Julie Frankel	247344	2022-01-21 10:37:07.698014+00	2022-01-21 10:37:07.698056+00	8	\N	\N	f	f
7894	PROJECT	Project	Juno Gold Wines	247345	2022-01-21 10:37:07.698152+00	2022-01-21 10:37:07.698287+00	8	\N	\N	f	f
7895	PROJECT	Project	Justine Outland	278548	2022-01-21 10:37:07.698537+00	2022-01-21 10:37:07.698583+00	8	\N	\N	f	f
7896	PROJECT	Project	Justin Hartman	247346	2022-01-21 10:37:07.698656+00	2022-01-21 10:37:07.698686+00	8	\N	\N	f	f
7897	PROJECT	Project	Justin Ramos	247347	2022-01-21 10:37:07.698977+00	2022-01-21 10:37:07.700841+00	8	\N	\N	f	f
7898	PROJECT	Project	Kababik and Ramariz Liquors Corporation	247349	2022-01-21 10:37:07.718084+00	2022-01-21 10:37:07.718204+00	8	\N	\N	f	f
7899	PROJECT	Project	Kalfa Painting Holding Corp.	247350	2022-01-21 10:37:07.718296+00	2022-01-21 10:37:07.718355+00	8	\N	\N	f	f
7900	PROJECT	Project	Kalinsky Consulting Group	247351	2022-01-21 10:37:07.718446+00	2022-01-21 10:37:07.718477+00	8	\N	\N	f	f
7901	PROJECT	Project	Kalisch Lumber Group	247352	2022-01-21 10:37:07.718753+00	2022-01-21 10:37:07.718811+00	8	\N	\N	f	f
7902	PROJECT	Project	Kallmeyer Antiques Dynamics	247353	2022-01-21 10:37:07.71894+00	2022-01-21 10:37:07.718972+00	8	\N	\N	f	f
7903	PROJECT	Project	Kamps Electric Systems	247354	2022-01-21 10:37:07.719049+00	2022-01-21 10:37:07.71908+00	8	\N	\N	f	f
7904	PROJECT	Project	Kara's Cafe	247355	2022-01-21 10:37:07.71914+00	2022-01-21 10:37:07.719275+00	8	\N	\N	f	f
7905	PROJECT	Project	Kari Steblay	278549	2022-01-21 10:37:07.719354+00	2022-01-21 10:37:07.719384+00	8	\N	\N	f	f
7906	PROJECT	Project	Karna Nisewaner	278550	2022-01-21 10:37:07.719685+00	2022-01-21 10:37:07.719731+00	8	\N	\N	f	f
7907	PROJECT	Project	Kate Whelan	246803	2022-01-21 10:37:07.719868+00	2022-01-21 10:37:07.719938+00	8	\N	\N	f	f
7908	PROJECT	Project	Kate Winters	247356	2022-01-21 10:37:07.720041+00	2022-01-21 10:37:07.720071+00	8	\N	\N	f	f
7909	PROJECT	Project	Katie Fischer	247357	2022-01-21 10:37:07.720135+00	2022-01-21 10:37:07.720166+00	8	\N	\N	f	f
7910	PROJECT	Project	Kavadias Construction Sales	247358	2022-01-21 10:37:07.720371+00	2022-01-21 10:37:07.720402+00	8	\N	\N	f	f
7911	PROJECT	Project	Kavanagh Brothers	247359	2022-01-21 10:37:07.720626+00	2022-01-21 10:37:07.720657+00	8	\N	\N	f	f
7912	PROJECT	Project	Kavanaugh Real Estate	247360	2022-01-21 10:37:07.72072+00	2022-01-21 10:37:07.72075+00	8	\N	\N	f	f
7913	PROJECT	Project	Keblish Catering Distributors	247361	2022-01-21 10:37:07.720874+00	2022-01-21 10:37:07.72095+00	8	\N	\N	f	f
7914	PROJECT	Project	Kelleher Title Services	247362	2022-01-21 10:37:07.721022+00	2022-01-21 10:37:07.721053+00	8	\N	\N	f	f
7915	PROJECT	Project	KEM Corporation	247348	2022-01-21 10:37:07.721237+00	2022-01-21 10:37:07.721271+00	8	\N	\N	f	f
7916	PROJECT	Project	Kemme Builders Management	247363	2022-01-21 10:37:07.721335+00	2022-01-21 10:37:07.721416+00	8	\N	\N	f	f
7917	PROJECT	Project	Kempker Title Manufacturing	247364	2022-01-21 10:37:07.721754+00	2022-01-21 10:37:07.721794+00	8	\N	\N	f	f
7918	PROJECT	Project	Ken Chua	247365	2022-01-21 10:37:07.721869+00	2022-01-21 10:37:07.72327+00	8	\N	\N	f	f
7919	PROJECT	Project	Kenney Windows Dynamics	247366	2022-01-21 10:37:07.723647+00	2022-01-21 10:37:07.723702+00	8	\N	\N	f	f
7920	PROJECT	Project	Kerekes Lumber Networking	247367	2022-01-21 10:37:07.723785+00	2022-01-21 10:37:07.723883+00	8	\N	\N	f	f
7921	PROJECT	Project	Kerfien Title Company	247368	2022-01-21 10:37:07.723998+00	2022-01-21 10:37:07.724032+00	8	\N	\N	f	f
7922	PROJECT	Project	Kerry Furnishings & Design	247369	2022-01-21 10:37:07.724247+00	2022-01-21 10:37:07.724283+00	8	\N	\N	f	f
7923	PROJECT	Project	Kevin Smith	247370	2022-01-21 10:37:07.724431+00	2022-01-21 10:37:07.724465+00	8	\N	\N	f	f
7924	PROJECT	Project	Kiedrowski Telecom Services	247371	2022-01-21 10:37:07.724937+00	2022-01-21 10:37:07.725072+00	8	\N	\N	f	f
7925	PROJECT	Project	Kieff Software Fabricators	247372	2022-01-21 10:37:07.725252+00	2022-01-21 10:37:07.725293+00	8	\N	\N	f	f
7926	PROJECT	Project	Killian Construction Networking	247373	2022-01-21 10:37:07.72541+00	2022-01-21 10:37:07.725463+00	8	\N	\N	f	f
7927	PROJECT	Project	Kim Wilson	247374	2022-01-21 10:37:07.725578+00	2022-01-21 10:37:07.726228+00	8	\N	\N	f	f
7928	PROJECT	Project	Kingman Antiques Corporation	247375	2022-01-21 10:37:07.726478+00	2022-01-21 10:37:07.726527+00	8	\N	\N	f	f
7929	PROJECT	Project	Kino Inc	247376	2022-01-21 10:37:07.726796+00	2022-01-21 10:37:07.726833+00	8	\N	\N	f	f
7930	PROJECT	Project	Kirkville Builders -	247377	2022-01-21 10:37:07.726993+00	2022-01-21 10:37:07.727026+00	8	\N	\N	f	f
7931	PROJECT	Project	Kittel Hardware Dynamics	247378	2022-01-21 10:37:07.727095+00	2022-01-21 10:37:07.727199+00	8	\N	\N	f	f
7932	PROJECT	Project	Knoop Telecom Agency	247379	2022-01-21 10:37:07.727278+00	2022-01-21 10:37:07.727308+00	8	\N	\N	f	f
7933	PROJECT	Project	Knotek Hospital Company	247380	2022-01-21 10:37:07.727468+00	2022-01-21 10:37:07.7275+00	8	\N	\N	f	f
7934	PROJECT	Project	Konecny Markets Co.	247381	2022-01-21 10:37:07.72779+00	2022-01-21 10:37:07.727964+00	8	\N	\N	f	f
7935	PROJECT	Project	Kookies by Kathy	246804	2022-01-21 10:37:07.728048+00	2022-01-21 10:37:07.728081+00	8	\N	\N	f	f
7936	PROJECT	Project	Koshi Metal Fabricators Corporation	247382	2022-01-21 10:37:07.728196+00	2022-01-21 10:37:07.728228+00	8	\N	\N	f	f
7937	PROJECT	Project	Kovats Publishing	247383	2022-01-21 10:37:07.728309+00	2022-01-21 10:37:07.728352+00	8	\N	\N	f	f
7938	PROJECT	Project	Kramer Construction	247384	2022-01-21 10:37:07.729758+00	2022-01-21 10:37:07.729815+00	8	\N	\N	f	f
7939	PROJECT	Project	Krista Thomas Recruiting	247385	2022-01-21 10:37:07.729901+00	2022-01-21 10:37:07.729985+00	8	\N	\N	f	f
7940	PROJECT	Project	Kristen Welch	247386	2022-01-21 10:37:07.730348+00	2022-01-21 10:37:07.730379+00	8	\N	\N	f	f
7941	PROJECT	Project	Kristy Abercrombie	278551	2022-01-21 10:37:07.730442+00	2022-01-21 10:37:07.730636+00	8	\N	\N	f	f
7942	PROJECT	Project	Kroetz Electric Dynamics	247387	2022-01-21 10:37:07.73088+00	2022-01-21 10:37:07.730915+00	8	\N	\N	f	f
7943	PROJECT	Project	Kugan Autodesk Inc	247388	2022-01-21 10:37:07.730978+00	2022-01-21 10:37:07.731033+00	8	\N	\N	f	f
7944	PROJECT	Project	Kunstlinger Automotive Manufacturing	247389	2022-01-21 10:37:07.731177+00	2022-01-21 10:37:07.731213+00	8	\N	\N	f	f
7945	PROJECT	Project	Kyle Keosian	247390	2022-01-21 10:37:07.731446+00	2022-01-21 10:37:07.731485+00	8	\N	\N	f	f
7946	PROJECT	Project	Labarba Markets Corporation	247392	2022-01-21 10:37:07.731901+00	2022-01-21 10:37:07.731973+00	8	\N	\N	f	f
7947	PROJECT	Project	labhvam	290031	2022-01-21 10:37:07.732062+00	2022-01-21 10:37:07.732092+00	8	\N	\N	f	f
7948	PROJECT	Project	Laditka and Ceppetelli Publishing Holding Corp.	247393	2022-01-21 10:37:07.741447+00	2022-01-21 10:37:07.74166+00	8	\N	\N	f	f
7949	PROJECT	Project	Lafayette Hardware Services	247394	2022-01-21 10:37:07.741787+00	2022-01-21 10:37:07.74184+00	8	\N	\N	f	f
7950	PROJECT	Project	Lafayette Metal Fabricators Rentals	247395	2022-01-21 10:37:07.741956+00	2022-01-21 10:37:07.742001+00	8	\N	\N	f	f
7951	PROJECT	Project	La Grande Liquors Dynamics	247391	2022-01-21 10:37:07.742251+00	2022-01-21 10:37:07.742303+00	8	\N	\N	f	f
7952	PROJECT	Project	Lakeside Inc	247397	2022-01-21 10:37:07.74241+00	2022-01-21 10:37:07.74245+00	8	\N	\N	f	f
7953	PROJECT	Project	Lake Worth Markets Fabricators	247396	2022-01-21 10:37:07.742542+00	2022-01-21 10:37:07.742582+00	8	\N	\N	f	f
7954	PROJECT	Project	Lancaster Liquors Inc.	247398	2022-01-21 10:37:07.742671+00	2022-01-21 10:37:07.74271+00	8	\N	\N	f	f
7955	PROJECT	Project	Lanning and Urraca Construction Corporation	247399	2022-01-21 10:37:07.7428+00	2022-01-21 10:37:07.742839+00	8	\N	\N	f	f
7956	PROJECT	Project	Laramie Construction Co.	247400	2022-01-21 10:37:07.74293+00	2022-01-21 10:37:07.742969+00	8	\N	\N	f	f
7957	PROJECT	Project	Largo Lumber Co.	247401	2022-01-21 10:37:07.743316+00	2022-01-21 10:37:07.74338+00	8	\N	\N	f	f
7958	PROJECT	Project	Lariosa Lumber Corporation	247402	2022-01-21 10:37:07.743496+00	2022-01-21 10:37:07.743539+00	8	\N	\N	f	f
7959	PROJECT	Project	Laser Images Inc.	247404	2022-01-21 10:37:07.743635+00	2022-01-21 10:37:07.743676+00	8	\N	\N	f	f
7960	PROJECT	Project	Las Vegas Electric Manufacturing	247403	2022-01-21 10:37:07.743777+00	2022-01-21 10:37:07.74382+00	8	\N	\N	f	f
7961	PROJECT	Project	Lawley and Barends Painting Distributors	247405	2022-01-21 10:37:07.743919+00	2022-01-21 10:37:07.743962+00	8	\N	\N	f	f
7962	PROJECT	Project	Lead 154	247406	2022-01-21 10:37:07.744511+00	2022-01-21 10:37:07.744711+00	8	\N	\N	f	f
7963	PROJECT	Project	Lead 155	247407	2022-01-21 10:37:07.744839+00	2022-01-21 10:37:07.744886+00	8	\N	\N	f	f
7964	PROJECT	Project	Leemans Builders Agency	247408	2022-01-21 10:37:07.744988+00	2022-01-21 10:37:07.74503+00	8	\N	\N	f	f
7965	PROJECT	Project	Lenza and Lanzoni Plumbing Co.	247409	2022-01-21 10:37:07.745244+00	2022-01-21 10:37:07.745299+00	8	\N	\N	f	f
7966	PROJECT	Project	Levitan Plumbing Dynamics	247410	2022-01-21 10:37:07.74541+00	2022-01-21 10:37:07.745456+00	8	\N	\N	f	f
7967	PROJECT	Project	Lew Plumbing	278552	2022-01-21 10:37:07.745561+00	2022-01-21 10:37:07.745602+00	8	\N	\N	f	f
7968	PROJECT	Project	Lexington Hospital Sales	247411	2022-01-21 10:37:07.745694+00	2022-01-21 10:37:07.745733+00	8	\N	\N	f	f
7969	PROJECT	Project	Liechti Lumber Sales	247412	2022-01-21 10:37:07.745824+00	2022-01-21 10:37:07.745866+00	8	\N	\N	f	f
7970	PROJECT	Project	Lillian Thurham	247413	2022-01-21 10:37:07.745962+00	2022-01-21 10:37:07.746002+00	8	\N	\N	f	f
7971	PROJECT	Project	Limbo Leasing Leasing	247414	2022-01-21 10:37:07.746565+00	2022-01-21 10:37:07.751797+00	8	\N	\N	f	f
7972	PROJECT	Project	Lina's Dance Studio	247415	2022-01-21 10:37:07.752+00	2022-01-21 10:37:07.752056+00	8	\N	\N	f	f
7973	PROJECT	Project	Linberg Windows Agency	247416	2022-01-21 10:37:07.752913+00	2022-01-21 10:37:07.752952+00	8	\N	\N	f	f
7974	PROJECT	Project	Linderman Builders Agency	247418	2022-01-21 10:37:07.754705+00	2022-01-21 10:37:07.754758+00	8	\N	\N	f	f
7975	PROJECT	Project	Linder Windows Rentals	247417	2022-01-21 10:37:07.754843+00	2022-01-21 10:37:07.754873+00	8	\N	\N	f	f
7976	PROJECT	Project	Lindman and Kastens Antiques -	247419	2022-01-21 10:37:07.754935+00	2022-01-21 10:37:07.754964+00	8	\N	\N	f	f
7977	PROJECT	Project	Linear International Footwear	247420	2022-01-21 10:37:07.755025+00	2022-01-21 10:37:07.755055+00	8	\N	\N	f	f
7978	PROJECT	Project	Lintex Group	247421	2022-01-21 10:37:07.755242+00	2022-01-21 10:37:07.755272+00	8	\N	\N	f	f
7979	PROJECT	Project	Lisa Fiore	247422	2022-01-21 10:37:07.755332+00	2022-01-21 10:37:07.755362+00	8	\N	\N	f	f
7980	PROJECT	Project	Lisa Wilson	247423	2022-01-21 10:37:07.755661+00	2022-01-21 10:37:07.755717+00	8	\N	\N	f	f
7981	PROJECT	Project	Liverpool Hospital Leasing	247424	2022-01-21 10:37:07.75579+00	2022-01-21 10:37:07.755819+00	8	\N	\N	f	f
7982	PROJECT	Project	Lizarrago Markets Corporation	247425	2022-01-21 10:37:07.756011+00	2022-01-21 10:37:07.756042+00	8	\N	\N	f	f
7983	PROJECT	Project	Lobby Remodel	247426	2022-01-21 10:37:07.756102+00	2022-01-21 10:37:07.756131+00	8	\N	\N	f	f
7984	PROJECT	Project	Lodato Painting and Associates	247427	2022-01-21 10:37:07.756192+00	2022-01-21 10:37:07.756221+00	8	\N	\N	f	f
7985	PROJECT	Project	Loeza Catering Agency	247428	2022-01-21 10:37:07.756281+00	2022-01-21 10:37:07.75631+00	8	\N	\N	f	f
7986	PROJECT	Project	Lois Automotive Agency	247429	2022-01-21 10:37:07.75637+00	2022-01-21 10:37:07.756399+00	8	\N	\N	f	f
7987	PROJECT	Project	Lomax Transportation	247430	2022-01-21 10:37:07.756459+00	2022-01-21 10:37:07.756488+00	8	\N	\N	f	f
7988	PROJECT	Project	Lompoc _ Systems	247431	2022-01-21 10:37:07.756548+00	2022-01-21 10:37:07.756577+00	8	\N	\N	f	f
7989	PROJECT	Project	Lonabaugh Markets Distributors	247432	2022-01-21 10:37:07.756638+00	2022-01-21 10:37:07.756668+00	8	\N	\N	f	f
7990	PROJECT	Project	Lorandeau Builders Holding Corp.	247433	2022-01-21 10:37:07.756728+00	2022-01-21 10:37:07.756757+00	8	\N	\N	f	f
7991	PROJECT	Project	Lou Baus	247434	2022-01-21 10:37:07.757098+00	2022-01-21 10:37:07.757129+00	8	\N	\N	f	f
7992	PROJECT	Project	Louis Fabre	247435	2022-01-21 10:37:07.75719+00	2022-01-21 10:37:07.757219+00	8	\N	\N	f	f
7993	PROJECT	Project	Loven and Frothingham Hardware Distributors	247436	2022-01-21 10:37:07.757403+00	2022-01-21 10:37:07.757432+00	8	\N	\N	f	f
7994	PROJECT	Project	Lucic and Perfect Publishing Systems	247437	2022-01-21 10:37:07.757492+00	2022-01-21 10:37:07.757521+00	8	\N	\N	f	f
7995	PROJECT	Project	Lucie Hospital Group	247438	2022-01-21 10:37:07.757584+00	2022-01-21 10:37:07.757614+00	8	\N	\N	f	f
7996	PROJECT	Project	Luffy Apartments Company	247439	2022-01-21 10:37:07.757674+00	2022-01-21 10:37:07.757702+00	8	\N	\N	f	f
7997	PROJECT	Project	Luigi Imports	247440	2022-01-21 10:37:07.757763+00	2022-01-21 10:37:07.757792+00	8	\N	\N	f	f
7998	PROJECT	Project	Lummus Telecom Rentals	247441	2022-01-21 10:37:07.771201+00	2022-01-21 10:37:07.771357+00	8	\N	\N	f	f
7999	PROJECT	Project	Lurtz Painting Co.	247442	2022-01-21 10:37:07.77197+00	2022-01-21 10:37:07.772047+00	8	\N	\N	f	f
8000	PROJECT	Project	Lyas Builders Inc.	247443	2022-01-21 10:37:07.772348+00	2022-01-21 10:37:07.772466+00	8	\N	\N	f	f
8001	PROJECT	Project	MAC	247444	2022-01-21 10:37:07.772951+00	2022-01-21 10:37:07.77299+00	8	\N	\N	f	f
8002	PROJECT	Project	Mackenzie Corporation	247447	2022-01-21 10:37:07.773064+00	2022-01-21 10:37:07.773096+00	8	\N	\N	f	f
8003	PROJECT	Project	Mackie Painting Company	247448	2022-01-21 10:37:07.773163+00	2022-01-21 10:37:07.773195+00	8	\N	\N	f	f
8004	PROJECT	Project	Malena Construction Fabricators	247449	2022-01-21 10:37:07.773258+00	2022-01-21 10:37:07.773289+00	8	\N	\N	f	f
8005	PROJECT	Project	Maleonado Publishing Company	247450	2022-01-21 10:37:07.773364+00	2022-01-21 10:37:07.773395+00	8	\N	\N	f	f
8006	PROJECT	Project	Mandos	247451	2022-01-21 10:37:07.773457+00	2022-01-21 10:37:07.773487+00	8	\N	\N	f	f
8007	PROJECT	Project	Manivong Apartments Incorporated	247452	2022-01-21 10:37:07.773548+00	2022-01-21 10:37:07.773578+00	8	\N	\N	f	f
8008	PROJECT	Project	Manwarren Markets Holding Corp.	247453	2022-01-21 10:37:07.773639+00	2022-01-21 10:37:07.773669+00	8	\N	\N	f	f
8009	PROJECT	Project	Maple Leaf Foods	247454	2022-01-21 10:37:07.77373+00	2022-01-21 10:37:07.77376+00	8	\N	\N	f	f
8010	PROJECT	Project	Marabella Title Agency	247455	2022-01-21 10:37:07.773821+00	2022-01-21 10:37:07.773851+00	8	\N	\N	f	f
8011	PROJECT	Project	Marietta Title Co.	247456	2022-01-21 10:37:07.773912+00	2022-01-21 10:37:07.773941+00	8	\N	\N	f	f
8012	PROJECT	Project	Marionneaux Catering Incorporated	247457	2022-01-21 10:37:07.774003+00	2022-01-21 10:37:07.774033+00	8	\N	\N	f	f
8013	PROJECT	Project	Mark Cho	246805	2022-01-21 10:37:07.774094+00	2022-01-21 10:37:07.774124+00	8	\N	\N	f	f
8014	PROJECT	Project	Markewich Builders Rentals	247459	2022-01-21 10:37:07.774292+00	2022-01-21 10:37:07.774323+00	8	\N	\N	f	f
8015	PROJECT	Project	Mark's Sporting Goods	247458	2022-01-21 10:37:07.774946+00	2022-01-21 10:37:07.775008+00	8	\N	\N	f	f
8016	PROJECT	Project	Marrello Software Services	247460	2022-01-21 10:37:07.775195+00	2022-01-21 10:37:07.775286+00	8	\N	\N	f	f
8017	PROJECT	Project	Marston Hardware -	247461	2022-01-21 10:37:07.775382+00	2022-01-21 10:37:07.775467+00	8	\N	\N	f	f
8018	PROJECT	Project	Martin Gelina	247462	2022-01-21 10:37:07.77607+00	2022-01-21 10:37:07.77615+00	8	\N	\N	f	f
8019	PROJECT	Project	Mason's Travel Services	247463	2022-01-21 10:37:07.776326+00	2022-01-21 10:37:07.776368+00	8	\N	\N	f	f
8020	PROJECT	Project	Matsuzaki Builders Services	247464	2022-01-21 10:37:07.776445+00	2022-01-21 10:37:07.776477+00	8	\N	\N	f	f
8021	PROJECT	Project	Matthew Davison	247465	2022-01-21 10:37:07.776552+00	2022-01-21 10:37:07.776583+00	8	\N	\N	f	f
8022	PROJECT	Project	Matzke Title Co.	247466	2022-01-21 10:37:07.77665+00	2022-01-21 10:37:07.776679+00	8	\N	\N	f	f
8023	PROJECT	Project	Maxx Corner Market	247467	2022-01-21 10:37:07.776746+00	2022-01-21 10:37:07.776776+00	8	\N	\N	f	f
8024	PROJECT	Project	Mcburnie Hardware Dynamics	247470	2022-01-21 10:37:07.77684+00	2022-01-21 10:37:07.776869+00	8	\N	\N	f	f
8025	PROJECT	Project	Mcdorman Software Holding Corp.	247471	2022-01-21 10:37:07.776932+00	2022-01-21 10:37:07.776961+00	8	\N	\N	f	f
8026	PROJECT	Project	McEdwards & Whitwell	247468	2022-01-21 10:37:07.777023+00	2022-01-21 10:37:07.777052+00	8	\N	\N	f	f
8027	PROJECT	Project	Mcelderry Apartments Systems	247472	2022-01-21 10:37:07.777142+00	2022-01-21 10:37:07.777172+00	8	\N	\N	f	f
8028	PROJECT	Project	Mcguff and Spriggins Hospital Group	247473	2022-01-21 10:37:07.777234+00	2022-01-21 10:37:07.777263+00	8	\N	\N	f	f
8029	PROJECT	Project	McKay Financial	247469	2022-01-21 10:37:07.777347+00	2022-01-21 10:37:07.777377+00	8	\N	\N	f	f
8030	PROJECT	Project	Mcoy and Donlin Attorneys Sales	247474	2022-01-21 10:37:07.7779+00	2022-01-21 10:37:07.777982+00	8	\N	\N	f	f
8031	PROJECT	Project	Medcan Mgmt Inc	247475	2022-01-21 10:37:07.778132+00	2022-01-21 10:37:07.778281+00	8	\N	\N	f	f
8032	PROJECT	Project	Medved	247476	2022-01-21 10:37:07.778461+00	2022-01-21 10:37:07.778514+00	8	\N	\N	f	f
8033	PROJECT	Project	Megaloid labs	247477	2022-01-21 10:37:07.778924+00	2022-01-21 10:37:07.778974+00	8	\N	\N	f	f
8034	PROJECT	Project	Meisner Software Inc.	247478	2022-01-21 10:37:07.779055+00	2022-01-21 10:37:07.779092+00	8	\N	\N	f	f
8035	PROJECT	Project	Mele Plumbing Manufacturing	247479	2022-01-21 10:37:07.779154+00	2022-01-21 10:37:07.779183+00	8	\N	\N	f	f
8036	PROJECT	Project	Melissa Wine Shop	247480	2022-01-21 10:37:07.779244+00	2022-01-21 10:37:07.779273+00	8	\N	\N	f	f
8037	PROJECT	Project	Melville Painting Rentals	247481	2022-01-21 10:37:07.779333+00	2022-01-21 10:37:07.779363+00	8	\N	\N	f	f
8038	PROJECT	Project	Meneses Telecom Corporation	247482	2022-01-21 10:37:07.779427+00	2022-01-21 10:37:07.779456+00	8	\N	\N	f	f
8039	PROJECT	Project	Mentor Graphics	247483	2022-01-21 10:37:07.779516+00	2022-01-21 10:37:07.779545+00	8	\N	\N	f	f
8040	PROJECT	Project	Micehl Bertrand	247484	2022-01-21 10:37:07.779741+00	2022-01-21 10:37:07.779866+00	8	\N	\N	f	f
8041	PROJECT	Project	Michael Jannsen	247485	2022-01-21 10:37:07.779958+00	2022-01-21 10:37:07.780006+00	8	\N	\N	f	f
8042	PROJECT	Project	Michael Spencer	247486	2022-01-21 10:37:07.780124+00	2022-01-21 10:37:07.780361+00	8	\N	\N	f	f
8043	PROJECT	Project	Michael Wakefield	247487	2022-01-21 10:37:07.780596+00	2022-01-21 10:37:07.780639+00	8	\N	\N	f	f
8044	PROJECT	Project	Microskills	247488	2022-01-21 10:37:07.780724+00	2022-01-21 10:37:07.780763+00	8	\N	\N	f	f
8045	PROJECT	Project	Midgette Markets	247489	2022-01-21 10:37:07.780857+00	2022-01-21 10:37:07.780895+00	8	\N	\N	f	f
8046	PROJECT	Project	Mike Dee	247490	2022-01-21 10:37:07.780981+00	2022-01-21 10:37:07.781019+00	8	\N	\N	f	f
8047	PROJECT	Project	Mike Franko	247491	2022-01-21 10:37:07.781106+00	2022-01-21 10:37:07.781146+00	8	\N	\N	f	f
8048	PROJECT	Project	Mike Miller	247492	2022-01-21 10:37:07.788517+00	2022-01-21 10:37:07.788573+00	8	\N	\N	f	f
8049	PROJECT	Project	Millenium Engineering	247493	2022-01-21 10:37:07.7887+00	2022-01-21 10:37:07.788744+00	8	\N	\N	f	f
8050	PROJECT	Project	Miller's Dry Cleaning	247494	2022-01-21 10:37:07.788868+00	2022-01-21 10:37:07.788913+00	8	\N	\N	f	f
8051	PROJECT	Project	Mindy Peiris	247495	2022-01-21 10:37:07.789045+00	2022-01-21 10:37:07.789085+00	8	\N	\N	f	f
8052	PROJECT	Project	Mineral Painting Inc.	247496	2022-01-21 10:37:07.789187+00	2022-01-21 10:37:07.78929+00	8	\N	\N	f	f
8053	PROJECT	Project	Miquel Apartments Leasing	247497	2022-01-21 10:37:07.789404+00	2022-01-21 10:37:07.789448+00	8	\N	\N	f	f
8054	PROJECT	Project	Mission Liquors	247498	2022-01-21 10:37:07.789567+00	2022-01-21 10:37:07.789607+00	8	\N	\N	f	f
8055	PROJECT	Project	Mitani Hardware Company	247499	2022-01-21 10:37:07.789714+00	2022-01-21 10:37:07.789757+00	8	\N	\N	f	f
8056	PROJECT	Project	Mitchell & assoc	247500	2022-01-21 10:37:07.789855+00	2022-01-21 10:37:07.789897+00	8	\N	\N	f	f
8057	PROJECT	Project	Mitchelle Title -	247501	2022-01-21 10:37:07.789991+00	2022-01-21 10:37:07.790031+00	8	\N	\N	f	f
8058	PROJECT	Project	Mitra	247502	2022-01-21 10:37:07.790123+00	2022-01-21 10:37:07.790166+00	8	\N	\N	f	f
8059	PROJECT	Project	Mobile App Redesign	284361	2022-01-21 10:37:07.79026+00	2022-01-21 10:37:07.790303+00	8	\N	\N	f	f
8060	PROJECT	Project	Molesworth and Repress Liquors Leasing	247503	2022-01-21 10:37:07.790671+00	2022-01-21 10:37:07.790722+00	8	\N	\N	f	f
8061	PROJECT	Project	Momphard Painting Sales	247504	2022-01-21 10:37:07.790825+00	2022-01-21 10:37:07.790869+00	8	\N	\N	f	f
8062	PROJECT	Project	Monica Parker	247505	2022-01-21 10:37:07.790972+00	2022-01-21 10:37:07.791017+00	8	\N	\N	f	f
8063	PROJECT	Project	Moores Builders Agency	247506	2022-01-21 10:37:07.791119+00	2022-01-21 10:37:07.791163+00	8	\N	\N	f	f
8064	PROJECT	Project	Moots Painting Distributors	247507	2022-01-21 10:37:07.791352+00	2022-01-21 10:37:07.791398+00	8	\N	\N	f	f
8065	PROJECT	Project	Moreb Plumbing Corporation	247508	2022-01-21 10:37:07.791505+00	2022-01-21 10:37:07.791549+00	8	\N	\N	f	f
8066	PROJECT	Project	Mortgage Center	247509	2022-01-21 10:37:07.791671+00	2022-01-21 10:37:07.791717+00	8	\N	\N	f	f
8067	PROJECT	Project	Moss Builders	247510	2022-01-21 10:37:07.791871+00	2022-01-21 10:37:07.791902+00	8	\N	\N	f	f
8068	PROJECT	Project	Moturu Tapasvi	278553	2022-01-21 10:37:07.791963+00	2022-01-21 10:37:07.791992+00	8	\N	\N	f	f
8069	PROJECT	Project	Mount Lake Terrace Markets Fabricators	247511	2022-01-21 10:37:07.792052+00	2022-01-21 10:37:07.792082+00	8	\N	\N	f	f
8070	PROJECT	Project	Moving Store	247512	2022-01-21 10:37:07.792141+00	2022-01-21 10:37:07.79217+00	8	\N	\N	f	f
8071	PROJECT	Project	MPower	247445	2022-01-21 10:37:07.792231+00	2022-01-21 10:37:07.79226+00	8	\N	\N	f	f
8072	PROJECT	Project	MuscleTech	247513	2022-01-21 10:37:07.792321+00	2022-01-21 10:37:07.792349+00	8	\N	\N	f	f
8073	PROJECT	Project	MW International (CAD)	247446	2022-01-21 10:37:07.79241+00	2022-01-21 10:37:07.792438+00	8	\N	\N	f	f
8074	PROJECT	Project	Nadia Phillipchuk	278554	2022-01-21 10:37:07.792499+00	2022-01-21 10:37:07.79253+00	8	\N	\N	f	f
8075	PROJECT	Project	Nania Painting Networking	247514	2022-01-21 10:37:07.79259+00	2022-01-21 10:37:07.792619+00	8	\N	\N	f	f
8076	PROJECT	Project	Neal Ferguson	247515	2022-01-21 10:37:07.792679+00	2022-01-21 10:37:07.792709+00	8	\N	\N	f	f
8077	PROJECT	Project	Nephew Publishing Group	247516	2022-01-21 10:37:07.792805+00	2022-01-21 10:37:07.792845+00	8	\N	\N	f	f
8078	PROJECT	Project	NetPace Promotions	247517	2022-01-21 10:37:07.793799+00	2022-01-21 10:37:07.793919+00	8	\N	\N	f	f
8079	PROJECT	Project	NetStar Inc	247518	2022-01-21 10:37:07.794079+00	2022-01-21 10:37:07.794123+00	8	\N	\N	f	f
8080	PROJECT	Project	NetSuite Incorp	247519	2022-01-21 10:37:07.79419+00	2022-01-21 10:37:07.794219+00	8	\N	\N	f	f
8081	PROJECT	Project	New Design of Rack	247520	2022-01-21 10:37:07.794279+00	2022-01-21 10:37:07.794308+00	8	\N	\N	f	f
8082	PROJECT	Project	New Server Rack Design	247521	2022-01-21 10:37:07.794368+00	2022-01-21 10:37:07.794397+00	8	\N	\N	f	f
8083	PROJECT	Project	New Ventures	247522	2022-01-21 10:37:07.794457+00	2022-01-21 10:37:07.794486+00	8	\N	\N	f	f
8084	PROJECT	Project	Niedzwiedz Antiques and Associates	247523	2022-01-21 10:37:07.794547+00	2022-01-21 10:37:07.794576+00	8	\N	\N	f	f
8085	PROJECT	Project	Nikon	247524	2022-01-21 10:37:07.794636+00	2022-01-21 10:37:07.794665+00	8	\N	\N	f	f
8086	PROJECT	Project	Nilesh	274659	2022-01-21 10:37:07.794725+00	2022-01-21 10:37:07.794754+00	8	\N	\N	f	f
8087	PROJECT	Project	Nordon Metal Fabricators Systems	247525	2022-01-21 10:37:07.794814+00	2022-01-21 10:37:07.794843+00	8	\N	\N	f	f
8088	PROJECT	Project	Novida and Chochrek Leasing Manufacturing	247526	2022-01-21 10:37:07.794903+00	2022-01-21 10:37:07.794932+00	8	\N	\N	f	f
8089	PROJECT	Project	Novx	247527	2022-01-21 10:37:07.794992+00	2022-01-21 10:37:07.795021+00	8	\N	\N	f	f
8090	PROJECT	Project	Oaks and Winters Inc	247531	2022-01-21 10:37:07.795082+00	2022-01-21 10:37:07.79511+00	8	\N	\N	f	f
8091	PROJECT	Project	Oceanside Hardware	247532	2022-01-21 10:37:07.79517+00	2022-01-21 10:37:07.795199+00	8	\N	\N	f	f
8092	PROJECT	Project	Oconner _ Holding Corp.	247533	2022-01-21 10:37:07.795259+00	2022-01-21 10:37:07.795288+00	8	\N	\N	f	f
8093	PROJECT	Project	Oeder Liquors Company	247534	2022-01-21 10:37:07.797369+00	2022-01-21 10:37:07.797429+00	8	\N	\N	f	f
8094	PROJECT	Project	Oestreich Liquors Inc.	247535	2022-01-21 10:37:07.797522+00	2022-01-21 10:37:07.797552+00	8	\N	\N	f	f
8095	PROJECT	Project	Office Remodel	247536	2022-01-21 10:37:07.797616+00	2022-01-21 10:37:07.797671+00	8	\N	\N	f	f
8096	PROJECT	Project	Oiler Corporation	247537	2022-01-21 10:37:07.797794+00	2022-01-21 10:37:07.797836+00	8	\N	\N	f	f
8097	PROJECT	Project	Oldsmar Liquors and Associates	247538	2022-01-21 10:37:07.797929+00	2022-01-21 10:37:07.797969+00	8	\N	\N	f	f
8098	PROJECT	Project	Oliver Skin Supplies	247539	2022-01-21 10:37:07.809167+00	2022-01-21 10:37:07.809212+00	8	\N	\N	f	f
8099	PROJECT	Project	Olympia Antiques Management	247540	2022-01-21 10:37:07.809277+00	2022-01-21 10:37:07.809306+00	8	\N	\N	f	f
8100	PROJECT	Project	ONLINE1	247528	2022-01-21 10:37:07.809368+00	2022-01-21 10:37:07.809397+00	8	\N	\N	f	f
8101	PROJECT	Project	Orange Leasing -	247541	2022-01-21 10:37:07.809458+00	2022-01-21 10:37:07.809487+00	8	\N	\N	f	f
8102	PROJECT	Project	OREA	247529	2022-01-21 10:37:07.809548+00	2022-01-21 10:37:07.809577+00	8	\N	\N	f	f
8103	PROJECT	Project	Orion Hardware	247542	2022-01-21 10:37:07.809638+00	2022-01-21 10:37:07.809667+00	8	\N	\N	f	f
8104	PROJECT	Project	Orlando Automotive Leasing	247543	2022-01-21 10:37:07.809727+00	2022-01-21 10:37:07.809757+00	8	\N	\N	f	f
8105	PROJECT	Project	Ornelas and Ciejka Painting and Associates	247544	2022-01-21 10:37:07.809817+00	2022-01-21 10:37:07.809847+00	8	\N	\N	f	f
8106	PROJECT	Project	Ortego Construction Distributors	247545	2022-01-21 10:37:07.809941+00	2022-01-21 10:37:07.809996+00	8	\N	\N	f	f
8107	PROJECT	Project	Osler Antiques -	247546	2022-01-21 10:37:07.810513+00	2022-01-21 10:37:07.810577+00	8	\N	\N	f	f
8108	PROJECT	Project	OSPE Inc	247530	2022-01-21 10:37:07.81068+00	2022-01-21 10:37:07.810721+00	8	\N	\N	f	f
8109	PROJECT	Project	Ostling Metal Fabricators Fabricators	247547	2022-01-21 10:37:07.810842+00	2022-01-21 10:37:07.810885+00	8	\N	\N	f	f
8110	PROJECT	Project	Ostrzyeki Markets Distributors	247548	2022-01-21 10:37:07.810984+00	2022-01-21 10:37:07.811038+00	8	\N	\N	f	f
8111	PROJECT	Project	Owasso Attorneys Holding Corp.	247549	2022-01-21 10:37:07.811425+00	2022-01-21 10:37:07.811469+00	8	\N	\N	f	f
8112	PROJECT	Project	Oxon Insurance Agency	278555	2022-01-21 10:37:07.811706+00	2022-01-21 10:37:07.811753+00	8	\N	\N	f	f
8113	PROJECT	Project	Oxon Insurance Agency:Oxon -- Holiday Party	278556	2022-01-21 10:37:07.811841+00	2022-01-21 10:37:07.811876+00	8	\N	\N	f	f
8114	PROJECT	Project	Oxon Insurance Agency:Oxon - Retreat	278557	2022-01-21 10:37:07.812124+00	2022-01-21 10:37:07.812254+00	8	\N	\N	f	f
8115	PROJECT	Project	Pacific Northwest	247550	2022-01-21 10:37:07.812368+00	2022-01-21 10:37:07.812407+00	8	\N	\N	f	f
8116	PROJECT	Project	Pagliari Builders Services	247551	2022-01-21 10:37:07.812492+00	2022-01-21 10:37:07.812527+00	8	\N	\N	f	f
8117	PROJECT	Project	Palmer and Barnar Liquors Leasing	247552	2022-01-21 10:37:07.812602+00	2022-01-21 10:37:07.812636+00	8	\N	\N	f	f
8118	PROJECT	Project	Palmisano Hospital Fabricators	247553	2022-01-21 10:37:07.812813+00	2022-01-21 10:37:07.812856+00	8	\N	\N	f	f
8119	PROJECT	Project	Palys Attorneys	247554	2022-01-21 10:37:07.813012+00	2022-01-21 10:37:07.813117+00	8	\N	\N	f	f
8120	PROJECT	Project	Panora Lumber Dynamics	247555	2022-01-21 10:37:07.813359+00	2022-01-21 10:37:07.813631+00	8	\N	\N	f	f
8121	PROJECT	Project	Parking Lot Construction	247556	2022-01-21 10:37:07.813753+00	2022-01-21 10:37:07.814089+00	8	\N	\N	f	f
8122	PROJECT	Project	Pasanen Attorneys Agency	247557	2022-01-21 10:37:07.814231+00	2022-01-21 10:37:07.814266+00	8	\N	\N	f	f
8123	PROJECT	Project	Patel Cafe	247558	2022-01-21 10:37:07.815226+00	2022-01-21 10:37:07.815748+00	8	\N	\N	f	f
8124	PROJECT	Project	Paulsen Medical Supplies	246806	2022-01-21 10:37:07.815894+00	2022-01-21 10:37:07.815936+00	8	\N	\N	f	f
8125	PROJECT	Project	Paveglio Leasing Leasing	247559	2022-01-21 10:37:07.816028+00	2022-01-21 10:37:07.81607+00	8	\N	\N	f	f
8126	PROJECT	Project	Peak Products	247560	2022-01-21 10:37:07.816387+00	2022-01-21 10:37:07.816438+00	8	\N	\N	f	f
8127	PROJECT	Project	Penalver Automotive and Associates	247561	2022-01-21 10:37:07.816516+00	2022-01-21 10:37:07.816547+00	8	\N	\N	f	f
8128	PROJECT	Project	Penco Medical Inc.	247562	2022-01-21 10:37:07.81661+00	2022-01-21 10:37:07.81664+00	8	\N	\N	f	f
8129	PROJECT	Project	Penister Hospital Fabricators	247563	2022-01-21 10:37:07.816701+00	2022-01-21 10:37:07.816731+00	8	\N	\N	f	f
8130	PROJECT	Project	Pertuit Liquors Management	247564	2022-01-21 10:37:07.816792+00	2022-01-21 10:37:07.816822+00	8	\N	\N	f	f
8131	PROJECT	Project	Peterson Builders & Assoc	247565	2022-01-21 10:37:07.816882+00	2022-01-21 10:37:07.816912+00	8	\N	\N	f	f
8132	PROJECT	Project	Petticrew Apartments Incorporated	247566	2022-01-21 10:37:07.816972+00	2022-01-21 10:37:07.817001+00	8	\N	\N	f	f
8133	PROJECT	Project	Peveler and Tyrer Software Networking	247567	2022-01-21 10:37:07.817061+00	2022-01-21 10:37:07.817091+00	8	\N	\N	f	f
8134	PROJECT	Project	Phillip Van Hook	247568	2022-01-21 10:37:07.817151+00	2022-01-21 10:37:07.817181+00	8	\N	\N	f	f
8135	PROJECT	Project	Pickler Construction Leasing	247569	2022-01-21 10:37:07.817241+00	2022-01-21 10:37:07.81727+00	8	\N	\N	f	f
8136	PROJECT	Project	Pigler Plumbing Management	247570	2022-01-21 10:37:07.817331+00	2022-01-21 10:37:07.81736+00	8	\N	\N	f	f
8137	PROJECT	Project	Pilkerton Windows Sales	247571	2022-01-21 10:37:07.81742+00	2022-01-21 10:37:07.817449+00	8	\N	\N	f	f
8138	PROJECT	Project	Pitney Bowes	247572	2022-01-21 10:37:07.817509+00	2022-01-21 10:37:07.817539+00	8	\N	\N	f	f
8139	PROJECT	Project	Pittaway Inc	247573	2022-01-21 10:37:07.8176+00	2022-01-21 10:37:07.817629+00	8	\N	\N	f	f
8140	PROJECT	Project	Pittsburgh Quantum Analytics	247574	2022-01-21 10:37:07.817688+00	2022-01-21 10:37:07.817718+00	8	\N	\N	f	f
8141	PROJECT	Project	Pittsburgh Windows Incorporated	247575	2022-01-21 10:37:07.817778+00	2022-01-21 10:37:07.817807+00	8	\N	\N	f	f
8142	PROJECT	Project	Plantronics (EUR)	247576	2022-01-21 10:37:07.817867+00	2022-01-21 10:37:07.817896+00	8	\N	\N	f	f
8143	PROJECT	Project	Platform APIs	284362	2022-01-21 10:37:07.817957+00	2022-01-21 10:37:07.817986+00	8	\N	\N	f	f
8144	PROJECT	Project	Plexfase Construction Inc.	247577	2022-01-21 10:37:07.818046+00	2022-01-21 10:37:07.818075+00	8	\N	\N	f	f
8145	PROJECT	Project	Podvin Software Networking	247578	2022-01-21 10:37:07.818136+00	2022-01-21 10:37:07.818165+00	8	\N	\N	f	f
8146	PROJECT	Project	Poland and Burrus Plumbing	247579	2022-01-21 10:37:07.818225+00	2022-01-21 10:37:07.818254+00	8	\N	\N	f	f
8147	PROJECT	Project	Polard Windows	247580	2022-01-21 10:37:07.818315+00	2022-01-21 10:37:07.818344+00	8	\N	\N	f	f
8148	PROJECT	Project	Pomona Hardware Leasing	247581	2022-01-21 10:37:07.831666+00	2022-01-21 10:37:07.831711+00	8	\N	\N	f	f
8149	PROJECT	Project	Ponniah	247582	2022-01-21 10:37:07.83178+00	2022-01-21 10:37:07.831811+00	8	\N	\N	f	f
8150	PROJECT	Project	Port Angeles Telecom Networking	247583	2022-01-21 10:37:07.831874+00	2022-01-21 10:37:07.831904+00	8	\N	\N	f	f
8151	PROJECT	Project	Port Townsend Title Corporation	247584	2022-01-21 10:37:07.831966+00	2022-01-21 10:37:07.831995+00	8	\N	\N	f	f
8152	PROJECT	Project	Pote Leasing Rentals	247585	2022-01-21 10:37:07.832599+00	2022-01-21 10:37:07.832749+00	8	\N	\N	f	f
8153	PROJECT	Project	Primas Consulting	247586	2022-01-21 10:37:07.833177+00	2022-01-21 10:37:07.833208+00	8	\N	\N	f	f
8154	PROJECT	Project	Princeton Automotive Management	247587	2022-01-21 10:37:07.833271+00	2022-01-21 10:37:07.8333+00	8	\N	\N	f	f
8155	PROJECT	Project	Pritts Construction Distributors	247588	2022-01-21 10:37:07.83336+00	2022-01-21 10:37:07.833371+00	8	\N	\N	f	f
8156	PROJECT	Project	Progress Inc	247589	2022-01-21 10:37:07.833421+00	2022-01-21 10:37:07.833451+00	8	\N	\N	f	f
8157	PROJECT	Project	Project 1	203309	2022-01-21 10:37:07.833513+00	2022-01-21 10:37:07.833543+00	8	\N	\N	f	f
8158	PROJECT	Project	Project 10	203318	2022-01-21 10:37:07.83375+00	2022-01-21 10:37:07.833804+00	8	\N	\N	f	f
8159	PROJECT	Project	Project 2	203310	2022-01-21 10:37:07.833901+00	2022-01-21 10:37:07.833985+00	8	\N	\N	f	f
8160	PROJECT	Project	Project 3	203311	2022-01-21 10:37:07.834382+00	2022-01-21 10:37:07.834445+00	8	\N	\N	f	f
8161	PROJECT	Project	Project 4	203312	2022-01-21 10:37:07.834872+00	2022-01-21 10:37:07.83502+00	8	\N	\N	f	f
8162	PROJECT	Project	Project 5	203313	2022-01-21 10:37:07.835516+00	2022-01-21 10:37:07.835968+00	8	\N	\N	f	f
8163	PROJECT	Project	Project 6	203314	2022-01-21 10:37:07.836101+00	2022-01-21 10:37:07.836138+00	8	\N	\N	f	f
8164	PROJECT	Project	Project 7	203315	2022-01-21 10:37:07.836317+00	2022-01-21 10:37:07.836359+00	8	\N	\N	f	f
8165	PROJECT	Project	Project 8	203316	2022-01-21 10:37:07.836455+00	2022-01-21 10:37:07.836487+00	8	\N	\N	f	f
8166	PROJECT	Project	Project 9	203317	2022-01-21 10:37:07.83655+00	2022-01-21 10:37:07.836579+00	8	\N	\N	f	f
8167	PROJECT	Project	Project Red	251304	2022-01-21 10:37:07.83664+00	2022-01-21 10:37:07.836687+00	8	\N	\N	f	f
8168	PROJECT	Project	Prokup Plumbing Corporation	247590	2022-01-21 10:37:07.836739+00	2022-01-21 10:37:07.83676+00	8	\N	\N	f	f
8169	PROJECT	Project	Prudential	247591	2022-01-21 10:37:07.836821+00	2022-01-21 10:37:07.83685+00	8	\N	\N	f	f
8170	PROJECT	Project	Ptomey Title Group	247592	2022-01-21 10:37:07.836911+00	2022-01-21 10:37:07.836941+00	8	\N	\N	f	f
8171	PROJECT	Project	Pueblo Construction Fabricators	247593	2022-01-21 10:37:07.837002+00	2022-01-21 10:37:07.837031+00	8	\N	\N	f	f
8172	PROJECT	Project	Pulse	247594	2022-01-21 10:37:07.837091+00	2022-01-21 10:37:07.837116+00	8	\N	\N	f	f
8173	PROJECT	Project	Purchase Construction Agency	247595	2022-01-21 10:37:07.837167+00	2022-01-21 10:37:07.837191+00	8	\N	\N	f	f
8174	PROJECT	Project	Puyallup Liquors Networking	247596	2022-01-21 10:37:07.837243+00	2022-01-21 10:37:07.837273+00	8	\N	\N	f	f
8175	PROJECT	Project	Pye's Cakes	246807	2022-01-21 10:37:07.837957+00	2022-01-21 10:37:07.838438+00	8	\N	\N	f	f
8176	PROJECT	Project	qa 54	247930	2022-01-21 10:37:07.839642+00	2022-01-21 10:37:07.839716+00	8	\N	\N	f	f
8177	PROJECT	Project	QJunction Inc	247597	2022-01-21 10:37:07.840029+00	2022-01-21 10:37:07.840265+00	8	\N	\N	f	f
8178	PROJECT	Project	Qualle Metal Fabricators Distributors	247598	2022-01-21 10:37:07.840759+00	2022-01-21 10:37:07.840817+00	8	\N	\N	f	f
8179	PROJECT	Project	Quantum X	247599	2022-01-21 10:37:07.8409+00	2022-01-21 10:37:07.840921+00	8	\N	\N	f	f
8180	PROJECT	Project	Quezad Lumber Leasing	247600	2022-01-21 10:37:07.840972+00	2022-01-21 10:37:07.841032+00	8	\N	\N	f	f
8181	PROJECT	Project	Quiterio Windows Co.	247601	2022-01-21 10:37:07.841087+00	2022-01-21 10:37:07.841118+00	8	\N	\N	f	f
8182	PROJECT	Project	Rabeck Liquors Group	247602	2022-01-21 10:37:07.844963+00	2022-01-21 10:37:07.845019+00	8	\N	\N	f	f
8183	PROJECT	Project	Rago Travel Agency	246808	2022-01-21 10:37:07.845184+00	2022-01-21 10:37:07.84523+00	8	\N	\N	f	f
8184	PROJECT	Project	Ralphs Attorneys Group	247603	2022-01-21 10:37:07.845337+00	2022-01-21 10:37:07.845439+00	8	\N	\N	f	f
8185	PROJECT	Project	Ramal Builders Incorporated	247604	2022-01-21 10:37:07.846074+00	2022-01-21 10:37:07.846154+00	8	\N	\N	f	f
8186	PROJECT	Project	Ramsy Publishing Company	247605	2022-01-21 10:37:07.846264+00	2022-01-21 10:37:07.846311+00	8	\N	\N	f	f
8187	PROJECT	Project	Randy James	247606	2022-01-21 10:37:07.846434+00	2022-01-21 10:37:07.84648+00	8	\N	\N	f	f
8188	PROJECT	Project	Randy Rudd	247607	2022-01-21 10:37:07.846595+00	2022-01-21 10:37:07.846638+00	8	\N	\N	f	f
8189	PROJECT	Project	Rastorfer Automotive Holding Corp.	247609	2022-01-21 10:37:07.846747+00	2022-01-21 10:37:07.847128+00	8	\N	\N	f	f
8190	PROJECT	Project	Ras Windows -	247608	2022-01-21 10:37:07.847311+00	2022-01-21 10:37:07.847392+00	8	\N	\N	f	f
8191	PROJECT	Project	Rauf Catering	247610	2022-01-21 10:37:07.847497+00	2022-01-21 10:37:07.847546+00	8	\N	\N	f	f
8192	PROJECT	Project	Redick Antiques Inc.	247612	2022-01-21 10:37:07.847625+00	2022-01-21 10:37:07.847805+00	8	\N	\N	f	f
8193	PROJECT	Project	RedPath Sugars	247611	2022-01-21 10:37:07.847878+00	2022-01-21 10:37:07.847907+00	8	\N	\N	f	f
8194	PROJECT	Project	Red Rock Diner	246809	2022-01-21 10:37:07.847969+00	2022-01-21 10:37:07.847995+00	8	\N	\N	f	f
8195	PROJECT	Project	Reedus Telecom Group	247613	2022-01-21 10:37:07.848047+00	2022-01-21 10:37:07.848077+00	8	\N	\N	f	f
8196	PROJECT	Project	Refco	247614	2022-01-21 10:37:07.848137+00	2022-01-21 10:37:07.848166+00	8	\N	\N	f	f
8197	PROJECT	Project	Reinfeld and Jurczak Hospital Incorporated	247615	2022-01-21 10:37:07.848263+00	2022-01-21 10:37:07.848409+00	8	\N	\N	f	f
8198	PROJECT	Project	Reinhardt and Sabori Painting Group	247616	2022-01-21 10:37:07.85886+00	2022-01-21 10:37:07.858955+00	8	\N	\N	f	f
8199	PROJECT	Project	Reisdorf Title Services	247617	2022-01-21 10:37:07.859353+00	2022-01-21 10:37:07.859416+00	8	\N	\N	f	f
8200	PROJECT	Project	Reisman Windows Management	247618	2022-01-21 10:37:07.859524+00	2022-01-21 10:37:07.859566+00	8	\N	\N	f	f
8201	PROJECT	Project	Remodel	247619	2022-01-21 10:37:07.859666+00	2022-01-21 10:37:07.85971+00	8	\N	\N	f	f
8202	PROJECT	Project	Rennemeyer Liquors Systems	247620	2022-01-21 10:37:07.860409+00	2022-01-21 10:37:07.86049+00	8	\N	\N	f	f
8203	PROJECT	Project	Republic Builders and Associates	247621	2022-01-21 10:37:07.860639+00	2022-01-21 10:37:07.860686+00	8	\N	\N	f	f
8204	PROJECT	Project	Rey Software Inc.	247622	2022-01-21 10:37:07.86081+00	2022-01-21 10:37:07.860941+00	8	\N	\N	f	f
8205	PROJECT	Project	Rezentes Catering Dynamics	247623	2022-01-21 10:37:07.861063+00	2022-01-21 10:37:07.861177+00	8	\N	\N	f	f
8206	PROJECT	Project	Rhody Leasing and Associates	247624	2022-01-21 10:37:07.86131+00	2022-01-21 10:37:07.861345+00	8	\N	\N	f	f
8207	PROJECT	Project	Rickers Apartments Company	247625	2022-01-21 10:37:07.861409+00	2022-01-21 10:37:07.861438+00	8	\N	\N	f	f
8208	PROJECT	Project	Ridderhoff Painting Services	247626	2022-01-21 10:37:07.861499+00	2022-01-21 10:37:07.861528+00	8	\N	\N	f	f
8209	PROJECT	Project	Ridgeway Corporation	247627	2022-01-21 10:37:07.861589+00	2022-01-21 10:37:07.861618+00	8	\N	\N	f	f
8210	PROJECT	Project	Riede Title and Associates	247628	2022-01-21 10:37:07.861678+00	2022-01-21 10:37:07.861707+00	8	\N	\N	f	f
8211	PROJECT	Project	Rio Rancho Painting Agency	247629	2022-01-21 10:37:07.861767+00	2022-01-21 10:37:07.861797+00	8	\N	\N	f	f
9128	CATEGORY	Category	Utility	142035	2022-01-21 10:42:23.978919+00	2022-01-21 10:42:23.979035+00	9	\N	\N	f	f
8212	PROJECT	Project	Riverside Hospital and Associates	247630	2022-01-21 10:37:07.861858+00	2022-01-21 10:37:07.861887+00	8	\N	\N	f	f
8213	PROJECT	Project	Robare Builders Corporation	247631	2022-01-21 10:37:07.861948+00	2022-01-21 10:37:07.861977+00	8	\N	\N	f	f
8214	PROJECT	Project	Rob deMontarnal	278558	2022-01-21 10:37:07.862037+00	2022-01-21 10:37:07.862066+00	8	\N	\N	f	f
8215	PROJECT	Project	Robert Brady	247632	2022-01-21 10:37:07.862127+00	2022-01-21 10:37:07.862156+00	8	\N	\N	f	f
8216	PROJECT	Project	Robert Huffman	247633	2022-01-21 10:37:07.862217+00	2022-01-21 10:37:07.862245+00	8	\N	\N	f	f
8217	PROJECT	Project	Robert Lee	247634	2022-01-21 10:37:07.862305+00	2022-01-21 10:37:07.862334+00	8	\N	\N	f	f
8218	PROJECT	Project	Robert Solan	247635	2022-01-21 10:37:07.862395+00	2022-01-21 10:37:07.862424+00	8	\N	\N	f	f
8219	PROJECT	Project	Rogers Communication	247636	2022-01-21 10:37:07.862484+00	2022-01-21 10:37:07.862513+00	8	\N	\N	f	f
8220	PROJECT	Project	Rondonuwu Fruit and Vegi	246810	2022-01-21 10:37:07.862574+00	2022-01-21 10:37:07.862603+00	8	\N	\N	f	f
8221	PROJECT	Project	Rosner and Savo Antiques Systems	247637	2022-01-21 10:37:07.862664+00	2022-01-21 10:37:07.862693+00	8	\N	\N	f	f
8222	PROJECT	Project	Ross Nepean	247638	2022-01-21 10:37:07.862752+00	2022-01-21 10:37:07.862781+00	8	\N	\N	f	f
8223	PROJECT	Project	Roswell Leasing Management	247639	2022-01-21 10:37:07.862842+00	2022-01-21 10:37:07.862871+00	8	\N	\N	f	f
8224	PROJECT	Project	Roule and Mattsey _ Management	247640	2022-01-21 10:37:07.862932+00	2022-01-21 10:37:07.862961+00	8	\N	\N	f	f
8225	PROJECT	Project	Roundtree Attorneys Inc.	247641	2022-01-21 10:37:07.863021+00	2022-01-21 10:37:07.863049+00	8	\N	\N	f	f
8226	PROJECT	Project	Rowie Williams	247642	2022-01-21 10:37:07.863109+00	2022-01-21 10:37:07.863138+00	8	\N	\N	f	f
8227	PROJECT	Project	Roycroft Construction	247643	2022-01-21 10:37:07.863199+00	2022-01-21 10:37:07.863227+00	8	\N	\N	f	f
8228	PROJECT	Project	Ruleman Title Distributors	247644	2022-01-21 10:37:07.863288+00	2022-01-21 10:37:07.863317+00	8	\N	\N	f	f
8229	PROJECT	Project	Russell Telecom	247646	2022-01-21 10:37:07.863377+00	2022-01-21 10:37:07.863406+00	8	\N	\N	f	f
8230	PROJECT	Project	Russ Mygrant	247645	2022-01-21 10:37:07.863467+00	2022-01-21 10:37:07.863496+00	8	\N	\N	f	f
8231	PROJECT	Project	Ruts Construction Holding Corp.	247647	2022-01-21 10:37:07.863556+00	2022-01-21 10:37:07.863585+00	8	\N	\N	f	f
8232	PROJECT	Project	Saenger _ Inc.	247649	2022-01-21 10:37:07.863645+00	2022-01-21 10:37:07.863674+00	8	\N	\N	f	f
8233	PROJECT	Project	Sage Project 1	243614	2022-01-21 10:37:07.863734+00	2022-01-21 10:37:07.863914+00	8	\N	\N	f	f
8234	PROJECT	Project	Sage Project 10	243621	2022-01-21 10:37:07.864003+00	2022-01-21 10:37:07.864032+00	8	\N	\N	f	f
8235	PROJECT	Project	Sage Project 2	243618	2022-01-21 10:37:07.864094+00	2022-01-21 10:37:07.864124+00	8	\N	\N	f	f
8236	PROJECT	Project	Sage Project 3	243613	2022-01-21 10:37:07.864184+00	2022-01-21 10:37:07.864213+00	8	\N	\N	f	f
8237	PROJECT	Project	Sage Project 4	243615	2022-01-21 10:37:07.864274+00	2022-01-21 10:37:07.864304+00	8	\N	\N	f	f
8238	PROJECT	Project	Sage Project 5	243612	2022-01-21 10:37:07.864364+00	2022-01-21 10:37:07.864393+00	8	\N	\N	f	f
8239	PROJECT	Project	Sage Project 6	243619	2022-01-21 10:37:07.864453+00	2022-01-21 10:37:07.864483+00	8	\N	\N	f	f
8240	PROJECT	Project	Sage Project 7	243620	2022-01-21 10:37:07.864543+00	2022-01-21 10:37:07.864572+00	8	\N	\N	f	f
8241	PROJECT	Project	Sage Project 8	243611	2022-01-21 10:37:07.864633+00	2022-01-21 10:37:07.864662+00	8	\N	\N	f	f
8242	PROJECT	Project	Sage Project 9	243617	2022-01-21 10:37:07.864723+00	2022-01-21 10:37:07.864752+00	8	\N	\N	f	f
8243	PROJECT	Project	Sage project fyle	243610	2022-01-21 10:37:07.864813+00	2022-01-21 10:37:07.864842+00	8	\N	\N	f	f
8244	PROJECT	Project	Salisbury Attorneys Group	247650	2022-01-21 10:37:07.864903+00	2022-01-21 10:37:07.864932+00	8	\N	\N	f	f
8245	PROJECT	Project	Sally Ward	247651	2022-01-21 10:37:07.864994+00	2022-01-21 10:37:07.865023+00	8	\N	\N	f	f
8246	PROJECT	Project	Samantha Walker	247653	2022-01-21 10:37:07.865084+00	2022-01-21 10:37:07.865113+00	8	\N	\N	f	f
8247	PROJECT	Project	Sam Brown	247652	2022-01-21 10:37:07.865174+00	2022-01-21 10:37:07.865203+00	8	\N	\N	f	f
8248	PROJECT	Project	Sample Test	278284	2022-01-21 10:37:08.231906+00	2022-01-21 10:37:08.231957+00	8	\N	\N	f	f
8249	PROJECT	Project	San Angelo Automotive Rentals	247654	2022-01-21 10:37:08.232026+00	2022-01-21 10:37:08.232056+00	8	\N	\N	f	f
8250	PROJECT	Project	San Diego Plumbing Distributors	247655	2022-01-21 10:37:08.232117+00	2022-01-21 10:37:08.232147+00	8	\N	\N	f	f
8251	PROJECT	Project	San Diego Windows Agency	247656	2022-01-21 10:37:08.232207+00	2022-01-21 10:37:08.232237+00	8	\N	\N	f	f
8252	PROJECT	Project	Sandoval Products Inc	247659	2022-01-21 10:37:08.232297+00	2022-01-21 10:37:08.232326+00	8	\N	\N	f	f
8253	PROJECT	Project	Sandra Burns	247660	2022-01-21 10:37:08.232387+00	2022-01-21 10:37:08.232416+00	8	\N	\N	f	f
8254	PROJECT	Project	Sandwich Antiques Services	247661	2022-01-21 10:37:08.232476+00	2022-01-21 10:37:08.232506+00	8	\N	\N	f	f
8255	PROJECT	Project	Sandwich Telecom Sales	247662	2022-01-21 10:37:08.232693+00	2022-01-21 10:37:08.232726+00	8	\N	\N	f	f
8256	PROJECT	Project	Sandy King	247663	2022-01-21 10:37:08.232788+00	2022-01-21 10:37:08.232817+00	8	\N	\N	f	f
8257	PROJECT	Project	Sandy Whines	247664	2022-01-21 10:37:08.232878+00	2022-01-21 10:37:08.232907+00	8	\N	\N	f	f
8258	PROJECT	Project	San Francisco Design Center	247657	2022-01-21 10:37:08.232968+00	2022-01-21 10:37:08.232997+00	8	\N	\N	f	f
8259	PROJECT	Project	San Luis Obispo Construction Inc.	247658	2022-01-21 10:37:08.233058+00	2022-01-21 10:37:08.233087+00	8	\N	\N	f	f
8260	PROJECT	Project	Santa Ana Telecom Management	247665	2022-01-21 10:37:08.233147+00	2022-01-21 10:37:08.233177+00	8	\N	\N	f	f
8261	PROJECT	Project	Santa Fe Springs Construction Corporation	247666	2022-01-21 10:37:08.233237+00	2022-01-21 10:37:08.233266+00	8	\N	\N	f	f
8262	PROJECT	Project	Santa Maria Lumber Inc.	247667	2022-01-21 10:37:08.233326+00	2022-01-21 10:37:08.233355+00	8	\N	\N	f	f
8263	PROJECT	Project	Santa Monica Attorneys Manufacturing	247668	2022-01-21 10:37:08.233415+00	2022-01-21 10:37:08.233445+00	8	\N	\N	f	f
8264	PROJECT	Project	Sarasota Software Rentals	247669	2022-01-21 10:37:08.233506+00	2022-01-21 10:37:08.233534+00	8	\N	\N	f	f
8265	PROJECT	Project	Sarchett Antiques Networking	247670	2022-01-21 10:37:08.233595+00	2022-01-21 10:37:08.233624+00	8	\N	\N	f	f
8266	PROJECT	Project	Sawatzky Catering Rentals	247671	2022-01-21 10:37:08.233684+00	2022-01-21 10:37:08.233713+00	8	\N	\N	f	f
8267	PROJECT	Project	Sax Lumber Co.	247672	2022-01-21 10:37:08.233773+00	2022-01-21 10:37:08.233802+00	8	\N	\N	f	f
8268	PROJECT	Project	Scalley Construction Inc.	247673	2022-01-21 10:37:08.233862+00	2022-01-21 10:37:08.233891+00	8	\N	\N	f	f
8269	PROJECT	Project	Schlicker Metal Fabricators Fabricators	247674	2022-01-21 10:37:08.23395+00	2022-01-21 10:37:08.233979+00	8	\N	\N	f	f
8270	PROJECT	Project	Schmauder Markets Corporation	247675	2022-01-21 10:37:08.234039+00	2022-01-21 10:37:08.234069+00	8	\N	\N	f	f
8271	PROJECT	Project	Schmidt Sporting Goods	247676	2022-01-21 10:37:08.234129+00	2022-01-21 10:37:08.234158+00	8	\N	\N	f	f
8272	PROJECT	Project	Schneck Automotive Group	247677	2022-01-21 10:37:08.234218+00	2022-01-21 10:37:08.234247+00	8	\N	\N	f	f
8273	PROJECT	Project	Scholl Catering -	247678	2022-01-21 10:37:08.234307+00	2022-01-21 10:37:08.234336+00	8	\N	\N	f	f
8274	PROJECT	Project	Schreck Hardware Systems	247679	2022-01-21 10:37:08.234396+00	2022-01-21 10:37:08.234425+00	8	\N	\N	f	f
8275	PROJECT	Project	Schwarzenbach Attorneys Systems	247680	2022-01-21 10:37:08.234485+00	2022-01-21 10:37:08.234514+00	8	\N	\N	f	f
8276	PROJECT	Project	Scottsbluff Lumber -	247681	2022-01-21 10:37:08.234574+00	2022-01-21 10:37:08.234603+00	8	\N	\N	f	f
8277	PROJECT	Project	Scottsbluff Plumbing Rentals	247682	2022-01-21 10:37:08.234664+00	2022-01-21 10:37:08.234693+00	8	\N	\N	f	f
8278	PROJECT	Project	Scullion Telecom Agency	247683	2022-01-21 10:37:08.234753+00	2022-01-21 10:37:08.234782+00	8	\N	\N	f	f
8279	PROJECT	Project	Sebastian Inc.	247684	2022-01-21 10:37:08.240901+00	2022-01-21 10:37:08.240973+00	8	\N	\N	f	f
8280	PROJECT	Project	Sebek Builders Distributors	247685	2022-01-21 10:37:08.241086+00	2022-01-21 10:37:08.241131+00	8	\N	\N	f	f
8281	PROJECT	Project	Sedlak Inc	247686	2022-01-21 10:37:08.24123+00	2022-01-21 10:37:08.24127+00	8	\N	\N	f	f
8282	PROJECT	Project	Seecharan and Horten Hardware Manufacturing	247687	2022-01-21 10:37:08.241389+00	2022-01-21 10:37:08.241438+00	8	\N	\N	f	f
8283	PROJECT	Project	Seena Rose	247688	2022-01-21 10:37:08.241873+00	2022-01-21 10:37:08.242103+00	8	\N	\N	f	f
8284	PROJECT	Project	Seilhymer Antiques Distributors	247689	2022-01-21 10:37:08.266597+00	2022-01-21 10:37:08.266674+00	8	\N	\N	f	f
8285	PROJECT	Project	Selders Distributors	247690	2022-01-21 10:37:08.267313+00	2022-01-21 10:37:08.26737+00	8	\N	\N	f	f
8286	PROJECT	Project	Selia Metal Fabricators Company	247691	2022-01-21 10:37:08.267463+00	2022-01-21 10:37:08.268107+00	8	\N	\N	f	f
8287	PROJECT	Project	Seney Windows Agency	247692	2022-01-21 10:37:08.268837+00	2022-01-21 10:37:08.268922+00	8	\N	\N	f	f
8288	PROJECT	Project	Sequim Automotive Systems	247693	2022-01-21 10:37:08.269634+00	2022-01-21 10:37:08.26971+00	8	\N	\N	f	f
8289	PROJECT	Project	Service Job	247694	2022-01-21 10:37:08.269854+00	2022-01-21 10:37:08.270435+00	8	\N	\N	f	f
8290	PROJECT	Project	Seyler Title Distributors	247695	2022-01-21 10:37:08.270625+00	2022-01-21 10:37:08.270678+00	8	\N	\N	f	f
8291	PROJECT	Project	Shackelton Hospital Sales	247696	2022-01-21 10:37:08.271106+00	2022-01-21 10:37:08.271168+00	8	\N	\N	f	f
8292	PROJECT	Project	Shara Barnett	246811	2022-01-21 10:37:08.273232+00	2022-01-21 10:37:08.273277+00	8	\N	\N	f	f
8293	PROJECT	Project	Shara Barnett:Barnett Design	246812	2022-01-21 10:37:08.27336+00	2022-01-21 10:37:08.273401+00	8	\N	\N	f	f
8294	PROJECT	Project	Sharon Stone	247697	2022-01-21 10:37:08.273757+00	2022-01-21 10:37:08.273815+00	8	\N	\N	f	f
8295	PROJECT	Project	Sheinbein Construction Fabricators	247698	2022-01-21 10:37:08.273929+00	2022-01-21 10:37:08.274014+00	8	\N	\N	f	f
8296	PROJECT	Project	Sheldon Cooper	246813	2022-01-21 10:37:08.274417+00	2022-01-21 10:37:08.274464+00	8	\N	\N	f	f
8297	PROJECT	Project	Sheldon Cooper:Incremental Project	246814	2022-01-21 10:37:08.274923+00	2022-01-21 10:37:08.275122+00	8	\N	\N	f	f
8298	PROJECT	Project	Shininger Lumber Holding Corp.	247699	2022-01-21 10:37:08.316132+00	2022-01-21 10:37:08.316216+00	8	\N	\N	f	f
8299	PROJECT	Project	Shutter Title Services	247700	2022-01-21 10:37:08.316359+00	2022-01-21 10:37:08.316412+00	8	\N	\N	f	f
8300	PROJECT	Project	Siddiq Software -	247701	2022-01-21 10:37:08.316525+00	2022-01-21 10:37:08.31657+00	8	\N	\N	f	f
8301	PROJECT	Project	Simatry	247702	2022-01-21 10:37:08.316677+00	2022-01-21 10:37:08.316721+00	8	\N	\N	f	f
8302	PROJECT	Project	Simi Valley Telecom Dynamics	247703	2022-01-21 10:37:08.31682+00	2022-01-21 10:37:08.316862+00	8	\N	\N	f	f
8303	PROJECT	Project	Sindt Electric	247704	2022-01-21 10:37:08.316962+00	2022-01-21 10:37:08.317004+00	8	\N	\N	f	f
8304	PROJECT	Project	Skibo Construction Dynamics	247705	2022-01-21 10:37:08.317104+00	2022-01-21 10:37:08.317145+00	8	\N	\N	f	f
8305	PROJECT	Project	Slankard Automotive	247706	2022-01-21 10:37:08.317241+00	2022-01-21 10:37:08.317283+00	8	\N	\N	f	f
8306	PROJECT	Project	Slatter Metal Fabricators Inc.	247707	2022-01-21 10:37:08.317378+00	2022-01-21 10:37:08.317419+00	8	\N	\N	f	f
8307	PROJECT	Project	SlingShot Communications	247708	2022-01-21 10:37:08.317514+00	2022-01-21 10:37:08.317553+00	8	\N	\N	f	f
8308	PROJECT	Project	Sloman and Zeccardi Builders Agency	247709	2022-01-21 10:37:08.317651+00	2022-01-21 10:37:08.317692+00	8	\N	\N	f	f
8309	PROJECT	Project	Smelley _ Manufacturing	247710	2022-01-21 10:37:08.317785+00	2022-01-21 10:37:08.317826+00	8	\N	\N	f	f
8310	PROJECT	Project	Smith East	247711	2022-01-21 10:37:08.31792+00	2022-01-21 10:37:08.317961+00	8	\N	\N	f	f
8311	PROJECT	Project	Smith Inc.	247712	2022-01-21 10:37:08.318054+00	2022-01-21 10:37:08.318094+00	8	\N	\N	f	f
8312	PROJECT	Project	Smith Photographic Equipment	247713	2022-01-21 10:37:08.318188+00	2022-01-21 10:37:08.318226+00	8	\N	\N	f	f
8313	PROJECT	Project	Smith West	247714	2022-01-21 10:37:08.318327+00	2022-01-21 10:37:08.318367+00	8	\N	\N	f	f
8314	PROJECT	Project	Snode and Draper Leasing Rentals	247715	2022-01-21 10:37:08.318461+00	2022-01-21 10:37:08.318505+00	8	\N	\N	f	f
8315	PROJECT	Project	Soares Builders Inc.	247716	2022-01-21 10:37:08.32185+00	2022-01-21 10:37:08.32189+00	8	\N	\N	f	f
8316	PROJECT	Project	Solidd Group Ltd	247717	2022-01-21 10:37:08.321957+00	2022-01-21 10:37:08.321988+00	8	\N	\N	f	f
8317	PROJECT	Project	Soltrus	247718	2022-01-21 10:37:08.32205+00	2022-01-21 10:37:08.32208+00	8	\N	\N	f	f
8318	PROJECT	Project	Solymani Electric Leasing	247719	2022-01-21 10:37:08.322141+00	2022-01-21 10:37:08.322171+00	8	\N	\N	f	f
8319	PROJECT	Project	Sonnenschein Family Store	246815	2022-01-21 10:37:08.322232+00	2022-01-21 10:37:08.322261+00	8	\N	\N	f	f
8320	PROJECT	Project	Sossong Plumbing Holding Corp.	247720	2022-01-21 10:37:08.322322+00	2022-01-21 10:37:08.322351+00	8	\N	\N	f	f
8321	PROJECT	Project	South East	247721	2022-01-21 10:37:08.322412+00	2022-01-21 10:37:08.322441+00	8	\N	\N	f	f
8322	PROJECT	Project	Spany ltd	247722	2022-01-21 10:37:08.322501+00	2022-01-21 10:37:08.322531+00	8	\N	\N	f	f
8323	PROJECT	Project	Spectrum Eye	247723	2022-01-21 10:37:08.322591+00	2022-01-21 10:37:08.322621+00	8	\N	\N	f	f
8324	PROJECT	Project	Sports Authority	247725	2022-01-21 10:37:08.322681+00	2022-01-21 10:37:08.322711+00	8	\N	\N	f	f
8325	PROJECT	Project	Sport Station	247724	2022-01-21 10:37:08.322771+00	2022-01-21 10:37:08.322801+00	8	\N	\N	f	f
8326	PROJECT	Project	Spurgin Telecom Agency	247726	2022-01-21 10:37:08.322861+00	2022-01-21 10:37:08.322891+00	8	\N	\N	f	f
8327	PROJECT	Project	Sravan Prod Test Pr@d	243616	2022-01-21 10:37:08.322951+00	2022-01-21 10:37:08.322981+00	8	\N	\N	f	f
8328	PROJECT	Project	Sravan Prod Test Prod	254098	2022-01-21 10:37:08.323042+00	2022-01-21 10:37:08.323071+00	8	\N	\N	f	f
8329	PROJECT	Project	SS&C	247648	2022-01-21 10:37:08.323131+00	2022-01-21 10:37:08.323161+00	8	\N	\N	f	f
8330	PROJECT	Project	Stai Publishing -	247730	2022-01-21 10:37:08.323222+00	2022-01-21 10:37:08.323252+00	8	\N	\N	f	f
8331	PROJECT	Project	Stampe Leasing and Associates	247731	2022-01-21 10:37:08.323312+00	2022-01-21 10:37:08.323342+00	8	\N	\N	f	f
8332	PROJECT	Project	Stantec Inc	247732	2022-01-21 10:37:08.323403+00	2022-01-21 10:37:08.323432+00	8	\N	\N	f	f
8333	PROJECT	Project	Star Structural	247733	2022-01-21 10:37:08.323493+00	2022-01-21 10:37:08.323522+00	8	\N	\N	f	f
8334	PROJECT	Project	Steacy Tech Inc	247734	2022-01-21 10:37:08.323584+00	2022-01-21 10:37:08.323613+00	8	\N	\N	f	f
8335	PROJECT	Project	Steep and Cloud Liquors Co.	247735	2022-01-21 10:37:08.323674+00	2022-01-21 10:37:08.323703+00	8	\N	\N	f	f
8336	PROJECT	Project	Steffensmeier Markets Co.	247736	2022-01-21 10:37:08.323764+00	2022-01-21 10:37:08.323794+00	8	\N	\N	f	f
8337	PROJECT	Project	Steinberg Electric Networking	247737	2022-01-21 10:37:08.323854+00	2022-01-21 10:37:08.323883+00	8	\N	\N	f	f
8338	PROJECT	Project	Stella Sebastian Inc	247738	2022-01-21 10:37:08.323944+00	2022-01-21 10:37:08.323973+00	8	\N	\N	f	f
8339	PROJECT	Project	Stephan Simms	247739	2022-01-21 10:37:08.324033+00	2022-01-21 10:37:08.324062+00	8	\N	\N	f	f
8340	PROJECT	Project	Sternberger Telecom Incorporated	247740	2022-01-21 10:37:08.324123+00	2022-01-21 10:37:08.324152+00	8	\N	\N	f	f
8341	PROJECT	Project	Sterr Lumber Systems	247741	2022-01-21 10:37:08.324213+00	2022-01-21 10:37:08.324242+00	8	\N	\N	f	f
8342	PROJECT	Project	Steve Davis	247742	2022-01-21 10:37:08.324303+00	2022-01-21 10:37:08.324332+00	8	\N	\N	f	f
8343	PROJECT	Project	Steve Smith	247743	2022-01-21 10:37:08.324392+00	2022-01-21 10:37:08.324422+00	8	\N	\N	f	f
8344	PROJECT	Project	Stewart's Valet Parking	247744	2022-01-21 10:37:08.324482+00	2022-01-21 10:37:08.324512+00	8	\N	\N	f	f
8345	PROJECT	Project	St. Francis Yacht Club	247728	2022-01-21 10:37:08.324573+00	2022-01-21 10:37:08.324602+00	8	\N	\N	f	f
8346	PROJECT	Project	Stirling Truck Services	247745	2022-01-21 10:37:08.324663+00	2022-01-21 10:37:08.324692+00	8	\N	\N	f	f
8347	PROJECT	Project	Stitch Software Distributors	247746	2022-01-21 10:37:08.324753+00	2022-01-21 10:37:08.324782+00	8	\N	\N	f	f
8348	PROJECT	Project	St Lawrence Starch	247727	2022-01-21 10:37:08.352654+00	2022-01-21 10:37:08.352697+00	8	\N	\N	f	f
8349	PROJECT	Project	St. Mark's Church	247729	2022-01-21 10:37:08.352761+00	2022-01-21 10:37:08.352791+00	8	\N	\N	f	f
8350	PROJECT	Project	Stoett Telecom Rentals	247747	2022-01-21 10:37:08.352852+00	2022-01-21 10:37:08.352881+00	8	\N	\N	f	f
8351	PROJECT	Project	Stofflet Hardware Incorporated	247748	2022-01-21 10:37:08.352942+00	2022-01-21 10:37:08.352971+00	8	\N	\N	f	f
8352	PROJECT	Project	Stone & Cox	247749	2022-01-21 10:37:08.353032+00	2022-01-21 10:37:08.35306+00	8	\N	\N	f	f
8353	PROJECT	Project	Stonum Catering Group	247750	2022-01-21 10:37:08.353121+00	2022-01-21 10:37:08.35315+00	8	\N	\N	f	f
8354	PROJECT	Project	Storch Title Manufacturing	247751	2022-01-21 10:37:08.35321+00	2022-01-21 10:37:08.353239+00	8	\N	\N	f	f
8355	PROJECT	Project	Stotelmyer and Conelly Metal Fabricators Group	247752	2022-01-21 10:37:08.3533+00	2022-01-21 10:37:08.353329+00	8	\N	\N	f	f
8356	PROJECT	Project	Stower Electric Company	247753	2022-01-21 10:37:08.353389+00	2022-01-21 10:37:08.353418+00	8	\N	\N	f	f
8357	PROJECT	Project	Streib and Cravy Hardware Rentals	247754	2022-01-21 10:37:08.353478+00	2022-01-21 10:37:08.353507+00	8	\N	\N	f	f
8358	PROJECT	Project	Sturrup Antiques Management	247755	2022-01-21 10:37:08.353567+00	2022-01-21 10:37:08.353597+00	8	\N	\N	f	f
8359	PROJECT	Project	Summerton Hospital Services	247756	2022-01-21 10:37:08.353818+00	2022-01-21 10:37:08.353919+00	8	\N	\N	f	f
8360	PROJECT	Project	Summons Apartments Company	247757	2022-01-21 10:37:08.354126+00	2022-01-21 10:37:08.354157+00	8	\N	\N	f	f
8361	PROJECT	Project	Sumter Apartments Systems	247758	2022-01-21 10:37:08.354221+00	2022-01-21 10:37:08.354251+00	8	\N	\N	f	f
8362	PROJECT	Project	Sunnybrook Hospital	247759	2022-01-21 10:37:08.354311+00	2022-01-21 10:37:08.354341+00	8	\N	\N	f	f
8363	PROJECT	Project	Superior Car care Inc.	247760	2022-01-21 10:37:08.354402+00	2022-01-21 10:37:08.354431+00	8	\N	\N	f	f
8364	PROJECT	Project	Support Taxes	284363	2022-01-21 10:37:08.354492+00	2022-01-21 10:37:08.354521+00	8	\N	\N	f	f
8365	PROJECT	Project	Support T&M	247761	2022-01-21 10:37:08.354582+00	2022-01-21 10:37:08.354612+00	8	\N	\N	f	f
8366	PROJECT	Project	Sur Windows Services	247762	2022-01-21 10:37:08.354673+00	2022-01-21 10:37:08.354702+00	8	\N	\N	f	f
8367	PROJECT	Project	Sushi by Katsuyuki	246816	2022-01-21 10:37:08.354763+00	2022-01-21 10:37:08.354792+00	8	\N	\N	f	f
8368	PROJECT	Project	Svancara Antiques Holding Corp.	247763	2022-01-21 10:37:08.354853+00	2022-01-21 10:37:08.354882+00	8	\N	\N	f	f
8369	PROJECT	Project	Swanger Spirits	247764	2022-01-21 10:37:08.354943+00	2022-01-21 10:37:08.354972+00	8	\N	\N	f	f
8370	PROJECT	Project	Sweeton and Ketron Liquors Group	247765	2022-01-21 10:37:08.355032+00	2022-01-21 10:37:08.355061+00	8	\N	\N	f	f
8371	PROJECT	Project	Swiech Telecom Networking	247766	2022-01-21 10:37:08.355122+00	2022-01-21 10:37:08.355151+00	8	\N	\N	f	f
8372	PROJECT	Project	Swinea Antiques Holding Corp.	247767	2022-01-21 10:37:08.355212+00	2022-01-21 10:37:08.355241+00	8	\N	\N	f	f
8373	PROJECT	Project	Symore Construction Dynamics	247768	2022-01-21 10:37:08.355302+00	2022-01-21 10:37:08.355331+00	8	\N	\N	f	f
8374	PROJECT	Project	Szewczyk Apartments Holding Corp.	247769	2022-01-21 10:37:08.355392+00	2022-01-21 10:37:08.355421+00	8	\N	\N	f	f
8375	PROJECT	Project	Taback Construction Leasing	247777	2022-01-21 10:37:08.355482+00	2022-01-21 10:37:08.355511+00	8	\N	\N	f	f
8376	PROJECT	Project	TAB Ltd	247771	2022-01-21 10:37:08.355571+00	2022-01-21 10:37:08.355601+00	8	\N	\N	f	f
8377	PROJECT	Project	Talboti and Pauli Title Agency	247778	2022-01-21 10:37:08.355662+00	2022-01-21 10:37:08.355691+00	8	\N	\N	f	f
8378	PROJECT	Project	Tamara Gibson	247780	2022-01-21 10:37:08.355752+00	2022-01-21 10:37:08.355781+00	8	\N	\N	f	f
8379	PROJECT	Project	Tam Liquors	247779	2022-01-21 10:37:08.355842+00	2022-01-21 10:37:08.355871+00	8	\N	\N	f	f
8380	PROJECT	Project	Tanya Guerrero	247781	2022-01-21 10:37:08.355932+00	2022-01-21 10:37:08.355962+00	8	\N	\N	f	f
8381	PROJECT	Project	Tarangelo and Mccrea Apartments Holding Corp.	247782	2022-01-21 10:37:08.356022+00	2022-01-21 10:37:08.356052+00	8	\N	\N	f	f
8382	PROJECT	Project	Tarbutton Software Management	247783	2022-01-21 10:37:08.356113+00	2022-01-21 10:37:08.356142+00	8	\N	\N	f	f
8383	PROJECT	Project	TargetVision	247784	2022-01-21 10:37:08.356202+00	2022-01-21 10:37:08.356231+00	8	\N	\N	f	f
8384	PROJECT	Project	Taverna Liquors Networking	247785	2022-01-21 10:37:08.356292+00	2022-01-21 10:37:08.356322+00	8	\N	\N	f	f
8385	PROJECT	Project	Team Industrial	247786	2022-01-21 10:37:08.356382+00	2022-01-21 10:37:08.356411+00	8	\N	\N	f	f
8386	PROJECT	Project	Tebo Builders Management	247787	2022-01-21 10:37:08.356472+00	2022-01-21 10:37:08.356788+00	8	\N	\N	f	f
8387	PROJECT	Project	Technology Consultants	247788	2022-01-21 10:37:08.356998+00	2022-01-21 10:37:08.357031+00	8	\N	\N	f	f
8388	PROJECT	Project	Teddy Leasing Manufacturing	247789	2022-01-21 10:37:08.357094+00	2022-01-21 10:37:08.357124+00	8	\N	\N	f	f
8389	PROJECT	Project	Tenen Markets Dynamics	247790	2022-01-21 10:37:08.357186+00	2022-01-21 10:37:08.357216+00	8	\N	\N	f	f
8390	PROJECT	Project	Territory JMP 2	247791	2022-01-21 10:37:08.357276+00	2022-01-21 10:37:08.357306+00	8	\N	\N	f	f
8391	PROJECT	Project	Territory JMP 3	247792	2022-01-21 10:37:08.357366+00	2022-01-21 10:37:08.357396+00	8	\N	\N	f	f
8392	PROJECT	Project	Territory JMP 4	247793	2022-01-21 10:37:08.357456+00	2022-01-21 10:37:08.357485+00	8	\N	\N	f	f
8393	PROJECT	Project	TES Inc	247772	2022-01-21 10:37:08.357545+00	2022-01-21 10:37:08.357574+00	8	\N	\N	f	f
8394	PROJECT	Project	Tessa Darby	247794	2022-01-21 10:37:08.357635+00	2022-01-21 10:37:08.357664+00	8	\N	\N	f	f
8395	PROJECT	Project	test	247931	2022-01-21 10:37:08.357725+00	2022-01-21 10:37:08.357754+00	8	\N	\N	f	f
8396	PROJECT	Project	Test 2	247795	2022-01-21 10:37:08.357814+00	2022-01-21 10:37:08.357844+00	8	\N	\N	f	f
8397	PROJECT	Project	Test 3	247796	2022-01-21 10:37:08.357904+00	2022-01-21 10:37:08.357933+00	8	\N	\N	f	f
8398	PROJECT	Project	Test a	247798	2022-01-21 10:37:08.368894+00	2022-01-21 10:37:08.368943+00	8	\N	\N	f	f
8399	PROJECT	Project	tester1	247932	2022-01-21 10:37:08.369019+00	2022-01-21 10:37:08.369053+00	8	\N	\N	f	f
8400	PROJECT	Project	Test Test	247797	2022-01-21 10:37:08.36912+00	2022-01-21 10:37:08.369151+00	8	\N	\N	f	f
8401	PROJECT	Project	Teton Winter Sports	247799	2022-01-21 10:37:08.369215+00	2022-01-21 10:37:08.369245+00	8	\N	\N	f	f
8402	PROJECT	Project	The Coffee Corner	247800	2022-01-21 10:37:08.369308+00	2022-01-21 10:37:08.369338+00	8	\N	\N	f	f
8403	PROJECT	Project	The Liquor Barn	247801	2022-01-21 10:37:08.369401+00	2022-01-21 10:37:08.369431+00	8	\N	\N	f	f
8404	PROJECT	Project	Thermo Electron Corporation	247803	2022-01-21 10:37:08.369493+00	2022-01-21 10:37:08.369523+00	8	\N	\N	f	f
8405	PROJECT	Project	Therrell Publishing Networking	247804	2022-01-21 10:37:08.369585+00	2022-01-21 10:37:08.369739+00	8	\N	\N	f	f
8406	PROJECT	Project	The Validation Group	247802	2022-01-21 10:37:08.369823+00	2022-01-21 10:37:08.369854+00	8	\N	\N	f	f
8407	PROJECT	Project	Thomison Windows Networking	247805	2022-01-21 10:37:08.369917+00	2022-01-21 10:37:08.369947+00	8	\N	\N	f	f
8408	PROJECT	Project	Thongchanh Telecom Rentals	247806	2022-01-21 10:37:08.370008+00	2022-01-21 10:37:08.370039+00	8	\N	\N	f	f
8409	PROJECT	Project	Thorne & Assoc	247807	2022-01-21 10:37:08.370101+00	2022-01-21 10:37:08.370131+00	8	\N	\N	f	f
8410	PROJECT	Project	Tim Griffin	247808	2022-01-21 10:37:08.370192+00	2022-01-21 10:37:08.370221+00	8	\N	\N	f	f
8411	PROJECT	Project	Timinsky Lumber Dynamics	247809	2022-01-21 10:37:08.370282+00	2022-01-21 10:37:08.370312+00	8	\N	\N	f	f
8412	PROJECT	Project	Timmy Brown	247810	2022-01-21 10:37:08.370373+00	2022-01-21 10:37:08.370402+00	8	\N	\N	f	f
8413	PROJECT	Project	Titam Business Services	247811	2022-01-21 10:37:08.370462+00	2022-01-21 10:37:08.370491+00	8	\N	\N	f	f
8414	PROJECT	Project	T-M Manufacturing Corp.	247770	2022-01-21 10:37:08.370553+00	2022-01-21 10:37:08.370582+00	8	\N	\N	f	f
8415	PROJECT	Project	T&M Project with Five Tasks	284364	2022-01-21 10:37:08.370778+00	2022-01-21 10:37:08.370809+00	8	\N	\N	f	f
8416	PROJECT	Project	Tom Calhoun	247812	2022-01-21 10:37:08.370871+00	2022-01-21 10:37:08.370901+00	8	\N	\N	f	f
8417	PROJECT	Project	Tom Kratz	247813	2022-01-21 10:37:08.370963+00	2022-01-21 10:37:08.370992+00	8	\N	\N	f	f
8418	PROJECT	Project	Tomlinson	247815	2022-01-21 10:37:08.371052+00	2022-01-21 10:37:08.371081+00	8	\N	\N	f	f
8419	PROJECT	Project	Tom MacGillivray	247814	2022-01-21 10:37:08.371142+00	2022-01-21 10:37:08.371171+00	8	\N	\N	f	f
8420	PROJECT	Project	Tony Matsuda	247816	2022-01-21 10:37:08.371231+00	2022-01-21 10:37:08.37126+00	8	\N	\N	f	f
8421	PROJECT	Project	Top Drawer Creative	247817	2022-01-21 10:37:08.371321+00	2022-01-21 10:37:08.37135+00	8	\N	\N	f	f
8422	PROJECT	Project	Touchard Liquors Holding Corp.	247818	2022-01-21 10:37:08.371411+00	2022-01-21 10:37:08.37144+00	8	\N	\N	f	f
8423	PROJECT	Project	Tower AV and Telephone Install	247819	2022-01-21 10:37:08.371504+00	2022-01-21 10:37:08.37155+00	8	\N	\N	f	f
8424	PROJECT	Project	Tower PL-01	247820	2022-01-21 10:37:08.371645+00	2022-01-21 10:37:08.371685+00	8	\N	\N	f	f
8425	PROJECT	Project	Towsend Software Co.	247821	2022-01-21 10:37:08.371774+00	2022-01-21 10:37:08.371813+00	8	\N	\N	f	f
8426	PROJECT	Project	Tracy Attorneys Management	247822	2022-01-21 10:37:08.371902+00	2022-01-21 10:37:08.371943+00	8	\N	\N	f	f
8427	PROJECT	Project	Travis Gilbert	247823	2022-01-21 10:37:08.372032+00	2022-01-21 10:37:08.372072+00	8	\N	\N	f	f
8428	PROJECT	Project	Travis Waldron	246817	2022-01-21 10:37:08.372162+00	2022-01-21 10:37:08.372202+00	8	\N	\N	f	f
8429	PROJECT	Project	Trebor Allen Candy	247824	2022-01-21 10:37:08.372291+00	2022-01-21 10:37:08.372329+00	8	\N	\N	f	f
8430	PROJECT	Project	Tredwell Lumber Holding Corp.	247825	2022-01-21 10:37:08.372421+00	2022-01-21 10:37:08.372461+00	8	\N	\N	f	f
8431	PROJECT	Project	Trent Barry	247826	2022-01-21 10:37:08.372552+00	2022-01-21 10:37:08.372592+00	8	\N	\N	f	f
8432	PROJECT	Project	Trenton Upwood Ltd	247827	2022-01-21 10:37:08.372685+00	2022-01-21 10:37:08.372724+00	8	\N	\N	f	f
8433	PROJECT	Project	TSM	247773	2022-01-21 10:37:08.372813+00	2022-01-21 10:37:08.372853+00	8	\N	\N	f	f
8434	PROJECT	Project	TST Solutions Inc	247774	2022-01-21 10:37:08.372944+00	2022-01-21 10:37:08.372984+00	8	\N	\N	f	f
8435	PROJECT	Project	TTS inc	247775	2022-01-21 10:37:08.373074+00	2022-01-21 10:37:08.373113+00	8	\N	\N	f	f
8436	PROJECT	Project	Tucson Apartments and Associates	247828	2022-01-21 10:37:08.373201+00	2022-01-21 10:37:08.37324+00	8	\N	\N	f	f
8437	PROJECT	Project	Turso Catering Agency	247829	2022-01-21 10:37:08.37333+00	2022-01-21 10:37:08.373369+00	8	\N	\N	f	f
8438	PROJECT	Project	Tuy and Sinha Construction Manufacturing	247830	2022-01-21 10:37:08.373459+00	2022-01-21 10:37:08.373498+00	8	\N	\N	f	f
8439	PROJECT	Project	TWC Financial	247776	2022-01-21 10:37:08.373588+00	2022-01-21 10:37:08.373628+00	8	\N	\N	f	f
8440	PROJECT	Project	Twigg Attorneys Company	247831	2022-01-21 10:37:08.373716+00	2022-01-21 10:37:08.373755+00	8	\N	\N	f	f
8441	PROJECT	Project	Twine Title Group	247832	2022-01-21 10:37:08.373842+00	2022-01-21 10:37:08.37388+00	8	\N	\N	f	f
8442	PROJECT	Project	Udoh Publishing Manufacturing	247834	2022-01-21 10:37:08.373967+00	2022-01-21 10:37:08.374005+00	8	\N	\N	f	f
8443	PROJECT	Project	ugkas	247933	2022-01-21 10:37:08.374093+00	2022-01-21 10:37:08.374131+00	8	\N	\N	f	f
8444	PROJECT	Project	Uimari Antiques Agency	247835	2022-01-21 10:37:08.374218+00	2022-01-21 10:37:08.374257+00	8	\N	\N	f	f
8445	PROJECT	Project	UK Customer	247833	2022-01-21 10:37:08.374344+00	2022-01-21 10:37:08.374382+00	8	\N	\N	f	f
8446	PROJECT	Project	Umali Publishing Distributors	247836	2022-01-21 10:37:08.374469+00	2022-01-21 10:37:08.374508+00	8	\N	\N	f	f
8447	PROJECT	Project	Umbrell Liquors Rentals	247837	2022-01-21 10:37:08.3746+00	2022-01-21 10:37:08.374639+00	8	\N	\N	f	f
8448	PROJECT	Project	Umeh Telecom Management	247838	2022-01-21 10:37:08.40803+00	2022-01-21 10:37:08.408082+00	8	\N	\N	f	f
8449	PROJECT	Project	Underdown Metal Fabricators and Associates	247839	2022-01-21 10:37:08.408164+00	2022-01-21 10:37:08.4082+00	8	\N	\N	f	f
8450	PROJECT	Project	Underwood New York	247840	2022-01-21 10:37:08.408276+00	2022-01-21 10:37:08.408308+00	8	\N	\N	f	f
8451	PROJECT	Project	Underwood Systems	247841	2022-01-21 10:37:08.408379+00	2022-01-21 10:37:08.40841+00	8	\N	\N	f	f
8452	PROJECT	Project	UniExchange	247842	2022-01-21 10:37:08.408476+00	2022-01-21 10:37:08.408507+00	8	\N	\N	f	f
8453	PROJECT	Project	Unnold Hospital Co.	247843	2022-01-21 10:37:08.408571+00	2022-01-21 10:37:08.408601+00	8	\N	\N	f	f
8454	PROJECT	Project	Upper 49th	247844	2022-01-21 10:37:08.408665+00	2022-01-21 10:37:08.408695+00	8	\N	\N	f	f
8455	PROJECT	Project	Ursery Publishing Group	247845	2022-01-21 10:37:08.408759+00	2022-01-21 10:37:08.408788+00	8	\N	\N	f	f
8456	PROJECT	Project	Urwin Leasing Group	247846	2022-01-21 10:37:08.408851+00	2022-01-21 10:37:08.40888+00	8	\N	\N	f	f
8457	PROJECT	Project	Valley Center Catering Leasing	247847	2022-01-21 10:37:08.408942+00	2022-01-21 10:37:08.415734+00	8	\N	\N	f	f
8458	PROJECT	Project	Vanaken Apartments Holding Corp.	247848	2022-01-21 10:37:08.415848+00	2022-01-21 10:37:08.415879+00	8	\N	\N	f	f
8459	PROJECT	Project	Vanasse Antiques Networking	247849	2022-01-21 10:37:08.415942+00	2022-01-21 10:37:08.415972+00	8	\N	\N	f	f
8460	PROJECT	Project	Vance Construction and Associates	247850	2022-01-21 10:37:08.416034+00	2022-01-21 10:37:08.416063+00	8	\N	\N	f	f
8461	PROJECT	Project	Vanwyngaarden Title Systems	247851	2022-01-21 10:37:08.416124+00	2022-01-21 10:37:08.416153+00	8	\N	\N	f	f
8462	PROJECT	Project	Vegas Tours	247852	2022-01-21 10:37:08.416214+00	2022-01-21 10:37:08.416244+00	8	\N	\N	f	f
8463	PROJECT	Project	Vellekamp Title Distributors	247853	2022-01-21 10:37:08.416304+00	2022-01-21 10:37:08.416334+00	8	\N	\N	f	f
8464	PROJECT	Project	Veradale Telecom Manufacturing	247854	2022-01-21 10:37:08.416394+00	2022-01-21 10:37:08.416424+00	8	\N	\N	f	f
8465	PROJECT	Project	Vermont Attorneys Company	247855	2022-01-21 10:37:08.416484+00	2022-01-21 10:37:08.416514+00	8	\N	\N	f	f
8466	PROJECT	Project	Verrelli Construction -	247856	2022-01-21 10:37:08.416574+00	2022-01-21 10:37:08.416603+00	8	\N	\N	f	f
8467	PROJECT	Project	Vertex	247857	2022-01-21 10:37:08.416664+00	2022-01-21 10:37:08.416694+00	8	\N	\N	f	f
8468	PROJECT	Project	Vessel Painting Holding Corp.	247858	2022-01-21 10:37:08.416753+00	2022-01-21 10:37:08.416783+00	8	\N	\N	f	f
8469	PROJECT	Project	Video Games by Dan	246818	2022-01-21 10:37:08.416843+00	2022-01-21 10:37:08.416872+00	8	\N	\N	f	f
8470	PROJECT	Project	Villanova Lumber Systems	247859	2022-01-21 10:37:08.416933+00	2022-01-21 10:37:08.416962+00	8	\N	\N	f	f
8471	PROJECT	Project	Virginia Beach Hospital Manufacturing	247860	2022-01-21 10:37:08.417022+00	2022-01-21 10:37:08.417051+00	8	\N	\N	f	f
8472	PROJECT	Project	Vista Lumber Agency	247861	2022-01-21 10:37:08.417112+00	2022-01-21 10:37:08.417141+00	8	\N	\N	f	f
8473	PROJECT	Project	Vivas Electric Sales	247862	2022-01-21 10:37:08.417202+00	2022-01-21 10:37:08.417231+00	8	\N	\N	f	f
8474	PROJECT	Project	Vodaphone	247863	2022-01-21 10:37:08.417292+00	2022-01-21 10:37:08.417321+00	8	\N	\N	f	f
8475	PROJECT	Project	Volden Publishing Systems	247864	2022-01-21 10:37:08.417382+00	2022-01-21 10:37:08.417412+00	8	\N	\N	f	f
8476	PROJECT	Project	Volmar Liquors and Associates	247865	2022-01-21 10:37:08.417472+00	2022-01-21 10:37:08.417501+00	8	\N	\N	f	f
8477	PROJECT	Project	Volmink Builders Inc.	247866	2022-01-21 10:37:08.417562+00	2022-01-21 10:37:08.417591+00	8	\N	\N	f	f
8478	PROJECT	Project	Wagenheim Painting and Associates	247867	2022-01-21 10:37:08.417651+00	2022-01-21 10:37:08.41768+00	8	\N	\N	f	f
8479	PROJECT	Project	Wahlers Lumber Management	247868	2022-01-21 10:37:08.417741+00	2022-01-21 10:37:08.41777+00	8	\N	\N	f	f
8480	PROJECT	Project	Wallace Printers	247869	2022-01-21 10:37:08.417831+00	2022-01-21 10:37:08.41786+00	8	\N	\N	f	f
8481	PROJECT	Project	Walter Martin	247870	2022-01-21 10:37:08.41792+00	2022-01-21 10:37:08.41795+00	8	\N	\N	f	f
8482	PROJECT	Project	Walters Production Company	247871	2022-01-21 10:37:08.41801+00	2022-01-21 10:37:08.418039+00	8	\N	\N	f	f
8483	PROJECT	Project	Wapp Hardware Sales	247872	2022-01-21 10:37:08.4181+00	2022-01-21 10:37:08.418129+00	8	\N	\N	f	f
8484	PROJECT	Project	Warnberg Automotive and Associates	247873	2022-01-21 10:37:08.418189+00	2022-01-21 10:37:08.418218+00	8	\N	\N	f	f
8485	PROJECT	Project	Warwick Lumber	247874	2022-01-21 10:37:08.418278+00	2022-01-21 10:37:08.418307+00	8	\N	\N	f	f
8486	PROJECT	Project	Wasager Wine Sales	247875	2022-01-21 10:37:08.418368+00	2022-01-21 10:37:08.418397+00	8	\N	\N	f	f
8487	PROJECT	Project	Wassenaar Construction Services	247876	2022-01-21 10:37:08.418457+00	2022-01-21 10:37:08.418486+00	8	\N	\N	f	f
8488	PROJECT	Project	Watertown Hicks	247877	2022-01-21 10:37:08.418547+00	2022-01-21 10:37:08.418783+00	8	\N	\N	f	f
8489	PROJECT	Project	Weare and Norvell Painting Co.	247878	2022-01-21 10:37:08.418887+00	2022-01-21 10:37:08.418917+00	8	\N	\N	f	f
8490	PROJECT	Project	Webmaster Gproxy	247879	2022-01-21 10:37:08.418978+00	2022-01-21 10:37:08.419007+00	8	\N	\N	f	f
8491	PROJECT	Project	Webster Electric	247880	2022-01-21 10:37:08.419067+00	2022-01-21 10:37:08.419096+00	8	\N	\N	f	f
8492	PROJECT	Project	Wedding Planning by Whitney	246819	2022-01-21 10:37:08.419156+00	2022-01-21 10:37:08.419185+00	8	\N	\N	f	f
8493	PROJECT	Project	Wedge Automotive Fabricators	247881	2022-01-21 10:37:08.419245+00	2022-01-21 10:37:08.419274+00	8	\N	\N	f	f
8494	PROJECT	Project	Weiskopf Consulting	246820	2022-01-21 10:37:08.419334+00	2022-01-21 10:37:08.419364+00	8	\N	\N	f	f
8495	PROJECT	Project	Wenatchee Builders Fabricators	247882	2022-01-21 10:37:08.419424+00	2022-01-21 10:37:08.419453+00	8	\N	\N	f	f
8496	PROJECT	Project	Wence Antiques Rentals	247883	2022-01-21 10:37:08.419513+00	2022-01-21 10:37:08.419542+00	8	\N	\N	f	f
8497	PROJECT	Project	Wendler Markets Leasing	247884	2022-01-21 10:37:08.419602+00	2022-01-21 10:37:08.419631+00	8	\N	\N	f	f
8498	PROJECT	Project	West Covina Builders Distributors	247885	2022-01-21 10:37:08.456866+00	2022-01-21 10:37:08.457486+00	8	\N	\N	f	f
8499	PROJECT	Project	Westminster Lumber Sales	247887	2022-01-21 10:37:08.45845+00	2022-01-21 10:37:08.459006+00	8	\N	\N	f	f
8500	PROJECT	Project	Westminster Lumber Sales 1	247888	2022-01-21 10:37:08.462729+00	2022-01-21 10:37:08.462931+00	8	\N	\N	f	f
8501	PROJECT	Project	West Palm Beach Painting Manufacturing	247886	2022-01-21 10:37:08.463085+00	2022-01-21 10:37:08.463127+00	8	\N	\N	f	f
8502	PROJECT	Project	Wethersfield Hardware Dynamics	247889	2022-01-21 10:37:08.46391+00	2022-01-21 10:37:08.463971+00	8	\N	\N	f	f
8503	PROJECT	Project	Wettlaufer Construction Systems	247890	2022-01-21 10:37:08.464065+00	2022-01-21 10:37:08.464104+00	8	\N	\N	f	f
8504	PROJECT	Project	Wever Apartments -	247891	2022-01-21 10:37:08.468432+00	2022-01-21 10:37:08.469216+00	8	\N	\N	f	f
8505	PROJECT	Project	Whetzell and Maymon Antiques Sales	247892	2022-01-21 10:37:08.469444+00	2022-01-21 10:37:08.469487+00	8	\N	\N	f	f
8506	PROJECT	Project	Whittier Hardware -	247893	2022-01-21 10:37:08.470054+00	2022-01-21 10:37:08.470097+00	8	\N	\N	f	f
8507	PROJECT	Project	Whole Oats Markets	247894	2022-01-21 10:37:08.470186+00	2022-01-21 10:37:08.470222+00	8	\N	\N	f	f
8508	PROJECT	Project	Wickenhauser Hardware Management	247895	2022-01-21 10:37:08.470288+00	2022-01-21 10:37:08.470318+00	8	\N	\N	f	f
8509	PROJECT	Project	Wicklund Leasing Corporation	247896	2022-01-21 10:37:08.470405+00	2022-01-21 10:37:08.47066+00	8	\N	\N	f	f
8510	PROJECT	Project	Wiesel Construction Dynamics	247897	2022-01-21 10:37:08.47076+00	2022-01-21 10:37:08.470798+00	8	\N	\N	f	f
8511	PROJECT	Project	Wiggles Inc.	247898	2022-01-21 10:37:08.470885+00	2022-01-21 10:37:08.470922+00	8	\N	\N	f	f
8512	PROJECT	Project	Wilkey Markets Group	247899	2022-01-21 10:37:08.471008+00	2022-01-21 10:37:08.471046+00	8	\N	\N	f	f
8513	PROJECT	Project	Williams Electronics and Communications	247901	2022-01-21 10:37:08.471131+00	2022-01-21 10:37:08.471169+00	8	\N	\N	f	f
8514	PROJECT	Project	Williams Wireless World	247902	2022-01-21 10:37:08.471256+00	2022-01-21 10:37:08.471293+00	8	\N	\N	f	f
8515	PROJECT	Project	Will's Leather Co.	247900	2022-01-21 10:37:08.47138+00	2022-01-21 10:37:08.471418+00	8	\N	\N	f	f
8516	PROJECT	Project	Wilner Liquors	247903	2022-01-21 10:37:08.471861+00	2022-01-21 10:37:08.471964+00	8	\N	\N	f	f
8517	PROJECT	Project	Wilson Kaplan	247904	2022-01-21 10:37:08.472354+00	2022-01-21 10:37:08.472441+00	8	\N	\N	f	f
8518	PROJECT	Project	Windisch Title Corporation	247905	2022-01-21 10:37:08.472722+00	2022-01-21 10:37:08.483823+00	8	\N	\N	f	f
8519	PROJECT	Project	Witten Antiques Services	247906	2022-01-21 10:37:08.484181+00	2022-01-21 10:37:08.484244+00	8	\N	\N	f	f
8520	PROJECT	Project	Wolfenden Markets Holding Corp.	247907	2022-01-21 10:37:08.484367+00	2022-01-21 10:37:08.484409+00	8	\N	\N	f	f
8521	PROJECT	Project	Wollan Software Rentals	247908	2022-01-21 10:37:08.484501+00	2022-01-21 10:37:08.484554+00	8	\N	\N	f	f
8522	PROJECT	Project	Wood-Mizer	247910	2022-01-21 10:37:08.484865+00	2022-01-21 10:37:08.484907+00	8	\N	\N	f	f
8523	PROJECT	Project	Woods Publishing Co.	247911	2022-01-21 10:37:08.484997+00	2022-01-21 10:37:08.485039+00	8	\N	\N	f	f
8524	PROJECT	Project	Wood Wonders Funiture	247909	2022-01-21 10:37:08.485128+00	2022-01-21 10:37:08.485166+00	8	\N	\N	f	f
8525	PROJECT	Project	Woon Hardware Networking	247912	2022-01-21 10:37:08.485255+00	2022-01-21 10:37:08.485294+00	8	\N	\N	f	f
8526	PROJECT	Project	Wraight Software and Associates	247913	2022-01-21 10:37:08.485382+00	2022-01-21 10:37:08.48542+00	8	\N	\N	f	f
8527	PROJECT	Project	X Eye Corp	247914	2022-01-21 10:37:08.485509+00	2022-01-21 10:37:08.485546+00	8	\N	\N	f	f
8528	PROJECT	Project	Yahl Markets Incorporated	247916	2022-01-21 10:37:08.485894+00	2022-01-21 10:37:08.485948+00	8	\N	\N	f	f
8529	PROJECT	Project	Yanity Apartments and Associates	247917	2022-01-21 10:37:08.486109+00	2022-01-21 10:37:08.486151+00	8	\N	\N	f	f
8530	PROJECT	Project	Yarnell Catering Holding Corp.	247918	2022-01-21 10:37:08.486259+00	2022-01-21 10:37:08.486294+00	8	\N	\N	f	f
8531	PROJECT	Project	Yockey Markets Inc.	247919	2022-01-21 10:37:08.486411+00	2022-01-21 10:37:08.486452+00	8	\N	\N	f	f
8532	PROJECT	Project	Yong Yi	247920	2022-01-21 10:37:08.487021+00	2022-01-21 10:37:08.487088+00	8	\N	\N	f	f
8533	PROJECT	Project	Y-Tec Manufacturing	247915	2022-01-21 10:37:08.487199+00	2022-01-21 10:37:08.487306+00	8	\N	\N	f	f
8534	PROJECT	Project	Yucca Valley Camping	247921	2022-01-21 10:37:08.487431+00	2022-01-21 10:37:08.487473+00	8	\N	\N	f	f
8535	PROJECT	Project	Yucca Valley Title Agency	247922	2022-01-21 10:37:08.487566+00	2022-01-21 10:37:08.487605+00	8	\N	\N	f	f
8536	PROJECT	Project	Zearfoss Windows Group	247923	2022-01-21 10:37:08.487694+00	2022-01-21 10:37:08.487866+00	8	\N	\N	f	f
8537	PROJECT	Project	Zechiel _ Management	247924	2022-01-21 10:37:08.487957+00	2022-01-21 10:37:08.487995+00	8	\N	\N	f	f
8538	PROJECT	Project	Zombro Telecom Leasing	247925	2022-01-21 10:37:08.488082+00	2022-01-21 10:37:08.48812+00	8	\N	\N	f	f
8539	PROJECT	Project	Zucca Electric Agency	247926	2022-01-21 10:37:08.488208+00	2022-01-21 10:37:08.488246+00	8	\N	\N	f	f
8540	PROJECT	Project	Zucconi Telecom Sales	247927	2022-01-21 10:37:08.48834+00	2022-01-21 10:37:08.488386+00	8	\N	\N	f	f
8541	PROJECT	Project	Zurasky Markets Dynamics	247928	2022-01-21 10:37:08.48848+00	2022-01-21 10:37:08.48852+00	8	\N	\N	f	f
8542	CLASS	Class	Adidas	expense_custom_field.class.1	2022-01-21 10:37:09.030314+00	2022-01-21 10:37:09.030691+00	8	\N	{"custom_field_id": 190717}	f	f
8543	CLASS	Class	cc1	expense_custom_field.class.2	2022-01-21 10:37:09.030916+00	2022-01-21 10:37:09.030965+00	8	\N	{"custom_field_id": 190717}	f	f
8544	CLASS	Class	cc2	expense_custom_field.class.3	2022-01-21 10:37:09.032143+00	2022-01-21 10:37:09.032203+00	8	\N	{"custom_field_id": 190717}	f	f
8545	CLASS	Class	Coachella	expense_custom_field.class.4	2022-01-21 10:37:09.033033+00	2022-01-21 10:37:09.033105+00	8	\N	{"custom_field_id": 190717}	f	f
8546	CLASS	Class	Radio	expense_custom_field.class.5	2022-01-21 10:37:09.033559+00	2022-01-21 10:37:09.033605+00	8	\N	{"custom_field_id": 190717}	f	f
8547	DEPARTMENTS	Departments	Bangalore	expense_custom_field.departments.1	2022-01-21 10:37:09.076211+00	2022-01-21 10:37:09.076293+00	8	\N	{"custom_field_id": 174997}	f	f
8548	DEPARTMENTS	Departments	San Fransisco	expense_custom_field.departments.2	2022-01-21 10:37:09.076665+00	2022-01-21 10:37:09.076716+00	8	\N	{"custom_field_id": 174997}	f	f
8549	KLASS	Klass	Small Business	expense_custom_field.klass.1	2022-01-21 10:37:09.104658+00	2022-01-21 10:37:09.104702+00	8	\N	{"custom_field_id": 196452}	f	f
8550	KLASS	Klass	Midsize Business	expense_custom_field.klass.2	2022-01-21 10:37:09.104777+00	2022-01-21 10:37:09.104807+00	8	\N	{"custom_field_id": 196452}	f	f
8551	KLASS	Klass	Enterprise	expense_custom_field.klass.3	2022-01-21 10:37:09.104878+00	2022-01-21 10:37:09.104908+00	8	\N	{"custom_field_id": 196452}	f	f
8552	KLASS	Klass	Service Line 2	expense_custom_field.klass.4	2022-01-21 10:37:09.104977+00	2022-01-21 10:37:09.105007+00	8	\N	{"custom_field_id": 196452}	f	f
8553	KLASS	Klass	Service Line 1	expense_custom_field.klass.5	2022-01-21 10:37:09.105076+00	2022-01-21 10:37:09.105105+00	8	\N	{"custom_field_id": 196452}	f	f
8554	KLASS	Klass	Service Line 3	expense_custom_field.klass.6	2022-01-21 10:37:09.105175+00	2022-01-21 10:37:09.105205+00	8	\N	{"custom_field_id": 196452}	f	f
8555	LOCATION	Location	USA 1	expense_custom_field.location.1	2022-01-21 10:37:09.169545+00	2022-01-21 10:37:09.169606+00	8	\N	{"custom_field_id": 845}	f	f
8556	LOCATION	Location	USA 2	expense_custom_field.location.2	2022-01-21 10:37:09.169755+00	2022-01-21 10:37:09.172815+00	8	\N	{"custom_field_id": 845}	f	f
8557	LOCATION	Location	Holding Company	expense_custom_field.location.3	2022-01-21 10:37:09.173405+00	2022-01-21 10:37:09.173476+00	8	\N	{"custom_field_id": 845}	f	f
8558	LOCATION	Location	Elimination - NA	expense_custom_field.location.4	2022-01-21 10:37:09.17366+00	2022-01-21 10:37:09.205478+00	8	\N	{"custom_field_id": 845}	f	f
8559	LOCATION	Location	Elimination - Global	expense_custom_field.location.5	2022-01-21 10:37:09.216052+00	2022-01-21 10:37:09.216123+00	8	\N	{"custom_field_id": 845}	f	f
8560	LOCATION	Location	India	expense_custom_field.location.6	2022-01-21 10:37:09.21627+00	2022-01-21 10:37:09.216311+00	8	\N	{"custom_field_id": 845}	f	f
8561	LOCATION	Location	Bangalore	expense_custom_field.location.7	2022-01-21 10:37:09.216418+00	2022-01-21 10:37:09.216461+00	8	\N	{"custom_field_id": 845}	f	f
8562	LOCATION	Location	Elimination - Sub	expense_custom_field.location.8	2022-01-21 10:37:09.216571+00	2022-01-21 10:37:09.216612+00	8	\N	{"custom_field_id": 845}	f	f
8563	LOCATION	Location	Canada	expense_custom_field.location.9	2022-01-21 10:37:09.216719+00	2022-01-21 10:37:09.216759+00	8	\N	{"custom_field_id": 845}	f	f
8564	LOCATION	Location	United Kingdom	expense_custom_field.location.10	2022-01-21 10:37:09.216867+00	2022-01-21 10:37:09.216907+00	8	\N	{"custom_field_id": 845}	f	f
8565	LOCATION	Location	London	expense_custom_field.location.11	2022-01-21 10:37:09.217014+00	2022-01-21 10:37:09.217053+00	8	\N	{"custom_field_id": 845}	f	f
8566	LOCATION	Location	Australia	expense_custom_field.location.12	2022-01-21 10:37:09.217156+00	2022-01-21 10:37:09.217196+00	8	\N	{"custom_field_id": 845}	f	f
8567	LOCATION	Location	New South Wales	expense_custom_field.location.13	2022-01-21 10:37:09.217299+00	2022-01-21 10:37:09.217337+00	8	\N	{"custom_field_id": 845}	f	f
8568	LOCATION	Location	South Africa	expense_custom_field.location.14	2022-01-21 10:37:09.217442+00	2022-01-21 10:37:09.217485+00	8	\N	{"custom_field_id": 845}	f	f
8569	LOCATION_ENTITY	Location Entity	USA1	expense_custom_field.location entity.1	2022-01-21 10:37:09.260188+00	2022-01-21 10:37:09.260268+00	8	\N	{"custom_field_id": 179638}	f	f
8570	LOCATION_ENTITY	Location Entity	USA2	expense_custom_field.location entity.2	2022-01-21 10:37:09.260466+00	2022-01-21 10:37:09.26051+00	8	\N	{"custom_field_id": 179638}	f	f
8571	LOCATION_ENTITY	Location Entity	USA3	expense_custom_field.location entity.3	2022-01-21 10:37:09.260596+00	2022-01-21 10:37:09.260831+00	8	\N	{"custom_field_id": 179638}	f	f
8572	LOCATION_ENTITY	Location Entity	India	expense_custom_field.location entity.4	2022-01-21 10:37:09.260935+00	2022-01-21 10:37:09.260965+00	8	\N	{"custom_field_id": 179638}	f	f
8573	OPERATING_SYSTEM	Operating System	USA1	expense_custom_field.operating system.1	2022-01-21 10:37:09.289629+00	2022-01-21 10:37:09.289672+00	8	\N	{"custom_field_id": 133433}	f	f
8574	OPERATING_SYSTEM	Operating System	USA2	expense_custom_field.operating system.2	2022-01-21 10:37:09.289747+00	2022-01-21 10:37:09.289777+00	8	\N	{"custom_field_id": 133433}	f	f
8575	OPERATING_SYSTEM	Operating System	USA3	expense_custom_field.operating system.3	2022-01-21 10:37:09.289848+00	2022-01-21 10:37:09.289877+00	8	\N	{"custom_field_id": 133433}	f	f
8576	OPERATING_SYSTEM	Operating System	India	expense_custom_field.operating system.4	2022-01-21 10:37:09.289947+00	2022-01-21 10:37:09.289976+00	8	\N	{"custom_field_id": 133433}	f	f
8577	SYSTEM_OPERATING	System Operating	BOOK	expense_custom_field.system operating.1	2022-01-21 10:37:09.317146+00	2022-01-21 10:37:09.317193+00	8	\N	{"custom_field_id": 174995}	f	f
8578	SYSTEM_OPERATING	System Operating	DevD	expense_custom_field.system operating.2	2022-01-21 10:37:09.317268+00	2022-01-21 10:37:09.317298+00	8	\N	{"custom_field_id": 174995}	f	f
8579	SYSTEM_OPERATING	System Operating	DevH	expense_custom_field.system operating.3	2022-01-21 10:37:09.31737+00	2022-01-21 10:37:09.3174+00	8	\N	{"custom_field_id": 174995}	f	f
8580	SYSTEM_OPERATING	System Operating	GB1-White	expense_custom_field.system operating.4	2022-01-21 10:37:09.31747+00	2022-01-21 10:37:09.317499+00	8	\N	{"custom_field_id": 174995}	f	f
8581	SYSTEM_OPERATING	System Operating	GB3-White	expense_custom_field.system operating.5	2022-01-21 10:37:09.317569+00	2022-01-21 10:37:09.317598+00	8	\N	{"custom_field_id": 174995}	f	f
8582	SYSTEM_OPERATING	System Operating	GB6-White	expense_custom_field.system operating.6	2022-01-21 10:37:09.317668+00	2022-01-21 10:37:09.317697+00	8	\N	{"custom_field_id": 174995}	f	f
8583	SYSTEM_OPERATING	System Operating	GB9-White	expense_custom_field.system operating.7	2022-01-21 10:37:09.317766+00	2022-01-21 10:37:09.317795+00	8	\N	{"custom_field_id": 174995}	f	f
8584	SYSTEM_OPERATING	System Operating	PMBr	expense_custom_field.system operating.8	2022-01-21 10:37:09.317865+00	2022-01-21 10:37:09.317894+00	8	\N	{"custom_field_id": 174995}	f	f
8585	SYSTEM_OPERATING	System Operating	PMD	expense_custom_field.system operating.9	2022-01-21 10:37:09.317964+00	2022-01-21 10:37:09.317993+00	8	\N	{"custom_field_id": 174995}	f	f
8586	SYSTEM_OPERATING	System Operating	PMDD	expense_custom_field.system operating.10	2022-01-21 10:37:09.318062+00	2022-01-21 10:37:09.318091+00	8	\N	{"custom_field_id": 174995}	f	f
8587	SYSTEM_OPERATING	System Operating	PMWe	expense_custom_field.system operating.11	2022-01-21 10:37:09.318161+00	2022-01-21 10:37:09.318394+00	8	\N	{"custom_field_id": 174995}	f	f
8588	SYSTEM_OPERATING	System Operating	Support-M	expense_custom_field.system operating.12	2022-01-21 10:37:09.318679+00	2022-01-21 10:37:09.318712+00	8	\N	{"custom_field_id": 174995}	f	f
8589	SYSTEM_OPERATING	System Operating	Train-MS	expense_custom_field.system operating.13	2022-01-21 10:37:09.318783+00	2022-01-21 10:37:09.318812+00	8	\N	{"custom_field_id": 174995}	f	f
8590	SYSTEM_OPERATING	System Operating	TSL - Black	expense_custom_field.system operating.14	2022-01-21 10:37:09.318881+00	2022-01-21 10:37:09.31891+00	8	\N	{"custom_field_id": 174995}	f	f
8591	SYSTEM_OPERATING	System Operating	TSM - Black	expense_custom_field.system operating.15	2022-01-21 10:37:09.31898+00	2022-01-21 10:37:09.319009+00	8	\N	{"custom_field_id": 174995}	f	f
8592	SYSTEM_OPERATING	System Operating	TSS - Black	expense_custom_field.system operating.16	2022-01-21 10:37:09.319078+00	2022-01-21 10:37:09.319121+00	8	\N	{"custom_field_id": 174995}	f	f
8593	TAX_GROUPS	Tax Groups	Tax 1	expense_custom_field.tax groups.1	2022-01-21 10:37:09.349846+00	2022-01-21 10:37:09.349888+00	8	\N	{"custom_field_id": 195201}	f	f
8594	TEAM	Team	CCC	expense_custom_field.team.1	2022-01-21 10:37:09.372854+00	2022-01-21 10:37:09.372899+00	8	\N	{"custom_field_id": 174175}	f	f
8595	TEAM	Team	Integrations	expense_custom_field.team.2	2022-01-21 10:37:09.372975+00	2022-01-21 10:37:09.373005+00	8	\N	{"custom_field_id": 174175}	f	f
8596	TEAM_2	Team 2	Eastside	expense_custom_field.team 2.1	2022-01-21 10:37:09.390088+00	2022-01-21 10:37:09.390132+00	8	\N	{"custom_field_id": 174994}	f	f
8597	TEAM_2	Team 2	North	expense_custom_field.team 2.2	2022-01-21 10:37:09.39021+00	2022-01-21 10:37:09.39024+00	8	\N	{"custom_field_id": 174994}	f	f
8598	TEAM_2	Team 2	South	expense_custom_field.team 2.3	2022-01-21 10:37:09.390313+00	2022-01-21 10:37:09.390343+00	8	\N	{"custom_field_id": 174994}	f	f
8599	TEAM_2	Team 2	West Coast	expense_custom_field.team 2.4	2022-01-21 10:37:09.390414+00	2022-01-21 10:37:09.390444+00	8	\N	{"custom_field_id": 174994}	f	f
8600	TEAM_COPY	Team Copy	Mobile App Redesign	expense_custom_field.team copy.1	2022-01-21 10:37:09.405671+00	2022-01-21 10:37:09.405714+00	8	\N	{"custom_field_id": 174993}	f	f
8601	TEAM_COPY	Team Copy	Platform APIs	expense_custom_field.team copy.2	2022-01-21 10:37:09.40579+00	2022-01-21 10:37:09.40582+00	8	\N	{"custom_field_id": 174993}	f	f
8602	TEAM_COPY	Team Copy	Fyle NetSuite Integration	expense_custom_field.team copy.3	2022-01-21 10:37:09.40589+00	2022-01-21 10:37:09.40592+00	8	\N	{"custom_field_id": 174993}	f	f
8603	TEAM_COPY	Team Copy	Fyle Sage Intacct Integration	expense_custom_field.team copy.4	2022-01-21 10:37:09.40599+00	2022-01-21 10:37:09.40602+00	8	\N	{"custom_field_id": 174993}	f	f
8604	TEAM_COPY	Team Copy	Support Taxes	expense_custom_field.team copy.5	2022-01-21 10:37:09.406089+00	2022-01-21 10:37:09.406119+00	8	\N	{"custom_field_id": 174993}	f	f
8605	TEAM_COPY	Team Copy	T&M Project with Five Tasks	expense_custom_field.team copy.6	2022-01-21 10:37:09.406188+00	2022-01-21 10:37:09.406217+00	8	\N	{"custom_field_id": 174993}	f	f
8606	TEAM_COPY	Team Copy	Fixed Fee Project with Five Tasks	expense_custom_field.team copy.7	2022-01-21 10:37:09.406286+00	2022-01-21 10:37:09.406315+00	8	\N	{"custom_field_id": 174993}	f	f
8607	TEAM_COPY	Team Copy	General Overhead	expense_custom_field.team copy.8	2022-01-21 10:37:09.406385+00	2022-01-21 10:37:09.406414+00	8	\N	{"custom_field_id": 174993}	f	f
8608	TEAM_COPY	Team Copy	General Overhead-Current	expense_custom_field.team copy.9	2022-01-21 10:37:09.406484+00	2022-01-21 10:37:09.406513+00	8	\N	{"custom_field_id": 174993}	f	f
8609	TEAM_COPY	Team Copy	Fyle Engineering	expense_custom_field.team copy.10	2022-01-21 10:37:09.406582+00	2022-01-21 10:37:09.406611+00	8	\N	{"custom_field_id": 174993}	f	f
8610	TEAM_COPY	Team Copy	Integrations	expense_custom_field.team copy.11	2022-01-21 10:37:09.406681+00	2022-01-21 10:37:09.40671+00	8	\N	{"custom_field_id": 174993}	f	f
8611	TEAM_COPY	Team Copy	labhvam	expense_custom_field.team copy.12	2022-01-21 10:37:09.406779+00	2022-01-21 10:37:09.406809+00	8	\N	{"custom_field_id": 174993}	f	f
8612	USER_DIMENSION	User Dimension	Admin	expense_custom_field.user dimension.1	2022-01-21 10:37:09.430833+00	2022-01-21 10:37:09.430946+00	8	\N	{"custom_field_id": 174176}	f	f
8613	USER_DIMENSION	User Dimension	Services	expense_custom_field.user dimension.2	2022-01-21 10:37:09.432215+00	2022-01-21 10:37:09.432284+00	8	\N	{"custom_field_id": 174176}	f	f
8614	USER_DIMENSION	User Dimension	Sales	expense_custom_field.user dimension.3	2022-01-21 10:37:09.432898+00	2022-01-21 10:37:09.432953+00	8	\N	{"custom_field_id": 174176}	f	f
8615	USER_DIMENSION	User Dimension	IT	expense_custom_field.user dimension.4	2022-01-21 10:37:09.433067+00	2022-01-21 10:37:09.433098+00	8	\N	{"custom_field_id": 174176}	f	f
8616	USER_DIMENSION	User Dimension	Marketing	expense_custom_field.user dimension.5	2022-01-21 10:37:09.433171+00	2022-01-21 10:37:09.433201+00	8	\N	{"custom_field_id": 174176}	f	f
8617	USER_DIMENSION_COPY	User Dimension Copy	Admin	expense_custom_field.user dimension copy.1	2022-01-21 10:37:09.451919+00	2022-01-21 10:37:09.452058+00	8	\N	{"custom_field_id": 174991}	f	f
8618	USER_DIMENSION_COPY	User Dimension Copy	Sales	expense_custom_field.user dimension copy.2	2022-01-21 10:37:09.452354+00	2022-01-21 10:37:09.452414+00	8	\N	{"custom_field_id": 174991}	f	f
8619	USER_DIMENSION_COPY	User Dimension Copy	Service	expense_custom_field.user dimension copy.3	2022-01-21 10:37:09.452595+00	2022-01-21 10:37:09.45265+00	8	\N	{"custom_field_id": 174991}	f	f
8620	USER_DIMENSION_COPY	User Dimension Copy	Marketing	expense_custom_field.user dimension copy.4	2022-01-21 10:37:09.45281+00	2022-01-21 10:37:09.452863+00	8	\N	{"custom_field_id": 174991}	f	f
8621	USER_DIMENSION_COPY	User Dimension Copy	Production	expense_custom_field.user dimension copy.5	2022-01-21 10:37:09.453496+00	2022-01-21 10:37:09.453576+00	8	\N	{"custom_field_id": 174991}	f	f
8622	USER_DIMENSION_COPY	User Dimension Copy	Machine Shop	expense_custom_field.user dimension copy.6	2022-01-21 10:37:09.453692+00	2022-01-21 10:37:09.453722+00	8	\N	{"custom_field_id": 174991}	f	f
8623	USER_DIMENSION_COPY	User Dimension Copy	Assembly	expense_custom_field.user dimension copy.7	2022-01-21 10:37:09.453796+00	2022-01-21 10:37:09.453826+00	8	\N	{"custom_field_id": 174991}	f	f
8624	USER_DIMENSION_COPY	User Dimension Copy	Inspection	expense_custom_field.user dimension copy.8	2022-01-21 10:37:09.453896+00	2022-01-21 10:37:09.453925+00	8	\N	{"custom_field_id": 174991}	f	f
8625	USER_DIMENSION_COPY	User Dimension Copy	Fabrication	expense_custom_field.user dimension copy.9	2022-01-21 10:37:09.453995+00	2022-01-21 10:37:09.454025+00	8	\N	{"custom_field_id": 174991}	f	f
8626	USER_DIMENSION_COPY	User Dimension Copy	Engineering	expense_custom_field.user dimension copy.10	2022-01-21 10:37:09.454095+00	2022-01-21 10:37:09.454125+00	8	\N	{"custom_field_id": 174991}	f	f
8627	USER_DIMENSION_COPY	User Dimension Copy	Product	expense_custom_field.user dimension copy.11	2022-01-21 10:37:09.454194+00	2022-01-21 10:37:09.454224+00	8	\N	{"custom_field_id": 174991}	f	f
8628	USER_DIMENSION_COPY	User Dimension Copy	Fyle	expense_custom_field.user dimension copy.12	2022-01-21 10:37:09.454293+00	2022-01-21 10:37:09.454323+00	8	\N	{"custom_field_id": 174991}	f	f
8629	TAX_GROUP	Tax Group	GST: NCF-AU @0.0%	tg09S3rMTTpo	2022-01-21 10:37:09.76704+00	2022-01-21 10:37:09.767092+00	8	\N	{"tax_rate": 0.0}	f	f
8630	TAX_GROUP	Tax Group	CGST	tg0fPRBFMZj7	2022-01-21 10:37:09.767234+00	2022-01-21 10:37:09.767279+00	8	\N	{"tax_rate": 0.5}	f	f
8631	TAX_GROUP	Tax Group	VAT: UNDEF-GB @0.0%	tg3Luhktgf4N	2022-01-21 10:37:09.768826+00	2022-01-21 10:37:09.768904+00	8	\N	{"tax_rate": 0.0}	f	f
8632	TAX_GROUP	Tax Group	GST: TFS-AU @0.0%	tg5uf1kTpljU	2022-01-21 10:37:09.769257+00	2022-01-21 10:37:09.769334+00	8	\N	{"tax_rate": 0.0}	f	f
8633	TAX_GROUP	Tax Group	GST-free non-capital - 0%	tg7ig0JL47TA	2022-01-21 10:37:09.769481+00	2022-01-21 10:37:09.769514+00	8	\N	{"tax_rate": 0.28}	f	f
8634	TAX_GROUP	Tax Group	Pant Tax @0%	tg7JTybZgV72	2022-01-21 10:37:09.770614+00	2022-01-21 10:37:09.771169+00	8	\N	{"tax_rate": 0.0}	f	f
8635	TAX_GROUP	Tax Group	GST on capital - 10%	tg8NsXbzhPL9	2022-01-21 10:37:09.775843+00	2022-01-21 10:37:09.775904+00	8	\N	{"tax_rate": 0.28}	f	f
8636	TAX_GROUP	Tax Group	ABN: dfvdfvf @20.0%	tgaj9yDnx3V7	2022-01-21 10:37:09.776024+00	2022-01-21 10:37:09.776066+00	8	\N	{"tax_rate": 0.2}	f	f
8637	TAX_GROUP	Tax Group	GST: ADJ-AU @0.0%	tgArJ1XJSvQ1	2022-01-21 10:37:09.776172+00	2022-01-21 10:37:09.776211+00	8	\N	{"tax_rate": 0.0}	f	f
8638	TAX_GROUP	Tax Group	Nilesh Tax @10%	tgB8tkI8kkOV	2022-01-21 10:37:09.776315+00	2022-01-21 10:37:09.776354+00	8	\N	{"tax_rate": 0.1}	f	f
8639	TAX_GROUP	Tax Group	GST on capital @0%	tgbyQDWdp4HT	2022-01-21 10:37:09.776457+00	2022-01-21 10:37:09.776495+00	8	\N	{"tax_rate": 0.0}	f	f
8640	TAX_GROUP	Tax Group	GST on non-capital @10%	tgbzwu7Cka9M	2022-01-21 10:37:09.776606+00	2022-01-21 10:37:09.77678+00	8	\N	{"tax_rate": 0.1}	f	f
8641	TAX_GROUP	Tax Group	GST-free capital @0%	tgCfp1fUBdlX	2022-01-21 10:37:09.776918+00	2022-01-21 10:37:09.776959+00	8	\N	{"tax_rate": 0}	f	f
8642	TAX_GROUP	Tax Group	GST: UNDEF-AU @0.0%	tgdDcmqveXjC	2022-01-21 10:37:09.777329+00	2022-01-21 10:37:09.779235+00	8	\N	{"tax_rate": 0.0}	f	f
8643	TAX_GROUP	Tax Group	GST on non-capital @0%	tgdIMfh7iBOY	2022-01-21 10:37:09.807516+00	2022-01-21 10:37:09.80774+00	8	\N	{"tax_rate": 0.0}	f	f
8644	TAX_GROUP	Tax Group	GST-free non-capital @0%	tgEru6wFHTM1	2022-01-21 10:37:09.807924+00	2022-01-21 10:37:09.808277+00	8	\N	{"tax_rate": 0}	f	f
8645	TAX_GROUP	Tax Group	GST: NA-AU @0.0%	tgf07hNu2f1L	2022-01-21 10:37:09.808478+00	2022-01-21 10:37:09.839862+00	8	\N	{"tax_rate": 0.0}	f	f
8646	TAX_GROUP	Tax Group	GST: EXPS-AU @0.0%	tgFQkkQOPT8i	2022-01-21 10:37:09.840117+00	2022-01-21 10:37:09.840177+00	8	\N	{"tax_rate": 0.0}	f	f
8647	TAX_GROUP	Tax Group	GST: NCI-AU @0.0%	tgG1mnAzZEit	2022-01-21 10:37:09.84035+00	2022-01-21 10:37:09.840398+00	8	\N	{"tax_rate": 0.0}	f	f
8648	TAX_GROUP	Tax Group	WET: WET-AU @29.0%	tggmh4xFPIrY	2022-01-21 10:37:09.840587+00	2022-01-21 10:37:09.841216+00	8	\N	{"tax_rate": 0.29}	f	f
8649	TAX_GROUP	Tax Group	GST-free capital - 0%	tggu76WXIdjY	2022-01-21 10:37:09.858794+00	2022-01-21 10:37:09.858891+00	8	\N	{"tax_rate": 0.28}	f	f
8650	TAX_GROUP	Tax Group	GST: CPI-AU @0.0%	tgHbN222yK8n	2022-01-21 10:37:09.859152+00	2022-01-21 10:37:09.859203+00	8	\N	{"tax_rate": 0.0}	f	f
8651	TAX_GROUP	Tax Group	GST: ITS-AU @0.0%	tgIyxnneqKm4	2022-01-21 10:37:09.859415+00	2022-01-21 10:37:09.859474+00	8	\N	{"tax_rate": 0.0}	f	f
8652	TAX_GROUP	Tax Group	GST: NCT-AU @10.0%	tgj97Eu6lEE3	2022-01-21 10:37:09.85975+00	2022-01-21 10:37:09.859796+00	8	\N	{"tax_rate": 0.1}	f	f
8653	TAX_GROUP	Tax Group	GST on non-capital - 10%	tgLgjZDkBHOX	2022-01-21 10:37:09.859953+00	2022-01-21 10:37:09.882828+00	8	\N	{"tax_rate": 0.28}	f	f
8654	TAX_GROUP	Tax Group	Nilesh Tax @0%	tglmrXAQ8A5f	2022-01-21 10:37:09.883062+00	2022-01-21 10:37:09.883111+00	8	\N	{"tax_rate": 0.0}	f	f
8655	TAX_GROUP	Tax Group	County: New York County @1.5%	tgn16RsBIa8O	2022-01-21 10:37:09.883298+00	2022-01-21 10:37:09.883357+00	8	\N	{"tax_rate": 0.01}	f	f
8656	TAX_GROUP	Tax Group	VAT	tgnci8BWh2e2	2022-01-21 10:37:09.884583+00	2022-01-21 10:37:09.88633+00	8	\N	{"tax_rate": 0.1}	f	f
8657	TAX_GROUP	Tax Group	GST: CPF-AU @0.0%	tgO8oQwXP01L	2022-01-21 10:37:09.886894+00	2022-01-21 10:37:09.886947+00	8	\N	{"tax_rate": 0.0}	f	f
8658	TAX_GROUP	Tax Group	VAT: UK Tax @10.0%	tgogXSf1onY0	2022-01-21 10:37:09.887088+00	2022-01-21 10:37:09.887882+00	8	\N	{"tax_rate": 0.1}	f	f
8659	TAX_GROUP	Tax Group	Input tax - 0%	tgP2csYPZYr1	2022-01-21 10:37:09.888141+00	2022-01-21 10:37:09.888308+00	8	\N	{"tax_rate": 0.28}	f	f
8660	TAX_GROUP	Tax Group	Pant Tax @20%	tgq2mKV86LWz	2022-01-21 10:37:09.888486+00	2022-01-21 10:37:09.888522+00	8	\N	{"tax_rate": 0.2}	f	f
8661	TAX_GROUP	Tax Group	GST: ashwin_tax_code_1 @2.0%	tgqpMNwVNkyv	2022-01-21 10:37:09.889804+00	2022-01-21 10:37:09.889881+00	8	\N	{"tax_rate": 0.02}	f	f
8662	TAX_GROUP	Tax Group	City: New York City @0.5%	tgrihEBRsqmk	2022-01-21 10:37:09.890135+00	2022-01-21 10:37:09.890183+00	8	\N	{"tax_rate": 0.01}	f	f
8663	TAX_GROUP	Tax Group	ABN: Nilesh @54.0%	tgRPkX7ymV2K	2022-01-21 10:37:09.890356+00	2022-01-21 10:37:09.890403+00	8	\N	{"tax_rate": 0.54}	f	f
8664	TAX_GROUP	Tax Group	GST: CPT-AU @10.0%	tgrSg9F7Y9sK	2022-01-21 10:37:09.89057+00	2022-01-21 10:37:09.895663+00	8	\N	{"tax_rate": 0.1}	f	f
8665	TAX_GROUP	Tax Group	ABN: Ashwin Tax Group @6.0%	tgrVpyLhsOsw	2022-01-21 10:37:09.909458+00	2022-01-21 10:37:09.90953+00	8	\N	{"tax_rate": 0.06}	f	f
8666	TAX_GROUP	Tax Group	LCT: LCT-AU @25.0%	tgupeKzRMBhH	2022-01-21 10:37:09.910358+00	2022-01-21 10:37:09.910432+00	8	\N	{"tax_rate": 0.25}	f	f
8667	TAX_GROUP	Tax Group	GST on capital @10%	tgVlVvok652A	2022-01-21 10:37:09.910971+00	2022-01-21 10:37:09.911938+00	8	\N	{"tax_rate": 0.1}	f	f
8668	TAX_GROUP	Tax Group	GST: ashwin_tax_code_2 @4.0%	tgwYo6RC8qsA	2022-01-21 10:37:09.912878+00	2022-01-21 10:37:09.91312+00	8	\N	{"tax_rate": 0.04}	f	f
8669	TAX_GROUP	Tax Group	State: New York State @6.5%	tgXqTTjgvNhW	2022-01-21 10:37:09.914004+00	2022-01-21 10:37:09.914136+00	8	\N	{"tax_rate": 0.07}	f	f
8670	TAX_GROUP	Tax Group	GST	tgXueCemFa6Q	2022-01-21 10:37:09.915053+00	2022-01-21 10:37:09.915472+00	8	\N	{"tax_rate": 0.18}	f	f
8671	TAX_GROUP	Tax Group	Pant Tax - 10%	tgy17771Fs0Z	2022-01-21 10:37:09.916188+00	2022-01-21 10:37:09.916264+00	8	\N	{"tax_rate": 0.28}	f	f
8672	TAX_GROUP	Tax Group	GST: TS-AU @10.0%	tgYJqx59P3t3	2022-01-21 10:37:09.917057+00	2022-01-21 10:37:09.917128+00	8	\N	{"tax_rate": 0.1}	f	f
8673	TAX_GROUP	Tax Group	Other 2 Sales Tax: GST @18.0%	tgYw6DkCzssM	2022-01-21 10:37:09.917456+00	2022-01-21 10:37:09.917786+00	8	\N	{"tax_rate": 0.18}	f	f
8674	TAX_GROUP	Tax Group	Input tax @0%	tgZCQgT9K0Fk	2022-01-21 10:37:09.919136+00	2022-01-21 10:37:09.921002+00	8	\N	{"tax_rate": 0}	f	f
8675	TAX_GROUP	Tax Group	Nilesh Tax - 10%	tgzVoKWXqWFB	2022-01-21 10:37:09.921142+00	2022-01-21 10:37:09.921168+00	8	\N	{"tax_rate": 0.28}	f	f
6968	EMPLOYEE	Employee	ashwin.t@fyle.in	ouVLOYP8lelN	2022-01-21 10:37:00.798282+00	2022-01-21 10:40:24.895325+00	8	\N	{"location": null, "full_name": "Ashwin", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
8676	EMPLOYEE	Employee	approver1@fyleforbill.cct	ouKBSnowXnxN	2022-01-21 10:42:20.693021+00	2022-01-21 10:42:20.69312+00	9	\N	{"location": null, "full_name": "Ryan Gallagher", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
8677	EMPLOYEE	Employee	owner@fyleforbill.cct	ouibj2LLdUmE	2022-01-21 10:42:20.693359+00	2022-01-21 10:42:20.693386+00	9	\N	{"location": null, "full_name": "Fyle For Intacct Bill-CCT", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
8678	EMPLOYEE	Employee	admin1@fyleforbill.cct	ouf3eOiWkaj1	2022-01-21 10:42:20.693458+00	2022-01-21 10:42:20.693485+00	9	\N	{"location": null, "full_name": "Theresa Brown", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
8679	EMPLOYEE	Employee	user10@fyleforbill.cct	ou40CAgM24WM	2022-01-21 10:42:20.693546+00	2022-01-21 10:42:20.693569+00	9	\N	{"location": null, "full_name": "Matthew Estrada", "department": "Department 2", "department_id": "deptUxQWUo5I4Z", "employee_code": null, "department_code": null}	f	f
8680	EMPLOYEE	Employee	user1@fyleforbill.cct	ouqpOdAQ9Ciq	2022-01-21 10:42:20.693642+00	2022-01-21 10:42:20.693672+00	9	\N	{"location": null, "full_name": "Joshua Wood", "department": "Department 3", "department_id": "depthXWVUDPbx2", "employee_code": null, "department_code": null}	f	f
8681	EMPLOYEE	Employee	user2@fyleforbill.cct	oueTfWeSMBXB	2022-01-21 10:42:20.69377+00	2022-01-21 10:42:20.693824+00	9	\N	{"location": null, "full_name": "Brian Foster", "department": "Department 2", "department_id": "deptUxQWUo5I4Z", "employee_code": null, "department_code": null}	f	f
8682	EMPLOYEE	Employee	user3@fyleforbill.cct	ouYsk56gFlSp	2022-01-21 10:42:20.693961+00	2022-01-21 10:42:20.694011+00	9	\N	{"location": null, "full_name": "Natalie Pope", "department": "Department 3", "department_id": "depthXWVUDPbx2", "employee_code": null, "department_code": null}	f	f
8683	EMPLOYEE	Employee	user4@fyleforbill.cct	ouo6vtsZ2Gg7	2022-01-21 10:42:20.694151+00	2022-01-21 10:42:20.6942+00	9	\N	{"location": null, "full_name": "Samantha Washington", "department": "Department 3", "department_id": "depthXWVUDPbx2", "employee_code": null, "department_code": null}	f	f
8684	EMPLOYEE	Employee	user5@fyleforbill.cct	oupBs6p0nMs2	2022-01-21 10:42:20.694395+00	2022-01-21 10:42:20.694441+00	9	\N	{"location": null, "full_name": "Chris Curtis", "department": "Department 2", "department_id": "deptUxQWUo5I4Z", "employee_code": null, "department_code": null}	f	f
8685	EMPLOYEE	Employee	user6@fyleforbill.cct	ouGE4NDpYh1R	2022-01-21 10:42:20.694569+00	2022-01-21 10:42:20.694622+00	9	\N	{"location": null, "full_name": "Victor Martinez", "department": "Department 1", "department_id": "dept2i0V5eKfV4", "employee_code": null, "department_code": null}	f	f
8686	EMPLOYEE	Employee	user7@fyleforbill.cct	ouxEY1eU72HD	2022-01-21 10:42:20.694767+00	2022-01-21 10:42:20.694807+00	9	\N	{"location": null, "full_name": "James Taylor", "department": "Department 2", "department_id": "deptUxQWUo5I4Z", "employee_code": null, "department_code": null}	f	f
8687	EMPLOYEE	Employee	user8@fyleforbill.cct	ouhVFXcYcGNb	2022-01-21 10:42:20.694882+00	2022-01-21 10:42:20.694911+00	9	\N	{"location": null, "full_name": "Jessica Lane", "department": "Department 1", "department_id": "dept2i0V5eKfV4", "employee_code": null, "department_code": null}	f	f
8688	EMPLOYEE	Employee	user9@fyleforbill.cct	ouaYCLXE3mdl	2022-01-21 10:42:20.694982+00	2022-01-21 10:42:20.695011+00	9	\N	{"location": null, "full_name": "Justin Glass", "department": "Department 3", "department_id": "depthXWVUDPbx2", "employee_code": null, "department_code": null}	f	f
12209	CORPORATE_CARD	Corporate Card	BANK OF INDIA - 219874	baccxoXQr0p2kj	2022-02-01 07:50:24.756246+00	2022-02-01 07:50:24.75642+00	8	\N	{"cardholder_name": null}	f	f
8690	EMPLOYEE	Employee	nilesh.p+1@fyle.in	ouyHH5kNYhzK	2022-01-21 10:42:20.695183+00	2022-01-21 10:42:20.695212+00	9	\N	{"location": null, "full_name": "Dwayne Jhonson", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
8691	CATEGORY	Category	121 payment processing	160956	2022-01-21 10:42:22.263906+00	2022-01-21 10:42:22.263974+00	9	\N	\N	f	f
8692	CATEGORY	Category	130fre	161193	2022-01-21 10:42:22.264379+00	2022-01-21 10:42:22.264476+00	9	\N	\N	f	f
8693	CATEGORY	Category	ABN Withholding	147766	2022-01-21 10:42:22.264612+00	2022-01-21 10:42:22.264647+00	9	\N	\N	f	f
8694	CATEGORY	Category	Accm.Depr. Furniture & Fixtures	142193	2022-01-21 10:42:22.264756+00	2022-01-21 10:42:22.264798+00	9	\N	\N	f	f
8695	CATEGORY	Category	Accounting	147272	2022-01-21 10:42:22.2649+00	2022-01-21 10:42:22.264939+00	9	\N	\N	f	f
8696	CATEGORY	Category	Accounts Payable	142227	2022-01-21 10:42:22.265038+00	2022-01-21 10:42:22.265077+00	9	\N	\N	f	f
8697	CATEGORY	Category	Accounts Payable - Employees	142226	2022-01-21 10:42:22.265178+00	2022-01-21 10:42:22.265221+00	9	\N	\N	f	f
8698	CATEGORY	Category	Accounts Receivable	142224	2022-01-21 10:42:22.266019+00	2022-01-21 10:42:22.266094+00	9	\N	\N	f	f
8699	CATEGORY	Category	Accounts Receivable - Other	142225	2022-01-21 10:42:22.266236+00	2022-01-21 10:42:22.266282+00	9	\N	\N	f	f
8700	CATEGORY	Category	Accr. Sales Tax Payable	154780	2022-01-21 10:42:22.266576+00	2022-01-21 10:42:22.27563+00	9	\N	\N	f	f
8701	CATEGORY	Category	Accrued Expense	154778	2022-01-21 10:42:22.276695+00	2022-01-21 10:42:22.277504+00	9	\N	\N	f	f
8702	CATEGORY	Category	Accrued Payroll Tax Payable	142154	2022-01-21 10:42:22.277663+00	2022-01-21 10:42:22.277715+00	9	\N	\N	f	f
8703	CATEGORY	Category	Accrued Sales Tax Payable	142155	2022-01-21 10:42:22.277908+00	2022-01-21 10:42:22.277953+00	9	\N	\N	f	f
8704	CATEGORY	Category	Accumulated OCI	142203	2022-01-21 10:42:22.327011+00	2022-01-21 10:42:22.327104+00	9	\N	\N	f	f
8705	CATEGORY	Category	Activity	142030	2022-01-21 10:42:22.327491+00	2022-01-21 10:42:22.327643+00	9	\N	\N	f	f
8706	CATEGORY	Category	Actual Landed Costs	142153	2022-01-21 10:42:22.32955+00	2022-01-21 10:42:22.329622+00	9	\N	\N	f	f
8707	CATEGORY	Category	Advances Paid	147268	2022-01-21 10:42:22.32976+00	2022-01-21 10:42:22.329864+00	9	\N	\N	f	f
8708	CATEGORY	Category	Advertising	145043	2022-01-21 10:42:22.330099+00	2022-01-21 10:42:22.330156+00	9	\N	\N	f	f
8709	CATEGORY	Category	Airfare	143131	2022-01-21 10:42:22.330286+00	2022-01-21 10:42:22.330331+00	9	\N	\N	f	f
8710	CATEGORY	Category	Allocations	142218	2022-01-21 10:42:22.330464+00	2022-01-21 10:42:22.330516+00	9	\N	\N	f	f
8711	CATEGORY	Category	Allowance For Doubtful Accounts	142145	2022-01-21 10:42:22.330651+00	2022-01-21 10:42:22.330699+00	9	\N	\N	f	f
8712	CATEGORY	Category	Amortisation (and depreciation) expense	147516	2022-01-21 10:42:22.330829+00	2022-01-21 10:42:22.330872+00	9	\N	\N	f	f
8713	CATEGORY	Category	Amortization Expense	142204	2022-01-21 10:42:22.330975+00	2022-01-21 10:42:22.331016+00	9	\N	\N	f	f
8714	CATEGORY	Category	AR - Retainage	154832	2022-01-21 10:42:22.331115+00	2022-01-21 10:42:22.331155+00	9	\N	\N	f	f
8715	CATEGORY	Category	AR-Retainage	142223	2022-01-21 10:42:22.331252+00	2022-01-21 10:42:22.331292+00	9	\N	\N	f	f
8716	CATEGORY	Category	ash	147304	2022-01-21 10:42:22.331388+00	2022-01-21 10:42:22.33143+00	9	\N	\N	f	f
8717	CATEGORY	Category	ASHWIN MANUALLY ADDED THIS	142230	2022-01-21 10:42:22.331529+00	2022-01-21 10:42:22.331569+00	9	\N	\N	f	f
8718	CATEGORY	Category	ASHWIN MANUALLY ADDED THIS2	142231	2022-01-21 10:42:22.331671+00	2022-01-21 10:42:22.33171+00	9	\N	\N	f	f
8719	CATEGORY	Category	Aus Category	153957	2022-01-21 10:42:22.331812+00	2022-01-21 10:42:22.331852+00	9	\N	\N	f	f
8720	CATEGORY	Category	Automobile	145044	2022-01-21 10:42:22.331947+00	2022-01-21 10:42:22.331987+00	9	\N	\N	f	f
8721	CATEGORY	Category	Automobile Expense	147238	2022-01-21 10:42:22.332088+00	2022-01-21 10:42:22.332134+00	9	\N	\N	f	f
8722	CATEGORY	Category	Automobile:Fuel	145045	2022-01-21 10:42:22.332243+00	2022-01-21 10:42:22.332277+00	9	\N	\N	f	f
8723	CATEGORY	Category	Bad Debt Expense	142156	2022-01-21 10:42:22.332384+00	2022-01-21 10:42:22.33243+00	9	\N	\N	f	f
8724	CATEGORY	Category	Bad debts	147517	2022-01-21 10:42:22.332549+00	2022-01-21 10:42:22.332589+00	9	\N	\N	f	f
8725	CATEGORY	Category	Bank Charges	142128	2022-01-21 10:42:22.332678+00	2022-01-21 10:42:22.332714+00	9	\N	\N	f	f
8726	CATEGORY	Category	Bank Service Charges	147241	2022-01-21 10:42:22.332801+00	2022-01-21 10:42:22.332837+00	9	\N	\N	f	f
8727	CATEGORY	Category	BAS Expense	147519	2022-01-21 10:42:22.332924+00	2022-01-21 10:42:22.33296+00	9	\N	\N	f	f
8728	CATEGORY	Category	Billable Hours	154835	2022-01-21 10:42:22.333046+00	2022-01-21 10:42:22.333083+00	9	\N	\N	f	f
8729	CATEGORY	Category	Billable Overtime Hours	154833	2022-01-21 10:42:22.333168+00	2022-01-21 10:42:22.333205+00	9	\N	\N	f	f
8730	CATEGORY	Category	Bill Exchange Rate Variance	147281	2022-01-21 10:42:22.33329+00	2022-01-21 10:42:22.333326+00	9	\N	\N	f	f
8731	CATEGORY	Category	Bill Price Variance	147280	2022-01-21 10:42:22.333411+00	2022-01-21 10:42:22.333447+00	9	\N	\N	f	f
8732	CATEGORY	Category	Bill Quantity Variance	147279	2022-01-21 10:42:22.333532+00	2022-01-21 10:42:22.333568+00	9	\N	\N	f	f
8733	CATEGORY	Category	Buildings	142188	2022-01-21 10:42:22.333653+00	2022-01-21 10:42:22.33369+00	9	\N	\N	f	f
8734	CATEGORY	Category	Buildings Accm. Depr.	154807	2022-01-21 10:42:22.333775+00	2022-01-21 10:42:22.333811+00	9	\N	\N	f	f
8735	CATEGORY	Category	Buildings Accm.Depr.	142189	2022-01-21 10:42:22.333896+00	2022-01-21 10:42:22.333932+00	9	\N	\N	f	f
8736	CATEGORY	Category	Build Price Variance	147292	2022-01-21 10:42:22.334018+00	2022-01-21 10:42:22.334053+00	9	\N	\N	f	f
8737	CATEGORY	Category	Build Quantity Variance	147293	2022-01-21 10:42:22.334139+00	2022-01-21 10:42:22.334175+00	9	\N	\N	f	f
8738	CATEGORY	Category	Bus	142041	2022-01-21 10:42:22.334266+00	2022-01-21 10:42:22.334638+00	9	\N	\N	f	f
8739	CATEGORY	Category	Business	147258	2022-01-21 10:42:22.350105+00	2022-01-21 10:42:22.350153+00	9	\N	\N	f	f
8740	CATEGORY	Category	Business Expense	160438	2022-01-21 10:42:22.350223+00	2022-01-21 10:42:22.350253+00	9	\N	\N	f	f
8741	CATEGORY	Category	Business Licenses and Permits	154543	2022-01-21 10:42:22.38116+00	2022-01-21 10:42:22.381223+00	9	\N	\N	f	f
8742	CATEGORY	Category	Capitalized Software Costs	142187	2022-01-21 10:42:22.381341+00	2022-01-21 10:42:22.381388+00	9	\N	\N	f	f
8743	CATEGORY	Category	Cash	142180	2022-01-21 10:42:22.381498+00	2022-01-21 10:42:22.38154+00	9	\N	\N	f	f
8744	CATEGORY	Category	Cash Equivalents	142181	2022-01-21 10:42:22.381642+00	2022-01-21 10:42:22.381683+00	9	\N	\N	f	f
8745	CATEGORY	Category	Cell phone	145132	2022-01-21 10:42:22.381787+00	2022-01-21 10:42:22.381843+00	9	\N	\N	f	f
8746	CATEGORY	Category	Cellular	147264	2022-01-21 10:42:22.382131+00	2022-01-21 10:42:22.382181+00	9	\N	\N	f	f
8747	CATEGORY	Category	Cellular Phone	143127	2022-01-21 10:42:22.382288+00	2022-01-21 10:42:22.38233+00	9	\N	\N	f	f
8748	CATEGORY	Category	Charitable Contributions	154544	2022-01-21 10:42:22.382433+00	2022-01-21 10:42:22.382662+00	9	\N	\N	f	f
8749	CATEGORY	Category	Checking	163335	2022-01-21 10:42:22.382777+00	2022-01-21 10:42:22.382819+00	9	\N	\N	f	f
8750	CATEGORY	Category	Checking 1 - SVB	154791	2022-01-21 10:42:22.382923+00	2022-01-21 10:42:22.382966+00	9	\N	\N	f	f
8751	CATEGORY	Category	Checking 2 - SVB	154792	2022-01-21 10:42:22.383069+00	2022-01-21 10:42:22.383111+00	9	\N	\N	f	f
8752	CATEGORY	Category	Checking 3 - SVB	154793	2022-01-21 10:42:22.383223+00	2022-01-21 10:42:22.383266+00	9	\N	\N	f	f
8753	CATEGORY	Category	Checking 4 - Bank Of Canada	154787	2022-01-21 10:42:22.383368+00	2022-01-21 10:42:22.383411+00	9	\N	\N	f	f
8754	CATEGORY	Category	Checking 5 - Bank Of England	154788	2022-01-21 10:42:22.383512+00	2022-01-21 10:42:22.383553+00	9	\N	\N	f	f
8755	CATEGORY	Category	Checking 6 - Bank Of Australia	154789	2022-01-21 10:42:22.383663+00	2022-01-21 10:42:22.383703+00	9	\N	\N	f	f
8756	CATEGORY	Category	Checking 7 - Bank Of South Africa	154790	2022-01-21 10:42:22.383804+00	2022-01-21 10:42:22.383866+00	9	\N	\N	f	f
8757	CATEGORY	Category	CMRR Add-On	154847	2022-01-21 10:42:22.384149+00	2022-01-21 10:42:22.384183+00	9	\N	\N	f	f
8758	CATEGORY	Category	CMRR Churn	154850	2022-01-21 10:42:22.384252+00	2022-01-21 10:42:22.384514+00	9	\N	\N	f	f
8759	CATEGORY	Category	CMRR New	154846	2022-01-21 10:42:22.38471+00	2022-01-21 10:42:22.384746+00	9	\N	\N	f	f
8760	CATEGORY	Category	CMRR Offset	154845	2022-01-21 10:42:22.384873+00	2022-01-21 10:42:22.38492+00	9	\N	\N	f	f
8761	CATEGORY	Category	CMRR Renewal	154851	2022-01-21 10:42:22.390013+00	2022-01-21 10:42:22.394283+00	9	\N	\N	f	f
8762	CATEGORY	Category	COGS-Billable Hours	142135	2022-01-21 10:42:22.394446+00	2022-01-21 10:42:22.394488+00	9	\N	\N	f	f
8763	CATEGORY	Category	COGS - Burden on Projects	154837	2022-01-21 10:42:22.394584+00	2022-01-21 10:42:22.394624+00	9	\N	\N	f	f
8764	CATEGORY	Category	COGS-Burden on Projects	142139	2022-01-21 10:42:22.394719+00	2022-01-21 10:42:22.394758+00	9	\N	\N	f	f
8765	CATEGORY	Category	COGS-Damage, Scrap, Spoilage	142217	2022-01-21 10:42:22.394852+00	2022-01-21 10:42:22.394892+00	9	\N	\N	f	f
8766	CATEGORY	Category	COGS - G&A on Projects	154839	2022-01-21 10:42:22.394988+00	2022-01-21 10:42:22.395029+00	9	\N	\N	f	f
8767	CATEGORY	Category	COGS-G&A on Projects	142141	2022-01-21 10:42:22.395122+00	2022-01-21 10:42:22.395172+00	9	\N	\N	f	f
8911	CATEGORY	Category	Inventory	142207	2022-01-21 10:42:22.832409+00	2022-01-21 10:42:22.832438+00	9	\N	\N	f	f
8768	CATEGORY	Category	COGS-Indirect projects Costs Offset	142142	2022-01-21 10:42:22.395275+00	2022-01-21 10:42:22.395309+00	9	\N	\N	f	f
8769	CATEGORY	Category	COGS - Indirect Projects Costs Offset	154840	2022-01-21 10:42:22.395413+00	2022-01-21 10:42:22.395458+00	9	\N	\N	f	f
8770	CATEGORY	Category	COGS - Materials	154826	2022-01-21 10:42:22.395648+00	2022-01-21 10:42:22.395678+00	9	\N	\N	f	f
8771	CATEGORY	Category	COGS-Non-Billable Hours	142138	2022-01-21 10:42:22.39574+00	2022-01-21 10:42:22.39577+00	9	\N	\N	f	f
8772	CATEGORY	Category	COGS - Other	154777	2022-01-21 10:42:22.395832+00	2022-01-21 10:42:22.395861+00	9	\N	\N	f	f
8773	CATEGORY	Category	COGS-Other	142144	2022-01-21 10:42:22.395922+00	2022-01-21 10:42:22.395951+00	9	\N	\N	f	f
8774	CATEGORY	Category	COGS - Overhead on Projects	154838	2022-01-21 10:42:22.396012+00	2022-01-21 10:42:22.396042+00	9	\N	\N	f	f
8775	CATEGORY	Category	COGS-Overhead on Projects	142140	2022-01-21 10:42:22.396102+00	2022-01-21 10:42:22.396131+00	9	\N	\N	f	f
8776	CATEGORY	Category	COGS - Reimbursed Expenses	154841	2022-01-21 10:42:22.396193+00	2022-01-21 10:42:22.396222+00	9	\N	\N	f	f
8777	CATEGORY	Category	COGS-Reimbursed Expenses	142143	2022-01-21 10:42:22.396284+00	2022-01-21 10:42:22.396313+00	9	\N	\N	f	f
8778	CATEGORY	Category	COGS Sales	142216	2022-01-21 10:42:22.396374+00	2022-01-21 10:42:22.396403+00	9	\N	\N	f	f
8779	CATEGORY	Category	COGS - Sales	154758	2022-01-21 10:42:22.396465+00	2022-01-21 10:42:22.396494+00	9	\N	\N	f	f
8780	CATEGORY	Category	COGS Services	142133	2022-01-21 10:42:22.396555+00	2022-01-21 10:42:22.396584+00	9	\N	\N	f	f
8781	CATEGORY	Category	COGS - Subcontractors	154759	2022-01-21 10:42:22.396645+00	2022-01-21 10:42:22.396674+00	9	\N	\N	f	f
8782	CATEGORY	Category	Commission	142130	2022-01-21 10:42:22.396735+00	2022-01-21 10:42:22.396765+00	9	\N	\N	f	f
8783	CATEGORY	Category	Commissions and fees	147520	2022-01-21 10:42:22.396826+00	2022-01-21 10:42:22.396855+00	9	\N	\N	f	f
8784	CATEGORY	Category	Commissions & fees	145046	2022-01-21 10:42:22.396917+00	2022-01-21 10:42:22.396946+00	9	\N	\N	f	f
8785	CATEGORY	Category	Common Stock	142213	2022-01-21 10:42:22.397007+00	2022-01-21 10:42:22.397036+00	9	\N	\N	f	f
8786	CATEGORY	Category	Communication Expense - Fixed	147521	2022-01-21 10:42:22.397097+00	2022-01-21 10:42:22.397126+00	9	\N	\N	f	f
8787	CATEGORY	Category	Company Credit Card Offset	142158	2022-01-21 10:42:22.397188+00	2022-01-21 10:42:22.397217+00	9	\N	\N	f	f
8788	CATEGORY	Category	Computer and Internet Expenses	154545	2022-01-21 10:42:22.397278+00	2022-01-21 10:42:22.397307+00	9	\N	\N	f	f
8789	CATEGORY	Category	Continuing Education	154546	2022-01-21 10:42:22.397369+00	2022-01-21 10:42:22.397398+00	9	\N	\N	f	f
8790	CATEGORY	Category	Contract Commission	154844	2022-01-21 10:42:22.39746+00	2022-01-21 10:42:22.397803+00	9	\N	\N	f	f
8791	CATEGORY	Category	Contract Royalty Expense	154843	2022-01-21 10:42:22.411852+00	2022-01-21 10:42:22.411894+00	9	\N	\N	f	f
8792	CATEGORY	Category	Contract Services	154774	2022-01-21 10:42:22.41196+00	2022-01-21 10:42:22.41199+00	9	\N	\N	f	f
8793	CATEGORY	Category	Contract Services - Billed	154769	2022-01-21 10:42:22.412053+00	2022-01-21 10:42:22.412082+00	9	\N	\N	f	f
8794	CATEGORY	Category	Contract Services - Paid	154772	2022-01-21 10:42:22.412143+00	2022-01-21 10:42:22.412173+00	9	\N	\N	f	f
8795	CATEGORY	Category	Contract Services - Unbilled	154775	2022-01-21 10:42:22.412234+00	2022-01-21 10:42:22.412264+00	9	\N	\N	f	f
8796	CATEGORY	Category	Contract Subscriptions	154764	2022-01-21 10:42:22.412325+00	2022-01-21 10:42:22.412354+00	9	\N	\N	f	f
8797	CATEGORY	Category	Contract Subscriptions - Billed	154766	2022-01-21 10:42:22.412415+00	2022-01-21 10:42:22.412444+00	9	\N	\N	f	f
8798	CATEGORY	Category	Contract Subscriptions - Paid	154768	2022-01-21 10:42:22.412506+00	2022-01-21 10:42:22.412535+00	9	\N	\N	f	f
8799	CATEGORY	Category	Contract Subscriptions - Unbilled	154762	2022-01-21 10:42:22.412597+00	2022-01-21 10:42:22.412626+00	9	\N	\N	f	f
8800	CATEGORY	Category	Contract Usage	154765	2022-01-21 10:42:22.412687+00	2022-01-21 10:42:22.412716+00	9	\N	\N	f	f
8801	CATEGORY	Category	Contract Usage - Billed	154761	2022-01-21 10:42:22.412778+00	2022-01-21 10:42:22.412807+00	9	\N	\N	f	f
8802	CATEGORY	Category	Contract Usage - Paid	154767	2022-01-21 10:42:22.412868+00	2022-01-21 10:42:22.412897+00	9	\N	\N	f	f
8803	CATEGORY	Category	Contract Usage - Unbilled	154760	2022-01-21 10:42:22.412958+00	2022-01-21 10:42:22.412987+00	9	\N	\N	f	f
8804	CATEGORY	Category	Contributions	147242	2022-01-21 10:42:22.413047+00	2022-01-21 10:42:22.413076+00	9	\N	\N	f	f
8805	CATEGORY	Category	Cost of Goods Sold	147270	2022-01-21 10:42:22.413154+00	2022-01-21 10:42:22.413184+00	9	\N	\N	f	f
8806	CATEGORY	Category	Courier	142044	2022-01-21 10:42:22.413245+00	2022-01-21 10:42:22.413274+00	9	\N	\N	f	f
8807	CATEGORY	Category	Credit Card Offset	154824	2022-01-21 10:42:22.413335+00	2022-01-21 10:42:22.413364+00	9	\N	\N	f	f
8808	CATEGORY	Category	CTA	154776	2022-01-21 10:42:22.413426+00	2022-01-21 10:42:22.413455+00	9	\N	\N	f	f
8809	CATEGORY	Category	Currency Gain-Loss	154781	2022-01-21 10:42:22.413516+00	2022-01-21 10:42:22.413545+00	9	\N	\N	f	f
8810	CATEGORY	Category	Customer Return Variance	147295	2022-01-21 10:42:22.413606+00	2022-01-21 10:42:22.413635+00	9	\N	\N	f	f
8811	CATEGORY	Category	Damaged Goods	147225	2022-01-21 10:42:22.413696+00	2022-01-21 10:42:22.413726+00	9	\N	\N	f	f
8812	CATEGORY	Category	Deferred Expense	154803	2022-01-21 10:42:22.413786+00	2022-01-21 10:42:22.413815+00	9	\N	\N	f	f
8813	CATEGORY	Category	Deferred Expense - Commission	154800	2022-01-21 10:42:22.413876+00	2022-01-21 10:42:22.413906+00	9	\N	\N	f	f
8814	CATEGORY	Category	Deferred Expense - Royalty	154801	2022-01-21 10:42:22.413966+00	2022-01-21 10:42:22.413995+00	9	\N	\N	f	f
8815	CATEGORY	Category	Deferred Revenue	142195	2022-01-21 10:42:22.414056+00	2022-01-21 10:42:22.414086+00	9	\N	\N	f	f
8816	CATEGORY	Category	Deferred Revenue Contra	142194	2022-01-21 10:42:22.414147+00	2022-01-21 10:42:22.414176+00	9	\N	\N	f	f
8817	CATEGORY	Category	Depreciation	163336	2022-01-21 10:42:22.414237+00	2022-01-21 10:42:22.414267+00	9	\N	\N	f	f
8818	CATEGORY	Category	Depreciation Expense	142163	2022-01-21 10:42:22.414328+00	2022-01-21 10:42:22.414358+00	9	\N	\N	f	f
8819	CATEGORY	Category	Description about 00	145128	2022-01-21 10:42:22.414419+00	2022-01-21 10:42:22.414448+00	9	\N	\N	f	f
8820	CATEGORY	Category	Description about ASHWIN MANUALLY ADDED THIS	145129	2022-01-21 10:42:22.414509+00	2022-01-21 10:42:22.414539+00	9	\N	\N	f	f
8821	CATEGORY	Category	Description about ASHWIN MANUALLY ADDED THIS2	145130	2022-01-21 10:42:22.414599+00	2022-01-21 10:42:22.414628+00	9	\N	\N	f	f
8822	CATEGORY	Category	Disability	147248	2022-01-21 10:42:22.414689+00	2022-01-21 10:42:22.414719+00	9	\N	\N	f	f
8823	CATEGORY	Category	Disposal Fees	145047	2022-01-21 10:42:22.41478+00	2022-01-21 10:42:22.414809+00	9	\N	\N	f	f
8824	CATEGORY	Category	Dividends	142176	2022-01-21 10:42:22.41487+00	2022-01-21 10:42:22.414899+00	9	\N	\N	f	f
8825	CATEGORY	Category	Downgrade	154842	2022-01-21 10:42:22.41496+00	2022-01-21 10:42:22.414989+00	9	\N	\N	f	f
8826	CATEGORY	Category	DR - Contract Services - Billed	154811	2022-01-21 10:42:22.41505+00	2022-01-21 10:42:22.415079+00	9	\N	\N	f	f
8827	CATEGORY	Category	DR - Contract Services - Paid	154814	2022-01-21 10:42:22.415141+00	2022-01-21 10:42:22.41517+00	9	\N	\N	f	f
8828	CATEGORY	Category	DR - Contract Services - Unbilled	154816	2022-01-21 10:42:22.415231+00	2022-01-21 10:42:22.41526+00	9	\N	\N	f	f
8829	CATEGORY	Category	DR - Contract Subscriptions - Billed	154810	2022-01-21 10:42:22.415321+00	2022-01-21 10:42:22.41535+00	9	\N	\N	f	f
8830	CATEGORY	Category	DR - Contract Subscriptions - Paid	154815	2022-01-21 10:42:22.415411+00	2022-01-21 10:42:22.41544+00	9	\N	\N	f	f
8831	CATEGORY	Category	DR - Contract Subscriptions - Unbilled	154808	2022-01-21 10:42:22.4155+00	2022-01-21 10:42:22.415529+00	9	\N	\N	f	f
8832	CATEGORY	Category	DR - Contract Usage - Billed	154812	2022-01-21 10:42:22.41559+00	2022-01-21 10:42:22.41562+00	9	\N	\N	f	f
8833	CATEGORY	Category	DR - Contract Usage - Paid	154813	2022-01-21 10:42:22.415681+00	2022-01-21 10:42:22.41571+00	9	\N	\N	f	f
8834	CATEGORY	Category	DR - Contract Usage - Unbilled	154809	2022-01-21 10:42:22.41577+00	2022-01-21 10:42:22.4158+00	9	\N	\N	f	f
8835	CATEGORY	Category	Due from Entity 100	142185	2022-01-21 10:42:22.41586+00	2022-01-21 10:42:22.415889+00	9	\N	\N	f	f
8836	CATEGORY	Category	Due from Entity 200	142183	2022-01-21 10:42:22.41595+00	2022-01-21 10:42:22.415979+00	9	\N	\N	f	f
8837	CATEGORY	Category	Due from Entity 300	142184	2022-01-21 10:42:22.41604+00	2022-01-21 10:42:22.416069+00	9	\N	\N	f	f
8838	CATEGORY	Category	Due from Entity 400	154794	2022-01-21 10:42:22.416132+00	2022-01-21 10:42:22.416161+00	9	\N	\N	f	f
8839	CATEGORY	Category	Due from Entity 500	154797	2022-01-21 10:42:22.416223+00	2022-01-21 10:42:22.416252+00	9	\N	\N	f	f
8840	CATEGORY	Category	Due from Entity 600	154796	2022-01-21 10:42:22.416312+00	2022-01-21 10:42:22.416342+00	9	\N	\N	f	f
8841	CATEGORY	Category	Due from Entity 700	154795	2022-01-21 10:42:22.479117+00	2022-01-21 10:42:22.479165+00	9	\N	\N	f	f
8842	CATEGORY	Category	Dues and Expenses from Intacct	142236	2022-01-21 10:42:22.479242+00	2022-01-21 10:42:22.479274+00	9	\N	\N	f	f
8843	CATEGORY	Category	Dues and Subscriptions	147243	2022-01-21 10:42:22.479343+00	2022-01-21 10:42:22.479376+00	9	\N	\N	f	f
8844	CATEGORY	Category	Dues Expenses from Intacct	142235	2022-01-21 10:42:22.479444+00	2022-01-21 10:42:22.479474+00	9	\N	\N	f	f
8845	CATEGORY	Category	Dues & Subscriptions	145048	2022-01-21 10:42:22.479541+00	2022-01-21 10:42:22.47987+00	9	\N	\N	f	f
8846	CATEGORY	Category	Due to Entity 100	142197	2022-01-21 10:42:22.480209+00	2022-01-21 10:42:22.480277+00	9	\N	\N	f	f
8847	CATEGORY	Category	Due to Entity 200	142198	2022-01-21 10:42:22.481039+00	2022-01-21 10:42:22.481141+00	9	\N	\N	f	f
8848	CATEGORY	Category	Due to Entity 300	142196	2022-01-21 10:42:22.482045+00	2022-01-21 10:42:22.482216+00	9	\N	\N	f	f
8849	CATEGORY	Category	Due to Entity 400	154819	2022-01-21 10:42:22.482776+00	2022-01-21 10:42:22.48283+00	9	\N	\N	f	f
8850	CATEGORY	Category	Due to Entity 500	154818	2022-01-21 10:42:22.482907+00	2022-01-21 10:42:22.482931+00	9	\N	\N	f	f
8851	CATEGORY	Category	Due to Entity 600	154820	2022-01-21 10:42:22.482999+00	2022-01-21 10:42:22.483029+00	9	\N	\N	f	f
8852	CATEGORY	Category	Due to Entity 700	154817	2022-01-21 10:42:22.483096+00	2022-01-21 10:42:22.483126+00	9	\N	\N	f	f
8853	CATEGORY	Category	Duty Expense	147275	2022-01-21 10:42:22.48319+00	2022-01-21 10:42:22.48322+00	9	\N	\N	f	f
8854	CATEGORY	Category	Elimination Adjustment	154854	2022-01-21 10:42:22.483283+00	2022-01-21 10:42:22.483313+00	9	\N	\N	f	f
8855	CATEGORY	Category	Emma	149018	2022-01-21 10:42:22.483553+00	2022-01-21 10:42:22.493255+00	9	\N	\N	f	f
8856	CATEGORY	Category	Employee Advances	142149	2022-01-21 10:42:22.493666+00	2022-01-21 10:42:22.493717+00	9	\N	\N	f	f
8857	CATEGORY	Category	Employee Benefits	142129	2022-01-21 10:42:22.493804+00	2022-01-21 10:42:22.493845+00	9	\N	\N	f	f
8858	CATEGORY	Category	Employee Deductions	142161	2022-01-21 10:42:22.495328+00	2022-01-21 10:42:22.497063+00	9	\N	\N	f	f
8859	CATEGORY	Category	Entertainment	142036	2022-01-21 10:42:22.498149+00	2022-01-21 10:42:22.498199+00	9	\N	\N	f	f
8860	CATEGORY	Category	Equipment	145133	2022-01-21 10:42:22.498276+00	2022-01-21 10:42:22.498306+00	9	\N	\N	f	f
8861	CATEGORY	Category	Equipment Rental	145049	2022-01-21 10:42:22.498752+00	2022-01-21 10:42:22.498817+00	9	\N	\N	f	f
8862	CATEGORY	Category	Estimated Landed Costs	142152	2022-01-21 10:42:22.498921+00	2022-01-21 10:42:22.498952+00	9	\N	\N	f	f
8863	CATEGORY	Category	Exchange Rate Variance	147274	2022-01-21 10:42:22.499016+00	2022-01-21 10:42:22.499046+00	9	\N	\N	f	f
8864	CATEGORY	Category	Excise Tax	142219	2022-01-21 10:42:22.499795+00	2022-01-21 10:42:22.527869+00	9	\N	\N	f	f
8865	CATEGORY	Category	expense category	143132	2022-01-21 10:42:22.528075+00	2022-01-21 10:42:22.528202+00	9	\N	\N	f	f
8866	CATEGORY	Category	Flight	142049	2022-01-21 10:42:22.529179+00	2022-01-21 10:42:22.529561+00	9	\N	\N	f	f
8867	CATEGORY	Category	Food	142039	2022-01-21 10:42:22.529734+00	2022-01-21 10:42:22.529796+00	9	\N	\N	f	f
8868	CATEGORY	Category	Freight & Delivery	147244	2022-01-21 10:42:22.530056+00	2022-01-21 10:42:22.53009+00	9	\N	\N	f	f
8869	CATEGORY	Category	Freight Expense	147276	2022-01-21 10:42:22.530157+00	2022-01-21 10:42:22.530217+00	9	\N	\N	f	f
8870	CATEGORY	Category	Fuel	142032	2022-01-21 10:42:22.530539+00	2022-01-21 10:42:22.530622+00	9	\N	\N	f	f
8871	CATEGORY	Category	Furniture & Fixtures	142192	2022-01-21 10:42:22.530701+00	2022-01-21 10:42:22.530731+00	9	\N	\N	f	f
8872	CATEGORY	Category	Furniture & Fixtures Expense	147271	2022-01-21 10:42:22.530794+00	2022-01-21 10:42:22.530824+00	9	\N	\N	f	f
8873	CATEGORY	Category	Furniture for the department	145131	2022-01-21 10:42:22.530886+00	2022-01-21 10:42:22.530915+00	9	\N	\N	f	f
8874	CATEGORY	Category	Fyle	142125	2022-01-21 10:42:22.531113+00	2022-01-21 10:42:22.531152+00	9	\N	\N	f	f
8875	CATEGORY	Category	Fyleasdads	142123	2022-01-21 10:42:22.531408+00	2022-01-21 10:42:22.531581+00	9	\N	\N	f	f
8876	CATEGORY	Category	Fyle Expenses	142232	2022-01-21 10:42:22.53167+00	2022-01-21 10:42:22.531703+00	9	\N	\N	f	f
8877	CATEGORY	Category	Fyle Expenses!	142124	2022-01-21 10:42:22.531928+00	2022-01-21 10:42:22.531967+00	9	\N	\N	f	f
8878	CATEGORY	Category	Gain for Sale of an asset	142175	2022-01-21 10:42:22.532119+00	2022-01-21 10:42:22.532154+00	9	\N	\N	f	f
8879	CATEGORY	Category	Gain (loss) on Sale of Assets	147266	2022-01-21 10:42:22.532221+00	2022-01-21 10:42:22.532255+00	9	\N	\N	f	f
8880	CATEGORY	Category	Gas & Oil	147239	2022-01-21 10:42:22.532578+00	2022-01-21 10:42:22.532617+00	9	\N	\N	f	f
8881	CATEGORY	Category	Gayathiri	163337	2022-01-21 10:42:22.532983+00	2022-01-21 10:42:22.533029+00	9	\N	\N	f	f
8882	CATEGORY	Category	Goods in Transit	142210	2022-01-21 10:42:22.533234+00	2022-01-21 10:42:22.533272+00	9	\N	\N	f	f
8883	CATEGORY	Category	Goods Received Not Invoiced (GRNI)	142151	2022-01-21 10:42:22.533506+00	2022-01-21 10:42:22.533549+00	9	\N	\N	f	f
8884	CATEGORY	Category	Goodwill	142162	2022-01-21 10:42:22.533645+00	2022-01-21 10:42:22.533678+00	9	\N	\N	f	f
8885	CATEGORY	Category	Ground Transportation-Parking	150887	2022-01-21 10:42:22.533747+00	2022-01-21 10:42:22.53379+00	9	\N	\N	f	f
8886	CATEGORY	Category	GST Paid	147763	2022-01-21 10:42:22.631299+00	2022-01-21 10:42:22.631384+00	9	\N	\N	f	f
8887	CATEGORY	Category	Holiday	154829	2022-01-21 10:42:22.631808+00	2022-01-21 10:42:22.631887+00	9	\N	\N	f	f
8888	CATEGORY	Category	Hotel	142045	2022-01-21 10:42:22.632055+00	2022-01-21 10:42:22.632801+00	9	\N	\N	f	f
8889	CATEGORY	Category	Hotel-Lodging	150888	2022-01-21 10:42:22.632899+00	2022-01-21 10:42:22.632929+00	9	\N	\N	f	f
8890	CATEGORY	Category	Income tax expense	147524	2022-01-21 10:42:22.632994+00	2022-01-21 10:42:22.633023+00	9	\N	\N	f	f
8891	CATEGORY	Category	Incremental Account	146044	2022-01-21 10:42:22.830545+00	2022-01-21 10:42:22.83059+00	9	\N	\N	f	f
8892	CATEGORY	Category	Indirect Labor	154828	2022-01-21 10:42:22.830658+00	2022-01-21 10:42:22.830688+00	9	\N	\N	f	f
8893	CATEGORY	Category	Indirect Labor Offset	154831	2022-01-21 10:42:22.83075+00	2022-01-21 10:42:22.83078+00	9	\N	\N	f	f
8894	CATEGORY	Category	Insurance	142170	2022-01-21 10:42:22.830841+00	2022-01-21 10:42:22.830871+00	9	\N	\N	f	f
8895	CATEGORY	Category	Insurance - Disability	147525	2022-01-21 10:42:22.830932+00	2022-01-21 10:42:22.830962+00	9	\N	\N	f	f
8896	CATEGORY	Category	Insurance Expense	147245	2022-01-21 10:42:22.831024+00	2022-01-21 10:42:22.831054+00	9	\N	\N	f	f
8897	CATEGORY	Category	Insurance Expense-General Liability Insurance	154548	2022-01-21 10:42:22.831116+00	2022-01-21 10:42:22.831145+00	9	\N	\N	f	f
8898	CATEGORY	Category	Insurance Expense-Health Insurance	154549	2022-01-21 10:42:22.831208+00	2022-01-21 10:42:22.831238+00	9	\N	\N	f	f
8899	CATEGORY	Category	Insurance Expense-Life and Disability Insurance	154550	2022-01-21 10:42:22.8313+00	2022-01-21 10:42:22.831329+00	9	\N	\N	f	f
8900	CATEGORY	Category	Insurance Expense-Professional Liability	154551	2022-01-21 10:42:22.831391+00	2022-01-21 10:42:22.831421+00	9	\N	\N	f	f
8901	CATEGORY	Category	Insurance - General	147526	2022-01-21 10:42:22.831497+00	2022-01-21 10:42:22.831527+00	9	\N	\N	f	f
8902	CATEGORY	Category	Insurance - Liability	147527	2022-01-21 10:42:22.831589+00	2022-01-21 10:42:22.831619+00	9	\N	\N	f	f
8903	CATEGORY	Category	Insurance:Workers Compensation	145050	2022-01-21 10:42:22.83168+00	2022-01-21 10:42:22.831709+00	9	\N	\N	f	f
8904	CATEGORY	Category	Integration Test Account	143129	2022-01-21 10:42:22.831771+00	2022-01-21 10:42:22.8318+00	9	\N	\N	f	f
8905	CATEGORY	Category	Intercompany Payables	142199	2022-01-21 10:42:22.831862+00	2022-01-21 10:42:22.831891+00	9	\N	\N	f	f
8906	CATEGORY	Category	Intercompany Professional Fees	142202	2022-01-21 10:42:22.831953+00	2022-01-21 10:42:22.831982+00	9	\N	\N	f	f
8907	CATEGORY	Category	Intercompany Receivables	142186	2022-01-21 10:42:22.832044+00	2022-01-21 10:42:22.832073+00	9	\N	\N	f	f
8908	CATEGORY	Category	Interest Expense	142201	2022-01-21 10:42:22.832135+00	2022-01-21 10:42:22.832165+00	9	\N	\N	f	f
8909	CATEGORY	Category	Interest Income	142200	2022-01-21 10:42:22.832227+00	2022-01-21 10:42:22.832256+00	9	\N	\N	f	f
8910	CATEGORY	Category	Internet	142042	2022-01-21 10:42:22.832318+00	2022-01-21 10:42:22.832347+00	9	\N	\N	f	f
8912	CATEGORY	Category	Inventory Asset	147269	2022-01-21 10:42:22.832499+00	2022-01-21 10:42:22.832528+00	9	\N	\N	f	f
8913	CATEGORY	Category	Inventory - GRNI	154779	2022-01-21 10:42:22.832589+00	2022-01-21 10:42:22.832618+00	9	\N	\N	f	f
8914	CATEGORY	Category	Inventory In Transit	147278	2022-01-21 10:42:22.83268+00	2022-01-21 10:42:22.832709+00	9	\N	\N	f	f
8915	CATEGORY	Category	Inventory-Kits	142209	2022-01-21 10:42:22.832771+00	2022-01-21 10:42:22.8328+00	9	\N	\N	f	f
8916	CATEGORY	Category	Inventory - Other	154823	2022-01-21 10:42:22.832862+00	2022-01-21 10:42:22.832892+00	9	\N	\N	f	f
8917	CATEGORY	Category	Inventory-Other	142208	2022-01-21 10:42:22.832954+00	2022-01-21 10:42:22.832983+00	9	\N	\N	f	f
8918	CATEGORY	Category	Inventory Returned Not Credited	147226	2022-01-21 10:42:22.833044+00	2022-01-21 10:42:22.833073+00	9	\N	\N	f	f
8919	CATEGORY	Category	Inventory Transfer Price Gain - Loss	147282	2022-01-21 10:42:22.833134+00	2022-01-21 10:42:22.833163+00	9	\N	\N	f	f
8920	CATEGORY	Category	Inventory Variance	147237	2022-01-21 10:42:22.833576+00	2022-01-21 10:42:22.833629+00	9	\N	\N	f	f
8921	CATEGORY	Category	Inventory Write Offs	147277	2022-01-21 10:42:22.834072+00	2022-01-21 10:42:22.834117+00	9	\N	\N	f	f
8922	CATEGORY	Category	Investments and Securities	142182	2022-01-21 10:42:22.834187+00	2022-01-21 10:42:22.834218+00	9	\N	\N	f	f
8923	CATEGORY	Category	Janitorial Expense	154553	2022-01-21 10:42:22.83428+00	2022-01-21 10:42:22.83431+00	9	\N	\N	f	f
8924	CATEGORY	Category	Janitors 101	160445	2022-01-21 10:42:22.834372+00	2022-01-21 10:42:22.834401+00	9	\N	\N	f	f
8925	CATEGORY	Category	Job Expenses	145051	2022-01-21 10:42:22.834462+00	2022-01-21 10:42:22.834491+00	9	\N	\N	f	f
8926	CATEGORY	Category	Job Expenses:Cost of Labor	145052	2022-01-21 10:42:22.83475+00	2022-01-21 10:42:22.834824+00	9	\N	\N	f	f
8927	CATEGORY	Category	Job Expenses:Cost of Labor:Installation	145018	2022-01-21 10:42:22.835187+00	2022-01-21 10:42:22.83523+00	9	\N	\N	f	f
8928	CATEGORY	Category	Job Expenses:Cost of Labor:Maintenance and Repairs	145019	2022-01-21 10:42:22.835298+00	2022-01-21 10:42:22.835328+00	9	\N	\N	f	f
8929	CATEGORY	Category	Job Expenses:Equipment Rental	145020	2022-01-21 10:42:22.841215+00	2022-01-21 10:42:22.841303+00	9	\N	\N	f	f
8930	CATEGORY	Category	Job Expenses:Job Materials	145021	2022-01-21 10:42:22.841601+00	2022-01-21 10:42:22.843631+00	9	\N	\N	f	f
8931	CATEGORY	Category	Job Expenses:Job Materials:Decks and Patios	145022	2022-01-21 10:42:22.843917+00	2022-01-21 10:42:22.843981+00	9	\N	\N	f	f
8932	CATEGORY	Category	Job Expenses:Job Materials:Fountain and Garden Lighting	145023	2022-01-21 10:42:22.844118+00	2022-01-21 10:42:22.844166+00	9	\N	\N	f	f
8933	CATEGORY	Category	Job Expenses:Job Materials:Plants and Soil	145024	2022-01-21 10:42:22.844278+00	2022-01-21 10:42:22.844322+00	9	\N	\N	f	f
8934	CATEGORY	Category	Job Expenses:Job Materials:Sprinklers and Drip Systems	145025	2022-01-21 10:42:22.844594+00	2022-01-21 10:42:22.844649+00	9	\N	\N	f	f
8935	CATEGORY	Category	Job Expenses:Permits	145053	2022-01-21 10:42:22.845055+00	2022-01-21 10:42:22.84511+00	9	\N	\N	f	f
8936	CATEGORY	Category	Journal Entry Rounding	154821	2022-01-21 10:42:22.845218+00	2022-01-21 10:42:22.845259+00	9	\N	\N	f	f
8937	CATEGORY	Category	Labor	147299	2022-01-21 10:42:22.845362+00	2022-01-21 10:42:22.845402+00	9	\N	\N	f	f
8938	CATEGORY	Category	Labor Burden	147300	2022-01-21 10:42:22.8455+00	2022-01-21 10:42:22.845665+00	9	\N	\N	f	f
8939	CATEGORY	Category	Labor Cost Offset	142137	2022-01-21 10:42:22.845809+00	2022-01-21 10:42:22.89557+00	9	\N	\N	f	f
8940	CATEGORY	Category	Labor Cost Variance	142136	2022-01-21 10:42:22.915727+00	2022-01-21 10:42:22.915822+00	9	\N	\N	f	f
8941	CATEGORY	Category	LCT Paid	147764	2022-01-21 10:42:23.100174+00	2022-01-21 10:42:23.10024+00	9	\N	\N	f	f
8942	CATEGORY	Category	Legal	147273	2022-01-21 10:42:23.100349+00	2022-01-21 10:42:23.100389+00	9	\N	\N	f	f
8943	CATEGORY	Category	Legal and professional fees	147529	2022-01-21 10:42:23.100496+00	2022-01-21 10:42:23.100524+00	9	\N	\N	f	f
8944	CATEGORY	Category	Legal & Professional Fees	145054	2022-01-21 10:42:23.10062+00	2022-01-21 10:42:23.110536+00	9	\N	\N	f	f
8945	CATEGORY	Category	Legal & Professional Fees:Accounting	145055	2022-01-21 10:42:23.110685+00	2022-01-21 10:42:23.110733+00	9	\N	\N	f	f
8946	CATEGORY	Category	Legal & Professional Fees:Bookkeeper	145026	2022-01-21 10:42:23.110844+00	2022-01-21 10:42:23.110894+00	9	\N	\N	f	f
8947	CATEGORY	Category	Legal & Professional Fees:Lawyer	145027	2022-01-21 10:42:23.111111+00	2022-01-21 10:42:23.11129+00	9	\N	\N	f	f
8948	CATEGORY	Category	Liability	147246	2022-01-21 10:42:23.111612+00	2022-01-21 10:42:23.111675+00	9	\N	\N	f	f
8949	CATEGORY	Category	Long Term Debt	154784	2022-01-21 10:42:23.116205+00	2022-01-21 10:42:23.118677+00	9	\N	\N	f	f
8950	CATEGORY	Category	Loss on discontinued operations, net of tax	147530	2022-01-21 10:42:23.161839+00	2022-01-21 10:42:23.162079+00	9	\N	\N	f	f
8951	CATEGORY	Category	Machine	147301	2022-01-21 10:42:23.162186+00	2022-01-21 10:42:23.162224+00	9	\N	\N	f	f
8952	CATEGORY	Category	Machine Burden	147302	2022-01-21 10:42:23.162554+00	2022-01-21 10:42:23.162599+00	9	\N	\N	f	f
8953	CATEGORY	Category	Machinery & Equipment	142190	2022-01-21 10:42:23.162986+00	2022-01-21 10:42:23.16304+00	9	\N	\N	f	f
8954	CATEGORY	Category	Machinery & Equipment Accm.Depr.	142191	2022-01-21 10:42:23.163157+00	2022-01-21 10:42:23.163197+00	9	\N	\N	f	f
8955	CATEGORY	Category	Maintenance and Repair	145028	2022-01-21 10:42:23.16329+00	2022-01-21 10:42:23.163328+00	9	\N	\N	f	f
8956	CATEGORY	Category	Maintenance and Repair:Building Repairs	145029	2022-01-21 10:42:23.163418+00	2022-01-21 10:42:23.163456+00	9	\N	\N	f	f
8957	CATEGORY	Category	Maintenance and Repair:Computer Repairs	145030	2022-01-21 10:42:23.163543+00	2022-01-21 10:42:23.16358+00	9	\N	\N	f	f
8958	CATEGORY	Category	Maintenance and Repair:Equipment Repairs	145031	2022-01-21 10:42:23.163669+00	2022-01-21 10:42:23.163706+00	9	\N	\N	f	f
8959	CATEGORY	Category	Management compensation	147531	2022-01-21 10:42:23.164227+00	2022-01-21 10:42:23.164281+00	9	\N	\N	f	f
8960	CATEGORY	Category	Manufacturing Expenses	147298	2022-01-21 10:42:23.164393+00	2022-01-21 10:42:23.164439+00	9	\N	\N	f	f
8961	CATEGORY	Category	Marketing and Advertising	142168	2022-01-21 10:42:23.164539+00	2022-01-21 10:42:23.164574+00	9	\N	\N	f	f
8962	CATEGORY	Category	Marketing Expense	154554	2022-01-21 10:42:23.164665+00	2022-01-21 10:42:23.164704+00	9	\N	\N	f	f
8963	CATEGORY	Category	Meals	145134	2022-01-21 10:42:23.164805+00	2022-01-21 10:42:23.164844+00	9	\N	\N	f	f
8964	CATEGORY	Category	Meals and Entertainment	142172	2022-01-21 10:42:23.164945+00	2022-01-21 10:42:23.164984+00	9	\N	\N	f	f
8965	CATEGORY	Category	Meals & Entertainment	143128	2022-01-21 10:42:23.165476+00	2022-01-21 10:42:23.165537+00	9	\N	\N	f	f
8966	CATEGORY	Category	Merchandise	147233	2022-01-21 10:42:23.165649+00	2022-01-21 10:42:23.16569+00	9	\N	\N	f	f
8967	CATEGORY	Category	Mfg Scrap	147297	2022-01-21 10:42:23.165788+00	2022-01-21 10:42:23.165829+00	9	\N	\N	f	f
8968	CATEGORY	Category	Mfg WIP	147290	2022-01-21 10:42:23.165933+00	2022-01-21 10:42:23.165972+00	9	\N	\N	f	f
8969	CATEGORY	Category	Mileage / COGS	148741	2022-01-21 10:42:23.166073+00	2022-01-21 10:42:23.166113+00	9	\N	\N	f	f
8970	CATEGORY	Category	Mileage	142038	2022-01-21 10:42:23.166205+00	2022-01-21 10:42:23.166243+00	9	\N	\N	f	f
8971	CATEGORY	Category	Mileage / Team outing	148742	2022-01-21 10:42:23.16634+00	2022-01-21 10:42:23.166377+00	9	\N	\N	f	f
8972	CATEGORY	Category	Miscellaneous	163338	2022-01-21 10:42:23.168216+00	2022-01-21 10:42:23.168238+00	9	\N	\N	f	f
8973	CATEGORY	Category	Miscellaneous Expense	147249	2022-01-21 10:42:23.168293+00	2022-01-21 10:42:23.16832+00	9	\N	\N	f	f
8974	CATEGORY	Category	Movies	145387	2022-01-21 10:42:23.168373+00	2022-01-21 10:42:23.168402+00	9	\N	\N	f	f
8975	CATEGORY	Category	Netflix	149017	2022-01-21 10:42:23.175966+00	2022-01-21 10:42:23.176259+00	9	\N	\N	f	f
8976	CATEGORY	Category	New Category	153956	2022-01-21 10:42:23.178256+00	2022-01-21 10:42:23.178534+00	9	\N	\N	f	f
8977	CATEGORY	Category	Non-Billable Hours	154836	2022-01-21 10:42:23.178921+00	2022-01-21 10:42:23.178995+00	9	\N	\N	f	f
8978	CATEGORY	Category	Non-Billable Overtime Hours	154834	2022-01-21 10:42:23.179145+00	2022-01-21 10:42:23.179954+00	9	\N	\N	f	f
8979	CATEGORY	Category	Note Receivable-Current	147232	2022-01-21 10:42:23.180563+00	2022-01-21 10:42:23.180742+00	9	\N	\N	f	f
8980	CATEGORY	Category	Notes Payable	142167	2022-01-21 10:42:23.181333+00	2022-01-21 10:42:23.18162+00	9	\N	\N	f	f
8981	CATEGORY	Category	OE Subscriptions	154763	2022-01-21 10:42:23.182105+00	2022-01-21 10:42:23.182307+00	9	\N	\N	f	f
8982	CATEGORY	Category	Office Expense	147250	2022-01-21 10:42:23.182468+00	2022-01-21 10:42:23.182508+00	9	\N	\N	f	f
8983	CATEGORY	Category	Office Expenses	145032	2022-01-21 10:42:23.182646+00	2022-01-21 10:42:23.182686+00	9	\N	\N	f	f
8984	CATEGORY	Category	Office-General Administrative Expenses	146047	2022-01-21 10:42:23.18285+00	2022-01-21 10:42:23.182901+00	9	\N	\N	f	f
8985	CATEGORY	Category	Office/General Administrative Expenses	158276	2022-01-21 10:42:23.183044+00	2022-01-21 10:42:23.183085+00	9	\N	\N	f	f
8986	CATEGORY	Category	Office Party	142048	2022-01-21 10:42:23.195522+00	2022-01-21 10:42:23.195561+00	9	\N	\N	f	f
8987	CATEGORY	Category	Office Supplies	142034	2022-01-21 10:42:23.195627+00	2022-01-21 10:42:23.195657+00	9	\N	\N	f	f
8988	CATEGORY	Category	Office Supplies 2	146046	2022-01-21 10:42:23.195721+00	2022-01-21 10:42:23.195751+00	9	\N	\N	f	f
8989	CATEGORY	Category	Office Suppliesdfsd	142131	2022-01-21 10:42:23.195812+00	2022-01-21 10:42:23.195841+00	9	\N	\N	f	f
8990	CATEGORY	Category	Online Fees	147265	2022-01-21 10:42:23.195903+00	2022-01-21 10:42:23.195932+00	9	\N	\N	f	f
8991	CATEGORY	Category	Opening Balance Equity	163339	2022-01-21 10:42:23.281147+00	2022-01-21 10:42:23.28121+00	9	\N	\N	f	f
8992	CATEGORY	Category	Other Assets	142212	2022-01-21 10:42:23.281361+00	2022-01-21 10:42:23.281413+00	9	\N	\N	f	f
8993	CATEGORY	Category	Other Direct Costs	147236	2022-01-21 10:42:23.281549+00	2022-01-21 10:42:23.281591+00	9	\N	\N	f	f
8994	CATEGORY	Category	Other Expense	142221	2022-01-21 10:42:23.281727+00	2022-01-21 10:42:23.281766+00	9	\N	\N	f	f
8995	CATEGORY	Category	Other G&A	142159	2022-01-21 10:42:23.2819+00	2022-01-21 10:42:23.281941+00	9	\N	\N	f	f
8996	CATEGORY	Category	Other general and administrative expenses	147534	2022-01-21 10:42:23.282077+00	2022-01-21 10:42:23.282127+00	9	\N	\N	f	f
8997	CATEGORY	Category	Other Income	142222	2022-01-21 10:42:23.282272+00	2022-01-21 10:42:23.282314+00	9	\N	\N	f	f
8998	CATEGORY	Category	Other Intangible Assets	142211	2022-01-21 10:42:23.282448+00	2022-01-21 10:42:23.282488+00	9	\N	\N	f	f
8999	CATEGORY	Category	Other Receivables	147229	2022-01-21 10:42:23.28383+00	2022-01-21 10:42:23.28392+00	9	\N	\N	f	f
9000	CATEGORY	Category	Others	142037	2022-01-21 10:42:23.301721+00	2022-01-21 10:42:23.301788+00	9	\N	\N	f	f
9001	CATEGORY	Category	Other selling expenses	147535	2022-01-21 10:42:23.317906+00	2022-01-21 10:42:23.317943+00	9	\N	\N	f	f
9002	CATEGORY	Category	Other Taxes	142220	2022-01-21 10:42:23.31801+00	2022-01-21 10:42:23.31804+00	9	\N	\N	f	f
9003	CATEGORY	Category	Other Types of Expenses-Advertising Expenses	147536	2022-01-21 10:42:23.318104+00	2022-01-21 10:42:23.318134+00	9	\N	\N	f	f
9004	CATEGORY	Category	Outside Services	147251	2022-01-21 10:42:23.318196+00	2022-01-21 10:42:23.318226+00	9	\N	\N	f	f
9005	CATEGORY	Category	Pager	147263	2022-01-21 10:42:23.318288+00	2022-01-21 10:42:23.318317+00	9	\N	\N	f	f
9006	CATEGORY	Category	Paid Time Off	154827	2022-01-21 10:42:23.318379+00	2022-01-21 10:42:23.318408+00	9	\N	\N	f	f
9007	CATEGORY	Category	Parking	142051	2022-01-21 10:42:23.31847+00	2022-01-21 10:42:23.318499+00	9	\N	\N	f	f
9008	CATEGORY	Category	Patents & Licenses	142127	2022-01-21 10:42:23.318561+00	2022-01-21 10:42:23.31859+00	9	\N	\N	f	f
9009	CATEGORY	Category	Pay As You Go Withholding	147767	2022-01-21 10:42:23.318652+00	2022-01-21 10:42:23.318681+00	9	\N	\N	f	f
9010	CATEGORY	Category	Payroll Expense	142126	2022-01-21 10:42:23.318743+00	2022-01-21 10:42:23.318772+00	9	\N	\N	f	f
9011	CATEGORY	Category	Payroll Expenses	142233	2022-01-21 10:42:23.327375+00	2022-01-21 10:42:23.32747+00	9	\N	\N	f	f
9012	CATEGORY	Category	Payroll Taxes	142206	2022-01-21 10:42:23.345141+00	2022-01-21 10:42:23.345188+00	9	\N	\N	f	f
9013	CATEGORY	Category	Penalties & Settlements	163340	2022-01-21 10:42:23.34528+00	2022-01-21 10:42:23.345317+00	9	\N	\N	f	f
9014	CATEGORY	Category	Per Diem	142040	2022-01-21 10:42:23.345404+00	2022-01-21 10:42:23.34544+00	9	\N	\N	f	f
9015	CATEGORY	Category	Phone	142047	2022-01-21 10:42:23.345527+00	2022-01-21 10:42:23.345563+00	9	\N	\N	f	f
9016	CATEGORY	Category	Postage and Delivery	154556	2022-01-21 10:42:23.34565+00	2022-01-21 10:42:23.345687+00	9	\N	\N	f	f
9017	CATEGORY	Category	Postage & Delivery	147252	2022-01-21 10:42:23.345773+00	2022-01-21 10:42:23.345809+00	9	\N	\N	f	f
9018	CATEGORY	Category	Potential Billings	154852	2022-01-21 10:42:23.348949+00	2022-01-21 10:42:23.34901+00	9	\N	\N	f	f
9019	CATEGORY	Category	Potential Billings Offset	154853	2022-01-21 10:42:23.349617+00	2022-01-21 10:42:23.34967+00	9	\N	\N	f	f
9020	CATEGORY	Category	Preferred Stock	142214	2022-01-21 10:42:23.349774+00	2022-01-21 10:42:23.349813+00	9	\N	\N	f	f
9021	CATEGORY	Category	Prepaid Expenses	147230	2022-01-21 10:42:23.349907+00	2022-01-21 10:42:23.349945+00	9	\N	\N	f	f
9022	CATEGORY	Category	Prepaid Income Taxes	147231	2022-01-21 10:42:23.350035+00	2022-01-21 10:42:23.350072+00	9	\N	\N	f	f
9023	CATEGORY	Category	Prepaid Insurance	142146	2022-01-21 10:42:23.35016+00	2022-01-21 10:42:23.350197+00	9	\N	\N	f	f
9024	CATEGORY	Category	Prepaid Other	142148	2022-01-21 10:42:23.350285+00	2022-01-21 10:42:23.350322+00	9	\N	\N	f	f
9025	CATEGORY	Category	Prepaid Rent	142147	2022-01-21 10:42:23.350409+00	2022-01-21 10:42:23.350446+00	9	\N	\N	f	f
9026	CATEGORY	Category	Printing and Reproduction	154557	2022-01-21 10:42:23.350757+00	2022-01-21 10:42:23.350797+00	9	\N	\N	f	f
9027	CATEGORY	Category	Professional Development	154830	2022-01-21 10:42:23.350887+00	2022-01-21 10:42:23.350925+00	9	\N	\N	f	f
9028	CATEGORY	Category	Professional Fees	147253	2022-01-21 10:42:23.351012+00	2022-01-21 10:42:23.351048+00	9	\N	\N	f	f
9029	CATEGORY	Category	Professional Fees Expense	142171	2022-01-21 10:42:23.351135+00	2022-01-21 10:42:23.351171+00	9	\N	\N	f	f
9030	CATEGORY	Category	Professional Services	142046	2022-01-21 10:42:23.351257+00	2022-01-21 10:42:23.351294+00	9	\N	\N	f	f
9031	CATEGORY	Category	Promotional	145033	2022-01-21 10:42:23.35138+00	2022-01-21 10:42:23.351416+00	9	\N	\N	f	f
9032	CATEGORY	Category	Property	147259	2022-01-21 10:42:23.351502+00	2022-01-21 10:42:23.351538+00	9	\N	\N	f	f
9033	CATEGORY	Category	Purchase Price Variance	147291	2022-01-21 10:42:23.351624+00	2022-01-21 10:42:23.35166+00	9	\N	\N	f	f
9034	CATEGORY	Category	Purchases	145034	2022-01-21 10:42:23.351746+00	2022-01-21 10:42:23.351782+00	9	\N	\N	f	f
9035	CATEGORY	Category	Realized Gain-Loss	147285	2022-01-21 10:42:23.351867+00	2022-01-21 10:42:23.351904+00	9	\N	\N	f	f
9036	CATEGORY	Category	Regular Service	147262	2022-01-21 10:42:23.351989+00	2022-01-21 10:42:23.352026+00	9	\N	\N	f	f
9037	CATEGORY	Category	Renewal Downgrade	154849	2022-01-21 10:42:23.352111+00	2022-01-21 10:42:23.352148+00	9	\N	\N	f	f
9038	CATEGORY	Category	Renewal Upgrade	154848	2022-01-21 10:42:23.35226+00	2022-01-21 10:42:23.396251+00	9	\N	\N	f	f
9039	CATEGORY	Category	Rent	142132	2022-01-21 10:42:23.397145+00	2022-01-21 10:42:23.397183+00	9	\N	\N	f	f
9040	CATEGORY	Category	Rent Expense	147254	2022-01-21 10:42:23.397768+00	2022-01-21 10:42:23.397817+00	9	\N	\N	f	f
9041	CATEGORY	Category	Rent or Lease	145035	2022-01-21 10:42:23.598737+00	2022-01-21 10:42:23.598798+00	9	\N	\N	f	f
9042	CATEGORY	Category	Rent or lease payments	147537	2022-01-21 10:42:23.59893+00	2022-01-21 10:42:23.600175+00	9	\N	\N	f	f
9043	CATEGORY	Category	Repair and maintenance	154558	2022-01-21 10:42:23.601407+00	2022-01-21 10:42:23.601468+00	9	\N	\N	f	f
9044	CATEGORY	Category	Repairs	147240	2022-01-21 10:42:23.601593+00	2022-01-21 10:42:23.601638+00	9	\N	\N	f	f
9045	CATEGORY	Category	Repairs and Maintenance	142173	2022-01-21 10:42:23.601749+00	2022-01-21 10:42:23.601793+00	9	\N	\N	f	f
9046	CATEGORY	Category	Repairs & Maintenance	147255	2022-01-21 10:42:23.601901+00	2022-01-21 10:42:23.601945+00	9	\N	\N	f	f
9047	CATEGORY	Category	Reserved Inventory	154822	2022-01-21 10:42:23.602046+00	2022-01-21 10:42:23.602089+00	9	\N	\N	f	f
9048	CATEGORY	Category	Retained Earnings	142215	2022-01-21 10:42:23.602189+00	2022-01-21 10:42:23.602232+00	9	\N	\N	f	f
9049	CATEGORY	Category	Revenue - Accessories	142164	2022-01-21 10:42:23.602331+00	2022-01-21 10:42:23.602375+00	9	\N	\N	f	f
9050	CATEGORY	Category	Revenue - Entry	142165	2022-01-21 10:42:23.602476+00	2022-01-21 10:42:23.602524+00	9	\N	\N	f	f
9051	CATEGORY	Category	Revenue - Other	142205	2022-01-21 10:42:23.602627+00	2022-01-21 10:42:23.60267+00	9	\N	\N	f	f
9052	CATEGORY	Category	Revenue - Reimbursed Expenses	154773	2022-01-21 10:42:23.602773+00	2022-01-21 10:42:23.602815+00	9	\N	\N	f	f
9053	CATEGORY	Category	Revenue - Services	154770	2022-01-21 10:42:23.602917+00	2022-01-21 10:42:23.602959+00	9	\N	\N	f	f
9054	CATEGORY	Category	Revenue - Subcontractors	154771	2022-01-21 10:42:23.662725+00	2022-01-21 10:42:23.662809+00	9	\N	\N	f	f
9055	CATEGORY	Category	Revenue - Surveillance	142166	2022-01-21 10:42:23.663367+00	2022-01-21 10:42:23.663407+00	9	\N	\N	f	f
9056	CATEGORY	Category	Rounding Gain-Loss	147284	2022-01-21 10:42:23.663496+00	2022-01-21 10:42:23.663528+00	9	\N	\N	f	f
9057	CATEGORY	Category	Salaries and Wages	142174	2022-01-21 10:42:23.663856+00	2022-01-21 10:42:23.663908+00	9	\N	\N	f	f
9058	CATEGORY	Category	Salaries Payable	142150	2022-01-21 10:42:23.664024+00	2022-01-21 10:42:23.664068+00	9	\N	\N	f	f
9059	CATEGORY	Category	Salaries & Wages	147235	2022-01-21 10:42:23.664165+00	2022-01-21 10:42:23.664207+00	9	\N	\N	f	f
9060	CATEGORY	Category	Salaries & Wages Expense	147267	2022-01-21 10:42:23.664305+00	2022-01-21 10:42:23.664346+00	9	\N	\N	f	f
9061	CATEGORY	Category	Sales Tax Payable	154825	2022-01-21 10:42:23.664447+00	2022-01-21 10:42:23.664652+00	9	\N	\N	f	f
9062	CATEGORY	Category	Savings	163341	2022-01-21 10:42:23.664769+00	2022-01-21 10:42:23.66481+00	9	\N	\N	f	f
9063	CATEGORY	Category	Service	147234	2022-01-21 10:42:23.664912+00	2022-01-21 10:42:23.664956+00	9	\N	\N	f	f
9064	CATEGORY	Category	Shipping and delivery expense	147538	2022-01-21 10:42:23.665057+00	2022-01-21 10:42:23.665096+00	9	\N	\N	f	f
9065	CATEGORY	Category	Snacks	142033	2022-01-21 10:42:23.665195+00	2022-01-21 10:42:23.665237+00	9	\N	\N	f	f
9066	CATEGORY	Category	Software	142050	2022-01-21 10:42:23.665344+00	2022-01-21 10:42:23.665388+00	9	\N	\N	f	f
9067	CATEGORY	Category	Software and Licenses	142228	2022-01-21 10:42:23.666163+00	2022-01-21 10:42:23.666229+00	9	\N	\N	f	f
9068	CATEGORY	Category	Spot Bonus	142134	2022-01-21 10:42:23.666372+00	2022-01-21 10:42:23.666429+00	9	\N	\N	f	f
9069	CATEGORY	Category	Stationery and printing	147539	2022-01-21 10:42:23.666559+00	2022-01-21 10:42:23.66661+00	9	\N	\N	f	f
9070	CATEGORY	Category	Stationery & Printing	145036	2022-01-21 10:42:23.666731+00	2022-01-21 10:42:23.666778+00	9	\N	\N	f	f
9071	CATEGORY	Category	sub ash	147305	2022-01-21 10:42:23.666894+00	2022-01-21 10:42:23.66694+00	9	\N	\N	f	f
9072	CATEGORY	Category	Supplies	145037	2022-01-21 10:42:23.667053+00	2022-01-21 10:42:23.699254+00	9	\N	\N	f	f
9073	CATEGORY	Category	Supplies Expense	147256	2022-01-21 10:42:23.699382+00	2022-01-21 10:42:23.699422+00	9	\N	\N	f	f
9074	CATEGORY	Category	Supplies Test 2	146048	2022-01-21 10:42:23.699518+00	2022-01-21 10:42:23.699558+00	9	\N	\N	f	f
9075	CATEGORY	Category	SVB Checking	142177	2022-01-21 10:42:23.699652+00	2022-01-21 10:42:23.699691+00	9	\N	\N	f	f
9076	CATEGORY	Category	SVB Checking 2	142178	2022-01-21 10:42:23.699782+00	2022-01-21 10:42:23.699821+00	9	\N	\N	f	f
9077	CATEGORY	Category	SVB Checking 3	142179	2022-01-21 10:42:23.699911+00	2022-01-21 10:42:23.69995+00	9	\N	\N	f	f
9078	CATEGORY	Category	Sync Expense Account	145038	2022-01-21 10:42:23.70004+00	2022-01-21 10:42:23.700079+00	9	\N	\N	f	f
9079	CATEGORY	Category	Tax	142053	2022-01-21 10:42:23.700169+00	2022-01-21 10:42:23.700209+00	9	\N	\N	f	f
9080	CATEGORY	Category	Taxes & Licenses	145039	2022-01-21 10:42:23.700298+00	2022-01-21 10:42:23.700337+00	9	\N	\N	f	f
9081	CATEGORY	Category	Taxes & Licenses-Other	147257	2022-01-21 10:42:23.700426+00	2022-01-21 10:42:23.700464+00	9	\N	\N	f	f
9082	CATEGORY	Category	Taxes - Property	154559	2022-01-21 10:42:23.700555+00	2022-01-21 10:42:23.700593+00	9	\N	\N	f	f
9083	CATEGORY	Category	Taxi	142043	2022-01-21 10:42:23.700683+00	2022-01-21 10:42:23.700918+00	9	\N	\N	f	f
9084	CATEGORY	Category	Tax Receivable	154802	2022-01-21 10:42:23.701045+00	2022-01-21 10:42:23.701075+00	9	\N	\N	f	f
9085	CATEGORY	Category	Telecommunication Expense	142160	2022-01-21 10:42:23.701138+00	2022-01-21 10:42:23.701167+00	9	\N	\N	f	f
9086	CATEGORY	Category	Telecommunications	154782	2022-01-21 10:42:23.701227+00	2022-01-21 10:42:23.701256+00	9	\N	\N	f	f
9087	CATEGORY	Category	Telephone Expense	147261	2022-01-21 10:42:23.701322+00	2022-01-21 10:42:23.701352+00	9	\N	\N	f	f
9088	CATEGORY	Category	test	145136	2022-01-21 10:42:23.701413+00	2022-01-21 10:42:23.701443+00	9	\N	\N	f	f
9089	CATEGORY	Category	test1	160410	2022-01-21 10:42:23.701504+00	2022-01-21 10:42:23.701533+00	9	\N	\N	f	f
9090	CATEGORY	Category	Test 2	146049	2022-01-21 10:42:23.701595+00	2022-01-21 10:42:23.701624+00	9	\N	\N	f	f
9091	CATEGORY	Category	Test Staging	146050	2022-01-21 10:42:23.734248+00	2022-01-21 10:42:23.73433+00	9	\N	\N	f	f
9092	CATEGORY	Category	Toll Charge	142052	2022-01-21 10:42:23.734457+00	2022-01-21 10:42:23.734501+00	9	\N	\N	f	f
9093	CATEGORY	Category	Trade Shows and Exhibits	142169	2022-01-21 10:42:23.734604+00	2022-01-21 10:42:23.734649+00	9	\N	\N	f	f
9094	CATEGORY	Category	Train	142031	2022-01-21 10:42:23.734756+00	2022-01-21 10:42:23.7348+00	9	\N	\N	f	f
9095	CATEGORY	Category	Training	142054	2022-01-21 10:42:23.734895+00	2022-01-21 10:42:23.734936+00	9	\N	\N	f	f
9096	CATEGORY	Category	Transactor Clearing	154855	2022-01-21 10:42:23.735036+00	2022-01-21 10:42:23.735079+00	9	\N	\N	f	f
9097	CATEGORY	Category	Travel	142157	2022-01-21 10:42:23.735182+00	2022-01-21 10:42:23.735224+00	9	\N	\N	f	f
9098	CATEGORY	Category	Travel - Automobile	153955	2022-01-21 10:42:23.735321+00	2022-01-21 10:42:23.735365+00	9	\N	\N	f	f
9099	CATEGORY	Category	Travel Expense	154560	2022-01-21 10:42:23.735469+00	2022-01-21 10:42:23.735513+00	9	\N	\N	f	f
9100	CATEGORY	Category	Travel Expenses	145135	2022-01-21 10:42:23.735612+00	2022-01-21 10:42:23.735653+00	9	\N	\N	f	f
9101	CATEGORY	Category	Travel expenses - general and admin expenses	147540	2022-01-21 10:42:23.735754+00	2022-01-21 10:42:23.735798+00	9	\N	\N	f	f
9102	CATEGORY	Category	Travel expenses - selling expenses	147541	2022-01-21 10:42:23.735905+00	2022-01-21 10:42:23.735945+00	9	\N	\N	f	f
9103	CATEGORY	Category	Travel Expenses which supports National - International	142234	2022-01-21 10:42:23.766074+00	2022-01-21 10:42:23.766161+00	9	\N	\N	f	f
9104	CATEGORY	Category	Travelling Charges	143130	2022-01-21 10:42:23.825049+00	2022-01-21 10:42:23.825115+00	9	\N	\N	f	f
9105	CATEGORY	Category	Travel Meals	145040	2022-01-21 10:42:23.825251+00	2022-01-21 10:42:23.825297+00	9	\N	\N	f	f
9106	CATEGORY	Category	UK EXP Account	157678	2022-01-21 10:42:23.825881+00	2022-01-21 10:42:23.825941+00	9	\N	\N	f	f
9107	CATEGORY	Category	UK Expense Acct	157677	2022-01-21 10:42:23.82604+00	2022-01-21 10:42:23.826072+00	9	\N	\N	f	f
9108	CATEGORY	Category	UK Expense Category	157700	2022-01-21 10:42:23.826137+00	2022-01-21 10:42:23.826167+00	9	\N	\N	f	f
9109	CATEGORY	Category	Unapplied Cash Bill Payment Expense	145041	2022-01-21 10:42:23.82623+00	2022-01-21 10:42:23.82626+00	9	\N	\N	f	f
9110	CATEGORY	Category	Unbilled AR	154806	2022-01-21 10:42:23.826322+00	2022-01-21 10:42:23.826367+00	9	\N	\N	f	f
9111	CATEGORY	Category	Unbilled AR - Contract Services	154798	2022-01-21 10:42:23.82643+00	2022-01-21 10:42:23.826459+00	9	\N	\N	f	f
9112	CATEGORY	Category	Unbilled AR - Contract Subscriptions	154804	2022-01-21 10:42:23.826522+00	2022-01-21 10:42:23.826551+00	9	\N	\N	f	f
9113	CATEGORY	Category	Unbilled AR - Contract Usage	154799	2022-01-21 10:42:23.826612+00	2022-01-21 10:42:23.826641+00	9	\N	\N	f	f
9114	CATEGORY	Category	Unbuild Variance	147283	2022-01-21 10:42:23.826703+00	2022-01-21 10:42:23.826733+00	9	\N	\N	f	f
9115	CATEGORY	Category	Uncategorised Expense	147542	2022-01-21 10:42:23.826794+00	2022-01-21 10:42:23.826823+00	9	\N	\N	f	f
9116	CATEGORY	Category	Uncategorized Expense	145042	2022-01-21 10:42:23.826885+00	2022-01-21 10:42:23.826915+00	9	\N	\N	f	f
9117	CATEGORY	Category	Undeposited Funds	147227	2022-01-21 10:42:23.826977+00	2022-01-21 10:42:23.827006+00	9	\N	\N	f	f
9118	CATEGORY	Category	Unrealized Currency Gain and Loss	154785	2022-01-21 10:42:23.827068+00	2022-01-21 10:42:23.827097+00	9	\N	\N	f	f
9119	CATEGORY	Category	Unrealized Gain-Loss	147286	2022-01-21 10:42:23.827159+00	2022-01-21 10:42:23.827188+00	9	\N	\N	f	f
9120	CATEGORY	Category	Unspecified	142055	2022-01-21 10:42:23.827249+00	2022-01-21 10:42:23.827278+00	9	\N	\N	f	f
9121	CATEGORY	Category	Utilities	142229	2022-01-21 10:42:23.82734+00	2022-01-21 10:42:23.827369+00	9	\N	\N	f	f
9122	CATEGORY	Category	Utilities - Electric & Gas	147543	2022-01-21 10:42:23.82743+00	2022-01-21 10:42:23.827459+00	9	\N	\N	f	f
9123	CATEGORY	Category	Utilities:Gas and Electric	145056	2022-01-21 10:42:23.827521+00	2022-01-21 10:42:23.835742+00	9	\N	\N	f	f
9124	CATEGORY	Category	Utilities:Telephone	145057	2022-01-21 10:42:23.836026+00	2022-01-21 10:42:23.836081+00	9	\N	\N	f	f
9125	CATEGORY	Category	Utilities:Utilities - Electric & Gas	154561	2022-01-21 10:42:23.836241+00	2022-01-21 10:42:23.885201+00	9	\N	\N	f	f
9126	CATEGORY	Category	Utilities:Utilities - Water	154562	2022-01-21 10:42:23.976676+00	2022-01-21 10:42:23.976816+00	9	\N	\N	f	f
9127	CATEGORY	Category	Utilities - Water	147544	2022-01-21 10:42:23.977075+00	2022-01-21 10:42:23.978167+00	9	\N	\N	f	f
9129	CATEGORY	Category	Valuation Reserves	154783	2022-01-21 10:42:23.979125+00	2022-01-21 10:42:23.979156+00	9	\N	\N	f	f
9130	CATEGORY	Category	VAT on Purchases	157676	2022-01-21 10:42:23.97937+00	2022-01-21 10:42:23.979409+00	9	\N	\N	f	f
9131	CATEGORY	Category	Vehicle Registration	147260	2022-01-21 10:42:23.979739+00	2022-01-21 10:42:23.979867+00	9	\N	\N	f	f
9132	CATEGORY	Category	Vendor Rebates	147294	2022-01-21 10:42:23.97995+00	2022-01-21 10:42:23.979983+00	9	\N	\N	f	f
9133	CATEGORY	Category	Vendor Return Variance	147296	2022-01-21 10:42:23.980209+00	2022-01-21 10:42:23.980247+00	9	\N	\N	f	f
9134	CATEGORY	Category	Wage expenses	147545	2022-01-21 10:42:23.980763+00	2022-01-21 10:42:23.980808+00	9	\N	\N	f	f
9135	CATEGORY	Category	WET Paid	147765	2022-01-21 10:42:23.980884+00	2022-01-21 10:42:23.980954+00	9	\N	\N	f	f
9136	CATEGORY	Category	WIP	147287	2022-01-21 10:42:23.981062+00	2022-01-21 10:42:23.981272+00	9	\N	\N	f	f
9137	CATEGORY	Category	WIP COGS	147289	2022-01-21 10:42:23.981351+00	2022-01-21 10:42:23.981616+00	9	\N	\N	f	f
9138	CATEGORY	Category	WIP (Labor Only)	154805	2022-01-21 10:42:23.98177+00	2022-01-21 10:42:23.981869+00	9	\N	\N	f	f
9139	CATEGORY	Category	WIP Revenue	147288	2022-01-21 10:42:23.981962+00	2022-01-21 10:42:23.982071+00	9	\N	\N	f	f
9140	CATEGORY	Category	WIP Variance	147303	2022-01-21 10:42:23.982166+00	2022-01-21 10:42:23.982197+00	9	\N	\N	f	f
9141	CATEGORY	Category	Workers' compensation	147247	2022-01-21 10:42:24.149067+00	2022-01-21 10:42:24.149112+00	9	\N	\N	f	f
9142	COST_CENTER	Cost Center	Administration	7451	2022-01-21 10:42:25.182798+00	2022-01-21 10:42:25.182851+00	9	\N	\N	f	f
9143	COST_CENTER	Cost Center	Analytics	7443	2022-01-21 10:42:25.182971+00	2022-01-21 10:42:25.183016+00	9	\N	\N	f	f
9144	COST_CENTER	Cost Center	F & A	7452	2022-01-21 10:42:25.183114+00	2022-01-21 10:42:25.183155+00	9	\N	\N	f	f
9145	COST_CENTER	Cost Center	Finance	7446	2022-01-21 10:42:25.183249+00	2022-01-21 10:42:25.183288+00	9	\N	\N	f	f
9146	COST_CENTER	Cost Center	Legal	7449	2022-01-21 10:42:25.183381+00	2022-01-21 10:42:25.18342+00	9	\N	\N	f	f
9147	COST_CENTER	Cost Center	Marketing	7450	2022-01-21 10:42:25.183513+00	2022-01-21 10:42:25.183551+00	9	\N	\N	f	f
9148	COST_CENTER	Cost Center	OPS & Retail	7447	2022-01-21 10:42:25.183642+00	2022-01-21 10:42:25.183681+00	9	\N	\N	f	f
9149	COST_CENTER	Cost Center	Resources	7444	2022-01-21 10:42:25.18377+00	2022-01-21 10:42:25.183808+00	9	\N	\N	f	f
9150	COST_CENTER	Cost Center	Sales and Cross	7445	2022-01-21 10:42:25.183898+00	2022-01-21 10:42:25.183936+00	9	\N	\N	f	f
9151	COST_CENTER	Cost Center	Strategy Planning	7448	2022-01-21 10:42:25.184024+00	2022-01-21 10:42:25.184062+00	9	\N	\N	f	f
9152	PROJECT	Project	3M	261307	2022-01-21 10:42:28.664663+00	2022-01-21 10:42:28.664939+00	9	\N	\N	f	f
9153	PROJECT	Project	Aaron Abbott	261308	2022-01-21 10:42:28.665129+00	2022-01-21 10:42:28.665189+00	9	\N	\N	f	f
9154	PROJECT	Project	Abercrombie International Group	285873	2022-01-21 10:42:28.665315+00	2022-01-21 10:42:28.665368+00	9	\N	\N	f	f
9155	PROJECT	Project	AB&I Holdings	261309	2022-01-21 10:42:28.665499+00	2022-01-21 10:42:28.66555+00	9	\N	\N	f	f
9156	PROJECT	Project	Absolute Location Support	261310	2022-01-21 10:42:28.665828+00	2022-01-21 10:42:28.665883+00	9	\N	\N	f	f
9157	PROJECT	Project	Academy Avenue Liquor Store	261311	2022-01-21 10:42:28.666007+00	2022-01-21 10:42:28.669272+00	9	\N	\N	f	f
9158	PROJECT	Project	Academy Sports & Outdoors	261312	2022-01-21 10:42:28.671105+00	2022-01-21 10:42:28.671244+00	9	\N	\N	f	f
9159	PROJECT	Project	Academy Vision Science Clinic	261313	2022-01-21 10:42:28.671374+00	2022-01-21 10:42:28.671418+00	9	\N	\N	f	f
9160	PROJECT	Project	Accountants Inc	261314	2022-01-21 10:42:28.671515+00	2022-01-21 10:42:28.671556+00	9	\N	\N	f	f
9161	PROJECT	Project	Acera	261315	2022-01-21 10:42:28.67202+00	2022-01-21 10:42:28.672091+00	9	\N	\N	f	f
9162	PROJECT	Project	Acme Systems Incorporated	261316	2022-01-21 10:42:28.672208+00	2022-01-21 10:42:28.672241+00	9	\N	\N	f	f
9163	PROJECT	Project	ACM Group	261317	2022-01-21 10:42:28.672323+00	2022-01-21 10:42:28.672362+00	9	\N	\N	f	f
9164	PROJECT	Project	AcuVision Eye Centre	261318	2022-01-21 10:42:28.672439+00	2022-01-21 10:42:28.672472+00	9	\N	\N	f	f
9165	PROJECT	Project	Advanced Design & Drafting Ltd	261319	2022-01-21 10:42:28.677043+00	2022-01-21 10:42:28.679748+00	9	\N	\N	f	f
9166	PROJECT	Project	Advanced Machining Techniques Inc.	261320	2022-01-21 10:42:28.680209+00	2022-01-21 10:42:28.680272+00	9	\N	\N	f	f
9167	PROJECT	Project	Adwin Ko	278559	2022-01-21 10:42:28.684717+00	2022-01-21 10:42:28.684855+00	9	\N	\N	f	f
9168	PROJECT	Project	Agrela Apartments Agency	261321	2022-01-21 10:42:28.690315+00	2022-01-21 10:42:28.690825+00	9	\N	\N	f	f
9169	PROJECT	Project	Ahonen Catering Group	261322	2022-01-21 10:42:28.691597+00	2022-01-21 10:42:28.691671+00	9	\N	\N	f	f
9170	PROJECT	Project	AIM Accounting	261323	2022-01-21 10:42:28.691807+00	2022-01-21 10:42:28.691851+00	9	\N	\N	f	f
9171	PROJECT	Project	AIQ Networks	261324	2022-01-21 10:42:28.705726+00	2022-01-21 10:42:28.706084+00	9	\N	\N	f	f
9172	PROJECT	Project	Alain Henderson	261325	2022-01-21 10:42:28.706255+00	2022-01-21 10:42:28.706303+00	9	\N	\N	f	f
9173	PROJECT	Project	Alamo Catering Group	261326	2022-01-21 10:42:28.706419+00	2022-01-21 10:42:28.706462+00	9	\N	\N	f	f
9174	PROJECT	Project	Alchemy PR	261327	2022-01-21 10:42:28.706584+00	2022-01-21 10:42:28.706625+00	9	\N	\N	f	f
9175	PROJECT	Project	Alesna Leasing Sales	261328	2022-01-21 10:42:28.707103+00	2022-01-21 10:42:28.707147+00	9	\N	\N	f	f
9176	PROJECT	Project	Alex Benedet	261329	2022-01-21 10:42:28.707263+00	2022-01-21 10:42:28.707315+00	9	\N	\N	f	f
9177	PROJECT	Project	Alex Blakey	278560	2022-01-21 10:42:28.707431+00	2022-01-21 10:42:28.708213+00	9	\N	\N	f	f
9178	PROJECT	Project	Alex Fabre	261330	2022-01-21 10:42:28.708592+00	2022-01-21 10:42:28.708652+00	9	\N	\N	f	f
9179	PROJECT	Project	Alex Wolfe	261331	2022-01-21 10:42:28.708794+00	2022-01-21 10:42:28.70922+00	9	\N	\N	f	f
9180	PROJECT	Project	All-Lift Inc	261332	2022-01-21 10:42:28.711137+00	2022-01-21 10:42:28.711211+00	9	\N	\N	f	f
9181	PROJECT	Project	All Occassions Event Coordination	261333	2022-01-21 10:42:28.711341+00	2022-01-21 10:42:28.711381+00	9	\N	\N	f	f
9182	PROJECT	Project	All Outdoors	261334	2022-01-21 10:42:28.711478+00	2022-01-21 10:42:28.711511+00	9	\N	\N	f	f
9183	PROJECT	Project	All World Produce	261335	2022-01-21 10:42:28.712381+00	2022-01-21 10:42:28.712462+00	9	\N	\N	f	f
9184	PROJECT	Project	Alpart	261336	2022-01-21 10:42:28.712807+00	2022-01-21 10:42:28.712862+00	9	\N	\N	f	f
9185	PROJECT	Project	Alpine Cafe and Wine Bar	261337	2022-01-21 10:42:28.712985+00	2022-01-21 10:42:28.713017+00	9	\N	\N	f	f
9186	PROJECT	Project	Altamirano Apartments Services	261338	2022-01-21 10:42:28.713081+00	2022-01-21 10:42:28.71311+00	9	\N	\N	f	f
9187	PROJECT	Project	Altonen Windows Rentals	261339	2022-01-21 10:42:28.713171+00	2022-01-21 10:42:28.7132+00	9	\N	\N	f	f
9188	PROJECT	Project	Amarillo Apartments Distributors	261340	2022-01-21 10:42:28.71367+00	2022-01-21 10:42:28.713717+00	9	\N	\N	f	f
9189	PROJECT	Project	Ambc	261341	2022-01-21 10:42:28.718956+00	2022-01-21 10:42:28.719065+00	9	\N	\N	f	f
9190	PROJECT	Project	AmerCaire	261342	2022-01-21 10:42:28.719484+00	2022-01-21 10:42:28.720031+00	9	\N	\N	f	f
9191	PROJECT	Project	AMG Inc	261343	2022-01-21 10:42:28.721031+00	2022-01-21 10:42:28.721199+00	9	\N	\N	f	f
9192	PROJECT	Project	Ammann Builders Fabricators	261344	2022-01-21 10:42:28.72142+00	2022-01-21 10:42:28.721744+00	9	\N	\N	f	f
9193	PROJECT	Project	Amsterdam Drug Store	261345	2022-01-21 10:42:28.721839+00	2022-01-21 10:42:28.721862+00	9	\N	\N	f	f
9194	PROJECT	Project	Amy Kall	261346	2022-01-21 10:42:28.721916+00	2022-01-21 10:42:28.721944+00	9	\N	\N	f	f
9195	PROJECT	Project	Anderson Boughton Inc.	261347	2022-01-21 10:42:28.721996+00	2022-01-21 10:42:28.722025+00	9	\N	\N	f	f
9196	PROJECT	Project	Andersson Hospital Inc.	261348	2022-01-21 10:42:28.722475+00	2022-01-21 10:42:28.722534+00	9	\N	\N	f	f
9197	PROJECT	Project	Andrew Mager	261349	2022-01-21 10:42:28.722903+00	2022-01-21 10:42:28.722972+00	9	\N	\N	f	f
9198	PROJECT	Project	Andy Johnson	261350	2022-01-21 10:42:28.72313+00	2022-01-21 10:42:28.723182+00	9	\N	\N	f	f
9199	PROJECT	Project	Andy Thompson	261351	2022-01-21 10:42:28.72332+00	2022-01-21 10:42:28.723363+00	9	\N	\N	f	f
9200	PROJECT	Project	Angerman Markets Company	261352	2022-01-21 10:42:28.723706+00	2022-01-21 10:42:28.72379+00	9	\N	\N	f	f
9201	PROJECT	Project	Anonymous Customer HQ	261353	2022-01-21 10:42:28.723948+00	2022-01-21 10:42:28.724003+00	9	\N	\N	f	f
9202	PROJECT	Project	Another Killer Product	261354	2022-01-21 10:42:28.744539+00	2022-01-21 10:42:28.744584+00	9	\N	\N	f	f
9203	PROJECT	Project	Another Killer Product 1	261355	2022-01-21 10:42:28.744649+00	2022-01-21 10:42:28.744679+00	9	\N	\N	f	f
9204	PROJECT	Project	Anthony Jacobs	261356	2022-01-21 10:42:28.744741+00	2022-01-21 10:42:28.744771+00	9	\N	\N	f	f
9205	PROJECT	Project	Antioch Construction Company	261357	2022-01-21 10:42:28.744832+00	2022-01-21 10:42:28.744862+00	9	\N	\N	f	f
9206	PROJECT	Project	Apfel Electric Co.	261358	2022-01-21 10:42:28.745322+00	2022-01-21 10:42:28.745811+00	9	\N	\N	f	f
9207	PROJECT	Project	Applications to go Inc	261359	2022-01-21 10:42:28.746027+00	2022-01-21 10:42:28.746084+00	9	\N	\N	f	f
9208	PROJECT	Project	Aquino Apartments Dynamics	261360	2022-01-21 10:42:28.746305+00	2022-01-21 10:42:28.746633+00	9	\N	\N	f	f
9209	PROJECT	Project	Arcizo Automotive Sales	261361	2022-01-21 10:42:28.746969+00	2022-01-21 10:42:28.747038+00	9	\N	\N	f	f
9210	PROJECT	Project	Arlington Software Management	261362	2022-01-21 10:42:28.747203+00	2022-01-21 10:42:28.747257+00	9	\N	\N	f	f
9211	PROJECT	Project	Arnold Tanner	261363	2022-01-21 10:42:28.755877+00	2022-01-21 10:42:28.756053+00	9	\N	\N	f	f
9212	PROJECT	Project	Arredla and Hillseth Hardware -	261364	2022-01-21 10:42:28.756389+00	2022-01-21 10:42:28.756475+00	9	\N	\N	f	f
9213	PROJECT	Project	Art Institute of California	261365	2022-01-21 10:42:28.756629+00	2022-01-21 10:42:28.756688+00	9	\N	\N	f	f
9214	PROJECT	Project	Asch _ Agency	261366	2022-01-21 10:42:28.756822+00	2022-01-21 10:42:28.757135+00	9	\N	\N	f	f
9215	PROJECT	Project	Ashley Smoth	261367	2022-01-21 10:42:28.757404+00	2022-01-21 10:42:28.757494+00	9	\N	\N	f	f
9216	PROJECT	Project	Ashton Consulting Ltd	261368	2022-01-21 10:42:28.757633+00	2022-01-21 10:42:28.757676+00	9	\N	\N	f	f
9217	PROJECT	Project	Aslanian Publishing Agency	261369	2022-01-21 10:42:28.758091+00	2022-01-21 10:42:28.758145+00	9	\N	\N	f	f
9218	PROJECT	Project	Astry Software Holding Corp.	261370	2022-01-21 10:42:28.758271+00	2022-01-21 10:42:28.758321+00	9	\N	\N	f	f
9219	PROJECT	Project	Atherton Grocery	261371	2022-01-21 10:42:28.758439+00	2022-01-21 10:42:28.758498+00	9	\N	\N	f	f
9220	PROJECT	Project	August Li	261372	2022-01-21 10:42:28.758758+00	2022-01-21 10:42:28.758813+00	9	\N	\N	f	f
9221	PROJECT	Project	Ausbrooks Construction Incorporated	261373	2022-01-21 10:42:28.758926+00	2022-01-21 10:42:28.758971+00	9	\N	\N	f	f
9222	PROJECT	Project	Austin Builders Distributors	261374	2022-01-21 10:42:28.7591+00	2022-01-21 10:42:28.759145+00	9	\N	\N	f	f
9223	PROJECT	Project	Austin Publishing Inc.	261375	2022-01-21 10:42:28.759322+00	2022-01-21 10:42:28.759648+00	9	\N	\N	f	f
9224	PROJECT	Project	Avac Supplies Ltd.	261376	2022-01-21 10:42:28.759805+00	2022-01-21 10:42:28.759858+00	9	\N	\N	f	f
9225	PROJECT	Project	Avani Walters	261377	2022-01-21 10:42:28.760002+00	2022-01-21 10:42:28.760057+00	9	\N	\N	f	f
9226	PROJECT	Project	Axxess Group	261378	2022-01-21 10:42:28.760382+00	2022-01-21 10:42:28.760447+00	9	\N	\N	f	f
9227	PROJECT	Project	Baim Lumber -	261379	2022-01-21 10:42:28.760576+00	2022-01-21 10:42:28.760614+00	9	\N	\N	f	f
9228	PROJECT	Project	Bakkala Catering Distributors	261380	2022-01-21 10:42:28.760721+00	2022-01-21 10:42:28.760763+00	9	\N	\N	f	f
9229	PROJECT	Project	Bankey and Marris Hardware Corporation	261381	2022-01-21 10:42:28.760892+00	2022-01-21 10:42:28.760934+00	9	\N	\N	f	f
9230	PROJECT	Project	Barham Automotive Services	261382	2022-01-21 10:42:28.761034+00	2022-01-21 10:42:28.761073+00	9	\N	\N	f	f
9231	PROJECT	Project	Barich Metal Fabricators Inc.	261383	2022-01-21 10:42:28.761724+00	2022-01-21 10:42:28.761859+00	9	\N	\N	f	f
9232	PROJECT	Project	Barners and Rushlow Liquors Sales	261384	2022-01-21 10:42:28.761997+00	2022-01-21 10:42:28.762038+00	9	\N	\N	f	f
9233	PROJECT	Project	Barnhurst Title Inc.	261385	2022-01-21 10:42:28.762463+00	2022-01-21 10:42:28.762531+00	9	\N	\N	f	f
9234	PROJECT	Project	Baron Chess	261386	2022-01-21 10:42:28.76264+00	2022-01-21 10:42:28.762688+00	9	\N	\N	f	f
9235	PROJECT	Project	Bartkus Automotive Company	261387	2022-01-21 10:42:28.762816+00	2022-01-21 10:42:28.762866+00	9	\N	\N	f	f
9236	PROJECT	Project	Baumgarn Windows and Associates	261388	2022-01-21 10:42:28.76297+00	2022-01-21 10:42:28.763012+00	9	\N	\N	f	f
9237	PROJECT	Project	Bayas Hardware Dynamics	261389	2022-01-21 10:42:28.765468+00	2022-01-21 10:42:28.765606+00	9	\N	\N	f	f
9238	PROJECT	Project	Baylore	261390	2022-01-21 10:42:28.766048+00	2022-01-21 10:42:28.766194+00	9	\N	\N	f	f
9239	PROJECT	Project	Bay Media Research	261391	2022-01-21 10:42:28.768527+00	2022-01-21 10:42:28.76861+00	9	\N	\N	f	f
9240	PROJECT	Project	BaySide Office Space	261392	2022-01-21 10:42:28.768948+00	2022-01-21 10:42:28.768979+00	9	\N	\N	f	f
9241	PROJECT	Project	Beams Electric Agency	261393	2022-01-21 10:42:28.769044+00	2022-01-21 10:42:28.769074+00	9	\N	\N	f	f
9242	PROJECT	Project	Beatie Leasing Networking	261394	2022-01-21 10:42:28.769134+00	2022-01-21 10:42:28.76916+00	9	\N	\N	f	f
9243	PROJECT	Project	Beattie Batteries	261395	2022-01-21 10:42:28.769206+00	2022-01-21 10:42:28.769227+00	9	\N	\N	f	f
9244	PROJECT	Project	Beaubien Antiques Leasing	261396	2022-01-21 10:42:28.769287+00	2022-01-21 10:42:28.769317+00	9	\N	\N	f	f
9245	PROJECT	Project	Belgrade Telecom -	261397	2022-01-21 10:42:28.770004+00	2022-01-21 10:42:28.770056+00	9	\N	\N	f	f
9246	PROJECT	Project	Belisle Title Networking	261398	2022-01-21 10:42:28.770168+00	2022-01-21 10:42:28.770211+00	9	\N	\N	f	f
9247	PROJECT	Project	Below Liquors Corporation	261399	2022-01-21 10:42:28.770312+00	2022-01-21 10:42:28.770355+00	9	\N	\N	f	f
9248	PROJECT	Project	Bemo Publishing Corporation	261400	2022-01-21 10:42:28.770456+00	2022-01-21 10:42:28.770496+00	9	\N	\N	f	f
9249	PROJECT	Project	Benabides and Louris Builders Services	261401	2022-01-21 10:42:28.770591+00	2022-01-21 10:42:28.77063+00	9	\N	\N	f	f
9250	PROJECT	Project	Benbow Software	261402	2022-01-21 10:42:28.770725+00	2022-01-21 10:42:28.770765+00	9	\N	\N	f	f
9251	PROJECT	Project	Benge Liquors Incorporated	261403	2022-01-21 10:42:28.770861+00	2022-01-21 10:42:28.770902+00	9	\N	\N	f	f
9252	PROJECT	Project	Benjamin Yeung	278561	2022-01-21 10:42:28.79297+00	2022-01-21 10:42:28.793012+00	9	\N	\N	f	f
9253	PROJECT	Project	Ben Lomond Software Incorporated	261404	2022-01-21 10:42:28.793075+00	2022-01-21 10:42:28.793105+00	9	\N	\N	f	f
9254	PROJECT	Project	Bennett Consulting	261405	2022-01-21 10:42:28.793167+00	2022-01-21 10:42:28.793197+00	9	\N	\N	f	f
9255	PROJECT	Project	Ben Sandler	261406	2022-01-21 10:42:28.793258+00	2022-01-21 10:42:28.793287+00	9	\N	\N	f	f
9256	PROJECT	Project	Benton Construction Inc.	261407	2022-01-21 10:42:28.793348+00	2022-01-21 10:42:28.793377+00	9	\N	\N	f	f
9257	PROJECT	Project	Berliner Apartments Networking	261408	2022-01-21 10:42:28.793438+00	2022-01-21 10:42:28.793467+00	9	\N	\N	f	f
9258	PROJECT	Project	Berschauer Leasing Rentals	261409	2022-01-21 10:42:28.793529+00	2022-01-21 10:42:28.793558+00	9	\N	\N	f	f
9259	PROJECT	Project	Berthelette Antiques	261410	2022-01-21 10:42:28.793619+00	2022-01-21 10:42:28.793897+00	9	\N	\N	f	f
9260	PROJECT	Project	Bertot Attorneys Company	261411	2022-01-21 10:42:28.794145+00	2022-01-21 10:42:28.794202+00	9	\N	\N	f	f
9261	PROJECT	Project	Bertulli & Assoc	261412	2022-01-21 10:42:28.794325+00	2022-01-21 10:42:28.794372+00	9	\N	\N	f	f
9262	PROJECT	Project	Bethurum Telecom Sales	261413	2022-01-21 10:42:28.794729+00	2022-01-21 10:42:28.794801+00	9	\N	\N	f	f
9263	PROJECT	Project	Better Buy	261414	2022-01-21 10:42:28.794897+00	2022-01-21 10:42:28.794929+00	9	\N	\N	f	f
9264	PROJECT	Project	Bezak Construction Dynamics	261415	2022-01-21 10:42:28.794998+00	2022-01-21 10:42:28.795029+00	9	\N	\N	f	f
9265	PROJECT	Project	BFI Inc	261416	2022-01-21 10:42:28.795092+00	2022-01-21 10:42:28.795122+00	9	\N	\N	f	f
9266	PROJECT	Project	Bicycle Trailers	261417	2022-01-21 10:42:28.795183+00	2022-01-21 10:42:28.795213+00	9	\N	\N	f	f
9267	PROJECT	Project	Big 5 Sporting Goods	261418	2022-01-21 10:42:28.795273+00	2022-01-21 10:42:28.795302+00	9	\N	\N	f	f
9268	PROJECT	Project	Big Bear Lake Electric	261419	2022-01-21 10:42:28.795363+00	2022-01-21 10:42:28.795392+00	9	\N	\N	f	f
9269	PROJECT	Project	Big Bear Lake Plumbing Holding Corp.	261420	2022-01-21 10:42:28.795712+00	2022-01-21 10:42:28.795818+00	9	\N	\N	f	f
9270	PROJECT	Project	Billafuerte Software Company	261421	2022-01-21 10:42:28.795941+00	2022-01-21 10:42:28.795991+00	9	\N	\N	f	f
9271	PROJECT	Project	Bill's Windsurf Shop	274664	2022-01-21 10:42:28.796278+00	2022-01-21 10:42:28.796319+00	9	\N	\N	f	f
9272	PROJECT	Project	Bisonette Leasing	261422	2022-01-21 10:42:28.796384+00	2022-01-21 10:42:28.796414+00	9	\N	\N	f	f
9273	PROJECT	Project	Bleser Antiques Incorporated	261423	2022-01-21 10:42:28.796781+00	2022-01-21 10:42:28.79687+00	9	\N	\N	f	f
9274	PROJECT	Project	Blier Lumber Dynamics	261424	2022-01-21 10:42:28.79696+00	2022-01-21 10:42:28.796992+00	9	\N	\N	f	f
9275	PROJECT	Project	Blue Street Liquor Store	261425	2022-01-21 10:42:28.797054+00	2022-01-21 10:42:28.797084+00	9	\N	\N	f	f
9276	PROJECT	Project	Bobby Kelly	261426	2022-01-21 10:42:28.797146+00	2022-01-21 10:42:28.797177+00	9	\N	\N	f	f
9277	PROJECT	Project	Bobby Strands (Bobby@Strands.com)	261427	2022-01-21 10:42:28.79727+00	2022-01-21 10:42:28.797311+00	9	\N	\N	f	f
9278	PROJECT	Project	Bob Ledner	261428	2022-01-21 10:42:28.797406+00	2022-01-21 10:42:28.79745+00	9	\N	\N	f	f
9279	PROJECT	Project	Bob Smith (bsmith@bobsmith.com)	261429	2022-01-21 10:42:28.797547+00	2022-01-21 10:42:28.79759+00	9	\N	\N	f	f
9280	PROJECT	Project	Bob Walsh Funiture Store	261430	2022-01-21 10:42:28.797686+00	2022-01-21 10:42:28.797728+00	9	\N	\N	f	f
9281	PROJECT	Project	Bochenek and Skoog Liquors Company	261431	2022-01-21 10:42:28.797822+00	2022-01-21 10:42:28.797865+00	9	\N	\N	f	f
9282	PROJECT	Project	Bodfish Liquors Corporation	261432	2022-01-21 10:42:28.79796+00	2022-01-21 10:42:28.798002+00	9	\N	\N	f	f
9283	PROJECT	Project	Boise Antiques and Associates	261433	2022-01-21 10:42:28.798097+00	2022-01-21 10:42:28.798142+00	9	\N	\N	f	f
9284	PROJECT	Project	Boise Publishing Co.	261434	2022-01-21 10:42:28.798241+00	2022-01-21 10:42:28.798285+00	9	\N	\N	f	f
9285	PROJECT	Project	Boisselle Windows Distributors	261435	2022-01-21 10:42:28.798384+00	2022-01-21 10:42:28.798428+00	9	\N	\N	f	f
9286	PROJECT	Project	Bolder Construction Inc.	261436	2022-01-21 10:42:28.798527+00	2022-01-21 10:42:28.798569+00	9	\N	\N	f	f
9287	PROJECT	Project	Bollman Attorneys Company	261437	2022-01-21 10:42:28.798663+00	2022-01-21 10:42:28.798705+00	9	\N	\N	f	f
9288	PROJECT	Project	Bona Source	261438	2022-01-21 10:42:28.798806+00	2022-01-21 10:42:28.79885+00	9	\N	\N	f	f
9289	PROJECT	Project	Boney Electric Dynamics	261439	2022-01-21 10:42:28.798957+00	2022-01-21 10:42:28.798999+00	9	\N	\N	f	f
9290	PROJECT	Project	Borowski Catering Management	261440	2022-01-21 10:42:28.799102+00	2022-01-21 10:42:28.799147+00	9	\N	\N	f	f
9291	PROJECT	Project	Botero Electric Co.	261441	2022-01-21 10:42:28.799244+00	2022-01-21 10:42:28.799288+00	9	\N	\N	f	f
9292	PROJECT	Project	Bowling Green Painting Incorporated	261442	2022-01-21 10:42:28.79942+00	2022-01-21 10:42:28.799463+00	9	\N	\N	f	f
9293	PROJECT	Project	Boynton Beach Title Networking	261443	2022-01-21 10:42:28.799564+00	2022-01-21 10:42:28.79961+00	9	\N	\N	f	f
9294	PROJECT	Project	Bracken Works Inc	261444	2022-01-21 10:42:28.799713+00	2022-01-21 10:42:28.799756+00	9	\N	\N	f	f
9295	PROJECT	Project	Braithwaite Tech	261445	2022-01-21 10:42:28.800058+00	2022-01-21 10:42:28.800114+00	9	\N	\N	f	f
9296	PROJECT	Project	Bramucci Construction	261446	2022-01-21 10:42:28.800262+00	2022-01-21 10:42:28.800311+00	9	\N	\N	f	f
9297	PROJECT	Project	Branding Analysis	284496	2022-01-21 10:42:28.800432+00	2022-01-21 10:42:28.800479+00	9	\N	\N	f	f
9298	PROJECT	Project	Branding Follow Up	284497	2022-01-21 10:42:28.800594+00	2022-01-21 10:42:28.800645+00	9	\N	\N	f	f
9299	PROJECT	Project	Brandwein Builders Fabricators	261447	2022-01-21 10:42:28.800758+00	2022-01-21 10:42:28.801174+00	9	\N	\N	f	f
9300	PROJECT	Project	Brea Painting Company	261448	2022-01-21 10:42:28.80226+00	2022-01-21 10:42:28.802625+00	9	\N	\N	f	f
9301	PROJECT	Project	Brent Apartments Rentals	261449	2022-01-21 10:42:28.802803+00	2022-01-21 10:42:28.802852+00	9	\N	\N	f	f
9302	PROJECT	Project	Brewers Retail	261450	2022-01-21 10:42:28.824591+00	2022-01-21 10:42:28.824659+00	9	\N	\N	f	f
9303	PROJECT	Project	Brick Metal Fabricators Services	261451	2022-01-21 10:42:28.824776+00	2022-01-21 10:42:28.824823+00	9	\N	\N	f	f
9304	PROJECT	Project	Bridgham Electric Inc.	261452	2022-01-21 10:42:28.824926+00	2022-01-21 10:42:28.824967+00	9	\N	\N	f	f
9305	PROJECT	Project	Bright Brothers Design	261453	2022-01-21 10:42:28.825068+00	2022-01-21 10:42:28.825111+00	9	\N	\N	f	f
9306	PROJECT	Project	Broadnay and Posthuma Lumber and Associates	261454	2022-01-21 10:42:28.825212+00	2022-01-21 10:42:28.825253+00	9	\N	\N	f	f
9307	PROJECT	Project	Brochard Metal Fabricators Incorporated	261455	2022-01-21 10:42:28.825354+00	2022-01-21 10:42:28.825394+00	9	\N	\N	f	f
9308	PROJECT	Project	Brosey Antiques	284385	2022-01-21 10:42:28.82549+00	2022-01-21 10:42:28.825529+00	9	\N	\N	f	f
9309	PROJECT	Project	Brosey Antiques -	261456	2022-01-21 10:42:28.825623+00	2022-01-21 10:42:28.825663+00	9	\N	\N	f	f
9310	PROJECT	Project	Bruce Storm	261457	2022-01-21 10:42:28.825755+00	2022-01-21 10:42:28.825795+00	9	\N	\N	f	f
9311	PROJECT	Project	Brutsch Builders Incorporated	261458	2022-01-21 10:42:28.825888+00	2022-01-21 10:42:28.825929+00	9	\N	\N	f	f
9312	PROJECT	Project	Brytor Inetrnational	261459	2022-01-21 10:42:28.826022+00	2022-01-21 10:42:28.826062+00	9	\N	\N	f	f
9313	PROJECT	Project	B-Sharp Music	261460	2022-01-21 10:42:28.826154+00	2022-01-21 10:42:28.826194+00	9	\N	\N	f	f
9314	PROJECT	Project	Burney and Oesterreich Title Manufacturing	261461	2022-01-21 10:42:28.826287+00	2022-01-21 10:42:28.826328+00	9	\N	\N	f	f
9315	PROJECT	Project	Buroker Markets Incorporated	261462	2022-01-21 10:42:28.826421+00	2022-01-21 10:42:28.826462+00	9	\N	\N	f	f
9316	PROJECT	Project	Busacker Liquors Services	261463	2022-01-21 10:42:28.826555+00	2022-01-21 10:42:28.826596+00	9	\N	\N	f	f
9317	PROJECT	Project	Bushnell	261464	2022-01-21 10:42:28.82669+00	2022-01-21 10:42:28.82673+00	9	\N	\N	f	f
9318	PROJECT	Project	By The Beach Cafe	261465	2022-01-21 10:42:28.826824+00	2022-01-21 10:42:28.826864+00	9	\N	\N	f	f
9319	PROJECT	Project	Caleb Attorneys Distributors	261466	2022-01-21 10:42:28.826957+00	2022-01-21 10:42:28.826997+00	9	\N	\N	f	f
9320	PROJECT	Project	Calley Leasing and Associates	261467	2022-01-21 10:42:28.82709+00	2022-01-21 10:42:28.82713+00	9	\N	\N	f	f
9321	PROJECT	Project	Cambareri Painting Sales	261468	2022-01-21 10:42:28.827223+00	2022-01-21 10:42:28.827263+00	9	\N	\N	f	f
9322	PROJECT	Project	Canadian Customer	261469	2022-01-21 10:42:28.827357+00	2022-01-21 10:42:28.827397+00	9	\N	\N	f	f
9323	PROJECT	Project	Canuck Door Systems Co.	261470	2022-01-21 10:42:28.827489+00	2022-01-21 10:42:28.827529+00	9	\N	\N	f	f
9324	PROJECT	Project	Capano Labs	261471	2022-01-21 10:42:28.827822+00	2022-01-21 10:42:28.827869+00	9	\N	\N	f	f
9325	PROJECT	Project	Caquias and Jank Catering Distributors	261472	2022-01-21 10:42:28.827973+00	2022-01-21 10:42:28.828017+00	9	\N	\N	f	f
9326	PROJECT	Project	Careymon Dudley	261473	2022-01-21 10:42:28.828117+00	2022-01-21 10:42:28.82816+00	9	\N	\N	f	f
9327	PROJECT	Project	Carloni Builders Company	261474	2022-01-21 10:42:28.828261+00	2022-01-21 10:42:28.828303+00	9	\N	\N	f	f
9328	PROJECT	Project	Carlos Beato	261475	2022-01-21 10:42:28.828472+00	2022-01-21 10:42:28.828509+00	9	\N	\N	f	f
9329	PROJECT	Project	Carmel Valley Metal Fabricators Holding Corp.	261476	2022-01-21 10:42:28.828573+00	2022-01-21 10:42:28.828602+00	9	\N	\N	f	f
9330	PROJECT	Project	Carpentersville Publishing	261477	2022-01-21 10:42:28.828749+00	2022-01-21 10:42:28.828793+00	9	\N	\N	f	f
9331	PROJECT	Project	Carpinteria Leasing Services	261478	2022-01-21 10:42:28.828885+00	2022-01-21 10:42:28.828925+00	9	\N	\N	f	f
9332	PROJECT	Project	Carrie Davis	261479	2022-01-21 10:42:28.829017+00	2022-01-21 10:42:28.829057+00	9	\N	\N	f	f
9333	PROJECT	Project	Cash & Warren	261480	2022-01-21 10:42:28.82915+00	2022-01-21 10:42:28.829191+00	9	\N	\N	f	f
9334	PROJECT	Project	Castek Inc	261481	2022-01-21 10:42:28.829282+00	2022-01-21 10:42:28.829322+00	9	\N	\N	f	f
9335	PROJECT	Project	Casuse Liquors Inc.	261482	2022-01-21 10:42:28.829416+00	2022-01-21 10:42:28.829456+00	9	\N	\N	f	f
9336	PROJECT	Project	Cathy Quon	278562	2022-01-21 10:42:28.829551+00	2022-01-21 10:42:28.829592+00	9	\N	\N	f	f
9337	PROJECT	Project	Cathy's Consulting Company	285874	2022-01-21 10:42:28.829686+00	2022-01-21 10:42:28.829726+00	9	\N	\N	f	f
9338	PROJECT	Project	Cathy's Consulting Company:Quon - Employee Party 2014	285875	2022-01-21 10:42:28.829822+00	2022-01-21 10:42:28.829863+00	9	\N	\N	f	f
9339	PROJECT	Project	Cathy's Consulting Company:Quon - Retreat 2014	285876	2022-01-21 10:42:28.829959+00	2022-01-21 10:42:28.83+00	9	\N	\N	f	f
9340	PROJECT	Project	Cathy Thoms	261483	2022-01-21 10:42:28.83016+00	2022-01-21 10:42:28.83029+00	9	\N	\N	f	f
9341	PROJECT	Project	Cawthron and Ullo Windows Corporation	261484	2022-01-21 10:42:28.830402+00	2022-01-21 10:42:28.830442+00	9	\N	\N	f	f
9342	PROJECT	Project	Celia Corp	261485	2022-01-21 10:42:28.830529+00	2022-01-21 10:42:28.830583+00	9	\N	\N	f	f
9343	PROJECT	Project	Central Islip Antiques Fabricators	261486	2022-01-21 10:42:28.836138+00	2022-01-21 10:42:28.836236+00	9	\N	\N	f	f
9344	PROJECT	Project	Cerritos Telecom and Associates	261487	2022-01-21 10:42:28.836392+00	2022-01-21 10:42:28.836435+00	9	\N	\N	f	f
9345	PROJECT	Project	CH2M Hill Ltd	261488	2022-01-21 10:42:28.836937+00	2022-01-21 10:42:28.837018+00	9	\N	\N	f	f
9346	PROJECT	Project	Chadha's Consultants	278563	2022-01-21 10:42:28.837113+00	2022-01-21 10:42:28.837145+00	9	\N	\N	f	f
9347	PROJECT	Project	Chadha's Consultants:Chadha - Employee Training	285877	2022-01-21 10:42:28.837212+00	2022-01-21 10:42:28.837242+00	9	\N	\N	f	f
9348	PROJECT	Project	Chamberlain Service Ltd	261489	2022-01-21 10:42:28.837306+00	2022-01-21 10:42:28.837336+00	9	\N	\N	f	f
9349	PROJECT	Project	Champaign Painting Rentals	261490	2022-01-21 10:42:28.837403+00	2022-01-21 10:42:28.837432+00	9	\N	\N	f	f
9350	PROJECT	Project	Chandrasekara Markets Sales	261491	2022-01-21 10:42:28.837618+00	2022-01-21 10:42:28.83765+00	9	\N	\N	f	f
9351	PROJECT	Project	Channer Antiques Dynamics	261492	2022-01-21 10:42:28.837712+00	2022-01-21 10:42:28.837742+00	9	\N	\N	f	f
9352	PROJECT	Project	Charlie Whitehead	278564	2022-01-21 10:42:28.843913+00	2022-01-21 10:42:28.843963+00	9	\N	\N	f	f
9353	PROJECT	Project	Charlotte Hospital Incorporated	261493	2022-01-21 10:42:28.84404+00	2022-01-21 10:42:28.844074+00	9	\N	\N	f	f
9354	PROJECT	Project	Cheese Factory	261494	2022-01-21 10:42:28.844141+00	2022-01-21 10:42:28.844173+00	9	\N	\N	f	f
9355	PROJECT	Project	Cheng-Cheng Lok	278565	2022-01-21 10:42:28.844236+00	2022-01-21 10:42:28.844266+00	9	\N	\N	f	f
9356	PROJECT	Project	Chess Art Gallery	261495	2022-01-21 10:42:28.844331+00	2022-01-21 10:42:28.844361+00	9	\N	\N	f	f
9357	PROJECT	Project	Chiaminto Attorneys Agency	261496	2022-01-21 10:42:28.844423+00	2022-01-21 10:42:28.844453+00	9	\N	\N	f	f
9358	PROJECT	Project	China Cuisine	261497	2022-01-21 10:42:28.844515+00	2022-01-21 10:42:28.844545+00	9	\N	\N	f	f
9359	PROJECT	Project	Chittenden _ Agency	261498	2022-01-21 10:42:28.844606+00	2022-01-21 10:42:28.844637+00	9	\N	\N	f	f
9360	PROJECT	Project	CICA	261499	2022-01-21 10:42:28.844697+00	2022-01-21 10:42:28.844727+00	9	\N	\N	f	f
9361	PROJECT	Project	Cino & Cino	261500	2022-01-21 10:42:28.844788+00	2022-01-21 10:42:28.844818+00	9	\N	\N	f	f
9362	PROJECT	Project	Circuit Cities	261501	2022-01-21 10:42:28.844879+00	2022-01-21 10:42:28.844908+00	9	\N	\N	f	f
9363	PROJECT	Project	CIS Environmental Services	261502	2022-01-21 10:42:28.844969+00	2022-01-21 10:42:28.844999+00	9	\N	\N	f	f
9364	PROJECT	Project	Clayton and Bubash Telecom Services	261503	2022-01-21 10:42:28.84506+00	2022-01-21 10:42:28.845089+00	9	\N	\N	f	f
9365	PROJECT	Project	Clement's Cleaners	278566	2022-01-21 10:42:28.84515+00	2022-01-21 10:42:28.845179+00	9	\N	\N	f	f
9366	PROJECT	Project	Clubb Electric Co.	261504	2022-01-21 10:42:28.84524+00	2022-01-21 10:42:28.84527+00	9	\N	\N	f	f
9367	PROJECT	Project	Cochell Markets Group	261505	2022-01-21 10:42:28.845331+00	2022-01-21 10:42:28.84536+00	9	\N	\N	f	f
9368	PROJECT	Project	Coen Publishing Co.	261506	2022-01-21 10:42:28.845421+00	2022-01-21 10:42:28.84545+00	9	\N	\N	f	f
9369	PROJECT	Project	Coklow Leasing Dynamics	261507	2022-01-21 10:42:28.845511+00	2022-01-21 10:42:28.84554+00	9	\N	\N	f	f
9370	PROJECT	Project	Coletta Hospital Inc.	261508	2022-01-21 10:42:28.8456+00	2022-01-21 10:42:28.845629+00	9	\N	\N	f	f
9371	PROJECT	Project	Colony Antiques	261509	2022-01-21 10:42:28.845689+00	2022-01-21 10:42:28.845719+00	9	\N	\N	f	f
9372	PROJECT	Project	Colorado Springs Leasing Fabricators	261510	2022-01-21 10:42:28.845779+00	2022-01-21 10:42:28.845809+00	9	\N	\N	f	f
9373	PROJECT	Project	Colosimo Catering and Associates	261511	2022-01-21 10:42:28.84587+00	2022-01-21 10:42:28.845899+00	9	\N	\N	f	f
9374	PROJECT	Project	Company 1618550408	261512	2022-01-21 10:42:28.84596+00	2022-01-21 10:42:28.845989+00	9	\N	\N	f	f
9375	PROJECT	Project	Company 1618566776	261513	2022-01-21 10:42:28.846049+00	2022-01-21 10:42:28.846079+00	9	\N	\N	f	f
9376	PROJECT	Project	Computer Literacy	261514	2022-01-21 10:42:28.84614+00	2022-01-21 10:42:28.846169+00	9	\N	\N	f	f
9377	PROJECT	Project	Computer Training Associates	261515	2022-01-21 10:42:28.84623+00	2022-01-21 10:42:28.846259+00	9	\N	\N	f	f
9378	PROJECT	Project	Connectus	261516	2022-01-21 10:42:28.84632+00	2022-01-21 10:42:28.846349+00	9	\N	\N	f	f
9379	PROJECT	Project	Constanza Liquors -	261517	2022-01-21 10:42:28.84641+00	2022-01-21 10:42:28.84644+00	9	\N	\N	f	f
9380	PROJECT	Project	Conteras Liquors Agency	261518	2022-01-21 10:42:28.8465+00	2022-01-21 10:42:28.846529+00	9	\N	\N	f	f
9381	PROJECT	Project	Conterras and Katen Attorneys Services	261519	2022-01-21 10:42:28.846591+00	2022-01-21 10:42:28.84662+00	9	\N	\N	f	f
9382	PROJECT	Project	Convery Attorneys and Associates	261520	2022-01-21 10:42:28.84668+00	2022-01-21 10:42:28.84671+00	9	\N	\N	f	f
9383	PROJECT	Project	Conway Products	261521	2022-01-21 10:42:28.852956+00	2022-01-21 10:42:28.854507+00	9	\N	\N	f	f
9384	PROJECT	Project	Cooler Title Company	261522	2022-01-21 10:42:28.855432+00	2022-01-21 10:42:28.85547+00	9	\N	\N	f	f
9385	PROJECT	Project	Cooper Equipment	261523	2022-01-21 10:42:28.855535+00	2022-01-21 10:42:28.855565+00	9	\N	\N	f	f
9386	PROJECT	Project	Cooper Industries	261524	2022-01-21 10:42:28.855627+00	2022-01-21 10:42:28.855656+00	9	\N	\N	f	f
9387	PROJECT	Project	Core Care Canada	261525	2022-01-21 10:42:28.855718+00	2022-01-21 10:42:28.855747+00	9	\N	\N	f	f
9388	PROJECT	Project	Core Care Technologies Inc.	261526	2022-01-21 10:42:28.855808+00	2022-01-21 10:42:28.855837+00	9	\N	\N	f	f
9389	PROJECT	Project	Coressel _ -	261527	2022-01-21 10:42:28.855898+00	2022-01-21 10:42:28.855927+00	9	\N	\N	f	f
9390	PROJECT	Project	Cosimini Software Agency	261528	2022-01-21 10:42:28.855987+00	2022-01-21 10:42:28.856016+00	9	\N	\N	f	f
9391	PROJECT	Project	Cotterman Software Company	261529	2022-01-21 10:42:28.856077+00	2022-01-21 10:42:28.856106+00	9	\N	\N	f	f
9392	PROJECT	Project	Cottew Publishing Inc.	261530	2022-01-21 10:42:28.856166+00	2022-01-21 10:42:28.856196+00	9	\N	\N	f	f
9393	PROJECT	Project	Cottman Publishing Manufacturing	261531	2022-01-21 10:42:28.856256+00	2022-01-21 10:42:28.856285+00	9	\N	\N	f	f
9394	PROJECT	Project	Coxum Software Dynamics	261532	2022-01-21 10:42:28.856345+00	2022-01-21 10:42:28.856375+00	9	\N	\N	f	f
9395	PROJECT	Project	CPSA	261533	2022-01-21 10:42:28.856537+00	2022-01-21 10:42:28.856568+00	9	\N	\N	f	f
9396	PROJECT	Project	CPS ltd	261534	2022-01-21 10:42:28.856629+00	2022-01-21 10:42:28.856658+00	9	\N	\N	f	f
9397	PROJECT	Project	Cray Systems	261535	2022-01-21 10:42:28.856718+00	2022-01-21 10:42:28.856747+00	9	\N	\N	f	f
9398	PROJECT	Project	Creasman Antiques Holding Corp.	261536	2022-01-21 10:42:28.856808+00	2022-01-21 10:42:28.856837+00	9	\N	\N	f	f
9399	PROJECT	Project	Creighton & Company	261537	2022-01-21 10:42:28.856898+00	2022-01-21 10:42:28.856927+00	9	\N	\N	f	f
9400	PROJECT	Project	Crighton Catering Company	261538	2022-01-21 10:42:28.856988+00	2022-01-21 10:42:28.857017+00	9	\N	\N	f	f
9401	PROJECT	Project	Crisafulli Hardware Holding Corp.	261539	2022-01-21 10:42:28.857078+00	2022-01-21 10:42:28.857108+00	9	\N	\N	f	f
9402	PROJECT	Project	Cruce Builders	261540	2022-01-21 10:42:28.861828+00	2022-01-21 10:42:28.86187+00	9	\N	\N	f	f
9403	PROJECT	Project	Culprit Inc.	261541	2022-01-21 10:42:28.861934+00	2022-01-21 10:42:28.861964+00	9	\N	\N	f	f
9404	PROJECT	Project	Customer Mapped Project	261115	2022-01-21 10:42:28.862026+00	2022-01-21 10:42:28.862055+00	9	\N	\N	f	f
9405	PROJECT	Project	Customer Sravan	274665	2022-01-21 10:42:28.862116+00	2022-01-21 10:42:28.862145+00	9	\N	\N	f	f
9406	PROJECT	Project	CVM Business Solutions	261542	2022-01-21 10:42:28.862205+00	2022-01-21 10:42:28.862235+00	9	\N	\N	f	f
9407	PROJECT	Project	Cwik and Klayman Metal Fabricators Holding Corp.	261543	2022-01-21 10:42:28.862295+00	2022-01-21 10:42:28.862324+00	9	\N	\N	f	f
9408	PROJECT	Project	Cytec Industries Inc	261544	2022-01-21 10:42:28.862384+00	2022-01-21 10:42:28.862413+00	9	\N	\N	f	f
9409	PROJECT	Project	Dale Jenson	261545	2022-01-21 10:42:28.862473+00	2022-01-21 10:42:28.862503+00	9	\N	\N	f	f
9410	PROJECT	Project	Dambrose and Ottum Leasing Holding Corp.	261546	2022-01-21 10:42:28.862563+00	2022-01-21 10:42:28.862592+00	9	\N	\N	f	f
9411	PROJECT	Project	Danniels Antiques Inc.	261547	2022-01-21 10:42:28.862653+00	2022-01-21 10:42:28.862682+00	9	\N	\N	f	f
9412	PROJECT	Project	Daquino Painting -	261548	2022-01-21 10:42:28.862742+00	2022-01-21 10:42:28.862771+00	9	\N	\N	f	f
9413	PROJECT	Project	Dary Construction Corporation	261549	2022-01-21 10:42:28.862832+00	2022-01-21 10:42:28.862861+00	9	\N	\N	f	f
9414	PROJECT	Project	David Langhor	261550	2022-01-21 10:42:28.862922+00	2022-01-21 10:42:28.862951+00	9	\N	\N	f	f
9415	PROJECT	Project	Days Creek Electric Services	261551	2022-01-21 10:42:28.863011+00	2022-01-21 10:42:28.863041+00	9	\N	\N	f	f
9416	PROJECT	Project	Deblasio Painting Holding Corp.	261552	2022-01-21 10:42:28.863101+00	2022-01-21 10:42:28.86313+00	9	\N	\N	f	f
9417	PROJECT	Project	Defaveri Construction	261553	2022-01-21 10:42:28.863211+00	2022-01-21 10:42:28.86324+00	9	\N	\N	f	f
9418	PROJECT	Project	Dehaney Liquors Co.	261554	2022-01-21 10:42:28.8633+00	2022-01-21 10:42:28.863329+00	9	\N	\N	f	f
9419	PROJECT	Project	DellPack (UK)	261555	2022-01-21 10:42:28.863389+00	2022-01-21 10:42:28.863766+00	9	\N	\N	f	f
9420	PROJECT	Project	DelRey Distributors	261556	2022-01-21 10:42:28.863866+00	2022-01-21 10:42:28.863896+00	9	\N	\N	f	f
9421	PROJECT	Project	Demaire Automotive Systems	261557	2022-01-21 10:42:28.867915+00	2022-01-21 10:42:28.868007+00	9	\N	\N	f	f
9422	PROJECT	Project	Denise Sweet	261558	2022-01-21 10:42:28.868185+00	2022-01-21 10:42:28.868264+00	9	\N	\N	f	f
9423	PROJECT	Project	Dennis Batemanger	261559	2022-01-21 10:42:28.868452+00	2022-01-21 10:42:28.868774+00	9	\N	\N	f	f
9424	PROJECT	Project	D&H Manufacturing	261560	2022-01-21 10:42:28.868921+00	2022-01-21 10:42:28.868966+00	9	\N	\N	f	f
9425	PROJECT	Project	Diamond Bar Plumbing	261561	2022-01-21 10:42:28.869062+00	2022-01-21 10:42:28.869115+00	9	\N	\N	f	f
9426	PROJECT	Project	Diego Rodriguez	274666	2022-01-21 10:42:28.869234+00	2022-01-21 10:42:28.869281+00	9	\N	\N	f	f
9427	PROJECT	Project	Diekema Attorneys Manufacturing	261562	2022-01-21 10:42:28.869424+00	2022-01-21 10:42:28.869466+00	9	\N	\N	f	f
9428	PROJECT	Project	Difebbo and Lewelling Markets Agency	261563	2022-01-21 10:42:28.869718+00	2022-01-21 10:42:28.869761+00	9	\N	\N	f	f
9429	PROJECT	Project	Dillain Collins	261564	2022-01-21 10:42:28.869854+00	2022-01-21 10:42:28.869896+00	9	\N	\N	f	f
9430	PROJECT	Project	Diluzio Automotive Group	261565	2022-01-21 10:42:28.86999+00	2022-01-21 10:42:28.871071+00	9	\N	\N	f	f
9431	PROJECT	Project	Dipiano Automotive Sales	261566	2022-01-21 10:42:28.873253+00	2022-01-21 10:42:28.873349+00	9	\N	\N	f	f
9432	PROJECT	Project	Direct Mail Campaign	284498	2022-01-21 10:42:28.873508+00	2022-01-21 10:42:28.873564+00	9	\N	\N	f	f
9433	PROJECT	Project	Doerrer Apartments Inc.	261567	2022-01-21 10:42:28.873694+00	2022-01-21 10:42:28.873751+00	9	\N	\N	f	f
9434	PROJECT	Project	Dogan Painting Leasing	261568	2022-01-21 10:42:28.874039+00	2022-01-21 10:42:28.8741+00	9	\N	\N	f	f
9435	PROJECT	Project	Doiel and Mcdivitt Construction Holding Corp.	261569	2022-01-21 10:42:28.874417+00	2022-01-21 10:42:28.874457+00	9	\N	\N	f	f
9436	PROJECT	Project	Dolfi Software Group	261570	2022-01-21 10:42:28.874548+00	2022-01-21 10:42:28.874589+00	9	\N	\N	f	f
9437	PROJECT	Project	Dominion Consulting	261571	2022-01-21 10:42:28.874683+00	2022-01-21 10:42:28.874724+00	9	\N	\N	f	f
9438	PROJECT	Project	Dorey Attorneys Distributors	261572	2022-01-21 10:42:28.874817+00	2022-01-21 10:42:28.874856+00	9	\N	\N	f	f
9439	PROJECT	Project	Dorminy Windows Rentals	261573	2022-01-21 10:42:28.874944+00	2022-01-21 10:42:28.874982+00	9	\N	\N	f	f
9440	PROJECT	Project	Douse Telecom Leasing	261574	2022-01-21 10:42:28.87507+00	2022-01-21 10:42:28.875107+00	9	\N	\N	f	f
9441	PROJECT	Project	Downey and Sweezer Electric Group	261575	2022-01-21 10:42:28.875196+00	2022-01-21 10:42:28.875235+00	9	\N	\N	f	f
9442	PROJECT	Project	Downey Catering Agency	261576	2022-01-21 10:42:28.87533+00	2022-01-21 10:42:28.875369+00	9	\N	\N	f	f
9443	PROJECT	Project	Dries Hospital Manufacturing	261577	2022-01-21 10:42:28.875459+00	2022-01-21 10:42:28.875498+00	9	\N	\N	f	f
9444	PROJECT	Project	Drown Markets Services	261578	2022-01-21 10:42:28.875586+00	2022-01-21 10:42:28.875625+00	9	\N	\N	f	f
9445	PROJECT	Project	Drumgoole Attorneys Corporation	261579	2022-01-21 10:42:28.875713+00	2022-01-21 10:42:28.875752+00	9	\N	\N	f	f
9446	PROJECT	Project	Duhamel Lumber Co.	261580	2022-01-21 10:42:28.875859+00	2022-01-21 10:42:28.875897+00	9	\N	\N	f	f
9447	PROJECT	Project	Dukes Basketball Camp	274667	2022-01-21 10:42:28.875984+00	2022-01-21 10:42:28.876023+00	9	\N	\N	f	f
9448	PROJECT	Project	Duman Windows Sales	261581	2022-01-21 10:42:28.876111+00	2022-01-21 10:42:28.876149+00	9	\N	\N	f	f
9449	PROJECT	Project	Dunlevy Software Corporation	261582	2022-01-21 10:42:28.876238+00	2022-01-21 10:42:28.876276+00	9	\N	\N	f	f
9450	PROJECT	Project	Duroseau Publishing	261583	2022-01-21 10:42:28.876363+00	2022-01-21 10:42:28.876402+00	9	\N	\N	f	f
9451	PROJECT	Project	Dylan Sollfrank	274668	2022-01-21 10:42:28.87649+00	2022-01-21 10:42:28.876529+00	9	\N	\N	f	f
9452	PROJECT	Project	Eachus Metal Fabricators Incorporated	261584	2022-01-21 10:42:28.905346+00	2022-01-21 10:42:28.9054+00	9	\N	\N	f	f
9453	PROJECT	Project	Eberlein and Preslipsky _ Holding Corp.	261585	2022-01-21 10:42:28.905758+00	2022-01-21 10:42:28.905815+00	9	\N	\N	f	f
9454	PROJECT	Project	Ecker Designs	278567	2022-01-21 10:42:28.90593+00	2022-01-21 10:42:28.905969+00	9	\N	\N	f	f
9455	PROJECT	Project	Ecker Designs:Ecker Holiday event	285878	2022-01-21 10:42:28.90606+00	2022-01-21 10:42:28.906099+00	9	\N	\N	f	f
9456	PROJECT	Project	Eckerman Leasing Management	261586	2022-01-21 10:42:28.906188+00	2022-01-21 10:42:28.906227+00	9	\N	\N	f	f
9457	PROJECT	Project	Eckler Leasing	261587	2022-01-21 10:42:28.906324+00	2022-01-21 10:42:28.906363+00	9	\N	\N	f	f
9458	PROJECT	Project	Eckrote Construction Fabricators	261588	2022-01-21 10:42:28.906451+00	2022-01-21 10:42:28.90649+00	9	\N	\N	f	f
9459	PROJECT	Project	Ecommerce Campaign	284499	2022-01-21 10:42:28.906579+00	2022-01-21 10:42:28.906641+00	9	\N	\N	f	f
9460	PROJECT	Project	Ede Title Rentals	261589	2022-01-21 10:42:28.906733+00	2022-01-21 10:42:28.906772+00	9	\N	\N	f	f
9461	PROJECT	Project	Edin Lumber Distributors	261590	2022-01-21 10:42:28.90686+00	2022-01-21 10:42:28.906897+00	9	\N	\N	f	f
9462	PROJECT	Project	Ed Obuz	261591	2022-01-21 10:42:28.906981+00	2022-01-21 10:42:28.907019+00	9	\N	\N	f	f
9463	PROJECT	Project	Effectiovation Inc	261592	2022-01-21 10:42:28.907259+00	2022-01-21 10:42:28.907595+00	9	\N	\N	f	f
9464	PROJECT	Project	Efficiency Engineering	261593	2022-01-21 10:42:28.90769+00	2022-01-21 10:42:28.90772+00	9	\N	\N	f	f
9465	PROJECT	Project	Eichner Antiques -	261594	2022-01-21 10:42:28.907782+00	2022-01-21 10:42:28.907811+00	9	\N	\N	f	f
9466	PROJECT	Project	Electronics Direct to You	261595	2022-01-21 10:42:28.907872+00	2022-01-21 10:42:28.907901+00	9	\N	\N	f	f
9467	PROJECT	Project	Elegance Interior Design	261596	2022-01-21 10:42:28.907962+00	2022-01-21 10:42:28.907991+00	9	\N	\N	f	f
9468	PROJECT	Project	Eliszewski Windows Dynamics	261597	2022-01-21 10:42:28.908052+00	2022-01-21 10:42:28.908081+00	9	\N	\N	f	f
9469	PROJECT	Project	Ellenberger Windows Management	261598	2022-01-21 10:42:28.908142+00	2022-01-21 10:42:28.908226+00	9	\N	\N	f	f
9470	PROJECT	Project	El Paso Hardware Co.	261599	2022-01-21 10:42:28.908371+00	2022-01-21 10:42:28.908434+00	9	\N	\N	f	f
9471	PROJECT	Project	Emergys	261600	2022-01-21 10:42:28.908531+00	2022-01-21 10:42:28.908571+00	9	\N	\N	f	f
9472	PROJECT	Project	Empire Financial Group	261601	2022-01-21 10:42:28.908665+00	2022-01-21 10:42:28.908705+00	9	\N	\N	f	f
9473	PROJECT	Project	eNable Corp	261602	2022-01-21 10:42:28.908797+00	2022-01-21 10:42:28.908838+00	9	\N	\N	f	f
9474	PROJECT	Project	Engelkemier Catering Management	261603	2022-01-21 10:42:28.908929+00	2022-01-21 10:42:28.90897+00	9	\N	\N	f	f
9475	PROJECT	Project	Epling Builders Inc.	261604	2022-01-21 10:42:28.911738+00	2022-01-21 10:42:28.913079+00	9	\N	\N	f	f
9476	PROJECT	Project	Eric Korb	261605	2022-01-21 10:42:28.913303+00	2022-01-21 10:42:28.913351+00	9	\N	\N	f	f
9477	PROJECT	Project	Eric Schmidt	261606	2022-01-21 10:42:28.913445+00	2022-01-21 10:42:28.914838+00	9	\N	\N	f	f
9478	PROJECT	Project	Erin Kessman	261607	2022-01-21 10:42:28.915073+00	2022-01-21 10:42:28.915117+00	9	\N	\N	f	f
9479	PROJECT	Project	Ertle Painting Leasing	261608	2022-01-21 10:42:28.915207+00	2022-01-21 10:42:28.916032+00	9	\N	\N	f	f
9480	PROJECT	Project	Espar Heater Systems	261609	2022-01-21 10:42:28.91622+00	2022-01-21 10:42:28.916282+00	9	\N	\N	f	f
9481	PROJECT	Project	Estanislau and Brodka Electric Holding Corp.	261610	2022-01-21 10:42:28.916414+00	2022-01-21 10:42:28.916683+00	9	\N	\N	f	f
9482	PROJECT	Project	Estee Lauder	261611	2022-01-21 10:42:28.917205+00	2022-01-21 10:42:28.91728+00	9	\N	\N	f	f
9483	PROJECT	Project	Estevez Title and Associates	261612	2022-01-21 10:42:28.917406+00	2022-01-21 10:42:28.91745+00	9	\N	\N	f	f
9484	PROJECT	Project	Eugenio	261613	2022-01-21 10:42:28.917546+00	2022-01-21 10:42:28.917587+00	9	\N	\N	f	f
9485	PROJECT	Project	Evans Leasing Fabricators	261614	2022-01-21 10:42:28.917681+00	2022-01-21 10:42:28.917722+00	9	\N	\N	f	f
9486	PROJECT	Project	Everett Fine Wines	261615	2022-01-21 10:42:28.917815+00	2022-01-21 10:42:28.917856+00	9	\N	\N	f	f
9487	PROJECT	Project	Everett International	261616	2022-01-21 10:42:28.91795+00	2022-01-21 10:42:28.91799+00	9	\N	\N	f	f
9488	PROJECT	Project	Eyram Marketing	261617	2022-01-21 10:42:28.918083+00	2022-01-21 10:42:28.918124+00	9	\N	\N	f	f
9489	PROJECT	Project	Fabre Enterprises	261618	2022-01-21 10:42:28.91885+00	2022-01-21 10:42:28.918948+00	9	\N	\N	f	f
9490	PROJECT	Project	Fabrizio's Dry Cleaners	261619	2022-01-21 10:42:28.919517+00	2022-01-21 10:42:28.92808+00	9	\N	\N	f	f
9491	PROJECT	Project	Fagnani Builders	261620	2022-01-21 10:42:28.92831+00	2022-01-21 10:42:28.928356+00	9	\N	\N	f	f
9492	PROJECT	Project	FA-HB Inc.	261621	2022-01-21 10:42:28.928451+00	2022-01-21 10:42:28.92849+00	9	\N	\N	f	f
9493	PROJECT	Project	FA-HB Job	261622	2022-01-21 10:42:28.928578+00	2022-01-21 10:42:28.928618+00	9	\N	\N	f	f
9494	PROJECT	Project	Falls Church _ Agency	261623	2022-01-21 10:42:28.928707+00	2022-01-21 10:42:28.928746+00	9	\N	\N	f	f
9495	PROJECT	Project	Fantasy Gemmart	261624	2022-01-21 10:42:28.928838+00	2022-01-21 10:42:28.928876+00	9	\N	\N	f	f
9496	PROJECT	Project	Fasefax Systems	261625	2022-01-21 10:42:28.928966+00	2022-01-21 10:42:28.929005+00	9	\N	\N	f	f
9497	PROJECT	Project	Faske Software Group	261626	2022-01-21 10:42:28.929094+00	2022-01-21 10:42:28.929133+00	9	\N	\N	f	f
9498	PROJECT	Project	Fauerbach _ Agency	261627	2022-01-21 10:42:28.929221+00	2022-01-21 10:42:28.929259+00	9	\N	\N	f	f
9499	PROJECT	Project	Fenceroy and Herling Metal Fabricators Management	261628	2022-01-21 10:42:28.929351+00	2022-01-21 10:42:28.929395+00	9	\N	\N	f	f
9500	PROJECT	Project	Fernstrom Automotive Systems	261629	2022-01-21 10:42:28.929489+00	2022-01-21 10:42:28.929527+00	9	\N	\N	f	f
9501	PROJECT	Project	Ferrio and Donlon Builders Management	261630	2022-01-21 10:42:28.929616+00	2022-01-21 10:42:28.929655+00	9	\N	\N	f	f
9502	PROJECT	Project	Fetterolf and Loud Apartments Inc.	261631	2022-01-21 10:42:28.939812+00	2022-01-21 10:42:28.939892+00	9	\N	\N	f	f
9503	PROJECT	Project	Ficke Apartments Group	261632	2022-01-21 10:42:28.940021+00	2022-01-21 10:42:28.940067+00	9	\N	\N	f	f
9504	PROJECT	Project	FigmentSoft Inc	261633	2022-01-21 10:42:28.940174+00	2022-01-21 10:42:28.94022+00	9	\N	\N	f	f
9505	PROJECT	Project	Fiore Fashion Inc	261634	2022-01-21 10:42:28.940322+00	2022-01-21 10:42:28.940364+00	9	\N	\N	f	f
9506	PROJECT	Project	Fixed Fee Project with Five Tasks	284462	2022-01-21 10:42:28.940458+00	2022-01-21 10:42:28.940498+00	9	\N	\N	f	f
9507	PROJECT	Project	Florence Liquors and Associates	261635	2022-01-21 10:42:28.940593+00	2022-01-21 10:42:28.940633+00	9	\N	\N	f	f
9508	PROJECT	Project	Flores Inc	261636	2022-01-21 10:42:28.940728+00	2022-01-21 10:42:28.940767+00	9	\N	\N	f	f
9509	PROJECT	Project	Focal Point Opticians	261637	2022-01-21 10:42:28.940861+00	2022-01-21 10:42:28.9409+00	9	\N	\N	f	f
9510	PROJECT	Project	Ford Models Inc	261638	2022-01-21 10:42:28.940995+00	2022-01-21 10:42:28.941036+00	9	\N	\N	f	f
9511	PROJECT	Project	Forest Grove Liquors Company	261639	2022-01-21 10:42:28.941148+00	2022-01-21 10:42:28.941192+00	9	\N	\N	f	f
9512	PROJECT	Project	Formal Furnishings	261640	2022-01-21 10:42:28.941285+00	2022-01-21 10:42:28.941325+00	9	\N	\N	f	f
9513	PROJECT	Project	Formisano Hardware -	261641	2022-01-21 10:42:28.941418+00	2022-01-21 10:42:28.941457+00	9	\N	\N	f	f
9514	PROJECT	Project	Fort Walton Beach Electric Company	261642	2022-01-21 10:42:28.941546+00	2022-01-21 10:42:28.941585+00	9	\N	\N	f	f
9515	PROJECT	Project	Fossil Watch Limited	261643	2022-01-21 10:42:28.941675+00	2022-01-21 10:42:28.941714+00	9	\N	\N	f	f
9516	PROJECT	Project	Foulds Plumbing -	261644	2022-01-21 10:42:28.941803+00	2022-01-21 10:42:28.941841+00	9	\N	\N	f	f
9517	PROJECT	Project	Foxe Windows Management	261645	2022-01-21 10:42:28.941929+00	2022-01-21 10:42:28.94197+00	9	\N	\N	f	f
9518	PROJECT	Project	Foxmoor Formula	261646	2022-01-21 10:42:28.942063+00	2022-01-21 10:42:28.942102+00	9	\N	\N	f	f
9519	PROJECT	Project	Frank Edwards	261647	2022-01-21 10:42:28.942198+00	2022-01-21 10:42:28.942239+00	9	\N	\N	f	f
9520	PROJECT	Project	Frankland Attorneys Sales	261648	2022-01-21 10:42:28.942331+00	2022-01-21 10:42:28.942371+00	9	\N	\N	f	f
9521	PROJECT	Project	Franklin Photography	261649	2022-01-21 10:42:28.942461+00	2022-01-21 10:42:28.9425+00	9	\N	\N	f	f
9522	PROJECT	Project	Franklin Windows Inc.	261650	2022-01-21 10:42:28.94259+00	2022-01-21 10:42:28.94263+00	9	\N	\N	f	f
9523	PROJECT	Project	Fredericksburg Liquors Dynamics	261651	2022-01-21 10:42:28.942721+00	2022-01-21 10:42:28.942762+00	9	\N	\N	f	f
9524	PROJECT	Project	Freeman Sporting Goods	274669	2022-01-21 10:42:28.942863+00	2022-01-21 10:42:28.9429+00	9	\N	\N	f	f
9525	PROJECT	Project	Freeman Sporting Goods:0969 Ocean View Road	274670	2022-01-21 10:42:28.942986+00	2022-01-21 10:42:28.943024+00	9	\N	\N	f	f
9526	PROJECT	Project	Freeman Sporting Goods:55 Twin Lane	274671	2022-01-21 10:42:28.943111+00	2022-01-21 10:42:28.943148+00	9	\N	\N	f	f
9527	PROJECT	Project	Freier Markets Incorporated	261652	2022-01-21 10:42:28.943237+00	2022-01-21 10:42:28.943274+00	9	\N	\N	f	f
9528	PROJECT	Project	Freshour Apartments Agency	261653	2022-01-21 10:42:28.943359+00	2022-01-21 10:42:28.943398+00	9	\N	\N	f	f
9529	PROJECT	Project	Froilan Rosqueta	278568	2022-01-21 10:42:28.943484+00	2022-01-21 10:42:28.943521+00	9	\N	\N	f	f
9530	PROJECT	Project	FSI Industries (EUR)	261654	2022-01-21 10:42:28.943606+00	2022-01-21 10:42:28.943644+00	9	\N	\N	f	f
9531	PROJECT	Project	Fuhrmann Lumber Manufacturing	261655	2022-01-21 10:42:28.943729+00	2022-01-21 10:42:28.943766+00	9	\N	\N	f	f
9532	PROJECT	Project	Fujimura Catering Corporation	261656	2022-01-21 10:42:28.943853+00	2022-01-21 10:42:28.943895+00	9	\N	\N	f	f
9533	PROJECT	Project	Fullerton Software Inc.	261657	2022-01-21 10:42:28.943984+00	2022-01-21 10:42:28.944023+00	9	\N	\N	f	f
9534	PROJECT	Project	Furay and Bielawski Liquors Corporation	261658	2022-01-21 10:42:28.944111+00	2022-01-21 10:42:28.944148+00	9	\N	\N	f	f
9535	PROJECT	Project	Furniture Concepts	261659	2022-01-21 10:42:28.944234+00	2022-01-21 10:42:28.944271+00	9	\N	\N	f	f
9536	PROJECT	Project	Fuster Builders Co.	261660	2022-01-21 10:42:28.944365+00	2022-01-21 10:42:28.944402+00	9	\N	\N	f	f
9537	PROJECT	Project	FuTech	261661	2022-01-21 10:42:28.944492+00	2022-01-21 10:42:28.94453+00	9	\N	\N	f	f
9538	PROJECT	Project	Future Office Designs	261662	2022-01-21 10:42:28.944624+00	2022-01-21 10:42:28.944781+00	9	\N	\N	f	f
9539	PROJECT	Project	Fyle Engineering	261116	2022-01-21 10:42:28.944926+00	2022-01-21 10:42:28.944966+00	9	\N	\N	f	f
9540	PROJECT	Project	Fyle Integrations	274672	2022-01-21 10:42:28.94506+00	2022-01-21 10:42:28.9451+00	9	\N	\N	f	f
9541	PROJECT	Project	Fyle Main Project	261117	2022-01-21 10:42:28.945185+00	2022-01-21 10:42:28.945224+00	9	\N	\N	f	f
9542	PROJECT	Project	Fyle NetSuite Integration	284463	2022-01-21 10:42:28.945315+00	2022-01-21 10:42:28.945352+00	9	\N	\N	f	f
9543	PROJECT	Project	Fyle Nilesh	274673	2022-01-21 10:42:28.945442+00	2022-01-21 10:42:28.94548+00	9	\N	\N	f	f
9544	PROJECT	Project	Fyle Sage Intacct Integration	284464	2022-01-21 10:42:28.945566+00	2022-01-21 10:42:28.945609+00	9	\N	\N	f	f
9545	PROJECT	Project	Fyle Team Integrations	261118	2022-01-21 10:42:28.945695+00	2022-01-21 10:42:28.945734+00	9	\N	\N	f	f
9546	PROJECT	Project	Gacad Publishing Co.	261663	2022-01-21 10:42:28.945823+00	2022-01-21 10:42:28.945861+00	9	\N	\N	f	f
9547	PROJECT	Project	Gadison Electric Inc.	261664	2022-01-21 10:42:28.945949+00	2022-01-21 10:42:28.945988+00	9	\N	\N	f	f
9548	PROJECT	Project	Gainesville Plumbing Co.	261665	2022-01-21 10:42:28.946077+00	2022-01-21 10:42:28.946116+00	9	\N	\N	f	f
9549	PROJECT	Project	Galagher Plumbing Sales	261666	2022-01-21 10:42:28.946203+00	2022-01-21 10:42:28.946242+00	9	\N	\N	f	f
9550	PROJECT	Project	Galas Electric Rentals	261667	2022-01-21 10:42:28.946331+00	2022-01-21 10:42:28.94637+00	9	\N	\N	f	f
9551	PROJECT	Project	Gale Custom Sailboat	261668	2022-01-21 10:42:28.94646+00	2022-01-21 10:42:28.946499+00	9	\N	\N	f	f
9552	PROJECT	Project	Gallaugher Title Dynamics	261669	2022-01-21 10:42:28.957737+00	2022-01-21 10:42:28.957796+00	9	\N	\N	f	f
9553	PROJECT	Project	Galvan Attorneys Systems	261670	2022-01-21 10:42:28.957889+00	2022-01-21 10:42:28.957928+00	9	\N	\N	f	f
9554	PROJECT	Project	Garden Automotive Systems	261671	2022-01-21 10:42:28.958015+00	2022-01-21 10:42:28.958054+00	9	\N	\N	f	f
9555	PROJECT	Project	Gardnerville Automotive Sales	261672	2022-01-21 10:42:28.958141+00	2022-01-21 10:42:28.958179+00	9	\N	\N	f	f
9556	PROJECT	Project	Garitty Metal Fabricators Rentals	261673	2022-01-21 10:42:28.958265+00	2022-01-21 10:42:28.958303+00	9	\N	\N	f	f
9557	PROJECT	Project	Garret Leasing Rentals	261674	2022-01-21 10:42:28.95839+00	2022-01-21 10:42:28.958428+00	9	\N	\N	f	f
9558	PROJECT	Project	Gary Underwood	261675	2022-01-21 10:42:28.958517+00	2022-01-21 10:42:28.958554+00	9	\N	\N	f	f
9559	PROJECT	Project	Gauch Metal Fabricators Sales	261676	2022-01-21 10:42:28.95864+00	2022-01-21 10:42:28.958678+00	9	\N	\N	f	f
9560	PROJECT	Project	Gearan Title Networking	261677	2022-01-21 10:42:28.958774+00	2022-01-21 10:42:28.958813+00	9	\N	\N	f	f
9561	PROJECT	Project	Geeta Kalapatapu	274674	2022-01-21 10:42:28.958903+00	2022-01-21 10:42:28.958941+00	9	\N	\N	f	f
9562	PROJECT	Project	General Overhead	284465	2022-01-21 10:42:28.959032+00	2022-01-21 10:42:28.959073+00	9	\N	\N	f	f
9563	PROJECT	Project	General Overhead-Current	284466	2022-01-21 10:42:28.95916+00	2022-01-21 10:42:28.959199+00	9	\N	\N	f	f
9564	PROJECT	Project	Genis Builders Holding Corp.	261678	2022-01-21 10:42:28.959284+00	2022-01-21 10:42:28.959322+00	9	\N	\N	f	f
9565	PROJECT	Project	Gerba Construction Corporation	261679	2022-01-21 10:42:28.959404+00	2022-01-21 10:42:28.959442+00	9	\N	\N	f	f
9566	PROJECT	Project	Gerney Antiques Management	261680	2022-01-21 10:42:28.959526+00	2022-01-21 10:42:28.959568+00	9	\N	\N	f	f
9567	PROJECT	Project	Gesamondo Construction Leasing	261681	2022-01-21 10:42:28.959662+00	2022-01-21 10:42:28.959702+00	9	\N	\N	f	f
9568	PROJECT	Project	Gettenberg Title Manufacturing	261682	2022-01-21 10:42:28.959792+00	2022-01-21 10:42:28.959831+00	9	\N	\N	f	f
9569	PROJECT	Project	Gevelber Photography	274675	2022-01-21 10:42:28.959922+00	2022-01-21 10:42:28.959962+00	9	\N	\N	f	f
9570	PROJECT	Project	Gibsons Corporation	261683	2022-01-21 10:42:28.960052+00	2022-01-21 10:42:28.960093+00	9	\N	\N	f	f
9571	PROJECT	Project	Gilcrease Telecom Systems	261684	2022-01-21 10:42:28.960185+00	2022-01-21 10:42:28.960224+00	9	\N	\N	f	f
9572	PROJECT	Project	Gilroy Electric Services	261685	2022-01-21 10:42:28.960315+00	2022-01-21 10:42:28.960354+00	9	\N	\N	f	f
9573	PROJECT	Project	Gionest Metal Fabricators Co.	261686	2022-01-21 10:42:28.960445+00	2022-01-21 10:42:28.960485+00	9	\N	\N	f	f
9574	PROJECT	Project	GlassHouse Systems	261687	2022-01-21 10:42:28.960576+00	2022-01-21 10:42:28.960617+00	9	\N	\N	f	f
9575	PROJECT	Project	Glish Hospital Incorporated	261688	2022-01-21 10:42:28.96071+00	2022-01-21 10:42:28.960751+00	9	\N	\N	f	f
9576	PROJECT	Project	Global Supplies Inc.	261689	2022-01-21 10:42:28.960841+00	2022-01-21 10:42:28.960882+00	9	\N	\N	f	f
9577	PROJECT	Project	Glore Apartments Distributors	261690	2022-01-21 10:42:28.960975+00	2022-01-21 10:42:28.961015+00	9	\N	\N	f	f
9578	PROJECT	Project	Goepel Windows Management	261691	2022-01-21 10:42:28.961106+00	2022-01-21 10:42:28.961146+00	9	\N	\N	f	f
9579	PROJECT	Project	Gorman Ho	278569	2022-01-21 10:42:28.961236+00	2022-01-21 10:42:28.961275+00	9	\N	\N	f	f
9580	PROJECT	Project	GProxy Online	261692	2022-01-21 10:42:28.961365+00	2022-01-21 10:42:28.961404+00	9	\N	\N	f	f
9581	PROJECT	Project	Graber & Assoc	261693	2022-01-21 10:42:28.961495+00	2022-01-21 10:42:28.961534+00	9	\N	\N	f	f
9582	PROJECT	Project	Grana Automotive and Associates	261694	2022-01-21 10:42:28.961624+00	2022-01-21 10:42:28.961662+00	9	\N	\N	f	f
9583	PROJECT	Project	Grangeville Apartments Dynamics	261695	2022-01-21 10:42:28.961753+00	2022-01-21 10:42:28.961792+00	9	\N	\N	f	f
9584	PROJECT	Project	Grant Electronics	261696	2022-01-21 10:42:28.961881+00	2022-01-21 10:42:28.961921+00	9	\N	\N	f	f
9585	PROJECT	Project	Graphics R Us	261697	2022-01-21 10:42:28.962013+00	2022-01-21 10:42:28.962053+00	9	\N	\N	f	f
9586	PROJECT	Project	Grave Apartments Sales	261698	2022-01-21 10:42:28.962142+00	2022-01-21 10:42:28.963659+00	9	\N	\N	f	f
9587	PROJECT	Project	Graydon	261699	2022-01-21 10:42:28.963827+00	2022-01-21 10:42:28.963872+00	9	\N	\N	f	f
9588	PROJECT	Project	Green Grocery	261700	2022-01-21 10:42:28.963978+00	2022-01-21 10:42:28.964017+00	9	\N	\N	f	f
9589	PROJECT	Project	Green Street Spirits	261701	2022-01-21 10:42:28.964118+00	2022-01-21 10:42:28.964157+00	9	\N	\N	f	f
9590	PROJECT	Project	Greg Muller	261702	2022-01-21 10:42:28.964251+00	2022-01-21 10:42:28.964289+00	9	\N	\N	f	f
9591	PROJECT	Project	Gregory Daniels	261703	2022-01-21 10:42:28.964554+00	2022-01-21 10:42:28.9646+00	9	\N	\N	f	f
9592	PROJECT	Project	Greg Yamashige	261704	2022-01-21 10:42:28.964734+00	2022-01-21 10:42:28.964865+00	9	\N	\N	f	f
9593	PROJECT	Project	Gresham	261705	2022-01-21 10:42:28.968466+00	2022-01-21 10:42:28.968516+00	9	\N	\N	f	f
9594	PROJECT	Project	Grines Apartments Co.	261706	2022-01-21 10:42:28.968586+00	2022-01-21 10:42:28.968615+00	9	\N	\N	f	f
9595	PROJECT	Project	Guidaboni Publishing Leasing	261707	2022-01-21 10:42:28.968676+00	2022-01-21 10:42:28.968706+00	9	\N	\N	f	f
9596	PROJECT	Project	Gus Lee	261708	2022-01-21 10:42:28.968766+00	2022-01-21 10:42:28.968796+00	9	\N	\N	f	f
9597	PROJECT	Project	Gus Li	261709	2022-01-21 10:42:28.968856+00	2022-01-21 10:42:28.968885+00	9	\N	\N	f	f
9598	PROJECT	Project	Gus Photography	261710	2022-01-21 10:42:28.968946+00	2022-01-21 10:42:28.968975+00	9	\N	\N	f	f
9599	PROJECT	Project	Guzalak Leasing Leasing	261711	2022-01-21 10:42:28.969036+00	2022-01-21 10:42:28.969065+00	9	\N	\N	f	f
9600	PROJECT	Project	Hahn & Associates	261712	2022-01-21 10:42:28.969125+00	2022-01-21 10:42:28.969154+00	9	\N	\N	f	f
9601	PROJECT	Project	Haleiwa Windows Leasing	261713	2022-01-21 10:42:28.969214+00	2022-01-21 10:42:28.969243+00	9	\N	\N	f	f
9602	PROJECT	Project	Halick Title and Associates	261714	2022-01-21 10:42:28.98348+00	2022-01-21 10:42:28.983526+00	9	\N	\N	f	f
9603	PROJECT	Project	Hambly Spirits	261715	2022-01-21 10:42:28.98359+00	2022-01-21 10:42:28.983621+00	9	\N	\N	f	f
9604	PROJECT	Project	Hanninen Painting Distributors	261716	2022-01-21 10:42:28.983682+00	2022-01-21 10:42:28.983711+00	9	\N	\N	f	f
9605	PROJECT	Project	Hansen Car Dealership	261717	2022-01-21 10:42:28.983771+00	2022-01-21 10:42:28.983801+00	9	\N	\N	f	f
9606	PROJECT	Project	Harriage Plumbing Dynamics	261718	2022-01-21 10:42:28.983861+00	2022-01-21 10:42:28.98389+00	9	\N	\N	f	f
9607	PROJECT	Project	Harriott Construction Services	261719	2022-01-21 10:42:28.98395+00	2022-01-21 10:42:28.98398+00	9	\N	\N	f	f
9608	PROJECT	Project	Harrop Attorneys Inc.	261720	2022-01-21 10:42:28.98404+00	2022-01-21 10:42:28.98407+00	9	\N	\N	f	f
9609	PROJECT	Project	Harting Electric Fabricators	261721	2022-01-21 10:42:28.98413+00	2022-01-21 10:42:28.984159+00	9	\N	\N	f	f
9610	PROJECT	Project	Hawk Liquors Agency	261722	2022-01-21 10:42:28.98422+00	2022-01-21 10:42:28.984249+00	9	\N	\N	f	f
9611	PROJECT	Project	Hazel Robinson	278570	2022-01-21 10:42:28.984309+00	2022-01-21 10:42:28.984338+00	9	\N	\N	f	f
9612	PROJECT	Project	Healy Lumber -	261723	2022-01-21 10:42:28.984398+00	2022-01-21 10:42:28.984427+00	9	\N	\N	f	f
9613	PROJECT	Project	Hebden Automotive Dynamics	261724	2022-01-21 10:42:28.984487+00	2022-01-21 10:42:28.984516+00	9	\N	\N	f	f
9614	PROJECT	Project	Heeralall Metal Fabricators Incorporated	261725	2022-01-21 10:42:28.984576+00	2022-01-21 10:42:28.984605+00	9	\N	\N	f	f
9615	PROJECT	Project	Helfenbein Apartments Co.	261726	2022-01-21 10:42:28.984665+00	2022-01-21 10:42:28.984694+00	9	\N	\N	f	f
9616	PROJECT	Project	Helferty _ Services	261727	2022-01-21 10:42:28.984755+00	2022-01-21 10:42:28.984784+00	9	\N	\N	f	f
9617	PROJECT	Project	Helker and Heidkamp Software Systems	261728	2022-01-21 10:42:28.984844+00	2022-01-21 10:42:28.984873+00	9	\N	\N	f	f
9618	PROJECT	Project	Helping Hands Medical Supply	261729	2022-01-21 10:42:28.984933+00	2022-01-21 10:42:28.984962+00	9	\N	\N	f	f
9619	PROJECT	Project	Helvey Catering Distributors	261730	2022-01-21 10:42:28.985022+00	2022-01-21 10:42:28.985051+00	9	\N	\N	f	f
9620	PROJECT	Project	Hemauer Builders Inc.	261731	2022-01-21 10:42:28.98511+00	2022-01-21 10:42:28.98514+00	9	\N	\N	f	f
9621	PROJECT	Project	Hemet Builders Sales	261732	2022-01-21 10:42:28.9852+00	2022-01-21 10:42:28.985229+00	9	\N	\N	f	f
9622	PROJECT	Project	Henderson Cooper	261733	2022-01-21 10:42:28.98529+00	2022-01-21 10:42:28.985319+00	9	\N	\N	f	f
9623	PROJECT	Project	Henderson Liquors Manufacturing	261734	2022-01-21 10:42:28.98538+00	2022-01-21 10:42:28.985409+00	9	\N	\N	f	f
9624	PROJECT	Project	Hendrikson Builders Corporation	261735	2022-01-21 10:42:28.985469+00	2022-01-21 10:42:28.985502+00	9	\N	\N	f	f
9625	PROJECT	Project	Henneman Hardware	261736	2022-01-21 10:42:28.985562+00	2022-01-21 10:42:28.985591+00	9	\N	\N	f	f
9626	PROJECT	Project	Herline Hospital Holding Corp.	261737	2022-01-21 10:42:28.985651+00	2022-01-21 10:42:28.98568+00	9	\N	\N	f	f
9627	PROJECT	Project	Hershey's Canada	261738	2022-01-21 10:42:28.98574+00	2022-01-21 10:42:28.985769+00	9	\N	\N	f	f
9628	PROJECT	Project	Hess Sundries	261739	2022-01-21 10:42:28.985829+00	2022-01-21 10:42:28.985858+00	9	\N	\N	f	f
9629	PROJECT	Project	Hextall Consulting	261740	2022-01-21 10:42:28.985918+00	2022-01-21 10:42:28.985947+00	9	\N	\N	f	f
9630	PROJECT	Project	HGH Vision	261741	2022-01-21 10:42:28.986007+00	2022-01-21 10:42:28.986046+00	9	\N	\N	f	f
9631	PROJECT	Project	Hillian Construction Fabricators	261742	2022-01-21 10:42:28.986145+00	2022-01-21 10:42:28.986189+00	9	\N	\N	f	f
9632	PROJECT	Project	Hilltop Info Inc	261743	2022-01-21 10:42:28.98629+00	2022-01-21 10:42:28.986335+00	9	\N	\N	f	f
9633	PROJECT	Project	Himateja Madala	278571	2022-01-21 10:42:28.986428+00	2022-01-21 10:42:28.986467+00	9	\N	\N	f	f
9634	PROJECT	Project	Hirschy and Fahrenwald Liquors Incorporated	261744	2022-01-21 10:42:28.986741+00	2022-01-21 10:42:28.98679+00	9	\N	\N	f	f
9635	PROJECT	Project	Hixson Construction Agency	261745	2022-01-21 10:42:28.986882+00	2022-01-21 10:42:28.986921+00	9	\N	\N	f	f
9636	PROJECT	Project	Ho Engineering Company	285879	2022-01-21 10:42:28.987202+00	2022-01-21 10:42:28.987248+00	9	\N	\N	f	f
9637	PROJECT	Project	Holgerson Automotive Services	261746	2022-01-21 10:42:28.987421+00	2022-01-21 10:42:28.987594+00	9	\N	\N	f	f
9638	PROJECT	Project	Hollyday Construction Networking	261747	2022-01-21 10:42:28.987703+00	2022-01-21 10:42:28.987762+00	9	\N	\N	f	f
9639	PROJECT	Project	Holly Romine	261748	2022-01-21 10:42:28.987857+00	2022-01-21 10:42:28.987897+00	9	\N	\N	f	f
9640	PROJECT	Project	Holtmeier Leasing -	261749	2022-01-21 10:42:28.987988+00	2022-01-21 10:42:28.988027+00	9	\N	\N	f	f
9641	PROJECT	Project	Honie Hospital Systems	261750	2022-01-21 10:42:28.988362+00	2022-01-21 10:42:28.988466+00	9	\N	\N	f	f
9642	PROJECT	Project	Honolulu Attorneys Sales	261751	2022-01-21 10:42:28.988605+00	2022-01-21 10:42:28.98866+00	9	\N	\N	f	f
9643	PROJECT	Project	Honolulu Markets Group	261752	2022-01-21 10:42:28.988783+00	2022-01-21 10:42:28.988832+00	9	\N	\N	f	f
9644	PROJECT	Project	Hood River Telecom	261753	2022-01-21 10:42:28.989086+00	2022-01-21 10:42:28.989371+00	9	\N	\N	f	f
9645	PROJECT	Project	Huck Apartments Inc.	261754	2022-01-21 10:42:28.989477+00	2022-01-21 10:42:28.989518+00	9	\N	\N	f	f
9646	PROJECT	Project	Hughson Runners	261755	2022-01-21 10:42:28.989635+00	2022-01-21 10:42:28.989677+00	9	\N	\N	f	f
9647	PROJECT	Project	Huit and Duer Publishing Dynamics	261756	2022-01-21 10:42:28.989772+00	2022-01-21 10:42:28.989815+00	9	\N	\N	f	f
9648	PROJECT	Project	Humphrey Yogurt	261757	2022-01-21 10:42:28.989914+00	2022-01-21 10:42:28.989957+00	9	\N	\N	f	f
9649	PROJECT	Project	Huntsville Apartments and Associates	261758	2022-01-21 10:42:28.990052+00	2022-01-21 10:42:28.990094+00	9	\N	\N	f	f
9650	PROJECT	Project	Hurlbutt Markets -	261759	2022-01-21 10:42:28.990194+00	2022-01-21 10:42:28.990234+00	9	\N	\N	f	f
9651	PROJECT	Project	Hurtgen Hospital Manufacturing	261760	2022-01-21 10:42:28.990331+00	2022-01-21 10:42:28.990374+00	9	\N	\N	f	f
9652	PROJECT	Project	Iain Bennett	261761	2022-01-21 10:42:29.009318+00	2022-01-21 10:42:29.009382+00	9	\N	\N	f	f
9653	PROJECT	Project	IBA Enterprises Inc	261762	2022-01-21 10:42:29.009489+00	2022-01-21 10:42:29.009532+00	9	\N	\N	f	f
9654	PROJECT	Project	ICC Inc	261763	2022-01-21 10:42:29.009627+00	2022-01-21 10:42:29.00967+00	9	\N	\N	f	f
9655	PROJECT	Project	Imperial Liquors Distributors	261764	2022-01-21 10:42:29.009768+00	2022-01-21 10:42:29.009812+00	9	\N	\N	f	f
9656	PROJECT	Project	Imran Kahn	261765	2022-01-21 10:42:29.009909+00	2022-01-21 10:42:29.010134+00	9	\N	\N	f	f
9657	PROJECT	Project	Indianapolis Liquors Rentals	261766	2022-01-21 10:42:29.010489+00	2022-01-21 10:42:29.010589+00	9	\N	\N	f	f
9658	PROJECT	Project	Installation 2	261767	2022-01-21 10:42:29.011071+00	2022-01-21 10:42:29.01114+00	9	\N	\N	f	f
9659	PROJECT	Project	Installation FP	261768	2022-01-21 10:42:29.011273+00	2022-01-21 10:42:29.011311+00	9	\N	\N	f	f
9660	PROJECT	Project	Integrations	284467	2022-01-21 10:42:29.011379+00	2022-01-21 10:42:29.011409+00	9	\N	\N	f	f
9661	PROJECT	Project	Integrys Ltd	261769	2022-01-21 10:42:29.011473+00	2022-01-21 10:42:29.011503+00	9	\N	\N	f	f
9662	PROJECT	Project	Interior Solutions	261770	2022-01-21 10:42:29.011563+00	2022-01-21 10:42:29.011592+00	9	\N	\N	f	f
9663	PROJECT	Project	InterWorks Ltd	261771	2022-01-21 10:42:29.011652+00	2022-01-21 10:42:29.011682+00	9	\N	\N	f	f
9664	PROJECT	Project	Iorio Lumber Incorporated	261772	2022-01-21 10:42:29.011741+00	2022-01-21 10:42:29.011796+00	9	\N	\N	f	f
9665	PROJECT	Project	Jacint Tumacder	278572	2022-01-21 10:42:29.012242+00	2022-01-21 10:42:29.012319+00	9	\N	\N	f	f
9666	PROJECT	Project	Jackie Kugan	261773	2022-01-21 10:42:29.012465+00	2022-01-21 10:42:29.012523+00	9	\N	\N	f	f
9667	PROJECT	Project	Jackson Alexander	261774	2022-01-21 10:42:29.012669+00	2022-01-21 10:42:29.012725+00	9	\N	\N	f	f
9668	PROJECT	Project	Jaenicke Builders Management	261775	2022-01-21 10:42:29.01285+00	2022-01-21 10:42:29.012899+00	9	\N	\N	f	f
9669	PROJECT	Project	Jake Hamilton	261776	2022-01-21 10:42:29.013019+00	2022-01-21 10:42:29.013065+00	9	\N	\N	f	f
9670	PROJECT	Project	James McClure	261777	2022-01-21 10:42:29.013179+00	2022-01-21 10:42:29.013226+00	9	\N	\N	f	f
9671	PROJECT	Project	Jamie Taylor	261778	2022-01-21 10:42:29.01334+00	2022-01-21 10:42:29.013442+00	9	\N	\N	f	f
9672	PROJECT	Project	Janiak Attorneys Inc.	261779	2022-01-21 10:42:29.013568+00	2022-01-21 10:42:29.013624+00	9	\N	\N	f	f
9673	PROJECT	Project	Jasmer Antiques Management	261780	2022-01-21 10:42:29.013875+00	2022-01-21 10:42:29.013931+00	9	\N	\N	f	f
9674	PROJECT	Project	Jason Jacob	261781	2022-01-21 10:42:29.014074+00	2022-01-21 10:42:29.014154+00	9	\N	\N	f	f
9675	PROJECT	Project	Jason Paul Distribution	261782	2022-01-21 10:42:29.014952+00	2022-01-21 10:42:29.015028+00	9	\N	\N	f	f
9676	PROJECT	Project	Jeff Campbell	261783	2022-01-21 10:42:29.015182+00	2022-01-21 10:42:29.015245+00	9	\N	\N	f	f
9677	PROJECT	Project	Jeff's Jalopies	274676	2022-01-21 10:42:29.015424+00	2022-01-21 10:42:29.015474+00	9	\N	\N	f	f
9678	PROJECT	Project	Jelle Catering Group	261784	2022-01-21 10:42:29.015591+00	2022-01-21 10:42:29.015637+00	9	\N	\N	f	f
9679	PROJECT	Project	Jennings Financial	261785	2022-01-21 10:42:29.015756+00	2022-01-21 10:42:29.015803+00	9	\N	\N	f	f
9680	PROJECT	Project	Jennings Financial Inc.	261786	2022-01-21 10:42:29.015918+00	2022-01-21 10:42:29.015961+00	9	\N	\N	f	f
9681	PROJECT	Project	Jen Zaccarella	278573	2022-01-21 10:42:29.016071+00	2022-01-21 10:42:29.016116+00	9	\N	\N	f	f
9682	PROJECT	Project	Jeune Antiques Group	261787	2022-01-21 10:42:29.016227+00	2022-01-21 10:42:29.016271+00	9	\N	\N	f	f
9683	PROJECT	Project	Jeziorski _ Dynamics	261788	2022-01-21 10:42:29.016415+00	2022-01-21 10:42:29.016459+00	9	\N	\N	f	f
9684	PROJECT	Project	Jim's Custom Frames	261789	2022-01-21 10:42:29.01657+00	2022-01-21 10:42:29.016616+00	9	\N	\N	f	f
9685	PROJECT	Project	Jim Strong	261790	2022-01-21 10:42:29.016763+00	2022-01-21 10:42:29.016809+00	9	\N	\N	f	f
9686	PROJECT	Project	JKL Co.	261791	2022-01-21 10:42:29.016927+00	2022-01-21 10:42:29.016973+00	9	\N	\N	f	f
9687	PROJECT	Project	Joanne Miller	261792	2022-01-21 10:42:29.017084+00	2022-01-21 10:42:29.017127+00	9	\N	\N	f	f
9688	PROJECT	Project	Joe Smith	261793	2022-01-21 10:42:29.017237+00	2022-01-21 10:42:29.017283+00	9	\N	\N	f	f
9689	PROJECT	Project	Johar Software Corporation	261794	2022-01-21 10:42:29.017395+00	2022-01-21 10:42:29.017474+00	9	\N	\N	f	f
9690	PROJECT	Project	John Boba	261795	2022-01-21 10:42:29.017584+00	2022-01-21 10:42:29.017632+00	9	\N	\N	f	f
9691	PROJECT	Project	John G. Roche Opticians	261796	2022-01-21 10:42:29.017745+00	2022-01-21 10:42:29.017791+00	9	\N	\N	f	f
9692	PROJECT	Project	John Melton	274677	2022-01-21 10:42:29.017938+00	2022-01-21 10:42:29.017986+00	9	\N	\N	f	f
9693	PROJECT	Project	John Nguyen	261797	2022-01-21 10:42:29.020372+00	2022-01-21 10:42:29.020429+00	9	\N	\N	f	f
9694	PROJECT	Project	John Paulsen	261798	2022-01-21 10:42:29.020517+00	2022-01-21 10:42:29.020547+00	9	\N	\N	f	f
9695	PROJECT	Project	John Smith Home Design	261799	2022-01-21 10:42:29.02061+00	2022-01-21 10:42:29.020639+00	9	\N	\N	f	f
9696	PROJECT	Project	Johnson & Johnson	261800	2022-01-21 10:42:29.020699+00	2022-01-21 10:42:29.020728+00	9	\N	\N	f	f
9697	PROJECT	Project	Jonas Island Applied Radiation	261801	2022-01-21 10:42:29.020788+00	2022-01-21 10:42:29.020818+00	9	\N	\N	f	f
9698	PROJECT	Project	Jonathan Ketner	261802	2022-01-21 10:42:29.020877+00	2022-01-21 10:42:29.020907+00	9	\N	\N	f	f
9699	PROJECT	Project	Jones & Bernstein Law Firm	261803	2022-01-21 10:42:29.020968+00	2022-01-21 10:42:29.020997+00	9	\N	\N	f	f
9700	PROJECT	Project	Jordan Burgess	278574	2022-01-21 10:42:29.021057+00	2022-01-21 10:42:29.021086+00	9	\N	\N	f	f
9701	PROJECT	Project	Julia Daniels	261804	2022-01-21 10:42:29.021146+00	2022-01-21 10:42:29.021175+00	9	\N	\N	f	f
9702	PROJECT	Project	Julie Frankel	261805	2022-01-21 10:42:29.036573+00	2022-01-21 10:42:29.036616+00	9	\N	\N	f	f
9703	PROJECT	Project	Juno Gold Wines	261806	2022-01-21 10:42:29.036681+00	2022-01-21 10:42:29.036711+00	9	\N	\N	f	f
9704	PROJECT	Project	Justine Outland	278575	2022-01-21 10:42:29.036772+00	2022-01-21 10:42:29.036801+00	9	\N	\N	f	f
9705	PROJECT	Project	Justin Hartman	261807	2022-01-21 10:42:29.036861+00	2022-01-21 10:42:29.03689+00	9	\N	\N	f	f
9706	PROJECT	Project	Justin Ramos	261808	2022-01-21 10:42:29.03695+00	2022-01-21 10:42:29.03698+00	9	\N	\N	f	f
9707	PROJECT	Project	Kababik and Ramariz Liquors Corporation	261809	2022-01-21 10:42:29.037041+00	2022-01-21 10:42:29.03707+00	9	\N	\N	f	f
9708	PROJECT	Project	Kalfa Painting Holding Corp.	261810	2022-01-21 10:42:29.03713+00	2022-01-21 10:42:29.037159+00	9	\N	\N	f	f
9709	PROJECT	Project	Kalinsky Consulting Group	261811	2022-01-21 10:42:29.03722+00	2022-01-21 10:42:29.037249+00	9	\N	\N	f	f
9710	PROJECT	Project	Kalisch Lumber Group	261812	2022-01-21 10:42:29.037309+00	2022-01-21 10:42:29.037339+00	9	\N	\N	f	f
9711	PROJECT	Project	Kallmeyer Antiques Dynamics	261813	2022-01-21 10:42:29.037399+00	2022-01-21 10:42:29.03744+00	9	\N	\N	f	f
9712	PROJECT	Project	Kamps Electric Systems	261814	2022-01-21 10:42:29.0375+00	2022-01-21 10:42:29.037529+00	9	\N	\N	f	f
9713	PROJECT	Project	Kara's Cafe	261815	2022-01-21 10:42:29.037588+00	2022-01-21 10:42:29.037617+00	9	\N	\N	f	f
9714	PROJECT	Project	Kari Steblay	278576	2022-01-21 10:42:29.037677+00	2022-01-21 10:42:29.037706+00	9	\N	\N	f	f
9715	PROJECT	Project	Karna Nisewaner	278577	2022-01-21 10:42:29.037766+00	2022-01-21 10:42:29.037795+00	9	\N	\N	f	f
9716	PROJECT	Project	Kate Whelan	274678	2022-01-21 10:42:29.037855+00	2022-01-21 10:42:29.037884+00	9	\N	\N	f	f
9717	PROJECT	Project	Kate Winters	261816	2022-01-21 10:42:29.037944+00	2022-01-21 10:42:29.037973+00	9	\N	\N	f	f
9718	PROJECT	Project	Katie Fischer	261817	2022-01-21 10:42:29.038033+00	2022-01-21 10:42:29.038061+00	9	\N	\N	f	f
9719	PROJECT	Project	Kavadias Construction Sales	261818	2022-01-21 10:42:29.038122+00	2022-01-21 10:42:29.038151+00	9	\N	\N	f	f
9720	PROJECT	Project	Kavanagh Brothers	261819	2022-01-21 10:42:29.038211+00	2022-01-21 10:42:29.03824+00	9	\N	\N	f	f
9721	PROJECT	Project	Kavanaugh Real Estate	261820	2022-01-21 10:42:29.038301+00	2022-01-21 10:42:29.038329+00	9	\N	\N	f	f
9722	PROJECT	Project	Keblish Catering Distributors	261821	2022-01-21 10:42:29.038389+00	2022-01-21 10:42:29.038418+00	9	\N	\N	f	f
9723	PROJECT	Project	Kelleher Title Services	261822	2022-01-21 10:42:29.038478+00	2022-01-21 10:42:29.038508+00	9	\N	\N	f	f
9724	PROJECT	Project	KEM Corporation	261823	2022-01-21 10:42:29.038568+00	2022-01-21 10:42:29.038597+00	9	\N	\N	f	f
9725	PROJECT	Project	Kemme Builders Management	261824	2022-01-21 10:42:29.038657+00	2022-01-21 10:42:29.038686+00	9	\N	\N	f	f
9726	PROJECT	Project	Kempker Title Manufacturing	261825	2022-01-21 10:42:29.038746+00	2022-01-21 10:42:29.038776+00	9	\N	\N	f	f
9727	PROJECT	Project	Ken Chua	261826	2022-01-21 10:42:29.038836+00	2022-01-21 10:42:29.038865+00	9	\N	\N	f	f
9728	PROJECT	Project	Kenney Windows Dynamics	261827	2022-01-21 10:42:29.038925+00	2022-01-21 10:42:29.038955+00	9	\N	\N	f	f
9729	PROJECT	Project	Kerekes Lumber Networking	261828	2022-01-21 10:42:29.039014+00	2022-01-21 10:42:29.039043+00	9	\N	\N	f	f
9730	PROJECT	Project	Kerfien Title Company	261829	2022-01-21 10:42:29.039103+00	2022-01-21 10:42:29.039132+00	9	\N	\N	f	f
9731	PROJECT	Project	Kerry Furnishings & Design	261830	2022-01-21 10:42:29.039192+00	2022-01-21 10:42:29.039221+00	9	\N	\N	f	f
9732	PROJECT	Project	Kevin Smith	261831	2022-01-21 10:42:29.039281+00	2022-01-21 10:42:29.03931+00	9	\N	\N	f	f
9733	PROJECT	Project	Kiedrowski Telecom Services	261832	2022-01-21 10:42:29.03937+00	2022-01-21 10:42:29.039399+00	9	\N	\N	f	f
9734	PROJECT	Project	Kieff Software Fabricators	261833	2022-01-21 10:42:29.039459+00	2022-01-21 10:42:29.039488+00	9	\N	\N	f	f
9735	PROJECT	Project	Killian Construction Networking	261834	2022-01-21 10:42:29.039547+00	2022-01-21 10:42:29.039576+00	9	\N	\N	f	f
9736	PROJECT	Project	Kim Wilson	261835	2022-01-21 10:42:29.039636+00	2022-01-21 10:42:29.039665+00	9	\N	\N	f	f
9737	PROJECT	Project	Kingman Antiques Corporation	261836	2022-01-21 10:42:29.039725+00	2022-01-21 10:42:29.039754+00	9	\N	\N	f	f
9738	PROJECT	Project	Kino Inc	261837	2022-01-21 10:42:29.039815+00	2022-01-21 10:42:29.039844+00	9	\N	\N	f	f
9739	PROJECT	Project	Kirkville Builders -	261838	2022-01-21 10:42:29.039904+00	2022-01-21 10:42:29.039933+00	9	\N	\N	f	f
9740	PROJECT	Project	Kittel Hardware Dynamics	261839	2022-01-21 10:42:29.039993+00	2022-01-21 10:42:29.040022+00	9	\N	\N	f	f
9741	PROJECT	Project	Knoop Telecom Agency	261840	2022-01-21 10:42:29.040082+00	2022-01-21 10:42:29.040111+00	9	\N	\N	f	f
9742	PROJECT	Project	Knotek Hospital Company	261841	2022-01-21 10:42:29.040172+00	2022-01-21 10:42:29.040202+00	9	\N	\N	f	f
9743	PROJECT	Project	Konecny Markets Co.	261842	2022-01-21 10:42:29.040262+00	2022-01-21 10:42:29.040291+00	9	\N	\N	f	f
9744	PROJECT	Project	Kookies by Kathy	274679	2022-01-21 10:42:29.040352+00	2022-01-21 10:42:29.040381+00	9	\N	\N	f	f
9745	PROJECT	Project	Koshi Metal Fabricators Corporation	261843	2022-01-21 10:42:29.040441+00	2022-01-21 10:42:29.04047+00	9	\N	\N	f	f
9746	PROJECT	Project	Kovats Publishing	261844	2022-01-21 10:42:29.040531+00	2022-01-21 10:42:29.04056+00	9	\N	\N	f	f
9747	PROJECT	Project	Kramer Construction	261845	2022-01-21 10:42:29.04062+00	2022-01-21 10:42:29.040649+00	9	\N	\N	f	f
9748	PROJECT	Project	Krista Thomas Recruiting	261846	2022-01-21 10:42:29.040708+00	2022-01-21 10:42:29.040738+00	9	\N	\N	f	f
9749	PROJECT	Project	Kristen Welch	261847	2022-01-21 10:42:29.040799+00	2022-01-21 10:42:29.040828+00	9	\N	\N	f	f
9750	PROJECT	Project	Kristy Abercrombie	278578	2022-01-21 10:42:29.040888+00	2022-01-21 10:42:29.040917+00	9	\N	\N	f	f
9751	PROJECT	Project	Kroetz Electric Dynamics	261848	2022-01-21 10:42:29.040977+00	2022-01-21 10:42:29.041006+00	9	\N	\N	f	f
9752	PROJECT	Project	Kugan Autodesk Inc	261849	2022-01-21 10:42:29.058923+00	2022-01-21 10:42:29.059076+00	9	\N	\N	f	f
9753	PROJECT	Project	Kunstlinger Automotive Manufacturing	261850	2022-01-21 10:42:29.05924+00	2022-01-21 10:42:29.059294+00	9	\N	\N	f	f
9754	PROJECT	Project	Kyle Keosian	261851	2022-01-21 10:42:29.059419+00	2022-01-21 10:42:29.059469+00	9	\N	\N	f	f
9755	PROJECT	Project	Labarba Markets Corporation	261852	2022-01-21 10:42:29.059584+00	2022-01-21 10:42:29.059809+00	9	\N	\N	f	f
9756	PROJECT	Project	labhvam	290041	2022-01-21 10:42:29.05996+00	2022-01-21 10:42:29.060014+00	9	\N	\N	f	f
9757	PROJECT	Project	Laditka and Ceppetelli Publishing Holding Corp.	261853	2022-01-21 10:42:29.060144+00	2022-01-21 10:42:29.060197+00	9	\N	\N	f	f
9758	PROJECT	Project	Lafayette Hardware Services	261854	2022-01-21 10:42:29.06033+00	2022-01-21 10:42:29.060379+00	9	\N	\N	f	f
9759	PROJECT	Project	Lafayette Metal Fabricators Rentals	261855	2022-01-21 10:42:29.060496+00	2022-01-21 10:42:29.060541+00	9	\N	\N	f	f
9760	PROJECT	Project	La Grande Liquors Dynamics	261856	2022-01-21 10:42:29.060651+00	2022-01-21 10:42:29.060696+00	9	\N	\N	f	f
9761	PROJECT	Project	Lakeside Inc	261857	2022-01-21 10:42:29.060802+00	2022-01-21 10:42:29.060847+00	9	\N	\N	f	f
9762	PROJECT	Project	Lake Worth Markets Fabricators	261858	2022-01-21 10:42:29.060955+00	2022-01-21 10:42:29.061+00	9	\N	\N	f	f
9763	PROJECT	Project	Lancaster Liquors Inc.	261859	2022-01-21 10:42:29.061105+00	2022-01-21 10:42:29.061151+00	9	\N	\N	f	f
9764	PROJECT	Project	Lanning and Urraca Construction Corporation	261860	2022-01-21 10:42:29.061579+00	2022-01-21 10:42:29.061659+00	9	\N	\N	f	f
9765	PROJECT	Project	Laramie Construction Co.	261861	2022-01-21 10:42:29.061854+00	2022-01-21 10:42:29.061968+00	9	\N	\N	f	f
9766	PROJECT	Project	Largo Lumber Co.	261862	2022-01-21 10:42:29.062145+00	2022-01-21 10:42:29.062219+00	9	\N	\N	f	f
9767	PROJECT	Project	Lariosa Lumber Corporation	261863	2022-01-21 10:42:29.063715+00	2022-01-21 10:42:29.070814+00	9	\N	\N	f	f
9768	PROJECT	Project	Laser Images Inc.	261864	2022-01-21 10:42:29.074437+00	2022-01-21 10:42:29.074747+00	9	\N	\N	f	f
9769	PROJECT	Project	Las Vegas Electric Manufacturing	261865	2022-01-21 10:42:29.07496+00	2022-01-21 10:42:29.075018+00	9	\N	\N	f	f
9770	PROJECT	Project	Lawley and Barends Painting Distributors	261866	2022-01-21 10:42:29.075222+00	2022-01-21 10:42:29.075285+00	9	\N	\N	f	f
9771	PROJECT	Project	Lead 154	261867	2022-01-21 10:42:29.075432+00	2022-01-21 10:42:29.075765+00	9	\N	\N	f	f
9772	PROJECT	Project	Lead 155	261868	2022-01-21 10:42:29.076327+00	2022-01-21 10:42:29.076405+00	9	\N	\N	f	f
9773	PROJECT	Project	Leemans Builders Agency	261869	2022-01-21 10:42:29.076581+00	2022-01-21 10:42:29.076838+00	9	\N	\N	f	f
9774	PROJECT	Project	Lenza and Lanzoni Plumbing Co.	261870	2022-01-21 10:42:29.077022+00	2022-01-21 10:42:29.077087+00	9	\N	\N	f	f
9775	PROJECT	Project	Levitan Plumbing Dynamics	261871	2022-01-21 10:42:29.077239+00	2022-01-21 10:42:29.077495+00	9	\N	\N	f	f
9776	PROJECT	Project	Lew Plumbing	278579	2022-01-21 10:42:29.077669+00	2022-01-21 10:42:29.077731+00	9	\N	\N	f	f
9777	PROJECT	Project	Lexington Hospital Sales	261872	2022-01-21 10:42:29.07787+00	2022-01-21 10:42:29.077925+00	9	\N	\N	f	f
9778	PROJECT	Project	Liechti Lumber Sales	261873	2022-01-21 10:42:29.078086+00	2022-01-21 10:42:29.078137+00	9	\N	\N	f	f
9779	PROJECT	Project	Lillian Thurham	261874	2022-01-21 10:42:29.078264+00	2022-01-21 10:42:29.078312+00	9	\N	\N	f	f
9780	PROJECT	Project	Limbo Leasing Leasing	261875	2022-01-21 10:42:29.078429+00	2022-01-21 10:42:29.078473+00	9	\N	\N	f	f
9781	PROJECT	Project	Lina's Dance Studio	261876	2022-01-21 10:42:29.078582+00	2022-01-21 10:42:29.078628+00	9	\N	\N	f	f
9782	PROJECT	Project	Linberg Windows Agency	261877	2022-01-21 10:42:29.078738+00	2022-01-21 10:42:29.078784+00	9	\N	\N	f	f
9783	PROJECT	Project	Linderman Builders Agency	261878	2022-01-21 10:42:29.078895+00	2022-01-21 10:42:29.078942+00	9	\N	\N	f	f
9784	PROJECT	Project	Linder Windows Rentals	261879	2022-01-21 10:42:29.079259+00	2022-01-21 10:42:29.079299+00	9	\N	\N	f	f
9785	PROJECT	Project	Lindman and Kastens Antiques -	261880	2022-01-21 10:42:29.079362+00	2022-01-21 10:42:29.079392+00	9	\N	\N	f	f
9786	PROJECT	Project	Linear International Footwear	261881	2022-01-21 10:42:29.079452+00	2022-01-21 10:42:29.079482+00	9	\N	\N	f	f
9787	PROJECT	Project	Lintex Group	261882	2022-01-21 10:42:29.079543+00	2022-01-21 10:42:29.079572+00	9	\N	\N	f	f
9788	PROJECT	Project	Lisa Fiore	261883	2022-01-21 10:42:29.079634+00	2022-01-21 10:42:29.079663+00	9	\N	\N	f	f
9789	PROJECT	Project	Lisa Wilson	261884	2022-01-21 10:42:29.079724+00	2022-01-21 10:42:29.079754+00	9	\N	\N	f	f
9790	PROJECT	Project	Liverpool Hospital Leasing	261885	2022-01-21 10:42:29.079815+00	2022-01-21 10:42:29.079844+00	9	\N	\N	f	f
9791	PROJECT	Project	Lizarrago Markets Corporation	261886	2022-01-21 10:42:29.079904+00	2022-01-21 10:42:29.079933+00	9	\N	\N	f	f
9792	PROJECT	Project	Lobby Remodel	261887	2022-01-21 10:42:29.079994+00	2022-01-21 10:42:29.080135+00	9	\N	\N	f	f
9793	PROJECT	Project	Lodato Painting and Associates	261888	2022-01-21 10:42:29.080198+00	2022-01-21 10:42:29.080228+00	9	\N	\N	f	f
9794	PROJECT	Project	Loeza Catering Agency	261889	2022-01-21 10:42:29.080289+00	2022-01-21 10:42:29.080319+00	9	\N	\N	f	f
9795	PROJECT	Project	Lois Automotive Agency	261890	2022-01-21 10:42:29.080953+00	2022-01-21 10:42:29.087241+00	9	\N	\N	f	f
9796	PROJECT	Project	Lok's Management Co.	285880	2022-01-21 10:42:29.088853+00	2022-01-21 10:42:29.088938+00	9	\N	\N	f	f
9797	PROJECT	Project	Lomax Transportation	261891	2022-01-21 10:42:29.089131+00	2022-01-21 10:42:29.089189+00	9	\N	\N	f	f
9798	PROJECT	Project	Lompoc _ Systems	261892	2022-01-21 10:42:29.089289+00	2022-01-21 10:42:29.089329+00	9	\N	\N	f	f
9799	PROJECT	Project	Lonabaugh Markets Distributors	261893	2022-01-21 10:42:29.089421+00	2022-01-21 10:42:29.089464+00	9	\N	\N	f	f
9800	PROJECT	Project	Lorandeau Builders Holding Corp.	261894	2022-01-21 10:42:29.089557+00	2022-01-21 10:42:29.089597+00	9	\N	\N	f	f
9801	PROJECT	Project	Lou Baus	261895	2022-01-21 10:42:29.089909+00	2022-01-21 10:42:29.08996+00	9	\N	\N	f	f
9802	PROJECT	Project	Louis Fabre	261896	2022-01-21 10:42:29.107946+00	2022-01-21 10:42:29.108006+00	9	\N	\N	f	f
9803	PROJECT	Project	Loven and Frothingham Hardware Distributors	261897	2022-01-21 10:42:29.108133+00	2022-01-21 10:42:29.108477+00	9	\N	\N	f	f
9804	PROJECT	Project	Lucic and Perfect Publishing Systems	261898	2022-01-21 10:42:29.108776+00	2022-01-21 10:42:29.108813+00	9	\N	\N	f	f
9805	PROJECT	Project	Lucie Hospital Group	261899	2022-01-21 10:42:29.108881+00	2022-01-21 10:42:29.10891+00	9	\N	\N	f	f
9806	PROJECT	Project	Luffy Apartments Company	261900	2022-01-21 10:42:29.10897+00	2022-01-21 10:42:29.108999+00	9	\N	\N	f	f
9807	PROJECT	Project	Luigi Imports	261901	2022-01-21 10:42:29.10906+00	2022-01-21 10:42:29.109089+00	9	\N	\N	f	f
9808	PROJECT	Project	Lummus Telecom Rentals	261902	2022-01-21 10:42:29.109288+00	2022-01-21 10:42:29.109325+00	9	\N	\N	f	f
9809	PROJECT	Project	Lurtz Painting Co.	261903	2022-01-21 10:42:29.109928+00	2022-01-21 10:42:29.1101+00	9	\N	\N	f	f
9810	PROJECT	Project	Lyas Builders Inc.	261904	2022-01-21 10:42:29.110202+00	2022-01-21 10:42:29.110233+00	9	\N	\N	f	f
9811	PROJECT	Project	MAC	261905	2022-01-21 10:42:29.110296+00	2022-01-21 10:42:29.110326+00	9	\N	\N	f	f
9812	PROJECT	Project	Mackenzie Corporation	261906	2022-01-21 10:42:29.110386+00	2022-01-21 10:42:29.110416+00	9	\N	\N	f	f
9813	PROJECT	Project	Mackie Painting Company	261907	2022-01-21 10:42:29.110476+00	2022-01-21 10:42:29.110506+00	9	\N	\N	f	f
9814	PROJECT	Project	Malena Construction Fabricators	261908	2022-01-21 10:42:29.110566+00	2022-01-21 10:42:29.110595+00	9	\N	\N	f	f
9815	PROJECT	Project	Maleonado Publishing Company	261909	2022-01-21 10:42:29.110655+00	2022-01-21 10:42:29.110684+00	9	\N	\N	f	f
9816	PROJECT	Project	Mandos	261910	2022-01-21 10:42:29.110761+00	2022-01-21 10:42:29.11079+00	9	\N	\N	f	f
9817	PROJECT	Project	Manivong Apartments Incorporated	261911	2022-01-21 10:42:29.110851+00	2022-01-21 10:42:29.11088+00	9	\N	\N	f	f
9818	PROJECT	Project	Manwarren Markets Holding Corp.	261912	2022-01-21 10:42:29.110941+00	2022-01-21 10:42:29.11097+00	9	\N	\N	f	f
9819	PROJECT	Project	Maple Leaf Foods	261913	2022-01-21 10:42:29.111031+00	2022-01-21 10:42:29.11106+00	9	\N	\N	f	f
9820	PROJECT	Project	Marabella Title Agency	261914	2022-01-21 10:42:29.11112+00	2022-01-21 10:42:29.111149+00	9	\N	\N	f	f
9821	PROJECT	Project	Marietta Title Co.	261915	2022-01-21 10:42:29.111209+00	2022-01-21 10:42:29.111399+00	9	\N	\N	f	f
9822	PROJECT	Project	Marionneaux Catering Incorporated	261916	2022-01-21 10:42:29.111738+00	2022-01-21 10:42:29.11179+00	9	\N	\N	f	f
9823	PROJECT	Project	Mark Cho	274680	2022-01-21 10:42:29.111947+00	2022-01-21 10:42:29.111981+00	9	\N	\N	f	f
9824	PROJECT	Project	Markewich Builders Rentals	261917	2022-01-21 10:42:29.11205+00	2022-01-21 10:42:29.112078+00	9	\N	\N	f	f
9825	PROJECT	Project	Mark's Sporting Goods	261918	2022-01-21 10:42:29.112134+00	2022-01-21 10:42:29.112162+00	9	\N	\N	f	f
9826	PROJECT	Project	Marrello Software Services	261919	2022-01-21 10:42:29.112218+00	2022-01-21 10:42:29.112245+00	9	\N	\N	f	f
9827	PROJECT	Project	Marston Hardware -	261920	2022-01-21 10:42:29.112301+00	2022-01-21 10:42:29.112328+00	9	\N	\N	f	f
9828	PROJECT	Project	Martin Gelina	261921	2022-01-21 10:42:29.112385+00	2022-01-21 10:42:29.112413+00	9	\N	\N	f	f
9829	PROJECT	Project	Mason's Travel Services	261922	2022-01-21 10:42:29.112469+00	2022-01-21 10:42:29.112497+00	9	\N	\N	f	f
9830	PROJECT	Project	Matsuzaki Builders Services	261923	2022-01-21 10:42:29.112696+00	2022-01-21 10:42:29.112734+00	9	\N	\N	f	f
9831	PROJECT	Project	Matthew Davison	261924	2022-01-21 10:42:29.112791+00	2022-01-21 10:42:29.112818+00	9	\N	\N	f	f
9832	PROJECT	Project	Matzke Title Co.	261925	2022-01-21 10:42:29.112875+00	2022-01-21 10:42:29.112902+00	9	\N	\N	f	f
9833	PROJECT	Project	Maxx Corner Market	261926	2022-01-21 10:42:29.112959+00	2022-01-21 10:42:29.112986+00	9	\N	\N	f	f
9834	PROJECT	Project	Mcburnie Hardware Dynamics	261927	2022-01-21 10:42:29.113042+00	2022-01-21 10:42:29.113069+00	9	\N	\N	f	f
9835	PROJECT	Project	Mcdorman Software Holding Corp.	261928	2022-01-21 10:42:29.113126+00	2022-01-21 10:42:29.113153+00	9	\N	\N	f	f
9836	PROJECT	Project	McEdwards & Whitwell	261929	2022-01-21 10:42:29.113209+00	2022-01-21 10:42:29.113237+00	9	\N	\N	f	f
9837	PROJECT	Project	Mcelderry Apartments Systems	261930	2022-01-21 10:42:29.113293+00	2022-01-21 10:42:29.11332+00	9	\N	\N	f	f
9838	PROJECT	Project	Mcguff and Spriggins Hospital Group	261931	2022-01-21 10:42:29.113377+00	2022-01-21 10:42:29.113404+00	9	\N	\N	f	f
9839	PROJECT	Project	McKay Financial	261932	2022-01-21 10:42:29.11346+00	2022-01-21 10:42:29.113488+00	9	\N	\N	f	f
9840	PROJECT	Project	Mcoy and Donlin Attorneys Sales	261933	2022-01-21 10:42:29.113667+00	2022-01-21 10:42:29.113697+00	9	\N	\N	f	f
9841	PROJECT	Project	Medcan Mgmt Inc	261934	2022-01-21 10:42:29.113867+00	2022-01-21 10:42:29.113986+00	9	\N	\N	f	f
9842	PROJECT	Project	Medved	261935	2022-01-21 10:42:29.114117+00	2022-01-21 10:42:29.114163+00	9	\N	\N	f	f
9843	PROJECT	Project	Megaloid labs	261936	2022-01-21 10:42:29.114336+00	2022-01-21 10:42:29.114386+00	9	\N	\N	f	f
9844	PROJECT	Project	Meisner Software Inc.	261937	2022-01-21 10:42:29.114498+00	2022-01-21 10:42:29.114719+00	9	\N	\N	f	f
9845	PROJECT	Project	Mele Plumbing Manufacturing	261938	2022-01-21 10:42:29.114881+00	2022-01-21 10:42:29.114935+00	9	\N	\N	f	f
9846	PROJECT	Project	Melissa Wine Shop	261939	2022-01-21 10:42:29.116047+00	2022-01-21 10:42:29.116198+00	9	\N	\N	f	f
9847	PROJECT	Project	Melville Painting Rentals	261940	2022-01-21 10:42:29.116419+00	2022-01-21 10:42:29.116481+00	9	\N	\N	f	f
9848	PROJECT	Project	Meneses Telecom Corporation	261941	2022-01-21 10:42:29.116954+00	2022-01-21 10:42:29.117081+00	9	\N	\N	f	f
9849	PROJECT	Project	Mentor Graphics	261942	2022-01-21 10:42:29.117231+00	2022-01-21 10:42:29.117269+00	9	\N	\N	f	f
9850	PROJECT	Project	Micehl Bertrand	261943	2022-01-21 10:42:29.118043+00	2022-01-21 10:42:29.118084+00	9	\N	\N	f	f
9851	PROJECT	Project	Michael Jannsen	261944	2022-01-21 10:42:29.118216+00	2022-01-21 10:42:29.118302+00	9	\N	\N	f	f
9852	PROJECT	Project	Michael Spencer	261945	2022-01-21 10:42:29.123978+00	2022-01-21 10:42:29.124017+00	9	\N	\N	f	f
9853	PROJECT	Project	Michael Wakefield	261946	2022-01-21 10:42:29.124076+00	2022-01-21 10:42:29.124104+00	9	\N	\N	f	f
9854	PROJECT	Project	Microskills	261947	2022-01-21 10:42:29.124161+00	2022-01-21 10:42:29.124189+00	9	\N	\N	f	f
9855	PROJECT	Project	Midgette Markets	261948	2022-01-21 10:42:29.124246+00	2022-01-21 10:42:29.124274+00	9	\N	\N	f	f
9856	PROJECT	Project	Mike Dee	261949	2022-01-21 10:42:29.12433+00	2022-01-21 10:42:29.124358+00	9	\N	\N	f	f
9857	PROJECT	Project	Mike Franko	261950	2022-01-21 10:42:29.124414+00	2022-01-21 10:42:29.124442+00	9	\N	\N	f	f
9858	PROJECT	Project	Mike Miller	261951	2022-01-21 10:42:29.124498+00	2022-01-21 10:42:29.124526+00	9	\N	\N	f	f
9859	PROJECT	Project	Millenium Engineering	261952	2022-01-21 10:42:29.124723+00	2022-01-21 10:42:29.124763+00	9	\N	\N	f	f
9860	PROJECT	Project	Miller's Dry Cleaning	261953	2022-01-21 10:42:29.124821+00	2022-01-21 10:42:29.124849+00	9	\N	\N	f	f
9861	PROJECT	Project	Mindy Peiris	261954	2022-01-21 10:42:29.124906+00	2022-01-21 10:42:29.124934+00	9	\N	\N	f	f
9862	PROJECT	Project	Mineral Painting Inc.	261955	2022-01-21 10:42:29.12499+00	2022-01-21 10:42:29.125018+00	9	\N	\N	f	f
9863	PROJECT	Project	Miquel Apartments Leasing	261956	2022-01-21 10:42:29.125075+00	2022-01-21 10:42:29.125103+00	9	\N	\N	f	f
9864	PROJECT	Project	Mission Liquors	261957	2022-01-21 10:42:29.125159+00	2022-01-21 10:42:29.125187+00	9	\N	\N	f	f
9865	PROJECT	Project	Mitani Hardware Company	261958	2022-01-21 10:42:29.125244+00	2022-01-21 10:42:29.125272+00	9	\N	\N	f	f
9866	PROJECT	Project	Mitchell & assoc	261959	2022-01-21 10:42:29.125328+00	2022-01-21 10:42:29.125356+00	9	\N	\N	f	f
9867	PROJECT	Project	Mitchelle Title -	261960	2022-01-21 10:42:29.125412+00	2022-01-21 10:42:29.12544+00	9	\N	\N	f	f
9868	PROJECT	Project	Mitra	261961	2022-01-21 10:42:29.125497+00	2022-01-21 10:42:29.12608+00	9	\N	\N	f	f
9869	PROJECT	Project	Mobile App Redesign	284468	2022-01-21 10:42:29.126289+00	2022-01-21 10:42:29.126324+00	9	\N	\N	f	f
9870	PROJECT	Project	Molesworth and Repress Liquors Leasing	261962	2022-01-21 10:42:29.126388+00	2022-01-21 10:42:29.126418+00	9	\N	\N	f	f
9871	PROJECT	Project	Momphard Painting Sales	261963	2022-01-21 10:42:29.126479+00	2022-01-21 10:42:29.126509+00	9	\N	\N	f	f
9872	PROJECT	Project	Monica Parker	261964	2022-01-21 10:42:29.126689+00	2022-01-21 10:42:29.126722+00	9	\N	\N	f	f
9873	PROJECT	Project	Moores Builders Agency	261965	2022-01-21 10:42:29.126784+00	2022-01-21 10:42:29.126813+00	9	\N	\N	f	f
9874	PROJECT	Project	Moots Painting Distributors	261966	2022-01-21 10:42:29.126874+00	2022-01-21 10:42:29.126903+00	9	\N	\N	f	f
9875	PROJECT	Project	Moreb Plumbing Corporation	261967	2022-01-21 10:42:29.126964+00	2022-01-21 10:42:29.126993+00	9	\N	\N	f	f
9876	PROJECT	Project	Mortgage Center	261968	2022-01-21 10:42:29.127053+00	2022-01-21 10:42:29.127083+00	9	\N	\N	f	f
9877	PROJECT	Project	Moss Builders	261969	2022-01-21 10:42:29.127144+00	2022-01-21 10:42:29.127173+00	9	\N	\N	f	f
9878	PROJECT	Project	Moturu Tapasvi	278580	2022-01-21 10:42:29.127315+00	2022-01-21 10:42:29.127357+00	9	\N	\N	f	f
9879	PROJECT	Project	Mount Lake Terrace Markets Fabricators	261970	2022-01-21 10:42:29.127424+00	2022-01-21 10:42:29.127454+00	9	\N	\N	f	f
9880	PROJECT	Project	Moving Store	261971	2022-01-21 10:42:29.127762+00	2022-01-21 10:42:29.127799+00	9	\N	\N	f	f
9881	PROJECT	Project	MPower	261972	2022-01-21 10:42:29.127862+00	2022-01-21 10:42:29.127903+00	9	\N	\N	f	f
9882	PROJECT	Project	MuscleTech	261973	2022-01-21 10:42:29.128022+00	2022-01-21 10:42:29.128053+00	9	\N	\N	f	f
9883	PROJECT	Project	MW International (CAD)	261974	2022-01-21 10:42:29.128116+00	2022-01-21 10:42:29.128145+00	9	\N	\N	f	f
9884	PROJECT	Project	Nadia Phillipchuk	278581	2022-01-21 10:42:29.128206+00	2022-01-21 10:42:29.128246+00	9	\N	\N	f	f
9885	PROJECT	Project	Nania Painting Networking	261975	2022-01-21 10:42:29.128365+00	2022-01-21 10:42:29.128413+00	9	\N	\N	f	f
9886	PROJECT	Project	Neal Ferguson	261976	2022-01-21 10:42:29.128546+00	2022-01-21 10:42:29.128718+00	9	\N	\N	f	f
9887	PROJECT	Project	Nephew Publishing Group	261977	2022-01-21 10:42:29.128876+00	2022-01-21 10:42:29.129098+00	9	\N	\N	f	f
9888	PROJECT	Project	NetPace Promotions	261978	2022-01-21 10:42:29.129259+00	2022-01-21 10:42:29.129421+00	9	\N	\N	f	f
9889	PROJECT	Project	NetStar Inc	261979	2022-01-21 10:42:29.1295+00	2022-01-21 10:42:29.12953+00	9	\N	\N	f	f
9890	PROJECT	Project	NetSuite Incorp	261980	2022-01-21 10:42:29.129591+00	2022-01-21 10:42:29.12962+00	9	\N	\N	f	f
9891	PROJECT	Project	New Design of Rack	261981	2022-01-21 10:42:29.129681+00	2022-01-21 10:42:29.12971+00	9	\N	\N	f	f
9892	PROJECT	Project	New Server Rack Design	261982	2022-01-21 10:42:29.129899+00	2022-01-21 10:42:29.12993+00	9	\N	\N	f	f
9893	PROJECT	Project	New Ventures	261983	2022-01-21 10:42:29.12999+00	2022-01-21 10:42:29.13002+00	9	\N	\N	f	f
9894	PROJECT	Project	Niedzwiedz Antiques and Associates	261984	2022-01-21 10:42:29.130081+00	2022-01-21 10:42:29.13011+00	9	\N	\N	f	f
9895	PROJECT	Project	Nikon	261985	2022-01-21 10:42:29.130248+00	2022-01-21 10:42:29.130281+00	9	\N	\N	f	f
9896	PROJECT	Project	Nilesh	274681	2022-01-21 10:42:29.130344+00	2022-01-21 10:42:29.130374+00	9	\N	\N	f	f
9897	PROJECT	Project	Nilesh Pant	290077	2022-01-21 10:42:29.130751+00	2022-01-21 10:42:29.130806+00	9	\N	\N	f	f
9898	PROJECT	Project	Nordon Metal Fabricators Systems	261986	2022-01-21 10:42:29.130892+00	2022-01-21 10:42:29.135911+00	9	\N	\N	f	f
9899	PROJECT	Project	Novida and Chochrek Leasing Manufacturing	261987	2022-01-21 10:42:29.137679+00	2022-01-21 10:42:29.13777+00	9	\N	\N	f	f
9900	PROJECT	Project	Novx	261988	2022-01-21 10:42:29.138012+00	2022-01-21 10:42:29.138083+00	9	\N	\N	f	f
9901	PROJECT	Project	Oaks and Winters Inc	261989	2022-01-21 10:42:29.138213+00	2022-01-21 10:42:29.138255+00	9	\N	\N	f	f
9902	PROJECT	Project	Oceanside Hardware	261990	2022-01-21 10:42:29.165497+00	2022-01-21 10:42:29.165766+00	9	\N	\N	f	f
9903	PROJECT	Project	Oconner _ Holding Corp.	261991	2022-01-21 10:42:29.166059+00	2022-01-21 10:42:29.166146+00	9	\N	\N	f	f
9904	PROJECT	Project	Oeder Liquors Company	261992	2022-01-21 10:42:29.16634+00	2022-01-21 10:42:29.166405+00	9	\N	\N	f	f
9905	PROJECT	Project	Oestreich Liquors Inc.	261993	2022-01-21 10:42:29.1679+00	2022-01-21 10:42:29.168032+00	9	\N	\N	f	f
9906	PROJECT	Project	Office Remodel	261994	2022-01-21 10:42:29.17161+00	2022-01-21 10:42:29.171688+00	9	\N	\N	f	f
9907	PROJECT	Project	Oiler Corporation	261995	2022-01-21 10:42:29.171791+00	2022-01-21 10:42:29.171921+00	9	\N	\N	f	f
9908	PROJECT	Project	Oldsmar Liquors and Associates	261996	2022-01-21 10:42:29.172041+00	2022-01-21 10:42:29.172073+00	9	\N	\N	f	f
9909	PROJECT	Project	Oliver Skin Supplies	261997	2022-01-21 10:42:29.172164+00	2022-01-21 10:42:29.172195+00	9	\N	\N	f	f
9910	PROJECT	Project	Olympia Antiques Management	261998	2022-01-21 10:42:29.172272+00	2022-01-21 10:42:29.172302+00	9	\N	\N	f	f
9911	PROJECT	Project	ONLINE1	261999	2022-01-21 10:42:29.172363+00	2022-01-21 10:42:29.172394+00	9	\N	\N	f	f
9912	PROJECT	Project	Orange Leasing -	262000	2022-01-21 10:42:29.172455+00	2022-01-21 10:42:29.172494+00	9	\N	\N	f	f
9913	PROJECT	Project	OREA	262001	2022-01-21 10:42:29.172731+00	2022-01-21 10:42:29.172764+00	9	\N	\N	f	f
9914	PROJECT	Project	Orion Hardware	262002	2022-01-21 10:42:29.172829+00	2022-01-21 10:42:29.172861+00	9	\N	\N	f	f
9915	PROJECT	Project	Orlando Automotive Leasing	262003	2022-01-21 10:42:29.172935+00	2022-01-21 10:42:29.172965+00	9	\N	\N	f	f
9916	PROJECT	Project	Ornelas and Ciejka Painting and Associates	262004	2022-01-21 10:42:29.173029+00	2022-01-21 10:42:29.173082+00	9	\N	\N	f	f
9917	PROJECT	Project	Ortego Construction Distributors	262005	2022-01-21 10:42:29.173145+00	2022-01-21 10:42:29.173185+00	9	\N	\N	f	f
9918	PROJECT	Project	Osler Antiques -	262006	2022-01-21 10:42:29.173249+00	2022-01-21 10:42:29.173278+00	9	\N	\N	f	f
9919	PROJECT	Project	OSPE Inc	262007	2022-01-21 10:42:29.173368+00	2022-01-21 10:42:29.173552+00	9	\N	\N	f	f
9920	PROJECT	Project	Ostling Metal Fabricators Fabricators	262008	2022-01-21 10:42:29.17364+00	2022-01-21 10:42:29.173671+00	9	\N	\N	f	f
9921	PROJECT	Project	Ostrzyeki Markets Distributors	262009	2022-01-21 10:42:29.173745+00	2022-01-21 10:42:29.173776+00	9	\N	\N	f	f
9922	PROJECT	Project	Owasso Attorneys Holding Corp.	262010	2022-01-21 10:42:29.173838+00	2022-01-21 10:42:29.173891+00	9	\N	\N	f	f
9923	PROJECT	Project	Oxon Insurance Agency	278582	2022-01-21 10:42:29.173954+00	2022-01-21 10:42:29.173994+00	9	\N	\N	f	f
9924	PROJECT	Project	Oxon Insurance Agency:Oxon - Holiday Party	285881	2022-01-21 10:42:29.174058+00	2022-01-21 10:42:29.174087+00	9	\N	\N	f	f
9925	PROJECT	Project	Oxon Insurance Agency:Oxon -- Holiday Party	278583	2022-01-21 10:42:29.174176+00	2022-01-21 10:42:29.174207+00	9	\N	\N	f	f
9926	PROJECT	Project	Oxon Insurance Agency:Oxon - Retreat	278584	2022-01-21 10:42:29.174281+00	2022-01-21 10:42:29.174311+00	9	\N	\N	f	f
9927	PROJECT	Project	Oxon Insurance Agency:Oxon - Retreat 2014	285882	2022-01-21 10:42:29.174373+00	2022-01-21 10:42:29.174404+00	9	\N	\N	f	f
9928	PROJECT	Project	Pacific Northwest	262011	2022-01-21 10:42:29.17449+00	2022-01-21 10:42:29.17452+00	9	\N	\N	f	f
9929	PROJECT	Project	Pagliari Builders Services	262012	2022-01-21 10:42:29.174768+00	2022-01-21 10:42:29.17481+00	9	\N	\N	f	f
9930	PROJECT	Project	Palmer and Barnar Liquors Leasing	262013	2022-01-21 10:42:29.174877+00	2022-01-21 10:42:29.174906+00	9	\N	\N	f	f
9931	PROJECT	Project	Palmisano Hospital Fabricators	262014	2022-01-21 10:42:29.174995+00	2022-01-21 10:42:29.175026+00	9	\N	\N	f	f
9932	PROJECT	Project	Palys Attorneys	262015	2022-01-21 10:42:29.175099+00	2022-01-21 10:42:29.175129+00	9	\N	\N	f	f
9933	PROJECT	Project	Panora Lumber Dynamics	262016	2022-01-21 10:42:29.175191+00	2022-01-21 10:42:29.175234+00	9	\N	\N	f	f
9934	PROJECT	Project	Parking Lot Construction	262017	2022-01-21 10:42:29.175309+00	2022-01-21 10:42:29.175339+00	9	\N	\N	f	f
9935	PROJECT	Project	Pasanen Attorneys Agency	262018	2022-01-21 10:42:29.175409+00	2022-01-21 10:42:29.175438+00	9	\N	\N	f	f
9936	PROJECT	Project	Patel Cafe	262019	2022-01-21 10:42:29.175499+00	2022-01-21 10:42:29.175649+00	9	\N	\N	f	f
9937	PROJECT	Project	Paulsen Medical Supplies	274682	2022-01-21 10:42:29.175713+00	2022-01-21 10:42:29.175743+00	9	\N	\N	f	f
9938	PROJECT	Project	Paveglio Leasing Leasing	262020	2022-01-21 10:42:29.175804+00	2022-01-21 10:42:29.175842+00	9	\N	\N	f	f
9939	PROJECT	Project	Peak Products	262021	2022-01-21 10:42:29.175917+00	2022-01-21 10:42:29.175948+00	9	\N	\N	f	f
9940	PROJECT	Project	Penalver Automotive and Associates	262022	2022-01-21 10:42:29.17601+00	2022-01-21 10:42:29.17604+00	9	\N	\N	f	f
9941	PROJECT	Project	Penco Medical Inc.	262023	2022-01-21 10:42:29.176103+00	2022-01-21 10:42:29.176142+00	9	\N	\N	f	f
9942	PROJECT	Project	Penister Hospital Fabricators	262024	2022-01-21 10:42:29.176205+00	2022-01-21 10:42:29.176236+00	9	\N	\N	f	f
9943	PROJECT	Project	Pertuit Liquors Management	262025	2022-01-21 10:42:29.176298+00	2022-01-21 10:42:29.176328+00	9	\N	\N	f	f
9944	PROJECT	Project	Peterson Builders & Assoc	262026	2022-01-21 10:42:29.176389+00	2022-01-21 10:42:29.17642+00	9	\N	\N	f	f
9945	PROJECT	Project	Petticrew Apartments Incorporated	262027	2022-01-21 10:42:29.177276+00	2022-01-21 10:42:29.177438+00	9	\N	\N	f	f
9946	PROJECT	Project	Peveler and Tyrer Software Networking	262028	2022-01-21 10:42:29.177785+00	2022-01-21 10:42:29.177822+00	9	\N	\N	f	f
9947	PROJECT	Project	Phillip Van Hook	262029	2022-01-21 10:42:29.177919+00	2022-01-21 10:42:29.17795+00	9	\N	\N	f	f
9948	PROJECT	Project	Pickler Construction Leasing	262030	2022-01-21 10:42:29.178025+00	2022-01-21 10:42:29.178056+00	9	\N	\N	f	f
9949	PROJECT	Project	Pigler Plumbing Management	262031	2022-01-21 10:42:29.17812+00	2022-01-21 10:42:29.178154+00	9	\N	\N	f	f
9950	PROJECT	Project	Pilkerton Windows Sales	262032	2022-01-21 10:42:29.178238+00	2022-01-21 10:42:29.178268+00	9	\N	\N	f	f
9951	PROJECT	Project	Pitney Bowes	262033	2022-01-21 10:42:29.178342+00	2022-01-21 10:42:29.178372+00	9	\N	\N	f	f
9952	PROJECT	Project	Pittaway Inc	262034	2022-01-21 10:42:29.191913+00	2022-01-21 10:42:29.191966+00	9	\N	\N	f	f
9953	PROJECT	Project	Pittsburgh Quantum Analytics	262035	2022-01-21 10:42:29.192035+00	2022-01-21 10:42:29.192065+00	9	\N	\N	f	f
9954	PROJECT	Project	Pittsburgh Windows Incorporated	262036	2022-01-21 10:42:29.192154+00	2022-01-21 10:42:29.192184+00	9	\N	\N	f	f
9955	PROJECT	Project	Plantronics (EUR)	262037	2022-01-21 10:42:29.192246+00	2022-01-21 10:42:29.192275+00	9	\N	\N	f	f
9956	PROJECT	Project	Platform APIs	284469	2022-01-21 10:42:29.192364+00	2022-01-21 10:42:29.192395+00	9	\N	\N	f	f
9957	PROJECT	Project	Plexfase Construction Inc.	262038	2022-01-21 10:42:29.192457+00	2022-01-21 10:42:29.192486+00	9	\N	\N	f	f
9958	PROJECT	Project	Podvin Software Networking	262039	2022-01-21 10:42:29.192766+00	2022-01-21 10:42:29.192922+00	9	\N	\N	f	f
9959	PROJECT	Project	Poland and Burrus Plumbing	262040	2022-01-21 10:42:29.193011+00	2022-01-21 10:42:29.193042+00	9	\N	\N	f	f
9960	PROJECT	Project	Polard Windows	262041	2022-01-21 10:42:29.193132+00	2022-01-21 10:42:29.193162+00	9	\N	\N	f	f
9961	PROJECT	Project	Pomona Hardware Leasing	262042	2022-01-21 10:42:29.193238+00	2022-01-21 10:42:29.193268+00	9	\N	\N	f	f
9962	PROJECT	Project	Ponniah	262043	2022-01-21 10:42:29.193329+00	2022-01-21 10:42:29.193363+00	9	\N	\N	f	f
9963	PROJECT	Project	Port Angeles Telecom Networking	262044	2022-01-21 10:42:29.193636+00	2022-01-21 10:42:29.19368+00	9	\N	\N	f	f
9964	PROJECT	Project	Port Townsend Title Corporation	262045	2022-01-21 10:42:29.193775+00	2022-01-21 10:42:29.193805+00	9	\N	\N	f	f
9965	PROJECT	Project	Pote Leasing Rentals	262046	2022-01-21 10:42:29.193866+00	2022-01-21 10:42:29.193895+00	9	\N	\N	f	f
9966	PROJECT	Project	Primas Consulting	262047	2022-01-21 10:42:29.193956+00	2022-01-21 10:42:29.194012+00	9	\N	\N	f	f
9967	PROJECT	Project	Princeton Automotive Management	262048	2022-01-21 10:42:29.194074+00	2022-01-21 10:42:29.194104+00	9	\N	\N	f	f
9968	PROJECT	Project	Pritts Construction Distributors	262049	2022-01-21 10:42:29.194177+00	2022-01-21 10:42:29.194206+00	9	\N	\N	f	f
9969	PROJECT	Project	Progress Inc	262050	2022-01-21 10:42:29.194282+00	2022-01-21 10:42:29.194323+00	9	\N	\N	f	f
9970	PROJECT	Project	Project 1	261068	2022-01-21 10:42:29.194632+00	2022-01-21 10:42:29.194683+00	9	\N	\N	f	f
9971	PROJECT	Project	Project 10	261077	2022-01-21 10:42:29.194763+00	2022-01-21 10:42:29.194792+00	9	\N	\N	f	f
9972	PROJECT	Project	Project 2	261069	2022-01-21 10:42:29.194867+00	2022-01-21 10:42:29.194897+00	9	\N	\N	f	f
9973	PROJECT	Project	Project 3	261070	2022-01-21 10:42:29.194969+00	2022-01-21 10:42:29.194999+00	9	\N	\N	f	f
9974	PROJECT	Project	Project 4	261071	2022-01-21 10:42:29.195073+00	2022-01-21 10:42:29.195118+00	9	\N	\N	f	f
9975	PROJECT	Project	Project 5	261072	2022-01-21 10:42:29.195182+00	2022-01-21 10:42:29.19522+00	9	\N	\N	f	f
9976	PROJECT	Project	Project 6	261073	2022-01-21 10:42:29.195282+00	2022-01-21 10:42:29.195311+00	9	\N	\N	f	f
9977	PROJECT	Project	Project 7	261074	2022-01-21 10:42:29.1954+00	2022-01-21 10:42:29.195431+00	9	\N	\N	f	f
9978	PROJECT	Project	Project 8	261075	2022-01-21 10:42:29.195608+00	2022-01-21 10:42:29.195642+00	9	\N	\N	f	f
9979	PROJECT	Project	Project 9	261076	2022-01-21 10:42:29.195725+00	2022-01-21 10:42:29.195755+00	9	\N	\N	f	f
9980	PROJECT	Project	Project Red	261119	2022-01-21 10:42:29.195829+00	2022-01-21 10:42:29.195858+00	9	\N	\N	f	f
9981	PROJECT	Project	Prokup Plumbing Corporation	262051	2022-01-21 10:42:29.195921+00	2022-01-21 10:42:29.195973+00	9	\N	\N	f	f
9982	PROJECT	Project	Prudential	262052	2022-01-21 10:42:29.196036+00	2022-01-21 10:42:29.196077+00	9	\N	\N	f	f
9983	PROJECT	Project	Ptomey Title Group	262053	2022-01-21 10:42:29.196139+00	2022-01-21 10:42:29.196168+00	9	\N	\N	f	f
9984	PROJECT	Project	Pueblo Construction Fabricators	262054	2022-01-21 10:42:29.196248+00	2022-01-21 10:42:29.196287+00	9	\N	\N	f	f
9985	PROJECT	Project	Pulse	262055	2022-01-21 10:42:29.196703+00	2022-01-21 10:42:29.196901+00	9	\N	\N	f	f
9986	PROJECT	Project	Purchase Construction Agency	262056	2022-01-21 10:42:29.19779+00	2022-01-21 10:42:29.197851+00	9	\N	\N	f	f
9987	PROJECT	Project	Puyallup Liquors Networking	262057	2022-01-21 10:42:29.197977+00	2022-01-21 10:42:29.198028+00	9	\N	\N	f	f
9988	PROJECT	Project	Pye's Cakes	274683	2022-01-21 10:42:29.198153+00	2022-01-21 10:42:29.198209+00	9	\N	\N	f	f
9989	PROJECT	Project	qa 54	262058	2022-01-21 10:42:29.198327+00	2022-01-21 10:42:29.198378+00	9	\N	\N	f	f
9990	PROJECT	Project	QJunction Inc	262059	2022-01-21 10:42:29.198942+00	2022-01-21 10:42:29.199132+00	9	\N	\N	f	f
9991	PROJECT	Project	Qualle Metal Fabricators Distributors	262060	2022-01-21 10:42:29.199324+00	2022-01-21 10:42:29.199383+00	9	\N	\N	f	f
9992	PROJECT	Project	Quantum X	262061	2022-01-21 10:42:29.199709+00	2022-01-21 10:42:29.199776+00	9	\N	\N	f	f
9993	PROJECT	Project	Quezad Lumber Leasing	262062	2022-01-21 10:42:29.199926+00	2022-01-21 10:42:29.200071+00	9	\N	\N	f	f
9994	PROJECT	Project	Quiterio Windows Co.	262063	2022-01-21 10:42:29.200226+00	2022-01-21 10:42:29.200295+00	9	\N	\N	f	f
9995	PROJECT	Project	Rabeck Liquors Group	262064	2022-01-21 10:42:29.200638+00	2022-01-21 10:42:29.200749+00	9	\N	\N	f	f
9996	PROJECT	Project	Rago Travel Agency	274684	2022-01-21 10:42:29.200852+00	2022-01-21 10:42:29.200883+00	9	\N	\N	f	f
10070	PROJECT	Project	Sandy Whines	262123	2022-01-21 10:42:29.241125+00	2022-01-21 10:42:29.241154+00	9	\N	\N	f	f
9997	PROJECT	Project	Ralphs Attorneys Group	262065	2022-01-21 10:42:29.200952+00	2022-01-21 10:42:29.200987+00	9	\N	\N	f	f
9998	PROJECT	Project	Ramal Builders Incorporated	262066	2022-01-21 10:42:29.20105+00	2022-01-21 10:42:29.20108+00	9	\N	\N	f	f
9999	PROJECT	Project	Ramsy Publishing Company	262067	2022-01-21 10:42:29.201144+00	2022-01-21 10:42:29.201173+00	9	\N	\N	f	f
10000	PROJECT	Project	Randy James	262068	2022-01-21 10:42:29.201248+00	2022-01-21 10:42:29.201279+00	9	\N	\N	f	f
10001	PROJECT	Project	Randy Rudd	262069	2022-01-21 10:42:29.201344+00	2022-01-21 10:42:29.201397+00	9	\N	\N	f	f
10002	PROJECT	Project	Rastorfer Automotive Holding Corp.	262070	2022-01-21 10:42:29.211138+00	2022-01-21 10:42:29.211183+00	9	\N	\N	f	f
10003	PROJECT	Project	Ras Windows -	262071	2022-01-21 10:42:29.211252+00	2022-01-21 10:42:29.211293+00	9	\N	\N	f	f
10004	PROJECT	Project	Rauf Catering	262072	2022-01-21 10:42:29.211358+00	2022-01-21 10:42:29.211391+00	9	\N	\N	f	f
10005	PROJECT	Project	Redick Antiques Inc.	262073	2022-01-21 10:42:29.211671+00	2022-01-21 10:42:29.21171+00	9	\N	\N	f	f
10006	PROJECT	Project	RedPath Sugars	262074	2022-01-21 10:42:29.211806+00	2022-01-21 10:42:29.211837+00	9	\N	\N	f	f
10007	PROJECT	Project	Red Rock Diner	274685	2022-01-21 10:42:29.211901+00	2022-01-21 10:42:29.211931+00	9	\N	\N	f	f
10008	PROJECT	Project	Reedus Telecom Group	262075	2022-01-21 10:42:29.211993+00	2022-01-21 10:42:29.212022+00	9	\N	\N	f	f
10009	PROJECT	Project	Refco	262076	2022-01-21 10:42:29.212111+00	2022-01-21 10:42:29.212142+00	9	\N	\N	f	f
10010	PROJECT	Project	Reinfeld and Jurczak Hospital Incorporated	262077	2022-01-21 10:42:29.212219+00	2022-01-21 10:42:29.212249+00	9	\N	\N	f	f
10011	PROJECT	Project	Reinhardt and Sabori Painting Group	262078	2022-01-21 10:42:29.212311+00	2022-01-21 10:42:29.212344+00	9	\N	\N	f	f
10012	PROJECT	Project	Reisdorf Title Services	262079	2022-01-21 10:42:29.21243+00	2022-01-21 10:42:29.212459+00	9	\N	\N	f	f
10013	PROJECT	Project	Reisman Windows Management	262080	2022-01-21 10:42:29.21252+00	2022-01-21 10:42:29.212761+00	9	\N	\N	f	f
10014	PROJECT	Project	Remodel	262081	2022-01-21 10:42:29.212914+00	2022-01-21 10:42:29.212969+00	9	\N	\N	f	f
10015	PROJECT	Project	Rennemeyer Liquors Systems	262082	2022-01-21 10:42:29.213159+00	2022-01-21 10:42:29.213211+00	9	\N	\N	f	f
10016	PROJECT	Project	Republic Builders and Associates	262083	2022-01-21 10:42:29.213381+00	2022-01-21 10:42:29.213941+00	9	\N	\N	f	f
10017	PROJECT	Project	Rey Software Inc.	262084	2022-01-21 10:42:29.214249+00	2022-01-21 10:42:29.214288+00	9	\N	\N	f	f
10018	PROJECT	Project	Rezentes Catering Dynamics	262085	2022-01-21 10:42:29.214354+00	2022-01-21 10:42:29.214385+00	9	\N	\N	f	f
10019	PROJECT	Project	Rhody Leasing and Associates	262086	2022-01-21 10:42:29.214811+00	2022-01-21 10:42:29.214906+00	9	\N	\N	f	f
10020	PROJECT	Project	Rickers Apartments Company	262087	2022-01-21 10:42:29.215016+00	2022-01-21 10:42:29.21515+00	9	\N	\N	f	f
10021	PROJECT	Project	Ridderhoff Painting Services	262088	2022-01-21 10:42:29.215243+00	2022-01-21 10:42:29.215273+00	9	\N	\N	f	f
10022	PROJECT	Project	Ridgeway Corporation	262089	2022-01-21 10:42:29.216613+00	2022-01-21 10:42:29.21803+00	9	\N	\N	f	f
10023	PROJECT	Project	Riede Title and Associates	262090	2022-01-21 10:42:29.218292+00	2022-01-21 10:42:29.218352+00	9	\N	\N	f	f
10024	PROJECT	Project	Rio Rancho Painting Agency	262091	2022-01-21 10:42:29.220074+00	2022-01-21 10:42:29.220162+00	9	\N	\N	f	f
10025	PROJECT	Project	Riverside Hospital and Associates	262092	2022-01-21 10:42:29.220323+00	2022-01-21 10:42:29.220375+00	9	\N	\N	f	f
10026	PROJECT	Project	Robare Builders Corporation	262093	2022-01-21 10:42:29.220498+00	2022-01-21 10:42:29.220546+00	9	\N	\N	f	f
10027	PROJECT	Project	Rob deMontarnal	278585	2022-01-21 10:42:29.220783+00	2022-01-21 10:42:29.220831+00	9	\N	\N	f	f
10028	PROJECT	Project	Robert Brady	262094	2022-01-21 10:42:29.220956+00	2022-01-21 10:42:29.221005+00	9	\N	\N	f	f
10029	PROJECT	Project	Robert Huffman	262095	2022-01-21 10:42:29.22143+00	2022-01-21 10:42:29.221479+00	9	\N	\N	f	f
10030	PROJECT	Project	Robert Lee	262096	2022-01-21 10:42:29.221748+00	2022-01-21 10:42:29.221784+00	9	\N	\N	f	f
10031	PROJECT	Project	Robert Solan	262097	2022-01-21 10:42:29.22185+00	2022-01-21 10:42:29.221906+00	9	\N	\N	f	f
10032	PROJECT	Project	Rogers Communication	262098	2022-01-21 10:42:29.221971+00	2022-01-21 10:42:29.222002+00	9	\N	\N	f	f
10033	PROJECT	Project	Rondonuwu Fruit and Vegi	274686	2022-01-21 10:42:29.222077+00	2022-01-21 10:42:29.222107+00	9	\N	\N	f	f
10034	PROJECT	Project	Rosner and Savo Antiques Systems	262099	2022-01-21 10:42:29.222184+00	2022-01-21 10:42:29.222225+00	9	\N	\N	f	f
10035	PROJECT	Project	Ross Nepean	262100	2022-01-21 10:42:29.222287+00	2022-01-21 10:42:29.222327+00	9	\N	\N	f	f
10036	PROJECT	Project	Roswell Leasing Management	262101	2022-01-21 10:42:29.22239+00	2022-01-21 10:42:29.22242+00	9	\N	\N	f	f
10037	PROJECT	Project	Roule and Mattsey _ Management	262102	2022-01-21 10:42:29.222509+00	2022-01-21 10:42:29.222662+00	9	\N	\N	f	f
10038	PROJECT	Project	Roundtree Attorneys Inc.	262103	2022-01-21 10:42:29.222731+00	2022-01-21 10:42:29.222787+00	9	\N	\N	f	f
10039	PROJECT	Project	Rowie Williams	262104	2022-01-21 10:42:29.222849+00	2022-01-21 10:42:29.222878+00	9	\N	\N	f	f
10040	PROJECT	Project	Roycroft Construction	262105	2022-01-21 10:42:29.222939+00	2022-01-21 10:42:29.223053+00	9	\N	\N	f	f
10041	PROJECT	Project	Ruleman Title Distributors	262106	2022-01-21 10:42:29.223498+00	2022-01-21 10:42:29.223562+00	9	\N	\N	f	f
10042	PROJECT	Project	Russell Telecom	262107	2022-01-21 10:42:29.223778+00	2022-01-21 10:42:29.223816+00	9	\N	\N	f	f
10043	PROJECT	Project	Russ Mygrant	262108	2022-01-21 10:42:29.22388+00	2022-01-21 10:42:29.223911+00	9	\N	\N	f	f
10044	PROJECT	Project	Ruts Construction Holding Corp.	262109	2022-01-21 10:42:29.223983+00	2022-01-21 10:42:29.224016+00	9	\N	\N	f	f
10045	PROJECT	Project	Saenger _ Inc.	262110	2022-01-21 10:42:29.224079+00	2022-01-21 10:42:29.22411+00	9	\N	\N	f	f
10046	PROJECT	Project	Sage Project 1	261120	2022-01-21 10:42:29.224183+00	2022-01-21 10:42:29.224215+00	9	\N	\N	f	f
10047	PROJECT	Project	Sage Project 10	261121	2022-01-21 10:42:29.224277+00	2022-01-21 10:42:29.224306+00	9	\N	\N	f	f
10048	PROJECT	Project	Sage Project 2	261122	2022-01-21 10:42:29.22437+00	2022-01-21 10:42:29.224409+00	9	\N	\N	f	f
10049	PROJECT	Project	Sage Project 3	261123	2022-01-21 10:42:29.224473+00	2022-01-21 10:42:29.224504+00	9	\N	\N	f	f
10050	PROJECT	Project	Sage Project 4	261124	2022-01-21 10:42:29.224566+00	2022-01-21 10:42:29.224711+00	9	\N	\N	f	f
10051	PROJECT	Project	Sage Project 5	261125	2022-01-21 10:42:29.224779+00	2022-01-21 10:42:29.224815+00	9	\N	\N	f	f
10052	PROJECT	Project	Sage Project 6	261126	2022-01-21 10:42:29.238238+00	2022-01-21 10:42:29.238287+00	9	\N	\N	f	f
10053	PROJECT	Project	Sage Project 7	261127	2022-01-21 10:42:29.238355+00	2022-01-21 10:42:29.238386+00	9	\N	\N	f	f
10054	PROJECT	Project	Sage Project 8	261128	2022-01-21 10:42:29.238696+00	2022-01-21 10:42:29.238742+00	9	\N	\N	f	f
10055	PROJECT	Project	Sage Project 9	261129	2022-01-21 10:42:29.238822+00	2022-01-21 10:42:29.238852+00	9	\N	\N	f	f
10056	PROJECT	Project	Sage project fyle	261130	2022-01-21 10:42:29.238913+00	2022-01-21 10:42:29.238942+00	9	\N	\N	f	f
10057	PROJECT	Project	Salisbury Attorneys Group	262111	2022-01-21 10:42:29.239003+00	2022-01-21 10:42:29.239033+00	9	\N	\N	f	f
10058	PROJECT	Project	Sally Ward	262112	2022-01-21 10:42:29.239093+00	2022-01-21 10:42:29.239122+00	9	\N	\N	f	f
10059	PROJECT	Project	Samantha Walker	262113	2022-01-21 10:42:29.239973+00	2022-01-21 10:42:29.240018+00	9	\N	\N	f	f
10060	PROJECT	Project	Sam Brown	262114	2022-01-21 10:42:29.240085+00	2022-01-21 10:42:29.240115+00	9	\N	\N	f	f
10061	PROJECT	Project	Sample Test	281090	2022-01-21 10:42:29.240175+00	2022-01-21 10:42:29.240204+00	9	\N	\N	f	f
10062	PROJECT	Project	San Angelo Automotive Rentals	262115	2022-01-21 10:42:29.240264+00	2022-01-21 10:42:29.240293+00	9	\N	\N	f	f
10063	PROJECT	Project	San Diego Plumbing Distributors	262116	2022-01-21 10:42:29.240353+00	2022-01-21 10:42:29.240382+00	9	\N	\N	f	f
10064	PROJECT	Project	San Diego Windows Agency	262117	2022-01-21 10:42:29.240442+00	2022-01-21 10:42:29.240471+00	9	\N	\N	f	f
10065	PROJECT	Project	Sandoval Products Inc	262118	2022-01-21 10:42:29.240677+00	2022-01-21 10:42:29.240707+00	9	\N	\N	f	f
10066	PROJECT	Project	Sandra Burns	262119	2022-01-21 10:42:29.240767+00	2022-01-21 10:42:29.240796+00	9	\N	\N	f	f
10067	PROJECT	Project	Sandwich Antiques Services	262120	2022-01-21 10:42:29.240857+00	2022-01-21 10:42:29.240886+00	9	\N	\N	f	f
10068	PROJECT	Project	Sandwich Telecom Sales	262121	2022-01-21 10:42:29.240946+00	2022-01-21 10:42:29.240975+00	9	\N	\N	f	f
10069	PROJECT	Project	Sandy King	262122	2022-01-21 10:42:29.241036+00	2022-01-21 10:42:29.241065+00	9	\N	\N	f	f
10071	PROJECT	Project	San Francisco Design Center	262124	2022-01-21 10:42:29.241214+00	2022-01-21 10:42:29.241244+00	9	\N	\N	f	f
10072	PROJECT	Project	San Luis Obispo Construction Inc.	262125	2022-01-21 10:42:29.241304+00	2022-01-21 10:42:29.241333+00	9	\N	\N	f	f
10073	PROJECT	Project	Santa Ana Telecom Management	262126	2022-01-21 10:42:29.241393+00	2022-01-21 10:42:29.241422+00	9	\N	\N	f	f
10074	PROJECT	Project	Santa Fe Springs Construction Corporation	262127	2022-01-21 10:42:29.241481+00	2022-01-21 10:42:29.24151+00	9	\N	\N	f	f
10075	PROJECT	Project	Santa Maria Lumber Inc.	262128	2022-01-21 10:42:29.24172+00	2022-01-21 10:42:29.24175+00	9	\N	\N	f	f
10076	PROJECT	Project	Santa Monica Attorneys Manufacturing	262129	2022-01-21 10:42:29.24181+00	2022-01-21 10:42:29.24184+00	9	\N	\N	f	f
10077	PROJECT	Project	Sarasota Software Rentals	262130	2022-01-21 10:42:29.2419+00	2022-01-21 10:42:29.241929+00	9	\N	\N	f	f
10078	PROJECT	Project	Sarchett Antiques Networking	262131	2022-01-21 10:42:29.24199+00	2022-01-21 10:42:29.24202+00	9	\N	\N	f	f
10079	PROJECT	Project	Sawatzky Catering Rentals	262132	2022-01-21 10:42:29.24208+00	2022-01-21 10:42:29.242109+00	9	\N	\N	f	f
10080	PROJECT	Project	Sax Lumber Co.	262133	2022-01-21 10:42:29.24217+00	2022-01-21 10:42:29.242199+00	9	\N	\N	f	f
10081	PROJECT	Project	Scalley Construction Inc.	262134	2022-01-21 10:42:29.242259+00	2022-01-21 10:42:29.242289+00	9	\N	\N	f	f
10082	PROJECT	Project	Schlicker Metal Fabricators Fabricators	262135	2022-01-21 10:42:29.242349+00	2022-01-21 10:42:29.242378+00	9	\N	\N	f	f
10083	PROJECT	Project	Schmauder Markets Corporation	262136	2022-01-21 10:42:29.242438+00	2022-01-21 10:42:29.242467+00	9	\N	\N	f	f
10084	PROJECT	Project	Schmidt Sporting Goods	262137	2022-01-21 10:42:29.242669+00	2022-01-21 10:42:29.242699+00	9	\N	\N	f	f
10085	PROJECT	Project	Schneck Automotive Group	262138	2022-01-21 10:42:29.242761+00	2022-01-21 10:42:29.24279+00	9	\N	\N	f	f
10086	PROJECT	Project	Scholl Catering -	262139	2022-01-21 10:42:29.242851+00	2022-01-21 10:42:29.24288+00	9	\N	\N	f	f
10087	PROJECT	Project	Schreck Hardware Systems	262140	2022-01-21 10:42:29.242941+00	2022-01-21 10:42:29.24297+00	9	\N	\N	f	f
10088	PROJECT	Project	Schwarzenbach Attorneys Systems	262141	2022-01-21 10:42:29.243031+00	2022-01-21 10:42:29.24306+00	9	\N	\N	f	f
10089	PROJECT	Project	Scottsbluff Lumber -	262142	2022-01-21 10:42:29.243121+00	2022-01-21 10:42:29.24315+00	9	\N	\N	f	f
10090	PROJECT	Project	Scottsbluff Plumbing Rentals	262143	2022-01-21 10:42:29.24321+00	2022-01-21 10:42:29.243239+00	9	\N	\N	f	f
10091	PROJECT	Project	Scullion Telecom Agency	262144	2022-01-21 10:42:29.243299+00	2022-01-21 10:42:29.243329+00	9	\N	\N	f	f
10092	PROJECT	Project	Sebastian Inc.	262145	2022-01-21 10:42:29.243389+00	2022-01-21 10:42:29.243418+00	9	\N	\N	f	f
10093	PROJECT	Project	Sebek Builders Distributors	262146	2022-01-21 10:42:29.243478+00	2022-01-21 10:42:29.243507+00	9	\N	\N	f	f
10094	PROJECT	Project	Sedlak Inc	262147	2022-01-21 10:42:29.243684+00	2022-01-21 10:42:29.243714+00	9	\N	\N	f	f
10095	PROJECT	Project	Seecharan and Horten Hardware Manufacturing	262148	2022-01-21 10:42:29.243774+00	2022-01-21 10:42:29.243803+00	9	\N	\N	f	f
10096	PROJECT	Project	Seena Rose	262149	2022-01-21 10:42:29.244661+00	2022-01-21 10:42:29.244747+00	9	\N	\N	f	f
10097	PROJECT	Project	Seilhymer Antiques Distributors	262150	2022-01-21 10:42:29.244828+00	2022-01-21 10:42:29.244857+00	9	\N	\N	f	f
10098	PROJECT	Project	Selders Distributors	262151	2022-01-21 10:42:29.244918+00	2022-01-21 10:42:29.244949+00	9	\N	\N	f	f
10099	PROJECT	Project	Selia Metal Fabricators Company	262152	2022-01-21 10:42:29.245011+00	2022-01-21 10:42:29.24504+00	9	\N	\N	f	f
10100	PROJECT	Project	Seney Windows Agency	262153	2022-01-21 10:42:29.2451+00	2022-01-21 10:42:29.245129+00	9	\N	\N	f	f
10101	PROJECT	Project	Sequim Automotive Systems	262154	2022-01-21 10:42:29.24519+00	2022-01-21 10:42:29.245219+00	9	\N	\N	f	f
10102	PROJECT	Project	Service Job	262155	2022-01-21 10:42:29.256139+00	2022-01-21 10:42:29.256184+00	9	\N	\N	f	f
10103	PROJECT	Project	Seyler Title Distributors	262156	2022-01-21 10:42:29.256248+00	2022-01-21 10:42:29.256278+00	9	\N	\N	f	f
10104	PROJECT	Project	Shackelton Hospital Sales	262157	2022-01-21 10:42:29.25634+00	2022-01-21 10:42:29.25637+00	9	\N	\N	f	f
10105	PROJECT	Project	Shara Barnett	274687	2022-01-21 10:42:29.256432+00	2022-01-21 10:42:29.256461+00	9	\N	\N	f	f
10106	PROJECT	Project	Shara Barnett:Barnett Design	274688	2022-01-21 10:42:29.256529+00	2022-01-21 10:42:29.256697+00	9	\N	\N	f	f
10107	PROJECT	Project	Sharon Stone	262158	2022-01-21 10:42:29.256761+00	2022-01-21 10:42:29.25679+00	9	\N	\N	f	f
10108	PROJECT	Project	Sheinbein Construction Fabricators	262159	2022-01-21 10:42:29.256851+00	2022-01-21 10:42:29.25688+00	9	\N	\N	f	f
10109	PROJECT	Project	Shininger Lumber Holding Corp.	262160	2022-01-21 10:42:29.25694+00	2022-01-21 10:42:29.25697+00	9	\N	\N	f	f
10110	PROJECT	Project	Shutter Title Services	262161	2022-01-21 10:42:29.25703+00	2022-01-21 10:42:29.257059+00	9	\N	\N	f	f
10111	PROJECT	Project	Siddiq Software -	262162	2022-01-21 10:42:29.257119+00	2022-01-21 10:42:29.257148+00	9	\N	\N	f	f
10112	PROJECT	Project	Simatry	262163	2022-01-21 10:42:29.257225+00	2022-01-21 10:42:29.257266+00	9	\N	\N	f	f
10113	PROJECT	Project	Simi Valley Telecom Dynamics	262164	2022-01-21 10:42:29.257328+00	2022-01-21 10:42:29.257358+00	9	\N	\N	f	f
10114	PROJECT	Project	Sindt Electric	262165	2022-01-21 10:42:29.257418+00	2022-01-21 10:42:29.257447+00	9	\N	\N	f	f
10115	PROJECT	Project	Skibo Construction Dynamics	262166	2022-01-21 10:42:29.257507+00	2022-01-21 10:42:29.25768+00	9	\N	\N	f	f
10116	PROJECT	Project	Slankard Automotive	262167	2022-01-21 10:42:29.257745+00	2022-01-21 10:42:29.257775+00	9	\N	\N	f	f
10117	PROJECT	Project	Slatter Metal Fabricators Inc.	262168	2022-01-21 10:42:29.257836+00	2022-01-21 10:42:29.257865+00	9	\N	\N	f	f
10118	PROJECT	Project	SlingShot Communications	262169	2022-01-21 10:42:29.257925+00	2022-01-21 10:42:29.257954+00	9	\N	\N	f	f
10119	PROJECT	Project	Sloman and Zeccardi Builders Agency	262170	2022-01-21 10:42:29.258015+00	2022-01-21 10:42:29.258044+00	9	\N	\N	f	f
10120	PROJECT	Project	Smelley _ Manufacturing	262171	2022-01-21 10:42:29.258109+00	2022-01-21 10:42:29.258138+00	9	\N	\N	f	f
10121	PROJECT	Project	Smith East	262172	2022-01-21 10:42:29.258199+00	2022-01-21 10:42:29.258229+00	9	\N	\N	f	f
10122	PROJECT	Project	Smith Inc.	262173	2022-01-21 10:42:29.258292+00	2022-01-21 10:42:29.258322+00	9	\N	\N	f	f
10123	PROJECT	Project	Smith Photographic Equipment	262174	2022-01-21 10:42:29.258383+00	2022-01-21 10:42:29.258412+00	9	\N	\N	f	f
10124	PROJECT	Project	Smith West	262175	2022-01-21 10:42:29.258473+00	2022-01-21 10:42:29.258502+00	9	\N	\N	f	f
10125	PROJECT	Project	Snode and Draper Leasing Rentals	262176	2022-01-21 10:42:29.258718+00	2022-01-21 10:42:29.258748+00	9	\N	\N	f	f
10126	PROJECT	Project	Soares Builders Inc.	262177	2022-01-21 10:42:29.258809+00	2022-01-21 10:42:29.258838+00	9	\N	\N	f	f
10127	PROJECT	Project	Solidd Group Ltd	262178	2022-01-21 10:42:29.258899+00	2022-01-21 10:42:29.258928+00	9	\N	\N	f	f
10128	PROJECT	Project	Soltrus	262179	2022-01-21 10:42:29.25899+00	2022-01-21 10:42:29.259047+00	9	\N	\N	f	f
10129	PROJECT	Project	Solymani Electric Leasing	262180	2022-01-21 10:42:29.25911+00	2022-01-21 10:42:29.25914+00	9	\N	\N	f	f
10130	PROJECT	Project	Sonnenschein Family Store	274689	2022-01-21 10:42:29.259201+00	2022-01-21 10:42:29.25923+00	9	\N	\N	f	f
10131	PROJECT	Project	Sossong Plumbing Holding Corp.	262181	2022-01-21 10:42:29.259291+00	2022-01-21 10:42:29.25932+00	9	\N	\N	f	f
10132	PROJECT	Project	South East	262182	2022-01-21 10:42:29.259409+00	2022-01-21 10:42:29.259439+00	9	\N	\N	f	f
10133	PROJECT	Project	Spany ltd	262183	2022-01-21 10:42:29.259499+00	2022-01-21 10:42:29.259693+00	9	\N	\N	f	f
10134	PROJECT	Project	Spectrum Eye	262184	2022-01-21 10:42:29.25976+00	2022-01-21 10:42:29.25979+00	9	\N	\N	f	f
10135	PROJECT	Project	Sports Authority	262185	2022-01-21 10:42:29.259851+00	2022-01-21 10:42:29.25988+00	9	\N	\N	f	f
10136	PROJECT	Project	Sport Station	262186	2022-01-21 10:42:29.259941+00	2022-01-21 10:42:29.25997+00	9	\N	\N	f	f
10137	PROJECT	Project	Spurgin Telecom Agency	262187	2022-01-21 10:42:29.260031+00	2022-01-21 10:42:29.26006+00	9	\N	\N	f	f
10138	PROJECT	Project	Sravan Prod Test Prod	261131	2022-01-21 10:42:29.260121+00	2022-01-21 10:42:29.26015+00	9	\N	\N	f	f
10139	PROJECT	Project	SS&C	262188	2022-01-21 10:42:29.26021+00	2022-01-21 10:42:29.260239+00	9	\N	\N	f	f
10140	PROJECT	Project	Stai Publishing -	262189	2022-01-21 10:42:29.26033+00	2022-01-21 10:42:29.260362+00	9	\N	\N	f	f
10141	PROJECT	Project	Stampe Leasing and Associates	262190	2022-01-21 10:42:29.260424+00	2022-01-21 10:42:29.260453+00	9	\N	\N	f	f
10142	PROJECT	Project	Stantec Inc	262191	2022-01-21 10:42:29.260514+00	2022-01-21 10:42:29.260762+00	9	\N	\N	f	f
10143	PROJECT	Project	Star Structural	262192	2022-01-21 10:42:29.261646+00	2022-01-21 10:42:29.261697+00	9	\N	\N	f	f
10144	PROJECT	Project	Steacy Tech Inc	262193	2022-01-21 10:42:29.261785+00	2022-01-21 10:42:29.261817+00	9	\N	\N	f	f
10145	PROJECT	Project	Steep and Cloud Liquors Co.	262194	2022-01-21 10:42:29.261882+00	2022-01-21 10:42:29.261913+00	9	\N	\N	f	f
10146	PROJECT	Project	Steffensmeier Markets Co.	262195	2022-01-21 10:42:29.261976+00	2022-01-21 10:42:29.262006+00	9	\N	\N	f	f
10147	PROJECT	Project	Steinberg Electric Networking	262196	2022-01-21 10:42:29.2621+00	2022-01-21 10:42:29.262132+00	9	\N	\N	f	f
10148	PROJECT	Project	Stella Sebastian Inc	262197	2022-01-21 10:42:29.262195+00	2022-01-21 10:42:29.262225+00	9	\N	\N	f	f
10149	PROJECT	Project	Stephan Simms	262198	2022-01-21 10:42:29.262288+00	2022-01-21 10:42:29.262317+00	9	\N	\N	f	f
10150	PROJECT	Project	Sternberger Telecom Incorporated	262199	2022-01-21 10:42:29.262378+00	2022-01-21 10:42:29.262408+00	9	\N	\N	f	f
10151	PROJECT	Project	Sterr Lumber Systems	262200	2022-01-21 10:42:29.262469+00	2022-01-21 10:42:29.262498+00	9	\N	\N	f	f
10152	PROJECT	Project	Steve Davis	262201	2022-01-21 10:42:29.276803+00	2022-01-21 10:42:29.276855+00	9	\N	\N	f	f
10153	PROJECT	Project	Steve Smith	262202	2022-01-21 10:42:29.276935+00	2022-01-21 10:42:29.276969+00	9	\N	\N	f	f
10154	PROJECT	Project	Stewart's Valet Parking	262203	2022-01-21 10:42:29.277037+00	2022-01-21 10:42:29.277068+00	9	\N	\N	f	f
10155	PROJECT	Project	St. Francis Yacht Club	262204	2022-01-21 10:42:29.277135+00	2022-01-21 10:42:29.277166+00	9	\N	\N	f	f
10156	PROJECT	Project	Stirling Truck Services	262205	2022-01-21 10:42:29.27723+00	2022-01-21 10:42:29.27726+00	9	\N	\N	f	f
10157	PROJECT	Project	Stitch Software Distributors	262206	2022-01-21 10:42:29.277326+00	2022-01-21 10:42:29.277358+00	9	\N	\N	f	f
10158	PROJECT	Project	St Lawrence Starch	262207	2022-01-21 10:42:29.277554+00	2022-01-21 10:42:29.277589+00	9	\N	\N	f	f
10159	PROJECT	Project	St. Mark's Church	262208	2022-01-21 10:42:29.277657+00	2022-01-21 10:42:29.277688+00	9	\N	\N	f	f
10160	PROJECT	Project	Stoett Telecom Rentals	262209	2022-01-21 10:42:29.277752+00	2022-01-21 10:42:29.277781+00	9	\N	\N	f	f
10161	PROJECT	Project	Stofflet Hardware Incorporated	262210	2022-01-21 10:42:29.277842+00	2022-01-21 10:42:29.277872+00	9	\N	\N	f	f
10162	PROJECT	Project	Stone & Cox	262211	2022-01-21 10:42:29.277934+00	2022-01-21 10:42:29.277963+00	9	\N	\N	f	f
10163	PROJECT	Project	Stonum Catering Group	262212	2022-01-21 10:42:29.278024+00	2022-01-21 10:42:29.278053+00	9	\N	\N	f	f
10164	PROJECT	Project	Storch Title Manufacturing	262213	2022-01-21 10:42:29.278114+00	2022-01-21 10:42:29.278143+00	9	\N	\N	f	f
10165	PROJECT	Project	Stotelmyer and Conelly Metal Fabricators Group	262214	2022-01-21 10:42:29.278204+00	2022-01-21 10:42:29.278233+00	9	\N	\N	f	f
10166	PROJECT	Project	Stower Electric Company	262215	2022-01-21 10:42:29.278293+00	2022-01-21 10:42:29.278323+00	9	\N	\N	f	f
10167	PROJECT	Project	Streib and Cravy Hardware Rentals	262216	2022-01-21 10:42:29.278383+00	2022-01-21 10:42:29.278412+00	9	\N	\N	f	f
10168	PROJECT	Project	Sturrup Antiques Management	262217	2022-01-21 10:42:29.278473+00	2022-01-21 10:42:29.278502+00	9	\N	\N	f	f
10169	PROJECT	Project	Summerton Hospital Services	262218	2022-01-21 10:42:29.278778+00	2022-01-21 10:42:29.27886+00	9	\N	\N	f	f
10170	PROJECT	Project	Summons Apartments Company	262219	2022-01-21 10:42:29.278966+00	2022-01-21 10:42:29.279008+00	9	\N	\N	f	f
10171	PROJECT	Project	Sumter Apartments Systems	262220	2022-01-21 10:42:29.279106+00	2022-01-21 10:42:29.279145+00	9	\N	\N	f	f
10172	PROJECT	Project	Sunnybrook Hospital	262221	2022-01-21 10:42:29.279236+00	2022-01-21 10:42:29.279276+00	9	\N	\N	f	f
10173	PROJECT	Project	Superior Car care Inc.	262222	2022-01-21 10:42:29.279366+00	2022-01-21 10:42:29.279407+00	9	\N	\N	f	f
10174	PROJECT	Project	Support Taxes	284470	2022-01-21 10:42:29.279659+00	2022-01-21 10:42:29.279717+00	9	\N	\N	f	f
10175	PROJECT	Project	Support T&M	262223	2022-01-21 10:42:29.27981+00	2022-01-21 10:42:29.27985+00	9	\N	\N	f	f
10176	PROJECT	Project	Sur Windows Services	262224	2022-01-21 10:42:29.280033+00	2022-01-21 10:42:29.280079+00	9	\N	\N	f	f
10177	PROJECT	Project	Sushi by Katsuyuki	274690	2022-01-21 10:42:29.280727+00	2022-01-21 10:42:29.28083+00	9	\N	\N	f	f
10178	PROJECT	Project	Svancara Antiques Holding Corp.	262225	2022-01-21 10:42:29.28098+00	2022-01-21 10:42:29.281035+00	9	\N	\N	f	f
10179	PROJECT	Project	Swanger Spirits	262226	2022-01-21 10:42:29.283294+00	2022-01-21 10:42:29.283601+00	9	\N	\N	f	f
10180	PROJECT	Project	Sweeton and Ketron Liquors Group	262227	2022-01-21 10:42:29.283833+00	2022-01-21 10:42:29.284078+00	9	\N	\N	f	f
10181	PROJECT	Project	Swiech Telecom Networking	262228	2022-01-21 10:42:29.284387+00	2022-01-21 10:42:29.28447+00	9	\N	\N	f	f
10182	PROJECT	Project	Swinea Antiques Holding Corp.	262229	2022-01-21 10:42:29.284786+00	2022-01-21 10:42:29.284856+00	9	\N	\N	f	f
10183	PROJECT	Project	Symore Construction Dynamics	262230	2022-01-21 10:42:29.28502+00	2022-01-21 10:42:29.285194+00	9	\N	\N	f	f
10184	PROJECT	Project	Szewczyk Apartments Holding Corp.	262231	2022-01-21 10:42:29.285853+00	2022-01-21 10:42:29.286075+00	9	\N	\N	f	f
10185	PROJECT	Project	Taback Construction Leasing	262232	2022-01-21 10:42:29.291143+00	2022-01-21 10:42:29.291615+00	9	\N	\N	f	f
10186	PROJECT	Project	TAB Ltd	262233	2022-01-21 10:42:29.293693+00	2022-01-21 10:42:29.29398+00	9	\N	\N	f	f
10187	PROJECT	Project	Talboti and Pauli Title Agency	262234	2022-01-21 10:42:29.296149+00	2022-01-21 10:42:29.296511+00	9	\N	\N	f	f
10188	PROJECT	Project	Tamara Gibson	262235	2022-01-21 10:42:29.31795+00	2022-01-21 10:42:29.31801+00	9	\N	\N	f	f
10189	PROJECT	Project	Tam Liquors	262236	2022-01-21 10:42:29.318103+00	2022-01-21 10:42:29.318142+00	9	\N	\N	f	f
10190	PROJECT	Project	Tanya Guerrero	262237	2022-01-21 10:42:29.318249+00	2022-01-21 10:42:29.318288+00	9	\N	\N	f	f
10191	PROJECT	Project	Tarangelo and Mccrea Apartments Holding Corp.	262238	2022-01-21 10:42:29.318375+00	2022-01-21 10:42:29.318413+00	9	\N	\N	f	f
10192	PROJECT	Project	Tarbutton Software Management	262239	2022-01-21 10:42:29.318501+00	2022-01-21 10:42:29.318539+00	9	\N	\N	f	f
10193	PROJECT	Project	TargetVision	262240	2022-01-21 10:42:29.318627+00	2022-01-21 10:42:29.318665+00	9	\N	\N	f	f
10194	PROJECT	Project	Taverna Liquors Networking	262241	2022-01-21 10:42:29.318752+00	2022-01-21 10:42:29.318791+00	9	\N	\N	f	f
10195	PROJECT	Project	Team Industrial	262242	2022-01-21 10:42:29.319194+00	2022-01-21 10:42:29.319247+00	9	\N	\N	f	f
10196	PROJECT	Project	Tebo Builders Management	262243	2022-01-21 10:42:29.319374+00	2022-01-21 10:42:29.321001+00	9	\N	\N	f	f
10197	PROJECT	Project	Technology Consultants	262244	2022-01-21 10:42:29.321367+00	2022-01-21 10:42:29.321425+00	9	\N	\N	f	f
10198	PROJECT	Project	Teddy Leasing Manufacturing	262245	2022-01-21 10:42:29.321531+00	2022-01-21 10:42:29.321571+00	9	\N	\N	f	f
10199	PROJECT	Project	Tenen Markets Dynamics	262246	2022-01-21 10:42:29.321665+00	2022-01-21 10:42:29.321704+00	9	\N	\N	f	f
10200	PROJECT	Project	Territory JMP 2	262247	2022-01-21 10:42:29.321795+00	2022-01-21 10:42:29.321833+00	9	\N	\N	f	f
10201	PROJECT	Project	Territory JMP 3	262248	2022-01-21 10:42:29.32192+00	2022-01-21 10:42:29.321965+00	9	\N	\N	f	f
10202	PROJECT	Project	Territory JMP 4	262249	2022-01-21 10:42:29.406951+00	2022-01-21 10:42:29.407035+00	9	\N	\N	f	f
10203	PROJECT	Project	TES Inc	262250	2022-01-21 10:42:29.411574+00	2022-01-21 10:42:29.411642+00	9	\N	\N	f	f
10204	PROJECT	Project	Tessa Darby	262251	2022-01-21 10:42:29.413114+00	2022-01-21 10:42:29.413374+00	9	\N	\N	f	f
10205	PROJECT	Project	test	262252	2022-01-21 10:42:29.418911+00	2022-01-21 10:42:29.418993+00	9	\N	\N	f	f
10206	PROJECT	Project	Test 2	262253	2022-01-21 10:42:29.419139+00	2022-01-21 10:42:29.419187+00	9	\N	\N	f	f
10207	PROJECT	Project	Test 3	262254	2022-01-21 10:42:29.4193+00	2022-01-21 10:42:29.419345+00	9	\N	\N	f	f
10208	PROJECT	Project	Test a	262255	2022-01-21 10:42:29.419448+00	2022-01-21 10:42:29.419489+00	9	\N	\N	f	f
10209	PROJECT	Project	tester1	262256	2022-01-21 10:42:29.419589+00	2022-01-21 10:42:29.419631+00	9	\N	\N	f	f
10210	PROJECT	Project	Test Test	262257	2022-01-21 10:42:29.419729+00	2022-01-21 10:42:29.41977+00	9	\N	\N	f	f
10211	PROJECT	Project	Teton Winter Sports	262258	2022-01-21 10:42:29.419867+00	2022-01-21 10:42:29.419909+00	9	\N	\N	f	f
10212	PROJECT	Project	The Coffee Corner	262259	2022-01-21 10:42:29.420004+00	2022-01-21 10:42:29.420046+00	9	\N	\N	f	f
10213	PROJECT	Project	The Liquor Barn	262260	2022-01-21 10:42:29.420142+00	2022-01-21 10:42:29.420701+00	9	\N	\N	f	f
10214	PROJECT	Project	Thermo Electron Corporation	262261	2022-01-21 10:42:29.420895+00	2022-01-21 10:42:29.420947+00	9	\N	\N	f	f
10215	PROJECT	Project	Therrell Publishing Networking	262262	2022-01-21 10:42:29.436715+00	2022-01-21 10:42:29.437159+00	9	\N	\N	f	f
10216	PROJECT	Project	The Validation Group	262263	2022-01-21 10:42:29.43821+00	2022-01-21 10:42:29.442973+00	9	\N	\N	f	f
10217	PROJECT	Project	Thomison Windows Networking	262264	2022-01-21 10:42:29.45886+00	2022-01-21 10:42:29.458956+00	9	\N	\N	f	f
10218	PROJECT	Project	Thongchanh Telecom Rentals	262265	2022-01-21 10:42:29.459159+00	2022-01-21 10:42:29.459202+00	9	\N	\N	f	f
10219	PROJECT	Project	Thorne & Assoc	262266	2022-01-21 10:42:29.459349+00	2022-01-21 10:42:29.459389+00	9	\N	\N	f	f
10220	PROJECT	Project	Tim Griffin	262267	2022-01-21 10:42:29.459453+00	2022-01-21 10:42:29.459482+00	9	\N	\N	f	f
10221	PROJECT	Project	Timinsky Lumber Dynamics	262268	2022-01-21 10:42:29.459543+00	2022-01-21 10:42:29.459572+00	9	\N	\N	f	f
10222	PROJECT	Project	Timmy Brown	262269	2022-01-21 10:42:29.459632+00	2022-01-21 10:42:29.459661+00	9	\N	\N	f	f
10223	PROJECT	Project	Titam Business Services	262270	2022-01-21 10:42:29.459721+00	2022-01-21 10:42:29.45975+00	9	\N	\N	f	f
10224	PROJECT	Project	T-M Manufacturing Corp.	262271	2022-01-21 10:42:29.459811+00	2022-01-21 10:42:29.45984+00	9	\N	\N	f	f
10225	PROJECT	Project	T&M Project with Five Tasks	284471	2022-01-21 10:42:29.4599+00	2022-01-21 10:42:29.459929+00	9	\N	\N	f	f
10226	PROJECT	Project	Tom Calhoun	262272	2022-01-21 10:42:29.45999+00	2022-01-21 10:42:29.460019+00	9	\N	\N	f	f
10227	PROJECT	Project	Tom Kratz	262273	2022-01-21 10:42:29.460079+00	2022-01-21 10:42:29.460108+00	9	\N	\N	f	f
10228	PROJECT	Project	Tomlinson	262274	2022-01-21 10:42:29.460169+00	2022-01-21 10:42:29.460198+00	9	\N	\N	f	f
10229	PROJECT	Project	Tom MacGillivray	262275	2022-01-21 10:42:29.46073+00	2022-01-21 10:42:29.460794+00	9	\N	\N	f	f
10230	PROJECT	Project	Tony Matsuda	262276	2022-01-21 10:42:29.46116+00	2022-01-21 10:42:29.46122+00	9	\N	\N	f	f
10231	PROJECT	Project	Top Drawer Creative	262277	2022-01-21 10:42:29.461371+00	2022-01-21 10:42:29.461544+00	9	\N	\N	f	f
10232	PROJECT	Project	Touchard Liquors Holding Corp.	262278	2022-01-21 10:42:29.461745+00	2022-01-21 10:42:29.461776+00	9	\N	\N	f	f
10233	PROJECT	Project	Tower AV and Telephone Install	262279	2022-01-21 10:42:29.461837+00	2022-01-21 10:42:29.461865+00	9	\N	\N	f	f
10234	PROJECT	Project	Tower PL-01	262280	2022-01-21 10:42:29.461925+00	2022-01-21 10:42:29.461954+00	9	\N	\N	f	f
10235	PROJECT	Project	Towsend Software Co.	262281	2022-01-21 10:42:29.462015+00	2022-01-21 10:42:29.462044+00	9	\N	\N	f	f
10236	PROJECT	Project	Tracy Attorneys Management	262282	2022-01-21 10:42:29.462104+00	2022-01-21 10:42:29.462132+00	9	\N	\N	f	f
10237	PROJECT	Project	Travis Gilbert	262283	2022-01-21 10:42:29.462192+00	2022-01-21 10:42:29.462221+00	9	\N	\N	f	f
10238	PROJECT	Project	Travis Waldron	274691	2022-01-21 10:42:29.462282+00	2022-01-21 10:42:29.462311+00	9	\N	\N	f	f
10239	PROJECT	Project	Trebor Allen Candy	262284	2022-01-21 10:42:29.462371+00	2022-01-21 10:42:29.4624+00	9	\N	\N	f	f
10240	PROJECT	Project	Tredwell Lumber Holding Corp.	262285	2022-01-21 10:42:29.46246+00	2022-01-21 10:42:29.462489+00	9	\N	\N	f	f
10241	PROJECT	Project	Trent Barry	262286	2022-01-21 10:42:29.462549+00	2022-01-21 10:42:29.462578+00	9	\N	\N	f	f
10242	PROJECT	Project	Trenton Upwood Ltd	262287	2022-01-21 10:42:29.462638+00	2022-01-21 10:42:29.462667+00	9	\N	\N	f	f
10243	PROJECT	Project	TSM	262288	2022-01-21 10:42:29.462727+00	2022-01-21 10:42:29.462756+00	9	\N	\N	f	f
10244	PROJECT	Project	TST Solutions Inc	262289	2022-01-21 10:42:29.462816+00	2022-01-21 10:42:29.462845+00	9	\N	\N	f	f
10245	PROJECT	Project	TTS inc	262290	2022-01-21 10:42:29.462905+00	2022-01-21 10:42:29.462934+00	9	\N	\N	f	f
10246	PROJECT	Project	Tucson Apartments and Associates	262291	2022-01-21 10:42:29.462994+00	2022-01-21 10:42:29.463022+00	9	\N	\N	f	f
10247	PROJECT	Project	Turso Catering Agency	262292	2022-01-21 10:42:29.463083+00	2022-01-21 10:42:29.463112+00	9	\N	\N	f	f
10248	PROJECT	Project	Tuy and Sinha Construction Manufacturing	262293	2022-01-21 10:42:29.463172+00	2022-01-21 10:42:29.463201+00	9	\N	\N	f	f
10249	PROJECT	Project	TWC Financial	262294	2022-01-21 10:42:29.463261+00	2022-01-21 10:42:29.463291+00	9	\N	\N	f	f
10250	PROJECT	Project	Twigg Attorneys Company	262295	2022-01-21 10:42:29.463351+00	2022-01-21 10:42:29.463381+00	9	\N	\N	f	f
10251	PROJECT	Project	Twine Title Group	262296	2022-01-21 10:42:29.463441+00	2022-01-21 10:42:29.46347+00	9	\N	\N	f	f
10252	PROJECT	Project	Udoh Publishing Manufacturing	262297	2022-01-21 10:42:29.509508+00	2022-01-21 10:42:29.509556+00	9	\N	\N	f	f
10253	PROJECT	Project	ugkas	262298	2022-01-21 10:42:29.509636+00	2022-01-21 10:42:29.509667+00	9	\N	\N	f	f
10254	PROJECT	Project	Uimari Antiques Agency	262299	2022-01-21 10:42:29.509731+00	2022-01-21 10:42:29.509761+00	9	\N	\N	f	f
10255	PROJECT	Project	UK Customer	262300	2022-01-21 10:42:29.509823+00	2022-01-21 10:42:29.509853+00	9	\N	\N	f	f
10256	PROJECT	Project	Umali Publishing Distributors	262301	2022-01-21 10:42:29.509914+00	2022-01-21 10:42:29.509944+00	9	\N	\N	f	f
10257	PROJECT	Project	Umbrell Liquors Rentals	262302	2022-01-21 10:42:29.510005+00	2022-01-21 10:42:29.510035+00	9	\N	\N	f	f
10258	PROJECT	Project	Umeh Telecom Management	262303	2022-01-21 10:42:29.510095+00	2022-01-21 10:42:29.510125+00	9	\N	\N	f	f
10259	PROJECT	Project	Underdown Metal Fabricators and Associates	262304	2022-01-21 10:42:29.510185+00	2022-01-21 10:42:29.510215+00	9	\N	\N	f	f
10260	PROJECT	Project	Underwood New York	262305	2022-01-21 10:42:29.510275+00	2022-01-21 10:42:29.510305+00	9	\N	\N	f	f
10261	PROJECT	Project	Underwood Systems	262306	2022-01-21 10:42:29.510365+00	2022-01-21 10:42:29.510395+00	9	\N	\N	f	f
10262	PROJECT	Project	UniExchange	262307	2022-01-21 10:42:29.510455+00	2022-01-21 10:42:29.510485+00	9	\N	\N	f	f
10263	PROJECT	Project	Unnold Hospital Co.	262308	2022-01-21 10:42:29.510546+00	2022-01-21 10:42:29.510575+00	9	\N	\N	f	f
10264	PROJECT	Project	Upper 49th	262309	2022-01-21 10:42:29.510909+00	2022-01-21 10:42:29.510969+00	9	\N	\N	f	f
10265	PROJECT	Project	Ursery Publishing Group	262310	2022-01-21 10:42:29.511106+00	2022-01-21 10:42:29.511159+00	9	\N	\N	f	f
10266	PROJECT	Project	Urwin Leasing Group	262311	2022-01-21 10:42:29.511285+00	2022-01-21 10:42:29.51134+00	9	\N	\N	f	f
10267	PROJECT	Project	Valley Center Catering Leasing	262312	2022-01-21 10:42:29.512007+00	2022-01-21 10:42:29.512093+00	9	\N	\N	f	f
10268	PROJECT	Project	Vanaken Apartments Holding Corp.	262313	2022-01-21 10:42:29.513084+00	2022-01-21 10:42:29.51324+00	9	\N	\N	f	f
10269	PROJECT	Project	Vanasse Antiques Networking	262314	2022-01-21 10:42:29.51363+00	2022-01-21 10:42:29.51371+00	9	\N	\N	f	f
10270	PROJECT	Project	Vance Construction and Associates	262315	2022-01-21 10:42:29.514081+00	2022-01-21 10:42:29.514157+00	9	\N	\N	f	f
10271	PROJECT	Project	Vanwyngaarden Title Systems	262316	2022-01-21 10:42:29.514333+00	2022-01-21 10:42:29.514398+00	9	\N	\N	f	f
10272	PROJECT	Project	Vegas Tours	262317	2022-01-21 10:42:29.520761+00	2022-01-21 10:42:29.520974+00	9	\N	\N	f	f
10273	PROJECT	Project	Vellekamp Title Distributors	262318	2022-01-21 10:42:29.521756+00	2022-01-21 10:42:29.521871+00	9	\N	\N	f	f
10274	PROJECT	Project	Veradale Telecom Manufacturing	262319	2022-01-21 10:42:29.523782+00	2022-01-21 10:42:29.52386+00	9	\N	\N	f	f
10275	PROJECT	Project	Vermont Attorneys Company	262320	2022-01-21 10:42:29.525305+00	2022-01-21 10:42:29.525391+00	9	\N	\N	f	f
10276	PROJECT	Project	Verrelli Construction -	262321	2022-01-21 10:42:29.526578+00	2022-01-21 10:42:29.526654+00	9	\N	\N	f	f
10277	PROJECT	Project	Vertex	262322	2022-01-21 10:42:29.527162+00	2022-01-21 10:42:29.527233+00	9	\N	\N	f	f
10278	PROJECT	Project	Vessel Painting Holding Corp.	262323	2022-01-21 10:42:29.527409+00	2022-01-21 10:42:29.527445+00	9	\N	\N	f	f
10279	PROJECT	Project	Video Games by Dan	274692	2022-01-21 10:42:29.527511+00	2022-01-21 10:42:29.527541+00	9	\N	\N	f	f
10280	PROJECT	Project	Villanova Lumber Systems	262324	2022-01-21 10:42:29.527603+00	2022-01-21 10:42:29.527633+00	9	\N	\N	f	f
10281	PROJECT	Project	Virginia Beach Hospital Manufacturing	262325	2022-01-21 10:42:29.527694+00	2022-01-21 10:42:29.527723+00	9	\N	\N	f	f
10282	PROJECT	Project	Vista Lumber Agency	262326	2022-01-21 10:42:29.527784+00	2022-01-21 10:42:29.527813+00	9	\N	\N	f	f
10283	PROJECT	Project	Vivas Electric Sales	262327	2022-01-21 10:42:29.531503+00	2022-01-21 10:42:29.53192+00	9	\N	\N	f	f
10284	PROJECT	Project	Vodaphone	262328	2022-01-21 10:42:29.535952+00	2022-01-21 10:42:29.536043+00	9	\N	\N	f	f
10285	PROJECT	Project	Volden Publishing Systems	262329	2022-01-21 10:42:29.538848+00	2022-01-21 10:42:29.538906+00	9	\N	\N	f	f
10286	PROJECT	Project	Volmar Liquors and Associates	262330	2022-01-21 10:42:29.538997+00	2022-01-21 10:42:29.539027+00	9	\N	\N	f	f
10287	PROJECT	Project	Volmink Builders Inc.	262331	2022-01-21 10:42:29.53909+00	2022-01-21 10:42:29.53912+00	9	\N	\N	f	f
10288	PROJECT	Project	Wagenheim Painting and Associates	262332	2022-01-21 10:42:29.539182+00	2022-01-21 10:42:29.539211+00	9	\N	\N	f	f
10289	PROJECT	Project	Wahlers Lumber Management	262333	2022-01-21 10:42:29.539272+00	2022-01-21 10:42:29.539301+00	9	\N	\N	f	f
10290	PROJECT	Project	Wallace Printers	262334	2022-01-21 10:42:29.539362+00	2022-01-21 10:42:29.539391+00	9	\N	\N	f	f
10291	PROJECT	Project	Walter Martin	262335	2022-01-21 10:42:29.539452+00	2022-01-21 10:42:29.539481+00	9	\N	\N	f	f
10292	PROJECT	Project	Walters Production Company	262336	2022-01-21 10:42:29.539541+00	2022-01-21 10:42:29.539571+00	9	\N	\N	f	f
10293	PROJECT	Project	Wapp Hardware Sales	262337	2022-01-21 10:42:29.539631+00	2022-01-21 10:42:29.53966+00	9	\N	\N	f	f
10294	PROJECT	Project	Warnberg Automotive and Associates	262338	2022-01-21 10:42:29.539721+00	2022-01-21 10:42:29.53975+00	9	\N	\N	f	f
10295	PROJECT	Project	Warwick Lumber	262339	2022-01-21 10:42:29.53981+00	2022-01-21 10:42:29.539839+00	9	\N	\N	f	f
10296	PROJECT	Project	Wasager Wine Sales	262340	2022-01-21 10:42:29.5399+00	2022-01-21 10:42:29.539929+00	9	\N	\N	f	f
10297	PROJECT	Project	Wassenaar Construction Services	262341	2022-01-21 10:42:29.539989+00	2022-01-21 10:42:29.540019+00	9	\N	\N	f	f
10298	PROJECT	Project	Watertown Hicks	262342	2022-01-21 10:42:29.540079+00	2022-01-21 10:42:29.540109+00	9	\N	\N	f	f
10299	PROJECT	Project	Weare and Norvell Painting Co.	262343	2022-01-21 10:42:29.54017+00	2022-01-21 10:42:29.540199+00	9	\N	\N	f	f
10300	PROJECT	Project	Webmaster Gproxy	262344	2022-01-21 10:42:29.540259+00	2022-01-21 10:42:29.540289+00	9	\N	\N	f	f
10301	PROJECT	Project	Webster Electric	262345	2022-01-21 10:42:29.540349+00	2022-01-21 10:42:29.540378+00	9	\N	\N	f	f
10302	PROJECT	Project	Wedding Planning by Whitney	274693	2022-01-21 10:42:29.559277+00	2022-01-21 10:42:29.559321+00	9	\N	\N	f	f
10303	PROJECT	Project	Wedge Automotive Fabricators	262346	2022-01-21 10:42:29.559385+00	2022-01-21 10:42:29.559416+00	9	\N	\N	f	f
10304	PROJECT	Project	Weiskopf Consulting	274694	2022-01-21 10:42:29.559478+00	2022-01-21 10:42:29.559507+00	9	\N	\N	f	f
10305	PROJECT	Project	Wenatchee Builders Fabricators	262347	2022-01-21 10:42:29.559568+00	2022-01-21 10:42:29.559598+00	9	\N	\N	f	f
10306	PROJECT	Project	Wence Antiques Rentals	262348	2022-01-21 10:42:29.55966+00	2022-01-21 10:42:29.559689+00	9	\N	\N	f	f
10307	PROJECT	Project	Wendler Markets Leasing	262349	2022-01-21 10:42:29.55975+00	2022-01-21 10:42:29.55978+00	9	\N	\N	f	f
10308	PROJECT	Project	West Covina Builders Distributors	262350	2022-01-21 10:42:29.55984+00	2022-01-21 10:42:29.55987+00	9	\N	\N	f	f
10309	PROJECT	Project	Westminster Lumber Sales	262351	2022-01-21 10:42:29.55993+00	2022-01-21 10:42:29.55996+00	9	\N	\N	f	f
10310	PROJECT	Project	Westminster Lumber Sales 1	262352	2022-01-21 10:42:29.56002+00	2022-01-21 10:42:29.56005+00	9	\N	\N	f	f
10311	PROJECT	Project	West Palm Beach Painting Manufacturing	262353	2022-01-21 10:42:29.56011+00	2022-01-21 10:42:29.560139+00	9	\N	\N	f	f
10312	PROJECT	Project	Wethersfield Hardware Dynamics	262354	2022-01-21 10:42:29.5602+00	2022-01-21 10:42:29.560229+00	9	\N	\N	f	f
10313	PROJECT	Project	Wettlaufer Construction Systems	262355	2022-01-21 10:42:29.560354+00	2022-01-21 10:42:29.564746+00	9	\N	\N	f	f
10314	PROJECT	Project	Wever Apartments -	262356	2022-01-21 10:42:29.572802+00	2022-01-21 10:42:29.575687+00	9	\N	\N	f	f
10315	PROJECT	Project	Whetzell and Maymon Antiques Sales	262357	2022-01-21 10:42:29.575842+00	2022-01-21 10:42:29.575867+00	9	\N	\N	f	f
10316	PROJECT	Project	Whitehead and Sons	285883	2022-01-21 10:42:29.575943+00	2022-01-21 10:42:29.58134+00	9	\N	\N	f	f
10317	PROJECT	Project	Whitehead and Sons:Whitehead - Employee celebration	285884	2022-01-21 10:42:29.58907+00	2022-01-21 10:42:29.589308+00	9	\N	\N	f	f
10318	PROJECT	Project	Whittier Hardware -	262358	2022-01-21 10:42:29.589445+00	2022-01-21 10:42:29.589493+00	9	\N	\N	f	f
10319	PROJECT	Project	Whole Oats Markets	262359	2022-01-21 10:42:29.589602+00	2022-01-21 10:42:29.589646+00	9	\N	\N	f	f
10320	PROJECT	Project	Wickenhauser Hardware Management	262360	2022-01-21 10:42:29.58975+00	2022-01-21 10:42:29.589783+00	9	\N	\N	f	f
10321	PROJECT	Project	Wicklund Leasing Corporation	262361	2022-01-21 10:42:29.589873+00	2022-01-21 10:42:29.589913+00	9	\N	\N	f	f
10322	PROJECT	Project	Wiesel Construction Dynamics	262362	2022-01-21 10:42:29.590011+00	2022-01-21 10:42:29.590051+00	9	\N	\N	f	f
10323	PROJECT	Project	Wiggles Inc.	262363	2022-01-21 10:42:29.590147+00	2022-01-21 10:42:29.590189+00	9	\N	\N	f	f
10324	PROJECT	Project	Wilkey Markets Group	262364	2022-01-21 10:42:29.590285+00	2022-01-21 10:42:29.590324+00	9	\N	\N	f	f
10325	PROJECT	Project	Williams Electronics and Communications	262365	2022-01-21 10:42:29.595184+00	2022-01-21 10:42:29.596586+00	9	\N	\N	f	f
10326	PROJECT	Project	Williams Wireless World	262366	2022-01-21 10:42:29.604237+00	2022-01-21 10:42:29.604295+00	9	\N	\N	f	f
10327	PROJECT	Project	Will's Leather Co.	262367	2022-01-21 10:42:29.604378+00	2022-01-21 10:42:29.604418+00	9	\N	\N	f	f
10328	PROJECT	Project	Wilner Liquors	262368	2022-01-21 10:42:29.604502+00	2022-01-21 10:42:29.604721+00	9	\N	\N	f	f
10329	PROJECT	Project	Wilson Kaplan	262369	2022-01-21 10:42:29.605115+00	2022-01-21 10:42:29.60515+00	9	\N	\N	f	f
10330	PROJECT	Project	Windisch Title Corporation	262370	2022-01-21 10:42:29.605241+00	2022-01-21 10:42:29.605281+00	9	\N	\N	f	f
10331	PROJECT	Project	Witten Antiques Services	262371	2022-01-21 10:42:29.605368+00	2022-01-21 10:42:29.60555+00	9	\N	\N	f	f
10332	PROJECT	Project	Wolfenden Markets Holding Corp.	262372	2022-01-21 10:42:29.60564+00	2022-01-21 10:42:29.605679+00	9	\N	\N	f	f
10333	PROJECT	Project	Wollan Software Rentals	262373	2022-01-21 10:42:29.605768+00	2022-01-21 10:42:29.605807+00	9	\N	\N	f	f
10334	PROJECT	Project	Wood-Mizer	262374	2022-01-21 10:42:29.605896+00	2022-01-21 10:42:29.605934+00	9	\N	\N	f	f
10335	PROJECT	Project	Woods Publishing Co.	262375	2022-01-21 10:42:29.606024+00	2022-01-21 10:42:29.606062+00	9	\N	\N	f	f
10336	PROJECT	Project	Wood Wonders Funiture	262376	2022-01-21 10:42:29.60615+00	2022-01-21 10:42:29.606189+00	9	\N	\N	f	f
10337	PROJECT	Project	Woon Hardware Networking	262377	2022-01-21 10:42:29.606276+00	2022-01-21 10:42:29.606314+00	9	\N	\N	f	f
10338	PROJECT	Project	Wraight Software and Associates	262378	2022-01-21 10:42:29.606401+00	2022-01-21 10:42:29.606438+00	9	\N	\N	f	f
10339	PROJECT	Project	X Eye Corp	262379	2022-01-21 10:42:29.606524+00	2022-01-21 10:42:29.606562+00	9	\N	\N	f	f
10340	PROJECT	Project	Yahl Markets Incorporated	262380	2022-01-21 10:42:29.60665+00	2022-01-21 10:42:29.60669+00	9	\N	\N	f	f
10341	PROJECT	Project	Yanity Apartments and Associates	262381	2022-01-21 10:42:29.606776+00	2022-01-21 10:42:29.606815+00	9	\N	\N	f	f
10342	PROJECT	Project	Yarnell Catering Holding Corp.	262382	2022-01-21 10:42:29.606901+00	2022-01-21 10:42:29.606939+00	9	\N	\N	f	f
10343	PROJECT	Project	Yockey Markets Inc.	262383	2022-01-21 10:42:29.607027+00	2022-01-21 10:42:29.607066+00	9	\N	\N	f	f
10344	PROJECT	Project	Yong Yi	262384	2022-01-21 10:42:29.607545+00	2022-01-21 10:42:29.607674+00	9	\N	\N	f	f
10345	PROJECT	Project	Y-Tec Manufacturing	262385	2022-01-21 10:42:29.607818+00	2022-01-21 10:42:29.60786+00	9	\N	\N	f	f
10346	PROJECT	Project	Yucca Valley Camping	262386	2022-01-21 10:42:29.608906+00	2022-01-21 10:42:29.608975+00	9	\N	\N	f	f
10347	PROJECT	Project	Yucca Valley Title Agency	262387	2022-01-21 10:42:29.613528+00	2022-01-21 10:42:29.613613+00	9	\N	\N	f	f
10348	PROJECT	Project	Zearfoss Windows Group	262388	2022-01-21 10:42:29.613704+00	2022-01-21 10:42:29.613735+00	9	\N	\N	f	f
10349	PROJECT	Project	Zechiel _ Management	262389	2022-01-21 10:42:29.613798+00	2022-01-21 10:42:29.613827+00	9	\N	\N	f	f
10350	PROJECT	Project	Zombro Telecom Leasing	262390	2022-01-21 10:42:29.613887+00	2022-01-21 10:42:29.613917+00	9	\N	\N	f	f
10351	PROJECT	Project	Zucca Electric Agency	262391	2022-01-21 10:42:29.613977+00	2022-01-21 10:42:29.614006+00	9	\N	\N	f	f
10352	PROJECT	Project	Zucconi Telecom Sales	262392	2022-01-21 10:42:29.655318+00	2022-01-21 10:42:29.655377+00	9	\N	\N	f	f
10353	PROJECT	Project	Zurasky Markets Dynamics	262393	2022-01-21 10:42:29.655467+00	2022-01-21 10:42:29.655505+00	9	\N	\N	f	f
10354	CLASS	Class	Fabrication	expense_custom_field.class.1	2022-01-21 10:42:30.106942+00	2022-01-21 10:42:30.107012+00	9	\N	{"custom_field_id": 197380}	f	f
10355	CLASS	Class	Adidas	expense_custom_field.class.2	2022-01-21 10:42:30.107153+00	2022-01-21 10:42:30.107199+00	9	\N	{"custom_field_id": 197380}	f	f
10356	CLASS	Class	FAE	expense_custom_field.class.3	2022-01-21 10:42:30.107325+00	2022-01-21 10:42:30.107366+00	9	\N	{"custom_field_id": 197380}	f	f
10357	TAX_GROUP	Tax Group	LCT: LCT-AU @25.0%	tg0jP7YiAnvm	2022-01-21 10:42:30.417815+00	2022-01-21 10:42:30.417861+00	9	\N	{"tax_rate": 0.25}	f	f
10358	TAX_GROUP	Tax Group	20.0% RC SG @0%	tg0o3fSL8NAA	2022-01-21 10:42:30.417937+00	2022-01-21 10:42:30.417968+00	9	\N	{"tax_rate": 0}	f	f
10359	TAX_GROUP	Tax Group	GST: ashwin_tax_code_1 @2.0%	tg3IOnT7GgBU	2022-01-21 10:42:30.41804+00	2022-01-21 10:42:30.418069+00	9	\N	{"tax_rate": 0.02}	f	f
10360	TAX_GROUP	Tax Group	City: New York City @0.50%	tg3ybu670Vkh	2022-01-21 10:42:30.418141+00	2022-01-21 10:42:30.41817+00	9	\N	{"tax_rate": 0.01}	f	f
10361	TAX_GROUP	Tax Group	GST: ADJ-AU @0.00%	tg56pDqYiTwV	2022-01-21 10:42:30.41824+00	2022-01-21 10:42:30.418269+00	9	\N	{"tax_rate": 0}	f	f
10362	TAX_GROUP	Tax Group	5.0% RC CIS @0%	tg5mTqU1vi4P	2022-01-21 10:42:30.418338+00	2022-01-21 10:42:30.418368+00	9	\N	{"tax_rate": 0}	f	f
10363	TAX_GROUP	Tax Group	GST: NCT-AU @10.0%	tg5zleSK4suF	2022-01-21 10:42:30.418439+00	2022-01-21 10:42:30.418469+00	9	\N	{"tax_rate": 0.1}	f	f
10364	TAX_GROUP	Tax Group	GST: CPI-AU @0.0%	tg6hRMmJHyiN	2022-01-21 10:42:30.41854+00	2022-01-21 10:42:30.418569+00	9	\N	{"tax_rate": 0.0}	f	f
10365	TAX_GROUP	Tax Group	GST on capital @10%	tg7qN6fQk0OO	2022-01-21 10:42:30.41864+00	2022-01-21 10:42:30.41867+00	9	\N	{"tax_rate": 0.1}	f	f
10366	TAX_GROUP	Tax Group	ABN: Nilesh @54.0%	tg841uXl0FJm	2022-01-21 10:42:30.418741+00	2022-01-21 10:42:30.41877+00	9	\N	{"tax_rate": 0.54}	f	f
10367	TAX_GROUP	Tax Group	GST-free capital @0%	tg8XdrMW1NFW	2022-01-21 10:42:30.41884+00	2022-01-21 10:42:30.418869+00	9	\N	{"tax_rate": 0}	f	f
10368	TAX_GROUP	Tax Group	GST: TFS-AU @0.0%	tg8zrjbf7Pek	2022-01-21 10:42:30.418939+00	2022-01-21 10:42:30.418969+00	9	\N	{"tax_rate": 0.0}	f	f
10369	TAX_GROUP	Tax Group	0.0% Z @0%	tg9wTORae59o	2022-01-21 10:42:30.419038+00	2022-01-21 10:42:30.419068+00	9	\N	{"tax_rate": 0}	f	f
10370	TAX_GROUP	Tax Group	5.0% R @0%	tgACRB9z5aIU	2022-01-21 10:42:30.419137+00	2022-01-21 10:42:30.419166+00	9	\N	{"tax_rate": 0}	f	f
10371	TAX_GROUP	Tax Group	0.0% ECG @0%	tgAnOXYKAmGt	2022-01-21 10:42:30.419287+00	2022-01-21 10:42:30.419318+00	9	\N	{"tax_rate": 0}	f	f
10372	TAX_GROUP	Tax Group	GST: NCF-AU @0.00%	tgApaULAyFVs	2022-01-21 10:42:30.419388+00	2022-01-21 10:42:30.419418+00	9	\N	{"tax_rate": 0}	f	f
10373	TAX_GROUP	Tax Group	GST: TFS-AU @0.00%	tgb8KBzGpC0q	2022-01-21 10:42:30.419487+00	2022-01-21 10:42:30.419516+00	9	\N	{"tax_rate": 0}	f	f
10374	TAX_GROUP	Tax Group	12.5% TR @12.5%	tgBa0XDF4hGq	2022-01-21 10:42:30.41959+00	2022-01-21 10:42:30.419619+00	9	\N	{"tax_rate": 0.12}	f	f
10375	TAX_GROUP	Tax Group	GST: NCF-AU @0.0%	tgBtbiOfxmUi	2022-01-21 10:42:30.419691+00	2022-01-21 10:42:30.419721+00	9	\N	{"tax_rate": 0.0}	f	f
10376	TAX_GROUP	Tax Group	GST on non-capital @10%	tgbXR6tQWMGX	2022-01-21 10:42:30.419792+00	2022-01-21 10:42:30.419822+00	9	\N	{"tax_rate": 0.1}	f	f
10377	TAX_GROUP	Tax Group	LCT: LCT-AU @25.00%	tgBZzCVa4zt5	2022-01-21 10:42:30.419894+00	2022-01-21 10:42:30.419923+00	9	\N	{"tax_rate": 0.25}	f	f
10378	TAX_GROUP	Tax Group	GST: CPF-AU @0.0%	tgC12NST1mOq	2022-01-21 10:42:30.419994+00	2022-01-21 10:42:30.420023+00	9	\N	{"tax_rate": 0.0}	f	f
10379	TAX_GROUP	Tax Group	20.0% ECG @0%	tgDHpcLDulrH	2022-01-21 10:42:30.420093+00	2022-01-21 10:42:30.420123+00	9	\N	{"tax_rate": 0}	f	f
10380	TAX_GROUP	Tax Group	GST: CPT-AU @10.0%	tgDp8PMghYAe	2022-01-21 10:42:30.420195+00	2022-01-21 10:42:30.420224+00	9	\N	{"tax_rate": 0.1}	f	f
10381	TAX_GROUP	Tax Group	State: New York State @6.5%	tgEaNHTqgTki	2022-01-21 10:42:30.420296+00	2022-01-21 10:42:30.420325+00	9	\N	{"tax_rate": 0.07}	f	f
10382	TAX_GROUP	Tax Group	GST: UNDEF-AU @0.00%	tgf4vbmRF3R3	2022-01-21 10:42:30.420394+00	2022-01-21 10:42:30.420424+00	9	\N	{"tax_rate": 0}	f	f
10383	TAX_GROUP	Tax Group	GST: NA-AU @0.00%	tgG1dhQralPG	2022-01-21 10:42:30.420494+00	2022-01-21 10:42:30.420523+00	9	\N	{"tax_rate": 0}	f	f
10384	TAX_GROUP	Tax Group	20.0% RC CIS @0%	tgG1HPbRVPAV	2022-01-21 10:42:30.420592+00	2022-01-21 10:42:30.420622+00	9	\N	{"tax_rate": 0}	f	f
10385	TAX_GROUP	Tax Group	PVA Import 0.0% @0%	tgG5fZGAjBIU	2022-01-21 10:42:30.420691+00	2022-01-21 10:42:30.42072+00	9	\N	{"tax_rate": 0}	f	f
10386	TAX_GROUP	Tax Group	VAT: Wow Tax @10.0%	tgg9pmMvaBj1	2022-01-21 10:42:30.420793+00	2022-01-21 10:42:30.420822+00	9	\N	{"tax_rate": 0.1}	f	f
10387	TAX_GROUP	Tax Group	GST: NCI-AU @0.00%	tgGRmMO8I2jF	2022-01-21 10:42:30.420893+00	2022-01-21 10:42:30.420922+00	9	\N	{"tax_rate": 0}	f	f
10388	TAX_GROUP	Tax Group	GST: ADJ-AU @0.0%	tggtXH6PA9to	2022-01-21 10:42:30.420993+00	2022-01-21 10:42:30.421023+00	9	\N	{"tax_rate": 0.0}	f	f
10389	TAX_GROUP	Tax Group	GST: CPT-AU @10.00%	tgi20gBQ6505	2022-01-21 10:42:30.421095+00	2022-01-21 10:42:30.421124+00	9	\N	{"tax_rate": 0.1}	f	f
10390	TAX_GROUP	Tax Group	Input tax @0%	tgjfUIqaAaln	2022-01-21 10:42:30.421194+00	2022-01-21 10:42:30.421223+00	9	\N	{"tax_rate": 0}	f	f
10391	TAX_GROUP	Tax Group	GST: NCI-AU @0.0%	tgjxMmKzEOa5	2022-01-21 10:42:30.421293+00	2022-01-21 10:42:30.421323+00	9	\N	{"tax_rate": 0.0}	f	f
10392	TAX_GROUP	Tax Group	GST: UNDEF-AU @0.0%	tgKbaSNHU1QX	2022-01-21 10:42:30.421393+00	2022-01-21 10:42:30.421423+00	9	\N	{"tax_rate": 0.0}	f	f
10393	TAX_GROUP	Tax Group	0.0% ECS @0%	tgkU7SzfzD7n	2022-01-21 10:42:30.421493+00	2022-01-21 10:42:30.421522+00	9	\N	{"tax_rate": 0}	f	f
10394	TAX_GROUP	Tax Group	VAT: UK Tax @10.0%	tgl64n2eY32Z	2022-01-21 10:42:30.421594+00	2022-01-21 10:42:30.421623+00	9	\N	{"tax_rate": 0.1}	f	f
10395	TAX_GROUP	Tax Group	GST: NCT-AU @10.00%	tglf3pMW8a1G	2022-01-21 10:42:30.421694+00	2022-01-21 10:42:30.421723+00	9	\N	{"tax_rate": 0.1}	f	f
10396	TAX_GROUP	Tax Group	Nilesh Tax @10%	tglqjzvubilx	2022-01-21 10:42:30.421794+00	2022-01-21 10:42:30.421824+00	9	\N	{"tax_rate": 0.1}	f	f
10397	TAX_GROUP	Tax Group	20.0% RC MPCCs @0%	tgm4KVJbnFhy	2022-01-21 10:42:30.421893+00	2022-01-21 10:42:30.421923+00	9	\N	{"tax_rate": 0}	f	f
10398	TAX_GROUP	Tax Group	20.0% RC @0%	tgmCW3nolkbr	2022-01-21 10:42:30.423062+00	2022-01-21 10:42:30.423114+00	9	\N	{"tax_rate": 0}	f	f
10399	TAX_GROUP	Tax Group	GST: ITS-AU @0.0%	tgmes5ns1ho0	2022-01-21 10:42:30.423212+00	2022-01-21 10:42:30.423242+00	9	\N	{"tax_rate": 0.0}	f	f
10400	TAX_GROUP	Tax Group	ABN: dfvdfvf @20.0%	tgMrxue8VEkZ	2022-01-21 10:42:30.423318+00	2022-01-21 10:42:30.423347+00	9	\N	{"tax_rate": 0.2}	f	f
10401	TAX_GROUP	Tax Group	City: New York City @0.5%	tgMuuSflHCmy	2022-01-21 10:42:30.423423+00	2022-01-21 10:42:30.423452+00	9	\N	{"tax_rate": 0.01}	f	f
10402	TAX_GROUP	Tax Group	20.0% S @20%	tgNAiAR2Iq9D	2022-01-21 10:42:30.423524+00	2022-01-21 10:42:30.423553+00	9	\N	{"tax_rate": 0.2}	f	f
10403	TAX_GROUP	Tax Group	GST: Testing Tax @25.0%	tgNAmDYiytPi	2022-01-21 10:42:30.423624+00	2022-01-21 10:42:30.423654+00	9	\N	{"tax_rate": 0.25}	f	f
10404	TAX_GROUP	Tax Group	GST: NA-AU @0.0%	tgNfLWOi9eOu	2022-01-21 10:42:30.423726+00	2022-01-21 10:42:30.423755+00	9	\N	{"tax_rate": 0.0}	f	f
10405	TAX_GROUP	Tax Group	20.0% S @0%	tgNhO6pwQm7i	2022-01-21 10:42:30.423824+00	2022-01-21 10:42:30.423854+00	9	\N	{"tax_rate": 0}	f	f
10406	TAX_GROUP	Tax Group	Asambhav Tax @0%	tgPmnTtbOKF0	2022-01-21 10:42:30.423923+00	2022-01-21 10:42:30.423952+00	9	\N	{"tax_rate": 0}	f	f
10407	TAX_GROUP	Tax Group	No VAT @0%	tgPO3nGIAB5s	2022-01-21 10:42:30.474651+00	2022-01-21 10:42:30.474726+00	9	\N	{"tax_rate": 0}	f	f
10408	TAX_GROUP	Tax Group	GST-free non-capital @0%	tgq1Otx0Ti7a	2022-01-21 10:42:30.475864+00	2022-01-21 10:42:30.475972+00	9	\N	{"tax_rate": 0}	f	f
10409	TAX_GROUP	Tax Group	GST: ITS-AU @0.00%	tgqR6gS2lzBp	2022-01-21 10:42:30.480205+00	2022-01-21 10:42:30.48851+00	9	\N	{"tax_rate": 0}	f	f
10410	TAX_GROUP	Tax Group	ABN: Ashwin Tax Group @6.0%	tgSA89iowJgX	2022-01-21 10:42:30.491138+00	2022-01-21 10:42:30.491228+00	9	\N	{"tax_rate": 0.06}	f	f
10411	TAX_GROUP	Tax Group	County: New York County @1.50%	tgsbKb0IOmXy	2022-01-21 10:42:30.492121+00	2022-01-21 10:42:30.492237+00	9	\N	{"tax_rate": 0.01}	f	f
10412	TAX_GROUP	Tax Group	20.0% ECS @0%	tgt6oULsRrbd	2022-01-21 10:42:30.492516+00	2022-01-21 10:42:30.492564+00	9	\N	{"tax_rate": 0}	f	f
10413	TAX_GROUP	Tax Group	12.5% TR @0%	tgu5g44DcXvs	2022-01-21 10:42:30.494416+00	2022-01-21 10:42:30.494504+00	9	\N	{"tax_rate": 0}	f	f
10414	TAX_GROUP	Tax Group	GST: TS-AU @10.0%	tguY5ftylp4n	2022-01-21 10:42:30.494703+00	2022-01-21 10:42:30.494752+00	9	\N	{"tax_rate": 0.1}	f	f
10415	TAX_GROUP	Tax Group	GST: ashwin_tax_code_2 @4.0%	tgUzUai1BPsD	2022-01-21 10:42:30.494906+00	2022-01-21 10:42:30.497061+00	9	\N	{"tax_rate": 0.04}	f	f
10416	TAX_GROUP	Tax Group	5.0% R @5%	tgVFPyoUMETN	2022-01-21 10:42:30.497797+00	2022-01-21 10:42:30.497861+00	9	\N	{"tax_rate": 0.05}	f	f
10417	TAX_GROUP	Tax Group	Other 2 Sales Tax: GST @18.0%	tgviK06kpxuB	2022-01-21 10:42:30.509089+00	2022-01-21 10:42:30.510846+00	9	\N	{"tax_rate": 0.18}	f	f
10418	TAX_GROUP	Tax Group	GST: EXPS-AU @0.0%	tgw4zSmEMSR3	2022-01-21 10:42:30.511958+00	2022-01-21 10:42:30.512129+00	9	\N	{"tax_rate": 0.0}	f	f
10419	TAX_GROUP	Tax Group	County: New York County @1.5%	tgwFGNWWL5Dr	2022-01-21 10:42:30.51305+00	2022-01-21 10:42:30.513092+00	9	\N	{"tax_rate": 0.01}	f	f
10420	TAX_GROUP	Tax Group	Exempt @0%	tgWRYVoRZP6Y	2022-01-21 10:42:30.51317+00	2022-01-21 10:42:30.5132+00	9	\N	{"tax_rate": 0}	f	f
10421	TAX_GROUP	Tax Group	Pant Tax @20%	tgxEyV3RQLIK	2022-01-21 10:42:30.513275+00	2022-01-21 10:42:30.513305+00	9	\N	{"tax_rate": 0.2}	f	f
10422	TAX_GROUP	Tax Group	GST: CPI-AU @0.00%	tgXkAYupySVc	2022-01-21 10:42:30.513376+00	2022-01-21 10:42:30.513406+00	9	\N	{"tax_rate": 0}	f	f
10423	TAX_GROUP	Tax Group	WET: WET-AU @29.0%	tgy5y5uO5qL7	2022-01-21 10:42:30.513478+00	2022-01-21 10:42:30.513509+00	9	\N	{"tax_rate": 0.29}	f	f
10424	TAX_GROUP	Tax Group	GST: EXPS-AU @0.00%	tgyve56tjSoq	2022-01-21 10:42:30.513584+00	2022-01-21 10:42:30.513614+00	9	\N	{"tax_rate": 0}	f	f
10425	TAX_GROUP	Tax Group	VAT: UNDEF-GB @0.0%	tgZ5uPnsE0Dh	2022-01-21 10:42:30.513686+00	2022-01-21 10:42:30.513716+00	9	\N	{"tax_rate": 0.0}	f	f
10426	TAX_GROUP	Tax Group	GST: CPF-AU @0.00%	tgZDLivGwC4C	2022-01-21 10:42:30.513786+00	2022-01-21 10:42:30.537152+00	9	\N	{"tax_rate": 0}	f	f
10427	TAX_GROUP	Tax Group	PVA Import 20.0% @0%	tgZHmshjcBit	2022-01-21 10:42:30.537397+00	2022-01-21 10:42:30.537446+00	9	\N	{"tax_rate": 0}	f	f
10428	TAX_GROUP	Tax Group	GST: TS-AU @10.00%	tgzoMYBncKYp	2022-01-21 10:42:30.537561+00	2022-01-21 10:42:30.537599+00	9	\N	{"tax_rate": 0.1}	f	f
12208	EMPLOYEE	Employee	mikasa@fyle.in	ou7l33OoTano	2022-01-28 10:12:31.762028+00	2022-01-28 10:12:31.762106+00	8	\N	{"location": null, "full_name": "mikasa", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
12210	CORPORATE_CARD	Corporate Card	BANK OF INDIA - 219875	baccKkmmW4u1N4	2022-02-01 07:50:24.756517+00	2022-02-01 07:50:24.756621+00	8	\N	{"cardholder_name": null}	f	f
12211	CORPORATE_CARD	Corporate Card	BANK OF INDIA - 219876	baccfiqYgkE8Db	2022-02-01 07:50:24.756754+00	2022-02-01 07:50:24.756788+00	8	\N	{"cardholder_name": null}	f	f
12212	CORPORATE_CARD	Corporate Card	Bank of America - 8084	baccMCkKmsHV9X	2022-02-01 07:50:24.757022+00	2022-02-01 07:50:24.75706+00	8	\N	{"cardholder_name": null}	f	f
12213	CORPORATE_CARD	Corporate Card	Bank of America - 1319	baccJKh39lWI2L	2022-02-01 07:50:24.757357+00	2022-02-01 07:50:24.757697+00	8	\N	{"cardholder_name": null}	f	f
12214	CORPORATE_CARD	Corporate Card	American Express - 30350	bacc3D6qx7cb4J	2022-02-01 07:50:24.758121+00	2022-02-01 07:50:24.758165+00	8	\N	{"cardholder_name": "Dr. Ross Eustace Geller's account"}	f	f
12215	CORPORATE_CARD	Corporate Card	American Express - 05556	baccuGmJMILiAr	2022-02-01 07:50:24.758242+00	2022-02-01 07:50:24.758271+00	8	\N	{"cardholder_name": "Phoebe Buffay-Hannigan's account"}	f	f
12216	CORPORATE_CARD	Corporate Card	American Express - 93634	bacc8nxvDzy9UB	2022-02-01 07:50:24.758341+00	2022-02-01 07:50:24.75837+00	8	\N	{"cardholder_name": "Joseph Francis Tribbiani, Jr's account"}	f	f
12217	CORPORATE_CARD	Corporate Card	American Express - 59344	baccRUz3T9WTG0	2022-02-01 07:50:24.75844+00	2022-02-01 07:50:24.758468+00	8	\N	{"cardholder_name": "Dr. Ross Eustace Geller's account"}	f	f
12218	CORPORATE_CARD	Corporate Card	American Express - 29676	baccJEu4LHANTj	2022-02-01 07:50:24.758538+00	2022-02-01 07:50:24.758567+00	8	\N	{"cardholder_name": "Monica E. Geller-Bing's account"}	f	f
12219	CORPORATE_CARD	Corporate Card	American Express - 97584	bacc3gPRo0BFI4	2022-02-01 07:50:24.759162+00	2022-02-01 07:50:24.759207+00	8	\N	{"cardholder_name": "Monica E. Geller-Bing's account"}	f	f
12220	CORPORATE_CARD	Corporate Card	American Express - 27881	baccT6Cr2LOoCU	2022-02-01 07:50:24.75939+00	2022-02-01 07:50:24.759424+00	8	\N	{"cardholder_name": "Monica E. Geller-Bing's account"}	f	f
12221	CORPORATE_CARD	Corporate Card	American Express - 40414	baccChwshlFsT5	2022-02-01 07:50:24.759647+00	2022-02-01 07:50:24.759689+00	8	\N	{"cardholder_name": "Monica E. Geller-Bing's account"}	f	f
12222	CORPORATE_CARD	Corporate Card	American Express - 71149	baccaQY7KB7ogS	2022-02-01 07:50:24.760033+00	2022-02-01 07:50:24.760097+00	8	\N	{"cardholder_name": "Joseph Francis Tribbiani, Jr's account"}	f	f
12223	CORPORATE_CARD	Corporate Card	American Express - 29578	bacce3rbqv5Veb	2022-02-01 07:50:24.760705+00	2022-02-01 07:50:24.760969+00	8	\N	{"cardholder_name": "Monica E. Geller-Bing's account"}	f	f
12224	CORPORATE_CARD	Corporate Card	American Express - 93356	baccUhWPMgn4EB	2022-02-01 07:50:24.761208+00	2022-02-01 07:50:24.761249+00	8	\N	{"cardholder_name": "Dr. Ross Eustace Geller's account"}	f	f
12225	CORPORATE_CARD	Corporate Card	American Express - 64504	baccE0fU1LTqxm	2022-02-01 07:50:24.761483+00	2022-02-01 07:50:24.761524+00	8	\N	{"cardholder_name": "Joseph Francis Tribbiani, Jr's account"}	f	f
12226	CORPORATE_CARD	Corporate Card	American Express - 69115	baccKzSkYJjBQt	2022-02-01 07:50:24.761756+00	2022-02-01 07:50:24.761791+00	8	\N	{"cardholder_name": "Joseph Francis Tribbiani, Jr's account"}	f	f
12227	CORPORATE_CARD	Corporate Card	GPAY BANK - 219875	baccbhkX5lA0TT	2022-02-01 07:57:28.821023+00	2022-02-01 07:57:28.821071+00	9	\N	{"cardholder_name": null}	f	f
12228	CORPORATE_CARD	Corporate Card	GPAY BANK - 219876	baccmW34eWxXXM	2022-02-01 07:57:28.821155+00	2022-02-01 07:57:28.821186+00	9	\N	{"cardholder_name": null}	f	f
12229	CORPORATE_CARD	Corporate Card	American Express - 70392	baccbGReqIa7xB	2022-02-01 07:57:28.821262+00	2022-02-01 07:57:28.821292+00	9	\N	{"cardholder_name": "Monica E. Geller-Bing's account"}	f	f
12230	CORPORATE_CARD	Corporate Card	GPAY BANK - 219874	baccNUw01Ere0t	2022-02-01 07:57:28.821365+00	2022-02-01 07:57:28.821394+00	9	\N	{"cardholder_name": null}	f	f
12231	CORPORATE_CARD	Corporate Card	American Express - 15812	baccDNQlplY8Yb	2022-02-01 07:57:28.821466+00	2022-02-01 07:57:28.821495+00	9	\N	{"cardholder_name": "Chandler Muriel Bing's account"}	f	f
12232	CORPORATE_CARD	Corporate Card	Bank of America - 8084	baccdf7BlqXmNS	2022-02-01 07:57:28.821742+00	2022-02-01 07:57:28.821773+00	9	\N	{"cardholder_name": null}	f	f
12233	CORPORATE_CARD	Corporate Card	Bank of America - 1319	bacctuee9mV2Dl	2022-02-01 07:57:28.821846+00	2022-02-01 07:57:28.821875+00	9	\N	{"cardholder_name": null}	f	f
12234	CORPORATE_CARD	Corporate Card	American Express - 85470	bacczbsnk4TKQ0	2022-02-01 07:57:28.821946+00	2022-02-01 07:57:28.821975+00	9	\N	{"cardholder_name": "Monica E. Geller-Bing's account"}	f	f
12235	CORPORATE_CARD	Corporate Card	American Express - 78448	baccPsL1HAPLtm	2022-02-01 07:57:28.822045+00	2022-02-01 07:57:28.822074+00	9	\N	{"cardholder_name": "Monica E. Geller-Bing's account"}	f	f
12236	CORPORATE_CARD	Corporate Card	American Express - 39509	baccu5vSVlzQrb	2022-02-01 07:57:28.822143+00	2022-02-01 07:57:28.822173+00	9	\N	{"cardholder_name": "Joseph Francis Tribbiani, Jr's account"}	f	f
12237	CORPORATE_CARD	Corporate Card	American Express - 62224	baccddo9BS6W6Y	2022-02-01 07:57:28.822242+00	2022-02-01 07:57:28.822271+00	9	\N	{"cardholder_name": "Chandler Muriel Bing's account"}	f	f
12238	CORPORATE_CARD	Corporate Card	American Express - 00428	baccO1KAFCsXaF	2022-02-01 07:57:28.822341+00	2022-02-01 07:57:28.82237+00	9	\N	{"cardholder_name": "Phoebe Buffay-Hannigan's account"}	f	f
12239	CORPORATE_CARD	Corporate Card	American Express - 13559	baccoVYhrFKuhV	2022-02-01 07:57:28.82244+00	2022-02-01 07:57:28.822469+00	9	\N	{"cardholder_name": "Monica E. Geller-Bing's account"}	f	f
12240	CORPORATE_CARD	Corporate Card	American Express - 94385	baccURYMBjekiy	2022-02-01 07:57:28.822538+00	2022-02-01 07:57:28.822722+00	9	\N	{"cardholder_name": "Chandler Muriel Bing's account"}	f	f
12241	CORPORATE_CARD	Corporate Card	American Express - 70381	baccvMtCrKypdV	2022-02-01 07:57:28.822795+00	2022-02-01 07:57:28.822824+00	9	\N	{"cardholder_name": "Dr. Ross Eustace Geller's account"}	f	f
12242	CORPORATE_CARD	Corporate Card	American Express - 05433	baccCc3H0QFgWw	2022-02-01 07:57:28.822894+00	2022-02-01 07:57:28.822923+00	9	\N	{"cardholder_name": "Phoebe Buffay-Hannigan's account"}	f	f
12243	CORPORATE_CARD	Corporate Card	American Express - 74399	bacczhJJcNhYue	2022-02-01 07:57:28.822993+00	2022-02-01 07:57:28.823022+00	9	\N	{"cardholder_name": "Dr. Ross Eustace Geller's account"}	f	f
12244	CORPORATE_CARD	Corporate Card	American Express - 25493	baccw7tz5rfIwZ	2022-02-01 07:57:28.823091+00	2022-02-01 07:57:28.82312+00	9	\N	{"cardholder_name": "Joseph Francis Tribbiani, Jr's account"}	f	f
\.


--
-- Data for Name: expense_group_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expense_group_settings (id, reimbursable_expense_group_fields, corporate_credit_card_expense_group_fields, created_at, updated_at, workspace_id, reimbursable_export_date_type, expense_state, import_card_credits, ccc_export_date_type) FROM stdin;
8	{employee_email,report_id,claim_number,fund_source}	{employee_email,report_id,claim_number,fund_source}	2022-01-21 10:34:47.717559+00	2022-01-21 10:34:47.717602+00	8	current_date	PAYMENT_PROCESSING	f	current_date
9	{employee_email,report_id,claim_number,fund_source}	{employee_email,fund_source,claim_number,expense_id,report_id}	2022-01-21 10:41:25.327593+00	2022-01-21 10:42:32.728758+00	9	current_date	PAYMENT_PROCESSING	t	spent_at
\.


--
-- Data for Name: expense_groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expense_groups (id, description, created_at, updated_at, workspace_id, fund_source, exported_at, response_logs) FROM stdin;
6	{"report_id": "rpqBKuvCwnTY", "fund_source": "PERSONAL", "claim_number": "C/2022/01/R/7", "employee_email": "ashwin.t@fyle.in"}	2022-01-21 10:45:18.55195+00	2022-01-21 10:45:34.191401+00	9	PERSONAL	2022-01-21 10:45:34.190723+00	{"Bill": {"Id": "146", "Line": [{"Id": "1", "Amount": 120.0, "LineNum": 1, "LinkedTxn": [], "DetailType": "AccountBasedExpenseLineDetail", "Description": "ashwin.t@fyle.in - Travel - 2022-01-21 - C/2022/01/R/7 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txDmcqOv8LMD?org_id=orGcBCVPijjO", "AccountBasedExpenseLineDetail": {"AccountRef": {"name": "Insurance:Workers Compensation", "value": "57"}, "TaxCodeRef": {"value": "NON"}, "BillableStatus": "NotBillable"}}], "domain": "QBO", "sparse": false, "Balance": 120.0, "DueDate": "2022-01-21", "TxnDate": "2022-01-21", "MetaData": {"CreateTime": "2022-01-21T02:45:34-08:00", "LastUpdatedTime": "2022-01-21T02:45:34-08:00"}, "TotalAmt": 120.0, "SyncToken": "0", "VendorRef": {"name": "Mahoney Mugs", "value": "43"}, "CurrencyRef": {"name": "United States Dollar", "value": "USD"}, "PrivateNote": "Reimbursable expense by ashwin.t@fyle.in on 2022-01-21", "APAccountRef": {"name": "Accounts Payable (A/P)", "value": "33"}}, "time": "2022-01-21T02:45:34.098-08:00"}
7	{"spent_at": "2022-01-21", "report_id": "rpqBKuvCwnTY", "expense_id": "txJkZlJS4LrA", "fund_source": "CCC", "claim_number": "C/2022/01/R/7", "employee_email": "ashwin.t@fyle.in"}	2022-01-21 10:45:18.559491+00	2022-01-21 10:45:38.000453+00	9	CCC	2022-01-21 10:45:38.00027+00	{"time": "2022-01-21T02:45:37.586-08:00", "Purchase": {"Id": "147", "Line": [{"Id": "1", "Amount": 50.0, "DetailType": "AccountBasedExpenseLineDetail", "Description": "ashwin.t@fyle.in - Travel - 2022-01-21 - C/2022/01/R/7 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txJkZlJS4LrA?org_id=orGcBCVPijjO", "AccountBasedExpenseLineDetail": {"AccountRef": {"name": "Insurance:Workers Compensation", "value": "57"}, "TaxCodeRef": {"value": "NON"}, "BillableStatus": "NotBillable"}}], "Credit": false, "domain": "QBO", "sparse": false, "TxnDate": "2022-01-21", "MetaData": {"CreateTime": "2022-01-21T02:45:37-08:00", "LastUpdatedTime": "2022-01-21T02:45:37-08:00"}, "TotalAmt": 50.0, "DocNumber": "E/2022/01/T/8", "EntityRef": {"name": "Credit Card Misc", "type": "Vendor", "value": "58"}, "SyncToken": "0", "AccountRef": {"name": "Visa", "value": "42"}, "PurchaseEx": {"any": [{"nil": false, "name": "{http://schema.intuit.com/finance/v3}NameValue", "scope": "javax.xml.bind.JAXBElement$GlobalScope", "value": {"Name": "TxnType", "Value": "54"}, "globalScope": true, "declaredType": "com.intuit.schema.finance.v3.NameValue", "typeSubstituted": false}]}, "CurrencyRef": {"name": "United States Dollar", "value": "USD"}, "CustomField": [], "PaymentType": "CreditCard", "PrivateNote": "Credit card expense by ashwin.t@fyle.in on 2022-01-21"}}
8	{"report_id": "rpeM68HKCNNA", "fund_source": "PERSONAL", "claim_number": "C/2022/01/R/8", "employee_email": "ashwin.t@fyle.in"}	2022-01-21 10:51:06.522345+00	2022-01-21 10:51:06.522418+00	9	PERSONAL	\N	\N
9	{"report_id": "rpeM68HKCNNA", "expense_id": "txvh8qm7RTRI", "fund_source": "CCC", "claim_number": "C/2022/01/R/8", "employee_email": "ashwin.t@fyle.in"}	2022-01-21 10:51:06.530816+00	2022-01-21 10:51:06.530894+00	9	CCC	\N	\N
12	{"report_id": "rp2HJURYKsXI", "fund_source": "CCC", "claim_number": "C/2022/01/R/14", "employee_email": "ashwin.t@fyle.in"}	2022-01-23 12:15:58.449459+00	2022-01-23 12:15:58.449534+00	8	CCC	\N	\N
10	{"report_id": "rp0jk7Rg1epk", "fund_source": "PERSONAL", "claim_number": "C/2022/01/R/13", "employee_email": "ashwin.t@fyle.in"}	2022-01-23 12:03:11.004879+00	2022-01-23 12:03:25.849971+00	8	PERSONAL	2022-01-23 12:03:25.849573+00	{"time": "2022-01-23T04:03:25.563-08:00", "Purchase": {"Id": "1969", "Line": [{"Id": "1", "Amount": 60.0, "DetailType": "AccountBasedExpenseLineDetail", "Description": "ashwin.t@fyle.in - Food - 2022-01-23 - C/2022/01/R/13 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txraSPJaG9Ep?org_id=or79Cob97KSh", "AccountBasedExpenseLineDetail": {"AccountRef": {"name": "Automobile:Fuel", "value": "56"}, "TaxCodeRef": {"value": "NON"}, "BillableStatus": "NotBillable"}}], "Credit": false, "domain": "QBO", "sparse": false, "TxnDate": "2022-01-23", "MetaData": {"CreateTime": "2022-01-23T04:03:25-08:00", "LastUpdatedTime": "2022-01-23T04:03:25-08:00"}, "TotalAmt": 60.0, "EntityRef": {"name": "Emily Platt", "type": "Employee", "value": "55"}, "SyncToken": "0", "AccountRef": {"name": "Mastercard", "value": "41"}, "PurchaseEx": {"any": [{"nil": false, "name": "{http://schema.intuit.com/finance/v3}NameValue", "scope": "javax.xml.bind.JAXBElement$GlobalScope", "value": {"Name": "TxnType", "Value": "54"}, "globalScope": true, "declaredType": "com.intuit.schema.finance.v3.NameValue", "typeSubstituted": false}]}, "CurrencyRef": {"name": "United States Dollar", "value": "USD"}, "CustomField": [], "PaymentType": "CreditCard", "PrivateNote": "Reimbursable expense by ashwin.t@fyle.in on 2022-01-23"}}
11	{"report_id": "rp2HJURYKsXI", "fund_source": "PERSONAL", "claim_number": "C/2022/01/R/14", "employee_email": "ashwin.t@fyle.in"}	2022-01-23 12:15:58.39212+00	2022-01-23 12:16:43.49229+00	8	PERSONAL	2022-01-23 12:16:43.491938+00	{"time": "2022-01-23T04:16:43.324-08:00", "Purchase": {"Id": "1970", "Line": [{"Id": "1", "Amount": 60.0, "DetailType": "AccountBasedExpenseLineDetail", "Description": "ashwin.t@fyle.in - Food - 2022-01-23 - C/2022/01/R/14 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txiKwmiTDjwJ?org_id=or79Cob97KSh", "AccountBasedExpenseLineDetail": {"AccountRef": {"name": "Automobile:Fuel", "value": "56"}, "TaxCodeRef": {"value": "NON"}, "BillableStatus": "NotBillable"}}], "Credit": false, "domain": "QBO", "sparse": false, "TxnDate": "2022-01-23", "MetaData": {"CreateTime": "2022-01-23T04:16:43-08:00", "LastUpdatedTime": "2022-01-23T04:16:43-08:00"}, "TotalAmt": 60.0, "EntityRef": {"name": "Emily Platt", "type": "Employee", "value": "55"}, "SyncToken": "0", "AccountRef": {"name": "Mastercard", "value": "41"}, "PurchaseEx": {"any": [{"nil": false, "name": "{http://schema.intuit.com/finance/v3}NameValue", "scope": "javax.xml.bind.JAXBElement$GlobalScope", "value": {"Name": "TxnType", "Value": "54"}, "globalScope": true, "declaredType": "com.intuit.schema.finance.v3.NameValue", "typeSubstituted": false}]}, "CurrencyRef": {"name": "United States Dollar", "value": "USD"}, "CustomField": [], "PaymentType": "CreditCard", "PrivateNote": "Reimbursable expense by ashwin.t@fyle.in on 2022-01-23"}}
13	{"report_id": "rprUeNwizDFb", "fund_source": "PERSONAL", "claim_number": "C/2022/01/R/15", "employee_email": "ashwin.t@fyle.in"}	2022-01-23 12:33:36.034871+00	2022-01-23 12:33:47.309099+00	8	PERSONAL	2022-01-23 12:33:47.308208+00	{"time": "2022-01-23T04:33:47.121-08:00", "Purchase": {"Id": "1972", "Line": [{"Id": "1", "Amount": 60.0, "DetailType": "AccountBasedExpenseLineDetail", "Description": "ashwin.t@fyle.in - Food - 2022-01-23 - C/2022/01/R/15 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txQybwOwoQAA?org_id=or79Cob97KSh", "AccountBasedExpenseLineDetail": {"AccountRef": {"name": "Automobile:Fuel", "value": "56"}, "TaxCodeRef": {"value": "NON"}, "BillableStatus": "NotBillable"}}], "Credit": false, "domain": "QBO", "sparse": false, "TxnDate": "2022-01-23", "MetaData": {"CreateTime": "2022-01-23T04:33:47-08:00", "LastUpdatedTime": "2022-01-23T04:33:47-08:00"}, "TotalAmt": 60.0, "EntityRef": {"name": "Emily Platt", "type": "Employee", "value": "55"}, "SyncToken": "0", "AccountRef": {"name": "Mastercard", "value": "41"}, "PurchaseEx": {"any": [{"nil": false, "name": "{http://schema.intuit.com/finance/v3}NameValue", "scope": "javax.xml.bind.JAXBElement$GlobalScope", "value": {"Name": "TxnType", "Value": "54"}, "globalScope": true, "declaredType": "com.intuit.schema.finance.v3.NameValue", "typeSubstituted": false}]}, "CurrencyRef": {"name": "United States Dollar", "value": "USD"}, "CustomField": [], "PaymentType": "CreditCard", "PrivateNote": "Reimbursable expense by ashwin.t@fyle.in on 2022-01-23"}}
14	{"report_id": "rpBQ9vx7FJc3", "fund_source": "PERSONAL", "claim_number": "C/2022/01/R/16", "employee_email": "ashwin.t@fyle.in"}	2022-01-23 12:37:54.136732+00	2022-01-23 12:37:54.136795+00	8	PERSONAL	\N	\N
\.


--
-- Data for Name: expense_groups_expenses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expense_groups_expenses (id, expensegroup_id, expense_id) FROM stdin;
6	6	6
7	7	7
8	8	8
9	9	9
10	10	10
11	11	11
12	12	12
13	13	13
14	14	14
\.


--
-- Data for Name: expenses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expenses (id, employee_email, category, sub_category, project, expense_id, expense_number, claim_number, amount, currency, foreign_amount, foreign_currency, settlement_id, reimbursable, exported, state, vendor, cost_center, purpose, report_id, spent_at, approved_at, expense_created_at, expense_updated_at, created_at, updated_at, fund_source, custom_properties, verified_at, billable, paid_on_qbo, org_id, tax_amount, tax_group_id, file_ids, corporate_card_id) FROM stdin;
6	ashwin.t@fyle.in	Travel	Travel	\N	txDmcqOv8LMD	E/2022/01/T/7	C/2022/01/R/7	120	USD	\N	\N	setS3D0ItJsD2	t	f	PAYMENT_PROCESSING	\N	\N	\N	rpqBKuvCwnTY	2022-01-21 00:00:00+00	2022-01-21 00:00:00+00	2022-01-21 10:00:23.459+00	2022-01-21 10:02:13.588+00	2022-01-21 10:45:18.322426+00	2022-01-21 10:45:18.322467+00	PERSONAL	{"Class": ""}	\N	\N	f	orGcBCVPijjO	\N	\N	\N	\N
7	ashwin.t@fyle.in	Travel	Travel	\N	txJkZlJS4LrA	E/2022/01/T/8	C/2022/01/R/7	50	USD	\N	\N	setS3D0ItJsD2	f	f	PAYMENT_PROCESSING	\N	\N	\N	rpqBKuvCwnTY	2022-01-21 00:00:00+00	2022-01-21 00:00:00+00	2022-01-21 10:00:41.232+00	2022-01-21 10:02:13.588+00	2022-01-21 10:45:18.435608+00	2022-01-21 10:45:18.435701+00	CCC	{"Class": ""}	\N	\N	f	orGcBCVPijjO	\N	\N	\N	\N
8	ashwin.t@fyle.in	Travel	Travel	\N	txlPjmNxssq1	E/2022/01/T/10	C/2022/01/R/8	60	USD	\N	\N	set5qvkasVDnI	t	f	PAYMENT_PROCESSING	\N	\N	\N	rpeM68HKCNNA	2022-01-21 00:00:00+00	2022-01-21 00:00:00+00	2022-01-21 10:46:19.877+00	2022-01-21 10:48:53.928+00	2022-01-21 10:51:06.448907+00	2022-01-21 10:51:06.448944+00	PERSONAL	{"Class": ""}	\N	\N	f	orGcBCVPijjO	\N	\N	\N	\N
9	ashwin.t@fyle.in	Travel	Travel	\N	txvh8qm7RTRI	E/2022/01/T/9	C/2022/01/R/8	30	USD	\N	\N	set5qvkasVDnI	f	f	PAYMENT_PROCESSING	\N	\N	\N	rpeM68HKCNNA	2022-01-21 00:00:00+00	2022-01-21 00:00:00+00	2022-01-21 10:45:58.459+00	2022-01-21 10:48:53.928+00	2022-01-21 10:51:06.469783+00	2022-01-21 10:51:06.469819+00	CCC	{"Class": ""}	\N	\N	f	orGcBCVPijjO	\N	\N	\N	\N
10	ashwin.t@fyle.in	Food	Food	Aaron Abbott	txraSPJaG9Ep	E/2022/01/T/13	C/2022/01/R/13	60	USD	\N	\N	setXTEjf2wY78	t	f	PAYMENT_PROCESSING	\N	\N	\N	rp0jk7Rg1epk	2022-01-23 00:00:00+00	2022-01-23 00:00:00+00	2022-01-23 12:01:23.234+00	2022-01-23 12:02:54.246+00	2022-01-23 12:03:10.909511+00	2022-01-23 12:03:10.909564+00	PERSONAL	{"Team": "", "Class": "", "Klass": "", "Team 2": "", "Location": "", "Team Copy": "", "Tax Groups": "", "Departments": "", "User Dimension": "", "Location Entity": "", "Operating System": "", "System Operating": "", "User Dimension Copy": ""}	\N	f	f	or79Cob97KSh	13.13	tggu76WXIdjY	\N	\N
11	ashwin.t@fyle.in	Food	Food	Aaron Abbott	txiKwmiTDjwJ	E/2022/01/T/15	C/2022/01/R/14	60	USD	\N	\N	set8I1KlM4ViY	t	f	PAYMENT_PROCESSING	\N	\N	\N	rp2HJURYKsXI	2022-01-23 00:00:00+00	2022-01-23 00:00:00+00	2022-01-23 12:13:28.367+00	2022-01-23 12:15:45.203+00	2022-01-23 12:15:58.201656+00	2022-01-23 12:15:58.201693+00	PERSONAL	{"Team": "", "Class": "", "Klass": "", "Team 2": "", "Location": "", "Team Copy": "", "Tax Groups": "", "Departments": "", "User Dimension": "", "Location Entity": "", "Operating System": "", "System Operating": "", "User Dimension Copy": ""}	\N	\N	f	or79Cob97KSh	13.13	tggu76WXIdjY	\N	\N
12	ashwin.t@fyle.in	Food	Food	Aaron Abbott	txMFjDHNxEPt	E/2022/01/T/14	C/2022/01/R/14	90	USD	\N	\N	set8I1KlM4ViY	f	f	PAYMENT_PROCESSING	\N	\N	\N	rp2HJURYKsXI	2022-01-23 00:00:00+00	2022-01-23 00:00:00+00	2022-01-23 12:13:03.532+00	2022-01-23 12:15:45.203+00	2022-01-23 12:15:58.31674+00	2022-01-23 12:15:58.316799+00	CCC	{"Team": "", "Class": "", "Klass": "", "Team 2": "", "Location": "", "Team Copy": "", "Tax Groups": "", "Departments": "", "User Dimension": "", "Location Entity": "", "Operating System": "", "System Operating": "", "User Dimension Copy": ""}	\N	\N	f	or79Cob97KSh	19.69	tggu76WXIdjY	\N	\N
13	ashwin.t@fyle.in	Food	Food	Aaron Abbott	txQybwOwoQAA	E/2022/01/T/16	C/2022/01/R/15	60	USD	\N	\N	setRaxYbWGAop	t	f	PAYMENT_PROCESSING	\N	\N	\N	rprUeNwizDFb	2022-01-23 00:00:00+00	2022-01-23 00:00:00+00	2022-01-23 12:32:28.737+00	2022-01-23 12:33:23.908+00	2022-01-23 12:33:35.849933+00	2022-01-23 12:33:35.849968+00	PERSONAL	{"Team": "", "Class": "", "Klass": "", "Team 2": "", "Location": "", "Team Copy": "", "Tax Groups": "", "Departments": "", "User Dimension": "", "Location Entity": "", "Operating System": "", "System Operating": "", "User Dimension Copy": ""}	\N	\N	f	or79Cob97KSh	13.13	tggu76WXIdjY	\N	\N
14	ashwin.t@fyle.in	Food	Food	Aaron Abbott	txRJYVMgMaH6	E/2022/01/T/17	C/2022/01/R/16	60	USD	\N	\N	setwQTDDrGSJN	t	f	PAYMENT_PROCESSING	\N	\N	\N	rpBQ9vx7FJc3	2022-01-23 00:00:00+00	2022-01-23 00:00:00+00	2022-01-23 12:34:58.834+00	2022-01-23 12:35:50.813+00	2022-01-23 12:37:54.106129+00	2022-01-23 12:37:54.106202+00	PERSONAL	{"Team": "", "Class": "", "Klass": "", "Team 2": "", "Location": "", "Team Copy": "", "Tax Groups": "", "Departments": "", "User Dimension": "", "Location Entity": "", "Operating System": "", "System Operating": "", "User Dimension Copy": ""}	\N	\N	f	or79Cob97KSh	13.13	tggu76WXIdjY	\N	\N
\.


--
-- Data for Name: fyle_credentials; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fyle_credentials (id, refresh_token, created_at, updated_at, workspace_id, cluster_domain) FROM stdin;
\.


--
-- Data for Name: general_mappings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.general_mappings (id, bank_account_name, bank_account_id, default_ccc_account_name, default_ccc_account_id, created_at, updated_at, workspace_id, accounts_payable_id, accounts_payable_name, default_ccc_vendor_id, default_ccc_vendor_name, bill_payment_account_id, bill_payment_account_name, qbo_expense_account_id, qbo_expense_account_name, default_tax_code_id, default_tax_code_name, default_debit_card_account_id, default_debit_card_account_name) FROM stdin;
5	Checking	35	Visa	42	2022-01-21 10:37:50.899425+00	2022-01-21 10:37:50.899782+00	8	\N	\N	\N	\N	\N	\N	41	Mastercard	\N	\N	\N	\N
6	\N	\N	Visa	42	2022-01-21 10:42:53.733958+00	2022-01-21 10:42:53.734048+00	9	33	Accounts Payable (A/P)	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
\.


--
-- Data for Name: journal_entries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.journal_entries (id, transaction_date, currency, private_note, created_at, updated_at, expense_group_id) FROM stdin;
\.


--
-- Data for Name: journal_entry_lineitems; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.journal_entry_lineitems (id, debit_account_id, account_id, class_id, entity_id, entity_type, customer_id, department_id, posting_type, amount, description, created_at, updated_at, expense_id, journal_entry_id, tax_amount, tax_code) FROM stdin;
\.


--
-- Data for Name: mapping_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mapping_settings (id, source_field, destination_field, created_at, updated_at, workspace_id, import_to_fyle, is_custom) FROM stdin;
8	CATEGORY	ACCOUNT	2022-01-21 10:42:32.726615+00	2022-01-21 10:42:32.726686+00	9	f	f
7	CATEGORY	ACCOUNT	2022-01-21 10:37:30.494542+00	2022-02-02 05:59:11.615431+00	8	f	f
10	CORPORATE_CARD	CREDIT_CARD_ACCOUNT	2022-02-02 05:59:11.684519+00	2022-02-02 05:59:11.68459+00	8	f	f
\.


--
-- Data for Name: mappings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mappings (id, source_type, destination_type, created_at, updated_at, destination_id, source_id, workspace_id) FROM stdin;
12	CATEGORY	ACCOUNT	2022-01-21 10:40:59.810425+00	2022-01-21 10:40:59.810526+00	1349	7099	8
13	CATEGORY	ACCOUNT	2022-01-21 10:43:37.42+00	2022-01-21 10:43:37.420061+00	1579	9097	9
15	CORPORATE_CARD	CREDIT_CARD_ACCOUNT	2022-02-02 11:26:30.925904+00	2022-02-02 11:26:30.926137+00	1941	12215	8
\.


--
-- Data for Name: qbo_credentials; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.qbo_credentials (id, refresh_token, realm_id, created_at, updated_at, workspace_id, company_name, country) FROM stdin;
\.


--
-- Data for Name: qbo_expense_lineitems; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.qbo_expense_lineitems (id, account_id, class_id, customer_id, amount, billable, description, created_at, updated_at, expense_id, qbo_expense_id, tax_amount, tax_code) FROM stdin;
1	56	\N	\N	60	f	ashwin.t@fyle.in - Food - 2022-01-23 - C/2022/01/R/13 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txraSPJaG9Ep?org_id=or79Cob97KSh	2022-01-23 12:03:22.643074+00	2022-01-23 12:03:22.643138+00	10	1	13.13	\N
2	56	\N	\N	60	\N	ashwin.t@fyle.in - Food - 2022-01-23 - C/2022/01/R/14 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txiKwmiTDjwJ?org_id=or79Cob97KSh	2022-01-23 12:16:41.671332+00	2022-01-23 12:16:41.671403+00	11	2	13.13	\N
3	56	\N	\N	60	\N	ashwin.t@fyle.in - Food - 2022-01-23 - C/2022/01/R/15 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txQybwOwoQAA?org_id=or79Cob97KSh	2022-01-23 12:33:45.521971+00	2022-01-23 12:33:45.522054+00	13	3	13.13	\N
\.


--
-- Data for Name: qbo_expenses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.qbo_expenses (id, expense_account_id, entity_id, department_id, transaction_date, currency, private_note, created_at, updated_at, expense_group_id) FROM stdin;
1	41	55	\N	2022-01-23	USD	Reimbursable expense by ashwin.t@fyle.in on 2022-01-23 	2022-01-23 12:03:21.11365+00	2022-01-23 12:03:21.113698+00	10
2	41	55	\N	2022-01-23	USD	Reimbursable expense by ashwin.t@fyle.in on 2022-01-23 	2022-01-23 12:16:40.977689+00	2022-01-23 12:16:40.977733+00	11
3	41	55	\N	2022-01-23	USD	Reimbursable expense by ashwin.t@fyle.in on 2022-01-23 	2022-01-23 12:33:44.563022+00	2022-01-23 12:33:44.563085+00	13
\.


--
-- Data for Name: reimbursements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reimbursements (id, settlement_id, reimbursement_id, state, created_at, updated_at, workspace_id) FROM stdin;
\.


--
-- Data for Name: task_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.task_logs (id, type, task_id, status, detail, created_at, updated_at, bill_id, expense_group_id, workspace_id, cheque_id, credit_card_purchase_id, journal_entry_id, bill_payment_id, qbo_expense_id, quickbooks_errors) FROM stdin;
7	FETCHING_EXPENSES	\N	COMPLETE	{"message": "Creating expense groups"}	2022-01-21 10:45:15.524593+00	2022-01-21 10:51:06.565798+00	\N	\N	9	\N	\N	\N	\N	\N	\N
9	CREATING_BILL	\N	COMPLETE	{"Bill": {"Id": "146", "Line": [{"Id": "1", "Amount": 120.0, "LineNum": 1, "LinkedTxn": [], "DetailType": "AccountBasedExpenseLineDetail", "Description": "ashwin.t@fyle.in - Travel - 2022-01-21 - C/2022/01/R/7 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txDmcqOv8LMD?org_id=orGcBCVPijjO", "AccountBasedExpenseLineDetail": {"AccountRef": {"name": "Insurance:Workers Compensation", "value": "57"}, "TaxCodeRef": {"value": "NON"}, "BillableStatus": "NotBillable"}}], "domain": "QBO", "sparse": false, "Balance": 120.0, "DueDate": "2022-01-21", "TxnDate": "2022-01-21", "MetaData": {"CreateTime": "2022-01-21T02:45:34-08:00", "LastUpdatedTime": "2022-01-21T02:45:34-08:00"}, "TotalAmt": 120.0, "SyncToken": "0", "VendorRef": {"name": "Mahoney Mugs", "value": "43"}, "CurrencyRef": {"name": "United States Dollar", "value": "USD"}, "PrivateNote": "Reimbursable expense by ashwin.t@fyle.in on 2022-01-21", "APAccountRef": {"name": "Accounts Payable (A/P)", "value": "33"}}, "time": "2022-01-21T02:45:34.098-08:00"}	2022-01-21 10:45:28.314982+00	2022-01-21 10:45:34.179194+00	3	6	9	\N	\N	\N	\N	\N	\N
8	CREATING_CREDIT_CARD_PURCHASE	\N	COMPLETE	{"time": "2022-01-21T02:45:37.586-08:00", "Purchase": {"Id": "147", "Line": [{"Id": "1", "Amount": 50.0, "DetailType": "AccountBasedExpenseLineDetail", "Description": "ashwin.t@fyle.in - Travel - 2022-01-21 - C/2022/01/R/7 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txJkZlJS4LrA?org_id=orGcBCVPijjO", "AccountBasedExpenseLineDetail": {"AccountRef": {"name": "Insurance:Workers Compensation", "value": "57"}, "TaxCodeRef": {"value": "NON"}, "BillableStatus": "NotBillable"}}], "Credit": false, "domain": "QBO", "sparse": false, "TxnDate": "2022-01-21", "MetaData": {"CreateTime": "2022-01-21T02:45:37-08:00", "LastUpdatedTime": "2022-01-21T02:45:37-08:00"}, "TotalAmt": 50.0, "DocNumber": "E/2022/01/T/8", "EntityRef": {"name": "Credit Card Misc", "type": "Vendor", "value": "58"}, "SyncToken": "0", "AccountRef": {"name": "Visa", "value": "42"}, "PurchaseEx": {"any": [{"nil": false, "name": "{http://schema.intuit.com/finance/v3}NameValue", "scope": "javax.xml.bind.JAXBElement$GlobalScope", "value": {"Name": "TxnType", "Value": "54"}, "globalScope": true, "declaredType": "com.intuit.schema.finance.v3.NameValue", "typeSubstituted": false}]}, "CurrencyRef": {"name": "United States Dollar", "value": "USD"}, "CustomField": [], "PaymentType": "CreditCard", "PrivateNote": "Credit card expense by ashwin.t@fyle.in on 2022-01-21"}}	2022-01-21 10:45:28.269498+00	2022-01-21 10:45:37.979199+00	\N	7	9	\N	4	\N	\N	\N	\N
14	CREATING_EXPENSE	\N	COMPLETE	{"time": "2022-01-23T04:16:43.324-08:00", "Purchase": {"Id": "1970", "Line": [{"Id": "1", "Amount": 60.0, "DetailType": "AccountBasedExpenseLineDetail", "Description": "ashwin.t@fyle.in - Food - 2022-01-23 - C/2022/01/R/14 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txiKwmiTDjwJ?org_id=or79Cob97KSh", "AccountBasedExpenseLineDetail": {"AccountRef": {"name": "Automobile:Fuel", "value": "56"}, "TaxCodeRef": {"value": "NON"}, "BillableStatus": "NotBillable"}}], "Credit": false, "domain": "QBO", "sparse": false, "TxnDate": "2022-01-23", "MetaData": {"CreateTime": "2022-01-23T04:16:43-08:00", "LastUpdatedTime": "2022-01-23T04:16:43-08:00"}, "TotalAmt": 60.0, "EntityRef": {"name": "Emily Platt", "type": "Employee", "value": "55"}, "SyncToken": "0", "AccountRef": {"name": "Mastercard", "value": "41"}, "PurchaseEx": {"any": [{"nil": false, "name": "{http://schema.intuit.com/finance/v3}NameValue", "scope": "javax.xml.bind.JAXBElement$GlobalScope", "value": {"Name": "TxnType", "Value": "54"}, "globalScope": true, "declaredType": "com.intuit.schema.finance.v3.NameValue", "typeSubstituted": false}]}, "CurrencyRef": {"name": "United States Dollar", "value": "USD"}, "CustomField": [], "PaymentType": "CreditCard", "PrivateNote": "Reimbursable expense by ashwin.t@fyle.in on 2022-01-23"}}	2022-01-23 12:16:37.740929+00	2022-01-23 12:16:43.48775+00	\N	11	8	\N	\N	\N	\N	2	\N
11	CREATING_BILL	\N	FATAL	{"error": "Traceback (most recent call last):\\n  File \\"/fyle-qbo-api/apps/quickbooks_online/tasks.py\\", line 242, in create_bill\\n    created_bill = qbo_connection.post_bill(bill_object, bill_lineitems_objects)\\n  File \\"/fyle-qbo-api/apps/quickbooks_online/utils.py\\", line 528, in post_bill\\n    print(labhvam)\\nNameError: name 'labhvam' is not defined\\n"}	2022-01-21 16:53:52.786689+00	2022-01-21 16:53:56.662613+00	\N	8	9	\N	\N	\N	\N	\N	\N
10	CREATING_CREDIT_CARD_PURCHASE	\N	FATAL	{"error": "Traceback (most recent call last):\\n  File \\"/fyle-qbo-api/apps/quickbooks_online/tasks.py\\", line 773, in create_credit_card_purchase\\n    credit_card_purchase_object, credit_card_purchase_lineitems_objects\\n  File \\"/fyle-qbo-api/apps/quickbooks_online/utils.py\\", line 775, in post_credit_card_purchase\\n    print(labhvam)\\nNameError: name 'labhvam' is not defined\\n"}	2022-01-21 16:53:52.742574+00	2022-01-21 16:53:59.952724+00	\N	9	9	\N	\N	\N	\N	\N	\N
15	CREATING_JOURNAL_ENTRY	\N	FATAL	{"error": "Traceback (most recent call last):\\n  File \\"/fyle-qbo-api/apps/quickbooks_online/tasks.py\\", line 889, in create_journal_entry\\n    journal_entry_object, journal_entry_lineitems_objects, general_settings.je_single_credit_line)\\n  File \\"/fyle-qbo-api/apps/quickbooks_online/utils.py\\", line 955, in post_journal_entry\\n    priint(labhvam)\\nNameError: name 'priint' is not defined\\n"}	2022-01-23 12:16:37.819397+00	2022-01-23 12:38:03.098434+00	\N	12	8	\N	\N	\N	\N	\N	\N
13	CREATING_EXPENSE	\N	COMPLETE	{"time": "2022-01-23T04:03:25.563-08:00", "Purchase": {"Id": "1969", "Line": [{"Id": "1", "Amount": 60.0, "DetailType": "AccountBasedExpenseLineDetail", "Description": "ashwin.t@fyle.in - Food - 2022-01-23 - C/2022/01/R/13 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txraSPJaG9Ep?org_id=or79Cob97KSh", "AccountBasedExpenseLineDetail": {"AccountRef": {"name": "Automobile:Fuel", "value": "56"}, "TaxCodeRef": {"value": "NON"}, "BillableStatus": "NotBillable"}}], "Credit": false, "domain": "QBO", "sparse": false, "TxnDate": "2022-01-23", "MetaData": {"CreateTime": "2022-01-23T04:03:25-08:00", "LastUpdatedTime": "2022-01-23T04:03:25-08:00"}, "TotalAmt": 60.0, "EntityRef": {"name": "Emily Platt", "type": "Employee", "value": "55"}, "SyncToken": "0", "AccountRef": {"name": "Mastercard", "value": "41"}, "PurchaseEx": {"any": [{"nil": false, "name": "{http://schema.intuit.com/finance/v3}NameValue", "scope": "javax.xml.bind.JAXBElement$GlobalScope", "value": {"Name": "TxnType", "Value": "54"}, "globalScope": true, "declaredType": "com.intuit.schema.finance.v3.NameValue", "typeSubstituted": false}]}, "CurrencyRef": {"name": "United States Dollar", "value": "USD"}, "CustomField": [], "PaymentType": "CreditCard", "PrivateNote": "Reimbursable expense by ashwin.t@fyle.in on 2022-01-23"}}	2022-01-23 12:03:18.259052+00	2022-01-23 12:03:25.844542+00	\N	10	8	\N	\N	\N	\N	1	\N
12	FETCHING_EXPENSES	\N	COMPLETE	{"message": "Creating expense groups"}	2022-01-23 12:03:07.245898+00	2022-01-23 12:37:54.165461+00	\N	\N	8	\N	\N	\N	\N	\N	\N
16	CREATING_EXPENSE	\N	COMPLETE	{"time": "2022-01-23T04:33:47.121-08:00", "Purchase": {"Id": "1972", "Line": [{"Id": "1", "Amount": 60.0, "DetailType": "AccountBasedExpenseLineDetail", "Description": "ashwin.t@fyle.in - Food - 2022-01-23 - C/2022/01/R/15 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txQybwOwoQAA?org_id=or79Cob97KSh", "AccountBasedExpenseLineDetail": {"AccountRef": {"name": "Automobile:Fuel", "value": "56"}, "TaxCodeRef": {"value": "NON"}, "BillableStatus": "NotBillable"}}], "Credit": false, "domain": "QBO", "sparse": false, "TxnDate": "2022-01-23", "MetaData": {"CreateTime": "2022-01-23T04:33:47-08:00", "LastUpdatedTime": "2022-01-23T04:33:47-08:00"}, "TotalAmt": 60.0, "EntityRef": {"name": "Emily Platt", "type": "Employee", "value": "55"}, "SyncToken": "0", "AccountRef": {"name": "Mastercard", "value": "41"}, "PurchaseEx": {"any": [{"nil": false, "name": "{http://schema.intuit.com/finance/v3}NameValue", "scope": "javax.xml.bind.JAXBElement$GlobalScope", "value": {"Name": "TxnType", "Value": "54"}, "globalScope": true, "declaredType": "com.intuit.schema.finance.v3.NameValue", "typeSubstituted": false}]}, "CurrencyRef": {"name": "United States Dollar", "value": "USD"}, "CustomField": [], "PaymentType": "CreditCard", "PrivateNote": "Reimbursable expense by ashwin.t@fyle.in on 2022-01-23"}}	2022-01-23 12:33:42.219271+00	2022-01-23 12:33:47.295229+00	\N	13	8	\N	\N	\N	\N	3	\N
17	CREATING_EXPENSE	\N	FATAL	{"error": "Traceback (most recent call last):\\n  File \\"/fyle-qbo-api/apps/quickbooks_online/tasks.py\\", line 652, in create_qbo_expense\\n    created_qbo_expense = qbo_connection.post_qbo_expense(qbo_expense_object, qbo_expense_line_item_objects)\\n  File \\"/fyle-qbo-api/apps/quickbooks_online/utils.py\\", line 612, in post_qbo_expense\\n    print(labhvam)\\nNameError: name 'labhvam' is not defined\\n"}	2022-01-23 12:37:59.596463+00	2022-01-23 12:38:04.718191+00	\N	14	8	\N	\N	\N	\N	\N	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (password, last_login, id, email, user_id, full_name, active, staff, admin) FROM stdin;
	\N	1	ashwin.t@fyle.in	usqywo0f3nBY		t	f	f
\.


--
-- Data for Name: workspace_general_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workspace_general_settings (id, reimbursable_expenses_object, corporate_credit_card_expenses_object, employee_field_mapping, created_at, updated_at, workspace_id, import_projects, import_categories, sync_fyle_to_qbo_payments, sync_qbo_to_fyle_payments, auto_map_employees, category_sync_version, auto_create_destination_entity, map_merchant_to_vendor, je_single_credit_line, change_accounting_period, import_tax_codes, charts_of_accounts, memo_structure, map_fyle_cards_qbo_account, skip_cards_mapping) FROM stdin;
5	EXPENSE	JOURNAL ENTRY	EMPLOYEE	2022-01-21 10:37:30.3399+00	2022-02-02 05:59:11.554072+00	8	f	f	f	f	\N	v2	f	t	f	f	\N	{Expense}	{employee_email,category,spent_on,report_number,purpose,expense_link}	t	f
6	BILL	CREDIT CARD PURCHASE	VENDOR	2022-01-21 10:42:32.68088+00	2022-02-02 11:46:34.058326+00	9	f	f	f	f	\N	v2	f	t	f	f	\N	{Expense}	{employee_email,category,spent_on,report_number,purpose,expense_link}	t	t
\.


--
-- Data for Name: workspace_schedules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workspace_schedules (id, enabled, start_datetime, interval_hours, schedule_id, workspace_id) FROM stdin;
\.


--
-- Data for Name: workspaces; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workspaces (id, name, fyle_org_id, qbo_realm_id, last_synced_at, created_at, updated_at, destination_synced_at, source_synced_at, cluster_domain) FROM stdin;
8	Fyle For Arkham Asylum	or79Cob97KSh	4620816365031245740	2022-01-23 12:37:54.049698+00	2022-01-21 10:34:47.666562+00	2022-02-02 11:25:54.936404+00	2022-02-02 11:26:24.190842+00	2022-02-02 11:23:46.41437+00	https://staging.fyle.tech
9	Fyle For Intacct Bill-CCT	orGcBCVPijjO	4620816365071123640	2022-01-21 10:51:06.388212+00	2022-01-21 10:41:25.311576+00	2022-02-02 11:30:26.526992+00	2022-02-02 11:47:23.913656+00	2022-02-02 11:47:09.229035+00	https://staging.fyle.tech
\.


--
-- Data for Name: workspaces_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workspaces_user (id, workspace_id, user_id) FROM stdin;
10	8	1
11	9	1
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 164, true);


--
-- Name: bill_payment_lineitems_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bill_payment_lineitems_id_seq', 1, false);


--
-- Name: bill_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bill_payments_id_seq', 1, false);


--
-- Name: category_mappings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.category_mappings_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 41, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 124, true);


--
-- Name: django_q_ormq_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_q_ormq_id_seq', 39, true);


--
-- Name: django_q_schedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_q_schedule_id_seq', 1, false);


--
-- Name: employee_mappings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employee_mappings_id_seq', 7, true);


--
-- Name: fyle_accounting_mappings_destinationattribute_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fyle_accounting_mappings_destinationattribute_id_seq', 1941, true);


--
-- Name: fyle_accounting_mappings_expenseattribute_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fyle_accounting_mappings_expenseattribute_id_seq', 12244, true);


--
-- Name: fyle_accounting_mappings_mapping_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fyle_accounting_mappings_mapping_id_seq', 15, true);


--
-- Name: fyle_accounting_mappings_mappingsetting_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fyle_accounting_mappings_mappingsetting_id_seq', 10, true);


--
-- Name: fyle_expense_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fyle_expense_id_seq', 15, true);


--
-- Name: fyle_expensegroup_expenses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fyle_expensegroup_expenses_id_seq', 15, true);


--
-- Name: fyle_expensegroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fyle_expensegroup_id_seq', 15, true);


--
-- Name: fyle_expensegroupsettings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fyle_expensegroupsettings_id_seq', 10, true);


--
-- Name: fyle_rest_auth_authtokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fyle_rest_auth_authtokens_id_seq', 5, true);


--
-- Name: mappings_generalmapping_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mappings_generalmapping_id_seq', 7, true);


--
-- Name: qbo_expense_lineitems_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.qbo_expense_lineitems_id_seq', 4, true);


--
-- Name: qbo_expenses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.qbo_expenses_id_seq', 4, true);


--
-- Name: quickbooks_online_bill_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quickbooks_online_bill_id_seq', 4, true);


--
-- Name: quickbooks_online_billlineitem_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quickbooks_online_billlineitem_id_seq', 4, true);


--
-- Name: quickbooks_online_cheque_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quickbooks_online_cheque_id_seq', 1, true);


--
-- Name: quickbooks_online_chequelineitem_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quickbooks_online_chequelineitem_id_seq', 1, true);


--
-- Name: quickbooks_online_creditcardpurchase_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quickbooks_online_creditcardpurchase_id_seq', 5, true);


--
-- Name: quickbooks_online_creditcardpurchaselineitem_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quickbooks_online_creditcardpurchaselineitem_id_seq', 5, true);


--
-- Name: quickbooks_online_journalentry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quickbooks_online_journalentry_id_seq', 3, true);


--
-- Name: quickbooks_online_journalentrylineitem_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quickbooks_online_journalentrylineitem_id_seq', 3, true);


--
-- Name: reimbursements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reimbursements_id_seq', 1, false);


--
-- Name: tasks_tasklog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tasks_tasklog_id_seq', 19, true);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_user_id_seq', 1, true);


--
-- Name: workspaces_fylecredential_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.workspaces_fylecredential_id_seq', 10, true);


--
-- Name: workspaces_qbocredential_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.workspaces_qbocredential_id_seq', 20, true);


--
-- Name: workspaces_workspace_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.workspaces_workspace_id_seq', 10, true);


--
-- Name: workspaces_workspace_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.workspaces_workspace_user_id_seq', 12, true);


--
-- Name: workspaces_workspacegeneralsettings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.workspaces_workspacegeneralsettings_id_seq', 7, true);


--
-- Name: workspaces_workspaceschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.workspaces_workspaceschedule_id_seq', 1, false);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: bill_payment_lineitems bill_payment_lineitems_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_payment_lineitems
    ADD CONSTRAINT bill_payment_lineitems_pkey PRIMARY KEY (id);


--
-- Name: bill_payments bill_payments_expense_group_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_payments
    ADD CONSTRAINT bill_payments_expense_group_id_key UNIQUE (expense_group_id);


--
-- Name: bill_payments bill_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_payments
    ADD CONSTRAINT bill_payments_pkey PRIMARY KEY (id);


--
-- Name: category_mappings category_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.category_mappings
    ADD CONSTRAINT category_mappings_pkey PRIMARY KEY (id);


--
-- Name: category_mappings category_mappings_source_category_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.category_mappings
    ADD CONSTRAINT category_mappings_source_category_id_key UNIQUE (source_category_id);


--
-- Name: destination_attributes destination_attributes_destination_id_attribute_dfb58751_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.destination_attributes
    ADD CONSTRAINT destination_attributes_destination_id_attribute_dfb58751_uniq UNIQUE (destination_id, attribute_type, workspace_id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_q_ormq django_q_ormq_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_q_ormq
    ADD CONSTRAINT django_q_ormq_pkey PRIMARY KEY (id);


--
-- Name: django_q_schedule django_q_schedule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_q_schedule
    ADD CONSTRAINT django_q_schedule_pkey PRIMARY KEY (id);


--
-- Name: django_q_task django_q_task_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_q_task
    ADD CONSTRAINT django_q_task_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: employee_mappings employee_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_mappings
    ADD CONSTRAINT employee_mappings_pkey PRIMARY KEY (id);


--
-- Name: employee_mappings employee_mappings_source_employee_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_mappings
    ADD CONSTRAINT employee_mappings_source_employee_id_key UNIQUE (source_employee_id);


--
-- Name: expense_attributes expense_attributes_value_attribute_type_wor_a06aa6b3_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_attributes
    ADD CONSTRAINT expense_attributes_value_attribute_type_wor_a06aa6b3_uniq UNIQUE (value, attribute_type, workspace_id);


--
-- Name: destination_attributes fyle_accounting_mappings_destinationattribute_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.destination_attributes
    ADD CONSTRAINT fyle_accounting_mappings_destinationattribute_pkey PRIMARY KEY (id);


--
-- Name: expense_attributes fyle_accounting_mappings_expenseattribute_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_attributes
    ADD CONSTRAINT fyle_accounting_mappings_expenseattribute_pkey PRIMARY KEY (id);


--
-- Name: mappings fyle_accounting_mappings_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mappings
    ADD CONSTRAINT fyle_accounting_mappings_mapping_pkey PRIMARY KEY (id);


--
-- Name: mapping_settings fyle_accounting_mappings_mappingsetting_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapping_settings
    ADD CONSTRAINT fyle_accounting_mappings_mappingsetting_pkey PRIMARY KEY (id);


--
-- Name: mappings fyle_accounting_mappings_source_type_source_id_de_e40411c3_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mappings
    ADD CONSTRAINT fyle_accounting_mappings_source_type_source_id_de_e40411c3_uniq UNIQUE (source_type, source_id, destination_type, workspace_id);


--
-- Name: expenses fyle_expense_expense_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT fyle_expense_expense_id_key UNIQUE (expense_id);


--
-- Name: expenses fyle_expense_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT fyle_expense_pkey PRIMARY KEY (id);


--
-- Name: expense_groups_expenses fyle_expensegroup_expens_expensegroup_id_expense__2b508048_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_groups_expenses
    ADD CONSTRAINT fyle_expensegroup_expens_expensegroup_id_expense__2b508048_uniq UNIQUE (expensegroup_id, expense_id);


--
-- Name: expense_groups_expenses fyle_expensegroup_expenses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_groups_expenses
    ADD CONSTRAINT fyle_expensegroup_expenses_pkey PRIMARY KEY (id);


--
-- Name: expense_groups fyle_expensegroup_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_groups
    ADD CONSTRAINT fyle_expensegroup_pkey PRIMARY KEY (id);


--
-- Name: expense_group_settings fyle_expensegroupsettings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_group_settings
    ADD CONSTRAINT fyle_expensegroupsettings_pkey PRIMARY KEY (id);


--
-- Name: expense_group_settings fyle_expensegroupsettings_workspace_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_group_settings
    ADD CONSTRAINT fyle_expensegroupsettings_workspace_id_key UNIQUE (workspace_id);


--
-- Name: auth_tokens fyle_rest_auth_authtokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_tokens
    ADD CONSTRAINT fyle_rest_auth_authtokens_pkey PRIMARY KEY (id);


--
-- Name: auth_tokens fyle_rest_auth_authtokens_user_id_3b4bd82e_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_tokens
    ADD CONSTRAINT fyle_rest_auth_authtokens_user_id_3b4bd82e_uniq UNIQUE (user_id);


--
-- Name: mapping_settings mapping_settings_source_field_destination_cdc65270_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapping_settings
    ADD CONSTRAINT mapping_settings_source_field_destination_cdc65270_uniq UNIQUE (source_field, destination_field, workspace_id);


--
-- Name: general_mappings mappings_generalmapping_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.general_mappings
    ADD CONSTRAINT mappings_generalmapping_pkey PRIMARY KEY (id);


--
-- Name: general_mappings mappings_generalmapping_workspace_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.general_mappings
    ADD CONSTRAINT mappings_generalmapping_workspace_id_key UNIQUE (workspace_id);


--
-- Name: qbo_expense_lineitems qbo_expense_lineitems_expense_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qbo_expense_lineitems
    ADD CONSTRAINT qbo_expense_lineitems_expense_id_key UNIQUE (expense_id);


--
-- Name: qbo_expense_lineitems qbo_expense_lineitems_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qbo_expense_lineitems
    ADD CONSTRAINT qbo_expense_lineitems_pkey PRIMARY KEY (id);


--
-- Name: qbo_expenses qbo_expenses_expense_group_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qbo_expenses
    ADD CONSTRAINT qbo_expenses_expense_group_id_key UNIQUE (expense_group_id);


--
-- Name: qbo_expenses qbo_expenses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qbo_expenses
    ADD CONSTRAINT qbo_expenses_pkey PRIMARY KEY (id);


--
-- Name: bills quickbooks_online_bill_expense_group_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bills
    ADD CONSTRAINT quickbooks_online_bill_expense_group_id_key UNIQUE (expense_group_id);


--
-- Name: bills quickbooks_online_bill_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bills
    ADD CONSTRAINT quickbooks_online_bill_pkey PRIMARY KEY (id);


--
-- Name: bill_lineitems quickbooks_online_billlineitem_expense_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_lineitems
    ADD CONSTRAINT quickbooks_online_billlineitem_expense_id_key UNIQUE (expense_id);


--
-- Name: bill_lineitems quickbooks_online_billlineitem_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_lineitems
    ADD CONSTRAINT quickbooks_online_billlineitem_pkey PRIMARY KEY (id);


--
-- Name: cheques quickbooks_online_cheque_expense_group_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cheques
    ADD CONSTRAINT quickbooks_online_cheque_expense_group_id_key UNIQUE (expense_group_id);


--
-- Name: cheques quickbooks_online_cheque_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cheques
    ADD CONSTRAINT quickbooks_online_cheque_pkey PRIMARY KEY (id);


--
-- Name: cheque_lineitems quickbooks_online_chequelineitem_expense_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cheque_lineitems
    ADD CONSTRAINT quickbooks_online_chequelineitem_expense_id_key UNIQUE (expense_id);


--
-- Name: cheque_lineitems quickbooks_online_chequelineitem_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cheque_lineitems
    ADD CONSTRAINT quickbooks_online_chequelineitem_pkey PRIMARY KEY (id);


--
-- Name: credit_card_purchases quickbooks_online_creditcardpurchase_expense_group_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credit_card_purchases
    ADD CONSTRAINT quickbooks_online_creditcardpurchase_expense_group_id_key UNIQUE (expense_group_id);


--
-- Name: credit_card_purchases quickbooks_online_creditcardpurchase_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credit_card_purchases
    ADD CONSTRAINT quickbooks_online_creditcardpurchase_pkey PRIMARY KEY (id);


--
-- Name: credit_card_purchase_lineitems quickbooks_online_creditcardpurchaselineitem_expense_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credit_card_purchase_lineitems
    ADD CONSTRAINT quickbooks_online_creditcardpurchaselineitem_expense_id_key UNIQUE (expense_id);


--
-- Name: credit_card_purchase_lineitems quickbooks_online_creditcardpurchaselineitem_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credit_card_purchase_lineitems
    ADD CONSTRAINT quickbooks_online_creditcardpurchaselineitem_pkey PRIMARY KEY (id);


--
-- Name: journal_entries quickbooks_online_journalentry_expense_group_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT quickbooks_online_journalentry_expense_group_id_key UNIQUE (expense_group_id);


--
-- Name: journal_entries quickbooks_online_journalentry_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT quickbooks_online_journalentry_pkey PRIMARY KEY (id);


--
-- Name: journal_entry_lineitems quickbooks_online_journalentrylineitem_expense_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.journal_entry_lineitems
    ADD CONSTRAINT quickbooks_online_journalentrylineitem_expense_id_key UNIQUE (expense_id);


--
-- Name: journal_entry_lineitems quickbooks_online_journalentrylineitem_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.journal_entry_lineitems
    ADD CONSTRAINT quickbooks_online_journalentrylineitem_pkey PRIMARY KEY (id);


--
-- Name: reimbursements reimbursements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reimbursements
    ADD CONSTRAINT reimbursements_pkey PRIMARY KEY (id);


--
-- Name: task_logs tasks_tasklog_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs
    ADD CONSTRAINT tasks_tasklog_pkey PRIMARY KEY (id);


--
-- Name: users users_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_user_pkey PRIMARY KEY (id);


--
-- Name: users users_user_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_user_user_id_key UNIQUE (user_id);


--
-- Name: workspace_schedules workspace_schedules_schedule_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_schedules
    ADD CONSTRAINT workspace_schedules_schedule_id_key UNIQUE (schedule_id);


--
-- Name: workspace_schedules workspace_schedules_workspace_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_schedules
    ADD CONSTRAINT workspace_schedules_workspace_id_key UNIQUE (workspace_id);


--
-- Name: fyle_credentials workspaces_fylecredential_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fyle_credentials
    ADD CONSTRAINT workspaces_fylecredential_pkey PRIMARY KEY (id);


--
-- Name: fyle_credentials workspaces_fylecredential_workspace_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fyle_credentials
    ADD CONSTRAINT workspaces_fylecredential_workspace_id_key UNIQUE (workspace_id);


--
-- Name: qbo_credentials workspaces_qbocredential_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qbo_credentials
    ADD CONSTRAINT workspaces_qbocredential_pkey PRIMARY KEY (id);


--
-- Name: qbo_credentials workspaces_qbocredential_workspace_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qbo_credentials
    ADD CONSTRAINT workspaces_qbocredential_workspace_id_key UNIQUE (workspace_id);


--
-- Name: workspaces workspaces_workspace_fyle_org_id_ffbabc15_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces
    ADD CONSTRAINT workspaces_workspace_fyle_org_id_ffbabc15_uniq UNIQUE (fyle_org_id);


--
-- Name: workspaces workspaces_workspace_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces
    ADD CONSTRAINT workspaces_workspace_pkey PRIMARY KEY (id);


--
-- Name: workspaces_user workspaces_workspace_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces_user
    ADD CONSTRAINT workspaces_workspace_user_pkey PRIMARY KEY (id);


--
-- Name: workspaces_user workspaces_workspace_user_workspace_id_user_id_1dfc2058_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces_user
    ADD CONSTRAINT workspaces_workspace_user_workspace_id_user_id_1dfc2058_uniq UNIQUE (workspace_id, user_id);


--
-- Name: workspace_general_settings workspaces_workspacegeneralsettings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_general_settings
    ADD CONSTRAINT workspaces_workspacegeneralsettings_pkey PRIMARY KEY (id);


--
-- Name: workspace_general_settings workspaces_workspacegeneralsettings_workspace_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_general_settings
    ADD CONSTRAINT workspaces_workspacegeneralsettings_workspace_id_key UNIQUE (workspace_id);


--
-- Name: workspace_schedules workspaces_workspaceschedule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_schedules
    ADD CONSTRAINT workspaces_workspaceschedule_pkey PRIMARY KEY (id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: bill_payment_lineitems_bill_payment_id_63819dd2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX bill_payment_lineitems_bill_payment_id_63819dd2 ON public.bill_payment_lineitems USING btree (bill_payment_id);


--
-- Name: category_mappings_destination_account_id_ebc44c1c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX category_mappings_destination_account_id_ebc44c1c ON public.category_mappings USING btree (destination_account_id);


--
-- Name: category_mappings_destination_expense_head_id_0ed87fbd; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX category_mappings_destination_expense_head_id_0ed87fbd ON public.category_mappings USING btree (destination_expense_head_id);


--
-- Name: category_mappings_workspace_id_222ea301; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX category_mappings_workspace_id_222ea301 ON public.category_mappings USING btree (workspace_id);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_q_task_id_32882367_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_q_task_id_32882367_like ON public.django_q_task USING btree (id varchar_pattern_ops);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: employee_mappings_destination_card_account_id_f030b899; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX employee_mappings_destination_card_account_id_f030b899 ON public.employee_mappings USING btree (destination_card_account_id);


--
-- Name: employee_mappings_destination_employee_id_b6764819; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX employee_mappings_destination_employee_id_b6764819 ON public.employee_mappings USING btree (destination_employee_id);


--
-- Name: employee_mappings_destination_vendor_id_c4bd73df; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX employee_mappings_destination_vendor_id_c4bd73df ON public.employee_mappings USING btree (destination_vendor_id);


--
-- Name: employee_mappings_workspace_id_4a25f8c9; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX employee_mappings_workspace_id_4a25f8c9 ON public.employee_mappings USING btree (workspace_id);


--
-- Name: fyle_accounting_mappings_d_workspace_id_a6a3ab6a; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fyle_accounting_mappings_d_workspace_id_a6a3ab6a ON public.destination_attributes USING btree (workspace_id);


--
-- Name: fyle_accounting_mappings_expenseattribute_workspace_id_4364b6d7; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fyle_accounting_mappings_expenseattribute_workspace_id_4364b6d7 ON public.expense_attributes USING btree (workspace_id);


--
-- Name: fyle_accounting_mappings_mapping_destination_id_79497f6e; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fyle_accounting_mappings_mapping_destination_id_79497f6e ON public.mappings USING btree (destination_id);


--
-- Name: fyle_accounting_mappings_mapping_source_id_7d692c36; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fyle_accounting_mappings_mapping_source_id_7d692c36 ON public.mappings USING btree (source_id);


--
-- Name: fyle_accounting_mappings_mapping_workspace_id_10d6edd3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fyle_accounting_mappings_mapping_workspace_id_10d6edd3 ON public.mappings USING btree (workspace_id);


--
-- Name: fyle_accounting_mappings_mappingsetting_workspace_id_c123c088; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fyle_accounting_mappings_mappingsetting_workspace_id_c123c088 ON public.mapping_settings USING btree (workspace_id);


--
-- Name: fyle_expense_expense_id_0e743f92_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fyle_expense_expense_id_0e743f92_like ON public.expenses USING btree (expense_id varchar_pattern_ops);


--
-- Name: fyle_expensegroup_expenses_expense_id_f959dd81; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fyle_expensegroup_expenses_expense_id_f959dd81 ON public.expense_groups_expenses USING btree (expense_id);


--
-- Name: fyle_expensegroup_expenses_expensegroup_id_1af76dce; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fyle_expensegroup_expenses_expensegroup_id_1af76dce ON public.expense_groups_expenses USING btree (expensegroup_id);


--
-- Name: fyle_expensegroup_workspace_id_c9b3a8e4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fyle_expensegroup_workspace_id_c9b3a8e4 ON public.expense_groups USING btree (workspace_id);


--
-- Name: qbo_expense_lineitems_qbo_expense_id_92c68be0; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX qbo_expense_lineitems_qbo_expense_id_92c68be0 ON public.qbo_expense_lineitems USING btree (qbo_expense_id);


--
-- Name: quickbooks_online_billlineitem_bill_id_ed04da35; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX quickbooks_online_billlineitem_bill_id_ed04da35 ON public.bill_lineitems USING btree (bill_id);


--
-- Name: quickbooks_online_chequelineitem_cheque_id_599be76a; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX quickbooks_online_chequelineitem_cheque_id_599be76a ON public.cheque_lineitems USING btree (cheque_id);


--
-- Name: quickbooks_online_creditca_credit_card_purchase_id_a58b6b4b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX quickbooks_online_creditca_credit_card_purchase_id_a58b6b4b ON public.credit_card_purchase_lineitems USING btree (credit_card_purchase_id);


--
-- Name: quickbooks_online_journale_journal_entry_id_30896a07; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX quickbooks_online_journale_journal_entry_id_30896a07 ON public.journal_entry_lineitems USING btree (journal_entry_id);


--
-- Name: reimbursements_workspace_id_084805e4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX reimbursements_workspace_id_084805e4 ON public.reimbursements USING btree (workspace_id);


--
-- Name: task_logs_bill_payment_id_fadb892c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX task_logs_bill_payment_id_fadb892c ON public.task_logs USING btree (bill_payment_id);


--
-- Name: task_logs_qbo_expense_id_c879994b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX task_logs_qbo_expense_id_c879994b ON public.task_logs USING btree (qbo_expense_id);


--
-- Name: tasks_tasklog_bill_id_9b095e33; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tasks_tasklog_bill_id_9b095e33 ON public.task_logs USING btree (bill_id);


--
-- Name: tasks_tasklog_cheque_id_31fb235b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tasks_tasklog_cheque_id_31fb235b ON public.task_logs USING btree (cheque_id);


--
-- Name: tasks_tasklog_credit_card_purchase_id_a7ac8cd3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tasks_tasklog_credit_card_purchase_id_a7ac8cd3 ON public.task_logs USING btree (credit_card_purchase_id);


--
-- Name: tasks_tasklog_expense_group_id_1f9994f0; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tasks_tasklog_expense_group_id_1f9994f0 ON public.task_logs USING btree (expense_group_id);


--
-- Name: tasks_tasklog_journal_entry_id_0d410476; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tasks_tasklog_journal_entry_id_0d410476 ON public.task_logs USING btree (journal_entry_id);


--
-- Name: tasks_tasklog_workspace_id_9ab9e212; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tasks_tasklog_workspace_id_9ab9e212 ON public.task_logs USING btree (workspace_id);


--
-- Name: users_user_user_id_4120b7b9_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX users_user_user_id_4120b7b9_like ON public.users USING btree (user_id varchar_pattern_ops);


--
-- Name: workspaces_workspace_fyle_org_id_ffbabc15_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX workspaces_workspace_fyle_org_id_ffbabc15_like ON public.workspaces USING btree (fyle_org_id varchar_pattern_ops);


--
-- Name: workspaces_workspace_user_user_id_7c254800; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX workspaces_workspace_user_user_id_7c254800 ON public.workspaces_user USING btree (user_id);


--
-- Name: workspaces_workspace_user_workspace_id_4a5fb64c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX workspaces_workspace_user_workspace_id_4a5fb64c ON public.workspaces_user USING btree (workspace_id);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bill_payment_lineitems bill_payment_lineite_bill_payment_id_63819dd2_fk_bill_paym; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_payment_lineitems
    ADD CONSTRAINT bill_payment_lineite_bill_payment_id_63819dd2_fk_bill_paym FOREIGN KEY (bill_payment_id) REFERENCES public.bill_payments(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bill_payments bill_payments_expense_group_id_a5b584c3_fk_expense_groups_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_payments
    ADD CONSTRAINT bill_payments_expense_group_id_a5b584c3_fk_expense_groups_id FOREIGN KEY (expense_group_id) REFERENCES public.expense_groups(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: category_mappings category_mappings_destination_account__ebc44c1c_fk_destinati; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.category_mappings
    ADD CONSTRAINT category_mappings_destination_account__ebc44c1c_fk_destinati FOREIGN KEY (destination_account_id) REFERENCES public.destination_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: category_mappings category_mappings_destination_expense__0ed87fbd_fk_destinati; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.category_mappings
    ADD CONSTRAINT category_mappings_destination_expense__0ed87fbd_fk_destinati FOREIGN KEY (destination_expense_head_id) REFERENCES public.destination_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: category_mappings category_mappings_source_category_id_46f19d95_fk_expense_a; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.category_mappings
    ADD CONSTRAINT category_mappings_source_category_id_46f19d95_fk_expense_a FOREIGN KEY (source_category_id) REFERENCES public.expense_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: category_mappings category_mappings_workspace_id_222ea301_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.category_mappings
    ADD CONSTRAINT category_mappings_workspace_id_222ea301_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: employee_mappings employee_mappings_destination_card_acc_f030b899_fk_destinati; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_mappings
    ADD CONSTRAINT employee_mappings_destination_card_acc_f030b899_fk_destinati FOREIGN KEY (destination_card_account_id) REFERENCES public.destination_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: employee_mappings employee_mappings_destination_employee_b6764819_fk_destinati; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_mappings
    ADD CONSTRAINT employee_mappings_destination_employee_b6764819_fk_destinati FOREIGN KEY (destination_employee_id) REFERENCES public.destination_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: employee_mappings employee_mappings_destination_vendor_i_c4bd73df_fk_destinati; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_mappings
    ADD CONSTRAINT employee_mappings_destination_vendor_i_c4bd73df_fk_destinati FOREIGN KEY (destination_vendor_id) REFERENCES public.destination_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: employee_mappings employee_mappings_source_employee_id_dd9948ba_fk_expense_a; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_mappings
    ADD CONSTRAINT employee_mappings_source_employee_id_dd9948ba_fk_expense_a FOREIGN KEY (source_employee_id) REFERENCES public.expense_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: employee_mappings employee_mappings_workspace_id_4a25f8c9_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_mappings
    ADD CONSTRAINT employee_mappings_workspace_id_4a25f8c9_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: mappings fyle_accounting_mapp_destination_id_79497f6e_fk_fyle_acco; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mappings
    ADD CONSTRAINT fyle_accounting_mapp_destination_id_79497f6e_fk_fyle_acco FOREIGN KEY (destination_id) REFERENCES public.destination_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: mappings fyle_accounting_mapp_source_id_7d692c36_fk_fyle_acco; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mappings
    ADD CONSTRAINT fyle_accounting_mapp_source_id_7d692c36_fk_fyle_acco FOREIGN KEY (source_id) REFERENCES public.expense_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: mappings fyle_accounting_mapp_workspace_id_10d6edd3_fk_workspace; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mappings
    ADD CONSTRAINT fyle_accounting_mapp_workspace_id_10d6edd3_fk_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expense_attributes fyle_accounting_mapp_workspace_id_4364b6d7_fk_workspace; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_attributes
    ADD CONSTRAINT fyle_accounting_mapp_workspace_id_4364b6d7_fk_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: destination_attributes fyle_accounting_mapp_workspace_id_a6a3ab6a_fk_workspace; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.destination_attributes
    ADD CONSTRAINT fyle_accounting_mapp_workspace_id_a6a3ab6a_fk_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: mapping_settings fyle_accounting_mapp_workspace_id_c123c088_fk_workspace; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapping_settings
    ADD CONSTRAINT fyle_accounting_mapp_workspace_id_c123c088_fk_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expense_groups_expenses fyle_expensegroup_ex_expense_id_f959dd81_fk_fyle_expe; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_groups_expenses
    ADD CONSTRAINT fyle_expensegroup_ex_expense_id_f959dd81_fk_fyle_expe FOREIGN KEY (expense_id) REFERENCES public.expenses(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expense_groups_expenses fyle_expensegroup_ex_expensegroup_id_1af76dce_fk_fyle_expe; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_groups_expenses
    ADD CONSTRAINT fyle_expensegroup_ex_expensegroup_id_1af76dce_fk_fyle_expe FOREIGN KEY (expensegroup_id) REFERENCES public.expense_groups(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expense_groups fyle_expensegroup_workspace_id_c9b3a8e4_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_groups
    ADD CONSTRAINT fyle_expensegroup_workspace_id_c9b3a8e4_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expense_group_settings fyle_expensegroupset_workspace_id_98c370a1_fk_workspace; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_group_settings
    ADD CONSTRAINT fyle_expensegroupset_workspace_id_98c370a1_fk_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_tokens fyle_rest_auth_authtokens_user_id_3b4bd82e_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_tokens
    ADD CONSTRAINT fyle_rest_auth_authtokens_user_id_3b4bd82e_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: general_mappings mappings_generalmapping_workspace_id_60759557_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.general_mappings
    ADD CONSTRAINT mappings_generalmapping_workspace_id_60759557_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: qbo_expense_lineitems qbo_expense_lineitem_qbo_expense_id_92c68be0_fk_qbo_expen; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qbo_expense_lineitems
    ADD CONSTRAINT qbo_expense_lineitem_qbo_expense_id_92c68be0_fk_qbo_expen FOREIGN KEY (qbo_expense_id) REFERENCES public.qbo_expenses(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: qbo_expense_lineitems qbo_expense_lineitems_expense_id_da6b8457_fk_expenses_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qbo_expense_lineitems
    ADD CONSTRAINT qbo_expense_lineitems_expense_id_da6b8457_fk_expenses_id FOREIGN KEY (expense_id) REFERENCES public.expenses(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: qbo_expenses qbo_expenses_expense_group_id_132f61dc_fk_expense_groups_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qbo_expenses
    ADD CONSTRAINT qbo_expenses_expense_group_id_132f61dc_fk_expense_groups_id FOREIGN KEY (expense_group_id) REFERENCES public.expense_groups(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bill_lineitems quickbooks_online_bi_bill_id_ed04da35_fk_quickbook; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_lineitems
    ADD CONSTRAINT quickbooks_online_bi_bill_id_ed04da35_fk_quickbook FOREIGN KEY (bill_id) REFERENCES public.bills(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bills quickbooks_online_bi_expense_group_id_5b6d4f34_fk_expense_g; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bills
    ADD CONSTRAINT quickbooks_online_bi_expense_group_id_5b6d4f34_fk_expense_g FOREIGN KEY (expense_group_id) REFERENCES public.expense_groups(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bill_lineitems quickbooks_online_bi_expense_id_7b28c8be_fk_expenses_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_lineitems
    ADD CONSTRAINT quickbooks_online_bi_expense_id_7b28c8be_fk_expenses_ FOREIGN KEY (expense_id) REFERENCES public.expenses(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cheque_lineitems quickbooks_online_ch_cheque_id_599be76a_fk_quickbook; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cheque_lineitems
    ADD CONSTRAINT quickbooks_online_ch_cheque_id_599be76a_fk_quickbook FOREIGN KEY (cheque_id) REFERENCES public.cheques(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cheques quickbooks_online_ch_expense_group_id_13bae293_fk_expense_g; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cheques
    ADD CONSTRAINT quickbooks_online_ch_expense_group_id_13bae293_fk_expense_g FOREIGN KEY (expense_group_id) REFERENCES public.expense_groups(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cheque_lineitems quickbooks_online_ch_expense_id_b36dd16a_fk_expenses_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cheque_lineitems
    ADD CONSTRAINT quickbooks_online_ch_expense_id_b36dd16a_fk_expenses_ FOREIGN KEY (expense_id) REFERENCES public.expenses(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: credit_card_purchase_lineitems quickbooks_online_cr_credit_card_purchase_a58b6b4b_fk_quickbook; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credit_card_purchase_lineitems
    ADD CONSTRAINT quickbooks_online_cr_credit_card_purchase_a58b6b4b_fk_quickbook FOREIGN KEY (credit_card_purchase_id) REFERENCES public.credit_card_purchases(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: credit_card_purchases quickbooks_online_cr_expense_group_id_b068cee7_fk_expense_g; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credit_card_purchases
    ADD CONSTRAINT quickbooks_online_cr_expense_group_id_b068cee7_fk_expense_g FOREIGN KEY (expense_group_id) REFERENCES public.expense_groups(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: credit_card_purchase_lineitems quickbooks_online_cr_expense_id_52bf1682_fk_expenses_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credit_card_purchase_lineitems
    ADD CONSTRAINT quickbooks_online_cr_expense_id_52bf1682_fk_expenses_ FOREIGN KEY (expense_id) REFERENCES public.expenses(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: journal_entries quickbooks_online_jo_expense_group_id_ccaf51db_fk_expense_g; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT quickbooks_online_jo_expense_group_id_ccaf51db_fk_expense_g FOREIGN KEY (expense_group_id) REFERENCES public.expense_groups(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: journal_entry_lineitems quickbooks_online_jo_expense_id_e3f816e0_fk_expenses_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.journal_entry_lineitems
    ADD CONSTRAINT quickbooks_online_jo_expense_id_e3f816e0_fk_expenses_ FOREIGN KEY (expense_id) REFERENCES public.expenses(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: journal_entry_lineitems quickbooks_online_jo_journal_entry_id_30896a07_fk_quickbook; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.journal_entry_lineitems
    ADD CONSTRAINT quickbooks_online_jo_journal_entry_id_30896a07_fk_quickbook FOREIGN KEY (journal_entry_id) REFERENCES public.journal_entries(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reimbursements reimbursements_workspace_id_084805e4_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reimbursements
    ADD CONSTRAINT reimbursements_workspace_id_084805e4_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: task_logs task_logs_bill_payment_id_fadb892c_fk_bill_payments_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs
    ADD CONSTRAINT task_logs_bill_payment_id_fadb892c_fk_bill_payments_id FOREIGN KEY (bill_payment_id) REFERENCES public.bill_payments(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: task_logs task_logs_qbo_expense_id_c879994b_fk_qbo_expenses_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs
    ADD CONSTRAINT task_logs_qbo_expense_id_c879994b_fk_qbo_expenses_id FOREIGN KEY (qbo_expense_id) REFERENCES public.qbo_expenses(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: task_logs tasks_tasklog_bill_id_9b095e33_fk_bills_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs
    ADD CONSTRAINT tasks_tasklog_bill_id_9b095e33_fk_bills_id FOREIGN KEY (bill_id) REFERENCES public.bills(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: task_logs tasks_tasklog_cheque_id_31fb235b_fk_cheques_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs
    ADD CONSTRAINT tasks_tasklog_cheque_id_31fb235b_fk_cheques_id FOREIGN KEY (cheque_id) REFERENCES public.cheques(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: task_logs tasks_tasklog_credit_card_purchase_a7ac8cd3_fk_credit_ca; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs
    ADD CONSTRAINT tasks_tasklog_credit_card_purchase_a7ac8cd3_fk_credit_ca FOREIGN KEY (credit_card_purchase_id) REFERENCES public.credit_card_purchases(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: task_logs tasks_tasklog_expense_group_id_1f9994f0_fk_expense_groups_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs
    ADD CONSTRAINT tasks_tasklog_expense_group_id_1f9994f0_fk_expense_groups_id FOREIGN KEY (expense_group_id) REFERENCES public.expense_groups(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: task_logs tasks_tasklog_journal_entry_id_0d410476_fk_journal_entries_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs
    ADD CONSTRAINT tasks_tasklog_journal_entry_id_0d410476_fk_journal_entries_id FOREIGN KEY (journal_entry_id) REFERENCES public.journal_entries(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: task_logs tasks_tasklog_workspace_id_9ab9e212_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs
    ADD CONSTRAINT tasks_tasklog_workspace_id_9ab9e212_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: workspace_schedules workspace_schedules_schedule_id_70b3d838_fk_django_q_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_schedules
    ADD CONSTRAINT workspace_schedules_schedule_id_70b3d838_fk_django_q_ FOREIGN KEY (schedule_id) REFERENCES public.django_q_schedule(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: workspace_schedules workspace_schedules_workspace_id_50ec990f_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_schedules
    ADD CONSTRAINT workspace_schedules_workspace_id_50ec990f_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: fyle_credentials workspaces_fylecrede_workspace_id_f31ac9d2_fk_workspace; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fyle_credentials
    ADD CONSTRAINT workspaces_fylecrede_workspace_id_f31ac9d2_fk_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: qbo_credentials workspaces_qbocreden_workspace_id_cd34e45b_fk_workspace; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qbo_credentials
    ADD CONSTRAINT workspaces_qbocreden_workspace_id_cd34e45b_fk_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: workspaces_user workspaces_workspace_user_user_id_7c254800_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces_user
    ADD CONSTRAINT workspaces_workspace_user_user_id_7c254800_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: workspaces_user workspaces_workspace_workspace_id_4a5fb64c_fk_workspace; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces_user
    ADD CONSTRAINT workspaces_workspace_workspace_id_4a5fb64c_fk_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: workspace_general_settings workspaces_workspace_workspace_id_a18c5f9f_fk_workspace; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_general_settings
    ADD CONSTRAINT workspaces_workspace_workspace_id_a18c5f9f_fk_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

