from app.use_cases import *
from app.ports.outbound.repositories.users_repo_port import UsersRepoPort
from app.ports.outbound.repositories.quiz_repo_port import QuizRepoPort
from app.ports.outbound.excel_parser_port import ExcelParserPort
from app.ports.outbound.repositories.telegram_auth_repo_port import TelegramAuthRepoPort
from app.ports.outbound.repositories.quiz_session_repo_port import QuizSessionRepoPort
from app.ports.outbound.excel_exporter_port import ExcelExporterPort


class AppActions:
    def __init__(
        self,
        users_repo: UsersRepoPort,
        tg_auth_repo: TelegramAuthRepoPort,
        quiz_repo: QuizRepoPort,
        excel_parser: ExcelParserPort,
        quiz_session_repo: QuizSessionRepoPort,
        excel_exporter: ExcelExporterPort
    ):
        self.add_quiz_from_excel = AddQuizFromExcelUC(parser=excel_parser, quiz_repo=quiz_repo)
        self.auth_by_telegram = AuthenticateByTelegramUC(users_repo=users_repo, tg_auth_repo=tg_auth_repo)
        self.check_admin_access = CheckAdminAccessUC(users_repo=users_repo)
        self.get_current_question = GetCurrentQuestionUC(quiz_session_repo=quiz_session_repo)
        self.start_quiz = StartQuizUC(users_repo=users_repo, quiz_session_repo=quiz_session_repo)
        self.submit_answer = SubmitAnswerUC(quiz_session_repo=quiz_session_repo)
        self.quiz_list = QuizListUC(quiz_repo=quiz_repo)
        self.set_user_name = SetUserNameUC(users_repo=users_repo)
        self.get_completed_quizzes = GetCompletedQuizzesUC(quiz_session_repo=quiz_session_repo)
        self.delete_quiz = DeleteQuizUC(quiz_repo=quiz_repo)
        self.excel_export_attempts = ExcelExportAttemptsUC(quiz_session_repo=quiz_session_repo, excel_exporter=excel_exporter)

