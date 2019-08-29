#1/usr/bin/env python
from app.models import (
    AuditStatus,
    AuditStatuses,
    AuditLog
    )

RUN_ID  = ""
SHOP_ID = ""

class Logger:

    @staticmethod
    def start(run_id, shop_id):
        Logger.status_message(run_id, shop_id, "Run started")
        audit = AuditStatus(run_id, shop_id, AuditStatuses.RUNNING)
        audit.save()

    @staticmethod
    def complete(run_id, shop_id):
        Logger.status_message(run_id, shop_id, "Run completed")
        audit = AuditStatus(run_id, shop_id, AuditStatuses.COMPLETE)
        audit.save()

    @staticmethod
    def error(run_id, shop_id):
        Logger.status_message(run_id, shop_id, "Run ended in error")
        audit = AuditStatus(run_id, shop_id, AuditStatuses.ERROR)
        audit.save()

    @staticmethod
    def error_message(run_id, shop_id, message):
        auditLog = AuditLog(run_id, shop_id, message)
        auditLog.save()
        Logger.error(run_id, shop_id)

    @staticmethod
    def status_message(run_id, shop_id, message):
        auditLog = AuditLog(run_id, shop_id, message)
        auditLog.save()
