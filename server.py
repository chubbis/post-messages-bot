import argparse
import asyncio
import logging
import sys
from enum import Enum

logging.basicConfig(
    format="%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)


class ServicesEnum(Enum):
    chatbot = "chatbot"
    cb_admin = "cb_admin"


def run_service(service: str):
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    match service:
        case ServicesEnum.chatbot.value:
            from chatbot.bot_start import start_chatbot

            loop.run_until_complete(start_chatbot())
        case ServicesEnum.cb_admin.value:
            from cb_admin.server import CBAdminServer

            cb_admin_server = CBAdminServer(port=8208, debug=True)
            loop.run_until_complete(cb_admin_server())
        case _:
            logger.error("No such service: %s", service_name)
            sys.exit(2)


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-s", "--service", help="Name of service to launch")

    args = argParser.parse_args()
    service_name = args.service
    if not service_name:
        argParser.print_help()
        sys.exit(2)

    run_service(service_name)
