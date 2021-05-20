from celery import Celery
from celery_tasks.main import app
from .ytx_sdk.sendSMS import CCP
import logging

logger = logging.getLogger("django")


@app.task(name='send_sms_code')
def send_sms_code(mobile, code, expires, template_id):
    """发送短信验证码"""
    try:

        result = CCP.sendTemplateSMS(mobile, code, expires, template_id)

    except Exception as e:
        logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
    else:
        if result == 0:
            logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
        else:
            logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)

