import typing



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

    
#TODO: Determine true type of the param file
def UploadHandler(content_type: str, file: str) -> bool:
    """
    Description:

    Requires:
    Query is a string for the
    Modifies:
    Effects:

    @param content_type: String containing the content type from the request header
    @param file: String containing the file data
    """
    supported_file_types = {"application/pdf" : pdf_upload_handler()}

    if content_type in supported_file_types:
        supported_file_types[content_type](file)