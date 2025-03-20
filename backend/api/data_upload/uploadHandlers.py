import typing

# INDIVIDUAL UPLOAD HANDLERS: DON'T USE DIRECTLY


class pdf_upload_handler:
    def __call__(self, data: str) -> bool:
        """
        Description:

        Requires:
        Query is a string for the

        Modifies:

        Effects:

        @param data: String to be used for pdf
        """
        pass


supported_file_types = {"application/pdf": pdf_upload_handler()}

# TODO: Determine true type of the param file

# DIRECTLY USABLE UPLOAD HANDLERS:


def upload_handler(content_type: str, content: str) -> bool:
    """
    Description:

    Requires:
    Query is a string for the

    Modifies:

    Effects:

    @param content_type: String containing the content type from the request header
    @param file: String containing the file data
    """

    if content_type in supported_file_types:
        supported_file_types[content_type](content)
