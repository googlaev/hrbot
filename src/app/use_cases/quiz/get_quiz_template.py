from app.ports.outbound.excel_parser_port import ExcelParserPort
from app.ports.outbound.csv_parser_port import CSVParserPort


class GetQuizTemplateUC:
    def __init__(self, ep: ExcelParserPort, cp: CSVParserPort):
        self.excel_parser = ep
        self.csv_parser = cp

    async def from_excel(self) -> bytes:
        return self.excel_parser.get_template()
    
    async def from_csv(self) -> bytes:
        return self.csv_parser.get_template()

