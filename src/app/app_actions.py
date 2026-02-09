from app.use_cases import *
from app.ports.outbound.logger_port import LoggerPort
from app.ports.outbound.repositories.users_repo_port import UsersRepoPort
from app.ports.outbound.repositories.quiz_repo_port import QuizRepoPort
from app.ports.outbound.excel_parser_port import ExcelParserPort
from app.ports.outbound.repositories.telegram_auth_repo_port import TelegramAuthRepoPort


class AppActions:
    def __init__(
        self,
        users_repo: UsersRepoPort,
        tg_auth_repo: TelegramAuthRepoPort,
        quiz_repo: QuizRepoPort,
        excel_parser: ExcelParserPort,
        logger: LoggerPort
    ):
        self.add_quiz_from_excel = AddQuizFromExcel(parser=excel_parser, quiz_repo=quiz_repo)
        self.auth_by_telegram = AuthenticateByTelegram(users_repo=users_repo, tg_auth_repo=tg_auth_repo)
        self.check_admin_access = CheckAdminAccess(users_repo=users_repo)

