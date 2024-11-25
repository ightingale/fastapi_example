import logging

from sqladmin import ModelView

from src.data_access.models import Tariff, Payment, TaskDB, UserDb

logger: logging.Logger = logging.getLogger(__name__)


class TariffAdmin(ModelView, model=Tariff):
    column_list = [Tariff.id, Tariff.title, Tariff.count]


class PaymentAdmin(ModelView, model=Payment):
    column_list = [
        Payment.id,
        Payment.payment_system,
        Payment.amount,
        Payment.user_id,
        Payment.confirm,
        Payment.created_at,
        Payment.updated_at,
        Payment.payment_method,
    ]
    column_searchable_list = [Payment.id, Payment.user_id]

    column_default_sort = (Payment.created_at, True)
    column_sortable_list = [Payment.created_at, Payment.user_id]


class TaskDBAdmin(ModelView, model=TaskDB):
    column_list = [
        TaskDB.id,
        TaskDB.task_id,
        TaskDB.user_id,
        TaskDB.status,
        TaskDB.successful_count,
        TaskDB.hold_sum,
        TaskDB.final_sum,
        TaskDB.started_at,
        TaskDB.updated_at,
    ]
    column_searchable_list = [TaskDB.id, TaskDB.task_id, TaskDB.user_id]

    column_details_list = [
        TaskDB.id,
        TaskDB.task_id,
        TaskDB.user_id,
        TaskDB.status,
        TaskDB.numbers,
        TaskDB.settings,
        TaskDB.successful_count,
        TaskDB.hold_sum,
        TaskDB.final_sum,
        TaskDB.started_at,
        TaskDB.updated_at,
        "file",
    ]

    column_formatters_detail = {
        "file": lambda model, _: f"https://tg-checker.com/api/get_file?file_id=xlsx_{model.task_id}"
    }

    column_default_sort = (TaskDB.started_at, True)
    column_sortable_list = [TaskDB.started_at]


class UserAdmin(ModelView, model=UserDb):
    column_list = [
        UserDb.id,
        UserDb.email,
        UserDb.balance,
    ]
    column_searchable_list = [UserDb.id, UserDb.email]

    column_default_sort = (UserDb.id, True)
    column_sortable_list = [UserDb.id]
