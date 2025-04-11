from enum import Enum

class ResultMessage(Enum):

    GENERAL_SUCCESS_RESPONSE = (True, "S-001", "berhasil")
    DELETED_SUCCESS_RESPONSE = (True, "S-002", "Data berhasil dihapus")

    GENERAL_ERROR_RESPONSE = (False, "E-001", "Maaf, sistem sedang mengalami kendala")
    INPUT_ERROR = (False, "E-002", "Data input tidak sesuai")
    NOT_FOUND_ERROR = (False, "E-003", "Data tidak ditemukan")
    

    def __init__(self, success, code, message):
        self.success = success
        self.code = code
        self.message = message



CODE_FIELD_ERRORS = {
    "max_length": "Kode maksimal 10 huruf",
    "blank": "Kode harus diisi",
    "required": "Kode harus diisi",
}

NAME_FIELD_ERRORS = {
    "max_length": "Nama maksimal 100 huruf",
    "blank": "Nama harus diisi",
    "required": "Nama harus diisi",
}

UNIT_FIELD_ERRORS = {
    "max_length": "Unit maksimal 5 huruf",
    "blank": "Unit harus diisi",
    "required": "Unit harus diisi",
}

DESC_FIELD_ERRORS = {
    "blank": "Deskripsi harus diisi",
    "required": "Deskripsi harus diisi",
}